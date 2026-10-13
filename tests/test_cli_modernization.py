#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for modernized CLI inspection, UI styling, and AppStream metadata.
"""

import io
import os
import subprocess
import sys
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

# Ensure src/ is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cli import cli_check, cli_info, get_version


class TestCliModernization(unittest.TestCase):
    def setUp(self):
        self.fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))
        self.valid_deb = os.path.join(self.fixtures_dir, "parslinux-hello_1.0.0_all.deb")
        self.nonexistent_deb = os.path.join(self.fixtures_dir, "does-not-exist.deb")

    def test_get_version(self):
        ver = get_version()
        self.assertIsInstance(ver, str)
        self.assertTrue(len(ver) > 0)

    def test_cli_info_valid_package(self):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            code = cli_info(self.valid_deb)
        output = buf.getvalue()

        self.assertEqual(code, 0)
        self.assertIn("parslinux-hello", output)
        self.assertIn("1.0.0", output)
        self.assertIn("all", output)
        self.assertIn("utils", output)
        self.assertIn("Pars Linux Team", output)

    def test_cli_info_missing_file(self):
        err_buf = io.StringIO()
        with patch("sys.stderr", err_buf):
            code = cli_info(self.nonexistent_deb)
        self.assertEqual(code, 1)
        self.assertIn("Dosya bulunamadı", err_buf.getvalue())

    def test_cli_check_valid_package(self):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            code = cli_check(self.valid_deb)
        output = buf.getvalue()

        self.assertEqual(code, 0)
        self.assertIn("parslinux-hello", output)
        self.assertIn("kurulabilir", output)

    def test_cli_check_missing_file(self):
        err_buf = io.StringIO()
        with patch("sys.stderr", err_buf):
            code = cli_check(self.nonexistent_deb)
        self.assertEqual(code, 1)
        self.assertIn("Dosya bulunamadı", err_buf.getvalue())

    def test_style_css_exists_and_valid(self):
        css_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ui", "style.css"))
        self.assertTrue(os.path.exists(css_path), "ui/style.css must exist")

        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn(".suggested-action", content)
        self.assertIn(".destructive-action", content)
        self.assertIn("#textview", content)
        self.assertIn(".badge-success", content)

        # Validate with Gtk CssProvider
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        provider = Gtk.CssProvider()
        provider.load_from_path(css_path)
        self.assertIsNotNone(provider)

    def test_appstream_metainfo_xml(self):
        xml_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "org.parslinux.package-installer.metainfo.xml")
        )
        self.assertTrue(os.path.exists(xml_path), "Metainfo XML file must exist")
        tree = ET.parse(xml_path)
        root = tree.getroot()
        self.assertEqual(root.tag, "component")
        self.assertEqual(root.findtext("id"), "org.parslinux.package-installer")
        self.assertIsNotNone(root.find("name"))
        self.assertIsNotNone(root.find("summary"))
        self.assertIsNotNone(root.find("description"))

    def test_main_cli_subprocess_flags(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        # Test --version
        res_ver = subprocess.run(
            [sys.executable, "src/Main.py", "--version"],
            cwd=root_dir, capture_output=True, text=True, check=True
        )
        self.assertIn("Pars Linux Package Installer v", res_ver.stdout)

        # Test -i (info)
        res_info = subprocess.run(
            [sys.executable, "src/Main.py", "-i", self.valid_deb],
            cwd=root_dir, capture_output=True, text=True, check=True
        )
        self.assertIn("parslinux-hello", res_info.stdout)

        # Test -c (check)
        res_check = subprocess.run(
            [sys.executable, "src/Main.py", "-c", self.valid_deb],
            cwd=root_dir, capture_output=True, text=True, check=True
        )
        self.assertIn("kurulabilir", res_check.stdout)

        # Test --adw --version delegation
        res_adw_ver = subprocess.run(
            [sys.executable, "src/Main.py", "--adw", "--version"],
            cwd=root_dir, capture_output=True, text=True, check=True
        )
        self.assertIn("Pars Linux Package Installer (Adw) v", res_adw_ver.stdout)

    def test_is_remote_url(self):
        from cli import is_remote_url
        self.assertTrue(is_remote_url("https://example.com/package.deb"))
        self.assertTrue(is_remote_url("http://repo.parslinux.org/pkg.deb"))
        self.assertFalse(is_remote_url("/tmp/package.deb"))
        self.assertFalse(is_remote_url("package.deb"))
        self.assertFalse(is_remote_url(None))

    def test_package_architecture_check(self):
        from DebPackage import DebPackage
        pkg = DebPackage(self.valid_deb)
        ok, msg = pkg.check_architecture()
        self.assertTrue(ok, "Architecture 'all' should always be valid")
        self.assertEqual(msg, "")


if __name__ == "__main__":
    unittest.main()
