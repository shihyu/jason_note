# ARM NEON 測試專案 Makefile
# 目標平台：Android ARM64 (aarch64) / QEMU ARM64

# ═══════════════════════════════════════════════════════════
# 編譯器設定
# ═══════════════════════════════════════════════════════════

# Android NDK 編譯器
NDK_HOME := /home/shihyu/android-ndk-r26d
NDK_CC := $(NDK_HOME)/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android26-clang
NDK_STRIP := $(NDK_HOME)/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-strip

# QEMU 交叉編譯器
QEMU_CC := aarch64-linux-gnu-gcc
QEMU_STRIP := aarch64-linux-gnu-strip
QEMU_RUNNER := qemu-aarch64-static

# x86_64 原生編譯器 (效能基準)
NATIVE_CC := gcc

# 編譯參數
CFLAGS := -O3 -march=armv8-a+simd -Wall -Wextra
# Android 15 (API 35) 需要 TLS 對齊至少 64 bytes
LDFLAGS_ANDROID := -Wl,-z,max-page-size=16384 -lm
# QEMU 使用靜態連結避免動態庫問題
LDFLAGS_QEMU := -static -lm
# 原生版本
LDFLAGS_NATIVE := -lm

# 目錄設定
SRC_DIR := .
BUILD_DIR_ANDROID := build/arm64-v8a
BUILD_DIR_QEMU := build/qemu-arm64
BUILD_DIR_NATIVE := build/x86_64
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
	@echo "【QEMU 測試流程】"
	@echo "  make setup-qemu     - 檢查 QEMU 環境"
	@echo "  make build-qemu     - 編譯 ARM64 版本 (QEMU)"
	@echo "  make test-qemu      - 使用 QEMU 執行測試"
	@echo "  make build-x86      - 編譯 x86_64 版本 (效能基準)"
	@echo "  make test-x86       - 執行 x86_64 版本測試"
	@echo ""
	@echo "【Android 實機測試】"
	@echo "  make setup-android  - 檢查 NDK 和 ADB 環境"
	@echo "  make build-android  - 編譯 Android 版本"
	@echo "  make deploy         - 透過 adb push 部署到裝置"
	@echo "  make run-android    - 在裝置上執行測試"
	@echo "  make test-android   - Android 完整測試流程"
	@echo ""
	@echo "【通用指令】"
	@echo "  make build          - 編譯所有版本 (QEMU + Android)"
	@echo "  make clean          - 清理建置產物"
	@echo "  make compare        - 比較測試結果"
	@echo ""
	@echo "使用範例："
	@echo "  make setup-qemu && make test-qemu    # QEMU 測試"
	@echo "  make test-android                    # Android 實機測試"
	@echo "  make build-qemu && make build-x86    # 編譯兩個版本"
	@echo ""

# ═══════════════════════════════════════════════════════════
# 環境檢查
# ═══════════════════════════════════════════════════════════

.PHONY: setup-qemu
setup-qemu:  ## 檢查 QEMU 環境
	@echo "檢查 QEMU 環境..."
	@command -v $(QEMU_CC) >/dev/null 2>&1 || { \
		echo "❌ 錯誤：找不到 $(QEMU_CC)"; \
		echo "   請執行: sudo apt-get install gcc-aarch64-linux-gnu"; \
		exit 1; \
	}
	@command -v $(QEMU_RUNNER) >/dev/null 2>&1 || { \
		echo "❌ 錯誤：找不到 $(QEMU_RUNNER)"; \
		echo "   請執行: sudo ./install_qemu.sh"; \
		echo "   或手動: sudo apt-get install qemu-user-static"; \
		exit 1; \
	}
	@echo "✅ QEMU 環境正常"
	@$(QEMU_CC) --version | head -n 1
	@$(QEMU_RUNNER) --version | head -n 1

.PHONY: setup-android
setup-android:  ## 檢查 Android NDK 環境
	@echo "檢查 Android NDK 環境..."
	@if [ ! -d "$(NDK_HOME)" ]; then \
		echo "❌ 錯誤：NDK_HOME 目錄不存在: $(NDK_HOME)"; \
		exit 1; \
	fi
	@if [ ! -f "$(NDK_CC)" ]; then \
		echo "❌ 錯誤：找不到編譯器: $(NDK_CC)"; \
		exit 1; \
	fi
	@echo "✅ NDK 環境正常"
	@$(NDK_CC) --version | head -n 1
	@echo ""
	@echo "檢查 adb 裝置連線..."
	@adb devices | grep -v "List" | grep "device" || (echo "❌ 錯誤：沒有連線的 Android 裝置"; exit 1)
	@echo "✅ 裝置已連線"
	@echo ""
	@echo "檢查裝置 CPU 特性..."
	@adb shell "cat /proc/cpuinfo | grep Features | head -n 1"

