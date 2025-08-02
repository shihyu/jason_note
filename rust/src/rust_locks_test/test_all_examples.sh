#!/bin/bash

# Rust 鎖機制指南 - 完整測試腳本
# 測試所有範例程式的編譯和執行

set -e  # 遇到錯誤立即退出

echo "🦀 Rust 鎖機制指南 - 完整測試腳本"
echo "=================================="
echo ""

# 檢查是否在正確目錄
if [ ! -f "Cargo.toml" ]; then
    echo "❌ 錯誤：請在 rust_locks_test 目錄中執行此腳本"
    exit 1
fi

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 成功/失敗計數
SUCCESS_COUNT=0
TOTAL_COUNT=0

# 測試函數
test_example() {
    local name=$1
    local description=$2
    
    echo -e "${BLUE}🔄 測試 $name - $description${NC}"
    echo "---"
    
    TOTAL_COUNT=$((TOTAL_COUNT + 1))
    
    if timeout 30s cargo run --example "$name" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $description 測試成功！${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${RED}❌ $description 測試失敗！${NC}"
        echo "   請手動執行查看詳細錯誤：cargo run --example $name"
    fi
    echo ""
}

# 測試 binary examples
test_binary() {
    local name=$1
    local description=$2
    
    echo -e "${BLUE}🔄 測試 $name - $description${NC}"
    echo "---"
    
    TOTAL_COUNT=$((TOTAL_COUNT + 1))
    
    if timeout 30s cargo run --bin "$name" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $description 測試成功！${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${RED}❌ $description 測試失敗！${NC}"
        echo "   請手動執行查看詳細錯誤：cargo run --bin $name"
    fi
    echo ""
}

# 首先檢查編譯
echo -e "${YELLOW}📦 檢查專案編譯...${NC}"
if cargo check; then
    echo -e "${GREEN}✅ 專案編譯成功${NC}"
    echo ""
else
    echo -e "${RED}❌ 專案編譯失敗，請先修復編譯錯誤${NC}"
    exit 1
fi

# 測試組織化的範例
echo -e "${YELLOW}🎯 測試組織化範例 (examples/)${NC}"
echo "======================================"

# 01. 基本互斥鎖範例
test_example "basic_counter" "Arc<Mutex<T>> 基本計數器"
test_example "shared_data_structure" "共享資料結構操作"
test_example "error_handling" "錯誤處理與毒化機制"

# 03. 原子操作範例
test_example "basic_atomic_counter" "基本原子計數器"
test_example "atomic_flags" "原子旗標控制"
test_example "compare_and_swap" "Compare-and-Swap 操作"

echo ""
echo -e "${YELLOW}🎯 測試傳統範例 (src/ binaries)${NC}"
echo "================================="

# 測試原有的 binary examples
test_binary "mutex_examples" "Arc<Mutex<T>> 完整範例集"
test_binary "rwlock_examples" "Arc<RwLock<T>> 讀寫鎖"
test_binary "atomic_examples" "Atomic 原子類型"
test_binary "channel_examples" "Channel 通道通訊"
test_binary "condvar_examples" "Condvar 條件變數"
test_binary "refcell_examples" "Rc<RefCell<T>> 單執行緒共享"

# 高級範例需要更長時間，單獨處理
echo -e "${BLUE}🔄 測試 advanced_examples - 高級並行模式${NC}"
echo "---"
TOTAL_COUNT=$((TOTAL_COUNT + 1))

if timeout 60s cargo run --bin advanced_examples > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 高級並行模式 測試成功！${NC}"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    echo -e "${YELLOW}⚠️  高級範例可能需要更長時間或手動停止${NC}"
    echo "   可手動執行查看：cargo run --bin advanced_examples"
fi
echo ""

# 測試主要執行程式
echo -e "${BLUE}🔄 測試 all_examples - 完整測試套件${NC}"
echo "---"
TOTAL_COUNT=$((TOTAL_COUNT + 1))

if timeout 60s cargo run --bin all_examples > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 完整測試套件 測試成功！${NC}"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    echo -e "${YELLOW}⚠️  完整測試可能需要更長時間${NC}"
    echo "   可手動執行查看：cargo run --bin all_examples"
fi
echo ""

# 效能測試（快速版本）
echo -e "${YELLOW}⚡ 快速效能測試${NC}"
echo "================"

echo -e "${BLUE}🏃 測試各種鎖機制的基本效能...${NC}"
cargo run --example basic_atomic_counter | grep "效能比較" || true
echo ""

# 最終統計
echo "=================================="
echo -e "${YELLOW}📊 測試結果統計${NC}"
echo "=================================="

if [ $SUCCESS_COUNT -eq $TOTAL_COUNT ]; then
    echo -e "${GREEN}🎉 所有測試通過！ ($SUCCESS_COUNT/$TOTAL_COUNT)${NC}"
    echo -e "${GREEN}✨ Rust 鎖機制指南的所有範例都正常運作${NC}"
else
    echo -e "${YELLOW}⚠️  部分測試通過：$SUCCESS_COUNT/$TOTAL_COUNT${NC}"
    FAILED_COUNT=$((TOTAL_COUNT - SUCCESS_COUNT))
    echo -e "${RED}❌ 失敗的測試數量：$FAILED_COUNT${NC}"
fi

echo ""
echo -e "${BLUE}💡 使用提示：${NC}"
echo "   • 執行單個範例：cargo run --example <名稱>"
echo "   • 執行傳統範例：cargo run --bin <名稱>"
echo "   • 查看可用範例：cargo run --example --help"
echo "   • 查看專案結構：tree examples/ 或 ls -la examples/"

echo ""
echo -e "${GREEN}🦀 Happy Rust Coding! 🦀${NC}"