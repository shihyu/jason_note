# 免費 DNS 與 SSL 完整指南 2025

## 🌐 免費 DNS 服務

DNS 服務可以分為兩大類：**公共 DNS 解析器**（用來加速上網）和**動態 DNS 服務**（用來獲得免費網域名）。

---

## 🚀 公共 DNS 解析器（提升上網速度）

這些服務可以取代你的 ISP DNS，提供更快、更安全的網路瀏覽體驗。

### 1. Cloudflare DNS（推薦）
- **主要 DNS**：`1.1.1.1`
- **次要 DNS**：`1.0.0.1`
- **特色**：
  - 全球最快的 DNS 服務之一
  - 強調隱私保護，24 小時內刪除記錄
  - 支援 DNS-over-HTTPS (DoH) 和 DNS-over-TLS (DoT)
  - 內建惡意網站防護
- **適用於**：注重速度和隱私的用戶

### 2. Google Public DNS
- **主要 DNS**：`8.8.8.8`
- **次要 DNS**：`8.8.4.4`
- **特色**：
  - Google 強大網路支援，穩定可靠
  - 支援 DNSSEC 安全擴展
  - 全球廣泛可用
  - 免費且快速
- **適用於**：需要穩定性的一般用戶

### 3. Quad9
- **主要 DNS**：`9.9.9.9`
- **次要 DNS**：`149.112.112.112`
- **特色**：
  - 免費安全 DNS 服務
  - 自動阻擋惡意網站和釣魚網站
  - 不記錄個人資料
  - 全球 150+ 解析叢集
- **適用於**：注重安全性的用戶

### 4. OpenDNS（Cisco）
- **主要 DNS**：`208.67.222.222`
- **次要 DNS**：`208.67.220.220`
- **特色**：
  - 免費版本包含基本安全防護
  - 家庭版可過濾不當內容
  - 支援自訂過濾選項
  - 99.9% 正常運行時間
- **適用於**：家庭用戶和需要內容過濾的環境

---

## 🏠 動態 DNS 服務（免費網域名）

這些服務提供免費的子網域，讓你可以用域名訪問家裡的伺服器。

### 1. DuckDNS（強烈推薦）
- **網址**：https://www.duckdns.org
- **免費額度**：5 個子網域
- **網域格式**：`your-name.duckdns.org`
- **特色**：
  - 完全免費，由 AWS 託管
  - 設定極其簡單
  - 支援 IPv4 和 IPv6
  - 提供多平臺自動更新腳本
  - 256 位元 SSL 安全連線
  - 不需註冊，OAuth 登入即可
- **缺點**：只能使用 duckdns.org 子網域
- **適用於**：新手和快速部署

### 2. No-IP
- **網址**：https://www.noip.com
- **免費額度**：3 個主機名
- **網域格式**：多種選擇，如 `yourname.ddns.net`
- **特色**：
  - 老牌 DDNS 服務商
  - 多種域名選項
  - 提供客戶端軟體
  - 100% 正常運行時間保證
- **缺點**：
  - 免費帳戶需每 30 天確認一次
  - 免費版功能受限
- **適用於**：需要多樣域名選擇的用戶

### 3. Dynu
- **網址**：https://www.dynu.com
- **免費額度**：4 個子網域
- **網域格式**：`yourname.dynu.net` 或自訂域名
- **特色**：
  - 支援頂級域名和三級域名
  - 全球名稱伺服器
  - IP 地址追蹤
  - 100% 正常運行時間
  - 提供客戶端程式
- **適用於**：需要進階功能的用戶

### 4. FreeDNS (afraid.org)
- **網址**：https://freedns.afraid.org
- **免費額度**：5 個子網域 + 無限自訂域名
- **特色**：
  - 功能強大且靈活
  - 支援多種記錄類型
  - 社群共享域名
  - 完全免費
- **缺點**：介面較舊，設定複雜
- **適用於**：進階用戶

---

## 🔒 免費 SSL 憑證服務

SSL 憑證對於網站安全至關重要，以下是主要的免費 SSL 提供商。

### 1. Let's Encrypt（推薦）
- **提供者**：非營利組織 Internet Security Research Group
- **憑證效期**：90 天（可自動更新）
- **特色**：
  - 完全免費且受所有主流瀏覽器信任
  - 支援通配符憑證（*.example.com）
  - 自動化部署和更新
  - 全球超過 2.5 億個域名使用
  - 支援多種驗證方式（HTTP、DNS、TLS-SNI）
- **使用工具**：Certbot
- **安裝指令**：
```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# 申請憑證
sudo certbot --nginx -d your-domain.com

# 自動更新（crontab）
0 3 * * * /usr/bin/certbot renew --quiet
```

