# Claude Code MCP 指令大全

## 📖 目錄
- [基本語法](#基本語法)
- [核心開發工具](#核心開發工具)
- [搜尋工具](#搜尋工具)
- [資料庫](#資料庫)
- [DevOps & 部署](#devops--部署)
- [雲端服務](#雲端服務)
- [專案管理](#專案管理)
- [開發輔助](#開發輔助)
- [特殊用途](#特殊用途)
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
claude mcp add git npx -y @modelcontextprotocol/server-git
claude mcp add --transport http grep https://mcp.grep.app
```

---

## 核心開發工具

### 檔案系統操作
```bash
# 必須指定允許存取的目錄
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem ~/projects

# 多個目錄
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem ~/projects ~/documents
```

### Git 版本控制
```bash
claude mcp add git npx -y @modelcontextprotocol/server-git
```

### GitHub API
```bash
# 需要先設定 GitHub Personal Access Token
export GITHUB_TOKEN="ghp_your_token_here"
claude mcp add github npx -y @modelcontextprotocol/server-github
```

### 網頁內容擷取
```bash
claude mcp add fetch npx -y @modelcontextprotocol/server-fetch
```

### 記憶體/持久化儲存
```bash
claude mcp add memory npx -y @modelcontextprotocol/server-memory
```

### Shell 指令執行
```bash
claude mcp add shell npx -y @fridayai/mcp-shell
```

---

## 搜尋工具

### GitHub 程式碼搜尋
```bash
# HTTP 版本（推薦）
claude mcp add --transport http grep https://mcp.grep.app

# stdio 版本
npm install -g @ai-tools-all/grep_app_mcp
claude mcp add grep_stdio grep_app_mcp
```

### Google 搜尋
```bash
claude mcp add google npx -y @kevincobain2000/mcp-google-search
```

### Stack Overflow
```bash
claude mcp add stackoverflow npx -y @bilalmirza/mcp-stackoverflow
```

### npm 套件搜尋
```bash
claude mcp add npm-tools npx -y @fridayai/mcp-npm-tools
```

### GitHub 專門搜尋
```bash
# 需要 GitHub Token
export GITHUB_TOKEN="your-token"
claude mcp add github-search npx -y @kevincobain2000/mcp-github-search
```

---

## 資料庫

### PostgreSQL
```bash
# 需要設定資料庫連線字串
export DATABASE_URL="postgresql://username:password@localhost:5432/database_name"
claude mcp add postgres npx -y @modelcontextprotocol/server-postgres
```

### SQLite
```bash
# 指定資料庫檔案路徑
claude mcp add sqlite npx -y @modelcontextprotocol/server-sqlite ~/mydatabase.db
```

### MySQL
```bash
export MYSQL_URL="mysql://user:password@localhost:3306/database"
claude mcp add mysql npx -y @kevincobain2000/mcp-mysql
```

### MongoDB
```bash
export MONGODB_URI="mongodb://localhost:27017/mydb"
claude mcp add mongodb npx -y @kevincobain2000/mcp-mongodb
```

### Redis
```bash
export REDIS_URL="redis://localhost:6379"
claude mcp add redis npx -y @kevincobain2000/mcp-redis
```

---

## DevOps & 部署

### Docker
```bash
claude mcp add docker npx -y @joshuamlee2020/mcp-docker
```

### Kubernetes
```bash
# 需要 kubectl 設定
claude mcp add kubernetes npx -y @mbusigin/mcp-kubernetes
```

### Terraform
```bash
claude mcp add terraform npx -y terraform-mcp-server
```

### Vercel
```bash
# 需要 Vercel Token
export VERCEL_TOKEN="your-vercel-token"
claude mcp add vercel npx -y @sgrove/mcp-vercel
```

### Netlify
```bash
export NETLIFY_TOKEN="your-netlify-token"
claude mcp add netlify npx -y @kevincobain2000/mcp-netlify
```

### Cloudflare
```bash
export CLOUDFLARE_API_TOKEN="your-token"
claude mcp add cloudflare npx -y @cloudflare/mcp-server-cloudflare
```

### Heroku
```bash
export HEROKU_API_KEY="your-api-key"
claude mcp add heroku npx -y @kevincobain2000/mcp-heroku
```

---

## 雲端服務

### AWS
```bash
# 需要 AWS 認證設定
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
claude mcp add aws npx -y @kevincobain2000/mcp-aws
```

### Google Cloud Platform
```bash
# 需要 GCP 認證
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
claude mcp add gcp npx -y @kevincobain2000/mcp-gcp
```

### Azure
```bash
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
claude mcp add azure npx -y @kevincobain2000/mcp-azure
```

### Supabase
```bash
export SUPABASE_URL="your-project-url"
export SUPABASE_KEY="your-anon-key"
claude mcp add supabase npx -y @kevincobain2000/mcp-supabase
```

### Firebase
```bash
export FIREBASE_PROJECT_ID="your-project-id"
claude mcp add firebase npx -y @kevincobain2000/mcp-firebase
```

---

## 專案管理

### Jira
```bash
export JIRA_HOST="yourcompany.atlassian.net"
export JIRA_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your-api-token"
claude mcp add jira npx -y @kevincobain2000/mcp-jira
```

### Linear
```bash
export LINEAR_API_KEY="your-linear-api-key"
claude mcp add linear npx -y linear-mcp
```

### Notion
```bash
export NOTION_TOKEN="your-notion-integration-token"
claude mcp add notion npx -y @kevincobain2000/mcp-notion
```

### Slack
```bash
export SLACK_BOT_TOKEN="xoxb-your-token"
claude mcp add slack npx -y @modelcontextprotocol/server-slack
```

### Discord
```bash
export DISCORD_TOKEN="your-bot-token"
claude mcp add discord npx -y @kevincobain2000/mcp-discord
```

### Asana
```bash
export ASANA_TOKEN="your-personal-access-token"
claude mcp add asana npx -y @kevincobain2000/mcp-asana
```

---

## 開發輔助

### 程式碼格式化
```bash
# Prettier
claude mcp add prettier npx -y @kevincobain2000/mcp-prettier

# ESLint
claude mcp add eslint npx -y @kevincobain2000/mcp-eslint

# Black (Python)
claude mcp add black npx -y @kevincobain2000/mcp-black
```

### 程式語言工具
```bash
# Python
claude mcp add python npx -y @kevincobain2000/mcp-python

# Node.js
claude mcp add nodejs npx -y @kevincobain2000/mcp-nodejs

# TypeScript
claude mcp add typescript npx -y @kevincobain2000/mcp-typescript

# Rust
claude mcp add rust npx -y @kevincobain2000/mcp-rust

# Go
claude mcp add golang npx -y @kevincobain2000/mcp-golang
```

### 測試工具
```bash
# Playwright
claude mcp add playwright npx -y @executeautomation/playwright-mcp-server

# Jest
claude mcp add jest npx -y @kevincobain2000/mcp-jest

# Cypress
claude mcp add cypress npx -y @kevincobain2000/mcp-cypress
```

---

## 特殊用途

### 瀏覽器自動化
```bash
claude mcp add browser npx -y @modelcontextprotocol/server-browser
```

### 文件處理
```bash
# PDF
claude mcp add pdf npx -y @kevincobain2000/mcp-pdf

# Excel
claude mcp add excel npx -y @kevincobain2000/mcp-excel

# Word
claude mcp add word npx -y @kevincobain2000/mcp-word
```

### 多媒體處理
```bash
# 圖片處理
claude mcp add image npx -y @kevincobain2000/mcp-image

# 影片處理
claude mcp add video npx -y @kevincobain2000/mcp-video

# 音訊處理
claude mcp add audio npx -y @kevincobain2000/mcp-audio
```

### 通訊工具
```bash
# Email
claude mcp add email npx -y @kevincobain2000/mcp-email

# SMS
claude mcp add sms npx -y @kevincobain2000/mcp-sms

# WhatsApp
claude mcp add whatsapp npx -y @kevincobain2000/mcp-whatsapp
```

### 其他工具
```bash
# Calendar
claude mcp add calendar npx -y @kevincobain2000/mcp-calendar

# Weather
claude mcp add weather npx -y @kevincobain2000/mcp-weather

# Translation
claude mcp add translate npx -y @kevincobain2000/mcp-translate
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
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem ~/projects
claude mcp add git npx -y @modelcontextprotocol/server-git
claude mcp add fetch npx -y @modelcontextprotocol/server-fetch
claude mcp add memory npx -y @modelcontextprotocol/server-memory
claude mcp add shell npx -y @fridayai/mcp-shell

# 搜尋工具
claude mcp add --transport http grep https://mcp.grep.app

echo "Basic setup complete!"
claude mcp list
```

### 完整開發環境
```bash
#!/bin/bash
# full-setup.sh

echo "Installing all MCP servers..."

# 基礎工具
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem ~/projects
claude mcp add git npx -y @modelcontextprotocol/server-git
claude mcp add fetch npx -y @modelcontextprotocol/server-fetch
claude mcp add memory npx -y @modelcontextprotocol/server-memory
claude mcp add shell npx -y @fridayai/mcp-shell

# 搜尋
claude mcp add --transport http grep https://mcp.grep.app
claude mcp add npm-tools npx -y @fridayai/mcp-npm-tools

# 開發輔助
claude mcp add prettier npx -y @kevincobain2000/mcp-prettier
claude mcp add eslint npx -y @kevincobain2000/mcp-eslint

# GitHub (如果有 token)
if [ -n "$GITHUB_TOKEN" ]; then
    claude mcp add github npx -y @modelcontextprotocol/server-github
else
    echo "Skipping GitHub MCP - set GITHUB_TOKEN first"
fi

# 資料庫 (如果有設定)
if [ -n "$DATABASE_URL" ]; then
    claude mcp add postgres npx -y @modelcontextprotocol/server-postgres
else
    echo "Skipping PostgreSQL MCP - set DATABASE_URL first"
fi

# Docker
claude mcp add docker npx -y @joshuamlee2020/mcp-docker

echo "Full setup complete!"
claude mcp list
```

### 系統程式開發環境
```bash
#!/bin/bash
# system-dev-setup.sh

echo "Installing System Programming MCP servers..."

# 核心工具
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem ~/projects ~/kernel ~/src
claude mcp add git npx -y @modelcontextprotocol/server-git
claude mcp add shell npx -y @fridayai/mcp-shell

# 搜尋工具
claude mcp add --transport http grep https://mcp.grep.app
claude mcp add ripgrep npx -y @modelcontextprotocol/server-ripgrep
claude mcp add ast-grep npx -y @ast-grep/mcp-server

# 編譯工具
claude mcp add make npx -y @kevincobain2000/mcp-make
claude mcp add cmake npx -y @kevincobain2000/mcp-cmake
claude mcp add gcc npx -y @kevincobain2000/mcp-gcc
claude mcp add clang npx -y @kevincobain2000/mcp-clang

# 除錯工具
claude mcp add gdb npx -y @kevincobain2000/mcp-gdb
claude mcp add valgrind npx -y @kevincobain2000/mcp-valgrind
claude mcp add perf npx -y @kevincobain2000/mcp-perf

# 系統分析
claude mcp add strace npx -y @kevincobain2000/mcp-strace
claude mcp add ltrace npx -y @kevincobain2000/mcp-ltrace
claude mcp add objdump npx -y @kevincobain2000/mcp-objdump

# 文件
claude mcp add man npx -y @kevincobain2000/mcp-man

echo "System programming setup complete!"
claude mcp list
```

### Rust 開發環境
```bash
#!/bin/bash
# rust-setup.sh

echo "Installing Rust development MCP servers..."

# 基礎工具
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem ~/rust-projects
claude mcp add git npx -y @modelcontextprotocol/server-git
claude mcp add shell npx -y @fridayai/mcp-shell

# Rust 專用
claude mcp add cargo npx -y @kevincobain2000/mcp-cargo
claude mcp add rust-analyzer npx -y @kevincobain2000/mcp-rust-analyzer
claude mcp add clippy npx -y @kevincobain2000/mcp-clippy
claude mcp add rustfmt npx -y @kevincobain2000/mcp-rustfmt
claude mcp add crates npx -y @kevincobain2000/mcp-crates

# 搜尋
claude mcp add --transport http grep https://mcp.grep.app
claude mcp add ripgrep npx -y @modelcontextprotocol/server-ripgrep

# 除錯
claude mcp add gdb npx -y @kevincobain2000/mcp-gdb
claude mcp add lldb npx -y @kevincobain2000/mcp-lldb

echo "Rust development setup complete!"
claude mcp list
```

### Linux Kernel 開發環境
```bash
#!/bin/bash
# kernel-setup.sh

echo "Installing Linux Kernel development MCP servers..."

# 基礎工具
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem ~/kernel ~/linux-stable
claude mcp add git npx -y @modelcontextprotocol/server-git
claude mcp add shell npx -y @fridayai/mcp-shell

# Kernel 建構
claude mcp add kbuild npx -y @kevincobain2000/mcp-kbuild
claude mcp add kconfig npx -y @kevincobain2000/mcp-kconfig
claude mcp add make npx -y @kevincobain2000/mcp-make

# Device Tree
claude mcp add dtc npx -y @kevincobain2000/mcp-dtc

# 除錯與測試
claude mcp add qemu npx -y @kevincobain2000/mcp-qemu
claude mcp add gdb npx -y @kevincobain2000/mcp-gdb

# 系統追蹤
claude mcp add strace npx -y @kevincobain2000/mcp-strace
claude mcp add perf npx -y @kevincobain2000/mcp-perf

# 文件
claude mcp add kernel-doc npx -y @kevincobain2000/mcp-kernel-doc
claude mcp add man npx -y @kevincobain2000/mcp-man

echo "Kernel development setup complete!"
claude mcp list
```

---

## 推薦組合

### 🎨 前端開發者
```bash
# 必備
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem ~/projects
claude mcp add git npx -y @modelcontextprotocol/server-git
claude mcp add --transport http grep https://mcp.grep.app
claude mcp add npm-tools npx -y @fridayai/mcp-npm-tools

# 格式化與檢查
claude mcp add prettier npx -y @kevincobain2000/mcp-prettier
claude mcp add eslint npx -y @kevincobain2000/mcp-eslint

# 部署
claude mcp add vercel npx -y @sgrove/mcp-vercel
claude mcp add netlify npx -y @kevincobain2000/mcp-netlify

# 測試
claude mcp add playwright npx -y @executeautomation/playwright-mcp-server
```

### 🔧 後端開發者
```bash
# 必備
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem ~/projects
claude mcp add git npx -y @modelcontextprotocol/server-git
claude mcp add --transport http grep https://mcp.grep.app

# 資料庫
claude mcp add postgres npx -y @modelcontextprotocol/server-postgres
claude mcp add redis npx -y @kevincobain2000/mcp-redis

# DevOps
claude mcp add docker npx -y @joshuamlee2020/mcp-docker
claude mcp add kubernetes npx -y @mbusigin/mcp-kubernetes

# 雲端
claude mcp add aws npx -y @kevincobain2000/mcp-aws
```

### 🚀 全端開發者
```bash
# 使用完整安裝腳本 (full-setup.sh)
# 包含前端 + 後端所有工具
```

### 📱 Mobile 開發者
```bash
# 基礎
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem ~/projects
claude mcp add git npx -y @modelcontextprotocol/server-git

# React Native
claude mcp add react-native npx -y @kevincobain2000/mcp-react-native

# Firebase
claude mcp add firebase npx -y @kevincobain2000/mcp-firebase

# 測試
claude mcp add jest npx -y @kevincobain2000/mcp-jest
```

### 🤖 DevOps 工程師
```bash
# 基礎
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem ~/projects
claude mcp add git npx -y @modelcontextprotocol/server-git
claude mcp add shell npx -y @fridayai/mcp-shell

# 容器與編排
claude mcp add docker npx -y @joshuamlee2020/mcp-docker
claude mcp add kubernetes npx -y @mbusigin/mcp-kubernetes

# IaC
claude mcp add terraform npx -y terraform-mcp-server

# 雲端平台
claude mcp add aws npx -y @kevincobain2000/mcp-aws
claude mcp add gcp npx -y @kevincobain2000/mcp-gcp
claude mcp add azure npx -y @kevincobain2000/mcp-azure

# 監控
claude mcp add prometheus npx -y @kevincobain2000/mcp-prometheus
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

### 2. 環境變數設定
```bash
# 在 ~/.bashrc 或 ~/.zshrc 加入
export GITHUB_TOKEN="your-token"
export DATABASE_URL="postgresql://..."
export VERCEL_TOKEN="..."

# 重新載入
source ~/.bashrc
```

### 3. 別名設定
```bash
# 加速常用指令
alias cc="claude"
alias cchat="claude chat"
alias ccode="claude code"
alias cmcp="claude mcp"
```

### 4. 批次操作
```bash
# 移除所有 MCP
claude mcp list | grep -v "Checking" | awk '{print $1}' | sed 's/://' | xargs -I {} claude mcp remove {}

# 重新安裝所有 MCP
./full-setup.sh
```

---

## 常見問題

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
claude mcp add <名稱> npx -y @latest-version
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

## 更新紀錄

- 2025-01: 初始版本
- 最後更新: 2025-01-27

---

## 相關資源

- [MCP 官方文件](https://modelcontextprotocol.io)
- [Claude Code 文件](https://docs.anthropic.com/en/docs/claude-code)
- [MCP Server 列表](https://github.com/modelcontextprotocol/servers)
- [Anthropic 官網](https://www.anthropic.com)

---

## 授權

本文件為公開參考資料，歡迎自由使用與分享。