################################################################################
# HFT Latency Testing Makefile
# 
# 使用方法：
#   make help              - 顯示所有可用命令
#   make all               - 編譯所有測試程式
#   make test              - 運行所有測試
#   make demo              - 運行演示（展示所有功能）
################################################################################

# 編譯器設置
CXX = g++
CXXFLAGS = -O3 -Wall -Wextra -std=c++17 -march=native -mtune=native
DEBUG_FLAGS = -g -O0 -DDEBUG
PROFILE_FLAGS = -pg -fno-omit-frame-pointer

# Directories
SRC_DIR = .
BENCH_DIR = benchmarks
NET_DIR = network
MEM_DIR = memory
UTILS_DIR = utils
BUILD_DIR = build
BIN_DIR = bin

# Create directories
$(shell mkdir -p $(BUILD_DIR) $(BIN_DIR))

# Source files
BENCH_SRCS = $(BENCH_DIR)/basic_latency.cpp \
             $(BENCH_DIR)/orderbook_latency.cpp
NET_SRCS = $(NET_DIR)/udp_server.cpp \
           $(NET_DIR)/udp_client.cpp
MEM_SRCS = $(MEM_DIR)/memory_pool.cpp

ALL_SRCS = $(BENCH_SRCS) $(NET_SRCS) $(MEM_SRCS)

# Targets
BENCH_TARGETS = $(BIN_DIR)/basic_latency \
                $(BIN_DIR)/orderbook_latency
NET_TARGETS = $(BIN_DIR)/udp_server \
              $(BIN_DIR)/udp_client
MEM_TARGETS = $(BIN_DIR)/memory_pool

ALL_TARGETS = $(BENCH_TARGETS) $(NET_TARGETS) $(MEM_TARGETS)

# Default target
all: $(ALL_TARGETS)

# Benchmark targets
benchmarks: $(BENCH_TARGETS)

# Network targets
network: $(NET_TARGETS)

# Memory targets
memory: $(MEM_TARGETS)

# Build rules
$(BIN_DIR)/basic_latency: $(BENCH_DIR)/basic_latency.cpp
	@echo "Building basic latency benchmark..."
	$(CXX) $(CXXFLAGS) -o $@ $< -pthread

$(BIN_DIR)/orderbook_latency: $(BENCH_DIR)/orderbook_latency.cpp
	@echo "Building orderbook latency benchmark..."
	$(CXX) $(CXXFLAGS) -o $@ $< -pthread

$(BIN_DIR)/udp_server: $(NET_DIR)/udp_server.cpp
	@echo "Building UDP server..."
	$(CXX) $(CXXFLAGS) -o $@ $< -pthread

$(BIN_DIR)/udp_client: $(NET_DIR)/udp_client.cpp
	@echo "Building UDP client..."
	$(CXX) $(CXXFLAGS) -o $@ $< -pthread

$(BIN_DIR)/memory_pool: $(MEM_DIR)/memory_pool.cpp
	@echo "Building memory pool benchmark..."
	$(CXX) $(CXXFLAGS) -o $@ $< -pthread

# Debug builds
debug: CXXFLAGS = $(DEBUG_FLAGS) -Wall -Wextra -std=c++17
debug: 
	@$(MAKE) clean
	@mkdir -p $(BIN_DIR)
	@$(MAKE) all

# Profile builds  
profile: CXXFLAGS += $(PROFILE_FLAGS)
profile:
	@$(MAKE) clean
	@mkdir -p $(BIN_DIR)
	@$(MAKE) all

# Test targets
test-basic: $(BIN_DIR)/basic_latency
	@echo "=== Running Basic Latency Tests ==="
	$(BIN_DIR)/basic_latency

test-orderbook: $(BIN_DIR)/orderbook_latency
	@echo "=== Running Order Book Tests ==="
	$(BIN_DIR)/orderbook_latency

