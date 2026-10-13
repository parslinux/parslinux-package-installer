# Pars Linux Paket Kurucu — Yerel Depo ve Barındırma (Self-Hosting) Kılavuzu

Bu kılavuz, kurum içi ağlarda veya özel ortamlarda kendi `.deb` veya `.pkg.tar.zst` paket deponuzu nasıl kuracağınızı ve `parslinux-package-installer` ile uyumlu paket dağıtımını nasıl yapacağınızı açıklar.

---

## 1. Debian / Ubuntu Yerel Deposu Kurma

Hızlı testler ve yerel ağ için `dpkg-scanpackages` ile minimal bir APT deposu kurabilirsiniz:

```bash
# 1. Paketlerin toplanacağı dizini oluşturun
mkdir -p /srv/parslinux-debs
cp *.deb /srv/parslinux-debs/

# 2. Paket indeksini oluşturun
cd /srv/parslinux-debs
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz

# 3. HTTP sunucusu başlatın
python3 -m http.server 8080
```

### İstemci Sistemlere Tanımlama:
İstemci makinelerde `/etc/apt/sources.list.d/local.list`:
```ini
deb [trusted=yes] http://<sunucu_ip>:8080/ ./
```
```bash
sudo apt update
```

---

## 2. Arch Linux Yerel Deposu Kurma

Arch Linux ortamları için `repo-add` aracıyla resmi Pacman veritabanı oluşturulabilir:

```bash
# 1. Paketlerin toplanacağı dizini oluşturun
mkdir -p /srv/parslinux-arch
cp *.pkg.tar.zst /srv/parslinux-arch/

# 2. Pacman depo veritabanını oluşturun
cd /srv/parslinux-arch
repo-add parslocal.db.tar.zst *.pkg.tar.zst

# 3. HTTP sunucusu başlatın
python3 -m http.server 8081
```

### İstemci Sistemlere Tanımlama:
İstemci makinelerde `/etc/pacman.conf` sonuna ekleyin:
```ini
[parslocal]
SigLevel = Optional TrustAll
Server = http://<sunucu_ip>:8081/
```
```bash
sudo pacman -Sy
```

Artık yerel ağdaki paketler ve bağımlılıkları `parslinux-package-installer` tarafından otomatik olarak çözümlenip kurulabilecektir.
