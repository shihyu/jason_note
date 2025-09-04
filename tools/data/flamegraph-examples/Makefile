# Makefile for Flamegraph Examples
# 火焰圖範例程式的編譯和測試腳本

# ========== 編譯器設定 ==========
CXX = g++
# 標準編譯選項：
# -g：產生調試資訊
# -O2：第二級優化
# -fno-omit-frame-pointer：保留 frame pointer，這對生成火焰圖很重要
# -Wall -Wextra：開啟所有警告訊息
CXXFLAGS = -g -O2 -fno-omit-frame-pointer -Wall -Wextra
# 激進優化選項：
# -O3：第三級優化（更激進）
# -march=native：針對本機 CPU 架構優化
CXXFLAGS_OPT = -g -O3 -march=native -fno-omit-frame-pointer -Wall -Wextra
# 多執行緒連結選項
LDFLAGS_THREAD = -pthread

# ========== 目標執行檔定義 ==========
# 基本範例程式
TARGETS = cpu_intensive memory_allocation lock_contention hft_simulation
# 優化版本的程式
OPTIMIZED_TARGETS = cpu_intensive_opt hft_simulation_opt

# 合併所有目標
ALL_TARGETS = $(TARGETS) $(OPTIMIZED_TARGETS)

# ========== 主要編譯目標 ==========
# 預設目標：編譯所有程式
.PHONY: all
all: $(ALL_TARGETS)
	@echo "✓ 所有程式編譯成功！"

# ========== 個別程式編譯規則 ==========
# CPU 密集型範例（標準版）
cpu_intensive: cpu_intensive.cpp
	@echo "編譯 CPU 密集型範例..."
	$(CXX) $(CXXFLAGS) $< -o $@

# CPU 密集型範例（優化版）
cpu_intensive_opt: cpu_intensive.cpp
	@echo "編譯優化版 CPU 密集型範例..."
	$(CXX) $(CXXFLAGS_OPT) $< -o $@

# 記憶體分配範例
memory_allocation: memory_allocation.cpp
	@echo "編譯記憶體分配範例..."
	$(CXX) $(CXXFLAGS) $< -o $@

# 鎖競爭範例（需要 pthread）
lock_contention: lock_contention.cpp
	@echo "編譯鎖競爭範例..."
	$(CXX) $(CXXFLAGS) $(LDFLAGS_THREAD) $< -o $@

# 高頻交易模擬（標準版）
hft_simulation: hft_simulation.cpp
	@echo "編譯高頻交易模擬..."
	$(CXX) $(CXXFLAGS) $< -o $@

# 高頻交易模擬（優化版）
hft_simulation_opt: hft_simulation.cpp
	@echo "編譯優化版高頻交易模擬..."
	$(CXX) $(CXXFLAGS_OPT) $< -o $@

# ========== 測試功能 ==========
# 測試所有編譯好的程式
.PHONY: test
test: all
	@echo "\n========== 測試所有範例程式 =========="
	@echo "\n[1/5] 測試 CPU 密集型程式..."
	@./cpu_intensive | tail -n 2
	@echo "\n[2/5] 測試記憶體分配程式..."
	@./memory_allocation | tail -n 1
	@echo "\n[3/5] 測試鎖競爭（粗粒度鎖）..."
	@./lock_contention bad | tail -n 2
	@echo "\n[4/5] 測試鎖競爭（原子操作）..."
	@./lock_contention atomic | tail -n 2
	@echo "\n[5/5] 測試高頻交易模擬..."
	@./hft_simulation | tail -n 3
	@echo "\n✓ 所有測試完成！"

# ========== 效能基準測試 ==========
# 執行效能測試比較不同優化等級
.PHONY: benchmark
benchmark: all
	@echo "\n========== 效能基準測試 =========="
	@echo "\n--- CPU 密集型基準測試 ---"
	@echo "標準優化 (O2):"
	@time -f "  執行時間: %e 秒" ./cpu_intensive > /dev/null 2>&1
	@echo "激進優化 (O3 + native):"
	@time -f "  執行時間: %e 秒" ./cpu_intensive_opt > /dev/null 2>&1
	@echo "\n--- 鎖競爭基準測試 ---"
	@echo "粗粒度鎖:"
	@./lock_contention bad | grep "Time:"
	@echo "細粒度鎖:"
	@./lock_contention better | grep "Time:"
	@echo "原子操作:"
	@./lock_contention atomic | grep "Time:"
	@echo "\n--- 高頻交易模擬基準測試 ---"
	@echo "標準優化:"
	@./hft_simulation | grep "Average latency:" | tail -n 1
	@echo "激進優化:"
	@./hft_simulation_opt | grep "Average latency:" | tail -n 1

