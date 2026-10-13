# Proje İlerlemesi — parslinux-package-installer

Bu dosya, projenin mevcut durumu, tamamlanan kilometre taşları ve gelecek hedeflerini özetler.

---

## 🎯 Kilometre Taşı 1: Çatallanma ve Pars Linux Markalaması ✅
- [x] Kaynak depo (`pardus-package-installer`) klonlandı.
- [x] Uygulama kimliği `org.parslinux.package-installer` olarak güncellendi.
- [x] Masaüstü kısayolu (`org.parslinux.package-installer.desktop`) ve PolicyKit yetkilendirme kuralı (`org.parslinux.pkexec.parslinux-package-installer.policy`) oluşturuldu.
- [x] Arayüz metinleri, başlıklar, telif bilgileri (`© Pars Linux`) ve ikonlar güncellendi.
- [x] Geriye dönük uyumluluk çalıştırıcısı sağlandı.

---

## 🎯 Kilometre Taşı 2: GDebi Dengi Çift Tıklama ve Dosya Yakalama ✅
- [x] Dosya yöneticisinden `.deb` dosyalarına çift tıklama entegrasyonu (MIME tipleri: `application/vnd.debian.binary-package`, `application/x-deb`, `application/x-debian-package`).
- [x] GApplication `do_open` ve `do_activate` senkronizasyonu sağlandı.
- [x] Sürükle ve Bırak (Drag & Drop) ve Boş Karşılama ekranı işlevselleştirildi.
- [x] Uçbirimden argümanlı doğrudan çalıştırma optimize edildi.

---

## 🎯 Kilometre Taşı 3: Bağımlılık ve Paket Motoru ✅
- [x] Saf Python tabanlı bağımsız `DebPackage.py` modülü geliştirildi (`ar` ve `tarfile`).
- [x] `python3-apt` bulunan ortamlarda sistem `apt.Cache` entegrasyonu sağlandı.
- [x] Bağımlılıkların çözümlenebilirliği ve eksik paketlerin durum rozeti olarak gösterimi tamamlandı.
- [x] Mimari uyuşmazlığı denetimi eklendi.

---

## 🎯 Kilometre Taşı 4: Dinamik Kurulum / Kaldırma Mekanizması ✅
- [x] Durum makinesi (0: Kur, 1: Sürüm Düşür, 2: Tekrar Yükle, 3: Yükselt) tamamlandı.
- [x] Kurulu paketler için tek tıkla Kaldırma (`Remove`) butonu bağlandı.
- [x] `Actions.py` kilit denetimi ve APT durum akışı (`Status-Fd=2`) entegre edildi.
- [x] Canlı yüzdelik ilerleme çubuğu ve açılır terminal konsolu bağlandı.

---

## 🎯 Kilometre Taşı 5: Dokümantasyon ve Paketleme ✅
- [x] Debian paketleme dosyaları (`debian/control`, `debian/changelog`, `debian/copyright`, `debian/rules`) düzenlendi.
- [x] Çeviriler (`tr.po`, `pt.po`, `pot`) güncellendi ve derlendi.
- [x] Kapsamlı dokümantasyon seti hazırlandı (`ARCHITECTURE`, `KULLANIM_KILAVUZU`, `PAKETLEME_VE_DAGITIM`, `GELISTIRICI_KILAVUZU`, `INSTALL`, `CHANGELOG`, `CLAUDE`, `CLI_REFERENCE`, `TESTING`, vb.).

---

## 🎯 Kilometre Taşı 6: Yeni Görsel Kimlik, Logo ve Boş Durum Tasarımı ✅
- [x] Modern Pars Linux squircle (128x128 SVG) uygulama logosu tasarlandı (`images/parslinux-package-installer.svg`).
- [x] 3D paket koli, altın mühür bandı, perspektifli `.deb` rozeti ve indirme oku görseli entegre edildi.
- [x] GTK Boş Durum ekranı modern logo, karşılama metni ve aksiyon butonu ile güçlendirildi.
- [x] Bozuk paket (`BrokenDebBox`) ekranına görsel uyarı sembolü eklendi.
- [x] Telif hakları `© Pars Linux` olarak tamamlandı.

---

