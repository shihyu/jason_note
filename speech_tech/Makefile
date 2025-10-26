.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build   - 安裝依賴套件"
	@echo "  make run     - 執行互動式 demo"
	@echo "  make test    - 執行所有測試"
	@echo "  make clean   - 清理建置產物和臨時檔案"
	@echo ""
	@echo "使用範例："
	@echo "  make build && make test"
	@echo "  make run"

.PHONY: build
build:  ## 安裝依賴套件
	@echo "安裝依賴套件..."
	pip install -q sherpa-onnx numpy scipy requests pytest tqdm
	@echo "✓ 依賴安裝完成"

.PHONY: run
run:  ## 執行互動式 demo
	@echo "啟動互動式 demo..."
	python src/sherpa_onnx_demo/demo.py

.PHONY: test
test:  ## 執行所有測試
	@echo "執行測試套件..."
	pytest tests/ -v --tb=short -k "not network"

.PHONY: clean
clean:  ## 清理建置產物和臨時檔案
	@echo "清理建置產物..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find tests/fixtures -type f -name "temp_*" -delete 2>/dev/null || true
	rm -f outputs/demo_*.wav 2>/dev/null || true
	@echo "✓ 清理完成"
