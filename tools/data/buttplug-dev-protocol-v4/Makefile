# Buttplug WASM Project Makefile with WebBluetooth Support
# 提供編譯、運行、清理功能，支援 WebBluetooth 設備配對和振動控制

.PHONY: all build run serve clean clean-all test dev install setup help

# 預設目標
all: build

# 變數定義
WASM_CRATE := crates/buttplug_server
PKG_DIR := $(WASM_CRATE)/pkg
EXAMPLE_DIR := example
FEATURES := wasm
PORT := 8000
DEV_PORT := 3000

# 檢查必要工具
check-tools:
	@echo "🔍 檢查必要工具..."
	@command -v wasm-pack >/dev/null 2>&1 || { echo "❌ wasm-pack 未安裝. 請執行: cargo install wasm-pack"; exit 1; }
	@command -v npm >/dev/null 2>&1 || { echo "❌ npm 未安裝"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "❌ python3 未安裝"; exit 1; }
	@echo "✅ 所有工具已就緒"

# 安裝依賴
install: check-tools
	@echo "📦 安裝依賴..."
	npm install
	cd $(EXAMPLE_DIR) && npm install
	@echo "✅ 依賴安裝完成"

# 編譯 WASM 模組
build-wasm:
	@echo "🚀 開始編譯 WASM 模組（支援 WebBluetooth）..."
	wasm-pack build --target web $(WASM_CRATE) --no-default-features --features $(FEATURES)
	@echo "✅ WASM 編譯完成！"

# 編譯 TypeScript
build-ts:
	@echo "📝 編譯 TypeScript..."
	npm run build:web
	@echo "✅ TypeScript 編譯完成"

# 複製 WASM 檔案到範例目錄
copy-wasm: build-wasm
	@echo "📂 複製 WASM 檔案到範例目錄..."
	mkdir -p $(EXAMPLE_DIR)/public/wasm
	cp $(PKG_DIR)/buttplug_server_bg.wasm $(EXAMPLE_DIR)/public/wasm/
	@echo "✅ WASM 檔案複製完成"

# 完整建構流程
build: install build-wasm build-ts copy-wasm
	@echo "🎉 建構完成！可以使用 WebBluetooth 功能進行設備配對和振動控制"

# 開發模式（自動重載）
dev: build
	@echo "🌐 啟動開發服務器（支援 WebBluetooth 設備控制）..."
	@echo "🔗 訪問: http://localhost:$(DEV_PORT)/"
	@echo "📱 功能: 設備掃描、配對、振動控制"
	@echo "💡 按 Ctrl+C 停止服務器"
	cd $(EXAMPLE_DIR) && npx vite --host 0.0.0.0 --port $(DEV_PORT)

# 快速開發（不重新建構）
quick-dev:
	@echo "⚡ 快速啟動開發服務器..."
	cd $(EXAMPLE_DIR) && npx vite --host 0.0.0.0 --port $(DEV_PORT)

# 啟動靜態文件伺服器（適用於測試）
serve: build
	@echo "🌐 啟動靜態文件伺服器 (端口 $(PORT))..."
	@echo "🔗 訪問: http://localhost:$(PORT)/example/"
	@echo "💡 按 Ctrl+C 停止伺服器"
	python3 -m http.server $(PORT)

# 運行生產版本
run: build
	@echo "🚀 啟動生產版本..."
	cd $(EXAMPLE_DIR) && npx vite preview --host 0.0.0.0 --port $(DEV_PORT)

# 快速測試
test: build
	@echo "🧪 啟動快速測試（WebBluetooth 功能）..."
	@python3 -m http.server $(PORT) > /dev/null 2>&1 & \
	echo $$! > .server.pid && \
	sleep 2 && \
	echo "🔗 完整示範: http://localhost:$(PORT)/example/" && \
	echo "⏹️  停止伺服器: make stop"

# 停止測試伺服器
stop:
	@if [ -f .server.pid ]; then \
		echo "⏹️  停止測試伺服器..."; \
		kill $$(cat .server.pid) 2>/dev/null || true; \
		rm -f .server.pid; \
		echo "✅ 伺服器已停止"; \
	else \
		echo "❓ 沒有運行中的測試伺服器"; \
	fi

