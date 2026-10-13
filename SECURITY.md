# Güvenlik Politikası

Pars Linux ekibi olarak kullanıcılarımızın güvenliğini ve sistem bütünlüğünü en üst düzeyde tutmayı taahhüt ediyoruz.

---

## 1. Desteklenen Sürümler

| Sürüm | Destek Durumu |
|:---|:---|
| 2.0.x | :white_check_mark: Aktif Olarak Destekleniyor |
| 1.x   | :warning: Güvenlik Güncellemeleri |
| < 1.0 | :x: Desteklenmiyor |

---

## 2. Güvenlik Modeli ve Polkit İncelemesi

`parslinux-package-installer` aşağıdaki güvenlik ilkelerine göre çalışır:

1. **Ayrıcalıksız Grafik Arayüz**: Grafiksel arayüz (`src/MainWindowAdw.py` / `src/Main.py`), GTK 4 / Libadwaita pencereleri ve paket inceleme mekanizmaları kesinlikle standart kullanıcı izinleriyle çalışır. Kök (`root`) yetkisi gerektirmez.
2. **Korumalı Yürütme**: Yalnızca paket kurulum ve kaldırma komutları (`src/Actions.py`) PolicyKit (`pkexec`) üzerinden denetlenir.
3. **Kural Denetimi**: `/usr/share/polkit-1/actions/org.parslinux.pkexec.parslinux-package-installer.policy` dosyası yalnızca yetkili sistem yöneticilerinin paket işlem yapabilmesine izin verir.
4. **Kilit Koruması**: Eşzamanlı paket yöneticisi çalıştırmalarından kaynaklanan veritabanı bozulmalarını önlemek için sistem paket kilitleri (Debian/Ubuntu için `/var/lib/dpkg/lock-frontend`, Arch Linux için `/var/lib/pacman/db.lck`) her işlem öncesinde kontrol edilir.

---

## 3. Güvenlik Açığı Bildirimi

Bir güvenlik açığı keşfederseniz, lütfen bunu herkese açık GitHub/GitLab sorunlarında (Issues) paylaşmayınız. 

Bunun yerine açığı şu adrese bildiriniz:

* **E-posta**: `security@parslinux.org` veya `dev@parslinux.org`
* **İçerik**:
  * Açığın türü ve etkisi
  * Yeniden üretme adımları ve PoC (varsa)
  * Etkilenen sistem ve mimari bilgileri

Güvenlik bildiriminiz en geç 48 saat içinde değerlendirilecek ve gerekli yamalar ivedilikle hazırlanacaktır.
