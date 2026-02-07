# 專案計畫：價格標籤檢測系統（乾淨重構版）

## 任務目標

基於手動標註訓練的 YOLO 模型（mAP50 = 98.01%），建立一個**乾淨、可維護、完整測試**的價格標籤檢測系統。

核心功能：
1. **YOLO 物體檢測**：檢測影片影格中的價格標籤
2. **雙色過濾**：只保留同時包含黃色和綠色區域的檢測框
3. **OCR 文字識別**：識別黃色和綠色區域內的價格數字
4. **模型訓練**：支援資料集分割、訓練、驗證
5. **完整測試**：所有功能都有對應的測試

## 專案結構組織

專案根目錄：`/home/shihyu/price-tag-detector`

```
price-tag-detector/
├── plan.md                     # 本檔案
├── README.md                   # 專案說明和使用教學
├── Makefile                    # 標準化建置流程
├── pyproject.toml              # 依賴管理（只保留必要的）
├── uv.lock                     # 鎖定版本
│
├── src/                        # 核心程式碼（重構後）
│   ├── __init__.py
│   ├── detector.py             # YOLO 檢測引擎（重構）
│   ├── color_filter.py         # 顏色過濾模組（重構）
│   ├── ocr_engine.py           # OCR 識別引擎（重構）
│   ├── trainer.py              # 模型訓練器（重構）
│   └── config.py               # 配置管理
│
├── cli/                        # 命令列介面
│   ├── __init__.py
│   ├── detect.py               # 檢測命令
│   └── train.py                # 訓練命令
│
├── utils/                      # 工具腳本
│   ├── __init__.py
│   ├── dataset_splitter.py     # 資料集分割器（重構）
│   └── visualizer.py           # 視覺化工具
│
├── tests/                      # 測試（TDD）
│   ├── __init__.py
│   ├── test_detector.py        # 檢測器測試
│   ├── test_color_filter.py   # 顏色過濾測試
│   ├── test_ocr_engine.py      # OCR 測試
│   ├── test_trainer.py         # 訓練器測試
│   ├── test_dataset_splitter.py # 資料集分割測試
│   └── fixtures/               # 測試用固定資料
│       └── sample_images/
│
├── data/                       # 資料目錄
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
│   ├── images/                 # 待檢測的影格
│   │   └── video1/
│   └── detections/             # 檢測結果輸出
│       └── video1/
│
└── .gitignore                  # Git 忽略規則
```

## 預期產出

### 1. 重構後的核心模組

#### `src/detector.py` - YOLO 檢測引擎
```python
class Detector:
    """YOLO 物體檢測器"""
    def __init__(self, model_path: str, conf_threshold: float = 0.05)
    def detect(self, image_path: str) -> List[Detection]
    def detect_batch(self, image_paths: List[str]) -> Dict[str, List[Detection]]
```

#### `src/color_filter.py` - 顏色過濾模組
```python
class ColorFilter:
    """雙色區域檢測器"""
    def __init__(self, yellow_range: tuple, green_range: tuple)
    def has_both_colors(self, image: np.ndarray, bbox: tuple) -> bool
    def extract_color_regions(self, image: np.ndarray, bbox: tuple) -> dict
```

#### `src/ocr_engine.py` - OCR 識別引擎
```python
class OCREngine:
    """文字識別引擎"""
    def __init__(self, lang: str = 'eng')
    def recognize(self, image: np.ndarray) -> OCRResult
    def batch_recognize(self, images: List[np.ndarray]) -> List[OCRResult]
```

#### `src/trainer.py` - 模型訓練器
```python
class Trainer:
    """YOLO 模型訓練器"""
    def __init__(self, data_yaml: str, base_model: str = 'yolov8n.pt')
    def train(self, epochs: int, batch_size: int) -> TrainingResult
    def validate(self) -> ValidationMetrics
```

### 2. 命令列介面

```bash
# 檢測影片影格
uv run cli/detect.py --input data/images/video1 --output data/detections/video1

# 訓練模型
uv run cli/train.py --data data/dataset/data.yaml --epochs 50 --batch 8
```

### 3. 完整測試套件

- 單元測試：每個模組都有對應的測試
- 整合測試：測試模組之間的協作
- 端到端測試：測試完整的檢測流程
- 測試覆蓋率：目標 ≥ 80%

### 4. 文檔

- README.md：專案介紹、安裝、使用教學
- API 文檔：每個類別和函數都有 docstring
- 使用範例：實際的使用案例

## Makefile 規範

### 必備目標

