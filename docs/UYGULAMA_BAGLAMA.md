# Pars Linux Paket Kurucu — Uygulama ve Dosya Bağlama (MIME) Kılavuzu

Bu doküman, `parslinux-package-installer` uygulamasının sistem genelinde `.deb` uzantılı dosyalarla ilişkilendirilmesi, dosya yöneticileri (Thunar, Nautilus, Dolphin vb.) ile entegrasyonu ve varsayılan paket kurucu olarak atanması süreçlerini kapsar.

---

## 1. Desteklenen MIME Türleri

Debian paketleri Linux masaüstü ortamlarında genellikle şu MIME türleri ile tanımlanır:

* `application/vnd.debian.binary-package` (Resmi ve standart IANA türü)
* `application/x-deb` (Geniş kullanımda olan alternatif tür)
* `application/x-debian-package` (Bazı eski masaüstü ortamları tarafından kullanılan tür)

---

## 2. Masaüstü Kısayolu Entegrasyonu

`/usr/share/applications/org.parslinux.package-installer.desktop` dosyasında şu tanımlar yer alır:

```ini
[Desktop Entry]
Name=Pars Linux Package Installer
Name[tr]=Pars Linux Paket Kurucu
Exec=parslinux-package-installer %f
Icon=parslinux-package-installer
Terminal=false
Type=Application
Categories=System;Settings;PackageManager;GTK;
MimeType=application/vnd.debian.binary-package;application/x-deb;application/x-debian-package;
StartupNotify=true
StartupWMClass=org.parslinux.package-installer
```

Burada `%f` parametresi, dosya yöneticisinde üzerine çift tıklanan tekil dosyanın mutlak yolunun uygulamaya argüman olarak aktarılmasını sağlar.

---

## 3. Sistem Genelinde Varsayılan Uygulama Yapma

Paket kurulduğunda veya yönetici tarafından ayarlandığında `/usr/share/applications/defaults.list` veya `/etc/xdg/mimeapps.list` içerisine şu satırlar eklenir:

```ini
[Default Applications]
application/vnd.debian.binary-package=org.parslinux.package-installer.desktop
application/x-deb=org.parslinux.package-installer.desktop
application/x-debian-package=org.parslinux.package-installer.desktop
```

Veritabanını yenilemek için:

```bash
sudo update-desktop-database /usr/share/applications
sudo update-mime-database /usr/share/mime
```

---

## 4. Kullanıcı Düzeyinde Varsayılan Yapma

Belirli bir kullanıcının oturumunda varsayılan yapmak için:

```bash
xdg-mime default org.parslinux.package-installer.desktop application/vnd.debian.binary-package
xdg-mime default org.parslinux.package-installer.desktop application/x-deb
```

Kontrol etmek için:

```bash
xdg-mime query default application/vnd.debian.binary-package
# Çıktı: org.parslinux.package-installer.desktop
```