## 🎯 Kilometre Taşı 7: Paket Dosya Ağacı (Included Files) Canlı Arama ve Filtreleme ✅
- [x] `DebPackage.get_file_details()` ile her dosyanın türü (dizin, dosya, sembolik bağ, çalıştırılabilir), boyutu ve izinleri ayrıştırıldı.
- [x] Ayrıntılar bölümüne **İçerilen Dosyalar** sekmesi eklendi.
- [x] Anlık arama kutusu (`GtkSearchEntry`) ve `GtkTreeModelFilter` ile sıfır gecikmeli canlı arama sağlandı.
- [x] Dosya türü ikonları (klasör, çalıştırılabilir, sembolik bağ, metin) ve biçimlendirilmiş boyut sütunları eklendi.
- [x] Eşleşen ve toplam dosya sayısı sayaç etiketi eklendi.

---

## 🎯 Kilometre Taşı 8: Toplu Paket Kurulumu (Batch Installer & Kuyruk) ✅
- [x] Dosya seçicide çoklu dosya seçimi (`set_select_multiple(True)`) aktif edildi.
- [x] Çoklu sürükle-bırak desteği (`on_mainwindow_drag_data_received`) ve CLI'dan birden fazla `.deb` argümanı kabul etme eklendi.
- [x] `BatchBox` arayüzü ile toplu paket kuyruğu ekranı oluşturuldu.
- [x] Onay kutuları (`GtkCellRendererToggle`), durum ikonları, sürüm ve boyut özeti entegre edildi.
- [x] Sıralı arka plan kurulum motoru (`_batch_worker`) ile PolicyKit korumalı toplu kurulum bağlandı.
- [x] Canlı yüzdelik ilerleme ve tamamlanma masaüstü bildirimleri (`Notify`) eklendi.

---

## 🎯 Kilometre Taşı 9: Modern GTK 4 ve Libadwaita Desteği ✅
- [x] `src/MainWindowAdw.py` ve `src/MainAdw.py` ile saf GTK 4 & Libadwaita ön yüzü geliştirildi.
- [x] `Adw.ApplicationWindow`, `Adw.ToolbarView`, `Adw.HeaderBar`, `Adw.ToastOverlay` modern GNOME/Adwaita bileşenleri kullanıldı.
- [x] `Adw.StatusPage` ile karşılama ve hata sayfaları, `Adw.PreferencesGroup` ve `Adw.ActionRow` ile paket detayları sunuldu.
- [x] Tekli paket, dosya arama ve toplu kurulum kuyruğu GTK 4 üzerinde tam işlevselleştirildi.
- [x] `--adw` ve `--gtk4` CLI parametreleri ve `parslinux-package-installer-adw` çalıştırıcısı eklendi.
- [x] `.desktop` dosyasına Modern Libadwaita Modunda Aç eylemi (`[Desktop Action Adw]`) eklendi.

---

---

## 🎯 Kilometre Taşı 11: Tam Modernizasyon, Güvenlik ve CLI Teftiş Modu ✅
- [x] **Kaldırma UX Güvenliği (Confirmation Dialog)**: Tek tıkla kazara paket/bağımlılık silinmesini önleyen `Gtk.MessageDialog` ve `Adw.MessageDialog` onay pencereleri entegre edildi.
- [x] **Modern CSS Tema Motoru (`ui/style.css`)**: `Gtk.CssProvider` ile modern eylem butonları (`.suggested-action`, `.destructive-action`, `.pill`), koyu monospace APT terminal çıktısı ve durum rozetleri bağlandı.
- [x] **Headless CLI Teftiş Modülü (`src/cli.py`)**:
  - `-i, --info <paket.deb>`: GUI açmadan terminalde paket detaylarını, mimarisini, boyutunu ve durumunu listeleme.
  - `-c, --check <paket.deb>`: Bağımlılıkları denetleyip eksik paketleri raporlama ve otomasyonlar için çıkış kodu (0 veya 1) üretme.
  - Her iki grafik arayüz (`Main.py` ve `MainAdw.py`) CLI komutlarını bağımsız çalıştırabilir hale getirildi.
- [x] **Evrensel Dil-Bağımsız Hata Yakalama**: APT ve dpkg hata akışları yerel dilden bağımsız hale getirildi.
- [x] **Kaynak ve Dosya Kaçaklarının Giderilmesi**: `__version__` ve arayüz dosyalarındaki tüm unclosed file uyarıları context manager ile temizlendi.
- [x] **Genişletilmiş Test Paketi**: `tests/test_cli_modernization.py` ile 11 adet otomatik test paketi %100 oranla geçmektedir.

