# Bitwarden CLI 完整使用指南

## 安裝 Bitwarden CLI

### macOS
```bash
# 使用 Homebrew
brew install bitwarden-cli

# 或下載預編譯檔案
curl -Lo bw.zip "https://vault.bitwarden.com/download/?app=cli&platform=macos"
unzip bw.zip
sudo mv bw /usr/local/bin/
```

### Linux
```bash
# 使用 npm (需先安裝 Node.js)
npm install -g @bitwarden/cli

# 或下載預編譯檔案 (以 x64 為例)
curl -Lo bw.zip "https://vault.bitwarden.com/download/?app=cli&platform=linux"
unzip bw.zip
sudo mv bw /usr/local/bin/
chmod +x /usr/local/bin/bw

# Debian/Ubuntu 可用 snap
sudo snap install bw
```

### 驗證安裝
```bash
bw --version
bw --help
```

## 初次設定與登入

### 1. 設定伺服器（如使用官方服務可跳過）
```bash
# 官方服務（預設）
bw config server https://vault.bitwarden.com

# 自建 vaultwarden
bw config server https://your-domain.com

# 查看目前設定
bw config
```

### 2. 登入帳號
```bash
# 基本登入
bw login your-email@example.com

# 或一步完成
bw login your-email@example.com --raw

# 如果有雙重認證
bw login your-email@example.com --method 0  # TOTP app
bw login your-email@example.com --method 1  # Email
```

### 3. 解鎖 vault
```bash
# 解鎖並獲取 session key
export BW_SESSION="$(bw unlock --raw)"

# 或直接輸入密碼解鎖
bw unlock
# 然後設定環境變數
export BW_SESSION="your-session-key"
```

### 4. 同步資料
```bash
bw sync
```

## 基本操作命令

### 查看項目
```bash
# 列出所有項目
bw list items

# 搜尋項目
bw list items --search "github"

# 依類型列出
bw list items --folderid null  # 未分類
bw list folders               # 列出資料夾
bw list collections          # 列出集合
```

### 獲取密碼和資訊
```bash
# 獲取密碼
bw get password "GitHub"
bw get password "service-name"

# 獲取使用者名稱
bw get username "GitHub"

# 獲取完整項目資訊
bw get item "GitHub"
bw get item "item-id"

# 獲取筆記內容 (適合存 API keys)
bw get notes "API Keys"

# 使用 jq 解析 JSON
bw get item "GitHub" | jq '.login.password'
bw get item "API Keys" | jq '.notes'
```

### 創建新項目
```bash
# 創建密碼項目
bw create item '{
  "type": 1,
  "name": "New Service",
  "login": {
    "username": "user@example.com",
    "password": "strong-password"
  },
  "notes": "Additional information"
}'

# 創建安全筆記 (適合 API keys)
bw create item '{
  "type": 2,
  "name": "API Keys",
  "secureNote": {
    "type": 0
  },
  "notes": "API_KEY=abc123\nSECRET_KEY=xyz789"
}'
```

### 生成密碼
```bash
# 生成隨機密碼
bw generate

# 指定長度
bw generate --length 32

# 包含特殊字元
bw generate --includeSymbols

# 密碼短語
bw generate --passphrase --words 4
```

## 進階使用

### 環境變數整合
```bash
# 在 .bashrc 或 .zshrc 中
export GITHUB_TOKEN=$(bw get password "GitHub API" 2>/dev/null)
export AWS_ACCESS_KEY=$(bw get notes "AWS Keys" | grep "ACCESS_KEY" | cut -d'=' -f2)

# 使用函數簡化
bw_get() {
  bw get password "$1" 2>/dev/null || echo "密碼不存在: $1"
}
```

### 與 direnv 整合
```bash
# 在專案目錄創建 .envrc
cat > .envrc << 'EOF'
# 確保 Bitwarden 已解鎖
if ! bw status | grep -q "unlocked"; then
  echo "請先解鎖 Bitwarden: bw unlock"
  return 1
fi

# 載入環境變數
export DATABASE_URL=$(bw get password "Project DB")
export API_SECRET=$(bw get notes "Project Secrets" | grep "API_SECRET" | cut -d'=' -f2)
export REDIS_URL=$(bw get password "Redis URL")
EOF

# 允許載入
direnv allow
```

### 腳本自動化
```bash
#!/bin/bash
# sync-and-get.sh - 同步並獲取密碼

# 檢查登入狀態
if ! bw status | grep -q "unlocked"; then
  echo "請先登入並解鎖 Bitwarden"
  exit 1
fi

# 同步最新資料
echo "同步 vault..."
bw sync

# 獲取所需密碼
echo "獲取密碼..."
GITHUB_TOKEN=$(bw get password "GitHub Token")
DATABASE_PASSWORD=$(bw get password "Production DB")

# 輸出到環境檔案
cat > .env.production << EOF
GITHUB_TOKEN=${GITHUB_TOKEN}
DATABASE_PASSWORD=${DATABASE_PASSWORD}
EOF

echo "密碼已更新到 .env.production"
```

