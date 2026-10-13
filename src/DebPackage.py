#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DebPackage handler for parslinux-package-installer.
Supports both native python-apt backend and standalone fallback deb parser.
Provides package metadata parsing, dependency verification, version comparison,
and detailed package file tree extraction.
"""

import io
import logging
import os
import re
import shutil
import subprocess
import tarfile
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("parslinux-debpackage")

HAVE_APT = False
try:
    import apt
    import apt.debfile as aptdeb
    HAVE_APT = True
except ImportError:
    HAVE_APT = False


class DebPackage:
    """Wrapper around Debian package inspection with python-apt and fallback support."""

    VERSION_NONE = 0
    VERSION_OUTDATED = 1
    VERSION_SAME = 2
    VERSION_NEWER = 3

    def __init__(self, filename: str, cache: Optional[Any] = None) -> None:
        self.filename: str = os.path.abspath(filename)
        if not os.path.isfile(self.filename):
            raise FileNotFoundError(f"File not found: {self.filename}")

        self.cache: Optional[Any] = cache
        self._apt_pkg: Optional[Any] = None
        self._sections: Dict[str, str] = {}
        self.pkgname: str = ""
        self._failure_string: str = ""
        self.missing_deps: List[str] = []
        self.required_changes: Dict[str, Any] = {}
        self.filelist: List[str] = []
        self._file_details: List[Dict[str, Any]] = []
        self._file_size_bytes: int = os.path.getsize(self.filename)

        if HAVE_APT:
            try:
                self._apt_pkg = aptdeb.DebPackage(self.filename, cache=self.cache)
                self.pkgname = self._apt_pkg.pkgname
                self._sections = dict(self._apt_pkg._sections)
            except Exception as e:
                logger.debug("python-apt failed for %s (%s); using fallback parser", self.filename, e)
                self._apt_pkg = None
                self._parse_deb_manually()
        else:
            self._parse_deb_manually()

    @staticmethod
    def _open_tar(content: bytes) -> tarfile.TarFile:
        """Open in-memory tar content with gzip, bz2, xz, and zstd fallback."""
        try:
            return tarfile.open(fileobj=io.BytesIO(content), mode="r:*")
        except Exception:
            try:
                p = subprocess.run(["zstd", "-d", "-c"], input=content, capture_output=True, check=False)
                if p.returncode == 0 and p.stdout:
                    return tarfile.open(fileobj=io.BytesIO(p.stdout), mode="r:")
            except Exception:
                pass
            raise

    def _parse_deb_manually(self) -> None:
        """Pure-python fallback to parse AR archive and extract debian control & file list."""
        control_content: Optional[str] = None
        file_list: List[str] = []

        with open(self.filename, "rb") as f:
            magic = f.read(8)
            if magic != b"!<arch>\n":
                raise ValueError(f"Invalid Debian package format (bad magic: {magic!r})")

            while True:
                hdr = f.read(60)
                if len(hdr) < 60:
                    break
                name = hdr[0:16].decode("latin1", errors="ignore").strip().rstrip("/")
                try:
                    size = int(hdr[48:58].decode("latin1", errors="ignore").strip())
                except ValueError:
                    break

                content = f.read(size)
                if size % 2 == 1:
                    f.read(1)  # Pad byte

                if name.startswith("control.tar"):
                    try:
                        with self._open_tar(content) as tar:
                            for member in tar.getmembers():
                                if member.name in ("./control", "control"):
                                    extracted = tar.extractfile(member)
                                    if extracted:
                                        control_content = extracted.read().decode("utf-8", errors="replace")
                    except Exception as e:
                        logger.warning("Error extracting control.tar in %s: %s", self.filename, e)

                elif name.startswith("data.tar"):
                    try:
                        with self._open_tar(content) as tar:
                            file_list = [m.name.lstrip(".") for m in tar.getmembers() if m.name not in (".", "./")]
                    except Exception as e:
                        logger.warning("Error reading data.tar in %s: %s", self.filename, e)

        if not control_content:
            raise ValueError(f"No control file found in Debian package: {self.filename}")

        self.filelist = sorted(file_list)
        self._sections = self._parse_control_rfc822(control_content)
        self.pkgname = self._sections.get("Package", "")

    @staticmethod
    def _parse_control_rfc822(text: str) -> Dict[str, str]:
        """Parse RFC822 Debian control file fields."""
        fields: Dict[str, str] = {}
        current_field: Optional[str] = None
        for line in text.splitlines():
            if line.startswith((" ", "\t")):
                if current_field:
                    fields[current_field] += "\n" + line.strip()
            elif ":" in line:
                key, val = line.split(":", 1)
                current_field = key.strip()
                fields[current_field] = val.strip()
            else:
                current_field = None
        return fields

    def __getitem__(self, key: str) -> str:
        return self._sections.get(key, "")

    def get(self, key: str, default: str = "") -> str:
        return self._sections.get(key, default)

    def check_architecture(self) -> Tuple[bool, str]:
        """Check if package architecture is compatible with the host system."""
        pkg_arch = self.get("Architecture", "").strip()
        if not pkg_arch or pkg_arch in ("all", "any"):
            return True, ""

        dpkg_bin = shutil.which("dpkg") or ("/usr/bin/dpkg" if os.path.exists("/usr/bin/dpkg") else None)
        if not dpkg_bin:
            return True, ""

        try:
            native = subprocess.check_output([dpkg_bin, "--print-architecture"], text=True, stderr=subprocess.DEVNULL).strip()
            if pkg_arch == native:
                return True, ""

            foreign = [l.strip() for l in subprocess.check_output([dpkg_bin, "--print-foreign-architectures"], text=True, stderr=subprocess.DEVNULL).splitlines() if l.strip()]
            if pkg_arch in foreign:
                return True, ""

            msg = f"Paket '{pkg_arch}' mimarisi gerektiriyor (Sistem: '{native}'). 'sudo dpkg --add-architecture {pkg_arch} && sudo apt update' komutunu çalıştırmayı deneyin."
            return False, msg
        except Exception as e:
            logger.debug("Architecture check failed: %s", e)
            return True, ""

    def check(self) -> bool:
        """Check if dependencies and architecture are satisfied."""
        arch_ok, arch_msg = self.check_architecture()
        if not arch_ok:
            self._failure_string = arch_msg
            return False

        if self._apt_pkg is not None:
            try:
                result = self._apt_pkg.check()
                self._failure_string = getattr(self._apt_pkg, "_failure_string", "")
                self.missing_deps = getattr(self._apt_pkg, "missing_deps", []) or []
                self.required_changes = getattr(self._apt_pkg, "required_changes", {}) or {}
                return bool(result)
            except Exception as e:
                self._failure_string = str(e)
                return False

        # Fallback check
        depends = self._sections.get("Depends", "")
        if not depends:
            return True

        # Check against installed packages via dpkg-query if available
        dep_items = [d.strip() for d in depends.split(",") if d.strip()]
        missing: List[str] = []
        for dep in dep_items:
            # Clean package name from version constraint: e.g. 'libc6 (>= 2.34)' -> 'libc6'
            pkg = re.split(r"[\s(]", dep)[0].strip()
            if not self._is_pkg_installed(pkg):
                # If pipe/alternative exists (e.g. 'default-jre | java8-runtime')
                if "|" in dep:
                    alts = [re.split(r"[\s(]", a)[0].strip() for a in dep.split("|")]
                    if any(self._is_pkg_installed(a) for a in alts):
                        continue
                missing.append(dep)

        if missing:
            # If dpkg isn't present, list info
            if not os.path.exists("/usr/bin/dpkg-query"):
                self.missing_deps = []
                self._failure_string = ""
                return True
            self.missing_deps = missing
            self._failure_string = f"Missing dependencies: {', '.join(missing)}"
            return False

        return True

    def _is_pkg_installed(self, pkgname: str) -> bool:
        """Check if package is installed in system."""
        if self.cache and pkgname in self.cache:
            try:
                return bool(self.cache[pkgname].is_installed)
            except Exception:
                pass

        if os.path.exists("/usr/bin/dpkg-query"):
            try:
                res = subprocess.run(
                    ["/usr/bin/dpkg-query", "-W", "-f=${Status}", pkgname],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    check=False
                )
                return "install ok installed" in res.stdout
            except Exception:
                pass
        return False

    def compare_to_version_in_cache(self) -> int:
        """Compare package version to installed version."""
        if self._apt_pkg is not None:
            try:
                return int(self._apt_pkg.compare_to_version_in_cache())
            except Exception:
                pass

        # Fallback version comparison
        installed_ver = self.get_installed_version()
        if not installed_ver:
            return self.VERSION_NONE

        target_ver = self._sections.get("Version", "")
        if not target_ver:
            return self.VERSION_NONE

        cmp_val = self._compare_debian_versions(target_ver, installed_ver)
        if cmp_val > 0:
            return self.VERSION_NEWER
        elif cmp_val < 0:
            return self.VERSION_OUTDATED
        else:
            return self.VERSION_SAME

    def get_installed_version(self) -> Optional[str]:
        """Get currently installed version of package."""
        if self.cache and self.pkgname in self.cache:
            try:
                pkg = self.cache[self.pkgname]
                if pkg.is_installed:
                    return str(pkg.installed.version)
            except Exception:
                pass

        if os.path.exists("/usr/bin/dpkg-query"):
            try:
                res = subprocess.run(
                    ["/usr/bin/dpkg-query", "-W", "-f=${Version}", self.pkgname],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    check=False
                )
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip()
            except Exception:
                pass
        return None

    @staticmethod
    def _compare_debian_versions(v1: str, v2: str) -> int:
        """Debian version comparison using dpkg if available or fallback."""
        if v1 == v2:
            return 0
        if os.path.exists("/usr/bin/dpkg"):
            try:
                res = subprocess.run(
                    ["/usr/bin/dpkg", "--compare-versions", v1, "gt", v2],
                    check=False
                )
                if res.returncode == 0:
                    return 1
                res2 = subprocess.run(
                    ["/usr/bin/dpkg", "--compare-versions", v1, "lt", v2],
                    check=False
                )
                if res2.returncode == 0:
                    return -1
                return 0
            except Exception:
                pass

        # Fallback lexical comparison
        return (v1 > v2) - (v1 < v2)

    def get_file_details(self) -> List[Dict[str, Any]]:
        """Get detailed metadata for all files in the package."""
        if hasattr(self, "_file_details") and self._file_details:
            return self._file_details
        self._file_details = []
        try:
            with open(self.filename, "rb") as f:
                f.seek(8)
                while True:
                    hdr = f.read(60)
                    if len(hdr) < 60:
                        break
                    name = hdr[0:16].decode("latin1", errors="ignore").strip().rstrip("/")
                    size = int(hdr[48:58].decode("latin1", errors="ignore").strip())
                    content = f.read(size)
                    if size % 2 == 1:
                        f.read(1)
                    if name.startswith("data.tar"):
                        with self._open_tar(content) as tar:
                            members = tar.getmembers()
                            details = []
                            for m in members:
                                if m.name in (".", "./"):
                                    continue
                                cname = m.name.lstrip(".")
                                if not cname.startswith("/"):
                                    cname = "/" + cname
                                is_dir = m.isdir()
                                is_sym = m.issym()
                                is_link = m.islnk()
                                is_exec = bool(m.mode & 0o111) if not is_dir else False
                                details.append({
                                    "name": cname,
                                    "size": m.size if not is_dir else 0,
                                    "is_dir": is_dir,
                                    "is_sym": is_sym or is_link,
                                    "is_exec": is_exec,
                                    "target": m.linkname if (is_sym or is_link) else "",
                                    "mode": oct(m.mode)
                                })
                            self._file_details = sorted(details, key=lambda x: x["name"])
                            self.filelist = [d["name"] for d in self._file_details]
                        break
        except Exception as e:
            logger.error("Error reading package files in %s: %s", self.filename, e)
        return self._file_details

    def get_file_list(self) -> List[str]:
        """Get the list of files in the package."""
        if self.filelist:
            return self.filelist
        self.get_file_details()
        return self.filelist