.PHONY: setup
setup: setup-android  ## 檢查 NDK 環境 (向後相容)

# ═══════════════════════════════════════════════════════════
# 編譯目標
# ═══════════════════════════════════════════════════════════

.PHONY: build-qemu
build-qemu: setup-qemu  ## 編譯 QEMU ARM64 版本
	@echo "開始編譯 QEMU ARM64 執行檔..."
	@mkdir -p $(BUILD_DIR_QEMU) build/logs
	@for src in $(SOURCES); do \
		target=$$(basename $$src .c); \
		echo "  編譯 $$target (QEMU)..."; \
		$(QEMU_CC) $(CFLAGS) -o $(BUILD_DIR_QEMU)/$$target $$src $(LDFLAGS_QEMU) 2>&1 | tee build/logs/$$target-qemu.log; \
		if [ $$? -eq 0 ]; then \
			$(QEMU_STRIP) $(BUILD_DIR_QEMU)/$$target; \
			echo "  ✅ $$target 編譯成功"; \
		else \
			echo "  ❌ $$target 編譯失敗"; \
			exit 1; \
		fi; \
	done
	@echo ""
	@echo "編譯完成！執行檔位於: $(BUILD_DIR_QEMU)/"
	@ls -lh $(BUILD_DIR_QEMU)/

.PHONY: build-x86
build-x86:  ## 編譯 x86_64 原生版本 (效能基準)
	@echo "開始編譯 x86_64 執行檔..."
	@mkdir -p $(BUILD_DIR_NATIVE) build/logs
	@for src in $(SOURCES); do \
		target=$$(basename $$src .c); \
		echo "  編譯 $$target (x86_64)..."; \
		$(NATIVE_CC) -O3 -Wall -Wextra -o $(BUILD_DIR_NATIVE)/$$target $$src $(LDFLAGS_NATIVE) 2>&1 | tee build/logs/$$target-x86.log; \
		if [ $$? -eq 0 ]; then \
			strip $(BUILD_DIR_NATIVE)/$$target; \
			echo "  ✅ $$target 編譯成功"; \
		else \
			echo "  ❌ $$target 編譯失敗 (可能因為 NEON intrinsics 不支援 x86)"; \
		fi; \
	done
	@echo ""
	@echo "編譯完成！執行檔位於: $(BUILD_DIR_NATIVE)/"
	@ls -lh $(BUILD_DIR_NATIVE)/ 2>/dev/null || true

.PHONY: build-android
build-android: setup-android  ## 編譯 Android 版本
	@echo "開始編譯 Android ARM64 執行檔..."
	@mkdir -p $(BUILD_DIR_ANDROID) build/logs
	@for src in $(SOURCES); do \
		target=$$(basename $$src .c); \
		echo "  編譯 $$target (Android)..."; \
		$(NDK_CC) $(CFLAGS) -o $(BUILD_DIR_ANDROID)/$$target $$src $(LDFLAGS_ANDROID) 2>&1 | tee build/logs/$$target-android.log; \
		if [ $$? -eq 0 ]; then \
			$(NDK_STRIP) $(BUILD_DIR_ANDROID)/$$target; \
			echo "  ✅ $$target 編譯成功"; \
		else \
			echo "  ❌ $$target 編譯失敗"; \
			exit 1; \
		fi; \
	done
	@echo ""
	@echo "編譯完成！執行檔位於: $(BUILD_DIR_ANDROID)/"
	@ls -lh $(BUILD_DIR_ANDROID)/

.PHONY: build
build: build-qemu build-android  ## 編譯所有版本 (QEMU + Android)

# ═══════════════════════════════════════════════════════════
# 測試執行
# ═══════════════════════════════════════════════════════════

