#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AppImagePackage.py for parslinux-package-installer.
Provides inspection, desktop integration, and execution management for standalone Linux AppImage packages.
"""

import logging
import os
import re
import shutil
import stat
import subprocess
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("parslinux-appimage")


class AppImagePackage:
    """Manages metadata parsing, desktop menu integration, and execution for AppImage bundles."""

    def __init__(self, filepath: str, cache: Any = None) -> None:
        self.file_path = os.path.abspath(filepath)
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(f"AppImage file not found: {filepath}")

        self.metadata: Dict[str, str] = {}
        self._parse_appimage()

    def _parse_appimage(self) -> None:
        """Extract metadata from AppImage filename, size, and ELF header."""
        filename = os.path.basename(self.file_path)
        raw_name = re.sub(r"\.appimage$", "", filename, flags=re.IGNORECASE)

        # Name and version heuristics from filename: e.g. Cursor-0.40.4-x86_64.AppImage
        version = "1.0.0"
        arch = "x86_64"

        # Check architecture from ELF binary header (bytes 4-5)
        try:
            with open(self.file_path, "rb") as f:
                header = f.read(20)
                if len(header) >= 19 and header[:4] == b"\x7fELF":
                    e_machine = header[18] | (header[19] << 8)
                    if e_machine == 0x3E:
                        arch = "x86_64"
                    elif e_machine == 0x03:
                        arch = "i386"
                    elif e_machine == 0xB7:
                        arch = "aarch64"
                    elif e_machine == 0x28:
                        arch = "armv7l"
        except Exception as e:
            logger.debug("Could not read ELF header: %s", e)

        # Remove architecture suffix before regex: e.g. -x86_64, _amd64
        clean_stem = re.sub(r"[-_](x86_64|amd64|aarch64|arm64|i386|x86)$", "", raw_name, flags=re.IGNORECASE)
        v_match = re.search(r"[-_]v?(\d+(\.\d+)*)$", clean_stem)
        if v_match:
            version = v_match.group(1)
            pkgname = clean_stem[:v_match.start()].strip("-_")
        else:
            v_match = re.search(r"[-_]v?(\d+(\.\d+)+)", clean_stem)
            if v_match:
                version = v_match.group(1)
                pkgname = clean_stem[:v_match.start()].strip("-_")
            else:
                pkgname = clean_stem

        pkgname = pkgname.replace("_", "-").strip("-")
        if not pkgname:
            pkgname = "appimage-application"

        file_size_kb = str(os.path.getsize(self.file_path) // 1024)

        self.pkgname = pkgname.lower()
        self.display_name = pkgname.replace("-", " ").title()

        self.metadata = {
            "Package": self.pkgname,
            "Version": version,
            "Architecture": arch,
            "Section": "AppImage / Portable",
            "Installed-Size": file_size_kb,
            "Maintainer": "AppImage Packager",
            "Homepage": "https://appimage.org",
            "Description": (
                f"{self.display_name} (AppImage Taşınabilir Paket)\n"
                f"Bağımsız, taşınabilir ve sistem kütüphanelerinden yalıtılmış tek dosyalı Linux uygulaması.\n"
                f"Konum: {self.file_path}"
            )
        }

    @property
    def missing_deps(self) -> List[str]:
        return []

    @property
    def _failure_string(self) -> str:
        return ""

    def check(self) -> bool:
        """AppImages bundle all required libraries, dependency check passes."""
        return True

    def get(self, field_name: str, default: Any = "") -> str:
        """Retrieve a metadata field value."""
        return self.metadata.get(field_name, default)

    @property
    def desktop_file_path(self) -> str:
        """Target path for desktop menu entry in user's applications folder."""
        apps_dir = os.path.expanduser("~/.local/share/applications")
        return os.path.join(apps_dir, f"appimage-{self.pkgname}.desktop")

    def is_integrated(self) -> bool:
        """Check if desktop entry exists for this AppImage."""
        return os.path.isfile(self.desktop_file_path)

    def compare_to_version_in_cache(self) -> int:
        """
        Status check:
        0: Not integrated into application menu
        2: Already integrated into application menu
        """
        return 2 if self.is_integrated() else 0

    def get_installed_version(self) -> Optional[str]:
        """Return installed/integrated version if .desktop exists."""
        if self.is_integrated():
            return self.get("Version")
        return None

    def check_dependencies(self) -> Tuple[int, List[str]]:
        """AppImages bundle their own dependencies; always return satisfied (0)."""
        return 0, []

    def get_file_details(self) -> List[Dict[str, Any]]:
        """List AppImage binary file details."""
        mode = os.stat(self.file_path).st_mode
        perms = stat.filemode(mode)
        size_bytes = os.path.getsize(self.file_path)

        return [{
            "path": self.file_path,
            "name": os.path.basename(self.file_path),
            "size": size_bytes,
            "mode": perms,
            "is_dir": False,
            "is_sym": False,
            "is_exec": bool(mode & stat.S_IXUSR),
            "type": "executable" if (mode & stat.S_IXUSR) else "file",
            "icon": "application-x-executable"
        }]

    def integrate_desktop(self) -> Tuple[bool, str]:
        """
        Make AppImage executable and create a ~/.local/share/applications/ entry.
        """
        try:
            # 1. Ensure executable permission
            current_mode = os.stat(self.file_path).st_mode
            os.chmod(self.file_path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

            # 2. Prepare user applications directory
            apps_dir = os.path.expanduser("~/.local/share/applications")
            os.makedirs(apps_dir, exist_ok=True)

            # 3. Create .desktop file
            desktop_content = f"""[Desktop Entry]
Type=Application
Name={self.display_name}
Comment={self.display_name} AppImage Portable Application
Exec="{self.file_path}" %U
Icon=application-x-executable
Terminal=false
Categories=Utility;Application;
StartupNotify=true
X-AppImage-Version={self.get("Version")}
"""
            with open(self.desktop_file_path, "w", encoding="utf-8") as f:
                f.write(desktop_content)

            # 4. Refresh desktop database if command available
            if shutil.which("update-desktop-database"):
                subprocess.run(
                    ["update-desktop-database", apps_dir],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False
                )

            return True, f"'{self.display_name}' başarıyla sistem uygulama menüsüne eklendi."
        except Exception as e:
            logger.error("Failed to integrate AppImage: %s", e)
            return False, str(e)

    def remove_desktop(self) -> Tuple[bool, str]:
        """Remove desktop entry and integration."""
        try:
            if os.path.isfile(self.desktop_file_path):
                os.remove(self.desktop_file_path)

            apps_dir = os.path.expanduser("~/.local/share/applications")
            if shutil.which("update-desktop-database"):
                subprocess.run(
                    ["update-desktop-database", apps_dir],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False
                )
            return True, f"'{self.display_name}' uygulama menüsünden kaldırıldı."
        except Exception as e:
            logger.error("Failed to remove AppImage integration: %s", e)
            return False, str(e)

    def launch(self) -> Tuple[bool, str]:
        """Launch the AppImage in background."""
        try:
            current_mode = os.stat(self.file_path).st_mode
            os.chmod(self.file_path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            subprocess.Popen([self.file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"'{self.display_name}' başlatıldı."
        except Exception as e:
            return False, str(e)
