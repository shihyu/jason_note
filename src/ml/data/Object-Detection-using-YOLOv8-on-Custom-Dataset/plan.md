# YOLOv8 Guitar Object Detection 專案計劃

## 任務目標
使用 YOLOv8 模型在自訂吉他資料集上進行物件偵測訓練,並建立可重現的訓練與驗證流程。

## 預期產出

### 檔案結構
```
.
├── plan.md                    # 本計劃文件
├── Makefile                   # 標準化建置與訓練流程
├── train.py                   # 訓練腳本
├── validate.py                # 驗證腳本
├── inference.py               # 推論測試腳本
├── visualize_comparison.py    # 視覺化比對腳本
├── guitar_dataset.yaml        # YOLOv8 資料集配置
├── requirements.txt           # Python 依賴清單
├── Dataset/
│   └── Guitar_dataset/
│       ├── train/
│       │   ├── images/       # 280 張訓練圖片
│       │   └── labels/       # YOLO 格式標註
│       └── val/
│           ├── images/       # 20 張驗證圖片
│           └── labels/       # YOLO 格式標註
├── runs/                      # 訓練輸出目錄 (自動生成)
│   └── detect/
│       └── train_*/
│           ├── weights/
│           │   ├── best.pt
│           │   └── last.pt
│           └── results.png
└── tests/                     # 測試相關檔案
    ├── baseline_metrics.json  # 基準指標記錄
    ├── inference_results/     # 推論結果圖片
    └── comparison_report.html # 視覺化比對報告
```

## 資料集資訊
- **類別數量**: 1 (Guitar)
- **訓練集**: 280 張圖片 (248 張含吉他 + 32 張背景)
- **驗證集**: 20 張圖片
- **標註格式**: YOLO (x_center_norm, y_center_norm, width_norm, height_norm)
- **圖片大小**: 640x640 (訓練時調整)

## 訓練參數
- **模型**: yolov8n.pt (預訓練權重)
- **Epochs**: 300
- **Batch Size**: 16
- **Image Size**: 640x640
- **Augmentation**: True (YOLOv8 內建)
- **Confidence Threshold**: 0.6 (推論時)

## 基準指標 (Baseline Metrics)
根據原始 Notebook 訓練結果:
- **Precision (Box)**: ~0.982
- **Recall (Box)**: ~1.0
- **mAP50**: ~0.995
- **mAP50-95**: ~0.874

## Makefile 規範

### 必備目標
- `make` (無參數): 顯示可用目標和使用範例
- `make setup`: 安裝依賴並檢查環境
- `make train`: 執行完整訓練流程
- `make validate`: 驗證訓練模型並比對基準指標
- `make inference`: 執行推論測試 (在驗證集上預測)
- `make visualize`: 生成視覺化比對報告 (訓練曲線、混淆矩陣、預測結果對比)
- `make test`: 執行測試 (驗證資料集完整性)
- `make clean`: 清理訓練產物和臨時檔案
- `make clean-all`: 完全清理 (包含下載的模型)

### 指令範例
```bash
# 完整流程
make setup      # 首次使用需執行
make train      # 訓練模型
make validate   # 驗證結果
make inference  # 推論測試
make visualize  # 生成視覺化報告

# 一鍵完整流程
make setup && make train && make validate && make inference && make visualize

# 重新訓練
make clean && make train

# 清理所有產物
make clean-all
```

## 驗收標準

### 功能性驗收
- [x] 資料集結構完整 (train/val 資料夾含 images 與 labels)
- [ ] Python 環境依賴正確安裝
- [ ] 訓練腳本可執行並完成 300 epochs
- [ ] 生成模型權重檔案 (best.pt, last.pt)
- [ ] 驗證腳本可載入訓練模型並輸出指標
- [ ] 推論腳本可在驗證集上執行預測
- [ ] 視覺化比對報告包含: 訓練曲線、混淆矩陣、預測圖片範例 (至少 10 張)

