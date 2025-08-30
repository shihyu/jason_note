#!/bin/bash

# Kernel Bypass 技術測試腳本
# 測試所有編譯好的程式

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 密碼
PASSWORD="f0409"

# 測試結果
PASSED=0
FAILED=0
SKIPPED=0

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Kernel Bypass 技術套件測試腳本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 檢查是否為 root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        echo -e "${YELLOW}某些測試需要 root 權限${NC}"
        echo -e "${YELLOW}使用 sudo $0 來執行完整測試${NC}"
        return 1
    fi
    return 0
}

# 列印測試標題
print_test_header() {
    echo ""
    echo -e "${BLUE}=== 測試: $1 ===${NC}"
}

# 列印測試結果
print_test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2 測試通過${NC}"
        ((PASSED++))
    elif [ $1 -eq 2 ]; then
        echo -e "${YELLOW}⊘ $2 測試跳過: $3${NC}"
        ((SKIPPED++))
    else
        echo -e "${RED}✗ $2 測試失敗${NC}"
        ((FAILED++))
    fi
}

# 檢查程式是否存在
check_program() {
    if [ ! -f "$1" ]; then
        echo -e "${YELLOW}程式 $1 未編譯${NC}"
        echo -e "${YELLOW}請先執行: make $2${NC}"
        return 1
    fi
    return 0
}

# 測試 io_uring
test_io_uring() {
    print_test_header "io_uring 非同步 I/O"
    
    if ! check_program "io_uring_async" "io_uring_async"; then
        print_test_result 2 "io_uring" "程式未編譯"
        return
    fi
    
    echo "啟動 io_uring 伺服器..."
    ./io_uring_async 12345 > /tmp/io_uring_test.log 2>&1 &
    SERVER_PID=$!
    sleep 2
    
    # 檢查伺服器是否執行
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        echo -e "${RED}伺服器啟動失敗${NC}"
        cat /tmp/io_uring_test.log
        print_test_result 1 "io_uring"
        return
    fi
    
    echo "測試連線和資料傳輸..."
    echo "測試訊息：你好 io_uring！" | nc -w 2 localhost 12345 > /tmp/io_uring_response.txt 2>&1
    
    # 檢查回應
    if grep -q "伺服器已收到" /tmp/io_uring_response.txt 2>/dev/null; then
        echo -e "${GREEN}收到正確回應${NC}"
        RESULT=0
    else
        echo -e "${RED}未收到預期回應${NC}"
        RESULT=1
    fi
    
    # 停止伺服器
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    
    # 顯示部分日誌
    echo "伺服器日誌:"
    tail -n 5 /tmp/io_uring_test.log
    
    print_test_result $RESULT "io_uring"
    rm -f /tmp/io_uring_test.log /tmp/io_uring_response.txt
}

# 測試 AF_XDP
test_af_xdp() {
    print_test_header "AF_XDP Socket"
    
    if ! check_program "af_xdp_socket" "af_xdp"; then
        print_test_result 2 "AF_XDP" "程式未編譯"
        return
    fi
    
    if ! check_root; then
        print_test_result 2 "AF_XDP" "需要 root 權限"
        return
    fi
    
    # 檢查是否有網路介面
    INTERFACE=$(ip link show | grep -E '^[0-9]+: (eth|ens|enp)' | head -1 | cut -d: -f2 | tr -d ' ')
    
    if [ -z "$INTERFACE" ]; then
        echo -e "${YELLOW}找不到適合的網路介面${NC}"
        print_test_result 2 "AF_XDP" "無網路介面"
        return
    fi
    
    echo "使用網路介面: $INTERFACE"
    echo "啟動 AF_XDP 程式 (5秒測試)..."
    
    timeout 5 ./af_xdp_socket $INTERFACE 0 > /tmp/af_xdp_test.log 2>&1
    
    # 檢查是否有錯誤
    if grep -q "錯誤" /tmp/af_xdp_test.log; then
        echo -e "${RED}AF_XDP 執行時發生錯誤${NC}"
        tail -n 5 /tmp/af_xdp_test.log
        print_test_result 1 "AF_XDP"
    else
        echo -e "${GREEN}AF_XDP 執行正常${NC}"
        print_test_result 0 "AF_XDP"
    fi
    
    rm -f /tmp/af_xdp_test.log
}

# 測試 RDMA
test_rdma() {
    print_test_header "RDMA 通訊"
    
    if ! check_program "rdma_communication" "rdma"; then
        print_test_result 2 "RDMA" "程式未編譯"
        return
    fi
    
    # 檢查是否有 RDMA 裝置
    if ! ls /sys/class/infiniband/ 2>/dev/null | grep -q .; then
        echo -e "${YELLOW}系統沒有 RDMA/InfiniBand 裝置${NC}"
        print_test_result 2 "RDMA" "無 RDMA 硬體"
        return
    fi
    
    echo "啟動 RDMA 伺服器..."
    ./rdma_communication server > /tmp/rdma_server.log 2>&1 &
    SERVER_PID=$!
    sleep 2
    
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        echo -e "${RED}RDMA 伺服器啟動失敗${NC}"
        cat /tmp/rdma_server.log
        print_test_result 1 "RDMA"
        return
    fi
    
    echo "啟動 RDMA 客戶端..."
    echo "測試 RDMA 訊息" | timeout 3 ./rdma_communication client localhost > /tmp/rdma_client.log 2>&1
    
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    
    if grep -q "成功連線" /tmp/rdma_client.log 2>/dev/null; then
        echo -e "${GREEN}RDMA 連線成功${NC}"
        print_test_result 0 "RDMA"
    else
        echo -e "${RED}RDMA 連線失敗${NC}"
        print_test_result 1 "RDMA"
    fi
    
    rm -f /tmp/rdma_server.log /tmp/rdma_client.log
}

