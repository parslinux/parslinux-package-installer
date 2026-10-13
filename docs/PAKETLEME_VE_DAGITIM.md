# Pars Linux Paket Kurucu — Paketleme ve Dağıtım Kılavuzu

Bu doküman, `parslinux-package-installer` uygulamasının Pars Linux ve Debian tabanlı dağıtımlar için `.deb` formatında paketlenmesi, sistem entegrasyonu ve dağıtım adımlarını açıklamaktadır.

---

## 1. Sistem Gereksinimleri

Paketleme ortamında aşağıdaki derleme ve geliştirme araçlarının bulunması gerekir:

```bash
sudo apt update
sudo apt install -y debhelper-compat dh-python python3-all python3-setuptools gettext devscripts git-buildpackage
```

---

## 2. Dosya Sistemi Düzeni

Paket kurulduğunda dosya sistemine yerleşecek olan temel yollar:

| Kaynak | Hedef Yol | Açıklama |
|:---|:---|:---|
| `parslinux-package-installer` | `/usr/bin/parslinux-package-installer` | Ana çalıştırılabilir ikili/betik |
| `pardus-package-installer` | `/usr/bin/pardus-package-installer` | Geriye dönük uyumluluk sarmalayıcısı |
| `src/*` | `/usr/share/parslinux/parslinux-package-installer/src/` | Uygulama mantığı ve `Actions.py` |
| `ui/*` | `/usr/share/parslinux/parslinux-package-installer/ui/` | Glade XML arayüz tanımları |
| `*.desktop` | `/usr/share/applications/org.parslinux.package-installer.desktop` | Masaüstü menüsü ve MIME ilişkilendirmesi |
| `*.policy` | `/usr/share/polkit-1/actions/org.parslinux.pkexec.parslinux-package-installer.policy` | PolicyKit yetkilendirme politikası |
| `images/*.svg` | `/usr/share/icons/hicolor/scalable/apps/parslinux-package-installer.svg` | Uygulama ikonu |
| `po/*/*.mo` | `/usr/share/locale/<dil>/LC_MESSAGES/parslinux-package-installer.mo` | Derlenmiş yerelleştirme dosyaları |

---

## 3. Debian Paketi Derleme

### 3.1. `debuild` veya `dpkg-buildpackage` ile Derleme

Depo kök dizinindeyken:

```bash
# İmzasız olarak hızlıca derlemek için:
dpkg-buildpackage -us -uc -b
```

veya `debuild` ile:

```bash
debuild -b -uc -us
```

Derleme tamamlandığında bir üst dizinde (`../`) `parslinux-package-installer_1.0.0_all.deb` paketi üretilir.

### 3.2. `git-buildpackage` (gbp) ile Derleme

```bash
gbp buildpackage --git-export-dir=/tmp/build/parslinux-package-installer -us -uc
```

---

## 4. MIME Türü ve Masaüstü Entegrasyonu

Uygulamanın `.deb` dosyaları için varsayılan uygulama olması için masaüstü veritabanlarının güncellenmesi gerekir. Bu işlem `.deb` paketi kurulurken `postinst` betikleri ve paket yöneticisi tetikleyicileri (triggers) tarafından otomatik yürütülür:

```bash
# Masaüstü ve MIME veritabanlarını el ile tazelemek için:
sudo update-desktop-database /usr/share/applications
sudo update-mime-database /usr/share/mime
```

Kullanıcı düzeyinde varsayılan yapmak için (`~/.config/mimeapps.list`):

```ini
[Default Applications]
application/vnd.debian.binary-package=org.parslinux.package-installer.desktop
application/x-deb=org.parslinux.package-installer.desktop
application/x-debian-package=org.parslinux.package-installer.desktop
```

---

## 5. Polkit İzinleri ve Güvenlik Doğrulaması

`/usr/share/polkit-1/actions/org.parslinux.pkexec.parslinux-package-installer.policy` dosyasının dosya izinleri `0644` ve sahibi `root:root` olmalıdır.

Politikanın geçerliliğini test etmek için:

```bash
pkcheck --action-id org.parslinux.pkexec.parslinux-package-installer --process $$
```

---

## 6. Üretilen Paketin Test Edilmesi

Derlenen paketi test ortamında kurmak için:

```bash
sudo apt install ../parslinux-package-installer_1.0.0_all.deb
```

Kurulumun ardından herhangi bir test `.deb` paketiyle sınayınız:

```bash
parslinux-package-installer test_app.deb
```
