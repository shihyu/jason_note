# MA 黃金交叉策略回測系統 - Agent Team 開發計畫

## 專案目標
建立一個 Agent Team 來開發 MA 黃金交叉策略回測系統

---

## 專案目錄結構

所有程式碼集中在 `ma-golden-cross/` 資料夾下：

```
ma-golden-cross/
├── backend/
│   ├── data/
│   │   └── fetcher.py          — 使用 yfinance 抓取股票歷史數據
│   ├── indicators/
│   │   └── ma.py               — MA 指標計算模組
│   ├── backtest/
│   │   └── engine.py           — 回測引擎核心
│   ├── api/
│   │   ├── routes.py           — API 路由定義
│   │   └── schemas.py          — Request/Response 格式
│   ├── tests/
│   │   ├── test_ma.py          — MA 指標計算測試
│   │   ├── test_backtest.py    — 回測引擎測試
│   │   ├── test_api.py         — API 路由測試
│   │   ├── test_fetcher.py     — 數據抓取測試
│   │   └── sample_data.csv     — 測試用範例 K 線數據（離線備用）
│   └── requirements.txt        — Python 依賴
├── frontend/
│   └── index.html              — 前端頁面（HTML + CSS + JS）
├── e2e/
│   ├── tests/
│   │   ├── test_full_flow.py   — Playwright 端對端測試
│   │   └── test_chart.py       — 前端圖表驗證測試
│   └── playwright.config.py    — Playwright 配置
├── logs/                       — Agent 對話紀錄（Lead 每個 Phase 匯出）
│   ├── phase0_architect.log
│   ├── phase1_backend.log
│   ├── phase1_frontend.log
│   ├── phase2_api.log
│   ├── phase3_test.log
│   └── phase4_e2e.log
└── docs/
    └── architecture.md         — 架構師輸出的架構設計文件
```

---

## 團隊成員與分工

### 成員0：架構師（最先開始，規劃全局）

- **角色**：系統架構設計、技術決策、介面規格定義
- **任務**：在任何實作開始前，完成完整的架構規劃
- **輸出檔案**：
  - `ma-golden-cross/docs/architecture.md` — 完整架構設計文件
- **職責細節**：
  1. **需求分析**：釐清 MA 黃金交叉策略的完整需求，包含參數、數據源、輸出格式
  2. **模組拆分**：定義各模組的職責邊界、輸入/輸出介面規格
  3. **API 契約**：設計 RESTful API 的完整規格（路由、參數、回應格式、錯誤處理）
  4. **數據流設計**：繪製從數據抓取 → MA 計算 → 回測 → API → 前端的完整數據流
  5. **技術選型確認**：確認各模組的技術棧（yfinance、Flask、Chart.js）及版本
  6. **測試策略**：定義單元測試、整合測試、E2E 測試的範圍與工具
  7. **介面 Mock 定義**：為前端提供 mock data 規格，使前端可並行開發
- **oh-my-openagent 配置**：
  ```
  task(
    category="ultrabrain",
    run_in_background=false,
    load_skills=["brainstorming", "writing-plans"],
    description="Architecture design for MA golden cross backtest system",
    prompt="Design complete architecture for MA golden cross backtest system.
            Define module boundaries, API contracts (Flask RESTful), data flow,
            interface specs, mock data for frontend parallel dev.
            Output to ma-golden-cross/docs/architecture.md.
            Must include: fetcher.py interface, ma.py interface, engine.py interface,
            API routes spec, Chart.js dataset format, error response format."
  )
  ```
- **依賴**：無（最先執行，blocking — 其他成員等架構完成才開始）

---

### 成員1：後端工程師（核心實作）
- **任務**：實做數據抓取、MA 指標計算和回測引擎
- **輸出檔案**：
  - `ma-golden-cross/backend/data/fetcher.py` — 使用 yfinance 抓取股票歷史數據
  - `ma-golden-cross/backend/indicators/ma.py` — MA 指標計算模組
  - `ma-golden-cross/backend/backtest/engine.py` — 回測引擎核心
  - `ma-golden-cross/backend/requirements.txt` — Python 依賴清單
