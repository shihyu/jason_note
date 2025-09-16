#!/bin/bash

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 測試計數器
TESTS_PASSED=0
TESTS_FAILED=0

# 打印標題
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# 打印測試結果
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ $2${NC}"
        ((TESTS_FAILED++))
    fi
}

# 確保程序已編譯
print_header "Building test programs"
make clean
make all

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to build test programs${NC}"
    exit 1
fi

# 測試1: 基本 addr2line 功能
print_header "Test 1: Basic addr2line functionality"

echo "Testing with segfault_demo..."
MAIN_ADDR=$(nm segfault_demo | grep " T main" | awk '{print "0x"$1}')
if [ -n "$MAIN_ADDR" ]; then
    echo "main() address: $MAIN_ADDR"
    RESULT=$(addr2line -fe segfault_demo $MAIN_ADDR 2>&1)
    echo "addr2line output: $RESULT"

    if echo "$RESULT" | grep -q "main"; then
        print_result 0 "Successfully resolved main() function"
    else
        print_result 1 "Failed to resolve main() function"
    fi

    if echo "$RESULT" | grep -q "segfault_demo.c"; then
        print_result 0 "Successfully resolved source file"
    else
        print_result 1 "Failed to resolve source file"
    fi
else
    print_result 1 "Could not find main() address"
fi

# 測試2: 多個地址解析
print_header "Test 2: Multiple address resolution"

echo "Getting multiple function addresses..."
FUNC_A=$(nm segfault_demo | grep " T function_a" | awk '{print "0x"$1}')
FUNC_B=$(nm segfault_demo | grep " T function_b" | awk '{print "0x"$1}')
FUNC_C=$(nm segfault_demo | grep " T function_c" | awk '{print "0x"$1}')

if [ -n "$FUNC_A" ] && [ -n "$FUNC_B" ] && [ -n "$FUNC_C" ]; then
    echo "Addresses: $FUNC_A $FUNC_B $FUNC_C"
    RESULT=$(addr2line -fe segfault_demo $FUNC_A $FUNC_B $FUNC_C 2>&1)
    echo "$RESULT"

    if echo "$RESULT" | grep -q "function_a" && \
       echo "$RESULT" | grep -q "function_b" && \
       echo "$RESULT" | grep -q "function_c"; then
        print_result 0 "Successfully resolved multiple functions"
    else
        print_result 1 "Failed to resolve all functions"
    fi
else
    print_result 1 "Could not find all function addresses"
fi

# 測試3: C++ 符號 demangling
print_header "Test 3: C++ symbol demangling"

echo "Testing C++ demangling..."
CPP_ADDR=$(nm cpp_demo | grep "Container.*process" | head -1 | awk '{print "0x"$1}')

if [ -n "$CPP_ADDR" ]; then
    echo "C++ symbol address: $CPP_ADDR"

    # 沒有 demangling
    RESULT_NO_DEMANGLE=$(addr2line -fe cpp_demo $CPP_ADDR 2>&1)
    echo "Without -C flag: $RESULT_NO_DEMANGLE"

    # 有 demangling
    RESULT_DEMANGLE=$(addr2line -Cfe cpp_demo $CPP_ADDR 2>&1)
    echo "With -C flag: $RESULT_DEMANGLE"

    if echo "$RESULT_DEMANGLE" | grep -q "Container"; then
        print_result 0 "C++ demangling works"
    else
        print_result 1 "C++ demangling failed"
    fi
else
    print_result 1 "Could not find C++ symbol"
fi

# 測試4: 管道輸入
print_header "Test 4: Pipe input test"

echo "Testing pipe input..."
echo "$MAIN_ADDR" | addr2line -fe segfault_demo > /tmp/addr2line_pipe.txt 2>&1

if grep -q "main" /tmp/addr2line_pipe.txt; then
    print_result 0 "Pipe input works"
else
    print_result 1 "Pipe input failed"
