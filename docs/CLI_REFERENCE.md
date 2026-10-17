# Pars Linux Paket Kurucu — Uçbirim (CLI) Referansı

`parslinux-package-installer` v3.0.0, saf **GTK 4 / Libadwaita** grafik arayüzünün yanı sıra arayüzsüz (headless) terminal teftiş yeteneklerine, otomasyon betiklerine ve PolicyKit korumalı `Actions.py` arka plan motoruna sahiptir.

---

## 1. Otomasyon Betikleri

Depo kök dizininde yer alan bağımsız betikler:

| Betik | Kullanım | Açıklama |
|:---|:---|:---|
| `./run.sh` | `./run.sh [dosya]` | Uygulamayı başlatır (`--sample`, `--test`, `-i`, `-c` destekler) |
| `./manage.sh` | `./manage.sh` | İnteraktif terminal yönetim menüsü veya CLI bayrakları |
| `./package.sh` | `./package.sh` | Dağıtıma göre `.deb` veya `.pkg.tar.zst` derler |
| `sudo ./install.sh` | `sudo ./install.sh` | Bağımlılıkları çözer ve sisteme kurar |
| `sudo ./uninstall.sh` | `sudo ./uninstall.sh` | Sistemden dosyaları ve paketleri temizler |
| `./stop.sh` | `./stop.sh` | Çalışan arayüz ve arka plan süreçlerini sonlandırır |

---

## 2. Ana Komut: `parslinux-package-installer`

### Kullanım Şekli:
```bash
parslinux-package-installer [SEÇENEKLER] [PAKET1] [PAKET2 ...]
```

### Desteklenen Paket Biçimleri:
* `.deb`: Debian / Ubuntu / Pars Linux ikili paketleri
* `.pkg.tar.zst`, `.pkg.tar.xz`, `.pkg.tar.gz`: Arch Linux paketleri
* `.rpm`: Red Hat / Fedora / openSUSE paketleri
* `.AppImage`: Bağımsız taşınabilir Linux ikilileri
* `.flatpakref`, `.flatpakrepo`: Flathub uygulama ve depo referansları
* `http://`, `https://`: Uzak web paket URL'leri

### Parametreler ve Seçenekler:
* `[PAKET]`: Yerel dosya yolu veya uzak URL.
* `-i, --info <PAKET>`: Grafik arayüz açmadan terminalde ayrıntılı paket metaverilerini görüntüler.
* `-c, --check <PAKET>`: Bağımlılıkları denetler (Çıkış kodu `0`: tüm gereksinimler karşılanıyor, `1`: eksik bağımlılık veya mimari sorunu var).
* `-v, --verbose`: Ayrıntılı hata ayıklama (debug) günlüklerini aktif eder.
* `--version`: Program sürüm numarasını görüntüler.
* `-h, --help`: Yardım kılavuzunu görüntüler.

---

## 3. Headless CLI Teftiş Örnekleri

### 3.1. Paket Bilgilerini Terminalde Görüntüleme (`-i, --info`)
```bash
parslinux-package-installer -i /tmp/vscode_amd64.deb
```
**Çıktı:**
```text
============================================================
 Paket Adı        : code
 Sürüm (Version)  : 1.87.0
 Mimari (Arch)    : amd64
 Durum (Status)   : Kurulu (1.86.0)
 Bölüm (Section)  : devel
 Boyut (Size)     : 365824 KB
 Geliştirici      : Microsoft Corporation <vscode-linux@microsoft.com>
 Web Sitesi       : https://code.visualstudio.com/
 Bağımlılıklar    : libc6 (>= 2.34), libnss3, libasound2
 Açıklama:
 Visual Studio Code is a code editor redefined and optimized for building and debugging modern web and cloud applications.
============================================================
```

Arch Linux paketleri için:
```bash
parslinux-package-installer -i ripgrep-14.1.0-1-x86_64.pkg.tar.zst
```

AppImage dosyaları için:
```bash
parslinux-package-installer -i Inkscape-1.3.AppImage
```

Flatpakref dosyaları için:
```bash
parslinux-package-installer -i org.videolan.VLC.flatpakref
```

### 3.2. Bağımlılık Doğrulama ve Script Entegrasyonu (`-c, --check`)
```bash
if parslinux-package-installer -c ornek-uygulama.deb; then
    echo "Paket güvenle kurulabilir."
else
    echo "Eksik bağımlılıklar tespit edildi!"
fi
```

### 3.3. Uzak URL'den Paket İnceleme
```bash
parslinux-package-installer -i https://repo.parslinux.org/packages/parslinux-editor_3.0.0_all.deb
```

---

## 4. Arka Plan İşlem Komutu: `Actions.py`

`Actions.py`, grafik arayüz tarafından `pkexec` (PolicyKit) ile ayrıcalık yükseltilerek çağrılan çok katmanlı paket işlem betiğidir.

### Kullanım Şekli:
```bash
pkexec /usr/share/parslinux/parslinux-package-installer/src/Actions.py <EYLEM> <HEDEFLER...>
```

### Eylemler (`<EYLEM>`):
* `install <paket1> [paket2 ...]`:
  - **Debian / Pars Linux**: `apt install <yollar> -yq -o APT::Status-Fd=2` ile toplu kurulum.
  - **Arch Linux**: `pacman -U --noconfirm --needed <yollar>` ile yerel arşiv kurulumu.
  - **Fedora / RPM**: `rpm -i <yollar>` ile yerel kurulum.
  - **Arch'ta .deb**: `debtap` yüklüyse otomatik dönüştürüp yerel paket olarak kurar.
* `reinstall <paket>`: Aynı sürümü yeniden yükler.
* `downgrade <paket>`: Paketi eski sürüme indirger.
* `remove <paket1> [paket2 ...]`:
  - **Debian**: `apt remove --purge <paketler>` ile tamamen kaldırır.
  - **Arch Linux**: `pacman -Rns --noconfirm <paketler>` ile kaldırır.
  - **RPM**: `rpm -e <paketler>` ile kaldırır.

### Çıkış Kodları:
* `0`: İşlem başarıyla tamamlandı.
* `1`: Hata oluştu (Bağımlılık çözülemedi, geçersiz arşiv vb.).
* `130`: Kullanıcı tarafından iptal edildi (SIGINT/SIGTERM).
* `256`: Dpkg (`/var/lib/dpkg/lock-frontend`) veya Pacman (`/var/lib/pacman/db.lck`) veritabanı kilitli.