```makefile
.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build     - 安裝依賴"
	@echo "  make train     - 訓練模型"
	@echo "  make detect    - 執行檢測"
	@echo "  make test      - 執行測試"
	@echo "  make clean     - 清理產物"
	@echo ""
	@echo "使用範例："
	@echo "  make build && make train"
	@echo "  make detect"

.PHONY: build
build:  ## 安裝依賴
	uv sync

.PHONY: train
train:  ## 訓練模型
	uv run cli/train.py

.PHONY: detect
detect:  ## 執行檢測
	uv run cli/detect.py

.PHONY: test
test:  ## 執行測試
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

.PHONY: clean
clean:  ## 清理建置產物和臨時檔案
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov
	rm -rf data/detections/*
```

## build/debug/test 指令

### Build
```bash
make build          # 安裝依賴
```

### Run
```bash
# 檢測
make detect

# 或手動指定參數
uv run cli/detect.py --input data/images/video1 --output data/detections/video1

# 訓練
make train

# 或手動指定參數
uv run cli/train.py --data data/dataset/data.yaml --epochs 50
```

### Debug
```bash
# 測試單個模組
uv run pytest tests/test_detector.py -v -s

# 測試時顯示 print 輸出
uv run pytest tests/ -v -s

# 測試覆蓋率報告
uv run pytest tests/ --cov=src --cov-report=html
```

### Test
```bash
make test           # 執行所有測試
```

## 驗收標準

- [ ] 所有模組都已重構，符合單一職責原則
- [ ] 所有函數都有 type hints 和 docstring
- [ ] 測試覆蓋率 ≥ 80%
- [ ] 所有測試通過
- [ ] 檢測功能正常（mAP50 ≥ 98%）
- [ ] OCR 功能正常（雙色區域識別率 ≥ 90%）
- [ ] Makefile 所有目標都能正常執行
- [ ] README.md 包含完整的使用說明
- [ ] 無 autodistill 依賴
- [ ] 程式碼乾淨，無冗餘或註釋掉的程式碼

## 子任務拆解

### 子任務 1：專案初始化

**目標**：建立專案基礎結構和依賴管理

**待做事項**：
1. 創建目錄結構
2. 建立 `pyproject.toml`（只保留必要依賴）
3. 建立 `.gitignore`
4. 建立 `README.md` 框架
5. 建立 Makefile
6. 執行 `make build` 驗證依賴安裝

**驗收**：
- [ ] 目錄結構正確
- [ ] `make build` 成功
- [ ] 所有必要依賴已安裝

---

### 子任務 2：撰寫測試 - 資料集分割器（TDD）

**目標**：先寫測試，定義資料集分割器的預期行為

**測試檔案**：`tests/test_dataset_splitter.py`

**測試案例**：
1. `test_split_ratio()` - 驗證 train/valid 分割比例
2. `test_no_overlap()` - 驗證沒有重疊
3. `test_labels_exist()` - 驗證標籤檔案存在
4. `test_random_seed()` - 驗證使用固定 seed 結果可重現

**執行**：`uv run pytest tests/test_dataset_splitter.py -v`

**驗收**：
- [ ] 測試撰寫完成
- [ ] 測試執行失敗（因為還沒寫實作）

---

### 子任務 3：實作資料集分割器

**目標**：實作 `utils/dataset_splitter.py`，通過所有測試

**待做事項**：
1. 實作 `DatasetSplitter` 類別
2. 實作 `split()` 方法
3. 執行測試：`uv run pytest tests/test_dataset_splitter.py -v`
4. 修改程式碼直到所有測試通過

**驗收**：
- [ ] 所有測試通過
- [ ] 程式碼有 type hints 和 docstring

---

### 子任務 4：撰寫測試 - 顏色過濾器（TDD）

**目標**：先寫測試，定義顏色過濾器的預期行為

**測試檔案**：`tests/test_color_filter.py`

**測試案例**：
1. `test_has_yellow()` - 驗證黃色檢測
2. `test_has_green()` - 驗證綠色檢測
3. `test_has_both_colors()` - 驗證雙色檢測
4. `test_extract_regions()` - 驗證區域提取

**驗收**：
- [ ] 測試撰寫完成
- [ ] 測試執行失敗（因為還沒寫實作）

---

### 子任務 5：實作顏色過濾器

**目標**：實作 `src/color_filter.py`，通過所有測試

**待做事項**：
1. 實作 `ColorFilter` 類別
2. 實作 `has_both_colors()`, `extract_color_regions()` 方法
3. 執行測試並修改直到通過

