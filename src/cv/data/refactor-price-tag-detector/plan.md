# 專案計畫：price-tag-detector 重構

## 任務目標

將現有的 price-tag-detector 專案重構到新目錄 `refactor-price-tag-detector`，移除不需要的程式碼、測試檔案和實驗性程式碼，保持專案乾淨整潔，同時確保準確度維持在原本水準（98.4% OCR 成功率）。

核心要求：
1. **只保留必要的程式碼**：移除實驗性 OCR 引擎版本
2. **只保留核心測試**：移除臨時測試和診斷工具
3. **保留關鍵資料**：manual_labels + videos + dataset + models
4. **移除測試產物**：images, detections, detections_v2, failure_analysis
5. **驗證準確度**：確保重構後準確度與原本一致（98.4%）

## 專案結構組織

專案根目錄：`/home/shihyu/refactor-price-tag-detector`

```
refactor-price-tag-detector/
├── plan.md                     # 本檔案
├── README.md                   # 專案說明（精簡版）
├── Makefile                    # 標準化建置流程
├── pyproject.toml              # 依賴管理（精簡版）
├── uv.lock                     # 鎖定版本
│
├── src/                        # 核心程式碼（精簡後）
│   ├── __init__.py
│   ├── detector.py             # YOLO 檢測引擎
│   ├── color_filter.py         # 顏色過濾模組
│   ├── ocr_engine.py           # OCR 識別引擎（只保留最佳版本）
│   └── trainer.py              # 模型訓練器
│
├── cli/                        # 命令列介面（精簡版）
│   ├── __init__.py
│   └── detect.py               # 檢測命令
│
├── utils/                      # 工具腳本（只保留核心）
│   ├── __init__.py
│   └── dataset_splitter.py     # 資料集分割器
│
├── tests/                      # 測試（只保留核心測試）
│   ├── __init__.py
│   ├── test_detector.py        # 檢測器測試
│   ├── test_color_filter.py   # 顏色過濾測試
│   ├── test_ocr_engine.py      # OCR 測試
│   ├── test_accuracy.py        # ⭐ 準確度驗證測試（對比 manual_labels）
│   └── fixtures/               # 測試用固定資料
│       └── sample_images/
│
├── data/                       # 資料目錄（精簡版）
│   ├── models/                 # 訓練好的模型
│   │   └── best.pt             # 最佳模型（98.01% mAP50）
│   ├── dataset/                # 訓練資料集
│   │   ├── train/
│   │   │   ├── images/
│   │   │   └── labels/
│   │   ├── valid/
│   │   │   ├── images/
│   │   │   └── labels/
│   │   └── data.yaml
│   ├── videos/                 # ⭐ 原始影片（必須保留）
│   │   ├── video1.mp4
│   │   ├── video2.mp4
│   │   └── video3.mp4
│   └── manual_labels/          # ⭐ 手動標註（必須保留，用於準確度驗證）
│       ├── video1/
│       ├── video2/
│       └── video3/
│
└── .gitignore                  # Git 忽略規則
```

## 預期產出

### 1. 精簡的核心模組

#### 需要保留的檔案
- `src/detector.py` - YOLO 檢測引擎（從舊版複製）
- `src/color_filter.py` - 顏色過濾模組（從舊版複製）
- `src/ocr_engine.py` - **只保留最佳版本**（應該是 ocr_engine_v2.py 的改進版）
- `src/trainer.py` - 模型訓練器（從舊版複製）

#### 需要移除的檔案
- ❌ `src/ocr_engine_paddle.py` - PaddleOCR 實驗版本（報告顯示 0% 成功率）
- ❌ `src/ocr_engine_v2.py` - 如果已整合到 ocr_engine.py，則移除

### 2. 精簡的測試檔案

