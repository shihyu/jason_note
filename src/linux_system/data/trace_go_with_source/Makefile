.DEFAULT_GOAL := help

BINARY := hello_noinline
SRC := hello.go

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build   - 編譯專案（禁用 inline 優化）"
	@echo "  make run     - 編譯並執行程式"
	@echo "  make trace   - 追蹤 Go runtime 並顯示原始碼位置（需要 sudo）"
	@echo "  make clean   - 清理建置產物"

.PHONY: build
build:  ## 編譯專案（-gcflags='-l' 禁用 inline）
	go build -gcflags='-l' -o $(BINARY) $(SRC)

.PHONY: run
run: build  ## 編譯並執行程式
	./$(BINARY)

.PHONY: trace
trace: build  ## 追蹤 Go runtime 並顯示原始碼位置（需要 sudo）
	./trace_go_with_source.sh ./$(BINARY)

.PHONY: clean
clean:  ## 清理建置產物
	rm -f $(BINARY)
