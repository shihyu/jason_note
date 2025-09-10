# Ubuntu 24.04 MySQL 安裝與客戶端工具指南

## MySQL Server 安裝

### 1. 更新系統套件
```bash
sudo apt update
sudo apt upgrade
```

### 2. 安裝 MySQL Server
```bash
sudo apt install mysql-server
```

### 3. 啟動並啟用 MySQL 服務
```bash
sudo systemctl start mysql
sudo systemctl enable mysql
```

### 4. 執行安全設定
```bash
sudo mysql_secure_installation
```

安全設定會詢問以下選項：
- 設定 root 密碼
- 移除匿名使用者
- 禁止 root 遠端登入
- 移除測試資料庫
- 重新載入權限表

## MySQL 客戶端工具推薦

### 命令列工具

#### MySQL Client (官方命令列工具)
```bash
# 安裝
sudo apt install mysql-client

# 使用
mysql -u username -p
mysql -h hostname -u username -p database_name
```

#### mycli (改良版命令列工具)
```bash
# 安裝
sudo apt install mycli

# 使用 (支援自動完成和語法高亮)
mycli -u username -p
```

### 圖形化界面工具

#### 1. MySQL Workbench (官方推薦)
```bash
# 安裝
sudo apt install mysql-workbench
```

**特色功能：**
- 官方開發，功能完整
- 資料庫設計與建模
- SQL 開發與執行
- 伺服器管理
- 資料匯入/匯出
- 視覺化 ER 圖設計

#### 2. DBeaver Community Edition (免費、功能豐富)
```bash
# 方法 1: Snap 安裝
sudo snap install dbeaver-ce

# 方法 2: 下載 .deb 套件
wget https://dbeaver.io/files/dbeaver-ce_latest_amd64.deb
sudo dpkg -i dbeaver-ce_latest_amd64.deb
sudo apt-get install -f
```

**特色功能：**
- 支援多種資料庫 (MySQL, PostgreSQL, SQLite 等)
- 現代化用戶界面
- 強大的 SQL 編輯器
- 資料視覺化
- ER 圖生成
- 資料匯入/匯出工具

#### 3. phpMyAdmin (Web 界面)
```bash
# 安裝
sudo apt install phpmyadmin apache2 php

# 配置 Apache
sudo a2enconf phpmyadmin
sudo systemctl reload apache2
```

**存取方式：**
- 瀏覽器開啟：`http://localhost/phpmyadmin`

**特色功能：**
- Web 界面，無需安裝客戶端
- 適合遠端管理
- 支援多語言
- 資料庫備份與還原

#### 4. Adminer (輕量級 Web 工具)
```bash
# 下載
sudo wget https://www.adminer.org/latest.php -O /var/www/html/adminer.php

# 存取
# http://localhost/adminer.php
```

### 程式碼編輯器擴充套件

#### Visual Studio Code
推薦擴充套件：
- **MySQL** - 官方 MySQL 擴充
- **SQLTools** - 多資料庫支援
- **SQL Database Projects** - 資料庫專案管理

#### JetBrains DataGrip (付費)
專業的資料庫 IDE，功能最為強大。

## 連線測試與基本使用

### 測試 MySQL 服務狀態
```bash
sudo systemctl status mysql
```

### 連線到 MySQL
```bash
# 使用 root 帳戶連線
sudo mysql

# 或使用密碼連線
mysql -u root -p
```

### 基本 MySQL 指令
```sql
-- 顯示所有資料庫
SHOW DATABASES;

-- 建立新資料庫
CREATE DATABASE myapp;

-- 選擇資料庫
USE myapp;

-- 顯示資料表
SHOW TABLES;

-- 建立使用者
CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'mypassword';

-- 授予權限
GRANT ALL PRIVILEGES ON myapp.* TO 'myuser'@'localhost';
FLUSH PRIVILEGES;
```

## 工具選擇建議

| 使用情境 | 推薦工具 | 原因 |
|---------|---------|------|
| 日常開發 | MySQL Workbench | 官方工具，功能完整 |
| 多資料庫環境 | DBeaver CE | 支援多種資料庫 |
| 遠端管理 | phpMyAdmin | Web 界面方便 |
| 輕量級使用 | mycli | 命令列但更友善 |
| 專業開發 | DataGrip | 功能最強大（付費）|

## 安全性建議

1. **定期更新 MySQL**
```bash
sudo apt update && sudo apt upgrade mysql-server
```

2. **配置防火牆**
```bash
sudo ufw allow mysql
```

3. **備份資料庫**
```bash
mysqldump -u root -p database_name > backup.sql
```

4. **監控日誌**
```bash
sudo tail -f /var/log/mysql/error.log
```

## 疑難排解

### 忘記 root 密碼
```bash
sudo mysql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'new_password';
FLUSH PRIVILEGES;
EXIT;
```

### 檢查 MySQL 版本
```bash
mysql --version
```

### 檢查連接埠
```bash
sudo netstat -tlnp | grep mysql
```

選擇適合你需求的工具，開始你的 MySQL 開發之旅！