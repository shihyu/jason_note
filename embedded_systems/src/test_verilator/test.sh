#!/bin/bash

# test.sh - Verilator 自動化測試腳本

echo "======================================"
echo "     Verilator Test Suite"
echo "======================================"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 設定環境變數
export PATH=$HOME/.mybin/verilator/bin:$PATH
export VERILATOR_ROOT=$HOME/.mybin/verilator/share/verilator

# 測試函數
test_command() {
    local cmd=$1
    local desc=$2
    echo -n "Testing: $desc... "
    if $cmd > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# 0. 清理環境
echo -e "${YELLOW}[0/5] Cleaning environment${NC}"
make clean

# 1. 檢查 Verilator 安裝
echo -e "${YELLOW}[1/5] Checking Verilator installation${NC}"
if ! command -v verilator &> /dev/null; then
    echo -e "${RED}Verilator not found in PATH${NC}"
    exit 1
fi
echo "Verilator version: $(verilator --version)"
echo "Verilator path: $(which verilator)"

# 2. 檢查環境變數
echo -e "${YELLOW}[2/5] Checking environment variables${NC}"
echo "VERILATOR_ROOT: $VERILATOR_ROOT"
echo "PATH includes: $HOME/.mybin/verilator/bin"

# 3. 編譯測試
echo -e "${YELLOW}[3/5] Compilation test${NC}"
test_command "make verilate" "Verilator compilation"

# 4. 模擬測試
echo -e "${YELLOW}[4/5] Simulation test${NC}"
test_command "make run" "Running simulation"

# 5. 檢查輸出檔案
echo -e "${YELLOW}[5/5] Checking output files${NC}"
if [ -f "counter.vcd" ]; then
    echo -e "${GREEN}✓ VCD file generated${NC}"
    ls -lh counter.vcd
else
    echo -e "${RED}✗ VCD file not found${NC}"
fi

# 檢查 GTKWave（可選）
echo ""
echo "Optional tools:"
if command -v gtkwave &> /dev/null; then
    echo -e "${GREEN}✓ GTKWave installed${NC}"
    echo "  Run 'make wave' to view waveform"
else
    echo -e "${YELLOW}⚠ GTKWave not installed${NC}"
    echo "  Install with: sudo apt-get install gtkwave"
fi

echo ""
echo "======================================"
echo -e "${GREEN}All tests completed!${NC}"
echo "======================================"
echo ""
echo "Quick commands:"
echo "  make       - Compile and run simulation"
echo "  make wave  - View waveform (requires GTKWave)"
echo "  make clean - Clean generated files"
echo "  make help  - Show help"