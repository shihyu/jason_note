# SSH 遠端連線配置成功指南

## 配置資訊
- **伺服器 IP**: 219.68.168.47
- **SSH Port**: 1234
- **使用者**: shihyu
- **連線指令**: `ssh -p 1234 shihyu@219.68.168.47`

## 配置步驟總結

### 1. 修改 SSH 配置檔
**檔案**: `/etc/ssh/sshd_config`
```bash
# 修改或新增以下設定
Port 1234
```

### 2. 重啟 SSH 服務
由於使用 systemd socket activation，需要執行特殊步驟：
```bash
sudo systemctl daemon-reload
sudo systemctl restart ssh.socket
sudo systemctl restart ssh
```

### 3. 確認服務監聽狀態
```bash
# 檢查 port 1234 是否正在監聽
ss -tln | grep :1234
```
預期輸出：
```
LISTEN 0      4096         0.0.0.0:1234       0.0.0.0:*
LISTEN 0      4096            [::]:1234          [::]:*
```

### 4. 配置防火牆
```bash
# 開放 port 1234
sudo ufw allow 1234/tcp

# 啟用防火牆
sudo ufw --force enable

# 檢查防火牆狀態
sudo ufw status
```

### 5. 測試連線
```bash
# 本機測試
ssh -p 1234 shihyu@localhost

# 外部測試
ssh -p 1234 shihyu@219.68.168.47
```

## 重要注意事項

### 安全建議
1. **使用 SSH 金鑰認證**（比密碼更安全）
   ```bash
   # 在客戶端生成金鑰
   ssh-keygen -t ed25519

   # 複製公鑰到伺服器
   ssh-copy-id -p 1234 shihyu@219.68.168.47
   ```

2. **禁用密碼登入**（設定金鑰後）
   編輯 `/etc/ssh/sshd_config`：
   ```
   PasswordAuthentication no
   ```

3. **限制登入來源**
   可在防火牆設定特定 IP 才能連線：
   ```bash
   sudo ufw allow from 特定IP to any port 1234
   ```

### 故障排除

#### 問題 1: 無法連線
- 檢查服務狀態：`systemctl status ssh`
- 檢查 port 監聽：`ss -tln | grep :1234`
- 檢查防火牆：`sudo ufw status`

#### 問題 2: Connection refused
- 確認 SSH 服務正在運行
- 確認防火牆規則已設定
- 確認路由器 port forwarding（如果在 NAT 後面）

#### 問題 3: Permission denied
- 確認使用者名稱和密碼正確
- 檢查 `/var/log/auth.log` 查看錯誤訊息
- 確認使用者有登入權限

## 常用管理指令

```bash
# 查看 SSH 服務狀態
systemctl status ssh

# 查看 SSH 連線記錄
sudo journalctl -u ssh -f

# 查看目前連線的使用者
who

# 查看登入記錄
last

# 查看失敗的登入嘗試
sudo grep "Failed password" /var/log/auth.log
```

## 進階配置選項

### 修改其他 SSH 設定
編輯 `/etc/ssh/sshd_config` 可調整：
- `LoginGraceTime`: 登入逾時時間
- `MaxAuthTries`: 最大認證嘗試次數
- `ClientAliveInterval`: 保持連線的間隔
- `MaxSessions`: 最大同時連線數

### 設定 SSH 別名（客戶端）
在客戶端的 `~/.ssh/config` 新增：
```
Host myserver
    HostName 219.68.168.47
    Port 1234
    User shihyu
```
之後可簡化連線指令為：`ssh myserver`

## 維護建議
1. 定期更新系統：`sudo apt update && sudo apt upgrade`
2. 定期檢查登入記錄
3. 考慮安裝 fail2ban 防止暴力破解
4. 定期備份 SSH 設定檔

---
文件建立日期：2025-09-30
