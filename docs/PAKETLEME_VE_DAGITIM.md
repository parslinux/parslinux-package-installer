# Pars Linux Paket Kurucu — Paketleme ve Dağıtım Kılavuzu

Bu doküman, `parslinux-package-installer` uygulamasının Debian tabanlı sistemler için `.deb` ve Arch Linux tabanlı sistemler için `PKGBUILD` formatında paketlenmesi, sistem entegrasyonu ve dağıtım adımlarını açıklamaktadır.

---

## 1. Debian / Pars Linux Paketleme (`.deb`)

### 1.1. Sistem Gereksinimleri
```bash
sudo apt update
sudo apt install -y debhelper-compat dh-python python3-all python3-setuptools gettext devscripts git-buildpackage
```

### 1.2. `debuild` veya `dpkg-buildpackage` ile Derleme
Depo kök dizinindeyken:
```bash
# İmzasız olarak hızlıca derlemek için:
dpkg-buildpackage -us -uc -b
```

veya `git-buildpackage` ile:
```bash
gbp buildpackage --git-export-dir=/tmp/build/parslinux-package-installer -us -uc
```

Derleme tamamlandığında bir üst dizinde (`../`) `parslinux-package-installer_1.0.0_all.deb` paketi üretilir.

---

## 2. Arch Linux Paketleme (`PKGBUILD` & AUR)

Proje kök dizininde standart Arch Linux derleme yönergeleri (`PKGBUILD` ve `.SRCINFO`) yer almaktadır.

### 2.1. Yerel Olarak Paket Derleme ve Kurma
Arch Linux sisteminde depo kök dizininde:
```bash
makepkg -si
```
Bu komut gerekli bağımlılıkları çeker, `setup.py` üzerinden paketi derler ve `parslinux-package-installer-1.0.0-1-any.pkg.tar.zst` paketini oluşturup sisteme kurar.

### 2.2. AUR (Arch User Repository) İçin `.SRCINFO` Güncelleme
PKGBUILD üzerinde herhangi bir sürüm veya bağımlılık değişikliği yapıldığında `.SRCINFO` dosyasını yenilemek için:
```bash
makepkg --printsrcinfo > .SRCINFO
```

---

## 3. Dosya Sistemi Düzeni

Paket kurulduğunda dosya sistemine yerleşecek olan temel yollar:

| Kaynak | Hedef Yol | Açıklama |
|:---|:---|:---|
| `parslinux-package-installer` | `/usr/bin/parslinux-package-installer` | Ana çalıştırılabilir betik |
| `parslinux-package-installer-adw` | `/usr/bin/parslinux-package-installer-adw` | Libadwaita doğrudan çalıştırıcısı |
| `pardus-package-installer` | `/usr/bin/pardus-package-installer` | Geriye dönük uyumluluk sarmalayıcısı |
| `src/*` | `/usr/share/parslinux/parslinux-package-installer/src/` | Uygulama modülleri ve `Actions.py` |
| `data/style.css` | `/usr/share/parslinux/parslinux-package-installer/data/style.css` | Modern CSS teması |
| `data/*.metainfo.xml` | `/usr/share/metainfo/org.parslinux.package-installer.metainfo.xml` | AppStream yazılım merkezi metaverisi |
| `*.desktop` | `/usr/share/applications/org.parslinux.package-installer.desktop` | Masaüstü menüsü ve MIME ilişkilendirmesi |
| `*.policy` | `/usr/share/polkit-1/actions/org.parslinux.pkexec.parslinux-package-installer.policy` | PolicyKit yetkilendirme politikası |
| `images/*.svg` | `/usr/share/icons/hicolor/scalable/apps/parslinux-package-installer.svg` | Uygulama ikonu |
| `po/*/*.mo` | `/usr/share/locale/<dil>/LC_MESSAGES/parslinux-package-installer.mo` | Derlenmiş yerelleştirme dosyaları |

---

## 4. MIME Türü ve Masaüstü Entegrasyonu

Uygulamanın hem `.deb` hem `.pkg.tar.*` paketleri için varsayılan açıcı olması için masaüstü veritabanları otomatik güncellenir:

```bash
# Masaüstü ve MIME veritabanlarını el ile tazelemek için:
sudo update-desktop-database /usr/share/applications
sudo update-mime-database /usr/share/mime
```

Kullanıcı düzeyinde varsayılan yapmak için (`~/.config/mimeapps.list`):
```ini
[Default Applications]
application/vnd.debian.binary-package=org.parslinux.package-installer.desktop
application/x-deb=org.parslinux.package-installer.desktop
application/x-debian-package=org.parslinux.package-installer.desktop
application/x-zstd-compressed-tar=org.parslinux.package-installer.desktop
application/x-arch-package=org.parslinux.package-installer.desktop
```

---

## 5. Polkit İzinleri ve Güvenlik Doğrulaması

`/usr/share/polkit-1/actions/org.parslinux.pkexec.parslinux-package-installer.policy` dosyasının izinleri `0644` ve sahibi `root:root` olmalıdır.

Politikanın geçerliliğini test etmek için:
```bash
pkcheck --action-id org.parslinux.pkexec.parslinux-package-installer --process $$
```
