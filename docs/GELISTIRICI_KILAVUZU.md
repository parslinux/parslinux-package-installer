# Pars Linux Paket Kurucu — Geliştirici Kılavuzu

Bu rehber, `parslinux-package-installer` kod tabanına katkıda bulunmak, yerel geliştirme ortamı kurmak, birim ve entegrasyon testlerini çalıştırmak ve çevirileri yönetmek isteyen geliştiriciler içindir.

---

## 1. Geliştirme Ortamı Kurulumu

Uygulama Python 3, PyGObject ve **GTK 4 / Libadwaita** üzerine kuruludur.

### 1.1. Debian / Pars Linux Tabanlı Sistemlerde:
```bash
sudo apt update
sudo apt install -y python3-all python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-notify-0.7 zstd policykit-1 gettext
# İsteğe bağlı
sudo apt install python3-apt
```

### 1.2. Arch Linux Tabanlı Geliştirme Ortamlarında:
```bash
sudo pacman -S python python-gobject gtk4 libadwaita libnotify zstd polkit gettext
```

---

## 2. Kaynak Koddan ve Betiklerle Çalıştırma

Projeyi klonladıktan sonra otomasyon betikleri veya doğrudan Python ile çalıştırabilirsiniz:

```bash
# Otomasyon betiği ile (Önerilen)
./run.sh                  # Boş ekranla başlatır
./run.sh --sample         # Örnek paketle başlatır
./run.sh /yol/paket.deb   # Belirtilen paketi açar
./run.sh --test           # Tüm testleri çalıştırır

# Doğrudan Python ile:
python3 src/Main.py
python3 src/Main.py /yol/paket.deb
python3 src/Main.py /yol/paket.pkg.tar.zst
python3 src/Main.py /yol/uygulama.AppImage
python3 src/Main.py /yol/paket.flatpakref

# Çoklu paket ile toplu kurulum kuyruğunu test etmek için:
python3 src/Main.py pkg1.deb pkg2.deb

# Headless CLI teftiş modlarını test etmek için:
python3 src/Main.py -i pkg1.deb
python3 src/Main.py -c pkg1.deb
```

---

## 3. Kod Yapısı ve Modüller

* **`src/Main.py`**: Libadwaita `ApplicationAdw` uygulamasının ana giriş noktası, CLI argüman ayrıştırıcısı.
* **`src/MainWindowAdw.py`**: Saf Python ile oluşturulmuş GTK 4 / Libadwaita ana penceresi (detaylar, canlı arama, toplu kuyruk, AppImage/Flatpak yönetimi).
* **`src/PackageLoader.py`**: Evrensel paket fabrikası (`open_package`, `is_supported_package`, `is_arch_system`, `is_fedora_system`).
* **`src/DebPackage.py`**: `.deb` arşivlerini açan, `control` dosyasını ayrıştıran ve bağımlılıkları denetleyen motor.
* **`src/ArchPackage.py`**: `.pkg.tar.zst` arşivlerini açan, `.PKGINFO` ayrıştıran ve pacman ile denetleyen motor.
* **`src/RpmPackage.py`**: `.rpm` paketlerini `rpm`/`rpm2cpio` ile ayrıştıran motor.
* **`src/AppImagePackage.py`**: ELF ikili başlığını, masaüstü entegrasyonunu (`~/.local/share/applications/`) ve çalıştırma izinlerini yöneten modül.
* **`src/FlatpakRefPackage.py`**: Flathub referanslarını (`.flatpakref`, `.flatpakrepo`) ayrıştıran ve kurulumunu yöneten modül.
* **`src/Actions.py`**: Kök yetkisiyle (`pkexec`) APT, Pacman ve RPM işlemlerini yürüten kilit denetimli backend.
* **`src/cli.py`**: Terminalde `-i` ve `-c` dökümleri sunan arayüzsüz modül.

---

## 4. Testleri Çalıştırma

Projedeki tüm birim, entegrasyon, CLI ve arayüz testleri tek bir komutla çalıştırılabilir:

```bash
./run.sh --test
# veya doğrudan:
python3 tests/run_all_tests.py
```

Tekil test modülleri:
* `python3 tests/test_arch_package.py` — Arch Linux motoru testleri
* `python3 tests/test_appimage_and_flatpakref.py` — AppImage ve Flatpakref testleri
* `python3 tests/test_rpm_package.py` — RPM paketi ayrıştırma testleri
* `python3 tests/test_batch_queue.py` — Toplu kuyruk testleri
* `python3 tests/test_included_files.py` — Dosya ağacı ayrıştırma testleri
* `python3 tests/test_cli_modernization.py` — Headless CLI ve AppStream testleri
* `python3 tests/test_gui_integration.py` — Libadwaita pencere yaşam döngüsü testleri

---

## 5. Çevirileri (i18n) Güncelleme

Yeni bir metin eklendiğinde veya var olanlar güncellendiğinde:

1. Metnin kod içinde `_("Metin")` şeklinde sarmalandığından emin olun.
2. `po/files` listesinde dosyanızın yer aldığını doğrulayın.
3. Çeviri şablonunu güncellemek için betiği çalıştırın:
   ```bash
   bash update-translations.sh
   ```
4. `po/tr.po` ve `po/pt.po` dosyalarındaki çevirileri tamamlayın.
5. `setup.py` çalıştırıldığında `.mo` dosyaları otomatik derlenir.
