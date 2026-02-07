# ============================================================================
# Autodistill Video Project Makefile
# ============================================================================
# 這個 Makefile 提供自動化的影片標記、模型訓練和測試流程
#
# 典型工作流程：
#   1. make build      → 安裝依賴
#   2. make run        → 處理影片並產生標記資料集
#   3. make train      → 訓練 YOLOv8 模型
#   4. make test-model → 測試訓練好的模型
# ============================================================================

.DEFAULT_GOAL := help

# ----------------------------------------------------------------------------
# help - 顯示所有可用的指令和說明
# ----------------------------------------------------------------------------
.PHONY: help
help:
	@echo "============================================================"
	@echo "Autodistill Video Project - 可用指令"
	@echo "============================================================"
	@echo ""
	@echo "基本流程："
	@echo "  make build      - 安裝專案依賴 (使用 uv)"
	@echo "  make run        - 執行影片處理與自動標記"
	@echo "  make train      - 訓練 YOLOv8 模型"
	@echo "  make test-model - 測試訓練好的模型效果"
	@echo ""
	@echo "輔助工具："
	@echo "  make visualize  - 產生單張預覽圖"
	@echo "  make plot       - 產生所有資料集圖片的標記預覽"
	@echo "  make detect-all - 使用模型檢測所有影格 (產生標記圖)"
	@echo "  make test       - 驗證資料集結構"
	@echo ""
	@echo "維護工具："
	@echo "  make clean      - 移除所有產出的檔案"
	@echo ""
	@echo "快速開始："
	@echo "  make build && make run && make train"
	@echo ""
	@echo "============================================================"

# ----------------------------------------------------------------------------
# build - 安裝專案依賴
# ----------------------------------------------------------------------------
# 功能：使用 uv 安裝 pyproject.toml 中定義的所有依賴
# 產出：.venv/ (虛擬環境), uv.lock (依賴鎖定檔)
# 執行時機：首次設定專案時，或更新依賴時
# ----------------------------------------------------------------------------
.PHONY: build
build:
	@echo "正在使用 uv 安裝依賴..."
	uv sync
	@echo "✓ 依賴安裝完成"

# ----------------------------------------------------------------------------
# run - 執行影片處理與自動標記
# ----------------------------------------------------------------------------
# 功能：
#   1. 掃描 data/videos/ 中的所有 .mp4 影片
#   2. 從每個影片提取影格 (stride=20)
#   3. 使用 GroundedSAM 自動標記物件
#   4. 產生 YOLOv8 格式的訓練資料集
#
# 產出：
#   - data/images/videoX/          → 提取的影格 (.jpg)
#   - data/datasets/videoX/        → YOLOv8 格式資料集
#     ├── train/images/            → 訓練圖片
#     ├── train/labels/            → YOLO 格式標籤 (.txt)
#     ├── valid/images/            → 驗證圖片
#     ├── valid/labels/            → 驗證標籤
#     └── data.yaml                → 資料集配置檔
#   - data/temp_images/videoX/     → 臨時處理圖片
#
# 前置條件：
#   - data/videos/ 目錄存在且包含 .mp4 影片
#   - 已執行 make build 安裝依賴
# ----------------------------------------------------------------------------
.PHONY: run
run:
	@echo "正在執行影片標記流程..."
	@echo "→ 掃描 data/videos/ 中的影片"
	@echo "→ 提取影格並自動標記"
	uv run main.py
	@echo "✓ 標記完成，資料集已產生"

# ----------------------------------------------------------------------------
# visualize - 產生單張標記預覽圖
# ----------------------------------------------------------------------------
# 功能：
#   從 data/images/ 中選擇一張圖片，使用 GroundedSAM 進行檢測
#   並產生帶有標記框的預覽圖
#
# 產出：
#   - data/visualizations/frame-XXXXX_annotated.jpg  → 1 張預覽圖
#
# 前置條件：
#   - 已執行 make run 產生影格
# ----------------------------------------------------------------------------
.PHONY: visualize
visualize:
	@echo "正在產生單張標記預覽圖..."
	uv run visualize.py
	@echo "✓ 預覽圖已保存到 data/visualizations/"

