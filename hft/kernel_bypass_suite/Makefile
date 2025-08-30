# Kernel Bypass 技術套件 Makefile
# 編譯所有 kernel bypass 範例程式

CXX = g++
CXXFLAGS = -std=c++17 -Wall -O3 -march=native -mtune=native
LDFLAGS = -pthread

# 顏色輸出
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

# 目標程式
TARGETS = dpdk_packet_processing af_xdp_socket io_uring_async rdma_communication performance_test

# 預設目標
.PHONY: all clean help check-deps install-deps test

all: check-deps
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)建置 Kernel Bypass 技術套件$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@$(MAKE) io_uring_async
	@$(MAKE) performance_test
	@echo ""
	@echo "$(YELLOW)注意: DPDK、AF_XDP 和 RDMA 程式需要特殊環境設定$(NC)"
	@echo "$(YELLOW)請執行 'make help' 查看詳細說明$(NC)"

help:
	@echo "$(GREEN)=== Kernel Bypass 技術套件說明 ===$(NC)"
	@echo ""
	@echo "$(YELLOW)可用目標:$(NC)"
	@echo "  make all           - 編譯所有可用的程式"
	@echo "  make io_uring_async - 編譯 io_uring 非同步 I/O 程式"
	@echo "  make performance_test - 編譯效能測試程式"
	@echo "  make dpdk          - 編譯 DPDK 程式 (需要 DPDK 環境)"
	@echo "  make af_xdp        - 編譯 AF_XDP 程式 (需要 libbpf)"
	@echo "  make rdma          - 編譯 RDMA 程式 (需要 RDMA 套件)"
	@echo "  make test          - 測試編譯好的程式"
	@echo "  make install-deps  - 安裝相依套件 (需要 sudo)"
	@echo "  make clean         - 清除編譯的檔案"
	@echo ""
	@echo "$(YELLOW)環境需求:$(NC)"
	@echo "  - Linux kernel >= 5.1 (io_uring)"
	@echo "  - Linux kernel >= 4.18 (AF_XDP)"
	@echo "  - DPDK 21.11+ (DPDK 程式)"
	@echo "  - RDMA 驅動程式 (RDMA 程式)"
	@echo ""
	@echo "$(YELLOW)執行範例:$(NC)"
	@echo "  sudo ./io_uring_async [port]     # 啟動 io_uring 伺服器"
	@echo "  sudo ./af_xdp_socket eth0 0      # 在 eth0 上執行 AF_XDP"
	@echo "  sudo ./dpdk_packet_processing    # 執行 DPDK (需要大頁面)"
	@echo "  ./rdma_communication server      # 啟動 RDMA 伺服器"

check-deps:
	@echo "$(YELLOW)檢查系統相依性...$(NC)"
	@which g++ > /dev/null 2>&1 || (echo "$(RED)錯誤: 找不到 g++ 編譯器$(NC)" && exit 1)
	@echo "$(GREEN)✓ g++ 編譯器$(NC)"
	@if [ -f /usr/include/liburing.h ]; then \
		echo "$(GREEN)✓ liburing (io_uring)$(NC)"; \
	else \
		echo "$(YELLOW)✗ liburing 未安裝 (執行 'make install-deps' 安裝)$(NC)"; \
	fi
	@if pkg-config --exists libbpf 2>/dev/null; then \
		echo "$(GREEN)✓ libbpf (AF_XDP)$(NC)"; \
	else \
		echo "$(YELLOW)✗ libbpf 未安裝$(NC)"; \
	fi
	@if [ -d /usr/include/infiniband ]; then \
		echo "$(GREEN)✓ RDMA 標頭檔$(NC)"; \
	else \
		echo "$(YELLOW)✗ RDMA 套件未安裝$(NC)"; \
	fi
	@if [ -n "$$RTE_SDK" ]; then \
		echo "$(GREEN)✓ DPDK 環境變數已設定$(NC)"; \
	else \
		echo "$(YELLOW)✗ DPDK 環境未設定 (RTE_SDK)$(NC)"; \
	fi

install-deps:
	@echo "$(YELLOW)安裝相依套件 (需要密碼: f0409)...$(NC)"
	@echo "f0409" | sudo -S apt-get update
	@echo "$(GREEN)安裝 liburing (io_uring 支援)...$(NC)"
	@echo "f0409" | sudo -S apt-get install -y liburing-dev
	@echo "$(GREEN)安裝 libbpf (AF_XDP 支援)...$(NC)"
	@echo "f0409" | sudo -S apt-get install -y libbpf-dev
	@echo "$(GREEN)安裝 RDMA 套件...$(NC)"
	@echo "f0409" | sudo -S apt-get install -y libibverbs-dev librdmacm-dev
	@echo "$(GREEN)安裝 Linux 工具...$(NC)"
	@echo "f0409" | sudo -S apt-get install -y linux-tools-common linux-tools-generic
	@echo "$(GREEN)相依套件安裝完成！$(NC)"

# io_uring 程式 (最容易編譯)
io_uring_async: io_uring_async.cpp
	@echo "$(GREEN)編譯 io_uring 非同步 I/O 程式...$(NC)"
	@if [ -f /usr/include/liburing.h ]; then \
		$(CXX) $(CXXFLAGS) -o $@ $< -luring $(LDFLAGS) && \
		echo "$(GREEN)✓ io_uring_async 編譯成功$(NC)"; \
	else \
		echo "$(RED)錯誤: liburing 未安裝，請先執行 'make install-deps'$(NC)"; \
		exit 1; \
	fi

