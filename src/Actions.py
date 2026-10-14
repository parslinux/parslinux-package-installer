#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actions.py for parslinux-package-installer.
Privileged backend executing APT actions (install, reinstall, downgrade, remove) via PolicyKit.
"""

import logging
import os
import signal
import subprocess
import sys
import shutil
import tempfile
from typing import List, Union

from SnapshotManager import SnapshotManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] parslinux-actions: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("parslinux-actions")


def handle_signal(sig, frame):
    logger.warning("Interrupted by signal %d, exiting...", sig)
    sys.exit(130)


signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


def is_arch_environment() -> bool:
    """Detect if running under an Arch Linux environment."""
    return os.path.exists("/etc/arch-release") or (bool(shutil.which("pacman")) and not bool(shutil.which("dpkg")))


def is_arch_package(filename: str) -> bool:
    """Check if target filename is an Arch package archive."""
    return str(filename).lower().endswith((".pkg.tar.zst", ".pkg.tar.xz", ".pkg.tar.gz", ".pkg.tar"))


def build_pacman_install_command(targets: List[str]) -> List[str]:
    """Construct pacman command line for installing local package archives."""
    return ["pacman", "-U", "--noconfirm", "--needed", *targets]


def build_pacman_remove_command(target: Union[str, List[str]]) -> List[str]:
    """Construct pacman command line for removing installed packages."""
    if isinstance(target, str):
        target = [target]
    return ["pacman", "-Rns", "--noconfirm", *target]


def control_lock() -> bool:
    """Verify that neither dpkg/apt nor pacman locks are currently held."""
    if is_arch_environment():
        pacman_lock = "/var/lib/pacman/db.lck"
        if os.path.exists(pacman_lock):
            logger.error("Pacman database is currently locked (%s exists).", pacman_lock)
            return False
        return True

    try:
        import apt_pkg
        apt_pkg.init_system()
        try:
            apt_pkg.pkgsystem_lock()
        except SystemError:
            return False
        apt_pkg.pkgsystem_unlock()
        return True
    except ImportError:
        lock_paths = (
            "/var/lib/dpkg/lock-frontend",
            "/var/lib/dpkg/lock",
            "/var/lib/apt/lists/lock"
        )
        for lock in lock_paths:
            if os.path.exists(lock):
                try:
                    import fcntl
                    with open(lock, "w") as f:
                        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        fcntl.flock(f, fcntl.LOCK_UN)
                except (IOError, OSError):
                    return False
        return True


def install(targets: Union[str, List[str]], create_snapshot: bool = False) -> int:
    """Install one or multiple local package archives (.deb or .pkg.tar.*)."""
    if isinstance(targets, str):
        targets = [targets]

    clean_targets = []
    for t in targets:
        if t == "--snapshot":
            create_snapshot = True
        else:
            clean_targets.append(t)
    targets = clean_targets

    if not targets:
        logger.error("No valid package path provided for install.")
        return 1

    if create_snapshot:
        if SnapshotManager.is_available():
            base_name = os.path.basename(targets[0])
            logger.info("Executing pre-installation snapshot for %s via %s...", base_name, SnapshotManager.get_backend_name())
            ok, msg = SnapshotManager.create_snapshot(f"parslinux-pre-install: {base_name}")
            if not ok:
                logger.warning("Snapshot creation issue: %s (Proceeding with installation)", msg)
        else:
            logger.info("Snapshot requested, but no configured snapshot tool detected. Proceeding...")

    pkg_paths = [os.path.abspath(p) for p in targets]

    # Arch Linux native package installation
    any_arch_pkg = any(is_arch_package(p) for p in pkg_paths)
    any_rpm_pkg = any(p.endswith(".rpm") for p in pkg_paths)

    # Native RPM environment
    if any_rpm_pkg and shutil.which("rpm") and not shutil.which("dpkg") and not shutil.which("pacman"):
        rpm_bin = shutil.which("rpm")
        cmd = [rpm_bin, "-Uvh", "--replacepkgs", *pkg_paths]
        res = subprocess.run(cmd, check=False)
        return res.returncode

    # RPM on Debian or Arch via alien
    if any_rpm_pkg:
        alien_bin = shutil.which("alien")
        if alien_bin:
            logger.info("Converting RPM via alien...")
            cmd = [alien_bin, "-i", *pkg_paths]
            res = subprocess.run(cmd, check=False)
            return res.returncode
        else:
            logger.error("RPM package installation requires 'rpm' on Red Hat/Fedora or 'alien' on Debian/Arch.")
            return 1

    if is_arch_environment() or any_arch_pkg:
        pacman_bin = shutil.which("pacman") or "/usr/bin/pacman"
        arch_targets = []
        for p in pkg_paths:
            if is_arch_package(p):
                arch_targets.append(p)
            elif p.endswith(".deb"):
                # Convert deb via debtap on Arch Linux if available
                debtap_bin = shutil.which("debtap")
                if debtap_bin:
                    logger.info("Converting %s via debtap...", p)
                    tmp_dir = tempfile.mkdtemp(prefix="debtap-")
                    res = subprocess.run([debtap_bin, "-q", "-Q", p], cwd=tmp_dir, check=False)
                    converted = [os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir) if is_arch_package(f)]
                    if converted:
                        arch_targets.append(converted[0])
                    else:
                        logger.error("debtap conversion failed for %s", p)
                else:
                    logger.warning("debtap not found. Cannot convert .deb on Arch Linux without debtap.")

        if arch_targets:
            cmd = build_pacman_install_command(arch_targets)
            res = subprocess.run(cmd, check=False)
            return res.returncode
        elif any(p.endswith(".deb") for p in pkg_paths) and not is_arch_environment():
            pass  # Fall through to standard APT
        else:
            logger.error("No valid installable packages found.")
            return 1

    # Standard Debian/Pars Linux APT installation
    cmd = [
        "apt", "install", *pkg_paths, "-yq",
        "-o", "APT::Status-Fd=2",
        "-o", "Dpkg::Options::=--force-confnew"
    ]
    env = {**os.environ, "DEBIAN_FRONTEND": "noninteractive"}
    res = subprocess.run(cmd, env=env, check=False)
    return res.returncode


def reinstall(target: str) -> int:
    """Reinstall the specified local package archive."""
    pkg_path = os.path.abspath(target)
    if is_arch_environment() or is_arch_package(pkg_path):
        pacman_bin = shutil.which("pacman") or "/usr/bin/pacman"
        cmd = [pacman_bin, "-U", "--noconfirm", pkg_path]
        res = subprocess.run(cmd, check=False)
        return res.returncode

    cmd = [
        "apt", "install", "--reinstall", "--allow-downgrades", pkg_path, "-yq",
        "-o", "APT::Status-Fd=2",
        "-o", "Dpkg::Options::=--force-confnew"
    ]
    env = {**os.environ, "DEBIAN_FRONTEND": "noninteractive"}
    res = subprocess.run(cmd, env=env, check=False)
    return res.returncode


def remove(packagenames: Union[str, List[str]]) -> int:
    """Purge remove one or more installed packages from the system."""
    if isinstance(packagenames, str):
        packagenames = [packagenames]

    if is_arch_environment():
        cmd = build_pacman_remove_command(packagenames)
        res = subprocess.run(cmd, check=False)
        return res.returncode

    cmd = [
        "apt", "remove", "--purge", *packagenames, "-yq",
        "-o", "APT::Status-Fd=2",
        "-o", "Dpkg::Options::=--force-confnew"
    ]
    env = {**os.environ, "DEBIAN_FRONTEND": "noninteractive"}
    res = subprocess.run(cmd, env=env, check=False)
    return res.returncode


def downgrade(target: str) -> int:
    """Downgrade package to the specified local archive version."""
    pkg_path = os.path.abspath(target)
    if is_arch_environment() or is_arch_package(pkg_path):
        pacman_bin = shutil.which("pacman") or "/usr/bin/pacman"
        cmd = [pacman_bin, "-U", "--noconfirm", pkg_path]
        res = subprocess.run(cmd, check=False)
        return res.returncode

    cmd = [
        "apt", "install", "--allow-downgrades", pkg_path, "-yq",
        "-o", "APT::Status-Fd=2",
        "-o", "Dpkg::Options::=--force-confnew"
    ]
    env = {**os.environ, "DEBIAN_FRONTEND": "noninteractive"}
    res = subprocess.run(cmd, env=env, check=False)
    return res.returncode


def create_snapshot_action(args: List[str]) -> int:
    """Create a system snapshot directly via privileged helper."""
    comment = " ".join(args) if args else "parslinux-manual-snapshot"
    ok, msg = SnapshotManager.create_snapshot(comment)
    print(msg)
    return 0 if ok else 1


def main() -> None:
    if len(sys.argv) <= 1:
        logger.error("No action specified.")
        sys.exit(1)

    action = sys.argv[1].lower()
    targets = sys.argv[2:]

    # Standalone snapshot action does not need dpkg/apt lock
    if action == "snapshot":
        sys.exit(create_snapshot_action(targets))

    if not targets:
        logger.error("No target specified for action: %s", action)
        sys.exit(1)

    if not control_lock():
        logger.error("Dpkg/APT frontend lock is currently held by another process.")
        sys.exit(256)

    action_map = {
        "install": lambda: install(targets),
        "remove": lambda: remove(targets),
        "reinstall": lambda: reinstall(targets[0]),
        "downgrade": lambda: downgrade(targets[0]),
    }

    handler = action_map.get(action)
    if not handler:
        logger.error("Unknown action: %s", action)
        sys.exit(1)

    exit_code = handler()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
