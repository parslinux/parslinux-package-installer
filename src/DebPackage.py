#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DebPackage handler for parslinux-package-installer.
Supports both native python-apt backend and standalone fallback deb parser.
"""

import io
import os
import re
import subprocess
import tarfile

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

    def __init__(self, filename, cache=None):
        self.filename = os.path.abspath(filename)
        if not os.path.isfile(self.filename):
            raise FileNotFoundError(f"File not found: {self.filename}")

        self.cache = cache
        self._apt_pkg = None
        self._sections = {}
        self.pkgname = ""
        self._failure_string = ""
        self.missing_deps = []
        self.required_changes = {}
        self.filelist = []
        self._file_size_bytes = os.path.getsize(self.filename)

        if HAVE_APT:
            try:
                self._apt_pkg = aptdeb.DebPackage(self.filename, cache=self.cache)
                self.pkgname = self._apt_pkg.pkgname
                self._sections = dict(self._apt_pkg._sections)
            except Exception as e:
                # Fallback to internal parser if python-apt fails on this specific deb file
                self._apt_pkg = None
                self._parse_deb_manually()
        else:
            self._parse_deb_manually()

    def _parse_deb_manually(self):
        """Pure-python fallback to parse AR archive and extract debian control & file list."""
        control_content = None
        file_list = []

        with open(self.filename, "rb") as f:
            magic = f.read(8)
            if magic != b"!<arch>\n":
                raise ValueError(f"Invalid Debian package format (bad magic: {magic})")

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
                        with tarfile.open(fileobj=io.BytesIO(content), mode="r:*") as tar:
                            for member in tar.getmembers():
                                if member.name in ("./control", "control"):
                                    extracted = tar.extractfile(member)
                                    if extracted:
                                        control_content = extracted.read().decode("utf-8", errors="replace")
                    except Exception as e:
                        print(f"Warning extracting control.tar: {e}")

                elif name.startswith("data.tar"):
                    try:
                        with tarfile.open(fileobj=io.BytesIO(content), mode="r:*") as tar:
                            file_list = [m.name.lstrip(".") for m in tar.getmembers() if m.name not in (".", "./")]
                    except Exception as e:
                        print(f"Warning reading data.tar: {e}")

        if not control_content:
            raise ValueError("No control file found in Debian package.")

        self.filelist = sorted(file_list)
        self._sections = self._parse_control_rfc822(control_content)
        self.pkgname = self._sections.get("Package", "")

    @staticmethod
    def _parse_control_rfc822(text):
        """Parse RFC822 Debian control file fields."""
        fields = {}
        current_field = None
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

    def __getitem__(self, key):
        return self._sections.get(key, "")

    def get(self, key, default=""):
        return self._sections.get(key, default)

    def check(self):
        """Check if dependencies are satisfied."""
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
        missing = []
        for dep in dep_items:
            # Clean package name from version constraint: e.g. "libc6 (>= 2.34)" -> "libc6"
            pkg = re.split(r"[\s(]", dep)[0].strip()
            if not self._is_pkg_installed(pkg):
                # If pipe/alternative exists (e.g. "default-jre | java8-runtime")
                if "|" in dep:
                    alts = [re.split(r"[\s(]", a)[0].strip() for a in dep.split("|")]
                    if any(self._is_pkg_installed(a) for a in alts):
                        continue
                missing.append(dep)

        if missing:
            # If dpkg isn't present (e.g. non-Debian host), we don't hard-block, but list info
            if not os.path.exists("/usr/bin/dpkg-query"):
                self.missing_deps = []
                self._failure_string = ""
                return True
            self.missing_deps = missing
            self._failure_string = f"Missing dependencies: {', '.join(missing)}"
            return False

        return True

    def _is_pkg_installed(self, pkgname):
        """Check if package is installed in system."""
        if self.cache and pkgname in self.cache:
            try:
                return self.cache[pkgname].is_installed
            except Exception:
                pass

        if os.path.exists("/usr/bin/dpkg-query"):
            try:
                res = subprocess.run(
                    ["/usr/bin/dpkg-query", "-W", "-f=${Status}", pkgname],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True
                )
                return "install ok installed" in res.stdout
            except Exception:
                pass
        return False

    def compare_to_version_in_cache(self):
        """Compare package version to installed version."""
        if self._apt_pkg is not None:
            try:
                return self._apt_pkg.compare_to_version_in_cache()
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

    def get_installed_version(self):
        """Get currently installed version of package."""
        if self.cache and self.pkgname in self.cache:
            try:
                pkg = self.cache[self.pkgname]
                if pkg.is_installed:
                    return pkg.installed.version
            except Exception:
                pass

        if os.path.exists("/usr/bin/dpkg-query"):
            try:
                res = subprocess.run(
                    ["/usr/bin/dpkg-query", "-W", "-f=${Version}", self.pkgname],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True
                )
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip()
            except Exception:
                pass
        return None

    @staticmethod
    def _compare_debian_versions(v1, v2):
        """Debian version comparison using dpkg if available or fallback."""
        if v1 == v2:
            return 0
        if os.path.exists("/usr/bin/dpkg"):
            try:
                res = subprocess.run(
                    ["/usr/bin/dpkg", "--compare-versions", v1, "gt", v2]
                )
                if res.returncode == 0:
                    return 1
                res2 = subprocess.run(
                    ["/usr/bin/dpkg", "--compare-versions", v1, "lt", v2]
                )
                if res2.returncode == 0:
                    return -1
                return 0
            except Exception:
                pass

        # Fallback lexical comparison
        return (v1 > v2) - (v1 < v2)

    def get_file_details(self):
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
                        with tarfile.open(fileobj=io.BytesIO(content), mode="r:*") as tar:
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
            print(f"Error reading package files: {e}")
        return self._file_details

    def get_file_list(self):
        """Get the list of files in the package."""
        if self.filelist:
            return self.filelist
        self.get_file_details()
        return self.filelist