---

## 🔍 Teknik Borç Durumu ve Analizi

### ✅ Çözülen Kritik Teknik Borçlar
1. **GLib IO Channel Kilitlenmesi (Busy Loop / %100 CPU):** Süreç çıktısı kapandığında (`EOF`) `return False` verilerek işlemcinin kilitlenmesi önlendi.
2. **zstd Sıkıştırma Engeli:** Standart Python kütüphanesinin zstd desteklememesi sorunu `_open_tar()` harici zstd fallback motoru ile çözüldü.
3. **Sorgusuz Paket Silme:** "Kaldır" butonuna basıldığı an paket ve bağımlılıklarının anında silinmesi engellendi; modal onay pencereleri bağlandı.
4. **Dile Bağımlı Hata Tespiti:** Yalnızca Türkçe/İngilizce harflere bakan regex evrenselleştirildi; APT ve dpkg kilit hataları dile bağımsız tespit ediliyor.
5. **Açık Kalan Dosya Tanıtıcıları:** `__version__` dosyası okumaları `with open` context manager ile sarılarak `ResourceWarning` uyarıları giderildi.
6. **Sıfır Test Durumu:** Projeye 4 ayrı test paketi ve 11 adet otomatik birim/entegrasyon testi kazandırıldı.

### 📌 Kalan / Takip Edilen Mimari Teknik Borçlar
1. **Çift Motor Bakım Yükü (Dual UI Architecture):**
   - Şu anda hem eski GTK 3 (`MainWindow.py` + Glade XML) hem de modern GTK 4/Libadwaita (`MainWindowAdw.py`) paralel yaşamaktadır. Bu durum her yeni arayüz özelliğinin iki farklı kütüphaneye de uyarlanmasını gerektirir.
2. **Toplu Kurulumda Çapraz Bağımlılık Çözümü:**
   - Kuyruktaki paketler şu anda adım adım tek tek `pkexec` ile kurulmaktadır. Birbirine bağımlı paketler aynı kuyruktaysa, APT'nin bunları tek bir transaction içinde çözebilmesi için toplu liste olarak `apt install deb1 deb2` şeklinde tek oturumda gönderilmesi daha dayanıklı bir çözüm olacaktır.
3. **Cache Güncelleme Mikro-Gecikmesi:**
   - `update_cache()` işlemi ana iş parçacığında `apt.Cache()` sorgulamaktadır. Çok sayıda PPA deposu olan yavaş diskli sistemlerde hafif arayüz gecikmelerini önlemek için tamamen asenkron arka plana taşınabilir.

---

## 🚀 Gelecek Yol Haritası (Roadmap v1.1.0 - v2.0.0)

### v1.1.0 (Yakın Gelecek)
- [ ] **🌐 Uzak URL'den Doğrudan İndirip İnceleme:**
  - `parslinux-package-installer https://example.com/app.deb` komutu veya arayüzden URL yapıştırma desteği.
- [ ] **📦 Toplu Kurulumda Tek Seferlik APT Oturumu:**
  - Kuyruktaki paketleri tek seferde `Actions.py install pkg1 pkg2 ...` şeklinde göndererek aralarındaki çapraz bağımlılıkları tek Polkit şifresiyle çözme.
- [ ] **🧩 Çoklu Mimari (Multiarch) Yardımcısı:**
  - `i386` veya farklı mimarili paketlerde sistemde eksik mimari varsa `dpkg --add-architecture` önerisi sunma.

### v1.2.0 (Akıllı Paket Yönetimi)
- [ ] **🛡️ Btrfs / Timeshift Anlık Görüntü (Snapshot) Güvencesi:**
  - Riskli sistem paketleri kurulmadan/kaldırılmadan önce tek tıkla otomatik sistem geri yükleme noktası oluşturma.
- [ ] **💡 Akıllı Alternatif / Flatpak Önerisi:**
  - Depolarda bulunmayan veya kırık bağımlılığı olan paketler için Flathub üzerinde alternatif sürüm arayıp önerme.

### v2.0.0 (Büyük Dönüşüm)
- [ ] **💎 Saf GTK 4 / Libadwaita'ya Tam Geçiş:**
  - Eski Glade 3 XML ve GTK 3 kodlarını tamamen emekliye ayırarak projeyi tek, saf ve ultra-hafif Libadwaita motoruna geçirme.