# ----------------------------------------------------------------------------
# plot - 產生所有資料集圖片的標記預覽
# ----------------------------------------------------------------------------
# 功能：
#   為 data/datasets/ 中所有資料集的圖片產生標記預覽圖
#   用於視覺化驗證標記品質
#
# 產出：
#   - data/visualizations/videoX_train_frame-XXXXX.jpg  → 訓練集預覽
#   - data/visualizations/videoX_valid_frame-XXXXX.jpg  → 驗證集預覽
#   (總計約 76+ 張圖片)
#
# 前置條件：
#   - 已執行 make run 產生資料集
# ----------------------------------------------------------------------------
.PHONY: plot
plot:
	@echo "正在產生資料集標記預覽圖..."
	@echo "→ 處理所有資料集的 train 和 valid 分割"
	uv run plot_dataset.py
	@echo "✓ 預覽圖已保存到 data/visualizations/"

# ----------------------------------------------------------------------------
# train - 訓練 YOLOv8 模型
# ----------------------------------------------------------------------------
# 功能：
#   1. 合併所有影片的資料集為單一訓練集
#   2. 使用 YOLOv8 Nano 模型進行訓練
#   3. 在驗證集上評估模型性能
#
# 產出：
#   - data/merged_dataset/                           → 合併的資料集
#     ├── train/ (63 張), valid/ (16 張)
#     └── data.yaml
#   - runs/detect/runs/train/price_tag_detector/
#     ├── weights/
#     │   ├── best.pt  ⭐ (最佳模型，6.2MB)
#     │   └── last.pt     (最後 epoch 模型)
#     ├── results.png                                → 訓練曲線
#     ├── confusion_matrix.png                       → 混淆矩陣
#     ├── F1_curve.png, P_curve.png, R_curve.png     → 性能曲線
#     └── ...其他訓練日誌
#   - train_log.txt                                  → 完整訓練日誌
#   - yolov8n.pt                                     → 下載的預訓練模型
#
# 訓練參數：
#   - Epochs: 50 (早停機制，耐心值=10)
#   - Image size: 640x640
#   - Batch size: 16
#   - Model: YOLOv8 Nano (輕量快速)
#
# 前置條件：
#   - 已執行 make run 產生資料集
#   - GPU 可用 (可選，但建議)
#
# 預期時間：約 5-10 分鐘 (取決於 GPU)
# ----------------------------------------------------------------------------
.PHONY: train
train:
	@echo "============================================================"
	@echo "開始訓練 YOLOv8 模型"
	@echo "============================================================"
	@echo "→ 合併資料集"
	@echo "→ 訓練 YOLOv8 Nano 模型 (50 epochs)"
	@echo "→ 驗證模型準確度"
	@echo ""
	uv run train.py
	@echo ""
	@echo "✓ 訓練完成！"
	@echo "✓ 最佳模型: runs/detect/runs/train/price_tag_detector/weights/best.pt"

# ----------------------------------------------------------------------------
# detect-all - 使用訓練好的模型檢測所有影格
# ----------------------------------------------------------------------------
# 功能：
#   使用訓練好的 YOLOv8 模型檢測 data/images/ 中所有影片的所有影格
#   並產生帶有檢測框的圖片
#
# 產出：
#   - data/detections/videoX/  → 每個影片的檢測結果
#     ├── frame-00000.jpg      → 帶檢測框的圖片
#     ├── frame-00001.jpg
#     └── ...                  → 所有影格 (數百張)
#
# 與 quick_test.py 的差異：
#   - quick_test.py: 只檢測前 5 張圖片 (快速測試)
#   - detect_all.py: 檢測所有圖片 (完整檢測)
#
# 前置條件：
#   - 已執行 make train 訓練模型
#   - 已執行 make run 產生影格
#
# 預期時間：數分鐘 (取決於圖片數量和 GPU 速度)
# ----------------------------------------------------------------------------
.PHONY: detect-all
detect-all:
	@echo "使用訓練好的模型檢測所有影格..."
	@echo "→ 這會處理所有影片的所有影格 (可能需要數分鐘)"
	uv run detect_all.py
	@echo "✓ 檢測完成，結果已保存到 data/detections/"

