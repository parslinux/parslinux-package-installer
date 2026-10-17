#!/usr/bin/env bash
# ==============================================================================
# Pars Linux Package Installer - Run Script
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

echo -e "${CYAN}${BOLD}=== Pars Linux Package Installer — Launcher ===${NC}"

show_help() {
    echo -e "Usage: ${BOLD}./run.sh [OPTIONS] [PACKAGE1 PACKAGE2 ...]${NC}"
    echo ""
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  --test            Run all automated unit and integration tests"
    echo "  --sample          Launch with a sample test package (.deb / .pkg.tar.zst)"
    echo "  --system          Run system-installed version instead of local dev source"
    echo "  -i, --info <PKG>  Headless metadata inspection in terminal"
    echo "  -c, --check <PKG> Dependency check in terminal (exit code 0/1)"
    echo "  -v, --verbose     Enable verbose debug logging"
    echo "  --adw             Force Libadwaita interface"
    echo ""
    echo "Examples:"
    echo "  ./run.sh                               # Launch blank window"
    echo "  ./run.sh app.deb                       # Inspect / install .deb package"
    echo "  ./run.sh pkg.pkg.tar.zst               # Inspect / install Arch package"
    echo "  ./run.sh --sample                      # Launch with sample package"
    echo "  ./run.sh -i /path/package.deb          # Terminal metadata dump"
    echo "  ./run.sh --test                        # Run test suite"
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# Run test suite
if [[ "$1" == "--test" ]]; then
    echo -e "${BLUE}▶ Launching test suite: tests/run_all_tests.py...${NC}"
    exec python3 tests/run_all_tests.py
fi

# Run system installed binary
if [[ "$1" == "--system" ]]; then
    shift
    if ! command -v parslinux-package-installer &>/dev/null; then
        echo -e "${RED}✗ Error: 'parslinux-package-installer' is not installed on system!${NC}"
        echo -e "Install first using ${BOLD}./install.sh${NC} or run without --system for dev mode."
        exit 1
    fi
    echo -e "${GREEN}▶ Running system installed version...${NC}"
    exec parslinux-package-installer "$@"
fi

# Run with sample package
if [[ "$1" == "--sample" ]]; then
    shift
    SAMPLE_PKG=""
    if [[ -f "scratch/parslinux-hello_1.0.0_all.deb" ]]; then
        SAMPLE_PKG="scratch/parslinux-hello_1.0.0_all.deb"
    elif [[ -f "tests/fixtures/parslinux-hello_1.0.0_all.deb" ]]; then
        SAMPLE_PKG="tests/fixtures/parslinux-hello_1.0.0_all.deb"
    elif [[ -f "tests/fixtures/parslinux-arch-hello-1.0.0-1-any.pkg.tar.zst" ]]; then
        SAMPLE_PKG="tests/fixtures/parslinux-arch-hello-1.0.0-1-any.pkg.tar.zst"
    fi

    if [[ -z "$SAMPLE_PKG" ]]; then
        echo -e "${YELLOW}⚠ Sample package not found, opening empty window.${NC}"
    else
        echo -e "${GREEN}▶ Selected sample package: ${SAMPLE_PKG}${NC}"
        set -- "$SAMPLE_PKG" "$@"
    fi
fi

# Check Python and GUI dependencies
echo -e "${BLUE}🔍 Checking environment and dependencies...${NC}"
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}✗ Error: python3 not found! Please install Python 3.${NC}"
    exit 1
fi

DEPS_CHECK=$(python3 -c "
import sys
missing = []
try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Gtk, Adw
except Exception as e:
    missing.append(f'PyGObject / GTK4 / Libadwaita ({e})')

if missing:
    print('; '.join(missing))
    sys.exit(1)
sys.exit(0)
" 2>&1) || {
    echo -e "${RED}✗ Missing GUI dependencies:${NC} $DEPS_CHECK"
    echo -e "${YELLOW}Please install the required packages:${NC}"
    echo -e "  Debian/Ubuntu/Pars: ${BOLD}sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-notify-0.7 zstd${NC}"
    echo -e "  Arch/Manjaro:       ${BOLD}sudo pacman -S python-gobject gtk4 libadwaita libnotify zstd${NC}"
    echo -e "  Or run:             ${BOLD}./install.sh${NC}"
    exit 1
}

echo -e "${GREEN}✓ Environment ready (Python 3, GTK 4, Libadwaita).${NC}"

# Launch application from local source
echo -e "${GREEN}▶ Starting application (Local source: ./parslinux-package-installer)...${NC}"
exec ./parslinux-package-installer "$@"
