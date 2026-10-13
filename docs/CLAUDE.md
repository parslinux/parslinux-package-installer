# CLAUDE.md — Pars Linux Package Installer Geliştirici Yönergesi

Bu dosya, `parslinux-package-installer` deposunda çalışan geliştiriciler ve AI kodlama asistanları için kritik mimari rehberdir.

---

## 🛠️ Temel Komutlar

### Uygulamayı Çalıştırma
```bash
# Boş ekranla başlatma (Saf GTK 4 / Libadwaita)
python3 src/Main.py

# Belirli bir paketle başlatma (.deb veya .pkg.tar.zst)
python3 src/Main.py [dosya.deb / dosya.pkg.tar.zst]

# Çoklu paket ile toplu kuyruk açma
python3 src/Main.py pkg1.deb pkg2.deb

# Headless CLI teftiş modları
python3 src/Main.py -i paket.deb
python3 src/Main.py -c paket.deb

# Doğrudan çalıştırıcı ile
./parslinux-package-installer [paket]
```

### Testleri Çalıştırma
```bash
# Tüm test paketlerini koşturma:
python3 tests/run_all_tests.py
```

### Çevirileri Derleme / Güncelleme
```bash
bash update-translations.sh
```

---

## 🏛️ Mimari Kuralları

1. **Saf Libadwaita / GTK4 Arayüzü**: Arayüz doğrudan `src/MainWindowAdw.py` içinde saf Python ve Libadwaita bileşenleri (`Adw.ApplicationWindow`, `Adw.ToolbarView`, `Adw.PreferencesGroup`, `Adw.ActionRow`) ile yazılmıştır. Eski Glade XML kullanılmaz.
2. **Evrensel Paket Yükleyici (`PackageLoader`)**: Paket açılırken doğrudan `DebPackage` çağırmak yerine daima `PackageLoader.open_package()` kullanılmalı; dosya kontrolünde `is_supported_package()` kullanılmalıdır.
3. **Çoklu Dağıtım Desteği (`Debian` & `Arch Linux`)**: Hem `.deb` hem `.pkg.tar.*` formatları eşit vatandaş muamelesi görür. Arch paketleri için `ArchPackage.py`, Debian paketleri için `DebPackage.py` çalışır.
4. **Kök Yetkisi Ayrımı (Polkit)**: Arayüz asla `root` olarak çalıştırılmaz. Kurulum/kaldırma işlemleri yalnızca `src/Actions.py` üzerinden `pkexec` ile çağrılır. `Actions.py` hem APT hem Pacman kilitlerini ve komutlarını çift motorlu yönetir.
5. **GApplication Yaşam Döngüsü**: Uygulama ID'si `org.parslinux.package-installer` olmalıdır. `do_open` ve `do_activate` sinyalleri tekli/toplu paketleri ve uzak web URL'lerini kusursuz yönetmelidir.
