# Cloudflare Pages 與 Functions：靜態網站 + 邊緣運算完整指南

在現代前端開發中，前後端的界線越來越模糊。**前端靜態頁面**和**後端無伺服器運算**的結合，讓開發者能以最少的基礎建設快速上線專案。Cloudflare 提供的 **Pages** 與 **Functions**，正是這種模式的最佳搭配。本文將帶你快速了解兩者的特性，以及如何結合使用。

---

## Cloudflare Pages：前端靜態網站平台

Cloudflare Pages 是一個**靜態網站託管服務**，支援從 GitHub/GitLab 自動部署。特色包括：

- **免費 & 全球 CDN**：內容自動分發到 Cloudflare 的邊緣節點，確保快速載入。
- **CI/CD 整合**：每次推送（push）程式碼就會自動部署。
- **預覽部署（Preview Deployments）**：每個 PR 都會產生預覽連結，方便團隊測試。
- **自訂網域**：可以綁定自己的網域並自動支援 HTTPS。
- **環境變數支援**：可在不同部署環境（Production / Preview / Dev）設定 API 金鑰、設定檔。

適合用來部署：

- 個人作品集
- 前端框架專案（React、Vue、Next.js、Astro）
- 文件網站或靜態部落格（Hugo、Jekyll）

參考文件：[Cloudflare Pages Framework Guides](https://developers.cloudflare.com/pages/framework-guides/)

---

## Cloudflare Functions：邊緣運算的後端

Functions 是 Cloudflare 提供的**無伺服器函式運算**（類似 AWS Lambda、Vercel Functions），但運行在 Cloudflare 的邊緣節點。特色包括：

- **全球邊緣節點**：程式碼在使用者最近的 Cloudflare 節點執行，延遲極低。
- **無伺服器**：不需要維護伺服器，Cloudflare 會自動擴展。
- **事件驅動**：支援 `fetch`、HTTP API 呼叫等事件觸發。
- **原生整合 Cloudflare 生態系**：可與 KV、D1（資料庫）、R2（S3 物件儲存）結合。
- **語言支援**：主要使用 JavaScript / TypeScript，並逐步支援更多生態系。

適合用來處理：

- API Proxy（避免 CORS 問題）
- 使用者驗證（Auth / JWT）
- 表單處理與寄信
- 輕量 API（查詢資料庫、KV、Redis）

---

## Pages + Functions：完美結合

Cloudflare Pages 與 Functions 的關係，可以理解成**前端 + 後端**的組合。

- **Pages**：負責靜態資源（HTML / CSS / JS）的快速載入。
- **Functions**：負責動態需求（API、商業邏輯、與資料庫互動）。

---

## 實戰範例：留言板（前後端 + KV + D1）

這是一個本地與正式環境均已驗證的完整範例：

| 層級 | 技術 | 用途 |
|------|------|------|
| 前端 | HTML / JS | 留言板 UI，由 Pages 托管 |
| 後端 | Cloudflare Functions | `/api/visits`、`/api/messages` |
| DB 1 | **KV** | 訪客計數器（key-value 快速讀寫）|
| DB 2 | **D1（SQLite）** | 留言資料（關聯式查詢）|

### 專案結構

```
cf-guestbook/
├── public/
│   └── index.html          # 前端頁面（Pages 托管）
├── functions/
│   └── api/
│       ├── visits.js       # GET /api/visits → KV 訪客計數
│       └── messages.js     # GET/POST /api/messages → D1 留言
├── wrangler.toml
├── Makefile
└── package.json
```

---

### 步驟 1：初始化專案

```bash
mkdir cf-guestbook && cd cf-guestbook
npm init -y
npm install --save-dev wrangler
mkdir -p public functions/api
```

---

### 步驟 2：設定 `wrangler.toml`（先填佔位符）

```toml
name = "cf-guestbook"
pages_build_output_dir = "public"
compatibility_date = "2024-01-01"

[[kv_namespaces]]
binding = "VISITS"
id = "visits-kv"        # 執行 make setup 後自動替換為真實 ID

[[d1_databases]]
binding = "DB"
database_name = "guestbook"
database_id = "guestbook-d1"   # 執行 make setup 後自動替換為真實 ID
```

> **重要**：`binding` 是程式碼中存取的變數名稱（`env.VISITS`、`env.DB`）。
> `id` 與 `database_id` 需填入 Cloudflare 上真實資源的 ID，透過 `make setup` 自動取得並寫入。

---

### 步驟 3：Makefile（含自動化 setup）

```makefile
PORT := 8788

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "可用目標："
	@echo "  make install  - 安裝相依套件"
	@echo "  make setup    - 建立 Cloudflare KV + D1，自動寫入 wrangler.toml（首次部署用）"
	@echo "  make dev      - 啟動本地開發伺服器（KV + D1 模擬）"
	@echo "  make test     - 執行 API curl 測試"
	@echo "  make deploy   - 部署到 Cloudflare Pages"
	@echo "  make clean    - 清理 node_modules 與 wrangler 本地狀態"
	@echo ""
	@echo "首次部署流程："
	@echo "  make install && npx wrangler login && make setup && make deploy"

.PHONY: install
install:
	npm install

.PHONY: setup
setup:  ## 建立 KV + D1，自動寫入 wrangler.toml
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
	@echo "wrangler.toml 更新完成："
	@grep -E "^id =|^database_id =" wrangler.toml

.PHONY: dev
dev:
	@lsof -ti:$(PORT) | xargs -r kill -9 2>/dev/null || true
	npx wrangler pages dev public --kv VISITS --d1 DB --port $(PORT)

.PHONY: test
test:
	@echo "=== [KV] GET /api/visits ==="
	@curl -s http://localhost:$(PORT)/api/visits | python3 -m json.tool
	@echo ""
	@echo "=== [D1] POST /api/messages ==="
	@curl -s -X POST http://localhost:$(PORT)/api/messages \
		-H "Content-Type: application/json" \
		-d '{"name":"測試者","message":"Hello from Makefile test!"}' | python3 -m json.tool
	@echo ""
	@echo "=== [D1] GET /api/messages ==="
	@curl -s http://localhost:$(PORT)/api/messages | python3 -m json.tool
	@echo ""
	@echo "=== 空白輸入防護（預期 400）==="
	@curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" \
		-X POST http://localhost:$(PORT)/api/messages \
		-H "Content-Type: application/json" \
		-d '{"name":"","message":""}'
	@echo ""
	@echo "=== [KV] 第二次計數（應遞增）==="
	@curl -s http://localhost:$(PORT)/api/visits | python3 -m json.tool

.PHONY: deploy
deploy:
	npx wrangler pages deploy public

.PHONY: clean
clean:
	rm -rf node_modules .wrangler
	@echo "清理完成"
```

---

### 步驟 4：前端頁面 `public/index.html`

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Cloudflare 留言板</title>
  <style>
    body { font-family: sans-serif; padding: 2rem; background: #f0f4f8; }
    .card { background: #fff; border-radius: 10px; padding: 1.5rem; margin-bottom: 1.5rem; }
    input, textarea { width: 100%; padding: 0.6rem; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 0.75rem; }
    button { background: #e36209; color: #fff; border: none; border-radius: 6px; padding: 0.6rem 1.5rem; cursor: pointer; }
    .msg-item { border-bottom: 1px solid #eee; padding: 0.75rem 0; }
  </style>
</head>
<body>
  <h1>Cloudflare 留言板</h1>
  <p>訪客人數（KV）：<strong id="visit-count">載入中...</strong></p>

  <div class="card">
    <h2>留下訊息（D1）</h2>
    <input id="name" type="text" placeholder="你的名字" />
    <textarea id="message" placeholder="留言內容..."></textarea>
    <button onclick="submitMessage()">送出</button>
    <div id="status"></div>
  </div>

  <div class="card">
    <h2>所有留言</h2>
    <div id="messages">載入中...</div>
  </div>

  <script>
    async function loadVisits() {
      const res = await fetch('/api/visits');
      const data = await res.json();
      document.getElementById('visit-count').textContent = data.count;
    }

    async function loadMessages() {
      const res = await fetch('/api/messages');
      const data = await res.json();
      const el = document.getElementById('messages');
      if (!data.messages?.length) { el.innerHTML = '<p>還沒有留言！</p>'; return; }
      el.innerHTML = data.messages.map(m => `
        <div class="msg-item">
          <strong>${escHtml(m.name)}</strong>
          <small> ${new Date(m.created_at).toLocaleString('zh-TW')}</small>
          <p>${escHtml(m.message)}</p>
        </div>
      `).join('');
    }

    async function submitMessage() {
      const name = document.getElementById('name').value.trim();
      const message = document.getElementById('message').value.trim();
      const status = document.getElementById('status');
      if (!name || !message) { status.textContent = '請填寫名字與留言！'; return; }
      const res = await fetch('/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, message }),
      });
      const data = await res.json();
      if (data.success) {
        status.textContent = '留言成功！';
        document.getElementById('name').value = '';
        document.getElementById('message').value = '';
        loadMessages();
      } else {
        status.textContent = '失敗：' + data.error;
      }
    }

    function escHtml(str) {
      return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }

    loadVisits();
    loadMessages();
  </script>
</body>
</html>
```

---

### 步驟 5：KV 訪客計數 `functions/api/visits.js`

```js
/**
 * GET /api/visits
 * 每次呼叫從 KV 讀取並自動 +1
 * Binding: env.VISITS (KV Namespace)
 */
export async function onRequestGet({ env }) {
  const key = 'visit_count';
  const raw = await env.VISITS.get(key);
  const count = raw ? parseInt(raw, 10) + 1 : 1;
  await env.VISITS.put(key, String(count));

  return new Response(JSON.stringify({ count }), {
    headers: { 'Content-Type': 'application/json' },
  });
}
```

> **重點**：
> - `env.VISITS` 來自 `wrangler.toml` 的 `binding = "VISITS"`
> - KV 適合高頻讀取、低頻寫入的場景（計數器、快取、設定值）

---

### 步驟 6：D1 留言 CRUD `functions/api/messages.js`

```js
/**
 * GET  /api/messages → 列出所有留言（D1）
 * POST /api/messages → 新增一則留言（D1）
 * Binding: env.DB (D1 Database)
 */

async function ensureTable(db) {
  // 注意：D1 本地模擬不支援多行 exec()，改用單行 prepare().run()
  await db.prepare(
    "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now')))"
  ).run();
}

export async function onRequestGet({ env }) {
  try {
    await ensureTable(env.DB);
    const { results } = await env.DB.prepare(
      'SELECT id, name, message, created_at FROM messages ORDER BY id DESC LIMIT 50'
    ).all();
    return new Response(JSON.stringify({ messages: results }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500, headers: { 'Content-Type': 'application/json' },
    });
  }
}

export async function onRequestPost({ request, env }) {
  try {
    const body = await request.json();
    const name    = (body.name    || '').trim().slice(0, 50);
    const message = (body.message || '').trim().slice(0, 500);

    if (!name || !message) {
      return new Response(JSON.stringify({ error: '名字與留言不可為空' }), {
        status: 400, headers: { 'Content-Type': 'application/json' },
      });
    }

    await ensureTable(env.DB);
    await env.DB.prepare(
      'INSERT INTO messages (name, message) VALUES (?, ?)'
    ).bind(name, message).run();

    return new Response(JSON.stringify({ success: true }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500, headers: { 'Content-Type': 'application/json' },
    });
  }
}
```

> **重點**：
> - D1 使用 **Prepared Statement**（`.prepare().bind().run()`）防止 SQL 注入
> - 本地開發時，wrangler 在 `.wrangler/state/` 自動建立 SQLite 模擬 D1
> - `db.exec()` 不支援多行 DDL，請改用單行 `prepare().run()`

---

### 步驟 7：取得 KV / D1 真實 ID

部署到 Cloudflare 前，必須先在帳號下建立真實資源，取得 ID 填入 `wrangler.toml`。

#### 手動方式

```bash
# 建立 KV Namespace，輸出中包含真實 ID
npx wrangler kv namespace create VISITS
# → id = "329919071143484c91ebbf78c31ab721"  ← 複製這個

# 建立 D1 Database，輸出中包含真實 ID
npx wrangler d1 create guestbook
# → database_id = "12e617bf-bbf1-43a6-918d-2446e01e56c2"  ← 複製這個
```

兩個 ID 建立後**永久固定**，不會改變，除非手動刪除資源重建。

#### 忘記 ID 怎麼辦

```bash
# 查詢現有 KV Namespace 列表
npx wrangler kv namespace list

# 查詢現有 D1 Database 列表
npx wrangler d1 list
```

#### 自動化方式（make setup）

執行 `make setup` 會自動完成：
1. 嘗試建立 KV / D1（首次）
2. 若已存在，改從清單查詢現有 ID
3. 直接用 `sed` 寫入 `wrangler.toml`，無需手動複製貼上

```bash
make setup
# 輸出：
# KV ID: 329919071143484c91ebbf78c31ab721
# D1 ID: 12e617bf-bbf1-43a6-918d-2446e01e56c2
# wrangler.toml 更新完成
```

---

### 步驟 8：本地執行驗證

```bash
# 啟動本地開發伺服器（自動模擬 KV + D1，無需連線 Cloudflare）
make dev
```

另開終端執行測試：

```bash
make test
```

預期輸出：

```
=== [KV] GET /api/visits ===
{"count": 1}

=== [D1] POST /api/messages ===
{"success": true}

=== [D1] GET /api/messages ===
{"messages": [{"id": 1, "name": "測試者", "message": "Hello from Makefile test!", ...}]}

=== 空白輸入防護（預期 400）===
HTTP Status: 400

=== [KV] 第二次計數（應遞增）===
{"count": 2}
```

---

### 步驟 9：部署到 Cloudflare 正式環境

```bash
# 首次部署完整流程
make install
npx wrangler login    # 瀏覽器授權一次（只需做一次）
make setup            # 建立 KV + D1，自動寫入 wrangler.toml
make deploy

# 之後更新只需
make deploy
```

部署成功後輸出：

```
✨ Deployment complete! Take a peek over at https://xxxx.cf-guestbook.pages.dev
```

正式網址：`https://cf-guestbook.pages.dev`

---

### 正式環境驗證結果

```bash
BASE="https://cf-guestbook.pages.dev"

curl "$BASE/api/visits"
# → {"count":7}

curl -X POST "$BASE/api/messages" \
  -H "Content-Type: application/json" \
  -d '{"name":"全流程驗證","message":"clean→install→setup→test→deploy 全OK！"}'
# → {"success":true}

curl "$BASE/api/messages"
# → {"messages":[{"id":5,"name":"全流程驗證","message":"clean→install→setup→test→deploy 全OK！",...},...]}

curl -o /dev/null -w "%{http_code}" -X POST "$BASE/api/messages" \
  -H "Content-Type: application/json" -d '{"name":"","message":""}'
# → 400
```

---

## KV vs D1 選擇指南

| 特性 | KV（Key-Value）| D1（SQLite）|
|------|----------------|-------------|
| 資料結構 | 鍵值對（字串 / 二進位）| 關聯式資料表 |
| 查詢方式 | 只能用 key 查詢 | 支援 SQL（JOIN、WHERE、ORDER BY）|
| 一致性 | 最終一致性（全球同步）| 強一致性（單一區域寫入）|
| 適合場景 | 計數器、快取、Session、設定值 | 使用者資料、留言、訂單、記錄 |
| 讀取延遲 | 極低（邊緣節點快取）| 低（但比 KV 稍高）|

---

## 結語

Cloudflare Pages 與 Functions 提供了**全靜態網站 + 輕量後端 API** 的完整解決方案，開發者能夠用最少的基礎建設快速打造完整應用。無論是個人部落格、作品集，還是中小型 Web 應用程式，都可以透過 Pages + Functions 來實現高效、安全、可擴展的架構。

如果你已經有一個 GitHub Repo 的靜態頁面，部署到 **Pages** 只要幾分鐘，而加上 **Functions** 後，你的靜態網站就瞬間升級成**全端應用**。
