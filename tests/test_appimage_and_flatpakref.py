#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated unit and integration tests for AppImage and FlatpakRef/Repo packages.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from AppImagePackage import AppImagePackage
from FlatpakRefPackage import FlatpakRefPackage
import PackageLoader
from cli import cli_info, cli_check


class TestAppImageAndFlatpakRef(unittest.TestCase):
    """Test suite for AppImage portable bundles and FlatpakRef/Repo packages."""

    @classmethod
    def setUpClass(cls):
        cls.fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        cls.appimage_path = os.path.join(cls.fixtures_dir, "sample-app-1.0.0-x86_64.AppImage")
        cls.flatpakref_path = os.path.join(cls.fixtures_dir, "sample-vlc.flatpakref")
        cls.flatpakrepo_path = os.path.join(cls.fixtures_dir, "sample-flathub.flatpakrepo")

    def test_extension_detection(self):
        """Verify PackageLoader recognizes .appimage, .flatpakref, and .flatpakrepo."""
        self.assertTrue(PackageLoader.is_supported_package(self.appimage_path))
        self.assertTrue(PackageLoader.is_supported_package(self.flatpakref_path))
        self.assertTrue(PackageLoader.is_supported_package(self.flatpakrepo_path))
        self.assertTrue(PackageLoader.is_supported_package("app.AppImage"))
        self.assertFalse(PackageLoader.is_supported_package("app.zip"))

    def test_appimage_metadata_parsing(self):
        """Verify AppImage package metadata extraction."""
        pkg = PackageLoader.open_package(self.appimage_path)
        self.assertIsInstance(pkg, AppImagePackage)
        self.assertEqual(pkg.pkgname, "sample-app")
        self.assertEqual(pkg.get("Version"), "1.0.0")
        self.assertEqual(pkg.get("Architecture"), "x86_64")
        self.assertEqual(pkg.get("Section"), "AppImage / Portable")
        self.assertIn("sample-app", pkg.get("Description").lower())

        files = pkg.get_file_details()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["name"], "sample-app-1.0.0-x86_64.AppImage")

        code, missing = pkg.check_dependencies()
        self.assertEqual(code, 0)
        self.assertEqual(missing, [])

    def test_appimage_desktop_integration(self):
        """Verify creating and removing desktop menu integration."""
        pkg = AppImagePackage(self.appimage_path)
        desktop_path = pkg.desktop_file_path

        # Clean prior state if any
        if os.path.exists(desktop_path):
            os.remove(desktop_path)

        self.assertFalse(pkg.is_integrated())
        self.assertEqual(pkg.compare_to_version_in_cache(), 0)

        # Integrate
        ok, msg = pkg.integrate_desktop()
        self.assertTrue(ok)
        self.assertTrue(os.path.isfile(desktop_path))
        self.assertTrue(pkg.is_integrated())
        self.assertEqual(pkg.compare_to_version_in_cache(), 2)

        with open(desktop_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Type=Application", content)
            self.assertIn(self.appimage_path, content)

        # Remove integration
        ok, msg = pkg.remove_desktop()
        self.assertTrue(ok)
        self.assertFalse(os.path.exists(desktop_path))
        self.assertFalse(pkg.is_integrated())

    def test_flatpakref_parsing(self):
        """Verify parsing of .flatpakref files."""
        pkg = PackageLoader.open_package(self.flatpakref_path)
        self.assertIsInstance(pkg, FlatpakRefPackage)
        self.assertFalse(pkg.is_repo)
        self.assertEqual(pkg.pkgname, "org.videolan.VLC")
        self.assertEqual(pkg.get("Version"), "stable")
        self.assertEqual(pkg.display_name, "VLC media player")
        self.assertIn("dl.flathub.org", pkg.get("Description"))

        files = pkg.get_file_details()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["name"], "sample-vlc.flatpakref")

    def test_flatpakrepo_parsing(self):
        """Verify parsing of .flatpakrepo files."""
        pkg = PackageLoader.open_package(self.flatpakrepo_path)
        self.assertIsInstance(pkg, FlatpakRefPackage)
        self.assertTrue(pkg.is_repo)
        self.assertEqual(pkg.pkgname, "flathub")
        self.assertEqual(pkg.get("Section"), "Flatpak / Depo")
        self.assertIn("flathub.org", pkg.get("Description"))

    def test_cli_info_and_check(self):
        """Verify terminal headless inspection for AppImage and FlatpakRef."""
        self.assertEqual(cli_info(self.appimage_path), 0)
        self.assertEqual(cli_check(self.appimage_path), 0)
        self.assertEqual(cli_info(self.flatpakref_path), 0)
        self.assertEqual(cli_info(self.flatpakrepo_path), 0)


if __name__ == "__main__":
    unittest.main()
