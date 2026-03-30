PORT := 8788

.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make install  - 安裝相依套件"
	@echo "  make dev      - 啟動本地開發伺服器（KV + D1 模擬）"
	@echo "  make test     - 執行 API curl 測試"
	@echo "  make deploy   - 部署到 Cloudflare Pages"
	@echo "  make clean    - 清理 node_modules 與 wrangler 本地狀態"
	@echo ""
	@echo "使用範例："
	@echo "  make install && make dev"
	@echo "  make test"

.PHONY: install
install:  ## 安裝相依套件
	npm install

.PHONY: dev
dev:  ## 啟動本地開發伺服器（自動清理佔用的 port）
	@echo "清理 port $(PORT)..."
	@lsof -ti:$(PORT) | xargs -r kill -9 2>/dev/null || true
	@echo "啟動 wrangler pages dev on port $(PORT)..."
	npx wrangler pages dev public --kv VISITS --d1 DB --port $(PORT)

.PHONY: test
test:  ## 執行 API curl 測試（需先 make dev 啟動伺服器）
	@echo "=== [KV] GET /api/visits ==="
	@curl -s http://localhost:$(PORT)/api/visits | python3 -m json.tool
	@echo ""
	@echo "=== [D1] POST /api/messages (新增留言) ==="
	@curl -s -X POST http://localhost:$(PORT)/api/messages \
		-H "Content-Type: application/json" \
		-d '{"name":"測試者","message":"Hello from Makefile test!"}' | python3 -m json.tool
	@echo ""
	@echo "=== [D1] GET /api/messages (列出留言) ==="
	@curl -s http://localhost:$(PORT)/api/messages | python3 -m json.tool
	@echo ""
	@echo "=== 空白輸入防護驗證（預期 400） ==="
	@curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" \
		-X POST http://localhost:$(PORT)/api/messages \
		-H "Content-Type: application/json" \
		-d '{"name":"","message":""}'
	@echo ""
	@echo "=== [KV] GET /api/visits（計數應遞增）==="
	@curl -s http://localhost:$(PORT)/api/visits | python3 -m json.tool

.PHONY: deploy
deploy:  ## 部署到 Cloudflare Pages（需先 wrangler login）
	npx wrangler pages deploy public

.PHONY: clean
clean:  ## 清理 node_modules 與 wrangler 本地狀態
	rm -rf node_modules .wrangler
	@echo "清理完成"
