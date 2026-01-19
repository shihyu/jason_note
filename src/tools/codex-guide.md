# Codex CLI 完整指南

## 目錄

- [目錄結構](#目錄結構)
- [配置文件說明](#配置文件說明)
- [instructions.md 全域指令](#instructionsmd-全域指令)
- [使用方式](#使用方式)
- [Profile 快捷切換](#profile-快捷切換)
- [常用指令](#常用指令)

---

## 目錄結構

```
~/.codex/
├── config.toml          # 主配置文件
├── instructions.md      # 全域指令 (類似 Claude Code 的 CLAUDE.md)
├── rules/               # 規則目錄
│   └── default.rules    # 指令白名單規則
├── skills/              # 自訂技能
├── sessions/            # 會話記錄
├── auth.json            # 認證資訊
└── history.jsonl        # 歷史紀錄
```

---

## 配置文件說明

### 完整 config.toml

```toml
# ========================================
# Codex CLI 工程師完整配置
# ========================================

# 模型設定
model = "gpt-5.2-codex"
model_reasoning_effort = "high"          # minimal | low | medium | high
model_context_window = 200000            # 上下文視窗大小
model_max_output_tokens = 100000         # 最大輸出 token

# 啟用網路搜尋功能
# web_search 是命令列參數，不是 config 選項，已移除

# 完全自動模式 - 跳過所有確認提示
approval_policy = "never"                # untrusted | on-failure | on-request | never

# 關閉沙盒限制
sandbox_mode = "danger-full-access"      # read-only | workspace-write | danger-full-access

# 編輯器整合 (nvim 用戶不需設定，直接註解掉)
# file_opener = "vscode"                 # vscode | vscode-insiders | cursor | windsurf

# 顯示設定
hide_agent_reasoning = false             # 顯示 AI 推理過程
show_raw_agent_reasoning = false         # 顯示原始推理內容

# 專案根目錄偵測標記
project_root_markers = [".git", ".hg", "Makefile", "package.json", "Cargo.toml", "go.mod"]

# ========================================
# 功能開關
# ========================================
# [features]
# shell_snapshot = true                  # 加速重複指令執行
# web_search_request = true              # 允許 AI 主動搜尋網路

# ========================================
# 全域信任設定
# ========================================
[projects."*"]
trust_level = "trusted"

# ========================================
# 沙盒網路設定 (當使用 workspace-write 模式時)
# ========================================
[sandbox_workspace_write]
network_access = true

# ========================================
# 環境變數政策
# ========================================
[shell_environment_policy]
inherit = "all"                          # none | all | allowlist
ignore_default_excludes = false
# 排除敏感環境變數
exclude = ["AWS_SECRET*", "AZURE_*", "GCP_*", "*_TOKEN", "*_KEY", "*_SECRET"]

# ========================================
# 配置 Profiles (可選)
# ========================================
# 使用方式: codex --profile quick
[profiles.quick]
model_reasoning_effort = "low"
approval_policy = "never"

[profiles.careful]
model_reasoning_effort = "high"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
```

### 配置項說明

#### 模型設定

| 配置 | 說明 | 可選值 |
|------|------|--------|
| `model` | 使用的 AI 模型 | 模型名稱 |
| `model_reasoning_effort` | 推理深度 | `minimal`, `low`, `medium`, `high` |
| `model_context_window` | 上下文視窗大小 | 數字 (tokens) |
| `model_max_output_tokens` | 最大輸出長度 | 數字 (tokens) |

#### 權限控制

| 配置 | 說明 | 可選值 |
|------|------|--------|
| `approval_policy` | 審批政策 | `untrusted`, `on-failure`, `on-request`, `never` |
| `sandbox_mode` | 沙盒模式 | `read-only`, `workspace-write`, `danger-full-access` |
| `trust_level` | 專案信任等級 | `untrusted`, `sandbox`, `trusted` |

#### approval_policy 詳解

| 值 | 行為 |
|----|------|
| `untrusted` | 只有白名單指令自動執行，其他都要確認 |
| `on-failure` | 自動執行，失敗時才詢問 |
| `on-request` | AI 決定何時詢問 |
| `never` | 永不詢問，完全自動 |

#### sandbox_mode 詳解

| 值 | 行為 |
|----|------|
| `read-only` | 只能讀取，不能修改檔案 |
| `workspace-write` | 可在工作目錄內讀寫 |
| `danger-full-access` | 完全無限制 |

---

## instructions.md 全域指令

### 作用

`~/.codex/instructions.md` 是 Codex 的**全域指令文件**，類似 Claude Code 的 `~/.claude/CLAUDE.md`。

**每次啟動 Codex 時會自動讀取此文件**，用於：

1. 定義 AI 的工作守則和行為規範
2. 設定環境資訊（如 sudo 密碼）
3. 指定偏好的工具和工作流程
4. 制定代碼品質標準

### 與 Claude Code 對照

| Claude Code | Codex | 用途 |
|-------------|-------|------|
| `~/.claude/CLAUDE.md` | `~/.codex/instructions.md` | 全域指令 |
| `~/.claude/rules/` | `~/.codex/rules/` | 規則目錄 |
| 專案內 `.claude/CLAUDE.md` | 專案內 `AGENTS.md` | 專案指令 |

### 建議內容結構

```markdown
# Codex 工作守則

## 環境設定
- sudo 密碼
- 偏好工具 (rg, fd, nvim 等)

## 工作流程
- TDD 流程
- plan.md 規範
- 分段執行原則

## 代碼品質
- 命名規範
- 安全性要求
- Git 工作流

## 禁止行為
- 不要先寫實作再補測試
- 不要過度設計
```

---

## 使用方式

### 基本啟動

```bash
# 互動模式
codex

# 帶提示詞啟動
codex "幫我寫一個 Python hello world"

# 指定工作目錄
codex -C /path/to/project "分析這個專案"
```

### 附加圖片

```bash
codex -i screenshot.png "這個 UI 有什麼問題？"
codex -i img1.png -i img2.png "比較這兩張圖"
```

### 非互動模式 (exec)

```bash
# 執行單一任務後退出
codex exec "列出所有 TODO 註解"
codex e "統計程式碼行數"
```

### 啟用網路搜尋

```bash
codex --search "最新的 React 19 有什麼新功能？"
```

---

## Profile 快捷切換

### 什麼是 Profile

Profile 是預設的配置組合，讓你用一個參數快速切換不同的工作模式。

### 使用方式

```bash
# 使用預設配置
codex "你的指令"

# 使用 quick profile (低推理、快速回應)
codex --profile quick "簡單問題"
codex -p quick "簡單問題"

# 使用 careful profile (高推理、需確認、有沙盒)
codex --profile careful "重要的程式修改"
codex -p careful "重要的程式修改"
```

### 目前定義的 Profiles

| Profile | 推理深度 | 審批政策 | 沙盒模式 | 適用場景 |
|---------|---------|---------|---------|---------|
| (預設) | high | never | danger-full-access | 日常開發 |
| `quick` | low | never | danger-full-access | 簡單問答、快速任務 |
| `careful` | high | on-request | workspace-write | 重要專案、需要審核 |

### 自訂 Profile

在 `config.toml` 中新增：

```toml
[profiles.my-profile]
model_reasoning_effort = "medium"
approval_policy = "on-failure"
sandbox_mode = "workspace-write"
```

然後使用：

```bash
codex --profile my-profile "指令"
```

---

## 常用指令

### 會話管理

```bash
# 恢復上一次會話
codex resume
codex resume --last

# Fork 之前的會話
codex fork
codex fork --last
```

### 套用變更

```bash
# 套用 Codex 產生的 diff
codex apply
codex a
```

### Code Review

```bash
# 非互動式 code review
codex review
```

### MCP Server

```bash
# 以 MCP server 模式運行
codex mcp-server
```

### 查看功能開關

```bash
codex features
```

### 命令列覆蓋配置

```bash
# 覆蓋單一配置
codex -c model="gpt-4" "指令"
codex -c model_reasoning_effort="low" "指令"

# 啟用/停用功能
codex --enable shell_snapshot "指令"
codex --disable web_search_request "指令"
```

---

## 官方文檔

- [Configuration Reference](https://developers.openai.com/codex/config-reference/)
- [Sample Configuration](https://developers.openai.com/codex/config-sample/)
- [Advanced Configuration](https://developers.openai.com/codex/config-advanced/)
- [CLI Features](https://developers.openai.com/codex/cli/features/)
- [GitHub Repo](https://github.com/openai/codex)
