# 價格標籤檢測系統 Makefile

.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示說明
	@echo "可用目標："
	@echo "  make build         - 安裝依賴"
	@echo "  make extract       - 從影片提取圖片幀"
	@echo "  make prepare       - 準備訓練資料集（轉換 JSON 為 YOLO 格式）"
	@echo "  make train         - 訓練模型"
	@echo "  make detect        - 執行檢測"
	@echo "  make test          - 執行測試"
	@echo "  make clean         - 清理產物（只保留 manual_labels + videos）"
	@echo "  make clean-keep-images - 清理產物（保留 manual_labels + videos + images）"
	@echo "  make rebuild       - 完整重建（clean + extract + prepare + train）"
	@echo ""
	@echo "從零開始建立："
	@echo "  make clean && make build && make extract && make prepare && make train && make detect"

.PHONY: build
build:  ## 安裝依賴
	@echo "安裝依賴..."
	uv sync
	@echo "✓ 完成"

.PHONY: extract
extract:  ## 從影片提取圖片幀
	@echo "從影片提取圖片幀..."
	uv run python utils/extract_frames.py
	@echo "✓ 完成"

.PHONY: train
train:  ## 訓練模型
	@echo "訓練模型..."
	uv run python cli/train.py
	@echo "✓ 完成"

.PHONY: detect
detect:  ## 執行檢測
	@echo "執行檢測..."
	uv run python cli/detect.py
	@echo "✓ 完成"

.PHONY: test
test:  ## 執行測試
	@echo "執行測試..."
	uv run pytest tests/ -v
	@echo "✓ 完成"

.PHONY: prepare
prepare:  ## 準備訓練資料集
	@echo "轉換手動標註為 YOLO 格式..."
	uv run python utils/convert_labels.py
	@echo "✓ 完成"

.PHONY: rebuild
rebuild:  ## 完整重建
	@echo "開始完整重建流程..."
	@$(MAKE) clean
	@$(MAKE) extract
	@$(MAKE) prepare
	@$(MAKE) train
	@echo ""
	@echo "✓ 重建完成！"
	@echo "下一步: make detect"

.PHONY: clean
clean:  ## 清理產物（只保留 manual_labels + videos）
	@echo "清理產生的檔案..."
	@echo "  - Python 快取"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "  - 測試快取"
	@rm -rf .pytest_cache .coverage htmlcov
	@echo "  - 訓練產物"
	@rm -rf runs/
	@rm -rf data/models/
	@echo "  - 檢測結果"
	@rm -rf data/detections/
	@rm -rf data/detections_v2/
	@echo "  - YOLO 訓練資料集"
	@rm -rf data/dataset/
	@echo "  - 提取的圖片幀"
	@rm -rf data/images/
	@echo ""
	@echo "✓ 清理完成"
	@echo ""
	@echo "保留的原始資料:"
	@echo "  ✓ data/manual_labels/  (手動標註)"
	@echo "  ✓ data/videos/         (原始影片)"
	@echo ""
	@echo "重建指令:"
	@echo "  make extract   # 從 videos/ 重新提取 images/"
	@echo "  make prepare   # 轉換標註格式"
	@echo "  make train     # 訓練模型"

.PHONY: clean-keep-images
clean-keep-images:  ## 清理產物（保留 manual_labels + videos + images）
	@echo "清理產生的檔案（保留 images/）..."
	@echo "  - Python 快取"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "  - 測試快取"
	@rm -rf .pytest_cache .coverage htmlcov
	@echo "  - 訓練產物"
	@rm -rf runs/
	@rm -rf data/models/
	@echo "  - 檢測結果"
	@rm -rf data/detections/
	@rm -rf data/detections_v2/
	@echo "  - YOLO 訓練資料集"
	@rm -rf data/dataset/
	@echo ""
	@echo "✓ 清理完成"
	@echo ""
	@echo "保留的資料:"
	@echo "  ✓ data/manual_labels/  (手動標註)"
	@echo "  ✓ data/videos/         (原始影片)"
	@echo "  ✓ data/images/         (提取的圖片)"
