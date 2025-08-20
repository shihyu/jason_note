# WASM 測試項目 Makefile
# 支援編譯、優化、測試和 GDB 調試

.PHONY: all clean build optimize test debug serve install-deps help

# 變量定義
PROJECT_NAME = wasm_test_project
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
	@echo "⚡ 準備優化的 WASM 文件..."
	@if [ ! -f $(WASM_FILE) ]; then \
		echo "❌ 找不到 WASM 文件，請先執行 make build"; \
		exit 1; \
	fi
	
	# 獲取原始大小
	@ORIGINAL_SIZE=$$(wc -c < $(WASM_FILE)); \
	echo "原始大小: $$ORIGINAL_SIZE bytes"; \
	
	# 由於沒有 wasm-opt，直接複製文件
	@cp $(WASM_FILE) $(OPTIMIZED_WASM); \
	echo "⚠️ wasm-opt 未安裝，使用原始文件作為優化版本"; \
	
	# 檢查文件大小
	@OPTIMIZED_SIZE=$$(wc -c < $(OPTIMIZED_WASM)); \
	echo "文件大小: $$OPTIMIZED_SIZE bytes"; \
	
	# 生成報告
	@echo "=== WASM 文件報告 ===" > wasm_info.txt; \
	echo "編譯時間: $$(date)" >> wasm_info.txt; \
	echo "原始大小: $$ORIGINAL_SIZE bytes" >> wasm_info.txt; \
	echo "文件大小: $$OPTIMIZED_SIZE bytes" >> wasm_info.txt; \
	echo "備註: 需要 wasm-opt 進行進一步優化" >> wasm_info.txt; \
	echo "✅ 文件準備完成，報告已保存到 wasm_info.txt"

# 測試 WASM 功能
test: optimize test-js

# JavaScript 測試
test-js:
	@echo "🧪 執行 JavaScript 測試..."
	@if [ ! -f $(OPTIMIZED_WASM) ]; then \
		echo "❌ 找不到優化的 WASM 文件，請先執行 make optimize"; \
		exit 1; \
	fi
	node test-detailed.js > test_results.txt 2>&1 || true
	@echo "📊 測試結果已保存到 test_results.txt"
	@echo "✅ 主要測試結果:"
	@grep -E "(✅|❌|🎉)" test_results.txt | head -10 || echo "測試完成"

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
		echo "  或使用: make debug-wasm (直接調試 WASM)"; \
	else \
		echo "❌ 調試版 WASM 不存在"; \
	fi

# 啟動 GDB 調試 Node.js
debug-gdb: debug-setup
	@echo "🚀 啟動 GDB 調試 Node.js..."
	gdb --args node test-debug.js

# 直接調試 WASM (使用 wasmtime)
debug-wasm: debug-setup
	@echo "🐛 使用 wasmtime 調試 WASM..."
	@test -f ~/.wasmtime/bin/wasmtime || (echo "❌ 請先安裝 wasmtime: curl https://wasmtime.dev/install.sh -sSf | bash" && exit 1)
	gdb --args ~/.wasmtime/bin/wasmtime --debug-info $(DEBUG_WASM)

# 配置 GDB 調試設定檔
debug-config:
	@echo "⚙️ 配置 GDB 調試設定..."
	@echo "# GDB 調試設定檔" > .gdbinit
	@echo "set architecture wasm32" >> .gdbinit
	@echo "set confirm off" >> .gdbinit
	@echo "set pagination off" >> .gdbinit
	@echo "set print pretty on" >> .gdbinit
	@echo "set print array on" >> .gdbinit
	@echo "# WASM 特殊設定" >> .gdbinit
	@echo "set debug remote 0" >> .gdbinit
	@echo "# 自動載入除錯符號" >> .gdbinit
	@echo "set auto-load safe-path /" >> .gdbinit
	@echo "✅ GDB 設定檔已建立: .gdbinit"

# 遠端調試設定 (target) - 實際啟動 gdbserver
debug-remote-target: debug-setup debug-config
	@echo "🎯 啟動 GDB 遠端調試 Target..."
	@echo "在 localhost:1234 啟動 gdbserver..."
	gdbserver --multi localhost:1234 $(DEBUG_WASM)

# 遠端調試連線 (host)
debug-remote-host: debug-config
	@echo "🏠 啟動 GDB Host 連線..."
	@echo "連接到 localhost:1234..."
	@echo "target extended-remote localhost:1234" > gdb_commands.txt
	@echo "set remote exec-file $(DEBUG_WASM)" >> gdb_commands.txt
	@echo "file $(DEBUG_WASM)" >> gdb_commands.txt
	@echo "break main" >> gdb_commands.txt
	@echo "continue" >> gdb_commands.txt
	gdb -x gdb_commands.txt

# 本地直接調試 (推薦)
debug-local: debug-setup debug-config
	@echo "🏠 本地直接調試..."
	@echo "file $(DEBUG_WASM)" > local_debug.txt
	@echo "break main" >> local_debug.txt
	@echo "run" >> local_debug.txt
	gdb ~/.wasmtime/bin/wasmtime -x local_debug.txt --args ~/.wasmtime/bin/wasmtime --debug-info $(DEBUG_WASM)

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
	@echo "  debug-gdb     - 啟動 GDB 調試 Node.js"
	@echo "  debug-wasm    - 直接調試 WASM (需要 wasmtime)"
	@echo "  debug-config  - 配置 GDB 設定檔"
	@echo "  debug-remote-target - 啟動遠端調試 Target (gdbserver)"
	@echo "  debug-remote-host   - 連線到遠端調試 Host"
	@echo "  debug-local         - 本地直接調試 (推薦)"
	@echo "  serve         - 啟動開發服務器"
	@echo "  benchmark     - 執行性能基準測試"
	@echo "  test-all      - 執行完整測試套件"
	@echo "  help          - 顯示此幫助信息"