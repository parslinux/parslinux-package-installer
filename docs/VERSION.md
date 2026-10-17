# Pars Linux Paket Kurucu — Sürüm Politikası

Bu doküman, `parslinux-package-installer` projesinin sürümleme mantığını ve yayınlama döngüsünü açıklar.

---

## 1. Semantik Sürümleme (SemVer 2.0.0)

Uygulama `MAJOR.MINOR.PATCH` biçiminde semantik sürümleme kurallarını takip eder:

* **MAJOR**: Geriye dönük uyumluluğu bozan köklü mimari değişiklikler (örn. GTK 3'ten GTK 4'e geçiş).
* **MINOR**: Geriye dönük uyumlu yeni özellikler ve geliştirmeler (örn. toplu paket kurma özelliği, yeni filtreleme aracı).
* **PATCH**: Geriye dönük uyumlu hata düzeltmeleri ve çeviri güncellemeleri.

---

## 2. Sürüm Senkronizasyonu

Sürüm bilgisi aşağıdaki noktalarda senkronize tutulur:

1. `debian/changelog`: En üstteki sürüm başlığı (örn. `parslinux-package-installer (3.0.0) unstable; urgency=medium`).
2. `PKGBUILD` & `.SRCINFO`: Arch Linux paket sürümü (`pkgver=3.0.0`).
3. `setup.py`: Paket derleme sırasında sürümü otomatik okur ve `src/__version__` dosyasına yazar.
4. `src/__version__`: Çalışma zamanında `MainWindowAdw.py` ve `cli.py` tarafından okunup gösterilir.
5. Git Etiketi (Tag): Sürüm yayınlandığında `v3.0.0` formatında Git etiketi basılır.
