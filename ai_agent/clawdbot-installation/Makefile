.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make install  - 安裝 Clawdbot"
	@echo "  make setup    - 配置 OAuth 和通訊平台"
	@echo "  make test     - 執行功能測試"
	@echo "  make clean    - 清理測試檔案"
	@echo "  make status   - 檢查系統狀態"
	@echo ""
	@echo "使用範例："
	@echo "  make install && make status"

.PHONY: install
install:  ## 安裝 Clawdbot
	@echo "開始安裝 Clawdbot..."
	curl -fsSL https://clawd.bot/install.sh | bash 2>&1 | tee install.log
	@echo ""
	@echo "驗證安裝..."
	clawdbot --version

.PHONY: setup
setup:  ## 配置 OAuth (需要互動)
	@echo "開始 OAuth 配置..."
	@echo "將會開啟瀏覽器進行 Claude 授權..."
	clawdbot models auth login --provider anthropic
	@echo ""
	@echo "設定預設 Model..."
	clawdbot models set anthropic/claude-sonnet-4-5
	@echo ""
	@echo "檢查認證狀態..."
	clawdbot models status

.PHONY: test
test:  ## 執行測試
	@echo "=== 測試 Gateway 狀態 ==="
	clawdbot gateway status
	@echo ""
	@echo "=== 測試 Model 狀態 ==="
	clawdbot models status
	@echo ""
	@echo "=== 測試 AI 回應 ==="
	@echo "發送測試訊息..."
	clawdbot agent --session-id test-install --message "你好,請用繁體中文簡短自我介紹" --json 2>&1 | tee tests/test-claude.log
	@echo ""
	@echo "測試完成!查看 tests/test-claude.log 了解詳細結果"

.PHONY: clean
clean:  ## 清理測試產物
	@echo "清理測試檔案..."
	rm -f tests/*.log
	rm -f install.log
	@echo "清理完成!"

.PHONY: status
status:  ## 檢查 Clawdbot 狀態
	@echo "=== Gateway 狀態 ==="
	clawdbot gateway status || echo "Gateway 未運行"
	@echo ""
	@echo "=== Model 狀態 ==="
	clawdbot models status || echo "Model 未配置"
	@echo ""
	@echo "=== 通訊頻道狀態 ==="
	clawdbot channels status || echo "頻道未配置"

.PHONY: gateway
gateway:  ## 啟動 Gateway
	@echo "啟動 Gateway (強制模式)..."
	clawdbot gateway --force