# 測試 DPDK
test_dpdk() {
    print_test_header "DPDK 封包處理"
    
    if ! check_program "dpdk_packet_processing" "dpdk"; then
        print_test_result 2 "DPDK" "程式未編譯"
        return
    fi
    
    if ! check_root; then
        print_test_result 2 "DPDK" "需要 root 權限"
        return
    fi
    
    # 檢查大頁面
    HUGEPAGES=$(grep HugePages_Total /proc/meminfo | awk '{print $2}')
    if [ "$HUGEPAGES" -eq 0 ] 2>/dev/null; then
        echo -e "${YELLOW}系統未配置大頁面記憶體${NC}"
        echo "嘗試配置大頁面..."
        echo $PASSWORD | sudo -S mkdir -p /mnt/huge
        echo $PASSWORD | sudo -S mount -t hugetlbfs nodev /mnt/huge 2>/dev/null
        echo $PASSWORD | sudo -S sh -c 'echo 64 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages'
        
        HUGEPAGES=$(grep HugePages_Total /proc/meminfo | awk '{print $2}')
        if [ "$HUGEPAGES" -eq 0 ] 2>/dev/null; then
            print_test_result 2 "DPDK" "無法配置大頁面"
            return
        fi
    fi
    
    echo "大頁面已配置: ${HUGEPAGES} 頁"
    echo "測試 DPDK 初始化 (3秒)..."
    
    timeout 3 ./dpdk_packet_processing -l 0 -n 1 --no-pci > /tmp/dpdk_test.log 2>&1
    
    if grep -q "EAL" /tmp/dpdk_test.log; then
        echo -e "${GREEN}DPDK EAL 初始化成功${NC}"
        print_test_result 0 "DPDK"
    else
        echo -e "${RED}DPDK 初始化失敗${NC}"
        tail -n 5 /tmp/dpdk_test.log
        print_test_result 1 "DPDK"
    fi
    
    rm -f /tmp/dpdk_test.log
}

# 效能測試
performance_test() {
    print_test_header "效能基準測試"
    
    if [ ! -f "io_uring_async" ]; then
        echo -e "${YELLOW}需要 io_uring_async 來執行效能測試${NC}"
        return
    fi
    
    echo "執行 io_uring 效能測試..."
    ./io_uring_async 12346 > /tmp/perf_test.log 2>&1 &
    SERVER_PID=$!
    sleep 1
    
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        echo -e "${RED}無法啟動效能測試伺服器${NC}"
        return
    fi
    
    echo "傳送 1000 個測試請求..."
    for i in {1..1000}; do
        echo "效能測試訊息 $i" | nc -w 0 localhost 12346 2>/dev/null &
    done
    
    wait
    sleep 2
    
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    
    # 分析結果
    if grep -q "請求:" /tmp/perf_test.log; then
        echo -e "${GREEN}效能測試結果:${NC}"
        grep "統計" /tmp/perf_test.log | tail -n 5
    fi
    
    rm -f /tmp/perf_test.log
}

# 主測試流程
main() {
    echo "開始時間: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # 編譯檢查
    echo -e "${BLUE}檢查編譯狀態...${NC}"
    make check-deps
    echo ""
    
    # 執行測試
    test_io_uring
    test_af_xdp
    test_rdma
    test_dpdk
    performance_test
    
    # 總結
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}           測試總結${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "通過: ${GREEN}$PASSED${NC}"
    echo -e "失敗: ${RED}$FAILED${NC}"
    echo -e "跳過: ${YELLOW}$SKIPPED${NC}"
    echo ""
    echo "結束時間: $(date '+%Y-%m-%d %H:%M:%S')"
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}所有測試完成！${NC}"
        exit 0
    else
        echo -e "${RED}有 $FAILED 個測試失敗${NC}"
        exit 1
    fi
}

# 顯示幫助
show_help() {
    echo "使用方法: $0 [選項]"
    echo ""
    echo "選項:"
    echo "  -h, --help      顯示此幫助訊息"
    echo "  -q, --quick     只執行快速測試"
    echo "  -f, --full      執行完整測試 (需要 root)"
    echo "  -p, --perf      只執行效能測試"
    echo ""
    echo "範例:"
    echo "  $0              # 執行標準測試"
    echo "  sudo $0 -f      # 執行完整測試"
    echo "  $0 -p           # 只執行效能測試"
}

# 處理命令列參數
case "$1" in
    -h|--help)
        show_help
        exit 0
        ;;
    -q|--quick)
        test_io_uring
        ;;
    -f|--full)
        if ! check_root; then
            echo -e "${RED}完整測試需要 root 權限${NC}"
            exit 1
        fi
        main
        ;;
    -p|--perf)
        performance_test
        ;;
    *)
        main
        ;;
esac