## 常用場景

### 1. 開發環境設定
```bash
# 創建開發環境密碼獲取函數
dev_setup() {
  if [ -z "$BW_SESSION" ]; then
    export BW_SESSION="$(bw unlock --raw)"
  fi
  
  export DB_PASSWORD=$(bw get password "Dev Database")
  export API_KEY=$(bw get notes "Dev API Keys" | grep "MAIN_API" | cut -d'=' -f2)
  export JWT_SECRET=$(bw get password "JWT Secret")
  
  echo "開發環境變數已設定完成"
}
```

### 2. 部署腳本整合
```bash
# deploy.sh
#!/bin/bash
set -e

echo "獲取部署所需的機密資訊..."
SERVER_PASSWORD=$(bw get password "Production Server")
DATABASE_URL=$(bw get password "Production Database URL")
API_SECRET=$(bw get notes "Production Secrets" | grep "API_SECRET" | cut -d'=' -f2)

# 使用 sshpass 自動化部署
sshpass -p "$SERVER_PASSWORD" scp .env.production user@server:/app/
sshpass -p "$SERVER_PASSWORD" ssh user@server "cd /app && docker-compose up -d"
```

### 3. 多環境管理
```bash
# 根據環境獲取不同的密碼
get_env_password() {
  local env=$1
  local service=$2
  
  case $env in
    "dev")
      bw get password "Dev $service"
      ;;
    "staging")
      bw get password "Staging $service"
      ;;
    "prod")
      bw get password "Production $service"
      ;;
    *)
      echo "未知環境: $env"
      exit 1
      ;;
  esac
}

# 使用範例
DATABASE_PASSWORD=$(get_env_password "prod" "Database")
```

## 安全最佳實踐

### 1. Session 管理
```bash
# 設定 session 超時
export BW_SESSION_TIMEOUT=3600  # 1小時後自動鎖定

# 完成工作後鎖定
bw_lock() {
  bw lock
  unset BW_SESSION
  echo "Bitwarden 已鎖定"
}

# 在 shell 退出時自動鎖定
trap bw_lock EXIT
```

### 2. 權限控制
```bash
# 確保設定檔案權限正確
chmod 600 ~/.config/Bitwarden\ CLI/
chmod 600 ~/.bashrc ~/.zshrc

# 避免在 shell history 中留下密碼
set +o history  # 暫停記錄 history
export SENSITIVE_VAR=$(bw get password "service")
set -o history   # 恢復記錄 history
```

### 3. 錯誤處理
```bash
# 安全的密碼獲取函數
safe_get_password() {
  local service_name="$1"
  local password
  
  # 檢查是否已解鎖
  if ! bw status | grep -q "unlocked"; then
    echo "Error: Bitwarden vault is locked" >&2
    return 1
  fi
  
  # 獲取密碼，避免顯示錯誤到 stdout
  password=$(bw get password "$service_name" 2>/dev/null)
  
  if [ -z "$password" ]; then
    echo "Error: Password not found for '$service_name'" >&2
    return 1
  fi
  
  echo "$password"
}
```

## 故障排除

### 常見問題
```bash
# 1. 忘記解鎖
if bw status | grep -q "locked"; then
  export BW_SESSION="$(bw unlock --raw)"
fi

# 2. 同步問題
bw sync --force

# 3. 查看詳細錯誤
bw --verbose get password "service-name"

# 4. 重新登入
bw logout
bw login your-email@example.com

# 5. 清除本地快取
rm -rf ~/.config/Bitwarden\ CLI/
```

### 狀態檢查
```bash
# 檢查登入狀態
bw status

# 檢查伺服器設定
bw config

# 測試連線
bw sync --check
```

## 實用別名和函數

```bash
# 在 .bashrc 或 .zshrc 中加入
alias bwu='export BW_SESSION="$(bw unlock --raw)"'
alias bws='bw sync'
alias bwl='bw lock && unset BW_SESSION'

# 快速獲取密碼
bwp() {
  bw get password "$1" 2>/dev/null | pbcopy  # macOS
  # bw get password "$1" 2>/dev/null | xclip -selection clipboard  # Linux
  echo "密碼已複製到剪貼簿"
}

# 快速搜尋
bwf() {
  bw list items --search "$1" | jq -r '.[].name'
}

# 安全筆記獲取
bwn() {
  bw get notes "$1" 2>/dev/null
}
```