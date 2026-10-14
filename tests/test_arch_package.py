#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for Arch Linux package support (.pkg.tar.zst) and multi-backend loading.
"""

import io
import os
import sys
import unittest
from unittest.mock import patch

# Ensure src directory is in sys.path
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from ArchPackage import ArchPackage, is_arch_package
from PackageLoader import open_package, is_supported_package, is_arch_system
from DebPackage import DebPackage
from cli import cli_info, cli_check
from Actions import is_arch_environment, build_pacman_install_command, build_pacman_remove_command


class TestArchPackageSupport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        cls.arch_fixture = os.path.join(cls.fixture_dir, "parslinux-arch-hello-1.0.0-1-any.pkg.tar.zst")
        cls.deb_fixture = os.path.join(cls.fixture_dir, "parslinux-hello_1.0.0_all.deb")
        assert os.path.exists(cls.arch_fixture), f"Arch fixture missing: {cls.arch_fixture}"
        assert os.path.exists(cls.deb_fixture), f"Deb fixture missing: {cls.deb_fixture}"

    def test_extension_detection(self):
        """Verify extension checks for Arch and Debian packages."""
        self.assertTrue(is_arch_package("sample.pkg.tar.zst"))
        self.assertTrue(is_arch_package("sample.pkg.tar.xz"))
        self.assertTrue(is_arch_package("sample.pkg.tar.gz"))
        self.assertFalse(is_arch_package("sample.deb"))
        self.assertFalse(is_arch_package("sample.tar.gz"))

        self.assertTrue(is_supported_package("sample.pkg.tar.zst"))
        self.assertTrue(is_supported_package("sample.deb"))
        self.assertTrue(is_supported_package("sample.rpm"))
        self.assertFalse(is_supported_package("sample.exe"))
        self.assertFalse(is_supported_package("sample.txt"))

    def test_polymorphic_package_loader(self):
        """Verify PackageLoader returns appropriate class instance."""
        pkg_arch = open_package(self.arch_fixture)
        self.assertIsInstance(pkg_arch, ArchPackage)
        self.assertEqual(pkg_arch.package_type, "arch")

        pkg_deb = open_package(self.deb_fixture)
        self.assertIsInstance(pkg_deb, DebPackage)

    def test_arch_metadata_parsing(self):
        """Verify .PKGINFO metadata fields extraction."""
        pkg = ArchPackage(self.arch_fixture)
        self.assertEqual(pkg.pkgname, "parslinux-arch-hello")
        self.assertEqual(pkg.pkgver, "1.0.0-1")
        self.assertEqual(pkg.get("Version"), "1.0.0-1")
        self.assertEqual(pkg.get("Description"), "Pars Linux Arch Test Package")
        self.assertEqual(pkg.get("Architecture"), "any")
        self.assertEqual(pkg.get("Homepage"), "https://parslinux.org")
        self.assertEqual(pkg.get("Maintainer"), "Pars Linux Team <dev@parslinux.org>")
        self.assertIn("bash", pkg.depends)
        self.assertIn("glibc", pkg.depends)
        self.assertIn("hello", pkg.provides)
        self.assertIn("old-hello", pkg.conflicts)
        self.assertEqual(pkg.get("Section"), "Arch Linux")

    def test_arch_file_details(self):
        """Verify filelist and detailed permissions extraction."""
        pkg = ArchPackage(self.arch_fixture)
        self.assertIn("/usr/bin/arch-hello", pkg.filelist)
        self.assertIn("/usr/share/doc/parslinux-arch-hello/README", pkg.filelist)
        # Ensure root metadata .PKGINFO is filtered out of payload filelist
        self.assertNotIn(".PKGINFO", pkg.filelist)

        details = pkg.get_file_details()
        bin_entry = next((d for d in details if d["name"] == "/usr/bin/arch-hello"), None)
        self.assertIsNotNone(bin_entry)
        self.assertTrue(bin_entry["is_exec"])
        self.assertIn("mode", bin_entry)

    def test_architecture_compatibility(self):
        """Verify host architecture verification."""
        pkg = ArchPackage(self.arch_fixture)
        ok, msg = pkg.check_architecture()
        self.assertTrue(ok)
        self.assertEqual(msg, "")

    def test_cli_info_arch(self):
        """Verify cli_info prints Arch package metadata."""
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            code = cli_info(self.arch_fixture)
        self.assertEqual(code, 0)
        output = captured.getvalue()
        self.assertIn("parslinux-arch-hello", output)
        self.assertIn("1.0.0-1", output)
        self.assertIn("Pars Linux Arch Test Package", output)

    def test_cli_check_arch(self):
        """Verify cli_check evaluates Arch package."""
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            code = cli_check(self.arch_fixture)
        self.assertEqual(code, 0)
        output = captured.getvalue()
        self.assertIn("parslinux-arch-hello", output)
        self.assertIn("✓ Bağımlılıklar", output)

    def test_actions_arch_commands(self):
        """Verify Pacman installation and removal commands construction."""
        install_cmd = build_pacman_install_command(["/tmp/pkg1.pkg.tar.zst", "/tmp/pkg2.pkg.tar.zst"])
        self.assertEqual(install_cmd, ["pacman", "-U", "--noconfirm", "--needed", "/tmp/pkg1.pkg.tar.zst", "/tmp/pkg2.pkg.tar.zst"])

        remove_cmd = build_pacman_remove_command("my-test-package")
        self.assertEqual(remove_cmd, ["pacman", "-Rns", "--noconfirm", "my-test-package"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
