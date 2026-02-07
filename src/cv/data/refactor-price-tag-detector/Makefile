# 價格標籤檢測系統 Makefile（精簡版）

.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build     - 安裝依賴"
	@echo "  make prepare   - 從 manual_labels 準備訓練資料集"
	@echo "  make train     - 訓練 YOLO 模型"
	@echo "  make detect    - 執行檢測"
	@echo "  make test      - 執行測試"
	@echo "  make accuracy  - 驗證準確度（對比 manual_labels）"
	@echo "  make clean     - 清理產物（含模型）"
	@echo ""
	@echo "完整流程（從 manual_labels 訓練模型）："
	@echo "  make clean && make build && make prepare && make train"
	@echo ""
	@echo "使用範例："
	@echo "  make build && make accuracy"

.PHONY: build
build:  ## 安裝依賴
	@echo "安裝依賴..."
	uv sync
	@echo "✓ 完成"

.PHONY: prepare
prepare:  ## 從 manual_labels 準備訓練資料集
	@echo "=========================================="
	@echo "準備訓練資料集"
	@echo "=========================================="
	@echo ""
	@echo "將 labelme 格式轉換為 YOLO 格式..."
	uv run python utils/labelme_to_yolo.py \
		--input data/manual_labels \
		--output data/dataset \
		--train-ratio 0.8
	@echo ""
	@echo "✓ 資料集準備完成"

.PHONY: train
train:  ## 訓練 YOLO 模型
	@echo "=========================================="
	@echo "訓練 YOLO 模型"
	@echo "=========================================="
	@echo ""
	@echo "檢查資料集..."
	@test -f data/dataset/data.yaml || (echo "✗ 錯誤：請先執行 make prepare" && exit 1)
	@echo "✓ 資料集存在"
	@echo ""
	@echo "開始訓練（這可能需要很長時間）..."
	uv run python src/trainer.py \
		--data data/dataset/data.yaml \
		--epochs 100 \
		--batch-size 8 \
		--img-size 640 \
		--output data/models
	@echo ""
	@echo "✓ 訓練完成"
	@echo ""
	@echo "模型已儲存到 data/models/best.pt"

.PHONY: detect
detect:  ## 執行檢測（使用 video1 作為範例）
	@echo "從 video1.mp4 提取影格並檢測..."
	@echo "注意：需要先手動提取影格或直接使用 manual_labels 中的圖片"
	@echo "執行檢測程式..."
	uv run python cli/detect.py
	@echo "✓ 完成"

.PHONY: test
test:  ## 執行核心測試（不需要載入模型的測試）
	@echo "執行核心測試..."
	@echo "（註：test_detector 和 test_accuracy 需要模型載入，使用獨立腳本驗證）"
	@echo ""
	uv run pytest tests/test_color_filter.py tests/test_dataset_splitter.py -v
	@echo ""
	@echo "✓ 完成"
	@echo ""
	@echo "提示：執行 'make accuracy' 進行完整準確度驗證"

.PHONY: accuracy
accuracy:  ## ⭐ 驗證準確度（對比 manual_labels）
	@echo "=========================================="
	@echo "準確度驗證測試（使用獨立腳本）"
	@echo "=========================================="
	@echo ""
	@echo "驗收標準："
	@echo "  - Video1: ≥ 100.0%"
	@echo "  - Video2: ≥ 96.9%"
	@echo "  - Video3: ≥ 98.2%"
	@echo "  - 總體:   ≥ 98.4%"
	@echo ""
	uv run python scripts/verify_accuracy.py
	@echo ""
	@echo "✓ 準確度驗證完成"

.PHONY: clean
clean:  ## 清理建置產物和臨時檔案（含模型）
	@echo "清理臨時檔案..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@rm -rf .pytest_cache .coverage htmlcov
	@rm -rf data/detections/* data/images/* runs/
	@echo "清理訓練產物..."
	@rm -rf data/dataset/train/* data/dataset/valid/* 2>/dev/null || true
	@rm -f data/models/best.pt data/models/*.pt 2>/dev/null || true
	@echo "✓ 清理完成"
	@echo ""
	@echo "保留的資料："
	@echo "  ✓ data/manual_labels/  (手動標註)"
	@echo "  ✓ data/videos/         (原始影片)"
	@echo ""
	@echo "已清理："
	@echo "  ✗ data/dataset/        (訓練資料集，可用 make prepare 重建)"
	@echo "  ✗ data/models/         (訓練好的模型，可用 make train 重建)"
