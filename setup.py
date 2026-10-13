#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
from setuptools import setup, find_packages


def create_mo_files():
    podir = "po"
    mo = []
    if os.path.exists(podir):
        for po in os.listdir(podir):
            if po.endswith(".po"):
                lang = po.split(".po")[0]
                lang_dir = f"{podir}/{lang}/LC_MESSAGES"
                os.makedirs(lang_dir, exist_ok=True)
                mo_file = f"{lang_dir}/parslinux-package-installer.mo"
                msgfmt_cmd = f"msgfmt {podir}/{po} -o {mo_file}"
                subprocess.call(msgfmt_cmd, shell=True)
                mo.append((f"/usr/share/locale/{lang}/LC_MESSAGES", [mo_file]))
    return mo


changelog = "debian/changelog"
version = "1.0.0"
if os.path.exists(changelog):
    try:
        head = open(changelog).readline()
        version = head.split("(")[1].split(")")[0]
    except Exception:
        pass

os.makedirs("src", exist_ok=True)
with open("src/__version__", "w") as f:
    f.write(version)

data_files = [
    ("/usr/share/applications", ["org.parslinux.package-installer.desktop"]),
    ("/usr/share/metainfo", ["data/org.parslinux.package-installer.metainfo.xml"]),
    ("/usr/share/parslinux/parslinux-package-installer/data", ["data/style.css"]),
    ("/usr/share/parslinux/parslinux-package-installer/ui", ["ui/MainWindow.glade", "ui/style.css"]),
    ("/usr/share/parslinux/parslinux-package-installer/src",
     ["src/Actions.py", "src/Main.py", "src/MainWindow.py", "src/DebPackage.py", "src/cli.py", "src/MainAdw.py", "src/MainWindowAdw.py", "src/__version__"]),
    ("/usr/bin", ["parslinux-package-installer", "parslinux-package-installer-adw", "pardus-package-installer"]),
    ("/usr/share/polkit-1/actions", ["org.parslinux.pkexec.parslinux-package-installer.policy"]),
    ("/usr/share/parslinux/parslinux-package-installer/images", ["images/parslinux-package-installer.svg"]),
    ("/usr/share/icons/hicolor/scalable/apps/", ["images/parslinux-package-installer.svg", "images/pardus-package-installer.svg"])
] + create_mo_files()

setup(
    name="Pars Linux Package Installer",
    version=version,
    packages=find_packages(),
    scripts=["parslinux-package-installer", "parslinux-package-installer-adw"],
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Pars Linux Developers",
    author_email="dev@parslinux.org",
    description="Pars Linux Deb Package Installer (GDebi Equivalent)",
    license="GPLv3",
    keywords="deb package installer parslinux gdebi",
    url="https://parslinux.org",
)
