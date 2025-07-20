# Facebook 爬蟲專案

簡單易用的 Facebook 貼文爬蟲工具，支援未登入和登入兩種模式。

## 🚀 快速開始

```bash
# 一鍵設置環境
make setup

# 執行爬蟲
make run
```

## 📁 專案結構

```
├── fb_scraper.py      # 主程式檔案
├── requirements.txt   # 套件依賴
├── Makefile          # 環境管理
└── README.md         # 專案說明
```

## 🛠️ 環境設置

### 自動設置（推薦）
```bash
make setup    # 建立虛擬環境 + 安裝套件
```

### 手動設置
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 執行方式

### 1. 未登入模式（預設）
直接執行，無需 Facebook 帳號：
```bash
make run
# 或
python fb_scraper.py
```

### 2. 登入模式
編輯 `fb_scraper.py`：
1. 註解掉 Example.1 區塊
2. 取消註解 Example.2 區塊  
3. 填入真實的 Facebook 帳號密碼
4. 執行程式

## 📋 輸出格式

程式會顯示：
- 用戶資訊（名稱、追蹤者）
- 貼文列表（日期、按讚數、留言數、分享數、內容預覽）
- 完整資料自動儲存到 `facebook_data.json`

範例輸出：
```
============================================================
用戶: 專職交易人，擅長日內當沖，有時隔日沖，偶爾期權，很少波段，歡迎交流
追蹤者: 8,781 followers
共 3 篇貼文
============================================================

【貼文 1】2025-06-02
👍 653 | 💬 33 | 📤 10
📝 當沖很難，但不是不能賺錢。很多人問：「你覺得當沖能不能賺錢？」答案是：能，但很難...
----------------------------------------
```

## 🔧 常用指令

```bash
make help         # 顯示所有指令
make setup        # 完整環境設置
make run          # 執行爬蟲
make check        # 檢查環境狀態
make show-result  # 查看爬取結果摘要
make clean        # 清理輸出檔案
make reset        # 重置環境
```

## ⚙️ 設定說明

在 `fb_scraper.py` 中可調整：
- `facebook_user_id`: 目標用戶 ID
- `days_limit`: 爬取天數限制（預設 60 天）
- `driver_path`: ChromeDriver 路徑（預設自動尋找）

## ⚠️ 注意事項

- 請遵守 Facebook 服務條款
- 建議只爬取公開資料或自己的資料
- 登入模式有帳號風險，請謹慎使用
- 頻繁爬取可能被 Facebook 限制

## 🐛 問題排除

### 環境問題
```bash
make check     # 檢查環境狀態
make rebuild   # 重建環境
```

### ChromeDriver 問題
```bash
# 手動安裝 ChromeDriver
sudo apt-get install chromium-chromedriver  # Ubuntu
brew install chromedriver                   # macOS
```

### 套件衝突
```bash
make reset     # 完全重置環境
make setup     # 重新設置
```

## 📋 系統需求

- Python 3.7+
- Chrome 瀏覽器
- Linux/macOS/Windows

## 🔒 隱私聲明

本工具僅供學習研究使用，使用者需自行承擔使用風險並遵守相關法律法規。