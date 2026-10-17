#!/usr/bin/env bash
# ==============================================================================
# Pars Linux Package Installer - Master Management Script
# ==============================================================================
set -e

# Color definitions
RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
BLUE=$'\033[0;34m'
CYAN=$'\033[0;36m'
MAGENTA=$'\033[0;35m'
BOLD=$'\033[1m'
NC=$'\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

show_header() {
    clear 2>/dev/null || true
    echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║        Pars Linux Package Installer — Control Panel          ║${NC}"
    echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

show_cli_help() {
    echo -e "Usage: ${BOLD}./manage.sh [COMMAND] [OPTIONS]${NC}"
    echo ""
    echo "Commands:"
    echo "  ${GREEN}run${NC}       [pkg/options]  Run the application (Development / Local)"
    echo "  ${RED}stop${NC}                    Terminate all running application processes"
    echo "  ${BLUE}install${NC}   [options]      Install distro dependencies and app to system"
    echo "  ${YELLOW}uninstall${NC} [options]      Completely remove the application from system"
    echo "  ${MAGENTA}package${NC}   [options]      Build .deb or .pkg.tar.zst packages"
    echo "  ${CYAN}test${NC}                      Run full automated unit and integration tests"
    echo "  ${BOLD}menu${NC}                      Open interactive terminal menu (default)"
}

ACTION="$1"
if [ -n "$ACTION" ]; then
    shift
    case "$ACTION" in
        run|calistir)
            exec ./run.sh "$@"
            ;;
        stop|durdur|kill)
            exec ./stop.sh "$@"
            ;;
        install|yukle|kur)
            exec ./install.sh "$@"
            ;;
        uninstall|kaldir|sil)
            exec ./uninstall.sh "$@"
            ;;
        package|paketle|build)
            exec ./package.sh "$@"
            ;;
        test|tests)
            echo -e "${BLUE}▶ Running test suite...${NC}"
            exec python3 tests/run_all_tests.py "$@"
            ;;
        -h|--help|help)
            show_cli_help
            exit 0
            ;;
        menu)
            ;;
        *)
            echo -e "${RED}✗ Unknown command: '$ACTION'${NC}"
            show_cli_help
            exit 1
            ;;
    esac
fi

# Interactive Menu
while true; do
    show_header
    echo -e "Please select an action to perform:"
    echo ""
    echo -e "  ${GREEN}${BOLD}1)${NC} Launch Application (Dev Mode)"
    echo -e "  ${GREEN}${BOLD}2)${NC} Launch with Sample Package (.deb / .pkg.tar.zst)"
    echo -e "  ${RED}${BOLD}3)${NC} Stop Running Application Processes"
    echo -e "  ${BLUE}${BOLD}4)${NC} Install Dependencies and Application (System Install)"
    echo -e "  ${YELLOW}${BOLD}5)${NC} Uninstall Application from System"
    echo -e "  ${MAGENTA}${BOLD}6)${NC} Build Distribution Package (Debian .deb / Arch .pkg.tar.zst)"
    echo -e "  ${CYAN}${BOLD}7)${NC} Run Automated Test Suite (Unit & Integration)"
    echo -e "  ${BOLD}0)${NC} Exit"
    echo ""
    read -rp "Selection [0-7]: " choice

    case "$choice" in
        1)
            echo ""
            ./run.sh
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        2)
            echo ""
            ./run.sh --sample
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        3)
            echo ""
            ./stop.sh
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        4)
            echo ""
            ./install.sh
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        5)
            echo ""
            ./uninstall.sh
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        6)
            echo ""
            ./package.sh
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        7)
            echo ""
            python3 tests/run_all_tests.py
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        0|q|Q)
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid selection, please try again.${NC}"
            sleep 1
            ;;
    esac
done
