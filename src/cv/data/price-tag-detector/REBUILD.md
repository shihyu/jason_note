# 重建指南

## 目錄結構說明

### 原始資料（必須保留）
```
data/
├── manual_labels/  (353M)  手動標註的 JSON 文件
├── videos/         (655M)  原始影片
└── images/         (341M)  從影片提取的圖片幀
```

### 產生的文件（可刪除重建）
```
data/
├── dataset/        (23M)   YOLO 訓練資料集
├── models/         (6M)    訓練好的模型
└── detections/     (4M)    檢測結果

runs/               (17M)   訓練日誌和檢查點
```

## Make 指令說明

### 基本指令
```bash
make              # 顯示說明
make build        # 安裝依賴
make prepare      # 轉換 JSON 為 YOLO 格式（創建 data/dataset/）
make train        # 訓練模型（創建 data/models/ 和 runs/）
make detect       # 執行檢測（創建 data/detections/）
make test         # 執行測試
make clean        # 清理所有產生的文件
make rebuild      # 完整重建（clean + prepare + train）
```

### make clean 行為
**刪除：**
- ✓ `data/dataset/` - YOLO 訓練資料集
- ✓ `data/models/` - 訓練好的模型
- ✓ `data/detections/` - 檢測結果
- ✓ `runs/` - 訓練日誌
- ✓ `__pycache__/` - Python 快取
- ✓ `.pytest_cache/` - 測試快取

**保留：**
- ✓ `data/manual_labels/` - 手動標註
- ✓ `data/videos/` - 原始影片
- ✓ `data/images/` - 原始圖片

## 完整重建流程

### 方法 1：一步步執行
```bash
make clean      # 1. 清理所有產生的文件
make build      # 2. 安裝依賴
make prepare    # 3. 轉換標註格式
make train      # 4. 訓練模型
make detect     # 5. 執行檢測
```

### 方法 2：使用 rebuild
```bash
make rebuild    # 自動執行 clean + prepare + train
make detect     # 手動執行檢測
```

### 方法 3：完整一行命令
```bash
make clean && make build && make prepare && make train && make detect
```

## 檔案大小統計

| 類型 | 大小 | 說明 |
|------|------|------|
| 原始資料 | 1.3GB | 必須保留 |
| 產生文件 | 50MB | 可刪除重建 |

## 注意事項

1. **首次建立**：需要先運行 `make build` 安裝依賴
2. **prepare 步驟**：需要 `convert_manual_labels.py` 腳本
3. **訓練時間**：完整訓練約需 5-10 分鐘（取決於硬體）
4. **磁碟空間**：重建後總空間約 1.35GB

## 驗證重建結果

```bash
# 檢查訓練結果
ls -lh data/models/best.pt

# 檢查訓練日誌
ls -lh runs/train/price_tag_detector/

# 檢查資料集
ls data/dataset/train/images/ | wc -l  # 應該是 39
ls data/dataset/valid/images/ | wc -l  # 應該是 10
```
