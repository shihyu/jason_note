# Rust WebAssembly Makefile

# 定義變量
PROJECT_NAME = rust-wasm-example
SERVER_PORT = 8000
PYTHON = python3

# 主要目標
.PHONY: all build serve clean help

# 預設目標，構建並運行
all: build serve

# 構建 WebAssembly
build:
	@echo "正在構建 WebAssembly..."
	wasm-pack build --target web
	@echo "構建完成！"

# 提供本地服務器運行示例
serve:
	@echo "啟動本地服務器在端口 $(SERVER_PORT)..."
	@if command -v $(PYTHON) > /dev/null 2>&1; then \
		$(PYTHON) -m http.server $(SERVER_PORT); \
	elif command -v python > /dev/null 2>&1; then \
		python -m http.server $(SERVER_PORT); \
	else \
		echo "錯誤: 未找到 Python。請安裝 Python 或使用其他 HTTP 服務器。"; \
		exit 1; \
	fi

# 快速啟動（構建並運行）
start: build serve

# 清理生成的文件
clean:
	@echo "正在清理項目..."
	rm -rf pkg
	rm -rf target
	@echo "清理完成！"

# 檢查依賴
check:
	@echo "檢查依賴..."
	@command -v rustc > /dev/null 2>&1 || { echo "錯誤: 未找到 Rust。請安裝 Rust: https://rustup.rs/"; exit 1; }
	@command -v wasm-pack > /dev/null 2>&1 || { echo "錯誤: 未找到 wasm-pack。請安裝: cargo install wasm-pack"; exit 1; }
	@echo "依賴檢查通過！"

# 構建發布版本
release:
	@echo "構建發布版本..."
	wasm-pack build --target web --release
	@echo "發布版本構建完成！"

# 顯示幫助信息
help:
	@echo "Rust WebAssembly 項目 Makefile"
	@echo ""
	@echo "可用命令:"
	@echo "  make            - 構建並運行 (相當於 make all)"
	@echo "  make build      - 僅構建 WebAssembly"
	@echo "  make serve      - 啟動本地服務器"
	@echo "  make start      - 構建並運行 (同 make all)"
	@echo "  make clean      - 清理生成的文件"
	@echo "  make check      - 檢查所需依賴"
	@echo "  make release    - 構建優化的發布版本"
	@echo "  make help       - 顯示此幫助信息"
	@echo ""
	@echo "項目將在 http://localhost:$(SERVER_PORT) 運行"
