# 專案計畫：整合顏色檢測與 OCR 功能到 detect-all

## 任務目標

修改 `detect_all.py`，整合 `color_ocr.py` 模組，實現：
1. 檢測框內同時包含黃色和綠色區域的過濾
2. OCR 識別黃色和綠色區域內的文字（目標準確率 ≥ 90%）
3. 在輸出圖片上標註 OCR 結果

## 專案結構組織

專案根目錄：`/home/shihyu/github/autodistill/autodistill-video-project`

```
autodistill-video-project/
├── detect_all.py          # 【待修改】整合 OCR 功能
├── color_ocr.py           # 【已存在】顏色檢測 + OCR 模組
├── tests/                 # 【新建】測試檔案目錄
│   ├── test_detect_all.py     # detect_all.py 的整合測試
│   └── output/                # 測試輸出（圖片、log）
├── data/
│   ├── images/                # 輸入影格
│   └── detections/            # 輸出帶標註的圖片
└── Makefile               # 【已存在】包含 detect-all 目標
```

## 預期產出

### 1. 修改後的 `detect_all.py`
- 整合 `color_ocr.py` 模組
- 新增顏色過濾邏輯（只處理雙色檢測框）
- 新增 OCR 結果標註功能
- 新增統計報告（OCR 成功率、平均置信度）

### 2. 測試檔案 `tests/test_detect_all.py`
- 測試顏色檢測功能
- 測試 OCR 識別準確率
- 驗證輸出圖片格式

### 3. 輸出檔案
- `data/detections/videoX/frame-XXXXX.jpg`：帶有 OCR 標註的圖片
- 終端輸出：OCR 統計報告（成功率、置信度）

## Makefile 規範

已存在的 `detect-all` 目標（無需修改）：
```makefile
.PHONY: detect-all
detect-all:
	@echo "使用訓練好的模型檢測所有影格..."
	uv run detect_all.py
	@echo "✓ 檢測完成，結果已保存到 data/detections/"
```

其他必備目標（已存在）：
- `make` (無參數)：顯示可用目標和使用範例
- `make build`：安裝依賴（`uv sync`）
- `make test`：執行測試（`uv run pytest tests/`）
- `make clean`：清理建置產物

## build/debug/test 指令

### Build
```bash
make build          # 安裝依賴
```

### Run
```bash
make detect-all     # 執行整合後的檢測+OCR
```

### Debug
```bash
# 單獨測試 color_ocr 模組
uv run test_color_ocr.py

# 檢視輸出圖片
eog data/detections/video1/frame-00000.jpg
```

### Test
```bash
make test           # 執行所有測試
```

## 驗收標準

- [ ] `detect_all.py` 成功整合 `color_ocr.py`
- [ ] 只處理同時包含黃色和綠色的檢測框
- [ ] OCR 識別準確率 ≥ 90%（基於測試集）
- [ ] 輸出圖片正確標註黃色和綠色區域的文字
- [ ] 終端顯示完整的 OCR 統計報告
- [ ] 所有測試通過

## 子任務拆解

### 子任務 1：修改 detect_all.py（整合 color_ocr）
**目標**：將 `color_ocr.py` 的功能整合到 `detect_all.py`

**待做事項**：
1. 匯入 `color_ocr` 模組：
   - `process_detection_with_ocr()`
   - `annotate_ocr_results()`
   - `OCRStatistics()`

2. 修改主迴圈：
   ```python
   for img_path in images:
       results = model.predict(img_path)
       image = cv2.imread(img_path)

       for bbox in results[0].boxes:
           # 【新增】顏色檢測 + OCR
           ocr_result = process_detection_with_ocr(image, bbox.xyxy[0], bbox.cls)

           # 【新增】只處理雙色檢測框
           if not ocr_result['has_both_colors']:
               continue

           # 【新增】標註 OCR 結果
           annotate_ocr_results(image, bbox.xyxy[0], ocr_result)

           # 【新增】更新統計
           stats.update(ocr_result)

       # 保存標註後的圖片
       cv2.imwrite(output_path, image)

   # 【新增】顯示統計報告
   print(stats.report())
   ```

3. 確保輸出目錄結構：
   - `data/detections/video1/` 等

**驗收**：
- 執行 `make detect-all` 成功
- 終端顯示 OCR 統計報告
- 輸出圖片包含 OCR 標註

---

### 子任務 2：撰寫測試（TDD）
**目標**：驗證整合功能的正確性

**測試檔案**：`tests/test_detect_all.py`

**測試案例**：
1. `test_dual_color_detection()`：
   - 驗證只處理雙色檢測框
   - 預期：單色檢測框被過濾

2. `test_ocr_accuracy()`：
   - 在測試集上運行 OCR
   - 預期：準確率 ≥ 90%

3. `test_output_format()`：
   - 檢查輸出圖片是否存在
   - 檢查圖片是否包含標註

**執行**：
```bash
make test
```

**驗收**：
- 所有測試通過
- OCR 準確率 ≥ 90%

---

### 子任務 3：清理臨時檔案
**目標**：測試完成後，清理不必要的檔案

**待做事項**：
1. 刪除 `tests/output/` 下的臨時圖片（如果有）
2. 確保只保留：
   - 程式碼檔案
   - 測試檔案
   - `data/detections/` 下的最終輸出

**驗收**：
- 專案目錄乾淨整潔
- 無多餘的 tmp/debug 檔案

---

## 注意事項

1. **OCR 準確率優化**：
   - 使用 `color_ocr.py` 中的 `preprocess_for_ocr()` 函數
   - 針對黃色和綠色使用不同的預處理策略

2. **依賴**：
   - 確保 `pytesseract` 已安裝（已在 `pyproject.toml` 中）
   - 確保系統安裝了 Tesseract OCR（`sudo apt install tesseract-ocr`）

3. **性能考量**：
   - OCR 會增加處理時間（預計 2-3 倍）
   - 可考慮加入進度條（已有 `tqdm`）

---

## ⚠️ 停止條件

在以下情況下停止並報告：
- 完成一個子任務
- 發現 plan.md 不完整或需要補充
- 測試失敗（先報告原因，不要自行修改）
- OCR 準確率低於 90%（需討論優化策略）
