# Buttplug WASM Project Makefile

# 路徑設定
RUST_DIR = rust
JS_DIR = ../js
EXAMPLE_DIR = example

# 建構目標
.PHONY: all build clean run dev install setup

# 預設目標
all: build

# 安裝依賴
install:
	@echo "安裝依賴..."
	npm install
	cd $(JS_DIR) && npm install
	cd $(EXAMPLE_DIR) && npm install

# 完整建構流程
build: install build-wasm build-js build-dist copy-wasm

# 編譯 Rust WASM
build-wasm:
	@echo "編譯 Rust WASM..."
	cd $(RUST_DIR) && wasm-pack build --release --target web

# 編譯 JS 專案
build-js:
	@echo "編譯 JS 專案..."
	cd $(JS_DIR) && npx vite build

# 編譯 TypeScript 和生成 dist
build-dist:
	@echo "編譯 TypeScript..."
	npm run build:web

# 複製 WASM 檔案到 public
copy-wasm:
	@echo "複製 WASM 檔案..."
	mkdir -p $(EXAMPLE_DIR)/public/wasm
	cp $(RUST_DIR)/pkg/buttplug_wasm_bg.wasm $(EXAMPLE_DIR)/public/wasm/

# 開發模式 (自動重載)
dev: build
	@echo "啟動開發服務器..."
	cd $(EXAMPLE_DIR) && npx vite --host 0.0.0.0 --port 3000

# 運行生產版本
run: build
	@echo "啟動服務器..."
	cd $(EXAMPLE_DIR) && npx vite preview --host 0.0.0.0 --port 3000

# 快速開發 (不完整建構)
quick-dev:
	@echo "快速啟動開發服務器..."
	cd $(EXAMPLE_DIR) && npx vite --host 0.0.0.0 --port 3000

# 清理建構檔案
clean:
	@echo "清理建構檔案..."
	rm -rf dist/
	rm -rf $(RUST_DIR)/pkg/
	rm -rf $(RUST_DIR)/target/
	rm -rf $(JS_DIR)/dist/
	rm -rf $(EXAMPLE_DIR)/public/wasm/
	rm -rf $(EXAMPLE_DIR)/dist/
	rm -rf node_modules/
	rm -rf $(JS_DIR)/node_modules/
	rm -rf $(EXAMPLE_DIR)/node_modules/

# 重新建構所有
rebuild: clean install build

# 只編譯 WASM (快速測試)
wasm-only:
	@echo "僅編譯 WASM..."
	cd $(RUST_DIR) && wasm-pack build --release --target web
	npm run build:web
	mkdir -p $(EXAMPLE_DIR)/public/wasm
	cp $(RUST_DIR)/pkg/buttplug_wasm_bg.wasm $(EXAMPLE_DIR)/public/wasm/

# 檢查依賴
check:
	@echo "檢查工具..."
	@command -v wasm-pack >/dev/null 2>&1 || { echo "需要安裝 wasm-pack"; exit 1; }
	@command -v npm >/dev/null 2>&1 || { echo "需要安裝 npm"; exit 1; }
	@echo "所有工具已安裝"

# 設定開發環境
setup: check install
	@echo "開發環境設定完成"

# 顯示幫助
help:
	@echo "Buttplug WASM 專案建構指令:"
	@echo ""
	@echo "  make install     - 安裝所有依賴"
	@echo "  make build       - 完整建構專案"
	@echo "  make dev         - 啟動開發服務器 (http://localhost:3000)"
	@echo "  make run         - 啟動生產服務器"
	@echo "  make clean       - 清理所有建構檔案"
	@echo "  make rebuild     - 清理並重新建構"
	@echo "  make wasm-only   - 僅重新編譯 WASM"
	@echo "  make quick-dev   - 快速啟動 (不重新建構)"
	@echo "  make setup       - 初始化開發環境"
	@echo "  make check       - 檢查必要工具"
	@echo "  make help        - 顯示此幫助訊息"