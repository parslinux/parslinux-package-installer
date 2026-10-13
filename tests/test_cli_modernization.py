#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for modernized CLI inspection and UI styling.
"""

import io
import os
import sys
import unittest
from unittest.mock import patch

# Ensure src/ is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cli import cli_info, cli_check, get_version


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


if __name__ == "__main__":
    unittest.main()
