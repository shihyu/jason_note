.DEFAULT_GOAL := help

.PHONY: help build run test clean

help:  ## 顯示說明
	@echo "可用目標："
	@echo "  make build   - 安裝 pipeline 自身依賴（不裝跨語言第三方工具）"
	@echo "  make run     - 對 examples/python 跑一次完整五階段"
	@echo "  make test    - 執行測試（./test.sh）"
	@echo "  make clean   - 清理狀態檔／coverage／mutation 暫存產物"

build:  ## 安裝依賴
	pip install -r requirements.txt

run:  ## 執行示範 pipeline（python 範例）
	python3 -m pipeline.cli run --lang python --task discount_demo

test:  ## 測試
	./test.sh

clean:  ## 清理
	rm -rf .pipeline_state .coverage htmlcov .mutation_tmp
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
