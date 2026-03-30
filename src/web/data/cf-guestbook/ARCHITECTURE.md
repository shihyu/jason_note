# cf-guestbook 架構圖

## 專案結構

```
cf-guestbook/
├── public/
│   └── index.html          # 前端頁面（Pages 托管）
├── functions/
│   └── api/
│       ├── visits.js       # GET /api/visits  → KV 訪客計數
│       └── messages.js     # GET/POST /api/messages → D1 留言
├── wrangler.toml           # Cloudflare 設定（KV / D1 binding）
├── Makefile                # 開發 / 部署 / 測試自動化
└── package.json
```

---

## 整體系統架構

```
  開發者本機                      Cloudflare 全球網路
 ┌─────────────────┐             ┌─────────────────────────────────────────┐
 │  原始碼         │             │  邊緣節點（離使用者最近）               │
 │  public/        │─make deploy▶│ ┌──────────────┐  ┌───────────────────┐ │
 │  functions/     │             │ │  Pages CDN   │  │    Functions      │ │
 │  wrangler.toml  │─make setup─▶│ │  HTML/CSS/JS │  │  /api/visits      │ │
 └─────────────────┘             │ │  （靜態快取）│  │  /api/messages    │ │
                                 │ └──────────────┘  └─────────┬─────────┘ │
                                 │                             │           │
                                 │                   ┌─────────▼─────────┐ │
                                 │                   │  持久化儲存       │ │
                                 │                   │ ┌───────────────┐ │ │
  使用者瀏覽器                   │                   │ │  KV Namespace │ │ │
 ┌──────────────┐                │                   │ │  VISITS       │ │ │
 │  index.html  │──① GET /──────▶ Pages CDN          │ │  visit_count  │ │ │
 │  留言板 UI   │◀─② HTML/JS──── │                   │ └───────────────┘ │ │
 │              │──③ /api/*─────▶ Functions ────────▶│ ┌───────────────┐ │ │
 │              │◀─⑦ JSON ────── │                   │ │  D1 Database  │ │ │
 └──────────────┘                │                   │ │  guestbook    │ │ │
                                 │                   │ │  messages 表  │ │ │
                                 │                   │ └───────────────┘ │ │
                                 │                   └───────────────────┘ │
                                 └─────────────────────────────────────────┘
```

---

## 請求生命週期

```
瀏覽器              Pages CDN          Functions           KV          D1 (SQLite)
  │                    │                   │                │               │
  │── ① GET / ────────▶│                   │                │               │
  │◀─ ② index.html ─── │                   │                │               │
  │                    │                   │                │               │
  │── ③ GET /api/visits ──────────────────▶│                │               │
  │                    │                   │── get("visit_count") ─────────▶│
  │                    │                   │◀─ "6" ─────────────────────────│
  │                    │                   │── put("visit_count","7") ─────▶│
  │◀─ {"count":7} ─────────────────────────│                │               │
  │                    │                   │                │               │
  │── ④ GET /api/messages ────────────────▶│                │               │
  │                    │                   │── SELECT ... ORDER BY id DESC ─▶│
  │                    │                   │◀─ [{id:5, name:"小花",...}] ─────│
  │◀─ {"messages":[...]} ──────────────────│                │               │
  │                    │                   │                │               │
  │── ⑤ POST /api/messages ───────────────▶│                │               │
  │   {"name":"Jason","message":"你好！"}  │── 驗證輸入     │               │
  │                    │                   │── INSERT INTO messages (?,?) ──▶│
  │                    │                   │◀─ success ──────────────────────│
  │◀─ {"success":true} ─────────────────── │                │               │
```

---

## KV vs D1 資料流

```
  GET /api/visits                         GET /api/messages
 ┌──────────────────────────────┐        ┌──────────────────────────────────┐
 │  visits.js                   │        │  messages.js                     │
 │                              │        │                                  │
 │  1. env.VISITS.get(key)      │        │  1. ensureTable(env.DB)          │
 │     ↓                        │        │     CREATE TABLE IF NOT EXISTS   │
 │  2. count = raw + 1          │        │     ↓                            │
 │     ↓                        │        │  2. env.DB.prepare(SELECT)       │
 │  3. env.VISITS.put(key, n)   │        │        .all()                    │
 │     ↓                        │        │     ↓                            │
 │  4. return { count }         │        │  3. return { messages: results } │
 └──────────────────────────────┘        └──────────────────────────────────┘

  POST /api/messages
 ┌──────────────────────────────────────┐
 │  messages.js                         │
 │                                      │
 │  1. request.json() → { name, msg }   │
 │     ↓                                │
 │  2. 驗證非空、截斷長度（50/500字）   │
 │     ↓ 空值 → HTTP 400                │
 │  3. env.DB.prepare(INSERT)           │
 │        .bind(name, message).run()    │
 │     ↓                                │
 │  4. return { success: true }         │
 └──────────────────────────────────────┘
```

---

## 本地開發 vs 正式環境

```
  本地開發（make dev）                    正式環境（make deploy）
 ┌────────────────────────────┐          ┌──────────────────────────────┐
 │  localhost:8788            │          │  cf-guestbook.pages.dev      │
 │                            │          │                              │
 │  ┌──────────────────────┐  │          │  ┌────────────────────────┐  │
 │  │  wrangler pages dev  │  │          │  │  Cloudflare Functions  │  │
 │  │  （模擬 Functions）  │  │          │  │  （全球邊緣節點）      │  │
 │  └──────────┬───────────┘  │          │  └──────────┬─────────────┘  │
 │             │              │          │             │                │
 │  ┌──────────┴───────────┐  │          │  ┌──────────┴─────────────┐  │
 │  │  .wrangler/state/    │  │          │  │  Cloudflare 雲端儲存   │  │
 │  │  ├── kv/             │  │          │  │  ├── KV  VISITS        │  │
 │  │  └── d1/*.sqlite     │  │          │  │  └── D1  guestbook     │  │
 │  └──────────────────────┘  │          │  └────────────────────────┘  │
 └────────────────────────────┘          └──────────────────────────────┘
           程式碼結構完全一致，make deploy 即可切換到正式環境
```

---

## 部署流程

```
  首次部署
  ─────────────────────────────────────────────────────────
  make install  →  npx wrangler login  →  make setup  →  make deploy
       │                  │                   │               │
  安裝 node_modules    瀏覽器授權          建立 KV + D1      上傳 public/
                       （只需一次）        寫入 wrangler.toml  + functions/
                                          自動取得真實 ID

  後續更新
  ─────────────────────────────────────────────────────────
  （改完程式碼後）make deploy
```
