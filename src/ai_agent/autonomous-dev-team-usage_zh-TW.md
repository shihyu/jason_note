# Autonomous Dev Team 使用指南

AI 驅動的自動化開發團隊，掃描 GitHub Issues 並透過 Dev → Review 流程產生 PR。

## 概述

```
Issue（含 autonomous 標籤）
  → Dev Agent（worktree 隔離、TDD、design canvas）
    → PR 建立
      → Review Agent（程式碼品質、E2E 驗證）
        → 自動合併或退回開發
```

## 架構流程圖

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        Autonomous Dev Team 自動化開發流程                             │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────┐     ┌───────────────┐     ┌──────────────┐     ┌───────────────┐   │
│  │  GitHub  │────▶│   Dispatcher  │────▶│  Dev Agent   │────▶│Review Agent   │   │
│  │  Issue  │     │   (排程掃描)   │     │  (開發實作)   │     │  (程式碼審查)  │   │
│  │         │◀────│               │◀────│              │◀────│               │   │
│  └──────────┘     └───────────────┘     └──────────────┘     └───────────────┘   │
│       │                  │                    │                    │                  │
│       │                  │                    │                    │                  │
│       ▼                  ▼                    ▼                    ▼                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                      Label 狀態機 State Machine                         │   │
│  │                                                                       │   │
│  │   autonomous → pending-dev → in-progress → pending-review → reviewing → approved → merged   │
│  │       ↑              │              │             │              │                   │
│  │       │              ▼              ▼             ▼              ▼                   │
│  │       │         (失敗)         (失敗)        (失敗)        (手動合併)              │
│  │       │              │              │             │              │                   │
│  │       └──────────────┴──────────────┴──────────────┘                   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         三個核心腳本                                       │   │
│  │  ┌────────────────┐ ┌──────────────────┐ ┌─────────────────────┐         │   │
│  │  │autonomous-dev  │ │autonomous-review │ │  dispatch-local    │         │   │
│  │  │     .sh       │ │       .sh        │ │       .sh          │         │   │
│  │  │  開發代理封裝   │ │   審查代理封裝    │ │  流程調度 + 並發控制 │         │   │
│  │  └────────────────┘ └──────────────────┘ └─────────────────────┘         │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         TDD 強制鉤子 (Hooks)                                │   │
│  │  ┌──────────────────┐ ┌───────────────────┐ ┌──────────────────┐          │   │
│  │  │ block-push-to-   │ │ block-commit-out- │ │ check-design-    │          │   │
│  │  │     main        │ │  side-worktree    │ │     canvas       │          │   │
│  │  │ 阻擋推送至 main  │ │  阻擋在 worktree  │ │  檢查設計文件     │          │   │
│  │  └──────────────────┘ │      外提交       │ └──────────────────┘          │   │
│  │  ┌──────────────────┐ ┌───────────────────┐ ┌──────────────────┐          │   │
│  │  │ check-code-      │ │  check-pr-       │ │ check-rebase-    │          │   │
│  │  │  simplifier      │ │    review        │ │ before-push      │          │   │
│  │  │ 程式碼簡化審查    │ │   PR 審查阻擋    │ │  推送前變基       │          │   │
│  │  └──────────────────┘ └───────────────────┘ └──────────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 設定

### 1. 複製並設定

```bash
git clone https://github.com/zxkane/autonomous-dev-team.git
cd autonomous-dev-team

cp skills/autonomous-dispatcher/scripts/autonomous.conf.example autonomous.conf
```

編輯 `autonomous.conf`：

```bash
# === 專案身份 ===
PROJECT_ID="my-project"
REPO="owner/repo-name"
REPO_OWNER="owner"
REPO_NAME="repo-name"
PROJECT_DIR="/path/to/your/project"

# === Agent 設定 ===
AGENT_CMD="claude"        # claude, codex, kiro 或其他 CLI agents
AGENT_DEV_MODEL=""         # 選填：指定開發 agent 模型
AGENT_REVIEW_MODEL="sonnet"  # 選填：指定審查 agent 模型

# === GitHub 認證 ===
GH_AUTH_MODE="token"       # "token"（預設）或 "app"（GitHub App）
# GitHub App 模式：
# GH_AUTH_MODE="app"
# DEV_AGENT_APP_ID="123456"
# DEV_AGENT_APP_PEM="/path/to.pem"
# REVIEW_AGENT_APP_ID="789012"
# REVIEW_AGENT_APP_PEM="/path/to.pem"
```

