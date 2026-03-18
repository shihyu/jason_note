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
