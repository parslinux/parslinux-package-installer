# Pars Linux Paket Kurucu — Uygulama ve Dosya Bağlama (MIME) Kılavuzu

Bu doküman, `parslinux-package-installer` uygulamasının sistem genelinde hem Debian (`.deb`) hem de Arch Linux (`.pkg.tar.*`) uzantılı dosyalarla ilişkilendirilmesi, dosya yöneticileri (Nautilus, Thunar, Dolphin vb.) ile entegrasyonu ve varsayılan paket kurucu olarak atanması süreçlerini kapsar.

---

## 1. Desteklenen MIME Türleri

### Debian Paketleri:
* `application/vnd.debian.binary-package` (Resmi ve standart IANA türü)
* `application/x-deb` (Geniş kullanımda olan alternatif tür)
* `application/x-debian-package` (Geleneksel masaüstü ortamları türü)

### Arch Linux Paketleri:
* `application/x-zstd-compressed-tar` (Zstandard ile sıkıştırılmış .pkg.tar.zst)
* `application/x-arch-package` (Özel Arch paketi türü)
* `application/x-tar` (Genel tar paket arşivleri)

---

## 2. Masaüstü Kısayolu Entegrasyonu

`/usr/share/applications/org.parslinux.package-installer.desktop` dosyasında şu tanımlar yer alır:

```ini
[Desktop Entry]
Name=Pars Linux Package Installer
Name[tr]=Pars Linux Paket Kurucu
GenericName=Package Installer
GenericName[tr]=Paket Kurucu
Comment=Install, view and manage Debian (.deb) and Arch Linux (.pkg.tar.*) packages
Comment[tr]=Debian (.deb) ve Arch Linux (.pkg.tar.*) yazılım paketlerini kur, incele ve yönet
Exec=parslinux-package-installer %F
Icon=parslinux-package-installer
Terminal=false
Type=Application
Categories=System;Settings;PackageManager;GTK;
MimeType=application/vnd.debian.binary-package;application/x-deb;application/x-debian-package;application/x-zstd-compressed-tar;application/x-tar;application/x-arch-package;
StartupNotify=true
StartupWMClass=org.parslinux.package-installer
Keywords=package;apt;dpkg;pacman;arch;install;deb;kurucu;paket;gdebi;toplu;
```

Burada `%F` parametresi, dosya yöneticisinde birden fazla paket seçildiğinde tüm dosyaların tek seferde toplu kuyruğa (`batch queue`) aktarılmasını sağlar.

---

## 3. Sistem Genelinde Varsayılan Uygulama Yapma

`/usr/share/applications/defaults.list` veya `/etc/xdg/mimeapps.list` içerisine şu satırlar eklenir:

```ini
[Default Applications]
application/vnd.debian.binary-package=org.parslinux.package-installer.desktop
application/x-deb=org.parslinux.package-installer.desktop
application/x-debian-package=org.parslinux.package-installer.desktop
application/x-zstd-compressed-tar=org.parslinux.package-installer.desktop
application/x-arch-package=org.parslinux.package-installer.desktop
```

Veritabanını yenilemek için:

```bash
sudo update-desktop-database /usr/share/applications
sudo update-mime-database /usr/share/mime
```

---

## 4. Kullanıcı Düzeyinde Varsayılan Yapma

```bash
xdg-mime default org.parslinux.package-installer.desktop application/vnd.debian.binary-package
xdg-mime default org.parslinux.package-installer.desktop application/x-zstd-compressed-tar
```

Kontrol etmek için:

```bash
xdg-mime query default application/vnd.debian.binary-package
xdg-mime query default application/x-zstd-compressed-tar
# Çıktı: org.parslinux.package-installer.desktop
```
