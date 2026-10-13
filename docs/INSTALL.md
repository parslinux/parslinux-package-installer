# Pars Linux Paket Kurucu — Kurulum Kılavuzu

Bu doküman, `parslinux-package-installer` uygulamasının farklı Linux dağıtımlarında sisteme kurulumunu ve kaldırılmasını açıklamaktadır.

---

## 1. Yöntem 1: Pars Linux / Debian Resmi Depolarından Kurulum (Önerilen)

Paket Pars Linux ve Debian resmi depolarına eklendiğinde doğrudan APT ile kurulabilir:

```bash
sudo apt update
sudo apt install parslinux-package-installer
```

Kurulumun ardından uygulama menünüze eklenecek ve `.deb` dosyaları için varsayılan açıcı olarak atanacaktır.

---

## 2. Yöntem 2: Arch Linux (AUR / PKGBUILD) ile Kurulum

Arch Linux, Manjaro veya EndeavourOS üzerinde depoyu klonlayıp PKGBUILD ile tek komutla kurabilirsiniz:

```bash
git clone https://github.com/parslinux/parslinux-package-installer.git
cd parslinux-package-installer
makepkg -si
```

Arch Linux'ta kaldırırken:
```bash
sudo pacman -Rns parslinux-package-installer
```

---

## 3. Yöntem 3: `.deb` Paket Dosyası ile Kurulum

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

## 4. Yöntem 4: Kaynak Koddan Kurulum (Geliştirici Kurulumu)

### 4.1. Bağımlılıkları Yükleyin

Debian / Ubuntu / Pars Linux:
```bash
sudo apt update
sudo apt install -y python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-notify-0.7 zstd policykit-1 gettext
```

Arch Linux tabanlı sistemlerde:
```bash
sudo pacman -S python python-gobject gtk4 libadwaita libnotify zstd polkit gettext
```

### 4.2. Depoyu İndirin ve Kurun

```bash
git clone https://github.com/parslinux/parslinux-package-installer.git
cd parslinux-package-installer
sudo python3 setup.py install --root=/ --optimize=1
```

---

## 5. Doğrulama ve Test

Kurulumun başarılı olduğunu doğrulamak için:

```bash
which parslinux-package-installer
parslinux-package-installer --version
parslinux-package-installer --help
```

---

## 6. Kaldırma (Uninstall)

### Debian / Pars Linux:
```bash
sudo apt remove --purge parslinux-package-installer
```

### Arch Linux:
```bash
sudo pacman -Rns parslinux-package-installer
```
