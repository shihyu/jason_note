# Node.js I/O 並發範例 Makefile

.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build     - 檢查 Node.js 環境"
	@echo "  make run       - 執行所有範例"
	@echo "  make run-simple    - 執行單線程異步範例"
	@echo "  make run-worker    - 執行 Worker Threads 範例"
	@echo "  make run-file      - 執行文件 I/O 範例"
	@echo "  make test      - 執行測試"
	@echo "  make clean     - 清理臨時檔案"
	@echo ""
	@echo "使用範例："
	@echo "  make build && make run"
	@echo "  make test"

.PHONY: build
build:  ## 檢查 Node.js 環境
	@echo "檢查 Node.js 環境..."
	@node --version || (echo "錯誤: Node.js 未安裝" && exit 1)
	@echo "Node.js 環境正常"

.PHONY: run
run: run-simple run-worker run-file  ## 執行所有範例

.PHONY: run-simple
run-simple:  ## 執行單線程異步範例
	@echo "\n=== 單線程異步 I/O 並發範例 ==="
	@node simple-io-concurrent.js

.PHONY: run-worker
run-worker:  ## 執行 Worker Threads 範例
	@echo "\n=== Worker Threads 多線程範例 ==="
	@node worker-threads-example.js

.PHONY: run-file
run-file:  ## 執行文件 I/O 範例
	@echo "\n=== 文件 I/O 並發讀取範例 ==="
	@node file-io-concurrent.js

.PHONY: test
test:  ## 執行測試
	@echo "執行測試..."
	@echo "測試 1: 單線程異步範例"
	@node simple-io-concurrent.js > /dev/null && echo "  PASS: simple-io-concurrent.js" || echo "  FAIL: simple-io-concurrent.js"
	@echo "測試 2: Worker Threads 範例"
	@node worker-threads-example.js > /dev/null && echo "  PASS: worker-threads-example.js" || echo "  FAIL: worker-threads-example.js"
	@echo "測試 3: 文件 I/O 範例"
	@node file-io-concurrent.js > /dev/null && echo "  PASS: file-io-concurrent.js" || echo "  FAIL: file-io-concurrent.js"
	@echo "\n所有測試完成"

.PHONY: clean
clean:  ## 清理臨時檔案
	@echo "清理臨時檔案..."
	@rm -rf tmp/
	@rm -f test*.txt
	@echo "清理完成"
