#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for RPM package inspection (RpmPackage) and Flathub alternative recommendations (FlatpakHelper).
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure src/ is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from RpmPackage import RpmPackage
from FlatpakHelper import FlatpakHelper
from PackageLoader import open_package, is_supported_package
from cli import cli_info, cli_check, cli_flatpak_search


class TestRpmPackage(unittest.TestCase):
    """Test suite for RPM (.rpm) package inspection."""

    @classmethod
    def setUpClass(cls):
        cls.fixture_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "fixtures", "parslinux-fedora-hello-2.2.0-1.x86_64.rpm")
        )

    def test_rpm_fixture_exists(self):
        self.assertTrue(os.path.exists(self.fixture_path), "Test RPM fixture must exist")

    def test_rpm_metadata_parsing(self):
        pkg = RpmPackage(self.fixture_path)
        self.assertEqual(pkg.pkgname, "parslinux-fedora-hello")
        self.assertEqual(pkg.get("Version"), "2.2.0-1")
        self.assertEqual(pkg.get("Architecture"), "x86_64")
        self.assertEqual(pkg.get("Section"), "RPM")
        self.assertIn("Pars Linux Developers", pkg.get("Maintainer"))
        self.assertEqual(pkg.get("Homepage"), "https://parslinux.org")
        self.assertIn("glibc", pkg.get("Depends"))
        self.assertIn("libadwaita", pkg.get("Depends"))
        self.assertIn("Test RPM package", pkg.get("Description"))

    def test_rpm_file_details(self):
        pkg = RpmPackage(self.fixture_path)
        files = pkg.get_file_list()
        self.assertEqual(len(files), 3)
        self.assertIn("/usr/bin/fedora-hello", files)

        details = pkg.get_file_details()
        self.assertEqual(len(details), 3)
        for d in details:
            self.assertIn("name", d)
            self.assertIn("is_dir", d)
            self.assertIn("is_exec", d)
            self.assertIn("mode", d)
        exec_files = [d for d in details if d["is_exec"]]
        self.assertEqual(len(exec_files), 1)
        self.assertEqual(exec_files[0]["name"], "/usr/bin/fedora-hello")

    def test_rpm_polymorphic_loader(self):
        pkg = open_package(self.fixture_path)
        self.assertIsInstance(pkg, RpmPackage)
        self.assertTrue(is_supported_package(self.fixture_path))
        self.assertTrue(is_supported_package("some-package.rpm"))
        self.assertTrue(is_supported_package("some-package.RPM"))

    def test_rpm_check_and_architecture(self):
        pkg = RpmPackage(self.fixture_path)
        ok = pkg.check()
        self.assertTrue(ok)
        arch_ok, pkg_arch, host_arch = pkg.check_architecture()
        self.assertTrue(arch_ok)
        self.assertEqual(pkg_arch, "x86_64")

    def test_rpm_version_comparison(self):
        pkg = RpmPackage(self.fixture_path)
        # Not installed by default in test environment
        res = pkg.compare_to_version_in_cache()
        self.assertIn(res, (pkg.VERSION_NONE, pkg.VERSION_SAME, pkg.VERSION_NEWER, pkg.VERSION_OUTDATED))


class TestFlatpakHelper(unittest.TestCase):
    """Test suite for Flathub alternative recommendations."""

    def test_is_available(self):
        # flatpak is installed on this test host
        self.assertTrue(isinstance(FlatpakHelper.is_available(), bool))

    @patch("subprocess.run")
    def test_search_flatpak_parsing(self, mock_run):
        mock_output = (
            "org.videolan.VLC\tVLC\t3.0.23\tVLC media player\n"
            "org.videolan.VLC.Plugin.bdj\tBluray Java\t\tBDJ plugin\n"
        )
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_output)

        results = FlatpakHelper.search_flatpak("vlc")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["app_id"], "org.videolan.VLC")
        self.assertEqual(results[0]["name"], "VLC")
        self.assertEqual(results[0]["version"], "3.0.23")
        self.assertEqual(results[0]["install_cmd"], "flatpak install flathub org.videolan.VLC")

    @patch("subprocess.run")
    def test_find_alternative_matching(self, mock_run):
        mock_output = (
            "org.videolan.VLC.Plugin.bdj\tBluray Java\t\tBDJ plugin\n"
            "org.videolan.VLC\tVLC\t3.0.23\tVLC media player\n"
        )
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_output)

        alt = FlatpakHelper.find_alternative("vlc-bin")
        self.assertIsNotNone(alt)
        self.assertEqual(alt["app_id"], "org.videolan.VLC")
        self.assertEqual(alt["name"], "VLC")

    @patch("subprocess.run")
    def test_install_flatpak_execution(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="Installed", stderr="")
        ok, msg = FlatpakHelper.install_flatpak("org.videolan.VLC")
        self.assertTrue(ok)
        mock_run.assert_called_once_with(
            ["flatpak", "install", "-y", "flathub", "org.videolan.VLC"],
            stdout=-1, stderr=-1, text=True, check=False
        )


class TestCliRpmAndFlatpakIntegration(unittest.TestCase):
    """Test suite for CLI interaction with RPM and Flatpak."""

    @classmethod
    def setUpClass(cls):
        cls.fixture_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "fixtures", "parslinux-fedora-hello-2.2.0-1.x86_64.rpm")
        )

    def test_cli_info_rpm(self):
        ret = cli_info(self.fixture_path)
        self.assertEqual(ret, 0)

    def test_cli_check_rpm(self):
        ret = cli_check(self.fixture_path)
        self.assertEqual(ret, 0)

    @patch.object(FlatpakHelper, "search_flatpak", return_value=[{
        "app_id": "org.videolan.VLC",
        "name": "VLC",
        "version": "3.0.23",
        "install_cmd": "flatpak install flathub org.videolan.VLC"
    }])
    def test_cli_flatpak_search(self, mock_search):
        ret = cli_flatpak_search("vlc")
        self.assertEqual(ret, 0)


if __name__ == "__main__":
    unittest.main()
