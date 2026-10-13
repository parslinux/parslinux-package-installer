#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actions.py for parslinux-package-installer.
Executes apt actions (install, reinstall, downgrade, remove) via pkexec.
"""

import os
import subprocess
import sys


def main():
    def control_lock():
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
            for lock in ("/var/lib/dpkg/lock-frontend", "/var/lib/dpkg/lock", "/var/lib/apt/lists/lock"):
                if os.path.exists(lock):
                    try:
                        import fcntl
                        with open(lock, "w") as f:
                            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                            fcntl.flock(f, fcntl.LOCK_UN)
                    except (IOError, OSError):
                        return False
            return True

    def install(targets):
        if isinstance(targets, str):
            targets = [targets]
        deb_paths = [os.path.abspath(p) for p in targets]
        return subprocess.call(
            ["apt", "install", *deb_paths, "-yq", "-o", "APT::Status-Fd=2",
             "-o", "Dpkg::Options::=--force-confnew"],
            env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'}
        )

    def reinstall(debianpackage):
        deb_path = os.path.abspath(debianpackage)
        return subprocess.call(
            ["apt", "install", "--reinstall", "--allow-downgrades", deb_path, "-yq", "-o", "APT::Status-Fd=2",
             "-o", "Dpkg::Options::=--force-confnew"],
            env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'}
        )

    def remove(packagenames):
        if isinstance(packagenames, str):
            packagenames = [packagenames]
        return subprocess.call(
            ["apt", "remove", "--purge", *packagenames, "-yq", "-o", "APT::Status-Fd=2",
             "-o", "Dpkg::Options::=--force-confnew"],
            env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'}
        )

    def downgrade(debianpackage):
        deb_path = os.path.abspath(debianpackage)
        return subprocess.call(
            ["apt", "install", "--allow-downgrades", deb_path, "-yq", "-o", "APT::Status-Fd=2",
             "-o", "Dpkg::Options::=--force-confnew"],
            env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'}
        )

    if len(sys.argv) > 2:
        if control_lock():
            action = sys.argv[1]
            targets = sys.argv[2:]
            if action == "install":
                sys.exit(install(targets))
            elif action == "remove":
                sys.exit(remove(targets))
            elif action == "reinstall":
                sys.exit(reinstall(targets[0]))
            elif action == "downgrade":
                sys.exit(downgrade(targets[0]))
            else:
                print(f"Unknown action: {action}")
                sys.exit(1)
        else:
            print("lock error")
            sys.exit(1)
    else:
        print("no argument passed")
        sys.exit(1)


if __name__ == "__main__":
    main()
