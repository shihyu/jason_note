#!/bin/bash
#
# HFT System Optimization Setup Script
#
# This script configures Ubuntu system for low-latency HFT workloads
#
# Usage:
#   sudo ./setup_hft_system.sh [OPTIONS]
#
# Options:
#   --check-only    Only check current settings without making changes
#   --permanent     Make changes permanent (requires reboot for some settings)
#   --temporary     Make temporary changes (until next reboot)
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ] && [ "$1" != "--check-only" ]; then
    echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
    exit 1
fi

echo "=========================================="
echo "   HFT System Optimization Setup"
echo "=========================================="
echo ""

# Parse arguments
CHECK_ONLY=0
PERMANENT=0
TEMPORARY=0

for arg in "$@"; do
    case $arg in
        --check-only)
            CHECK_ONLY=1
            ;;
        --permanent)
            PERMANENT=1
            ;;
        --temporary)
            TEMPORARY=1
            ;;
        *)
            echo "Unknown option: $arg"
            exit 1
            ;;
    esac
done

# Default to temporary if neither specified
if [ $PERMANENT -eq 0 ] && [ $TEMPORARY -eq 0 ]; then
    TEMPORARY=1
fi

# Function to check current settings
check_settings() {
    echo "=== Current System Settings ==="
    echo ""

    # CPU Governor
    echo "1. CPU Governor:"
    GOVERNOR=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo "unknown")
    if [ "$GOVERNOR" = "performance" ]; then
        echo -e "   ${GREEN}✓${NC} Performance mode: $GOVERNOR"
    else
        echo -e "   ${YELLOW}⚠${NC} Current mode: $GOVERNOR (should be 'performance')"
    fi

    # Transparent Huge Pages
    echo ""
    echo "2. Transparent Huge Pages (THP):"
    THP_ENABLED=$(cat /sys/kernel/mm/transparent_hugepage/enabled)
    if echo "$THP_ENABLED" | grep -q "\[never\]"; then
        echo -e "   ${GREEN}✓${NC} THP disabled: $THP_ENABLED"
    else
        echo -e "   ${YELLOW}⚠${NC} THP status: $THP_ENABLED (should be 'never')"
    fi

    # HugePages
    echo ""
    echo "3. HugePages:"
    HUGEPAGES_TOTAL=$(grep HugePages_Total /proc/meminfo | awk '{print $2}')
    HUGEPAGES_FREE=$(grep HugePages_Free /proc/meminfo | awk '{print $2}')
    if [ "$HUGEPAGES_TOTAL" -gt 0 ]; then
        echo -e "   ${GREEN}✓${NC} HugePages allocated: $HUGEPAGES_TOTAL (Free: $HUGEPAGES_FREE)"
    else
        echo -e "   ${YELLOW}⚠${NC} No HugePages allocated (recommended: 512+)"
    fi

    # isolcpus
    echo ""
    echo "4. CPU Isolation (isolcpus):"
    if grep -q "isolcpus" /proc/cmdline; then
        ISOLCPUS=$(cat /proc/cmdline | grep -o 'isolcpus=[^ ]*')
        echo -e "   ${GREEN}✓${NC} CPU isolation enabled: $ISOLCPUS"
    else
        echo -e "   ${YELLOW}⚠${NC} CPU isolation not configured"
    fi

    # nohz_full
    echo ""
    echo "5. Tickless Mode (nohz_full):"
    if grep -q "nohz_full" /proc/cmdline; then
        NOHZ=$(cat /proc/cmdline | grep -o 'nohz_full=[^ ]*')
        echo -e "   ${GREEN}✓${NC} Tickless mode enabled: $NOHZ"
    else
        echo -e "   ${YELLOW}⚠${NC} Tickless mode not configured"
    fi

    # File descriptor limits
    echo ""
    echo "6. File Descriptor Limits:"
    ULIMIT_N=$(ulimit -n)
    if [ "$ULIMIT_N" -ge 65536 ]; then
        echo -e "   ${GREEN}✓${NC} Limit: $ULIMIT_N"
    else
        echo -e "   ${YELLOW}⚠${NC} Current: $ULIMIT_N (recommended: 65536+)"
    fi

    # Memory lock limit
    echo ""
    echo "7. Memory Lock Limit:"
    ULIMIT_L=$(ulimit -l)
    if [ "$ULIMIT_L" = "unlimited" ] || [ "$ULIMIT_L" -gt 8000000 ]; then
        echo -e "   ${GREEN}✓${NC} Limit: $ULIMIT_L KB"
    else
        echo -e "   ${YELLOW}⚠${NC} Current: $ULIMIT_L KB (recommended: unlimited)"
    fi

    # NUMA
    echo ""
    echo "8. NUMA Configuration:"
    if command -v numactl &> /dev/null; then
        NUMA_NODES=$(numactl --hardware | grep "available:" | awk '{print $2}')
        echo -e "   ${GREEN}✓${NC} numactl available: $NUMA_NODES node(s)"
    else
        echo -e "   ${YELLOW}⚠${NC} numactl not installed"
    fi

    # Swappiness
    echo ""
    echo "9. Swappiness:"
    SWAPPINESS=$(cat /proc/sys/vm/swappiness)
    if [ "$SWAPPINESS" -le 10 ]; then
        echo -e "   ${GREEN}✓${NC} Swappiness: $SWAPPINESS"
    else
        echo -e "   ${YELLOW}⚠${NC} Swappiness: $SWAPPINESS (recommended: 10 or lower)"
    fi

    echo ""
    echo "=========================================="
}

