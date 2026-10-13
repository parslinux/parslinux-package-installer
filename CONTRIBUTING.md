# Pars Linux Paket Kurucu — Katkı Sağlama Rehberi

Pars Linux projesine katkıda bulunmak istediğiniz için teşekkür ederiz! Açık kaynak topluluğumuzun katkılarıyla projemiz daha güvenli, hızlı ve kullanıcı dostu hale gelmektedir.

---

## 1. Katkı Türleri

* **Hata Bildirimi (Bug Report)**: Karşılaştığınız beklenmeyen durumları, hata çıktılarını ve yeniden üretme adımlarını detaylandırarak bir konu (issue) açabilirsiniz.
* **Yeni Özellik / İyileştirme**: Yeni özellik istekleri veya arayüz iyileştirme önerileri.
* **Çeviri ve Yerelleştirme**: Yeni diller ekleme veya mevcut Türkçe/Portekizce çevirileri iyileştirme.
* **Dokümantasyon**: Belgeleri genişletme, imla ve teknik detay düzeltmeleri.
* **Kod Katkısı**: Hata düzeltmeleri veya mimari geliştirmeler.

---

## 2. Geliştirme İş Akışı

1. Depoyu kendi hesabınıza çatallayın (Fork).
2. Anlamlı bir dal (branch) açın:
   ```bash
   git checkout -b feature/yeni-ozellik
   ```
   veya
   ```bash
   git checkout -b fix/hata-cozumu
   ```
3. Değişikliklerinizi yapın ve yerel testleri çalıştırın:
   ```bash
   python3 tests/run_all_tests.py
   ```
4. Git commit mesajlarınızı Conventional Commits standardına uygun yazın:
   * `feat: ...` — Yeni bir özellik
   * `fix: ...` — Bir hatanın giderilmesi
   * `docs: ...` — Dokümantasyon değişiklikleri
   * `i18n: ...` — Çeviri ve dil dosyaları
   * `refactor: ...` — Kod sadeleştirme ve yeniden yapılandırma
5. Dalınızı GitHub/GitLab'a itin ve ana depoya bir Çekme İsteği (Pull Request) gönderin.

---

## 3. Kod Standartları

* Kodlar PEP 8 kurallarına uygun, temiz ve okunabilir olmalıdır.
* Grafik arayüz bileşenleri saf **GTK 4 / Libadwaita** widget hiyerarşisine uymalıdır.
* Paket işlemleri doğrudan spesifik sınıflar yerine `PackageLoader.open_package()` polimorfizmi üzerinden yürütülmelidir.
* Kullanıcı arayüzünde gösterilecek metinler `_("Metin")` ile uluslararasılaştırma fonksiyonuna sarılmalıdır.
* Geliştirilen yeni modüller hem Debian/Ubuntu (`python3-apt`) hem de Arch Linux tabanlı ortamları desteklemelidir.
