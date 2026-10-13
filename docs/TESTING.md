# Pars Linux Paket Kurucu — Test ve Kalite Güvencesi Kılavuzu

Bu doküman, `parslinux-package-installer` üzerinde yürütülen test türlerini, otomatikleştirilmiş doğrulama paketlerini ve senaryo denemelerini açıklar.

---

## 1. Test Mimarisi ve Paketleri

Projede süreç izolasyonu (process isolation) ile çalışan 5 ana test modülü bulunur:

1. **`tests/test_included_files.py`**:
   - `DebPackage.get_file_details()` metodunun dosya türlerini (dizin, çalıştırılabilir, sembolik bağ) ve dosya izinlerini doğru ayrıştırdığını doğrular.
2. **`tests/test_batch_queue.py`**:
   - Birden fazla paket verildiğinde kuyruk veri yapısının ve toplam boyut hesaplamasının doğruluğunu sınar.
3. **`tests/test_cli_modernization.py`**:
   - Headless CLI `-i` (`cli_info`) ve `-c` (`cli_check`) komutlarını, AppStream XML metaverisini ve CSS kurallarını test eder.
4. **`tests/test_arch_package.py`**:
   - Arch Linux `.pkg.tar.zst` paketlerinin `.PKGINFO` metaverilerini, `zstd` dosya ağacını, mimari kontrolünü ve pacman komut inşasını doğrular.
5. **`tests/test_gui_integration.py`**:
   - Saf GTK 4 / Libadwaita penceresinin (`MainWindowAdw`) Debian ve Arch paketlerini sorunsuz yüklediğini ve `Main.py` giriş noktasının çalıştığını doğrular.

---

## 2. Testleri Çalıştırma

Tüm test paketlerini tek bir komutla çalıştırmak için:

```bash
python3 tests/run_all_tests.py
```

### Örnek Başarılı Test Çıktısı:
```text
=== Running Included Files Tests ===
..
----------------------------------------------------------------------
Ran 2 tests in 0.002s
OK
PASSED: Included Files Tests

=== Running Batch Queue Tests ===
.
----------------------------------------------------------------------
Ran 1 test in 0.001s
OK
PASSED: Batch Queue Tests

=== Running CLI & UI Modernization Tests ===
..........
----------------------------------------------------------------------
Ran 10 tests in 0.315s
OK
PASSED: CLI & UI Modernization Tests

=== Running Arch Linux Support Tests ===
........
----------------------------------------------------------------------
Ran 8 tests in 0.051s
OK
PASSED: Arch Linux Support Tests

=== Running Libadwaita Debian Window Test ===
.
----------------------------------------------------------------------
Ran 1 test in 0.186s
OK
PASSED: Libadwaita Debian Window Test

=== Running Libadwaita Arch Package Window Test ===
.
----------------------------------------------------------------------
Ran 1 test in 0.223s
OK
PASSED: Libadwaita Arch Package Window Test

=== Running Main Entrypoint Test ===
.
----------------------------------------------------------------------
Ran 1 test in 0.138s
OK
PASSED: Main Entrypoint Test

ALL TEST SUITES PASSED PERFECTLY!
```

---

## 3. Test Fikstürleri (`tests/fixtures/`)

Otomatik testlerde kullanılan deterministik ve hafif paket arşivleri:
* `tests/fixtures/parslinux-hello_1.0.0_all.deb`: Temel Debian test paketi.
* `tests/fixtures/parslinux-editor_2.0.0_all.deb`: İçerisinde çok sayıda dosya barındıran Debian test paketi.
* `tests/fixtures/parslinux-arch-hello-1.0.0-1-any.pkg.tar.zst`: Zstandard ile sıkıştırılmış doğal Arch Linux test paketi.

---

## 4. Test Senaryoları Matrisi

| Senaryo No | Test Adı | Beklenen Sonuç |
|:---|:---|:---|
| **TC-01** | Parametresiz başlatma | Boş (`empty`) Libadwaita karşılama sayfası, "Paket Aç" butonu görünür |
| **TC-02** | Geçerli `.deb` ile başlatma | Paket adı, sürümü, rozeti ve detayları görünür, "Kur" butonu aktif |
| **TC-03** | Geçerli `.pkg.tar.zst` ile başlatma | Arch Linux paket metaverileri ve dosya ağacı pürüzsüz yüklenir |
| **TC-04** | Çoklu paket ile başlatma | Doğrudan **Toplu Kurulum Kuyruğu** açılır, onay kutuları ve toplam boyut gösterilir |
| **TC-05** | Bozuk / geçersiz dosya | Hata sayfası açılır ve detaylı açıklama gösterilir |
| **TC-06** | Mimari uyuşmazlığı | Mimari hata bildirimi gösterilir ve kurulum kilitlenir |
| **TC-07** | Canlı dosya arama | Arama kutusuna yazıldığında sadece eşleşen dosyalar anında listelenir |
| **TC-08** | Headless CLI `-i` / `-c` | Terminalde formatlı metaveri dökümü basılır ve exit code 0 döner |
| **TC-09** | Uzak URL paketi | `https://` paketi geçici dizine indirilip doğrudan açılır |
