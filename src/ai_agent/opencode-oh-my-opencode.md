# OpenCode & oh-my-opencode 完整指南

## 什麼是 OpenCode？

**OpenCode** 是一個開源的 AI 編程助手，運行於終端機（Terminal）中，由 **SST（Serverless Stack）** 團隊開發。它將 AI 對話與程式碼編輯整合在 TUI（Terminal User Interface）環境中，讓開發者無需離開終端即可獲得 AI 的協助。

- 官網：https://opencode.ai
- GitHub：https://github.com/sst/opencode
- 支援多種 AI 模型（Claude、GPT、Gemini、Kimi 等）
- 支援 MCP（Model Context Protocol）工具整合
- 內建 LSP 理解程式碼結構

---

## 與龍蝦（🦞）的關係

OpenCode 由 **SST** 團隊打造，而 SST 的吉祥物正是一隻 **龍蝦（Lobster）**。這隻龍蝦已成為 SST 生態系的品牌象徵，出現在官方 Logo、文件與社群中。

SST 原本是知名的 Serverless 框架（用於 AWS），後來擴展到開發工具領域，打造了 OpenCode。因此你在 opencode 的 UI、文件或社群討論中看到龍蝦圖示，就是 SST 的品牌標誌。

---

## 安裝 OpenCode

```bash
curl -fsSL https://opencode.ai/install | bash
```

### 基本使用

```bash
# 啟動 OpenCode
opencode

# 在特定目錄啟動
opencode /path/to/project

# 指定使用的 AI 模型
opencode --model claude-sonnet-4-6
```

---

## oh-my-opencode 多模型編排框架

### 什麼是 oh-my-opencode？

類似 `oh-my-zsh` 之於 `zsh`，**oh-my-opencode** 是 OpenCode 的多 Agent 編排框架，讓你可以用不同 AI 模型扮演不同角色，協同完成開發任務。

> 官方哲學：*"Claude / Kimi / GLM for orchestration. GPT for reasoning. Minimax for speed. Gemini for creativity. The future isn't picking one winner—it's orchestrating them all."*

### 安裝

```bash
bunx oh-my-openagent install  # 推薦（較快）
# 或
npx oh-my-openagent install
```

安裝過程中會互動式選擇你擁有的 AI 訂閱（Claude、ChatGPT、Gemini、GitHub Copilot 等）。

### 驗證安裝

```bash
opencode --version           # 需要 >= 1.0.150
cat ~/.config/opencode/opencode.json  # 確認 plugin 陣列中有 "oh-my-openagent"
```

### 登入認證

```bash
opencode auth login  # GitHub OAuth 流程
```

---

## 多模型分工：Claude Opus 指揮 Minimax、Kimi、Codex

### 架構概念

```
Claude Opus（主指揮 / ultrawork）
    └── Sisyphus orchestrator
            ├── Kimi K2.5       → 主要編程任務
            ├── Minimax         → 快速瑣碎任務
            ├── Codex/GPT       → 推理分析
            └── Gemini          → 視覺/創意/文件
```

**完全可以！** 透過設定檔指定每個 Agent 使用的模型，Claude Opus 擔任最高層指揮，自動將子任務分配給最適合的模型。

### 設定檔（`~/.config/opencode/oh-my-openagent.jsonc`）

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/dev/assets/oh-my-openagent.schema.json",

  "agents": {
    // 主指揮：Claude Opus 負責 ultrawork 重任務
    "sisyphus": {
      "model": "kimi-for-coding/k2p5",
      "ultrawork": { "model": "anthropic/claude-opus-4-6", "variant": "max" }
    },

    // 文件搜尋：便宜模型即可
    "librarian": { "model": "google/gemini-3-flash" },

    // 程式碼搜尋
    "explore": { "model": "minimax/fast" },

    // 架構諮詢：Claude Opus
    "oracle": { "model": "anthropic/claude-opus-4-6", "variant": "max" },

    // 計畫生成（繼承 sisyphus 模型）
    "prometheus": {
      "prompt_append": "Leverage deep & quick agents heavily, always in parallel."
    }
  },

  "categories": {
    "quick":            { "model": "minimax/fast" },                              // 快速小任務
    "unspecified-low":  { "model": "kimi-for-coding/k2p5" },                     // 一般編程
    "unspecified-high": { "model": "anthropic/claude-opus-4-6", "variant": "max" }, // 高難度
    "writing":          { "model": "google/gemini-3-flash" },                    // 文件撰寫
    "visual-engineering": { "model": "google/gemini-3.1-pro", "variant": "high" } // 視覺工程
  },

  "background_task": {
    "providerConcurrency": {
      "anthropic": 3,        // Opus 同時最多 3 個（費用考量）
      "minimax": 10,         // Minimax 快，多開
      "kimi-for-coding": 5
    },
    "modelConcurrency": {
      "anthropic/claude-opus-4-6": 2
    }
  }
}
```

---

## 核心 Agent 說明

| Agent | 預設用途 | 建議模型 |
|-------|----------|----------|
| `sisyphus` | 主編排者，接收並分配任務 | Kimi K2.5 / Claude Opus |
| `oracle` | 架構諮詢（唯讀高推理） | Claude Opus / GPT |
| `prometheus` | 拆解任務、產生執行計畫 | 繼承 sisyphus |
| `librarian` | 文件查詢、程式碼搜尋 | Gemini Flash |
| `explore` | 快速 grep 程式碼庫 | Minimax / Copilot |
| `hephaestus` | 深度自主實作工作 | Kimi K2.5 |

---

## 使用方式

### 呼叫專門 Agent

```plaintext
Ask @oracle to review this architecture design   # 架構分析
Ask @librarian how is this feature implemented   # 文件/程式碼搜尋
Ask @explore for the policy on this module       # 快速搜尋
```

### ulw（ultrawork）— 自動分配複雜任務

```plaintext
ulw fix the failing tests
ulw add input validation to the API
ulw implement JWT authentication following our patterns
ulw create a new CLI command for deployments
```

執行流程：
1. **Claude Opus** 接收需求
2. **Prometheus** 拆解成多個子任務
3. **Sisyphus** 依類型分配：快速 → Minimax、編程 → Kimi、推理 → GPT
4. **Claude Opus** 整合結果

### 執行計畫

```bash
/start-work [plan-name]   # 執行 Prometheus 產生的計畫
```

### 自訂 Skill

```markdown
---
name: my-custom-skill
description: 我的專業領域
---

# 規則
- 遵循這些模式...
```

---

## 其他常用輔助工具

| 套件 | 說明 |
|------|------|
| `@opencode/mcp` | OpenCode 官方 MCP 工具整合 |
| `ripgrep` (`rg`) | 高效能搜尋，OpenCode 內部依賴 |
| `fd` | 快速檔案搜尋 |
| `fzf` | 模糊搜尋，互動式選擇 |
