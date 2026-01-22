# 工程師必備 MCP 完整指南 2026

## 📋 目錄
1. [快速開始](#快速開始)
2. [MCP 配置文件備份與恢復](#mcp-配置文件備份與恢復)
3. [必備 MCP 伺服器完整清單](#必備-mcp-伺服器完整清單)
4. [安裝命令速查表](#安裝命令速查表)
5. [快速安裝腳本](#快速安裝腳本)
6. [量身定制組合](#量身定制組合-for-quant-trader--developer)
7. [MCP 發現與更新](#mcp-發現與更新)
8. [故障排除](#故障排除)

---

## 快速開始

### 檢查 MCP 配置文件位置

**基本信息：**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Claude Code 配置：**
- `~/.claude.json` 或 `/home/user/.claude.json`

### 快速查看已安裝的 MCP
```bash
# 列出所有 MCP 伺服器
claude mcp list

# 驗證特定 MCP
claude mcp verify <mcp-name>
```

---

## MCP 配置文件備份與恢復

### 備份策略

#### 方案 1：Git 版本控制（推薦）
```bash
# 初始化 Git 倉庫
cd ~/mcp-config-backup
git init

# 複製配置文件
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json ./claude_desktop_config.json

# 提交
git add .
git commit -m "Initial MCP config backup"
git remote add origin https://github.com/your-user/mcp-config-backup.git
git push -u origin main
```

#### 方案 2：自動備份腳本

**macOS/Linux (`backup-mcp.sh`)：**
```bash
#!/bin/bash

BACKUP_DIR="$HOME/mcp-backups"
CONFIG_FILE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
cp "$CONFIG_FILE" "$BACKUP_DIR/claude_desktop_config_${TIMESTAMP}.json"

echo "✅ Backup created: $BACKUP_DIR/claude_desktop_config_${TIMESTAMP}.json"

# 自動清理 30 天前的備份
find "$BACKUP_DIR" -name "*.json" -mtime +30 -delete
```

**Windows PowerShell (`Backup-MCP.ps1`)：**
```powershell
$BackupDir = "$env:USERPROFILE\mcp-backups"
$ConfigFile = "$env:APPDATA\Claude\claude_desktop_config.json"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
Copy-Item $ConfigFile -Destination "$BackupDir\claude_desktop_config_${Timestamp}.json"

Write-Host "✅ Backup created: $BackupDir\claude_desktop_config_${Timestamp}.json"

# 自動清理 30 天前的備份
Get-ChildItem $BackupDir -Filter "*.json" -File | 
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | 
  Remove-Item
```

### 恢復配置

```bash
# 恢復特定備份
cp ~/mcp-backups/claude_desktop_config_20260122_112000.json \
   ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 重啟 Claude Desktop
# ⚠️ 重要：重啟後所有 MCP 伺服器會自動恢復
```

---

## 必備 MCP 伺服器完整清單

### 第 1 層：絕對必備（All Engineers）

| MCP 伺服器 | 用途 | 功能 |
|-----------|------|------|
| **GitHub MCP** | 版本控制 | PR、Issues、分支、倉庫管理、自動化 |
| **Filesystem MCP** | 文件管理 | 讀取和操作本地項目結構 |
| **Sequential Thinking** | 複雜問題解決 | 架構設計、演算法分解、深度分析 |

### 第 2 層：框架/技術棧特定

#### 前端開發者必備：
| MCP 伺服器 | 功能 | 重要性 |
|-----------|------|--------|
| **Context7** | 實時框架文檔（React、Next.js、Vue） | ⭐⭐⭐⭐⭐ 最重要 |
| **Playwright MCP** | E2E 測試自動化 | ⭐⭐⭐⭐ |

#### 後端開發者必備：
| MCP 伺服器 | 功能 |
|-----------|------|
| **PostgreSQL** | 數據庫查詢、遷移、schema |
| **Docker MCP** | 容器構建、運行、調試 |
| **Supabase** | Serverless Postgres、實時、邊界函數 |

#### 全棧開發者推薦組合：
```bash
github + context7 + filesystem + postgres + docker
```

### 第 3 層：基礎設施 & DevOps

| MCP 伺服器 | 功能 |
|-----------|------|
| **Vercel MCP** | 部署管理、CI/CD、preview URLs |
| **Kubernetes MCP** | Pod、部署、服務 |
| **Cloudflare MCP** | Workers、DNS、安全規則 |
| **AWS MCP** | EC2、S3、IAM、日誌 |
| **Azure MCP** | 40+ Azure 服務 |

### 第 4 層：知識 & 協作

| MCP 伺服器 | 功能 |
|-----------|------|
| **Notion MCP** | 文檔、任務、知識庫 |
| **Google Drive MCP** | 搜索、讀取、整理文件 |
| **Slack MCP** | 發送消息、讀取頻道 |

### 第 5 層：搜索 & 數據

| MCP 伺服器 | 功能 |
|-----------|------|
| **Tavily MCP** | 實時網路搜索、內容提取 |
| **Brave Search MCP** | 隱私搜索、代碼上下文 |
| **Vectara MCP** | RAG、語義搜索、向量數據庫 |

---

## 安裝命令速查表

### 核心必備
```bash
# GitHub 整合
claude mcp add github -- npx -y @github/github-mcp-server

# 文件系統
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem

# 最新文檔（Context7）
claude mcp add context7 -- npx -y @context7/mcp
```

### 後端開發
```bash
# PostgreSQL
claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres --dsn postgresql://user:password@localhost:5432/dbname

# Docker
claude mcp add docker -- npx -y @modelcontextprotocol/server-docker

# Supabase
claude mcp add supabase -- npx -y @supabase/mcp-server
```

### 前端開發
```bash
# Playwright E2E 測試
claude mcp add playwright -- npx -y @modelcontextprotocol/server-playwright
```

### 部署與基礎設施
```bash
# Vercel
claude mcp add vercel -- npx -y @vercel/mcp

# Cloudflare
claude mcp add cloudflare -- npx -y

# AWS
claude mcp add aws -- npx -y

# Kubernetes
claude mcp add kubernetes -- npx -y
```

### 知識與協作
```bash
# Notion
claude mcp add notion -- npx -y @modelcontextprotocol/server-notion

# Google Drive
claude mcp add google-drive -- npx -y

# Slack
claude mcp add slack -- npx -y
```

### 搜索
```bash
# Tavily
claude mcp add tavily -- npx -y

# Brave Search
claude mcp add brave-search -- npx -y

# Vectara
claude mcp add vectara -- npx -y
```

---

## 快速安裝腳本

### macOS/Linux (`install-mcp-essential.sh`)

```bash
#!/bin/bash
set -e

echo "🚀 Installing Essential MCPs for Engineers..."

# 核心必備
echo "📦 Installing Core MCPs..."
claude mcp add github -- npx -y @github/github-mcp-server
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem
claude mcp add context7 -- npx -y @context7/mcp

# 後端開發
echo "📦 Installing Backend MCPs..."
claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres
claude mcp add docker -- npx -y @modelcontextprotocol/server-docker

# 部署
echo "📦 Installing Deployment MCPs..."
claude mcp add vercel -- npx -y @vercel/mcp
claude mcp add cloudflare -- npx -y

# 搜索
echo "📦 Installing Search MCPs..."
claude mcp add tavily -- npx -y

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Installed MCPs:"
claude mcp list

echo ""
echo "💡 Tips:"
echo "- Restart Claude Desktop to activate MCPs"
echo "- Use 'claude mcp list' to verify installation"
echo "- Read docs at https://modelcontextprotocol.io"
```

### Windows PowerShell (`Install-MCP-Essential.ps1`)

```powershell
Write-Host "🚀 Installing Essential MCPs for Engineers..." -ForegroundColor Green

# 核心必備
Write-Host "📦 Installing Core MCPs..." -ForegroundColor Cyan
claude mcp add github -- npx -y @github/github-mcp-server
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem
claude mcp add context7 -- npx -y @context7/mcp

# 後端開發
Write-Host "📦 Installing Backend MCPs..." -ForegroundColor Cyan
claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres
claude mcp add docker -- npx -y @modelcontextprotocol/server-docker

# 部署
Write-Host "📦 Installing Deployment MCPs..." -ForegroundColor Cyan
claude mcp add vercel -- npx -y @vercel/mcp
claude mcp add cloudflare -- npx -y

# 搜索
Write-Host "📦 Installing Search MCPs..." -ForegroundColor Cyan
claude mcp add tavily -- npx -y

Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Installed MCPs:" -ForegroundColor Cyan
claude mcp list

Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "- Restart Claude Desktop to activate MCPs"
Write-Host "- Use 'claude mcp list' to verify installation"
Write-Host "- Read docs at https://modelcontextprotocol.io"
```

### 使用腳本

**macOS/Linux：**
```bash
chmod +x install-mcp-essential.sh
./install-mcp-essential.sh
```

**Windows PowerShell：**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\Install-MCP-Essential.ps1
```

---

## 量身定制組合 (For Quant Trader + Developer)

### Tier 1：必裝（5 個）
```bash
# 版本控制 & 代碼
claude mcp add github -- npx -y @github/github-mcp-server
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem

# 數據 & 分析
claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres
claude mcp add context7 -- npx -y @context7/mcp

# 容器化
claude mcp add docker -- npx -y @modelcontextprotocol/server-docker
```

### Tier 2：強烈推薦（加 3 個）
```bash
# 部署 & 基礎設施
claude mcp add vercel -- npx -y @vercel/mcp
claude mcp add cloudflare -- npx -y

# 搜索（用於交易數據、市場分析、技術研究）
claude mcp add tavily -- npx -y
```

### Tier 3：可選（根據需要）
```bash
# 前端自動化測試
claude mcp add playwright -- npx -y @modelcontextprotocol/server-playwright

# 雲端存儲
claude mcp add google-drive -- npx -y

# 知識管理
claude mcp add notion -- npx -y @modelcontextprotocol/server-notion

# 通知 & 協作
claude mcp add slack -- npx -y
```

### 推薦配置（`~/.claude.json` 示例）

```json
{
  "servers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@github/github-mcp-server"],
      "env": {
        "GITHUB_TOKEN": "your-github-token"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://user:password@localhost:5432/dbname"
      }
    },
    "docker": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-docker"]
    },
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp"],
      "env": {
        "TAVILY_API_KEY": "your-api-key"
      }
    }
  }
}
```

---

## MCP 發現與更新

### 官方 MCP 註冊表

| 平台 | 網址 | 特色 |
|------|------|------|
| **MCP.so** | https://mcp.so | 3000+ 伺服器，有評分 |
| **Smithery** | https://smithery.ai | 2200+ 伺服器，自動安裝 |
| **MCPMarket** | https://mcpmarket.com | GitHub stars 排名 |
| **ClaudeMCP.com** | https://claudemcp.com | 精選推薦 |
| **GitHub Awesome MCP** | https://github.com/topics/mcp | 開源 MCP 集合 |

### 定期更新

```bash
# 檢查 MCP 更新
npm outdated -g

# 更新特定 MCP
npm install -g @github/github-mcp-server@latest

# 更新所有 global 包
npm update -g
```

### 追蹤新 MCP

```bash
# 關注 GitHub 主題
curl -s https://api.github.com/search/repositories?q=topic:mcp+language:typescript&sort=stars | jq

# RSS 訂閱
# 訂閱 https://github.com/topics/mcp.atom
```

---

## 故障排除

### MCP 無法啟動

**問題：** `Error: Failed to start MCP server`

**解決方案：**
```bash
# 1. 驗證安裝
claude mcp list

# 2. 檢查依賴
npm ls -g @github/github-mcp-server

# 3. 重新安裝
npm uninstall -g @github/github-mcp-server
claude mcp add github -- npx -y @github/github-mcp-server

# 4. 檢查配置文件語法
cat ~/.claude.json | jq .
```

### 配置文件損毀

**問題：** Claude 無法讀取配置

**解決方案：**
```bash
# 1. 備份損毀文件
cp ~/.claude.json ~/.claude.json.backup

# 2. 從備份恢復
cp ~/mcp-backups/claude_desktop_config_XXXXXXX.json ~/.claude.json

# 3. 驗證
cat ~/.claude.json | jq .

# 4. 重啟 Claude Desktop
```

### 權限問題

**問題：** `Permission denied` 錯誤

**解決方案：**
```bash
# macOS/Linux
chmod 644 ~/.claude.json
chmod 755 ~/.config/Claude

# 驗證
ls -la ~/.claude.json
```

### 依賴衝突

**問題：** NPM 版本衝突

**解決方案：**
```bash
# 清除 npm 快取
npm cache clean --force

# 重新安裝 MCP
claude mcp add github -- npx -y @github/github-mcp-server

# 檢查版本
npm ls -g | grep mcp
```

---

## 進階技巧

### 建立 MCP 快速啟用菜單

**macOS：**
```bash
# 建立 shell 函數（加到 .zshrc 或 .bash_profile）
function mcp-toggle() {
  case $1 in
    all)
      echo "Enabling all MCPs..."
      # 啟用所有 MCP
      ;;
    essential)
      echo "Enabling essential MCPs only..."
      # 啟用必備 MCP
      ;;
    *)
      echo "Usage: mcp-toggle [all|essential]"
      ;;
  esac
}
```

### MCP 性能優化

```bash
# 只加載常用 MCP，減少啟動時間
# 在 ~/.claude.json 中用 "enabled": false 禁用臨時 MCP

