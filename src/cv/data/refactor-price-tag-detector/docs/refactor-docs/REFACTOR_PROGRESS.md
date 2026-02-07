# 重構進度報告

**日期**: 2026-02-07
**專案**: price-tag-detector 重構
**目標**: 從 29GB 縮減到 ~1GB，保持 98.4% 準確度

---

## ✅ 已完成的子任務 (1-7)

### 子任務 1: 建立新專案結構 ✓
- ✅ 目錄結構已建立：src/, cli/, utils/, tests/, data/
- ✅ __init__.py 檔案已建立
- ✅ .gitignore, Makefile, pyproject.toml 已複製

### 子任務 2: 複製關鍵資料 ✓
- ✅ `data/videos/` (655MB) - 3 個 .mp4 檔案
- ✅ `data/manual_labels/` (353MB) - 3 個子目錄（video1/video2/video3）
- ✅ `data/dataset/` (22MB) - train/, valid/, data.yaml
- ✅ `data/models/` (6MB) - best.pt

### 子任務 3: 複製核心程式碼 ✓
- ✅ `src/detector.py` (3.2K)
- ✅ `src/color_filter.py` (4.2K)
- ✅ `src/ocr_engine.py` (14K) - **重要**: 使用改進版 OCR (來自 ocr_engine_v2.py)
- ✅ `src/trainer.py` (4.1K)
- ✅ `cli/detect.py` (6.9K)
- ✅ `utils/dataset_splitter.py` (5.7K)
- ❌ 移除: ocr_engine_paddle.py（PaddleOCR，0% 成功率）

### 子任務 4: 撰寫準確度驗證測試 ✓
- ✅ `tests/test_accuracy.py` (11K) 已建立
- ✅ 測試邏輯：
  - 解析 manual_labels（按 x 座標排序：左=黃色，右=綠色）
  - 使用 PriceTagOCR.recognize_yellow/recognize_green
  - 4 個測試案例：video1, video2, video3, overall
- ✅ 驗收標準：
  - Video1: ≥ 100.0%
  - Video2: ≥ 96.9%
  - Video3: ≥ 98.2%
  - 總體: ≥ 98.4%

### 子任務 5: 複製核心測試 ✓
- ✅ `tests/test_detector.py` (2.2K)
- ✅ `tests/test_color_filter.py` (3.7K)
- ✅ `tests/test_ocr_engine.py` (3.4K)
- ✅ `tests/test_dataset_splitter.py` (6.0K)
- ✅ `tests/fixtures/sample_images/`

### 子任務 6: 精簡依賴配置 ✓
- ✅ 移除 `paddlepaddle>=3.3.0`
- ✅ 移除 `paddleocr>=3.4.0`
- ✅ `uv sync` 成功（安裝 55 個套件）
- ✅ `README.md` 已建立

### 子任務 7: 精簡 Makefile ✓
- ✅ 保留核心目標：help, build, detect, test, clean
- ✅ 新增 `make accuracy` 目標（準確度驗證）
- ❌ 移除：extract, prepare, train, rebuild
- ✅ `make` 顯示正確的 help 訊息

---

## ❌ 遇到問題的子任務

### 子任務 8: 執行準確度測試並修正

#### 問題描述
執行 `make accuracy` 或 `uv run pytest tests/test_accuracy.py` 時出錯：

```
ModuleNotFoundError: No module named 'ultralytics.nn.modules.conv';
'ultralytics.nn.modules' is not a package
```

#### 根本原因
1. `data/models/best.pt` 是用**舊版 ultralytics** 訓練的
2. 模型檔案內部儲存的類別路徑是 `ultralytics.nn.modules.conv.Conv`
3. 新版 ultralytics 8.4.12 改變了內部模組結構，該路徑已不存在
4. **直接執行 Python 可以載入**：
   ```bash
   uv run python -c "from src.detector import Detector; d = Detector('data/models/best.pt')"
   # ✓ 模型載入成功
   ```
5. **但在 pytest 環境中失敗**

#### 已嘗試的解決方案
1. ❌ Monkey patch torch.load（detector.py 中已有，但 pytest 環境中失效）
2. ❌ conftest.py 中再次 patch（仍然失敗）
3. ❌ 設定 `TORCH_LOAD_WEIGHTS_ONLY=0`（已設定，無效）

#### 觀察
- 原始專案（/home/shihyu/price-tag-detector）可以載入模型
- 兩個專案使用相同的 ultralytics 版本 (8.4.12)
- detector.py 完全相同（diff 無差異）
- **直接執行可以，pytest 不行** → 問題出在 pytest 的導入順序或環境

---

## 🔧 解決方案選項

### 選項 1: 使用獨立腳本替代 pytest（推薦）
**優點**:
- 已證實直接執行 Python 可以載入模型
- 可以繞過 pytest 的導入問題
- 快速驗證準確度

**做法**:
1. 建立 `scripts/verify_accuracy.py`
2. 使用相同的測試邏輯
3. 直接執行 `uv run python scripts/verify_accuracy.py`
4. 輸出準確度報告

### 選項 2: 修改 torch unpickler 重映射模組路徑
**優點**:
- 根本解決問題
- pytest 也能正常運行

**做法**:
1. 在 conftest.py 中建立自訂 Unpickler
2. 重映射 `ultralytics.nn.modules.conv` → 新路徑
3. 需要研究新版 ultralytics 的正確路徑

**缺點**: 技術性較強，需要時間研究

