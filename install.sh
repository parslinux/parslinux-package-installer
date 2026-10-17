#!/usr/bin/env bash
# ==============================================================================
# Pars Linux Package Installer - System Installation Script
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

echo -e "${CYAN}${BOLD}=== Pars Linux Package Installer — Installer ===${NC}"

show_help() {
    echo -e "Usage: ${BOLD}./install.sh [OPTIONS]${NC}"
    echo ""
    echo "Options:"
    echo "  -h, --help       Show this help manual"
    echo "  --no-deps        Skip package manager dependency installation"
    echo "  --deps-only      Only install system dependencies, do not install the app"
    echo "  --user           Install to user directory instead of system-wide"
    echo ""
    echo "Examples:"
    echo "  ./install.sh             # Full automated dependencies and app installation"
    echo "  ./install.sh --no-deps   # Install app directly without checking dependencies"
    echo "  ./install.sh --deps-only # Only install prerequisite distro packages"
}

NO_DEPS=false
DEPS_ONLY=false

for arg in "$@"; do
    case "$arg" in
        -h|--help)
            show_help
            exit 0
            ;;
        --no-deps)
            NO_DEPS=true
            ;;
        --deps-only)
            DEPS_ONLY=true
            ;;
    esac
done

# Distribution detection
DISTRO="unknown"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO_ID="${ID:-}"
    DISTRO_LIKE="${ID_LIKE:-}"
    
    if [[ "$DISTRO_ID" == "debian" || "$DISTRO_ID" == "ubuntu" || "$DISTRO_ID" == "parslinux" || "$DISTRO_ID" == "linuxmint" || "$DISTRO_LIKE" == *"debian"* || "$DISTRO_LIKE" == *"ubuntu"* ]]; then
        DISTRO="debian"
    elif [[ "$DISTRO_ID" == "arch" || "$DISTRO_ID" == "cachyos" || "$DISTRO_ID" == "manjaro" || "$DISTRO_ID" == "endeavouros" || "$DISTRO_LIKE" == *"arch"* ]]; then
        DISTRO="arch"
    elif [[ "$DISTRO_ID" == "fedora" || "$DISTRO_LIKE" == *"fedora"* || "$DISTRO_LIKE" == *"rhel"* ]]; then
        DISTRO="fedora"
    fi
fi

echo -e "${BLUE}ℹ Detected Distribution Family: ${BOLD}${DISTRO} (${NAME:-Unknown})${NC}"

# Root / Sudo check
SUDO=""
if [ "$EUID" -ne 0 ]; then
    if command -v sudo &>/dev/null; then
        SUDO="sudo"
    else
        echo -e "${RED}✗ Error: Root privileges required for installation and 'sudo' was not found.${NC}"
        exit 1
    fi
fi

# 1. Dependency installation
if [ "$NO_DEPS" = false ]; then
    echo -e "\n${BLUE}▶ Installing distro dependencies...${NC}"
    case "$DISTRO" in
        debian)
            $SUDO apt update
            $SUDO apt install -y python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-notify-0.7 zstd policykit-1 gettext python3-setuptools
            $SUDO apt install -y python3-apt 2>/dev/null || true
            ;;
        arch)
            $SUDO pacman -S --needed --noconfirm python python-gobject gtk4 libadwaita libnotify zstd polkit gettext python-setuptools
            ;;
        fedora)
            $SUDO dnf install -y python3 python3-gobject gtk4 libadwaita libnotify zstd polkit gettext python3-setuptools
            ;;
        *)
            echo -e "${YELLOW}⚠ Unrecognized distribution. Ensure the following packages are present:${NC}"
            echo -e "  Python 3, PyGObject, GTK 4, Libadwaita 1, Libnotify, Zstandard (zstd), Polkit, Gettext"
            ;;
    esac
    echo -e "${GREEN}✓ System dependencies ready.${NC}"
fi

if [ "$DEPS_ONLY" = true ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully.${NC}"
    exit 0
fi

# 2. Compile translations
echo -e "\n${BLUE}▶ Compiling translation files (.mo)...${NC}"
if [ -f "./update-translations.sh" ]; then
    bash ./update-translations.sh 2>/dev/null || true
fi

# 3. Install via setup.py
echo -e "\n${BLUE}▶ Installing application to /usr...${NC}"
$SUDO python3 setup.py install --root=/ --prefix=/usr --optimize=1

# 4. Configure Polkit policy
POLICY_FILE="/usr/share/polkit-1/actions/org.parslinux.pkexec.parslinux-package-installer.policy"
if [ -f "$POLICY_FILE" ]; then
    echo -e "${BLUE}▶ Setting PolicyKit permissions (0644 root:root)...${NC}"
    $SUDO chmod 0644 "$POLICY_FILE"
    $SUDO chown root:root "$POLICY_FILE" 2>/dev/null || true
fi

# 5. Update Desktop and MIME databases
echo -e "${BLUE}▶ Updating desktop and MIME caches...${NC}"
if command -v update-desktop-database &>/dev/null; then
    $SUDO update-desktop-database /usr/share/applications 2>/dev/null || true
fi
if command -v update-mime-database &>/dev/null; then
    $SUDO update-mime-database /usr/share/mime 2>/dev/null || true
fi
if command -v gtk-update-icon-cache &>/dev/null; then
    $SUDO gtk-update-icon-cache -q /usr/share/icons/hicolor 2>/dev/null || true
fi

# 6. Verification
echo -e "\n${BLUE}▶ Verifying installation...${NC}"
if command -v parslinux-package-installer &>/dev/null; then
    INSTALLED_PATH=$(which parslinux-package-installer)
    echo -e "${GREEN}✓ Success! Executable located at:${NC} $INSTALLED_PATH"
    parslinux-package-installer --version 2>/dev/null || true
    echo -e "\n${GREEN}${BOLD}🎉 Installation completed successfully!${NC}"
    echo -e "You can launch the app from your application menu or via ${BOLD}parslinux-package-installer${NC} in terminal."
else
    echo -e "${YELLOW}⚠ Warning: Executable not found in PATH immediately. Check your environment settings.${NC}"
fi