# 例如：
{
  "servers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@github/github-mcp-server"],
      "enabled": true
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-playwright"],
      "enabled": false
    }
  }
}
```

### MCP 日誌調試

```bash
# 啟用詳細日誌
export DEBUG=mcp:*
claude mcp list

# 查看日誌
tail -f ~/.claude_logs.txt
```

---

## 參考資源

### 官方文檔
- **MCP 主頁：** https://modelcontextprotocol.io
- **Claude Code 文檔：** https://code.claude.com/docs/en/mcp
- **GitHub MCP 伺服器：** https://github.com/github/github-mcp-server

### 社區資源
- **GitHub Discussions：** https://github.com/orgs/modelcontextprotocol/discussions
- **Reddit r/ClaudeCode：** https://reddit.com/r/ClaudeCode
- **Reddit r/ClaudeAI：** https://reddit.com/r/ClaudeAI

### 相關項目
- **Context7：** https://github.com/upstash/context7
- **MCP Config Manager：** https://github.com/holstein13/mcp-config-manager
- **MCP Backup Server：** https://github.com/hexitex/MCP-Backup-Server

---

## 更新日誌

### 版本 1.0（2026-01-22）
- ✅ 初始版本發佈
- ✅ 完整的 MCP 清單
- ✅ 安裝腳本與備份指南
- ✅ 量身定制組合（Quant Trader + Developer）
- ✅ 故障排除指南

---

## 快速檢查清單

### 初次安裝
- [ ] 備份現有配置：`cp ~/Library/Application\ Support/Claude/claude_desktop_config.json ~/mcp-backups/`
- [ ] 執行安裝腳本或逐個執行命令
- [ ] 重啟 Claude Desktop
- [ ] 驗證：`claude mcp list`

### 定期維護
- [ ] 每週檢查 MCP 更新：`npm outdated -g`
- [ ] 每月自動備份配置
- [ ] 定期清理未使用的 MCP
- [ ] 追蹤新推出的 MCP

### 備份策略
- [ ] 設置 Git 自動備份（推薦）
- [ ] 定期手動備份到雲端
- [ ] 保留至少 3 個月的備份

---

**最後更新：2026-01-22**

祝你使用愉快！如有問題，歡迎提交 Issue 或查閱官方文檔。
