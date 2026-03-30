# Makefile for cf-binance-ws

PORT := 8888
PUBLIC_DIR := public

.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build   - 安裝依賴 (npm install)"
	@echo "  make run     - 啟動本地預覽 (port $(PORT))"
	@echo "  make test    - 執行測試 (Node.js assert)"
	@echo "  make deploy  - 部署到 Cloudflare Pages"
	@echo "  make clean   - 清理 node_modules 與臨時檔案"
	@echo ""
	@echo "使用範例："
	@echo "  make build && make run"
	@echo "  make test"
	@echo "  make deploy"

.PHONY: build
build:  ## 安裝依賴
	npm install

.PHONY: run
run:  ## 執行本地預覽
	@echo "檢查 port $(PORT)..."
	@lsof -ti:$(PORT) | xargs -r kill -9 2>/dev/null || true
	@echo "啟動 wrangler pages dev..."
	npx wrangler pages dev $(PUBLIC_DIR) --port $(PORT)

.PHONY: test
test:  ## 執行測試
	npm test

.PHONY: deploy
deploy:  ## 部署到 Cloudflare Pages
	npm run deploy

.PHONY: clean
clean:  ## 清理建置產物
	rm -rf node_modules
	rm -f package-lock.json
	@echo "清理完成。"
