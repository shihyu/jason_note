# WASM 專案 Makefile

.PHONY: all build test serve clean help

# 預設目標
all: build

# 編譯 WASM
build:
	@echo "🔨 編譯 WASM..."
	@wasm-pack build --target web --out-dir pkg
	@echo "✅ 編譯完成"

# 執行測試
test: build
	@echo "🧪 執行測試..."
	@node test.js

# 啟動開發伺服器
serve: build
	@echo "🔍 檢查並清理 8000 端口..."
	@lsof -ti:8000 | xargs -r kill -9 2>/dev/null || true
	@echo "🌐 啟動伺服器 (http://localhost:8000)..."
	@echo "📋 測試頁面:"
	@echo "  - http://localhost:8000/test-with-logs.html (Log 顯示)"
	@echo "  - http://localhost:8000/test.html (基本測試)"
	@python3 -m http.server 8000

# 清理檔案
clean:
	@echo "🧹 清理檔案..."
	@rm -rf pkg/ target/
	@cargo clean

# 說明
help:
	@echo "可用指令:"
	@echo "  make build  - 編譯 WASM"
	@echo "  make test   - 執行測試"  
	@echo "  make serve  - 啟動開發伺服器"
	@echo "  make clean  - 清理生成檔案"
	@echo "  make help   - 顯示說明"