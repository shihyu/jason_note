# Autodistill Video Project Makefile

.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示說明訊息
	@echo "使用方式："
	@echo "  make build      - 安裝專案依賴 (使用 uv)"
	@echo "  make run        - 執行影片處理與自動標記"
	@echo "  make visualize  - 產生單張預覽圖"
	@echo "  make plot       - 產生所有資料集圖片的標記預覽"
	@echo "  make test       - 驗證資料集結構"
	@echo "  make clean      - 移除產出的圖片與資料集"

.PHONY: build
build:  ## 安裝依賴
	@echo "正在使用 uv 安裝依賴..."
	uv sync

.PHONY: run
run:  ## 執行程式
	@echo "正在執行標記流程..."
	uv run main.py

.PHONY: visualize
visualize:  ## 繪製標記預覽圖 (單張)
	@echo "正在產生標記預覽圖..."
	uv run visualize.py

.PHONY: plot
plot:  ## 產生所有資料集圖片的標記預覽
	@echo "正在產生資料集標記預覽圖..."
	uv run plot_dataset.py

.PHONY: test
test:  ## 驗證結果
	@echo "驗證資料集..."
	@ls data/dataset/train/images/*.jpg >/dev/null 2>&1 || (echo "Error: Train images missing"; exit 1)
	@ls data/dataset/train/labels/*.txt >/dev/null 2>&1 || (echo "Error: Train labels missing"; exit 1)
	@test -f data/dataset/data.yaml || (echo "Error: data.yaml missing"; exit 1)
	@echo "驗證成功！YOLOv8 資料集已備妥。"

.PHONY: clean
clean:  ## 清理產出
	rm -rf data/images
	rm -rf data/datasets
	rm -rf data/temp_images
	rm -rf data/visualizations
	@echo "清理完成。"
