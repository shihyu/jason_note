# seL4 QEMU + GDB 開發環境 Makefile
# 使用說明：
#   make init    - 初始化專案（首次使用，下載 seL4 原始碼）
#   make config  - 配置構建環境
#   make build   - 編譯 seL4 kernel 與 sel4test
#   make qemu    - 啟動 QEMU 運行 seL4
#   make debug   - 啟動 QEMU + GDB server（在另一終端執行 make gdb）
#   make gdb     - 連線到 QEMU 的 GDB server
#   make clean   - 清理構建產物
#   make distclean - 完全清理（包含下載的原始碼）

# 變數定義
BUILD_DIR := tests/build
BUILD_TARGET := $(BUILD_DIR)/build-x86_64
PLATFORM := x86_64
SIMULATION := TRUE
BUILD_TYPE := Debug
IMAGE := $(BUILD_TARGET)/images/sel4test-driver-image-x86_64-pc99
KERNEL := $(BUILD_TARGET)/images/kernel-x86_64-pc99

# 顏色輸出
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: all init config build qemu debug gdb clean distclean help status

# 預設目標
all: build

# 顯示說明
help:
	@echo "$(GREEN)=== seL4 QEMU + GDB 開發環境 ===$(NC)"
	@echo ""
	@echo "$(YELLOW)可用目標：$(NC)"
	@echo "  make init      - 初始化專案（首次使用，下載 seL4 原始碼）"
	@echo "  make config    - 配置構建環境（CMake configure）"
	@echo "  make build     - 編譯 seL4 kernel 與 sel4test"
	@echo "  make qemu      - 啟動 QEMU 運行 seL4"
	@echo "  make debug     - 啟動 QEMU + GDB server"
	@echo "  make gdb       - 連線到 QEMU 的 GDB server"
	@echo "  make clean     - 清理構建產物"
	@echo "  make distclean - 完全清理（包含下載的原始碼）"
	@echo "  make status    - 顯示當前狀態"
	@echo ""
	@echo "$(YELLOW)GDB 除錯流程：$(NC)"
	@echo "  1. 終端 1: make debug    # 啟動 QEMU，等待 GDB 連線"
	@echo "  2. 終端 2: make gdb      # 連線 GDB，開始除錯"
	@echo ""

# 顯示狀態
status:
	@echo "$(GREEN)=== 專案狀態 ===$(NC)"
	@if [ -d "$(BUILD_DIR)/.repo" ]; then \
		echo "$(GREEN)✓$(NC) 專案已初始化"; \
	else \
		echo "$(RED)✗$(NC) 專案未初始化（執行 make init）"; \
	fi
	@if [ -f "$(BUILD_TARGET)/build.ninja" ]; then \
		echo "$(GREEN)✓$(NC) 構建已配置"; \
	else \
		echo "$(RED)✗$(NC) 構建未配置（執行 make config）"; \
	fi
	@if [ -f "$(IMAGE)" ]; then \
		echo "$(GREEN)✓$(NC) 映像檔已構建: $(IMAGE)"; \
	else \
		echo "$(RED)✗$(NC) 映像檔未構建（執行 make build）"; \
	fi

# 初始化專案（下載 seL4 原始碼）
init:
	@echo "$(GREEN)=== 初始化 seL4 專案 ===$(NC)"
	@if [ -d "$(BUILD_DIR)/.repo" ]; then \
		echo "$(YELLOW)專案已初始化，跳過$(NC)"; \
	else \
		echo "$(GREEN)建立測試目錄...$(NC)"; \
		mkdir -p tests/build tests/logs; \
		echo "*" > tests/.gitignore; \
		echo "$(GREEN)使用 repo 下載 seL4 原始碼...$(NC)"; \
		cd $(BUILD_DIR) && \
		repo init -u https://github.com/seL4/sel4test-manifest.git && \
		repo sync -j4; \
		echo "$(GREEN)✓ 初始化完成$(NC)"; \
	fi

