#!/bin/bash

echo "======================================================"
echo "         高頻交易完整測試套件 v1.0"
echo "======================================================"
echo ""

# 設定工作目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 顏色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 測試結果檔案
RESULT_FILE="hft_test_results_$(date +%Y%m%d_%H%M%S).txt"
echo "測試開始時間: $(date)" > $RESULT_FILE

# 檢查必要工具
check_tools() {
    echo -e "${BLUE}[檢查] 檢查必要工具...${NC}"
    
    # 檢查 perf
    if ! command -v perf &> /dev/null; then
        echo -e "${YELLOW}警告: perf 未安裝，部分測試將跳過${NC}"
        echo "安裝方法: sudo apt-get install linux-tools-common linux-tools-generic"
    fi
    
    # 檢查 taskset
    if ! command -v taskset &> /dev/null; then
        echo -e "${YELLOW}警告: taskset 未安裝${NC}"
        echo "安裝方法: sudo apt-get install util-linux"
    fi
    
    echo ""
}

# 1. 延遲測試 (Latency Test)
run_latency_test() {
    echo -e "${GREEN}========== 1. 延遲測試 (Latency Test) ==========${NC}"
    echo "測試訂單處理延遲分布..."
    echo ""
    
    echo "1. 延遲測試" >> $RESULT_FILE
    echo "==================" >> $RESULT_FILE
    
    # C++ 延遲測試
    echo "C++ 延遲測試:"
    if [ -f "hft_cpp_example/hft_trading" ]; then
        cd hft_cpp_example
        ./hft_trading 5 2>&1 | grep -E "latency|Average|P50|P95|P99" | tee -a ../$RESULT_FILE
        cd ..
    fi
    echo ""
    
    # Rust 延遲測試
    echo "Rust 延遲測試:"
    if [ -f "hft_rust_example/target/release/hft_rust_example" ]; then
        ./hft_rust_example/target/release/hft_rust_example 5 2>&1 | grep -E "latency|Average|P50|P95|P99" | tee -a $RESULT_FILE
    fi
    echo "" >> $RESULT_FILE
    echo ""
}

# 2. 吞吐量測試 (Throughput Test)
run_throughput_test() {
    echo -e "${GREEN}========== 2. 吞吐量測試 (Throughput Test) ==========${NC}"
    echo "測試每秒處理訂單數量..."
    echo ""
    
    echo "2. 吞吐量測試" >> $RESULT_FILE
    echo "==================" >> $RESULT_FILE
    
    # 測試不同負載下的吞吐量
    for load in 1 5 10 20; do
        echo "負載等級: $load 秒"
        echo "負載等級: $load 秒" >> $RESULT_FILE
        
        # C++ 測試
        echo -n "C++ 吞吐量: "
        if [ -f "hft_cpp_example/hft_trading" ]; then
            cd hft_cpp_example
            # 不使用 timeout，讓程式自然結束
            output=$(./hft_trading $load 2>&1 | grep "Total orders processed" | awk '{print $4}')
            cd ..
            if [ -n "$output" ]; then
                throughput=$((output / load))
            else
                throughput=0
            fi
            echo "$throughput orders/sec"
            echo "C++: $throughput orders/sec" >> $RESULT_FILE
        fi
        
        # Rust 測試
        echo -n "Rust 吞吐量: "
        if [ -f "hft_rust_example/target/release/hft_rust_example" ]; then
            # 不使用 timeout，讓程式自然結束
            output=$(./hft_rust_example/target/release/hft_rust_example $load 2>&1 | grep "Total orders processed" | awk '{print $4}')
            if [ -n "$output" ]; then
                throughput=$((output / load))
            else
                throughput=0
            fi
            echo "$throughput orders/sec"
            echo "Rust: $throughput orders/sec" >> $RESULT_FILE
        fi
        echo ""
    done
    echo "" >> $RESULT_FILE
}

