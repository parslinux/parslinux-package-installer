#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SnapshotManager.py for parslinux-package-installer.
Detects available system snapshot backends (Timeshift, Snapper, Btrfs)
and coordinates automated system restore point creation before package operations.
"""

import datetime
import logging
import os
import re
import shutil
import subprocess
from typing import List, Optional, Tuple

logger = logging.getLogger("parslinux-snapshot")


class SnapshotManager:
    """Manages system restore point creation across Timeshift, Snapper and Btrfs."""

    BACKEND_TIMESHIFT = "timeshift"
    BACKEND_SNAPPER = "snapper"
    BACKEND_BTRFS = "btrfs"

    @classmethod
    def is_root_btrfs(cls) -> bool:
        """Detect whether the root filesystem '/' is formatted with btrfs."""
        try:
            with open("/proc/mounts", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 3 and parts[1] == "/" and parts[2].lower() == "btrfs":
                        return True
        except Exception as e:
            logger.debug("Failed to inspect /proc/mounts: %s", e)
        return False

    @classmethod
    def detect_backend(cls) -> Optional[str]:
        """
        Detect the best available snapshot backend on the current system.
        Priority:
        1. Timeshift (most common, supports both RSYNC and BTRFS modes)
        2. Snapper (SUSE/openSUSE/Arch standard btrfs snapshot manager)
        3. Native Btrfs (if root is on btrfs and btrfs-progs is available)
        """
        # 1. Check Timeshift
        timeshift_bin = shutil.which("timeshift")
        if timeshift_bin:
            # Verify if timeshift configuration exists
            ts_configs = ["/etc/timeshift/timeshift.json", "/etc/timeshift.json"]
            if any(os.path.exists(cfg) for cfg in ts_configs) or os.path.exists(timeshift_bin):
                return cls.BACKEND_TIMESHIFT

        # 2. Check Snapper
        snapper_bin = shutil.which("snapper")
        if snapper_bin:
            snapper_configs = ["/etc/snapper/configs/root"]
            if any(os.path.exists(cfg) for cfg in snapper_configs) or os.path.isdir("/etc/snapper/configs"):
                return cls.BACKEND_SNAPPER

        # 3. Check Native Btrfs
        if cls.is_root_btrfs() and shutil.which("btrfs"):
            snapshot_dirs = ["/.snapshots", "/snapshots"]
            if any(os.path.isdir(d) for d in snapshot_dirs):
                return cls.BACKEND_BTRFS

        return None

    @classmethod
    def is_available(cls) -> bool:
        """Return True if any supported snapshot backend is present."""
        return cls.detect_backend() is not None

    @classmethod
    def get_backend_name(cls) -> str:
        """Return human-readable title of detected backend."""
        backend = cls.detect_backend()
        if backend == cls.BACKEND_TIMESHIFT:
            return "Timeshift"
        elif backend == cls.BACKEND_SNAPPER:
            return "Snapper"
        elif backend == cls.BACKEND_BTRFS:
            return "Btrfs Snapshots"
        return "Mevcut Değil"

    @classmethod
    def get_backend_description(cls) -> str:
        """Return descriptive status summary for UI display."""
        backend = cls.detect_backend()
        if backend == cls.BACKEND_TIMESHIFT:
            return "Timeshift ile kurulum öncesi otomatik sistem geri yükleme noktası oluşturulur."
        elif backend == cls.BACKEND_SNAPPER:
            return "Snapper ile Btrfs kök dizini için geri alma anlık görüntüsü oluşturulur."
        elif backend == cls.BACKEND_BTRFS:
            return "Btrfs kök alt birimi için doğrudan anlık görüntü (snapshot) alınır."
        return "Sistemde yapılandırılmış Timeshift veya Snapper aracı bulunamadı."

    @classmethod
    def build_snapshot_command(cls, comment: str = "parslinux-pre-install") -> Optional[List[str]]:
        """Construct the privileged command list to execute the snapshot."""
        backend = cls.detect_backend()
        safe_comment = re.sub(r"[^\w\s\.-]", "_", comment).strip() or "parslinux-pre-install"

        if backend == cls.BACKEND_TIMESHIFT:
            ts_bin = shutil.which("timeshift") or "/usr/bin/timeshift"
            return [ts_bin, "--create", "--comments", safe_comment, "--tags", "O"]

        elif backend == cls.BACKEND_SNAPPER:
            snapper_bin = shutil.which("snapper") or "/usr/bin/snapper"
            return [snapper_bin, "-c", "root", "create", "-d", safe_comment]

        elif backend == cls.BACKEND_BTRFS:
            btrfs_bin = shutil.which("btrfs") or "/usr/bin/btrfs"
            ts_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = f"/.snapshots/parslinux_{ts_str}"
            return [btrfs_bin, "subvolume", "snapshot", "-r", "/", dest]

        return None

    @classmethod
    def create_snapshot(cls, comment: str = "parslinux-pre-install") -> Tuple[bool, str]:
        """
        Execute snapshot creation directly (requires root privileges if called standalone).
        Returns (success: bool, message: str).
        """
        cmd = cls.build_snapshot_command(comment)
        if not cmd:
            return False, "Sistemde kullanılabilir anlık görüntü aracı bulunamadı."

        logger.info("Executing snapshot command: %s", " ".join(cmd))
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            output = (res.stdout + "\n" + res.stderr).strip()
            if res.returncode == 0:
                logger.info("Snapshot successfully created.")
                return True, output or "Anlık görüntü başarıyla oluşturuldu."
            else:
                logger.warning("Snapshot command returned non-zero code %d: %s", res.returncode, output)
                return False, output or f"Hata kodu: {res.returncode}"
        except Exception as e:
            logger.error("Snapshot creation failed with exception: %s", e)
            return False, str(e)