- **技術要求**：
  - 使用 `yfinance` 抓取真實股票數據（支援台股如 `2330.TW`、美股如 `AAPL`）
  - 純 Python 實作 MA 計算，不使用 TA-Lib
  - 嚴格遵循架構師定義的介面規格
- **oh-my-openagent 配置**：
  ```
  task(
    category="deep",
    run_in_background=true,
    load_skills=["test-driven-development"],
    description="Implement backend core: fetcher, MA indicator, backtest engine",
    prompt="Follow architecture.md specs. Implement fetcher.py, ma.py, engine.py with TDD. All code under ma-golden-cross/backend/"
  )
  ```
- **依賴**：成員0 完成架構設計後開始

---

### 成員2：API 工程師
- **任務**：實做 RESTful API 供前端使用
- **輸出檔案**：
  - `ma-golden-cross/backend/api/routes.py` — API 路由定義
  - `ma-golden-cross/backend/api/schemas.py` — Request/Response 格式
- **技術要求**：使用 Flask 框架實作 RESTful API，嚴格遵循架構師定義的 API 契約
- **oh-my-openagent 配置**：
  ```
  task(
    category="quick",
    run_in_background=true,
    load_skills=["test-driven-development"],
    description="Implement RESTful API routes and schemas",
    prompt="Follow architecture.md API contract. Implement routes.py and schemas.py under ma-golden-cross/backend/api/"
  )
  ```
- **依賴**：成員0 + 成員1 完成後開始（需 import 後端模組）

---

### 成員3：前端工程師
- **任務**：實做前端介面顯示回測結果
- **輸出檔案**：
  - `ma-golden-cross/frontend/index.html` — 前端頁面（HTML + CSS + JS）
- **技術要求**：使用 Chart.js 畫 K 線和 MA 線，標記黃金交叉點
- **oh-my-openagent 配置**：
  ```
  task(
    category="visual-engineering",
    run_in_background=true,
    load_skills=["frontend-design", "beautiful-ui"],
    description="Implement frontend UI with Chart.js",
    prompt="Build frontend with Chart.js for K-line, MA lines, and golden cross markers. Use mock data from architecture.md first, then wire to real API. Output to ma-golden-cross/frontend/index.html"
  )
  ```
- **依賴**：成員0 完成後可並行開發（使用架構師定義的 mock data），API 串接需等成員2 完成

---

### 成員4：測試工程師（單元測試 + 整合測試）
- **任務**：實做單元測試和整合測試
- **輸出檔案**：
  - `ma-golden-cross/backend/tests/test_ma.py` — MA 指標計算測試
  - `ma-golden-cross/backend/tests/test_backtest.py` — 回測引擎測試
  - `ma-golden-cross/backend/tests/test_api.py` — API 路由測試
  - `ma-golden-cross/backend/tests/test_fetcher.py` — 數據抓取測試
  - `ma-golden-cross/backend/tests/sample_data.csv` — 測試用範例 K 線數據（離線備用）
- **技術要求**：
  - 使用 pytest 框架
  - 用已驗證的數據確保正確性
- **oh-my-openagent 配置**：
  ```
  task(
    category="deep",
    run_in_background=true,
    load_skills=["test-driven-development", "systematic-debugging"],
    description="Implement unit and integration tests",
    prompt="Write comprehensive tests for all backend modules. Use pytest. Verify against known data. Output to ma-golden-cross/backend/tests/"
  )
  ```
- **依賴**：成員1 完成後開始單元測試，成員2 完成後開始 API 測試

---

### 成員5：E2E 驗證工程師（Playwright，最終驗收）

- **角色**：使用 Playwright 進行端對端自動化驗證
- **任務**：透過真實瀏覽器操作驗證整個系統功能，確保每個功能點實際可用
- **輸出檔案**：
  - `ma-golden-cross/e2e/tests/test_full_flow.py` — 完整端對端流程測試
  - `ma-golden-cross/e2e/tests/test_chart.py` — 前端圖表視覺驗證
  - `ma-golden-cross/e2e/playwright.config.py` — Playwright 配置
