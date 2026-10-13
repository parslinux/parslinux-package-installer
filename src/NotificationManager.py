#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotificationManager.py for parslinux-package-installer.
Provides desktop notification integration using native Gio.Notification (GApplication)
and notify-send fallback for package installation, batch actions, and errors.
"""

import logging
import os
import shutil
import subprocess
from typing import Optional

logger = logging.getLogger("parslinux-notifications")


def send_notification(
    title: str,
    body: str,
    icon_name: str = "parslinux-package-installer",
    app=None,
    urgency: str = "normal"
) -> bool:
    """
    Send desktop notification using Gio.Notification if app is available,
    or falling back to notify-send command.
    """
    # 1. Native Gio.Notification via Gtk/Adw Application
    if app is not None:
        try:
            from gi.repository import Gio
            if hasattr(app, "send_notification"):
                notif = Gio.Notification.new(title)
                notif.set_body(body)
                if icon_name:
                    notif.set_icon(Gio.ThemedIcon.new(icon_name))
                app.send_notification("parslinux-status", notif)
                return True
        except Exception as e:
            logger.debug("Gio.Notification error: %s", e)

    # 2. FreeDesktop notify-send fallback
    notify_send_bin = shutil.which("notify-send")
    if notify_send_bin:
        try:
            cmd = [
                notify_send_bin,
                "-a", "Pars Linux Paket Kurucu",
                "-i", icon_name,
                "-u", urgency,
                title,
                body
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            logger.debug("notify-send execution failed: %s", e)

    return False


def notify_install_success(package_name: str, version: str = "", app=None) -> bool:
    """Notify user of successful package installation."""
    ver_str = f" ({version})" if version else ""
    return send_notification(
        title="Kurulum Tamamlandı",
        body=f"'{package_name}'{ver_str} paketi sisteme başarıyla kuruldu.",
        icon_name="emblem-ok-symbolic",
        app=app
    )


def notify_install_failure(package_name: str, error_msg: str = "", app=None) -> bool:
    """Notify user of package installation failure."""
    body = f"'{package_name}' paketi kurulurken bir hata oluştu."
    if error_msg:
        body += f"\n{error_msg}"
    return send_notification(
        title="Kurulum Başarısız",
        body=body,
        icon_name="dialog-error-symbolic",
        app=app,
        urgency="critical"
    )


def notify_remove_success(package_name: str, app=None) -> bool:
    """Notify user of package removal."""
    return send_notification(
        title="Paket Kaldırıldı",
        body=f"'{package_name}' paketi sistemden kaldırıldı.",
        icon_name="emblem-ok-symbolic",
        app=app
    )


def notify_batch_success(count: int, app=None) -> bool:
    """Notify user of successful batch queue installation."""
    return send_notification(
        title="Toplu Kurulum Tamamlandı",
        body=f"{count} adet paket başarıyla kuruldu.",
        icon_name="emblem-ok-symbolic",
        app=app
    )
