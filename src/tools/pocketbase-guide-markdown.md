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


```bash
#!/bin/bash

# 股票買賣超資料腳本
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTUwMTA1NzgsImlkIjoiMnloYjhsd2tsZ3k0Zzk0IiwidHlwZSI6ImFkbWluIn0.rPi3xend3dCrHzDIpG86uDwsZ4eGXrNb4SsK8poDaRw"
BASE_URL="http://202.182.118.167:8090"

echo "=== 股票券商買賣超資料 ==="

# 1. 建立集合
echo "1. 創建集合 broker_trades..."
curl -X POST "$BASE_URL/api/collections" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "broker_trades",
    "type": "base",
    "schema": [
      {"name": "symbol", "type": "text", "required": true},
      {"name": "date", "type": "date", "required": true},
      {"name": "type", "type": "text", "required": true},
      {"name": "broker", "type": "text", "required": true},
      {"name": "volume", "type": "number", "required": true},
      {"name": "avg_buy", "type": "number", "required": true},
      {"name": "avg_sell", "type": "number", "required": true}
    ]
  }' > /dev/null 2>&1
echo "✓ 集合創建完成"

# 資料共用參數
SYMBOL="2330"
DATE="2025-07-29"

# 2. 寫入買超 Top15
echo "2. 寫入買超 Top15..."
declare -a BUYERS=(
"新加坡商瑞銀,1337,1140.32,1140.55"
"美商高盛,1328,1136.23,1133.81"
"美林,1142,1134.32,1134.55"
"富邦-台北,1027,1137.64,1133.18"
"凱基-台北,593,1134.65,1132.22"
"花旗環球,311,1135.53,1137.82"
"港商麥格理,166,1136.74,1136.80"
"永豐金,128,1135.34,1134.11"
"永豐金-中正,61,1135.74,1130.32"
"華南永昌-岡山,58,1134.33,1130.00"
"台中銀,56,1130.10,1132.78"
"凱基-松山,50,1136.30,1134.96"
"第一金-彰化,44,1130.46,1137.09"
"香港上海匯豐,33,1135.15,1135.60"
"元大-天母,33,1132.91,1133.75"
)

for line in "${BUYERS[@]}"; do
  IFS=',' read -r BROKER VOLUME BUY SELL <<< "$line"
  curl -s -X POST "$BASE_URL/api/collections/broker_trades/records" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{
      \"symbol\": \"$SYMBOL\",
      \"date\": \"$DATE\",
      \"type\": \"buy\",
      \"broker\": \"$BROKER\",
      \"volume\": $VOLUME,
      \"avg_buy\": $BUY,
      \"avg_sell\": $SELL
    }" > /dev/null
done

# 3. 寫入賣超 Top15
echo "3. 寫入賣超 Top15..."
declare -a SELLERS=(
"摩根士丹利,1751,1137.06,1132.54"
"摩根大通,1533,1137.90,1136.03"
"富邦-南京,657,1131.71,1139.32"
"富邦,403,1133.88,1134.93"
"元大,258,1133.46,1134.04"
"大和國泰,238,1130.00,1141.76"
"港商野村,222,1134.49,1136.85"
"國泰,187,1134.92,1134.45"
"元富,113,1133.70,1134.56"
"致和,99,1131.23,1144.90"
"兆豐-三民,96,1138.28,1129.90"
"凱基,88,1137.39,1131.14"
"中國信託,85,1133.87,1131.53"
"第一金,79,1134.46,1130.28"
"第一金-新興,78,1136.50,1130.34"
)

for line in "${SELLERS[@]}"; do
  IFS=',' read -r BROKER VOLUME BUY SELL <<< "$line"
  curl -s -X POST "$BASE_URL/api/collections/broker_trades/records" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{
      \"symbol\": \"$SYMBOL\",
      \"date\": \"$DATE\",
      \"type\": \"sell\",
      \"broker\": \"$BROKER\",
      \"volume\": $VOLUME,
      \"avg_buy\": $BUY,
      \"avg_sell\": $SELL
    }" > /dev/null
done

echo "✓ 資料寫入完成"

# 4. 讀取資料
echo "4. 顯示資料..."
curl -s "$BASE_URL/api/collections/broker_trades/records" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '.items[] | {symbol, date, type, broker, volume, avg_buy, avg_sell}'

# 5. 匯出CSV
echo "5. 導出 CSV..."
echo "symbol,date,type,broker,volume,avg_buy,avg_sell" > broker_trades.csv
curl -s "$BASE_URL/api/collections/broker_trades/records" \
  -H "Authorization: Bearer $TOKEN" | \
  jq -r '.items[] | [.symbol, .date, .type, .broker, .volume, .avg_buy, .avg_sell] | @csv' >> broker_trades.csv

echo "✓ 資料已導出 broker_trades.csv"
echo ""
echo "=== 完成 ==="
```

