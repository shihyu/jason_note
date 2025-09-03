# Makefile for Flamegraph Examples
# 用於編譯和測試所有火焰圖範例程式

# 編譯器設定
CXX = g++
CXXFLAGS = -g -O2 -fno-omit-frame-pointer -Wall -Wextra
CXXFLAGS_OPT = -g -O3 -march=native -fno-omit-frame-pointer -Wall -Wextra
LDFLAGS_THREAD = -pthread

# 目標執行檔
TARGETS = cpu_intensive memory_allocation lock_contention hft_simulation
OPTIMIZED_TARGETS = cpu_intensive_opt hft_simulation_opt

# 所有目標
ALL_TARGETS = $(TARGETS) $(OPTIMIZED_TARGETS)

# 預設目標
.PHONY: all
all: $(ALL_TARGETS)
	@echo "✓ All targets built successfully!"

# CPU 密集型範例
cpu_intensive: cpu_intensive.cpp
	@echo "Building CPU intensive example..."
	$(CXX) $(CXXFLAGS) $< -o $@

cpu_intensive_opt: cpu_intensive.cpp
	@echo "Building optimized CPU intensive example..."
	$(CXX) $(CXXFLAGS_OPT) $< -o $@

# 記憶體分配範例
memory_allocation: memory_allocation.cpp
	@echo "Building memory allocation example..."
	$(CXX) $(CXXFLAGS) $< -o $@

# 鎖競爭範例
lock_contention: lock_contention.cpp
	@echo "Building lock contention example..."
	$(CXX) $(CXXFLAGS) $(LDFLAGS_THREAD) $< -o $@

# 高頻交易模擬
hft_simulation: hft_simulation.cpp
	@echo "Building HFT simulation..."
	$(CXX) $(CXXFLAGS) $< -o $@

hft_simulation_opt: hft_simulation.cpp
	@echo "Building optimized HFT simulation..."
	$(CXX) $(CXXFLAGS_OPT) $< -o $@

# 測試所有程式
.PHONY: test
test: all
	@echo "\n========== Testing All Examples =========="
	@echo "\n[1/5] Testing CPU intensive..."
	@./cpu_intensive | tail -n 2
	@echo "\n[2/5] Testing memory allocation..."
	@./memory_allocation | tail -n 1
	@echo "\n[3/5] Testing lock contention (bad mode)..."
	@./lock_contention bad | tail -n 2
	@echo "\n[4/5] Testing lock contention (atomic mode)..."
	@./lock_contention atomic | tail -n 2
	@echo "\n[5/5] Testing HFT simulation..."
	@./hft_simulation | tail -n 3
	@echo "\n✓ All tests passed successfully!"

# 效能測試
.PHONY: benchmark
benchmark: all
	@echo "\n========== Performance Benchmark =========="
	@echo "\n--- CPU Intensive Benchmark ---"
	@echo "Standard optimization (O2):"
	@time -f "  Time: %e seconds" ./cpu_intensive > /dev/null 2>&1
	@echo "Aggressive optimization (O3 + native):"
	@time -f "  Time: %e seconds" ./cpu_intensive_opt > /dev/null 2>&1
	@echo "\n--- Lock Contention Benchmark ---"
	@echo "Bad locking:"
	@./lock_contention bad | grep "Time:"
	@echo "Better locking:"
	@./lock_contention better | grep "Time:"
	@echo "Atomic operations:"
	@./lock_contention atomic | grep "Time:"
	@echo "\n--- HFT Simulation Benchmark ---"
	@echo "Standard optimization:"
	@./hft_simulation | grep "Average latency:" | tail -n 1
	@echo "Aggressive optimization:"
	@./hft_simulation_opt | grep "Average latency:" | tail -n 1

# 安裝 FlameGraph 工具
.PHONY: install-flamegraph
install-flamegraph:
	@if [ ! -d "FlameGraph" ]; then \
		echo "Installing FlameGraph tools..."; \
		git clone https://github.com/brendangregg/FlameGraph.git; \
		echo "✓ FlameGraph tools installed"; \
	else \
		echo "FlameGraph tools already installed"; \
	fi

# 生成火焰圖 (需要 perf 和 FlameGraph)
.PHONY: flamegraph-cpu
flamegraph-cpu: cpu_intensive install-flamegraph
	@echo "Generating CPU flamegraph..."
	@mkdir -p flamegraphs
	@echo "Note: This requires perf tools and may need sudo permission"
	@./cpu_intensive & PID=$$!; \
	sleep 1; \
	perf record -F 99 -p $$PID -g -o flamegraphs/cpu.data -- sleep 5 2>/dev/null || \
		(echo "Need sudo for perf" && sudo perf record -F 99 -p $$PID -g -o flamegraphs/cpu.data -- sleep 5); \
	wait $$PID; \
	perf script -i flamegraphs/cpu.data 2>/dev/null | \
		./FlameGraph/stackcollapse-perf.pl > flamegraphs/cpu.folded; \
	./FlameGraph/flamegraph.pl \
		--title="CPU Intensive Flamegraph" \
		--width=1400 \
		flamegraphs/cpu.folded > flamegraphs/cpu.svg
	@echo "✓ Flamegraph saved to flamegraphs/cpu.svg"

# 分析火焰圖數據
.PHONY: analyze
analyze: flamegraphs/cpu.folded
	@echo "Analyzing flamegraph data..."
	@python3 analyze_flamegraph.py flamegraphs/cpu.folded -n 10

# 執行比較腳本
.PHONY: compare
compare: cpu_intensive cpu_intensive_opt install-flamegraph
	@echo "Running performance comparison..."
	@./compare_performance.sh

# 清理編譯產物
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	@rm -f $(ALL_TARGETS)
	@rm -f baseline optimized
	@rm -rf flamegraphs/
	@rm -f *.data *.folded *.svg
	@echo "✓ Cleaned"

# 完整清理（包含 FlameGraph）
.PHONY: distclean
distclean: clean
	@echo "Removing FlameGraph tools..."
	@rm -rf FlameGraph/
	@echo "✓ Dist cleaned"

# 顯示幫助
.PHONY: help
help:
	@echo "Flamegraph Examples Makefile"
	@echo "============================"
	@echo ""
	@echo "Targets:"
	@echo "  make all              - Build all examples"
	@echo "  make test             - Test all examples"
	@echo "  make benchmark        - Run performance benchmarks"
	@echo "  make flamegraph-cpu   - Generate CPU flamegraph"
	@echo "  make analyze          - Analyze flamegraph data"
	@echo "  make compare          - Compare baseline vs optimized"
	@echo "  make clean            - Remove build artifacts"
	@echo "  make distclean        - Remove everything including tools"
	@echo "  make help             - Show this help message"
	@echo ""
	@echo "Individual targets:"
	@echo "  make cpu_intensive    - Build CPU intensive example"
	@echo "  make memory_allocation- Build memory allocation example"
	@echo "  make lock_contention  - Build lock contention example"
	@echo "  make hft_simulation   - Build HFT simulation"
	@echo ""
	@echo "Requirements:"
	@echo "  - g++ compiler"
	@echo "  - perf tools (for flamegraph generation)"
	@echo "  - python3 (for analysis)"
	@echo "  - git (for FlameGraph installation)"

# 設定預設目標
.DEFAULT_GOAL := help