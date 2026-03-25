.DEFAULT_GOAL := help

DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "Transformer 股價預測器 — 場景 A"
	@echo ""
	@echo "可用目標："
	@echo "  make build        - 安裝依賴"
	@echo "  make run          - yfinance 版：訓練 + 回測 (預設: TSM)"
	@echo "  make run-finlab   - FinLab 版：台股多股票訓練 + sim() 回測"
	@echo "  make test         - 執行所有單元測試"
	@echo "  make test-finlab  - 只執行 FinLab 整合測試"
	@echo "  make clean        - 清理產出檔案"
	@echo ""
	@echo "使用範例："
	@echo "  make run"
	@echo "  make run TICKER=AAPL"
	@echo "  make run-finlab"
	@echo "  make run-finlab TOP_N=20 RESAMPLE=M"

TICKER ?= TSM
TOP_N ?= 10
MAX_STOCKS ?= 100
RESAMPLE ?= W

.PHONY: build
build:  ## 安裝依賴
	pip install yfinance torch pandas numpy matplotlib scikit-learn finlab

.PHONY: run
run:  ## yfinance 版：執行訓練 + 回測
	cd $(DIR) && python main.py --ticker $(TICKER)

.PHONY: run-finlab
run-finlab:  ## FinLab 版：台股多股票訓練 + sim() 回測
	cd $(DIR) && python main_finlab.py --top-n $(TOP_N) --max-stocks $(MAX_STOCKS) --resample $(RESAMPLE)

.PHONY: test
test:  ## 執行所有單元測試
	cd $(DIR) && python -m pytest tests/ -v

.PHONY: test-finlab
test-finlab:  ## 只執行 FinLab 整合測試
	cd $(DIR) && python -m pytest tests/test_finlab.py -v

.PHONY: clean
clean:  ## 清理產出檔案
	rm -f $(DIR)backtest_results.png $(DIR)training_loss.png $(DIR)finlab_backtest.png
	rm -rf $(DIR)__pycache__ $(DIR)tests/__pycache__ $(DIR).pytest_cache
