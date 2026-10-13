# Pars Linux Paket Kurucu — Kullanım Kılavuzu

**Pars Linux Paket Kurucu** (`parslinux-package-installer`), Pars Linux, Debian ve Arch Linux tabanlı dağıtımlarda `.deb` ve `.pkg.tar.zst` uzantılı yerel yazılım paketlerini incelemenizi, bağımlılık durumlarını denetlemenizi ve tek tıkla kurup kaldırmanızı sağlayan saf **GTK 4 ve Libadwaita** tabanlı modern bir grafiksel araçtır.

---

## 1. Paket Açma Yöntemleri

### 1.1. Çift Tıklama ile Açma (Önerilen)
Web tarayıcınızdan veya dosya yöneticinizden indirdiğiniz herhangi bir `.deb` veya `.pkg.tar.zst` dosyasına çift tıkladığınızda, uygulama otomatik olarak açılır ve paketin bilgilerini yükler.

### 1.2. Sürükle ve Bırak (Drag & Drop)
Uygulama açıkken herhangi bir `.deb` veya `.pkg.tar.*` dosyasını pencereye sürükleyip bırakabilirsiniz. Birden çok dosya sürüklerseniz uygulama doğrudan **Toplu Kurulum Kuyruğu** ekranına geçer.

### 1.3. Aç Butonu ile Dosya Seçme
Karşılama ekranında yer alan **Paket Aç** butonuna veya üst çubuktaki (HeaderBar) dosya açma simgesine tıklayarak dosya yöneticisinden tekli veya çoklu paket seçebilirsiniz.

### 1.4. Uçbirimden (CLI) ve Uzak Bağlantı ile Başlatma
Terminal üzerinden bir veya birden fazla yerel paket yolu ya da doğrudan bir web URL'si vererek başlatabilirsiniz:

```bash
# Yerel dosya:
parslinux-package-installer paket.deb
parslinux-package-installer paket.pkg.tar.zst

# Çoklu dosya (Toplu kuyruk):
parslinux-package-installer app1.deb app2.deb app3.deb

# Uzak web adresi (otomatik indirip açar):
parslinux-package-installer https://example.com/uygulama.deb
```

---

## 2. Arayüz ve Görünüm Sekmeleri

Paket başarıyla yüklendiğinde Libadwaita arayüzünde iki ana sekme yer alır:

### 2.1. Paket Detayları Sekmesi
* **Paket Adı ve Sürüm Rozeti**: Resmi adı, paket sürümü ve mimarisi.
* **Durum Bildirimi**: Sistemde kurulu olup olmadığı veya hangi sürümünün kurulu olduğu.
* **Açıklama**: Yazılımın ne işe yaradığını özetleyen metin.
* **Geliştirici / Bakımcı Bilgisi**: Paketi hazırlayan kişi/ekip.
* **Web Sitesi**: Projenin resmi ana sayfası.
* **Disk Boyutu**: Paketin kaplayacağı boyut.
* **Bağımlılıklar (Dependencies)**: Paketin ihtiyaç duyduğu kütüphaneler.

### 2.2. İçerilen Dosyalar Sekmesi (Canlı Arama)
* Paketin içerdiği tüm dosya ve dizinler ağaç listesi olarak gösterilir.
* Dosya türü ikonları (klasör, çalıştırılabilir, sembolik bağ, metin dosyası) ve boyut bilgisi listelenir.
* Üstteki canlı arama kutusuna yazarak paket içindeki binlerce dosya arasında anında arama yapabilirsiniz.

---

## 3. Kurulum, Yükseltme ve Kaldırma

### 3.1. Akıllı Kurulum Butonu
Paketin sistemdeki durumuna göre buton otomatik şekillenir:
1. **Paketi Kur (Install)**: Paket sistemde kurulu değilse görünür. Bağımlılıklar doğrulanıp kurulum başlatılır.
2. **Yükselt (Upgrade)**: İncelediğiniz dosya sistemdeki sürümden daha yeniyse buton "Yükselt" haline gelir.
3. **Tekrar Yükle (Reinstall)**: Aynı sürüm zaten kuruluysa paket dosyalarını tazelemek için "Tekrar Yükle" sunulur.
4. **Sürüm Düşür (Downgrade)**: Dosya, sistemdekinden daha eski bir sürüm ise "Sürüm Düşür" aktifleşir.

### 3.2. Kaldır Butonu ve Güvenlik Onayı
Paket sistemde zaten kuruluysa kırmızı **Kaldır** butonu aktifleşir. Kazara veri veya bağımlılık kaybını önlemek için modern bir onay modal penceresi açılır ve onayınızla kaldırma işlemi gerçekleştirilir.

---

## 4. Toplu Paket Kurulumu (Batch Queue)

Birden çok paket seçildiğinde açılan Toplu Kurulum görünümünde:
1. Kuyruktaki tüm paketlerin adı, sürümü, kurulum durumu ve disk boyutu tablo halinde sunulur.
2. İstemediğiniz paketlerin yanındaki onay kutusunu kaldırabilirsiniz.
3. **Seçilenleri Kur** butonuna bastığınızda:
   - **Tek bir PolicyKit yetkilendirme oturumu** açılır (her paket için ayrı ayrı şifre sorulmaz).
   - Çapraz bağımlılıklar tek bir oturumda çözülerek tüm paketler sıralı kurulur.
   - Tamamlandığında sistem masaüstü bildirimi görüntülenir.

---

## 5. Sorun Giderme

### 5.1. Dpkg / APT Kilit Hatası (Debian / Pars Linux)
* **Sebep**: Arka planda başka bir paket aracı çalışmaktadır.
* **Çözüm**: Diğer güncelleme uygulamasını kapatın. Kilit askıda kaldıysa:
  ```bash
  sudo rm /var/lib/dpkg/lock-frontend
  sudo dpkg --configure -a
  ```

### 5.2. Pacman Kilit Hatası (Arch Linux)
* **Sebep**: `/var/lib/pacman/db.lck` kilit dosyası mevcuttur.
* **Çözüm**: Arka plandaki pacman/yay işlemlerinin bitmesini bekleyin veya askıda kalan kilidi temizleyin:
  ```bash
  sudo rm /var/lib/pacman/db.lck
  ```

### 5.3. Arch Linux'ta .deb Dosyası Kurulumu
* **Çözüm**: Arch Linux üzerinde `.deb` dosyalarını doğrudan kurabilmek için sisteminizde `debtap` bulunması önerilir (`yay -S debtap && sudo debtap -u`). Uygulama `debtap`'ı otomatik algılayıp arka planda Arch paketine dönüştürerek kurar.