### 2. Cloudflare Universal SSL
- **網址**：https://www.cloudflare.com
- **憑證效期**：1 年（自動更新）
- **特色**：
  - 免費計劃包含 SSL
  - 支援通配符憑證
  - 全球 CDN 加速
  - DDoS 防護
  - 設定極其簡單
  - 支援 HTTP/2 和 HTTP/3
- **設定步驟**：
  1. 註冊 Cloudflare 帳戶
  2. 添加你的域名
  3. 更改域名伺服器到 Cloudflare
  4. 自動獲得 SSL 憑證
- **適用於**：需要 CDN 和額外安全功能的用戶

### 3. Google Trust Services
- **提供者**：Google
- **憑證效期**：90 天
- **特色**：
  - Google 的 CA 服務
  - 與 GlobalSign 交叉簽署，相容性佳
  - 支援現代加密算法
- **主要用於**：Google Cloud Platform 用戶

### 4. SSL.com（免費試用）
- **提供者**：SSL.com
- **免費期間**：90 天試用
- **特色**：
  - 高相容性（99.9% 瀏覽器支援）
  - 支援多種驗證類型
  - 企業級功能
- **適用於**：需要測試企業級 SSL 的用戶

---

## 🛠️ 實際部署範例

### 使用 DuckDNS + Let's Encrypt 的完整設定

**步驟 1：設定 DuckDNS**
```bash
# 1. 到 https://www.duckdns.org 用 GitHub/Google 登入
# 2. 創建子網域，例如：myserver.duckdns.org
# 3. 記下你的 token

# 4. 創建更新腳本
mkdir ~/duckdns
nano ~/duckdns/duck.sh
```

**腳本內容：**
```bash
#!/bin/bash
DOMAIN="myserver"
TOKEN="your-token-here"
curl -k -o ~/duckdns/duck.log "https://www.duckdns.org/update?domains=${DOMAIN}&token=${TOKEN}"
```

**步驟 2：設定自動更新**
```bash
chmod +x ~/duckdns/duck.sh

# 設定 crontab 每 5 分鐘更新
crontab -e
# 加入這行：
*/5 * * * * ~/duckdns/duck.sh
```

**步驟 3：申請 Let's Encrypt SSL**
```bash
# 安裝 Certbot
sudo apt install certbot python3-certbot-nginx

# 申請憑證
sudo certbot --nginx -d myserver.duckdns.org

# 設定自動更新
echo "0 3 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### 使用 Cloudflare 的設定

**步驟 1：轉移 DNS 到 Cloudflare**
```bash
# 1. 註冊 Cloudflare 帳戶
# 2. 添加你的域名
# 3. 更改域名伺服器到 Cloudflare 提供的 NS
# 4. 等待 DNS 傳播（通常 24 小時內）
```

**步驟 2：啟用 SSL**
```bash
# 在 Cloudflare Dashboard：
# 1. 進入 SSL/TLS 設定
# 2. 選擇 "Full" 或 "Full (strict)" 模式
# 3. 啟用 "Always Use HTTPS"
# 4. 啟用 "Automatic HTTPS Rewrites"
```

---

## 🔧 進階配置建議

### DNS 效能最佳化
```bash
# 測試不同 DNS 的速度
dig @1.1.1.1 google.com
dig @8.8.8.8 google.com
dig @9.9.9.9 google.com

# 設定多個 DNS（/etc/resolv.conf）
nameserver 1.1.1.1
nameserver 8.8.8.8
nameserver 9.9.9.9
```

### SSL 安全最佳化
```nginx
# Nginx SSL 最佳實踐
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;

# 安全標頭
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
```

---

## 💡 選擇建議

### DNS 服務選擇
- **速度優先**：Cloudflare DNS (1.1.1.1)
- **安全優先**：Quad9 (9.9.9.9)
- **穩定優先**：Google DNS (8.8.8.8)
- **家庭使用**：OpenDNS

### 動態 DNS 選擇
- **新手推薦**：DuckDNS
- **功能需求**：Dynu
- **穩定需求**：No-IP
- **進階用戶**：FreeDNS

### SSL 憑證選擇
- **技術用戶**：Let's Encrypt
- **簡單需求**：Cloudflare Universal SSL
- **企業用戶**：Let's Encrypt + 商業 CA 備份

---

## ✅ 檢查清單

部署完成後確認：

**DNS 檢查**
- [ ] DNS 解析正確：`nslookup your-domain.com`
- [ ] IP 更新正常：檢查 DDNS 服務面板
- [ ] 自動更新腳本運作正常

**SSL 檢查**
- [ ] HTTPS 正常訪問
- [ ] 憑證有效期：瀏覽器鎖頭圖示
- [ ] SSL 評級：https://www.ssllabs.com/ssltest/
- [ ] 自動更新設定完成

**安全檢查**
- [ ] HTTP 自動跳轉 HTTPS
- [ ] 安全標頭正確設定
- [ ] 防火牆規則適當

這些免費服務已經能滿足大多數個人和小型企業的需求，而且品質完全不輸付費服務！