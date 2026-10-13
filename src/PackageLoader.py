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
    """Check whether the given path is a supported package format (.deb or .pkg.tar.*)."""
    if not isinstance(filepath, str):
        return False
    lower = filepath.lower()
    return lower.endswith(".deb") or is_arch_package(lower)


def open_package(filepath: str, cache: Any = None) -> Any:
    """Polymorphic factory function returning either DebPackage or ArchPackage."""
    if is_arch_package(filepath):
        return ArchPackage(filepath, cache=cache)
    return DebPackage(filepath, cache=cache)
