#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern GTK 4 & Libadwaita Interface for parslinux-package-installer.
"""

import os
import sys
import threading
from subprocess import Popen, PIPE
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw, Gio, GLib, GObject

from DebPackage import DebPackage, HAVE_APT
from PackageLoader import open_package, is_supported_package
from SnapshotManager import SnapshotManager
from FlatpakHelper import FlatpakHelper
import NotificationManager
from cli import get_version


class MainWindowAdw(Adw.ApplicationWindow):
    def __init__(self, application, target_file=None):
        super().__init__(application=application, title="Pars Linux Paket Kurucu")
        self.application = application
        self.set_default_size(720, 680)

        self.cache = None
        self.package = None
        self.debianpackage = ""
        self.batch_items = []  # list of dicts: {'path': ..., 'pkg': ..., 'selected': True, 'status': ..., 'icon': ...}

        self.setup_ui()

        if target_file:
            path = target_file.get_path() if hasattr(target_file, 'get_path') else target_file
            if path and os.path.exists(path):
                self.from_file(path)

    def setup_ui(self):
        # Toast overlay
        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)

        # Toolbar view
        self.toolbar_view = Adw.ToolbarView()
        self.toast_overlay.set_child(self.toolbar_view)

        # Header bar
        self.header_bar = Adw.HeaderBar()
        self.toolbar_view.add_top_bar(self.header_bar)

        # Header Title
        self.window_title = Adw.WindowTitle(title="Pars Linux Paket Kurucu", subtitle="Debian Paket Yöneticisi")
        self.header_bar.set_title_widget(self.window_title)

        # Header Buttons
        self.btn_open = Gtk.Button(icon_name="document-open-symbolic", tooltip_text="Paket Aç...")
        self.btn_open.connect("clicked", self.on_open_clicked)
        self.header_bar.pack_start(self.btn_open)

        self.btn_batch_view = Gtk.Button(icon_name="view-list-bullet-symbolic", tooltip_text="Toplu Kurulum Kuyruğu")
        self.btn_batch_view.connect("clicked", self.on_batch_view_clicked)
        self.header_bar.pack_start(self.btn_batch_view)

        self.btn_about = Gtk.Button(icon_name="help-about-symbolic", tooltip_text="Hakkında")
        self.btn_about.connect("clicked", self.on_about_clicked)
        self.header_bar.pack_end(self.btn_about)

        # View Stack
        self.stack = Adw.ViewStack()
        self.toolbar_view.set_content(self.stack)

        # 1. Page: Empty (Drop Target & Status Page)
        self.page_empty = Adw.StatusPage(
            title="Paket Seçin veya Sürükleyin",
            description="İncelemek veya kurmak istediğiniz .deb paketini seçin ya da pencereye sürükleyip bırakın.",
            icon_name="package-x-generic-symbolic"
        )
        empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, halign=Gtk.Align.CENTER)
        btn_browse = Gtk.Button(label="Paket Dosyası Aç...", halign=Gtk.Align.CENTER)
        btn_browse.add_css_class("suggested-action")
        btn_browse.add_css_class("pill")
        btn_browse.connect("clicked", self.on_open_clicked)
        empty_box.append(btn_browse)
        self.page_empty.set_child(empty_box)
        self.stack.add_titled(self.page_empty, "empty", "Boş")

        # 2. Page: Single Package
        self.setup_package_page()

        # 3. Page: Batch Queue
        self.setup_batch_page()

        # 4. Page: Broken Package
        self.page_broken = Adw.StatusPage(
            title="Paket Yüklenemedi",
            description="Paket dosyası bozuk veya geçersiz bir Debian arşivi.",
            icon_name="dialog-error-symbolic"
        )
        self.stack.add_titled(self.page_broken, "broken", "Hata")

        # Drop Target Setup (Gtk4)
        drop_target = Gtk.DropTarget.new(Gio.File, Gdk.DragAction.COPY)
        drop_target.connect("drop", self.on_file_dropped)
        self.add_controller(drop_target)

    def setup_package_page(self):
        scrolled = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        clamp = Adw.Clamp(maximum_size=780, tightening_threshold=600)
        scrolled.set_child(clamp)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18, margin_top=18, margin_bottom=24, margin_start=18, margin_end=18)
        clamp.set_child(main_box)

        # Hero Card
        hero_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        pkg_icon = Gtk.Image.new_from_icon_name("package-x-generic")
        pkg_icon.set_pixel_size(64)
        hero_box.append(pkg_icon)

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, hexpand=True)
        self.lbl_pkgname = Gtk.Label(halign=Gtk.Align.START, xalign=0.0)
        self.lbl_pkgname.add_css_class("title-1")
        title_box.append(self.lbl_pkgname)

        self.lbl_version_badge = Gtk.Label(halign=Gtk.Align.START, xalign=0.0)
        self.lbl_version_badge.add_css_class("caption")
        self.lbl_version_badge.add_css_class("dim-label")
        title_box.append(self.lbl_version_badge)

        self.lbl_shortdesc = Gtk.Label(halign=Gtk.Align.START, xalign=0.0, wrap=True)
        self.lbl_shortdesc.add_css_class("body")
        title_box.append(self.lbl_shortdesc)
        hero_box.append(title_box)

        main_box.append(hero_box)

        # Status Banner
        self.banner_status = Adw.Banner(title="Bu paket kurulabilir")
        self.banner_status.set_revealed(True)
        main_box.append(self.banner_status)

        # Flathub Alternative Banner
        self.banner_flatpak = Adw.Banner(title="Bu uygulamanın Flathub sürümü mevcut")
        self.banner_flatpak.set_button_label("Flatpak ile Kur")
        self.banner_flatpak.connect("button-clicked", self.on_flatpak_install_clicked)
        self.banner_flatpak.set_revealed(False)
        main_box.append(self.banner_flatpak)

        # Action Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, halign=Gtk.Align.START)
        self.btn_install = Gtk.Button(label="Kur")
        self.btn_install.add_css_class("suggested-action")
        self.btn_install.add_css_class("pill")
        self.btn_install.connect("clicked", self.on_install_clicked)
        btn_box.append(self.btn_install)

        self.btn_remove = Gtk.Button(label="Kaldır")
        self.btn_remove.add_css_class("destructive-action")
        self.btn_remove.add_css_class("pill")
        self.btn_remove.connect("clicked", self.on_remove_clicked)
        btn_box.append(self.btn_remove)

        main_box.append(btn_box)

        # Progress / Output Revealer
        self.install_revealer = Gtk.Revealer(transition_type=Gtk.RevealerTransitionType.SLIDE_DOWN)
        progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.pkg_progressbar = Gtk.ProgressBar(show_text=True)
        self.pkg_status_lbl = Gtk.Label(halign=Gtk.Align.START)
        progress_box.append(self.pkg_progressbar)
        progress_box.append(self.pkg_status_lbl)
        self.install_revealer.set_child(progress_box)
        main_box.append(self.install_revealer)

        # Snapshot / Restore Point Protection Group
        self.grp_snapshot = Adw.PreferencesGroup(title="Sistem Güvencesi")
        self.switch_snapshot = Adw.SwitchRow(
            title="Kurulum Öncesi Sistem Anlık Görüntüsü (Snapshot)",
            subtitle=SnapshotManager.get_backend_description(),
            active=SnapshotManager.is_available()
        )
        if not SnapshotManager.is_available():
            self.switch_snapshot.set_sensitive(False)
        self.grp_snapshot.add(self.switch_snapshot)
        main_box.append(self.grp_snapshot)

        # Details Preferences Group
        self.grp_details = Adw.PreferencesGroup(title="Paket Ayrıntıları")
        self.row_arch = Adw.ActionRow(title="Mimari")
        self.grp_details.add(self.row_arch)
        self.row_section = Adw.ActionRow(title="Bölüm / Kategori")
        self.grp_details.add(self.row_section)
        self.row_size = Adw.ActionRow(title="Kurulum Boyutu")
        self.grp_details.add(self.row_size)
        self.row_installed = Adw.ActionRow(title="Sistemde Kurulu Sürüm")
        self.grp_details.add(self.row_installed)
        self.row_maintainer = Adw.ActionRow(title="Paket Yöneticisi")
        self.grp_details.add(self.row_maintainer)
        self.row_homepage = Adw.ActionRow(title="Proje Web Sitesi")
        self.grp_details.add(self.row_homepage)
        main_box.append(self.grp_details)

        # Dependencies Group
        self.grp_deps = Adw.PreferencesGroup(title="Bağımlılıklar")
        self.row_depends = Adw.ActionRow(title="Gereken Paketler")
        self.grp_deps.add(self.row_depends)
        self.row_missingdeps = Adw.ActionRow(title="Eksik Bağımlılıklar")
        self.grp_deps.add(self.row_missingdeps)
        main_box.append(self.grp_deps)

        # Included Files Group with Search
        self.grp_files = Adw.PreferencesGroup(title="İçerilen Dosyalar")
        files_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, hexpand=True)
        self.files_search_entry = Gtk.SearchEntry(placeholder_text="Paket dosyalarında ara...", hexpand=True)
        self.files_search_entry.connect("search-changed", self.on_files_search_changed)
        files_header.append(self.files_search_entry)
        self.lbl_files_count = Gtk.Label(label="0 dosya", css_classes=["dim-label"])
        files_header.append(self.lbl_files_count)
        self.grp_files.set_header_suffix(files_header)

        # Files ListBox inside a scrollable box
        files_scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, min_content_height=200, max_content_height=300)
        self.files_listbox = Gtk.ListBox(css_classes=["boxed-list"])
        self.files_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.files_listbox.set_filter_func(self.filter_files_func)
        files_scroll.set_child(self.files_listbox)
        self.grp_files.add(files_scroll)
        main_box.append(self.grp_files)

        self.stack.add_titled(scrolled, "package", "Paket")

    def setup_batch_page(self):
        scrolled = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        clamp = Adw.Clamp(maximum_size=780, tightening_threshold=600)
        scrolled.set_child(clamp)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16, margin_top=18, margin_bottom=24, margin_start=18, margin_end=18)
        clamp.set_child(box)

        # Batch Header
        batch_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        batch_icon = Gtk.Image.new_from_icon_name("package-x-generic")
        batch_icon.set_pixel_size(48)
        batch_header.append(batch_icon)

        batch_title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2, hexpand=True)
        lbl_batch_title = Gtk.Label(label="Toplu Paket Kurulumu", halign=Gtk.Align.START, css_classes=["title-2"])
        batch_title_box.append(lbl_batch_title)
        self.lbl_batch_sub = Gtk.Label(label="0 paket kuyrukta", halign=Gtk.Align.START, css_classes=["dim-label"])
        batch_title_box.append(self.lbl_batch_sub)
        batch_header.append(batch_title_box)
        box.append(batch_header)

        # Batch Toolbar
        tb_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_sel_all = Gtk.Button(label="Tümünü Seç / Bırak")
        btn_sel_all.connect("clicked", self.on_batch_select_all)
        tb_box.append(btn_sel_all)

        btn_add = Gtk.Button(label="+ Paket Ekle")
        btn_add.connect("clicked", self.on_batch_add_clicked)
        tb_box.append(btn_add)

        btn_clear = Gtk.Button(label="Temizle")
        btn_clear.connect("clicked", self.on_batch_clear_clicked)
        tb_box.append(btn_clear)

        self.lbl_batch_summary = Gtk.Label(label="Toplam: 0 MB", halign=Gtk.Align.END, hexpand=True, css_classes=["dim-label"])
        tb_box.append(self.lbl_batch_summary)
        box.append(tb_box)

        # Batch Queue Preferences Group
        self.grp_batch = Adw.PreferencesGroup(title="Kurulum Kuyruğu")
        self.batch_switch_snapshot = Adw.SwitchRow(
            title="Kurulum Öncesi Sistem Anlık Görüntüsü (Snapshot)",
            subtitle=SnapshotManager.get_backend_description(),
            active=SnapshotManager.is_available()
        )
        if not SnapshotManager.is_available():
            self.batch_switch_snapshot.set_sensitive(False)
        self.grp_batch.add(self.batch_switch_snapshot)

        self.batch_listbox = Gtk.ListBox(css_classes=["boxed-list"])
        self.batch_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.grp_batch.add(self.batch_listbox)
        box.append(self.grp_batch)

        # Progress bar
        self.batch_progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, visible=False)
        self.batch_progress = Gtk.ProgressBar(show_text=True)
        self.batch_progress_lbl = Gtk.Label(halign=Gtk.Align.START)
        self.batch_progress_box.append(self.batch_progress)
        self.batch_progress_box.append(self.batch_progress_lbl)
        box.append(self.batch_progress_box)

        # Bottom Actions
        act_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_back = Gtk.Button(label="Geri Dön")
        btn_back.connect("clicked", lambda _: self.stack.set_visible_child_name("package" if self.package else "empty"))
        act_box.append(btn_back)

        self.btn_batch_install = Gtk.Button(label="Seçilenleri Sırayla Kur", hexpand=True, halign=Gtk.Align.END)
        self.btn_batch_install.add_css_class("suggested-action")
        self.btn_batch_install.add_css_class("pill")
        self.btn_batch_install.connect("clicked", self.on_batch_start_install)
        act_box.append(self.btn_batch_install)
        box.append(act_box)

        self.stack.add_titled(scrolled, "batch", "Toplu Kurulum")

    def on_file_dropped(self, target, value, x, y):
        if isinstance(value, Gio.File):
            path = value.get_path()
            if path and is_supported_package(path):
                self.from_file(path)
                return True
        return False

    def on_open_clicked(self, button):
        dialog = Gtk.FileDialog(title="Paket Dosyası Seçin")
        filters = Gio.ListStore.new(Gtk.FileFilter)

        f_all = Gtk.FileFilter()
        f_all.set_name("Tüm Paketler (*.deb, *.pkg.tar.*, *.rpm)")
        f_all.add_pattern("*.deb")
        f_all.add_pattern("*.pkg.tar.zst")
        f_all.add_pattern("*.pkg.tar.xz")
        f_all.add_pattern("*.pkg.tar.gz")
        f_all.add_pattern("*.pkg.tar")
        f_all.add_pattern("*.rpm")
        filters.append(f_all)

        f_deb = Gtk.FileFilter()
        f_deb.set_name("Debian Paketleri (*.deb)")
        f_deb.add_pattern("*.deb")
        f_deb.add_mime_type("application/vnd.debian.binary-package")
        filters.append(f_deb)

        f_arch = Gtk.FileFilter()
        f_arch.set_name("Arch Linux Paketleri (*.pkg.tar.*)")
        f_arch.add_pattern("*.pkg.tar.zst")
        f_arch.add_pattern("*.pkg.tar.xz")
        f_arch.add_pattern("*.pkg.tar")
        filters.append(f_arch)

        f_rpm = Gtk.FileFilter()
        f_rpm.set_name("Red Hat / RPM Paketleri (*.rpm)")
        f_rpm.add_pattern("*.rpm")
        f_rpm.add_mime_type("application/x-rpm")
        filters.append(f_rpm)

        dialog.set_filters(filters)
        dialog.open_multiple(self, None, self.on_files_selected)

    def on_files_selected(self, dialog, result):
        try:
            files = dialog.open_multiple_finish(result)
            paths = [f.get_path() for f in files if f.get_path() and is_supported_package(f.get_path())]
            if len(paths) == 1:
                self.from_file(paths[0])
            elif len(paths) > 1:
                self.open_batch(paths)
        except Exception as e:
            pass

    def from_file(self, path):
        path = os.path.abspath(path)
        if not os.path.exists(path):
            self.show_toast(f"Dosya bulunamadı: {path}")
            return

        try:
            self.package = open_package(path)
            self.debianpackage = path
        except Exception as e:
            self.page_broken.set_description(str(e))
            self.stack.set_visible_child_name("broken")
            return

        pkgname = self.package.pkgname
        version = self.package.get("Version", "-")
        desc_lines = self.package.get("Description", "").splitlines()
        shortdesc = desc_lines[0] if desc_lines else "-"

        self.lbl_pkgname.set_label(pkgname)
        self.lbl_version_badge.set_label(f"Sürüm: {version}")
        self.lbl_shortdesc.set_label(shortdesc)

        # Status & Version check
        chk = self.package.compare_to_version_in_cache()
        installed_ver = self.package.get_installed_version()

        if chk == 0:
            self.banner_status.set_title("Bu paket kurulmaya hazır")
            self.btn_install.set_label("Kur")
            self.btn_install.set_sensitive(True)
            self.btn_remove.set_sensitive(False)
        elif chk == 1:
            self.banner_status.set_title(f"Sürüm düşürme (Kurulu: {installed_ver})")
            self.btn_install.set_label("Sürüm Düşür")
            self.btn_install.set_sensitive(True)
            self.btn_remove.set_sensitive(True)
        elif chk == 2:
            self.banner_status.set_title(f"Paket zaten kurulu (v{installed_ver})")
            self.btn_install.set_label("Tekrar Yükle")
            self.btn_install.set_sensitive(True)
            self.btn_remove.set_sensitive(True)
        elif chk == 3:
            self.banner_status.set_title(f"Güncelleme mevcut (Kurulu: {installed_ver})")
            self.btn_install.set_label("Yükselt")
            self.btn_install.set_sensitive(True)
            self.btn_remove.set_sensitive(True)

        # Fill Details
        def safe_txt(val):
            return GLib.markup_escape_text(str(val or "-"), -1)

        self.row_arch.set_subtitle(safe_txt(self.package.get("Architecture", "-")))
        self.row_section.set_subtitle(safe_txt(self.package.get("Section", "-")))
        raw_size = self.package.get("Installed-Size", "-")
        self.row_size.set_subtitle(f"{raw_size} KiB" if raw_size != "-" else "-")
        self.row_installed.set_subtitle(safe_txt(installed_ver or "Kurulu Değil"))
        self.row_maintainer.set_subtitle(safe_txt(self.package.get("Maintainer", "-")))
        self.row_homepage.set_subtitle(safe_txt(self.package.get("Homepage", "-")))

        # Depends
        deps = self.package.get("Depends", "-")
        self.row_depends.set_subtitle(safe_txt(deps))
        missing = self.package.packagemissingdeps if hasattr(self.package, 'packagemissingdeps') else ""
        self.row_missingdeps.set_subtitle(safe_txt(missing or "Tüm bağımlılıklar karşılandı"))

        # Populate Files
        self.populate_files()

        self.stack.set_visible_child_name("package")
        self.window_title.set_subtitle(f"{pkgname} v{version}")

        # Check Flathub alternative asynchronously
        self.current_flatpak_alt = None
        self.banner_flatpak.set_revealed(False)
        if FlatpakHelper.is_available():
            def check_flatpak():
                alt = FlatpakHelper.find_alternative(pkgname)
                if alt:
                    def show_flatpak():
                        self.current_flatpak_alt = alt
                        self.banner_flatpak.set_title(f"💡 Flathub Alternatifi Mevcut: {alt['name']} ({alt['app_id']})")
                        self.banner_flatpak.set_revealed(True)
                    GLib.idle_add(show_flatpak)
            threading.Thread(target=check_flatpak, daemon=True).start()

    def on_flatpak_install_clicked(self, banner):
        if not hasattr(self, "current_flatpak_alt") or not self.current_flatpak_alt:
            return
        alt = self.current_flatpak_alt
        self.show_toast(f"'{alt['name']}' Flathub üzerinden kuruluyor...")

        def worker():
            ok, msg = FlatpakHelper.install_flatpak(alt['app_id'])
            def done():
                if ok:
                    self.show_toast(f"'{alt['name']}' Flatpak başarıyla kuruldu!")
                    NotificationManager.notify_install_success(alt['name'], alt.get('version', ''), app=self.get_application())
                else:
                    self.show_toast("Flatpak kurulumu tamamlanamadı.")
            GLib.idle_add(done)
        threading.Thread(target=worker, daemon=True).start()

    def populate_files(self):
        # Clear existing listbox
        while True:
            child = self.files_listbox.get_first_child()
            if not child:
                break
            self.files_listbox.remove(child)

        details = self.package.get_file_details()
        self.file_items = details
        self.lbl_files_count.set_label(f"{len(details)} dosya")

        for d in details:
            row = Adw.ActionRow(title=d["name"])
            icon_name = "folder-symbolic" if d["is_dir"] else ("emblem-symbolic-link" if d["is_sym"] else ("application-x-executable-symbolic" if d["is_exec"] else "text-x-generic-symbolic"))
            row.add_prefix(Gtk.Image.new_from_icon_name(icon_name))
            size_str = "-" if d["is_dir"] else MainWindowAdw.format_size(d["size"])
            row.add_suffix(Gtk.Label(label=size_str, css_classes=["dim-label"]))
            row._filepath = d["name"].lower()
            self.files_listbox.append(row)

    def filter_files_func(self, row):
        query = self.files_search_entry.get_text().strip().lower()
        if not query:
            return True
        return query in getattr(row, "_filepath", "")

    def on_files_search_changed(self, entry):
        self.files_listbox.invalidate_filter()

    # Batch Implementation
    def on_batch_view_clicked(self, button):
        self.stack.set_visible_child_name("batch")

    def open_batch(self, paths):
        self.batch_items.clear()
        while True:
            c = self.batch_listbox.get_first_child()
            if not c:
                break
            self.batch_listbox.remove(c)

        total_bytes = 0
        for p in paths:
            if not os.path.exists(p):
                continue
            try:
                pkg = open_package(p)
                raw_size = int(pkg.get("Installed-Size", 0)) * 1024
                total_bytes += raw_size
                item = {
                    'path': p,
                    'pkg': pkg,
                    'selected': True,
                    'status': 'Kurulabilir',
                    'icon': 'emblem-default-symbolic'
                }
                self.batch_items.append(item)
                self.add_batch_row(item)
            except Exception as e:
                pass

        self.lbl_batch_sub.set_label(f"{len(self.batch_items)} paket kuyrukta")
        self.lbl_batch_summary.set_label(f"Toplam: {MainWindowAdw.format_size(total_bytes)}")
        self.stack.set_visible_child_name("batch")

    def add_batch_row(self, item):
        row = Adw.ActionRow(title=item['pkg'].pkgname, subtitle=f"v{item['pkg'].get('Version', '-')}")
        check = Gtk.CheckButton(active=True)
        check.connect("toggled", lambda cb: self.on_batch_check_toggled(item, cb.get_active()))
        row.add_prefix(check)

        status_icon = Gtk.Image.new_from_icon_name(item['icon'])
        row.add_suffix(status_icon)
        item['row_widget'] = row
        item['icon_widget'] = status_icon
        self.batch_listbox.append(row)

    def on_batch_check_toggled(self, item, active):
        item['selected'] = active

    def on_batch_select_all(self, button):
        all_on = all(it['selected'] for it in self.batch_items)
        new_state = not all_on
        for it in self.batch_items:
            it['selected'] = new_state
            # update check
            cb = it['row_widget'].get_first_child()
            if isinstance(cb, Gtk.CheckButton):
                cb.set_active(new_state)

    def on_batch_add_clicked(self, button):
        self.on_open_clicked(button)

    def on_batch_clear_clicked(self, button):
        self.batch_items.clear()
        while True:
            c = self.batch_listbox.get_first_child()
            if not c:
                break
            self.batch_listbox.remove(c)
        self.lbl_batch_sub.set_label("0 paket kuyrukta")
        self.lbl_batch_summary.set_label("Toplam: 0 MB")

    def on_batch_start_install(self, button):
        selected = [it for it in self.batch_items if it['selected']]
        if not selected:
            self.show_toast("Kurulum için paket seçilmedi.")
            return

        self.btn_batch_install.set_sensitive(False)
        self.batch_progress_box.set_visible(True)
        self.batch_progress.set_fraction(0.0)

        threading.Thread(target=self._run_batch_install, args=(selected,), daemon=True).start()

    def _run_batch_install(self, items):
        actions_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Actions.py")
        total = len(items)

        def set_all_working():
            for it in items:
                it['icon_widget'].set_from_icon_name("process-working-symbolic")
                it['row_widget'].set_subtitle("Kuruluyor...")
            self.batch_progress.set_fraction(0.3)
            self.batch_progress.set_text(f"{total} paket kuruluyor...")
            self.batch_progress_lbl.set_label("Toplu paketler tek işlemde kuruluyor...")
        GLib.idle_add(set_all_working)

        paths = [it['path'] for it in items]
        use_snapshot = (self.batch_switch_snapshot.get_active() and SnapshotManager.is_available())
        cmd = ["pkexec", actions_script, "install"]
        if use_snapshot:
            cmd.append("--snapshot")
        cmd.extend(paths)

        try:
            proc = Popen(cmd, stdout=PIPE, stderr=PIPE, text=True)
            proc.communicate()
            success = (proc.returncode == 0)
        except Exception:
            success = False

        def update_results():
            for it in items:
                is_inst = success
                if not is_inst and os.path.exists("/usr/bin/dpkg-query"):
                    try:
                        res = subprocess.run(["dpkg-query", "-W", "-f=${Status}", it['pkg'].pkgname],
                                             stdout=PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
                        is_inst = "install ok installed" in res.stdout
                    except Exception:
                        pass

                it['icon_widget'].set_from_icon_name("emblem-ok-symbolic" if is_inst else "dialog-error-symbolic")
                it['row_widget'].set_subtitle("Kuruldu" if is_inst else "Hata!")

            self.batch_progress.set_fraction(1.0)
            status_text = "Toplu kurulum tamamlandı" if success else "İşlem tamamlandı (bazı hatalar olabilir)"
            self.batch_progress.set_text(status_text)
            self.batch_progress_lbl.set_label("Tüm paketler kuruldu." if success else "İşlem tamamlandı.")
            self.btn_batch_install.set_sensitive(True)
            self.show_toast("Toplu paket kurulumu tamamlandı!")

            app = self.get_application()
            if success:
                NotificationManager.notify_batch_success(len(items), app=app)
            else:
                NotificationManager.notify_install_failure("Toplu Kurulum", app=app)

        GLib.idle_add(update_results)

    # Actions: Install & Remove Single
    def on_install_clicked(self, button):
        self.run_single_action("install")

    def on_remove_clicked(self, button):
        pkg_name = self.package.pkgname if self.package else ""
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Paketi Kaldır?",
            body=f"'{pkg_name}' paketini sistemden kaldırmak istediğinizden emin misiniz?\nBu işlem pakete bağımlı diğer bileşenleri de kaldırabilir.",
        )
        dialog.add_response("cancel", "İptal")
        dialog.add_response("remove", "Kaldır")
        dialog.set_response_appearance("remove", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")

        def on_response(dlg, response_id):
            if response_id == "remove":
                self.run_single_action("remove")

        dialog.connect("response", on_response)
        dialog.present()

    def run_single_action(self, action_type):
        if not self.debianpackage:
            return
        self.btn_install.set_sensitive(False)
        self.btn_remove.set_sensitive(False)
        self.install_revealer.set_reveal_child(True)
        self.pkg_progressbar.set_fraction(0.0)
        self.pkg_status_lbl.set_label(f"{action_type.capitalize()} işlemi yürütülüyor...")

        actions_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Actions.py")
        target = self.debianpackage if action_type == "install" else self.package.pkgname
        use_snapshot = (action_type == "install" and self.switch_snapshot.get_active() and SnapshotManager.is_available())

        def worker():
            cmd = ["pkexec", actions_script, action_type]
            if use_snapshot:
                cmd.append("--snapshot")
            cmd.append(target)

            try:
                proc = Popen(cmd, stdout=PIPE, stderr=PIPE, text=True)
                stdout, stderr = proc.communicate()
                ok = (proc.returncode == 0)
            except Exception:
                ok = False

            def done():
                self.btn_install.set_sensitive(True)
                self.btn_remove.set_sensitive(True)
                self.pkg_progressbar.set_fraction(1.0)
                msg = f"Paket başarıyla {action_type} edildi." if ok else "İşlem sırasında hata oluştu."
                self.pkg_status_lbl.set_label(msg)
                self.show_toast(msg)

                # Send system desktop notification
                pkg_title = self.package.pkgname if self.package else "Paket"
                pkg_ver = self.package.get('Version', '') if self.package else ""
                app = self.get_application()
                if ok:
                    if action_type == "install":
                        NotificationManager.notify_install_success(pkg_title, pkg_ver, app=app)
                    else:
                        NotificationManager.notify_remove_success(pkg_title, app=app)
                else:
                    NotificationManager.notify_install_failure(pkg_title, app=app)

            GLib.idle_add(done)

        threading.Thread(target=worker, daemon=True).start()

    def show_toast(self, text):
        toast = Adw.Toast.new(text)
        self.toast_overlay.add_toast(toast)

    def on_about_clicked(self, button):
        about = Adw.AboutDialog()
        about.set_application_name("Pars Linux Paket Kurucu")
        about.set_developer_name("Pars Linux Geliştirici Ekibi")
        about.set_version(get_version())
        about.set_application_icon("parslinux-package-installer")
        about.set_comments("Modern GTK 4 ve Libadwaita tabanlı paket kurucu arayüzü.")
        about.set_website("https://parslinux.org")
        about.present(self)

    @staticmethod
    def format_size(num_bytes):
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
