# Ruler - 統一 AI 編程工具規則管理系統

## 目錄

- [專案概述](#專案概述)
- [核心功能](#核心功能)
- [快速開始](#快速開始)
- [檔案結構](#檔案結構)
- [配置詳解](#配置詳解)
- [進階功能](#進階功能)
- [最佳實踐](#最佳實踐)
- [支援的 AI 工具](#支援的-ai-工具)

## 專案概述

**Ruler** 的設計哲學是「**apply the same rules to all coding agents**」，它不僅提供統一的規則管理，更重要的是確保這些規則能夠有效地傳達給各種 AI 編程工具，並透過自動化機制保證規則的執行一致性。

### 解決的核心問題

在多 AI 工具的開發環境中，團隊面臨的挑戰包括：

- **不一致的指導**：不同 AI 工具間的規則不統一
- **重複維護成本**：需要維護多個配置檔案
- **上下文漂移**：隨著專案需求演變，規則容易不同步
- **新工具導入困難**：每次引入新 AI 工具都需要重新配置
- **複雜專案結構**：不同元件需要不同的上下文特定指令

### Ruler 的解決方案

Ruler 透過以下機制解決這些問題：

1. **集中化規則管理**：使用專門的 `.ruler/` 目錄儲存所有 AI 指令
2. **巢狀規則載入**：支援複雜專案結構的上下文特定指令
3. **自動分發機制**：自動將規則套用到支援的 AI 代理工具配置檔案
4. **精確代理配置**：透過 `ruler.toml` 細調哪些代理受影響及其特定輸出路徑
5. **MCP 伺服器傳播**：管理和分發 Model Context Protocol (MCP) 伺服器設定

## 核心功能

### 1. 統一規則管理
- 單一來源的真實性（Single Source of Truth）
- 跨多個 AI 工具的一致性
- 自動化規則分發

### 2. 巢狀規則載入
- 支援 Monorepo 架構
- 上下文感知的規則應用
- 階層式規則繼承

### 3. MCP 伺服器整合
- Model Context Protocol 支援
- 統一的伺服器配置管理
- 跨工具的上下文共享

### 4. 版本控制整合
- 自動 `.gitignore` 管理
- 備份與回復機制
- 安全的實驗環境

## Ruler 的運作原理

### 規則檔案的標準化輸出

當你執行 `ruler apply` 時，ruler 會：

1. **讀取** `.ruler/` 目錄下的所有規則檔案
2. **自動生成**每個 AI 工具專屬的配置檔案
3. **寫入**到各 AI 工具預期的位置

```bash
# 執行 ruler apply 後的檔案生成流程
.ruler/AGENTS.md  ──────┐
.ruler/coding_style.md  ├──> 自動轉換並生成
.ruler/api_rules.md     │
                        ↓
├── CLAUDE.md                    # Claude Code 會讀取這個
├── .cursor/rules/ruler_cursor_instructions.mdc  # Cursor 會讀取這個
├── .github/copilot-instructions.md  # GitHub Copilot 會讀取這個
├── .codex/rules.md              # Codex 會讀取這個
└── .clinerules                  # Cline 會讀取這個
```

### AI 工具的內建機制

每個 AI 工具都有自己的**規則檔案約定**：

| AI 工具 | 預期的規則檔案位置 | 工具如何發現規則 |
|---------|-------------------|-----------------|
| **Claude Code** | `CLAUDE.md` (根目錄) | Claude Code 啟動時自動掃描專案根目錄尋找 `CLAUDE.md` |
| **Cursor** | `.cursor/rules/*.mdc` | Cursor IDE 會自動載入 `.cursor/rules/` 目錄下的所有 `.mdc` 檔案 |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Copilot 擴充功能會自動讀取這個路徑 |
| **Windsurf** | `.windsurf/rules/*.md` | Windsurf 會掃描其專屬目錄 |
| **Cline** | `.clinerules` | Cline 會在專案根目錄尋找這個檔案 |
| **Aider** | `AGENTS.md`, `.aider.conf.yml` | Aider 會讀取這兩個配置檔案 |
| **Codex** | `.codex/rules.md` | Codex 會在專案中掃描 `.codex/` 目錄下的規則檔案 |

### 運作流程圖

```
開發者編寫規則 → ruler apply → 生成各工具配置 → AI 工具自動載入
     ↓                ↓              ↓                ↓
.ruler/AGENTS.md   處理與轉換    CLAUDE.md等      即時生效
```

### 為什麼 AI 工具會遵守這些規則？

1. **約定優於配置 (Convention over Configuration)**
   - 每個 AI 工具都有預定義的檔案路徑
   - 它們會自動尋找並載入這些檔案

2. **自動發現機制**
   - AI 工具在啟動或每次互動時會掃描特定位置
   - 發現規則檔案後自動載入並應用

3. **即時生效**
   - 大多數工具在每次互動時重新讀取規則
   - 某些工具可能需要重新啟動才能載入新規則

### MCP (Model Context Protocol) 的角色

MCP 檔案提供額外的上下文配置，定義 AI 工具可以訪問的外部服務和資源：

- **`.mcp.json`** - Claude Code 的 MCP 伺服器配置
- **`.cursor/mcp.json`** - Cursor 的 MCP 伺服器配置
- **`.vscode/mcp.json`** - GitHub Copilot 的 MCP 配置

這些配置允許 AI 工具訪問檔案系統、Git 倉庫、資料庫等外部資源。

## 快速開始

### 安裝

```bash
# 全域安裝（推薦用於 CLI）
npm install -g @intellectronica/ruler

# 或使用 npx（一次性命令）
npx @intellectronica/ruler apply
```

### 初始化專案

```bash
# 導航到專案根目錄
cd your-project

# 初始化 ruler
ruler init

# 建立全域配置（可選）
ruler init --global
```

### 套用規則

```bash
# 套用規則到所有配置的代理工具
ruler apply

# 只套用到特定代理工具
ruler apply --agents copilot,claude,codex

# 使用巢狀規則載入
ruler apply --nested

# 預覽變更而不實際寫入檔案
ruler apply --dry-run
```

## 檔案結構

### 基本目錄結構

```
.ruler/
├── AGENTS.md           # 主要規則檔案
├── ruler.toml          # 主配置檔案
└── coding_style.md     # 額外的規則檔案
```

### 規則檔案優先順序

1. **儲存庫根目錄的 `AGENTS.md`**（最高優先級，會被前置）
2. **`.ruler/AGENTS.md`**（新的預設起始檔案）
3. **傳統的 `.ruler/instructions.md`**（僅當 `.ruler/AGENTS.md` 不存在時）
4. **其餘在 `.ruler/` 下的 `*.md` 檔案**（按排序順序）

每個檔案的內容都會加上 `--- Source: <relative_path_to_md_file> ---` 標記以便追蹤。

### 巢狀規則結構範例

```
project/
├── .ruler/                 # 全域專案規則
│   ├── AGENTS.md
│   └── coding_style.md
├── src/
│   └── .ruler/             # 元件特定規則
│       └── api_guidelines.md
├── tests/
│   └── .ruler/             # 測試特定規則
│       └── testing_conventions.md
└── docs/
    └── .ruler/             # 文檔規則
        └── writing_style.md
```

## 配置詳解

### ruler.toml 配置檔案

```toml
# 預設執行的代理工具
default_agents = ["copilot", "claude", "aider", "codex"]

# 全域 MCP 伺服器配置
[mcp]
enabled = true
merge_strategy = "merge"

# MCP 伺服器定義
[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]

[mcp_servers.git]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-git", "--repository", "."]

# 自動 .gitignore 配置
[gitignore]
enabled = true

# 代理工具特定配置
[agents.copilot]
enabled = true
output_path = ".github/copilot-instructions.md"

[agents.claude]
enabled = true
output_path = "CLAUDE.md"

[agents.cursor]
enabled = true
output_path = ".cursor/rules/ruler_cursor_instructions.mdc"

[agents.codex]
enabled = true
output_path = ".codex/rules.md"
mcp_config_path = ".codex/mcp.json"
```

### MCP 伺服器配置

#### 本地/stdio 伺服器

```toml
[mcp_servers.local_server]
command = "node"
args = ["server.js"]

[mcp_servers.local_server.env]
DEBUG = "1"
API_KEY = "your-api-key"
```

#### 遠端伺服器

```toml
[mcp_servers.remote_server]
url = "https://api.example.com"

[mcp_servers.remote_server.headers]
Authorization = "Bearer token"
"X-API-Version" = "v1"
```

## 進階功能

### Codex 整合配置

#### Codex 特定設定

Codex 是一個先進的 AI 編程助手，支援深度程式碼理解和生成。透過 Ruler 可以為 Codex 配置特定的規則和 MCP 伺服器。

##### 基本 Codex 配置 (.ruler/codex_config.md)

```markdown
# Codex 開發規範

## 程式碼生成原則
- 優先生成可測試和可維護的程式碼
- 遵循 SOLID 原則
- 使用適當的設計模式
- 生成程式碼時包含必要的註解

## 效能優化
- 避免不必要的記憶體分配
- 使用適當的資料結構
- 考慮時間和空間複雜度

## API 設計
- 保持介面簡潔明瞭
- 提供清晰的錯誤訊息
- 實作適當的驗證邏輯
```

##### Codex MCP 伺服器配置

在 `ruler.toml` 中加入 Codex 特定的 MCP 伺服器：

```toml
[agents.codex]
enabled = true
output_path = ".codex/rules.md"
mcp_config_path = ".codex/mcp.json"
# Codex 特定選項
use_context_aware_generation = true
max_context_length = 8000
include_test_generation = true

[mcp_servers.codex_analyzer]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-code-analyzer"]
# Codex 專用的程式碼分析伺服器

[mcp_servers.codex_linter]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-eslint", "--config", ".eslintrc.json"]
# 整合 linter 以確保生成的程式碼品質
```

##### Codex 巢狀規則範例

```bash
# 為不同模組建立 Codex 特定規則
mkdir -p backend/.codex
cat > backend/.codex/backend_rules.md << 'EOF'
# 後端 Codex 規範

## 資料庫互動
- 使用 ORM 而非原生 SQL
- 實作交易處理
- 加入適當的索引提示

## API 端點生成
- 自動生成 OpenAPI 文檔
- 包含請求驗證邏輯
- 實作錯誤處理中介軟體
EOF

mkdir -p frontend/.codex
cat > frontend/.codex/frontend_rules.md << 'EOF'
# 前端 Codex 規範

## 組件生成
- 生成 TypeScript 類型定義
- 包含 Props 驗證
- 實作無障礙功能 (a11y)

## 狀態管理
- 使用 Context API 或 Redux
- 避免 prop drilling
- 實作適當的 memorization
EOF
```

### 回復機制

```bash
# 回復所有 ruler 變更
ruler revert

# 預覽會被回復的內容
ruler revert --dry-run

# 只回復特定代理工具
ruler revert --agents claude,copilot

# 回復後保留備份檔案
ruler revert --keep-backups
```

### 自動 .gitignore 管理

Ruler 自動管理 `.gitignore` 檔案，確保生成的代理工具配置檔案不會被意外提交：

```gitignore
# Your existing rules
node_modules/
*.log

# START Ruler Generated Files
.aider.conf.yml
.clinerules
.codex/rules.md
.cursor/rules/ruler_cursor_instructions.mdc
.github/copilot-instructions.md
.windsurf/rules/ruler_windsurf_instructions.md
AGENTS.md
CLAUDE.md
# END Ruler Generated Files

dist/
```

### 命令列選項

| 選項 | 說明 |
|------|------|
| `--project-root <path>` | 專案根目錄路徑 |
| `--agents <agent1,agent2>` | 指定要套用的代理工具 |
| `--config <path>` | 自訂 ruler.toml 配置檔路徑 |
| `--nested` | 啟用巢狀規則載入 |
| `--dry-run` | 預覽變更而不寫入檔案 |
| `--verbose` | 顯示詳細執行過程 |
| `--no-gitignore` | 停用 .gitignore 自動更新 |

## 最佳實踐

### 團隊協作工作流程

#### 1. 建立團隊規範

```bash
# 建立團隊共用的規則檔案
mkdir -p .ruler
cat > .ruler/AGENTS.md << 'EOF'
# 團隊開發規範

## 程式碼品質標準
- 所有函數都必須有文檔字串
- 使用類型提示提高程式碼可讀性
- 遵循專案的命名約定

## 測試要求
- 新功能必須包含測試
- 測試覆蓋率維持在 80% 以上
- 使用描述性的測試名稱
EOF

# 套用到所有代理工具
ruler apply
```

#### 2. 版本控制整合

```bash
# 將 .ruler 目錄提交到儲存庫
git add .ruler/
git commit -m "feat: add team AI coding standards with ruler"

# 團隊成員拉取變更後套用配置
git pull
ruler apply
```

#### 3. package.json 腳本整合

```json
{
  "scripts": {
    "ruler:apply": "ruler apply",
    "dev": "npm run ruler:apply && your_dev_command",
    "precommit": "npm run ruler:apply"
  }
}
```

### Monorepo 的巢狀規則策略

```bash
# 建立服務特定的規則
mkdir -p services/api/.ruler
cat > services/api/.ruler/api_standards.md << 'EOF'
# API 服務開發規範

## 資料庫操作
- 使用連線池管理資料庫連線
- 實作適當的查詢超時
- 記錄慢查詢用於效能監控
EOF

mkdir -p services/frontend/.ruler
cat > services/frontend/.ruler/frontend_standards.md << 'EOF'
# 前端開發規範

## React 最佳實踐
- 使用函數式元件和 Hooks
- 實作適當的錯誤邊界
- 優化組件重新渲染
EOF

# 套用巢狀規則
ruler apply --nested --verbose
```

### 規則檔案範例

#### 基本規則檔案 (.ruler/AGENTS.md)

```markdown
# 專案開發規範

## 程式碼風格
- 遵循 PEP 8 規範（Python 專案）
- 使用類型提示標註所有函數簽名和複雜變數
- 保持函數簡短並專注於單一任務

## 錯誤處理
- 使用特定的異常類型而不是通用的 `Exception`
- 有效記錄錯誤並提供上下文資訊

## 安全性
- 始終驗證和清理使用者輸入
- 注意潛在的注入漏洞
```

#### API 規則檔案 (.ruler/api_conventions.md)

```markdown
# API 設計約定

## RESTful API 設計
- 使用適當的 HTTP 動詞（GET, POST, PUT, DELETE）
- 回應狀態碼必須正確且一致
- API 端點命名使用複數名詞

## 資料驗證
- 所有輸入都必須使用 zod 進行驗證
- 錯誤回應格式必須統一
- 實作適當的速率限制

## 文件要求
- 每個 API 端點都必須有 OpenAPI 規範
- 包含請求/回應範例
- 標註必要的認證要求
```

#### 測試規則檔案 (.ruler/testing_conventions.md)

```markdown
# 測試開發規範

## 測試結構
- 遵循 AAA 模式（Arrange, Act, Assert）
- 測試函數名稱必須描述性強
- 每個測試只驗證一個行為

## 測試覆蓋率
- 單元測試覆蓋率不低於 85%
- 關鍵業務邏輯必須 100% 覆蓋
- 包含邊界條件測試

## Mock 使用
- 優先使用測試替身而非真實服務
- Mock 物件的行為必須與真實物件一致
- 避免過度 Mock 導致測試失去意義
```

## 支援的 AI 工具

| Agent | 規則檔案 | MCP 配置 |
|-------|----------|----------|
| GitHub Copilot | `.github/copilot-instructions.md` | `.vscode/mcp.json` |
| Claude Code | `CLAUDE.md` | `.mcp.json` |
| Cursor | `.cursor/rules/ruler_cursor_instructions.mdc` | `.cursor/mcp.json` |
| Windsurf | `.windsurf/rules/ruler_windsurf_instructions.md` | - |
| Cline | `.clinerules` | - |
| Aider | `AGENTS.md`, `.aider.conf.yml` | `.mcp.json` |
| Amazon Q CLI | `.amazonq/rules/ruler_q_rules.md` | `.amazonq/mcp.json` |
| Zed | `AGENTS.md` | `.zed/settings.json` |
| Codex | `.codex/rules.md` | `.codex/mcp.json` |

## 結論

Ruler 是一個強大的工具，專為管理多個 AI 編程助手的規則和配置而設計。透過集中化管理、巢狀規則載入和自動化分發機制，它大大簡化了團隊在使用多個 AI 工具時的配置管理工作，確保了開發標準的一致性和可維護性。

無論是小型專案還是大型 Monorepo，Ruler 都能提供靈活且強大的規則管理解決方案，讓團隊能夠專注於開發工作，而不是花時間在重複的配置管理上。
