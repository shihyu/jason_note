# Claude Code — Plugins / Skills / MCP 整理

> 整理日期：2026-03-31（含社群大神推薦）  
> 身份：C/C++、Rust、Go、Python、Node.js、前後端 + 系統開發工程師

---

## 目錄

1. [已安裝 Plugins](#已安裝-plugins)
2. [已安裝 Skills](#已安裝-skills)
3. [已啟用 MCP Servers](#已啟用-mcp-servers)
4. [建議安裝清單](#建議安裝清單)
5. [安裝指令速查](#安裝指令速查)
6. [社群資源 / Skills 市場平台](#社群資源--skills-市場平台)

---

## 已安裝 Plugins

### LSP 語言伺服器

| Plugin | 語言 | Scope | 安裝來源 |
|--------|------|-------|---------|
| `pyright-lsp` | Python | project + user | claude-plugins-official |
| `rust-analyzer-lsp` | Rust | project | claude-plugins-official |
| `clangd-lsp` | C/C++ | project | claude-plugins-official |
| `gopls-lsp` | Go | user | claude-plugins-official |
| `typescript-lsp` | TypeScript/JS | user | claude-plugins-official |

### 開發工具

| Plugin | 功能 | Scope |
|--------|------|-------|
| `playwright` | 瀏覽器自動化測試 | project |
| `ralph-loop` | 迴圈執行 prompt | project |
| `code-simplifier` | 程式碼品質簡化 | project |
| `skill-creator` | 建立自訂 Skills | user |
| `github` | GitHub PR/Issue 整合 | user |

### Skills 套件（plugin 形式）

| Plugin | 包含內容 | Scope |
|--------|---------|-------|
| `example-skills@anthropic-agent-skills` | 17 個通用 Skills | project |
| `document-skills@anthropic-agent-skills` | 17 個文件 Skills | project |
| `claude-mem@thedotmack` | 跨 Session 記憶系統 + 5 個 Skills | user |

---

## 已安裝 Skills

### 自訂 Skills（`~/.claude/skills/`）

| Skill | 觸發方式 | 功能 |
|-------|---------|------|
| `agent-browser` | `/agent-browser` | Playwright 瀏覽器自動化 |
| `all-plan` | `/all-plan` | 多 AI 協作規劃（Claude/Codex/Gemini） |
| `cask` | `/cask` | 非同步發問給 Codex |
| `dask` | `/dask` | 非同步發問給 Droid |
| `gask` | `/gask` | 非同步發問給 Gemini |
| `oask` | `/oask` | 非同步發問給 OpenCode |
| `skill-creator-advanced` | `/skill-creator-advanced` | 建立/改版/審查 Skills |

### anthropic-agent-skills 提供的 Skills

| Skill | 功能 |
|-------|------|
| `pdf` | 讀寫 PDF |
| `docx` | 讀寫 Word 文件 |
| `xlsx` | 讀寫 Excel 試算表 |
| `pptx` | 讀寫 PowerPoint |
| `frontend-design` | 高品質前端 UI 設計 |
| `webapp-testing` | Playwright 測試 Web App |
| `claude-api` | 使用 Claude / Anthropic SDK |
| `mcp-builder` | 建立 MCP Server |
| `skill-creator` | 建立 Skills |
| `algorithmic-art` | p5.js 演算法藝術 |
| `canvas-design` | PNG/PDF 視覺設計 |
| `web-artifacts-builder` | 多組件 HTML artifacts |
| `slack-gif-creator` | Slack 動態 GIF |
| `theme-factory` | 主題樣式套用 |
| `brand-guidelines` | Anthropic 品牌規範 |
| `doc-coauthoring` | 協作文件撰寫 |
| `internal-comms` | 內部溝通文件 |

### claude-mem 提供的 Skills

| Skill | 功能 |
|-------|------|
| `mem-search` | 搜尋跨 Session 記憶 |
| `make-plan` | 建立實作計畫（含文件探索） |
| `smart-explore` | 用 AST 解析做 token 高效代碼搜尋 |
| `timeline-report` | 生成專案演進敘事報告 |
| `do` | 使用 subagent 執行實作計畫 |

---

## 已啟用 MCP Servers

| Server Name | 提供者 | 類型 | 功能 |
|-------------|--------|------|------|
| `mcp-search` | claude-mem plugin | stdio | 跨 Session 持久記憶搜尋 |

> `settings.json` / `settings.local.json` 目前無額外自定義 MCP。

---

## 建議安裝清單

### 優先推薦（針對你的技術棧）

#### 開發流程工具（高價值）

| Plugin | 安裝指令 | 推薦理由 |
|--------|---------|---------|
| `commit-commands` | `/plugin install commit-commands@claude-plugins-official` | 一鍵 commit/push/PR，減少 git 手動操作 |
| `code-review` | `/plugin install code-review@claude-plugins-official` | 自動 PR 多角度 code review（平行 agents）|
| `pr-review-toolkit` | `/plugin install pr-review-toolkit@claude-plugins-official` | 6 個專項 review agents（型別、測試、error handling 等）|
| `feature-dev` | `/plugin install feature-dev@claude-plugins-official` | 7 階段結構化功能開發流程 |
| `hookify` | `/plugin install hookify@claude-plugins-official` | 用 markdown 定義 hooks，防止壞習慣（例：避免 `rm -rf`）|

#### 系統 / 後端開發

| Plugin | 安裝指令 | 推薦理由 |
|--------|---------|---------|
| `security-guidance` | `/plugin install security-guidance@claude-plugins-official` | 安全漏洞偵測 hooks，系統開發必備 |
| `claude-md-management` | `/plugin install claude-md-management@claude-plugins-official` | 管理多專案 CLAUDE.md，維護工作守則 |

#### 外部整合（依需求選用）

| Plugin | 安裝指令 | 推薦理由 |
|--------|---------|---------|
| `github` | 已安裝 | 已有，確認正常使用 |
| `linear` | `/plugin install linear@claude-plugins-official` | Linear issue 追蹤整合（若你用 Linear）|
| `context7` | `/plugin install context7@claude-plugins-official` | 自動注入最新 library 文件（Rust/Go/Node.js 文件支援）|

### 可選安裝（特定情境）

| Plugin | 安裝指令 | 適用情境 |
|--------|---------|---------|
| `greptile` | `/plugin install greptile@claude-plugins-official` | AI PR review 整合 GitHub/GitLab（需 Greptile 帳號）|
| `agent-sdk-dev` | `/plugin install agent-sdk-dev@claude-plugins-official` | 開發 Claude agent/tool |
| `mcp-server-dev` | `/plugin install mcp-server-dev@claude-plugins-official` | 開發自己的 MCP Server |

### 暫不建議安裝

| Plugin | 原因 |
|--------|------|
| `csharp-lsp` / `kotlin-lsp` / `swift-lsp` / `php-lsp` / `ruby-lsp` / `lua-lsp` | 你的技術棧用不到 |
| `jdtls-lsp` (Java) | 同上 |
| `discord` / `telegram` / `imessage` / `slack` | 依個人通訊需求決定 |

---

## 安裝指令速查

### Plugin 操作

```bash
# 瀏覽可用 plugins
/plugin

# 安裝 plugin（user 層級，所有專案共用）
/plugin install <plugin-name>@<marketplace>

# 安裝 plugin（project 層級，只限目前專案）
/plugin install <plugin-name>@<marketplace> --scope project

# 移除 plugin
/plugin remove <plugin-name>@<marketplace>

# 列出已安裝
/plugin list
```

### 推薦安裝順序

```bash
# 第一波：開發流程必備
/plugin install commit-commands@claude-plugins-official
/plugin install code-review@claude-plugins-official
/plugin install pr-review-toolkit@claude-plugins-official
/plugin install hookify@claude-plugins-official

# 第二波：安全 + 專案管理
/plugin install security-guidance@claude-plugins-official
/plugin install claude-md-management@claude-plugins-official
/plugin install feature-dev@claude-plugins-official

# 第三波：依需求
/plugin install context7@claude-plugins-official   # 若常查 library 文件
/plugin install linear@claude-plugins-official     # 若用 Linear
```

### MCP Server 手動新增（自定義）

若要在 `~/.claude/settings.json` 手動加 MCP：

```json
{
  "mcpServers": {
    "my-server": {
      "type": "stdio",
      "command": "/path/to/server",
      "args": ["--flag"]
    }
  }
}
```

---

## 現有安裝總覽（快速參考）

```
LSP:        clangd ✓  rust-analyzer ✓  gopls ✓  pyright ✓  typescript ✓
測試:        playwright ✓
記憶:        claude-mem ✓ (MCP: mcp-search)
技能套件:    example-skills ✓  document-skills ✓
工具:        code-simplifier ✓  skill-creator ✓  ralph-loop ✓  github ✓
多AI協作:    cask(Codex) ✓  gask(Gemini) ✓  oask(OpenCode) ✓

建議補裝:    commit-commands / code-review / pr-review-toolkit
             hookify / security-guidance / feature-dev / context7
```

---

## 社群大神推薦 MCP（網路調查 2025-2026）

> 來源：Reddit、Medium、GitHub、MCPcat、Apidog 等多個技術社群

### Sequential Thinking MCP — 值得裝嗎？

**是什麼：** Anthropic 官方出品的 MCP，讓 Claude 在解題時進行結構化的分步推理——可修正前面的步驟、探索多條路徑、對假設做驗證，適合「需要在白板上想清楚才能動手」的問題。

**社群評價：**

| 立場 | 說法 |
|------|------|
| 支持派 | 架構決策、複雜 debug、多步驟規劃明顯有感；某作者說「有人說 Claude 內建就做到了，我目前不同意，它幫我分解問題很多次」 |
| 質疑派 | Claude Sonnet 4+ 的 extended thinking 模式已內建類似推理，功能重疊 |
| 共識 | 純計算、不需外部 API、安裝成本極低 → **建議裝，特別是做系統設計/Rust/Go 的人** |

**安裝：**
```bash
claude mcp add sequentialthinking -- npx -y @modelcontextprotocol/server-sequentialthinking
```

---

### Tier 1 — 社群近乎一致推薦

| MCP Server | 安裝指令 | 針對你的價值 |
|-----------|---------|------------|
| **GitHub MCP**（官方）| `claude mcp add github` | 已裝 plugin，補 MCP 可做更深的 API 操作 |
| **Filesystem MCP**（官方）| `claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem ~/projects` | 大重構、跨目錄操作有 permission scoping |
| **Context7**（Upstash）| `claude mcp add context7 -- npx -y @upstash/context7-mcp@latest` | 自動注入最新 library 文件；Rust crate / Go stdlib / Node.js 版本差異必備，**殺手級功能** |
| **Sequential Thinking** | 見上方 | 架構決策、記憶體安全分析、並發設計 |

### Tier 2 — 系統/後端開發者強力推薦

| MCP Server | 安裝指令 | 說明 |
|-----------|---------|------|
| **Memory/Knowledge Graph**（官方）| `claude mcp add memory -- npx -y @modelcontextprotocol/server-memory` | 跨 session 持久化：API 契約、ABI 限制、系統不變量等設計決策 |
| **Serena MCP** | `claude mcp add serena -- uvx --from serena-mcp serena-mcp` | LSP-aware 語意程式碼搜尋，理解「意圖」而非單純文字匹配；大型多語言 monorepo 必備 |
| **Docker MCP** | `claude mcp add docker -- npx -y @modelcontextprotocol/server-docker` | 用自然語言管理 container、dev 環境；配合 Filesystem MCP 更強 |
| **PostgreSQL MCP**（官方）| `claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres <conn_str>` | 自然語言 DB 查詢、Schema 檢查、migration 撰寫 |
| **Git MCP** | `claude mcp add git -- uvx mcp-server-git` | 進階 git 操作：log 分析、bisect、複雜歷史查詢 |

### Tier 3 — 情境型（按需安裝）

| MCP Server | 適用情境 |
|-----------|---------|
| **Playwright MCP** | 有 HTTP API 或 Web 前端要做整合測試 |
| **Brave Search / DuckDuckGo MCP** | 不離開 Claude 做網路研究（DuckDuckGo 免費不需 API key）|
| **Sentry MCP** | 分析生產環境 error pattern |
| **Firecrawl MCP** | 抓取外部 spec、RFC、library 文件 |
| **Supabase MCP** | 若後端用 Supabase |

### 大型 Codebase 特別推薦

**`@zilliz/claude-context-mcp`** — 混合語意 + 關鍵字搜尋（BM25 + dense vector），AST-aware chunking，號稱減少 ~40% token 用量。原生支援 C++、Rust、Go、Python，需要 Milvus 或 Zilliz Cloud 作後端。適合 codebase 大到塞不進 context window 時使用。

```bash
claude mcp add claude-context -- npx -y @zilliz/claude-context-mcp
```

---

### 我的優先安裝建議（針對你的技術棧）

```bash
# 第一優先：立刻裝
claude mcp add sequentialthinking -- npx -y @modelcontextprotocol/server-sequentialthinking
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem ~/

# 第二優先：系統開發必備
claude mcp add memory -- npx -y @modelcontextprotocol/server-memory
claude mcp add git -- uvx mcp-server-git

# 第三優先：依需求
claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres <your_conn_string>
claude mcp add docker -- npx -y @modelcontextprotocol/server-docker
```

> **社群提示：** 同時開啟的 MCP 不要超過 5-6 個，太多會拖慢 Claude Code 啟動速度並增加 context 消耗。

---

---

## 社群資源 / Skills 市場平台

### ClawHub — Skills 市場平台

**網址：** <https://clawhub.ai/skills>

ClawHub 是目前最大的 Claude Code Skills 社群市場，收錄超過 **13,700+** 個 Skills，由 Peter Steinberger 建立，MIT 開源授權。支援 GitHub 帳號登入，提供 Staff Picks 精選推薦。

**特色：**
- 按下載數、分類瀏覽 Skills
- VirusTotal + OpenClaw 安全掃描驗證
- 社群貢獻 + 版本追蹤

---

### DennisLiuCk/claude-plugin-marketplace — 繁體中文插件市場

**GitHub：** <https://github.com/DennisLiuCk/claude-plugin-marketplace>

社群維護的**繁體中文** Claude Code 插件市場，精選 **20 個插件**，降低台灣 / 中文開發者的入門門檻。

**分類：**

| 類別 | 數量 | 包含內容 |
|------|------|---------|
| 開發工具 | 10 | Agent SDK、多階段功能開發、程式碼簡化、舊專案分析 |
| 生產力工具 | 7 | Git 自動化、PR review、code review、SQL migration |
| 安全 | 1 | 即時弱點偵測（編輯時自動掃描） |
| 學習 | 2 | 教學型輸出模式、互動式學習 |

**安裝方式：**
```bash
claude plugin install github:DennisLiuCk/claude-plugin-marketplace/plugins/<plugin-name>
```

---

### 社群推薦文章：必裝 Skills 精選

#### DataCamp — Best ClawHub Skills 完整指南

**網址：** <https://www.datacamp.com/blog/best-clawhub-skills>

由 Khalid Abdelaty 撰寫（2026-03-05），涵蓋如何安裝和管理 Skills、安全注意事項、常見設定錯誤排除。

---

#### CNBlogs — 10 個必裝 OpenClaw Skills（中文）

**網址：** <https://www.cnblogs.com/informatics/p/19679935>

作者 warm3snow 從 ClawHub 13,700+ Skills 中精選 10 個必裝項目，全部本地運行、不需外部 API key，分為四層：

| 層級 | Skills | 功能 |
|------|--------|------|
| **生存層** | Agent Browser、Self-Improving Agent、Agent Memory | 瀏覽器自動化、錯誤學習、持久記憶 |
| **效率層** | Agent Autopilot、Diagram Generator、Airpoint | 自主任務執行、視覺化生成、macOS 控制 |
| **安全層** | ClawdStrike、Credential Manager | 安全稽核、本地憑證管理 |
| **進階層** | Evolver、Adaptive Reasoning | 持續 AI 改進、智慧任務複雜度評估 |

> **延伸資源：** [awesome-openclaw-skills](https://github.com/search?q=awesome-openclaw-skills)（5,494 個 Skills，32 個分類）

---

### 參考來源

- [Sequential Thinking MCP - Official GitHub](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)
- [Context7 MCP - Upstash GitHub](https://github.com/upstash/context7)
- [10 Must-Have MCP Servers 2025 - Medium](https://roobia.medium.com/the-10-must-have-mcp-servers-for-claude-code-2025-developer-edition-43dc3c15c887)
- [Top 10 Essential MCP Servers - Apidog](https://apidog.com/blog/top-10-mcp-servers-for-claude-code/)
- [MCP Servers for Rust Developers - Shuttle.dev](https://www.shuttle.dev/blog/2025/09/15/mcp-servers-rust-comparison)
- [Claude Code Development Powerhouse - Robert Marshall](https://robertmarshall.dev/blog/turning-claude-code-into-a-development-powerhouse/)
- [Sequential Thinking 深度分析 - QED42](https://www.qed42.com/insights/enhancing-claude-with-in-conversation-reasoning---the-sequentialthinking-mcp-server)
- [Zilliz claude-context semantic search - GitHub](https://github.com/zilliztech/claude-context)
