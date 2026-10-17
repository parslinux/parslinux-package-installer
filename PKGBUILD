# Maintainer: Pars Linux Developers <dev@parslinux.org>
pkgname=parslinux-package-installer
pkgver=3.0.0
pkgrel=1
pkgdesc="Pars Linux Package Installer for Debian (.deb), Arch Linux (.pkg.tar.*), and RPM (.rpm) packages"
arch=('any')
url="https://parslinux.org"
license=('GPL-3.0-or-later')
depends=(
    'python'
    'python-gobject'
    'gtk3'
    'libadwaita'
    'libnotify'
    'polkit'
    'zstd'
)
optdepends=(
    'debtap: Convert and install Debian (.deb) packages on Arch Linux'
)
makedepends=(
    'python-setuptools'
    'gettext'
)

build() {
    cd "$srcdir/$pkgname-$pkgver" 2>/dev/null || cd "$startdir"
    python3 setup.py build
}

package() {
    cd "$srcdir/$pkgname-$pkgver" 2>/dev/null || cd "$startdir"
    python3 setup.py install --root="$pkgdir" --prefix=/usr --optimize=1
}