**驗收**：
- [ ] 所有測試通過
- [ ] 程式碼重構乾淨，移除冗餘

---

### 子任務 6：撰寫測試 - OCR 引擎（TDD）

**目標**：先寫測試，定義 OCR 引擎的預期行為

**測試檔案**：`tests/test_ocr_engine.py`

**測試案例**：
1. `test_recognize_digits()` - 驗證數字識別
2. `test_confidence_score()` - 驗證置信度分數
3. `test_empty_image()` - 驗證空白圖片處理
4. `test_batch_recognize()` - 驗證批次識別

**驗收**：
- [ ] 測試撰寫完成
- [ ] 測試執行失敗

---

### 子任務 7：實作 OCR 引擎

**目標**：實作 `src/ocr_engine.py`，通過所有測試

**待做事項**：
1. 實作 `OCREngine` 類別
2. 實作 `recognize()`, `batch_recognize()` 方法
3. 加入影像預處理（提高 OCR 準確率）
4. 執行測試並修改直到通過

**驗收**：
- [ ] 所有測試通過
- [ ] OCR 準確率 ≥ 90%

---

### 子任務 8：撰寫測試 - YOLO 檢測器（TDD）

**目標**：先寫測試，定義 YOLO 檢測器的預期行為

**測試檔案**：`tests/test_detector.py`

**測試案例**：
1. `test_model_loading()` - 驗證模型載入
2. `test_detect_single_image()` - 驗證單張圖片檢測
3. `test_detect_batch()` - 驗證批次檢測
4. `test_detection_accuracy()` - 驗證檢測準確率

**驗收**：
- [ ] 測試撰寫完成
- [ ] 測試執行失敗

---

### 子任務 9：實作 YOLO 檢測器

**目標**：實作 `src/detector.py`，通過所有測試

**待做事項**：
1. 實作 `Detector` 類別
2. 實作 `detect()`, `detect_batch()` 方法
3. 整合 ColorFilter 和 OCREngine
4. 執行測試並修改直到通過

**驗收**：
- [ ] 所有測試通過
- [ ] 檢測準確率 mAP50 ≥ 98%

---

### 子任務 10：實作命令列介面

**目標**：建立易用的 CLI 介面

**待做事項**：
1. 實作 `cli/detect.py`（檢測命令）
2. 實作 `cli/train.py`（訓練命令）
3. 加入參數解析（argparse 或 click）
4. 加入進度條（tqdm）

**驗收**：
- [ ] `make detect` 成功執行
- [ ] `make train` 成功執行
- [ ] CLI 介面友善，有清楚的輸出

---

### 子任務 11：端到端測試

**目標**：測試完整的檢測流程

**測試檔案**：`tests/test_e2e.py`

**測試案例**：
1. `test_full_detection_pipeline()` - 測試完整流程
2. `test_output_format()` - 驗證輸出格式
3. `test_statistics_report()` - 驗證統計報告

**執行**：`make test`

**驗收**：
- [ ] 所有測試通過
- [ ] 測試覆蓋率 ≥ 80%

---

### 子任務 12：撰寫文檔和清理

**目標**：完成文檔，清理臨時檔案

**待做事項**：
1. 完成 README.md（安裝、使用、API 說明）
2. 檢查所有函數都有 docstring
3. 清理臨時檔案和測試產物
4. 執行 `make clean`
5. 最終測試：`make build && make test && make detect`

**驗收**：
- [ ] README.md 完整清楚
- [ ] 專案目錄乾淨整潔
- [ ] 所有 Makefile 目標都能正常執行
- [ ] 最終測試全部通過

---

## 注意事項

1. **程式碼品質**：
   - 所有函數都要有 type hints
   - 所有類別和函數都要有 docstring
   - 遵循 PEP 8 規範
   - 變數命名清楚有意義

2. **測試驅動開發**：
   - 先寫測試，再寫實作
   - 測試失敗時，不要跳過，先修正
   - 每個子任務完成後立即測試

3. **依賴管理**：
   - 只安裝必要的套件
   - 移除所有 autodistill 相關依賴
   - 使用 uv 管理依賴

4. **Git 工作流**：
   - 每個子任務完成後 commit
   - Commit message 要清楚描述變更

5. **效能考量**：
   - 批次處理提高效率
   - 使用進度條顯示處理進度

---

## ⚠️ 停止條件

在以下情況下停止並報告：
- 完成一個子任務
- 測試失敗（先報告原因，不要自行修改）
- 發現 plan.md 不完整或需要補充
- 模型準確率低於預期（需討論優化策略）
