# Google Benchmark 專案 Makefile
# ========================================

# 編譯器設定
CC = gcc
CXX = g++
CFLAGS = -O3 -Wall -Wextra -std=c11
CXXFLAGS = -O3 -Wall -Wextra -std=c++17
LDFLAGS = -lbenchmark -pthread

# 目錄設定
SRC_DIR = src
BENCH_DIR = benchmark
BUILD_DIR = build

# 顏色輸出設定
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

# 原始檔
C_SOURCES = $(wildcard $(SRC_DIR)/*.c)
C_OBJECTS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(C_SOURCES))

# 基準測試程式
BENCH_SOURCES = $(wildcard $(BENCH_DIR)/*.cpp)
BENCH_TARGETS = $(patsubst $(BENCH_DIR)/%.cpp,$(BUILD_DIR)/%,$(BENCH_SOURCES))

# 預設目標
.PHONY: all
all: info $(BUILD_DIR) $(BENCH_TARGETS)
	@echo "$(GREEN)✓ 編譯完成！$(NC)"
	@echo "$(BLUE)可執行檔位於 $(BUILD_DIR)/ 目錄$(NC)"

# 顯示專案資訊
.PHONY: info
info:
	@echo "$(BLUE)========================================$(NC)"
	@echo "$(BLUE)   Google Benchmark 測試專案$(NC)"
	@echo "$(BLUE)========================================$(NC)"
	@echo "$(YELLOW)編譯器: $(CC) (C), $(CXX) (C++)$(NC)"
	@echo "$(YELLOW)優化等級: -O3$(NC)"
	@echo ""

# 建立建構目錄
$(BUILD_DIR):
	@echo "$(YELLOW)→ 建立建構目錄 $(BUILD_DIR)/$(NC)"
	@mkdir -p $(BUILD_DIR)

# 編譯 C 原始檔
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	@echo "$(YELLOW)→ 編譯 C 檔案: $<$(NC)"
	@$(CC) $(CFLAGS) -c $< -o $@

# 編譯基本基準測試（純 C++）
$(BUILD_DIR)/test_basic_benchmark: $(BENCH_DIR)/test_basic_benchmark.cpp
	@echo "$(YELLOW)→ 建構基本基準測試: $@$(NC)"
	@$(CXX) $(CXXFLAGS) $< $(LDFLAGS) -o $@

# 編譯 C 語言基準測試（需要 C 物件檔）
$(BUILD_DIR)/test_c_benchmark: $(BENCH_DIR)/test_c_benchmark.cpp $(C_OBJECTS)
	@echo "$(YELLOW)→ 建構 C 語言基準測試: $@$(NC)"
	@$(CXX) $(CXXFLAGS) -I$(SRC_DIR) $< $(C_OBJECTS) $(LDFLAGS) -o $@

# 執行所有基準測試
.PHONY: benchmark
benchmark: all
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)   執行所有基準測試$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@for bench in $(BENCH_TARGETS); do \
		echo "$(BLUE)→ 執行 $$bench$(NC)"; \
		$$bench --benchmark_min_time=0.1s; \
		echo ""; \
	done

# 執行基本測試
.PHONY: test-basic
test-basic: $(BUILD_DIR)/test_basic_benchmark
	@echo "$(GREEN)執行基本基準測試$(NC)"
	@$(BUILD_DIR)/test_basic_benchmark --benchmark_min_time=0.1s

# 執行 C 語言測試
.PHONY: test-c
test-c: $(BUILD_DIR)/test_c_benchmark
	@echo "$(GREEN)執行 C 語言基準測試$(NC)"
	@$(BUILD_DIR)/test_c_benchmark --benchmark_min_time=0.1s

# 執行快速測試（只執行部分測試）
.PHONY: quick-test
quick-test: all
	@echo "$(GREEN)執行快速測試$(NC)"
	@$(BUILD_DIR)/test_basic_benchmark --benchmark_filter="BM_StringCreation|BM_Calculation" --benchmark_min_time=0.05s
	@echo ""
	@$(BUILD_DIR)/test_c_benchmark --benchmark_filter="BM_Fibonacci|BM_GCD" --benchmark_min_time=0.05s

# 列出所有測試
.PHONY: list-tests
list-tests: all
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)   所有可用的測試$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(BLUE)基本測試:$(NC)"
	@$(BUILD_DIR)/test_basic_benchmark --benchmark_list_tests
	@echo ""
	@echo "$(BLUE)C 語言測試:$(NC)"
	@$(BUILD_DIR)/test_c_benchmark --benchmark_list_tests

# 執行並輸出 JSON 格式
.PHONY: benchmark-json
benchmark-json: all
	@echo "$(GREEN)產生 JSON 格式報告$(NC)"
	@mkdir -p $(BUILD_DIR)/reports
	@for bench in $(BENCH_TARGETS); do \
		name=$$(basename $$bench); \
		echo "$(YELLOW)→ 產生 $$name.json$(NC)"; \
		$$bench --benchmark_format=json --benchmark_out=$(BUILD_DIR)/reports/$$name.json; \
	done
	@echo "$(GREEN)✓ JSON 報告已儲存至 $(BUILD_DIR)/reports/$(NC)"

# 執行並輸出 CSV 格式
.PHONY: benchmark-csv
benchmark-csv: all
	@echo "$(GREEN)產生 CSV 格式報告$(NC)"
	@mkdir -p $(BUILD_DIR)/reports
	@for bench in $(BENCH_TARGETS); do \
		name=$$(basename $$bench); \
		echo "$(YELLOW)→ 產生 $$name.csv$(NC)"; \
		$$bench --benchmark_format=csv --benchmark_out=$(BUILD_DIR)/reports/$$name.csv; \
	done
	@echo "$(GREEN)✓ CSV 報告已儲存至 $(BUILD_DIR)/reports/$(NC)"

# 效能分析（詳細統計）
.PHONY: profile
profile: all
	@echo "$(GREEN)執行詳細效能分析$(NC)"
	@for bench in $(BENCH_TARGETS); do \
		echo "$(BLUE)→ 分析 $$bench$(NC)"; \
		$$bench --benchmark_repetitions=10 --benchmark_report_aggregates_only=true --benchmark_min_time=0.5s; \
		echo ""; \
	done

# 檢查記憶體洩漏（使用 valgrind）
.PHONY: memcheck
memcheck: all
	@echo "$(GREEN)檢查記憶體洩漏$(NC)"
	@command -v valgrind >/dev/null 2>&1 || { echo "$(RED)錯誤: 需要安裝 valgrind$(NC)"; exit 1; }
	@for bench in $(BENCH_TARGETS); do \
		echo "$(BLUE)→ 檢查 $$bench$(NC)"; \
		valgrind --leak-check=full --show-leak-kinds=all $$bench --benchmark_filter="BM_StringCreation" --benchmark_min_time=0.01s 2>&1 | grep -E "(definitely lost|ERROR SUMMARY)"; \
	done

# 清理建構檔案
.PHONY: clean
clean:
	@echo "$(YELLOW)→ 清理建構檔案$(NC)"
	@rm -rf $(BUILD_DIR)
	@rm -f test_basic_benchmark test_c_benchmark algorithms.o
	@echo "$(GREEN)✓ 清理完成$(NC)"

# 完整清理（包含報告）
.PHONY: distclean
distclean: clean
	@echo "$(YELLOW)→ 完整清理（包含報告）$(NC)"
	@rm -rf $(BUILD_DIR)/reports
	@echo "$(GREEN)✓ 完整清理完成$(NC)"

# 顯示說明
.PHONY: help
help:
	@echo "$(BLUE)========================================$(NC)"
	@echo "$(BLUE)   Google Benchmark Makefile 說明$(NC)"
	@echo "$(BLUE)========================================$(NC)"
	@echo ""
	@echo "$(YELLOW)可用的目標:$(NC)"
	@echo "  $(GREEN)make$(NC)              - 編譯所有程式"
	@echo "  $(GREEN)make benchmark$(NC)    - 執行所有基準測試"
	@echo "  $(GREEN)make test-basic$(NC)   - 只執行基本測試"
	@echo "  $(GREEN)make test-c$(NC)       - 只執行 C 語言測試"
	@echo "  $(GREEN)make quick-test$(NC)   - 執行快速測試（部分測試）"
	@echo "  $(GREEN)make list-tests$(NC)   - 列出所有可用的測試"
	@echo "  $(GREEN)make benchmark-json$(NC) - 產生 JSON 格式報告"
	@echo "  $(GREEN)make benchmark-csv$(NC)  - 產生 CSV 格式報告"
	@echo "  $(GREEN)make profile$(NC)      - 執行詳細效能分析"
	@echo "  $(GREEN)make memcheck$(NC)     - 檢查記憶體洩漏（需要 valgrind）"
	@echo "  $(GREEN)make clean$(NC)        - 清理建構檔案"
	@echo "  $(GREEN)make distclean$(NC)    - 完整清理（包含報告）"
	@echo "  $(GREEN)make help$(NC)         - 顯示此說明訊息"
	@echo ""
	@echo "$(YELLOW)範例:$(NC)"
	@echo "  make              # 編譯所有程式"
	@echo "  make benchmark    # 執行所有測試"
	@echo "  make quick-test   # 快速測試"
	@echo ""

# 偵錯模式編譯
.PHONY: debug
debug: CFLAGS = -g -O0 -Wall -Wextra -std=c11
debug: CXXFLAGS = -g -O0 -Wall -Wextra -std=c++17
debug: all
	@echo "$(GREEN)✓ 偵錯版本編譯完成$(NC)"

# 安裝檢查
.PHONY: check-deps
check-deps:
	@echo "$(BLUE)檢查相依套件...$(NC)"
	@command -v $(CC) >/dev/null 2>&1 && echo "$(GREEN)✓ $(CC) 已安裝$(NC)" || echo "$(RED)✗ $(CC) 未安裝$(NC)"
	@command -v $(CXX) >/dev/null 2>&1 && echo "$(GREEN)✓ $(CXX) 已安裝$(NC)" || echo "$(RED)✗ $(CXX) 未安裝$(NC)"
	@command -v make >/dev/null 2>&1 && echo "$(GREEN)✓ make 已安裝$(NC)" || echo "$(RED)✗ make 未安裝$(NC)"
	@echo "$(BLUE)檢查 Google Benchmark...$(NC)"
	@echo '#include <benchmark/benchmark.h>' | $(CXX) -x c++ -E - >/dev/null 2>&1 && \
		echo "$(GREEN)✓ Google Benchmark 已安裝$(NC)" || \
		echo "$(RED)✗ Google Benchmark 未安裝（請參考 README 安裝）$(NC)"

.PHONY: install-benchmark
install-benchmark:
	@echo "$(BLUE)安裝 Google Benchmark...$(NC)"
	@echo "$(YELLOW)請執行以下指令:$(NC)"
	@echo "git clone https://github.com/google/benchmark.git"
	@echo "cd benchmark"
	@echo "cmake -E make_directory build"
	@echo "cmake -E chdir build cmake -DBENCHMARK_DOWNLOAD_DEPENDENCIES=on -DCMAKE_BUILD_TYPE=Release ../"
	@echo "cmake --build build --config Release"
	@echo "sudo cmake --build build --config Release --target install"