test-memory: $(BIN_DIR)/memory_pool
	@echo "=== Running Memory Pool Tests ==="
	$(BIN_DIR)/memory_pool

test-network: $(NET_TARGETS)
	@echo "=== Starting Network Tests ==="
	@echo "Starting server in background..."
	$(BIN_DIR)/udp_server &
	@sleep 1
	@echo "Running client tests..."
	-$(BIN_DIR)/udp_client
	@echo "Stopping server..."
	@pkill -f udp_server || true

# Run all tests
test: test-basic test-orderbook test-memory
	@echo "=== All local tests completed ==="

# Run all tests including network
test-all: test test-network
	@echo "=== All tests completed ==="

# Benchmark runner
run-benchmarks: benchmarks
	@echo "=== Running All Benchmarks ==="
	@echo "\n--- Basic Latency ---"
	$(BIN_DIR)/basic_latency
	@echo "\n--- Order Book ---"
	$(BIN_DIR)/orderbook_latency
	@echo "\n--- Memory Pool ---"
	$(BIN_DIR)/memory_pool

# Performance analysis with perf
perf-basic: $(BIN_DIR)/basic_latency
	perf stat -e cycles,instructions,cache-misses,branch-misses $(BIN_DIR)/basic_latency

perf-orderbook: $(BIN_DIR)/orderbook_latency
	perf stat -e cycles,instructions,cache-misses,branch-misses $(BIN_DIR)/orderbook_latency

perf-memory: $(BIN_DIR)/memory_pool
	perf stat -e cycles,instructions,cache-misses,branch-misses $(BIN_DIR)/memory_pool

# Clean
clean:
	@echo "Cleaning..."
	rm -rf $(BUILD_DIR) $(BIN_DIR)

# Install dependencies (optional)
install-deps:
	@echo "Checking for required tools..."
	@which g++ > /dev/null || echo "g++ not found, please install build-essential"
	@which perf > /dev/null || echo "perf not found, please install linux-tools-generic"

# Demo - 展示所有功能
demo: all
	@echo "=================================="
	@echo "    HFT 延遲測試演示"
	@echo "=================================="
	@echo ""
	@echo "1. 基礎延遲測試..."
	@$(BIN_DIR)/basic_latency map | head -20
	@echo ""
	@echo "2. 訂單簿測試..."
	@$(BIN_DIR)/orderbook_latency ops | head -20
	@echo ""
	@echo "3. 記憶體池測試..."
	@$(BIN_DIR)/memory_pool strategies | head -20
	@echo ""
	@echo "完整測試請運行: make test-all"

# 快速測試 - 只運行最重要的測試
quick-test: benchmarks
	@echo "=== 快速測試 ==="
	@$(BIN_DIR)/basic_latency timer
	@$(BIN_DIR)/orderbook_latency ops | grep -A 5 "Add Order"
	@$(BIN_DIR)/memory_pool strategies | grep -A 5 "Memory Pool"

# 驗證編譯
verify: clean
	@echo "=== 驗證所有目標編譯 ==="
	@$(MAKE) all > /dev/null 2>&1 && echo "✓ 標準編譯成功" || echo "✗ 標準編譯失敗"
	@$(MAKE) clean > /dev/null 2>&1
	@$(MAKE) debug > /dev/null 2>&1 && echo "✓ Debug 編譯成功" || echo "✗ Debug 編譯失敗"
	@$(MAKE) clean > /dev/null 2>&1
	@$(MAKE) profile > /dev/null 2>&1 && echo "✓ Profile 編譯成功" || echo "✗ Profile 編譯失敗"
	@echo "=== 編譯驗證完成 ==="

