# Django + Nginx + Gunicorn + SSL 完整部署指南

## 📖 架構說明

### 為什麼不用 Django 內建伺服器？
Django 內建的 `python manage.py runserver` 只適合**開發環境**，因為：
- 性能差，無法處理大量並發請求
- 沒有安全防護機制
- 不支援 SSL/HTTPS
- 無法處理靜態檔案的高效分發
- 官方明確說明不適合生產環境

### 生產環境架構
```
用戶瀏覽器 → Nginx (443/80端口) → Gunicorn (8000端口) → Django 應用
```

**各組件作用：**
- **Nginx**：網頁伺服器，處理 SSL、靜態檔案、反向代理
- **Gunicorn**：WSGI 伺服器，運行 Django 應用
- **Django**：應用程式邏輯處理

---

## 🚀 安裝步驟

### 1. 移除 Apache（如果已安裝）
```bash
# 停止並移除 Apache
sudo systemctl stop apache2
sudo systemctl disable apache2
sudo apt remove --purge apache2 apache2-utils apache2-bin
sudo apt autoremove

# 清理殘留
sudo rm -rf /etc/apache2
sudo rm -rf /var/log/apache2
```

### 2. 安裝 Nginx
```bash
# 更新套件列表
sudo apt update

# 安裝 Nginx
sudo apt install nginx

# 啟動並設定開機自啟
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 3. 安裝 Gunicorn
```bash
# 在你的 Django 虛擬環境中安裝
source /path/to/your/venv/bin/activate
pip install gunicorn
```

---

## 🔧 配置 Nginx

### 1. 創建網站配置檔
```bash
sudo nano /etc/nginx/sites-available/your-domain
```

### 2. 基本 HTTP 配置（先測試用）
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/project/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/your/project/media/;
        expires 30d;
    }
}
```

### 3. 啟用網站
```bash
# 創建符號連結
sudo ln -s /etc/nginx/sites-available/your-domain /etc/nginx/sites-enabled/

# 移除預設網站
sudo rm /etc/nginx/sites-enabled/default

# 測試配置語法
sudo nginx -t

# 重新載入配置
sudo systemctl reload nginx
```

---

## ⚙️ 配置 Gunicorn

### 1. 測試 Gunicorn 運行
```bash
cd /path/to/your/django/project
gunicorn your_project.wsgi:application --bind 127.0.0.1:8000
```

### 2. 創建 Gunicorn 系統服務
```bash
sudo nano /etc/systemd/system/your-project.service
```

### 3. 服務配置檔內容
```ini
[Unit]
Description=Gunicorn instance to serve your-project
After=network.target

[Service]
User=your-username
Group=www-data
WorkingDirectory=/path/to/your/project
Environment="PATH=/path/to/your/venv/bin"
ExecStart=/path/to/your/venv/bin/gunicorn \
    --workers 3 \
    --timeout 30 \
    --bind 127.0.0.1:8000 \
    your_project.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 4. 啟動服務
```bash
# 重新載入系統服務
sudo systemctl daemon-reload

# 啟動並設定開機自啟
sudo systemctl start your-project
sudo systemctl enable your-project

# 檢查狀態
sudo systemctl status your-project
```

---

## 🔒 SSL/HTTPS 配置

### 1. 安裝 Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

### 2. 申請 SSL 憑證
```bash
# 使用 Nginx 插件自動配置
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 或手動申請（需要暫停 Nginx）
sudo systemctl stop nginx
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com
sudo systemctl start nginx
```

### 3. 完整的 HTTPS Nginx 配置
```nginx
# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL 憑證路徑
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL 安全設定
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全標頭
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;

    # 反向代理到 Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超時設定
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # 靜態檔案直接由 Nginx 處理
    location /static/ {
        alias /path/to/your/project/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/your/project/media/;
        expires 30d;
    }

    # 安全：禁止訪問隱藏檔案
    location ~ /\. {
        deny all;
    }
}
```

### 4. 設定自動更新憑證
```bash
# 編輯 crontab
sudo crontab -e

# 加入這行（每天凌晨 3 點檢查更新）
0 3 * * * /usr/bin/certbot renew --quiet && /bin/systemctl reload nginx
```

---

## 🔧 Django 設定調整

### settings.py 生產環境設定
```python
# 安全設定
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# HTTPS 設定
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1年
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session 安全
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# 靜態檔案設定
STATIC_URL = '/static/'
STATIC_ROOT = '/path/to/your/project/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/path/to/your/project/media/'
```

---

## 🧪 測試步驟

### 1. 檢查服務狀態
```bash
# 檢查 Nginx
sudo systemctl status nginx
sudo nginx -t

# 檢查 Gunicorn
sudo systemctl status your-project

# 檢查端口監聽
sudo ss -tlnp | grep -E ":80|:443|:8000"
```

### 2. 測試 HTTP/HTTPS 連線
```bash
# 測試 HTTP（應該重定向到 HTTPS）
curl -I http://your-domain.com

# 測試 HTTPS
curl -I https://your-domain.com

# 測試 SSL 憑證
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

### 3. 檢查防火牆
```bash
# 開放必要端口
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh

# 封鎖直接訪問 Django 端口
sudo ufw deny 8000

# 檢查狀態
sudo ufw status
```

---

## 🛠️ 常用管理指令

### 重啟服務
```bash
# 重啟 Django 應用
sudo systemctl restart your-project

# 重新載入 Nginx 配置
sudo systemctl reload nginx

# 完全重啟 Nginx
sudo systemctl restart nginx
```

### 查看日誌
```bash
# Django 應用日誌
sudo journalctl -u your-project -f

# Nginx 錯誤日誌
sudo tail -f /var/log/nginx/error.log

# Nginx 訪問日誌
sudo tail -f /var/log/nginx/access.log
```

### 更新 SSL 憑證
```bash
# 測試更新（不會實際更新）
sudo certbot renew --dry-run

# 手動更新
sudo certbot renew
```

---

## 💡 配置原因解釋

### 為什麼用反向代理？
- **分工明確**：Nginx 處理網路層，Django 處理應用層
- **性能優化**：Nginx 處理靜態檔案比 Django 快得多
- **安全性**：Django 不直接暴露在網路上
- **擴展性**：可以輕鬆添加負載平衡、快取等功能

### SSL 終止的好處
- **效能**：Nginx 處理 SSL 加密解密，Django 專心處理業務邏輯
- **管理**：憑證統一在 Nginx 管理
- **安全**：現代化的 SSL 配置和安全標頭

### Gunicorn 的優勢
- **多進程**：可以同時處理多個請求
- **穩定性**：程序崩潰會自動重啟
- **效能**：比 Django 內建伺服器快很多
- **生產就緒**：專為生產環境設計

---

## ✅ 檢查清單

部署完成後，確認以下項目：

- [ ] Nginx 正常運行且通過語法檢查
- [ ] Gunicorn 服務正常運行
- [ ] HTTP 自動重定向到 HTTPS
- [ ] SSL 憑證有效且評級良好
- [ ] 靜態檔案正常載入
- [ ] Django 應用功能正常
- [ ] 防火牆正確配置
- [ ] 自動更新憑證已設定
- [ ] 服務設定為開機自啟

完成以上步驟，你的 Django 應用就能安全、穩定地運行在生產環境中了！