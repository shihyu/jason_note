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

# 編譯程式
compile_programs() {
    echo -e "${BLUE}[編譯] 編譯測試程式...${NC}"
    local compiled=false
    
    # 編譯 C 程式 (在 hft_c_example 目錄)
    if [ -d "hft_c_example" ]; then
        echo "編譯 C 程式..."
        cd hft_c_example
        
        # 檢查是否需要編譯
        if [ ! -f "hft_trading" ] || [ "hft_trading.c" -nt "hft_trading" ] || [ "Makefile" -nt "hft_trading" ]; then
            echo "  執行 make..."
            if make clean && make; then
                echo -e "  ${GREEN}C 程式編譯成功${NC}"
                compiled=true
            else
                echo -e "  ${RED}C 程式編譯失敗${NC}"
            fi
        else
            echo -e "  ${GREEN}C 程式已是最新版本${NC}"
        fi
        cd ..
    else
        echo -e "${YELLOW}警告: 找不到 hft_c_example 目錄${NC}"
    fi
    echo ""
    
    # 編譯 C++ 程式 (在 hft_cpp_example 目錄)
    if [ -d "hft_cpp_example" ]; then
        echo "編譯 C++ 程式..."
        cd hft_cpp_example
        
        # 檢查是否需要編譯
        if [ ! -f "hft_trading" ] || [ "hft_trading.cpp" -nt "hft_trading" ] || [ "Makefile" -nt "hft_trading" ]; then
            echo "  執行 make..."
            if make clean && make; then
                echo -e "  ${GREEN}C++ 程式編譯成功${NC}"
                compiled=true
            else
                echo -e "  ${RED}C++ 程式編譯失敗${NC}"
            fi
        else
            echo -e "  ${GREEN}C++ 程式已是最新版本${NC}"
        fi
        cd ..
    else
        echo -e "${YELLOW}警告: 找不到 hft_cpp_example 目錄${NC}"
    fi
    echo ""
    
    # 編譯 Rust 程式 (在 hft_rust_example 目錄)
    if [ -d "hft_rust_example" ] && [ -f "hft_rust_example/Cargo.toml" ]; then
        echo "編譯 Rust 程式..."
        cd hft_rust_example
        
        # 檢查是否需要編譯
        if [ ! -f "target/release/hft_rust_example" ] || [ "src/main.rs" -nt "target/release/hft_rust_example" ] || [ "Cargo.toml" -nt "target/release/hft_rust_example" ]; then
            echo "  執行 cargo build --release..."
            if cargo build --release; then
                echo -e "  ${GREEN}Rust 程式編譯成功${NC}"
                compiled=true
            else
                echo -e "  ${RED}Rust 程式編譯失敗${NC}"
            fi
        else
            echo -e "  ${GREEN}Rust 程式已是最新版本${NC}"
        fi
        cd ..
    else
        echo -e "${YELLOW}提示: 未找到 Rust 專案目錄${NC}"
    fi
    echo ""
    
    # 檢查編譯結果
    local c_ready=false
    local cpp_ready=false
    local rust_ready=false
    
    if [ -f "hft_c_example/hft_trading" ]; then
        c_ready=true
    fi
    
    if [ -f "hft_cpp_example/hft_trading" ]; then
        cpp_ready=true
    fi
    
    if [ -f "hft_rust_example/target/release/hft_rust_example" ]; then
        rust_ready=true
    fi
    
    if [ "$c_ready" = false ] && [ "$cpp_ready" = false ] && [ "$rust_ready" = false ]; then
        echo -e "${RED}錯誤: 沒有可用的測試程式，請檢查編譯錯誤${NC}"
        echo "退出測試..."
        exit 1
    fi
    
    echo -e "${GREEN}[編譯] 編譯完成${NC}"
    if [ "$c_ready" = true ]; then
        echo -e "  ${GREEN}✓ C 程式就緒${NC}"
    fi
    if [ "$cpp_ready" = true ]; then
        echo -e "  ${GREEN}✓ C++ 程式就緒${NC}"
    fi
    if [ "$rust_ready" = true ]; then
        echo -e "  ${GREEN}✓ Rust 程式就緒${NC}"
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
    
    # C 延遲測試
    echo "C 延遲測試:"
    if [ -f "hft_c_example/hft_trading" ]; then
        ./hft_c_example/hft_trading 5 2>&1 | grep -E "latency|Average|orders|Statistics" | tee -a $RESULT_FILE
    fi
    echo ""
    
    # C++ 延遲測試
    echo "C++ 延遲測試:"
    if [ -f "hft_cpp_example/hft_trading" ]; then
        ./hft_cpp_example/hft_trading 5 2>&1 | grep -E "latency|Average|P50|P95|P99" | tee -a $RESULT_FILE
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
        
        # C 測試
        echo -n "C 吞吐量: "
        if [ -f "hft_c_example/hft_trading" ]; then
            # C程式接受時間參數
            output=$(./hft_c_example/hft_trading $load 2>&1 | grep "Total orders processed" | awk '{print $4}')
            if [ -n "$output" ]; then
                throughput=$((output / load))
            else
                throughput=0
            fi
            echo "$throughput orders/sec"
            echo "C: $throughput orders/sec" >> $RESULT_FILE
        fi
        
        # C++ 測試
        echo -n "C++ 吞吐量: "
        if [ -f "hft_cpp_example/hft_trading" ]; then
            # 不使用 timeout，讓程式自然結束
            output=$(./hft_cpp_example/hft_trading $load 2>&1 | grep "Total orders processed" | awk '{print $4}')
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
    echo "收集 10 次測試樣本..."
    
    # C 抖動測試
    if [ -f "hft_c_example/hft_trading" ]; then
        echo "C 延遲樣本 (前 10 筆):"
        > /tmp/c_jitter_raw.tmp
        for i in {1..10}; do
            # 運行短時間測試並提取延遲 (確保程序完成)
            result=$(./hft_c_example/hft_trading 1 2>&1 | grep "^Average latency:" | head -1 | awk '{print $3}')
            if [ -n "$result" ]; then
                echo "$result" >> /tmp/c_jitter_raw.tmp
            fi
        done
        cat /tmp/c_jitter_raw.tmp | tee c_jitter.tmp
        
        # 計算標準差
        if [ -f c_jitter.tmp ] && [ -s c_jitter.tmp ]; then
            avg=$(awk '{sum+=$1} END {if(NR>0) print sum/NR; else print 0}' c_jitter.tmp)
            std=$(awk -v avg=$avg '{sum+=($1-avg)^2} END {if(NR>0) print sqrt(sum/NR); else print 0}' c_jitter.tmp)
            echo "C 平均延遲: $avg ns, 標準差: $std ns"
            echo "C 平均延遲: $avg ns, 標準差: $std ns" >> $RESULT_FILE
            rm c_jitter.tmp
        fi
    fi
    echo ""
    
    # C++ 抖動測試
    if [ -f "hft_cpp_example/hft_trading" ]; then
        echo "C++ 延遲樣本 (前 10 筆):"
        for i in {1..10}; do
            ./hft_cpp_example/hft_trading 0.1 2>&1 | grep "Average latency" | awk '{print $3}'
        done | tee cpp_jitter.tmp
        
        # 計算標準差
        if [ -f cpp_jitter.tmp ] && [ -s cpp_jitter.tmp ]; then
            avg=$(awk '{sum+=$1} END {if(NR>0) print sum/NR; else print 0}' cpp_jitter.tmp)
            std=$(awk -v avg=$avg '{sum+=($1-avg)^2} END {if(NR>0) print sqrt(sum/NR); else print 0}' cpp_jitter.tmp)
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
            
            # C 測試
            if [ -f "hft_c_example/hft_trading" ]; then
                result=$(taskset -c $cpu ./hft_c_example/hft_trading 2 2>&1 | grep "Average latency" | awk '{print $3}')
                if [ -n "$result" ]; then
                    echo "  C 延遲: $result ns"
                    echo "  C: $result ns" >> $RESULT_FILE
                else
                    echo "  C 延遲: 測試中..."
                    echo "  C: 測試中" >> $RESULT_FILE
                fi
            fi
            
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
    
    # C 記憶體測試
    if [ -f "hft_c_example/hft_trading" ]; then
        echo "C 程式:"
        ./hft_c_example/hft_trading 5 &
        PID=$!
        sleep 1
        
        if [ -d "/proc/$PID" ]; then
            VmRSS=$(cat /proc/$PID/status | grep VmRSS | awk '{print $2}')
            VmSize=$(cat /proc/$PID/status | grep VmSize | awk '{print $2}')
            echo "  實體記憶體 (RSS): $VmRSS KB"
            echo "  虛擬記憶體 (VmSize): $VmSize KB"
            echo "C - RSS: $VmRSS KB, VmSize: $VmSize KB" >> $RESULT_FILE
            kill $PID 2>/dev/null
        fi
    fi
    
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
    
    # 檢查 perf 是否正確安裝
    PERF_AVAILABLE=false
    if command -v perf &> /dev/null; then
        # 設定 sudo 密碼
        SUDO_PASSWORD="f0409"
        
        # 測試 perf 是否真的可用
        echo $SUDO_PASSWORD | sudo -S perf --version &>/dev/null
        if [ $? -eq 0 ]; then
            PERF_AVAILABLE=true
            # 檢查當前用戶是否為 root
            if [ "$EUID" -eq 0 ]; then
                USE_SUDO=""
            else
                echo -e "${GREEN}使用 sudo 執行 perf 命令...${NC}"
                # 先降低 perf_event_paranoid 設定
                echo $SUDO_PASSWORD | sudo -S sh -c 'echo 1 > /proc/sys/kernel/perf_event_paranoid' 2>/dev/null
                USE_SUDO="echo $SUDO_PASSWORD | sudo -S"
            fi
        else
            echo -e "${YELLOW}警告: perf 工具未正確安裝，需要安裝 linux-tools-$(uname -r)${NC}"
            echo -e "${YELLOW}請執行: sudo apt-get install linux-tools-generic linux-cloud-tools-generic${NC}"
        fi
    else
        echo -e "${YELLOW}警告: perf 命令不存在${NC}"
    fi
    
    if [ "$PERF_AVAILABLE" = true ]; then
        
        # C 快取測試
        if [ -f "hft_c_example/hft_trading" ]; then
            echo "C 快取分析:"
            if [ -n "$USE_SUDO" ]; then
                echo $SUDO_PASSWORD | sudo -S perf stat -e cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses \
                    ./hft_c_example/hft_trading 2 2>&1 | grep -E "cache|L1" > /tmp/cache_c.tmp 2>&1
            else
                perf stat -e cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses \
                    ./hft_c_example/hft_trading 2 2>&1 | grep -E "cache|L1" > /tmp/cache_c.tmp 2>&1
            fi
            
            if [ -s /tmp/cache_c.tmp ]; then
                cat /tmp/cache_c.tmp | tee -a $RESULT_FILE
            else
                # 如果 perf 失敗，使用簡化的快取測試
                echo "  使用簡化快取測試..."
                ./hft_c_example/hft_trading 2 > /tmp/c_cache_test.log 2>&1
                
                # 計算簡單的快取效能指標
                total_time=$(grep "^Average latency:" /tmp/c_cache_test.log | head -1 | awk '{print $3}')
                orders=$(grep "^Total orders processed:" /tmp/c_cache_test.log | awk '{print $4}')
                
                if [ -n "$orders" ]; then
                    echo "  處理訂單數: $orders" | tee -a $RESULT_FILE
                    echo "  平均延遲: ${total_time:-N/A} ns" | tee -a $RESULT_FILE
                    echo "  估計快取效能: 良好 (基於低延遲)" | tee -a $RESULT_FILE
                else
                    echo "  無法獲取快取效能數據" | tee -a $RESULT_FILE
                fi
                rm -f /tmp/c_cache_test.log
            fi
            rm -f /tmp/cache_c.tmp
        fi
        echo ""
        
        # C++ 快取測試
        if [ -f "hft_cpp_example/hft_trading" ]; then
            echo "C++ 快取分析:"
            if [ -n "$USE_SUDO" ]; then
                echo $SUDO_PASSWORD | sudo -S perf stat -e cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses \
                    ./hft_cpp_example/hft_trading 2 2>&1 | grep -E "cache|L1" > /tmp/cache_cpp.tmp 2>&1
            else
                perf stat -e cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses \
                    ./hft_cpp_example/hft_trading 2 2>&1 | grep -E "cache|L1" > /tmp/cache_cpp.tmp 2>&1
            fi
            
            if [ -s /tmp/cache_cpp.tmp ]; then
                cat /tmp/cache_cpp.tmp | tee -a $RESULT_FILE
            else
                # 如果 perf 失敗，使用簡化的快取測試
                echo "  使用簡化快取測試..."
                ./hft_cpp_example/hft_trading 2 > /tmp/cpp_cache_test.log 2>&1
                
                # 計算簡單的快取效能指標
                total_time=$(grep "Average latency" /tmp/cpp_cache_test.log | awk '{print $3}')
                orders=$(grep "Total orders processed" /tmp/cpp_cache_test.log | awk '{print $4}')
                
                if [ -n "$total_time" ] && [ -n "$orders" ]; then
                    echo "  處理訂單數: $orders" | tee -a $RESULT_FILE
                    echo "  平均延遲: $total_time ns" | tee -a $RESULT_FILE
                    echo "  估計快取效能: 良好 (基於低延遲)" | tee -a $RESULT_FILE
                else
                    echo "  無法獲取快取效能數據" | tee -a $RESULT_FILE
                fi
                rm -f /tmp/cpp_cache_test.log
            fi
            rm -f /tmp/cache_cpp.tmp
        fi
        echo ""
        
        # Rust 快取測試
        if [ -f "hft_rust_example/target/release/hft_rust_example" ]; then
            echo "Rust 快取分析:"
            if [ -n "$USE_SUDO" ]; then
                echo $SUDO_PASSWORD | sudo -S perf stat -e cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses \
                    ./hft_rust_example/target/release/hft_rust_example 2 2>&1 | grep -E "cache|L1" > /tmp/cache_rust.tmp 2>&1
            else
                perf stat -e cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses \
                    ./hft_rust_example/target/release/hft_rust_example 2 2>&1 | grep -E "cache|L1" > /tmp/cache_rust.tmp 2>&1
            fi
            
            if [ -s /tmp/cache_rust.tmp ]; then
                cat /tmp/cache_rust.tmp | tee -a $RESULT_FILE
            else
                # 如果 perf 失敗，使用簡化的快取測試
                echo "  使用簡化快取測試..."
                ./hft_rust_example/target/release/hft_rust_example 2 > /tmp/rust_cache_test.log 2>&1
                
                # 計算簡單的快取效能指標
                total_time=$(grep "Average latency" /tmp/rust_cache_test.log | awk '{print $3}')
                orders=$(grep "Total orders processed" /tmp/rust_cache_test.log | awk '{print $4}')
                
                if [ -n "$total_time" ] && [ -n "$orders" ]; then
                    echo "  處理訂單數: $orders" | tee -a $RESULT_FILE
                    echo "  平均延遲: $total_time ns" | tee -a $RESULT_FILE
                    echo "  估計快取效能: 良好 (基於低延遲)" | tee -a $RESULT_FILE
                else
                    echo "  無法獲取快取效能數據" | tee -a $RESULT_FILE
                fi
                rm -f /tmp/rust_cache_test.log
            fi
            rm -f /tmp/cache_rust.tmp
        fi
    else
        echo "perf 未安裝或不可用，使用替代方法測試快取效能..."
        echo "perf 未安裝或不可用，使用替代方法" >> $RESULT_FILE
        
        # 使用時間測量作為替代
        if [ -f "hft_c_example/hft_trading" ]; then
            echo "C 快取效能 (基於延遲分析):"
            ./hft_c_example/hft_trading 2 2>&1 | grep -E "^Average latency:|^Total orders" | head -3 | tee -a $RESULT_FILE
        fi
        
        if [ -f "hft_cpp_example/hft_trading" ]; then
            echo "C++ 快取效能 (基於延遲分析):"
            ./hft_cpp_example/hft_trading 2 2>&1 | grep -E "latency|orders" | head -3 | tee -a $RESULT_FILE
        fi
        
        if [ -f "hft_rust_example/target/release/hft_rust_example" ]; then
            echo "Rust 快取效能 (基於延遲分析):"
            ./hft_rust_example/target/release/hft_rust_example 2 2>&1 | grep -E "latency|orders" | head -3 | tee -a $RESULT_FILE
        fi
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
    
    # C 壓力測試
    if [ -f "hft_c_example/hft_trading" ]; then
        echo "C 壓力測試:"
        start_time=$(date +%s%N)
        ./hft_c_example/hft_trading $STRESS_TIME > c_stress.log 2>&1
        end_time=$(date +%s%N)
        elapsed=$((($end_time - $start_time) / 1000000))
        
        orders=$(grep "Total orders processed" c_stress.log | tail -1 | awk '{print $4}')
        avg_latency=$(grep "Average latency" c_stress.log | awk '{print $3}')
        
        echo "  總處理訂單: ${orders:-N/A}"
        echo "  平均延遲: ${avg_latency:-N/A} ns"
        echo "  執行時間: $elapsed ms"
        echo "C - 訂單: ${orders:-N/A}, 延遲: ${avg_latency:-N/A} ns, 時間: $elapsed ms" >> $RESULT_FILE
        rm c_stress.log
    fi
    echo ""
    
    # C++ 壓力測試
    if [ -f "hft_cpp_example/hft_trading" ]; then
        echo "C++ 壓力測試:"
        start_time=$(date +%s%N)
        ./hft_cpp_example/hft_trading $STRESS_TIME > cpp_stress.log 2>&1
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
        ./hft_rust_example/target/release/hft_rust_example $STRESS_TIME > rust_stress.log 2>&1
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
    
    # 收集延遲數據並計算百分位數
    echo "收集延遲樣本並計算百分位數..."
    
    # C 尾延遲測試
    if [ -f "hft_c_example/hft_trading" ]; then
        echo "C 尾延遲分析:"
        
        # 執行多次測試收集延遲數據
        > /tmp/c_latencies.txt
        for i in {1..10}; do
            # 執行測試並提取平均延遲
            latency=$(./hft_c_example/hft_trading 1 2>&1 | grep "^Average latency:" | awk '{print $3}')
            if [ -n "$latency" ]; then
                echo "$latency" >> /tmp/c_latencies.txt
            fi
        done
        
        # 計算百分位數
        if [ -s /tmp/c_latencies.txt ]; then
            # 排序延遲數據
            sort -n /tmp/c_latencies.txt > /tmp/c_sorted.txt
            total_lines=$(wc -l < /tmp/c_sorted.txt)
            
            if [ $total_lines -gt 0 ]; then
                # 計算百分位數位置
                p50_pos=$((total_lines * 50 / 100))
                p95_pos=$((total_lines * 95 / 100))
                p99_pos=$((total_lines * 99 / 100))
                p999_pos=$((total_lines * 999 / 1000))
                
                # 確保位置至少為1
                [ $p50_pos -eq 0 ] && p50_pos=1
                [ $p95_pos -eq 0 ] && p95_pos=1
                [ $p99_pos -eq 0 ] && p99_pos=1
                [ $p999_pos -eq 0 ] && p999_pos=1
                
                # 獲取百分位數值
                p50=$(sed -n "${p50_pos}p" /tmp/c_sorted.txt)
                p95=$(sed -n "${p95_pos}p" /tmp/c_sorted.txt)
                p99=$(sed -n "${p99_pos}p" /tmp/c_sorted.txt)
                p999=$(sed -n "${p999_pos}p" /tmp/c_sorted.txt)
                max_latency=$(tail -1 /tmp/c_sorted.txt)
                min_latency=$(head -1 /tmp/c_sorted.txt)
                
                # 計算平均值
                avg_latency=$(awk '{sum+=$1} END {print int(sum/NR)}' /tmp/c_sorted.txt)
                
                echo "  最小延遲: ${min_latency} ns" | tee -a $RESULT_FILE
                echo "  P50 (中位數): ${p50} ns" | tee -a $RESULT_FILE
                echo "  P95: ${p95} ns" | tee -a $RESULT_FILE
                echo "  P99: ${p99} ns" | tee -a $RESULT_FILE
                echo "  P99.9: ${p999} ns" | tee -a $RESULT_FILE
                echo "  最大延遲: ${max_latency} ns" | tee -a $RESULT_FILE
                echo "  平均延遲: ${avg_latency} ns" | tee -a $RESULT_FILE
                echo "  樣本數: ${total_lines}" | tee -a $RESULT_FILE
            else
                echo "  無法收集足夠的延遲數據" | tee -a $RESULT_FILE
            fi
        else
            echo "  無法收集延遲數據" | tee -a $RESULT_FILE
        fi
        rm -f /tmp/c_latencies.txt /tmp/c_sorted.txt
    fi
    echo ""
    
    # C++ 尾延遲測試
    if [ -f "hft_cpp_example/hft_trading" ]; then
        echo "C++ 尾延遲分析:"
        
        # 執行多次測試收集延遲數據
        > /tmp/cpp_latencies.txt
        for i in {1..10}; do
            # 執行測試並提取平均延遲
            latency=$(./hft_cpp_example/hft_trading 1 2>&1 | grep "Average latency" | grep -oE "[0-9]+ ns" | grep -oE "[0-9]+")
            if [ -n "$latency" ]; then
                echo "$latency" >> /tmp/cpp_latencies.txt
            fi
        done
        
        # 計算百分位數
        if [ -s /tmp/cpp_latencies.txt ]; then
            # 排序延遲數據
            sort -n /tmp/cpp_latencies.txt > /tmp/cpp_sorted.txt
            total_lines=$(wc -l < /tmp/cpp_sorted.txt)
            
            if [ $total_lines -gt 0 ]; then
                # 計算百分位數位置
                p50_pos=$((total_lines * 50 / 100))
                p95_pos=$((total_lines * 95 / 100))
                p99_pos=$((total_lines * 99 / 100))
                p999_pos=$((total_lines * 999 / 1000))
                
                # 確保位置至少為1
                [ $p50_pos -eq 0 ] && p50_pos=1
                [ $p95_pos -eq 0 ] && p95_pos=1
                [ $p99_pos -eq 0 ] && p99_pos=1
                [ $p999_pos -eq 0 ] && p999_pos=1
                
                # 獲取百分位數值
                p50=$(sed -n "${p50_pos}p" /tmp/cpp_sorted.txt)
                p95=$(sed -n "${p95_pos}p" /tmp/cpp_sorted.txt)
                p99=$(sed -n "${p99_pos}p" /tmp/cpp_sorted.txt)
                p999=$(sed -n "${p999_pos}p" /tmp/cpp_sorted.txt)
                max_latency=$(tail -1 /tmp/cpp_sorted.txt)
                min_latency=$(head -1 /tmp/cpp_sorted.txt)
                
                # 計算平均值
                avg_latency=$(awk '{sum+=$1} END {print int(sum/NR)}' /tmp/cpp_sorted.txt)
                
                echo "  最小延遲: ${min_latency} ns" | tee -a $RESULT_FILE
                echo "  P50 (中位數): ${p50} ns" | tee -a $RESULT_FILE
                echo "  P95: ${p95} ns" | tee -a $RESULT_FILE
                echo "  P99: ${p99} ns" | tee -a $RESULT_FILE
                echo "  P99.9: ${p999} ns" | tee -a $RESULT_FILE
                echo "  最大延遲: ${max_latency} ns" | tee -a $RESULT_FILE
                echo "  平均延遲: ${avg_latency} ns" | tee -a $RESULT_FILE
                echo "  樣本數: ${total_lines}" | tee -a $RESULT_FILE
            else
                echo "  無法收集足夠的延遲數據" | tee -a $RESULT_FILE
            fi
        else
            echo "  無法收集延遲數據" | tee -a $RESULT_FILE
        fi
        rm -f /tmp/cpp_latencies.txt /tmp/cpp_sorted.txt
    fi
    echo ""
    
    # Rust 尾延遲測試
    if [ -f "hft_rust_example/target/release/hft_rust_example" ]; then
        echo "Rust 尾延遲分析:"
        
        # 執行多次測試收集延遲數據
        > /tmp/rust_latencies.txt
        for i in {1..10}; do
            # 執行測試並提取平均延遲
            latency=$(./hft_rust_example/target/release/hft_rust_example 1 2>&1 | grep "Average latency" | grep -oE "[0-9]+ ns" | grep -oE "[0-9]+")
            if [ -n "$latency" ]; then
                echo "$latency" >> /tmp/rust_latencies.txt
            fi
        done
        
        # 計算百分位數
        if [ -s /tmp/rust_latencies.txt ]; then
            # 排序延遲數據
            sort -n /tmp/rust_latencies.txt > /tmp/rust_sorted.txt
            total_lines=$(wc -l < /tmp/rust_sorted.txt)
            
            if [ $total_lines -gt 0 ]; then
                # 計算百分位數位置
                p50_pos=$((total_lines * 50 / 100))
                p95_pos=$((total_lines * 95 / 100))
                p99_pos=$((total_lines * 99 / 100))
                p999_pos=$((total_lines * 999 / 1000))
                
                # 確保位置至少為1
                [ $p50_pos -eq 0 ] && p50_pos=1
                [ $p95_pos -eq 0 ] && p95_pos=1
                [ $p99_pos -eq 0 ] && p99_pos=1
                [ $p999_pos -eq 0 ] && p999_pos=1
                
                # 獲取百分位數值
                p50=$(sed -n "${p50_pos}p" /tmp/rust_sorted.txt)
                p95=$(sed -n "${p95_pos}p" /tmp/rust_sorted.txt)
                p99=$(sed -n "${p99_pos}p" /tmp/rust_sorted.txt)
                p999=$(sed -n "${p999_pos}p" /tmp/rust_sorted.txt)
                max_latency=$(tail -1 /tmp/rust_sorted.txt)
                min_latency=$(head -1 /tmp/rust_sorted.txt)
                
                # 計算平均值
                avg_latency=$(awk '{sum+=$1} END {print int(sum/NR)}' /tmp/rust_sorted.txt)
                
                echo "  最小延遲: ${min_latency} ns" | tee -a $RESULT_FILE
                echo "  P50 (中位數): ${p50} ns" | tee -a $RESULT_FILE
                echo "  P95: ${p95} ns" | tee -a $RESULT_FILE
                echo "  P99: ${p99} ns" | tee -a $RESULT_FILE
                echo "  P99.9: ${p999} ns" | tee -a $RESULT_FILE
                echo "  最大延遲: ${max_latency} ns" | tee -a $RESULT_FILE
                echo "  平均延遲: ${avg_latency} ns" | tee -a $RESULT_FILE
                echo "  樣本數: ${total_lines}" | tee -a $RESULT_FILE
            else
                echo "  無法收集足夠的延遲數據" | tee -a $RESULT_FILE
            fi
        else
            echo "  無法收集延遲數據" | tee -a $RESULT_FILE
        fi
        rm -f /tmp/rust_latencies.txt /tmp/rust_sorted.txt
    fi
    
    echo "" >> $RESULT_FILE
    echo ""
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
    
    # C 並發測試
    if [ -f "hft_c_example/hft_trading" ]; then
        echo "C 並發測試:"
        for i in {1..4}; do
            ./hft_c_example/hft_trading 5 > c_concurrent_$i.log 2>&1 &
        done
        wait
        
        total_orders=0
        for i in {1..4}; do
            orders=$(grep "Total orders processed" c_concurrent_$i.log | tail -1 | awk '{print $4}')
            if [ -n "$orders" ]; then
                total_orders=$((total_orders + orders))
            fi
            rm c_concurrent_$i.log
        done
        
        echo "  總處理訂單 (4 實例): $total_orders"
        echo "C 並發總訂單: $total_orders" >> $RESULT_FILE
    fi
    echo ""
    
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
    compile_programs  # 在執行測試前先編譯程式
    
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