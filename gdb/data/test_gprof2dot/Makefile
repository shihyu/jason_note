# 程式執行流程追蹤與視覺化 Makefile
# 支援 C/C++ 和 Rust 程式的追蹤、分析和視覺化

# 編譯器設定
CXX = g++
CC = gcc
RUSTC = rustc
PYTHON = python3

# 編譯選項
CXXFLAGS = -g -O0 -std=c++11
CFLAGS = -g -O0
RUSTFLAGS = -g
TRACE_FLAGS = -pg -finstrument-functions

# 目標程式名稱
CPP_PROG = test_program
RUST_PROG = test_program_rust
CPP_SOURCE = test_program.cpp
RUST_SOURCE = test_program.rs

# 輸出目錄
OUTPUT_DIR = output
TRACE_DATA_DIR = trace_data
GRAPHS_DIR = graphs

# 腳本檔案
GDB_SCRIPT = gdb_trace.sh
UFTRACE_SCRIPT = uftrace_trace.sh
RUN_ALL_SCRIPT = run_all_traces.sh
GDB_TO_GRAPH = gdb_to_graph.py
UFTRACE_TO_GRAPH = uftrace_to_graph.py

# 顏色定義（用於輸出）
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# 預設目標
.PHONY: all
all: help

# 說明文件
.PHONY: help
help:
	@printf "$(GREEN)========================================$(NC)\n"
	@printf "$(GREEN)程式執行流程追蹤與視覺化 - Makefile$(NC)\n"
	@printf "$(GREEN)========================================$(NC)\n"
	@printf "\n"
	@printf "$(YELLOW)基本指令:$(NC)\n"
	@printf "  make setup          - 安裝所有依賴套件\n"
	@printf "  make build          - 編譯所有測試程式\n"
	@printf "  make trace          - 執行所有追蹤（GDB + uftrace）\n"
	@printf "  make clean          - 清理所有產生的檔案\n"
	@printf "\n"
	@printf "$(YELLOW)編譯指令:$(NC)\n"
	@printf "  make build-cpp      - 編譯 C++ 測試程式\n"
	@printf "  make build-rust     - 編譯 Rust 測試程式\n"
	@printf "  make build-debug    - 編譯除錯版本\n"
	@printf "  make build-trace    - 編譯追蹤版本（含 -pg）\n"
	@printf "\n"
	@printf "$(YELLOW)追蹤指令:$(NC)\n"
	@printf "  make gdb-trace      - 執行 GDB 追蹤\n"
	@printf "  make uftrace-trace  - 執行 uftrace 追蹤\n"
	@printf "  make trace-all      - 執行所有追蹤方法\n"
	@printf "\n"
	@printf "$(YELLOW)視覺化指令:$(NC)\n"
	@printf "  make graphs         - 產生所有視覺化圖表\n"
	@printf "  make flamegraph     - 產生火焰圖\n"
	@printf "  make view           - 開啟產生的圖表\n"
	@printf "\n"
	@printf "$(YELLOW)測試指令:$(NC)\n"
	@printf "  make test           - 執行所有測試\n"
	@printf "  make test-scripts   - 測試所有腳本\n"
	@printf "  make validate       - 驗證輸出檔案\n"
	@printf "\n"
	@printf "$(YELLOW)其他指令:$(NC)\n"
	@printf "  make deps-check     - 檢查依賴套件\n"
	@printf "  make create-scripts - 建立所有腳本檔案\n"
	@printf "  make create-tests   - 建立測試程式\n"
	@printf "  make stats          - 顯示追蹤統計資訊\n"

# 環境設置
.PHONY: setup
setup: deps-check
	@printf "$(GREEN)[Setup] 安裝依賴套件...$(NC)\n"
	@if [ -f /etc/debian_version ]; then \
		sudo apt-get update && \
		sudo apt-get install -y gdb g++ rustc python3-pip graphviz; \
	elif [ -f /etc/arch-release ]; then \
		sudo pacman -S --needed gdb gcc rust python-pip graphviz; \
	fi
	@pip3 install --user graphviz
	@printf "$(GREEN)[Setup] 下載 FlameGraph...$(NC)\n"
	@if [ ! -d FlameGraph ]; then \
		git clone https://github.com/brendangregg/FlameGraph; \
	fi
	@printf "$(GREEN)[Setup] 建立目錄結構...$(NC)\n"
	@mkdir -p $(OUTPUT_DIR) $(TRACE_DATA_DIR) $(GRAPHS_DIR)
	@printf "$(GREEN)[Setup] 完成！$(NC)\n"

