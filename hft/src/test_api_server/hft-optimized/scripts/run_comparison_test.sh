#!/bin/bash

# HFT 優化版 vs 原版效能比較測試腳本
# 用法: sudo ./run_comparison_test.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BASE_DIR="/home/shihyu/github/jason_note/src/hft/src/test_api_server"
RESULTS_DIR="${BASE_DIR}/hft-optimized/test_results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}HFT 優化版 vs 原版效能比較測試${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 檢查是否以 root 執行
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}請使用 sudo 執行此腳本${NC}"
    echo "用法: sudo ./run_comparison_test.sh"
    exit 1
fi

# 創建結果目錄
mkdir -p "$RESULTS_DIR"

# 檢查伺服器是否運行
echo -e "${YELLOW}檢查伺服器狀態...${NC}"
if ! curl -s http://localhost:8080/stats > /dev/null 2>&1; then
    echo -e "${RED}錯誤: API 伺服器未運行${NC}"
    echo "請先啟動伺服器:"
    echo "  cd ${BASE_DIR}/rust-api-server"
    echo "  cargo run --release &"
    exit 1
fi
echo -e "${GREEN}✓ 伺服器運行中${NC}"
echo ""

# 應用系統優化
echo -e "${YELLOW}應用 HFT 系統優化...${NC}"
cd "${BASE_DIR}/hft-optimized/scripts"
./setup_hft_system.sh --apply-temp
echo ""

# 測試參數
TESTS=(
    "1000:100:100:中等規模"
    "10000:100:100:大規模"
)

# 函數: 執行測試並保存結果
run_test() {
    local client_name=$1
    local client_path=$2
    local orders=$3
    local connections=$4
    local warmup=$5
    local test_name=$6
    local output_file=$7

    echo -e "${BLUE}執行 ${client_name} - ${test_name}${NC}"
    echo "參數: orders=$orders, connections=$connections, warmup=$warmup"

    # 執行測試並保存輸出
    if [ "$client_name" == "HFT 優化版" ]; then
        # 確保 capabilities 設定
        setcap cap_ipc_lock+ep "$client_path" 2>/dev/null || true
        "$client_path" $orders $connections $warmup | tee "$output_file"
    else
        "$client_path" $orders $connections $warmup | tee "$output_file"
    fi

    echo ""
    sleep 3  # 讓伺服器休息一下
}

# 編譯客戶端
echo -e "${YELLOW}編譯客戶端...${NC}"

# 編譯原版
cd "${BASE_DIR}/c-client"
make clean && make
echo -e "${GREEN}✓ 原版 C 客戶端編譯完成${NC}"

# 編譯 HFT 版
cd "${BASE_DIR}/hft-optimized/c-client"
make clean && make
echo -e "${GREEN}✓ HFT 優化版編譯完成${NC}"
echo ""

