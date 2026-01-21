# FinLab-AI 專案說明

## 專案概述

**FinLab-AI** 是一個**台股量化交易工具包插件**，為 FinLab Python 套件提供 AI 整合功能。讓交易者和研究人員能透過 AI 助手建立、回測和執行交易策略。

**標語:** "Let AI discover your next alpha."

---

## 專案統計

| 項目 | 數值 |
|------|------|
| 總大小 | 23 MB |
| 文件行數 | 5,038 行 markdown |
| 檔案數 | 18 個追蹤檔案 |
| 提交次數 | 73 commits |
| 授權 | MIT |

---

## 專案結構

```
finlab-ai/
├── assets/                          # 行銷與展示素材
│   ├── banner.png
│   ├── demo-chart.png
│   ├── demo-data.png
│   └── demo.gif
├── .claude-plugin/                  # Claude 插件市場設定
│   └── marketplace.json
├── finlab-plugin/                   # 主要插件目錄
│   ├── .claude-plugin/
│   │   └── plugin.json              # 插件元資料
│   └── skills/finlab/               # AI 技能文件 (核心)
│       ├── SKILL.md                 # 執行哲學與核心指南
│       ├── README.md                # 技能概述
│       ├── data-reference.md        # 資料 API 目錄 (900+ 欄位)
│       ├── backtesting-reference.md # sim() API 與回測指南
│       ├── dataframe-reference.md   # FinLabDataFrame 方法
│       ├── factor-examples.md       # 60+ 策略範例
│       ├── factor-analysis-reference.md # IC、Shapley、因子分析
│       ├── trading-reference.md     # 實盤交易與券商整合
│       ├── best-practices.md        # 反模式與前視偏差
│       └── machine-learning-reference.md # ML 特徵工程
├── workers/                         # Cloudflare Workers 後端
│   ├── src/
│   │   └── index.ts                 # MCP 伺服器實作 (TypeScript)
│   ├── build.mjs                    # 建置腳本 - 產生 docs.ts
│   ├── build.py                     # Python 替代建置腳本
│   ├── package.json
│   ├── tsconfig.json
│   └── wrangler.toml                # Cloudflare Workers 設定
├── README.md                        # 主文件 (英文)
├── README.zh-TW.md                  # 文件 (繁體中文)
├── server.json                      # MCP 伺服器註冊
└── FEEDBACK_PROCESSOR.txt           # 使用者回饋處理指南
```

---

## 核心元件

### 1. Skill 文件 (`finlab-plugin/skills/finlab/`)

**核心元件**，包含完整的 AI 技能文件：

| 文件 | 用途 | 行數 |
|------|------|------|
| **SKILL.md** | 執行哲學與前置條件 | ~422 |
| **data-reference.md** | API 文件 (900+ 資料欄位) | ~517 |
| **backtesting-reference.md** | 回測工作流程 | ~413 |
| **dataframe-reference.md** | FinLabDataFrame 方法 | ~651 |
| **factor-examples.md** | 60+ 策略範例 | ~966 |
| **best-practices.md** | 模式與反模式 | ~528 |
| **trading-reference.md** | 實盤交易整合 | ~327 |
| **factor-analysis-reference.md** | 因子分析工具 | ~675 |
| **machine-learning-reference.md** | ML 工作流程 | ~671 |

### 2. MCP 伺服器 (`workers/`)

Cloudflare Workers 後端，提供 **Model Context Protocol (MCP)** 介面：

**技術棧:**
- TypeScript + Cloudflare Workers (無伺服器)
- MCP 協定 (串流 HTTP)

**端點:**
- `/mcp` - MCP 伺服器 (工具呼叫)
- `/sse` - MCP 串流
- `/health` - 健康檢查
- `/feedback` - 使用者回饋

**可用工具:**

| 工具 | 功能 |
|------|------|
| `list_documents()` | 列出所有文件 |
| `get_document(doc_name)` | 取得特定文件 |
| `search_finlab_docs(query)` | 全文搜尋 |
| `get_factor_examples(factor_type)` | 依類型篩選策略 |

---

## 元件互動流程

```
使用者 (AI 助手)
    ↓
Claude Code / Codex / Gemini CLI
    ↓
finlab-plugin/skills/finlab/ (Skill 文件)
    ↓
MCP Server (Cloudflare Workers)
    ├─ GET /mcp → list_documents()
    ├─ POST /mcp → tools/call (搜尋、取得)
    └─ POST /feedback → 儲存回饋
    ↓
FinLab Python Package API
    ↓
台股市場資料
```

---

## 核心工作流程

### 五步驟策略開發

1. **取得資料** - 使用 `data.get("<TABLE>:<COLUMN>")`
2. **建立因子** - 使用 FinLabDataFrame 方法
3. **建構部位** - 用布林邏輯組合條件
4. **回測** - 執行 `sim()` 設定風險參數
5. **執行下單** - 選擇性透過券商實盤交易

### 資料存取能力

- **900+ 欄位**，橫跨 80+ 資料表
- **歷史價格資料** (日線、T+0)
- **財務報表** (季報/月報)
- **估值指標** (本益比、股價淨值比)
- **法人動向** (外資追蹤)
- **技術指標** (RSI、MACD、KD)

---

## 安裝方式

### 方法一：Claude Code (CLI) - Skill 安裝 (推薦)

```bash
claude plugin marketplace add koreal6803/finlab-ai
claude plugin install finlab-plugin@finlab-plugins
```

### 方法二：Cursor IDE - MCP 安裝

```json
{
  "mcpServers": {
    "finlab": {
      "url": "https://finlab-ai-plugin.koreal6803.workers.dev/mcp"
    }
  }
}
```

---

## 設計哲學

### 執行優於說明

在 SKILL.md 中明確指出：

> "You are not a tutorial. You are an executor."
>
> 當使用者要求回測，他們要的是**螢幕上的結果**，不是要複製貼上的指令。

**實作原則:**
- ✅ **正確:** 執行程式碼、顯示指標、呈現圖表
- ❌ **錯誤:** 丟出程式碼區塊說「自己跑這個」

---

## API Token 等級

| 等級 | 配額 | 識別方式 |
|------|------|---------|
| Free | 500 MB/天 | 結尾有 `#free` |
| VIP | 5000 MB/天 | 無後綴 |

**重置時間:** 每日台灣時間 8:00 AM (UTC+8)

---

## 總結

**FinLab-AI** 是一個架構完善的插件生態系：

1. **知識集中化** - 所有 FinLab 文件的單一真相來源
2. **多客戶端支援** - Claude Code (Skill)、Cursor (MCP)、其他 CLI
3. **強調執行** - 哲學：先看結果，不是教學
4. **深度領域知識** - 5,000+ 行量化交易文件
5. **支援實盤整合** - 從回測到真實市場執行
6. **回饋收集** - 內建回饋系統持續改進
7. **雲端原生** - Cloudflare Workers 後端，零維護負擔

專為讓 AI 助手能撰寫正確的量化交易程式碼而設計，有 60+ 完整策略範例和全面的 API 文件支援。