.PHONY: test-qemu
test-qemu: build-qemu  ## 使用 QEMU 執行測試
	@echo "使用 QEMU 執行測試程式..."
	@mkdir -p $(TEST_DIR)/qemu_results
	@echo "════════════════════════════════════════" | tee $(TEST_DIR)/qemu_results/test_output.txt
	@echo "  QEMU ARM64 測試結果" | tee -a $(TEST_DIR)/qemu_results/test_output.txt
	@echo "  測試時間: $$(date '+%Y-%m-%d %H:%M:%S')" | tee -a $(TEST_DIR)/qemu_results/test_output.txt
	@echo "════════════════════════════════════════" | tee -a $(TEST_DIR)/qemu_results/test_output.txt
	@for exe in $(BUILD_DIR_QEMU)/*; do \
		if [ -f "$$exe" ] && [ -x "$$exe" ]; then \
			target=$$(basename $$exe); \
			echo "" | tee -a $(TEST_DIR)/qemu_results/test_output.txt; \
			echo "執行: $$target" | tee -a $(TEST_DIR)/qemu_results/test_output.txt; \
			echo "────────────────────────────────────────" | tee -a $(TEST_DIR)/qemu_results/test_output.txt; \
			$(QEMU_RUNNER) $$exe 2>&1 | tee -a $(TEST_DIR)/qemu_results/test_output.txt; \
			echo "" | tee -a $(TEST_DIR)/qemu_results/test_output.txt; \
		fi; \
	done
	@echo "════════════════════════════════════════" | tee -a $(TEST_DIR)/qemu_results/test_output.txt
	@echo "✅ 所有測試執行完成！" | tee -a $(TEST_DIR)/qemu_results/test_output.txt
	@echo ""
	@echo "測試結果已儲存到: $(TEST_DIR)/qemu_results/test_output.txt"

.PHONY: test-x86
test-x86: build-x86  ## 執行 x86_64 版本測試
	@echo "執行 x86_64 測試程式..."
	@mkdir -p $(TEST_DIR)/x86_results
	@echo "════════════════════════════════════════" | tee $(TEST_DIR)/x86_results/test_output.txt
	@echo "  x86_64 測試結果" | tee -a $(TEST_DIR)/x86_results/test_output.txt
	@echo "  測試時間: $$(date '+%Y-%m-%d %H:%M:%S')" | tee -a $(TEST_DIR)/x86_results/test_output.txt
	@echo "════════════════════════════════════════" | tee -a $(TEST_DIR)/x86_results/test_output.txt
	@for exe in $(BUILD_DIR_NATIVE)/*; do \
		if [ -f "$$exe" ] && [ -x "$$exe" ]; then \
			target=$$(basename $$exe); \
			echo "" | tee -a $(TEST_DIR)/x86_results/test_output.txt; \
			echo "執行: $$target" | tee -a $(TEST_DIR)/x86_results/test_output.txt; \
			echo "────────────────────────────────────────" | tee -a $(TEST_DIR)/x86_results/test_output.txt; \
			$$exe 2>&1 | tee -a $(TEST_DIR)/x86_results/test_output.txt || echo "⚠️ 測試失敗 (可能因為 NEON 不支援 x86)" | tee -a $(TEST_DIR)/x86_results/test_output.txt; \
			echo "" | tee -a $(TEST_DIR)/x86_results/test_output.txt; \
		fi; \
	done
	@echo "════════════════════════════════════════" | tee -a $(TEST_DIR)/x86_results/test_output.txt
	@echo "✅ 所有測試執行完成！" | tee -a $(TEST_DIR)/x86_results/test_output.txt
	@echo ""
	@echo "測試結果已儲存到: $(TEST_DIR)/x86_results/test_output.txt"

.PHONY: deploy
deploy:  ## 透過 adb push 部署執行檔
	@echo "部署執行檔到裝置..."
	@adb shell "mkdir -p $(DEVICE_DIR)"
	@adb shell "mkdir -p $(DEVICE_DIR)/results"
	@for exe in $(BUILD_DIR_ANDROID)/*; do \
		if [ -f "$$exe" ] && [ -x "$$exe" ]; then \
			echo "  上傳 $$(basename $$exe)..."; \
			adb push $$exe $(DEVICE_DIR)/ > /dev/null 2>&1; \
			adb shell "chmod 755 $(DEVICE_DIR)/$$(basename $$exe)"; \
		fi; \
	done
	@echo "✅ 部署完成！"
	@echo ""
	@adb shell "ls -lh $(DEVICE_DIR)/"

.PHONY: run-android
run-android:  ## 在 Android 裝置上執行測試
	@echo "在 Android 裝置上執行測試程式..."
	@mkdir -p $(TEST_DIR)/android_results
	@echo "════════════════════════════════════════" | tee $(TEST_DIR)/android_results/test_output.txt
	@echo "  Android 實機測試結果" | tee -a $(TEST_DIR)/android_results/test_output.txt
	@echo "  測試時間: $$(date '+%Y-%m-%d %H:%M:%S')" | tee -a $(TEST_DIR)/android_results/test_output.txt
	@echo "════════════════════════════════════════" | tee -a $(TEST_DIR)/android_results/test_output.txt
	@for exe in $(BUILD_DIR_ANDROID)/*; do \
		if [ -f "$$exe" ] && [ -x "$$exe" ]; then \
			target=$$(basename $$exe); \
			echo "" | tee -a $(TEST_DIR)/android_results/test_output.txt; \
			echo "執行: $$target" | tee -a $(TEST_DIR)/android_results/test_output.txt; \
			echo "────────────────────────────────────────" | tee -a $(TEST_DIR)/android_results/test_output.txt; \
			adb shell "cd $(DEVICE_DIR) && ./$$target" 2>&1 | tee -a $(TEST_DIR)/android_results/test_output.txt; \
			echo "" | tee -a $(TEST_DIR)/android_results/test_output.txt; \
		fi; \
	done
	@echo "════════════════════════════════════════" | tee -a $(TEST_DIR)/android_results/test_output.txt
	@echo "✅ 所有測試執行完成！" | tee -a $(TEST_DIR)/android_results/test_output.txt
	@echo ""
	@echo "測試結果已儲存到: $(TEST_DIR)/android_results/test_output.txt"

.PHONY: test-android
test-android: build-android deploy run-android  ## Android 完整測試流程

# ═══════════════════════════════════════════════════════════
# 結果比較與分析
# ═══════════════════════════════════════════════════════════

.PHONY: compare
compare:  ## 比較不同環境的測試結果
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  測試結果比較分析"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@echo "【QEMU ARM64 測試結果】"
	@echo "────────────────────────────────────────"
	@if [ -f "$(TEST_DIR)/qemu_results/test_output.txt" ]; then \
		cat $(TEST_DIR)/qemu_results/test_output.txt; \
	else \
		echo "⚠️  尚未執行 QEMU 測試，請先執行: make test-qemu"; \
	fi
	@echo ""
	@echo "【Android 實機測試結果】"
	@echo "────────────────────────────────────────"
	@if [ -f "$(TEST_DIR)/android_results/test_output.txt" ]; then \
		cat $(TEST_DIR)/android_results/test_output.txt; \
	else \
		echo "⚠️  尚未執行 Android 測試，請先執行: make test-android"; \
	fi
	@echo ""
	@echo "【x86_64 測試結果】"
	@echo "────────────────────────────────────────"
	@if [ -f "$(TEST_DIR)/x86_results/test_output.txt" ]; then \
		cat $(TEST_DIR)/x86_results/test_output.txt; \
	else \
		echo "⚠️  尚未執行 x86 測試，請先執行: make test-x86"; \
	fi
	@echo ""
	@echo "═══════════════════════════════════════════════════════════"

# ═══════════════════════════════════════════════════════════
# 清理與維護
# ═══════════════════════════════════════════════════════════

.PHONY: clean
clean:  ## 清理建置產物和臨時檔案
	@echo "清理本地建置產物..."
	rm -rf $(BUILD_DIR_ANDROID)/*
	rm -rf $(BUILD_DIR_QEMU)/*
	rm -rf $(BUILD_DIR_NATIVE)/*
	rm -rf build/logs/*
	@echo "清理測試結果..."
	rm -rf $(TEST_DIR)/qemu_results/*
	rm -rf $(TEST_DIR)/android_results/*
	rm -rf $(TEST_DIR)/x86_results/*
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
	@echo "  NDK 編譯器: $(NDK_CC)"
	@echo "  QEMU 編譯器: $(QEMU_CC)"
	@echo "  QEMU 執行器: $(QEMU_RUNNER)"
	@echo "  編譯參數: $(CFLAGS)"
	@echo "  來源目錄: $(SRC_DIR)"
	@echo "  建置目錄 (Android): $(BUILD_DIR_ANDROID)"
	@echo "  建置目錄 (QEMU): $(BUILD_DIR_QEMU)"
	@echo "  建置目錄 (x86): $(BUILD_DIR_NATIVE)"
	@echo "  測試目錄: $(TEST_DIR)"
	@echo "  裝置目錄: $(DEVICE_DIR)"
	@echo ""
	@echo "來源檔案:"
	@ls -1 $(SRC_DIR)/*.c 2>/dev/null || echo "  (尚未建立)"
