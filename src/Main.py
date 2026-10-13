#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for parslinux-package-installer.
Modern GTK 4 & Libadwaita primary user interface with headless CLI inspection.
"""

import argparse
import logging
import os
import sys
from typing import Any, List, Optional

from cli import cli_check, cli_info, cli_snapshot_status, get_version, is_remote_url, download_remote_deb
from PackageLoader import is_supported_package

logger = logging.getLogger("parslinux-package-installer")


def _get_application_class() -> Any:
    """Lazily load GTK4 and Libadwaita and return ApplicationAdw class."""
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Adw, Gio, GLib
    from MainWindowAdw import MainWindowAdw

    class ApplicationAdw(Adw.Application):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(
                *args,
                application_id="org.parslinux.package-installer",
                flags=Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE,
                **kwargs
            )
            self.window: Optional[MainWindowAdw] = None
            GLib.set_prgname("org.parslinux.package-installer")

        def do_activate(self) -> None:
            target_files: List[str] = []
            for arg in sys.argv[1:]:
                if arg.startswith("-"):
                    continue
                if is_remote_url(arg):
                    try:
                        downloaded = download_remote_deb(arg)
                        target_files.append(downloaded)
                    except Exception as e:
                        logger.error("Failed to download remote deb %s: %s", arg, e)
                elif os.path.exists(arg) and is_supported_package(arg):
                    target_files.append(os.path.abspath(arg))

            if self.window is None:
                first_file = target_files[0] if len(target_files) == 1 else None
                self.window = MainWindowAdw(self, first_file)

            if len(target_files) == 1:
                self.window.from_file(target_files[0])
            elif len(target_files) > 1:
                self.window.open_batch(target_files)

            self.window.present()

        def do_open(self, files: List[Gio.File], filecount: int, hint: str) -> None:
            target_paths: List[str] = []
            for f in files:
                p = f.get_path()
                if p and os.path.exists(p) and is_supported_package(p):
                    target_paths.append(p)

            if self.window is None:
                first_file = target_paths[0] if len(target_paths) == 1 else None
                self.window = MainWindowAdw(self, first_file)

            if len(target_paths) == 1:
                self.window.from_file(target_paths[0])
            elif len(target_paths) > 1:
                self.window.open_batch(target_paths)

            self.window.present()

    return ApplicationAdw


def __getattr__(name: str) -> Any:
    if name in ("Application", "ApplicationAdw"):
        return _get_application_class()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="parslinux-package-installer",
        description="Pars Linux Package Installer (GTK 4 / Libadwaita Interface)"
    )
    parser.add_argument("files", nargs="*", help="Package files (.deb, .pkg.tar.*) to inspect or install")
    parser.add_argument("-i", "--info", metavar="PKG_FILE", help="Display package metadata in terminal without GUI")
    parser.add_argument("-c", "--check", metavar="PKG_FILE", help="Verify package dependencies in terminal (exit 0: ok, 1: missing)")
    parser.add_argument("--snapshot-status", action="store_true", help="Display system snapshot (Timeshift/Snapper/Btrfs) status and exit")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logging")
    parser.add_argument("--version", action="store_true", help="Show program version and exit")
    parser.add_argument("--adw", "--gtk4", action="store_true", dest="adw", help="Modern Libadwaita mode (default)")

    args, unknown = parser.parse_known_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )

    if args.adw:
        if '--adw' in sys.argv:
            sys.argv.remove('--adw')
        if '--gtk4' in sys.argv:
            sys.argv.remove('--gtk4')
        import MainAdw
        return MainAdw.main()

    if args.version:
        print(f"Pars Linux Package Installer v{get_version()}")
        return 0

    if args.snapshot_status:
        return cli_snapshot_status()

    if args.info:
        return cli_info(args.info)

    if args.check:
        return cli_check(args.check)

    app_cls = _get_application_class()
    app = app_cls()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
