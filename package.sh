#!/usr/bin/env bash
# ==============================================================================
# Pars Linux Package Installer - Packaging and Build Script
# ==============================================================================
set -e

# Color definitions
RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
BLUE=$'\033[0;34m'
CYAN=$'\033[0;36m'
BOLD=$'\033[1m'
NC=$'\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

DIST_DIR="$PROJECT_DIR/dist"
mkdir -p "$DIST_DIR"

echo -e "${CYAN}${BOLD}=== Pars Linux Package Installer — Package Builder ===${NC}"

show_help() {
    echo -e "Usage: ${BOLD}./package.sh [OPTIONS]${NC}"
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help manual"
    echo "  --deb         Build only Debian / Pars Linux (.deb) package"
    echo "  --arch        Build only Arch Linux (.pkg.tar.zst) package"
    echo "  --clean       Clean previous build artifacts (build, dist, etc.)"
    echo "  --all         Try to build both formats if tools are installed"
    echo ""
    echo "Examples:"
    echo "  ./package.sh          # Auto-detects OS and builds appropriate package"
    echo "  ./package.sh --arch   # Build Arch Linux package"
    echo "  ./package.sh --deb    # Build Debian package"
    echo "  ./package.sh --clean  # Remove build artifacts and temporary files"
}

CLEAN_FIRST=false
TARGET_FORMAT="auto"

for arg in "$@"; do
    case "$arg" in
        -h|--help)
            show_help
            exit 0
            ;;
        --clean)
            CLEAN_FIRST=true
            ;;
        --deb)
            TARGET_FORMAT="deb"
            ;;
        --arch)
            TARGET_FORMAT="arch"
            ;;
        --all)
            TARGET_FORMAT="all"
            ;;
    esac
done

clean_artifacts() {
    echo -e "${BLUE}▶ Cleaning previous build artifacts...${NC}"
    if [ -d build ] && [ ! -w build ]; then
        mv build "/tmp/parslinux_build_$$" 2>/dev/null || true
    fi
    rm -rf build/ dist/ debian/.debhelper/ debian/parslinux-package-installer/ 2>/dev/null || true
    rm -f debian/debhelper-build-stamp debian/files *.deb *.tar.gz *.tar.xz *.pkg.tar.zst
    rm -rf src/__pycache__ tests/__pycache__ __pycache__ *.egg-info
    mkdir -p "$DIST_DIR"
    echo -e "${GREEN}✓ Cleaned successfully.${NC}"
}

if [ "$CLEAN_FIRST" = true ]; then
    clean_artifacts
    if [ "$TARGET_FORMAT" == "auto" ] && [ $# -eq 1 ]; then
        exit 0
    fi
fi

# Detect distribution if target is auto
if [ "$TARGET_FORMAT" == "auto" ]; then
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO_ID="${ID:-}"
        DISTRO_LIKE="${ID_LIKE:-}"
        if [[ "$DISTRO_ID" == "debian" || "$DISTRO_ID" == "ubuntu" || "$DISTRO_ID" == "parslinux" || "$DISTRO_LIKE" == *"debian"* ]]; then
            TARGET_FORMAT="deb"
        elif [[ "$DISTRO_ID" == "arch" || "$DISTRO_ID" == "cachyos" || "$DISTRO_ID" == "manjaro" || "$DISTRO_LIKE" == *"arch"* ]]; then
            TARGET_FORMAT="arch"
        elif command -v dpkg-buildpackage &>/dev/null; then
            TARGET_FORMAT="deb"
        elif command -v makepkg &>/dev/null; then
            TARGET_FORMAT="arch"
        else
            echo -e "${RED}✗ Error: Unable to detect packaging environment!${NC}"
            echo -e "Please specify '${BOLD}--deb${NC}' or '${BOLD}--arch${NC}'."
            exit 1
        fi
    fi
fi

# Update translations
echo -e "${BLUE}▶ Updating translation strings...${NC}"
if [ -f "./update-translations.sh" ]; then
    bash ./update-translations.sh 2>/dev/null || true
fi

# 1. Debian (.deb)
build_deb() {
    echo -e "\n${BLUE}▶ Building Debian / Pars Linux (.deb) package...${NC}"
    if ! command -v dpkg-buildpackage &>/dev/null; then
        echo -e "${RED}✗ Error: 'dpkg-buildpackage' not found!${NC}"
        echo -e "Install via: ${BOLD}sudo apt install -y devscripts debhelper-compat dh-python${NC}"
        return 1
    fi

    dpkg-buildpackage -us -uc -b

    PARENT_DIR="$(dirname "$PROJECT_DIR")"
    FOUND_DEB=$(ls -1 "$PARENT_DIR"/parslinux-package-installer_*_all.deb 2>/dev/null | head -n 1 || true)
    
    if [ -n "$FOUND_DEB" ] && [ -f "$FOUND_DEB" ]; then
        cp -f "$FOUND_DEB" "$DIST_DIR/"
        cp -f "${FOUND_DEB%.deb}.buildinfo" "$DIST_DIR/" 2>/dev/null || true
        cp -f "${FOUND_DEB%.deb}.changes" "$DIST_DIR/" 2>/dev/null || true
        echo -e "${GREEN}✓ Debian package created:${NC} $DIST_DIR/$(basename "$FOUND_DEB")"
    else
        echo -e "${YELLOW}⚠ Package built but could not locate output in parent directory.${NC}"
    fi
}

# 2. Arch Linux (.pkg.tar.zst)
build_arch() {
    echo -e "\n${BLUE}▶ Building Arch Linux (.pkg.tar.zst) package...${NC}"
    if ! command -v makepkg &>/dev/null; then
        echo -e "${RED}✗ Error: 'makepkg' not found!${NC}"
        echo -e "Install via: ${BOLD}sudo pacman -S base-devel${NC}"
        return 1
    fi

    echo -e "  Updating .SRCINFO..."
    makepkg --printsrcinfo > .SRCINFO 2>/dev/null || true

    echo -e "  Executing makepkg..."
    makepkg -f --nodeps

    for pkg in parslinux-package-installer-*.pkg.tar.zst; do
        if [ -f "$pkg" ]; then
            cp -f "$pkg" "$DIST_DIR/"
            echo -e "${GREEN}✓ Arch Linux package created:${NC} $DIST_DIR/$pkg"
        fi
    done
}

case "$TARGET_FORMAT" in
    deb)
        build_deb
        ;;
    arch)
        build_arch
        ;;
    all)
        build_deb || true
        build_arch || true
        ;;
esac

# Summary
echo -e "\n${GREEN}${BOLD}=== Generated Distribution Packages (dist/) ===${NC}"
cd "$DIST_DIR"
if [ "$(ls -A . 2>/dev/null)" ]; then
    for item in *; do
        if [ -f "$item" ]; then
            SIZE=$(du -h "$item" | cut -f1)
            SHA=$(sha256sum "$item" | cut -d' ' -f1)
            echo -e "  📦 ${BOLD}$item${NC} (${SIZE})"
            echo -e "     SHA256: ${CYAN}${SHA}${NC}"
        fi
    done
    echo -e "\n${GREEN}Packaging completed successfully.${NC}"
else
    echo -e "${YELLOW}No package files found in dist/ directory.${NC}"
fi
