#!/bin/bash

# Go 並行範例測試腳本 - 重構版
set -e

echo "🚀 開始測試 Go 並行範例程式..."
echo "================================================"

# 計數器
TOTAL=0
PASSED=0
FAILED=0

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 測試函數
test_example() {
    local file=$1
    local description=$2
    local timeout=${3:-10}
    
    TOTAL=$((TOTAL + 1))
    echo -e "${BLUE}📋 測試 $TOTAL: $description${NC}"
    echo "   檔案: $file"
    
    if timeout ${timeout}s go run "$file" > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ 通過${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "   ${RED}❌ 失敗${NC}"
        FAILED=$((FAILED + 1))
        echo "   詳細錯誤："
        go run "$file" 2>&1 | head -10 | sed 's/^/      /'
    fi
    echo
}

# 檢查是否在正確目錄
if [ ! -f "01_goroutine_basics.go" ]; then
    echo -e "${RED}❌ 錯誤: 請從 concurrency_examples 目錄執行此腳本${NC}"
    exit 1
fi

# 開始測試
echo -e "${YELLOW}開始時間: $(date)${NC}"
echo

# 測試所有範例（按編號順序）
echo -e "${BLUE}🧪 執行範例測試...${NC}"
echo

test_example "01_goroutine_basics.go" "Goroutine 基礎操作" 15
test_example "02_channel_communication.go" "Channel 通訊機制" 15
test_example "03_select_multiplexing.go" "Select 多路復用" 15
test_example "04_mutex_synchronization.go" "Mutex 互斥同步" 15
test_example "05_rwmutex_optimization.go" "RWMutex 讀寫鎖優化" 15
test_example "06_waitgroup_synchronization.go" "WaitGroup 同步控制" 15
test_example "07_atomic_operations.go" "原子操作" 15
test_example "08_context_control.go" "Context 上下文控制" 20
test_example "09_producer_consumer_pattern.go" "生產者-消費者模式" 20
test_example "10_pipeline_pattern.go" "Pipeline 管道模式" 20
test_example "11_worker_pool_advanced.go" "高級 Worker Pool" 25

# 編譯測試
echo -e "${BLUE}🔨 編譯測試...${NC}"
compile_errors=0
find . -name "*.go" -type f | while read -r file; do
    echo "   編譯檢查: $file"
    if ! go build -o /tmp/concurrency_test_build "$file" 2>/dev/null; then
        echo -e "   ${RED}❌ 編譯失敗: $file${NC}"
        compile_errors=$((compile_errors + 1))
    fi
    rm -f /tmp/concurrency_test_build
done

# 計算成功率
if [ $TOTAL -gt 0 ]; then
    SUCCESS_RATE=$(( PASSED * 100 / TOTAL ))
else
    SUCCESS_RATE=0
fi

echo "================================================"
echo -e "${BLUE}📊 測試結果統計${NC}"
echo "總計: $TOTAL"
echo -e "通過: ${GREEN}$PASSED${NC}"
echo -e "失敗: ${RED}$FAILED${NC}"
echo "成功率: $SUCCESS_RATE%"
echo -e "${YELLOW}結束時間: $(date)${NC}"

# 顯示系統信息
echo
echo -e "${BLUE}🖥️  系統信息:${NC}"
echo "Go 版本: $(go version)"
echo "CPU 核心數: $(nproc 2>/dev/null || echo "未知")"
echo "記憶體使用: $(free -h 2>/dev/null | grep Mem | awk '{print $3"/"$2}' || echo "未知")"

# 性能建議
echo
echo -e "${BLUE}💡 建議:${NC}"
if [ $SUCCESS_RATE -eq 100 ]; then
    echo -e "${GREEN}🎉 所有測試通過！程式品質優秀。${NC}"
elif [ $SUCCESS_RATE -ge 80 ]; then
    echo -e "${YELLOW}⚠️  大部分測試通過，需要檢查失敗的測試。${NC}"
else
    echo -e "${RED}💥 多個測試失敗，需要仔細檢查程式碼。${NC}"
fi

# 提供快速修復建議
if [ $FAILED -gt 0 ]; then
    echo
    echo -e "${YELLOW}🔧 快速修復建議:${NC}"
    echo "1. 檢查 Go 版本是否 >= 1.18"
    echo "2. 確保所有依賴都已安裝: go mod tidy"
    echo "3. 檢查系統資源是否充足"
    echo "4. 單獨運行失敗的測試進行調試"
fi

# 範例使用說明
echo
echo -e "${BLUE}📖 使用說明:${NC}"
echo "單獨運行範例:"
echo "  go run 01_goroutine_basics.go"
echo
echo "查看範例代碼:"
echo "  less 01_goroutine_basics.go"
echo
echo "進行基準測試:"
echo "  go test -bench=. -benchmem"

# 退出狀態
if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 所有測試通過！${NC}"
    exit 0
else
    echo -e "\n${RED}💥 有 $FAILED 個測試失敗${NC}"
    exit 1
fi