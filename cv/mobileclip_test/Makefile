# MobileCLIP 以圖找圖測試專案 Makefile

.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標:"
	@echo "  make setup       - 安裝依賴套件"
	@echo "  make install-mc  - 安裝 MobileCLIP"
	@echo "  make download    - 下載測試圖片"
	@echo "  make test        - 執行所有測試"
	@echo "  make run         - 執行以圖找圖測試"
	@echo "  make clean       - 清理臨時檔案"
	@echo ""
	@echo "使用範例:"
	@echo "  make setup"
	@echo "  make install-mc"
	@echo "  make download"
	@echo "  make test"

.PHONY: setup
setup:  ## 安裝依賴套件
	@echo "安裝 Python 依賴套件..."
	pip install -r requirements.txt

.PHONY: install-mc
install-mc:  ## 安裝 MobileCLIP
	@echo "Clone MobileCLIP 倉庫..."
	@if [ ! -d "ml-mobileclip" ]; then \
		git clone https://github.com/apple/ml-mobileclip.git; \
	fi
	@echo "安裝 MobileCLIP..."
	cd ml-mobileclip && pip install -e .
	@echo "✓ MobileCLIP 安裝完成"

.PHONY: download
download:  ## 下載測試圖片
	@echo "下載測試圖片..."
	python src/download_images.py

.PHONY: test
test:  ## 執行測試
	@echo "執行測試..."
	pytest tests/ -v --tb=short

.PHONY: run
run:  ## 執行以圖找圖測試
	@echo "執行以圖找圖測試..."
	python src/image_search.py

.PHONY: clean
clean:  ## 清理建置產物和臨時檔案
	@echo "清理臨時檔案..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find results/logs -type f -name "*.log" -delete 2>/dev/null || true
	rm -rf tests/fixtures/queries/* 2>/dev/null || true
	@echo "✓ 清理完成"
