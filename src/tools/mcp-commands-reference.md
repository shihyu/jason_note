# Claude Code MCP 指令大全

## 📖 目錄
- [基本語法](#基本語法)
- [核心開發工具](#核心開發工具)
- [搜尋工具](#搜尋工具)
- [資料庫](#資料庫)
- [DevOps & 部署](#devops--部署)
- [專案管理](#專案管理)
- [開發輔助](#開發輔助)
- [管理指令](#管理指令)
- [快速安裝腳本](#快速安裝腳本)
- [推薦組合](#推薦組合)

---

## 基本語法

```bash
# stdio 傳輸（本地執行）
claude mcp add <名稱> <執行指令> <參數...>

# HTTP 傳輸（遠端服務）
claude mcp add --transport http <名稱> <URL>

# 範例
claude mcp add git npx --yes @cyanheads/git-mcp-server
claude mcp add --transport http grep https://mcp.grep.app
```

---

## 核心開發工具

### 檔案系統操作
```bash
# 必須指定允許存取的目錄
claude mcp add filesystem npx --yes @modelcontextprotocol/server-filesystem ~/projects

# 多個目錄
claude mcp add filesystem npx --yes @modelcontextprotocol/server-filesystem ~/projects ~/documents
```

### Git 版本控制
```bash
# 使用第三方套件
claude mcp add git npx --yes @cyanheads/git-mcp-server
```

### GitHub API
```bash
# 需要先設定 GitHub Personal Access Token
export GITHUB_TOKEN="ghp_your_token_here"
claude mcp add github npx --yes @modelcontextprotocol/server-github
```

### 記憶體/持久化儲存
```bash
claude mcp add memory npx --yes @modelcontextprotocol/server-memory
```

### Sequential Thinking
```bash
claude mcp add thinking npx --yes @modelcontextprotocol/server-sequential-thinking
```

---

## 搜尋工具

### GitHub 程式碼搜尋
```bash
# HTTP 版本（推薦）
claude mcp add --transport http grep https://mcp.grep.app
```

---

## 資料庫

### PostgreSQL
```bash
# 需要設定資料庫連線字串
export DATABASE_URL="postgresql://username:password@localhost:5432/database_name"
claude mcp add postgres npx --yes @henkey/postgres-mcp-server
```

---

## DevOps & 部署

### Docker
```bash
claude mcp add docker npx --yes mcp-server-docker
```

### Vercel
```bash
export VERCEL_TOKEN="your-vercel-token"
claude mcp add vercel npx --yes @sgrove/mcp-vercel
```

### Cloudflare
```bash
export CLOUDFLARE_API_TOKEN="your-token"
claude mcp add cloudflare npx --yes @cloudflare/mcp-server-cloudflare
```

---

## 專案管理

### Notion
```bash
export NOTION_TOKEN="your-notion-integration-token"
claude mcp add notion npx --yes @notionhq/notion-mcp-server
```

### Slack
```bash
export SLACK_BOT_TOKEN="xoxb-your-token"
claude mcp add slack npx --yes @modelcontextprotocol/server-slack
```

### Sentry
```bash
claude mcp add sentry npx --yes @sentry/mcp-server
```

---

## 開發輔助

### Playwright
```bash
# 選項 1: ExecuteAutomation 版本
claude mcp add playwright npx --yes @executeautomation/playwright-mcp-server

# 選項 2: 官方 Playwright MCP
claude mcp add playwright npx --yes @playwright/mcp

# 選項 3: Better Playwright MCP
claude mcp add playwright npx --yes better-playwright-mcp
```

### 瀏覽器自動化
```bash
claude mcp add browser npx --yes @agent-infra/mcp-server-browser
```

---

## 管理指令

### 基本管理
```bash
# 列出所有已安裝的 MCP
claude mcp list

# 檢查連線狀態（詳細）
claude mcp list --verbose

# 移除 MCP
claude mcp remove <名稱>

# 查看說明
claude mcp --help
```

### 故障排除
```bash
# 檢查特定 MCP 狀態
claude mcp list | grep <名稱>

# 重新安裝 MCP
claude mcp remove <名稱>
claude mcp add <名稱> <指令>

# 查看設定檔
cat ~/.claude/config.json
```

---

## 快速安裝腳本

### 基礎開發環境
```bash
#!/bin/bash
# basic-setup.sh

echo "Installing basic MCP servers..."

# 核心工具
claude mcp add filesystem npx --yes @modelcontextprotocol/server-filesystem ~/projects
claude mcp add memory npx --yes @modelcontextprotocol/server-memory

# Git
claude mcp add git npx --yes @cyanheads/git-mcp-server

# 搜尋工具
claude mcp add --transport http grep https://mcp.grep.app

# GitHub（如果有 token）
if [ -n "$GITHUB_TOKEN" ]; then
    claude mcp add github npx --yes @modelcontextprotocol/server-github
else
    echo "Skipping GitHub MCP - set GITHUB_TOKEN first"
fi

# Playwright
claude mcp add playwright npx --yes @executeautomation/playwright-mcp-server

echo "Basic setup complete!"
claude mcp list
```

### 驗證套件存在性腳本
```bash
#!/bin/bash
# verify-package.sh

# 使用前先驗證套件是否存在
verify_npm_package() {
    local package=$1
    npm view "$package" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ $package exists"
        return 0
    else
        echo "❌ $package does not exist"
        return 1
    fi
}

# 測試套件
verify_npm_package "@modelcontextprotocol/server-filesystem"
verify_npm_package "@cyanheads/git-mcp-server"
verify_npm_package "@executeautomation/playwright-mcp-server"
```

---

## 推薦組合

### 🎨 前端開發者
```bash
# 必備
claude mcp add filesystem npx --yes @modelcontextprotocol/server-filesystem ~/projects
claude mcp add git npx --yes @cyanheads/git-mcp-server
claude mcp add --transport http grep https://mcp.grep.app

# 部署
claude mcp add vercel npx --yes @sgrove/mcp-vercel

# 測試
claude mcp add playwright npx --yes @executeautomation/playwright-mcp-server
```

### 🔧 後端開發者
```bash
# 必備
claude mcp add filesystem npx --yes @modelcontextprotocol/server-filesystem ~/projects
claude mcp add git npx --yes @cyanheads/git-mcp-server
claude mcp add --transport http grep https://mcp.grep.app

# 資料庫（如果有設定）
if [ -n "$DATABASE_URL" ]; then
    claude mcp add postgres npx --yes @henkey/postgres-mcp-server
fi

# DevOps
claude mcp add docker npx --yes mcp-server-docker
```

### 🚀 全端開發者
```bash
# 基礎工具
claude mcp add filesystem npx --yes @modelcontextprotocol/server-filesystem ~/projects
claude mcp add git npx --yes @cyanheads/git-mcp-server
claude mcp add memory npx --yes @modelcontextprotocol/server-memory
claude mcp add --transport http grep https://mcp.grep.app

# GitHub
if [ -n "$GITHUB_TOKEN" ]; then
    claude mcp add github npx --yes @modelcontextprotocol/server-github
fi

# 開發輔助
claude mcp add playwright npx --yes @executeautomation/playwright-mcp-server
claude mcp add browser npx --yes @agent-infra/mcp-server-browser

# 部署
claude mcp add docker npx --yes mcp-server-docker
claude mcp add vercel npx --yes @sgrove/mcp-vercel
```

---

## 使用技巧

### 1. 測試 MCP 連線
```bash
# 測試所有 MCP
claude mcp list

# 測試特定功能
claude "用 grep 搜尋 React hooks 範例"
claude "用 filesystem 列出 ~/projects 的檔案"
```

### 2. 驗證套件存在
```bash
# 在安裝前先驗證
npm search "套件名稱"
npm view @套件名稱

# 測試執行
npx --yes @套件名稱 --version
```

### 3. 環境變數設定
```bash
# 在 ~/.bashrc 或 ~/.zshrc 加入
export GITHUB_TOKEN="your-token"
export DATABASE_URL="postgresql://..."
export VERCEL_TOKEN="..."

# 重新載入
source ~/.bashrc
```

### 4. 別名設定
```bash
# 加速常用指令
alias cc="claude"
alias cchat="claude chat"
alias ccode="claude code"
alias cmcp="claude mcp"
```

---

## 常見問題

### Q: 如何確認套件是否存在？
```bash
# 方法 1: npm search
npm search @modelcontextprotocol

# 方法 2: npm view
npm view @套件名稱

# 方法 3: 直接測試
npx --yes @套件名稱 --help
```

### Q: MCP 連線失敗怎麼辦？
```bash
# 1. 檢查網路
curl -I https://mcp.grep.app

# 2. 重新安裝
claude mcp remove <名稱>
claude mcp add <名稱> <指令>

# 3. 檢查環境變數
env | grep TOKEN
```

### Q: 如何更新 MCP？
```bash
# 移除舊版本
claude mcp remove <名稱>

# 安裝新版本
claude mcp add <名稱> npx --yes @latest-version
```

### Q: 設定檔在哪裡？
```bash
# 可能的位置
~/.claude/config.json
~/.config/claude-code/config.json
~/.claude-code/config.json

# 尋找設定檔
find ~ -name "config.json" -path "*/claude*" 2>/dev/null
```

---

## 確認可用的套件列表

### 官方套件 (@modelcontextprotocol)
- @modelcontextprotocol/server-filesystem
- @modelcontextprotocol/server-memory
- @modelcontextprotocol/server-github
- @modelcontextprotocol/server-sequential-thinking
- @modelcontextprotocol/server-slack

### 第三方套件
- @cyanheads/git-mcp-server
- @henkey/postgres-mcp-server
- @executeautomation/playwright-mcp-server
- @playwright/mcp
- better-playwright-mcp
- @notionhq/notion-mcp-server
- @sentry/mcp-server
- @cloudflare/mcp-server-cloudflare
- @sgrove/mcp-vercel
- @agent-infra/mcp-server-browser
- mcp-server-docker

---

## 更新紀錄

- 2025-01-27: 移除所有不存在的套件，保留經過驗證的可用套件
- 2025-01: 初始版本

---

## 相關資源

- [MCP 官方文件](https://modelcontextprotocol.io)
- [Claude Code 文件](https://docs.anthropic.com/en/docs/claude-code)
- [NPM Registry](https://www.npmjs.com) - 驗證套件是否存在
- [GitHub MCP Servers](https://github.com/modelcontextprotocol/servers) - 官方服務列表

---

## 授權

本文件為公開參考資料，歡迎自由使用與分享。