APP       := myapp
TRACE_DIR := tmp
PID_FILE  := $(TRACE_DIR)/myapp.pid
RUN_LOG   := $(TRACE_DIR)/myapp_stdout.log
TRACE_LOG := $(TRACE_DIR)/trace_smoke.log
BPFTRACE  := sudo bpftrace

.DEFAULT_GOAL := help

.PHONY: help build run test clean \
        trace-list trace-main trace-step1 trace-step2 trace-flow \
        trace-latency trace-count trace-stack \
        trace-alloc trace-goroutine trace-sleep trace-runtime \
        run-bg stop-bg trace-smoke

help: ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build            - 編譯專案"
	@echo "  make run              - 執行程式"
	@echo "  make test             - 執行測試"
	@echo "  make clean            - 清理建置產物"
	@echo ""
	@echo "App 層追蹤："
	@echo "  make trace-list       - 列出 main.* probes"
	@echo "  make trace-main       - 追蹤 main.main"
	@echo "  make trace-step1      - 追蹤 main.Step1"
	@echo "  make trace-step2      - 追蹤 main.Step2"
	@echo "  make trace-flow       - 追蹤所有 main.* 函數"
	@echo "  make trace-latency    - 統計 Step1/Step2 耗時"
	@echo "  make trace-count      - 統計函數命中次數"
	@echo "  make trace-stack      - 顯示 Step1 呼叫堆疊"
	@echo ""
	@echo "Runtime 層追蹤："
	@echo "  make trace-alloc      - 追蹤 heap 分配 (runtime.mallocgc)"
	@echo "  make trace-goroutine  - 追蹤 goroutine 生命週期"
	@echo "  make trace-sleep      - 追蹤 time.Sleep 實際參數"
	@echo "  make trace-runtime    - 綜合：app + runtime 同時追蹤"
	@echo ""
	@echo "自動化："
	@echo "  make run-bg           - 背景啟動程式並記錄 PID"
	@echo "  make stop-bg          - 停止背景程式"
	@echo "  make trace-smoke      - 自動背景啟動後做短時間 trace"
	@echo ""
	@echo "使用範例："
	@echo "  make build && make run"
	@echo "  make test"
	@echo "  sudo make trace-alloc"
	@echo "  sudo make trace-runtime"
	@echo "  sudo make trace-smoke"

build: ## 編譯專案
	go build -o $(APP) .

run: build ## 執行程式
	./$(APP)

test: build ## 執行測試
	go test -v .

clean: ## 清理建置產物和臨時檔案
	@$(MAKE) stop-bg >/dev/null 2>&1 || true
	rm -f $(APP)
	rm -rf $(TRACE_DIR)

# --- App 層追蹤 ---

trace-list: build ## 列出 main.* probes
	$(BPFTRACE) -l 'uprobe:./$(APP):main.*'

trace-main: build ## 追蹤 main.main
	$(BPFTRACE) -e 'uprobe:./$(APP):main.main { printf("時間: %llu ms | 函數: %s\n", elapsed / 1000000, probe); }'

trace-step1: build ## 追蹤 main.Step1
	$(BPFTRACE) -e 'uprobe:./$(APP):main.Step1 { printf("時間: %llu ms | 函數: %s\n", elapsed / 1000000, probe); }'

trace-step2: build ## 追蹤 main.Step2
	$(BPFTRACE) -e 'uprobe:./$(APP):main.Step2 { printf("時間: %llu ms | 函數: %s\n", elapsed / 1000000, probe); }'

trace-flow: build ## 追蹤所有 main.* 函數
	$(BPFTRACE) -e 'uprobe:./$(APP):main.* { printf("時間: %llu ms | 函數: %s\n", elapsed / 1000000, probe); }'

trace-latency: build ## 統計 Step1 與 Step2 耗時
	$(BPFTRACE) -e 'uprobe:./$(APP):main.Step1 { @step1[tid] = nsecs; } uretprobe:./$(APP):main.Step1 /@step1[tid]/ { printf("Step1 耗時: %llu us\n", (nsecs - @step1[tid]) / 1000); delete(@step1[tid]); } uprobe:./$(APP):main.Step2 { @step2[tid] = nsecs; } uretprobe:./$(APP):main.Step2 /@step2[tid]/ { printf("Step2 耗時: %llu us\n", (nsecs - @step2[tid]) / 1000); delete(@step2[tid]); }'