- **驗證項目**（必須全部通過才算驗收成功）：

  | # | 驗證項目 | 驗證方式 |
  |---|---------|---------|
  | 1 | 前端頁面可載入 | `page.goto()` + 確認無 console error |
  | 2 | 輸入股票代碼並提交 | `page.fill()` + `page.click()` |
  | 3 | API 回應正確 | `page.expect_response()` 攔截 API 呼叫，驗證 JSON 結構 |
  | 4 | K 線圖表顯示 | `page.locator('canvas')` 確認 Chart.js canvas 存在且有繪製 |
  | 5 | MA 線顯示 | 截圖比對或驗證 Chart.js dataset 數量 |
  | 6 | 黃金交叉標記存在 | 驗證交叉點標記元素或 dataset |
  | 7 | 回測結果數據正確 | 驗證頁面顯示的交易次數、勝率等與 API 回傳一致 |
  | 8 | 錯誤處理 | 輸入無效股票代碼，確認顯示錯誤訊息而非白屏 |

- **為什麼需要 Playwright**：
  > Agent 宣稱「驗收測試通過」但實際內容不正確的問題，根本原因是單元測試只驗證邏輯正確性，
  > 無法驗證「整個系統串接起來後，使用者看到的結果是否正確」。
  > Playwright 透過真實瀏覽器操作，模擬使用者行為，能捕捉到整合時的錯誤。

- **oh-my-openagent 配置**：
  ```
  task(
    category="deep",
    run_in_background=false,
    load_skills=["e2e-verify", "systematic-debugging"],
    description="E2E verification with Playwright - final acceptance gate",
    prompt="Run Playwright E2E tests against the running system. Start Flask server, open browser, verify all 8 acceptance criteria. Screenshots on failure. This is the FINAL gate - do not pass until ALL tests are green with real browser verification."
  )
  ```
- **依賴**：所有其他成員完成後最後執行
- **驗收紀律**：
  - E2E 測試失敗時，回報具體失敗截圖與 DOM 狀態給 Lead
  - Lead 指派回原模組負責人修復
  - 修復後必須重新執行全部 E2E 測試（不允許只跑單一測試）

---

## 策略參數定義

| 參數 | 設定值 | 說明 |
|------|--------|------|
| 短期 MA | 5 日 | 快速均線 |
| 長期 MA | 20 日 | 慢速均線 |
| 黃金交叉 | 短期 MA 上穿長期 MA | 買入訊號 |
| 死亡交叉 | 短期 MA 下穿長期 MA | 賣出訊號 |

---

## 數據來源

使用 `yfinance` 套件抓取真實股票歷史數據：

```python
import yfinance as yf

# 台股範例
df = yf.download("2330.TW", start="2024-01-01", end="2024-12-31")

# 美股範例
df = yf.download("AAPL", start="2024-01-01", end="2024-12-31")
```

### `backend/data/fetcher.py` 介面規格

```python
def fetch_stock_data(symbol: str, start: str, end: str) -> pd.DataFrame:
    """
    抓取股票歷史 K 線數據

    Args:
        symbol: 股票代碼（如 "2330.TW", "AAPL"）
        start: 開始日期（如 "2024-01-01"）
        end: 結束日期（如 "2024-12-31"）

    Returns:
        DataFrame with columns: date, open, high, low, close, volume
    """
```

---

## 數據格式

### K 線數據（DataFrame）
```
date,open,high,low,close,volume
2024-01-02,595.0,600.0,590.0,598.0,25000000
...
```

### 輸出：回測結果
```json
{
  "total_trades": 10,
  "win_rate": 0.6,
  "total_profit": 1500.0,
  "max_drawdown": 200.0,
  "trades": [
    {
      "entry_date": "2024-01-05",
      "entry_price": 101.0,
      "exit_date": "2024-01-10",
      "exit_price": 105.0,
      "profit": 400.0,
      "type": "golden_cross"
    }
  ]
}
```

---

## 任務依賴關係圖

```
成員0 (架構師) ──┬──> 成員1 (後端) ──┬──> 成員2 (API) ──┬──> 成員5 (E2E 驗證)
                │                  │                  │
                ├──> 成員3 (前端UI) │  [並行 mock 開發] │
                │                  │                  │
                │                  └──> 成員4 (單元測試) │
                │                                     │
                └─────────────────────────────────────>│
```

