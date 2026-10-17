# Pars Linux Paket Kurucu — Kullanım Kılavuzu

**Pars Linux Paket Kurucu** (`parslinux-package-installer`), Pars Linux, Debian, Arch Linux ve Fedora tabanlı dağıtımlarda `.deb`, `.pkg.tar.*`, `.rpm`, `.AppImage`, `.flatpakref` ve `.flatpakrepo` uzantılı yerel yazılım paketlerini incelemenizi, bağımlılık durumlarını denetlemenizi ve tek tıkla kurup kaldırmanızı sağlayan saf **GTK 4 ve Libadwaita** tabanlı modern bir grafiksel araçtır.

---

## 1. Paket Açma Yöntemleri

### 1.1. Çift Tıklama ile Açma (Önerilen)
Web tarayıcınızdan veya dosya yöneticinizden indirdiğiniz herhangi bir `.deb`, `.pkg.tar.zst`, `.rpm`, `.AppImage` veya `.flatpakref` dosyasına çift tıkladığınızda, uygulama otomatik olarak açılır ve paketin bilgilerini yükler.

### 1.2. Sürükle ve Bırak (Drag & Drop)
Uygulama açıkken herhangi bir desteklenen paketi pencereye sürükleyip bırakabilirsiniz. Birden çok dosya sürüklerseniz uygulama doğrudan **Toplu Kurulum Kuyruğu** ekranına geçer.

### 1.3. Aç Butonu ile Dosya Seçme
Karşılama ekranında yer alan **Paket Aç** butonuna veya üst çubuktaki (HeaderBar) dosya açma simgesine tıklayarak dosya yöneticisinden tekli veya çoklu paket seçebilirsiniz.

### 1.4. Uçbirimden (CLI) ve Hızlı Betiklerle Başlatma
Terminal üzerinden bir veya birden fazla yerel paket yolu ya da doğrudan bir web URL'si vererek başlatabilirsiniz:

```bash
# Otomasyon betiği ile yerel geliştirme modunda çalıştırma:
./run.sh paket.deb
./run.sh paket.pkg.tar.zst
./run.sh paket.rpm
./run.sh uygulama.AppImage
./run.sh yazilim.flatpakref

# Çoklu dosya (Toplu kuyruk):
./run.sh app1.deb app2.deb app3.deb

# Uzak web adresi (otomatik indirip açar):
./run.sh https://example.com/uygulama.deb

# İnteraktif terminal yönetim paneli:
./manage.sh
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

## 5. AppImage ve Flatpak Desteği

### 5.1. AppImage Taşınabilir Paketleri (.AppImage)
* AppImage dosyasını açtığınızda paket detayları, mimarisi ve boyutu otomatik gösterilir.
* **Menüye Ekle**: Tek tıkla dosyaya çalışma izni (`chmod +x`) verilir ve `~/.local/share/applications/` altına standart bir `.desktop` kısayolu yerleştirilir. Uygulama sistem menünüzde hemen görünür.
* **Başlat**: Entegre edilmiş AppImage uygulamalarını doğrudan pencereden başlatabilirsiniz.
* **Menüden Kaldır**: Oluşturulan masaüstü kısayolu tek tıkla temizlenir.

### 5.2. Flathub Flatpakref ve Yazılım Depoları (.flatpakref & .flatpakrepo)
* `.flatpakref` açıldığında uygulama adı, özeti ve Flathub dalı listelenir. "Flathub'dan Kur" butonu ile doğrudan kullanıcı oturumunuza kurulur.
* `.flatpakrepo` açıldığında yazılım deposu adı ve bağlantı adresi listelenir. "Depoyu Ekle" butonu ile sisteme eklenir.

---

## 6. Sorun Giderme

### 6.1. Dpkg / APT Kilit Hatası (Debian / Pars Linux)
* **Sebep**: Arka planda başka bir paket aracı çalışmaktadır.
* **Çözüm**: Diğer güncelleme uygulamasını kapatın. Kilit askıda kaldıysa:
  ```bash
  sudo rm /var/lib/dpkg/lock-frontend
  sudo dpkg --configure -a
  ```

### 6.2. Pacman Kilit Hatası (Arch Linux)
* **Sebep**: `/var/lib/pacman/db.lck` kilit dosyası mevcuttur.
* **Çözüm**: Arka plandaki pacman/yay işlemlerinin bitmesini bekleyin veya askıda kalan kilidi temizleyin:
  ```bash
  sudo rm /var/lib/pacman/db.lck
  ```

### 6.3. Arch Linux'ta .deb Dosyası Kurulumu
* **Çözüm**: Arch Linux üzerinde `.deb` dosyalarını doğrudan kurabilmek için sisteminizde `debtap` bulunması önerilir (`yay -S debtap && sudo debtap -u`). Uygulama `debtap`'ı otomatik algılayıp arka planda Arch paketine dönüştürerek kurar.

