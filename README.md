# Pars Linux Package Installer

**Pars Linux Package Installer** (`parslinux-package-installer`), Pars Linux ve Debian tabanlı dağıtımlar için tasarlanmış, GDebi dengi modern ve hafif bir grafiksel `.deb` paket yöneticisidir.

İndirilen veya yerel diskte bulunan `.deb` dosyalarına dosya yöneticisinden çift tıklandığında otomatik olarak açılır, bağımlılıkları kontrol eder ve tek tıkla kurulum, yeniden kurulum, yükseltme, sürüm düşürme veya sistemden kaldırma imkânı tanır.

---

## 🚀 Özellikler

- **Çift Tıklama ile Açılma**: `.deb` MIME türleri (`application/vnd.debian.binary-package`, `application/x-deb`, `application/x-debian-package`) ile tam entegre.
- **Sürükle & Bırak Desteği**: İndirilen `.deb` dosyalarını pencereye sürükleyip bırakarak anında inceleme.
- **Akıllı Bağımlılık Kontrolü**:
  - Gerekli tüm bağımlılıkların karşılanıp karşılanmadığını (`All dependencies are satisfied`) doğrular.
  - Eksik bağımlılıkları ve depolardan indirilecek ek paketleri listeler.
  - Sistem mimarisi ile paket mimarisi (örn. `amd64`, `arm64`, `all`) uyumluluğunu denetler.
- **Tek Tıkla Dinamik Kurulum / Kaldırma**:
  - Paket kurulu değilse: **Kur** (`Install`)
  - Paket daha yeni bir sürümse: **Yükselt** (`Upgrade`)
  - Aynı sürüm sistemde mevcutsa: **Yeniden Kur** (`Reinstall`)
  - Daha eski bir sürümse: **Sürüm Düşür** (`Downgrade`)
  - Sistemde mevcutsa: **Kaldır** (`Uninstall`)
- **Detaylı Paket Bilgisi**:
  - Paket adı, sürüm, sistemde kurulu sürüm, açıklama, geliştirici/bakımcı, ana sayfa, bölüm ve paket boyutu.
- **Güvenli Yetkilendirme (Polkit)**:
  - Kurulum ve kaldırma işlemleri PolicyKit (`pkexec`) üzerinden güvenli root haklarıyla yönetilir.
- **Canlı Konsol ve İlerleme Takibi**:
  - APT çıktısını anlık olarak yüzdelik ilerleme çubuğu ve açılır terminal detaylarıyla görüntüler.

---

## 📦 Bağımlılıklar

```bash
gir1.2-glib-2.0 gir1.2-gtk-3.0 gir1.2-notify-0.7 python3-apt
```

---

## 🛠️ Kaynaktan Çalıştırma

```bash
# Bağımlılıkların kurulu olduğundan emin olun
python3 src/Main.py [dosya.deb]
```

Veya doğrudan çalıştırıcı ile:

```bash
./parslinux-package-installer [dosya.deb]
```

---

## 🔨 Paketleme (Debian Paketi Oluşturma)

```bash
sudo apt install devscripts git-buildpackage
sudo mk-build-deps -ir
gbp buildpackage --git-export-dir=/tmp/build/parslinux-package-installer -us -uc
```

---

## 📚 Dokümantasyon

Detaylı teknik kılavuzlar ve belgeler için aşağıdaki bağlantıları inceleyebilirsiniz:

- 📖 [Dokümantasyon İndeksi](docs/INDEX.md)
- 🖥️ [Kullanım Kılavuzu](docs/KULLANIM_KILAVUZU.md) — Grafik arayüz, paket açma yöntemleri ve sorun giderme
- 🏗️ [Mimari Spesifikasyonu](docs/ARCHITECTURE.md) — Modül yapısı, GApplication yaşam döngüsü ve durum makinesi
- 📦 [Paketleme ve Dağıtım](docs/PAKETLEME_VE_DAGITIM.md) — Debian paketi derleme, MIME entegrasyonu ve Polkit
- 💻 [Geliştirici Kılavuzu](docs/GELISTIRICI_KILAVUZU.md) — Geliştirme ortamı, testler ve çeviri yönetimi
- 🔀 [Fork ve Geliştirme Notları](FORK.md) — Proje geçmişi ve yapılan yenilikler
- 🤝 [Katkı Sağlama Rehberi](CONTRIBUTING.md) — Katkı kuralları ve PR iş akışı
- 🔒 [Güvenlik Politikası](SECURITY.md) — Polkit modeli ve güvenlik bildirimleri

---

## 📄 Lisans

GPL-3.0+ — Ayrıntılar için [LICENSE](LICENSE) ve [FORK.md](FORK.md) dosyalarına bakınız.

