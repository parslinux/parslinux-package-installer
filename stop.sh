#!/usr/bin/env bash
# ==============================================================================
# Pars Linux Package Installer - Stop Script
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

echo -e "${CYAN}${BOLD}=== Pars Linux Package Installer — Process Terminator ===${NC}"

PATTERNS=(
    "parslinux-package-installer"
    "parslinux-package-installer-adw"
    "pardus-package-installer"
    "src/Main.py"
    "src/MainAdw.py"
    "src/Actions.py"
)

FOUND_PIDS=()

for pattern in "${PATTERNS[@]}"; do
    PIDS=$(pgrep -f "$pattern" 2>/dev/null || true)
    for pid in $PIDS; do
        if [[ "$pid" != "$$" && "$pid" != "$PPID" ]]; then
            FOUND_PIDS+=("$pid")
        fi
    done
done

UNIQUE_PIDS=($(printf "%s\n" "${FOUND_PIDS[@]}" | sort -u))

if [ ${#UNIQUE_PIDS[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ No running Pars Linux Package Installer processes found.${NC}"
    exit 0
fi

echo -e "${YELLOW}⚠ Found ${#UNIQUE_PIDS[@]} running process(es): ${UNIQUE_PIDS[*]}${NC}"
echo -e "${BLUE}▶ Terminating processes gracefully (SIGTERM)...${NC}"

for pid in "${UNIQUE_PIDS[@]}"; do
    kill -15 "$pid" 2>/dev/null || true
done

sleep 2

REMAINING=()
for pid in "${UNIQUE_PIDS[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then
        REMAINING+=("$pid")
    fi
done

if [ ${#REMAINING[@]} -gt 0 ]; then
    echo -e "${RED}⚠ Force killing lingering processes (SIGKILL): ${REMAINING[*]}${NC}"
    for pid in "${REMAINING[@]}"; do
        kill -9 "$pid" 2>/dev/null || true
    done
fi

echo -e "${GREEN}✓ All processes stopped successfully.${NC}"
