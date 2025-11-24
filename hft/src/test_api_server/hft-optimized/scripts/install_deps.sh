#!/bin/bash
#
# Install HFT Dependencies
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "   Installing HFT Dependencies"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
    exit 1
fi

# Update package list
echo "Updating package list..."
apt-get update -qq

# Install build essentials
echo -n "Installing build-essential... "
apt-get install -y build-essential > /dev/null 2>&1
echo -e "${GREEN}✓${NC}"

# Install libcurl
echo -n "Installing libcurl4-openssl-dev... "
apt-get install -y libcurl4-openssl-dev > /dev/null 2>&1
echo -e "${GREEN}✓${NC}"

# Install NUMA libraries
echo -n "Installing libnuma-dev... "
apt-get install -y libnuma-dev > /dev/null 2>&1
echo -e "${GREEN}✓${NC}"

# Install numactl
echo -n "Installing numactl... "
apt-get install -y numactl > /dev/null 2>&1
echo -e "${GREEN}✓${NC}"

# Install cpufrequtils
echo -n "Installing cpufrequtils... "
apt-get install -y cpufrequtils > /dev/null 2>&1
echo -e "${GREEN}✓${NC}"

# Install bc (for calculations in scripts)
echo -n "Installing bc... "
apt-get install -y bc > /dev/null 2>&1
echo -e "${GREEN}✓${NC}"

echo ""
echo -e "${GREEN}All dependencies installed successfully!${NC}"
echo ""
echo "You can now build the HFT-optimized clients."