fi

# 測試5: 優雅格式輸出 (-p)
print_header "Test 5: Pretty print format"

echo "Testing pretty print format..."
RESULT=$(addr2line -pfe segfault_demo $MAIN_ADDR 2>&1)
echo "Pretty format: $RESULT"

if echo "$RESULT" | grep -q "at"; then
    print_result 0 "Pretty print format works"
else
    print_result 1 "Pretty print format failed"
fi

# 測試6: Backtrace 功能
print_header "Test 6: Backtrace functionality"

echo "Running backtrace_demo..."
./backtrace_demo 1 > /tmp/backtrace_output.txt 2>&1

if grep -q "addr2line" /tmp/backtrace_output.txt; then
    print_result 0 "Backtrace demo generates addr2line commands"

    # 提取一個地址並測試
    ADDR=$(grep "Frame 0:" /tmp/backtrace_output.txt | awk '{print $3}')
    if [ -n "$ADDR" ]; then
        echo "Testing extracted address: $ADDR"
        RESULT=$(addr2line -Cfe backtrace_demo $ADDR 2>&1)
        echo "Resolved to: $RESULT"
        print_result 0 "Successfully resolved backtrace address"
    fi
else
    print_result 1 "Backtrace demo failed"
fi

# 測試7: 測試函數處理
print_header "Test 7: Test function handling"

TEST_ADDR=$(nm segfault_demo | grep "test_function" | awk '{print "0x"$1}')
if [ -n "$TEST_ADDR" ]; then
    echo "Testing test_function at: $TEST_ADDR"
    RESULT=$(addr2line -fe segfault_demo $TEST_ADDR 2>&1)
    echo "Result: $RESULT"
    if echo "$RESULT" | grep -q "test_function"; then
        print_result 0 "Test function resolved correctly"
    else
        print_result 1 "Test function resolution failed"
    fi
else
    print_result 1 "Could not find test_function"
fi

# 測試8: 從 objdump 提取地址
print_header "Test 8: Integration with objdump"

echo "Extracting call instructions from objdump..."
objdump -d segfault_demo | grep "call" | head -5 | while read line; do
    ADDR=$(echo $line | awk '{print $1}' | sed 's/://')
    if [ -n "$ADDR" ]; then
        echo "Address: $ADDR"
        addr2line -fe segfault_demo 0x$ADDR 2>&1 | head -1
    fi
done

print_result 0 "objdump integration test completed"

# 測試9: 錯誤處理
print_header "Test 9: Error handling"

echo "Testing with invalid address..."
RESULT=$(addr2line -fe segfault_demo 0xdeadbeef 2>&1)
echo "Result for invalid address: $RESULT"

if echo "$RESULT" | grep -q "??"; then
    print_result 0 "Correctly handles invalid addresses"
else
    print_result 1 "Error handling issue"
fi

# 測試10: 實際崩潰分析（可選）
print_header "Test 10: Crash analysis simulation"

echo "Simulating crash analysis..."
cat > /tmp/crash_addresses.txt << EOF
$MAIN_ADDR
$FUNC_A
$FUNC_B
$FUNC_C
EOF

echo "Batch processing addresses..."
cat /tmp/crash_addresses.txt | while read addr; do
    if [ -n "$addr" ]; then
        addr2line -Cfpe segfault_demo $addr
    fi
done > /tmp/crash_analysis.txt 2>&1

if [ -s /tmp/crash_analysis.txt ]; then
    echo "Crash analysis output:"
    cat /tmp/crash_analysis.txt
    print_result 0 "Batch processing works"
else
    print_result 1 "Batch processing failed"
fi

# 最終報告
print_header "Test Summary"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ($TESTS_PASSED/$TOTAL_TESTS)${NC}"
    exit 0
else
    echo -e "${YELLOW}Some tests failed: $TESTS_FAILED/$TOTAL_TESTS${NC}"
    exit 1
fi