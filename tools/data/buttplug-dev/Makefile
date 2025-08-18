# Buttplug Server WASM Makefile
# 提供編譯、運行、清理功能

.PHONY: all build run serve clean clean-all test help

# 預設目標
all: build

# 變數定義
WASM_CRATE := crates/buttplug_server
PKG_DIR := $(WASM_CRATE)/pkg
WEB_EXAMPLE_DIR := web_example
FEATURES := wasm
PORT := 8000
WEB_PORT := 8080

# 檢查必要工具
check-tools:
	@echo "🔍 檢查必要工具..."
	@command -v wasm-pack >/dev/null 2>&1 || { echo "❌ wasm-pack 未安裝. 請執行: cargo install wasm-pack"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "❌ python3 未安裝"; exit 1; }
	@echo "✅ 所有工具已就緒"

# 編譯 WASM 模組
build: check-tools
	@echo "🚀 開始編譯 WASM 模組..."
	wasm-pack build --target web $(WASM_CRATE) --no-default-features --features $(FEATURES)
	@echo "✅ WASM 編譯完成！"
	@echo "📁 輸出位置: $(PKG_DIR)"

# 複製 WASM 檔案到 web 範例目錄
copy-wasm: build
	@echo "📂 複製 WASM 檔案到 web 範例目錄..."
	cp -r $(PKG_DIR) $(WEB_EXAMPLE_DIR)/
	@echo "✅ 檔案複製完成"

# 啟動簡單測試伺服器（根目錄）
run: copy-wasm
	@echo "🌐 啟動測試伺服器 (端口 $(PORT))..."
	@echo "🔗 訪問: http://localhost:$(PORT)/web_example/"
	@echo "💡 按 Ctrl+C 停止伺服器"
	python3 -m http.server $(PORT)

# 啟動 web 範例伺服器
serve: copy-wasm
	@echo "🌐 啟動 Web 範例伺服器 (端口 $(WEB_PORT))..."
	@echo "🔗 訪問: http://localhost:$(WEB_PORT)/"
	@echo "💡 按 Ctrl+C 停止伺服器"
	cd $(WEB_EXAMPLE_DIR) && python3 -m http.server $(WEB_PORT)

# 快速測試（後台啟動伺服器並開啟瀏覽器）
test: copy-wasm
	@echo "🧪 啟動快速測試..."
	@python3 -m http.server $(PORT) > /dev/null 2>&1 & \
	echo $$! > .server.pid && \
	sleep 2 && \
	echo "🔗 完整示範: http://localhost:$(PORT)/web_example/" && \
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

# 清理 WASM 編譯輸出
clean:
	@echo "🧹 清理 WASM 編譯輸出..."
	rm -rf $(PKG_DIR)
	rm -rf $(WEB_EXAMPLE_DIR)/pkg
	@echo "✅ 清理完成"

# 完全清理（包含 Cargo 快取）
clean-all: clean stop
	@echo "🧹 執行完全清理..."
	cargo clean
	rm -f .server.pid
	@echo "✅ 完全清理完成"

# 重新編譯
rebuild: clean build

# 檢查編譯結果
check: build
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

# 顯示說明
help:
	@echo ""
	@echo "🔌 Buttplug Server WASM 編譯工具"
	@echo ""
	@echo "📋 可用目標:"
	@echo "  build        - 編譯 WASM 模組"
	@echo "  run          - 編譯並啟動測試伺服器 (端口 $(PORT))"
	@echo "  serve        - 啟動 Web 範例伺服器 (端口 $(WEB_PORT))"
	@echo "  test         - 快速測試 (後台啟動)"
	@echo "  stop         - 停止測試伺服器"
	@echo "  check        - 檢查編譯結果"
	@echo "  rebuild      - 清理並重新編譯"
	@echo "  clean        - 清理編譯輸出"
	@echo "  clean-all    - 完全清理 (包含 Cargo 快取)"
	@echo "  help         - 顯示此說明"
	@echo ""
	@echo "🚀 快速開始:"
	@echo "  make build   # 編譯"
	@echo "  make run     # 編譯並運行"
	@echo "  make serve   # 運行 Web 範例"
	@echo ""
	@echo "🌐 測試網址:"
	@echo "  http://localhost:$(PORT)/web_example/        # 完整示範"
	@echo "  http://localhost:$(WEB_PORT)/                       # Web 範例專用"
	@echo ""