### 2. 設定 GitHub 標籤

```bash
bash skills/autonomous-dispatcher/scripts/setup-labels.sh
```

建立以下標籤：

| 標籤 | 描述 |
|-------|------|
| `autonomous` | 符合自動化處理條件的 Issues |
| `pending-dev` | 等待開發 |
| `in-progress` | 開發中 |
| `pending-review` | 等待審查 |
| `reviewing` | 審查中 |
| `approved` | 核准合併 |

### 3. 前置需求

- [`gh`](https://cli.github.com/) CLI，已認證（`gh auth login`）
- Agent CLI 已安裝並可存取：
  - **Claude Code**：`claude` 命令可用
  - **Codex**：`codex` 命令可用
  - **Kiro**：`kiro-cli` 命令可用

## 使用方式

### 觸發開發

#### 方法 A：手動觸發（測試）

```bash
# 為 issue 加上 autonomous 標籤
gh issue edit 42 --repo owner/repo --add-label autonomous

# 手動執行開發 agent
export AUTONOMOUS_CONF="/path/to/autonomous.conf"
bash skills/autonomous-dispatcher/scripts/autonomous-dev.sh --issue 42 --mode new
```

#### 方法 B：Dispatcher（正式環境）

Dispatcher 持續掃描帶有 `autonomous` 標籤的 issues 並自動產生 agents。

### 開發流程

1. **在 GitHub 建立 Issue**，清楚描述需求
2. **加上** `autonomous` **標籤**
3. **Dev Agent** 自動接取：
   - 建立專用 Git worktree（`feat/issue-{number}-...`）
   - 建立設計畫布（`docs/designs/feat-xxx.md`）
   - 遵循 TDD：先寫測試，再實作
   - 開啟 PR 並標記「Closes #{issue_number}」
4. **Review Agent** 驗證 PR：
   - 檢查程式碼品質和測試覆蓋率
   - 如有設定則執行 E2E 驗證
   - 全部檢查通過則自動合併，或退回開發修復

### 開發者指令

```bash
# 恢復開發階段（審查回饋後）
bash skills/autonomous-dispatcher/scripts/autonomous-dev.sh \
  --issue 42 --mode resume --session <session-id>

# 手動執行審查 agent
bash skills/autonomous-dispatcher/scripts/autonomous-review.sh --issue 42

# 查看 agent 日誌
tail -f /tmp/agent-my-project-issue-42.log
tail -f /tmp/agent-my-project-review-42.log

# 查看開啟中的 PRs
gh pr list --repo owner/repo --state open
```

## 架構

### 三個核心腳本

| 腳本 | 角色 |
|------|------|
| `autonomous-dev.sh` | Dev agent 封裝 — 建立 PR、處理恢復/失敗 |
| `autonomous-review.sh` | Review agent 封裝 — 驗證 PR、合併或退回 |
| `dispatch-local.sh` | 流程產生器，含並發控制 |

### TDD 強制鉤子 (Hooks)

位於 `skills/autonomous-common/hooks/`，這些 PreToolUse 鉤子強制執行紀律：

| 鉤子 | 用途 |
|------|------|
| `block-push-to-main` | 阻擋直接推送至 main 分支 |
| `block-commit-outside-worktree` | 確保在專用 worktrees 中作業 |
| `check-design-canvas` | 程式碼前要求設計文件 |
| `check-code-simplifier` | 執行程式碼品質檢查 |
| `check-pr-review` | 驗證 PR 審查要求 |
| `check-unit-tests` | 強制測試優先開發 |
| `check-rebase-before-push` | 確保推送前乾淨變基 |
| `warn-skip-verification` | 跳過驗證步驟時警告 |

### Agent 抽象層

系統透過 `lib-agent.sh` 抽象 AI agent CLI，支援：

- **Claude Code**（預設）
- **Codex**
- **Kiro**
- **通用備援**（任何接受 `-p prompt` 的 CLI）

### 認證

`lib-auth.sh` 兩種模式：

1. **Token 模式**（`GH_AUTH_MODE=token`）：使用 `GH_TOKEN` 環境變數或 `gh auth`
2. **GitHub App 模式**（`GH_AUTH_MODE=app`）：使用短期權杖配合背景刷新 daemon。支援開發和審查 agents 使用不同的 App ID。

### 並發控制

`dispatch-local.sh` 透過 `MAX_CONCURRENT` 設定限制並發 agents（預設：5）。PID guard 防止同一 issue 的重複執行個體。

## 檔案結構

```
skills/
├── autonomous-dev/              # Dev agent skill
│   └── SKILL.md               # TDD 流程、design canvas、worktree 生命週期
├── autonomous-review/         # Review agent skill
│   └── SKILL.md               # PR 審查清單、E2E 驗證、自動合併
├── autonomous-dispatcher/      # Dispatcher skill
│   ├── SKILL.md               # Issue 掃描器、cron 派遣、停滯偵測
│   └── scripts/
│       ├── autonomous-dev.sh
│       ├── autonomous-review.sh
│       ├── dispatch-local.sh
│       ├── lib-agent.sh        # Agent CLI 抽象層
│       ├── lib-auth.sh        # GitHub 認證
│       ├── autonomous.conf.example
│       └── gh-app-token.sh
└── autonomous-common/         # 共享資源
    ├── hooks/                  # TDD 強制鉤子（11 個腳本）
    └── scripts/
        ├── gh-as-user.sh       # Bot 安全審查觸發
        ├── mark-issue-checkbox.sh
        ├── reply-to-comments.sh
        ├── resolve-threads.sh
        └── upload-screenshot.sh
```

## 設定參考

完整設定請參閱 `skills/autonomous-dispatcher/scripts/autonomous.conf.example`。

### 重要環境變數

| 變數 | 預設 | 描述 |
|------|------|------|
| `AUTONOMOUS_CONF` | 自動偵測 | 設定檔路徑 |
| `GH_AUTH_MODE` | `token` | `token` 或 `app` |
| `AGENT_CMD` | `claude` | Agent CLI |
| `AGENT_DEV_MODEL` | （無） | 覆寫開發 agent 模型 |
| `AGENT_REVIEW_MODEL` | `sonnet` | 覆寫審查 agent 模型 |
| `MAX_CONCURRENT` | `5` | 最大並發 agents 數 |
| `E2E_ENABLED` | `false` | 啟用 E2E 驗證 |
| `E2E_PREVIEW_URL_PATTERN` | — | 預覽 URL 模式（例如 `https://pr-{N}.preview.app`）|

## 標籤與狀態機

```
pending-dev → in-progress → pending-review → reviewing → approved → merged
     ↑              ↓             ↓           ↓
     ←─────── (失敗) ←────────┘           ↓
                                            （no-auto-close）
```

- `pending-dev`：等待開發
- `in-progress`：Dev agent 正在作業
- `pending-review`：開發完成，等待審查
- `reviewing`：Review agent 正在作業
- `approved`：審查通過，準備合併
- `no-auto-close`：審查通過但跳過自動合併（需要手動合併）

---

## 程式碼對照驗證

以下為文件所述與實際程式碼的對照：

| 文件描述 | 實際程式碼位置 | 驗證狀態 |
|----------|----------------|----------|
| autonomous-dev.sh 處理 --mode new/resume | `lib-agent.sh:run_agent()`, `lib-agent.sh:resume_agent()` | ✅ 符合 |
| 標籤轉換：成功→pending-review，失敗→pending-dev | `autonomous-dev.sh:cleanup()` 第 141-166 行 | ✅ 符合 |
| autonomous-review.sh 找 PR、審查、合併/退回 | `autonomous-review.sh:Find PR`, 第 131-157 行 | ✅ 符合 |
| E2E 驗證透過 Chrome DevTools MCP | `autonomous-review.sh:E2E Block` 第 320-422 行 | ✅ 符合 |
| dispatch-local.sh 並發控制 PID guard | `lib-agent.sh:acquire_pid_guard()` 第 34-46 行 | ✅ 符合 |
| lib-agent.sh 支援 claude/codex/kiro | 第 56-86 行 `run_agent()`, 第 93-121 行 `resume_agent()` | ✅ 符合 |
| Hooks 列表與用途 | `hooks/README.md` 與 `skills/autonomous-common/hooks/` 各腳本 | ✅ 符合 |
| Label 狀態機流程 | 各 script 中 `gh issue edit --add-label/--remove-label` 呼叫 | ✅ 符合 |

**結論**：文件所述流程、腳本功能、狀態機制與實際程式碼完全相符。
