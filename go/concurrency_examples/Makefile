# Go 並行範例 Makefile - 重構版

.PHONY: all test clean build fmt lint help run-all list demo install-tools check-env race-test

# 目錄設定
EXAMPLES_DIR = .
BUILD_DIR = build

# 顏色定義
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m

# 默認目標
all: fmt test

# 運行所有測試
test:
	@echo -e "$(BLUE)🧪 運行並行範例測試...$(NC)"
	@./test_concurrency_examples.sh

# 格式化所有代碼
fmt:
	@echo -e "$(BLUE)🎨 格式化代碼...$(NC)"
	@find $(EXAMPLES_DIR) -name "*.go" -exec go fmt {} \;
	@echo -e "$(GREEN)✅ 代碼格式化完成$(NC)"

# 代碼檢查
lint:
	@echo -e "$(BLUE)🔍 代碼檢查...$(NC)"
	@if command -v golint >/dev/null 2>&1; then \
		find $(EXAMPLES_DIR) -name "*.go" -exec golint {} \; ; \
	else \
		echo -e "$(YELLOW)⚠️  golint 未安裝，跳過 lint 檢查$(NC)"; \
		echo "運行 'make install-tools' 安裝開發工具"; \
	fi

# 編譯所有範例
build:
	@echo -e "$(BLUE)🔨 編譯所有範例...$(NC)"
	@mkdir -p $(BUILD_DIR)
	@success=0; total=0; \
	for file in $$(find $(EXAMPLES_DIR) -name "*.go" -type f | sort); do \
		total=$$((total + 1)); \
		filename=$$(basename $$file .go); \
		output="$(BUILD_DIR)/$$filename"; \
		echo "編譯 $$file -> $$output"; \
		if go build -o "$$output" "$$file"; then \
			success=$$((success + 1)); \
		else \
			echo -e "$(RED)❌ 編譯失敗: $$file$(NC)"; \
		fi; \
	done; \
	echo -e "$(GREEN)✅ 編譯完成: $$success/$$total 成功$(NC)"; \
	echo "輸出目錄: $(BUILD_DIR)/"

# 清理編譯文件
clean:
	@echo -e "$(BLUE)🧹 清理編譯文件...$(NC)"
	@rm -rf $(BUILD_DIR)/
	@echo -e "$(GREEN)✅ 清理完成$(NC)"

# 列出所有範例
list:
	@echo -e "$(BLUE)📋 可用的並行範例:$(NC)"
	@echo "================================================"
	@echo "編號 | 檔案名稱                          | 描述"
	@echo "----|-----------------------------------|------------------"
	@echo " 01  | 01_goroutine_basics.go            | Goroutine 基礎"
	@echo " 02  | 02_channel_communication.go      | Channel 通訊"
	@echo " 03  | 03_select_multiplexing.go        | Select 多路復用"
	@echo " 04  | 04_mutex_synchronization.go      | Mutex 互斥鎖"
	@echo " 05  | 05_rwmutex_optimization.go       | RWMutex 讀寫鎖"
	@echo " 06  | 06_waitgroup_synchronization.go  | WaitGroup 同步"
	@echo " 07  | 07_atomic_operations.go          | 原子操作"
	@echo " 08  | 08_context_control.go            | Context 控制"
	@echo " 09  | 09_producer_consumer_pattern.go  | 生產者-消費者"
	@echo " 10  | 10_pipeline_pattern.go           | Pipeline 管道"
	@echo " 11  | 11_worker_pool_advanced.go       | 高級 Worker Pool"
	@echo "================================================"
	@echo "運行範例: make run-<編號> (例如: make run-01)"
	@echo "使用方法: 請從 concurrency_examples/ 目錄執行"

# 運行特定範例
run-01:
	@echo -e "$(BLUE)🚀 運行 Goroutine 基礎範例...$(NC)"
	@go run 01_goroutine_basics.go

run-02:
	@echo -e "$(BLUE)📡 運行 Channel 通訊範例...$(NC)"
	@go run 02_channel_communication.go

run-03:
	@echo -e "$(BLUE)🎯 運行 Select 多路復用範例...$(NC)"
	@timeout 15s go run 03_select_multiplexing.go

run-04:
	@echo -e "$(BLUE)🔒 運行 Mutex 同步範例...$(NC)"
	@go run 04_mutex_synchronization.go

run-05:
	@echo -e "$(BLUE)📖 運行 RWMutex 範例...$(NC)"
	@go run 05_rwmutex_optimization.go

run-06:
	@echo -e "$(BLUE)🎯 運行 WaitGroup 範例...$(NC)"
	@go run 06_waitgroup_synchronization.go

run-07:
	@echo -e "$(BLUE)⚛️ 運行原子操作範例...$(NC)"
	@go run 07_atomic_operations.go

run-08:
	@echo -e "$(BLUE)🎯 運行 Context 範例...$(NC)"
	@go run 08_context_control.go

run-09:
	@echo -e "$(BLUE)🏭 運行生產者-消費者範例...$(NC)"
	@go run 09_producer_consumer_pattern.go

run-10:
	@echo -e "$(BLUE)🔄 運行 Pipeline 範例...$(NC)"
	@go run 10_pipeline_pattern.go

run-11:
	@echo -e "$(BLUE)⚡ 運行高級 Worker Pool 範例...$(NC)"
	@go run 11_worker_pool_advanced.go

# 依序運行所有範例
run-all:
	@echo -e "$(BLUE)🚀 依序運行所有範例...$(NC)"
	@for i in 01 02 03 04 05 06 07 08 09 10 11; do \
		echo -e "\n$(YELLOW)======== 運行範例 $$i ========$(NC)"; \
		$(MAKE) run-$$i || echo -e "$(RED)範例 $$i 運行失敗$(NC)"; \
		echo -e "$(GREEN)範例 $$i 完成$(NC)"; \
		sleep 2; \
	done
	@echo -e "\n$(GREEN)🎉 所有範例運行完成！$(NC)"

