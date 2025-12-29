.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make setup        - 安裝專案依賴"
	@echo "  make test         - 執行所有測試"
	@echo "  make test-verbose - 執行測試（顯示詳細輸出）"
	@echo "  make clean        - 清理暫存檔案"
	@echo ""
	@echo "使用範例："
	@echo "  make setup && make test"

.PHONY: setup
setup:  ## 安裝專案依賴
	pip install -r requirements.txt

.PHONY: test
test:  ## 執行所有測試
	pytest tests/ -v

.PHONY: test-verbose
test-verbose:  ## 執行測試（顯示詳細輸出）
	pytest tests/ -vv -s

.PHONY: clean
clean:  ## 清理暫存檔案
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