# 3. 抖動分析 (Jitter Analysis)
run_jitter_test() {
    echo -e "${GREEN}========== 3. 抖動分析 (Jitter Analysis) ==========${NC}"
    echo "分析延遲變異性..."
    echo ""
    
    echo "3. 抖動分析" >> $RESULT_FILE
    echo "==================" >> $RESULT_FILE
    
    # 收集 100 次測試的延遲數據
    echo "收集 100 次測試樣本..."
    
    # C++ 抖動測試
    if [ -f "hft_cpp_example/hft_trading" ]; then
        echo "C++ 延遲樣本 (前 10 筆):"
        for i in {1..10}; do
            ./hft_cpp_example/hft_trading 0.1 2>&1 | grep "Average latency" | awk '{print $3}'
        done | tee cpp_jitter.tmp
        
        # 計算標準差
        if [ -f cpp_jitter.tmp ]; then
            avg=$(awk '{sum+=$1} END {print sum/NR}' cpp_jitter.tmp)
            std=$(awk -v avg=$avg '{sum+=($1-avg)^2} END {print sqrt(sum/NR)}' cpp_jitter.tmp)
            echo "C++ 平均延遲: $avg ns, 標準差: $std ns"
            echo "C++ 平均延遲: $avg ns, 標準差: $std ns" >> $RESULT_FILE
            rm cpp_jitter.tmp
        fi
    fi
    echo ""
    
    # Rust 抖動測試
    if [ -f "hft_rust_example/target/release/hft_rust_example" ]; then
        echo "Rust 延遲樣本 (前 10 筆):"
        for i in {1..10}; do
            ./hft_rust_example/target/release/hft_rust_example 0.1 2>&1 | grep "Average latency" | awk '{print $3}'
        done | tee rust_jitter.tmp
        
        # 計算標準差
        if [ -f rust_jitter.tmp ]; then
            avg=$(awk '{sum+=$1} END {print sum/NR}' rust_jitter.tmp)
            std=$(awk -v avg=$avg '{sum+=($1-avg)^2} END {print sqrt(sum/NR)}' rust_jitter.tmp)
            echo "Rust 平均延遲: $avg ns, 標準差: $std ns"
            echo "Rust 平均延遲: $avg ns, 標準差: $std ns" >> $RESULT_FILE
            rm rust_jitter.tmp
        fi
    fi
    echo "" >> $RESULT_FILE
    echo ""
}

# 4. CPU 親和性測試 (CPU Affinity Test)
run_cpu_affinity_test() {
    echo -e "${GREEN}========== 4. CPU 親和性測試 (CPU Affinity) ==========${NC}"
    echo "測試 CPU 核心綁定對效能的影響..."
    echo ""
    
    echo "4. CPU 親和性測試" >> $RESULT_FILE
    echo "==================" >> $RESULT_FILE
    
    if command -v taskset &> /dev/null; then
        # 測試不同 CPU 核心
        for cpu in 0 1 2 3; do
            echo "綁定到 CPU $cpu:"
            echo "CPU $cpu:" >> $RESULT_FILE
            
            # C++ 測試
            if [ -f "hft_cpp_example/hft_trading" ]; then
                result=$(taskset -c $cpu ./hft_cpp_example/hft_trading 2 2>&1 | grep "Average latency" | awk '{print $3}')
                echo "  C++ 延遲: $result ns"
                echo "  C++: $result ns" >> $RESULT_FILE
            fi
            
            # Rust 測試
            if [ -f "hft_rust_example/target/release/hft_rust_example" ]; then
                result=$(taskset -c $cpu ./hft_rust_example/target/release/hft_rust_example 2 2>&1 | grep "Average latency" | awk '{print $3}')
                echo "  Rust 延遲: $result ns"
                echo "  Rust: $result ns" >> $RESULT_FILE
            fi
        done
    else
        echo "taskset 未安裝，跳過此測試"
        echo "taskset 未安裝" >> $RESULT_FILE
    fi
    echo "" >> $RESULT_FILE
    echo ""
}

