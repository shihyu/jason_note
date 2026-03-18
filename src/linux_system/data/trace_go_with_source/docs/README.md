# trace_go_with_source — Go 函數追蹤工具集

追蹤 Go 程式的函數呼叫，提供兩種模式：

- **bpftrace 模式**：用 kernel uprobe 從外部觀測，不改任何程式碼（需 sudo）
- **instrument 模式**：AST 自動插樁，記錄函數進出與耗時（不需 sudo，不動原始碼）

## 快速開始

```bash
# 查看所有可用指令
make

# 一般編譯 & 執行
make run

# bpftrace 追蹤（需 sudo）
make trace

# AST 插樁追蹤（用 overlay 編譯，不動原始碼）
make instrument
```

## 範例輸出

### bpftrace 模式（`make trace`）

```
ORDER TIME(us)        FUNCTION                                           SOURCE
----- --------        --------                                           ------
1     0               runtime.text/0                                     -
2     23              internal/cpu.Initialize                            cpu.go:26
...
58    2430            main.main                                          hello.go:11
59    2445            main.swap                                          hello.go:7
```

### instrument 模式（`make instrument`）

```
--> main.main
Before swap: a = 1, b = 2
  --> main.swap
  <-- main.swap (220ns)
After swap: a = 2, b = 1
<-- main.main (14.343µs)
```

## 兩種模式比較

| | bpftrace | instrument |
|---|---|---|
| 原始碼修改 | 不動 | 不動（overlay 模式） |
| 需要 sudo | 是 | 否 |
| 追蹤範圍 | 所有符號（含 runtime） | 使用者函數 |
| 效能影響 | 極小 | 每函數多一次 defer |
| 平台 | Linux only | 跨平台 |
| 適用場景 | 生產診斷 | 開發除錯 |
