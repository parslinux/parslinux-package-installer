#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MainWindow for parslinux-package-installer.
Provides graphical package installation, removal, dependency verification,
and detailed inspection of .deb packages.
"""

import locale
from locale import gettext as _
import os
import re
from subprocess import PIPE, Popen
import sys
import threading

import gi

gi.require_version('Gtk', '3.0')
gi.require_version("Notify", "0.7")
from gi.repository import Gdk, Gio, GLib, GObject, Gtk, Notify

from DebPackage import DebPackage, HAVE_APT

if HAVE_APT:
    import apt

locale.bindtextdomain('parslinux-package-installer', '/usr/share/locale')
locale.textdomain('parslinux-package-installer')


class MainWindow(object):
    def __init__(self, application, file):
        self.closestatus = False
        self.error = False
        self.dpkglockerror = False
        self.dpkgconferror = False
        self.debianpackage = ""
        self.installable = False
        self.packagename = ""
        self.packagefailure = ""
        self.file = file
        self.notificationstate = True
        self.isinstalling = False
        self.isbroken = False
        self.debianpackage_errormsg = ""
        self.pid = None
        self.package = None
        self.cache = None

        # Gtk Builder UI file resolution
        ui_system = "/usr/share/parslinux/parslinux-package-installer/ui/MainWindow.glade"
        ui_local = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ui", "MainWindow.glade")
        if os.path.exists(ui_system):
            self.MainWindowUIFileName = ui_system
        else:
            self.MainWindowUIFileName = os.path.abspath(ui_local)

        try:
            self.builder = Gtk.Builder.new_from_file(self.MainWindowUIFileName)
            self.builder.connect_signals(self)
        except GObject.GError:
            print("Error reading GUI file: " + self.MainWindowUIFileName)
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
                version = open(ver_file).readline().strip()
                self.about_dialog.set_version(version)
        except Exception:
            pass

        self.about_dialog.set_program_name(_("Pars Linux Package Installer"))
        if self.about_dialog.get_titlebar() is None:
            about_headerbar = Gtk.HeaderBar.new()
            about_headerbar.set_show_close_button(True)
            about_headerbar.set_title(_("About Pars Linux Package Installer"))
            about_headerbar.pack_start(
                Gtk.Image.new_from_icon_name("parslinux-package-installer", Gtk.IconSize.LARGE_TOOLBAR))
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

    def get_actions_script(self):
        """Resolve path to Actions.py script."""
        system_path = "/usr/share/parslinux/parslinux-package-installer/src/Actions.py"
        if os.path.exists(system_path):
            return system_path
        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Actions.py")
        if os.path.exists(local_path):
            return local_path
        return system_path

    def worker(self):
        result = self.initialize_backend()
        GLib.idle_add(self.initialize_ui, result)

    def initialize_backend(self):
        if not self.file:
            # Check if an argument was passed on command line
            if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and os.path.exists(sys.argv[1]):
                self.debianpackage = os.path.abspath(sys.argv[1])
            else:
                return {"state": "empty"}
        else:
            if hasattr(self.file, "get_path"):
                self.debianpackage = os.path.abspath(self.file.get_path())
            elif isinstance(self.file, str):
                self.debianpackage = os.path.abspath(self.file)
            else:
                return {"state": "empty"}

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

    def initialize_ui(self, result):
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

    def _clear_package_labels(self):
        self.pacname.set_text("")
        self.pacversion.set_text("")
        self.shortdesc.set_text("")
        self.installed_version_title.set_text("")
        self.installed_version.set_text("")

    def set_labels(self):
        self.depends.set_text("")
        self.missingdeps.set_text("")
        self.mainstack.set_visible_child_name("package")
        self.progstack.set_visible(False)
        self.doneinfolabel.set_text("")
        self.errorlabel.set_visible(False)

        self.pacname.set_markup(
            "<span size='x-large'><b>{}</b></span>".format(
                GLib.markup_escape_text(self.packagename, -1)
            )
        )

        self.pacversion.set_markup(
            "<small>{}</small>".format(
                GLib.markup_escape_text(self.packageversion, -1)
            )
        )

        self.shortdesc.set_markup(
            "<small>{}</small>".format(
                GLib.markup_escape_text(self.packageshortdescription, -1)
            )
        )
        self.shortdesc.set_tooltip_text(self.packagedescription)

        self.maintainername.set_text(self.packagemaintainername)

        if self.packagemaintainermail != "-":
            mail = GLib.markup_escape_text(self.packagemaintainermail, -1)
            self.maintainermail.set_markup(
                f"<a title='{mail}' href='mailto:{mail}'>{mail}</a>"
            )
        else:
            self.maintainermail.set_text(self.packagemaintainermail)

        if self.packagehomepage != "-":
            homepage = GLib.markup_escape_text(self.packagehomepage, -1)
            self.homepage.set_markup(
                f"<a title='{homepage}' href='{homepage}'>{homepage}</a>"
            )
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
        formatted = []
        for item in items:
            formatted.append(item.replace("|", " | "))
        pd = "\n\n".join(formatted) if formatted else _("No dependencies")
        self.depends.set_markup("<small>{}</small>".format(GLib.markup_escape_text(pd, -1)))

        if self.packagemissingdeps:
            self.missingdeps.set_markup("<small><b><span color='red'>{}</span></b>\n{}</small>".format(
                _("Unsatisfied Dependencies:"),
                GLib.markup_escape_text(self.packagemissingdeps, -1)))
        else:
            self.missingdeps.set_markup("<small><span color='green'>{}</span></small>".format(
                _("All dependencies are satisfied")))

        self.installed_version_title.set_markup(
            "<small><span weight='light'>{}</span></small>".format(_("Installed Version :")))

        installed_ver = None
        if self.package:
            installed_ver = self.package.get_installed_version()

        if installed_ver:
            self.installed_version.set_markup(f"<small><span weight='light'>{installed_ver}</span></small>")
        else:
            self.installed_version.set_markup(
                "<small><span weight='light'>{}</span></small>".format(_("Not installed")))

        self.progressbar.set_show_text(False)
        self.progressbar.set_fraction(0)

        self.window.set_focus(None)

    def package_main(self, actioned, status, packagefailure):
        has_error = bool(packagefailure and "A later version is already installed" not in packagefailure)

        if has_error:
            self.errorlabel.set_visible(True)
            self.errorlabel.set_markup(
                "<b><span color='red'>{}</span></b>\n{}".format(
                    _("Error !"),
                    GLib.markup_escape_text(packagefailure, -1)
                )
            )

        # Status meanings:
        # VERSION_NONE = 0      (Not installed)
        # VERSION_OUTDATED = 1  (Downgrade)
        # VERSION_SAME = 2      (Reinstall)
        # VERSION_NEWER = 3     (Upgrade)
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

    def on_mainwindow_drag_data_received(self, treeview, context, posx, posy, selection, info, timestamp):
        if self.pid:
            print("There is a process currently running.")
            return
        for uri in selection.get_uris():
            file = Gio.File.new_for_uri(uri)
            path = file.get_path()
            if path:
                self.from_file(path)

    def define_components(self):
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

    def start(self, debpackage):
        self.errorlabel.set_visible(False)
        self.errorlabel.set_text("")

        if self.update_cache():
            try:
                self.package = DebPackage(debpackage, cache=self.cache)
            except Exception as e:
                print(f"Error loading package: {e}")
                self.debianpackage_errormsg = str(e)
                return None

            self.packagename = self.package.pkgname
            self.firststatus = self.package.compare_to_version_in_cache()
            self.installable = self.package.check()

            self.packageversion = self.package.get("Version", "-")
            self.packagedescription = self.package.get("Description", "")
            self.packageshortdescription = self.packagedescription.split("\n")[0] if self.packagedescription else ""

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

    def update_cache(self):
        if not HAVE_APT:
            self.cache = None
            self.isbroken = False
            return True
        try:
            self.cache = apt.Cache()
        except Exception:
            self.cache = None
            self.isbroken = True
            return False
        if self.cache and self.cache.broken_count > 0:
            self.isbroken = True
            return False
        self.isbroken = False
        return True

    def compare_version(self):
        if self.package:
            return self.package.compare_to_version_in_cache()
        return 0

    def failure_control(self):
        if self.package:
            return self.package._failure_string
        return ""

    def install_package(self, isupgrading):
        if self.installable:
            self.isinstalling = True
            self.progressbar.set_show_text(False)
            self.progressbar.set_fraction(0)
            self.button1.set_sensitive(False)
            self.button2.set_sensitive(False)
            self.openbutton.set_sensitive(False)
            self.closestatus = True
            if isupgrading:
                self.notification = Notify.Notification.new(self.packagename + _(" upgraded"))
            else:
                self.notification = Notify.Notification.new(self.packagename + _(" installed"))

            self.command = ["/usr/bin/pkexec", self.get_actions_script(), "install", self.debianpackage]
            self.pid = self.start_process(self.command)
        else:
            print("package is not installable")
            try:
                self.systemarchitecture = Popen(["/usr/bin/dpkg", "--print-architecture"],
                                                stdout=PIPE, universal_newlines=True).communicate()[0].strip()
            except Exception:
                self.systemarchitecture = "not detected"
            if self.packagearchitecture != self.systemarchitecture and self.packagearchitecture != "all":
                print(f"Error: Package Architecture = {self.packagearchitecture}, System Architecture = {self.systemarchitecture}")
                self.button1.set_sensitive(False)
                self.button2.set_sensitive(False)
                self.progstack.set_visible(True)
                self.progstack.set_visible_child_name("doneinfo")
                self.doneinfolabel.set_markup("<b><span color='red'>{}\n</span>{}:{}, {}:{}".format(
                    _("Package Architecture Error"), _("System"), self.systemarchitecture, _("Package"),
                    self.packagearchitecture))

    def remove_package(self):
        self.progressbar.set_show_text(False)
        self.progressbar.set_fraction(0)
        self.button1.set_sensitive(False)
        self.button2.set_sensitive(False)
        self.openbutton.set_sensitive(False)
        self.closestatus = True
        self.notification = Notify.Notification.new(self.packagename + _(" uninstalled"))
        self.command = ["/usr/bin/pkexec", self.get_actions_script(), "remove", self.packagename]
        self.pid = self.start_process(self.command)

    def reinstall_package(self):
        self.progressbar.set_show_text(False)
        self.progressbar.set_fraction(0)
        self.button1.set_sensitive(False)
        self.button2.set_sensitive(False)
        self.openbutton.set_sensitive(False)
        self.closestatus = True
        self.notification = Notify.Notification.new(self.packagename + _(" reinstalled"))
        self.command = ["/usr/bin/pkexec", self.get_actions_script(), "reinstall", self.debianpackage]
        self.pid = self.start_process(self.command)

    def downgrade_package(self):
        self.progressbar.set_show_text(False)
        self.progressbar.set_fraction(0)
        self.button1.set_sensitive(False)
        self.button2.set_sensitive(False)
        self.openbutton.set_sensitive(False)
        self.closestatus = True
        self.notification = Notify.Notification.new(self.packagename + _(" downgraded"))
        self.command = ["/usr/bin/pkexec", self.get_actions_script(), "downgrade", self.debianpackage]
        self.pid = self.start_process(self.command)

    def on_button1_clicked(self, button):
        print("debianpackage = " + self.debianpackage)
        packagestatus = self.compare_version()
        self.progstack.set_visible(True)
        self.progstack.set_visible_child_name("progress")
        self.outputSW.set_visible(True)

        if packagestatus == 0:
            print("Installing Button Clicked")
            self.packageaction = _("Installing")
            self.install_package(False)

        elif packagestatus == 1:
            self.packageaction = _("Downgrading")
            print("Downgrading Button Clicked")
            self.downgrade_package()

        elif packagestatus == 2:
            self.packageaction = _("Reinstalling")
            print("Reinstalling Button Clicked")
            self.reinstall_package()

        elif packagestatus == 3:
            self.packageaction = _("Upgrading")
            print("Upgrading Button Clicked")
            self.install_package(True)

    def on_button2_clicked(self, button):
        self.packageaction = _("Uninstalling")
        print("Uninstalling Button Clicked")
        self.progstack.set_visible(True)
        self.progstack.set_visible_child_name("progress")
        self.outputSW.set_visible(True)
        self.remove_package()

    def on_donebutton_clicked(self, button):
        self.window.get_application().quit()

    def on_openbutton_clicked(self, button):
        self.filechooser.run()
        self.filechooser.hide()

    def on_selectbutton_clicked(self, widget):
        self.filename = self.filechooser.get_filename()
        self.filechooser.hide()
        if self.filename:
            self.from_file(self.filename)

    def on_filechooser_file_activated(self, widget):
        self.filename = self.filechooser.get_filename()
        self.filechooser.hide()
        if self.filename:
            self.from_file(self.filename)

    def on_aboutbutton_clicked(self, button):
        self.about_dialog.run()
        self.about_dialog.hide()

    def on_detailsbutton_toggled(self, button):
        self.detailsrevealer.set_reveal_child(button.get_active())

    def open_broken_dialog(self):
        self.BrokenBox.set_visible(True)
        self.mainstack.set_visible_child_name("broken")

    def on_detailsbutton_clicked(self, button):
        if self.detailsrevealer.get_reveal_child():
            self.detailsrevealer.set_reveal_child(False)
            self.detailsbutton.set_label(_("Show Details"))
        else:
            self.detailsrevealer.set_reveal_child(True)
            self.detailsbutton.set_label(_("Hide Details"))

    def from_file(self, path):
        self.openbutton.set_visible(True)

        # clear output textbuffer
        self.outputSW.set_visible(False)
        start, end = self.textview.get_buffer().get_bounds()
        self.textview.get_buffer().delete(start, end)

        fileFormat = os.path.basename(path).split(".")[-1].lower()
        if fileFormat == "deb":
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
            print("Only .deb files are supported.")

    def on_close(self, *args):
        if self.closestatus:
            self.cannotclose_dialog.run()
            self.cannotclose_dialog.hide()
            return True
        return self.closestatus

    def start_process(self, params):
        pid, stdin, stdout, stderr = GLib.spawn_async(params, flags=GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                                                      standard_output=True, standard_error=True)
        GLib.io_add_watch(GLib.IOChannel(stdout), GLib.IO_IN | GLib.IO_HUP, self.on_process_stdout)
        GLib.io_add_watch(GLib.IOChannel(stderr), GLib.IO_IN | GLib.IO_HUP, self.on_process_stderr)
        GLib.child_watch_add(GLib.PRIORITY_DEFAULT, pid, self.on_process_exit)

        return pid

    def on_process_stdout(self, source, condition):
        if condition == GLib.IO_HUP:
            return False

        line = source.readline()
        if line:
            self.textview.get_buffer().insert(self.textview.get_buffer().get_end_iter(), line)
            self.textview.scroll_to_iter(self.textview.get_buffer().get_end_iter(), 0.0, False, 0.0, 0.0)

        return True

    def on_process_stderr(self, source, condition):
        if condition == GLib.IO_HUP:
            return False
        line = source.readline()
        if line is not None:
            if "dlstatus" in line:
                percent = line.split(":")[2].split(".")[0]
                self.progressbar.set_show_text(True)
                self.progressbar.set_text("{} %".format(percent))
                self.progressbar.set_fraction(int(percent) / 100)
            elif "pmstatus" in line:
                percent = line.split(":")[2].split(".")[0]
                self.progressbar.set_show_text(True)
                self.progressbar.set_text("{} {} %".format(self.packageaction, percent))
                self.progressbar.set_fraction(int(percent) / 100)
            elif re.match(r"^[A-Za-zÇĞİÖŞÜçğıöşü]+:", line.strip()) and ".deb" in line:
                print("connection error")
                self.error = True
            elif re.match(r"^[A-Za-zÇĞİÖŞÜçğıöşü]+:", line.strip()) and "dpkg --configure -a" in line:
                print("dpkg --configure -a error")
                self.error = True
                self.dpkgconferror = True
            elif re.match(r"^[A-Za-zÇĞİÖŞÜçğıöşü]+:", line.strip()) and "/var/lib/dpkg/lock-frontend" in line:
                print("/var/lib/dpkg/lock-frontend error")
                self.error = True
                self.dpkglockerror = True

            self.textview.get_buffer().insert(self.textview.get_buffer().get_end_iter(), line)
            self.textview.scroll_to_iter(self.textview.get_buffer().get_end_iter(), 0.0, False, 0.0, 0.0)

        return True

    def on_process_exit(self, pid, retval):
        print(f"Done. exit code: {retval}")
        self.pid = None
        if self.error is False:
            if retval == 0:
                self.notificationstate = True
                if self.progressbar.get_show_text():
                    self.progressbar.set_text("100 %")
                    self.progressbar.set_fraction(1)
                self.progstack.set_visible_child_name("done")
            else:
                self.progstack.set_visible_child_name("doneinfo")
                self.doneinfolabel.set_markup("<b>{}</b>".format(_("Not Completed !")))
                self.notificationstate = False
        else:
            errormessage = _("<b><span color='red'>Connection Error !</span></b>")
            if self.dpkglockerror:
                errormessage = _("<b><span color='red'>Dpkg Lock Error !</span></b>")
            elif self.dpkgconferror:
                errormessage = _("<b><span color='red'>Dpkg Interrupt Error !</span></b>")
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
            self.installed_version.set_markup(
                "<small><span weight='light'>{}</span></small>".format(_("Not installed")))

        self.openbutton.set_sensitive(True)
        self.closestatus = False
        if self.isinstalling and self.status == 0 and retval == 0:
            print("connection lost")
            errormessage = _("<b><span color='red'>Connection Error !</span></b>")
            if self.dpkglockerror:
                errormessage = _("<b><span color='red'>Dpkg Lock Error !</span></b>")
            elif self.dpkgconferror:
                errormessage = _("<b><span color='red'>Dpkg Interrupt Error !</span></b>")
            self.doneinfolabel.set_markup(errormessage)
            if self.progressbar.get_show_text():
                self.progressbar.set_show_text(False)
                self.progressbar.set_fraction(0)
            self.progstack.set_visible_child_name("doneinfo")
            self.notificationstate = False

        if retval == 256:
            errormessage = _("Only one software management tool is allowed to run at the same time.\n"
                             "Please close the other application\ne.g. 'Update Manager', 'aptitude' or 'Synaptic' first.")
            self.doneinfolabel.set_markup(errormessage)
            if self.progressbar.get_show_text():
                self.progressbar.set_show_text(False)
                self.progressbar.set_fraction(0)
            self.progstack.set_visible_child_name("doneinfo")
            self.notificationstate = False

        self.error = False
        self.dpkglockerror = False
        self.dpkgconferror = False
        self.isinstalling = False
        self.notify()
        self.textview.scroll_to_iter(self.textview.get_buffer().get_end_iter(), 0.0, False, 0.0, 0.0)

    def notify(self):
        if not self.notificationstate:
            return

        if not Notify.is_initted():
            Notify.init("org.parslinux.package-installer")

        icon_theme = Gtk.IconTheme.get_default()
        icon_names = [self.packagename, "parslinux-package-installer", "dialog-information"]

        pixbuf = None
        for name in icon_names:
            try:
                pixbuf = icon_theme.load_icon(name, 64, Gtk.IconLookupFlags.FORCE_SIZE)
                break
            except GLib.Error:
                continue

        if pixbuf and hasattr(self, "notification") and self.notification:
            self.notification.set_icon_from_pixbuf(pixbuf)

        if hasattr(self, "notification") and self.notification and not self.window.is_active():
            self.notification.show()
