#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Headless CLI inspection utilities for parslinux-package-installer.
Provides package metadata display and dependency checking without any GUI dependency.
"""

import os
import sys
import tempfile
import urllib.parse
import urllib.request
from typing import Optional

from DebPackage import DebPackage
from PackageLoader import open_package, is_supported_package


def is_remote_url(target: str) -> bool:
    """Check if target string is an HTTP or HTTPS URL."""
    if not isinstance(target, str):
        return False
    parsed = urllib.parse.urlparse(target)
    return parsed.scheme in ("http", "https")


def download_remote_deb(url: str, progress_cb=None) -> str:
    """Download remote package (.deb or .pkg.tar.*) to a secure temporary file and return the path."""
    parsed = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed.path) or "downloaded_package.deb"
    if not is_supported_package(filename):
        filename += ".deb"

    fd, temp_path = tempfile.mkstemp(prefix="parslinux-pkg-", suffix="-" + filename)
    os.close(fd)

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 ParsLinuxPackageInstaller/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as response, open(temp_path, "wb") as out_file:
        total_size = response.headers.get("Content-Length")
        total_size = int(total_size) if total_size and total_size.isdigit() else None
        bytes_downloaded = 0
        chunk_size = 64 * 1024

        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            bytes_downloaded += len(chunk)
            if progress_cb and total_size:
                progress_cb(bytes_downloaded, total_size)

    return temp_path


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
    temp_file = None
    if is_remote_url(deb_path):
        print(f"Uzak paket indiriliyor: {deb_path} ...")
        try:
            deb_path = download_remote_deb(deb_path)
            temp_file = deb_path
        except Exception as e:
            print(f"Hata: Uzak paket indirilemedi: {e}", file=sys.stderr)
            return 1

    if not os.path.exists(deb_path):
        print(f"Hata: Dosya bulunamadı: {deb_path}", file=sys.stderr)
        return 1
    try:
        pkg = open_package(deb_path)
    except Exception as e:
        print(f"Hata: Paket okunamadı: {e}", file=sys.stderr)
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
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
    temp_file = None
    if is_remote_url(deb_path):
        print(f"Uzak paket indiriliyor: {deb_path} ...")
        try:
            deb_path = download_remote_deb(deb_path)
            temp_file = deb_path
        except Exception as e:
            print(f"Hata: Uzak paket indirilemedi: {e}", file=sys.stderr)
            return 1

    if not os.path.exists(deb_path):
        print(f"Hata: Dosya bulunamadı: {deb_path}", file=sys.stderr)
        return 1
    try:
        pkg = open_package(deb_path)
    except Exception as e:
        print(f"Hata: Paket okunamadı: {e}", file=sys.stderr)
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
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
