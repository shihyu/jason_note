# DuckDNS + Let's Encrypt 一鍵安裝指南

## 📖 簡介

這個指南提供一個完整的自動化腳本，幫你快速設定：
- **DuckDNS** 免費動態 DNS 服務
- **Let's Encrypt** 免費 SSL 憑證
- **Nginx** 網頁伺服器配置
- **自動化更新** IP 和 SSL 憑證

完成後你將擁有一個完全免費、安全的 HTTPS 網站！

---

## 🚀 功能特色

### ✅ 自動化安裝
- 一鍵安裝所有必要套件
- 自動配置所有服務
- 智能錯誤檢測和處理

### ✅ DuckDNS 設定
- 自動創建更新腳本
- 每 5 分鐘自動更新 IP
- 詳細的運行日誌

### ✅ SSL 憑證管理
- 自動申請 Let's Encrypt 憑證
- 90 天到期前自動更新
- 完整的 HTTPS 重定向

### ✅ Nginx 配置
- 最佳化的安全設定
- 美觀的預設首頁
- 準備好的反向代理配置

---

## 📋 前置準備

### 1. DuckDNS 帳戶設定
```bash
# 1. 前往 https://www.duckdns.org
# 2. 使用 GitHub/Google 帳戶登入
# 3. 創建一個子網域，例如：myserver
# 4. 記下你的 Token（類似：a7c4d0ad-114e-40ef-ba1d-d217904a50f2）
```

### 2. 伺服器需求
- **作業系統**：Ubuntu 18.04+ 或 Debian 9+
- **權限**：sudo 或 root 存取權限
- **網路**：可連接外網的伺服器
- **端口**：80 和 443 端口對外開放

---

## 🛠️ 一鍵安裝腳本

### 創建安裝腳本

創建檔案 `setup_duckdns_ssl.sh`：

