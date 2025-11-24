# Makefile for GDB Trace Examples
CC = gcc
CFLAGS = -g -Wall -Wextra
PROG = demo
SRC = demo.c

# 顏色定義
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

.PHONY: all clean help build test-basic test-python test-batch test-record analyze

all: build

# 編譯程式
build:
	@echo "$(GREEN)Building demo program...$(NC)"
	$(CC) $(CFLAGS) -o $(PROG) $(SRC)
	@echo "$(GREEN)Build complete!$(NC)"

# 方法一：基本 GDB 追蹤
test-basic: build
	@echo "$(YELLOW)Running Method 1: Basic GDB Trace$(NC)"
	@echo "----------------------------------------"
	gdb -x basic_trace/basic_trace.gdb ./$(PROG)
	@echo "$(GREEN)Output saved to: basic_trace.txt$(NC)"
	@echo ""

# 方法二：Python 腳本追蹤
test-python: build
	@echo "$(YELLOW)Running Method 2: Python Script Trace$(NC)"
	@echo "----------------------------------------"
	@echo "run" | gdb -x python_trace/trace.py \
		-ex "trace-start" \
		-ex "run" \
		-ex "trace-stop" \
		-ex "quit" ./$(PROG)
	@echo "$(GREEN)Output saved to: trace_log.txt$(NC)"
	@echo ""

# 方法三：批次命令追蹤
test-batch: build
	@echo "$(YELLOW)Running Method 3: Batch Command Trace$(NC)"
	@echo "----------------------------------------"
	gdb -x batch_trace/trace_commands.gdb ./$(PROG)
	@echo "$(GREEN)Output saved to: auto_trace.txt$(NC)"
	@echo ""

# 方法四：記錄/重播功能
test-record: build
	@echo "$(YELLOW)Running Method 4: Record/Replay$(NC)"
	@echo "----------------------------------------"
	@echo "Note: This may not work on all systems"
	gdb -x record_replay/record_replay.gdb ./$(PROG) || true
	@echo ""

# 執行所有測試
test-all: test-basic test-python test-batch
	@echo "$(GREEN)All tests completed!$(NC)"
	@echo "Generated trace files:"
	@ls -la *.txt 2>/dev/null || echo "No trace files generated yet"

# 分析追蹤結果
analyze:
	@echo "$(YELLOW)Analyzing trace results...$(NC)"
	@echo "----------------------------------------"
	@if [ -f trace_log.txt ]; then \
		python3 analysis_tools/analyze_trace.py trace_log.txt; \
	elif [ -f basic_trace.txt ]; then \
		python3 analysis_tools/analyze_trace.py basic_trace.txt; \
	elif [ -f auto_trace.txt ]; then \
		python3 analysis_tools/analyze_trace.py auto_trace.txt; \
	else \
		echo "No trace files found. Run 'make test-all' first."; \
	fi

# 執行程式（不含 GDB）
run: build
	@echo "$(YELLOW)Running demo program normally...$(NC)"
	@echo "----------------------------------------"
	./$(PROG)

# 使用 gprof 產生呼叫圖
profile: 
	@echo "$(YELLOW)Building with profiling support...$(NC)"
	$(CC) -pg -g -o $(PROG)_prof $(SRC)
	./$(PROG)_prof
	gprof $(PROG)_prof gmon.out > call_graph.txt
	@echo "$(GREEN)Call graph saved to: call_graph.txt$(NC)"

# 清理檔案
clean:
	@echo "$(YELLOW)Cleaning up...$(NC)"
	rm -f $(PROG) $(PROG)_prof
	rm -f *.txt
	rm -f gmon.out
	rm -f .gdb_history
	@echo "$(GREEN)Clean complete!$(NC)"

# 顯示說明
help:
	@echo "$(GREEN)GDB Trace Examples - Available Commands$(NC)"
	@echo "========================================"
	@echo "  make build      - Build the demo program"
	@echo "  make run        - Run demo program normally"
	@echo "  make test-basic - Run basic GDB trace (Method 1)"
	@echo "  make test-python- Run Python script trace (Method 2)"
	@echo "  make test-batch - Run batch command trace (Method 3)"
	@echo "  make test-record- Run record/replay demo (Method 4)"
	@echo "  make test-all   - Run all trace methods"
	@echo "  make analyze    - Analyze trace results"
	@echo "  make profile    - Generate call graph with gprof"
	@echo "  make clean      - Remove all generated files"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  1. make build"
	@echo "  2. make test-all"
	@echo "  3. make analyze"