# 5. 記憶體效能測試 (Memory Performance)
run_memory_test() {
    echo -e "${GREEN}========== 5. 記憶體效能測試 (Memory Performance) ==========${NC}"
    echo "測試記憶體分配和快取效能..."
    echo ""
    
    echo "5. 記憶體效能測試" >> $RESULT_FILE
    echo "==================" >> $RESULT_FILE
    
    # 檢查記憶體使用
    echo "記憶體使用分析:"
    
    # C++ 記憶體測試
    if [ -f "hft_cpp_example/hft_trading" ]; then
        echo "C++ 程式:"
        ./hft_cpp_example/hft_trading 5 &
        PID=$!
        sleep 1
        
        if [ -d "/proc/$PID" ]; then
            VmRSS=$(cat /proc/$PID/status | grep VmRSS | awk '{print $2}')
            VmSize=$(cat /proc/$PID/status | grep VmSize | awk '{print $2}')
            echo "  實體記憶體 (RSS): $VmRSS KB"
            echo "  虛擬記憶體 (VmSize): $VmSize KB"
            echo "C++ - RSS: $VmRSS KB, VmSize: $VmSize KB" >> $RESULT_FILE
            kill $PID 2>/dev/null
        fi
    fi
    
    # Rust 記憶體測試
    if [ -f "hft_rust_example/target/release/hft_rust_example" ]; then
        echo "Rust 程式:"
        ./hft_rust_example/target/release/hft_rust_example 5 &
        PID=$!
        sleep 1
        
        if [ -d "/proc/$PID" ]; then
            VmRSS=$(cat /proc/$PID/status | grep VmRSS | awk '{print $2}')
            VmSize=$(cat /proc/$PID/status | grep VmSize | awk '{print $2}')
            echo "  實體記憶體 (RSS): $VmRSS KB"
            echo "  虛擬記憶體 (VmSize): $VmSize KB"
            echo "Rust - RSS: $VmRSS KB, VmSize: $VmSize KB" >> $RESULT_FILE
            kill $PID 2>/dev/null
        fi
    fi
    echo "" >> $RESULT_FILE
    echo ""
}

# 6. 快取效能測試 (Cache Performance)
run_cache_test() {
    echo -e "${GREEN}========== 6. 快取效能測試 (Cache Performance) ==========${NC}"
    echo "使用 perf 分析快取命中率..."
    echo ""
    
    echo "6. 快取效能測試" >> $RESULT_FILE
    echo "==================" >> $RESULT_FILE
    
    if command -v perf &> /dev/null; then
        # C++ 快取測試
        if [ -f "hft_cpp_example/hft_trading" ]; then
            echo "C++ 快取分析:"
            sudo perf stat -e cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses \
                ./hft_cpp_example/hft_trading 2 2>&1 | grep -E "cache|L1" | tee -a $RESULT_FILE
        fi
        echo ""
        
        # Rust 快取測試
        if [ -f "hft_rust_example/target/release/hft_rust_example" ]; then
            echo "Rust 快取分析:"
            sudo perf stat -e cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses \
                ./hft_rust_example/target/release/hft_rust_example 2 2>&1 | grep -E "cache|L1" | tee -a $RESULT_FILE
        fi
    else
        echo "perf 未安裝，跳過快取測試"
        echo "perf 未安裝" >> $RESULT_FILE
    fi
    echo "" >> $RESULT_FILE
    echo ""
}

