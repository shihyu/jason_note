#!/bin/bash

# HFT Latency Testing Runner Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
PASSED=0
FAILED=0
SKIPPED=0

echo -e "${GREEN}=================================================="
echo "        HFT Latency Testing Suite"
echo -e "==================================================${NC}\n"

# Check if running as root (for huge pages and CPU affinity)
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}Running as root - enabling performance optimizations${NC}"
    
    # Disable CPU frequency scaling
    echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null 2>&1 || true
    
    # Increase network buffer sizes
    sysctl -w net.core.rmem_max=134217728 > /dev/null 2>&1 || true
    sysctl -w net.core.wmem_max=134217728 > /dev/null 2>&1 || true
    
    # Enable huge pages if available
    echo 128 > /proc/sys/vm/nr_hugepages 2>/dev/null || true
else
    echo -e "${YELLOW}Not running as root - some optimizations disabled${NC}"
fi

# Function to run a test
run_test() {
    local test_name="$1"
    local test_cmd="$2"
    
    echo -e "\n${YELLOW}Running: $test_name${NC}"
    echo "----------------------------------------"
    
    if eval $test_cmd; then
        echo -e "${GREEN}✓ $test_name passed${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ $test_name failed${NC}"
        ((FAILED++))
        return 1
    fi
}

# Build all tests
echo -e "${YELLOW}Building all tests...${NC}"
make clean > /dev/null 2>&1
make all > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Build successful!${NC}\n"

# Run basic latency tests
echo -e "\n${GREEN}=== BASIC LATENCY TESTS ===${NC}"
run_test "Map vs Unordered Map" "./bin/basic_latency map"
run_test "Memory Copy vs Move" "./bin/basic_latency copy"
run_test "Dynamic Allocation" "./bin/basic_latency alloc"
run_test "Timer Overhead" "./bin/basic_latency timer"

# Run orderbook tests
echo -e "\n${GREEN}=== ORDER BOOK TESTS ===${NC}"
run_test "Order Book Operations" "./bin/orderbook_latency ops"
run_test "Order Matching" "./bin/orderbook_latency match"
run_test "Order Book Stress" "./bin/orderbook_latency stress"

# Run memory pool tests
echo -e "\n${GREEN}=== MEMORY POOL TESTS ===${NC}"
run_test "Allocation Strategies" "./bin/memory_pool strategies"
run_test "Allocation Patterns" "./bin/memory_pool patterns"
run_test "Cache Effects" "./bin/memory_pool cache"

# Network tests (optional)
echo -e "\n${GREEN}=== NETWORK TESTS ===${NC}"
if [ "$1" == "--with-network" ]; then
    # Start server
    echo -e "${YELLOW}Starting UDP server...${NC}"
    ./bin/udp_server > /tmp/udp_server.log 2>&1 &
    SERVER_PID=$!
    sleep 1
    
    # Run client
    if run_test "Network Round Trip" "timeout 30 ./bin/udp_client"; then
        :
    fi
    
    # Stop server
    echo -e "${YELLOW}Stopping UDP server...${NC}"
    kill $SERVER_PID 2>/dev/null || true
    wait $SERVER_PID 2>/dev/null || true
else
    echo -e "${YELLOW}Skipping network tests (use --with-network to enable)${NC}"
    ((SKIPPED++))
fi

# Summary
echo -e "\n${GREEN}=================================================="
echo "                 TEST SUMMARY"
echo -e "==================================================${NC}"
echo -e "Passed:  ${GREEN}$PASSED${NC}"
echo -e "Failed:  ${RED}$FAILED${NC}"
echo -e "Skipped: ${YELLOW}$SKIPPED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed!${NC}"
    exit 1
fi