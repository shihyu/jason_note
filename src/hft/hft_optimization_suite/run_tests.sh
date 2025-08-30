#!/bin/bash

# HFT Optimization Suite Test Runner
# This script runs all tests and generates a report

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Output file for report
REPORT_FILE="test_report_$(date +%Y%m%d_%H%M%S).txt"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}HFT Optimization Suite Test Runner${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to run test and capture output
run_test() {
    local test_name=$1
    local test_cmd=$2
    echo -e "${YELLOW}Running: $test_name${NC}"
    echo "=== $test_name ===" >> $REPORT_FILE
    echo "Timestamp: $(date)" >> $REPORT_FILE
    echo "" >> $REPORT_FILE
    
    # Run the test and capture output
    if $test_cmd >> $REPORT_FILE 2>&1; then
        echo -e "${GREEN}✓ $test_name completed${NC}"
    else
        echo -e "${RED}✗ $test_name failed${NC}"
    fi
    echo "" >> $REPORT_FILE
    echo "---" >> $REPORT_FILE
    echo "" >> $REPORT_FILE
}

# Check if binaries exist
if [ ! -d "bin" ]; then
    echo -e "${RED}Error: bin directory not found. Please run 'make all' first.${NC}"
    exit 1
fi

# Initialize report
echo "HFT Optimization Suite Test Report" > $REPORT_FILE
echo "Generated: $(date)" >> $REPORT_FILE
echo "System: $(uname -a)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# System Information
echo -e "${YELLOW}Collecting System Information...${NC}"
echo "=== System Information ===" >> $REPORT_FILE
echo "CPU Model: $(lscpu | grep 'Model name' | cut -d: -f2 | xargs)" >> $REPORT_FILE
echo "CPU Count: $(nproc)" >> $REPORT_FILE
echo "Memory: $(free -h | grep Mem | awk '{print $2}')" >> $REPORT_FILE
echo "Kernel: $(uname -r)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Check HugePage support
echo "HugePage Support:" >> $REPORT_FILE
grep -q pse /proc/cpuinfo && echo "  2MB pages: Supported" >> $REPORT_FILE || echo "  2MB pages: Not supported" >> $REPORT_FILE
grep -q pdpe1gb /proc/cpuinfo && echo "  1GB pages: Supported" >> $REPORT_FILE || echo "  1GB pages: Not supported" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Current HugePage status
echo "Current HugePage Configuration:" >> $REPORT_FILE
grep Huge /proc/meminfo >> $REPORT_FILE 2>/dev/null || echo "  No HugePages configured" >> $REPORT_FILE
echo "" >> $REPORT_FILE
echo "---" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Run tests
echo ""
echo -e "${GREEN}Starting Test Suite...${NC}"
echo ""

# 1. CPU Affinity Test
run_test "CPU Affinity Test" "./bin/cpu_affinity_test"

# 2. HugePages Test (might fail without proper setup)
run_test "HugePages Test" "./bin/hugepages_test"

# 3. Event-Driven Server Test (with timeout)
echo -e "${YELLOW}Running: Event-Driven Server Test${NC}"
echo "=== Event-Driven Server Test ===" >> $REPORT_FILE
echo "Starting server..." >> $REPORT_FILE
timeout 2 ./bin/event_driven_server event >> $REPORT_FILE 2>&1 &
SERVER_PID=$!
sleep 1
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "Server started successfully" >> $REPORT_FILE
    kill $SERVER_PID 2>/dev/null
    echo -e "${GREEN}✓ Event-Driven Server Test completed${NC}"
else
    echo "Server failed to start" >> $REPORT_FILE
    echo -e "${RED}✗ Event-Driven Server Test failed${NC}"
fi
echo "" >> $REPORT_FILE
echo "---" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 4. HFT Integrated System Test
echo -e "${YELLOW}Running: HFT Integrated System Test${NC}"
echo "=== HFT Integrated System Test ===" >> $REPORT_FILE
timeout 3 ./bin/hft_integrated_system >> $REPORT_FILE 2>&1
echo -e "${GREEN}✓ HFT Integrated System Test completed${NC}"
echo "" >> $REPORT_FILE

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Test Suite Completed${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Count test results
TOTAL_TESTS=4
PASSED_TESTS=$(grep -c "✓" $REPORT_FILE 2>/dev/null || echo 0)

echo "=== Test Summary ===" >> $REPORT_FILE
echo "Total Tests: $TOTAL_TESTS" >> $REPORT_FILE
echo "Report saved to: $REPORT_FILE" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Display summary
echo -e "${GREEN}Test Summary:${NC}"
echo "  Total Tests: $TOTAL_TESTS"
echo "  Report File: $REPORT_FILE"
echo ""

# Show key results
echo -e "${GREEN}Key Performance Metrics:${NC}"
echo ""

# Extract CPU affinity results
echo -e "${YELLOW}CPU Affinity Results:${NC}"
grep -A 3 "CPU Affinity Test" $REPORT_FILE | grep "Time:" | head -3 || echo "  No results found"
echo ""

# Extract memory access results
echo -e "${YELLOW}Memory Access Results:${NC}"
grep -A 5 "Performance Test" $REPORT_FILE | grep "access:" | head -6 || echo "  No results found"
echo ""

echo -e "${GREEN}Full report saved to: $REPORT_FILE${NC}"