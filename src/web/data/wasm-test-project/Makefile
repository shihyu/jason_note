# WASM 測試項目 Makefile
# 支援編譯、優化、測試和 GDB 調試

.PHONY: all clean build optimize test debug serve install-deps help

# 變量定義
PROJECT_NAME = wasm-test-project
PKG_DIR = pkg
WASM_FILE = $(PKG_DIR)/$(PROJECT_NAME)_bg.wasm
OPTIMIZED_WASM = $(PKG_DIR)/optimized.wasm
DEBUG_WASM = $(PKG_DIR)/debug.wasm
PORT = 8080

# 默認目標
all: clean build optimize test

# 清理生成文件
clean:
	@echo "🧹 清理舊文件..."
	rm -rf $(PKG_DIR)/
	rm -f *.wasm *.wat
	rm -f wasm_info.txt test_results.txt
	cargo clean

# 安裝依賴
install-deps:
	@echo "📦 安裝必要依賴..."
	# 檢查 Rust 工具鏈
	@which rustc > /dev/null || (echo "❌ 請先安裝 Rust" && exit 1)
	@which wasm-pack > /dev/null || (echo "⬇️ 安裝 wasm-pack..." && curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh)
	@which wasm-opt > /dev/null || (echo "⬇️ 請安裝 binaryen (wasm-opt)" && exit 1)
	@which gdb > /dev/null || (echo "⬇️ 請安裝 gdb" && exit 1)
	# 添加 WASM 目標
	rustup target add wasm32-unknown-unknown
	@echo "✅ 依賴安裝完成"

# 編譯 WASM (發布版)
build:
	@echo "🔨 編譯 WASM (Release)..."
	wasm-pack build --target web --out-dir $(PKG_DIR) --release
	@if [ -f $(WASM_FILE) ]; then \
		echo "✅ 編譯成功"; \
		ls -lh $(WASM_FILE); \
	else \
		echo "❌ 編譯失敗"; \
		exit 1; \
	fi

# 編譯 WASM (調試版)
build-debug:
	@echo "🔨 編譯 WASM (Debug)..."
	wasm-pack build --target web --out-dir $(PKG_DIR) --dev
	cp $(WASM_FILE) $(DEBUG_WASM)
	@echo "✅ 調試版編譯完成"
	@ls -lh $(DEBUG_WASM)

# 優化 WASM 文件
optimize: build
	@echo "⚡ 優化 WASM 文件..."
	@if [ ! -f $(WASM_FILE) ]; then \
		echo "❌ 找不到 WASM 文件，請先執行 make build"; \
		exit 1; \
	fi
	
	# 獲取原始大小
	@ORIGINAL_SIZE=$$(wc -c < $(WASM_FILE)); \
	echo "原始大小: $$ORIGINAL_SIZE bytes"; \
	
	# 執行優化
	wasm-opt -Oz --enable-bulk-memory --enable-sign-ext \
		-o $(OPTIMIZED_WASM) $(WASM_FILE); \
	
	# 計算優化效果
	@OPTIMIZED_SIZE=$$(wc -c < $(OPTIMIZED_WASM)); \
	REDUCTION=$$(($$ORIGINAL_SIZE - $$OPTIMIZED_SIZE)); \
	PERCENTAGE=$$(echo "scale=2; $$REDUCTION * 100 / $$ORIGINAL_SIZE" | bc); \
	echo "優化後大小: $$OPTIMIZED_SIZE bytes"; \
	echo "減少: $$REDUCTION bytes ($$PERCENTAGE%)"; \
	
	# 生成報告
	@echo "=== WASM 優化報告 ===" > wasm_info.txt; \
	echo "編譯時間: $$(date)" >> wasm_info.txt; \
	echo "原始大小: $$ORIGINAL_SIZE bytes" >> wasm_info.txt; \
	echo "優化大小: $$OPTIMIZED_SIZE bytes" >> wasm_info.txt; \
	echo "壓縮率: $$PERCENTAGE%" >> wasm_info.txt; \
	echo "✅ 優化完成，報告已保存到 wasm_info.txt"

# 測試 WASM 功能
test: optimize test-js

