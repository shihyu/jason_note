.DEFAULT_GOAL := help

BINARY := hello_noinline
SRC := hello.go

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build      - 編譯專案（禁用 inline 優化）"
	@echo "  make run        - 編譯並執行程式"
	@echo "  make trace      - bpftrace 追蹤（需要 sudo）"
	@echo "  make instrument - AST 插樁追蹤函數進出（不需 sudo，不動原始碼）"
	@echo "  make clean      - 清理建置產物"

.PHONY: build
build:  ## 編譯專案（-gcflags='-l' 禁用 inline）
	go build -gcflags='-l' -o $(BINARY) $(SRC)

.PHONY: run
run: build  ## 編譯並執行程式
	./$(BINARY)

.PHONY: trace
trace: build  ## bpftrace 追蹤（需要 sudo）
	./trace_go_with_source.sh ./$(BINARY)

.PHONY: instrument
instrument:  ## AST 插樁：用 overlay 編譯，原始碼不動
	@TMPDIR=$$(mktemp -d /tmp/go_instrument.XXXXXX); \
	OVERLAY=$$(go run ./cmd/instrument -overlay "$$TMPDIR" $(SRC)); \
	go build -overlay="$$OVERLAY" -gcflags='-l' -o hello_traced $(SRC); \
	./hello_traced; \
	rm -rf "$$TMPDIR" hello_traced

.PHONY: clean
clean:  ## 清理建置產物
	rm -f $(BINARY) hello_traced
