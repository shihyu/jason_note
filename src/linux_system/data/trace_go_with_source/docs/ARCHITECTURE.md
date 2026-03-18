# 架構設計

## 系統架構

```
┌─────────────────────────────────────────────────────────┐
│                    使用者程式 (hello.go)                  │
│                   原始碼完全不修改                         │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
     ┌─────────▼─────────┐  ┌────────▼────────────┐
     │  bpftrace 模式     │  │  instrument 模式     │
     │  (外部觀測)        │  │  (編譯時插樁)        │
     └─────────┬─────────┘  └────────┬────────────┘
               │                      │
               ▼                      ▼
     ┌───────────────────┐  ┌─────────────────────┐
     │ trace_go_with_     │  │ cmd/instrument/     │
     │ source.sh          │  │ main.go             │
     │                    │  │                     │
     │ 1. objdump 建對照表 │  │ 1. go/ast 解析原始碼 │
     │ 2. bpftrace uprobe │  │ 2. 注入 defer Trace │
     │ 3. awk 合併輸出    │  │ 3. 輸出插樁版       │
     └─────────┬─────────┘  └────────┬────────────┘
               │                      │
               ▼                      ▼
     ┌───────────────────┐  ┌─────────────────────┐
     │ kernel uprobe      │  │ go build -overlay   │
     │ 動態探針攔截       │  │ compiler 替換原始碼   │
     └─────────┬─────────┘  └────────┬────────────┘
               │                      │
               ▼                      ▼
     ┌───────────────────┐  ┌─────────────────────┐
     │ 函數名 + 原始碼位置 │  │ 函數進出 + 縮排深度  │
     │ + 呼叫順序         │  │ + 耗時               │
     └───────────────────┘  └─────────────────────┘
```

## bpftrace 如何對應函數到原始碼行號

bpftrace 的 uprobe 只能攔截到函數名，不知道原始碼位置。
對應行號靠的是 **Go binary 內建的 DWARF 除錯資訊**。

### ELF binary 裡的 DWARF sections

Go 預設編譯就包含 DWARF（不像 C 要加 `-g`）。
binary 裡有多個 section 各司其職：

```
ELF binary (hello_noinline)
│
├── .text             機器碼（函數的實際指令）
│     0x4932a0: MOVQ AX, CX    ← main.swap 的第一條指令
│     0x4932c0: CMPQ SP, ...   ← main.main 的第一條指令
│
├── .symtab           符號表（函數名 → 地址）
│     main.swap  → 0x4932a0
│     main.main  → 0x4932c0
│
├── .debug_info       函數的 metadata（DWARF）
│     main.swap:
│       DW_AT_name      = "main.swap"
│       DW_AT_low_pc    = 0x4932a0    ← 函數起始地址
│       DW_AT_high_pc   = 0x4932aa    ← 函數結束地址
│       DW_AT_decl_file = 2           ← 檔案索引（hello.go）
│       DW_AT_decl_line = 7           ← 宣告在第 7 行
│
├── .debug_line       行號表（地址 ↔ 原始碼行號，逐條指令）
│     0x4932a0 → hello.go:8
│     0x4932a3 → hello.go:8
│     0x4932c0 → hello.go:11
│     0x4932ce → hello.go:11
│     0x4932d2 → hello.go:13
│
└── .debug_frame      stack frame 資訊（給 debugger 回溯 call stack）
```

### 查詢流程

```
bpftrace uprobe 攔截到地址 0x4932a0
         │
         ▼
.symtab 查到：0x4932a0 = main.swap       ← 「這是哪個函數？」
         │
         ▼
go tool objdump 內部做的事：
.debug_info  查到：main.swap 宣告在 file=2, line=7
.debug_line  查到：0x4932a0 對應 hello.go:8    ← 「第一條指令在哪一行？」
         │
         ▼
輸出：main.swap → hello.go:8
```

### go tool objdump 的 TEXT 行

`go tool objdump` 輸出的 `TEXT` 不是 ELF section 名，
是它自己的輸出格式，表示「這裡開始是一個函數的反組譯」：

```
$ go tool objdump hello_noinline | grep -A3 'TEXT main.swap'

TEXT main.swap(SB) /full/path/hello.go     ← 讀 .debug_info 的 DW_AT_decl_file 得到路徑
  hello.go:8    0x4932a0    MOVQ AX, CX   ← 讀 .debug_line 得到 地址→行號 對應
  hello.go:8    0x4932a3    MOVQ BX, AX
  hello.go:8    0x4932a6    MOVQ CX, BX
```

### trace_go_with_source.sh 的兩步驟

```
步驟 1：go tool objdump 建對照表
────────────────────────────────────

Go binary（含 DWARF）
       │
       ▼
go tool objdump → awk 解析
       │
       │  碰到 TEXT 行 → 取函數名 + 檔案路徑
       │  讀下一行指令 → 取行號
       │
       ▼
對照表（MAP_FILE）：
  main.swap     hello.go:8
  main.main     hello.go:11
  runtime.xxx   proc.go:145
  ...


步驟 2：bpftrace uprobe + awk 合併
────────────────────────────────────

bpftrace uprobe 攔截函數呼叫
       │
       │  kernel 在函數入口觸發探針
       │  得到 func 名（例如 main.swap）
       │
       ▼
awk 拿 func 名查對照表
       │
       ▼
輸出：main.swap → hello.go:8
```

### 注意事項

- `go build -ldflags='-s -w'` 會去掉符號表和 DWARF，對照表將失效
- `-gcflags='-l'` 禁用 inline 確保函數不被內聯，否則 uprobe 抓不到被內聯的函數

## instrument overlay 模式資料流

```
hello.go (原始碼，不動)
    │
    ▼
cmd/instrument -overlay /tmp/dir hello.go
    │
    ├──▶ /tmp/dir/hello.go        (插樁版，加了 defer tracer.Trace())
    └──▶ /tmp/dir/overlay.json    (替換對照表)
              │
              ▼
go build -overlay=/tmp/dir/overlay.json -o binary hello.go
    │
    │  compiler 讀 hello.go 時查 overlay.json
    │  實際讀取 /tmp/dir/hello.go（插樁版）
    │
    ▼
binary（含 tracing，但原始碼零修改）
    │
    ▼
執行後自動清理 /tmp/dir/
```

## 檔案結構

```
trace_go_with_source/
├── hello.go                    # 使用者程式（追蹤目標）
├── Makefile                    # build/run/trace/instrument/clean
├── go.mod                      # Go module 定義
├── tracer/
│   └── tracer.go               # Trace() 函數：記錄進出、縮排、耗時
├── cmd/
│   └── instrument/
│       └── main.go             # AST 改寫工具（支援 overlay 模式）
├── trace_go_with_source.sh     # bpftrace 追蹤腳本
├── bpftrace-introduction.html  # bpftrace 參考文件
└── docs/
    ├── README.md               # 專案說明
    └── ARCHITECTURE.md         # 本文件
```

## tracer.Trace() 原理

```go
// 使用者寫的函數
func swap(a, b int) (int, int) {
    return b, a
}

// 插樁後（overlay 模式下只存在於 /tmp）
func swap(a, b int) (int, int) {
    defer tracer.Trace("main.swap")()  // ← 自動注入
    return b, a
}
```

`Trace("name")` 返回一個 closure：
1. 呼叫時印 `--> name`，depth++
2. `defer` 觸發時印 `<-- name (耗時)`，depth--
3. depth 控制縮排，呈現呼叫巢狀關係
