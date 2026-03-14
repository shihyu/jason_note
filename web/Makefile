.DEFAULT_GOAL := help

.PHONY: help
help: ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build   - 檢查目標文章與圖片資產"
	@echo "  make run     - 啟動本地預覽伺服器"
	@echo "  make test    - 執行 Markdown 驗證"
	@echo "  make clean   - 清理測試暫存檔"
	@echo ""
	@echo "使用範例："
	@echo "  make build && make test"
	@echo "  make run"

.PHONY: build
build: ## 檢查目標文章與圖片資產
	@test -f oauth2-proxy-zero-trust-access-control.md
	@test -d images
	@echo "build ok"

.PHONY: run
run: ## 啟動本地預覽伺服器（自動清理 8000 port）
	@echo "清理 port 8000..."
	@lsof -ti:8000 | xargs -r kill -9 2>/dev/null || true
	@echo "啟動預覽伺服器..."
	@python3 -m http.server 8000

.PHONY: test
test: ## 執行 Markdown 驗證
	@bash tests/markdown_syntax_test.sh

.PHONY: clean
clean: ## 清理建置產物和臨時檔案
	@rm -rf tests/tmp
	@mkdir -p tests/tmp
	@echo "clean ok"
