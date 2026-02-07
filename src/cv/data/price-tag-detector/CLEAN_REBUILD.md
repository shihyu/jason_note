# Clean 和 Rebuild 指南

## 問題解答

**Q: `make clean` 後，data 資料夾只要有 manual_labels 跟 videos，其他資料夾應該可以先砍掉之後從新產生對嘛？**

**A: 是的，完全正確！** ✅

## 資料夾分類

### 🔒 原始資料（永久保留）
```
data/manual_labels/  (353M)  - 手動標註的 JSON 文件
data/videos/         (655M)  - 原始 MP4 影片
```
**總計**: 1GB

### 🔄 產生的資料（可刪除重建）
```
data/images/         (341M)  - 從 videos/ 提取的圖片幀
data/dataset/        (23M)   - YOLO 訓練資料集
data/models/         (6M)    - 訓練好的模型
data/detections/     (4M)    - 檢測結果
data/detections_v2/  (?)     - 改進 OCR 的檢測結果
runs/                (17M)   - 訓練日誌和檢查點
```
**總計**: ~391MB

## Make 指令說明

### `make clean`
**完整清理** - 只保留 manual_labels + videos

```bash
make clean
```

**刪除:**
- ✓ data/images/         # 提取的圖片幀
- ✓ data/dataset/        # YOLO 訓練資料集
- ✓ data/models/         # 訓練模型
- ✓ data/detections/     # 檢測結果
- ✓ data/detections_v2/  # 改進 OCR 檢測結果
- ✓ runs/                # 訓練日誌
- ✓ __pycache__/         # Python 快取
- ✓ .pytest_cache/       # 測試快取

**保留:**
- ✓ data/manual_labels/  # 手動標註
- ✓ data/videos/         # 原始影片

**節省空間**: ~391MB

### `make clean-keep-images`
**保守清理** - 保留 manual_labels + videos + images

```bash
make clean-keep-images
```

**刪除:**
- ✓ data/dataset/
- ✓ data/models/
- ✓ data/detections/
- ✓ data/detections_v2/
- ✓ runs/
- ✓ 快取文件

**保留:**
- ✓ data/manual_labels/
- ✓ data/videos/
- ✓ data/images/         # ← 保留圖片幀

**節省空間**: ~50MB

**適用場景**:
- 影片提取很慢，想保留 images/
- 只想重新訓練模型
- 磁碟空間不是問題

## 完整重建流程

### 方法 1: 使用 rebuild（推薦）
```bash
make rebuild
```
等同於:
```bash
make clean      # 清理所有產生的文件
make extract    # 從 videos/ 提取 images/
make prepare    # 轉換標註為 YOLO 格式
make train      # 訓練模型
```

### 方法 2: 手動分步執行
```bash
# 1. 清理
make clean

# 2. 安裝依賴（如果需要）
make build

# 3. 從影片提取圖片幀
make extract    # 輸出: data/images/

# 4. 轉換標註格式
make prepare    # 輸出: data/dataset/

# 5. 訓練模型
make train      # 輸出: data/models/best.pt, runs/

# 6. 執行檢測
make detect     # 輸出: data/detections/
```

## 新增功能

### `make extract`
從 videos/ 提取所有圖片幀到 images/

```bash
make extract
```

**處理流程:**
1. 讀取 `data/videos/*.mp4`
2. 逐幀提取圖片
3. 保存到 `data/images/video1/`, `data/images/video2/`, `data/images/video3/`

**輸出:**
```
data/images/
├── video1/  (437 frames)
├── video2/  (205 frames)
└── video3/  (19 frames)
```

**處理時間**: 約 1-2 分鐘（取決於影片大小）

## 磁碟空間管理

### 完整清理後
```
原始資料: 1.0GB
  - manual_labels: 353MB
  - videos: 655MB
```

### 重建後
```
總計: 1.4GB
  - 原始資料: 1.0GB
  - 產生資料: 0.4GB
```

### 建議策略

**開發階段** - 保留 images/
```bash
make clean-keep-images  # 快速重建
make prepare
make train
```

**釋放空間** - 完整清理
```bash
make clean  # 刪除所有產生的文件
```

**正式部署** - 只保留必要文件
```bash
make clean
# 只保留 manual_labels 和 videos
# 需要時再重建
```

## 驗證清理結果

### 檢查保留的文件
```bash
ls -lh data/
# 應該只有 manual_labels/ 和 videos/
```

### 檢查磁碟使用
```bash
du -sh data/
# 應該約 1.0GB
```

### 測試重建
```bash
make rebuild
# 應該成功重建所有文件
```

## 常見問題

### Q: 為什麼要刪除 data/images/?
A:
- images/ 可以從 videos/ 重新提取
- 節省 341MB 空間
- 確保從原始影片重建，避免中間文件損壞

### Q: 提取圖片幀需要多久?
A:
- video1 (437 frames): ~30 秒
- video2 (205 frames): ~15 秒
- video3 (19 frames): ~2 秒
- 總計: ~1 分鐘

### Q: 如果只想重新訓練模型?
A:
```bash
make clean-keep-images  # 保留 images/
make prepare            # 重新轉換標註
make train              # 重新訓練
```

### Q: 如何完全從零開始?
A:
```bash
make clean              # 完整清理
make build              # 安裝依賴
make rebuild            # 完整重建
make detect             # 執行檢測
```

## 總結

✅ **您的理解完全正確**
- `make clean` 後只保留 manual_labels + videos
- 其他所有資料夾都會被刪除
- 可以通過 `make rebuild` 重新建立所有文件

✅ **兩種清理選項**
- `make clean` - 完整清理（節省 391MB）
- `make clean-keep-images` - 保守清理（節省 50MB）

✅ **自動化重建**
- `make extract` - 提取圖片幀
- `make rebuild` - 一鍵重建全部
