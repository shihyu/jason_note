# PocketBase 完整安裝使用指南

PocketBase 是一個極輕量的後端解決方案，安裝使用非常簡單！

## 📦 安裝方式

### 方法 1: 直接下載 (推薦)

```bash
# 到官網下載對應系統的執行檔
# https://pocketbase.io/docs/

# Linux/macOS
wget https://github.com/pocketbase/pocketbase/releases/download/v0.22.0/pocketbase_0.22.0_linux_amd64.zip
unzip pocketbase_0.22.0_linux_amd64.zip

# 給執行權限
chmod +x pocketbase

# 啟動
./pocketbase serve
```

### 方法 2: 使用 Go 安裝

```bash
go install github.com/pocketbase/pocketbase@latest
pocketbase serve
```

### 方法 3: Docker

```bash
# 使用官方 Docker 映像檔
docker run -d \
  --name pocketbase \
  -p 8090:8090 \
  -v /path/to/pb_data:/pb_data \
  ghcr.io/muchobien/pocketbase:latest
```

## 🚀 基本使用

### 1. 啟動服務

```bash
# 基本啟動 (預設 port 8090)
./pocketbase serve

# 自定義端口
./pocketbase serve --http=0.0.0.0:8080

# 啟動時顯示更多資訊
./pocketbase serve --dev
```

啟動後訪問：
- **管理介面**: http://localhost:8090/_/
- **API 端點**: http://localhost:8090/api/

### 2. 建立管理員帳號

首次啟動會要求建立管理員帳號，或訪問 `http://localhost:8090/_/` 手動建立。

### 3. 建立 Collection (資料表)

在管理介面中：
1. 點擊 "New collection"
2. 設定 Collection 名稱 (例如: `users`, `posts`)
3. 添加欄位 (text, number, email, file 等)
4. 設定權限規則

## 💻 Python 客戶端使用

### 安裝 Python SDK

```bash
pip install pocketbase
```

### 基本操作範例

```python
from pocketbase import PocketBase

# 連接到 PocketBase
client = PocketBase('http://127.0.0.1:8090')

# === 身份驗證 ===

# 管理員登入
admin_data = client.admins.auth_with_password("admin@example.com", "password123")
print("管理員登入成功:", admin_data.token)

# 用戶註冊
user_data = {
    "username": "testuser",
    "email": "test@example.com", 
    "password": "password123",
    "passwordConfirm": "password123"
}

try:
    user = client.collection("users").create(user_data)
    print("用戶註冊成功:", user.id)
except Exception as e:
    print("註冊失敗:", e)

# 用戶登入
try:
    auth_data = client.collection("users").auth_with_password("test@example.com", "password123")
    print("用戶登入成功:", auth_data.token)
except Exception as e:
    print("登入失敗:", e)
```

### CRUD 操作

```python
# 建立資料
def create_post():
    data = {
        "title": "我的第一篇文章",
        "content": "這是文章內容",
        "author": client.auth_store.model.id  # 當前用戶 ID
    }
    
    try:
        record = client.collection("posts").create(data)
        print("建立成功:", record.id)
        return record
    except Exception as e:
        print("建立失敗:", e)
        return None

# 查詢資料
def get_posts():
    try:
        # 查詢所有文章
        records = client.collection("posts").get_full_list()
        print(f"共找到 {len(records)} 篇文章")
        
        for record in records:
            print(f"- {record.title} (ID: {record.id})")
            
        return records
    except Exception as e:
        print("查詢失敗:", e)
        return []

# 根據 ID 查詢單筆資料
def get_post_by_id(post_id):
    try:
        record = client.collection("posts").get_one(post_id)
        print("找到文章:", record.title)
        return record
    except Exception as e:
        print("查詢失敗:", e)
        return None

# 條件查詢
def search_posts(keyword):
    try:
        # 使用過濾器查詢
        filter_query = f'title ~ "{keyword}" || content ~ "{keyword}"'
        records = client.collection("posts").get_full_list(filter=filter_query)
        
        print(f"搜尋 '{keyword}' 找到 {len(records)} 結果")
        return records
    except Exception as e:
        print("搜尋失敗:", e)
        return []

# 更新資料
def update_post(post_id, new_title):
    try:
        data = {"title": new_title}
        record = client.collection("posts").update(post_id, data)
        print("更新成功:", record.title)
        return record
    except Exception as e:
        print("更新失敗:", e)
        return None

# 刪除資料
def delete_post(post_id):
    try:
        client.collection("posts").delete(post_id)
        print("刪除成功")
        return True
    except Exception as e:
        print("刪除失敗:", e)
        return False
```

