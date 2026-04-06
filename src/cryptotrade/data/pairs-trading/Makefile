.PHONY: help install download backtest analyze clean test

DEFAULT_GOAL := help

help:
	@echo "可用目標："
	@echo "  make install   - 安裝依賴"
	@echo "  make download  - 下載歷史K線數據"
	@echo "  make backtest  - 執行回測"
	@echo "  make analyze   - 分析結果"
	@echo "  make test      - 執行測試"
	@echo "  make clean     - 清理數據"

install:
	pip install -r requirements.txt

download:
	python src/downloader.py

backtest:
	python src/backtester.py

analyze:
	python src/analyzer.py

test:
	cd tests && python -m pytest -v

clean:
	rm -rf data/raw/*
	rm -rf results/*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