# ========== FlameGraph 工具安裝 ==========
# 下載並安裝 Brendan Gregg 的 FlameGraph 工具
.PHONY: install-flamegraph
install-flamegraph:
	@if [ ! -d "FlameGraph" ]; then \
		echo "正在安裝 FlameGraph 工具..."; \
		git clone https://github.com/brendangregg/FlameGraph.git; \
		echo "✓ FlameGraph 工具安裝完成"; \
	else \
		echo "FlameGraph 工具已經安裝"; \
	fi

# ========== 生成火焰圖 ==========
# 生成 CPU 火焰圖（需要 perf 和 FlameGraph）
.PHONY: flamegraph-cpu
flamegraph-cpu: cpu_intensive install-flamegraph
	@echo "正在生成 CPU 火焰圖..."
	@mkdir -p flamegraphs
	@echo "注意：需要 perf 工具，可能需要 sudo 權限"
	@# 啟動程式並在背景執行
	@./cpu_intensive & PID=$$!; \
	sleep 1; \
	# 使用 perf 收集效能數據（採樣頻率 99Hz，持續 5 秒）
	perf record -F 99 -p $$PID -g -o flamegraphs/cpu.data -- sleep 5 2>/dev/null || \
		(echo "需要 sudo 權限執行 perf" && sudo perf record -F 99 -p $$PID -g -o flamegraphs/cpu.data -- sleep 5); \
	wait $$PID; \
	# 將 perf 數據轉換為火焰圖格式
	perf script -i flamegraphs/cpu.data 2>/dev/null | \
		./FlameGraph/stackcollapse-perf.pl > flamegraphs/cpu.folded; \
	# 生成 SVG 火焰圖
	./FlameGraph/flamegraph.pl \
		--title="CPU 密集型程式火焰圖" \
		--width=1400 \
		flamegraphs/cpu.folded > flamegraphs/cpu.svg
	@echo "✓ 火焰圖已儲存至 flamegraphs/cpu.svg"

# ========== 分析火焰圖數據 ==========
# 使用 Python 腳本分析火焰圖數據
.PHONY: analyze
analyze: flamegraphs/cpu.folded
	@echo "分析火焰圖數據..."
	@python3 analyze_flamegraph.py flamegraphs/cpu.folded -n 10

# ========== 效能比較 ==========
# 執行基準版與優化版的效能比較
.PHONY: compare
compare: cpu_intensive cpu_intensive_opt install-flamegraph
	@echo "執行效能比較..."
	@./compare_performance.sh

# ========== 清理功能 ==========
# 清理編譯產物
.PHONY: clean
clean:
	@echo "清理編譯產物..."
	@rm -f $(ALL_TARGETS)
	@rm -f baseline optimized
	@rm -rf flamegraphs/
	@rm -f *.data *.folded *.svg
	@echo "✓ 清理完成"

# 完整清理（包含 FlameGraph 工具）
.PHONY: distclean
distclean: clean
	@echo "移除 FlameGraph 工具..."
	@rm -rf FlameGraph/
	@echo "✓ 完整清理完成"

# ========== 幫助訊息 ==========
# 顯示使用說明
.PHONY: help
help:
	@echo "火焰圖範例 Makefile 使用說明"
	@echo "============================"
	@echo ""
	@echo "主要目標："
	@echo "  make all              - 編譯所有範例程式"
	@echo "  make test             - 測試所有範例程式"
	@echo "  make benchmark        - 執行效能基準測試"
	@echo "  make flamegraph-cpu   - 生成 CPU 火焰圖"
	@echo "  make analyze          - 分析火焰圖數據"
	@echo "  make compare          - 比較基準版與優化版"
	@echo "  make clean            - 清理編譯產物"
	@echo "  make distclean        - 完整清理（含工具）"
	@echo "  make help             - 顯示此說明訊息"
	@echo ""
	@echo "個別程式編譯："
	@echo "  make cpu_intensive    - 編譯 CPU 密集型範例"
	@echo "  make memory_allocation- 編譯記憶體分配範例"
	@echo "  make lock_contention  - 編譯鎖競爭範例"
	@echo "  make hft_simulation   - 編譯高頻交易模擬"
	@echo ""
	@echo "系統需求："
	@echo "  - g++ 編譯器"
	@echo "  - perf 工具（生成火焰圖用）"
	@echo "  - python3（分析腳本用）"
	@echo "  - git（安裝 FlameGraph 用）"

# 設定預設目標為顯示幫助
.DEFAULT_GOAL := help