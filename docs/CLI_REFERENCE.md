# Pars Linux Paket Kurucu — Uçbirim (CLI) Referansı

`parslinux-package-installer` grafiksel bir uygulama olmasına rağmen uçbirimden parametrelerle çalıştırılabilir ve arka planda `Actions.py` yardımcı komut satırı aracını kullanır.

---

## 1. Ana Komut: `parslinux-package-installer`

### Kullanım Şekli:
```bash
parslinux-package-installer [SEÇENEKLER] [DOSYA1.DEB] [DOSYA2.DEB ...]
```

### Parametreler ve Seçenekler:
* `[DOSYA1.DEB]`: Tek bir paket verilirse doğrudan tekli paket inceleme ve kurma ekranı açılır.
* `[DOSYA1.DEB] [DOSYA2.DEB ...]`: Birden fazla paket verildiğinde doğrudan **Toplu Kurulum (Batch Installer)** kuyruğu açılır.
* `--adw`, `--gtk4`: Uygulamayı modern GTK 4 & Libadwaita arayüz motoru ile başlatır.
* `--help`, `-h`: Yardım mesajını görüntüler.
* `--version`: Sürüm numarasını görüntüler.

### Alternatif Çalıştırıcı: `parslinux-package-installer-adw`
Doğrudan modern GTK 4 / Libadwaita modunda başlatmak için kullanılır:
```bash
parslinux-package-installer-adw [DOSYALAR.DEB...]
```

### Örnekler:
```bash
# Boş karşılama ekranını aç (GTK3)
parslinux-package-installer

# İndirilen paketi doğrudan aç
parslinux-package-installer ~/İndirilenler/discord_0.0.40_amd64.deb

# Birden fazla paketi toplu kuyrukta aç
parslinux-package-installer pkg1.deb pkg2.deb pkg3.deb

# Modern Libadwaita (GTK4) arayüzünde başlat
parslinux-package-installer --adw ./uygulama.deb
parslinux-package-installer-adw ./uygulama.deb
```

---

## 2. Arka Plan İşlem Komutu: `Actions.py`

`Actions.py`, grafik arayüz tarafından `pkexec` (PolicyKit) ile yetkilendirilerek çağrılan kök yetkili yardımcı betiktir.

### Kullanım Şekli:
```bash
pkexec /usr/share/parslinux/parslinux-package-installer/src/Actions.py <EYLEM> <HEDEFLER...>
```

### Eylemler (`<EYLEM>`):
* `install <dosya1.deb> [dosya2.deb ...]`: Belirtilen tekli veya çoklu yerel `.deb` paketlerini `apt install <yollar> -yq -o APT::Status-Fd=2` komutu ile kurar.
* `reinstall <dosya.deb>`: Aynı sürümdeki paketi `--reinstall --allow-downgrades` bayraklarıyla yeniden kurar.
* `downgrade <dosya.deb>`: Paketi `--allow-downgrades` bayrağı ile eski sürüme düşürür.
* `remove <paket1> [paket2 ...]`: Belirtilen kurulu paketleri `apt remove --purge <paketler>` ile sistemden tamamen kaldırır.

### Çıkış Kodları (Exit Codes):
* `0`: İşlem başarıyla tamamlandı.
* `1`: Hata oluştu (Kilit hatası, bağımlılık çözülememesi vb.).
* `256`: Başka bir paket yönetim aracı çalıştığı için kilit alınamadı.
