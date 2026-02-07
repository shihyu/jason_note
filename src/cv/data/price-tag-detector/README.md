# 價格標籤檢測系統

基於手動標註訓練的 YOLO 模型（mAP50 = 98.01%），結合顏色過濾和 OCR 文字識別的價格標籤檢測系統。

## ✨ 功能特色

- 🎯 **高準確度檢測**：YOLO 模型在獨立驗證集上達到 98.01% mAP50
- 🌈 **雙色過濾**：只保留同時包含黃色和綠色區域的價格標籤
- 🔤 **OCR 識別**：自動識別價格數字
- 🧪 **完整測試**：測試覆蓋率 ≥ 80%
- 🛠️ **易於使用**：標準化 Makefile 和 CLI 介面

## 📋 系統需求

- Python ≥ 3.11
- [uv](https://github.com/astral-sh/uv) - Python 套件管理器
- Tesseract OCR（用於文字識別）

### 安裝 Tesseract OCR

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# 驗證安裝
tesseract --version
```

## 🚀 快速開始

### 1. 安裝依賴

```bash
make build
```

### 2. 檢測價格標籤

```bash
make detect
```

### 3. 訓練模型（可選）

```bash
make train
```

### 4. 執行測試

```bash
make test
```

## 📁 專案結構

```
price-tag-detector/
├── src/                    # 核心程式碼
│   ├── detector.py         # YOLO 檢測引擎
│   ├── color_filter.py     # 顏色過濾模組
│   ├── ocr_engine.py       # OCR 識別引擎
│   ├── trainer.py          # 模型訓練器
│   └── config.py           # 配置管理
├── cli/                    # 命令列介面
│   ├── detect.py           # 檢測命令
│   └── train.py            # 訓練命令
├── utils/                  # 工具腳本
│   ├── dataset_splitter.py # 資料集分割器
│   └── visualizer.py       # 視覺化工具
├── tests/                  # 測試
├── data/                   # 資料目錄
│   ├── models/             # 訓練好的模型
│   ├── dataset/            # 訓練資料集
│   ├── images/             # 待檢測的影格
│   └── detections/         # 檢測結果輸出
└── Makefile                # 建置工具
```

## 🎯 使用方法

### 檢測價格標籤

```bash
# 使用預設設定
make detect

# 或手動指定參數
uv run cli/detect.py --input data/images/video1 --output data/detections/video1
```

### 訓練模型

```bash
# 使用預設設定
make train

# 或手動指定參數
uv run cli/train.py --data data/dataset/data.yaml --epochs 50 --batch 8
```

### 資料集分割

```bash
uv run python -m utils.dataset_splitter --input data/raw --output data/dataset --ratio 0.8
```

## 📊 模型效能

| 指標 | 數值 |
|------|------|
| mAP50 | 98.01% |
| Precision | 90.27% |
| Recall | 100.00% |
| mAP50-95 | 63.55% |

*評估於獨立驗證集（10 張圖片，21 個價格標籤）*

## 🧪 測試

```bash
# 執行所有測試
make test

# 執行特定測試
uv run pytest tests/test_detector.py -v

# 生成測試覆蓋率報告
uv run pytest tests/ --cov=src --cov-report=html
```

## 🛠️ Makefile 目標

```bash
make help       # 顯示說明
make build      # 安裝依賴
make train      # 訓練模型
make detect     # 執行檢測
make test       # 執行測試
make clean      # 清理產物
```

## 📝 API 文檔

### Detector

```python
from src.detector import Detector

# 初始化檢測器
detector = Detector(model_path="data/models/best.pt", conf_threshold=0.05)

# 檢測單張圖片
detections = detector.detect("data/images/frame-00000.jpg")

# 批次檢測
results = detector.detect_batch(["img1.jpg", "img2.jpg"])
```

### ColorFilter

```python
from src.color_filter import ColorFilter

# 初始化顏色過濾器
color_filter = ColorFilter()

# 檢查是否包含雙色
has_both = color_filter.has_both_colors(image, bbox)

# 提取顏色區域
regions = color_filter.extract_color_regions(image, bbox)
```

### OCREngine

```python
from src.ocr_engine import OCREngine

# 初始化 OCR 引擎
ocr = OCREngine(lang='eng')

# 識別文字
result = ocr.recognize(image)
print(f"Text: {result.text}, Confidence: {result.confidence}")
```

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License

## 🙏 致謝

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [OpenCV](https://opencv.org/)
