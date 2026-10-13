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

## 🚀 Gelecek Planları (Roadmap v1.1.0+)
- [ ] Uzak URL'den `.deb` bağlantısı verildiğinde otomatik indirip inceleme desteği.
- [ ] Flatpak / Snap dönüştürücü analiz modülü entegrasyonu.
- [ ] Çoklu mimari (Multiarch) kütüphane çakışmalarında otomatik alternatif önerme.