# 執行所有測試
for test_config in "${TESTS[@]}"; do
    IFS=':' read -r orders connections warmup test_name <<< "$test_config"

    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}測試: ${test_name} (${orders} 訂單)${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    # 測試原版
    ORIGINAL_OUTPUT="${RESULTS_DIR}/original_${orders}_${TIMESTAMP}.txt"
    run_test "原版 C 客戶端" \
             "${BASE_DIR}/c-client/c_client" \
             "$orders" "$connections" "$warmup" \
             "$test_name" \
             "$ORIGINAL_OUTPUT"

    # 測試 HFT 版
    HFT_OUTPUT="${RESULTS_DIR}/hft_${orders}_${TIMESTAMP}.txt"
    run_test "HFT 優化版" \
             "${BASE_DIR}/hft-optimized/c-client/c_client_simple_hft" \
             "$orders" "$connections" "$warmup" \
             "$test_name" \
             "$HFT_OUTPUT"

    echo -e "${GREEN}✓ ${test_name} 測試完成${NC}"
    echo -e "${BLUE}結果已保存:${NC}"
    echo "  原版: $ORIGINAL_OUTPUT"
    echo "  HFT: $HFT_OUTPUT"
    echo ""
done

# 生成比較報告
COMPARISON_REPORT="${RESULTS_DIR}/comparison_report_${TIMESTAMP}.md"

echo -e "${YELLOW}生成比較報告...${NC}"

cat > "$COMPARISON_REPORT" << 'EOF'
# HFT 優化效能比較報告

## 測試時間
EOF

echo "**測試時間**: $(date)" >> "$COMPARISON_REPORT"
echo "" >> "$COMPARISON_REPORT"

cat >> "$COMPARISON_REPORT" << 'EOF'
## 測試環境

EOF

# 添加系統資訊
cat >> "$COMPARISON_REPORT" << EOF
- **CPU**: $(lscpu | grep "Model name" | sed 's/Model name: *//')
- **CPU 核心數**: $(nproc)
- **作業系統**: $(lsb_release -d | cut -f2)
- **核心版本**: $(uname -r)
- **記憶體**: $(free -h | awk '/^Mem:/ {print $2}')

## 系統優化狀態

EOF

# 檢查系統優化
cd "${BASE_DIR}/hft-optimized/scripts"
./setup_hft_system.sh --check >> "$COMPARISON_REPORT"

echo "" >> "$COMPARISON_REPORT"
echo "## 測試結果" >> "$COMPARISON_REPORT"
echo "" >> "$COMPARISON_REPORT"

# 解析測試結果
for test_config in "${TESTS[@]}"; do
    IFS=':' read -r orders connections warmup test_name <<< "$test_config"

    ORIGINAL_OUTPUT="${RESULTS_DIR}/original_${orders}_${TIMESTAMP}.txt"
    HFT_OUTPUT="${RESULTS_DIR}/hft_${orders}_${TIMESTAMP}.txt"

    echo "### ${test_name} (${orders} 訂單, ${connections} 並發)" >> "$COMPARISON_REPORT"
    echo "" >> "$COMPARISON_REPORT"
    echo "| 指標 | 原版 C 客戶端 | HFT 優化版 | 改善幅度 |" >> "$COMPARISON_REPORT"
    echo "|------|--------------|-----------|---------|" >> "$COMPARISON_REPORT"

    # 提取關鍵指標
    extract_metric() {
        local file=$1
        local metric=$2
        grep "$metric" "$file" | awk '{print $(NF-1)}' | head -1
    }

    # 計算改善百分比
    calc_improvement() {
        local original=$1
        local optimized=$2
        echo "scale=1; (($original - $optimized) / $original) * 100" | bc
    }

    # Min latency
    orig_min=$(extract_metric "$ORIGINAL_OUTPUT" "Min latency")
    hft_min=$(extract_metric "$HFT_OUTPUT" "Min latency")
    if [ -n "$orig_min" ] && [ -n "$hft_min" ]; then
        improvement=$(calc_improvement "$orig_min" "$hft_min")
        echo "| **最小延遲** | ${orig_min} ms | ${hft_min} ms | ↓ ${improvement}% |" >> "$COMPARISON_REPORT"
    fi

    # Max latency
    orig_max=$(extract_metric "$ORIGINAL_OUTPUT" "Max latency")
    hft_max=$(extract_metric "$HFT_OUTPUT" "Max latency")
    if [ -n "$orig_max" ] && [ -n "$hft_max" ]; then
        improvement=$(calc_improvement "$orig_max" "$hft_max")
        echo "| **最大延遲** | ${orig_max} ms | ${hft_max} ms | ↓ ${improvement}% |" >> "$COMPARISON_REPORT"
    fi

    # Avg latency
    orig_avg=$(extract_metric "$ORIGINAL_OUTPUT" "Avg latency")
    hft_avg=$(extract_metric "$HFT_OUTPUT" "Avg latency")
    if [ -n "$orig_avg" ] && [ -n "$hft_avg" ]; then
        improvement=$(calc_improvement "$orig_avg" "$hft_avg")
        echo "| **平均延遲** | ${orig_avg} ms | ${hft_avg} ms | ↓ ${improvement}% |" >> "$COMPARISON_REPORT"
    fi

    # P50
    orig_p50=$(extract_metric "$ORIGINAL_OUTPUT" "P50")
    hft_p50=$(extract_metric "$HFT_OUTPUT" "P50")
    if [ -n "$orig_p50" ] && [ -n "$hft_p50" ]; then
        improvement=$(calc_improvement "$orig_p50" "$hft_p50")
        echo "| **中位數 (P50)** | ${orig_p50} ms | ${hft_p50} ms | ↓ ${improvement}% |" >> "$COMPARISON_REPORT"
    fi

    # P90
    orig_p90=$(extract_metric "$ORIGINAL_OUTPUT" "P90")
    hft_p90=$(extract_metric "$HFT_OUTPUT" "P90")
    if [ -n "$orig_p90" ] && [ -n "$hft_p90" ]; then
        improvement=$(calc_improvement "$orig_p90" "$hft_p90")
        echo "| **P90 延遲** | ${orig_p90} ms | ${hft_p90} ms | ↓ ${improvement}% |" >> "$COMPARISON_REPORT"
    fi

    # P95
    orig_p95=$(extract_metric "$ORIGINAL_OUTPUT" "P95")
    hft_p95=$(extract_metric "$HFT_OUTPUT" "P95")
    if [ -n "$orig_p95" ] && [ -n "$hft_p95" ]; then
        improvement=$(calc_improvement "$orig_p95" "$hft_p95")
        echo "| **P95 延遲** | ${orig_p95} ms | ${hft_p95} ms | ↓ ${improvement}% |" >> "$COMPARISON_REPORT"
    fi

    # P99
    orig_p99=$(extract_metric "$ORIGINAL_OUTPUT" "P99")
    hft_p99=$(extract_metric "$HFT_OUTPUT" "P99")
    if [ -n "$orig_p99" ] && [ -n "$hft_p99" ]; then
        improvement=$(calc_improvement "$orig_p99" "$hft_p99")
        echo "| **P99 延遲** | ${orig_p99} ms | ${hft_p99} ms | ↓ ${improvement}% |" >> "$COMPARISON_REPORT"
    fi

    # Throughput
    orig_throughput=$(grep "Throughput:" "$ORIGINAL_OUTPUT" | awk '{print $2}')
    hft_throughput=$(grep "Throughput:" "$HFT_OUTPUT" | awk '{print $2}')
    if [ -n "$orig_throughput" ] && [ -n "$hft_throughput" ]; then
        echo "| **吞吐量** | ${orig_throughput} req/s | ${hft_throughput} req/s | - |" >> "$COMPARISON_REPORT"
    fi

    echo "" >> "$COMPARISON_REPORT"
done

# 添加原始測試輸出連結
cat >> "$COMPARISON_REPORT" << EOF
## 原始測試輸出

EOF

for test_config in "${TESTS[@]}"; do
    IFS=':' read -r orders connections warmup test_name <<< "$test_config"
    echo "### ${test_name}" >> "$COMPARISON_REPORT"
    echo "- 原版: \`original_${orders}_${TIMESTAMP}.txt\`" >> "$COMPARISON_REPORT"
    echo "- HFT: \`hft_${orders}_${TIMESTAMP}.txt\`" >> "$COMPARISON_REPORT"
    echo "" >> "$COMPARISON_REPORT"
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}測試完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}結果目錄: ${RESULTS_DIR}${NC}"
echo -e "${BLUE}比較報告: ${COMPARISON_REPORT}${NC}"
echo ""
echo "檢視報告:"
echo "  cat ${COMPARISON_REPORT}"
echo ""