```python
import requests
import csv

# === 設定 ===
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTUwMTA1NzgsImlkIjoiMnloYjhsd2tsZ3k0Zzk0IiwidHlwZSI6ImFkbWluIn0.rPi3xend3dCrHzDIpG86uDwsZ4eGXrNb4SsK8poDaRw"

BASE_URL = "http://202.182.118.167:8090"
HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}

SYMBOL = "2330"
DATE = "2025-07-29"
COLLECTION = "broker_trades"

# === 資料 ===
buyers = [
    ("新加坡商瑞銀", 1337, 1140.32, 1140.55),
    ("美商高盛", 1328, 1136.23, 1133.81),
    ("美林", 1142, 1134.32, 1134.55),
    ("富邦-台北", 1027, 1137.64, 1133.18),
    ("凱基-台北", 593, 1134.65, 1132.22),
    ("花旗環球", 311, 1135.53, 1137.82),
    ("港商麥格理", 166, 1136.74, 1136.80),
    ("永豐金", 128, 1135.34, 1134.11),
    ("永豐金-中正", 61, 1135.74, 1130.32),
    ("華南永昌-岡山", 58, 1134.33, 1130.00),
    ("台中銀", 56, 1130.10, 1132.78),
    ("凱基-松山", 50, 1136.30, 1134.96),
    ("第一金-彰化", 44, 1130.46, 1137.09),
    ("香港上海匯豐", 33, 1135.15, 1135.60),
    ("元大-天母", 33, 1132.91, 1133.75),
]

sellers = [
    ("摩根士丹利", 1751, 1137.06, 1132.54),
    ("摩根大通", 1533, 1137.90, 1136.03),
    ("富邦-南京", 657, 1131.71, 1139.32),
    ("富邦", 403, 1133.88, 1134.93),
    ("元大", 258, 1133.46, 1134.04),
    ("大和國泰", 238, 1130.00, 1141.76),
    ("港商野村", 222, 1134.49, 1136.85),
    ("國泰", 187, 1134.92, 1134.45),
    ("元富", 113, 1133.70, 1134.56),
    ("致和", 99, 1131.23, 1144.90),
    ("兆豐-三民", 96, 1138.28, 1129.90),
    ("凱基", 88, 1137.39, 1131.14),
    ("中國信託", 85, 1133.87, 1131.53),
    ("第一金", 79, 1134.46, 1130.28),
    ("第一金-新興", 78, 1136.50, 1130.34),
]


# === 工具函式 ===


def create_collection():
    print("1. 創建集合...")
    payload = {
        "name": COLLECTION,
        "type": "base",
        "schema": [
            {"name": "symbol", "type": "text", "required": True},
            {"name": "date", "type": "date", "required": True},
            {"name": "type", "type": "text", "required": True},
            {"name": "broker", "type": "text", "required": True},
            {"name": "volume", "type": "number", "required": True},
            {"name": "avg_buy", "type": "number", "required": True},
            {"name": "avg_sell", "type": "number", "required": True},
        ],
    }
    r = requests.post(f"{BASE_URL}/api/collections", headers=HEADERS, json=payload)
    if r.ok:
        print("✓ 集合已創建")
    else:
        print(f"⚠️ 集合創建失敗：{r.status_code} - {r.text}")


def insert_records(records, trade_type):
    for broker, volume, avg_buy, avg_sell in records:
        payload = {
            "symbol": SYMBOL,
            "date": DATE,
            "type": trade_type,
            "broker": broker,
            "volume": volume,
            "avg_buy": avg_buy,
            "avg_sell": avg_sell,
        }
        r = requests.post(
            f"{BASE_URL}/api/collections/{COLLECTION}/records",
            headers=HEADERS,
            json=payload,
        )
        if not r.ok:
            print(f"⚠️ 寫入失敗: {broker} ({trade_type})")


def fetch_all_records():
    res = requests.get(
        f"{BASE_URL}/api/collections/{COLLECTION}/records", headers=HEADERS
    )
    if not res.ok:
        print("⚠️ 讀取資料失敗")
        return []
    return res.json().get("items", [])


def print_records(records):
    print("4. 資料預覽：")
    for item in records:
        print(
            f"{item['date']} [{item['type']}] {item['broker']}: "
            f"{item['volume']} 張 | 買 {item['avg_buy']} 賣 {item['avg_sell']}"
        )


def export_to_csv(records, filename="broker_trades.csv"):
    print(f"5. 匯出 CSV 至 {filename}...")
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["symbol", "date", "type", "broker", "volume", "avg_buy", "avg_sell"]
        )
        for item in records:
            writer.writerow(
                [
                    item["symbol"],
                    item["date"],
                    item["type"],
                    item["broker"],
                    item["volume"],
                    item["avg_buy"],
                    item["avg_sell"],
                ]
            )
    print("✓ 匯出完成")


# === 執行流程 ===
def main():
    create_collection()
    print("2. 寫入買超 Top15...")
    insert_records(buyers, "buy")
    print("3. 寫入賣超 Top15...")
    insert_records(sellers, "sell")
    print("✓ 資料已寫入")

    data = fetch_all_records()
    print_records(data)
    export_to_csv(data)


if __name__ == "__main__":
    main()

```
