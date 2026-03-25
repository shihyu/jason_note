.DEFAULT_GOAL := help

.PHONY: help
help: ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build   - 檢查文件與測試檔是否存在"
	@echo "  make run     - 顯示閱讀順序"
	@echo "  make test    - 執行測試"
	@echo "  make clean   - 清理測試暫存檔"
	@echo ""
	@echo "使用範例："
	@echo "  make build && make test"
	@echo "  make run"

.PHONY: build
build: ## 檢查必要檔案是否存在
	@test -f docs/README.md
	@test -f tests/test_markdown_structure.sh

.PHONY: run
run: ## 顯示建議閱讀順序
	@echo "閱讀入口：docs/README.md"

.PHONY: test
test: ## 執行測試
	@bash tests/test_markdown_structure.sh

.PHONY: clean
clean: ## 清理建置產物和臨時檔案
	@rm -rf tests/tmp/*