### 檔案上傳

```python
def upload_file():
    try:
        # 上傳檔案到 posts collection
        with open("example.jpg", "rb") as f:
            data = {
                "title": "帶圖片的文章",
                "content": "這篇文章有圖片",
                "image": f  # 直接傳入檔案物件
            }
            
            record = client.collection("posts").create(data)
            print("檔案上傳成功:", record.image)
            
            # 取得檔案 URL
            file_url = client.get_file_url(record, record.image)
            print("檔案連結:", file_url)
            
    except Exception as e:
        print("檔案上傳失敗:", e)
```

### 即時訂閱

```python
def setup_realtime():
    def on_record_change(e):
        print("資料異動:", e.action, e.record.id)
        
    # 訂閱 posts collection 的變化
    client.collection("posts").subscribe("*", on_record_change)
```

## 🔧 進階設定

### 環境變數設定

```bash
# 設定資料庫路徑
export PB_DATA=/path/to/pb_data

# 設定加密密鑰
export PB_ENCRYPTION_KEY=your-32-char-key

# 啟動
./pocketbase serve
```

### 自定義 Hooks (Go)

如果需要自定義邏輯，可以將 PocketBase 作為 Go 框架使用：

```go
package main

import (
    "log"
    "github.com/pocketbase/pocketbase"
    "github.com/pocketbase/pocketbase/core"
)

func main() {
    app := pocketbase.New()

    // 添加自定義 Hook
    app.OnBeforeServe().Add(func(e *core.ServeEvent) error {
        // 自定義邏輯
        return nil
    })

    if err := app.Start(); err != nil {
        log.Fatal(err)
    }
}
```

## 🌐 部署到生產環境

### Systemd 服務

建立服務檔案：

```bash
sudo nano /etc/systemd/system/pocketbase.service
```

服務設定：

```ini
[Unit]
Description=PocketBase
After=network.target

[Service]
Type=simple
User=pocketbase
WorkingDirectory=/opt/pocketbase
ExecStart=/opt/pocketbase/pocketbase serve --http=0.0.0.0:8090
Restart=always

[Install]
WantedBy=multi-user.target
```

啟用服務：

```bash
sudo systemctl enable pocketbase
sudo systemctl start pocketbase
```

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8090;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📁 目錄結構

```
pb_data/
├── data.db          # SQLite 資料庫
├── logs.db          # 日誌資料庫
└── storage/         # 檔案儲存目錄
    └── collections/
```

## 🔍 管理介面功能

- **Collections 管理**: 建立、編輯資料表結構
- **Records 管理**: 新增、編輯、刪除資料
- **Users 管理**: 用戶帳號管理
- **Files 管理**: 檔案上傳與管理
- **Logs 查看**: 系統日誌監控
- **Settings**: 系統設定

## 🎯 主要優勢

- **極度簡單**: 一個檔案就能運行完整的後端服務
- **快速部署**: 無需複雜的設定和依賴
- **輕量級**: 使用 SQLite，資源消耗低
- **完整功能**: 包含認證、資料庫、檔案儲存、即時訂閱
- **開源**: 完全開源，可自由修改

## 📝 適用場景

- 快速原型開發
- 小型專案或個人專案
- 資源有限的環境
- 需要快速上線的 MVP
- 學習和實驗用途

PocketBase 的最大優勢就是**極度簡單**，非常適合快速開發和部署！

---

## 🔬 測試範例

### Python 測試腳本

```python
from pocketbase import PocketBase
import requests

client = PocketBase("http://202.182.118.167:8090")


# 方法1: 直接 HTTP 請求測試
def test_auth_endpoints():
    endpoints = [
        "/api/admins/auth-with-password",
    ]

    for endpoint in endpoints:
        url = f"http://202.182.118.167:8090{endpoint}"
        payload = {"identity": "yaoshihyu@gmail.com", "password": "2lraroai2lraroai"}

        try:
            response = requests.post(url, json=payload, timeout=10)
            print(f"Testing {endpoint}:")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  Success! Response: {response.json()}")
                return endpoint, response.json()
            else:
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"  Exception: {e}")

    return None, None


# 測試不同端點
endpoint, auth_data = test_auth_endpoints()

if auth_data:
    print(f"\n成功認證使用端點: {endpoint}")
else:
    print("\n所有端點都失敗了")

    # 方法2: 嘗試使用 PocketBase 客戶端的不同方法
    try:
        # 嘗試作為普通用戶認證
        user_auth = client.collection("users").auth_with_password(
            "xxxxxxxx@gmail.com", "2lxxxxx"
        )
        print("用戶認證成功:", user_auth.token)
    except Exception as e:
        print(f"用戶認證失敗: {e}")
```