#### 需要保留的測試
- `tests/test_detector.py` - 檢測器核心測試
- `tests/test_color_filter.py` - 顏色過濾核心測試
- `tests/test_ocr_engine.py` - OCR 核心測試
- `tests/test_dataset_splitter.py` - 資料集分割測試
- ⭐ `tests/test_accuracy.py` - **新增：準確度驗證測試**

#### test_accuracy.py 規格
```python
"""
準確度驗證測試：對比系統輸出與 manual_labels

測試流程：
1. 從 data/videos/ 提取影格
2. 執行檢測（YOLO + ColorFilter + OCR）
3. 對比結果與 data/manual_labels/
4. 計算準確度指標：
   - 綠色區域 OCR 成功率
   - 黃色區域 OCR 成功率
   - 總體 OCR 成功率

驗收標準：
- Video1: ≥ 100.0%
- Video2: ≥ 96.9%
- Video3: ≥ 98.2%
- 總體平均: ≥ 98.4%
"""

def test_video1_accuracy():
    """測試 Video1 準確度 (應達 100%)"""
    pass

def test_video2_accuracy():
    """測試 Video2 準確度 (應達 96.9%)"""
    pass

def test_video3_accuracy():
    """測試 Video3 準確度 (應達 98.2%)"""
    pass

def test_overall_accuracy():
    """測試整體準確度 (應達 98.4%)"""
    pass
```

### 3. 精簡的資料目錄

#### 需要保留的資料（~1GB）
- ✅ `data/videos/` (655MB) - 原始影片，用於重新生成影格
- ✅ `data/manual_labels/` (353MB) - 手動標註，用於準確度驗證
- ✅ `data/dataset/` (22MB) - 訓練資料集
- ✅ `data/models/` (6MB) - 訓練好的模型

#### 需要移除的資料（~18GB）
- ❌ `data/images/` (6.7GB) - 從影片提取的影格（可重新生成）
- ❌ `data/detections/` (4.9GB) - 舊版檢測結果
- ❌ `data/detections_v2/` (6.7GB) - 新版檢測結果
- ❌ `data/failure_analysis/` (1.4MB) - 失敗案例分析圖片

### 4. 精簡的工具目錄

#### 需要保留
- ✅ `utils/dataset_splitter.py` - 資料集分割（核心功能）

#### 需要移除
- ❌ `utils/diagnose_green_ocr.py` - 診斷工具（實驗性）
- ❌ `utils/compare_ocr_engines.py` - 對比工具（實驗性）
- ❌ `utils/visualize_failures.py` - 視覺化工具（實驗性）
- ❌ `utils/visualizer.py` - 如果不是核心功能

### 5. 精簡的文件

#### 需要保留
- ✅ `README.md` - 精簡版，只包含核心使用說明
- ✅ `plan.md` - 本檔案

#### 需要移除
- ❌ `CLEAN_REBUILD.md` - 建置記錄
- ❌ `COMPLETE_ANALYSIS_REPORT.md` - 分析報告
- ❌ `FAILURE_CASE_ANALYSIS.md` - 失敗案例分析
- ❌ `OCR_IMPROVEMENTS.md` - 改進記錄
- ❌ `OCR_TEST_SUMMARY.md` - 測試摘要
- ❌ `REBUILD.md` - 建置記錄
- ❌ `VIDEO3_GREEN_OCR_ANALYSIS.md` - Video3 分析

### 6. 精簡的依賴（pyproject.toml）

```toml
[project]
name = "price-tag-detector"
version = "1.0.0"
description = "價格標籤檢測系統（精簡版）"
requires-python = ">=3.11"
dependencies = [
    "opencv-python>=4.8.0",
    "ultralytics>=8.0.0",
    "pytesseract>=0.3.10",
    "numpy>=1.24.0",
    "Pillow>=10.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
]
```

**移除的依賴**：
- ❌ paddlepaddle - PaddleOCR 已證實不適用
- ❌ paddleocr - 不需要
- ❌ autodistill - 已移除

## Makefile 規範

