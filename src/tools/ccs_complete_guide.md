📖 CCS (Claude Code Switch) 完整指南

  🎯 核心功能（三大支柱）

  | 功能類型         | 說明                                      | 管理方式  |
  |------------------|-------------------------------------------|-----------|
  | 多個 Claude 帳號 | 同時運行工作/個人 Claude 訂閱帳號         | Dashboard |
  | OAuth 供應商     | Gemini、Codex、Copilot 等，免 API key     | Dashboard |
  | API Profiles     | GLM、Kimi 或任何相容 Anthropic API 的服務 | Dashboard |

  ---
  🚀 快速開始

  1. 安裝

  npm install -g @kaitranntt/ccs

  # 其他套件管理器
  yarn global add @kaitranntt/ccs
  pnpm add -g @kaitranntt/ccs
  bun add -g @kaitranntt/ccs

  2. 開啟 Dashboard

  ccs config
  # 開啟 http://localhost:3000

  3. 設定帳號

  - Claude 帳號: 建立隔離實例
  - OAuth 認證: Gemini、Codex、Copilot
  - API Keys: GLM、Kimi、DeepSeek
  - 健康監控: 即時狀態檢查

  ---
  💻 基本使用

  內建供應商指令

  | 供應商        | 指令                    | 認證方式 | 適用場景            |
  |---------------|-------------------------|----------|---------------------|
  | Claude        | ccs                     | 訂閱     | 預設、策略規劃      |
  | Gemini        | ccs gemini              | OAuth    | 零配置、快速迭代    |
  | Codex         | ccs codex               | OAuth    | 程式碼生成          |
  | Copilot       | ccs ghcp 或 ccs copilot | OAuth    | GitHub Copilot 模型 |
  | Kiro          | ccs kiro                | OAuth    | AWS CodeWhisperer   |
  | Antigravity   | ccs agy                 | OAuth    | 替代路由            |
  | OpenRouter    | ccs openrouter          | API Key  | 300+ 模型統一 API   |
  | GLM           | ccs glm                 | API Key  | 成本優化            |
  | Kimi          | ccs kimi                | API Key  | 長上下文、思考模式  |
  | Azure Foundry | ccs foundry             | API Key  | Claude via Azure    |
  | Minimax       | ccs minimax             | API Key  | M2 系列、1M 上下文  |
  | DeepSeek      | ccs deepseek            | API Key  | V3.2 和 R1 推理     |
  | Qwen          | ccs qwen                | API Key  | 阿里雲、qwen3-coder |

  ---
  🔧 多帳號 Claude 管理

  建立獨立 Claude 實例

  # 建立工作帳號
  ccs auth create work

  # 建立個人帳號
  ccs auth create personal

  # 建立客戶專案帳號
  ccs auth create client-projectX

  並行使用

  # 終端機 1 - 工作帳號
  ccs work "實作新功能"

  # 終端機 2 - 個人帳號
  ccs personal "審查程式碼"

  # 終端機 3 - 預設帳號
  ccs "寫技術文件"

  ---
  🌊 平行工作流程範例

  場景：開發新功能

  # 終端機 1: 規劃架構 (Claude Pro - 高品質思考)
  ccs work "設計使用者認證系統的架構，包含 OAuth2.0 和 JWT"

  # 終端機 2: 快速原型 (Gemini - 免費且快速)
  ccs gemini "根據規劃實作基本的登入功能 prototype"

  # 終端機 3: 成本優化執行 (GLM - 省成本)
  ccs glm "實作使用者資料庫 CRUD 操作"

  # 終端機 4: 安全審查 (DeepSeek - 推理能力強)
  ccs deepseek "審查認證系統的安全性漏洞"

  場景：程式碼審查 + 測試

  # 終端機 1: Code Review
  ccs gemini "審查這個 PR 的程式碼品質"

  # 終端機 2: 撰寫測試
  ccs codex "為這個功能寫單元測試和整合測試"

  # 終端機 3: 文件撰寫
  ccs "更新 API 文件和使用範例"

  ---
  ⚙️ 管理指令

  帳號管理

  # 建立新的 Claude 帳號實例
  ccs auth create <profile-name>

  # 列出所有帳號
  ccs auth list

  # 刪除帳號
  ccs auth remove <profile-name>

  API Profile 管理

  # 建立 API profile（互動式）
  ccs api create

  # 使用預設範本建立
  ccs api create --preset glm
  ccs api create --preset openrouter
  ccs api create --preset foundry

  # 列出所有 API profiles
  ccs api list

  # 刪除 API profile
  ccs api remove <profile-name>

  系統維護

  # 健康檢查
  ccs doctor

  # 更新到最新版本
  ccs update
  ccs update --force      # 強制重新安裝
  ccs update --beta       # 安裝開發版本

  # 同步共享項目（commands、skills、settings）
  ccs sync

  # 顯示幫助
  ccs --help

  ---
  🌐 WebSearch 功能

  工作原理

  | Profile 類型    | WebSearch 方法          |
  |-----------------|-------------------------|
  | Claude (原生)   | Anthropic WebSearch API |
  | 第三方 profiles | CLI 工具備援鏈          |

  CLI 工具備援順序

  | 優先順序 | 工具       | 認證         | 安裝指令                                      |
  |----------|------------|--------------|-----------------------------------------------|
  | 1st      | Gemini CLI | OAuth (免費) | npm install -g @google/gemini-cli             |
  | 2nd      | OpenCode   | OAuth (免費) | curl -fsSL https://opencode.ai/install | bash |
  | 3rd      | Grok CLI   | API Key      | npm install -g @vibe-kit/grok-cli             |

  設定方式

  透過 Dashboard: Settings 頁面

  透過配置檔 (~/.ccs/config.yaml):
  websearch:
    enabled: true
    gemini:
      enabled: true
      model: gemini-2.5-flash
    opencode:
      enabled: true
    grok:
      enabled: false  # 需要 XAI_API_KEY

  ---
  🔌 遠端 CLIProxy

  使用場景

  - 團隊共享: 一個 CLIProxyAPI server 給多個開發者
  - 成本優化: 集中式 API key 管理
  - 網路隔離: API credentials 保存在安全伺服器

  CLI 使用

  # 指定遠端 proxy
  ccs gemini --proxy-host 192.168.1.100 --proxy-port 8317

  # HTTPS proxy
  ccs codex --proxy-host proxy.example.com --proxy-protocol https

  # 使用認證 token
  ccs gemini --proxy-host remote.example.com --proxy-auth-token "your-token"

  # 強制本地模式
  ccs gemini --local-proxy

  # 只使用遠端（失敗時不備援）
  ccs gemini --remote-only

  ---
  📁 重要路徑

  | 項目            | 路徑                    |
  |-----------------|-------------------------|
  | 主配置檔        | ~/.ccs/config.yaml      |
  | Claude 帳號資料 | ~/.ccs/<profile-name>/  |
  | OAuth tokens    | ~/.ccs/cliproxy/auth/   |
  | 共享 commands   | ~/.ccs/shared/commands/ |
  | 共享 skills     | ~/.ccs/shared/skills/   |
  | 共享 agents     | ~/.ccs/shared/agents/   |

  ---
  🎓 實用技巧

  1. 成本優化策略

  # 高成本任務用 Claude
  ccs work "複雜的系統設計和架構決策"

  # 中等任務用 Gemini (免費 OAuth)
  ccs gemini "實作標準功能"

  # 大量執行用 GLM (便宜)
  ccs glm "批次處理資料轉換"

  2. 專案隔離

  # 為每個客戶建立獨立 profile
  ccs auth create client-acme
  ccs auth create client-globex

  # 避免上下文混淆
  ccs client-acme "處理 ACME 專案需求"
  ccs client-globex "處理 Globex 專案需求"

  3. 快速切換

  # 短別名最快
  ccs           # 預設
  ccs work      # 工作
  ccs gemini    # Gemini
  ccs glm       # GLM

  ---
  🐛 故障排除

  常見問題

  1. OAuth 認證失敗
  # 刪除舊 token 重新認證
  rm -rf ~/.ccs/cliproxy/auth/
  ccs gemini  # 會重新開啟瀏覽器認證

  2. Profile 無法連線
  ccs doctor  # 執行診斷

  3. 配置檔損壞
  # 備份並重置
  cp ~/.ccs/config.yaml ~/.ccs/config.yaml.backup
  ccs sync

  4. Windows 符號連結問題
  - 啟用開發者模式 (Settings → For developers → Developer Mode)
  - 重新安裝: npm install -g @kaitranntt/ccs

  ---
  📚 更多資源

  | 主題         | 連結                                                     |
  |--------------|----------------------------------------------------------|
  | 官方網站     | https://ccs.kaitran.ca                                   |
  | 文件         | https://docs.ccs.kaitran.ca                              |
  | 安裝指南     | https://docs.ccs.kaitran.ca/getting-started/installation |
  | API Profiles | https://docs.ccs.kaitran.ca/providers/api-profiles       |
  | 遠端 Proxy   | https://docs.ccs.kaitran.ca/features/remote-proxy        |
  | Issue 回報   | https://github.com/kaitranntt/ccs/issues                 |

  ---
  ⚡ 快速參考卡

  # 安裝與設定
  npm install -g @kaitranntt/ccs
  ccs config                    # 開啟 Dashboard

  # 基本使用
  ccs                          # Claude 預設
  ccs gemini                   # Gemini
  ccs glm                      # GLM
  ccs work                     # 自訂 profile

  # 管理
  ccs auth create <name>       # 建立帳號
  ccs api create               # 建立 API profile
  ccs doctor                   # 健康檢查
  ccs update                   # 更新
  ccs sync                     # 同步共享項目

  # 進階
  ccs gemini --proxy-host <ip> # 遠端 proxy
  ccs --help                   # 顯示幫助

  ---
  核心哲學:
  - ✅ YAGNI: 不做「以防萬一」的功能
  - ✅ KISS: 保持簡單
  - ✅ DRY: 單一資料來源 (config.yaml)

