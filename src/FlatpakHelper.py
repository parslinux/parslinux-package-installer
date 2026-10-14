#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlatpakHelper.py for parslinux-package-installer.
Provides Flathub integration for finding and recommending sandbox alternatives
when native distro packages have broken dependencies or conflict with the host.
"""

import logging
import re
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("parslinux-flatpak")


class FlatpakHelper:
    """Manages searching and recommending Flatpak / Flathub application alternatives."""

    @classmethod
    def is_available(cls) -> bool:
        """Check if flatpak binary is installed and operational."""
        return shutil.which("flatpak") is not None

    @classmethod
    def search_flatpak(cls, query: str) -> List[Dict[str, str]]:
        """
        Search Flathub repositories for applications matching the query string.
        Returns list of application metadata dictionaries.
        """
        if not cls.is_available() or not query:
            return []

        clean_query = re.sub(r"[^\w\.-]", "", query).strip()
        if not clean_query:
            return []

        cmd = [
            "flatpak", "search",
            "--columns=application:f,name:f,version:f,desc:f",
            clean_query
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10, check=False)
            if res.returncode != 0:
                return []

            results = []
            for line in res.stdout.strip().split("\n"):
                parts = line.split("\t")
                if len(parts) >= 2:
                    app_id = parts[0].strip()
                    name = parts[1].strip()
                    version = parts[2].strip() if len(parts) > 2 else ""
                    desc = parts[3].strip() if len(parts) > 3 else ""

                    if not app_id or app_id == "Uygulama Kimliği" or app_id == "Application ID":
                        continue

                    results.append({
                        "app_id": app_id,
                        "name": name,
                        "version": version,
                        "description": desc,
                        "install_cmd": f"flatpak install flathub {app_id}"
                    })
            return results
        except Exception as e:
            logger.debug("Flatpak search error: %s", e)
            return []

    @classmethod
    def find_alternative(cls, package_name: str) -> Optional[Dict[str, str]]:
        """
        Find the single best matching Flatpak alternative for a native package name.
        Normalizes package names (strips -bin, -git, -deb suffixes).
        """
        if not package_name:
            return None

        # Clean common package naming affixes: vlc-bin -> vlc, code-oss -> code
        normalized = re.sub(r"-(bin|git|deb|rpm|desktop|stable|beta)$", "", package_name.lower().strip())
        results = cls.search_flatpak(normalized)
        if not results:
            results = cls.search_flatpak(package_name)

        if not results:
            return None

        # 1. Exact match on app_id suffix or name
        for r in results:
            app_id_lower = r["app_id"].lower()
            name_lower = r["name"].lower()
            if app_id_lower.endswith(f".{normalized}") or app_id_lower == normalized or name_lower == normalized:
                return r

        # 2. Filter out plugins/extensions and return first primary app
        for r in results:
            if ".Plugin." not in r["app_id"] and ".Extension." not in r["app_id"]:
                return r

        return results[0]

    @classmethod
    def install_flatpak(cls, app_id: str) -> Tuple[bool, str]:
        """Install a flatpak application using user or system scope."""
        if not cls.is_available():
            return False, "Sistemde 'flatpak' komutu bulunamadı."

        cmd = ["flatpak", "install", "-y", "flathub", app_id]
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            output = (proc.stdout + "\n" + proc.stderr).strip()
            return (proc.returncode == 0), output
        except Exception as e:
            return False, str(e)