```makefile
.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build     - 安裝依賴"
	@echo "  make detect    - 執行檢測"
	@echo "  make test      - 執行測試"
	@echo "  make accuracy  - 驗證準確度（對比 manual_labels）"
	@echo "  make clean     - 清理產物"
	@echo ""
	@echo "使用範例："
	@echo "  make build && make accuracy"

.PHONY: build
build:  ## 安裝依賴
	uv sync

.PHONY: detect
detect:  ## 執行檢測
	@echo "從 video1.mp4 提取影格並檢測..."
	uv run cli/detect.py --video data/videos/video1.mp4 --output data/detections/video1

.PHONY: test
test:  ## 執行測試
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

.PHONY: accuracy
accuracy:  ## ⭐ 驗證準確度（對比 manual_labels）
	uv run pytest tests/test_accuracy.py -v -s

.PHONY: clean
clean:  ## 清理建置產物和臨時檔案
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov
	rm -rf data/detections/* data/images/*
```

## build/debug/test 指令

### Build
```bash
make build          # 安裝依賴
```

### Run
```bash
# 檢測（從影片提取影格並檢測）
make detect

# 或手動指定影片
uv run cli/detect.py --video data/videos/video2.mp4 --output data/detections/video2
```

### Debug
```bash
# 測試單個模組
uv run pytest tests/test_detector.py -v -s

# 測試準確度（顯示詳細輸出）
uv run pytest tests/test_accuracy.py -v -s
```

### Test
```bash
make test           # 執行所有測試
make accuracy       # ⭐ 驗證準確度（最重要）
```

## 驗收標準

- [ ] 專案目錄從 29GB 縮減到 ~1GB
- [ ] 只保留必要的程式碼檔案（4 個 src 檔案）
- [ ] 只保留核心測試（4 個核心測試 + 1 個準確度測試）
- [ ] 保留關鍵資料：manual_labels + videos + dataset + models
- [ ] 移除所有實驗性程式碼和分析文件
- [ ] ⭐ **準確度測試通過**：
  - Video1: ≥ 100.0%
  - Video2: ≥ 96.9%
  - Video3: ≥ 98.2%
  - 總體平均: ≥ 98.4%
- [ ] 所有核心測試通過
- [ ] Makefile 所有目標都能正常執行
- [ ] README.md 精簡清晰
- [ ] 無 PaddleOCR 依賴
- [ ] 程式碼乾淨，無註釋掉的程式碼

## 子任務拆解

### 子任務 1：建立新專案結構

**目標**：建立 refactor-price-tag-detector 目錄和基礎結構

**待做事項**：
1. 建立新目錄 `/home/shihyu/refactor-price-tag-detector`
2. 建立子目錄：src/, cli/, utils/, tests/, data/
3. 建立空檔案：__init__.py, .gitignore
4. 複製 Makefile（準備稍後精簡）
5. 複製 pyproject.toml（準備稍後精簡）

**驗收**：
- [ ] 目錄結構正確
- [ ] 基礎檔案已建立

---

### 子任務 2：複製關鍵資料

**目標**：複製必須保留的資料（videos, manual_labels, dataset, models）

**待做事項**：
1. 複製 `data/videos/` → `refactor-price-tag-detector/data/videos/`
2. 複製 `data/manual_labels/` → `refactor-price-tag-detector/data/manual_labels/`
3. 複製 `data/dataset/` → `refactor-price-tag-detector/data/dataset/`
4. 複製 `data/models/` → `refactor-price-tag-detector/data/models/`
5. 驗證檔案完整性（檢查檔案數量）

**驗收**：
- [ ] videos/ 包含 3 個 .mp4 檔案
- [ ] manual_labels/ 包含 3 個子目錄
- [ ] dataset/ 包含 train/, valid/, data.yaml
- [ ] models/ 包含 best.pt

---

### 子任務 3：複製並精簡核心程式碼

**目標**：只複製必要的程式碼，移除實驗性版本

