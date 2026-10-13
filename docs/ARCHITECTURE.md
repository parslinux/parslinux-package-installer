# Pars Linux Package Installer — Mimari ve Tasarım Spesifikasyonu

Bu doküman, `parslinux-package-installer` uygulamasının teknik mimarisini, bileşenler arası veri akışını, durum makinelerini ve güvenlik modelini detaylandırmaktadır.

---

## 1. Genel Mimari Bakış

Uygulama, zayıf bağlı (loosely-coupled) bir model izleyerek kullanıcı arayüzü (GTK 3), paket inceleme/çözümleme motoru (`DebPackage`), ayrıcalık yükseltme (Polkit `pkexec`) ve sistem paket yöneticisi (`apt`/`dpkg`) katmanlarını birbirinden ayırır.

```mermaid
graph TD
    User([Kullanıcı / Dosya Yöneticisi]) -->|Çift Tıklama / CLI / Sürükle-Bırak| Main[src/Main.py]
    Main -->|GApplication Yaşam Döngüsü| Win[src/MainWindow.py]
    Win -->|UI Tanımı| Glade[ui/MainWindow.glade]
    Win -->|Paket Çözümleme & Bağımlılık Kontrolü| DebPkg[src/DebPackage.py]
    
    subgraph Sistem Katmanı
        DebPkg -->|Tercih Edilen| PyApt[python3-apt / apt.Cache]
        DebPkg -->|Yedek / Fallback| Standalone[Saf Python AR & Tar Ayrıştırıcı]
        PyApt -->|Durum Sorgusu| DpkgDb[(/var/lib/dpkg/status)]
    end
    
    Win -->|Kurulum / Kaldırma İsteği| Polkit[pkexec / Polkit Daemon]
    Polkit -->|Yetkilendirme Onayı| Actions[src/Actions.py]
    Actions -->|Kilit Denetimi| Locks[/var/lib/dpkg/lock-frontend]
    Actions -->|APT İşlemi| AptBin[/usr/bin/apt]
    AptBin -->|Status-Fd Çıktısı| Win
```

---

## 2. Temel Modüller ve Rolleri

### 2.1. `src/Main.py` (GApplication Yönetimi)
* **GApplication Kimliği**: `org.parslinux.package-installer`
* **Bayraklar**: `Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE`
* **Görevi**: 
  * Dosya yöneticisinden çift tıklandığında gelen `do_open` sinyallerini karşılar.
  * Uçbirimden argümanla veya argümansız başlatıldığında `do_activate` sinyalini yönetir.
  * Zaten açık olan bir pencere varsa yeni pencere açmak yerine mevcut pencereye odaklanır ve paketi yükler.

### 2.2. `src/MainWindow.py` (Arayüz ve Orkestrasyon)
* **GTK 3 + Glade**: Arayüz bileşenlerini yükler, sinyalleri bağlar.
* **Worker Thread**: Büyük `.deb` dosyalarının incelenmesi ve `apt.Cache` başlatılmasını arayüzü dondurmamak için arka plan iş parçacığında (`threading.Thread`) yürütür, sonucu `GLib.idle_add` ile UI'a aktarır.
* **Durum Yöneticisi**: `mainstack` bileşeni üzerinden `splash`, `empty`, `package`, `brokendeb`, `broken` durumları arasında geçiş yapar.
* **Canlı Süreç İzleme**: `Actions.py` sürecini `GLib.spawn_async` ile başlatır; `stdout` ve `stderr` akışlarını `GLib.IOChannel` ve `io_add_watch` ile dinler.
* **Yüzdelik İlerleme Çözümleme**: APT `Status-Fd=2` çıktısındaki `dlstatus` (indirme) ve `pmstatus` (paket yöneticisi) akışlarını regex ile yakalayıp ilerleme çubuğunu günceller.

### 2.3. `src/DebPackage.py` (Hibrit Paket İnceleme Motoru)
* **`python3-apt` Varsa**:
  * `apt.debfile.DebPackage` sarmalayıcısını kullanır.
  * `check()` metodu ile bağımlılıkların depolardan karşılanıp karşılanamayacağını hesaplar.
  * `compare_to_version_in_cache()` ile sistemdeki sürümle karşılaştırma yapar.
* **`python3-apt` Yoksa (Geliştirici / Fallback Modu)**:
  * Saf Python ile Debian paketinin `ar` arşiv yapısını (`!<arch>\n`) okur.
  * `control.tar.*` içinden RFC822 formatındaki `control` dosyasını çözümler.
  * `data.tar.*` içinden paketin içerdiği dosyaların listesini çıkarır.
  * Sistemde `dpkg-query` varsa kurulu sürümle karşılaştırır.

### 2.4. `src/Actions.py` (Root Ayrıcalıklı İşlem Yürütücü)
* Bu betik doğrudan kullanıcı tarafından değil, `MainWindow` tarafından `pkexec` aracılığıyla kök kullanıcı yetkileriyle çağrılır.
* **İşlemler**:
  * `install`: `apt install <tam_yol.deb> -yq -o APT::Status-Fd=2 -o Dpkg::Options::=--force-confnew`
  * `reinstall`: `apt install --reinstall --allow-downgrades <tam_yol.deb> ...`
  * `downgrade`: `apt install --allow-downgrades <tam_yol.deb> ...`
  * `remove`: `apt remove --purge <paket_adi> ...`
* **Kilit Denetimi**: İşleme başlamadan önce `/var/lib/dpkg/lock-frontend` ve ilgili APT kilitlerini kontrol eder; başka bir paket yöneticisi çalışıyorsa çakışmayı önler.

---

## 3. Paket Durum Makinesi

Bir `.deb` paketi yüklendiğinde sürüm karşılaştırma motoru aşağıdaki durum kodlarını üretir:

| Durum Kodu | Sabit Adı | Anlamı | Buton 1 Etiketi | Buton 2 (Kaldır) |
|:---|:---|:---|:---|:---|
| `0` | `VERSION_NONE` | Paket sistemde hiç kurulu değil | **Kur** (`Install`) | Devre Dışı |
| `1` | `VERSION_OUTDATED` | Paket sistemde kurulu olandan daha eski | **Sürüm Düşür** (`Downgrade`) | **Aktif** |
| `2` | `VERSION_SAME` | Aynı sürüm sistemde zaten kurulu | **Yeniden Kur** (`Reinstall`) | **Aktif** |
| `3` | `VERSION_NEWER` | Paket kurulu olandan daha yeni | **Yükselt** (`Upgrade`) | **Aktif** |

---

## 4. Güvenlik ve Yetkilendirme Modeli

1. **Ayrıcalık Ayrımı**: Grafik arayüzü (`MainWindow.py`) kesinlikle `root` olarak çalıştırılmaz; normal kullanıcı yetkileriyle çalışır.
2. **PolicyKit Entegrasyonu**: Kök yetki gerektiren tek işlem `src/Actions.py` çalıştırmasıdır.
3. **Kural Dosyası**: `/usr/share/polkit-1/actions/org.parslinux.pkexec.parslinux-package-installer.policy`
4. **Denetim**: Sistem yöneticisi şifre doğrulama ekranı PolicyKit GUI ajanı tarafından güvenli bir şekilde sunulur.
