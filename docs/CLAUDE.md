# CLAUDE.md — Pars Linux Package Installer Geliştirici Yönergesi

Bu dosya, `parslinux-package-installer` v3.0.0 deposunda çalışan geliştiriciler ve AI kodlama asistanları için kritik mimari rehberdir.

---

## 🛠️ Temel Komutlar

### Otomasyon Betikleri (Önerilen)
```bash
./run.sh                  # Arayüzü boş olarak başlatır
./run.sh --sample         # Örnek paketle başlatır
./run.sh --test           # Tüm test paketlerini koşturur
./run.sh dosya.deb        # Belirtilen paketi açar (.deb, .pkg.tar.*, .rpm, .appimage, .flatpakref, .flatpakrepo)

./manage.sh               # İnteraktif CLI yönetim menüsü
./package.sh              # Otomatik sistem tespitiyle paketler (.deb / .pkg.tar.zst)
sudo ./install.sh         # Bağımlılıkları kurar ve sisteme yükler
sudo ./uninstall.sh       # Sistemden tamamen kaldırır
```

### Manuel Python Komutları
```bash
# Boş ekranla başlatma (Saf GTK 4 / Libadwaita)
python3 src/Main.py

# Belirli bir paketle başlatma
python3 src/Main.py [dosya.deb / dosya.pkg.tar.zst / dosya.rpm / dosya.AppImage / dosya.flatpakref]

# Çoklu paket ile toplu kuyruk açma
python3 src/Main.py pkg1.deb pkg2.deb

# Headless CLI teftiş modları
python3 src/Main.py -i paket.deb
python3 src/Main.py -c paket.deb
```

### Testleri Çalıştırma
```bash
./run.sh --test
# veya doğrudan:
python3 tests/run_all_tests.py
```

### Çevirileri Derleme / Güncelleme
```bash
bash update-translations.sh
```

---

## 🏛️ Mimari Kuralları

1. **Saf Libadwaita / GTK4 Arayüzü**: Arayüz doğrudan `src/MainWindowAdw.py` içinde saf Python ve Libadwaita bileşenleri (`Adw.ApplicationWindow`, `Adw.ToolbarView`, `Adw.PreferencesGroup`, `Adw.ActionRow`) ile yazılmıştır. Eski Glade XML ve GTK3 tamamen kaldırılmıştır.
2. **Evrensel Paket Yükleyici (`PackageLoader`)**: Paket açılırken doğrudan motor çağırmak yerine daima `PackageLoader.open_package()` kullanılmalı; dosya kontrolünde `is_supported_package()` kullanılmalıdır.
3. **Çoklu Dağıtım ve Format Desteği**:
   - Debian (`.deb`) -> `src/DebPackage.py`
   - Arch Linux (`.pkg.tar.*`) -> `src/ArchPackage.py`
   - Red Hat / Fedora (`.rpm`) -> `src/RpmPackage.py`
   - Taşınabilir AppImage (`.AppImage`) -> `src/AppImagePackage.py`
   - Flatpak Uygulama & Depoları (`.flatpakref`, `.flatpakrepo`) -> `src/FlatpakRefPackage.py`
4. **Kök Yetkisi Ayrımı (Polkit)**: Arayüz asla `root` olarak çalıştırılmaz. Kurulum/kaldırma işlemleri yalnızca `src/Actions.py` üzerinden `pkexec` ile çağrılır. `Actions.py` hem APT hem Pacman kilitlerini ve komutlarını çift motorlu yönetir.
5. **GApplication Yaşam Döngüsü**: Uygulama ID'si `org.parslinux.package-installer` olmalıdır. `do_open` ve `do_activate` sinyalleri tekli/toplu paketleri ve uzak web URL'lerini yönetmelidir.