**待做事項**：
1. 複製 `src/detector.py`
2. 複製 `src/color_filter.py`
3. **決定 OCR 引擎版本**：
   - 閱讀 `src/ocr_engine.py`, `src/ocr_engine_v2.py`
   - 選擇最佳版本（應該是包含改進的版本）
   - 重命名為 `ocr_engine.py`（如果選擇 v2）
4. 複製 `src/trainer.py`
5. 複製 `cli/detect.py`
6. 複製 `utils/dataset_splitter.py`

**驗收**：
- [ ] src/ 只包含 4 個 .py 檔案（+ __init__.py）
- [ ] cli/ 只包含 1 個 detect.py
- [ ] utils/ 只包含 1 個 dataset_splitter.py
- [ ] 無 ocr_engine_paddle.py

---

### 子任務 4：撰寫測試 - 準確度驗證（TDD）

**目標**：先寫準確度驗證測試，這是最重要的測試

**測試檔案**：`tests/test_accuracy.py`

**測試案例**：
1. `test_video1_accuracy()` - 驗證 Video1 準確度 ≥ 100%
2. `test_video2_accuracy()` - 驗證 Video2 準確度 ≥ 96.9%
3. `test_video3_accuracy()` - 驗證 Video3 準確度 ≥ 98.2%
4. `test_overall_accuracy()` - 驗證總體準確度 ≥ 98.4%

**測試邏輯**：
```python
def test_video1_accuracy():
    # 1. 從 video1.mp4 提取影格
    # 2. 對每個影格執行檢測
    # 3. 讀取對應的 manual_labels/video1/frame-*.json
    # 4. 對比 OCR 結果
    # 5. 計算成功率
    # 6. assert 成功率 >= 100.0
```

**執行**：`uv run pytest tests/test_accuracy.py -v -s`

**驗收**：
- [ ] 測試撰寫完成
- [ ] 測試執行（可能失敗，因為還沒確認 OCR 引擎版本）

---

### 子任務 5：複製核心測試

**目標**：複製核心單元測試

**待做事項**：
1. 複製 `tests/test_detector.py`
2. 複製 `tests/test_color_filter.py`
3. 複製 `tests/test_ocr_engine.py`
4. 複製 `tests/test_dataset_splitter.py`
5. 複製 `tests/fixtures/` 資料

**驗收**：
- [ ] tests/ 包含 5 個測試檔案（4 個核心 + 1 個準確度）
- [ ] fixtures/ 資料完整

---

### 子任務 6：精簡依賴配置

**目標**：移除不需要的依賴（PaddleOCR, autodistill）

**待做事項**：
1. 編輯 `pyproject.toml`
2. 移除 paddlepaddle, paddleocr 依賴
3. 移除 autodistill 依賴
4. 只保留核心依賴：opencv, ultralytics, pytesseract, numpy, Pillow
5. 執行 `uv sync` 重新安裝

**驗收**：
- [ ] pyproject.toml 精簡完成
- [ ] uv.lock 更新
- [ ] `make build` 成功

---

### 子任務 7：精簡 Makefile

**目標**：更新 Makefile，移除不需要的目標

**待做事項**：
1. 保留核心目標：help, build, detect, test, clean
2. 新增 `accuracy` 目標（執行準確度測試）
3. 更新 detect 目標（從 videos/ 提取影格）
4. 更新 clean 目標（清理 detections/, images/）

**驗收**：
- [ ] `make` 顯示正確的 help 訊息
- [ ] `make build` 成功
- [ ] `make accuracy` 可執行（即使失敗）

---

### 子任務 8：執行準確度測試並修正

**目標**：確保準確度測試通過

**待做事項**：
1. 執行 `make accuracy`
2. 檢查測試結果
3. 如果失敗，分析原因：
   - OCR 引擎版本不對？
   - 程式碼複製有誤？
   - 參數設定不對？
4. 修正問題
5. 重新執行直到所有測試通過

