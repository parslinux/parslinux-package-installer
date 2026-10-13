# Ödeme ve Lisans Entegrasyonu Kapsamı (Payment Integration)

Bu doküman, `parslinux-package-installer` uygulamasının ödeme ve ticari paket kapsamını açıklamaktadır.

---

## 1. Kapsam Durumu: Yerel Paket Yöneticisi

`parslinux-package-installer`, yerel diskte bulunan `.deb` ve `.pkg.tar.zst` dosyalarını sisteme kurmak/kaldırmak için tasarlanmış bağımsız, açık kaynaklı ve ücretsiz bir sistem aracıdır.

* **Ödeme Entegrasyonu İçermez**: Bu araç doğrudan herhangi bir ödeme ağ geçidi, kredi kartı işleme veya abonelik mekanizması barındırmaz.
* **Ücretsiz ve Açık Kaynak**: GPL-3.0+ lisansı altındadır.

---

## 2. Pars Linux Ekosisteminde Ödeme ve Mağaza Modeli

Pars Linux ekosistemindeki ücretli, bağış tabanlı veya abonelikli uygulamalar `parslinux-software` (Pars Linux Yazılım Merkezi) üzerinden yönetilir. 

`parslinux-package-installer` yalnızca kullanıcının yerel diskine indirilmiş veya uzak URL'den belirtilmiş olan ikili `.deb` ve `.pkg.tar.zst` paketlerinin sistem kurulumu ve bağımlılık kontrolünden sorumludur.