```bash
#!/bin/bash

# DuckDNS + Let's Encrypt 自動化安裝腳本
# 使用方法: sudo bash setup_duckdns_ssl.sh

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 輸出函數
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查是否為 root 用戶
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "此腳本需要 root 權限運行"
        print_info "請使用: sudo bash $0"
        exit 1
    fi
}

# 獲取用戶輸入
get_user_input() {
    print_info "=== DuckDNS + Let's Encrypt 設定 ==="
    echo
    
    # DuckDNS 設定
    read -p "請輸入你的 DuckDNS 子網域名稱 (不含 .duckdns.org): " DUCKDNS_DOMAIN
    if [[ -z "$DUCKDNS_DOMAIN" ]]; then
        print_error "網域名稱不能為空"
        exit 1
    fi
    
    read -p "請輸入你的 DuckDNS Token: " DUCKDNS_TOKEN
    if [[ -z "$DUCKDNS_TOKEN" ]]; then
        print_error "Token 不能為空"
        exit 1
    fi
    
    # 用戶設定
    read -p "請輸入要運行 DuckDNS 更新的用戶名稱 (預設: $SUDO_USER): " DUCK_USER
    DUCK_USER=${DUCK_USER:-$SUDO_USER}
    if [[ -z "$DUCK_USER" ]]; then
        print_error "用戶名稱不能為空"
        exit 1
    fi
    
    # 確認設定
    echo
    print_info "=== 設定確認 ==="
    echo "網域: ${DUCKDNS_DOMAIN}.duckdns.org"
    echo "Token: ${DUCKDNS_TOKEN:0:8}..."
    echo "用戶: $DUCK_USER"
    echo
    read -p "確認以上設定正確嗎? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_warning "安裝已取消"
        exit 0
    fi
}

# 安裝必要套件
install_packages() {
    print_info "更新套件列表並安裝必要工具..."
    
    apt update
    apt install -y curl cron certbot python3-certbot-nginx nginx
    
    print_success "套件安裝完成"
}

# 設定 DuckDNS
setup_duckdns() {
    print_info "設定 DuckDNS..."
    
    # 取得用戶家目錄
    USER_HOME=$(eval echo ~$DUCK_USER)
    DUCKDNS_DIR="$USER_HOME/duckdns"
    
    # 創建目錄
    mkdir -p "$DUCKDNS_DIR"
    
    # 創建更新腳本
    cat > "$DUCKDNS_DIR/duck.sh" << EOF
#!/bin/bash
# DuckDNS 自動更新腳本
# 由 setup_duckdns_ssl.sh 自動生成

DOMAIN="$DUCKDNS_DOMAIN"
TOKEN="$DUCKDNS_TOKEN"
LOG_FILE="\$HOME/duckdns/duck.log"

# 記錄時間
echo "\$(date): 開始更新 DuckDNS IP" >> "\$LOG_FILE"

# 更新 IP
curl -s "https://www.duckdns.org/update?domains=\$DOMAIN&token=\$TOKEN" -o "\$LOG_FILE.tmp"

# 檢查結果
if grep -q "OK" "\$LOG_FILE.tmp"; then
    echo "\$(date): IP 更新成功" >> "\$LOG_FILE"
else
    echo "\$(date): IP 更新失敗" >> "\$LOG_FILE"
    cat "\$LOG_FILE.tmp" >> "\$LOG_FILE"
fi

rm -f "\$LOG_FILE.tmp"
EOF
    
    # 設定權限
    chmod +x "$DUCKDNS_DIR/duck.sh"
    chown -R $DUCK_USER:$DUCK_USER "$DUCKDNS_DIR"
    
    # 執行一次測試
    print_info "測試 DuckDNS 更新..."
    sudo -u $DUCK_USER "$DUCKDNS_DIR/duck.sh"
    
    if grep -q "OK" "$DUCKDNS_DIR/duck.log"; then
        print_success "DuckDNS 設定成功"
    else
        print_error "DuckDNS 測試失敗，請檢查 Token 和網域名稱"
        cat "$DUCKDNS_DIR/duck.log"
        exit 1
    fi
}

# 設定 crontab
setup_crontab() {
    print_info "設定 DuckDNS 自動更新 (每5分鐘)..."
    
    USER_HOME=$(eval echo ~$DUCK_USER)
    CRON_CMD="*/5 * * * * $USER_HOME/duckdns/duck.sh"
    
    # 檢查是否已存在相同的 cron job
    if sudo -u $DUCK_USER crontab -l 2>/dev/null | grep -q "duck.sh"; then
        print_warning "DuckDNS cron job 已存在，跳過設定"
    else
        # 添加 cron job
        (sudo -u $DUCK_USER crontab -l 2>/dev/null; echo "$CRON_CMD") | sudo -u $DUCK_USER crontab -
        print_success "DuckDNS 自動更新已設定"
    fi
}

# 等待 DNS 傳播
wait_dns_propagation() {
    print_info "等待 DNS 記錄傳播..."
    FULL_DOMAIN="${DUCKDNS_DOMAIN}.duckdns.org"
    
    for i in {1..12}; do
        if nslookup "$FULL_DOMAIN" > /dev/null 2>&1; then
            print_success "DNS 記錄已生效"
            return 0
        fi
        print_info "等待 DNS 傳播... ($i/12)"
        sleep 10
    done
    
    print_warning "DNS 傳播可能需要更長時間，繼續進行 SSL 設定"
}

# 基本 Nginx 設定
setup_nginx_basic() {
    print_info "設定基本 Nginx 配置..."
    
    FULL_DOMAIN="${DUCKDNS_DOMAIN}.duckdns.org"
    NGINX_CONF="/etc/nginx/sites-available/$DUCKDNS_DOMAIN"
    
    # 創建基本配置（HTTP only，為了 Let's Encrypt 驗證）
    cat > "$NGINX_CONF" << EOF
server {
    listen 80;
    server_name $FULL_DOMAIN;
    
    # Let's Encrypt 驗證路徑
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # 臨時首頁
    location / {
        root /var/www/html;
        index index.html;
    }
}
EOF
    
    # 創建簡單的首頁
    cat > "/var/www/html/index.html" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>$FULL_DOMAIN</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; }
        .container { max-width: 600px; margin: 0 auto; }
        .success { color: #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="success">🎉 網站設定成功！</h1>
        <p>你的網域 <strong>$FULL_DOMAIN</strong> 已經可以正常訪問了。</p>
        <p>SSL 憑證正在設定中...</p>
        <hr>
        <p><small>Powered by DuckDNS + Let's Encrypt</small></p>
    </div>
</body>
</html>
EOF
    
    # 啟用網站
    ln -sf "$NGINX_CONF" "/etc/nginx/sites-enabled/"
    
    # 移除預設網站
    rm -f /etc/nginx/sites-enabled/default
    
    # 測試配置
    nginx -t
    systemctl reload nginx
    
    print_success "基本 Nginx 配置完成"
}

# 申請 Let's Encrypt SSL 憑證
setup_ssl() {
    print_info "申請 Let's Encrypt SSL 憑證..."
    
    FULL_DOMAIN="${DUCKDNS_DOMAIN}.duckdns.org"
    EMAIL="admin@${FULL_DOMAIN}"
    
    # 申請憑證
    certbot --nginx \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        --domains "$FULL_DOMAIN" \
        --redirect
    
    if [[ $? -eq 0 ]]; then
        print_success "SSL 憑證申請成功"
    else
        print_error "SSL 憑證申請失敗"
        return 1
    fi
}

# 設定 SSL 自動更新
setup_ssl_auto_renewal() {
    print_info "設定 SSL 憑證自動更新..."
    
    # 檢查是否已有自動更新設定
    if crontab -l 2>/dev/null | grep -q "certbot renew"; then
        print_warning "SSL 自動更新已設定，跳過"
    else
        # 添加自動更新 cron job (每天凌晨3點檢查)
        (crontab -l 2>/dev/null; echo "0 3 * * * /usr/bin/certbot renew --quiet --nginx") | crontab -
        print_success "SSL 自動更新已設定"
    fi
}

# 最終檢查和優化
final_optimization() {
    print_info "進行最終優化..."
    
    FULL_DOMAIN="${DUCKDNS_DOMAIN}.duckdns.org"
    
    # 更新首頁，移除 "SSL 設定中" 訊息
    cat > "/var/www/html/index.html" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>$FULL_DOMAIN</title>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            text-align: center; 
            margin: 0;
            padding: 50px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            box-sizing: border-box;
        }
        .container { 
            max-width: 600px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .success { color: #4CAF50; }
        .badge { 
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            margin: 10px 5px;
        }
        .info { 
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 恭喜！網站設定完成</h1>
        <div class="badge">✅ HTTPS 已啟用</div>
        <div class="badge">🔒 SSL 憑證有效</div>
        <div class="badge">🔄 自動更新</div>
        
        <div class="info">
            <h3>網站資訊</h3>
            <p><strong>網域:</strong> $FULL_DOMAIN</p>
            <p><strong>服務:</strong> DuckDNS + Let's Encrypt</p>
            <p><strong>狀態:</strong> <span class="success">運行正常</span></p>
        </div>
        
        <p>你的網站現在已經:</p>
        <ul style="text-align: left; display: inline-block;">
            <li>✅ 支援 HTTPS 安全連線</li>
            <li>✅ SSL 憑證自動更新</li>
            <li>✅ DuckDNS IP 自動同步</li>
            <li>✅ 準備好部署你的應用</li>
        </ul>
        
        <hr style="margin: 30px 0; border: 1px solid rgba(255,255,255,0.3);">
        <p><small>Generated by DuckDNS + Let's Encrypt Auto Setup Script</small></p>
    </div>
</body>
</html>
EOF
    
    # 檢查服務狀態
    systemctl enable nginx
    systemctl enable cron
    
    print_success "最終優化完成"
}

# 顯示完成資訊
show_completion_info() {
    FULL_DOMAIN="${DUCKDNS_DOMAIN}.duckdns.org"
    USER_HOME=$(eval echo ~$DUCK_USER)
    
    echo
    print_success "=== 安裝完成！ ==="
    echo
    echo "📋 安裝摘要:"
    echo "  🌐 網域: https://$FULL_DOMAIN"
    echo "  🔒 SSL: Let's Encrypt (90天自動更新)"
    echo "  🔄 DuckDNS: 每5分鐘自動更新IP"
    echo "  👤 運行用戶: $DUCK_USER"
    echo
    echo "📁 重要檔案位置:"
    echo "  DuckDNS 腳本: $USER_HOME/duckdns/duck.sh"
    echo "  DuckDNS 日誌: $USER_HOME/duckdns/duck.log"
    echo "  Nginx 配置: /etc/nginx/sites-available/$DUCKDNS_DOMAIN"
    echo "  SSL 憑證: /etc/letsencrypt/live/$FULL_DOMAIN/"
    echo
    echo "🔧 常用管理指令:"
    echo "  查看 DuckDNS 日誌: tail -f $USER_HOME/duckdns/duck.log"
    echo "  手動更新 DuckDNS: $USER_HOME/duckdns/duck.sh"
    echo "  檢查 SSL 憑證: certbot certificates"
    echo "  手動更新 SSL: sudo certbot renew"
    echo "  重啟 Nginx: sudo systemctl restart nginx"
    echo
    echo "📅 自動化任務:"
    echo "  DuckDNS 更新: 每5分鐘"
    echo "  SSL 憑證更新: 每天凌晨3點檢查"
    echo
    print_info "現在可以訪問 https://$FULL_DOMAIN 測試你的網站！"
    echo
}

# 主要執行流程
main() {
    clear
    print_info "DuckDNS + Let's Encrypt 自動化安裝腳本"
    print_info "此腳本將幫你設定免費的動態DNS和SSL憑證"
    echo
    
    check_root
    get_user_input
    
    print_info "開始安裝..."
    install_packages
    setup_duckdns
    setup_crontab
    wait_dns_propagation
    setup_nginx_basic
    setup_ssl
    setup_ssl_auto_renewal
    final_optimization
    
    show_completion_info
}

# 執行主程式
main "$@"
```

