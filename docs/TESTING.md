# Pars Linux Paket Kurucu — Test ve Kalite Güvencesi Kılavuzu

Bu doküman, `parslinux-package-installer` üzerinde yürütülen test türlerini, otomatikleştirilmiş doğrulama adımlarını ve test paketleri ile senaryo denemelerini açıklar.

---

## 1. Test Düzeyleri

1. **Birim Testleri (Unit Tests)**: `src/DebPackage.py` sınıfının AR ve Tar arşivlerini okuma, RFC822 kontrol alanlarını ayrıştırma ve bağımlılık listesini çıkarma yeteneklerini sınar.
2. **Arayüz / Entegrasyon Testleri (Integration Tests)**: GTK Builder, sinyal bağlayıcıları ve `MainWindow` durum makinesinin (Empty, Package, Brokendeb, Done vb.) düzgün çalıştığını doğrular.
3. **Senaryo Testleri (Scenario Tests)**: Çift tıklama, sürükle-bırak, dosya açma ve parametreli çalıştırma durumlarının test edilmesi.

---

## 2. Otomatik Doğrulama Betiği

Tüm testleri tek komutla koşturmak için aşağıdaki komutu kullanabilirsiniz:

```bash
python3 -c '
import os, sys
sys.path.insert(0, "src")
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib
from DebPackage import DebPackage
from MainWindow import MainWindow

print(">>> 1. DebPackage ayrıştırma testi...")
pkg = DebPackage("scratch/parslinux-hello_1.0.0_all.deb")
assert pkg.pkgname == "parslinux-hello", "Paket adı uyuşmuyor"
assert pkg["Version"] == "1.0.0", "Sürüm uyuşmuyor"
assert pkg.check() is True, "Bağımlılık kontrolü başarısız"
print("    [PASS] DebPackage motoru başarılı.")

print(">>> 2. Arayüz ve durum testi...")
class TestApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.parslinux.package-installer")

app = TestApp()
f = Gio.File.new_for_path("scratch/parslinux-hello_1.0.0_all.deb")
win = MainWindow(app, f)

loop = GLib.MainLoop()

def verify():
    assert win.pacname.get_text() == "parslinux-hello"
    assert win.button1.get_sensitive() is True
    assert win.button2.get_sensitive() is False
    assert win.mainstack.get_visible_child_name() == "package"
    print("    [PASS] Arayüz başarıyla yüklendi.")
    loop.quit()

GLib.timeout_add(200, verify)
loop.run()
print("TÜM TESTLER BAŞARIYLA TAMAMLANDI!")
'
```

---

## 3. Test Senaryoları Matrisi

| Senaryo No | Test Adı | Beklenen Sonuç |
|:---|:---|:---|
| **TC-01** | Parametresiz başlatma | Boş (`empty`) ekran, "Aç" butonu görünür, "Kur" butonu pasif |
| **TC-02** | Geçerli `.deb` ile başlatma | Paket adı, sürümü ve detayları görünür, "Kur" butonu aktif |
| **TC-03** | Bozuk / geçersiz dosya | `brokendeb` ekranı açılır ve hata mesajı gösterilir |
| **TC-04** | Mimari uyuşmazlığı | Mimari hata etiketi gösterilir ve "Kur" butonu kilitlenir |
| **TC-05** | Eksik bağımlılık | Kırmızı renkte eksik bağımlılık listesi gösterilir |
| **TC-06** | Sürükle ve bırak | Yeni dosya sürüklendiğinde arayüz derhal yeni paketi yükler |
