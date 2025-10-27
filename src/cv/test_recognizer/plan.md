# 手機圖片辨識與價格查詢系統

## 任務目標
建立一個能夠透過手機圖片辨識手機型號並顯示價格的系統。

## 專案配置
- 預設 Port: 8080（如果選擇 Web 介面）
- Python 版本: 3.8+
- 主要套件: torch, transformers, pillow, numpy

## 預期產出

### 目錄結構
```
mobileclip_test/
├── data/
│   ├── phones/           # 手機圖片資料庫
│   │   ├── iphone_15_pro/
│   │   ├── samsung_s24/
│   │   └── ...
│   ├── phone_data.json   # 手機完整資料（價格、規格、介紹）
│   └── seed_data.json    # 初始測試資料集
├── src/
│   ├── __init__.py
│   ├── scraper.py        # 資料收集模組
│   ├── database.py       # 資料庫管理
│   ├── recognizer.py     # 圖片辨識核心
│   └── main.py           # 主程式入口
├── tests/
│   ├── test_scraper.py
│   ├── test_database.py
│   ├── test_recognizer.py
│   └── fixtures/         # 測試用圖片
├── Makefile
├── requirements.txt
└── README.md
```

## 功能規格

### 1. 手機資料爬取（scraper.py）
- 自動從網路來源收集手機資料
- 資料內容：型號、品牌、價格、規格介紹、參考圖片
- 資料來源：固定的測試資料集（JSON 格式，包含常見手機）
- 自動下載參考圖片到 data/phones/ 目錄

### 2. 手機資料庫管理（database.py）
- 載入手機資料（圖片路徑、型號、價格、介紹）
- 新增/更新手機資料
- 查詢手機完整資訊

### 3. 圖片辨識（recognizer.py）
- 使用 MobileCLIP 提取圖片特徵
- 與資料庫中的手機圖片進行相似度比對
- 返回最相似的手機型號及信心分數

### 4. 主程式（main.py）
- CLI 介面：輸入圖片路徑，輸出手機完整資訊
- 格式：`python src/main.py --image <圖片路徑>`
- 輸出：型號、品牌、價格、規格介紹

## Makefile 規範

### 必備目標
- `make` (無參數)：顯示可用目標和使用範例
- `make setup`：安裝依賴套件
- `make init-data`：初始化手機資料（自動下載參考圖片和價格資訊）
- `make build`：準備執行環境（下載模型等）
- `make run`：執行示範程式
- `make test`：執行所有測試
- `make clean`：清理建置產物和臨時檔案

### 使用範例
```bash
make setup          # 初次安裝
make init-data      # 自動收集手機資料
make build          # 下載 MobileCLIP 模型
make run IMG=test.jpg  # 辨識圖片
make test           # 執行測試
```

## Build/Debug/Test 指令

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 初始化資料
```bash
# 自動收集手機資料並下載圖片
python src/scraper.py --init

# 查看已收集的手機列表
python src/database.py --list
```

### 執行程式
```bash
# 辨識單張圖片並顯示完整資訊
python src/main.py --image path/to/phone.jpg

# 顯示詳細比對資訊
python src/main.py --image path/to/phone.jpg --verbose
```

### 執行測試
```bash
# 執行所有測試
pytest tests/ -v

# 執行特定測試
pytest tests/test_recognizer.py -v
```

### Debug
```bash
# 顯示辨識詳細資訊
python src/main.py --image test.jpg --verbose

# 測試資料庫連線
python src/database.py --list
```

## 驗收標準

### 功能驗收
- [ ] 能夠載入至少 5 種不同手機的資料
- [ ] 輸入手機圖片，能正確辨識型號（準確率 > 80%）
- [ ] 顯示手機價格資訊
- [ ] 處理不在資料庫中的手機（顯示「無法辨識」）

### 測試驗收
- [ ] 所有單元測試通過
- [ ] 測試覆蓋率 > 70%
- [ ] 包含至少 3 個不同角度的測試圖片

### 程式碼品質
- [ ] 符合 PEP 8 規範
- [ ] 包含適當的錯誤處理
- [ ] 有清楚的 README 說明

## 子任務拆解

### Phase 1: 基礎架構
1. 建立專案結構和 Makefile
2. 設定 requirements.txt
3. 建立 seed_data.json（初始測試資料，包含 5-10 支手機）

### Phase 2: 資料收集與管理
4. 實作 scraper.py（下載圖片和建立資料庫）
5. 實作 database.py（資料載入、查詢、管理）
6. 測試資料收集功能

### Phase 3: 圖片辨識核心
7. 整合 MobileCLIP 模型
8. 實作特徵提取功能
9. 實作相似度比對演算法

### Phase 4: 主程式與測試
10. 實作 CLI 介面（顯示完整資訊）
11. 撰寫單元測試
12. 整合測試與效能驗證

### Phase 5: 優化與文件
13. 錯誤處理優化
14. 撰寫 README
15. 清理臨時檔案

## 資料格式定義

### phone_data.json
```json
{
  "phones": [
    {
      "id": "iphone_15_pro",
      "name": "iPhone 15 Pro",
      "brand": "Apple",
      "price": 36900,
      "currency": "TWD",
      "specs": {
        "display": "6.1 吋 Super Retina XDR",
        "processor": "A17 Pro 晶片",
        "camera": "48MP 主鏡頭 + 12MP 超廣角 + 12MP 望遠",
        "battery": "最長 23 小時影片播放",
        "storage": "128GB / 256GB / 512GB / 1TB"
      },
      "description": "採用航太級鈦金屬設計，配備 A17 Pro 晶片與專業級相機系統",
      "image_path": "data/phones/iphone_15_pro/reference.jpg",
      "image_url": "https://example.com/iphone15pro.jpg",
      "features_path": "data/phones/iphone_15_pro/features.npy"
    }
  ]
}
```

### seed_data.json（初始測試資料）
```json
{
  "phones": [
    {
      "name": "iPhone 15 Pro",
      "brand": "Apple",
      "price": 36900,
      "image_url": "https://store.storeimages.cdn-apple.com/...",
      "specs": {...},
      "description": "..."
    },
    {
      "name": "Samsung Galaxy S24 Ultra",
      "brand": "Samsung",
      "price": 42900,
      "image_url": "https://...",
      "specs": {...},
      "description": "..."
    }
  ]
}
```

## 技術細節

### MobileCLIP 使用
- 模型：apple/mobileclip_s0 或 s1（較輕量）
- 輸入：PIL Image
- 輸出：特徵向量（用於相似度比對）

### 相似度計算
- 使用餘弦相似度（Cosine Similarity）
- 閾值：> 0.8 視為匹配，< 0.5 視為無法辨識

## 待討論問題

1. **手機資料範圍**：要支援哪些品牌和型號？
2. **價格更新**：價格資料如何維護（手動 or 自動）？
3. **介面選擇**：CLI 或 Web 介面？
4. **擴充性**：未來是否需要支援其他商品類別？

## 注意事項

- MobileCLIP 模型首次執行會自動下載（約 20-50MB）
- 測試圖片建議使用白色背景，清晰的手機正面照
- 系統對圖片品質和角度有要求，建議提供使用指南
