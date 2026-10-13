# Pars Linux Package Installer — Mimari ve Tasarım Spesifikasyonu

Bu doküman, `parslinux-package-installer` uygulamasının teknik mimarisini, bileşenler arası veri akışını, durum makinelerini ve güvenlik modelini detaylandırmaktadır.

---

## 1. Genel Mimari Bakış

Uygulama, zayıf bağlı (loosely-coupled) bir model izleyerek kullanıcı arayüzü (GTK 3 ve GTK 4 / Libadwaita), paket inceleme/çözümleme motoru (`DebPackage`), ayrıcalık yükseltme (Polkit `pkexec`) ve sistem paket yöneticisi (`apt`/`dpkg`) katmanlarını birbirinden ayırır.

```mermaid
graph TD
    User([Kullanıcı / Dosya Yöneticisi]) -->|Tekli / Toplu Parametre / DND| Entry[parslinux-package-installer]
    Entry -->|Varsayılan GTK3| Main[src/Main.py]
    Entry -->|--adw / --gtk4 Bayrağı| MainAdw[src/MainAdw.py]
    
    Main -->|Pencere Yönetimi| Win[src/MainWindow.py]
    Win -->|UI Tanımı| Glade[ui/MainWindow.glade]
    MainAdw -->|GTK4 / Libadwaita UI| WinAdw[src/MainWindowAdw.py]
    
    Win -->|Paket İnceleme & Dosya Listesi| DebPkg[src/DebPackage.py]
    WinAdw -->|Paket İnceleme & Dosya Listesi| DebPkg
    
    subgraph Sistem ve Çözümleme Katmanı
        DebPkg -->|Tercih Edilen| PyApt[python3-apt / apt.Cache]
        DebPkg -->|Yedek / Fallback| Standalone[Saf Python AR & Tar Ayrıştırıcı]
        PyApt -->|Durum Sorgusu| DpkgDb[(/var/lib/dpkg/status)]
    end
    
    Win -->|Tekli / Toplu Kurulum İsteği| Polkit[pkexec / Polkit Daemon]
    WinAdw -->|Tekli / Toplu Kurulum İsteği| Polkit
    Polkit -->|Yetkilendirme Onayı| Actions[src/Actions.py]
    Actions -->|Kilit Denetimi| Locks[/var/lib/dpkg/lock-frontend]
    Actions -->|APT İşlemi| AptBin[/usr/bin/apt]
    AptBin -->|Status-Fd Çıktısı| Win
```

---

## 2. Temel Modüller ve Rolleri

### 2.1. `src/Main.py` (GTK3 GApplication Yönetimi)
* **GApplication Kimliği**: `org.parslinux.package-installer`
* **Bayraklar**: `Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE`
* **Görevi**: 
  * Dosya yöneticisinden çift tıklandığında veya toplu seçim yapıldığında gelen `do_open` sinyallerini karşılar.
  * Uçbirimden tekli veya çoklu argümanla başlatıldığında `do_activate` sinyalini yönetir (Tek dosya ise doğrudan paket görünümü, çoklu ise toplu kuyruk görünümü).

### 2.2. `src/MainWindow.py` (GTK3 Denetleyici ve Durum Makinesi)
* **Arayüz Durumları**:
  * `empty`: Paket yüklenmediğinde karşılama ve sürükle-bırak hedefi.
  * `package`: Paket bilgileri, sürüm rozetleri ve dinamik eylem butonları (Kur / Kaldır / Yükselt / Sürüm Düşür).
  * `batch`: Toplu paket kurulum kuyruğu (`BatchBox`).
  * `broken`: Bozuk sistem veya bağımlılık hatası.
  * `brokendeb`: Bozuk `.deb` arşivi.
* **İçerilen Dosyalar Arama ve Filtreleme**: `GtkSearchEntry`, `GtkTreeModelFilter` ve `GtkTreeView` entegrasyonu ile arşiv içeriğindeki dosyaları gerçek zamanlı filtreler.
* **Toplu Kurulum Kuyruğu**: Arka plan iş parçacığında (`_batch_worker`) sırayla `Actions.py` çalıştırarak durum ikonlarını ve genel ilerleme çubuğunu günceller.

### 2.3. `src/MainAdw.py` & `src/MainWindowAdw.py` (Modern GTK4 / Libadwaita Motoru)
* Saf GTK 4 ve Libadwaita (`Adw.Application`, `Adw.ApplicationWindow`, `Adw.ToolbarView`, `Adw.HeaderBar`) kullanır.
* `Adw.StatusPage` ile karşılama ve hata sayfaları, `Adw.PreferencesGroup` ve `Adw.ActionRow` ile sistem ayarlarına uyumlu paket detayları sunar.
* GNOME / Pars Linux modern masaüstü standartlarına tam uyumludur.

### 2.4. `src/DebPackage.py` (Bağımsız Hibrit Paket Motoru)
* Hibrit çalışma mantığı: `python3-apt` varsa sistem kütüphanesini kullanır, yoksa dahili saf Python AR ve Tar arşiv ayrıştırıcısı ile çalışır.
* `get_file_details()` metoduyla her bir dosya üyesinin adı, boyutu, türü (dizin, dosya, sembolik bağ) ve çalıştırılabilir bitlerini anında raporlar.

### 2.5. `src/Actions.py` (Ayrıcalıklı Kurulum ve Kaldırma Yardımcısı)
* Yalnızca `root` yetkisiyle `pkexec` üzerinden çağrılır.
* APT kilit dosyasını (`/var/lib/dpkg/lock-frontend`) denetler; kilit meşgulse işlem yapmadan 256 çıkış koduyla kullanıcıyı uyarır.
* Çoklu paket yollarını tek bir `apt install <yollar...>` çağrısında toplu kurabilir.

---

## 3. Test ve Kalite Güvencesi Mimarisi

* `tests/test_included_files.py`: `DebPackage` dosya ayrıştırma ve metaveri doğruluğu.
* `tests/test_batch_queue.py`: Toplu kurulum kuyruğu çoklu paket ayrıştırması.
* `tests/test_gui_integration.py`: GTK 3 ve GTK 4 arayüz bileşenlerinin yaşam döngüsü.
* `tests/run_all_tests.py`: Tüm testleri süreç izolasyonuyla koşturan ana çalıştırıcı.
