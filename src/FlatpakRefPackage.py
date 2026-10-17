#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlatpakRefPackage.py for parslinux-package-installer.
Provides inspection, repository addition, and one-click installation for .flatpakref and .flatpakrepo files.
"""

import configparser
import logging
import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("parslinux-flatpakref")


class FlatpakRefPackage:
    """Manages metadata parsing and installation of .flatpakref and .flatpakrepo files."""

    def __init__(self, filepath: str, cache: Any = None) -> None:
        self.file_path = os.path.abspath(filepath)
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(f"Flatpak ref file not found: {filepath}")

        self.is_repo = self.file_path.lower().endswith(".flatpakrepo")
        self.metadata: Dict[str, str] = {}
        self._parse_file()

    def _parse_file(self) -> None:
        """Parse INI format of .flatpakref or .flatpakrepo."""
        config = configparser.ConfigParser(interpolation=None)
        try:
            config.read(self.file_path, encoding="utf-8")
        except Exception as e:
            logger.error("Failed to parse flatpak ref file: %s", e)
            raise ValueError(f"Geçersiz Flatpak dosyası: {e}")

        if self.is_repo:
            section_name = "Flatpak Repo"
            if not config.has_section(section_name):
                # Fallback to first section
                sections = config.sections()
                section_name = sections[0] if sections else ""

            title = config.get(section_name, "Title", fallback="Flathub Repository")
            url = config.get(section_name, "Url", fallback="-")
            homepage = config.get(section_name, "Homepage", fallback="https://flathub.org")
            comment = config.get(section_name, "Comment", fallback="Flatpak Yazılım Deposu")
            desc = config.get(section_name, "Description", fallback=comment)

            self.pkgname = title.lower().replace(" ", "-")
            self.display_name = title
            self.app_id = self.pkgname
            self.url = url

            self.metadata = {
                "Package": self.pkgname,
                "Version": "Repo",
                "Architecture": "all",
                "Section": "Flatpak / Depo",
                "Installed-Size": "1",
                "Maintainer": "Flathub Community",
                "Homepage": homepage,
                "Description": f"{title}\n{desc}\nDepo URL: {url}"
            }
        else:
            section_name = "Flatpak Ref"
            if not config.has_section(section_name):
                sections = config.sections()
                section_name = sections[0] if sections else ""

            name = config.get(section_name, "Name", fallback="org.flatpak.App")
            title = config.get(section_name, "Title", fallback=name.split(".")[-1].capitalize())
            branch = config.get(section_name, "Branch", fallback="stable")
            url = config.get(section_name, "Url", fallback="https://flathub.org")
            comment = config.get(section_name, "Comment", fallback="Flatpak Sandbox Uygulaması")
            desc = config.get(section_name, "Description", fallback=comment)
            homepage = config.get(section_name, "Homepage", fallback=url)

            self.pkgname = name
            self.display_name = title
            self.app_id = name
            self.branch = branch

            file_size_kb = str(max(1, os.path.getsize(self.file_path) // 1024))

            self.metadata = {
                "Package": name,
                "Version": branch,
                "Architecture": "all",
                "Section": "Flatpak / Flathub",
                "Installed-Size": file_size_kb,
                "Maintainer": "Flathub Packager",
                "Homepage": homepage,
                "Description": f"{title} ({name})\n{desc}\nDal: {branch}\nDepo: {url}"
            }

    def get(self, field_name: str, default: Any = "") -> str:
        return self.metadata.get(field_name, default)

    def is_installed(self) -> bool:
        """Check if application or repo is installed on host."""
        if not shutil.which("flatpak"):
            return False

        try:
            if self.is_repo:
                proc = subprocess.run(
                    ["flatpak", "remotes"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                return self.pkgname in proc.stdout.lower() or self.display_name.lower() in proc.stdout.lower()
            else:
                proc = subprocess.run(
                    ["flatpak", "info", self.app_id],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                return proc.returncode == 0
        except Exception:
            return False

    def compare_to_version_in_cache(self) -> int:
        """
        0: Ready to install
        2: Already installed
        """
        return 2 if self.is_installed() else 0

    def get_installed_version(self) -> Optional[str]:
        if not self.is_installed():
            return None
        if self.is_repo:
            return "Aktif Depo"

        try:
            proc = subprocess.run(
                ["flatpak", "info", "--show-version", self.app_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            v = proc.stdout.strip()
            return v if v else self.get("Version")
        except Exception:
            return self.get("Version")

    @property
    def missing_deps(self) -> List[str]:
        code, missing = self.check_dependencies()
        return missing

    @property
    def _failure_string(self) -> str:
        return "Sistemde 'flatpak' kurulu değil." if not shutil.which("flatpak") else ""

    def check(self) -> bool:
        """Verify flatpak command availability for CLI check."""
        code, _ = self.check_dependencies()
        return code == 0

    def check_dependencies(self) -> Tuple[int, List[str]]:
        """Verify flatpak command availability."""
        if not shutil.which("flatpak"):
            return 1, ["flatpak (Sistemde flatpak kurulu değil)"]
        return 0, []

    def get_file_details(self) -> List[Dict[str, Any]]:
        size_bytes = os.path.getsize(self.file_path)
        return [{
            "path": self.file_path,
            "name": os.path.basename(self.file_path),
            "size": size_bytes,
            "mode": "-rw-r--r--",
            "is_dir": False,
            "is_sym": False,
            "is_exec": False,
            "type": "file",
            "icon": "application-x-addon" if self.is_repo else "package-x-generic"
        }]

    def install(self) -> Tuple[bool, str]:
        """Install application from .flatpakref or add repository from .flatpakrepo."""
        if not shutil.which("flatpak"):
            return False, "Sisteminizde 'flatpak' kurulu değil. Lütfen önce flatpak paketini yükleyin."

        try:
            if self.is_repo:
                cmd = ["flatpak", "remote-add", "--if-not-exists", "--user", self.pkgname, self.file_path]
            else:
                cmd = ["flatpak", "install", "--user", "-y", "--from", self.file_path]

            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            output = (proc.stdout + "\n" + proc.stderr).strip()
            return (proc.returncode == 0), output
        except Exception as e:
            return False, str(e)

    def remove(self) -> Tuple[bool, str]:
        """Uninstall application or remove remote repository."""
        if not shutil.which("flatpak"):
            return False, "'flatpak' kurulu değil."

        try:
            if self.is_repo:
                cmd = ["flatpak", "remote-delete", "--user", "-y", self.pkgname]
            else:
                cmd = ["flatpak", "uninstall", "--user", "-y", self.app_id]

            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            output = (proc.stdout + "\n" + proc.stderr).strip()
            return (proc.returncode == 0), output
        except Exception as e:
            return False, str(e)
