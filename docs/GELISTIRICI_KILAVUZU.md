# Pars Linux Paket Kurucu — Geliştirici Kılavuzu

Bu rehber, `parslinux-package-installer` kod tabanına katkıda bulunmak, yerel geliştirme ortamı kurmak, testler çalıştırmak ve çevirileri yönetmek isteyen geliştiriciler içindir.

---

## 1. Geliştirme Ortamı Kurulumu

Uygulama Python 3 ve PyGObject (GTK+ 3) üzerine kuruludur.

### 1.1. Debian / Pars Linux Tabanlı Sistemlerde:
```bash
sudo apt update
sudo apt install -y python3-all python3-gi python3-apt gir1.2-gtk-3.0 gir1.2-notify-0.7 gettext glade
```

### 1.2. Arch Linux Tabanlı Geliştirme Ortamlarında:
Sistemde `python-apt` bulunmasa dahi geliştirilen `DebPackage.py` saf Python ayrıştırıcısı sayesinde arayüz ve paket inceleme özellikleri test edilebilir:
```bash
sudo pacman -S python python-gobject gtk3 libnotify gettext glade
```

---

## 2. Kaynak Koddan Çalıştırma

Projeyi klonladıktan sonra doğrudan geliştirme dizininden çalıştırabilirsiniz:

```bash
# Boş karşılama ekranını açmak için:
python3 src/Main.py

# Belirli bir .deb paketini incelemek için:
python3 src/Main.py /yol/paket.deb
```

Veya kök dizindeki çalıştırıcı betikle:

```bash
./parslinux-package-installer [paket.deb]
```

---

## 3. Test Paketi Oluşturma

Hızlıca yerel bir test `.deb` paketi üretmek için Python'un `tarfile` ve `io` kütüphanelerinden faydalanabilirsiniz:

```python
import io, tarfile, time, os

os.makedirs("scratch", exist_ok=True)
control_text = """Package: ornek-uygulama
Version: 1.0.0
Architecture: all
Maintainer: Pars Linux <dev@parslinux.org>
Installed-Size: 10
Depends: bash
Section: utils
Description: Test Paketi
 Pars Linux Paket Kurucu testleri icin ornek paket.
"""

c_buf = io.BytesIO()
with tarfile.open(fileobj=c_buf, mode="w:gz") as tar:
    data = control_text.encode("utf-8")
    ti = tarfile.TarInfo("./control")
    ti.size = len(data)
    ti.mtime = int(time.time())
    tar.addfile(ti, io.BytesIO(data))

d_buf = io.BytesIO()
with tarfile.open(fileobj=d_buf, mode="w:gz") as tar:
    content = b"echo 'Merhaba'\n"
    ti = tarfile.TarInfo("./usr/bin/ornek")
    ti.size = len(content)
    ti.mtime = int(time.time())
    tar.addfile(ti, io.BytesIO(content))

def make_ar_entry(name, content):
    name_bytes = name.encode("ascii").ljust(16)
    mtime = str(int(time.time())).encode("ascii").ljust(12)
    owner = b"0     "
    group = b"0     "
    mode = b"100644  "
    size = str(len(content)).encode("ascii").ljust(10)
    pad = b"\n" if len(content) % 2 == 1 else b""
    return name_bytes + mtime + owner + group + mode + size + b"`\n" + content + pad

with open("scratch/ornek-uygulama_1.0.0_all.deb", "wb") as f:
    f.write(b"!<arch>\n")
    f.write(make_ar_entry("debian-binary", b"2.0\n"))
    f.write(make_ar_entry("control.tar.gz", c_buf.getvalue()))
    f.write(make_ar_entry("data.tar.gz", d_buf.getvalue()))
```

---

## 4. Testleri Çalıştırma

Kod tabanındaki bağımsız ayrıştırıcıyı, arayüz yüklemesini ve sinyal geçişlerini doğrulamak için:

```bash
python3 -c '
import sys
sys.path.insert(0, "src")
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib
from DebPackage import DebPackage
from MainWindow import MainWindow

pkg = DebPackage("scratch/ornek-uygulama_1.0.0_all.deb")
assert pkg.pkgname == "ornek-uygulama"
assert pkg["Version"] == "1.0.0"
print("DebPackage Test: OK")
'
```

---

## 5. Çevirileri (i18n) Güncelleme

Yeni bir metin eklendiğinde veya var olanlar güncellendiğinde:

1. Metnin kodda `_("Metin")` veya Glade içinde `translatable="yes"` olarak işaretlendiğinden emin olun.
2. `po/files` listesine gerekirse yeni dosya ekleyin.
3. Çevirileri tazelemek için betiği çalıştırın:
   ```bash
   ./update-translations.sh
   ```
4. `po/tr.po` ve `po/pt.po` dosyalarındaki çevirileri tamamlayın.
5. `setup.py` çalıştırıldığında `.mo` ikili dosyaları otomatik üretilir.

---

## 6. Arayüzü (UI) Düzenleme

Arayüz `ui/MainWindow.glade` dosyası içerisindedir. Glade görsel aracı ile düzenlenebilir:

```bash
glade ui/MainWindow.glade
```

Düzenleme yaparken bileşen id'lerinin (`mainwindow`, `mainstack`, `button1`, `button2`, `pacname`, `errorlabel` vb.) `src/MainWindow.py` içerisindeki bağlayıcılarla uyumlu kalmasına dikkat edilmelidir.
