.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "可用目標："
	@echo "  make build  - 檢查程式可匯入並編譯"
	@echo "  make run    - 執行 FinLab 牛熊回測"
	@echo "  make test   - 執行 pytest"
	@echo "  make clean  - 清理暫存與快取"
	@echo ""
	@echo "使用範例："
	@echo "  make build && make test"
	@echo "  make run"

.PHONY: build
build:
	python3 -m compileall src

.PHONY: run
run:
	python3 src/main.py

.PHONY: test
test:
	python3 -m pytest tests/ -v

.PHONY: clean
clean:
	rm -rf tests/tmp/* .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
