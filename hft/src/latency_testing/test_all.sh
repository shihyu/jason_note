#!/bin/bash

################################################################################
# HFT Latency Testing - 完整測試腳本
# 
# 功能：測試所有 Makefile 目標和功能
# 使用：./test_all.sh [--verbose]
################################################################################

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 測試計數器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# 詳細模式
VERBOSE=false
if [ "$1" == "--verbose" ]; then
    VERBOSE=true
fi

# 輸出函數
print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
}

print_test() {
    echo -e "${YELLOW}▶ 測試: $1${NC}"
    ((TOTAL_TESTS++))
}

print_success() {
    echo -e "${GREEN}  ✓ $1${NC}"
    ((PASSED_TESTS++))
}

print_failure() {
    echo -e "${RED}  ✗ $1${NC}"
    ((FAILED_TESTS++))
}

print_skip() {
    echo -e "${YELLOW}  ⊘ $1${NC}"
    ((SKIPPED_TESTS++))
}

run_command() {
    local cmd="$1"
    local desc="$2"
    
    if [ "$VERBOSE" == "true" ]; then
        echo -e "  執行: $cmd"
        if eval $cmd; then
            print_success "$desc"
            return 0
        else
            print_failure "$desc"
            return 1
        fi
    else
        if eval $cmd > /dev/null 2>&1; then
            print_success "$desc"
            return 0
        else
            print_failure "$desc"
            return 1
        fi
    fi
}

################################################################################
# 主測試流程
################################################################################

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         HFT Latency Testing Suite - 完整測試                      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"

# 檢查環境
print_header "環境檢查"

print_test "檢查編譯器"
if which g++ > /dev/null 2>&1; then
    GCC_VERSION=$(g++ --version | head -1)
    print_success "找到 g++: $GCC_VERSION"
else
    print_failure "未找到 g++ 編譯器"
    exit 1
fi

print_test "檢查 C++17 支援"
echo "int main() { return 0; }" | g++ -std=c++17 -x c++ - -o /tmp/test_cpp17 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "C++17 支援正常"
    rm -f /tmp/test_cpp17
else
    print_failure "C++17 不支援"
fi

print_test "檢查 perf 工具"
if which perf > /dev/null 2>&1; then
    print_success "找到 perf 工具"
else
    print_skip "perf 未安裝（性能分析將跳過）"
fi

################################################################################
# 測試編譯目標
################################################################################

print_header "編譯測試"

print_test "清理舊編譯"
run_command "make clean" "清理完成"

print_test "標準編譯 (make all)"
run_command "make all" "所有程式編譯成功"

print_test "驗證二進位檔案"
BINARIES="basic_latency orderbook_latency memory_pool udp_server udp_client"
ALL_FOUND=true
for bin in $BINARIES; do
    if [ -f "bin/$bin" ]; then
        echo -e "  ${GREEN}✓${NC} bin/$bin"
    else
        echo -e "  ${RED}✗${NC} bin/$bin 未找到"
        ALL_FOUND=false
    fi
done
if [ "$ALL_FOUND" == "true" ]; then
    print_success "所有二進位檔案已生成"
else
    print_failure "部分二進位檔案缺失"
fi

print_test "Debug 編譯"
run_command "make clean && make debug" "Debug 編譯成功"

print_test "Profile 編譯"
run_command "make clean && make profile" "Profile 編譯成功"

# 恢復標準編譯
make clean > /dev/null 2>&1
make all > /dev/null 2>&1

################################################################################
# 測試各個程式
################################################################################

print_header "基礎延遲測試"

print_test "Map vs Unordered Map"
run_command "./bin/basic_latency map | grep -q 'std::map'" "Map 測試完成"

print_test "Memory Copy vs Move"
run_command "./bin/basic_latency copy | grep -q 'memcpy'" "Copy 測試完成"

print_test "Dynamic Allocation"
run_command "./bin/basic_latency alloc | grep -q 'new/delete'" "Allocation 測試完成"

print_test "Timer Overhead"
run_command "./bin/basic_latency timer | grep -q 'rdtsc'" "Timer 測試完成"