| 成員 | 角色 | 依賴 | 說明 |
|------|------|-------|------|
| 成員0 | 架構師 | 無 | 最先開始，輸出架構文件供所有人參考 |
| 成員1 | 後端工程師 | 成員0 | 等架構設計完成 |
| 成員2 | API 工程師 | 成員0 + 成員1 | 等後端模組完成 |
| 成員3 | 前端工程師 | 成員0 | UI 可與成員1 並行（使用架構師的 mock data），串接需等 API |
| 成員4 | 測試工程師 | 成員1 + 成員2 | 單元測試等成員1，API 測試等成員2 |
| 成員5 | E2E 驗證工程師 | 全部 | 所有開發完成後，最終驗收關卡 |

---

## 執行模式

### Lead 職責
- 負責任務分配、協調、進度追蹤
- 使用 `task()` 分派工作給各成員，設定適當的 `category` 和 `load_skills`
- 可並行的任務使用 `run_in_background=true` 同時啟動
- **協調記錄**：使用 `task_create` / `task_update` 記錄每個成員的進度狀態
  - 每個成員啟動時建立 task（含 `blockedBy` 依賴）
  - 完成時 `task_update(status="completed")`
  - 失敗時記錄原因到 task description
- **事後追溯**：所有 agent 對話自動記錄在 session 中，可用 `session_list` / `session_read` / `session_search` 查詢
- **自動對話紀錄**：Lead 必須載入 `session-logger` skill，自動完成以下工作：
  - 任務開始時建立 `logs/` 目錄
  - 每個 Phase 完成後寫入 phase summary
  - 每個 background task 完成後記錄到 `background_tasks.jsonl`
  - 全部完成後自動匯出完整 session JSON + 生成可讀報告
  - Log 檔集中在 `ma-golden-cross/logs/` 目錄，方便事後追查問題

### 執行流程

```
Phase 0: 架構設計
  └─ 成員0 (架構師) — category="ultrabrain", blocking
      輸出：architecture.md（含模組介面、API 契約、mock data）

Phase 1: 核心開發（可並行）
  ├─ 成員1 (後端) — category="deep", background
  └─ 成員3 (前端 mock) — category="visual-engineering", background

Phase 2: 整合開發
  ├─ 成員2 (API) — category="quick", background（等成員1 完成）
  └─ 成員3 (前端串接) — 等成員2 完成後串接真實 API

Phase 3: 測試
  └─ 成員4 (測試) — category="deep", background

Phase 4: E2E 驗證（最終關卡）
  └─ 成員5 (Playwright) — category="deep", blocking
      啟動 Flask server → 開啟瀏覽器 → 逐項驗證 → 截圖存證
```

### Teammate 職責
- 負責實際程式碼實作，完成後回報進度並協助解決問題
- 每個成員完成任務後通知 Lead

### Bug 修復原則
- 成員4（測試）或成員5（E2E）發現問題後回報 Lead
- Lead 指派回原模組負責人修復
- 修復後由成員4 重新驗證單元測試，成員5 重新執行 E2E 測試

### Skill 使用原則
每位成員必須按照自己的任務職責，主動檢查並使用適合的 skill。這是強制要求，不可省略：

- **開發前**：使用 `brainstorming` skill 進行方案構思，使用 `writing-plans` skill 撰寫實作計畫
- **實作中**：使用 `test-driven-development` skill 以 TDD 方式開發，確保先寫測試再寫實作
- **除錯時**：使用 `systematic-debugging` skill 進行系統化除錯，禁止盲目修改
- **完成後**：使用 `requesting-code-review` skill 提交程式碼審查，使用 `verification-before-completion` skill 驗證成果

### 各角色適用 skill 與 oh-my-openagent category 對照

| 成員 | category | 必須使用的 Skill |
|------|----------|-----------------|
| 成員0（架構師） | `ultrabrain` | `brainstorming`、`writing-plans` |
| 成員1（後端） | `deep` | `brainstorming`、`writing-plans`、`test-driven-development`、`systematic-debugging` |
| 成員2（API） | `quick` | `brainstorming`、`test-driven-development`、`systematic-debugging` |
| 成員3（前端） | `visual-engineering` | `brainstorming`、`frontend-design`、`beautiful-ui` |
| 成員4（測試） | `deep` | `test-driven-development`、`systematic-debugging`、`requesting-code-review` |
| 成員5（E2E 驗證） | `deep` | `e2e-verify`、`systematic-debugging`、`verification-before-completion` |