# 清理編譯輸出
clean:
	@echo "🧹 清理編譯輸出..."
	rm -rf $(PKG_DIR)
	rm -rf $(EXAMPLE_DIR)/public/wasm/
	rm -rf dist/
	rm -rf node_modules/
	rm -rf $(EXAMPLE_DIR)/node_modules/
	@echo "✅ 清理完成"

# 完全清理（包含 Cargo 快取）
clean-all: clean stop
	@echo "🧹 執行完全清理..."
	cargo clean
	rm -f .server.pid
	@echo "✅ 完全清理完成"

# 重新建構
rebuild: clean build

# 只編譯 WASM（快速測試）
wasm-only:
	@echo "⚡ 僅編譯 WASM（快速測試）..."
	wasm-pack build --target web $(WASM_CRATE) --no-default-features --features $(FEATURES)
	mkdir -p $(EXAMPLE_DIR)/public/wasm
	cp $(PKG_DIR)/buttplug_server_bg.wasm $(EXAMPLE_DIR)/public/wasm/

# 檢查編譯結果
check: build-wasm
	@echo "🔍 檢查編譯結果..."
	@if [ -f "$(PKG_DIR)/buttplug_server.js" ]; then \
		echo "✅ buttplug_server.js 存在"; \
	else \
		echo "❌ buttplug_server.js 不存在"; \
	fi
	@if [ -f "$(PKG_DIR)/buttplug_server_bg.wasm" ]; then \
		echo "✅ buttplug_server_bg.wasm 存在"; \
		echo "📊 WASM 檔案大小: $$(du -h $(PKG_DIR)/buttplug_server_bg.wasm | cut -f1)"; \
	else \
		echo "❌ buttplug_server_bg.wasm 不存在"; \
	fi
	@if [ -f "$(PKG_DIR)/package.json" ]; then \
		echo "✅ package.json 存在"; \
		echo "📦 版本: $$(grep '"version"' $(PKG_DIR)/package.json | cut -d'"' -f4)"; \
	else \
		echo "❌ package.json 不存在"; \
	fi

# 設定開發環境
setup: check-tools install
	@echo "🎯 開發環境設定完成！"
	@echo "📋 可用功能："
	@echo "   • WebBluetooth 設備掃描和配對"
	@echo "   • 振動強度控制"
	@echo "   • 實時設備狀態監控"

# 顯示說明
help:
	@echo ""
	@echo "🔌 Buttplug WASM 專案建構工具（支援 WebBluetooth）"
	@echo ""
	@echo "📋 主要指令:"
	@echo "  install      - 安裝所有依賴"
	@echo "  build        - 完整建構專案"
	@echo "  dev          - 啟動開發服務器（支援熱重載）"
	@echo "  run          - 啟動生產版本"
	@echo "  serve        - 啟動靜態文件服務器"
	@echo ""
	@echo "🔧 開發指令:"
	@echo "  quick-dev    - 快速啟動（不重新建構）"
	@echo "  wasm-only    - 僅重新編譯 WASM"
	@echo "  rebuild      - 清理並重新建構"
	@echo "  clean        - 清理編譯輸出"
	@echo "  clean-all    - 完全清理（包含 Cargo 快取）"
	@echo ""
	@echo "🧪 測試指令:"
	@echo "  test         - 快速測試（後台啟動）"
	@echo "  stop         - 停止測試伺服器"
	@echo "  check        - 檢查編譯結果"
	@echo "  setup        - 設定開發環境"
	@echo "  help         - 顯示此說明"
	@echo ""
	@echo "🚀 快速開始:"
	@echo "  make setup   # 初始化環境"
	@echo "  make dev     # 開發模式"
	@echo "  make run     # 生產模式"
	@echo ""
	@echo "🌐 測試網址:"
	@echo "  http://localhost:$(DEV_PORT)/                # 開發模式"
	@echo "  http://localhost:$(PORT)/example/      # 靜態文件模式"
	@echo ""
	@echo "🎯 主要功能:"
	@echo "  • WebBluetooth 設備自動掃描和配對"
	@echo "  • 振動強度滑桿控制（0-100%）"
	@echo "  • 實時設備連接狀態顯示"
	@echo "  • 完整的錯誤處理和日誌記錄"
	@echo ""