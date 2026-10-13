#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Headless CLI inspection utilities for parslinux-package-installer.
Provides package metadata display and dependency checking without any GUI dependency.
"""

import os
import sys

from DebPackage import DebPackage


def get_version() -> str:
    """Retrieve package version from __version__ file or fallback."""
    ver_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "__version__")
    if os.path.exists(ver_file):
        try:
            with open(ver_file, "r", encoding="utf-8") as f:
                return f.readline().strip()
        except Exception:
            pass
    return "1.0.0"


def cli_info(deb_path: str) -> int:
    """Print formatted package metadata to terminal without launching GUI."""
    if not os.path.exists(deb_path):
        print(f"Hata: Dosya bulunamadı: {deb_path}", file=sys.stderr)
        return 1
    try:
        pkg = DebPackage(deb_path)
    except Exception as e:
        print(f"Hata: Paket okunamadı: {e}", file=sys.stderr)
        return 1

    installed_ver = pkg.get_installed_version()
    status_str = f"Kurulu ({installed_ver})" if installed_ver else "Kurulu Değil"

    raw_size = pkg.get("Installed-Size", "")
    size_str = f"{raw_size} KB" if raw_size else "-"

    print("=" * 60)
    print(f" Paket Adı        : {pkg.pkgname}")
    print(f" Sürüm (Version)  : {pkg.get('Version', '-')}")
    print(f" Mimari (Arch)    : {pkg.get('Architecture', '-')}")
    print(f" Durum (Status)   : {status_str}")
    print(f" Bölüm (Section)  : {pkg.get('Section', '-')}")
    print(f" Boyut (Size)     : {size_str}")
    print(f" Geliştirici      : {pkg.get('Maintainer', '-')}")
    if pkg.get("Homepage"):
        print(f" Web Sitesi       : {pkg.get('Homepage')}")
    print(f" Bağımlılıklar    : {pkg.get('Depends', '(Yok)')}")
    desc = pkg.get("Description", "").strip()
    if desc:
        print("-" * 60)
        print(f" Açıklama:\n{desc}")
    print("=" * 60)
    return 0


def cli_check(deb_path: str) -> int:
    """Check package dependencies and report status with exit code."""
    if not os.path.exists(deb_path):
        print(f"Hata: Dosya bulunamadı: {deb_path}", file=sys.stderr)
        return 1
    try:
        pkg = DebPackage(deb_path)
    except Exception as e:
        print(f"Hata: Paket okunamadı: {e}", file=sys.stderr)
        return 1

    ok = pkg.check()
    print(f"Paket: {pkg.pkgname} (v{pkg.get('Version', '-')})")
    if ok:
        print("✓ Bağımlılıklar: Tüm gereksinimler karşılanıyor, kurulabilir.")
        return 0
    else:
        print("✗ Bağımlılık Sorunu:", file=sys.stderr)
        if pkg.missing_deps:
            print(f"  Eksik Paketler: {', '.join(pkg.missing_deps)}", file=sys.stderr)
        if pkg._failure_string:
            print(f"  Hata Detayı: {pkg._failure_string}", file=sys.stderr)
        return 1