- **判斷原則**：即使只有 1% 的可能性某個 skill 適用於當前任務，也必須先調用該 skill 確認
- **違反處理**：若成員未使用適當 skill 就提交成果，Lead 應退回並要求重做

---

## oh-my-openagent 配置

### 已配置的檔案

| 檔案 | 位置 | 用途 |
|------|------|------|
| 全局 agent 配置 | `~/.config/opencode/oh-my-openagent.json` | 所有 agent/category 使用 MiniMax-M2.7-highspeed |
| 全局 opencode 配置 | `~/.config/opencode/opencode.json` | plugin、MCP（Playwright、Tavily、Context7）|
| 專案級配置 | `.opencode/oh-my-opencode.jsonc` | background agent 並行數、task system 啟用 |
| E2E 驗證 Skill | `~/.config/opencode/skills/e2e-verify/SKILL.md` | Playwright 端對端驗收測試（全局 skill，自動載入） |
| Session Logger Skill | `~/.config/opencode/skills/session-logger/SKILL.md` | 自動匯出 agent 對話紀錄到 logs/（全局 skill） |
| 工作守則 | `~/.config/opencode/AGENTS.md` | TDD 流程、Makefile 規範、驗證檢查清單 |

### Category → 模型映射（繼承全局配置）

所有 category 統一使用 `minimax/MiniMax-M2.7-highspeed`：

| Category | 用途 | 對應成員 |
|----------|------|---------|
| `ultrabrain` | 架構決策、複雜推理 | 成員0（架構師） |
| `deep` | 自主研究與深度執行 | 成員1（後端）、成員4（測試）、成員5（E2E） |
| `quick` | 單檔修改、簡單任務 | 成員2（API） |
| `visual-engineering` | 前端、UI/UX | 成員3（前端） |

### MCP 服務（已在全局配置中啟用）

| MCP | 用途 | 使用場景 |
|-----|------|---------|
| `playwright` | 瀏覽器自動化 | 成員5 E2E 驗證 |
| `tavily` | 網路搜尋 | 架構師查找技術方案 |
| `context7` | 官方文件查詢 | 所有成員查 Flask/Chart.js/yfinance 文件 |

### 如何在 opencode 中執行此計畫

在 `src/ai_agent/` 目錄下啟動 opencode，輸入：

```
閱讀 agent-team-ma-strategy.md，按照計畫的 Phase 順序執行：
1. 載入 session-logger skill，在 ma-golden-cross/logs/ 自動記錄所有對話
2. Phase 0: 先以 ultrabrain category 完成架構設計
3. Phase 1: 並行啟動後端（deep）和前端 mock（visual-engineering）
4. Phase 2: 等後端完成後啟動 API（quick）
5. Phase 3: 啟動測試（deep）
6. Phase 4: 最後用 e2e-verify skill 做 Playwright 驗收
7. 全部完成後，匯出完整 session JSON 並生成可讀報告到 logs/
所有程式碼集中在 ma-golden-cross/ 資料夾下。
```

---

## 驗收標準

1. 可透過 yfinance 抓取真實股票數據（台股 `2330.TW`、美股 `AAPL` 皆可運行）
2. MA 計算正確（5日、20日均線與預期一致）
3. 黃金交叉/死亡交叉判斷正確
4. 回測引擎輸出格式符合規格
5. API 可正常呼叫並返回正確資料（支援傳入股票代碼與日期區間）
6. 前端可顯示 K 線、MA 線及交叉點標記
7. 所有單元測試通過（pytest）
8. **所有 E2E 測試通過（Playwright，透過真實瀏覽器驗證）**
9. 端對端可運行：輸入股票代碼 → 抓取數據 → 計算 MA → 回測 → 前端顯示結果
10. **E2E 截圖存證**：驗證通過時保留最終截圖作為驗收證據
