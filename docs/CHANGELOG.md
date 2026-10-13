# Değişiklik Günlüğü (Changelog) — Pars Linux Package Installer

Tüm önemli sürüm değişiklikleri bu dosyada belgelenmektedir. Format [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standardına uygundur.

---

## [1.0.0] - 2026-10-13

### Eklendi
- **Pars Linux Çatallanması (Fork)**: Proje `pardus-package-installer` temel alınarak Pars Linux için yeniden markalandı.
- **`src/DebPackage.py` Hibrit Ayrıştırıcı**: `python3-apt` bulunmayan ortamlarda saf Python (`tarfile` ve `ar`) ile `.deb` paketlerini açma ve kontrol etme desteği.
- **Akıllı Dosya Yakalama**: Dosya yöneticisinden çift tıklama (`%f` parametresi ve GApplication `do_open`), uçbirim yolu ve sürükle-bırak desteği.
- **Gelişmiş Bağımlılık Raporlama**: Bağımlılıkların eksiksiz karşılanıp karşılanmadığını net yeşil/kırmızı durum göstergeleriyle sunma.
- **Dinamik İşlem Butonu**: Kurulum (0), Sürüm Düşürme (1), Yeniden Kurulum (2), Yükseltme (3) ve Kaldırma durumları için akıllı durum makinesi.
- **Yeni Masaüstü ve Polkit Yapılandırması**: `org.parslinux.package-installer.desktop` ve `org.parslinux.pkexec.parslinux-package-installer.policy`.
- **Kapsamlı Dokümantasyon Seti**: Mimari, kullanım, paketleme, test, CLI ve geliştirici kılavuzları.

### Değiştirildi
- Uygulama ID'si `org.parslinux.package-installer` olarak güncellendi.
- Kök yetkili `Actions.py` betiğinde mutlak dosya yolu çözümlemesi ve gelişmiş kilit denetimi eklendi.
- UI bileşenleri ve metinleri Pars Linux kimliğine uyarlandı.
- Türkçe ve Portekizce dil dosyaları güncellendi.

---

## [0.7.0] - 2026-03-06 (Yukarı Akış / Pardus)
- Sürükle ve bırak desteği eklendi.
- Arka plan iş parçacığı frontend ve backend olarak ikiye ayrıldı.
- Bildirim sistemi optimize edildi.
- Türkçe çeviriler güncellendi.

---

## [0.6.5] - 2025-11-23 (Yukarı Akış / Pardus)
- APT çıktı hata denetimlerine regex desteği eklendi.
- Kilit hataları için bilgilendirme mesajları iyileştirildi.
