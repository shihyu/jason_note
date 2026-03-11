# Claude Code Plugin 觸發機制完整說明

本文件說明 everything-claude-code plugin 中五種檔案類型的觸發方式與運作原理。

---

## 速查卡（Quick Reference）

```
想要…                             用這個
────────────────────────────────────────────────────
輸入一個指令立刻執行固定流程        Command   /code-review
讓 Claude 自動感知情境套用知識      Skill     語意匹配
讓 Claude 自動派出專門助手          Agent     自主委派
強制 Claude 永遠遵守某個規定        Rule      永遠生效
在工具呼叫前後自動執行腳本          Hook      事件觸發
```

---

## 目錄

1. [五種機制概覽](#五種機制概覽)
2. [Commands — 手動指令觸發](#1-commands)
3. [Skills — 語意自動匹配](#2-skills)
4. [Agents — Claude 主動委派](#3-agents)
5. [Rules — 永遠自動載入](#4-rules)
6. [Hooks — 工具事件自動觸發](#5-hooks)
7. [完整觸發流程圖](#完整觸發流程圖)
8. [執行模型對比](#執行模型對比)
9. [如何選擇？決策樹](#如何選擇決策樹)
10. [關鍵差異對照表](#關鍵差異對照表)

---

## 五種機制概覽

```
┌────────────────────────────────────────────────────────────────┐
│                    Claude Code Plugin 機制總覽                 │
├──────────┬──────────────┬────────────┬──────────┬──────────────┤
│          │  Commands    │   Skills   │  Agents  │    Rules     │
│          │              │            │          │    Hooks     │
├──────────┼──────────────┼────────────┼──────────┼──────────────┤
│ 誰觸發   │    使用者    │ Claude自動 │  Claude  │  永遠/事件   │
│ 怎麼觸發 │  /指令名稱   │ 語意匹配   │  自主判斷│ 自動/工具事件│
│ 在哪執行 │  主對話      │ 主對話     │ 子執行緒 │ 系統層/主對話│
│ 可否關閉 │ 不輸入即停   │ 可忽略     │ 可忽略   │  難以關閉    │
└──────────┴──────────────┴────────────┴──────────┴──────────────┘
```

---

## 1. Commands

**位置**：`commands/*.md`
**觸發方式**：使用者手動輸入 `/指令名稱`

### 運作原理

```
使用者輸入 /code-review
        │
        ▼
Claude Code 找到 commands/code-review.md
        │
        ▼
整個 md 內容當作 prompt，在主對話直接執行
        │
        ▼
輸出結果給使用者
```

### 觸發規則

- 檔名即指令名稱，無需 frontmatter
- Claude 讀取整個 md 內容，作為 prompt 執行
- 一對一對應：一個檔案 = 一個斜線指令

### 檔案結構範例

```
commands/
├── code-review.md   →  /code-review
├── tdd.md           →  /tdd
├── plan.md          →  /plan
├── e2e.md           →  /e2e
├── build-fix.md     →  /build-fix
└── verify.md        →  /verify
```

### 檔案內容格式

純指令說明文字，無 frontmatter：

```markdown
# Code Review

Comprehensive security and quality review of uncommitted changes:

1. Get changed files: git diff --name-only HEAD
2. For each changed file, check for:
   - Hardcoded credentials, API keys
   - SQL injection vulnerabilities
   ...
```

### 使用方式

```
你：/code-review
Claude：（執行 commands/code-review.md 的完整內容）
```

---

## 2. Skills

**位置**：`skills/*/SKILL.md`
**觸發方式**：語意自動匹配 或 Skill tool 手動呼叫

### 運作原理

```
使用者說「幫我用 TDD 寫這個功能」
        │
        ▼
Claude 掃描所有已安裝 skill 的 description 欄位
        │
   ┌────┴─────────────────────────┐
   │ 比對語意相似度               │
   │ tdd-workflow: "Use when      │
   │   writing new features..."   │
   └────────────┬─────────────────┘
               │ 匹配成功
               ▼
    載入 skills/tdd-workflow/SKILL.md
               │
               ▼
    在當前主對話中執行（非子執行緒）
```

### Skills 有 YAML frontmatter

```yaml
---
name: tdd-workflow
description: Use this skill when writing new features, fixing bugs, or refactoring code.
             Enforces test-driven development with 80%+ coverage including unit,
             integration, and E2E tests.
origin: ECC
---
```

### A. 語意自動匹配

Claude 讀取你的請求，跟所有已安裝 skill 的 `description` 做語意比對，自動選擇最符合的 skill：

| 使用者說 | 匹配 Skill |
|---------|-----------|
| 「幫我用 TDD 寫這個功能」 | `tdd-workflow` |
| 「做一個安全審查」 | `security-review` |
| 「幫我規劃後端架構」 | `backend-patterns` |
| 「我需要驗證這段邏輯」 | `verification-loop` |

### B. 手動呼叫（Skill tool）

```
你：使用 Skill tool 執行 tdd-workflow
Claude：（載入並執行 skills/tdd-workflow/SKILL.md）
```

### Skills 的命名空間與衝突處理

Skills 來自兩個來源，用不同格式區隔：

| 來源 | 存放位置 | 識別格式 | 範例 |
|------|---------|---------|------|
| 用戶自建 | `~/.claude/skills/` | `skill-name` | `go-dev`、`finlab` |
| Plugin 安裝 | `~/.claude/plugins/...` | `plugin-name:skill-name` | `claude-mem:do`、`playground:playground` |

**兩個 plugin 有相同 skill name 時**，靠 plugin 名稱前綴區隔，完全不衝突：

```
claude-mem:do        ← claude-mem plugin 的 do skill
openclaw:do          ← openclaw plugin 的 do skill
```

### 已有 Skills 清單

```
skills/
├── tdd-workflow/          → TDD 開發流程
├── backend-patterns/      → 後端架構模式
├── frontend-patterns/     → 前端架構模式
├── security-review/       → 安全性審查
├── coding-standards/      → 程式碼標準
├── verification-loop/     → 驗證迴圈
├── eval-harness/          → 評估框架
└── strategic-compact/     → 策略規劃
```

---

## 3. Agents

**位置**：`agents/*.md`
**觸發方式**：Claude 在執行任務時，根據 `description` 自主決定委派給哪個 subagent

### 運作原理

```
使用者說「review my code」
        │
        ▼
Claude 判斷：這個任務適合委派給專門的審查員
        │
        ▼
啟動 agents/code-reviewer.md 作為獨立 subagent
        │
   ┌────┴─────────────────────────────────────┐
   │          獨立子執行緒                     │
   │  ┌──────────────────────────────────┐    │
   │  │ tools: ["Read","Grep","Glob","Bash"]│  │
   │  │ model: sonnet                    │    │
   │  │ 執行 code-reviewer 的任務邏輯     │    │
   │  └──────────────────────────────────┘    │
   └────────────────────┬─────────────────────┘
                        │ 結果回傳主對話
                        ▼
               使用者看到審查報告
```

### Agents 有完整 frontmatter

```yaml
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality,
             security, and maintainability. Use immediately after writing or
             modifying code. MUST BE USED for all code changes.
tools: ["Read", "Grep", "Glob", "Bash"]
model: sonnet
---
```

### 自動委派邏輯

Claude 分析任務需求，從 description 判斷哪個 agent 最合適：

| 使用者說 | 觸發 Agent |
|---------|-----------|
| 「review my code」 | `code-reviewer` |
| 「fix this failing test」 | `tdd-guide` |
| 「plan this new feature」 | `planner` |
| 「clean up and refactor」 | `refactor-cleaner` |
| 「check for security issues」 | `security-reviewer` |
| 「update the docs」 | `doc-updater` |
| 「design the database schema」 | `database-reviewer` |

### Commands 與 Agents 同名不衝突

Commands 和 Agents 存在於**不同命名空間**，即使同名也不衝突：

```
commands/code-review.md  →  使用者輸入 /code-review 觸發（主對話執行）
agents/code-reviewer.md  →  Claude 自主委派時觸發（子執行緒執行）
```

> **功能相似，入口不同，互不呼叫。**
> - `/code-review` → 在主對話執行，你看到整個過程
> - `agents/code-reviewer.md` → 子執行緒，有 tools/model 限制，Claude 自己決定何時用

### 此 repo 的命名慣例

作者刻意用**動作名詞 vs 執行者名詞**來區分，提升可讀性：

| Commands（動作名詞） | Agents（執行者名詞，-er 後綴） |
|---------------------|-------------------------------|
| `code-review.md` | `code-reviewer.md` |
| `go-review.md` | `go-reviewer.md` |
| `python-review.md` | `python-reviewer.md` |
| `refactor-clean.md` | `refactor-cleaner.md` |

這是**慣例選擇，非技術限制**。

### 已有 Agents 清單

```
agents/
├── code-reviewer.md       → 程式碼審查
├── tdd-guide.md           → TDD 指導
├── planner.md             → 任務規劃
├── refactor-cleaner.md    → 重構清理
├── security-reviewer.md   → 安全審查
├── doc-updater.md         → 文件更新
├── database-reviewer.md   → 資料庫設計
├── architect.md           → 系統架構
├── e2e-runner.md          → E2E 測試執行
└── build-error-resolver.md → 建置錯誤修復
```

---

## 4. Rules

**位置**：`rules/**/*.md`
**觸發方式**：不需要觸發，安裝後每次對話永遠自動注入為背景指令

### 運作原理

```
任何對話開始
      │
      ▼
Claude Code 自動載入 ~/.claude/rules/**/*.md
      │
      ▼
所有 rule 內容注入 Claude 的系統 prompt
      │
      ▼
Claude 整個對話期間都受這些規則約束
      │
   ┌──┴──────────────────────────────────────┐
   │   rules/common/testing.md               │
   │   → 「寫 code 前必須先寫測試」            │
   │   rules/common/security.md              │
   │   → 「禁止硬編碼 API Key」               │
   │   rules/typescript/patterns.md          │
   │   → 「使用 TypeScript 嚴格模式」         │
   └─────────────────────────────────────────┘
         全部同時生效，無法個別關閉
```

### 觸發規則

- Rules 是純 Markdown，無 frontmatter
- 安裝到 `~/.claude/rules/` 後，每次 Claude 啟動都自動載入
- 作為**行為準則**存在，Claude 必須遵守

### 檔案結構

```
rules/
├── common/
│   ├── testing.md        ← 永遠生效：80% 覆蓋率要求
│   ├── security.md       ← 永遠生效：禁止硬編碼金鑰
│   ├── coding-style.md   ← 永遠生效：程式碼風格
│   ├── patterns.md       ← 永遠生效：設計模式
│   ├── performance.md    ← 永遠生效：效能要求
│   ├── git-workflow.md   ← 永遠生效：Git 工作流
│   └── hooks.md          ← 永遠生效：Hook 使用規範
├── typescript/
│   ├── patterns.md       ← TypeScript 專案自動套用
│   └── testing.md
├── python/
│   └── patterns.md       ← Python 專案自動套用
└── golang/
    └── patterns.md       ← Go 專案自動套用
```

### Rules 的特性

- 你**不需要呼叫** rules
- 你**無法關閉**特定 rule（除非移除檔案）
- 所有 rules 同時生效，形成完整的行為約束

---

## 5. Hooks

**位置**：`hooks/hooks.json`
**觸發方式**：偵測到特定工具（Tool）被呼叫時，自動執行對應腳本

### 運作原理

```
Claude 準備呼叫 Bash 工具
        │
        ▼
系統檢查 hooks.json 有無 PreToolUse/Bash 設定
        │
   ┌────┴──────────────────────────────────────┐
   │  有 matcher 符合                           │
   │  → 先執行 hooks 腳本                       │
   │  → 腳本可輸出提示、警告，甚至阻止工具執行  │
   └────────────────────┬──────────────────────┘
                        │
                        ▼
              Bash 工具正式執行
                        │
                        ▼
           PostToolUse hooks 執行（如有）
```

### hooks.json 格式

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "node scripts/hooks/pre-bash-tmux-reminder.js"
        }],
        "description": "Reminder to use tmux for long-running commands"
      },
      {
        "matcher": "Write",
        "hooks": [{
          "type": "command",
          "command": "node scripts/hooks/doc-file-warning.js"
        }],
        "description": "Warn about non-standard documentation files"
      }
    ],
    "PostToolUse": [...]
  }
}
```

### 支援的事件類型

| 事件 | 說明 |
|------|------|
| `PreToolUse` | 工具執行**前**觸發 |
| `PostToolUse` | 工具執行**後**觸發 |
| `Notification` | Claude 發送通知時觸發 |
| `SessionStart` | 對話開始時觸發 |
| `Stop` | Claude 停止回應時觸發 |

### matcher 範例

| matcher | 觸發時機 |
|---------|---------|
| `"Bash"` | 每次 Claude 呼叫 Bash 工具 |
| `"Write"` | 每次 Claude 寫入檔案 |
| `"Edit"` | 每次 Claude 編輯檔案 |
| `"Edit\|Write"` | Edit 或 Write 任一觸發 |
| `".*"` | 任何工具都觸發 |

### 常見 Hooks 用途

| Hook 腳本 | 觸發時機 | 用途 |
|-----------|---------|------|
| `pre-bash-tmux-reminder.js` | Bash 執行前 | 提醒使用 tmux 執行長指令 |
| `pre-bash-git-push-reminder.js` | Bash 執行前 | git push 前提醒確認 |
| `doc-file-warning.js` | Write 執行前 | 警告非標準文件檔案 |
| `suggest-compact.js` | Edit/Write 執行前 | 建議程式碼精簡 |
| `session-persistence.js` | SessionStart | 載入上次對話記憶 |

---

## 完整觸發流程圖

```
┌─────────────────────────────────────────────────────────────────┐
│                         使用者輸入                               │
└──────────────────────────────┬──────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   ┌─────────────┐    ┌────────────────┐   ┌──────────────────┐
   │ /code-review│    │「幫我 TDD 寫」 │   │「review my code」│
   │  手動指令   │    │   自然語言     │   │   自然語言       │
   └──────┬──────┘    └───────┬────────┘   └────────┬─────────┘
          │                   │                     │
          ▼                   ▼                     ▼
   ┌─────────────┐    ┌────────────────┐   ┌──────────────────┐
   │  commands/  │    │   skills/      │   │    agents/       │
   │code-review  │    │ tdd-workflow/  │   │ code-reviewer    │
   │   .md       │    │  SKILL.md      │   │    .md           │
   └──────┬──────┘    └───────┬────────┘   └────────┬─────────┘
          │                   │                     │
          ▼                   ▼                     ▼
   ┌─────────────┐    ┌────────────────┐   ┌──────────────────┐
   │  主對話執行 │    │  主對話執行    │   │  子執行緒執行    │
   │  直接輸出   │    │  知識/流程注入 │   │  tools/model限制 │
   └─────────────┘    └────────────────┘   └──────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         任何對話                                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │    rules/**/*.md   │
                    │  永遠自動注入為    │
                    │  系統 prompt 背景  │
                    └────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Claude 呼叫工具                               │
└──────────────────────────────┬──────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   ┌─────────────┐    ┌────────────────┐   ┌──────────────────┐
   │  呼叫 Bash  │    │  呼叫 Write    │   │  呼叫任何工具    │
   └──────┬──────┘    └───────┬────────┘   └────────┬─────────┘
          │                   │                     │
          ▼                   ▼                     ▼
   PreToolUse/Bash   PreToolUse/Write        PostToolUse/.*
   腳本自動執行       腳本自動執行            腳本自動執行
```

---

## 執行模型對比

```
┌──────────────────────────────────────────────────────────────────┐
│                        執行位置與控制權                           │
├──────────┬─────────────────────────────────────────────────────  │
│          │                                                        │
│ Command  │  [主對話]─────────────────────────────────────────►  │
│          │  整個 md 內容直接在對話串中執行，使用者全程看到        │
│          │                                                        │
│  Skill   │  [主對話]─────────────────────────────────────────►  │
│          │  知識/流程注入當前對話，Claude 用來指導自己的行為      │
│          │                                                        │
│  Agent   │  [主對話]──►[子執行緒]────────────────────────────►  │
│          │              獨立空間，有 tools/model 限制             │
│          │              完成後結果回傳主對話                       │
│          │                                                        │
│  Rule    │  [系統層]─────────────────────────────────────────►  │
│          │  所有對話永遠都有效，Claude 無法「忽略」               │
│          │                                                        │
│  Hook    │  [系統層]──►[工具執行前/後]────────────────────────►  │
│          │  攔截工具呼叫，腳本可輸出提示或阻止執行               │
│          │                                                        │
└──────────┴─────────────────────────────────────────────────────  ┘
```

---

## 如何選擇？決策樹

```
我想達成什麼目的？
│
├─► 我要執行一個固定的工作流程，每次都一樣
│       └─► Command  （/tdd, /plan, /code-review）
│
├─► 我要給 Claude 領域知識，讓它自動選擇適用時機
│       └─► Skill  （description 寫清楚觸發情境）
│
├─► 我要 Claude 在複雜任務中派出「專門助手」處理子任務
│       └─► Agent  （設定 tools 限制、model 指定）
│
├─► 我要強制 Claude 在所有情況下都遵守某個規定
│       └─► Rule  （放入 rules/，永遠生效）
│
└─► 我要在 Claude 用某個工具的前後自動執行腳本
        └─► Hook  （設定 matcher，腳本在工具呼叫前後觸發）
```

### 常見組合模式

```
使用者需求                 最佳組合
─────────────────────────────────────────────────────
固定 code review 流程    Command(/code-review)
                          + Agent(code-reviewer) 自動深入分析

確保測試品質              Rule(testing.md) 永遠強制
                          + Skill(tdd-workflow) 指引流程
                          + Command(/tdd) 手動啟動

保護 git 操作             Hook(PreToolUse/Bash) 攔截 git push
                          + Rule(git-workflow.md) 規範流程
```

---

## 關鍵差異對照表

| 類型 | 位置 | 觸發方式 | 執行位置 | 關鍵欄位 | 使用場景 |
|------|------|---------|---------|---------|---------|
| **Command** | `commands/*.md` | `/name` 手動輸入 | 主對話 | 檔名即指令名 | 固定工作流程的一鍵執行 |
| **Skill** | `skills/*/SKILL.md` | 語意自動或手動 | 主對話 | `description:` | 提供領域知識與流程指引 |
| **Agent** | `agents/*.md` | Claude 自主委派 | 子執行緒 | `description:` + `tools:` + `model:` | 獨立執行複雜任務 |
| **Rule** | `rules/**/*.md` | 永遠自動 | 系統層 | 無（純內文） | 強制行為約束 |
| **Hook** | `hooks/hooks.json` | 工具事件 | 系統層 | `matcher:` | 工具呼叫前後的自動化 |

### Skills vs Agents 細部對比

| 面向 | Skills | Agents |
|------|--------|--------|
| 執行方式 | 在當前對話執行 | 作為獨立 subagent 執行 |
| 有無工具限制 | 無 | 有（`tools:` 欄位指定） |
| 有無 model 指定 | 無 | 有（`model:` 欄位指定） |
| context 共享 | 完全共享主對話 context | 有自己的獨立 context |
| 適合情境 | 提供知識/流程指引 | 需要獨立執行任務 |
| 觸發控制 | Claude 語意判斷 | Claude 主動委派決策 |

---

## 安裝後的載入路徑

```
~/.claude/
├── commands/        ← /斜線指令來源
├── skills/          ← 語意匹配的技能庫
├── agents/          ← subagent 定義
├── rules/           ← 永遠生效的規則
└── hooks/
    └── hooks.json   ← 工具事件監聽設定
```

> 這些路徑是 Claude Code 的**全域設定目錄**，安裝到這裡的檔案對所有專案生效。
> 若要只對特定專案生效，可改放在專案根目錄的 `.claude/` 下。
