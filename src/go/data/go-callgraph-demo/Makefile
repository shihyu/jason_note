BINARY   := demo
TRACED   := demo-traced
NOINLINE := demo-noinline
PKG      := ./cmd/traced/

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Go 函數呼叫圖 — 五種方法"
	@echo ""
	@echo "  make static      靜態呼叫圖 (go-callvis → SVG)"
	@echo "  make trace       動態函數執行路徑 (tracer.Enter)"
	@echo "  make ebpf        eBPF 非侵入追蹤 (需 sudo)"
	@echo "  make pprof       pprof 呼叫圖 (CPU profile → SVG)"
	@echo "  make rtrace      runtime/trace 時間線"
	@echo "  make all         跑全部（ebpf 除外）"
	@echo ""
	@echo "  make build       編譯"
	@echo "  make run         執行 demo"
	@echo "  make test        執行測試"
	@echo "  make clean       清理產物"

.PHONY: build
build:
	go build -o $(BINARY) .

.PHONY: run
run: build
	./$(BINARY)

.PHONY: test
test:
	go test -v ./...

# ===== 方法一：go-callvis 靜態呼叫圖 =====
.PHONY: static
static:
	go-callvis -file static-callgraph -format svg -nostd -group pkg,type .
	@echo "→ static-callgraph.svg"

# ===== 方法二：tracer.Enter() 動態執行路徑 =====
.PHONY: trace
trace:
	go run $(PKG)
	@echo "→ function-trace.md"

# ===== 方法三：eBPF uprobe =====
.PHONY: ebpf
ebpf: $(NOINLINE)
	sudo bpftrace trace-uprobe-entry.bt -c ./$(NOINLINE)

$(NOINLINE):
	go build -gcflags='-l' -o $(NOINLINE) .

# ===== 方法四：pprof 呼叫圖 =====
.PHONY: pprof
pprof:
	go test -bench=BenchmarkFullWorkflow -cpuprofile=cpu.prof -benchtime=3s . > /dev/null 2>&1
	go tool pprof -svg -output=pprof-callgraph.svg cpu.prof
	@echo "→ pprof-callgraph.svg"
	@echo "  互動式: go tool pprof -http=:8080 cpu.prof"

# ===== 方法五：runtime/trace =====
.PHONY: rtrace
rtrace: build
	./$(BINARY) --trace
	@echo "→ trace.out"
	@echo "  分析: go tool trace trace.out"

# ===== 全部（ebpf 需 sudo，單獨跑） =====
.PHONY: all
all: static trace pprof rtrace
	@echo ""
	@echo "完成！產出檔案："
	@ls -lh static-callgraph.svg pprof-callgraph.svg trace.out function-trace.md 2>/dev/null

.PHONY: clean
clean:
	rm -f $(BINARY) $(TRACED) $(NOINLINE)
	rm -f *.svg *.gv *.prof trace.out function-trace.md
	rm -f go-callgraph-demo.test