# AF_XDP 程式
af_xdp: af_xdp_socket
af_xdp_socket: af_xdp_socket.cpp
	@echo "$(GREEN)編譯 AF_XDP socket 程式...$(NC)"
	@if pkg-config --exists libbpf libxdp 2>/dev/null; then \
		$(CXX) $(CXXFLAGS) -o $@ $< \
			`pkg-config --cflags --libs libbpf libxdp` \
			-lbpf -lxdp $(LDFLAGS) && \
		echo "$(GREEN)✓ af_xdp_socket 編譯成功$(NC)"; \
	else \
		echo "$(RED)錯誤: libbpf/libxdp 未安裝或設定不正確$(NC)"; \
		echo "$(YELLOW)請安裝: sudo apt-get install libbpf-dev libxdp-dev$(NC)"; \
		exit 1; \
	fi

# RDMA 程式
rdma: rdma_communication
rdma_communication: rdma_communication.cpp
	@echo "$(GREEN)編譯 RDMA 通訊程式...$(NC)"
	@if [ -d /usr/include/infiniband ]; then \
		$(CXX) $(CXXFLAGS) -o $@ $< \
			-libverbs -lrdmacm $(LDFLAGS) && \
		echo "$(GREEN)✓ rdma_communication 編譯成功$(NC)"; \
	else \
		echo "$(RED)錯誤: RDMA 套件未安裝$(NC)"; \
		echo "$(YELLOW)請安裝: sudo apt-get install libibverbs-dev librdmacm-dev$(NC)"; \
		exit 1; \
	fi

# DPDK 程式 (需要 DPDK 環境)
dpdk: dpdk_packet_processing
dpdk_packet_processing: dpdk_packet_processing.cpp
	@echo "$(GREEN)編譯 DPDK 封包處理程式...$(NC)"
	@if [ -n "$$RTE_SDK" ] && [ -n "$$RTE_TARGET" ]; then \
		$(CXX) $(CXXFLAGS) -o $@ $< \
			-I$$RTE_SDK/$$RTE_TARGET/include \
			-L$$RTE_SDK/$$RTE_TARGET/lib \
			-Wl,--whole-archive -ldpdk -Wl,--no-whole-archive \
			-lnuma -ldl -lm $(LDFLAGS) && \
		echo "$(GREEN)✓ dpdk_packet_processing 編譯成功$(NC)"; \
	else \
		echo "$(RED)錯誤: DPDK 環境未設定$(NC)"; \
		echo "$(YELLOW)請設定 RTE_SDK 和 RTE_TARGET 環境變數$(NC)"; \
		echo "$(YELLOW)範例: export RTE_SDK=/path/to/dpdk$(NC)"; \
		echo "$(YELLOW)      export RTE_TARGET=x86_64-native-linux-gcc$(NC)"; \
		exit 1; \
	fi

# 測試編譯的程式
test:
	@echo "$(GREEN)=== 測試 Kernel Bypass 程式 ===$(NC)"
	@echo ""
	@if [ -f io_uring_async ]; then \
		echo "$(GREEN)測試 io_uring_async...$(NC)"; \
		timeout 2 ./io_uring_async 12345 > /dev/null 2>&1 & \
		sleep 1; \
		echo "測試訊息" | nc -w 1 localhost 12345 2>/dev/null || true; \
		pkill -f io_uring_async 2>/dev/null || true; \
		echo "$(GREEN)✓ io_uring_async 測試完成$(NC)"; \
	else \
		echo "$(YELLOW)io_uring_async 未編譯$(NC)"; \
	fi
	@echo ""
	@if [ -f af_xdp_socket ]; then \
		echo "$(YELLOW)AF_XDP 需要 root 權限和網路介面，跳過自動測試$(NC)"; \
		echo "手動測試: sudo ./af_xdp_socket eth0 0"; \
	fi
	@echo ""
	@if [ -f rdma_communication ]; then \
		echo "$(YELLOW)RDMA 需要 InfiniBand/RoCE 硬體，跳過自動測試$(NC)"; \
		echo "手動測試: ./rdma_communication server"; \
	fi
	@echo ""
	@if [ -f dpdk_packet_processing ]; then \
		echo "$(YELLOW)DPDK 需要大頁面和綁定網路介面，跳過自動測試$(NC)"; \
		echo "手動測試: sudo ./dpdk_packet_processing"; \
	fi

# 效能測試程式
performance_test: performance_test.cpp
	@echo "$(GREEN)編譯效能測試程式...$(NC)"
	@if [ -f /usr/include/liburing.h ]; then \
		$(CXX) $(CXXFLAGS) -o $@ $< -luring $(LDFLAGS) && \
		echo "$(GREEN)✓ performance_test 編譯成功$(NC)"; \
	else \
		echo "$(RED)錯誤: liburing 未安裝，請先執行 'make install-deps'$(NC)"; \
		exit 1; \
	fi

# 清理
clean:
	@echo "$(YELLOW)清除編譯的檔案...$(NC)"
	@rm -f $(TARGETS)
	@rm -f *.o
	@echo "$(GREEN)清除完成$(NC)"

# 設定大頁面 (DPDK 需要)
setup-hugepages:
	@echo "$(YELLOW)設定大頁面記憶體 (需要密碼: f0409)...$(NC)"
	@echo "f0409" | sudo -S mkdir -p /mnt/huge
	@echo "f0409" | sudo -S mount -t hugetlbfs nodev /mnt/huge
	@echo "f0409" | sudo -S sh -c 'echo 1024 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages'
	@echo "$(GREEN)大頁面設定完成$(NC)"
	@echo "f0409" | sudo -S grep Huge /proc/meminfo

# 個別編譯規則 (簡化版本，用於快速測試)
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

.PHONY: dpdk af_xdp rdma setup-hugepages