# 演示模式 (每個範例運行更短時間)
demo:
	@echo -e "$(BLUE)🎬 演示模式 - 快速展示所有範例...$(NC)"
	@for file in $$(find $(EXAMPLES_DIR) -name "*.go" -type f | sort); do \
		echo -e "\n$(YELLOW)======== 演示: $$(basename $$file) ========$(NC)"; \
		timeout 5s go run "$$file" || echo -e "$(YELLOW)演示完成$(NC)"; \
		sleep 1; \
	done
	@echo -e "\n$(GREEN)🎉 演示完成！$(NC)"

# 競爭條件檢測
race-test:
	@echo -e "$(BLUE)🏃 運行競爭條件檢測...$(NC)"
	@success=0; total=0; \
	for file in $$(find $(EXAMPLES_DIR) -name "*.go" -type f | sort); do \
		total=$$((total + 1)); \
		echo "檢測 $$file"; \
		if timeout 10s go run -race "$$file" >/dev/null 2>&1; then \
			success=$$((success + 1)); \
		else \
			echo -e "$(YELLOW)⚠️  $$file 檢測異常或超時$(NC)"; \
		fi; \
	done; \
	echo -e "$(GREEN)✅ 競爭檢測完成: $$success/$$total 通過$(NC)"

# 基準測試
benchmark:
	@echo -e "$(BLUE)📊 運行基準測試...$(NC)"
	@if find $(EXAMPLES_DIR) -name "*_test.go" -type f | grep -q .; then \
		cd $(EXAMPLES_DIR) && go test -bench=. -benchmem; \
	else \
		echo -e "$(YELLOW)沒有找到基準測試文件$(NC)"; \
	fi

# API 文檔生成
docs:
	@echo -e "$(BLUE)📚 生成 API 文檔...$(NC)"
	@if command -v godoc >/dev/null 2>&1; then \
		echo "啟動文檔服務器: http://localhost:6060"; \
		godoc -http=:6060; \
	else \
		echo -e "$(YELLOW)godoc 未安裝$(NC)"; \
		echo "安裝命令: go install golang.org/x/tools/cmd/godoc@latest"; \
	fi

# 安裝開發工具
install-tools:
	@echo -e "$(BLUE)🔧 安裝開發工具...$(NC)"
	go install golang.org/x/lint/golint@latest
	go install golang.org/x/tools/cmd/goimports@latest
	go install golang.org/x/tools/cmd/godoc@latest
	@echo -e "$(GREEN)✅ 開發工具安裝完成$(NC)"

# 檢查環境
check-env:
	@echo -e "$(BLUE)🔍 檢查 Go 環境...$(NC)"
	@echo "Go 版本: $$(go version)"
	@echo "GOROOT: $$(go env GOROOT)"
	@echo "GOPATH: $$(go env GOPATH)"
	@echo "GOOS: $$(go env GOOS)"
	@echo "GOARCH: $$(go env GOARCH)"
	@echo "CPU 核心數: $$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo "未知")"
	@echo "可用記憶體: $$(free -h 2>/dev/null | grep Mem | awk '{print $$2}' || echo "未知")"
	@echo "範例目錄: $$(ls -la $(EXAMPLES_DIR) | wc -l) 個文件"

# 程式碼統計
stats:
	@echo -e "$(BLUE)📈 程式碼統計...$(NC)"
	@echo "總文件數: $$(find $(EXAMPLES_DIR) -name "*.go" | wc -l)"
	@echo "總行數: $$(find $(EXAMPLES_DIR) -name "*.go" -exec cat {} \; | wc -l)"
	@echo "總字符數: $$(find $(EXAMPLES_DIR) -name "*.go" -exec cat {} \; | wc -c)"
	@echo ""
	@echo "各範例行數統計:"
	@find $(EXAMPLES_DIR) -name "*.go" -exec wc -l {} \; | sort -nr

# 幫助信息
help:
	@echo -e "$(BLUE)Go 並行範例 Makefile 幫助$(NC)"
	@echo ""
	@echo -e "$(YELLOW)主要目標:$(NC)"
	@echo "  all          - 格式化並測試 (默認)"
	@echo "  test         - 運行所有測試"
	@echo "  build        - 編譯所有範例"
	@echo "  clean        - 清理編譯文件"
	@echo ""
	@echo -e "$(YELLOW)代碼品質:$(NC)"
	@echo "  fmt          - 格式化代碼"
	@echo "  lint         - 代碼檢查"
	@echo "  race-test    - 競爭條件檢測"
	@echo ""
	@echo -e "$(YELLOW)運行範例:$(NC)"
	@echo "  list         - 列出所有範例"
	@echo "  run-<編號>   - 運行特定範例 (例如: run-01)"
	@echo "  run-all      - 依序運行所有範例"
	@echo "  demo         - 快速演示模式"
	@echo ""
	@echo -e "$(YELLOW)工具與環境:$(NC)"
	@echo "  install-tools- 安裝development工具"
	@echo "  check-env    - 檢查 Go 環境"
	@echo "  stats        - 程式碼統計"
	@echo "  docs         - 生成 API 文檔"
	@echo "  help         - 顯示此幫助信息"
	@echo ""
	@echo -e "$(YELLOW)範例:$(NC)"
	@echo "  make test                    # 運行所有測試"
	@echo "  make run-01                  # 運行 Goroutine 基礎範例"
	@echo "  make demo                    # 快速演示所有範例"
	@echo "  make build                   # 編譯所有範例"