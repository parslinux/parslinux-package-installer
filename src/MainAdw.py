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
    app = ApplicationAdw()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
