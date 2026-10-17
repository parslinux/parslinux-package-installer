# Pars Linux Paket Kurucu — Kurulum Kılavuzu

Bu doküman, `parslinux-package-installer` v3.0.0 uygulamasının farklı Linux dağıtımlarında sisteme kurulumunu ve kaldırılmasını açıklamaktadır.

---

## 1. Hızlı ve Otomatik Kurulum (Önerilen Script)

Depoyu klonladıktan sonra sisteminize uygun bağımlılıkları otomatik algılayıp kuran kurulum betiğini çalıştırabilirsiniz:

```bash
git clone https://github.com/parslinux/parslinux-package-installer.git
cd parslinux-package-installer

# Bağımlılıkları kontrol eder ve sisteme (/usr) kurar:
sudo ./install.sh
```

Sistemden tamamen temizlemek için:
```bash
sudo ./uninstall.sh
```

---

## 2. Pars Linux / Debian Resmi Depolarından Kurulum

Paket Pars Linux ve Debian depolarına eklendiğinde doğrudan APT ile kurulabilir:

```bash
sudo apt update
sudo apt install parslinux-package-installer
```

Kurulumun ardından uygulama menünüze eklenecek ve `.deb`, `.pkg.tar.*`, `.rpm`, `.appimage`, `.flatpakref`, `.flatpakrepo` dosyaları için sistem ilişkilendirmeleri tamamlanacaktır.

---

## 3. Arch Linux (AUR / PKGBUILD) ile Kurulum

Arch Linux, CachyOS, Manjaro veya EndeavourOS üzerinde depoyu klonlayıp PKGBUILD ile tek komutla kurabilirsiniz:

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

## 4. `.deb` Paket Dosyası ile Kurulum

Elinizde derlenmiş `parslinux-package-installer_3.0.0_all.deb` paketi bulunuyorsa:

```bash
sudo apt install ./parslinux-package-installer_3.0.0_all.deb
```

Veya `dpkg` kullanarak:

```bash
sudo dpkg -i parslinux-package-installer_3.0.0_all.deb
sudo apt-get install -f -y  # Eksik bağımlılıkları tamamlamak için
```

---

## 5. Kaynak Koddan Manuel Kurulum

### 5.1. Bağımlılıkları Yükleyin

Debian / Ubuntu / Pars Linux:
```bash
sudo apt update
sudo apt install -y python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-notify-0.7 zstd policykit-1 gettext desktop-file-utils shared-mime-info
```

Arch Linux tabanlı sistemlerde:
```bash
sudo pacman -S python python-gobject gtk4 libadwaita libnotify zstd polkit gettext desktop-file-utils shared-mime-info
```

Fedora tabanlı sistemlerde:
```bash
sudo dnf install -y python3 python3-gobject gtk4 libadwaita libnotify zstd polkit gettext desktop-file-utils shared-mime-info
```

### 5.2. Kurulum Komutu

```bash
git clone https://github.com/parslinux/parslinux-package-installer.git
cd parslinux-package-installer
sudo python3 setup.py install --root=/ --optimize=1
```

---

## 6. Doğrulama ve Test

Kurulumun başarılı olduğunu doğrulamak için:

```bash
which parslinux-package-installer
parslinux-package-installer --version
parslinux-package-installer --help
```

---

## 7. Kaldırma (Uninstall)

### Script ile Kaldırma:
```bash
sudo ./uninstall.sh
```

### Debian / Pars Linux (APT):
```bash
sudo apt remove --purge parslinux-package-installer
```

### Arch Linux (Pacman):
```bash
sudo pacman -Rns parslinux-package-installer
```

