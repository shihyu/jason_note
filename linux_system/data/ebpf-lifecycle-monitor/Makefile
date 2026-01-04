# 工具鏈定義
CLANG ?= clang
BPFTOOL ?= bpftool
GCC ?= g++
CC ?= gcc
ARCH := $(shell uname -m | sed 's/x86_64/x86/' | sed 's/aarch64/arm64/' | sed 's/ppc64le/powerpc/' | sed 's/mips.*/mips/')

# 路徑定義
SRC_DIR := src
BPF_DIR := bpf
DIST_DIR := dist
TEST_DIR := tests

# 輸出檔案
TARGET := $(DIST_DIR)/monitor
BPF_OBJ := $(BPF_DIR)/monitor.bpf.o
BPF_SKEL := $(SRC_DIR)/monitor.skel.h
VMLINUX := $(BPF_DIR)/vmlinux.h
TEST_OOM := $(DIST_DIR)/oom_trigger

# 預設目標
.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build   - 編譯專案 (BPF + C++ Backend)"
	@echo "  make run     - 執行監控程式 (自動清理 Port 8080)"
	@echo "  make test    - 編譯並執行 OOM 觸發測試"
	@echo "  make clean   - 清理建置產物"
	@echo ""
	@echo "使用範例："
	@echo "  make build"
	@echo "  make run"

# 確保輸出目錄存在
$(DIST_DIR):
	mkdir -p $(DIST_DIR)

# 1. 產生 vmlinux.h
$(VMLINUX):
	@echo "  GEN     $@"
	@$(BPFTOOL) btf dump file /sys/kernel/btf/vmlinux format c > $@

# 2. 編譯 BPF 程式
$(BPF_OBJ): $(VMLINUX) $(BPF_DIR)/monitor.bpf.c
	@echo "  BPF     $@"
	@$(CLANG) -g -O2 -target bpf -D__TARGET_ARCH_$(ARCH) -I. -c $(BPF_DIR)/monitor.bpf.c -o $@

# 3. 產生 Skeleton Header
$(BPF_SKEL): $(BPF_OBJ)
	@echo "  GEN-SKEL $@"
	@$(BPFTOOL) gen skeleton $(BPF_OBJ) > $@

# 4. 編譯 C++ 使用者空間程式
$(TARGET): $(DIST_DIR) $(BPF_SKEL) $(SRC_DIR)/main.cpp $(SRC_DIR)/mongoose.c
	@echo "  CC      $@"
	@$(GCC) -std=c++17 -I $(SRC_DIR) -I $(BPF_DIR) -o $@ $(SRC_DIR)/main.cpp $(SRC_DIR)/mongoose.c -lbpf -lelf -lz

.PHONY: build
build: $(TARGET) ## 編譯專案

.PHONY: run
run: build ## 執行程式
	@echo "清理 port 8080..."
	@sudo lsof -ti:8080 | xargs -r sudo kill -9 2>/dev/null || true
	@echo "啟動 eBPF Monitor..."
	@cd $(DIST_DIR) && sudo ./monitor

.PHONY: test
test: $(DIST_DIR) ## 執行測試 (OOM Trigger)
	@echo "編譯測試工具..."
	@$(CC) $(TEST_DIR)/oom_trigger.c -o $(TEST_OOM)
	@echo "執行 OOM 觸發測試 (警告: 將消耗大量記憶體)..."
	@sudo $(TEST_OOM)

.PHONY: clean
clean: ## 清理
	@echo "  CLEAN"
	@rm -rf $(DIST_DIR)
	@rm -f $(BPF_OBJ) $(BPF_SKEL) $(VMLINUX)
	@rm -rf node_modules
	@rm -rf web/node_modules
	@rm -rf web/dist