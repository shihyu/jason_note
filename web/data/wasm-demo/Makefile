.PHONY: build run serve clean kill-port help install

# 預設的 dev server port
PORT ?= 8080

help:
	@echo "Makefile commands:"
	@echo "  make install    - 安裝依賴"
	@echo "  make build      - 編譯 Rust + WebAssembly"
	@echo "  make run        - Kill port 並啟動開發伺服器"
	@echo "  make serve      - 同 run"
	@echo "  make kill-port  - Kill 佔用 port $(PORT) 的進程"
	@echo "  make clean      - 清理生成的檔案"
	@echo "  make help       - 顯示此幫助訊息"

# 安裝依賴
install:
	@echo "==> 安裝 Node.js 依賴..."
	npm install
	@echo "==> 檢查 wasm-bindgen-cli..."
	@which wasm-bindgen > /dev/null || cargo install wasm-bindgen-cli
	@echo "==> 依賴安裝完成"

# 編譯
build:
	@echo "==> 編譯 Rust + WebAssembly..."
	npm run build
	@echo "==> 編譯完成"

# Kill 佔用的 port
kill-port:
	@echo "==> 檢查 port $(PORT) 是否被佔用..."
	@PID=$$(lsof -ti:$(PORT)) && \
		if [ -n "$$PID" ]; then \
			echo "==> 終止佔用 port $(PORT) 的進程 (PID: $$PID)"; \
			kill -9 $$PID; \
			sleep 1; \
		else \
			echo "==> Port $(PORT) 未被佔用"; \
		fi || echo "==> Port $(PORT) 未被佔用"

# 啟動開發伺服器（先 kill port）
run: kill-port
	@echo "==> 啟動開發伺服器於 http://localhost:$(PORT)..."
	npm run serve

serve: run

# 清理生成的檔案
clean:
	@echo "==> 清理生成的檔案..."
	rm -f wasm_demo.js wasm_demo_bg.js wasm_demo_bg.wasm wasm_demo.d.ts wasm_demo_bg.wasm.d.ts
	rm -rf target/
	rm -rf node_modules/
	rm -rf dist/
	rm -f package-lock.json
	@echo "==> 清理完成"

# 完整的重建流程
rebuild: clean install build
	@echo "==> 重建完成"