# 7. 壓力測試 (Stress Test)
run_stress_test() {
    echo -e "${GREEN}========== 7. 壓力測試 (Stress Test) ==========${NC}"
    echo "長時間高負載測試..."
    echo ""
    
    echo "7. 壓力測試" >> $RESULT_FILE
    echo "==================" >> $RESULT_FILE
    
    STRESS_TIME=30
    echo "執行 $STRESS_TIME 秒壓力測試..."
    
    # C++ 壓力測試
    if [ -f "hft_cpp_example/hft_trading" ]; then
        echo "C++ 壓力測試:"
        start_time=$(date +%s%N)
        timeout $STRESS_TIME ./hft_cpp_example/hft_trading $STRESS_TIME > cpp_stress.log 2>&1
        end_time=$(date +%s%N)
        elapsed=$((($end_time - $start_time) / 1000000))
        
        orders=$(grep "Total orders processed" cpp_stress.log | awk '{print $4}')
        avg_latency=$(grep "Average latency" cpp_stress.log | awk '{print $3}')
        
        echo "  總處理訂單: $orders"
        echo "  平均延遲: $avg_latency ns"
        echo "  執行時間: $elapsed ms"
        echo "C++ - 訂單: $orders, 延遲: $avg_latency ns, 時間: $elapsed ms" >> $RESULT_FILE
        rm cpp_stress.log
    fi
    echo ""
    
    # Rust 壓力測試
    if [ -f "hft_rust_example/target/release/hft_rust_example" ]; then
        echo "Rust 壓力測試:"
        start_time=$(date +%s%N)
        timeout $STRESS_TIME ./hft_rust_example/target/release/hft_rust_example $STRESS_TIME > rust_stress.log 2>&1
        end_time=$(date +%s%N)
        elapsed=$((($end_time - $start_time) / 1000000))
        
        orders=$(grep "Total orders processed" rust_stress.log | awk '{print $4}')
        avg_latency=$(grep "Average latency" rust_stress.log | awk '{print $3}')
        
        echo "  總處理訂單: $orders"
        echo "  平均延遲: $avg_latency ns"
        echo "  執行時間: $elapsed ms"
        echo "Rust - 訂單: $orders, 延遲: $avg_latency ns, 時間: $elapsed ms" >> $RESULT_FILE
        rm rust_stress.log
    fi
    echo "" >> $RESULT_FILE
    echo ""
}

# 8. 尾延遲測試 (Tail Latency Test)
run_tail_latency_test() {
    echo -e "${GREEN}========== 8. 尾延遲測試 (Tail Latency) ==========${NC}"
    echo "分析 P50, P95, P99, P99.9 延遲..."
    echo ""
    
    echo "8. 尾延遲測試" >> $RESULT_FILE
    echo "==================" >> $RESULT_FILE
    
    # 這需要修改原始程式來輸出百分位數
    echo "需要程式支援百分位數統計輸出"
    echo "建議實作內容:"
    echo "  - P50 (中位數延遲)"
    echo "  - P95 (95% 的請求在此延遲內)"
    echo "  - P99 (99% 的請求在此延遲內)"
    echo "  - P99.9 (99.9% 的請求在此延遲內)"
    echo "  - 最大延遲"
    echo ""
    echo "需要程式支援" >> $RESULT_FILE
    echo "" >> $RESULT_FILE
}

# 9. 並發測試 (Concurrency Test)
run_concurrency_test() {
    echo -e "${GREEN}========== 9. 並發測試 (Concurrency Test) ==========${NC}"
    echo "測試多執行緒效能..."
    echo ""
    
    echo "9. 並發測試" >> $RESULT_FILE
    echo "==================" >> $RESULT_FILE
    
    # 同時執行多個實例
    echo "執行 4 個並發實例..."
    
    # C++ 並發測試
    if [ -f "hft_cpp_example/hft_trading" ]; then
        echo "C++ 並發測試:"
        for i in {1..4}; do
            ./hft_cpp_example/hft_trading 5 > cpp_concurrent_$i.log 2>&1 &
        done
        wait
        
        total_orders=0
        for i in {1..4}; do
            orders=$(grep "Total orders processed" cpp_concurrent_$i.log | awk '{print $4}')
            total_orders=$((total_orders + orders))
            rm cpp_concurrent_$i.log
        done
        
        echo "  總處理訂單 (4 實例): $total_orders"
        echo "C++ 並發總訂單: $total_orders" >> $RESULT_FILE
    fi
    echo ""
    
    # Rust 並發測試
    if [ -f "hft_rust_example/target/release/hft_rust_example" ]; then
        echo "Rust 並發測試:"
        for i in {1..4}; do
            ./hft_rust_example/target/release/hft_rust_example 5 > rust_concurrent_$i.log 2>&1 &
        done
        wait
        
        total_orders=0
        for i in {1..4}; do
            orders=$(grep "Total orders processed" rust_concurrent_$i.log | awk '{print $4}')
            total_orders=$((total_orders + orders))
            rm rust_concurrent_$i.log
        done
        
        echo "  總處理訂單 (4 實例): $total_orders"
        echo "Rust 並發總訂單: $total_orders" >> $RESULT_FILE
    fi
    echo "" >> $RESULT_FILE
    echo ""
}

