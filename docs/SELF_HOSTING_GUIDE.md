# Pars Linux Paket Kurucu — Yerel Depo ve Barındırma (Self-Hosting) Kılavuzu

Bu kılavuz, kurum içi ağlarda veya özel ortamlarda kendi `.deb` paketi deponuzu nasıl kuracağınızı ve `parslinux-package-installer` ile uyumlu paket dağıtımını nasıl yapacağınızı açıklar.

---

## 1. Basit Yerel Dizin Deposu Kurma

Hızlı testler ve yerel ağ için `dpkg-scanpackages` ile minimal bir depo kurabilirsiniz:

```bash
# 1. Paketlerin toplanacağı dizini oluşturun
mkdir -p /srv/parslinux-packages

# 2. .deb paketlerinizi bu dizine kopyalayın
cp *.deb /srv/parslinux-packages/

# 3. Paket indeksini oluşturun
cd /srv/parslinux-packages
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz

# 4. Basit bir HTTP sunucusu başlatın
python3 -m http.server 8080
```

---

## 2. İstemci Sistemlere Depoyu Tanımlama

İstemci makinelerde `/etc/apt/sources.list.d/local.list` dosyası oluşturun:

```ini
deb [trusted=yes] http://<sunucu_ip>:8080/ ./
```

Depoyu güncelleyin:

```bash
sudo apt update
```

Artık yerel ağdaki paketler ve bağımlılıkları `parslinux-package-installer` tarafından otomatik olarak çözümlenip indirilebilir hale gelecektir.
