#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MainWindow for parslinux-package-installer.
Provides graphical package installation, removal, dependency verification,
interactive included file inspection, and batch package queue management.
"""

import locale
from locale import gettext as _
import logging
import os
import re
from subprocess import PIPE, Popen
import sys
import threading
from typing import List, Optional, Tuple

import gi

gi.require_version('Gtk', '3.0')
gi.require_version("Notify", "0.7")
from gi.repository import Gdk, Gio, GLib, GObject, Gtk, Notify

from DebPackage import DebPackage, HAVE_APT

if HAVE_APT:
    import apt

locale.bindtextdomain('parslinux-package-installer', '/usr/share/locale')
locale.textdomain('parslinux-package-installer')

logger = logging.getLogger("parslinux-package-installer")


def load_stylesheet() -> None:
    """Load modern GTK stylesheet if available."""
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "style.css"),
        "/usr/share/parslinux/parslinux-package-installer/data/style.css"
    ]
    for css_path in candidates:
        if os.path.exists(css_path):
            try:
                provider = Gtk.CssProvider()
                provider.load_from_path(css_path)
                screen = Gdk.Screen.get_default()
                if screen:
                    Gtk.StyleContext.add_provider_for_screen(
                        screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                    )
                logger.debug("Loaded CSS from %s", css_path)
                break
            except Exception as e:
                logger.debug("Failed to load CSS: %s", e)


class MainWindow:
    def __init__(self, application: Gtk.Application, file: Optional[Gio.File]) -> None:
        load_stylesheet()

        self.closestatus: bool = False
        self.error: bool = False
        self.dpkglockerror: bool = False
        self.dpkgconferror: bool = False
        self.debianpackage: str = ""
        self.installable: bool = False
        self.packagename: str = ""
        self.packagefailure: str = ""
        self.file = file
        self.notificationstate: bool = True
        self.isinstalling: bool = False
        self.isbroken: bool = False
        self.debianpackage_errormsg: str = ""
        self.pid: Optional[int] = None
        self.package: Optional[DebPackage] = None
        self.cache: Optional[apt.Cache] = None if HAVE_APT else None

        # Gtk Builder UI file resolution
        ui_system = "/usr/share/parslinux/parslinux-package-installer/ui/MainWindow.glade"
        ui_local = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ui", "MainWindow.glade")

        if os.path.exists(ui_system):
            self.MainWindowUIFileName = ui_system
        else:
            self.MainWindowUIFileName = os.path.abspath(ui_local)

        self.builder = Gtk.Builder()
        self.builder.set_translation_domain("parslinux-package-installer")

        try:
            self.builder.add_from_file(self.MainWindowUIFileName)
            self.builder.connect_signals(self)
        except GObject.GError as e:
            logger.error("Error reading GUI file %s: %s", self.MainWindowUIFileName, e)
            raise

        self.window = self.builder.get_object("mainwindow")
        self.window.set_application(application)
        self.define_components()
        self.window.connect('delete_event', self.on_close)

        self.mainstack.set_visible_child_name("splash")

        # Set version from __version__ file or default
        try:
            ver_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "__version__")
            if os.path.exists(ver_file):
                with open(ver_file, "r", encoding="utf-8") as f:
                    version = f.readline().strip()
                self.about_dialog.set_version(version)
        except Exception:
            pass

        self.about_dialog.set_program_name(_("Pars Linux Package Installer"))
        if self.about_dialog.get_titlebar() is None:
            about_headerbar = Gtk.HeaderBar.new()
            about_headerbar.set_show_close_button(True)
            about_headerbar.set_title(_("About Pars Linux Package Installer"))
            about_headerbar.pack_start(
                Gtk.Image.new_from_icon_name("parslinux-package-installer", Gtk.IconSize.LARGE_TOOLBAR)
            )
            about_headerbar.show_all()
            self.about_dialog.set_titlebar(about_headerbar)

        self.window.drag_dest_set(
            Gtk.DestDefaults.ALL,
            [Gtk.TargetEntry.new("text/uri-list", 0, 0)],
            Gdk.DragAction.COPY
        )

        self.window.show_all()

        if self.isbroken:
            self.open_broken_dialog()

        self.openbutton.set_visible(False)
        self.progstack.set_visible(False)
        self.errorlabel.set_visible(False)
        self.BrokenBox.set_visible(False)
        self.outputSW.set_visible(False)

        threading.Thread(target=self.worker, daemon=True).start()

    def get_actions_script(self) -> str:
        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Actions.py")
        if os.path.exists(local_path):
            return local_path
        return "/usr/share/parslinux/parslinux-package-installer/src/Actions.py"

    def worker(self) -> None:
        result = self.initialize_backend()
        GLib.idle_add(self.initialize_ui, result)

    def initialize_backend(self) -> dict:
        if not self.file:
            return {"state": "empty"}

        if hasattr(self.file, "get_path"):
            self.debianpackage = os.path.abspath(self.file.get_path())
        elif isinstance(self.file, str):
            self.debianpackage = os.path.abspath(self.file)

        if not os.path.exists(self.debianpackage):
            return {
                "state": "broken",
                "error": f"File does not exist: {self.debianpackage}"
            }

        debianpackage_status = self.start(self.debianpackage)

        if debianpackage_status is None:
            return {
                "state": "broken",
                "error": self.debianpackage_errormsg
            }

        if debianpackage_status:
            return {
                "state": "ok",
                "firststatus": self.firststatus,
                "packagefailure": self.packagefailure
            }

        return {"state": "invalid"}

    def initialize_ui(self, result: dict) -> bool:
        state = result.get("state", "empty")

        self.button1.set_label(_("Install"))
        self.button2.set_label(_("Uninstall"))

        if state == "empty":
            self.mainstack.set_visible_child_name("empty")
            self.button1.set_sensitive(False)
            self.button2.set_sensitive(False)
            self._clear_package_labels()

        elif state == "broken":
            self._clear_package_labels()
            self.debpackage_brokenmsg.set_text(result.get("error", _("Broken package")))
            self.mainstack.set_visible_child_name("brokendeb")

        elif state == "invalid":
            self._clear_package_labels()
            self.open_broken_dialog()

        elif state == "ok":
            self.openbutton.set_visible(True)
            self.mainstack.set_visible_child_name("package")

            self.set_labels()
            self.package_main(
                False,
                result.get("firststatus", 0),
                result.get("packagefailure", "")
            )

        return False

    def _clear_package_labels(self) -> None:
        self.pacname.set_text("")
        self.pacversion.set_text("")
        self.shortdesc.set_text("")
        self.installed_version_title.set_text("")
        self.installed_version.set_text("")

    def set_labels(self) -> None:
        self.depends.set_text("")
        self.missingdeps.set_text("")
        self.mainstack.set_visible_child_name("package")
        self.progstack.set_visible(False)
        self.doneinfolabel.set_text("")
        self.errorlabel.set_visible(False)

        esc_name = GLib.markup_escape_text(self.packagename, -1)
        self.pacname.set_markup(f"<span size='x-large'><b>{esc_name}</b></span>")

        esc_ver = GLib.markup_escape_text(self.packageversion, -1)
        self.pacversion.set_markup(f"<small>{esc_ver}</small>")

        esc_desc = GLib.markup_escape_text(self.packageshortdescription, -1)
        self.shortdesc.set_markup(f"<small>{esc_desc}</small>")
        self.shortdesc.set_tooltip_text(self.packagedescription)

        self.maintainername.set_text(self.packagemaintainername)

        if self.packagemaintainermail != "-":
            mail = GLib.markup_escape_text(self.packagemaintainermail, -1)
            self.maintainermail.set_markup(f"<a title='{mail}' href='mailto:{mail}'>{mail}</a>")
        else:
            self.maintainermail.set_text(self.packagemaintainermail)

        if self.packagehomepage != "-":
            homepage = GLib.markup_escape_text(self.packagehomepage, -1)
            self.homepage.set_markup(f"<a title='{homepage}' href='{homepage}'>{homepage}</a>")
        else:
            self.homepage.set_text(self.packagehomepage)

        self.section.set_text(self.packagesection)
        self.architecture.set_text(self.packagearchitecture)

        if self.packagesize != "-":
            self.size.set_text(f"{self.packagesize} KiB")
        else:
            self.size.set_text(self.packagesize)

        pd = self.packagedepends or ""
        items = [item.strip() for item in pd.split(",") if item.strip()]
        formatted = [item.replace("|", " | ") for item in items]
        pd_text = "\n\n".join(formatted) if formatted else _("No dependencies")
        esc_pd = GLib.markup_escape_text(pd_text, -1)
        self.depends.set_markup(f"<small>{esc_pd}</small>")

        if self.packagemissingdeps:
            esc_missing = GLib.markup_escape_text(self.packagemissingdeps, -1)
            self.missingdeps.set_markup(
                f"<small><b><span color='red'>{_('Unsatisfied Dependencies:')}</span></b>\n{esc_missing}</small>"
            )
        else:
            self.missingdeps.set_markup(f"<small><span color='green'>{_('All dependencies are satisfied')}</span></small>")

        self.installed_version_title.set_markup(f"<small><span weight='light'>{_('Installed Version :')}</span></small>")

        installed_ver = self.package.get_installed_version() if self.package else None
        if installed_ver:
            self.installed_version.set_markup(f"<small><span weight='light'>{installed_ver}</span></small>")
        else:
            self.installed_version.set_markup(f"<small><span weight='light'>{_('Not installed')}</span></small>")

        self.progressbar.set_show_text(False)
        self.progressbar.set_fraction(0)

        # Populate files list
        if hasattr(self, "files_store") and self.package:
            self.files_store.clear()
            details = self.package.get_file_details()
            for d in details:
                icon = "folder-symbolic" if d["is_dir"] else (
                    "emblem-symbolic-link" if d["is_sym"] else (
                        "application-x-executable-symbolic" if d["is_exec"] else "text-x-generic-symbolic"
                    )
                )
                size_str = "-" if d["is_dir"] else self._format_size(d["size"])
                self.files_store.append([icon, d["name"], size_str, d["mode"]])
            if hasattr(self, "file_count_label") and self.file_count_label:
                self.file_count_label.set_text(f"{len(details)} dosya")

        self.window.set_focus(None)

    def package_main(self, actioned: bool, status: int, packagefailure: str) -> None:
        has_error = bool(packagefailure and "A later version is already installed" not in packagefailure)

        if has_error:
            self.errorlabel.set_visible(True)
            esc_fail = GLib.markup_escape_text(packagefailure, -1)
            self.errorlabel.set_markup(f"<b><span color='red'>{_('Error:')}</span></b>\n{esc_fail}")

        config = {
            0: (_("Install"), self.installicon, False),
            1: (_("Downgrade"), self.downgradeicon, True),
            2: (_("Reinstall"), self.reinstallicon, True),
            3: (_("Upgrade"), self.upgradeicon, True),
        }

        label, icon, allow_remove = config.get(status, config[0])

        self.button1.set_label(label)
        self.button1.set_image(icon)
        self.button1.set_sensitive(not has_error)
        self.button2.set_sensitive(allow_remove and not has_error)

    def on_mainwindow_drag_data_received(self, treeview, context, posx, posy, selection, info, timestamp) -> None:
        if self.pid:
            logger.warning("There is a process currently running.")
            return
        paths: List[str] = []
        for uri in selection.get_uris():
            file = Gio.File.new_for_uri(uri)
            p = file.get_path()
            if p and p.lower().endswith(".deb") and os.path.exists(p):
                paths.append(p)
        if len(paths) == 1:
            self.from_file(paths[0])
        elif len(paths) > 1:
            self.open_batch(paths)

    def define_components(self) -> None:
        self.button1 = self.builder.get_object("button1")
        self.button2 = self.builder.get_object("button2")
        self.openbutton = self.builder.get_object("openbutton")
        self.headerseperator = self.builder.get_object("headerseperator")
        self.filechooser = self.builder.get_object("filechooser")
        self.selectbutton = self.builder.get_object("selectbutton")
        self.aboutbutton = self.builder.get_object("aboutbutton")
        self.broken_close_button = self.builder.get_object("broken_close_button")
        self.debpackage_brokenmsg = self.builder.get_object("debpackage_brokenmsg")

        self.pacname = self.builder.get_object("pacname")
        self.shortdesc = self.builder.get_object("shortdesc")
        self.pacversion = self.builder.get_object("pacversion")
        self.namegrid = self.builder.get_object("namegrid")
        self.installedversiongrid = self.builder.get_object("installedversiongrid")
        self.bottomseparator = self.builder.get_object("bottomseparator")
        self.bottomlabel = self.builder.get_object("bottomlabel")
        self.errorlabel = self.builder.get_object("errorlabel")

        self.maintainername = self.builder.get_object("maintainername")
        self.maintainermail = self.builder.get_object("maintainermail")
        self.homepage = self.builder.get_object("homepage")
        self.section = self.builder.get_object("section")
        self.size = self.builder.get_object("size")
        self.architecture = self.builder.get_object("architecture")
        self.depends = self.builder.get_object("depends")
        self.missingdeps = self.builder.get_object("missingdeps")

        self.spinner = self.builder.get_object("spinner")
        self.progress = self.builder.get_object("progress")

        self.detailsbutton = self.builder.get_object("detailsbutton")
        self.detailsrevealer = self.builder.get_object("detailsrevealer")

        self.progstack = self.builder.get_object("progstack")
        self.progressbar = self.builder.get_object("progressbar")
        self.donebutton = self.builder.get_object("donebutton")
        self.doneinfolabel = self.builder.get_object("doneinfolabel")

        self.textview = self.builder.get_object("textview")
        self.descriptionscrolledwindow = self.builder.get_object("descriptionscrolledwindow")
        self.stack1 = self.builder.get_object("stack1")
        self.mainstack = self.builder.get_object("mainstack")

        self.installicon = self.builder.get_object("install_icon")
        self.upgradeicon = self.builder.get_object("upgrade_icon")
        self.downgradeicon = self.builder.get_object("downgrade_icon")
        self.reinstallicon = self.builder.get_object("reinstall_icon")

        self.installed_version = self.builder.get_object("installed_version")
        self.installed_version_title = self.builder.get_object("installed_version_title")

        self.outputSW = self.builder.get_object("outputSW")

        self.BrokenBox = self.builder.get_object("BrokenBox")
        self.cannotclose_dialog = self.builder.get_object("cannotclose_dialog")
        self.about_dialog = self.builder.get_object("about_dialog")

        # Files tab components
        self.files_treeview = self.builder.get_object("files_treeview")
        self.file_search_entry = self.builder.get_object("file_search_entry")
        self.file_count_label = self.builder.get_object("file_count_label")
        self.setup_files_view()

        # Batch installation components
        self.BatchBox = self.builder.get_object("BatchBox")
        self.batch_title = self.builder.get_object("batch_title")
        self.batch_subtitle = self.builder.get_object("batch_subtitle")
        self.batch_summary_label = self.builder.get_object("batch_summary_label")
        self.batch_treeview = self.builder.get_object("batch_treeview")
        self.batch_progressbar = self.builder.get_object("batch_progressbar")
        self.batch_progress_label = self.builder.get_object("batch_progress_label")
        self.batch_select_all_btn = self.builder.get_object("batch_select_all_btn")
        self.batch_add_btn = self.builder.get_object("batch_add_btn")
        self.batch_clear_btn = self.builder.get_object("batch_clear_btn")
        self.batch_install_btn = self.builder.get_object("batch_install_btn")
        self.batch_back_btn = self.builder.get_object("batch_back_btn")
        self.setup_batch_view()

    def start(self, debpackage: str) -> Optional[bool]:
        self.errorlabel.set_visible(False)
        self.errorlabel.set_text("")

        if self.update_cache():
            try:
                self.package = DebPackage(debpackage, cache=self.cache)
            except Exception as e:
                logger.error("Error loading package: %s", e)
                self.debianpackage_errormsg = str(e)
                return None

            self.packagename = self.package.pkgname
            self.firststatus = self.package.compare_to_version_in_cache()
            self.installable = self.package.check()

            self.packageversion = self.package.get("Version", "-")
            self.packagedescription = self.package.get("Description", "")
            lines = self.packagedescription.splitlines()
            self.packageshortdescription = lines[0] if lines else ""

            self.packagemaintainer = self.package.get("Maintainer", "-")
            if " <" in self.packagemaintainer:
                parts = self.packagemaintainer.split(" <")
                self.packagemaintainername = parts[0]
                self.packagemaintainermail = parts[1].replace(">", "")
            else:
                self.packagemaintainername = self.packagemaintainer
                self.packagemaintainermail = "-"

            self.packagehomepage = self.package.get("Homepage", "-")
            self.packagesection = self.package.get("Section", "-")
            self.packagesize = self.package.get("Installed-Size", "-")
            self.packagearchitecture = self.package.get("Architecture", "-")

            depends = self.package.get("Depends", "")
            recommends = self.package.get("Recommends", "")
            if depends and recommends:
                self.packagedepends = f"{depends}, {recommends}"
            else:
                self.packagedepends = depends or recommends

            missing = self.package.missing_deps or []
            self.packagemissingdeps = "\n\n".join(map(str, missing))
            self.packagefailure = self.package._failure_string or ""

            return True

        return False

    def update_cache(self) -> bool:
        if not HAVE_APT:
            self.cache = None
            self.isbroken = False
            return True
        try:
            self.cache = apt.Cache()
        except Exception as e:
            logger.debug("apt.Cache init failed: %s", e)
            self.cache = None
            self.isbroken = True
            return False
        if self.cache and self.cache.broken_count > 0:
            self.isbroken = True
            return False
        self.isbroken = False
        return True

    def compare_version(self) -> int:
        if self.package:
            return self.package.compare_to_version_in_cache()
        return 0

    def failure_control(self) -> str:
        if self.package:
            return self.package._failure_string or ""
        return ""

    def install_package(self, isupgrading: bool) -> None:
        if self.installable:
            self.isinstalling = True
            self.progressbar.set_show_text(False)
            self.progressbar.set_fraction(0)
            self.button1.set_sensitive(False)
            self.button2.set_sensitive(False)
            self.openbutton.set_sensitive(False)
            self.closestatus = True

            action_name = _("upgraded") if isupgrading else _("installed")
            self.notification = Notify.Notification.new(f"{self.packagename} {action_name}")

            self.command = ["/usr/bin/pkexec", self.get_actions_script(), "install", self.debianpackage]
            self.pid = self.start_process(self.command)
        else:
            logger.warning("Package is not installable")
            try:
                proc = Popen(["/usr/bin/dpkg", "--print-architecture"], stdout=PIPE, universal_newlines=True)
                self.systemarchitecture = proc.communicate()[0].strip()
            except Exception:
                self.systemarchitecture = "not detected"
            if self.packagearchitecture != self.systemarchitecture and self.packagearchitecture != "all":
                logger.error(
                    "Package Architecture = %s, System Architecture = %s",
                    self.packagearchitecture, self.systemarchitecture
                )
                self.doneinfolabel.set_markup(
                    f"<b><span color='red'>{_('Architecture Error!')}\n</span>"
                    f"{_('Package Architecture')}:{self.packagearchitecture}, "
                    f"{_('System Architecture')}:{self.systemarchitecture}</b>"
                )
                self.progstack.set_visible_child_name("doneinfo")
                self.notificationstate = False

    def remove_package(self) -> None:
        self.progressbar.set_show_text(False)
        self.progressbar.set_fraction(0)
        self.button1.set_sensitive(False)
        self.button2.set_sensitive(False)
        self.openbutton.set_sensitive(False)
        self.closestatus = True
        self.notification = Notify.Notification.new(f"{self.packagename} {_('removed')}")

        self.command = ["/usr/bin/pkexec", self.get_actions_script(), "remove", self.packagename]
        self.pid = self.start_process(self.command)

    def reinstall_package(self) -> None:
        self.progressbar.set_show_text(False)
        self.progressbar.set_fraction(0)
        self.button1.set_sensitive(False)
        self.button2.set_sensitive(False)
        self.openbutton.set_sensitive(False)
        self.closestatus = True
        self.notification = Notify.Notification.new(f"{self.packagename} {_('reinstalled')}")

        self.command = ["/usr/bin/pkexec", self.get_actions_script(), "reinstall", self.debianpackage]
        self.pid = self.start_process(self.command)

    def downgrade_package(self) -> None:
        self.progressbar.set_show_text(False)
        self.progressbar.set_fraction(0)
        self.button1.set_sensitive(False)
        self.button2.set_sensitive(False)
        self.openbutton.set_sensitive(False)
        self.closestatus = True
        self.notification = Notify.Notification.new(f"{self.packagename} {_('downgraded')}")

        self.command = ["/usr/bin/pkexec", self.get_actions_script(), "downgrade", self.debianpackage]
        self.pid = self.start_process(self.command)

    def on_button1_clicked(self, button: Gtk.Button) -> None:
        self.error = False
        self.dpkglockerror = False
        self.dpkgconferror = False
        self.progstack.set_visible(True)
        self.progstack.set_visible_child_name("progress")
        self.outputSW.set_visible(True)
        self.status = self.compare_version()

        if self.status == 0:
            self.packageaction = _("Installing")
            self.install_package(False)
        elif self.status == 1:
            self.packageaction = _("Downgrading")
            self.downgrade_package()
        elif self.status == 2:
            self.packageaction = _("Reinstalling")
            self.reinstall_package()
        elif self.status == 3:
            self.packageaction = _("Upgrading")
            self.install_package(True)

    def on_button2_clicked(self, button: Gtk.Button) -> None:
        self.packageaction = _("Uninstalling")
        self.progstack.set_visible(True)
        self.progstack.set_visible_child_name("progress")
        self.outputSW.set_visible(True)
        self.remove_package()

    def on_donebutton_clicked(self, button: Gtk.Button) -> None:
        self.window.get_application().quit()

    def on_openbutton_clicked(self, button: Gtk.Button) -> None:
        self.filechooser.set_select_multiple(True)
        res = self.filechooser.run()
        if res in (Gtk.ResponseType.ACCEPT, Gtk.ResponseType.OK, -5):
            filenames = self.filechooser.get_filenames()
            self.filechooser.hide()
            if len(filenames) == 1:
                self.from_file(filenames[0])
            elif len(filenames) > 1:
                self.open_batch(filenames)
        else:
            self.filechooser.hide()

    def on_selectbutton_clicked(self, widget: Gtk.Widget) -> None:
        self.filechooser.set_select_multiple(True)
        filenames = self.filechooser.get_filenames()
        self.filechooser.hide()
        if len(filenames) == 1:
            self.from_file(filenames[0])
        elif len(filenames) > 1:
            self.open_batch(filenames)

    def on_filechooser_file_activated(self, widget: Gtk.Widget) -> None:
        self.filechooser.set_select_multiple(True)
        filenames = self.filechooser.get_filenames()
        self.filechooser.hide()
        if len(filenames) == 1:
            self.from_file(filenames[0])
        elif len(filenames) > 1:
            self.open_batch(filenames)

    def on_aboutbutton_clicked(self, button: Gtk.Button) -> None:
        self.about_dialog.run()
        self.about_dialog.hide()

    def on_detailsbutton_toggled(self, button: Gtk.ToggleButton) -> None:
        self.detailsrevealer.set_reveal_child(button.get_active())

    def open_broken_dialog(self) -> None:
        self.BrokenBox.set_visible(True)
        self.mainstack.set_visible_child_name("broken")

    def on_detailsbutton_clicked(self, button: Gtk.Button) -> None:
        current = self.detailsrevealer.get_reveal_child()
        self.detailsrevealer.set_reveal_child(not current)
        self.detailsbutton.set_label(_("Show Details") if current else _("Hide Details"))

    def from_file(self, path: str) -> None:
        self.openbutton.set_visible(True)

        # Clear output textbuffer
        self.outputSW.set_visible(False)
        start, end = self.textview.get_buffer().get_bounds()
        self.textview.get_buffer().delete(start, end)

        ext = os.path.basename(path).split(".")[-1].lower()
        if ext == "deb":
            self.debianpackage = os.path.abspath(path)
            debianpackage_status = self.start(self.debianpackage)
            if debianpackage_status is not None:
                if debianpackage_status:
                    self.set_labels()
                    self.package_main(False, self.firststatus, self.packagefailure)
                else:
                    self.button1.set_sensitive(False)
                    self.button2.set_sensitive(False)
                    self.button1.set_label(_("Install"))
                    self.button2.set_label(_("Uninstall"))
                    self._clear_package_labels()
                    self.open_broken_dialog()
            else:
                self.button1.set_sensitive(False)
                self.button2.set_sensitive(False)
                self.button1.set_label(_("Install"))
                self.button2.set_label(_("Uninstall"))
                self._clear_package_labels()
                self.debpackage_brokenmsg.set_text(self.debianpackage_errormsg)
                self.mainstack.set_visible_child_name("brokendeb")
        else:
            logger.warning("Only .deb files are supported: %s", path)

    def on_close(self, *args) -> bool:
        if self.closestatus:
            self.cannotclose_dialog.run()
            self.cannotclose_dialog.hide()
            return True
        return self.closestatus

    def start_process(self, params: List[str]) -> int:
        pid, stdin, stdout, stderr = GLib.spawn_async(
            params, flags=GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            standard_output=True, standard_error=True
        )
        GLib.io_add_watch(GLib.IOChannel(stdout), GLib.IO_IN | GLib.IO_HUP, self.on_process_stdout)
        GLib.io_add_watch(GLib.IOChannel(stderr), GLib.IO_IN | GLib.IO_HUP, self.on_process_stderr)
        GLib.child_watch_add(GLib.PRIORITY_DEFAULT, pid, self.on_process_exit)
        return pid

    def on_process_stdout(self, source, condition) -> bool:
        if condition == GLib.IO_HUP:
            return False
        line = source.readline()
        if not line:
            return False
        self.textview.get_buffer().insert(self.textview.get_buffer().get_end_iter(), line)
        self.textview.scroll_to_iter(self.textview.get_buffer().get_end_iter(), 0.0, False, 0.0, 0.0)
        return True

    def on_process_stderr(self, source, condition) -> bool:
        if condition == GLib.IO_HUP:
            return False
        line = source.readline()
        if not line:
            return False

        if "dlstatus" in line:
            parts = line.split(":")
            if len(parts) >= 3:
                try:
                    percent = parts[2].split(".")[0]
                    self.progressbar.set_show_text(True)
                    self.progressbar.set_text(f"{percent} %")
                    self.progressbar.set_fraction(int(percent) / 100)
                except ValueError:
                    pass
        elif "pmstatus" in line:
            parts = line.split(":")
            if len(parts) >= 3:
                try:
                    percent = parts[2].split(".")[0]
                    self.progressbar.set_show_text(True)
                    self.progressbar.set_text(f"{self.packageaction} {percent} %")
                    self.progressbar.set_fraction(int(percent) / 100)
                except ValueError:
                    pass
        line_clean = line.strip()
        line_lower = line_clean.lower()
        if "dpkg --configure -a" in line:
            logger.error("dpkg interrupt error detected")
            self.error = True
            self.dpkgconferror = True
        elif "/var/lib/dpkg/lock" in line or "could not get lock" in line_lower:
            logger.error("Dpkg lock contention error detected")
            self.error = True
            self.dpkglockerror = True
        elif (".deb" in line or "fetch" in line_lower or "http" in line_lower) and (
            re.match(r"^\w+:", line_clean, re.UNICODE) or any(k in line_lower for k in ("error", "hata", "erro", "failed", "başarısız"))
        ):
            logger.error("Connection or package download error detected")
            self.error = True

        self.textview.get_buffer().insert(self.textview.get_buffer().get_end_iter(), line)
        self.textview.scroll_to_iter(self.textview.get_buffer().get_end_iter(), 0.0, False, 0.0, 0.0)
        return True

    def on_process_exit(self, pid: int, retval: int) -> None:
        logger.info("Process finished with return code: %d", retval)
        self.pid = None
        if not self.error:
            if retval == 0:
                self.notificationstate = True
                if self.progressbar.get_show_text():
                    self.progressbar.set_text("100 %")
                    self.progressbar.set_fraction(1)
                self.progstack.set_visible_child_name("done")
            else:
                self.progstack.set_visible_child_name("doneinfo")
                self.doneinfolabel.set_markup(f"<b>{_('Not Completed !')}</b>")
                self.notificationstate = False
        else:
            errormessage = f"<b><span color='red'>{_('Connection Error !')}</span></b>"
            if self.dpkglockerror:
                errormessage = f"<b><span color='red'>{_('Dpkg Lock Error !')}</span></b>"
            elif self.dpkgconferror:
                errormessage = f"<b><span color='red'>{_('Dpkg Interrupt Error !')}</span></b>"
            self.doneinfolabel.set_markup(errormessage)
            self.notificationstate = False
            if self.progressbar.get_show_text():
                self.progressbar.set_show_text(False)
                self.progressbar.set_fraction(0)
            self.progstack.set_visible_child_name("doneinfo")

        self.update_cache()
        self.status = self.compare_version()
        self.packagefailure = self.failure_control()
        self.package_main(True, self.status, self.packagefailure)

        installed_ver = self.package.get_installed_version() if self.package else None
        if installed_ver:
            self.installed_version.set_markup(f"<small><span weight='light'>{installed_ver}</span></small>")
        else:
            self.installed_version.set_markup(f"<small><span weight='light'>{_('Not installed')}</span></small>")

        self.openbutton.set_sensitive(True)
        self.closestatus = False

        if self.isinstalling and self.status == 0 and retval == 0:
            logger.warning("Connection lost / package not verified as installed")
            errormessage = f"<b><span color='red'>{_('Connection Error !')}</span></b>"
            if self.dpkglockerror:
                errormessage = f"<b><span color='red'>{_('Dpkg Lock Error !')}</span></b>"
            elif self.dpkgconferror:
                errormessage = f"<b><span color='red'>{_('Dpkg Interrupt Error !')}</span></b>"
            self.doneinfolabel.set_markup(errormessage)
            if self.progressbar.get_show_text():
                self.progressbar.set_show_text(False)
                self.progressbar.set_fraction(0)
            self.progstack.set_visible_child_name("doneinfo")
            self.notificationstate = False

        if self.notificationstate and self.notification:
            self.notify()

    def notify(self) -> None:
        try:
            self.notification.set_icon_name("parslinux-package-installer")
            self.notification.show()
        except Exception as e:
            logger.debug("Notification could not be shown: %s", e)

    @staticmethod
    def _format_size(num_bytes) -> str:
        if not num_bytes or num_bytes == "-":
            return "-"
        try:
            n = float(num_bytes)
            for unit in ["B", "KiB", "MiB", "GiB"]:
                if n < 1024.0:
                    return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
                n /= 1024.0
            return f"{n:.1f} TiB"
        except Exception:
            return str(num_bytes)

    def setup_files_view(self) -> None:
        if not self.files_treeview:
            return
        self.files_store = Gtk.ListStore(str, str, str, str)
        self.files_filter = self.files_store.filter_new()
        self.files_filter.set_visible_func(self.files_filter_func)
        self.files_treeview.set_model(self.files_filter)

        for col in self.files_treeview.get_columns():
            self.files_treeview.remove_column(col)

        col_file = Gtk.TreeViewColumn(_("Dosya Yolu"))
        col_file.set_resizable(True)
        col_file.set_expand(True)

        cr_icon = Gtk.CellRendererPixbuf()
        col_file.pack_start(cr_icon, False)
        col_file.add_attribute(cr_icon, "icon-name", 0)

        cr_text = Gtk.CellRendererText()
        cr_text.set_property("ellipsize", 1)
        col_file.pack_start(cr_text, True)
        col_file.add_attribute(cr_text, "text", 1)
        self.files_treeview.append_column(col_file)

        col_size = Gtk.TreeViewColumn(_("Boyut"))
        col_size.set_resizable(True)
        cr_size = Gtk.CellRendererText(xalign=1.0)
        col_size.pack_start(cr_size, False)
        col_size.add_attribute(cr_size, "text", 2)
        self.files_treeview.append_column(col_size)

        if self.file_search_entry:
            self.file_search_entry.connect("search-changed", self.on_file_search_changed)

    def files_filter_func(self, model: Gtk.TreeModel, iter: Gtk.TreeIter, data) -> bool:
        if not self.file_search_entry:
            return True
        query = self.file_search_entry.get_text().strip().lower()
        if not query:
            return True
        val = model.get_value(iter, 1)
        return query in (val.lower() if val else "")

    def on_file_search_changed(self, entry: Gtk.SearchEntry) -> None:
        if hasattr(self, "files_filter"):
            self.files_filter.refilter()
            query = entry.get_text().strip()
            total = len(self.files_store)
            if query:
                matching = sum(1 for row in self.files_store if query.lower() in row[1].lower())
                self.file_count_label.set_text(f"{matching} / {total} eşleşti")
            else:
                self.file_count_label.set_text(f"{total} dosya")

    def setup_batch_view(self) -> None:
        if not self.batch_treeview:
            return
        self.batch_store = Gtk.ListStore(bool, str, str, str, str, str, str)
        self.batch_treeview.set_model(self.batch_store)

        for col in self.batch_treeview.get_columns():
            self.batch_treeview.remove_column(col)

        col_check = Gtk.TreeViewColumn("")
        cr_toggle = Gtk.CellRendererToggle()
        cr_toggle.connect("toggled", self.on_batch_row_toggled)
        col_check.pack_start(cr_toggle, False)
        col_check.add_attribute(cr_toggle, "active", 0)
        self.batch_treeview.append_column(col_check)

        col_icon = Gtk.TreeViewColumn("")
        cr_status_icon = Gtk.CellRendererPixbuf()
        col_icon.pack_start(cr_status_icon, False)
        col_icon.add_attribute(cr_status_icon, "icon-name", 1)
        self.batch_treeview.append_column(col_icon)

        col_pkg = Gtk.TreeViewColumn(_("Paket"))
        col_pkg.set_resizable(True)
        col_pkg.set_expand(True)
        cr_pkg = Gtk.CellRendererText(weight=600)
        col_pkg.pack_start(cr_pkg, True)
        col_pkg.add_attribute(cr_pkg, "text", 2)
        self.batch_treeview.append_column(col_pkg)

        col_ver = Gtk.TreeViewColumn(_("Sürüm"))
        col_ver.set_resizable(True)
        cr_ver = Gtk.CellRendererText()
        col_ver.pack_start(cr_ver, False)
        col_ver.add_attribute(cr_ver, "text", 3)
        self.batch_treeview.append_column(col_ver)

        col_stat = Gtk.TreeViewColumn(_("Durum"))
        col_stat.set_resizable(True)
        cr_stat = Gtk.CellRendererText()
        col_stat.pack_start(cr_stat, False)
        col_stat.add_attribute(cr_stat, "text", 4)
        self.batch_treeview.append_column(col_stat)

        col_size = Gtk.TreeViewColumn(_("Boyut"))
        col_size.set_resizable(True)
        cr_size = Gtk.CellRendererText(xalign=1.0)
        col_size.pack_start(cr_size, False)
        col_size.add_attribute(cr_size, "text", 5)
        self.batch_treeview.append_column(col_size)

        if self.batch_select_all_btn:
            self.batch_select_all_btn.connect("clicked", self.on_batch_select_all_clicked)
        if self.batch_add_btn:
            self.batch_add_btn.connect("clicked", self.on_batch_add_btn_clicked)
        if self.batch_clear_btn:
            self.batch_clear_btn.connect("clicked", self.on_batch_clear_btn_clicked)
        if self.batch_back_btn:
            self.batch_back_btn.connect("clicked", self.on_batch_back_btn_clicked)
        if self.batch_install_btn:
            self.batch_install_btn.connect("clicked", self.on_batch_install_btn_clicked)

    def on_batch_row_toggled(self, cell: Gtk.CellRendererToggle, path_str: str) -> None:
        self.batch_store[path_str][0] = not self.batch_store[path_str][0]
        has_selected = any(row[0] for row in self.batch_store)
        if self.batch_install_btn:
            self.batch_install_btn.set_sensitive(has_selected)

    def on_batch_select_all_clicked(self, button: Gtk.Button) -> None:
        all_selected = all(row[0] for row in self.batch_store)
        new_state = not all_selected
        for row in self.batch_store:
            row[0] = new_state
        if self.batch_install_btn:
            self.batch_install_btn.set_sensitive(new_state and len(self.batch_store) > 0)

    def on_batch_clear_btn_clicked(self, button: Gtk.Button) -> None:
        self.batch_store.clear()
        self.mainstack.set_visible_child_name("empty")
        self.openbutton.set_visible(False)

    def on_batch_back_btn_clicked(self, button: Gtk.Button) -> None:
        if self.debianpackage and os.path.exists(self.debianpackage):
            self.mainstack.set_visible_child_name("package")
        else:
            self.mainstack.set_visible_child_name("empty")

    def on_batch_add_btn_clicked(self, button: Gtk.Button) -> None:
        self.filechooser.set_select_multiple(True)
        res = self.filechooser.run()
        if res in (Gtk.ResponseType.ACCEPT, Gtk.ResponseType.OK, -5):
            filenames = self.filechooser.get_filenames()
            self.filechooser.hide()
            if filenames:
                self.add_to_batch(filenames)
        else:
            self.filechooser.hide()

    def open_batch(self, file_paths: List[str]) -> None:
        self.batch_store.clear()
        self.add_to_batch(file_paths)

    def add_to_batch(self, file_paths: List[str]) -> None:
        self.openbutton.set_visible(True)
        self.mainstack.set_visible_child_name("batch")

        existing_paths = {row[6] for row in self.batch_store}
        self.update_cache()

        for fp in file_paths:
            fp = os.path.abspath(fp)
            if fp in existing_paths or not os.path.exists(fp) or not fp.lower().endswith(".deb"):
                continue
            try:
                pkg = DebPackage(fp, cache=self.cache)
                pkgname = pkg.pkgname
                version = pkg.get("Version", "-")
                raw_size = pkg.get("Installed-Size", "0")
                try:
                    size_kb = int(raw_size) * 1024
                    size_str = self._format_size(size_kb)
                except Exception:
                    size_str = raw_size

                check_status = pkg.compare_to_version_in_cache()
                status_desc = {
                    0: _("Kurulabilir"),
                    1: _("Sürüm Düşürülebilir"),
                    2: _("Zaten Kurulu"),
                    3: _("Yükseltilebilir")
                }.get(check_status, _("Kurulabilir"))

                icon = "emblem-default-symbolic"
                self.batch_store.append([True, icon, pkgname, version, status_desc, size_str, fp])
                existing_paths.add(fp)
            except Exception as e:
                logger.error("Error parsing %s in batch: %s", fp, e)
                self.batch_store.append([
                    False, "dialog-error-symbolic", os.path.basename(fp),
                    "-", _("Geçersiz Paket"), "-", fp
                ])

        total_pkgs = len(self.batch_store)
        selected_pkgs = sum(1 for row in self.batch_store if row[0])
        self.batch_subtitle.set_text(f"{total_pkgs} paket kuyrukta")
        self.batch_summary_label.set_text(f"{selected_pkgs} paket seçili")
        if self.batch_install_btn:
            self.batch_install_btn.set_sensitive(selected_pkgs > 0)
        self.batch_progressbar.set_visible(False)
        self.batch_progress_label.set_visible(False)

    def on_batch_install_btn_clicked(self, button: Gtk.Button) -> None:
        items = []
        for i, row in enumerate(self.batch_store):
            if row[0]:
                items.append((i, row[6], row[2]))

        if not items:
            return

        self.batch_install_btn.set_sensitive(False)
        self.batch_select_all_btn.set_sensitive(False)
        self.batch_add_btn.set_sensitive(False)
        self.batch_clear_btn.set_sensitive(False)
        self.batch_back_btn.set_sensitive(False)

        self.batch_progressbar.set_visible(True)
        self.batch_progress_label.set_visible(True)
        self.batch_progressbar.set_fraction(0.0)
        self.batch_progressbar.set_text(_("Toplu kurulum başlatılıyor..."))

        threading.Thread(target=self._batch_worker, args=(items,), daemon=True).start()

    def _batch_worker(self, items: List[Tuple[int, str, str]]) -> None:
        actions_script = self.get_actions_script()
        total = len(items)

        # 1. Set all items to working status in UI
        def set_all_working():
            for row_idx, _, pkgname in items:
                self.batch_store[row_idx][1] = "process-working-symbolic"
                self.batch_store[row_idx][4] = _("Kuruluyor...")
            self.batch_progressbar.set_fraction(0.3)
            self.batch_progressbar.set_text(f"{total} {_('paket kuruluyor...')}")
            self.batch_progress_label.set_text(_("Tek işlemde toplu APT kurulumu yürütülüyor..."))
        GLib.idle_add(set_all_working)

        # 2. Run unified batch installation via pkexec Actions.py install *paths
        deb_paths = [fp for _, fp, _ in items]
        cmd = ["pkexec", actions_script, "install", *deb_paths]
        try:
            proc = Popen(cmd, stdout=PIPE, stderr=PIPE, text=True)
            proc.communicate()
            success = (proc.returncode == 0)
        except Exception as e:
            logger.error("Failed to run batch action: %s", e)
            success = False

        # 3. Update result on each item in UI
        def update_results():
            for row_idx, fp, pkgname in items:
                if success:
                    self.batch_store[row_idx][1] = "emblem-ok-symbolic"
                    self.batch_store[row_idx][4] = _("Kuruldu")
                else:
                    # Check if specifically this package got installed anyway
                    is_inst = False
                    if os.path.exists("/usr/bin/dpkg-query"):
                        try:
                            check = subprocess.run(["dpkg-query", "-W", "-f=${Status}", pkgname],
                                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
                            is_inst = "install ok installed" in check.stdout
                        except Exception:
                            pass
                    if is_inst:
                        self.batch_store[row_idx][1] = "emblem-ok-symbolic"
                        self.batch_store[row_idx][4] = _("Kuruldu")
                    else:
                        self.batch_store[row_idx][1] = "dialog-error-symbolic"
                        self.batch_store[row_idx][4] = _("Hata!")

            self.batch_progressbar.set_fraction(1.0)
            status_text = _("Toplu kurulum tamamlandı") if success else _("İşlem hatalarla tamamlandı")
            self.batch_progressbar.set_text(status_text)
            self.batch_progress_label.set_text(
                _("Tüm paketler başarıyla kuruldu.") if success else _("Bazı paketler kurulamadı.")
            )
            self.batch_install_btn.set_sensitive(True)
            self.batch_select_all_btn.set_sensitive(True)
            self.batch_add_btn.set_sensitive(True)
            self.batch_clear_btn.set_sensitive(True)
            self.batch_back_btn.set_sensitive(True)
            try:
                notif = Notify.Notification.new(_("Toplu Kurulum"), status_text, "package-x-generic")
                notif.show()
            except Exception:
                pass
        GLib.idle_add(update_results)
