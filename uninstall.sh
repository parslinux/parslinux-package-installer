#!/usr/bin/env bash
# ==============================================================================
# Pars Linux Package Installer - System Uninstallation Script
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

echo -e "${CYAN}${BOLD}=== Pars Linux Package Installer — Uninstaller ===${NC}"

show_help() {
    echo -e "Usage: ${BOLD}./uninstall.sh [OPTIONS]${NC}"
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help manual"
    echo "  -y, --yes     Proceed without interactive confirmation prompt"
    echo "  --force       Force removal of all remnants even if errors occur"
}

CONFIRM=true
for arg in "$@"; do
    case "$arg" in
        -h|--help)
            show_help
            exit 0
            ;;
        -y|--yes)
            CONFIRM=false
            ;;
    esac
done

if [ "$CONFIRM" = true ]; then
    echo -e "${YELLOW}Pars Linux Package Installer will be removed completely from your system.${NC}"
    read -rp "Do you wish to proceed? [y/N]: " response
    case "$response" in
        [yY][eE][sS]|[yY]|[eE][vV][eE][tT]|[eE])
            ;;
        *)
            echo -e "${BLUE}Operation cancelled by user.${NC}"
            exit 0
            ;;
    esac
fi

# Root / Sudo check
SUDO=""
if [ "$EUID" -ne 0 ]; then
    if command -v sudo &>/dev/null; then
        SUDO="sudo"
    else
        echo -e "${RED}✗ Error: Root privileges required for uninstallation and 'sudo' was not found.${NC}"
        exit 1
    fi
fi

# 1. Stop any running processes first
if [ -f "./stop.sh" ]; then
    bash ./stop.sh 2>/dev/null || true
fi

# 2. Check package manager installations
if command -v dpkg &>/dev/null; then
    if dpkg -s parslinux-package-installer &>/dev/null; then
        echo -e "${BLUE}▶ Detected APT/dpkg installation, removing...${NC}"
        $SUDO apt-get remove --purge -y parslinux-package-installer || true
    fi
fi

if command -v pacman &>/dev/null; then
    if pacman -Qi parslinux-package-installer &>/dev/null; then
        echo -e "${BLUE}▶ Detected Pacman installation, removing...${NC}"
        $SUDO pacman -Rns --noconfirm parslinux-package-installer || true
    fi
fi

# 3. Clean up manual setup.py files
echo -e "${BLUE}▶ Cleaning system directories and application files...${NC}"

FILES_TO_REMOVE=(
    "/usr/bin/parslinux-package-installer"
    "/usr/bin/parslinux-package-installer-adw"
    "/usr/bin/pardus-package-installer"
    "/usr/share/applications/org.parslinux.package-installer.desktop"
    "/usr/share/metainfo/org.parslinux.package-installer.metainfo.xml"
    "/usr/share/polkit-1/actions/org.parslinux.pkexec.parslinux-package-installer.policy"
    "/usr/share/icons/hicolor/scalable/apps/parslinux-package-installer.svg"
)

for file in "${FILES_TO_REMOVE[@]}"; do
    if [ -f "$file" ]; then
        echo "  Removing: $file"
        $SUDO rm -f "$file"
    fi
done

if [ -d "/usr/share/parslinux/parslinux-package-installer" ]; then
    echo "  Removing: /usr/share/parslinux/parslinux-package-installer"
    $SUDO rm -rf "/usr/share/parslinux/parslinux-package-installer"
fi

if [ -d "/usr/share/parslinux" ] && [ -z "$(ls -A /usr/share/parslinux 2>/dev/null)" ]; then
    $SUDO rmdir "/usr/share/parslinux" 2>/dev/null || true
fi

$SUDO find /usr/local/lib/python* /usr/lib/python* -name "*Pars_Linux_Package_Installer*" -exec rm -rf {} + 2>/dev/null || true
$SUDO find /usr/local/lib/python* /usr/lib/python* -name "*parslinux_package_installer*" -exec rm -rf {} + 2>/dev/null || true
$SUDO rm -f /usr/share/locale/*/LC_MESSAGES/parslinux-package-installer.mo 2>/dev/null || true

# 4. Refresh Desktop and MIME caches
echo -e "${BLUE}▶ Refreshing desktop and MIME caches...${NC}"
if command -v update-desktop-database &>/dev/null; then
    $SUDO update-desktop-database /usr/share/applications 2>/dev/null || true
fi
if command -v update-mime-database &>/dev/null; then
    $SUDO update-mime-database /usr/share/mime 2>/dev/null || true
fi
if command -v gtk-update-icon-cache &>/dev/null; then
    $SUDO gtk-update-icon-cache -q /usr/share/icons/hicolor 2>/dev/null || true
fi

# 5. Verification
if ! command -v parslinux-package-installer &>/dev/null; then
    echo -e "\n${GREEN}${BOLD}✓ Pars Linux Package Installer removed successfully from system.${NC}"
else
    REMAINING_BIN=$(which parslinux-package-installer)
    echo -e "\n${YELLOW}⚠ A binary was still found at: $REMAINING_BIN${NC}"
fi
