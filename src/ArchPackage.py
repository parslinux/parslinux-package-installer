#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArchPackage handler for parslinux-package-installer.
Parses Arch Linux native binary packages (.pkg.tar.zst, .pkg.tar.xz, .pkg.tar.gz).
Provides full metadata extraction, file tree inspection, and dependency checking via pacman.
"""

import io
import logging
import os
import re
import shutil
import subprocess
import tarfile
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("parslinux-archpackage")


def is_arch_package(filepath: str) -> bool:
    """Check if the given path has an Arch Linux package extension."""
    if not isinstance(filepath, str):
        return False
    lower = filepath.lower()
    return lower.endswith((
        ".pkg.tar.zst",
        ".pkg.tar.xz",
        ".pkg.tar.gz",
        ".pkg.tar.bz2",
        ".pkg.tar"
    ))


class ArchPackage:
    """Inspection and verification handler for Arch Linux binary packages."""

    VERSION_NONE = 0
    VERSION_OUTDATED = 1
    VERSION_SAME = 2
    VERSION_NEWER = 3

    def __init__(self, filename: str, cache: Any = None) -> None:
        self.filename = os.path.abspath(filename)
        if not os.path.isfile(self.filename):
            raise FileNotFoundError(f"File not found: {self.filename}")

        self.cache = cache
        self.package_type = "arch"
        self.pkgname = ""
        self.pkgver = ""
        self.pkgdesc = ""
        self.url = ""
        self.packager = ""
        self.arch = ""
        self.size = 0
        self.license = ""
        self.depends: List[str] = []
        self.optdepends: List[str] = []
        self.conflicts: List[str] = []
        self.provides: List[str] = []
        self._sections: Dict[str, str] = {}
        self.missing_deps: List[str] = []
        self._failure_string = ""
        self.required_changes: Dict[str, Any] = {}
        self.filelist: List[str] = []
        self._file_details: Optional[List[Dict[str, Any]]] = None
        self._file_size_bytes = os.path.getsize(self.filename)

        self._parse_arch_package()

    @staticmethod
    def _open_tar(content_or_file) -> tarfile.TarFile:
        """Open tar archive handling gzip, xz, bz2, and zstd formats."""
        if isinstance(content_or_file, (str, os.PathLike)):
            path = str(content_or_file)
            if path.endswith(".zst"):
                try:
                    p = subprocess.run(["zstd", "-d", "-c", path], capture_output=True, check=True)
                    return tarfile.open(fileobj=io.BytesIO(p.stdout), mode="r:")
                except Exception as e:
                    logger.error("Failed decompressing zstd archive %s: %s", path, e)
                    raise
            return tarfile.open(path, mode="r:*")
        elif isinstance(content_or_file, bytes):
            try:
                return tarfile.open(fileobj=io.BytesIO(content_or_file), mode="r:*")
            except Exception:
                try:
                    p = subprocess.run(["zstd", "-d", "-c"], input=content_or_file, capture_output=True, check=True)
                    return tarfile.open(fileobj=io.BytesIO(p.stdout), mode="r:")
                except Exception:
                    pass
                raise
        raise ValueError("Invalid tar content input")

    def _parse_arch_package(self) -> None:
        """Extract .PKGINFO metadata and internal file list from Arch package."""
        pkginfo_text = None
        files: List[str] = []
        details: List[Dict[str, Any]] = []

        try:
            with self._open_tar(self.filename) as tar:
                for member in tar.getmembers():
                    # Ignore root metadata files in standard file tree display
                    if member.name in (".PKGINFO", ".BUILDINFO", ".MTREE", ".INSTALL"):
                        if member.name == ".PKGINFO":
                            extracted = tar.extractfile(member)
                            if extracted:
                                pkginfo_text = extracted.read().decode("utf-8", errors="replace")
                        continue

                    clean_name = member.name.lstrip(".")
                    if clean_name and clean_name != "/":
                        if not clean_name.startswith("/"):
                            clean_name = "/" + clean_name
                        files.append(clean_name)
                        details.append({
                            "name": clean_name,
                            "size": member.size if not member.isdir() else 0,
                            "is_dir": member.isdir(),
                            "is_sym": member.issym() or member.islnk(),
                            "is_exec": bool(member.mode & 0o111) if not member.isdir() else False,
                            "mode": oct(member.mode) if member.mode else "0644",
                            "mode_str": oct(member.mode)[-3:] if member.mode else "644",
                            "target": member.linkname if (member.issym() or member.islnk()) else ""
                        })
        except Exception as e:
            logger.error("Error opening Arch package %s: %s", self.filename, e)
            raise ValueError(f"Geçersiz Arch Linux paketi: {e}")

        if not pkginfo_text:
            raise ValueError("Paket içinde .PKGINFO dosyası bulunamadı.")

        self.filelist = sorted(files)
        self._file_details = sorted(details, key=lambda d: d["name"])
        self._parse_pkginfo(pkginfo_text)

    def _parse_pkginfo(self, text: str) -> None:
        """Parse key = value entries from .PKGINFO text."""
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                k = key.strip()
                v = val.strip()

                if k == "pkgname":
                    self.pkgname = v
                elif k == "pkgver":
                    self.pkgver = v
                elif k == "pkgdesc":
                    self.pkgdesc = v
                elif k == "url":
                    self.url = v
                elif k == "packager":
                    self.packager = v
                elif k == "size":
                    try:
                        self.size = int(v)
                    except ValueError:
                        self.size = 0
                elif k == "arch":
                    self.arch = v
                elif k == "license":
                    self.license = v
                elif k == "depend":
                    self.depends.append(v)
                elif k == "optdepend":
                    self.optdepends.append(v)
                elif k == "conflict":
                    self.conflicts.append(v)
                elif k == "provides":
                    self.provides.append(v)

        # Populate dictionary sections for generic compatibility
        size_kb = str(self.size // 1024) if self.size else "0"
        self._sections = {
            "Package": self.pkgname,
            "Version": self.pkgver,
            "Description": self.pkgdesc,
            "Architecture": self.arch,
            "Installed-Size": size_kb,
            "Maintainer": self.packager,
            "Homepage": self.url,
            "Depends": ", ".join(self.depends),
            "Section": "Arch Linux",
            "License": self.license
        }

    def __getitem__(self, key: str) -> str:
        return self._sections.get(key, "")

    def get(self, key: str, default: str = "") -> str:
        return self._sections.get(key, default)

    def get_file_details(self) -> List[Dict[str, Any]]:
        """Return rich file information list for UI tree views."""
        if self._file_details is None:
            self._file_details = []
        return self._file_details

    def get_installed_version(self) -> Optional[str]:
        """Query currently installed package version via pacman -Q."""
        pacman_bin = shutil.which("pacman") or ("/usr/bin/pacman" if os.path.exists("/usr/bin/pacman") else None)
        if not pacman_bin or not self.pkgname:
            return None

        try:
            res = subprocess.run(
                [pacman_bin, "-Q", self.pkgname],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False
            )
            if res.returncode == 0 and res.stdout:
                # pacman -Q outputs: "pkgname version"
                parts = res.stdout.strip().split()
                if len(parts) >= 2:
                    return parts[1]
        except Exception as e:
            logger.debug("pacman -Q check failed: %s", e)
        return None

    def compare_to_version_in_cache(self) -> int:
        """Compare package version to installed pacman version."""
        installed_ver = self.get_installed_version()
        if not installed_ver:
            return self.VERSION_NONE

        target_ver = self.pkgver
        if not target_ver:
            return self.VERSION_NONE

        if target_ver == installed_ver:
            return self.VERSION_SAME

        # Try vercmp if installed on Arch
        vercmp_bin = shutil.which("vercmp")
        if vercmp_bin:
            try:
                res = subprocess.run([vercmp_bin, target_ver, installed_ver], stdout=subprocess.PIPE, text=True, check=False)
                val = int(res.stdout.strip())
                if val > 0:
                    return self.VERSION_NEWER
                elif val < 0:
                    return self.VERSION_OUTDATED
                return self.VERSION_SAME
            except Exception:
                pass

        # Fallback basic version comparison
        if target_ver > installed_ver:
            return self.VERSION_NEWER
        elif target_ver < installed_ver:
            return self.VERSION_OUTDATED
        return self.VERSION_SAME

    def check_architecture(self) -> Tuple[bool, str]:
        """Verify architecture compatibility against host."""
        if not self.arch or self.arch in ("any", "all"):
            return True, ""

        host_arch = os.uname().machine
        # Normalize x86_64 and aarch64
        arch_aliases = {
            "x86_64": ["x86_64", "amd64"],
            "aarch64": ["aarch64", "arm64"],
            "i686": ["i686", "i386"],
        }
        compatible = arch_aliases.get(host_arch, [host_arch])
        if self.arch in compatible:
            return True, ""

        return False, f"Paket '{self.arch}' mimarisi gerektiriyor (Sistem mimarisi: '{host_arch}')."

    def check(self) -> bool:
        """Check if dependencies and architecture are satisfied in Arch Linux."""
        arch_ok, arch_msg = self.check_architecture()
        if not arch_ok:
            self._failure_string = arch_msg
            return False

        pacman_bin = shutil.which("pacman")
        if not pacman_bin:
            # If pacman isn't installed (e.g. running on Debian/Ubuntu), report installable
            self.missing_deps = []
            self._failure_string = ""
            return True

        missing: List[str] = []
        for dep in self.depends:
            # Clean version constraint: e.g. "glibc>=2.34" -> "glibc"
            clean_dep = re.split(r"[><=]", dep)[0].strip()
            res = subprocess.run(
                [pacman_bin, "-Q", clean_dep],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
            if res.returncode != 0:
                missing.append(dep)

        if missing:
            self.missing_deps = missing
            self._failure_string = f"Eksik bağımlılıklar: {', '.join(missing)}"
            return False

        self.missing_deps = []
        self._failure_string = ""
        return True
