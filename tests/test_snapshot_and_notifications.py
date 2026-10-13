#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for SnapshotManager and NotificationManager in parslinux-package-installer.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure src/ directory is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from SnapshotManager import SnapshotManager
import NotificationManager
import Actions


class TestSnapshotManager(unittest.TestCase):
    """Test suite for system restore point detection and command construction."""

    @patch("shutil.which")
    @patch("os.path.exists")
    def test_detect_backend_timeshift(self, mock_exists, mock_which):
        def fake_which(cmd):
            return "/usr/bin/timeshift" if cmd == "timeshift" else None
        mock_which.side_effect = fake_which
        mock_exists.return_value = True

        self.assertEqual(SnapshotManager.detect_backend(), SnapshotManager.BACKEND_TIMESHIFT)
        self.assertTrue(SnapshotManager.is_available())
        self.assertEqual(SnapshotManager.get_backend_name(), "Timeshift")

    @patch("shutil.which")
    @patch("os.path.exists")
    def test_detect_backend_snapper(self, mock_exists, mock_which):
        def fake_which(cmd):
            return "/usr/bin/snapper" if cmd == "snapper" else None
        mock_which.side_effect = fake_which
        mock_exists.return_value = True

        self.assertEqual(SnapshotManager.detect_backend(), SnapshotManager.BACKEND_SNAPPER)
        self.assertTrue(SnapshotManager.is_available())
        self.assertEqual(SnapshotManager.get_backend_name(), "Snapper")

    @patch.object(SnapshotManager, "is_root_btrfs", return_value=True)
    @patch("shutil.which")
    @patch("os.path.isdir")
    def test_detect_backend_btrfs(self, mock_isdir, mock_which, mock_btrfs):
        def fake_which(cmd):
            return "/usr/bin/btrfs" if cmd == "btrfs" else None
        mock_which.side_effect = fake_which
        mock_isdir.return_value = True

        self.assertEqual(SnapshotManager.detect_backend(), SnapshotManager.BACKEND_BTRFS)
        self.assertTrue(SnapshotManager.is_available())
        self.assertEqual(SnapshotManager.get_backend_name(), "Btrfs Snapshots")

    @patch.object(SnapshotManager, "is_root_btrfs", return_value=False)
    @patch("shutil.which", return_value=None)
    def test_detect_backend_none(self, mock_which, mock_btrfs):
        self.assertIsNone(SnapshotManager.detect_backend())
        self.assertFalse(SnapshotManager.is_available())
        self.assertEqual(SnapshotManager.get_backend_name(), "Mevcut Değil")

    @patch.object(SnapshotManager, "detect_backend", return_value=SnapshotManager.BACKEND_TIMESHIFT)
    @patch("shutil.which", return_value="/usr/bin/timeshift")
    def test_build_command_timeshift(self, mock_which, mock_backend):
        cmd = SnapshotManager.build_snapshot_command("test-package")
        self.assertIsNotNone(cmd)
        self.assertIn("/usr/bin/timeshift", cmd[0])
        self.assertIn("--create", cmd)
        self.assertIn("--comments", cmd)
        self.assertIn("test-package", cmd)
        self.assertIn("--tags", cmd)

    @patch.object(SnapshotManager, "detect_backend", return_value=SnapshotManager.BACKEND_SNAPPER)
    @patch("shutil.which", return_value="/usr/bin/snapper")
    def test_build_command_snapper(self, mock_which, mock_backend):
        cmd = SnapshotManager.build_snapshot_command("test-package")
        self.assertIsNotNone(cmd)
        self.assertIn("/usr/bin/snapper", cmd[0])
        self.assertIn("create", cmd)
        self.assertIn("-d", cmd)
        self.assertIn("test-package", cmd)

    @patch.object(SnapshotManager, "detect_backend", return_value=SnapshotManager.BACKEND_BTRFS)
    @patch("shutil.which", return_value="/usr/bin/btrfs")
    def test_build_command_btrfs(self, mock_which, mock_backend):
        cmd = SnapshotManager.build_snapshot_command("test-package")
        self.assertIsNotNone(cmd)
        self.assertIn("btrfs", cmd[0])
        self.assertIn("subvolume", cmd)
        self.assertIn("snapshot", cmd)

    @patch("subprocess.run")
    @patch.object(SnapshotManager, "build_snapshot_command", return_value=["timeshift", "--create"])
    def test_create_snapshot_success(self, mock_build, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="Snapshot created successfully", stderr="")
        ok, msg = SnapshotManager.create_snapshot("pre-install")
        self.assertTrue(ok)
        self.assertIn("Snapshot created", msg)

    @patch("subprocess.run")
    @patch.object(SnapshotManager, "build_snapshot_command", return_value=["timeshift", "--create"])
    def test_create_snapshot_failure(self, mock_build, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Disk full error")
        ok, msg = SnapshotManager.create_snapshot("pre-install")
        self.assertFalse(ok)
        self.assertIn("Disk full error", msg)


class TestNotificationManager(unittest.TestCase):
    """Test suite for desktop and application notifications."""

    @patch("subprocess.Popen")
    @patch("shutil.which", return_value="/usr/bin/notify-send")
    def test_notify_install_success_cli(self, mock_which, mock_popen):
        res = NotificationManager.notify_install_success("parslinux-app", "2.1.0")
        self.assertTrue(res)
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        self.assertEqual(args[0], "/usr/bin/notify-send")
        self.assertIn("Kurulum Tamamlandı", args)
        self.assertIn("parslinux-app", args[-1])

    @patch("subprocess.Popen")
    @patch("shutil.which", return_value="/usr/bin/notify-send")
    def test_notify_install_failure_cli(self, mock_which, mock_popen):
        res = NotificationManager.notify_install_failure("broken-app", "Bağımlılık hatası")
        self.assertTrue(res)
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        self.assertIn("critical", args)
        self.assertIn("broken-app", args[-1])

    @patch("subprocess.Popen")
    @patch("shutil.which", return_value="/usr/bin/notify-send")
    def test_notify_remove_success(self, mock_which, mock_popen):
        res = NotificationManager.notify_remove_success("parslinux-app")
        self.assertTrue(res)
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        self.assertIn("Paket Kaldırıldı", args)

    @patch("subprocess.Popen")
    @patch("shutil.which", return_value="/usr/bin/notify-send")
    def test_notify_batch_success(self, mock_which, mock_popen):
        res = NotificationManager.notify_batch_success(5)
        self.assertTrue(res)
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        self.assertIn("Toplu Kurulum Tamamlandı", args)
        self.assertIn("5", args[-1])

    def test_native_gio_notification(self):
        mock_app = MagicMock()
        res = NotificationManager.send_notification(
            title="Test",
            body="Test body",
            icon_name="emblem-ok-symbolic",
            app=mock_app
        )
        self.assertTrue(res)
        mock_app.send_notification.assert_called_once()


class TestActionsSnapshotIntegration(unittest.TestCase):
    """Test suite for Actions.py privileged integration with SnapshotManager."""

    @patch.object(SnapshotManager, "is_available", return_value=True)
    @patch.object(SnapshotManager, "create_snapshot", return_value=(True, "Created"))
    @patch("Actions.is_arch_environment", return_value=False)
    @patch("subprocess.run")
    def test_actions_install_with_snapshot_flag(self, mock_run, mock_arch, mock_snap, mock_avail):
        mock_run.return_value = MagicMock(returncode=0)
        ret = Actions.install(["/tmp/test.deb", "--snapshot"])
        self.assertEqual(ret, 0)
        mock_snap.assert_called_once()
        self.assertIn("test.deb", mock_snap.call_args[0][0])

    @patch.object(SnapshotManager, "create_snapshot", return_value=(True, "Snapshot OK"))
    def test_actions_standalone_snapshot(self, mock_snap):
        ret = Actions.create_snapshot_action(["manual", "test", "point"])
        self.assertEqual(ret, 0)
        mock_snap.assert_called_once_with("manual test point")


if __name__ == "__main__":
    unittest.main()