**驗收**：
- [ ] Video1 準確度 ≥ 100%
- [ ] Video2 準確度 ≥ 96.9%
- [ ] Video3 準確度 ≥ 98.2%
- [ ] 總體準確度 ≥ 98.4%

---

### 子任務 9：執行核心測試

**目標**：確保所有核心測試通過

**待做事項**：
1. 執行 `make test`
2. 檢查測試結果
3. 修正失敗的測試
4. 重新執行直到所有測試通過

**驗收**：
- [ ] 所有測試通過
- [ ] 測試覆蓋率 ≥ 80%

---

### 子任務 10：撰寫精簡版 README.md

**目標**：撰寫清晰簡潔的 README

**內容大綱**：
```markdown
# 價格標籤檢測系統

## 功能
- YOLO 物體檢測
- 雙色過濾
- OCR 文字識別

## 安裝
...

## 使用
...

## 準確度
- Video1: 100.0%
- Video2: 96.9%
- Video3: 98.2%
- 總體: 98.4%

## 測試
...
```

**驗收**：
- [ ] README.md 精簡清楚
- [ ] 包含核心使用說明

---

### 子任務 11：清理和驗證

**目標**：最後清理，確保專案整潔

**待做事項**：
1. 執行 `make clean`
2. 刪除所有 __pycache__ 和 .pyc
3. 檢查目錄大小：`du -sh .`（應該 ~1GB）
4. 執行最終測試：`make build && make test && make accuracy`
5. 驗證所有 Makefile 目標

**驗收**：
- [ ] 專案大小 ≤ 1.5GB
- [ ] 所有測試通過
- [ ] 準確度測試通過
- [ ] 專案目錄乾淨整潔

---

### 子任務 12：文件和交接

**目標**：完成文件，準備交接

**待做事項**：
1. 檢查 plan.md 是否需要更新
2. 確認所有驗收標準都已達成
3. 生成最終測試報告
4. 清理臨時檔案

**驗收**：
- [ ] 所有驗收標準達成
- [ ] 文件完整
- [ ] 專案可以直接使用

---

## 注意事項

1. **OCR 引擎版本選擇**：
   - 根據 COMPLETE_ANALYSIS_REPORT.md，改進版 Tesseract 達到 98.2%
   - 應該選擇包含動態放大、自適應 CLAHE、多策略組合的版本
   - 可能是 ocr_engine_v2.py

2. **準確度驗證最重要**：
   - 子任務 8（準確度測試）是最關鍵的驗收點
   - 如果準確度不達標，需要回頭檢查 OCR 引擎版本

3. **資料完整性**：
   - manual_labels 是準確度驗證的基準，必須完整複製
   - videos 用於重新生成影格，必須保留

4. **空間節省**：
   - 移除 images/, detections/, detections_v2/ 可節省 18GB
   - 影格可以隨時從 videos/ 重新生成

5. **測試驅動**：
   - 先寫準確度測試（子任務 4）
   - 確保測試通過後才算完成

---

## ⚠️ 停止條件

在以下情況下停止並報告：
- 完成一個子任務
- 準確度測試失敗（需分析原因）
- OCR 引擎版本選擇不確定（需討論）
- 測試未定義或失敗
- 發現 plan.md 不完整或需要補充

---

## 驗證檢查清單

每次完成子任務前，必須確認：

- [ ] 該子任務的所有待做事項已完成
- [ ] 該子任務的驗收條件已達成
- [ ] 如有測試，測試已執行並通過
- [ ] 無臨時檔案殘留
- [ ] plan.md 更新建議已提出（如需要）

最終驗收（子任務 11 完成後）：

- [ ] 專案大小 ≤ 1.5GB
- [ ] 準確度測試通過（≥ 98.4%）
- [ ] 所有核心測試通過
- [ ] Makefile 所有目標正常執行
- [ ] README.md 完整清晰
- [ ] 專案目錄乾淨整潔