# 10. 系統資源監控
run_system_monitor() {
    echo -e "${GREEN}========== 10. 系統資源監控 ==========${NC}"
    echo "監控測試期間的系統資源..."
    echo ""
    
    echo "10. 系統資源" >> $RESULT_FILE
    echo "==================" >> $RESULT_FILE
    
    # CPU 資訊
    echo "CPU 資訊:"
    lscpu | grep -E "Model name|CPU\(s\)|Thread|Core|Socket" | tee -a $RESULT_FILE
    echo ""
    
    # 記憶體資訊
    echo "記憶體資訊:"
    free -h | tee -a $RESULT_FILE
    echo ""
    
    # 系統負載
    echo "系統負載:"
    uptime | tee -a $RESULT_FILE
    echo "" >> $RESULT_FILE
}

# 產生測試報告
generate_report() {
    echo -e "${BLUE}======================================================"
    echo "                  測試報告摘要"
    echo "======================================================${NC}"
    echo ""
    
    echo "測試結果已儲存至: $RESULT_FILE"
    echo ""
    
    # 顯示關鍵指標
    echo "關鍵效能指標:"
    echo "-------------"
    
    if [ -f "$RESULT_FILE" ]; then
        # 提取關鍵數據
        echo "1. 延遲測試結果:"
        grep -A 2 "1. 延遲測試" $RESULT_FILE | tail -2
        
        echo ""
        echo "2. 吞吐量峰值:"
        grep "orders/sec" $RESULT_FILE | sort -t: -k2 -n | tail -2
        
        echo ""
        echo "3. 記憶體使用:"
        grep "RSS:" $RESULT_FILE
        
        echo ""
        echo "測試完成時間: $(date)"
    fi
    
    echo ""
    echo -e "${GREEN}測試完成！${NC}"
}

# 主選單
show_menu() {
    echo "選擇測試項目:"
    echo "============="
    echo "1) 執行所有測試"
    echo "2) 延遲測試"
    echo "3) 吞吐量測試"
    echo "4) 抖動分析"
    echo "5) CPU 親和性測試"
    echo "6) 記憶體效能測試"
    echo "7) 快取效能測試"
    echo "8) 壓力測試"
    echo "9) 尾延遲測試"
    echo "10) 並發測試"
    echo "11) 系統資源監控"
    echo "0) 退出"
    echo ""
}

# 主程式
main() {
    check_tools
    
    if [ "$1" == "--all" ] || [ "$1" == "-a" ]; then
        echo "執行所有測試..."
        run_latency_test
        run_throughput_test
        run_jitter_test
        run_cpu_affinity_test
        run_memory_test
        run_cache_test
        run_stress_test
        run_tail_latency_test
        run_concurrency_test
        run_system_monitor
        generate_report
    else
        while true; do
            show_menu
            read -p "請選擇 (0-11): " choice
            
            case $choice in
                1)
                    run_latency_test
                    run_throughput_test
                    run_jitter_test
                    run_cpu_affinity_test
                    run_memory_test
                    run_cache_test
                    run_stress_test
                    run_tail_latency_test
                    run_concurrency_test
                    run_system_monitor
                    generate_report
                    ;;
                2) run_latency_test ;;
                3) run_throughput_test ;;
                4) run_jitter_test ;;
                5) run_cpu_affinity_test ;;
                6) run_memory_test ;;
                7) run_cache_test ;;
                8) run_stress_test ;;
                9) run_tail_latency_test ;;
                10) run_concurrency_test ;;
                11) run_system_monitor ;;
                0) 
                    echo "退出測試套件"
                    exit 0
                    ;;
                *)
                    echo "無效選擇，請重試"
                    ;;
            esac
            
            echo ""
            read -p "按 Enter 繼續..."
        done
    fi
}

# 執行主程式
main "$@"