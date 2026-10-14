# 不用再配伺服器了！這套 Next.js + Cloudflare 模板，一個人零成本搞定全端出海

作為開發者，我們都想快速驗證自己的想法，尤其是在海外市場。但一想到要配伺服器、搞資料庫、CDN、CI/CD，一個人基本就被勸退了。

這篇文章想分享一個開源模板，它把這套事全包了。

核心就是：**一個人、零成本、用 Next.js + Cloudflare 生態搞定全端出海。**

---

- **GitHub 倉庫：** [TangSY/edge-next-starter](https://github.com/TangSY/edge-next-starter)
- **線上 Demo：** [7723b3e2.cloudflare-worker-template-prod.pages.dev](https://7723b3e2.cloudflare-worker-template-prod.pages.dev/)

---

這篇文章特別適合：獨立開發者、早期新創團隊，或者任何需要快速驗證海外市場的工程師。

## 為什麼說「一個人就能搞定」？

說「一個人就能搞」，不是吹牛。核心是這個模板已經把最繁瑣的「髒活累活」幹完了。

你不用再從零開始搭架子。這個模板把一個全端應用需要的東西都分好類，並提供了最佳實踐：

- **前端：** Next.js 15.5.2（App Router + TypeScript）
- **後端：** Cloudflare Pages Functions（Edge Runtime），API 路由開箱即用
- **資料：** Prisma ORM + D1 資料庫
- **儲存：** R2 物件儲存
- **快取：** KV 鍵值儲存
- **觀測：** 結構化日誌 + Analytics 事件
- **工程：** 統一回應／錯誤／中介軟體／速率限制
- **測試：** Vitest
- **部署：** Wrangler + GitHub Actions

你能真正專注於業務本身：頁面、資料模型、介面邏輯。其餘的工程必需品，例如日誌、限流、錯誤處理、回應格式、快取、上傳、健康檢查、多環境配置與 CI/CD，都已預設提供。

對你來說，這意味著：

1. **節省大量時間：** 減少 70% 以上的重複配置工作。
2. **不用糾結選型：** 直接使用 Next.js + Cloudflare 這套統一的現代技術棧。
3. **部署無憂：** 環境變數、CI/CD 腳本與文件都已備好，照著跑就行。

---

## 輕鬆上手：5 步跑通全端

上手不難，這個模板把關鍵步驟都腳本化了。你只需要準備好這幾樣東西：

- Node.js >= 20（專案裡有 `.nvmrc`）
- pnpm >= 8
- 一個 Cloudflare 帳戶（需要開通 Pages、Workers、D1、R2、KV）

然後，跟著 `QUICKSTART-zh.md` 文件，5 步就能跑起來：

1. **初始化：** `pnpm i` 裝好依賴，`wrangler login` 登入 Cloudflare。
2. **配環境：** 配置 `wrangler.toml`（本地）、`wrangler.test.toml`（測試）和 `wrangler.prod.toml`（正式環境）。
3. **建資源：**
   - D1（資料庫）：`pnpm run db:migrate:local`
   - R2（儲存）：`pnpm run r2:create:test`（或 `prod`）
   - KV（快取）：`pnpm run kv:create:test`（或 `prod`）
4. **跑開發：**
   - 本地開發（Next.js）：`pnpm dev`
   - 模擬 Cloudflare 環境：`pnpm run cf:dev`
5. **部署上線：**
   - 測試環境：`pnpm run pages:deploy:test`
   - 正式環境：`pnpm run pages:deploy:prod`

如果順利，你一天內就能跑通 Demo，一週內就能上線 MVP，去驗證海外訪問體驗。

---

## 零成本起步：Cloudflare 免費額度有多香？

「完全免費」是這套方案最大的誘惑。Cloudflare 的 Free Tier 真的非常大方，用來做 MVP 甚至中小流量專案都綽綽有餘，但實際額度仍要以 Cloudflare 官方最新文件為準。

- **Pages（靜態託管）**
  - 專案數量：100 個
  - 每月建置：500 次
  - 頻寬／靜態請求：無限制
- **Pages Functions（與 Workers 共享額度）**
  - 每日請求：100,000 次
  - CPU 時間：每次請求 10 毫秒
- **D1 Database（資料庫）**
  - 資料庫數量：10 個
  - 總儲存：5 GB（所有資料庫共享）
- **R2 Storage（物件儲存）**
  - **核心優勢：零出站費用（Egress Zero）**，這點對出海非常重要。

這些額度對個人開發者相當友善。你能以**零伺服器成本**跑一個真實的全端應用。

---

## Cloudflare 前後端架設最佳實踐

在 Cloudflare 架設前後端網站，最佳實踐是：**用 Cloudflare Pages 託管前端（React / Vue / Astro 等），用 Pages Functions 或 Cloudflare Workers 處理後端 API**，達成免伺服器、全域 CDN 加速、免費的高效能架構。

```mermaid
graph LR
    subgraph Dev["本地開發"]
        Code["前端專案\n(React / Vue / Astro\nNext.js...)"]
        Fn["後端邏輯\n/functions 或\nWorker 腳本"]
    end

    subgraph Git["版本控制"]
        GH["GitHub / GitLab"]
    end

    subgraph CF["☁️ Cloudflare"]
        Pages["Pages\n前端靜態 / SSR\n自動 CI/CD"]
        Functions["Pages Functions\n或 Workers\nEdge Runtime API"]
        D1[("D1\nSQL 資料庫")]
        KV[("KV\nNoSQL 快取")]
        SSL["自動 SSL\n自訂網域"]
    end

    Code -->|git push| GH
    Fn -->|git push| GH
    GH -->|觸發建置| Pages
    GH -->|自動部署| Functions
    Pages --- Functions
    Functions --> D1
    Functions --> KV
    Pages --> SSL
```

### 前後端架設步驟

#### 步驟 1：準備代碼

將前端專案 push 到 GitHub 或 GitLab。

```bash
git add .
git commit -m "init project"
git push origin main
```

#### 步驟 2：部署前端（Pages）

1. 登入 Cloudflare，進入「**Workers & Pages**」>「**Create application**」>「**Pages**」>「**Connect to Git**」
2. 選擇你的 Git 專案
3. 依框架設定建構指令與輸出目錄：

| 框架 | 建構指令 | 輸出目錄 |
| --- | --- | --- |
| React (Vite) | `npm run build` | `dist` |
| Next.js | `npm run build` | `.next` / `out` |
| Vue | `npm run build` | `dist` |
| Astro | `npm run build` | `dist` |
| SvelteKit | `npm run build` | `build` |

4. 點擊「**Save and Deploy**」，Cloudflare 自動建置並部署。

#### 步驟 3：配置後端（兩種方法）

**方法 A（推薦）— Pages Functions**

在專案根目錄建立 `/functions` 資料夾，檔案即路由，隨前端一起部署：

```text
my-project/
├── src/               ← 前端源碼
├── functions/
│   ├── api/
│   │   ├── hello.ts   → GET /api/hello
│   │   └── users/
│   │       └── index.ts → GET/POST /api/users
│   └── _middleware.ts ← 全域中介軟體
├── package.json
└── wrangler.toml
```

```typescript
// functions/api/hello.ts
export const onRequest: PagesFunction = async (ctx) => {
  return Response.json({ message: "Hello from Edge!" });
};
```

**方法 B — 獨立 Cloudflare Workers**

適用於需要與前端分離部署的獨立後端服務：

```bash
# 建立 Worker 專案
npm create cloudflare@latest my-api -- --type=worker

# 部署
npx wrangler deploy
```

#### 步驟 4：整合資料庫

```bash
# 建立 D1 資料庫
npx wrangler d1 create my-database

# 在 wrangler.toml 綁定
# [[d1_databases]]
# binding = "DB"
# database_name = "my-database"
# database_id = "xxxx-xxxx-xxxx"

# 建立 KV 命名空間
npx wrangler kv namespace create MY_KV
```

```typescript
// 在 Functions 中使用 D1
export const onRequest: PagesFunction<{ DB: D1Database }> = async (ctx) => {
  const result = await ctx.env.DB.prepare("SELECT * FROM users").all();
  return Response.json(result.results);
};
```

#### 步驟 5：綁定自訂網域

在 Pages 設定的「**Custom domains**」中加入你的網域，Cloudflare 會**自動處理 SSL 憑證**。

```text
your-domain.com        → Pages 前端
your-domain.com/api/*  → Pages Functions 自動路由
api.your-domain.com    → 獨立 Workers（方法 B）
```

---

### 關鍵優勢

| 優勢 | 說明 |
| --- | --- |
| **全域部署** | 內容自動分發至 200+ 邊緣節點，存取速度極快 |
| **CI/CD 自動化** | Git Push 即觸發建置與部署，無需額外配置 |
| **無伺服器** | 無需管理伺服器，自動擴縮容，零維運成本 |
| **整合資料庫** | 搭配 D1（SQL）+ KV（NoSQL）實現真正無伺服器全棧 |
| **自動 SSL** | 自訂網域自動頒發與續期 TLS 憑證 |
| **免費起步** | Free Tier 即可跑真實全端應用，超量再升級 |

---

## 完整的生態：不只是拼湊

這個模板不是簡單把 Next.js 和 Cloudflare 拼在一起，而是把它們的原生生態串成一個有機整體。它已經為你規劃好每個元件的職責：

```mermaid
graph TB
    User(["🌍 使用者"])

    subgraph CF["☁️ Cloudflare 全球邊緣（200+ POP）"]
        direction TB
        subgraph App["Next.js on Cloudflare Pages"]
            FE["📄 前端頁面\nApp Router · SSR / SSG / ISR\nTailwind CSS · TypeScript"]
            BE["⚡ Edge API\nPages Functions · Edge Runtime\napp/api/* 路由"]
        end
        subgraph DataLayer["資料與儲存"]
            D1[("🗄️ D1\nSQLite + Prisma ORM")]
            KV[("⚡ KV\n鍵值快取 + 滑動視窗限流")]
            R2[("📦 R2\n物件儲存 · 零出站費")]
        end
        subgraph Obs["可觀測性"]
            AE["📊 Analytics Engine\n業務事件打點"]
            LOG["📝 結構化日誌 pino\nJSON（正式）/ Pretty（開發）"]
        end
    end

    subgraph Deploy["部署流程"]
        GH["🐙 GitHub Actions\nCI / CD"]
        WR["🔧 Wrangler CLI\n多環境部署"]
    end

    User -->|"就近接入（低延遲）"| FE
    User <-->|"HTTPS API 請求"| BE
    FE <-->|"SSR 資料"| BE
    BE -->|"Prisma CRUD"| D1
    BE <-->|"快取讀寫"| KV
    BE -->|"上傳 / 下載"| R2
    BE -.->|"事件打點"| AE
    BE -.->|"請求 & 慢查詢日誌"| LOG
    GH -->|"push / merge 觸發"| WR
    WR -->|"deploy"| App
```

- **前端／頁面：** Next.js App Router 負責承載 UI，SSR、SSG、ISR 都具備，Tailwind CSS 也已配好。
- **後端／API：** 執行在 Edge Runtime 上的 Next.js 路由（`app/api/*`）負責處理業務邏輯。
- **資料／ORM：** Prisma 配合 `@prisma/adapter-d1` 連接 D1 資料庫，享受型別安全與關聯查詢。
- **快取：** KV 作為高效能鍵值儲存，用於快取熱點資料。
- **儲存：** R2 負責物件儲存，適合圖片與附件上傳，對 CDN 友好。
- **可觀測性：** 結構化日誌（`pino`）與 Analytics Engine 負責事件打點，方便排查問題。
- **部署：** Wrangler 統一驅動本地開發與多環境（`local`、`test`、`prod`）部署。
- **規範／工程：** 統一的錯誤類型、Repository 模式分層、CI/CD 自動化。

你不需要再折騰「如何把這些拼好」，直接用即可。

---

## 跟傳統 VPS 有什麼不一樣？

如果只用一句話總結：

**傳統 VPS 是你自己養一台機器；Next.js + Cloudflare 則是把前端、API、快取、儲存等能力拆給平台代管。**

### 架構對照

#### 傳統 VPS

```text
   使用者
     │
     ▼
  ┌──────┐
  │ DNS  │
  └──┬───┘
     │
     ▼
  ┌──────────────────┐
  │  Nginx / Apache  │  ← 反向代理，你自己管
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │    App Server    │  ← 後端服務，你自己管
  │ (Node / Go ...)  │
  └──┬────────┬───┬──┘
     │        │   │
     ▼        ▼   ▼
  ┌──────┐ ┌─────┐ ┌──────────────┐
  │  DB  │ │Redis│ │ 本機 / S3    │
  │(PG / │ │ 快取│ │  物件儲存    │
  │MySQL)│ │     │ │              │
  └──────┘ └─────┘ └──────────────┘

  ⚠  單一機房、固定月費、維運全靠自己
```

#### Next.js + Cloudflare

```text
   使用者（全球各地）
         │  就近接入 · 低延遲
         ▼
  ┌──────────────────────────────────────────────────┐
  │        Cloudflare 全球邊緣（200+ POP）           │
  │                                                  │
  │  ┌──────────────────────────────────────────┐    │
  │  │      Pages（靜態資產 / SSR 頁面）        │    │
  │  │   Next.js App Router · Tailwind CSS      │    │
  │  └───────────────────┬──────────────────────┘    │
  │                      │                           │
  │  ┌───────────────────▼─────────────────────┐     │
  │  │      Functions（Edge Runtime API）      │     │
  │  │      Next.js app/api/* 路由             │     │
  │  └────────┬────────────┬────────┬──────────┘     │
  │           │            │        │                │
  │      ┌────▼────┐   ┌───▼────┐ ┌─▼──────┐         │
  │      │   D1    │   │  KV    │ │  R2    │         │
  │      │ 資料庫  │   │   快取 │ │  儲存  │         │
  │      │(SQLite) │   │ (限流) │ │(零出站 │         │
  │      └─────────┘   └────────┘ └────────┘         │
  │                                                  │
  │      平台代管 · 自動擴展 · 全球分散              │
  └──────────────────────────────────────────────────┘

  ✅  全球就近接入、按用量計費、零維運成本
```

### 核心差異比較

| 面向 | 傳統 VPS | Next.js + Cloudflare |
| --- | --- | --- |
| 核心模型 | 一台或多台你自己管理的伺服器 | 平台代管的 Edge / Serverless 服務 |
| 部署單位 | 主機、Container、Process | Pages、Functions、Workers |
| 維運責任 | 幾乎都要自己處理 | 大部分交給平台 |
| 擴充方式 | 加機器、配 Load Balancer、調 Nginx | 平台自動擴展為主 |
| 延遲表現 | 通常集中在單區機房 | 可利用全球邊緣節點 |
| 成本結構 | 固定月租 | 常見是低流量便宜、隨用量增加 |
| 上手速度 | 要先配好整套主機環境 | 很快，但要接受平台規則 |
| 自由度 | 很高 | 中高，但受平台限制 |
| 除錯方式 | SSH 進機器直接查 | 主要依賴平台日誌與本地模擬 |
| 狀態保存 | 本機磁碟、自己架 DB / Redis | D1、KV、R2、Durable Objects 等託管服務 |
| 適合場景 | 長連線、特殊服務、自訂環境 | MVP、內容站、API、全球訪問產品 |
| 主要風險 | 維運負擔、單點、備份遺漏 | 供應商綁定、執行限制較多 |

### 金流、資料庫、背景任務、WebSocket 的差異

| 面向 | 傳統 VPS | Next.js + Cloudflare |
| --- | --- | --- |
| 金流 | 後端可長駐，Webhook、排程、重試流程都自己掌控 | 能接金流 API 與 Webhook，但要配合無狀態、短生命週期的執行模型 |
| 資料庫 | 常直接連 PostgreSQL / MySQL，自管或買託管 DB | 常搭 D1、外部託管 DB，或 HTTP 型資料服務；連線模型與延遲要重新設計 |
| 背景任務 | 可用 `cron`、Supervisor、Queue Worker、Celery、Sidekiq 這類常駐 worker | 不適合傳統長駐 worker，通常改用 Queue、Cron Trigger、事件驅動拆小任務 |
| WebSocket | 適合長連線、Socket Server、自管 session 與連線狀態 | 可做，但限制較多；若是大量即時連線，通常要靠 Durable Objects 或外部即時服務 |
| 狀態管理 | 容易放在記憶體、本機檔案、Redis | 不能假設單機記憶體持久，狀態通常放 KV、D1、Durable Objects、R2 |
| 排程與重試 | 很直覺，直接在主機上跑 | 要依賴平台提供的排程與佇列能力 |

### 四個面向的直觀理解

#### 1. 金流

```text
VPS
┌────────┐   ┌──────────────┐   ┌──────────┐
│  前端  │──>│   你的 API   │──>│  金流商  │
└────────┘   └──────┬───────┘   └────┬─────┘
                    │                │ Webhook
              自己更新 DB      ───────▼────────
              自己重試補單     │ 回打固定後端  │
                               │ 更新 DB/重試  │
                               └──────────────┘

Cloudflare
┌────────┐   ┌──────────────┐   ┌──────────┐
│  前端  │──>│  Edge API    │──>│  金流商  │
└────────┘   └──────────────┘   └────┬─────┘
                                      │ Webhook
                               ───────▼─────────────────
                               │  Edge Function         │
                               │  狀態寫入 D1 / KV      │
                               │  重試靠 Queue / Trigger│
                               └────────────────────────┘
```

#### 2. 資料庫

```text
VPS
┌────────────┐                    ┌──────────────────┐
│ App Server │◄──── 長連線 ──────►│ PostgreSQL/MySQL │
└────────────┘                    └──────────────────┘
  （持久連線池，低延遲）                （同機房，快）

Cloudflare
┌───────────────┐                 ┌─────────────────────────────┐
│ Edge Function │──── 短請求 ────►│ D1 / HTTP DB / 外部託管 DB  │
└───────────────┘                 └─────────────────────────────┘
  （無狀態，每次請求建連）            （連線模型與延遲要重新設計）
```

#### 3. 背景任務

```text
VPS
                ┌─────────────────────────┐
Request ───────>│    App Server           │
                └──────┬──────────────────┘
                       │ 丟給常駐 Worker
                       ▼
                ┌──────────────┐
                │ Worker 常駐  │──> 寄信 / 轉檔 / 同步
                └──────────────┘     （慢慢跑完）

Cloudflare
                ┌─────────────────────────┐
Request ───────>│    Edge Function        │
                └──────┬──────────────────┘
                       │ 寫入 Queue
                       ▼
                ┌──────────────────┐
                │ Consumer /       │──> 分批小任務
                │ Cron Trigger     │     （短生命週期）
                └──────────────────┘
```

#### 4. WebSocket

```text
VPS
┌────────┐                    ┌──────────────────┐
│ Client │◄═══ 長連線 ═══════►│ WebSocket Server │
└────────┘                    └──────┬───────────┘
                                     │
                              ┌──────┴──────┐
                              │ Redis Pub/  │
                              │ Sub  &  DB  │
                              └─────────────┘

Cloudflare
┌────────┐     ┌───────────────────────────────────────────┐
│ Client │◄═══►│  Edge / Durable Objects / 第三方即時服務  │
└────────┘     └───────────────────────────────────────────┘
                 ⚠ 大量即時連線建議搭配 Durable Objects
                   或外部即時服務（如 Pusher / Ably）
```

### 實務上的選型建議

| 需求 | 較適合 |
| --- | --- |
| 官網、內容站、MVP、全球訪問 API | Cloudflare |
| 複雜後台、重背景任務、長連線服務 | VPS |
| 金流 + 一般 CRUD + 檔案上傳 | Cloudflare 可行 |
| 大量 WebSocket、遊戲、即時協作核心服務 | VPS 或專門即時架構 |
| 需要 root 權限、自訂系統套件 | VPS |

簡單說，**VPS 比較像自己養基礎設施；Cloudflare 比較像把基礎設施外包給平台，自己專注在產品與功能。**

---

## 為什麼說它適合「出海」？

海外使用者最關心兩件事：**訪問速度**和**穩定性**。

這套方案天生就是為全球訪問設計的：

```text
全球邊緣加速示意
──────────────────────────────────────────────────────────
  🇯🇵 日本 ────┐                         ┌──── 🇺🇸 美國
  🇹🇼 台灣 ────┤                         ├──── 🇬🇧 英國
  🇸🇬 新加坡 ──┼──────────────────────────┤──── 🇩🇪 德國
  🇦🇺 澳洲 ────┘         就近接入         └──── 🌍 其他
                              │
                ┌─────────────▼───────────────┐
                │   Cloudflare 全球 POP       │
                │      200+ 個節點            │
                │   （延遲通常 < 50ms）       │
                └─────────────┬───────────────┘
                              │
                ┌─────────────▼──────────────┐
                │        你的應用            │
                │   Pages（前端）            │
                │   Functions（API）         │
                └──────┬──────┬────────┬─────┘
                       │      │        │
                  ┌────▼───┐ ┌▼────┐  ┌▼─────────┐
                  │  D1    │ │ KV  │  │   R2     │
                  │ 資料庫 │ │快取 │  │ 零出站費 │
                  └────────┘ └─────┘  └──────────┘
```

1. **全球邊緣節點：** 你的應用和服務（Pages、Workers）都部署在 Cloudflare 的全球 POP 上，使用者可以就近接入，延遲自然更低。
2. **D1 邊緣資料庫：** 很適合輕中量業務，能減少資料庫跨區查詢延遲。
3. **R2 零出站費：** 海外使用者下載圖片或檔案時，不必支付高昂流量費，成本結構更漂亮。
4. **邊緣快取（KV）：** 以極低延遲服務熱點資料。
5. **輕鬆多環境：** 測試與正式環境分離，按分支策略（`develop -> test`、`main -> prod`）自動部署。

這套技術棧能讓你快速上線、穩定運行、低成本迭代，把精力真正花在試錯與打磨產品上。

---

## 模板裡的一些「私貨」：工程亮點

這部分是模板真正有價值的地方。只提供元件拼裝是不夠的，作者把正式環境中必備的工程實踐都標準化了。

```mermaid
graph TD
    A[User Request] --> B(Cloudflare Edge / Next.js API Route)

    subgraph "請求處理管線"
        B --> C(1. 統一中介軟體<br/>withMiddleware)
        C --> D(2. 速率限制<br/>withRateLimit)
        D --> E{3. 是否命中快取？<br/>withCache}
    end

    subgraph "資料與服務"
        K[("KV<br/>(Cache / Rate Limit)")]
        I[(D1 資料庫)]
        J[(R2 物件儲存)]
        L((可觀測性<br/>日誌 / Analytics))
    end

    subgraph "業務邏輯層"
        F(4. API 核心邏輯)
        G(5. 倉儲層<br/>withRepositories)
        H("6. Prisma Client（單例）")
    end

    M(Response)

    C -.-> L
    D --> K
    E -- "Hit（命中）" --> M
    E -- "Miss（未命中）" --> F
    F --> G
    G --> H
    H --> I
    F -- "例如：Upload API" --> J
    F -.-> L
    G -.-> L
    F --> M
    M --> A
```

1. **統一 API 回應與中介軟體**
   - `lib/api/response.ts` 定義 `success`／`error` 的結構，`errorResponse` 會自動映射錯誤類型與狀態碼。
   - `lib/api/middleware.ts` 會自動注入 `requestId`、記錄請求耗時，並追加追蹤標頭。

2. **錯誤類型體系**
   - `lib/errors/index.ts` 定義十多種常見錯誤類型，例如資料庫、驗證、認證、限流等。
   - `ERROR_STATUS_MAP` 統一管理 HTTP 狀態碼，讓錯誤處理更規範。

3. **結構化日誌（正式環境 JSON、開發環境 Pretty）**
   - `lib/logger/index.ts` 支援 `http()`、`performance()`、`query()` 等專用方法，也能配置慢查詢門檻。

4. **Analytics 事件打點**
   - `lib/analytics/index.ts` 定義各種業務事件，可選擇 Sink（例如寫入 D1 或 KV），失敗時自動降級到日誌。

5. **速率限制（KV 滑動視窗）**
   - `lib/api/rate-limit.ts` 利用 KV 的原子性實作滑動視窗限流。預設每分鐘 300 次，也能在路由上自訂，例如限制建立使用者介面為 `10/min`。

6. **Repository 模式 + Prisma + D1 單例**
   - `repositories/*` 封裝資料存取，`lib/api/database.ts` 提供 `withRepositories` 注入。
   - `lib/db/client.ts` 對 Prisma Client 做了**單例重用**。這很關鍵，能減少約 50 到 100 毫秒的資料庫冷啟動開銷。

7. **開箱即用的快取裝飾器**
   - `lib/cache/client.ts` 提供 `withCache(key, fn, ttl)` 裝飾器，自動處理快取命中、穿透與回源。

8. **封裝 R2 上傳與下載**
   - `lib/r2/client.ts` 封裝上傳與下載，`app/api/upload/route.ts` 是完整範例，你不需要直接面對複雜的 S3 SDK。

9. **健康檢查端點**
   - `app/api/health/route.ts` 提供健康檢查端點，方便 CI/CD 或監控系統檢測 D1、R2、KV 是否可用。

10. **CI/CD 與變更記錄**
    - `.github/workflows/*` 負責 CI 與部署。
    - `release-please` 用來自動管理 `CHANGELOG`。

---

## 實踐路徑：從零到 MVP

我建議的實踐路徑如下：

### Day 1：跑通並上線 Demo

- Fork 專案，配置好 Cloudflare 帳戶與 Wrangler，建立 D1、R2、KV 並完成綁定。
- 在本地跑通 `pnpm dev` 和 `pnpm run cf:dev`，確認 Edge API 正常。
- 跑通遷移腳本，驗證 `/api/health`、`/api/users` 等核心介面。
- 部署到測試環境：`pnpm run pages:deploy:test`

### Day 2 到 Day 3：客製你的業務模型

- 修改 `prisma/schema.prisma`，加入自己的模型，例如 `Comment` 或 `Order`。
- 在 `repositories/*` 目錄新增自己的資料倉儲，可參考 `users.repository.ts`。
- 在 `app/api/*` 目錄新增自己的路由，統一使用 `withRepositories` + `withMiddleware`；需要快取與限流時，再加上 `withCache` / `withRateLimit`。
- 推到正式環境：`pnpm run pages:deploy:prod`，並觀察日誌與 Analytics 事件。

### Day 4 到 Day 7：出海驗證與優化

- 開始關注真實數據，對熱門介面（例如列表頁）加上 `withCache`。
- 保護寫操作（例如註冊、下單）與外部服務整合，調整限流策略。
- 透過 `logger.query`、`performance` 與 Analytics 觀測慢查詢與慢操作。
- 收集海外使用者回饋，快速迭代。

---

## 成本與擴展：免費起步，平滑升級

**免費層能跑多久？**

依作者經驗，做 MVP 和中小流量（日 10 萬請求）絕對夠用。5 GB 的 D1 儲存也能支撐一段時間，而 R2 的零出站費更是巨大的成本優勢。

**未來如何擴展？**

當你的業務開始成長後，這套架構也能平滑升級：

1. **資料：** 讀寫壓力變大時，先上讀快取（KV）；再不夠就考慮接入專業託管資料庫，例如 PlanetScale，讓 Edge 扮演 BFF 層。
2. **儲存：** R2 本身效能很強，後續重點通常在管理策略。
3. **觀測：** Analytics Engine 可以持久化資料，也能再對接外部可觀測平台。

---

## 常見問題（FAQ）

**Q1：為什麼選 Next.js + Cloudflare？**  
A：前端生態成熟，加上 Edge 原生執行時。對獨立開發者來說，沒有伺服器維護成本、全球 POP 優勢，以及 D1、R2、KV 的一體化，是很關鍵的決定因素。

**Q2：會不會很難上手？**  
A：如果你本來就熟 Next.js，幾乎沒有門檻。模板已經把資料庫連接、日誌、部署這些最麻煩的工程部分包好，你只需要寫業務。

**Q3：免費層真的夠用嗎？**  
A：對 MVP 和中小流量來說通常足夠。上線後持續觀察 Cloudflare 用量統計，快超額時再升級或優化即可。

**Q4：如何面向海外做優化？**  
A：核心就是盡量靠近使用者。善用邊緣快取（KV）、R2 零出站費，以及 SSR、SSG、ISR，減少跨區往返；同時為介面加上 `withCache` 和合理的 `Cache-Control` 標頭。

**Q5：如何擴展複雜業務？**  
A：透過 Repository 模式擴展資料存取層；在 API 層統一使用 `withRepositories` + `withMiddleware`。Prisma 本身也支援交易、分頁與過濾等能力。

---

## 結語：把精力還給產品

如果你也是獨立開發者或小團隊，正苦於出海專案的啟動成本與複雜度，希望這套模板能幫你省下大量搭建基礎設施的時間。

「一個人就能搞定出海全端」不是口號，而是一種可行的實踐。

---

### 立刻開始：一天內上線你的出海應用

別再猶豫了。你的下一個想法，不該死在繁瑣的伺服器配置上。

**立即 Fork 倉庫，開始構建：**  
[https://github.com/TangSY/edge-next-starter](https://github.com/TangSY/edge-next-starter)

祝你出海順利。

---

原文出處：[https://juejin.cn/post/7564921269491580943](https://juejin.cn/post/7564921269491580943)
