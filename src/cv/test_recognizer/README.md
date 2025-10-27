# 手機圖片辨識系統

使用 MobileCLIP 進行手機圖片辨識，輸入手機圖片後自動顯示型號、品牌、價格和規格資訊。

## 系統需求

- Python 3.8+
- PyTorch
- MobileCLIP

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 辨識手機圖片

```bash
python src/recognizer.py --image <手機圖片路徑>
```

**範例：**

```bash
# 辨識 iPhone 15 Pro
python src/recognizer.py --image data/phones/apple_iphone_15_pro/reference.jpg

# 辨識 iPhone 14 Pro
python src/recognizer.py --image data/phones/apple_iphone_14_pro/reference.jpg

# 辨識自己的手機圖片
python src/recognizer.py --image ~/Downloads/my_phone.jpg
```

### 3. 輸出範例

```
============================================================
✓ 辨識成功！

信心度: 100.0%
============================================================

手機型號：iPhone 15 Pro
品牌：Apple
價格：NT$ 36,900

規格：
  • display: 6.1 吋 Super Retina XDR OLED
  • processor: A17 Pro 晶片
  • camera: 48MP 主鏡頭 + 12MP 超廣角 + 12MP 望遠 (3x)
  • battery: 最長 23 小時影片播放
  • storage: 128GB / 256GB / 512GB / 1TB
  • ram: 8GB

介紹：
  採用航太級鈦金屬設計，配備 A17 Pro 晶片與專業級相機系統
============================================================
```

## 其他功能

### 查看資料庫

```bash
# 列出所有手機
python src/database.py --list

# 查詢特定手機
python src/database.py --id apple_iphone_15_pro

# 搜尋品牌
python src/database.py --brand Apple
```

### 新增手機資料

1. 編輯 `data/seed_data.json` 加入新手機資料
2. 執行初始化指令：

```bash
python src/scraper.py --init
```

### 執行測試

```bash
# 執行所有測試
python -m pytest tests/ -v

# 執行特定測試
python -m pytest tests/test_recognizer.py -v
```

## 專案結構

```
test_recognizer/
├── data/
│   ├── phone_data.json          # 手機資料庫
│   ├── seed_data.json           # 初始測試資料
│   └── phones/                  # 手機圖片和特徵
│       ├── apple_iphone_15_pro/
│       │   ├── reference.jpg
│       │   └── features.npy
│       └── apple_iphone_14_pro/
│           ├── reference.jpg
│           └── features.npy
├── src/
│   ├── recognizer.py           # 圖片辨識核心
│   ├── database.py             # 資料庫管理
│   └── scraper.py              # 資料收集
├── tests/                      # 單元測試
├── Makefile                    # 建置腳本
└── requirements.txt            # Python 依賴
```

## 技術細節

- **模型**: MobileCLIP S0 (輕量級視覺語言模型)
- **特徵提取**: 使用 MobileCLIP 提取圖片特徵向量
- **相似度計算**: 餘弦相似度 (Cosine Similarity)
- **辨識閾值**: 0.5 (低於此值視為無法辨識)

## 目前支援的手機

- iPhone 15 Pro (NT$ 36,900)
- iPhone 14 Pro (NT$ 32,900)

## 注意事項

- 首次執行會自動提取並儲存手機特徵向量
- 建議使用清晰的手機正面照，白色背景效果最佳
- 系統對圖片品質和角度有一定要求

## 授權

本專案使用 MobileCLIP 模型，請參考 [Apple ML Research](https://github.com/apple/ml-mobileclip)。