# Apply temporary optimizations
apply_temporary() {
    echo "=== Applying Temporary Optimizations ==="
    echo ""

    # 1. CPU Governor to performance
    echo "1. Setting CPU governor to 'performance'..."
    for gov_file in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo "performance" > "$gov_file" 2>/dev/null || true
    done
    echo -e "   ${GREEN}✓${NC} CPU governor set to performance"

    # 2. Disable Transparent Huge Pages
    echo ""
    echo "2. Disabling Transparent Huge Pages..."
    echo never > /sys/kernel/mm/transparent_hugepage/enabled
    echo never > /sys/kernel/mm/transparent_hugepage/defrag
    echo -e "   ${GREEN}✓${NC} THP disabled"

    # 3. Allocate HugePages
    echo ""
    echo "3. Allocating HugePages (512 x 2MB = 1GB)..."
    echo 512 > /proc/sys/vm/nr_hugepages
    ACTUAL_HUGEPAGES=$(cat /proc/sys/vm/nr_hugepages)
    echo -e "   ${GREEN}✓${NC} HugePages allocated: $ACTUAL_HUGEPAGES"

    # 4. Set swappiness to 1
    echo ""
    echo "4. Setting swappiness to 1..."
    echo 1 > /proc/sys/vm/swappiness
    echo -e "   ${GREEN}✓${NC} Swappiness set to 1"

    # 5. Disable swap (optional)
    echo ""
    echo "5. Disabling swap..."
    swapoff -a 2>/dev/null || echo "   (No swap to disable)"
    echo -e "   ${GREEN}✓${NC} Swap disabled"

    echo ""
    echo -e "${GREEN}Temporary optimizations applied successfully!${NC}"
    echo -e "${YELLOW}Note: These changes will be lost after reboot${NC}"
}

# Apply permanent optimizations
apply_permanent() {
    echo "=== Applying Permanent Optimizations ==="
    echo ""

    # Apply temporary first
    apply_temporary

    echo ""
    echo "6. Making changes permanent..."

    # Add to sysctl.conf
    echo ""
    echo "   Updating /etc/sysctl.conf..."

    if ! grep -q "vm.nr_hugepages" /etc/sysctl.conf; then
        echo "vm.nr_hugepages = 512" >> /etc/sysctl.conf
    fi

    if ! grep -q "vm.swappiness" /etc/sysctl.conf; then
        echo "vm.swappiness = 1" >> /etc/sysctl.conf
    fi

    # Update limits.conf
    echo "   Updating /etc/security/limits.conf..."
    if ! grep -q "nofile 65536" /etc/security/limits.conf; then
        echo "* soft nofile 65536" >> /etc/security/limits.conf
        echo "* hard nofile 65536" >> /etc/security/limits.conf
    fi

    if ! grep -q "memlock unlimited" /etc/security/limits.conf; then
        echo "* soft memlock unlimited" >> /etc/security/limits.conf
        echo "* hard memlock unlimited" >> /etc/security/limits.conf
    fi

    # Install cpufrequtils for persistent governor
    echo "   Installing cpufrequtils..."
    apt-get install -y cpufrequtils > /dev/null 2>&1 || true
    echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils

    # Create systemd service for THP
    echo "   Creating systemd service for THP..."
    cat > /etc/systemd/system/disable-thp.service <<EOF
[Unit]
Description=Disable Transparent Huge Pages (THP)
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo never > /sys/kernel/mm/transparent_hugepage/enabled'
ExecStart=/bin/sh -c 'echo never > /sys/kernel/mm/transparent_hugepage/defrag'

[Install]
WantedBy=multi-user.target
EOF

    systemctl enable disable-thp.service > /dev/null 2>&1

    echo -e "   ${GREEN}✓${NC} Permanent settings configured"
    echo ""
    echo -e "${YELLOW}=== IMPORTANT: GRUB Configuration Required ===${NC}"
    echo ""
    echo "To enable CPU isolation and tickless mode, manually edit /etc/default/grub:"
    echo ""
    echo "1. Open the file:"
    echo "   sudo nano /etc/default/grub"
    echo ""
    echo "2. Modify GRUB_CMDLINE_LINUX_DEFAULT to add:"
    echo "   GRUB_CMDLINE_LINUX_DEFAULT=\"quiet splash isolcpus=8-27 nohz_full=8-27 rcu_nocbs=8-27 transparent_hugepage=never\""
    echo ""
    echo "3. Update GRUB:"
    echo "   sudo update-grub"
    echo ""
    echo "4. Reboot:"
    echo "   sudo reboot"
    echo ""
    echo -e "${GREEN}All other permanent optimizations applied!${NC}"
}

# Main logic
if [ $CHECK_ONLY -eq 1 ]; then
    check_settings
elif [ $TEMPORARY -eq 1 ]; then
    check_settings
    echo ""
    read -p "Apply temporary optimizations? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        apply_temporary
        echo ""
        check_settings
    fi
elif [ $PERMANENT -eq 1 ]; then
    check_settings
    echo ""
    read -p "Apply permanent optimizations? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        apply_permanent
        echo ""
        check_settings
    fi
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="