trace-count: build ## 統計函數命中次數
	$(BPFTRACE) -e 'uprobe:./$(APP):main.* { @[probe] = count(); }'

trace-stack: build ## 顯示 Step1 呼叫堆疊
	$(BPFTRACE) -e 'uprobe:./$(APP):main.Step1 { printf("命中 %s\n", probe); print(ustack()); }'

# --- Runtime 層追蹤 ---

trace-alloc: build ## 追蹤 heap 分配：Allocate 呼叫 + mallocgc 大小分布
	$(BPFTRACE) -e 'uprobe:./$(APP):main.Allocate { printf("[Allocate] elapsed=%llu ms\n", elapsed/1000000); } uprobe:./$(APP):runtime.mallocgc { @size = hist(reg("ax")); } END { print(@size); }'

trace-goroutine: build ## 追蹤 goroutine 生命週期：newproc + Worker 執行
	$(BPFTRACE) -e 'uprobe:./$(APP):runtime.newproc { printf("[newproc] 新 goroutine elapsed=%llu ms\n", elapsed/1000000); } uprobe:./$(APP):main.Worker { printf("[Worker]  goroutine 執行 elapsed=%llu ms\n", elapsed/1000000); } uprobe:./$(APP):runtime.goexit0 { printf("[goexit0] goroutine 結束 elapsed=%llu ms\n", elapsed/1000000); }'

trace-sleep: build ## 追蹤 time.Sleep 實際 duration（同時顯示主/Worker goroutine）
	$(BPFTRACE) -e 'uprobe:./$(APP):time.Sleep { printf("[time.Sleep] duration=%lld ms tid=%d\n", reg("ax")/1000000, tid); }'

trace-runtime: build ## 綜合追蹤：app 函數 + runtime（排程次數、分配總量）
	$(BPFTRACE) -e 'uprobe:./$(APP):main.Step1 { printf("[app] Step1 elapsed=%llu ms\n", elapsed/1000000); } uprobe:./$(APP):main.Step2 { printf("[app] Step2 elapsed=%llu ms\n", elapsed/1000000); } uprobe:./$(APP):main.Allocate { printf("[app] Allocate elapsed=%llu ms\n", elapsed/1000000); } uprobe:./$(APP):main.Worker { printf("[app] Worker elapsed=%llu ms\n", elapsed/1000000); } uprobe:./$(APP):time.Sleep { printf("[runtime] Sleep %lld ms tid=%d\n", reg("ax")/1000000, tid); } uprobe:./$(APP):runtime.schedule { @sched = count(); } uprobe:./$(APP):runtime.mallocgc { @alloc_bytes = sum(reg("ax")); } END { printf("\n--- 統計 ---\n"); print(@sched); print(@alloc_bytes); }'

# --- 自動化 ---

run-bg: build ## 背景啟動程式並記錄 PID
	@mkdir -p $(TRACE_DIR)
	@if [ -f $(PID_FILE) ]; then \
		pid="$$(cat $(PID_FILE))"; \
		if kill -0 "$$pid" 2>/dev/null; then \
			echo "背景程式已在執行: $$pid"; \
			exit 0; \
		fi; \
		rm -f $(PID_FILE); \
	fi
	@./$(APP) >$(RUN_LOG) 2>&1 & echo $$! > $(PID_FILE)
	@sleep 1
	@echo "背景程式 PID: $$(cat $(PID_FILE))"

stop-bg: ## 停止背景程式
	@mkdir -p $(TRACE_DIR)
	@if [ ! -f $(PID_FILE) ]; then \
		echo "沒有背景程式"; \
		exit 0; \
	fi
	@pid="$$(cat $(PID_FILE))"; \
	if kill -0 "$$pid" 2>/dev/null; then \
		kill -9 "$$pid" 2>/dev/null || true; \
		echo "已停止背景程式: $$pid"; \
	else \
		echo "背景程式不存在: $$pid"; \
	fi
	@rm -f $(PID_FILE)

trace-smoke: build ## 自動背景啟動後做短時間 trace
	@$(MAKE) run-bg
	@timeout 5s $(BPFTRACE) -e 'uprobe:./$(APP):main.* { printf("時間: %llu ms | 函數: %s\n", elapsed / 1000000, probe); }' >$(TRACE_LOG) 2>&1 || true
	@$(MAKE) stop-bg
	@cat $(TRACE_LOG)