# Help - 詳細使用說明
help:
	@echo "╔══════════════════════════════════════════════════════════════════╗"
	@echo "║           HFT Latency Testing Suite - 使用指南                    ║"
	@echo "╚══════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "【基本命令】"
	@echo "  make all              編譯所有測試程式"
	@echo "  make clean            清理編譯產物"
	@echo "  make help             顯示此幫助訊息"
	@echo ""
	@echo "【編譯選項】"
	@echo "  make benchmarks       只編譯基準測試"
	@echo "  make network          只編譯網路測試"
	@echo "  make memory           只編譯記憶體測試"
	@echo "  make debug            Debug 模式編譯（含符號表）"
	@echo "  make profile          性能分析模式編譯（支援 gprof）"
	@echo ""
	@echo "【測試執行】"
	@echo "  make test             運行所有本地測試"
	@echo "  make test-all         運行所有測試（含網路）"
	@echo "  make test-basic       只測基礎延遲"
	@echo "  make test-orderbook   只測訂單簿"
	@echo "  make test-memory      只測記憶體池"
	@echo "  make test-network     只測網路延遲"
	@echo "  make quick-test       快速測試（精簡版）"
	@echo "  make demo             功能演示"
	@echo ""
	@echo "【性能分析】"
	@echo "  make perf-basic       分析基礎延遲效能"
	@echo "  make perf-orderbook   分析訂單簿效能"
	@echo "  make perf-memory      分析記憶體池效能"
	@echo "  make run-benchmarks   運行完整基準測試"
	@echo ""
	@echo "【驗證工具】"
	@echo "  make verify           驗證所有編譯選項"
	@echo "  make install-deps     檢查依賴項"
	@echo ""
	@echo "【單獨執行測試程式】"
	@echo "  基礎延遲測試："
	@echo "    ./bin/basic_latency           # 運行所有基礎測試"
	@echo "    ./bin/basic_latency map       # 只測 map vs unordered_map"
	@echo "    ./bin/basic_latency copy      # 只測 memcpy vs move"
	@echo "    ./bin/basic_latency alloc     # 只測記憶體分配"
	@echo "    ./bin/basic_latency timer     # 只測計時器開銷"
	@echo ""
	@echo "  訂單簿測試："
	@echo "    ./bin/orderbook_latency       # 運行所有訂單簿測試"
	@echo "    ./bin/orderbook_latency ops   # 只測訂單操作"
	@echo "    ./bin/orderbook_latency match # 只測撮合模擬"
	@echo "    ./bin/orderbook_latency stress # 只測壓力測試"
	@echo ""
	@echo "  記憶體池測試："
	@echo "    ./bin/memory_pool             # 運行所有記憶體測試"
	@echo "    ./bin/memory_pool strategies  # 只測分配策略"
	@echo "    ./bin/memory_pool patterns    # 只測分配模式"
	@echo "    ./bin/memory_pool cache       # 只測緩存效應"
	@echo ""
	@echo "  網路測試："
	@echo "    ./bin/udp_server [port]       # 啟動 UDP 伺服器"
	@echo "    ./bin/udp_client [ip] [port]  # 運行 UDP 客戶端測試"
	@echo ""
	@echo "【使用範例】"
	@echo "  1. 完整測試流程："
	@echo "     make clean && make all && make test-all"
	@echo ""
	@echo "  2. Debug 模式測試："
	@echo "     make debug && gdb ./bin/basic_latency"
	@echo ""
	@echo "  3. 性能分析："
	@echo "     make profile && ./bin/basic_latency && gprof ./bin/basic_latency"
	@echo ""
	@echo "  4. 網路延遲測試："
	@echo "     終端1: ./bin/udp_server"
	@echo "     終端2: ./bin/udp_client localhost 9000"
	@echo ""
	@echo "【注意事項】"
	@echo "  • 需要 g++ 支援 C++17"
	@echo "  • 網路測試需要兩個終端"
	@echo "  • 性能測試建議在低負載環境運行"
	@echo "  • 使用 sudo 可啟用更多優化（huge pages、CPU governor）"

.PHONY: all benchmarks network memory debug profile test test-all test-basic test-orderbook test-memory test-network run-benchmarks clean install-deps help perf-basic perf-orderbook perf-memory demo quick-test verify