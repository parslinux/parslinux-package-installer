# Pars Linux Paket Kurucu — Çeviri ve Yerelleştirme Kılavuzu

`parslinux-package-installer`, standart GNU `gettext` altyapısını kullanarak çoklu dil desteği sunar.

---

## 1. Dizin ve Dosya Yapısı

* `po/files`: Çevrilebilir dizgelerin taranacağı kaynak dosyaların listesi (`ui/MainWindow.glade`, `src/MainWindow.py`, `src/DebPackage.py`).
* `po/parslinux-package-installer.pot`: Tüm çevrilebilir dizgeleri içeren ana şablon dosya.
* `po/tr.po`: Türkçe çeviriler.
* `po/pt.po`: Portekizce çeviriler.
* `update-translations.sh`: Şablon ve dil dosyalarını tazeleyen otomatik betik.

---

## 2. Çevirileri Güncelleme İş Akışı

1. Kaynak kod veya Glade dosyalarında yeni metinler eklendiğinde:
   ```bash
   ./update-translations.sh
   ```
2. Bu betik:
   - `xgettext` ile `po/parslinux-package-installer.pot` dosyasını günceller.
   - `msgmerge` ile mevcut `po/*.po` dosyalarını yeni şablonla birleştirir.

---

## 3. Yeni Bir Dil Ekleme

Örneğin Almanca (`de`) desteği eklemek için:

1. `update-translations.sh` dosyasındaki `langs` dizisine dili ekleyin:
   ```bash
   langs=("tr" "pt" "de")
   ```
2. Şablon dosyasından yeni bir dil dosyası kopyalayın:
   ```bash
   cp po/parslinux-package-installer.pot po/de.po
   ```
3. Poedit veya herhangi bir metin düzenleyici ile `po/de.po` dosyasını çevirin.
4. `setup.py` dosyası çalıştırıldığında `/usr/share/locale/de/LC_MESSAGES/parslinux-package-installer.mo` otomatik olarak derlenecektir.
