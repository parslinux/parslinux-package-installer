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
from typing import List, Union

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


def control_lock() -> bool:
    """Verify that neither dpkg nor apt locks are currently held."""
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


def install(targets: Union[str, List[str]]) -> int:
    """Install one or multiple local .deb package archives."""
    if isinstance(targets, str):
        targets = [targets]
    deb_paths = [os.path.abspath(p) for p in targets]
    cmd = [
        "apt", "install", *deb_paths, "-yq",
        "-o", "APT::Status-Fd=2",
        "-o", "Dpkg::Options::=--force-confnew"
    ]
    env = {**os.environ, "DEBIAN_FRONTEND": "noninteractive"}
    res = subprocess.run(cmd, env=env, check=False)
    return res.returncode


def reinstall(debianpackage: str) -> int:
    """Reinstall the specified local package."""
    deb_path = os.path.abspath(debianpackage)
    cmd = [
        "apt", "install", "--reinstall", "--allow-downgrades", deb_path, "-yq",
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
    cmd = [
        "apt", "remove", "--purge", *packagenames, "-yq",
        "-o", "APT::Status-Fd=2",
        "-o", "Dpkg::Options::=--force-confnew"
    ]
    env = {**os.environ, "DEBIAN_FRONTEND": "noninteractive"}
    res = subprocess.run(cmd, env=env, check=False)
    return res.returncode


def downgrade(debianpackage: str) -> int:
    """Downgrade the package to the version in the specified archive."""
    deb_path = os.path.abspath(debianpackage)
    cmd = [
        "apt", "install", "--allow-downgrades", deb_path, "-yq",
        "-o", "APT::Status-Fd=2",
        "-o", "Dpkg::Options::=--force-confnew"
    ]
    env = {**os.environ, "DEBIAN_FRONTEND": "noninteractive"}
    res = subprocess.run(cmd, env=env, check=False)
    return res.returncode


def main() -> None:
    if len(sys.argv) <= 2:
        logger.error("No action or target specified.")
        sys.exit(1)

    if not control_lock():
        logger.error("Dpkg/APT frontend lock is currently held by another process.")
        sys.exit(256)

    action = sys.argv[1].lower()
    targets = sys.argv[2:]

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
