# YOLOv8 Guitar Detection - 使用指南

這是一個基於 YOLOv8 的吉他物件偵測專案，提供完整的訓練、驗證、推論與視覺化流程。

## 快速開始

### 1. 環境設定

首次使用需要安裝依賴套件:

```bash
make setup
```

這會自動:
- 檢查 Python 版本
- 安裝所有必要的套件 (ultralytics, opencv-python, torch 等)
- 驗證資料集完整性

### 2. 訓練模型

執行完整的訓練流程 (300 epochs):

```bash
make train
```

訓練參數:
- 模型: yolov8n.pt (預訓練模型)
- Epochs: 300
- Batch Size: 16
- Image Size: 640x640
- Augmentation: 啟用

訓練產物會儲存在 `runs/detect/guitar_train/`

### 3. 驗證模型

訓練完成後，驗證模型並比對基準指標:

```bash
make validate
```

這會:
- 載入訓練好的模型 (`runs/detect/guitar_train/weights/best.pt`)
- 在驗證集上評估指標
- 與基準指標比對 (容許 ±5% 誤差)
- 輸出比較結果

### 4. 推論測試

在驗證集上執行推論:

```bash
make inference
```

這會:
- 使用訓練好的模型預測所有驗證圖片
- 將預測結果儲存到 `tests/inference_results/`
- 顯示偵測統計資訊

### 5. 視覺化報告

生成包含所有結果的 HTML 報告:

```bash
make visualize
```

報告包含:
- 訓練曲線 (Loss, Precision, Recall, mAP)
- 混淆矩陣與 PR 曲線
- 預測結果範例 (並排顯示)
- 指標比對表格

查看報告:
```bash
xdg-open tests/comparison_report.html
# 或
firefox tests/comparison_report.html
```

## 完整流程

一鍵執行所有步驟:

```bash
make setup && make train && make validate && make inference && make visualize
```

或使用快捷指令:

```bash
make all
```

## 其他指令

### 檢查資料集

```bash
make test
```

顯示資料集統計資訊並驗證結構完整性。

### 清理產物

清理訓練產物但保留程式碼和基準指標:

```bash
make clean
```

完全清理 (包含基準指標和下載的模型):

```bash
make clean-all
```

### 重新訓練

```bash
make clean && make train
```

## 專案結構

```
.
├── Makefile                     # 建置流程
├── plan.md                      # 專案計劃
├── USAGE.md                     # 本文件
├── requirements.txt             # Python 依賴
├── guitar_dataset.yaml          # 資料集配置
├── train.py                     # 訓練腳本
├── validate.py                  # 驗證腳本
├── inference.py                 # 推論腳本
├── visualize_comparison.py      # 視覺化腳本
├── Dataset/
│   └── Guitar_dataset/          # 資料集 (280 訓練 + 20 驗證)
├── runs/
│   └── detect/
│       └── guitar_train/        # 訓練產物
└── tests/
    ├── baseline_metrics.json    # 基準指標
    ├── current_metrics.json     # 當前指標
    ├── inference_results/       # 推論結果
    └── comparison_report.html   # 視覺化報告
```

## 基準指標

原始 Notebook 訓練結果 (作為基準):

| 指標 | 值 |
|------|-----|
| Precision | 0.982 |
| Recall | 1.0 |
| mAP50 | 0.995 |
| mAP50-95 | 0.874 |

新訓練結果需在 ±5% 範圍內才算通過驗證。

## 常見問題

### Q: 訓練需要多久?

A:
- GPU (Tesla T4): 約 2-3 小時
- CPU: 約 10-15 小時

### Q: 需要多少磁碟空間?

A: 約 500MB (包含模型權重、訓練日誌、推論結果)

### Q: 如何只看幫助訊息?

A:
```bash
make
# 或
make help
```

### Q: 訓練指標與基準差異較大怎麼辦?

A: 由於訓練有隨機性，指標可能有波動。若差異超過 ±5%:
1. 檢查資料集是否完整
2. 確認訓練完成 300 epochs
3. 可以重新訓練 2-3 次取最佳結果

### Q: 如何查看詳細的訓練日誌?

A: 訓練日誌儲存在:
```
runs/detect/guitar_train/results.csv
runs/detect/guitar_train/results.png
```

## 技術細節

### YOLOv8 訓練指令 (train.py 內部執行)

```python
model.train(
    data='guitar_dataset.yaml',
    epochs=300,
    batch=16,
    imgsz=640,
    augment=True,
    project='runs/detect',
    name='guitar_train'
)
```

### YOLOv8 驗證指令 (validate.py 內部執行)

```python
model.val(
    data='guitar_dataset.yaml',
    batch=16,
    imgsz=640
)
```

### YOLOv8 推論指令 (inference.py 內部執行)

```python
model.predict(
    source='Dataset/Guitar_dataset/val/images',
    imgsz=640,
    conf=0.6,
    save=True
)
```

## 授權

本專案基於原始的 YOLOv8 Guitar Detection Jupyter Notebook 改寫。

## 聯絡資訊

如有問題或建議，請提交 issue。