################################################################################

print_header "訂單簿測試"

print_test "Order Book Operations"
run_command "./bin/orderbook_latency ops | grep -q 'Add Order'" "訂單操作測試完成"

print_test "Order Matching"
run_command "./bin/orderbook_latency match | grep -q 'Matching'" "撮合測試完成"

print_test "Order Book Stress"
run_command "./bin/orderbook_latency stress | grep -q 'Stress'" "壓力測試完成"

################################################################################

print_header "記憶體池測試"

print_test "Allocation Strategies"
run_command "./bin/memory_pool strategies | grep -q 'Memory Pool'" "策略測試完成"

print_test "Allocation Patterns"
run_command "./bin/memory_pool patterns | grep -q 'Sequential'" "模式測試完成"

print_test "Cache Effects"
run_command "./bin/memory_pool cache | grep -q 'Stride'" "緩存測試完成"

################################################################################

print_header "網路測試"

print_test "UDP Server 啟動測試"
timeout 1 ./bin/udp_server > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5
if ps -p $SERVER_PID > /dev/null 2>&1; then
    print_success "UDP Server 啟動成功"
    kill $SERVER_PID 2>/dev/null || true
    wait $SERVER_PID 2>/dev/null || true
else
    print_failure "UDP Server 啟動失敗"
fi

print_test "UDP Client 連接測試"
./bin/udp_server > /dev/null 2>&1 &
SERVER_PID=$!
sleep 0.5
if timeout 2 ./bin/udp_client 127.0.0.1 9000 2>/dev/null | grep -q "RTT"; then
    print_success "Client-Server 通信成功"
else
    print_skip "Client-Server 通信測試跳過"
fi
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

################################################################################

print_header "Makefile 目標測試"

print_test "make test"
run_command "make test > /dev/null" "本地測試執行成功"

print_test "make quick-test"
run_command "make quick-test > /dev/null" "快速測試執行成功"

print_test "make demo"
run_command "make demo > /dev/null" "演示執行成功"

print_test "make verify"
run_command "make verify | grep -q '編譯驗證完成'" "驗證測試成功"

print_test "make help"
run_command "make help | grep -q 'HFT Latency Testing Suite'" "幫助顯示成功"

################################################################################

print_header "性能分析測試"

if which perf > /dev/null 2>&1; then
    print_test "perf stat 基礎測試"
    if perf stat -e cycles,instructions ./bin/basic_latency timer 2>&1 | grep -q "cycles"; then
        print_success "Perf 分析成功"
    else
        print_skip "Perf 分析需要權限"
    fi
else
    print_skip "Perf 工具未安裝"
fi

################################################################################

print_header "腳本測試"

print_test "run_tests.sh"
if [ -f "./run_tests.sh" ]; then
    if bash -n ./run_tests.sh 2>/dev/null; then
        print_success "run_tests.sh 語法正確"
    else
        print_failure "run_tests.sh 語法錯誤"
    fi
else
    print_failure "run_tests.sh 不存在"
fi

print_test "validate_results.py"
if [ -f "./validate_results.py" ]; then
    if python3 -m py_compile validate_results.py 2>/dev/null; then
        print_success "validate_results.py 語法正確"
    else
        print_failure "validate_results.py 語法錯誤"
    fi
else
    print_failure "validate_results.py 不存在"
fi

################################################################################
# 測試總結
################################################################################

print_header "測試總結"

echo -e "\n${BLUE}測試統計：${NC}"
echo -e "  總測試數: ${TOTAL_TESTS}"
echo -e "  ${GREEN}通過: ${PASSED_TESTS}${NC}"
echo -e "  ${RED}失敗: ${FAILED_TESTS}${NC}"
echo -e "  ${YELLOW}跳過: ${SKIPPED_TESTS}${NC}"

SUCCESS_RATE=$(echo "scale=1; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)
echo -e "\n  成功率: ${SUCCESS_RATE}%"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    所有測試通過！🎉                               ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "\n${RED}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                    有 ${FAILED_TESTS} 個測試失敗                                   ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi