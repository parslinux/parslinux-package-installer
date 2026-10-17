#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PackageLoader for parslinux-package-installer.
Provides universal package loading supporting both Debian (.deb) and Arch Linux (.pkg.tar.zst) packages.
"""

import os
import shutil
from typing import Any, Optional

from ArchPackage import ArchPackage, is_arch_package
from DebPackage import DebPackage
from RpmPackage import RpmPackage
from AppImagePackage import AppImagePackage
from FlatpakRefPackage import FlatpakRefPackage


def is_arch_system() -> bool:
    """Detect if the current operating system is Arch Linux or Arch-based."""
    if os.path.exists("/etc/arch-release"):
        return True
    if os.path.exists("/etc/os-release"):
        try:
            with open("/etc/os-release", "r", encoding="utf-8") as f:
                content = f.read().lower()
                if any(x in content for x in ("id=arch", "id_like=arch", "id=manjaro", "id=endeavouros", "id=garuda")):
                    return True
        except Exception:
            pass
    return bool(shutil.which("pacman")) and not bool(shutil.which("dpkg"))


def is_supported_package(filepath: str) -> bool:
    """Check whether the given path is a supported package format."""
    if not isinstance(filepath, str):
        return False
    lower = filepath.lower()
    return (
        lower.endswith(".deb")
        or lower.endswith(".rpm")
        or lower.endswith(".appimage")
        or lower.endswith(".flatpakref")
        or lower.endswith(".flatpakrepo")
        or is_arch_package(lower)
    )


def open_package(filepath: str, cache: Any = None) -> Any:
    """Polymorphic factory function returning the appropriate package handler class."""
    lower = filepath.lower()
    if is_arch_package(filepath):
        return ArchPackage(filepath, cache=cache)
    elif lower.endswith(".rpm"):
        return RpmPackage(filepath)
    elif lower.endswith(".appimage"):
        return AppImagePackage(filepath, cache=cache)
    elif lower.endswith(".flatpakref") or lower.endswith(".flatpakrepo"):
        return FlatpakRefPackage(filepath, cache=cache)
    return DebPackage(filepath, cache=cache)