---

## 📱 使用步驟

### 1. 下載並準備腳本
```bash
# 創建腳本檔案
nano setup_duckdns_ssl.sh

# 複製上面的腳本內容到檔案中
# 儲存並退出編輯器

# 給予執行權限
chmod +x setup_duckdns_ssl.sh
```

### 2. 執行安裝
```bash
# 使用 sudo 執行腳本
sudo bash setup_duckdns_ssl.sh
```

### 3. 輸入設定資訊
腳本會依序詢問：
- **DuckDNS 子網域名稱**：例如 `myserver`（不要包含 `.duckdns.org`）
- **DuckDNS Token**：從你的 DuckDNS 帳戶頁面複製
- **運行用戶**：通常按 Enter 使用預設即可

### 4. 確認設定並等待完成
- 腳本會顯示設定摘要供你確認
- 確認後會自動安裝和配置所有服務
- 整個過程大約需要 5-10 分鐘

---

## 🎯 完成後的結果

### ✅ 你將擁有
- **安全的 HTTPS 網站**：`https://yourname.duckdns.org`
- **自動 IP 更新**：每 5 分鐘檢查並更新 IP 地址
- **自動 SSL 更新**：憑證到期前自動更新
- **美觀的首頁**：展示安裝成功和系統狀態

### 📁 重要檔案位置
```
~/duckdns/duck.sh              # DuckDNS 更新腳本
~/duckdns/duck.log             # 更新日誌檔案
/etc/nginx/sites-available/    # Nginx 網站配置
/etc/letsencrypt/live/         # SSL 憑證儲存位置
/var/www/html/index.html       # 網站首頁
```

