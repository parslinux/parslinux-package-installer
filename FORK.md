# Pars Linux Package Installer — Fork ve Geliştirme Notları

Bu proje, Pardus ekibi tarafından geliştirilen `pardus-package-installer` projesi temel alınarak **Pars Linux** ekosistemi için çatallanmış (fork) ve modernize edilmiş halidir.

## Yapılan Başlıca İyileştirmeler ve Uyarlamalar

1. **Marka ve Sistem Entegrasyonu**:
   - Paket adı `parslinux-package-installer` olarak güncellendi.
   - Uygulama ID'si `org.parslinux.package-installer` olarak ayarlandı.
   - Masaüstü kısayolu `org.parslinux.package-installer.desktop` oluşturuldu ve Debian paket (`.deb`) MIME tipleri (`application/vnd.debian.binary-package`, `application/x-deb`, `application/x-debian-package`) ile tam ilişkilendirildi.
   - Polkit yetkilendirme politikası `org.parslinux.pkexec.parslinux-package-installer.policy` olarak tanımlandı.
   - İkon ve grafiksel arayüz Pars Linux kimliğiyle uyarlandı.

2. **GDebi Dengi Çift Tıklama Mekanizması**:
   - Dosya yöneticisinden `.deb` paketine çift tıklandığında doğrudan açılma (`%f` parametresi ve GApplication `do_open` / `do_activate` senkronizasyonu) sağlandı.
   - Sürükle ve bırak (Drag & Drop) desteği ve boş pencerede dosya seçici mekanizması korundu ve güçlendirildi.
   - CLI argümanı üzerinden doğrudan çağırma (`parslinux-package-installer dosya.deb`) hatasız çalışacak şekilde optimize edildi.

3. **Gelişmiş Bağımlılık Kontrolü & Tek Tıkla Kurulum / Kaldırma**:
   - `python3-apt` bulunan ortamlarda sistem APT önbelleği (`apt.Cache`) ve `DebPackage` motoru ile tam uyumlu bağımlılık kontrolü.
   - `python3-apt` bulunmayan geliştirme/test ortamları için saf Python (`tarfile` / `ar`) tabanlı bağımsız `DebPackage` okuyucu/ayrıştırıcı modülü (`src/DebPackage.py`) geliştirildi.
   - Duruma duyarlı dinamik işlem butonu:
     - Kurulu değilse: **Paketi Kur** (`Install`)
     - Eski sürüm kuruluysa: **Yükselt** (`Upgrade`)
     - Aynı sürüm kuruluysa: **Yeniden Kur** (`Reinstall`)
     - Daha yeni sürüm kuruluysa: **Sürüm Düşür** (`Downgrade`)
     - Sistemde mevcutsa: **Kaldır** (`Uninstall`) butonu aktifleşir.
   - Bağımlılıkların karşılanıp karşılanmadığı net ve renkli durum rozetleriyle kullanıcıya gösterilir.
   - Kurulum esnasında APT durum akışı (`dlstatus`, `pmstatus`) üzerinden gerçek zamanlı yüzdelik ilerleme ve detaylar konsolu.

4. **Geriye Dönük Uyumluluk**:
   - Eski script çağrıları için `pardus-package-installer` sarmalayıcısı muhafaza edildi.
   - Türkçe ve Portekizce yerelleştirmeleri güncellendi.
