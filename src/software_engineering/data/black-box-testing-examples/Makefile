# Makefile for Black Box Testing Examples
.DEFAULT_GOAL := help

PYTHON := python3
PYTEST := pytest
PYTEST_ARGS ?=

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "====================================="
	@echo "  黑箱測試方法範例專案"
	@echo "====================================="
	@echo ""
	@echo "可用目標："
	@echo "  make setup          - 安裝依賴套件"
	@echo "  make test           - 執行所有測試"
	@echo "  make test-boundary  - 執行邊界值測試"
	@echo "  make test-pairwise  - 執行組合測試"
	@echo "  make test-decision  - 執行決策表測試"
	@echo "  make test-state     - 執行狀態測試"
	@echo "  make test-verbose   - 執行所有測試（詳細輸出）"
	@echo "  make coverage       - 執行測試並生成覆蓋率報告"
	@echo "  make clean          - 清理建置產物和快取"
	@echo ""
	@echo "使用範例："
	@echo "  make setup && make test"
	@echo "  make test-boundary"
	@echo "  make test PYTEST_ARGS=\"-v\""
	@echo ""

.PHONY: setup
setup:  ## 安裝依賴套件
	@echo "安裝 Python 依賴套件..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	@echo "✓ 依賴套件安裝完成"

.PHONY: test
test:  ## 執行所有測試
	@echo "執行所有測試..."
	$(PYTEST) tests/ $(PYTEST_ARGS)

.PHONY: test-boundary
test-boundary:  ## 執行邊界值測試
	@echo "執行邊界值測試..."
	$(PYTEST) tests/test_boundary_value.py -v

.PHONY: test-pairwise
test-pairwise:  ## 執行組合測試
	@echo "執行組合測試..."
	$(PYTEST) tests/test_pairwise.py -v

.PHONY: test-decision
test-decision:  ## 執行決策表測試
	@echo "執行決策表測試..."
	$(PYTEST) tests/test_decision_table.py -v

.PHONY: test-state
test-state:  ## 執行狀態測試
	@echo "執行狀態測試..."
	$(PYTEST) tests/test_state_transition.py -v

.PHONY: test-verbose
test-verbose:  ## 執行所有測試（詳細輸出）
	@echo "執行所有測試（詳細模式）..."
	$(PYTEST) tests/ -v

.PHONY: coverage
coverage:  ## 執行測試並生成覆蓋率報告
	@echo "執行測試並生成覆蓋率報告..."
	$(PYTEST) tests/ --cov=src --cov-report=html --cov-report=term
	@echo "✓ 覆蓋率報告已生成至 htmlcov/ 目錄"

.PHONY: clean
clean:  ## 清理建置產物和快取
	@echo "清理建置產物..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	@echo "✓ 清理完成"