### Shell 腳本測試

```shell
#!/bin/bash

# 獲取 token
TOKEN=$(curl -s -X POST "http://202.182.118.167:8090/api/admins/auth-with-password" \
  -H "Content-Type: application/json" \
  -d '{"identity":"xxxxxxxxxx@gmail.com","password":"2lxxx"}' | jq -r '.token')

echo "Token: $TOKEN"


echo "=== 所有 Collections ==="
COLLECTIONS=$(curl -s -X GET "http://202.182.118.167:8090/api/collections" \
  -H "Authorization: Bearer $TOKEN")

echo "$COLLECTIONS" | jq '.items[] | {
  name: .name,
  type: .type,
  id: .id,
  created: .created,
  schema_fields: [.schema[] | .name]
}'

# 創建測試用戶
echo "=== 創建用戶 ==="
curl -X POST "http://202.182.118.167:8090/api/collections/users/records" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "username": "john_doe_tt",
    "email": "john.doeTT@example.com",
    "password": "securepass1235",
    "passwordConfirm": "securepass1235",
    "name": "John Doe TT"
  }' | jq '.'

# 查看所有用戶
echo "=== 查看所有用戶 ==="
curl -s -X GET "http://202.182.118.167:8090/api/collections/users/records" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### 股票數據操作腳本

```shell
#!/bin/bash

# 簡單股票數據腳本
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTUwMTA1NzgsImlkIjoiMnloYjhsd2tsZ3k0Zzk0IiwidHlwZSI6ImFkbWluIn0.rPi3xend3dCrHzDIpG86uDwsZ4eGXrNb4SsK8poDaRw"
BASE_URL="http://202.182.118.167:8090"

echo "=== 股票數據操作 ==="

# 1. 創建股票數據集合
echo "1. 創建股票集合..."
curl -X POST "$BASE_URL/api/collections" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "stocks",
    "type": "base",
    "schema": [
      {"name": "symbol", "type": "text", "required": true},
      {"name": "name", "type": "text"},
      {"name": "date", "type": "date", "required": true},
      {"name": "open", "type": "number", "required": true},
      {"name": "high", "type": "number", "required": true},
      {"name": "low", "type": "number", "required": true},
      {"name": "close", "type": "number", "required": true},
      {"name": "volume", "type": "number", "required": true}
    ]
  }' > /dev/null 2>&1

echo "✓ 集合創建完成"

# 2. 寫入股票數據
echo "2. 寫入股票數據..."

# 台積電
curl -s -X POST "$BASE_URL/api/collections/stocks/records" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "symbol": "2330",
    "name": "台積電",
    "date": "2025-07-29",
    "open": 1010.0,
    "high": 1025.0,
    "low": 1005.0,
    "close": 1020.0,
    "volume": 15623000
  }' > /dev/null

# 鴻海
curl -s -X POST "$BASE_URL/api/collections/stocks/records" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "symbol": "2317",
    "name": "鴻海",
    "date": "2025-07-29",
    "open": 120.5,
    "high": 122.0,
    "low": 119.0,
    "close": 121.5,
    "volume": 8945000
  }' > /dev/null

# 聯發科
curl -s -X POST "$BASE_URL/api/collections/stocks/records" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "symbol": "2454",
    "name": "聯發科",
    "date": "2025-07-29",
    "open": 800.0,
    "high": 815.0,
    "low": 795.0,
    "close": 810.0,
    "volume": 3245000
  }' > /dev/null

echo "✓ 股票數據寫入完成"

# 3. 讀取數據
echo "3. 讀取股票數據..."
curl -s "$BASE_URL/api/collections/stocks/records" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '.items[] | {symbol, name, date, open, high, low, close, volume}'

# 4. 導出 CSV
echo "4. 導出 CSV..."
echo "symbol,name,date,open,high,low,close,volume" > stocks.csv
curl -s "$BASE_URL/api/collections/stocks/records" \
  -H "Authorization: Bearer $TOKEN" | \
  jq -r '.items[] | [.symbol, .name, .date, .open, .high, .low, .close, .volume] | @csv' >> stocks.csv

echo "✓ 數據已導出到 stocks.csv"
echo ""
echo "=== 完成 ==="
echo "- 集合已創建"
echo "- 3筆股票數據已寫入"
echo "- 數據已顯示"
echo "- CSV已導出"
```
