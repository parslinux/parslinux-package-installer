#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, GLib

from MainWindow import MainWindow


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.parslinux.package-installer",
                         flags=Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE, **kwargs)
        self.window = None
        GLib.set_prgname("org.parslinux.package-installer")

    def do_activate(self):
        target_file = None
        if len(sys.argv) > 1:
            candidate = sys.argv[1]
            if not candidate.startswith("-") and os.path.exists(candidate) and candidate.lower().endswith(".deb"):
                target_file = Gio.File.new_for_path(os.path.abspath(candidate))

        if self.window is not None:
            if target_file:
                self.window.from_file(target_file.get_path())
            self.window.window.present()
        else:
            self.window = MainWindow(self, target_file)

    def do_open(self, files, filecount, hint):
        if filecount >= 1:
            file = files[0]
            path = file.get_path()
            if path and os.path.exists(path):
                if path.lower().endswith(".deb"):
                    if self.window is not None:
                        self.window.from_file(path)
                        self.window.window.present()
                    else:
                        self.window = MainWindow(self, file)
                else:
                    print(f"Error: Only .deb files are supported ({path}).")
            else:
                print(f"File does not exist: {path}")
        else:
            print("No files provided.")


if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)
