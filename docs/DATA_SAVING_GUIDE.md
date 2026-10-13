# Pars Linux Paket Kurucu — Veri Tasarrufu ve Önbellek Kılavuzu

Bu kılavuz, kotalı internet bağlantılarında veya çevrimdışı (offline) ortamlarda `parslinux-package-installer` kullanırken veri tasarrufu sağlama ve önbellek yönetimi yöntemlerini açıklar.

---

## 1. Paket Önbelleğinin Kullanımı (APT ve Pacman)

### Debian / Ubuntu (APT)
Bir `.deb` paketi kurulurken eksik bağımlılıklar varsa, APT bu bağımlılıkları depolardan indirir ve `/var/cache/apt/archives/` dizininde saklar.
* Disk alanı daraldığında önbellek temizlenebilir:
  ```bash
  sudo apt clean     # Tüm önbelleği siler
  sudo apt autoclean # Artık depolarda bulunmayan eski paketleri siler
  ```

### Arch Linux (Pacman)
Arch Linux üzerinde `.pkg.tar.zst` paketlerinin bağımlılıkları veya sistem paketleri `/var/cache/pacman/pkg/` dizininde saklanır.
* Disk alanı daraldığında veya veri temizliği istendiğinde:
  ```bash
  sudo pacman -Sc    # Kurulu olmayan eski paketlerin önbelleğini temizler
  sudo pacman -Scc   # Tüm önbelleği tamamen siler
  paccache -r        # pacman-contrib ile son 3 sürüm haricini temizler
  ```

---

## 2. Çevrimdışı (Offline) Paket Kurulumu

İnternet bağlantısı olmayan veya kısıtlı olan ortamlarda:

1. Uygulamanın **Bağımlılıklar** panelinden paketin ihtiyaç duyduğu kütüphaneleri inceleyin.
2. İnternet erişimi olan başka bir makinede bu bağımlılıkları indirin:
   - **Debian / Pars Linux:**
     ```bash
     apt-get download <bagimlilik_adi>
     ```
   - **Arch Linux:**
     ```bash
     pacman -Sw <bagimlilik_adi>   # Paketleri kurmadan /var/cache/pacman/pkg altına indirir
     ```
3. İndirilen tüm `.deb` veya `.pkg.tar.zst` paketlerini hedef sisteme aktarın.
4. Toplu kurulum listesine ekleyerek tek seferde `parslinux-package-installer` ile kurunuz.

---

## 3. Bant Genişliği Tasarrufu İpuçları

* Yerel paket kurucu yalnızca sistemde eksik olan bağımlılıkları çeker; halihazırda sistemde mevcut olan kütüphaneleri tekrar indirmez.
* Sürüm düşürme veya yeniden yükleme işlemlerinde paket dosyası yerel olarak zaten mevcutsa gereksiz ağ trafiği oluşturulmaz.
