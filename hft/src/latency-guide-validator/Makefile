# 低延遲技術指南驗證專案 Makefile

.DEFAULT_GOAL := help

# 編譯器設定
CXX := g++
CXXFLAGS := -O3 -march=native -mtune=native -std=c++17 -pthread -Wall -Wextra
SRC_DIR := src
BIN_DIR := bin
TEST_DIR := tests

# 測試程式
TESTS := rdtsc_test lockfree_test mempool_test cache_test branch_test
TEST_BINS := $(addprefix $(BIN_DIR)/, $(TESTS))

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標:"
	@echo "  make build   - 編譯所有測試程式"
	@echo "  make run     - 執行所有驗證測試"
	@echo "  make test    - 執行測試並生成報告"
	@echo "  make clean   - 清理建置產物"
	@echo ""
	@echo "單獨執行:"
	@echo "  make rdtsc      - 執行 RDTSC 測量驗證"
	@echo "  make lockfree   - 執行 Lock-Free Queue 驗證"
	@echo "  make mempool    - 執行 Memory Pool 驗證"
	@echo "  make cache      - 執行 Cache Alignment 驗證"
	@echo "  make branch     - 執行 Branch Prediction 驗證"

.PHONY: build
build: $(BIN_DIR) $(TEST_BINS)  ## 編譯所有測試程式

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BIN_DIR)/rdtsc_test: $(SRC_DIR)/rdtsc_test.cpp
	$(CXX) $(CXXFLAGS) $< -o $@

$(BIN_DIR)/lockfree_test: $(SRC_DIR)/lockfree_queue_test.cpp
	$(CXX) $(CXXFLAGS) $< -o $@

$(BIN_DIR)/mempool_test: $(SRC_DIR)/memory_pool_test.cpp
	$(CXX) $(CXXFLAGS) $< -o $@

$(BIN_DIR)/cache_test: $(SRC_DIR)/cache_alignment_test.cpp
	$(CXX) $(CXXFLAGS) $< -o $@

$(BIN_DIR)/branch_test: $(SRC_DIR)/branch_prediction_test.cpp
	$(CXX) $(CXXFLAGS) $< -o $@

.PHONY: run
run: build  ## 執行所有驗證測試
	@echo "============================================"
	@echo "  低延遲技術指南驗證測試"
	@echo "============================================"
	@echo ""
	@echo "=== [1/5] RDTSC 測量驗證 ==="
	@./$(BIN_DIR)/rdtsc_test
	@echo ""
	@echo "=== [2/5] Lock-Free Queue 驗證 ==="
	@./$(BIN_DIR)/lockfree_test
	@echo ""
	@echo "=== [3/5] Memory Pool 驗證 ==="
	@./$(BIN_DIR)/mempool_test
	@echo ""
	@echo "=== [4/5] Cache Alignment 驗證 ==="
	@./$(BIN_DIR)/cache_test
	@echo ""
	@echo "=== [5/5] Branch Prediction 驗證 ==="
	@./$(BIN_DIR)/branch_test
	@echo ""
	@echo "============================================"
	@echo "  所有測試完成"
	@echo "============================================"

.PHONY: test
test: run  ## 執行測試並生成報告
	@echo ""
	@echo "生成驗證報告到 $(TEST_DIR)/validation_report.md"
	@echo "執行: make run > $(TEST_DIR)/validation_output.tmp 2>&1"

.PHONY: rdtsc
rdtsc: $(BIN_DIR)/rdtsc_test  ## 執行 RDTSC 測量驗證
	@echo "=== RDTSC 測量驗證 ==="
	@./$(BIN_DIR)/rdtsc_test

.PHONY: lockfree
lockfree: $(BIN_DIR)/lockfree_test  ## 執行 Lock-Free Queue 驗證
	@echo "=== Lock-Free Queue 驗證 ==="
	@./$(BIN_DIR)/lockfree_test

.PHONY: mempool
mempool: $(BIN_DIR)/mempool_test  ## 執行 Memory Pool 驗證
	@echo "=== Memory Pool 驗證 ==="
	@./$(BIN_DIR)/mempool_test

.PHONY: cache
cache: $(BIN_DIR)/cache_test  ## 執行 Cache Alignment 驗證
	@echo "=== Cache Alignment 驗證 ==="
	@./$(BIN_DIR)/cache_test

.PHONY: branch
branch: $(BIN_DIR)/branch_test  ## 執行 Branch Prediction 驗證
	@echo "=== Branch Prediction 驗證 ==="
	@./$(BIN_DIR)/branch_test

.PHONY: clean
clean:  ## 清理建置產物
	rm -rf $(BIN_DIR)/*
	rm -f $(TEST_DIR)/*.tmp
	@echo "清理完成"
