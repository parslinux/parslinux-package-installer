#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for parslinux-package-installer (GTK3 frontend).
"""

import argparse
import logging
import os
import sys
from typing import List

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, GLib

from MainWindow import MainWindow

logger = logging.getLogger("parslinux-package-installer")


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            application_id="org.parslinux.package-installer",
            flags=Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE,
            **kwargs
        )
        self.window = None
        GLib.set_prgname("org.parslinux.package-installer")

    def do_activate(self) -> None:
        target_files: List[str] = []
        for arg in sys.argv[1:]:
            if not arg.startswith("-") and os.path.exists(arg) and arg.lower().endswith(".deb"):
                target_files.append(os.path.abspath(arg))

        if self.window is not None:
            if len(target_files) == 1:
                self.window.from_file(target_files[0])
            elif len(target_files) > 1:
                self.window.open_batch(target_files)
            self.window.window.present()
        else:
            first_file = Gio.File.new_for_path(target_files[0]) if len(target_files) == 1 else None
            self.window = MainWindow(self, first_file)
            if len(target_files) > 1:
                self.window.open_batch(target_files)

    def do_open(self, files: List[Gio.File], filecount: int, hint: str) -> None:
        target_paths: List[str] = []
        for f in files:
            p = f.get_path()
            if p and os.path.exists(p) and p.lower().endswith(".deb"):
                target_paths.append(p)

        if self.window is None:
            first_file = files[0] if len(target_paths) == 1 else None
            self.window = MainWindow(self, first_file)

        if len(target_paths) == 1:
            self.window.from_file(target_paths[0])
            self.window.window.present()
        elif len(target_paths) > 1:
            self.window.open_batch(target_paths)
            self.window.window.present()
        else:
            self.window.window.present()


from cli import cli_info, cli_check


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="parslinux-package-installer",
        description="Pars Linux Deb Package Installer (GDebi Equivalent)"
    )
    parser.add_argument("files", nargs="*", help="Debian package files (.deb) to inspect or install")
    parser.add_argument("-i", "--info", metavar="DEB_FILE", help="Display package metadata in terminal without GUI")
    parser.add_argument("-c", "--check", metavar="DEB_FILE", help="Verify package dependencies in terminal (exit 0: ok, 1: missing)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logging")
    parser.add_argument("--version", action="store_true", help="Show program version and exit")
    parser.add_argument("--adw", "--gtk4", action="store_true", dest="adw", help="Launch in GTK 4 / Libadwaita mode")

    args, unknown = parser.parse_known_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )

    if args.version:
        ver = "1.0.0"
        ver_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "__version__")
        if os.path.exists(ver_file):
            try:
                with open(ver_file, "r", encoding="utf-8") as f:
                    ver = f.readline().strip()
            except Exception:
                pass
        print(f"Pars Linux Package Installer v{ver}")
        return 0

    if args.info:
        return cli_info(args.info)

    if args.check:
        return cli_check(args.check)

    if args.adw:
        import MainAdw
        return MainAdw.main()

    app = Application()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
