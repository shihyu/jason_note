.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "Go 效能優化指南 - 可用目標："
	@echo "  make build          - 編譯所有範例程式"
	@echo "  make run-trace      - 執行 trace 範例並產生 trace.out"
	@echo "  make run-false      - 執行 false sharing 範例"
	@echo "  make run-gc         - 執行 GC 壓力分析範例"
	@echo "  make run-pool       - 執行 goroutine pool 比較範例"
	@echo "  make bench          - 執行 false sharing benchmark"
	@echo "  make trace-ui       - 開啟 go tool trace UI (需先 run-trace)"
	@echo "  make test           - 執行所有測試"
	@echo "  make clean          - 清理建置產物"

.PHONY: build
build:  ## 編譯所有範例
	go build -o bin/trace-demo ./cmd/trace-demo/
	go build -o bin/false-sharing ./cmd/false-sharing/
	go build -o bin/gc-pressure ./cmd/gc-pressure/
	go build -o bin/pool-benchmark ./cmd/pool-benchmark/

.PHONY: run-trace
run-trace: build  ## 執行 trace 範例
	./bin/trace-demo

.PHONY: run-false
run-false: build  ## 執行 false sharing 範例
	./bin/false-sharing

.PHONY: run-gc
run-gc: build  ## 執行 GC 壓力分析
	./bin/gc-pressure

.PHONY: run-pool
run-pool: build  ## 執行 pool 比較
	./bin/pool-benchmark

.PHONY: bench
bench:  ## 執行 benchmark
	go test -bench=. -count=3 ./cmd/false-sharing/

.PHONY: trace-ui
trace-ui:  ## 開啟 trace UI
	@test -f trace.out || (echo "請先執行 make run-trace" && exit 1)
	go tool trace trace.out

.PHONY: test
test:  ## 執行測試
	go test ./...

.PHONY: clean
clean:  ## 清理
	rm -rf bin/ trace.out