# JavaScript 測試
test-js:
	@echo "🧪 執行 JavaScript 測試..."
	@if [ ! -f $(OPTIMIZED_WASM) ]; then \
		echo "❌ 找不到優化的 WASM 文件，請先執行 make optimize"; \
		exit 1; \
	fi
	node test.js > test_results.txt 2>&1 || true
	@echo "📊 測試結果已保存到 test_results.txt"
	@cat test_results.txt

# WASM 文件分析
analyze:
	@echo "🔍 分析 WASM 文件..."
	@if [ -f $(OPTIMIZED_WASM) ]; then \
		echo "=== 文件結構 ==="; \
		wasm-objdump -h $(OPTIMIZED_WASM); \
		echo ""; \
		echo "=== 導出函數 ==="; \
		wasm-objdump -j Export $(OPTIMIZED_WASM); \
		echo ""; \
		echo "=== 文件驗證 ==="; \
		wasm-validate $(OPTIMIZED_WASM) && echo "✅ 文件有效" || echo "❌ 文件無效"; \
	else \
		echo "❌ 找不到 WASM 文件，請先執行 make optimize"; \
	fi

# 轉換為 WAT 格式
to-wat:
	@echo "📝 轉換為 WAT 格式..."
	@if [ -f $(OPTIMIZED_WASM) ]; then \
		wasm2wat $(OPTIMIZED_WASM) -o optimized.wat; \
		echo "✅ 已轉換為 optimized.wat"; \
		wc -l optimized.wat; \
	else \
		echo "❌ 找不到 WASM 文件"; \
	fi

# GDB 調試準備
debug-setup: build-debug
	@echo "🐛 準備 GDB 調試環境..."
	@if [ -f $(DEBUG_WASM) ]; then \
		echo "✅ 調試版 WASM 已準備: $(DEBUG_WASM)"; \
		echo "📋 調試命令:"; \
		echo "  gdb --args node test-debug.js"; \
		echo "  或使用: make debug-gdb"; \
	else \
		echo "❌ 調試版 WASM 不存在"; \
	fi

# 啟動 GDB 調試
debug-gdb: debug-setup
	@echo "🚀 啟動 GDB 調試..."
	gdb --args node test-debug.js

# 啟動開發服務器
serve:
	@echo "🌐 啟動開發服務器 (端口 $(PORT))..."
	@if command -v python3 >/dev/null 2>&1; then \
		echo "使用 Python HTTP 服務器..."; \
		python3 -m http.server $(PORT); \
	elif command -v npx >/dev/null 2>&1; then \
		echo "使用 Node.js 服務器..."; \
		npx serve . -p $(PORT); \
	else \
		echo "❌ 請安裝 Python3 或 Node.js"; \
		exit 1; \
	fi

# 性能基準測試
benchmark: optimize
	@echo "⏱️ 執行性能基準測試..."
	node benchmark.js > benchmark_results.txt 2>&1
	@echo "📊 基準測試結果:"
	@cat benchmark_results.txt

# 完整測試套件
test-all: clean install-deps build optimize analyze test benchmark
	@echo "🎉 完整測試套件執行完成!"
	@echo "📁 生成的文件:"
	@ls -la *.txt *.wasm *.wat 2>/dev/null || true

# 幫助信息
help:
	@echo "WASM 測試項目 Makefile"
	@echo ""
	@echo "可用目標:"
	@echo "  all           - 執行完整構建流程 (clean + build + optimize + test)"
	@echo "  clean         - 清理生成文件"
	@echo "  install-deps  - 安裝必要依賴"
	@echo "  build         - 編譯 WASM (發布版)"
	@echo "  build-debug   - 編譯 WASM (調試版)"
	@echo "  optimize      - 優化 WASM 文件"
	@echo "  test          - 執行測試"
	@echo "  test-js       - 執行 JavaScript 測試"
	@echo "  analyze       - 分析 WASM 文件"
	@echo "  to-wat        - 轉換為 WAT 格式"
	@echo "  debug-setup   - 準備 GDB 調試環境"
	@echo "  debug-gdb     - 啟動 GDB 調試"
	@echo "  serve         - 啟動開發服務器"
	@echo "  benchmark     - 執行性能基準測試"
	@echo "  test-all      - 執行完整測試套件"
	@echo "  help          - 顯示此幫助信息"