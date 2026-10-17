#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI integration tests for Pars Linux Package Installer (Pure GTK 4 / Libadwaita).
"""

import os
import subprocess
import sys
import unittest


class TestGuiIntegrations(unittest.TestCase):
    def test_gtk4_adw_window(self):
        """Verify opening Debian package in Libadwaita window."""
        sub_code = (
            "import sys, os, gi\n"
            "sys.path.insert(0, os.path.abspath('src'))\n"
            "gi.require_version('Gtk', '4.0')\n"
            "gi.require_version('Adw', '1')\n"
            "from gi.repository import Adw\n"
            "from MainWindowAdw import MainWindowAdw\n"
            "app = Adw.Application(application_id='org.parslinux.test.adw_deb')\n"
            "fixture = os.path.abspath('tests/fixtures/parslinux-editor_2.0.0_all.deb')\n"
            "def on_act(app):\n"
            "    win = MainWindowAdw(app, fixture)\n"
            "    assert win.lbl_pkgname.get_label() == 'parslinux-editor'\n"
            "    assert len(win.file_items) == 11\n"
            "    app.quit()\n"
            "app.connect('activate', on_act)\n"
            "app.run([])\n"
        )
        res = subprocess.run([sys.executable, "-c", sub_code], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"GTK4 Debian window test failed: {res.stderr}")

    def test_gtk4_adw_arch_package(self):
        """Verify opening Arch Linux package (.pkg.tar.zst) in Libadwaita window."""
        sub_code = (
            "import sys, os, gi\n"
            "sys.path.insert(0, os.path.abspath('src'))\n"
            "gi.require_version('Gtk', '4.0')\n"
            "gi.require_version('Adw', '1')\n"
            "from gi.repository import Adw\n"
            "from MainWindowAdw import MainWindowAdw\n"
            "app = Adw.Application(application_id='org.parslinux.test.adw_arch')\n"
            "fixture = os.path.abspath('tests/fixtures/parslinux-arch-hello-1.0.0-1-any.pkg.tar.zst')\n"
            "def on_act(app):\n"
            "    win = MainWindowAdw(app, fixture)\n"
            "    assert win.lbl_pkgname.get_label() == 'parslinux-arch-hello'\n"
            "    assert win.package.get('Version') == '1.0.0-1'\n"
            "    app.quit()\n"
            "app.connect('activate', on_act)\n"
            "app.run([])\n"
        )
        res = subprocess.run([sys.executable, "-c", sub_code], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"GTK4 Arch package test failed: {res.stderr}")

    def test_main_entrypoint(self):
        """Verify Main.py initializes ApplicationAdw without GTK3 dependencies."""
        sub_code = (
            "import sys, os\n"
            "sys.path.insert(0, os.path.abspath('src'))\n"
            "import Main\n"
            "app_cls = Main._get_application_class()\n"
            "assert app_cls.__name__ == 'ApplicationAdw'\n"
        )
        res = subprocess.run([sys.executable, "-c", sub_code], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Main.py entrypoint check failed: {res.stderr}")

    def test_gtk4_adw_rpm_package(self):
        """Verify opening RPM package (.rpm) in Libadwaita window."""
        sub_code = (
            "import sys, os, gi\n"
            "sys.path.insert(0, os.path.abspath('src'))\n"
            "gi.require_version('Gtk', '4.0')\n"
            "gi.require_version('Adw', '1')\n"
            "from gi.repository import Adw\n"
            "from MainWindowAdw import MainWindowAdw\n"
            "app = Adw.Application(application_id='org.parslinux.test.adw_rpm')\n"
            "fixture = os.path.abspath('tests/fixtures/parslinux-fedora-hello-2.2.0-1.x86_64.rpm')\n"
            "def on_act(app):\n"
            "    win = MainWindowAdw(app, fixture)\n"
            "    assert win.lbl_pkgname.get_label() == 'parslinux-fedora-hello'\n"
            "    assert win.package.get('Version') == '2.2.0-1'\n"
            "    assert len(win.file_items) == 3\n"
            "    app.quit()\n"
            "app.connect('activate', on_act)\n"
            "app.run([])\n"
        )
        res = subprocess.run([sys.executable, "-c", sub_code], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"GTK4 RPM package test failed: {res.stderr}")

    def test_gtk4_adw_appimage(self):
        """Verify opening AppImage (.AppImage) in Libadwaita window."""
        sub_code = (
            "import sys, os, gi\n"
            "sys.path.insert(0, os.path.abspath('src'))\n"
            "gi.require_version('Gtk', '4.0')\n"
            "gi.require_version('Adw', '1')\n"
            "from gi.repository import Adw\n"
            "from MainWindowAdw import MainWindowAdw\n"
            "app = Adw.Application(application_id='org.parslinux.test.adw_appimage')\n"
            "fixture = os.path.abspath('tests/fixtures/sample-app-1.0.0-x86_64.AppImage')\n"
            "def on_act(app):\n"
            "    win = MainWindowAdw(app, fixture)\n"
            "    assert win.lbl_pkgname.get_label() == 'sample-app'\n"
            "    assert win.package.get('Version') == '1.0.0'\n"
            "    assert win.btn_install.get_label() == 'Menüye Ekle'\n"
            "    app.quit()\n"
            "app.connect('activate', on_act)\n"
            "app.run([])\n"
        )
        res = subprocess.run([sys.executable, "-c", sub_code], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"GTK4 AppImage test failed: {res.stderr}")

    def test_gtk4_adw_flatpakref(self):
        """Verify opening FlatpakRef (.flatpakref) in Libadwaita window."""
        sub_code = (
            "import sys, os, gi\n"
            "sys.path.insert(0, os.path.abspath('src'))\n"
            "gi.require_version('Gtk', '4.0')\n"
            "gi.require_version('Adw', '1')\n"
            "from gi.repository import Adw\n"
            "from MainWindowAdw import MainWindowAdw\n"
            "app = Adw.Application(application_id='org.parslinux.test.adw_flatpakref')\n"
            "fixture = os.path.abspath('tests/fixtures/sample-vlc.flatpakref')\n"
            "def on_act(app):\n"
            "    win = MainWindowAdw(app, fixture)\n"
            "    assert win.lbl_pkgname.get_label() == 'org.videolan.VLC'\n"
            "    assert 'Flathub' in win.btn_install.get_label() or 'Kur' in win.btn_install.get_label()\n"
            "    app.quit()\n"
            "app.connect('activate', on_act)\n"
            "app.run([])\n"
        )
        res = subprocess.run([sys.executable, "-c", sub_code], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"GTK4 FlatpakRef test failed: {res.stderr}")


if __name__ == '__main__':
    unittest.main()
