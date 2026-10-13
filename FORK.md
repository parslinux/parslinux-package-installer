# Pars Linux Package Installer — Fork ve Geliştirme Notları

Bu proje, Pardus ekibi tarafından geliştirilen `pardus-package-installer` projesi temel alınarak **Pars Linux** ekosistemi için çatallanmış (fork), baştan sona yeniden yazılarak tam modernize edilmiş halidir.

---

## Yapılan Başlıca İyileştirmeler ve Uyarlamalar

1. **Saf GTK 4 & Libadwaita Dönüşümü (Büyük Temizlik)**:
   - Eski ve hantal `ui/MainWindow.glade` (1.250 satır) ve GTK 3 `src/MainWindow.py` tamamen emekliye ayrıldı.
   - Uygulama %100 modern GNOME standartlarında saf Python **Libadwaita** ön yüzüne kavuşturuldu.
   - Kod tabanının **%82.6'sı (çekirdek Python kodlarının %97.5'i)** sıfırdan Pars Linux ekibi tarafından yazıldı.

2. **Arch Linux ve Çoklu Dağıtım Desteği (Multi-Distro Engine)**:
   - `src/ArchPackage.py`: `.pkg.tar.zst`, `.pkg.tar.xz`, `.pkg.tar.gz` paketlerini çözme, `.PKGINFO` ayrıştırma ve zstd dosya ağacı denetimi.
   - `src/PackageLoader.py`: `.deb` ve `.pkg.tar.*` formatlarını polimorfik olarak otomatik açan evrensel paket fabrikası.
   - `PKGBUILD` ve `.SRCINFO`: Standart Arch Linux / AUR derleme ve paketleme dosyaları.
   - `pacman` motoru: Arch üzerinde `pacman -U` ve `pacman -Rns` komutlarıyla paket kurma ve kaldırma; `/var/lib/pacman/db.lck` kilit kontrolü.
   - `debtap` köprüsü: Arch Linux üzerinde `.deb` açıldığında otomatik paket dönüştürme ve kurma.

3. **Toplu Kurulum Kuyruğu (Batch Installer)**:
   - Çoklu paket seçimi ve sürükle-bırak desteği.
   - Tüm kuyruğu **tek bir PolicyKit yetkilendirme oturumunda** çapraz bağımlılıklarla tek seferde kurabilme.

4. **İçerilen Dosyalar Canlı Arama (Included Files)**:
   - Paket içerisindeki tüm dosya ve dizinleri dosya türü ikonları, izin modları ve boyutlarıyla listeleme.
   - Anlık arama kutusu ile sıfır gecikmeli dosya süzme.

5. **Headless CLI Teftiş Modülü (`src/cli.py`)**:
   - `parslinux-package-installer -i <paket>`: Terminalde detaylı metaveri dökümü.
   - `parslinux-package-installer -c <paket>`: Bağımlılıkları kontrol edip eksik paketleri listeleme ve exit code üretme.
   - Uzak HTTP/HTTPS paket URL'lerini otomatik indirip inceleme.

6. **Güvenlik ve Onay Denetimi**:
   - Paket kaldırırken veri ve bağımlılık kaybını önleyen onay modal pencereleri (`Adw.MessageDialog`).
   - Evrensel kilit denetimi (Dpkg ve Pacman).
   - Tam kapsamlı otomatik test paketi (`tests/run_all_tests.py`).
