# CLAUDE.md — Pars Linux Package Installer Geliştirici Yönergesi

Bu dosya, `parslinux-package-installer` deposunda çalışan geliştiriciler ve AI kodlama asistanları için kritik rehberdir.

---

## 🛠️ Temel Komutlar

### Uygulamayı Çalıştırma
```bash
# Boş ekranla başlatma
python3 src/Main.py

# Belirli bir paketle başlatma
python3 src/Main.py [dosya.deb]

# Çalıştırıcı ikili ile başlatma
./parslinux-package-installer [dosya.deb]
```

### Testleri Çalıştırma
```bash
# Doğrulama test betiği
python3 -c '
import sys; sys.path.insert(0, "src")
from DebPackage import DebPackage
pkg = DebPackage("scratch/parslinux-hello_1.0.0_all.deb")
assert pkg.pkgname == "parslinux-hello"
print("OK")
'
```

### Çevirileri Derleme / Güncelleme
```bash
./update-translations.sh
python3 setup.py --help
```

---

## 🏛️ Mimari Kuralları

1. **Çift Motor Yaklaşımı**: `src/DebPackage.py` içerisinde hem `python3-apt` hem de saf Python fallback motoru korunmalıdır. `import apt` doğrudan `MainWindow.py` içinde tepe noktada zorunlu tutulmamalı, `DebPackage.HAVE_APT` kontrolü ile kullanılmalıdır.
2. **Kök Yetkisi Ayrımı**: Arayüz (`MainWindow.py`) asla `root` olarak çalıştırılmaz. Paket kurma/kaldırma işlemleri yalnızca `/usr/share/parslinux/parslinux-package-installer/src/Actions.py` üzerinden `pkexec` ile çağrılır.
3. **MIME & GApplication**: Uygulama ID'si `org.parslinux.package-installer` olmalıdır. `do_open` ve `do_activate` sinyalleri yeni pencere oluşturmadan mevcut pencereyi öne getirecek şekilde yönetilmelidir.
4. **UI Düzenleme**: `ui/MainWindow.glade` dosyası GTK 3 standartlarına uygun olmalı, id isimleri `src/MainWindow.py` içindeki `define_components` ile birebir eşleşmelidir.