# ----------------------------------------------------------------------------
# test-model - 測試訓練好的模型效果
# ----------------------------------------------------------------------------
# 功能：
#   提供互動式介面測試訓練好的 YOLOv8 模型
#   可選擇測試圖片、影片或驗證集
#
# 測試模式：
#   1. 測試樣本圖片 - 從 data/images/ 選擇影片的影格
#   2. 測試影片     - 處理整個影片並產生檢測結果影片
#   3. 測試驗證集   - 在驗證集上評估準確度指標
#   4. 自訂路徑     - 測試任意圖片或影片
#
# 產出 (依選擇模式而異)：
#   - data/test_results/              → 圖片檢測結果
#   - data/test_results/*.mp4         → 影片檢測結果
#   - 終端顯示詳細的準確度指標
#
# 前置條件：
#   - 已執行 make train 訓練模型
#   - best.pt 模型檔案存在
# ----------------------------------------------------------------------------
.PHONY: test-model
test-model:
	@echo "測試 YOLOv8 模型..."
	@echo "→ 啟動互動式測試工具"
	uv run test.py

# ----------------------------------------------------------------------------
# test - 驗證資料集結構
# ----------------------------------------------------------------------------
# 功能：
#   驗證 YOLOv8 資料集的檔案結構是否正確
#   檢查訓練圖片、標籤檔和配置檔是否存在
#
# 檢查項目：
#   - data/datasets/*/train/images/*.jpg  → 訓練圖片
#   - data/datasets/*/train/labels/*.txt  → 標籤檔案
#   - data/datasets/*/data.yaml           → 配置檔
#
# 產出：無檔案產出，僅在終端顯示驗證結果
#
# 前置條件：
#   - 已執行 make run 產生資料集
# ----------------------------------------------------------------------------
.PHONY: test
test:
	@echo "驗證資料集結構..."
	@if [ -d "data/datasets" ]; then \
		echo "✓ data/datasets/ 存在"; \
		for dir in data/datasets/*; do \
			if [ -d "$$dir/train/images" ] && [ -d "$$dir/train/labels" ] && [ -f "$$dir/data.yaml" ]; then \
				echo "✓ $$(basename $$dir) - 結構正確"; \
			else \
				echo "✗ $$(basename $$dir) - 結構不完整"; \
				exit 1; \
			fi; \
		done; \
		echo ""; \
		echo "✓ 所有資料集結構驗證通過！"; \
	else \
		echo "✗ Error: data/datasets/ 不存在"; \
		echo "  請先執行 'make run' 產生資料集"; \
		exit 1; \
	fi

# ----------------------------------------------------------------------------
# clean - 清理所有產出的檔案
# ----------------------------------------------------------------------------
# 功能：
#   刪除所有執行過程中產生的檔案和目錄
#   保留原始程式碼和影片檔案
#
# 刪除內容：
#   - data/images/           → 提取的影格
#   - data/datasets/         → 標記好的資料集
#   - data/temp_images/      → 臨時處理圖片
#   - data/visualizations/   → 預覽圖
#   - data/merged_dataset/   → 合併的訓練資料集
#   - data/test_results/     → 測試結果
#   - runs/                  → 訓練和測試的所有輸出
#   - train_log.txt          → 訓練日誌
#   - yolov8n.pt            → 下載的預訓練模型
#
# 保留內容：
#   - data/videos/           → 原始影片 (重要！)
#   - .venv/                 → 虛擬環境
#   - 所有 .py 檔案          → 程式碼
# ----------------------------------------------------------------------------
.PHONY: clean
clean:
	@echo "清理產出檔案..."
	rm -rf data/images
	rm -rf data/datasets
	rm -rf data/temp_images
	rm -rf data/visualizations
	rm -rf data/merged_dataset
	rm -rf data/test_results
	rm -rf data/detections
	rm -rf runs
	rm -f train_log.txt
	rm -f yolov8n.pt
	@echo "✓ 清理完成"
	@echo "✓ 保留: data/videos/ (原始影片), .venv/ (虛擬環境)"
