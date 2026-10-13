# Pars Linux Paket Kurucu — Veri Tasarrufu ve Önbellek Kılavuzu

Bu kılavuz, kotalı internet bağlantılarında veya çevrimdışı (offline) ortamlarda `parslinux-package-installer` kullanırken veri tasarrufu sağlama ve önbellek yönetimi yöntemlerini açıklar.

---

## 1. APT Paket Önbelleğinin Kullanımı

Bir `.deb` paketi kurulurken eksik bağımlılıklar varsa, APT bu bağımlılıkları resmi depolardan indirir ve `/var/cache/apt/archives/` dizininde saklar.

* Aynı bağımlılığı kullanan başka bir paket kurarken bu arşivler tekrar indirilmez, önbellekten kullanılır.
* Disk alanı daraldığında önbellek temizlenebilir:
  ```bash
  sudo apt clean     # Tüm önbelleği siler
  sudo apt autoclean # Artık depolarda bulunmayan eski paketleri siler
  ```

---

## 2. Çevrimdışı (Offline) Paket Kurulumu

İnternet bağlantısı olmayan veya kısıtlı olan ortamlarda:

1. Uygulamanın **Bağımlılıklar** panelinden paketin ihtiyaç duyduğu kütüphaneleri inceleyin.
2. İnternet erişimi olan başka bir makinede bu bağımlılıkları indirin:
   ```bash
   apt-get download <bagimlilik_adi>
   ```
3. İndirilen tüm `.deb` paketlerini hedef sisteme aktarın.
4. Önce temel bağımlılık paketlerini, ardından ana uygulamayı `parslinux-package-installer` ile kurunuz.

---

## 3. Bant Genişliği Tasarrufu İpuçları

* Yerel paket kurucu yalnızca sistemde eksik olan bağımlılıkları çeker; halihazırda sistemde mevcut olan kütüphaneleri tekrar indirmez.
* Sürüm düşürme veya yeniden yükleme işlemlerinde paket dosyası yerel olarak zaten mevcutsa gereksiz ağ trafiği oluşturulmaz.
