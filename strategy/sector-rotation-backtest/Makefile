.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "可用目標："
	@echo "  make setup   - 安裝依賴並驗證 FinLab API Token"
	@echo "  make test    - 執行所有測試"
	@echo "  make run     - 執行完整回測（3 個策略）"
	@echo "  make clean   - 清理結果檔案和快取"
	@echo ""
	@echo "使用範例："
	@echo "  make setup && make test && make run"

.PHONY: setup
setup:
	@echo "檢查 FinLab 安裝..."
	@python3 -c "import finlab" || python3 -m pip install finlab
	@python3 -c "import pytest" || python3 -m pip install pytest
	@python3 -c "import dotenv" || python3 -m pip install python-dotenv
	@echo "驗證 API Token..."
	@python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); token = os.getenv('FINLAB_API_TOKEN'); assert token, '缺少 FINLAB_API_TOKEN'; print('Token OK')"

.PHONY: test
test:
	@echo "執行測試..."
	python3 -m pytest tests/ -v

.PHONY: run
run:
	@echo "開始回測..."
	@mkdir -p results
	python3 src/backtest_runner.py

.PHONY: clean
clean:
	@echo "清理檔案..."
	rm -rf results/*.txt results/*.csv __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
