# ARM NEON 測試專案 Makefile
# 目標平台：Android ARM64 (aarch64)

# 編譯器設定
NDK_HOME := /home/shihyu/android-ndk-r26d
CC := $(NDK_HOME)/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android26-clang
STRIP := $(NDK_HOME)/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-strip

# 編譯參數
CFLAGS := -O3 -march=armv8-a+simd -Wall -Wextra
# Android 15 (API 35) 需要 TLS 對齊至少 64 bytes
LDFLAGS := -Wl,-z,max-page-size=16384 -lm

# 目錄設定
SRC_DIR := .
BUILD_DIR := build/arm64-v8a
TEST_DIR := ../../tests
DEVICE_DIR := /data/local/tmp/neon_test

# 來源檔案
SOURCES := $(wildcard neon_test_*.c)
TARGETS := $(patsubst %.c,$(BUILD_DIR)/%,$(SOURCES))

# 預設目標
.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  ARM NEON 測試專案 - Makefile"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@echo "可用目標："
	@echo "  make setup    - 檢查 NDK 環境"
	@echo "  make build    - 編譯所有測試程式"
	@echo "  make deploy   - 透過 adb push 部署到裝置"
	@echo "  make run      - 在裝置上執行測試"
	@echo "  make test     - 執行完整測試流程 (build + deploy + run)"
	@echo "  make clean    - 清理建置產物"
	@echo "  make results  - 從裝置下載測試結果"
	@echo ""
	@echo "使用範例："
	@echo "  make test                    # 完整測試流程"
	@echo "  make build                   # 只編譯"
	@echo "  make deploy && make run      # 部署並執行"
	@echo ""
	@echo "編譯器資訊："
	@echo "  NDK: $(NDK_HOME)"
	@echo "  編譯器: aarch64-linux-android26-clang"
	@echo "  優化: -O3 -march=armv8-a+simd"
	@echo ""

.PHONY: setup
setup:  ## 檢查 NDK 環境
	@echo "檢查 Android NDK 環境..."
	@if [ ! -d "$(NDK_HOME)" ]; then \
		echo "❌ 錯誤：NDK_HOME 目錄不存在: $(NDK_HOME)"; \
		exit 1; \
	fi
	@if [ ! -f "$(CC)" ]; then \
		echo "❌ 錯誤：找不到編譯器: $(CC)"; \
		exit 1; \
	fi
	@echo "✅ NDK 環境正常"
	@$(CC) --version | head -n 1
	@echo ""
	@echo "檢查 adb 裝置連線..."
	@adb devices | grep -v "List" | grep "device" || (echo "❌ 錯誤：沒有連線的 Android 裝置"; exit 1)
	@echo "✅ 裝置已連線"
	@echo ""
	@echo "檢查裝置 CPU 特性..."
	@adb shell "cat /proc/cpuinfo | grep Features | head -n 1"

.PHONY: build
build: setup  ## 編譯所有測試程式
	@echo "開始編譯 ARM64 執行檔..."
	@mkdir -p $(BUILD_DIR) build/logs
	@for src in $(SOURCES); do \
		target=$$(basename $$src .c); \
		echo "  編譯 $$target..."; \
		$(CC) $(CFLAGS) -o $(BUILD_DIR)/$$target $$src $(LDFLAGS) 2>&1 | tee build/logs/$$target.log; \
		if [ $$? -eq 0 ]; then \
			$(STRIP) $(BUILD_DIR)/$$target; \
			echo "  ✅ $$target 編譯成功"; \
		else \
			echo "  ❌ $$target 編譯失敗"; \
			exit 1; \
		fi; \
	done
	@echo ""
	@echo "編譯完成！執行檔位於: $(BUILD_DIR)/"
	@ls -lh $(BUILD_DIR)/

.PHONY: deploy
deploy:  ## 透過 adb push 部署執行檔
	@echo "部署執行檔到裝置..."
	@adb shell "mkdir -p $(DEVICE_DIR)"
	@adb shell "mkdir -p $(DEVICE_DIR)/results"
	@for exe in $(BUILD_DIR)/*; do \
		if [ -f "$$exe" ] && [ -x "$$exe" ]; then \
			echo "  上傳 $$(basename $$exe)..."; \
			adb push $$exe $(DEVICE_DIR)/ > /dev/null 2>&1; \
			adb shell "chmod 755 $(DEVICE_DIR)/$$(basename $$exe)"; \
		fi; \
	done
	@echo "✅ 部署完成！"
	@echo ""
	@adb shell "ls -lh $(DEVICE_DIR)/"

.PHONY: run
run:  ## 在裝置上執行測試
	@echo "在裝置上執行測試程式..."
	@echo "════════════════════════════════════════"
	@for exe in $(BUILD_DIR)/*; do \
		if [ -f "$$exe" ] && [ -x "$$exe" ]; then \
			target=$$(basename $$exe); \
			echo ""; \
			echo "執行: $$target"; \
			echo "────────────────────────────────────────"; \
			adb shell "cd $(DEVICE_DIR) && ./$$target"; \
			echo ""; \
		fi; \
	done
	@echo "════════════════════════════════════════"
	@echo "✅ 所有測試執行完成！"

.PHONY: test
test: build deploy run  ## 執行完整測試流程

.PHONY: clean
clean:  ## 清理建置產物和臨時檔案
	@echo "清理本地建置產物..."
	rm -rf $(BUILD_DIR)/*
	rm -rf build/logs/*
	@echo "清理裝置上的測試檔案..."
	adb shell "rm -rf $(DEVICE_DIR)" 2>/dev/null || true
	@echo "✅ 清理完成！"

.PHONY: results
results:  ## 從裝置下載測試結果
	@echo "從裝置下載測試結果..."
	@mkdir -p $(TEST_DIR)/results
	adb pull $(DEVICE_DIR)/results/ $(TEST_DIR)/results/ 2>/dev/null || echo "⚠️  裝置上沒有結果檔案"
	@echo "結果已下載到: $(TEST_DIR)/results/"

.PHONY: info
info:  ## 顯示編譯資訊
	@echo "專案資訊："
	@echo "  NDK Home: $(NDK_HOME)"
	@echo "  編譯器: $(CC)"
	@echo "  編譯參數: $(CFLAGS)"
	@echo "  連結參數: $(LDFLAGS)"
	@echo "  來源目錄: $(SRC_DIR)"
	@echo "  建置目錄: $(BUILD_DIR)"
	@echo "  裝置目錄: $(DEVICE_DIR)"
	@echo ""
	@echo "來源檔案:"
	@ls -1 $(SRC_DIR)/*.c 2>/dev/null || echo "  (尚未建立)"
