# Pars Linux Paket Kurucu — Uçbirim (CLI) Referansı

`parslinux-package-installer` grafiksel bir uygulama olmasına rağmen uçbirimden parametrelerle çalıştırılabilir ve arka planda `Actions.py` yardımcı komut satırı aracını kullanır.

---

## 1. Ana Komut: `parslinux-package-installer`

### Kullanım Şekli:
```bash
parslinux-package-installer [SEÇENEKLER] [DOSYA.DEB]
```

### Parametreler:
* `[DOSYA.DEB]`: İncelenecek ve kurulacak Debian paket dosyasının göreceli veya mutlak dosya yolu. Parametre verilmezse uygulama boş karşılama ekranıyla açılır.
* `--help`, `-h`: Yardım mesajını görüntüler.
* `--version`: Sürüm numarasını görüntüler.

### Örnekler:
```bash
# Boş karşılama ekranını aç
parslinux-package-installer

# İndirilen paketi doğrudan aç
parslinux-package-installer ~/İndirilenler/discord_0.0.40_amd64.deb

# Göreceli yoldan aç
parslinux-package-installer ./test.deb
```

---

## 2. Arka Plan İşlem Komutu: `Actions.py`

`Actions.py`, grafik arayüz tarafından `pkexec` (PolicyKit) ile yetkilendirilerek çağrılan kök yetkili yardımcı betiktir.

### Kullanım Şekli:
```bash
pkexec /usr/share/parslinux/parslinux-package-installer/src/Actions.py <EYLEM> <HEDEF>
```

### Eylemler (`<EYLEM>`):
* `install <dosya.deb>`: Belirtilen yerel `.deb` paketini `apt install <yol> -yq -o APT::Status-Fd=2` komutu ile kurar.
* `reinstall <dosya.deb>`: Aynı sürümdeki paketi `--reinstall --allow-downgrades` bayraklarıyla yeniden kurar.
* `downgrade <dosya.deb>`: Paketi `--allow-downgrades` bayrağı ile eski sürüme düşürür.
* `remove <paket_adi>`: Belirtilen kurulu paketi `apt remove --purge <paket_adi>` ile sistemden tamamen kaldırır.

### Çıkış Kodları (Exit Codes):
* `0`: İşlem başarıyla tamamlandı.
* `1`: Hata oluştu (Kilit hatası, bağımlılık çözülememesi vb.).
* `256`: Başka bir paket yönetim aracı çalıştığı için kilit alınamadı.