### 選項 3: 降級 ultralytics
**優點**:
- 可能完全解決相容性問題

**做法**:
1. 找到訓練時使用的 ultralytics 版本
2. 修改 pyproject.toml 固定版本
3. 重新 `uv sync`

**缺點**:
- 不知道確切的訓練版本
- 可能影響其他相容性

### 選項 4: 重新訓練模型（不推薦）
**缺點**:
- 會改變 mAP (98.01%)
- 不符合重構的目標（保持準確度一致）

---

## 📊 重構成果統計

### 空間節省
- **原始專案**: 29GB
- **重構專案**: ~1.1GB
- **節省**: 96% (27.9GB)

### 檔案精簡
| 類別 | 原始 | 重構 | 說明 |
|------|------|------|------|
| 程式碼 (src/) | 7 檔案 | 4 檔案 | 移除 ocr_engine_paddle, ocr_engine_v2 |
| CLI (cli/) | 2 檔案 | 1 檔案 | 只保留 detect.py |
| 工具 (utils/) | 7 檔案 | 1 檔案 | 只保留 dataset_splitter.py |
| 測試 (tests/) | 4 檔案 | 5 檔案 | 新增 test_accuracy.py |
| 文檔 | 8 .md 檔案 | 2 .md 檔案 | README.md + 本檔案 |

### 資料保留
- ✅ `data/videos/` (655MB) - 原始影片
- ✅ `data/manual_labels/` (353MB) - 手動標註（準確度基準）
- ✅ `data/dataset/` (22MB) - 訓練資料集
- ✅ `data/models/best.pt` (6MB) - 訓練好的模型
- ❌ `data/images/` (6.7GB) - 移除（可從 videos 重新生成）
- ❌ `data/detections/` (4.9GB) - 移除（測試產物）
- ❌ `data/detections_v2/` (6.7GB) - 移除（測試產物）
- ❌ `data/failure_analysis/` (1.4MB) - 移除（分析資料）

### 依賴精簡
**移除的依賴**:
- ❌ `paddlepaddle>=3.3.0`
- ❌ `paddleocr>=3.4.0`

**保留的核心依賴**:
- ultralytics>=8.4.0 (YOLO)
- torch>=2.0.0 (深度學習)
- opencv-python>=4.8.0 (圖像處理)
- pytesseract>=0.3.10 (OCR)
- numpy, pillow, tqdm, pyyaml

---

## 📝 剩餘子任務 (9-12)

### 子任務 9: 執行核心測試
**待做**:
- 執行 `make test`
- 檢查測試結果
- 修正失敗的測試

**狀態**: 未開始（等待子任務 8 完成）

### 子任務 10: 撰寫精簡版 README.md
**待做**:
- 完成 README.md（已有框架）
- 加入實際的準確度數據

**狀態**: 部分完成（已有基礎版本）

### 子任務 11: 清理和驗證
**待做**:
- 執行 `make clean`
- 刪除所有 __pycache__
- 檢查目錄大小
- 執行最終測試

**狀態**: 未開始

### 子任務 12: 文件和交接
**待做**:
- 檢查 plan.md
- 確認所有驗收標準
- 生成最終測試報告

**狀態**: 未開始

---

## 🚀 下一步行動

### 優先順序 1: 解決模型載入問題
**推薦方案**: 選項 1（使用獨立腳本）

**步驟**:
1. 建立 `scripts/verify_accuracy.py`
2. 複製 test_accuracy.py 的邏輯
3. 執行驗證並生成報告
4. 確認準確度 ≥ 98.4%

### 優先順序 2: 完成剩餘子任務
1. 執行核心測試（子任務 9）
2. 完善 README.md（子任務 10）
3. 清理專案（子任務 11）
4. 最終驗收（子任務 12）

---

## 🔍 技術細節

### OCR 引擎版本選擇
- ✅ **選擇**: ocr_engine_v2.py（重命名為 ocr_engine.py）
- **原因**: 包含改進特徵（動態放大、CLAHE 5.0、多策略組合）
- **成果**: 達到 98.2% 成功率（根據 COMPLETE_ANALYSIS_REPORT.md）

### manual_labels 格式
- **格式**: labelme JSON
- **shapes**: 每個 JSON 有 2 個 shapes（標註）
- **解析規則**: 按 x 座標排序
  - 左邊（x 較小）= 黃色區域
  - 右邊（x 較大）= 綠色區域
- **label**: 數字字串（如 "1", "10", "17"）

### PriceTagOCR API
```python
from src.ocr_engine import PriceTagOCR

ocr = PriceTagOCR()
yellow_result = ocr.recognize_yellow(yellow_crop)  # OCRResult
green_result = ocr.recognize_green(green_crop)      # OCRResult
```

---

## 📞 聯絡與支援

**專案位置**: `/home/shihyu/refactor-price-tag-detector`
**原始專案**: `/home/shihyu/price-tag-detector`
**計畫文件**: `/home/shihyu/plan_refactor.md`

**關鍵指令**:
```bash
cd /home/shihyu/refactor-price-tag-detector

# 安裝依賴
make build

# 測試模型載入（直接執行，不用 pytest）
uv run python -c "from src.detector import Detector; d = Detector('data/models/best.pt'); print('✓ OK')"

# 準確度測試（目前會失敗）
make accuracy

# 清理
make clean
```

---

**最後更新**: 2026-02-07 20:10
**完成進度**: 7/12 子任務 (58%)
**當前狀態**: 等待解決模型載入問題