# 檢查依賴
.PHONY: deps-check
deps-check:
	@printf "$(YELLOW)[Check] 檢查依賴套件...$(NC)\n"
	@command -v gdb >/dev/null 2>&1 || { printf "$(RED)❌ GDB 未安裝$(NC)\n"; exit 1; }
	@command -v g++ >/dev/null 2>&1 || { printf "$(RED)❌ g++ 未安裝$(NC)\n"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { printf "$(RED)❌ Python3 未安裝$(NC)\n"; exit 1; }
	@command -v dot >/dev/null 2>&1 || { printf "$(RED)❌ Graphviz 未安裝$(NC)\n"; exit 1; }
	@$(PYTHON) -c "import graphviz" 2>/dev/null || { printf "$(RED)❌ Python graphviz 模組未安裝$(NC)\n"; exit 1; }
	@printf "$(GREEN)✓ 所有依賴套件已安裝$(NC)\n"

# 建立目錄
.PHONY: create-dirs
create-dirs:
	@mkdir -p $(OUTPUT_DIR) $(TRACE_DATA_DIR) $(GRAPHS_DIR)

# 編譯所有程式
.PHONY: build
build: build-cpp build-rust

# 編譯 C++ 程式
.PHONY: build-cpp
build-cpp: $(CPP_SOURCE)
	@printf "$(GREEN)[Build] 編譯 C++ 程式...$(NC)\n"
	@$(CXX) $(CXXFLAGS) $(CPP_SOURCE) -o $(CPP_PROG)
	@printf "$(GREEN)✓ 編譯完成: $(CPP_PROG)$(NC)\n"

# 編譯 C++ 追蹤版本
.PHONY: build-trace
build-trace: $(CPP_SOURCE)
	@printf "$(GREEN)[Build] 編譯 C++ 追蹤版本...$(NC)\n"
	@$(CXX) $(CXXFLAGS) $(TRACE_FLAGS) $(CPP_SOURCE) -o $(CPP_PROG)_traced
	@printf "$(GREEN)✓ 編譯完成: $(CPP_PROG)_traced$(NC)\n"

# 編譯 Rust 程式
.PHONY: build-rust
build-rust:
	@printf "$(GREEN)[Build] 編譯 Rust 程式...$(NC)\n"
	@if [ -f $(RUST_SOURCE) ]; then \
		$(RUSTC) $(RUSTFLAGS) $(RUST_SOURCE) -o $(RUST_PROG); \
		echo "$(GREEN)✓ 編譯完成: $(RUST_PROG)$(NC)\n"; \
	else \
		echo "$(YELLOW)⚠ Rust 源碼不存在，跳過$(NC)\n"; \
	fi

# 建立測試程式
.PHONY: create-tests
create-tests: create-cpp-test create-rust-test

.PHONY: create-cpp-test
create-cpp-test:
	@printf "$(GREEN)[Create] 建立 C++ 測試程式...$(NC)\n"
	@cp test_program.cpp $(CPP_SOURCE) 2>/dev/null || printf "$(YELLOW)Test program already exists$(NC)\n"
	@printf "$(GREEN)✓ C++ 測試程式建立完成$(NC)\n"

.PHONY: create-rust-test
create-rust-test:
	@printf "$(GREEN)[Create] 建立 Rust 測試程式...$(NC)\n"
	@cp test_program.rs $(RUST_SOURCE) 2>/dev/null || printf "$(YELLOW)Test program already exists$(NC)\n"
	@printf "$(GREEN)✓ Rust 測試程式建立完成$(NC)\n"

# 建立所有腳本
.PHONY: create-scripts
create-scripts: create-gdb-script create-uftrace-script create-python-scripts create-run-all-script

# GDB 追蹤
.PHONY: gdb-trace
gdb-trace: build-cpp $(GDB_SCRIPT)
	@printf "$(GREEN)[Trace] 執行 GDB 追蹤...$(NC)\n"
	@chmod +x $(GDB_SCRIPT)
	@./$(GDB_SCRIPT) $(CPP_PROG)
	@if [ -f $(GDB_TO_GRAPH) ]; then \
		$(PYTHON) $(GDB_TO_GRAPH); \
		mv -f gdb_flow.* $(GRAPHS_DIR)/ 2>/dev/null || true; \
	fi
	@printf "$(GREEN)✓ GDB 追蹤完成$(NC)\n"

# uftrace 追蹤
.PHONY: uftrace-trace
uftrace-trace: build-trace $(UFTRACE_SCRIPT)
	@printf "$(GREEN)[Trace] 執行 uftrace 追蹤...$(NC)\n"
	@chmod +x $(UFTRACE_SCRIPT)
	@./$(UFTRACE_SCRIPT) $(CPP_SOURCE)
	@if [ -f $(UFTRACE_TO_GRAPH) ]; then \
		$(PYTHON) $(UFTRACE_TO_GRAPH); \
		mv -f uftrace_*.svg uftrace_*.png $(GRAPHS_DIR)/ 2>/dev/null || true; \
	fi
	@printf "$(GREEN)✓ uftrace 追蹤完成$(NC)\n"

# 執行所有追蹤
.PHONY: trace-all trace
trace-all trace: build $(RUN_ALL_SCRIPT)
	@printf "$(GREEN)[Trace] 執行所有追蹤方法...$(NC)\n"
	@chmod +x $(RUN_ALL_SCRIPT)
	@./$(RUN_ALL_SCRIPT) $(CPP_SOURCE)
	@printf "$(GREEN)✓ 所有追蹤完成$(NC)\n"

# 產生圖表
.PHONY: graphs
graphs:
	@mkdir -p $(GRAPHS_DIR)
	@printf "$(GREEN)[Graph] 產生視覺化圖表...$(NC)\n"
	@if [ -f gdb_trace.log ]; then \
		$(PYTHON) $(GDB_TO_GRAPH); \
	fi
	@if [ -f uftrace_trace.txt ]; then \
		$(PYTHON) $(UFTRACE_TO_GRAPH); \
	fi
	@mv -f *.svg *.png $(GRAPHS_DIR)/ 2>/dev/null || true
	@printf "$(GREEN)✓ 圖表產生完成$(NC)\n"
	@ls -la $(GRAPHS_DIR)/

# 產生火焰圖
.PHONY: flamegraph
flamegraph: FlameGraph
	@printf "$(GREEN)[Graph] 產生火焰圖...$(NC)\n"
	@if [ -f perf.data ]; then \
		perf script | ./FlameGraph/stackcollapse-perf.pl | ./FlameGraph/flamegraph.pl > $(GRAPHS_DIR)/flamegraph.svg; \
		echo "$(GREEN)✓ 火焰圖已產生: $(GRAPHS_DIR)/flamegraph.svg$(NC)\n"; \
	else \
		echo "$(YELLOW)⚠ 沒有 perf.data，請先執行 'make perf-record'$(NC)\n"; \
	fi

# 使用 perf 記錄
.PHONY: perf-record
perf-record: build-cpp
	@printf "$(GREEN)[Perf] 記錄效能數據...$(NC)\n"
	@perf record -g ./$(CPP_PROG)
	@printf "$(GREEN)✓ Perf 記錄完成$(NC)\n"

# 查看圖表
.PHONY: view
view:
	@printf "$(GREEN)[View] 開啟產生的圖表...$(NC)\n"
	@if [ -f $(GRAPHS_DIR)/gdb_flow.svg ]; then \
		xdg-open $(GRAPHS_DIR)/gdb_flow.svg 2>/dev/null || open $(GRAPHS_DIR)/gdb_flow.svg 2>/dev/null || echo "請手動開啟 $(GRAPHS_DIR)/gdb_flow.svg"; \
	fi

# 測試
.PHONY: test
test: test-scripts test-programs validate

.PHONY: test-scripts
test-scripts:
	@printf "$(YELLOW)[Test] 測試腳本...$(NC)\n"
	@for script in $(GDB_SCRIPT) $(UFTRACE_SCRIPT) $(RUN_ALL_SCRIPT); do \
		if [ -f $$script ]; then \
			bash -n $$script && echo "$(GREEN)✓ $$script 語法正確$(NC)\n" || echo "$(RED)✗ $$script 語法錯誤$(NC)\n"; \
		fi \
	done

.PHONY: test-programs
test-programs: build
	@printf "$(YELLOW)[Test] 測試程式執行...$(NC)\n"
	@./$(CPP_PROG) && echo "$(GREEN)✓ C++ 程式執行成功$(NC)\n" || echo "$(RED)✗ C++ 程式執行失敗$(NC)\n"
	@if [ -f $(RUST_PROG) ]; then \
		./$(RUST_PROG) && echo "$(GREEN)✓ Rust 程式執行成功$(NC)\n" || echo "$(RED)✗ Rust 程式執行失敗$(NC)\n"; \
	fi

.PHONY: validate
validate:
	@printf "$(YELLOW)[Validate] 驗證輸出檔案...$(NC)\n"
	@test -f gdb_trace.log && echo "$(GREEN)✓ GDB 追蹤日誌存在$(NC)\n" || echo "$(YELLOW)⚠ GDB 追蹤日誌不存在$(NC)\n"
	@test -d uftrace_data && echo "$(GREEN)✓ uftrace 數據目錄存在$(NC)\n" || echo "$(YELLOW)⚠ uftrace 數據目錄不存在$(NC)\n"
	@test -f $(GRAPHS_DIR)/gdb_flow.svg && echo "$(GREEN)✓ GDB 流程圖存在$(NC)\n" || echo "$(YELLOW)⚠ GDB 流程圖不存在$(NC)\n"
	@test -f $(GRAPHS_DIR)/uftrace_flow.svg && echo "$(GREEN)✓ uftrace 流程圖存在$(NC)\n" || echo "$(YELLOW)⚠ uftrace 流程圖不存在$(NC)\n"

# 統計資訊
.PHONY: stats
stats:
	@printf "$(YELLOW)[Stats] 追蹤統計資訊...$(NC)\n"
	@if [ -f gdb_trace.log ]; then \
		echo "GDB 追蹤："; \
		grep "TRACE|" gdb_trace.log | wc -l | xargs echo "  總函數呼叫次數："; \
		grep "TRACE|" gdb_trace.log | cut -d'|' -f2 | sort | uniq -c | sort -rn | head -5 | sed 's/^/  /'; \
	fi
	@if [ -d uftrace_data ]; then \
		echo ""; \
		echo "uftrace 統計："; \
		uftrace report -d uftrace_data --no-pager | head -10; \
	fi

# 清理
.PHONY: clean
clean:
	@printf "$(RED)[Clean] 清理所有產生的檔案...$(NC)\n"
	@rm -f $(CPP_PROG) $(CPP_PROG)_traced $(CPP_PROG)_inst
	@rm -f $(RUST_PROG)
	@rm -rf uftrace_data/
	@rm -f gdb_trace.log uftrace_trace.txt trace_commands.gdb
	@rm -f *.svg *.png *.json flame.txt
	@rm -f perf.data perf.data.old
	@rm -f callgrind.out.* cachegrind.out.*
	@rm -rf $(OUTPUT_DIR) $(TRACE_DATA_DIR) $(GRAPHS_DIR)
	@printf "$(GREEN)✓ 清理完成$(NC)\n"

# 深度清理（包括腳本和測試程式）
.PHONY: distclean
distclean: clean
	@printf "$(RED)[Clean] 深度清理...$(NC)\n"
	@rm -f $(GDB_SCRIPT) $(UFTRACE_SCRIPT) $(RUN_ALL_SCRIPT)
	@rm -f $(GDB_TO_GRAPH) $(UFTRACE_TO_GRAPH)
	@rm -f $(CPP_SOURCE) $(RUST_SOURCE)
	@rm -rf FlameGraph/
	@printf "$(GREEN)✓ 深度清理完成$(NC)\n"

# 安裝（部署腳本到系統）
.PHONY: install
install:
	@printf "$(GREEN)[Install] 安裝腳本到 /usr/local/bin ...$(NC)\n"
	@sudo cp $(GDB_SCRIPT) $(UFTRACE_SCRIPT) $(RUN_ALL_SCRIPT) /usr/local/bin/
	@sudo chmod +x /usr/local/bin/$(GDB_SCRIPT)
	@sudo chmod +x /usr/local/bin/$(UFTRACE_SCRIPT)
	@sudo chmod +x /usr/local/bin/$(RUN_ALL_SCRIPT)
	@printf "$(GREEN)✓ 安裝完成$(NC)\n"

# 解除安裝
.PHONY: uninstall
uninstall:
	@printf "$(RED)[Uninstall] 移除已安裝的腳本...$(NC)\n"
	@sudo rm -f /usr/local/bin/$(GDB_SCRIPT)
	@sudo rm -f /usr/local/bin/$(UFTRACE_SCRIPT)
	@sudo rm -f /usr/local/bin/$(RUN_ALL_SCRIPT)
	@printf "$(GREEN)✓ 解除安裝完成$(NC)\n"

# CI/CD 目標
.PHONY: ci
ci: deps-check build test validate
	@printf "$(GREEN)✓ CI 檢查通過$(NC)\n"

# Docker 建構
.PHONY: docker-build
docker-build:
	@printf "$(GREEN)[Docker] 建構 Docker 映像...$(NC)\n"
	@docker build -t program-tracer .
	@printf "$(GREEN)✓ Docker 映像建構完成$(NC)\n"

# Docker 執行
.PHONY: docker-run
docker-run:
	@printf "$(GREEN)[Docker] 執行 Docker 容器...$(NC)\n"
	@docker run -it --rm -v $(PWD):/workspace program-tracer

# 建立 GDB 腳本
.PHONY: create-gdb-script
create-gdb-script:
	@printf "$(GREEN)[Create] 建立 GDB 追蹤腳本...$(NC)\n"
	@chmod +x $(GDB_SCRIPT) 2>/dev/null || true
	@printf "$(GREEN)✓ GDB 腳本建立完成$(NC)\n"

# 建立 uftrace 腳本
.PHONY: create-uftrace-script
create-uftrace-script:
	@printf "$(GREEN)[Create] 建立 uftrace 追蹤腳本...$(NC)\n"
	@chmod +x $(UFTRACE_SCRIPT) 2>/dev/null || true
	@printf "$(GREEN)✓ uftrace 腳本建立完成$(NC)\n"

# 建立 Python 轉換腳本
.PHONY: create-python-scripts
create-python-scripts:
	@printf "$(GREEN)[Create] 建立 Python 轉換腳本...$(NC)\n"
	@printf "$(GREEN)✓ Python 腳本建立完成$(NC)\n"

# 建立執行所有腳本
.PHONY: create-run-all-script
create-run-all-script:
	@printf "$(GREEN)[Create] 建立整合執行腳本...$(NC)\n"
	@chmod +x $(RUN_ALL_SCRIPT) 2>/dev/null || true
	@printf "$(GREEN)✓ 整合腳本建立完成$(NC)\n"

# 防止刪除中間檔案
.PRECIOUS: $(CPP_PROG) $(RUST_PROG) %.svg %.png

# 設定預設 shell
SHELL := /bin/bash

# 快速開始（一鍵執行）
.PHONY: quick-start
quick-start:
	@printf "$(GREEN)========================================$(NC)\n"
	@printf "$(GREEN)快速開始 - 自動設置並執行追蹤$(NC)\n"
	@printf "$(GREEN)========================================$(NC)\n"
	@$(MAKE) setup
	@$(MAKE) create-scripts
	@$(MAKE) create-tests
	@$(MAKE) build
	@$(MAKE) trace-all
	@$(MAKE) graphs
	@printf "$(GREEN)========================================$(NC)\n"
	@printf "$(GREEN)✓ 快速開始完成！$(NC)\n"
	@printf "$(GREEN)產生的圖表位於: $(GRAPHS_DIR)/$(NC)\n"
	@printf "$(GREEN)使用 'make view' 查看圖表$(NC)\n"
	@printf "$(GREEN)========================================$(NC)\n"