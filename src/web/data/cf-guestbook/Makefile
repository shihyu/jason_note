PORT := 8788

.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-15s - %s\n", $$1, $$2}'
	@echo ""
	@echo "首次部署流程："
	@echo "  make install"
	@echo "  npx wrangler login"
	@echo "  make setup"
	@echo "  make deploy"

.PHONY: install
install:  ## 安裝相依套件
	npm install

.PHONY: setup
setup:  ## 建立 Cloudflare KV + D1，自動寫入 wrangler.toml（首次部署用）
	@echo "建立 KV Namespace: VISITS..."
	$(eval KV_ID := $(shell npx wrangler kv namespace create VISITS 2>&1 | grep 'id = ' | sed 's/.*id = "\(.*\)"/\1/'))
	@if [ -z "$(KV_ID)" ]; then echo "KV 已存在，從清單取得 ID..."; fi
	$(eval KV_ID := $(or $(KV_ID), $(shell npx wrangler kv namespace list 2>&1 | python3 -c "import sys,json; ns=[x for x in json.load(sys.stdin) if x['title']=='VISITS']; print(ns[0]['id'] if ns else '')")))
	@echo "KV ID: $(KV_ID)"

	@echo "建立 D1 Database: guestbook..."
	$(eval D1_ID := $(shell npx wrangler d1 create guestbook 2>&1 | grep 'database_id' | sed 's/.*database_id = "\(.*\)"/\1/'))
	@if [ -z "$(D1_ID)" ]; then echo "D1 已存在，從清單取得 ID..."; fi
	$(eval D1_ID := $(or $(D1_ID), $(shell npx wrangler d1 list 2>&1 | grep 'guestbook' | awk '{print $$2}')))
	@echo "D1 ID: $(D1_ID)"

	@echo "寫入 wrangler.toml..."
	@sed -i "s|^id = .*|id = \"$(KV_ID)\"|" wrangler.toml
	@sed -i "s|^database_id = .*|database_id = \"$(D1_ID)\"|" wrangler.toml
	@echo "wrangler.toml 更新完成"
	@grep -E "^id =|^database_id =" wrangler.toml

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

.PHONY: inspect-d1
inspect-d1:  ## 查看 D1 資料庫 (Remote)
	@echo "=== [D1] messages 資料表內容 (前 20 筆) ==="
	npx wrangler d1 execute guestbook --remote --command "SELECT * FROM messages ORDER BY id DESC LIMIT 20;"

.PHONY: inspect-kv
inspect-kv:  ## 查看 KV 內容 (Remote)
	$(eval KV_NS_ID := $(shell npx wrangler kv namespace list 2>/dev/null | python3 -c "import sys,json; ns=[x for x in json.load(sys.stdin) if x['title']=='VISITS']; print(ns[0]['id'] if ns else '')"))
	@echo "=== [KV] 所有的 Key 列表 (namespace: $(KV_NS_ID)) ==="
	@npx wrangler kv key list --namespace-id $(KV_NS_ID) --remote
	@echo "=== [KV] 訪客計數 (visit_count) ==="
	@val=$$(npx wrangler kv key get --namespace-id $(KV_NS_ID) "visit_count" --remote 2>&1); echo "$${val:-(尚未有資料)}"

.PHONY: inspect
inspect: inspect-d1 inspect-kv  ## 同時查看 D1 與 KV 內容 (Remote)

.PHONY: diag
diag:  ## 診斷 Cloudflare 設定與 ID (比對本地與雲端)
	@echo "=== [Local] wrangler.toml 設定 ==="
	@grep -E "id =|database_id =" wrangler.toml
	@echo ""
	@echo "=== [Remote] Cloudflare 實際現有的 KV 列表 ==="
	npx wrangler kv namespace list
	@echo ""
	@echo "=== [Remote] Cloudflare 實際現有的 D1 列表 ==="
	npx wrangler d1 list

.PHONY: clean
clean:  ## 清理 node_modules 與 wrangler 本地狀態
	rm -rf node_modules .wrangler
	@echo "清理完成"
