#!/bin/bash
# compare_performance.sh - 對比優化前後的性能

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Performance Comparison Script${NC}"
echo "===================================="

# 檢查是否有 perf 工具
if ! command -v perf &> /dev/null; then
    echo -e "${RED}Error: perf tool is not installed${NC}"
    echo "Please install perf tools:"
    echo "  Ubuntu/Debian: sudo apt-get install linux-tools-common linux-tools-generic"
    echo "  RHEL/CentOS: sudo yum install perf"
    exit 1
fi

# 檢查 FlameGraph 工具是否存在
if [ ! -d "FlameGraph" ]; then
    echo -e "${YELLOW}FlameGraph tools not found. Cloning from GitHub...${NC}"
    git clone https://github.com/brendangregg/FlameGraph.git
fi

# 編譯兩個版本
echo -e "\n${YELLOW}Compiling baseline version...${NC}"
g++ -g -O2 -fno-omit-frame-pointer -DBASELINE cpu_intensive.cpp -o baseline
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to compile baseline version${NC}"
    exit 1
fi

echo -e "${YELLOW}Compiling optimized version...${NC}"
g++ -g -O3 -march=native -fno-omit-frame-pointer cpu_intensive.cpp -o optimized
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to compile optimized version${NC}"
    exit 1
fi

# 創建輸出目錄
mkdir -p flamegraphs

# 收集基準版本數據
echo -e "\n${RED}Collecting baseline performance data...${NC}"
./baseline &
PID=$!
sleep 1

# 檢查是否需要 sudo
if perf record -F 99 -p $PID -g -o flamegraphs/baseline.data -- sleep 5 2>&1 | grep -q "Permission"; then
    echo -e "${YELLOW}Need sudo permission for perf record${NC}"
    sudo perf record -F 99 -p $PID -g -o flamegraphs/baseline.data -- sleep 5
fi
wait $PID

# 收集優化版本數據
echo -e "\n${GREEN}Collecting optimized performance data...${NC}"
./optimized &
PID=$!
sleep 1

if perf record -F 99 -p $PID -g -o flamegraphs/optimized.data -- sleep 5 2>&1 | grep -q "Permission"; then
    sudo perf record -F 99 -p $PID -g -o flamegraphs/optimized.data -- sleep 5
else
    perf record -F 99 -p $PID -g -o flamegraphs/optimized.data -- sleep 5
fi
wait $PID

# 生成火焰圖
echo -e "\n${YELLOW}Generating flame graphs...${NC}"

# 處理基準版本
if [ -f "flamegraphs/baseline.data" ]; then
    perf script -i flamegraphs/baseline.data 2>/dev/null | \
        ./FlameGraph/stackcollapse-perf.pl > flamegraphs/baseline.folded
    ./FlameGraph/flamegraph.pl \
        --title="Baseline CPU Performance" \
        --subtitle="O2 optimization" \
        --width=1400 \
        flamegraphs/baseline.folded > flamegraphs/baseline.svg
fi

# 處理優化版本
if [ -f "flamegraphs/optimized.data" ]; then
    perf script -i flamegraphs/optimized.data 2>/dev/null | \
        ./FlameGraph/stackcollapse-perf.pl > flamegraphs/optimized.folded
    ./FlameGraph/flamegraph.pl \
        --title="Optimized CPU Performance" \
        --subtitle="O3 optimization with native arch" \
        --width=1400 \
        flamegraphs/optimized.folded > flamegraphs/optimized.svg
fi

# 生成對比火焰圖
if [ -f "flamegraphs/baseline.folded" ] && [ -f "flamegraphs/optimized.folded" ]; then
    ./FlameGraph/difffolded.pl flamegraphs/baseline.folded flamegraphs/optimized.folded | \
        ./FlameGraph/flamegraph.pl \
            --title="Optimization Comparison" \
            --subtitle="Red = Slower in optimized, Blue = Faster in optimized" \
            --colors=java \
            --width=1400 > flamegraphs/diff.svg
fi

echo -e "\n${GREEN}Generated files:${NC}"
[ -f "flamegraphs/baseline.svg" ] && echo "  ✓ flamegraphs/baseline.svg (baseline performance)"
[ -f "flamegraphs/optimized.svg" ] && echo "  ✓ flamegraphs/optimized.svg (optimized performance)"
[ -f "flamegraphs/diff.svg" ] && echo "  ✓ flamegraphs/diff.svg (performance difference)"

# 簡單的性能統計
echo -e "\n${GREEN}Performance Summary:${NC}"
if [ -f "flamegraphs/baseline.folded" ]; then
    echo -n "Baseline samples: "
    awk '{sum+=$NF} END {print sum}' flamegraphs/baseline.folded
fi

if [ -f "flamegraphs/optimized.folded" ]; then
    echo -n "Optimized samples: "
    awk '{sum+=$NF} END {print sum}' flamegraphs/optimized.folded
fi

# 找出最大的改進
if [ -f "flamegraphs/baseline.folded" ] && [ -f "flamegraphs/optimized.folded" ]; then
    echo -e "\n${GREEN}Top improvements (if any):${NC}"
    ./FlameGraph/difffolded.pl flamegraphs/baseline.folded flamegraphs/optimized.folded 2>/dev/null | \
        sort -t' ' -k2 -nr | head -5 | while read line; do
            echo "  $line"
        done
fi

echo -e "\n${GREEN}Comparison complete!${NC}"
echo "View the flamegraphs in your browser:"
echo "  firefox flamegraphs/*.svg"