# 配置構建環境
config: init
	@echo "$(GREEN)=== 配置構建環境 ===$(NC)"
	@if [ -f "$(BUILD_TARGET)/build.ninja" ]; then \
		echo "$(YELLOW)構建已配置，跳過（如需重新配置，先執行 make clean）$(NC)"; \
	else \
		echo "$(GREEN)建立構建目錄...$(NC)"; \
		mkdir -p $(BUILD_TARGET); \
		echo "$(GREEN)執行 CMake 配置...$(NC)"; \
		cd $(BUILD_TARGET) && \
		../init-build.sh \
			-DPLATFORM=$(PLATFORM) \
			-DSIMULATION=$(SIMULATION) \
			-DCMAKE_BUILD_TYPE=$(BUILD_TYPE) \
			2>&1 | tee ../../logs/cmake-config.log; \
		echo "$(GREEN)✓ 配置完成$(NC)"; \
	fi

# 編譯
build: config
	@echo "$(GREEN)=== 編譯 seL4 kernel 與 sel4test ===$(NC)"
	@cd $(BUILD_TARGET) && \
		ninja 2>&1 | tee ../../logs/ninja-build.log
	@echo "$(GREEN)✓ 構建完成$(NC)"
	@echo "$(GREEN)映像檔位置: $(IMAGE)$(NC)"

# 啟動 QEMU
qemu: build
	@echo "$(GREEN)=== 啟動 QEMU 運行 seL4 ===$(NC)"
	@echo "$(YELLOW)提示：按 Ctrl+A 然後按 X 退出 QEMU$(NC)"
	@cd $(BUILD_TARGET) && ./simulate

# 啟動 QEMU + GDB server
debug: build
	@echo "$(GREEN)=== 啟動 QEMU + GDB Server ===$(NC)"
	@echo "$(YELLOW)QEMU 將在 port 1234 等待 GDB 連線$(NC)"
	@echo "$(YELLOW)在另一個終端執行: make gdb$(NC)"
	@echo ""
	@cd $(BUILD_TARGET) && ./simulate -d

# 連線 GDB
gdb:
	@echo "$(GREEN)=== 啟動 GDB 並連線到 QEMU ===$(NC)"
	@if ! pgrep -f "qemu-system-x86_64.*sel4test.*-s -S" > /dev/null; then \
		echo "$(RED)錯誤: QEMU + GDB server 未運行$(NC)"; \
		echo "$(YELLOW)請先在另一個終端執行: make debug$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)連線到 localhost:1234...$(NC)"
	@echo "$(YELLOW)常用 GDB 命令：$(NC)"
	@echo "  break <function>  - 設定中斷點"
	@echo "  continue (c)      - 繼續執行"
	@echo "  step (s)          - 單步執行（進入函式）"
	@echo "  next (n)          - 單步執行（不進入函式）"
	@echo "  info registers    - 顯示暫存器"
	@echo "  backtrace (bt)    - 顯示呼叫堆疊"
	@echo "  quit              - 退出 GDB"
	@echo ""
	@cd $(BUILD_TARGET) && \
		gdb -ex "target remote :1234" \
		    -ex "source ../kernel/gdb-macros" \
		    images/sel4test-driver-image-x86_64-pc99

# 清理構建產物
clean:
	@echo "$(GREEN)=== 清理構建產物 ===$(NC)"
	@if [ -d "$(BUILD_DIR)" ]; then \
		echo "$(YELLOW)刪除構建目錄: $(BUILD_DIR)$(NC)"; \
		rm -rf $(BUILD_DIR); \
	fi
	@if [ -d "tests/logs" ]; then \
		echo "$(YELLOW)刪除日誌目錄: tests/logs$(NC)"; \
		rm -rf tests/logs; \
	fi
	@if [ -d "tests/{build,logs}" ]; then \
		echo "$(YELLOW)刪除錯誤目錄: tests/{build,logs}$(NC)"; \
		rm -rf "tests/{build,logs}"; \
	fi
	@echo "$(GREEN)✓ 清理完成$(NC)"

# 完全清理
distclean:
	@echo "$(RED)=== 完全清理（包含下載的原始碼）===$(NC)"
	@read -p "確定要刪除 tests/ 目錄嗎？[y/N] " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(YELLOW)刪除 tests/ 目錄...$(NC)"; \
		rm -rf tests/; \
		echo "$(GREEN)✓ 完全清理完成$(NC)"; \
	else \
		echo "$(YELLOW)取消操作$(NC)"; \
	fi
