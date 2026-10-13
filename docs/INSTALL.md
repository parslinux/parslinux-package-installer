# Pars Linux Paket Kurucu — Kurulum Kılavuzu

Bu doküman, `parslinux-package-installer` uygulamasının farklı yöntemlerle sisteme kurulumunu ve kaldırılmasını açıklamaktadır.

---

## 1. Yöntem 1: Pars Linux / Debian Resmi Depolarından Kurulum (Önerilen)

Paket Pars Linux resmi depolarına eklendiğinde doğrudan APT ile kurulabilir:

```bash
sudo apt update
sudo apt install parslinux-package-installer
```

Kurulumun ardından uygulama menünüze eklenecek ve `.deb` dosyaları için varsayılan açıcı olarak atanacaktır.

---

## 2. Yöntem 2: `.deb` Paket Dosyası ile Kurulum

Elinizde derlenmiş `parslinux-package-installer_1.0.0_all.deb` paketi bulunuyorsa:

```bash
sudo apt install ./parslinux-package-installer_1.0.0_all.deb
```

Veya `dpkg` kullanarak:

```bash
sudo dpkg -i parslinux-package-installer_1.0.0_all.deb
sudo apt-get install -f -y  # Eksik bağımlılıkları tamamlamak için
```

---

## 3. Yöntem 3: Kaynak Koddan Kurulum (Geliştirici Kurulumu)

### 3.1. Bağımlılıkları Yükleyin

Debian / Ubuntu / Pars Linux:
```bash
sudo apt update
sudo apt install -y python3 python3-gi python3-apt gir1.2-gtk-3.0 gir1.2-notify-0.7 gettext
```

Arch Linux tabanlı sistemlerde:
```bash
sudo pacman -S python python-gobject gtk3 libnotify gettext
```

### 3.2. Depoyu İndirin ve Çalıştırın

```bash
git clone https://github.com/parslinux/parslinux-package-installer.git
cd parslinux-package-installer
python3 setup.py install --user
```

veya sistem geneline:

```bash
sudo python3 setup.py install --root=/
```

---

## 4. Doğrulama ve Test

Kurulumun başarılı olduğunu doğrulamak için:

```bash
which parslinux-package-installer
parslinux-package-installer --help
```

---

## 5. Kaldırma (Uninstall)

Sistemden tamamen kaldırmak için:

```bash
sudo apt remove --purge parslinux-package-installer
```
