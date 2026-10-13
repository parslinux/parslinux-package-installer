# Pars Linux Paket Kurucu — Kullanım Kılavuzu

**Pars Linux Paket Kurucu** (`parslinux-package-installer`), Pars Linux üzerinde `.deb` uzantılı yerel yazılım paketlerini incelemenizi, bağımlılık durumlarını denetlemenizi ve tek tıkla kurup kaldırmanızı sağlayan pratik bir grafiksel araçtır.

---

## 1. Paket Açma Yöntemleri

### 1.1. Çift Tıklama ile Açma (Önerilen)
Web tarayıcınızdan veya dosya yöneticinizden indirdiğiniz herhangi bir `.deb` dosyasına çift tıkladığınızda, Pars Linux Paket Kurucu otomatik olarak açılır ve paketin bilgilerini yükler.

### 1.2. Sürükle ve Bırak (Drag & Drop)
Uygulama açıkken herhangi bir `.deb` dosyasını pencere içerisine sürükleyip bırakabilirsiniz. Uygulama mevcut içeriği temizleyip yeni paketi yükleyecektir.

### 1.3. Aç Butonu ile Dosya Seçme
Uygulama açılış ekranında (`empty` durumu) yer alan **Aç** butonuna veya üst çubuktaki (HeaderBar) dosya açma düğmesine basarak dosya yöneticisinden `.deb` paketinizi seçebilirsiniz.

### 1.4. Uçbirimden (CLI) Başlatma
Terminal üzerinden bir paket yolunu belirterek doğrudan başlatabilirsiniz:

```bash
parslinux-package-installer /home/kullanici/Indirilenler/ornek-paket_1.0.0_amd64.deb
```

---

## 2. Arayüz Elemanları ve Bilgi Alanları

Paket başarıyla yüklendiğinde arayüzde aşağıdaki bilgiler görüntülenir:

* **Paket Adı ve Sürümü**: Paketin resmi adı ve bu dosyadaki sürüm numarası.
* **Kurulu Sürüm**: Paketin sisteminizde halihazırda kurulu olup olmadığını veya hangi sürümünün kurulu olduğunu gösterir.
* **Kısa ve Uzun Açıklama**: Yazılımın ne işe yaradığını özetleyen metin.
* **Geliştirici / Bakımcı Bilgisi**: Paketi hazırlayan kişi/ekip ve e-posta adresi (tıklanabilir `mailto:` bağlantısı).
* **Ana Sayfa**: Projenin resmi web sitesi bağlantısı.
* **Bölüm (Section) & Mimari**: Paketin ait olduğu kategori (`utils`, `admin`, `net` vb.) ve desteklediği işlemci mimarisi (`amd64`, `arm64`, `all`).
* **Boyut**: Paketin sistemde kaplayacağı disk alanı (KiB).
* **Bağımlılıklar (Dependencies)**: Paketin çalışabilmesi için ihtiyaç duyduğu kütüphaneler ve sistem araçları.

---

## 3. Kurulum ve Kaldırma İşlemleri

Uygulamanın sağ üst köşesinde akıllı işlem butonları yer alır:

### 3.1. Kurulum Butonu (`Button 1`)
Paketin durumuna göre bu buton otomatik olarak şekillenir:

1. **Paketi Kur (Install)**: Paket sistemde kurulu değilse görünür. Tıklandığında gerekli bağımlılıklar kontrol edilir ve kurulum başlatılır.
2. **Yükselt (Upgrade)**: İncelediğiniz `.deb` dosyası sisteminizdeki kurulu sürümden daha yeniyse buton "Yükselt" haline gelir.
3. **Tekrar Yükle (Reinstall)**: Aynı sürüm zaten kuruluysa paket dosyalarını onarmak veya tazelemek için "Tekrar Yükle" seçeneği sunulur.
4. **Sürüm Düşür (Downgrade)**: Dosya, sistemde kurulu olandan daha eski bir sürüm ise "Sürüm Düşür" seçeneği aktifleşir.

> [!NOTE]
> Kurulum işlemi başladığında sizden sistem yöneticisi (root/sudo) şifreniz istenecektir.

### 3.2. Paketi Kaldır Butonu (`Button 2`)
Eğer incelenen paket sisteminizde zaten kuruluysa kırmızı çöp kutusu simgeli **Kaldır** butonu aktifleşir. Bu butona basıldığında paket tüm yapılandırmalarıyla sistemden temizlenir.

---

## 4. İlerleme Takibi ve Terminal Detayları

Kurulum veya kaldırma butonuna basıldığında:
1. Üst kısımda anlık yüzdeyi gösteren bir **İlerleme Çubuğu** belirir.
2. Sağ alttaki **Detayları Göster** butonuna tıklayarak açılan terminal konsolundan APT ve Dpkg süreçlerinin arka plandaki canlı çıktılarını izleyebilirsiniz.
3. İşlem tamamlandığında sistem bildirimi ve başarı ekranı görüntülenir.

---

## 5. Sık Karşılaşılan Sorunlar ve Çözümleri

### 5.1. Dpkg Kilit Hatası (Dpkg Lock Error)
* **Sebep**: Arka planda `apt`, `synaptic`, `parslinux-software` veya başka bir güncelleme aracı çalışıyor olabilir.
* **Çözüm**: Diğer paket yöneticisi uygulamasını kapatın ve birkaç saniye sonra tekrar deneyin.

### 5.2. Yarım Kalan Yapılandırma Hatası (Dpkg Interrupt Error)
* **Sebep**: Daha önceki bir kurulum yarım kalmış veya kesintiye uğramıştır.
* **Çözüm**: Bir uçbirim açarak aşağıdaki komutu çalıştırın:
  ```bash
  sudo dpkg --configure -a
  ```

### 5.3. Karşılanamayan Bağımlılıklar (Unsatisfied Dependencies)
* **Sebep**: Paketin ihtiyaç duyduğu kütüphaneler Pars Linux resmi depolarında bulunmuyor veya sürüm uyuşmazlığı var.
* **Çözüm**: Uçbirimde `sudo apt update && sudo apt install -f` komutunu çalıştırarak depoları tazeleyin. Paket üçüncü taraf ve uyumsuz bir sistem için derlenmişse ilgili kütüphanenin temin edilmesi gerekir.

### 5.4. Mimari Hatası (Package Architecture Error)
* **Sebep**: 64-bit (`amd64`) bir sisteme örneğin 32-bit (`i386`) veya ARM (`arm64`) için hazırlanmış bir paketi kurmaya çalışmak.
* **Çözüm**: Sisteminizin mimarisine uygun `.deb` dosyasını indirdiğinizden emin olun.
