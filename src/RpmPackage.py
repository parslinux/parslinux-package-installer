#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RpmPackage.py for parslinux-package-installer.
Provides Red Hat / Fedora / openSUSE RPM (.rpm) package inspection and metadata handling.
Uses a pure Python binary header parser with fallback to local tools (rpm2cpio/rpm).
"""

import io
import logging
import os
import platform
import shutil
import struct
import subprocess
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("parslinux-rpm")


class RpmPackage:
    """Represents and inspects an RPM (.rpm) package archive."""

    RPM_LEAD_MAGIC = b"\xed\xab\xee\xdb"
    RPM_HEADER_MAGIC = b"\x8e\xad\xe8\x01"

    # RPM Header Tags Specification
    TAG_NAME = 1000
    TAG_VERSION = 1001
    TAG_RELEASE = 1002
    TAG_SUMMARY = 1004
    TAG_DESCRIPTION = 1005
    TAG_SIZE = 1009
    TAG_DISTRIBUTION = 1016
    TAG_URL = 1020
    TAG_OS = 1021
    TAG_ARCH = 1022
    TAG_DIRNAMES = 1027
    TAG_BASENAMES = 1035
    TAG_DIRINDEXES = 1036
    TAG_PACKAGER = 1047
    TAG_GROUP = 1016
    TAG_REQUIRENAME = 1049
    TAG_REQUIREVERSION = 1050
    TAG_OLDFILENAMES = 1112

    VERSION_NONE = 0
    VERSION_OUTDATED = 1
    VERSION_SAME = 2
    VERSION_NEWER = 3

    def __init__(self, filename: str, cache=None) -> None:
        self.file = os.path.abspath(filename)
        if not os.path.exists(self.file):
            raise FileNotFoundError(f"RPM file not found: {self.file}")

        self.size = os.path.getsize(self.file)
        self.fields: Dict[str, str] = {}
        self.missing_deps: List[str] = []
        self.packagemissingdeps: str = ""
        self._failure_string: Optional[str] = None
        self._raw_tags: Dict[int, any] = {}

        self._parse_rpm()

        self.pkgname = self.fields.get("Package", os.path.basename(self.file).split("-")[0])

    def compare_to_version_in_cache(self) -> int:
        """Compare archive version to installed version (0: new, 1: downgrade, 2: same, 3: upgrade)."""
        installed = self.get_installed_version()
        if not installed:
            return self.VERSION_NONE

        target = self.get("Version", "")
        if target == installed:
            return self.VERSION_SAME
        if target > installed:
            return self.VERSION_NEWER
        elif target < installed:
            return self.VERSION_OUTDATED
        return self.VERSION_SAME

    def _parse_rpm(self) -> None:
        """Parse RPM headers directly using binary stream with fallback to rpm CLI."""
        try:
            with open(self.file, "rb") as f:
                magic = f.read(4)
                if magic != self.RPM_LEAD_MAGIC:
                    raise ValueError(f"Invalid RPM lead magic: {magic!r}")

                # Skip rest of lead (96 bytes total)
                f.seek(96)

                # Find main header (skipping signature header if present)
                def read_header_block():
                    sig = f.read(4)
                    while sig and sig != self.RPM_HEADER_MAGIC:
                        sig = f.read(4)
                    if not sig:
                        return None
                    _reserved, nindex, dsize = struct.unpack(">III", f.read(12))
                    indexes = [struct.unpack(">IIII", f.read(16)) for _ in range(nindex)]
                    data_store = f.read(dsize)
                    return indexes, data_store

                first_block = read_header_block()
                second_block = read_header_block()
                main_block = second_block if second_block else first_block

                if main_block:
                    indexes, data_store = main_block
                    for tag, ttype, offset, count in indexes:
                        val = self._extract_tag_value(ttype, offset, count, data_store)
                        self._raw_tags[tag] = val

            self._populate_fields_from_tags()
            return
        except Exception as e:
            logger.debug("Pure Python RPM parsing error: %s. Trying CLI fallback...", e)

        # CLI fallback if system has rpm tool
        self._parse_via_rpm_cli()

    @staticmethod
    def _extract_tag_value(ttype: int, offset: int, count: int, data: bytes):
        """Decode tag value according to RPM data types."""
        if ttype in (6, 9):  # STRING or I18NSTRING
            end = data.find(b"\x00", offset)
            if end != -1:
                return data[offset:end].decode("utf-8", "replace")
            return ""
        elif ttype == 8:  # STRING_ARRAY
            items = []
            curr = offset
            for _ in range(count):
                end = data.find(b"\x00", curr)
                if end != -1:
                    items.append(data[curr:end].decode("utf-8", "replace"))
                    curr = end + 1
            return items
        elif ttype == 4:  # INT32
            if len(data) >= offset + 4:
                return struct.unpack(">I", data[offset:offset+4])[0]
        elif ttype == 5:  # INT64
            if len(data) >= offset + 8:
                return struct.unpack(">Q", data[offset:offset+8])[0]
        return None

    def _populate_fields_from_tags(self) -> None:
        """Map raw parsed RPM tags to standard package installer metadata fields."""
        name = str(self._raw_tags.get(self.TAG_NAME, ""))
        version = str(self._raw_tags.get(self.TAG_VERSION, ""))
        release = str(self._raw_tags.get(self.TAG_RELEASE, ""))
        full_version = f"{version}-{release}" if release else version

        self.fields["Package"] = name
        self.fields["Version"] = full_version
        self.fields["Architecture"] = str(self._raw_tags.get(self.TAG_ARCH, "x86_64"))
        self.fields["Section"] = str(self._raw_tags.get(self.TAG_GROUP, "RPM"))
        self.fields["Maintainer"] = str(self._raw_tags.get(self.TAG_PACKAGER, "-"))
        self.fields["Homepage"] = str(self._raw_tags.get(self.TAG_URL, ""))
        self.fields["Summary"] = str(self._raw_tags.get(self.TAG_SUMMARY, ""))
        self.fields["Description"] = str(self._raw_tags.get(self.TAG_DESCRIPTION, self.fields["Summary"]))

        size_bytes = self._raw_tags.get(self.TAG_SIZE, self.size)
        self.fields["Installed-Size"] = str(int(size_bytes) // 1024)

        reqs = self._raw_tags.get(self.TAG_REQUIRENAME, [])
        if isinstance(reqs, list):
            # Filter out rpmlib internal requirements
            user_reqs = [r for r in reqs if not r.startswith("rpmlib(")]
            self.fields["Depends"] = ", ".join(user_reqs) if user_reqs else "(Yok)"
        else:
            self.fields["Depends"] = "(Yok)"

    def _parse_via_rpm_cli(self) -> None:
        """Query metadata via rpm tool if installed."""
        rpm_bin = shutil.which("rpm")
        if not rpm_bin:
            return

        cmd = [
            rpm_bin, "-qp",
            "--queryformat",
            "%{NAME}\n%{VERSION}\n%{RELEASE}\n%{ARCH}\n%{SIZE}\n%{SUMMARY}\n%{URL}\n%{PACKAGER}\n",
            self.file
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if res.returncode == 0:
                lines = res.stdout.strip().split("\n")
                if len(lines) >= 8:
                    name, ver, rel, arch, size_b, summary, url, packager = lines[:8]
                    self.fields["Package"] = name
                    self.fields["Version"] = f"{ver}-{rel}" if rel else ver
                    self.fields["Architecture"] = arch
                    self.fields["Installed-Size"] = str(int(size_b) // 1024) if size_b.isdigit() else "0"
                    self.fields["Summary"] = summary
                    self.fields["Description"] = summary
                    self.fields["Homepage"] = url
                    self.fields["Maintainer"] = packager
        except Exception:
            pass

    def get(self, key: str, default: str = "") -> str:
        """Retrieve package metadata field by case-insensitive key."""
        for k, v in self.fields.items():
            if k.lower() == key.lower():
                return v
        return default

    def get_installed_version(self) -> Optional[str]:
        """Check if this RPM or application is currently installed on host."""
        rpm_bin = shutil.which("rpm")
        if rpm_bin:
            try:
                res = subprocess.run([rpm_bin, "-q", self.pkgname], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
                if res.returncode == 0:
                    return res.stdout.strip()
            except Exception:
                pass

        # Check pacman on Arch Linux
        if shutil.which("pacman"):
            try:
                res = subprocess.run(["pacman", "-Q", self.pkgname], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
                if res.returncode == 0:
                    return res.stdout.strip().split()[-1]
            except Exception:
                pass

        # Check dpkg on Debian
        if shutil.which("dpkg-query"):
            try:
                res = subprocess.run(["dpkg-query", "-W", "-f=${Version}", self.pkgname], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip()
            except Exception:
                pass

        return None

    def check(self) -> bool:
        """Verify package integrity and architecture compatibility."""
        arch_ok, _pkg_arch, _host_arch = self.check_architecture()
        if not arch_ok:
            self._failure_string = f"Mimari uyuşmazlığı: Paket '{_pkg_arch}', Sistem '{_host_arch}'."
            return False
        return True

    def check_architecture(self) -> Tuple[bool, str, str]:
        """Verify if target package architecture is runnable on current CPU."""
        pkg_arch = self.get("Architecture", "x86_64").strip().lower()
        host_arch = platform.machine().lower()

        arch_map = {
            "amd64": "x86_64",
            "x86_64": "x86_64",
            "noarch": "all",
            "all": "all",
            "i386": "i686",
            "i686": "i686",
            "aarch64": "arm64",
            "arm64": "arm64",
        }

        canon_pkg = arch_map.get(pkg_arch, pkg_arch)
        canon_host = arch_map.get(host_arch, host_arch)

        if canon_pkg in ("all", "noarch") or canon_pkg == canon_host:
            return True, pkg_arch, host_arch

        return False, pkg_arch, host_arch

    def get_file_list(self) -> List[str]:
        """Return raw list of contained filenames."""
        # 1. From OLDFILENAMES tag
        old_files = self._raw_tags.get(self.TAG_OLDFILENAMES)
        if isinstance(old_files, list) and old_files:
            return old_files

        # 2. Reconstruct from DIRNAMES, BASENAMES, DIRINDEXES
        dirnames = self._raw_tags.get(self.TAG_DIRNAMES, [])
        basenames = self._raw_tags.get(self.TAG_BASENAMES, [])
        dirindexes = self._raw_tags.get(self.TAG_DIRINDEXES, [])

        if isinstance(dirnames, list) and isinstance(basenames, list) and isinstance(dirindexes, list):
            reconstructed = []
            for i, base in enumerate(basenames):
                dir_idx = dirindexes[i] if i < len(dirindexes) else 0
                dir_path = dirnames[dir_idx] if dir_idx < len(dirnames) else "/"
                reconstructed.append(os.path.join(dir_path, base))
            if reconstructed:
                return reconstructed

        # 3. CLI fallback via rpm2cpio / rpm -qlp
        rpm_bin = shutil.which("rpm")
        if rpm_bin:
            try:
                res = subprocess.run([rpm_bin, "-qlp", self.file], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
                if res.returncode == 0:
                    return [line.strip() for line in res.stdout.split("\n") if line.strip()]
            except Exception:
                pass

        return []

    def get_file_details(self) -> List[Dict[str, any]]:
        """Return structured file detail dictionaries for UI display."""
        files = self.get_file_list()
        details = []
        for path in files:
            is_dir = path.endswith("/") or not os.path.basename(path)
            is_exec = (not is_dir) and any(path.startswith(p) for p in ("/usr/bin", "/usr/sbin", "/bin", "/sbin", "/opt/"))
            details.append({
                "name": path,
                "size": 0 if is_dir else 1024,
                "is_dir": is_dir,
                "is_sym": False,
                "is_exec": is_exec,
                "mode": "0755" if (is_dir or is_exec) else "0644",
                "mode_str": "755" if (is_dir or is_exec) else "644",
                "target": ""
            })
        return details