---

## 🔧 日常管理指令

### DuckDNS 管理
```bash
# 查看更新日誌
tail -f ~/duckdns/duck.log

# 手動執行更新
~/duckdns/duck.sh

# 查看 cron 任務
crontab -l
```

### SSL 憑證管理
```bash
# 檢查憑證狀態
sudo certbot certificates

# 手動更新憑證
sudo certbot renew

# 測試自動更新
sudo certbot renew --dry-run
```

### Nginx 管理
```bash
# 檢查配置語法
sudo nginx -t

# 重新載入配置
sudo systemctl reload nginx

# 重啟 Nginx
sudo systemctl restart nginx

# 查看狀態
sudo systemctl status nginx
```

---

## 🚀 部署你的應用

安裝完成後，你可以將 Django 應用部署到這個環境：

### 修改 Nginx 配置
```bash
# 編輯 Nginx 配置
sudo nano /etc/nginx/sites-available/yourname

# 添加反向代理到你的 Django 應用
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# 重新載入配置
sudo systemctl reload nginx
```

### Django 設定
```python
# settings.py
ALLOWED_HOSTS = ['yourname.duckdns.org']
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

---

## 🛡️ 安全性和最佳實踐

### 自動化任務檢查
```bash
# DuckDNS 更新：每5分鐘
*/5 * * * * /home/user/duckdns/duck.sh

# SSL 更新：每天凌晨3點
0 3 * * * /usr/bin/certbot renew --quiet --nginx
```

### 防火牆設定
```bash
# 開放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 監控和備份
```bash
# 設定日誌輪轉
sudo nano /etc/logrotate.d/duckdns

# 內容：
/home/*/duckdns/duck.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
}
```

---

## 🔍 故障排除

### 常見問題

**1. DuckDNS 更新失敗**
```bash
# 檢查日誌
cat ~/duckdns/duck.log

# 確認 Token 和網域名稱正確
# 手動測試更新
curl "https://www.duckdns.org/update?domains=yourname&token=yourtoken"
```

**2. SSL 憑證申請失敗**
```bash
# 檢查 DNS 解析
nslookup yourname.duckdns.org

# 確認防火牆開放 80 端口
sudo ufw status

# 手動申請憑證
sudo certbot --nginx -d yourname.duckdns.org
```

**3. Nginx 配置錯誤**
```bash
# 測試配置
sudo nginx -t

# 查看錯誤日誌
sudo tail -f /var/log/nginx/error.log
```

---

## 📞 支援和社群

- **DuckDNS 官網**：https://www.duckdns.org
- **Let's Encrypt 文檔**：https://letsencrypt.org/docs/
- **Nginx 官方文檔**：https://nginx.org/en/docs/

這個一鍵安裝腳本讓你能在幾分鐘內擁有一個完全免費、安全且自動化的 HTTPS 網站！