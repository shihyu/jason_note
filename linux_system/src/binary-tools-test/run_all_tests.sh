#!/bin/bash

# Master test script for Linux Binary Tools Guide

echo "=========================================="
echo "Linux Binary Tools - Complete Test Suite"
echo "=========================================="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

run_test() {
    local test_name="$1"
    local test_script="$2"

    echo -e "${GREEN}[TEST]${NC} $test_name"
    if [ -f "$test_script" ]; then
        bash "$test_script" > /tmp/test_output_$$.log 2>&1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[PASS]${NC} $test_name completed successfully"
        else
            echo -e "${RED}[FAIL]${NC} $test_name had errors (check /tmp/test_output_$$.log)"
        fi
    else
        echo -e "${RED}[SKIP]${NC} $test_script not found"
    fi
    echo
}

# Run all tests
echo "Starting test suite..."
echo

# 1. Core tools
cd core-tools
run_test "Core Binary Analysis Tools" "test_core_tools.sh"
cd ..

# 2. Static libraries
cd static-lib
run_test "Static Library Creation and Usage" "test_static_lib.sh"
cd ..

# 3. Dynamic libraries
cd dynamic-lib
run_test "Dynamic Library Creation and Features" "test_dynamic_lib.sh"
cd ..

# 4. dlopen and plugins
cd dlopen-demo
run_test "dlopen and Plugin System" "test_dlopen.sh"
cd ..

# 5. LD tools and environment
run_test "LD Environment Variables and Tools" "test_ld_tools.sh"

# 6. Debug tools
run_test "Debugging and Tracing Tools" "test_debug_tools.sh"

echo "=========================================="
echo "Test Suite Complete!"
echo "See TEST_REPORT.md for detailed results"
echo "=========================================="

# Check for missing tools and provide recommendations
echo
echo "Tool Availability Check:"
echo "------------------------"

check_tool() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 - installed"
    else
        echo -e "${RED}✗${NC} $1 - not installed (install with: $2)"
    fi
}

check_tool "nm" "binutils"
check_tool "objdump" "binutils"
check_tool "readelf" "binutils"
check_tool "ldd" "libc-bin"
check_tool "strace" "sudo apt-get install strace"
check_tool "ltrace" "sudo apt-get install ltrace"
check_tool "valgrind" "sudo apt-get install valgrind"
check_tool "perf" "sudo apt-get install linux-tools-common"
check_tool "gdb" "sudo apt-get install gdb"

echo
echo "For comprehensive testing, consider installing missing tools."