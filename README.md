<p align="center">
  <img src="images/parslinux-package-installer.svg" width="128" height="128" alt="Pars Linux Package Installer Logo" />
</p>

# Pars Linux Package Installer

**Pars Linux Package Installer** (`parslinux-package-installer`), Pars Linux, Debian ve Arch Linux tabanlı dağıtımlar için tasarlanmış, saf **GTK 4 ve Libadwaita** arayüzüne sahip, evrensel ve modern bir paket kurucu ve inceleme aracıdır.

İndirilen veya yerel diskte bulunan `.deb` ve `.pkg.tar.zst` arşivlerine dosya yöneticisinden çift tıklandığında otomatik açılır, paket metaverilerini ve içerilen dosya ağacını listeler, bağımlılıkları denetler; tek tıkla kurulum, yeniden kurulum, yükseltme, sürüm düşürme veya sistemden kaldırma imkânı tanır.

---

## 🚀 Öne Çıkan Özellikler

- **💎 Saf GTK 4 & Libadwaita Deneyimi**: GNOME tasarım ilkeleriyle %100 uyumlu, pürüzsüz animasyonlar, Toast bildirimleri ve karanlık tema uyumu.
- **🌐 Evrensel Çoklu Dağıtım Desteği (Multi-Distro)**:
  - **Debian / Pars Linux**: `.deb` paketlerini saf Python ayrıştırıcı veya `python3-apt` önbelleği ile inceleme, APT motoru ile kurma.
  - **Arch Linux**: `.pkg.tar.zst`, `.pkg.tar.xz`, `.pkg.tar.gz` paketlerini `.PKGINFO` üzerinden okuma, dosya ağacını zstd ile açma, `pacman` motoru ile kurma ve yönetme.
  - **Arch'ta .deb Kurulumu**: Arch Linux üzerinde `debtap` yüklüyse `.deb` dosyalarını otomatik dönüştürüp yerel paket olarak kurabilme.
- **📦 Toplu Kurulum Kuyruğu (Batch Queue)**:
  - Birden çok paketi aynı anda seçip veya sürükleyip bırakarak toplu kuyruğa ekleme.
  - Tek bir PolicyKit yetkilendirme oturumu ile tüm kuyruğu sıralı ve bağımlılık uyumlu kurma.
- **🔍 İçerilen Dosyalar Canlı Arama (Included Files)**:
  - Paket içerisindeki tüm dosya ve dizinleri dosya türü ikonları, izin modları ve boyutlarıyla listeleme.
  - Anlık arama çubuğu ile sıfır gecikmeli dosya süzme.
- **⚡ Headless CLI Teftiş Modu**:
  - `parslinux-package-installer -i paket.deb / paket.pkg.tar.zst`: Arayüz açmadan terminalde ayrıntılı metaveri dökümü.
  - `parslinux-package-installer -c paket.deb / paket.pkg.tar.zst`: Bağımlılıkları kontrol edip eksik paketleri raporlama (otomasyonlar için exit code 0 veya 1).
- **🌐 Uzak URL'den Doğrudan Açma**:
  - `parslinux-package-installer https://example.com/yazilim.deb` şeklinde verilen uzak paketleri geçici dizine indirip anında inceleme.
- **🛡️ Güvenli Yetkilendirme & Onay Pencereleri**:
  - Yetki gerektiren tüm işlemler PolicyKit (`pkexec`) ile yönetilir.
  - Kazara paket silinmesini önleyen onay pencereleri (`MessageDialog`).

## 📸 Ekran Görüntüleri

<p align="center">
  <img src="screenshots/parslinux-package-installer-1.png" width="48%" alt="Tekli Paket İnceleme" />
  <img src="screenshots/parslinux-package-installer-2.png" width="48%" alt="Arch Linux Paketi" />
</p>
<p align="center">
  <img src="screenshots/parslinux-package-installer-3.png" width="48%" alt="İçerilen Dosyalar Arama" />
  <img src="screenshots/parslinux-package-installer-4.png" width="48%" alt="Toplu Kurulum Kuyruğu" />
</p>

---

## 📦 Sistem Gereksinimleri

### Debian / Ubuntu / Pars Linux
```bash
sudo apt install python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-notify-0.7 zstd policykit-1
# İsteğe bağlı
sudo apt install python3-apt
```

### Arch Linux / Manjaro / EndeavourOS
```bash
sudo pacman -S python python-gobject gtk4 libadwaita libnotify zstd polkit
# İsteğe bağlı (Arch'ta .deb dönüştürmek için)
yay -S debtap
```

---

## 🛠️ Çalıştırma

```bash
# Grafik arayüz ile paket açma:
parslinux-package-installer paket.deb
# veya Arch paketi:
parslinux-package-installer paket.pkg.tar.zst

# Uzak URL açma:
parslinux-package-installer https://example.com/uygulama.deb

# Terminalde metaveri görüntüleme (Headless):
parslinux-package-installer -i paket.deb

# Terminalde bağımlılık doğrulama:
parslinux-package-installer -c paket.deb
```

---

## 🔨 Paketleme ve Derleme

### Debian Paketi Oluşturma (`.deb`):
```bash
sudo apt install devscripts git-buildpackage
gbp buildpackage --git-export-dir=/tmp/build/parslinux-package-installer -us -uc
```

### Arch Linux Paketi Oluşturma (`PKGBUILD`):
```bash
makepkg -si
```

---

## 🧪 Testleri Çalıştırma

Proje tam kapsamlı otomatik birim ve entegrasyon testleriyle korunmaktadır:

```bash
python3 tests/run_all_tests.py
```

---

## 📚 Dokümantasyon

- 📖 [Dokümantasyon İndeksi](docs/INDEX.md)
- 🖥️ [Kullanım Kılavuzu](docs/KULLANIM_KILAVUZU.md) — Grafik arayüz, toplu kuyruk, dosya arama ve kullanım senaryoları
- 🏗️ [Mimari Spesifikasyonu](docs/ARCHITECTURE.md) — Modül yapısı, Libadwaita motoru, PackageLoader ve durum makinesi
- 📦 [Paketleme ve Dağıtım](docs/PAKETLEME_VE_DAGITIM.md) — Debian ve Arch Linux (PKGBUILD) paketleme yönergeleri
- 💻 [Geliştirici Kılavuzu](docs/GELISTIRICI_KILAVUZU.md) — Kod tabanı, geliştirme ortamı ve test mimarisi
- ⚡ [CLI Referansı](docs/CLI_REFERENCE.md) — Komut satırı parametreleri ve teftiş komutları
- 🧪 [Test Dokümantasyonu](docs/TESTING.md) — Otomatik test paketleri ve fikstürler
- 📈 [Proje İlerlemesi](docs/progress.md) — Kilometre taşları, teknik borç analizi ve yol haritası
- 🔀 [Fork ve Geliştirme Notları](FORK.md) — Proje geçmişi ve yapılan yenilikler

---

## 📄 Lisans

GPL-3.0-or-later — Ayrıntılar için [LICENSE](LICENSE) ve [FORK.md](FORK.md) dosyalarına bakınız.