### 指標驗收 (容許 ±5% 誤差)
- [ ] Precision ≥ 0.93 (0.982 * 0.95)
- [ ] Recall ≥ 0.95 (1.0 * 0.95)
- [ ] mAP50 ≥ 0.945 (0.995 * 0.95)
- [ ] mAP50-95 ≥ 0.83 (0.874 * 0.95)

### Makefile 驗收
- [ ] `make` 無參數時顯示 help
- [ ] 所有目標可獨立執行
- [ ] `make clean` 清理訓練產物但保留程式碼
- [ ] `make clean-all` 完全清理

## 子任務拆解

### Phase 1: 環境設定
1. 建立 `requirements.txt` 定義依賴
2. 建立 `guitar_dataset.yaml` 配置資料集路徑
3. 實作 Makefile 的 `setup` 目標

### Phase 2: 訓練流程
4. 實作 `train.py` 腳本 (基於 Notebook cell 19)
5. 實作 Makefile 的 `train` 目標
6. 驗證訓練可完整執行並生成模型

### Phase 3: 驗證流程
7. 實作 `validate.py` 腳本 (基於 Notebook cell 21)
8. 儲存基準指標到 `tests/baseline_metrics.json`
9. 實作指標比對邏輯 (±5% 容忍度)
10. 實作 Makefile 的 `validate` 目標

### Phase 4: 推論與視覺化
11. 實作 `inference.py` 腳本 (基於 Notebook cell 28)
12. 實作 `visualize_comparison.py` 生成比對報告
13. 實作 Makefile 的 `inference` 和 `visualize` 目標

### Phase 5: 清理與測試
14. 實作 Makefile 的 `clean` 和 `clean-all` 目標
15. 實作 `test` 目標驗證資料集完整性
16. 整合測試所有流程

## 技術細節

### YOLOv8 訓練指令
```bash
yolo task=detect \
     mode=train \
     model=yolov8n.pt \
     imgsz=640 \
     data=guitar_dataset.yaml \
     epochs=300 \
     batch=16 \
     augment=True \
     name=guitar_train
```

### YOLOv8 驗證指令
```bash
yolo task=detect \
     mode=val \
     model=runs/detect/guitar_train/weights/best.pt \
     data=guitar_dataset.yaml \
     name=guitar_val
```

### YOLOv8 推論指令
```bash
yolo task=detect \
     mode=predict \
     model=runs/detect/guitar_train/weights/best.pt \
     source=Dataset/Guitar_dataset/val/images \
     imgsz=640 \
     conf=0.6 \
     name=guitar_inference
```

### 指標擷取方式
- 從訓練輸出的 `results.csv` 或終端輸出解析指標
- 使用 Python 腳本解析並比對

### 視覺化報告內容
1. **訓練曲線比對**:
   - Loss 曲線 (Box loss, Object loss, Class loss)
   - Precision/Recall 曲線
   - mAP 曲線

2. **混淆矩陣比對**:
   - 歸一化混淆矩陣
   - PR 曲線

3. **預測結果比對**:
   - 並排顯示 Ground Truth 與 Prediction
   - 至少 10 張驗證集圖片
   - 顯示信心分數與 IoU

4. **指標總結表格**:
   - 基準指標 vs 新訓練指標
   - 差異百分比
   - 通過/失敗狀態

## 注意事項

1. **路徑處理**: 使用絕對路徑或相對於專案根目錄的路徑
2. **GPU 支援**: 自動偵測 CUDA,無 GPU 則使用 CPU (訓練會較慢)
3. **磁碟空間**: 訓練過程約需 500MB 空間存放權重與日誌
4. **時間估計**:
   - GPU (Tesla T4): ~2-3 小時
   - CPU: ~10-15 小時
5. **隨機性**: 由於訓練隨機性,指標可能有小幅波動 (故設 ±5% 容忍)

## 更新記錄
- 2025-11-10: 初始版本建立
- 2025-11-10: 新增推論測試與視覺化比對需求
