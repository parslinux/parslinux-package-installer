# Değişiklik Günlüğü (Changelog) — Pars Linux Package Installer

Tüm önemli sürüm değişiklikleri bu dosyada belgelenmektedir. Format [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standardına uygundur.

---

## [2.2.0] - 2026-10-14

### Eklendi
- **Flathub Akıllı Alternatif Motoru (`src/FlatpakHelper.py`)**:
  - Depolarda bulunmayan veya bağımlılıkları karşılanamayan paketler için Flathub üzerinden otomatik alternatif arama (`flatpak search`).
  - `MainWindowAdw.py` Libadwaita arayüzünde dinamik uyarı banner'ı (`banner_flatpak`) ve tek tıkla doğrudan "Flathub Üzerinden Kur" eylemi.
  - CLI arayüzüne `--flatpak-search <terim>` parametresi eklendi; `cli_check()` ve `cli_info()` çıktılarında akıllı Flathub alternatif önerileri listelendi.
- **Evrensel RPM (.rpm) Ailesi Desteği (`src/RpmPackage.py`)**:
  - `rpm-python` C kütüphanesi veya `rpm` ikili aracı gerektirmeyen, ikili RPM başlıklarını (`Lead` ve `Header` formatı) doğrudan `struct` ile ayrıştıran bağımsız saf Python motoru.
  - RPM paket adı, sürüm-release, mimari, özet, açıklama, lisans, kurulu boyut ve paket içi tam dosya ağacı (`OLDFILENAMES` ve `BASENAMES/DIRNAMES`) dökümü.
  - `PackageLoader.py` polimorfik motoruna `.rpm` uzantısı tam entegre edildi.
  - RPM tabanlı dağıtımlarda `rpm -Uvh`, Debian/Arch ortamlarında `alien` uyumluluk köprüsü.
- **Kapsamlı Test ve GUI Entegrasyonu**:
  - `tests/fixtures/parslinux-fedora-hello-2.2.0-1.x86_64.rpm` gerçek test paketi.
  - `tests/test_rpm_and_flatpak.py` (13 yeni test) ve Libadwaita RPM pencere entegrasyon testi.
  - Toplam 7 test paketinde 54 test senaryosu %100 başarıyla geçmektedir.

---

## [2.1.0] - 2026-10-14

### Eklendi
- **Sistem Anlık Görüntüsü (Snapshot) Güvencesi (`src/SnapshotManager.py`)**:
  - Kurulum öncesinde otomatik sistem geri yükleme noktası oluşturma altyapısı.
  - Timeshift (RSYNC / BTRFS modları), Snapper ve Btrfs alt birimleri için otomatik arka uç tespiti.
  - `Actions.py` içine `--snapshot` bayrağı ve `snapshot` eylemi desteği.
  - Grafik arayüzde (tekli paket ve toplu kuyruk sayfalarında) anlık görüntü oluşturma tercihi switch'i.
  - CLI `--snapshot-status` parametresi ile kurulu araç durumunu sorgulama.
- **Masaüstü Bildirim Sistemi (`src/NotificationManager.py`)**:
  - GApplication tabanlı `Gio.Notification` ve FreeDesktop `notify-send` çift motorlu bildirim desteği.
  - Kurulum, kaldırma veya toplu kuyruk işlemleri tamamlandığında masaüstü bildirimleri gösterme.
- **Test Kapsamı**:
  - `tests/test_snapshot_and_notifications.py` (16 yeni test ile toplam 40 otomatik test, %100 başarı).

---

## [2.0.0] - 2026-10-14

### Eklendi
- **Arch Linux & Çoklu Dağıtım Desteği (Multi-Distro Engine)**:
  - `src/ArchPackage.py`: `.pkg.tar.zst`, `.pkg.tar.xz`, `.pkg.tar.gz` arşivlerini doğrudan okuma, `.PKGINFO` metaverilerini ve dosya ağacını ayrıştırma.
  - `src/PackageLoader.py`: `.deb` ve `.pkg.tar.*` paketlerini polimorfik olarak otomatik açan evrensel yükleyici.
  - `PKGBUILD` ve `.SRCINFO`: Standart Arch Linux ve AUR paketleme altyapısı.
  - `pacman` desteği: Arch üzerinde `pacman -U` ve `pacman -Rns` komutlarıyla paket kurma ve kaldırma; `/var/lib/pacman/db.lck` kilit kontrolü.
  - `debtap` köprüsü: Arch Linux üzerinde `.deb` açıldığında otomatik paket dönüştürme ve kurma.
- **Toplu Paket Kurulum Kuyruğu (Batch Installer)**:
  - Birden fazla paketi sürükleyip bırakarak veya dosya seçiciyle kuyruğa ekleme.
  - Tek bir PolicyKit oturumu ile tüm kuyruğu tek seferde kurabilme.
- **İçerilen Dosyalar Canlı Arama (Included Files)**:
  - Arşiv içindeki tüm dosyaları izinleri, tür ikonları ve boyutlarıyla listeleme.
  - Gerçek zamanlı arama kutusu ile anında filtreleme.
- **Headless CLI Teftiş Modülü (`src/cli.py`)**:
  - `-i, --info`: Grafik arayüz açmadan terminalde ayrıntılı metaveri dökümü.
  - `-c, --check`: Bağımlılıkları kontrol edip eksik paketleri listeleme ve exit code üretme.
- **Uzak URL'den Paket İndirme**:
  - `http://` ve `https://` paket adreslerini geçici dizine indirip anında inceleme.
- **Çoklu Mimari (Multiarch) Yardımcısı**:
  - Yabancı mimarili paketlerde `dpkg --add-architecture` çözümü önerme.
- **Genişletilmiş Test Paketi**:
  - `tests/run_all_tests.py` ile 5 test paketinde birim, CLI, Libadwaita ve Arch entegrasyon testleri.

### Değiştirildi & Temizlendi
- **Saf GTK 4 & Libadwaita Mimarisi**:
  - Eski `ui/MainWindow.glade` (1.250 satırlık XML) ve `src/MainWindow.py` tamamen emekliye ayrıldı.
  - Ana uygulama doğrudan saf Python ile yazılan modern `src/MainWindowAdw.py` arayüzüne geçirildi.
  - Kod tabanının %97.5'i doğrudan Pars Linux ekibi tarafından yazılmış hale geldi.
- **Kaldırma UX Güvenliği**:
  - Kazara paket silinmesini önleyen onay modal pencereleri eklendi.
- **Changelog Temizliği**:
  - Eski dağıtımın 300 satırlık log kalıntıları temizlendi.

---

## [1.0.0] - 2026-10-13

### Eklendi
- **Pars Linux Çatallanması (Fork)**: Proje `pardus-package-installer` temel alınarak Pars Linux için yeniden markalandı.
- **`src/DebPackage.py` Hibrit Ayrıştırıcı**: `python3-apt` bulunmayan ortamlarda saf Python (`tarfile` ve `ar`) ile `.deb` paketlerini açma ve kontrol etme desteği.
- **Akıllı Dosya Yakalama**: Dosya yöneticisinden çift tıklama (`%F` parametresi ve GApplication `do_open`), uçbirim yolu ve sürükle-bırak desteği.
- **Gelişmiş Bağımlılık Raporlama**: Bağımlılıkların eksiksiz karşılanıp karşılanmadığını net durum göstergeleriyle sunma.
- **Dinamik İşlem Butonu**: Kurulum, Sürüm Düşürme, Yeniden Kurulum, Yükseltme ve Kaldırma durumları için akıllı durum makinesi.
- **Yeni Masaüstü ve Polkit Yapılandırması**: `org.parslinux.package-installer.desktop` ve `org.parslinux.pkexec.parslinux-package-installer.policy`.
- **Kapsamlı Dokümantasyon Seti**: Mimari, kullanım, paketleme, test, CLI ve geliştirici kılavuzları.
