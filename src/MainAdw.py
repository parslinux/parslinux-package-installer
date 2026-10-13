#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gio, GLib, Adw

from MainWindowAdw import MainWindowAdw


class ApplicationAdw(Adw.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.parslinux.package-installer",
                         flags=Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE, **kwargs)
        self.window = None
        GLib.set_prgname("org.parslinux.package-installer")

    def do_activate(self):
        target_files = []
        for arg in sys.argv[1:]:
            if not arg.startswith("-") and os.path.exists(arg) and arg.lower().endswith(".deb"):
                target_files.append(os.path.abspath(arg))

        if self.window is None:
            first_file = target_files[0] if len(target_files) == 1 else None
            self.window = MainWindowAdw(self, first_file)

        if len(target_files) == 1:
            self.window.from_file(target_files[0])
        elif len(target_files) > 1:
            self.window.open_batch(target_files)

        self.window.present()

    def do_open(self, files, filecount, hint):
        target_paths = []
        for f in files:
            p = f.get_path()
            if p and os.path.exists(p) and p.lower().endswith(".deb"):
                target_paths.append(p)

        if self.window is None:
            first_file = target_paths[0] if len(target_paths) == 1 else None
            self.window = MainWindowAdw(self, first_file)

        if len(target_paths) == 1:
            self.window.from_file(target_paths[0])
        elif len(target_paths) > 1:
            self.window.open_batch(target_paths)

        self.window.present()


def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog="parslinux-package-installer-adw",
        description="Pars Linux Deb Package Installer (GTK 4 / Libadwaita Interface)"
    )
    parser.add_argument("files", nargs="*", help="Debian package files (.deb) to inspect or install")
    parser.add_argument("-i", "--info", metavar="DEB_FILE", help="Display package metadata in terminal without GUI")
    parser.add_argument("-c", "--check", metavar="DEB_FILE", help="Verify package dependencies in terminal (exit 0: ok, 1: missing)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logging")
    parser.add_argument("--version", action="store_true", help="Show program version and exit")

    args, unknown = parser.parse_known_args()

    if args.version:
        ver = "1.0.0"
        ver_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "__version__")
        if os.path.exists(ver_file):
            try:
                with open(ver_file, "r", encoding="utf-8") as f:
                    ver = f.readline().strip()
            except Exception:
                pass
        print(f"Pars Linux Package Installer (Adw) v{ver}")
        return 0

    if args.info:
        from cli import cli_info
        return cli_info(args.info)

    if args.check:
        from cli import cli_check
        return cli_check(args.check)

    app = ApplicationAdw()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
