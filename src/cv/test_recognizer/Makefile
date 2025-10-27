# 手機圖片辨識與價格查詢系統 Makefile

.DEFAULT_GOAL := help

# 變數定義
IMG ?= tests/fixtures/test_phone.jpg

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make setup       - 安裝依賴套件"
	@echo "  make init-data   - 初始化手機資料（下載參考圖片）"
	@echo "  make build       - 準備執行環境（下載 MobileCLIP 模型）"
	@echo "  make run         - 辨識手機圖片並顯示資訊"
	@echo "  make test        - 執行所有測試"
	@echo "  make clean       - 清理建置產物和臨時檔案"
	@echo ""
	@echo "使用範例："
	@echo "  make setup                 # 初次安裝"
	@echo "  make init-data             # 收集手機資料"
	@echo "  make build                 # 下載模型"
	@echo "  make run IMG=myphone.jpg   # 辨識圖片"
	@echo "  make test                  # 執行測試"

.PHONY: setup
setup:  ## 安裝依賴套件
	@echo "安裝 Python 依賴套件..."
	pip install -r requirements.txt
	@echo "✓ 依賴套件安裝完成"

.PHONY: init-data
init-data:  ## 初始化手機資料
	@echo "初始化手機資料..."
	@if [ ! -f "data/seed_data.json" ]; then \
		echo "錯誤: data/seed_data.json 不存在"; \
		exit 1; \
	fi
	python src/scraper.py --init
	@echo "✓ 手機資料初始化完成"

.PHONY: build
build:  ## 準備執行環境（下載模型）
	@echo "下載 MobileCLIP 模型..."
	python -c "from transformers import AutoModel, AutoProcessor; \
		model = AutoModel.from_pretrained('apple/mobileclip_s0'); \
		processor = AutoProcessor.from_pretrained('apple/mobileclip_s0'); \
		print('✓ 模型下載完成')"

.PHONY: run
run:  ## 執行程式（辨識手機圖片）
	@echo "辨識手機圖片: $(IMG)"
	@if [ ! -f "$(IMG)" ]; then \
		echo "錯誤: 圖片檔案不存在: $(IMG)"; \
		exit 1; \
	fi
	python src/main.py --image $(IMG)

.PHONY: test
test:  ## 執行測試
	@echo "執行測試..."
	pytest tests/ -v --tb=short

.PHONY: clean
clean:  ## 清理建置產物和臨時檔案
	@echo "清理臨時檔案..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	find tests/ -type f -name "*.log" -delete 2>/dev/null || true
	@echo "✓ 清理完成"
