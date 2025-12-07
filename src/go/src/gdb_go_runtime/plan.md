# GDB 調試 Go Runtime 專案

## 任務目標
創建一個簡單的 Go 程式，方便使用 GDB 進入 runtime 程式碼進行調試學習。

## 預期產出
- `test.go`：包含 main 函數的簡單 Go 程式
- `Makefile`：標準化建置流程
- `README.md`：GDB 調試指南

## 專案結構
```
test_go/
├── plan.md
├── Makefile
├── test.go
└── README.md
```

## Makefile 規範

### 必備目標
- `make` (無參數)：顯示可用目標和使用範例
- `make build`：編譯程式（帶 debug symbols）
- `make debug`：啟動 GDB 調試（自動設置斷點）
- `make clean`：清理建置產物

### 編譯參數
- 使用 `-gcflags="all=-N -l"` 禁用優化和內聯
- 保留完整的 debug 資訊

### debug 目標特性
- **自動設置斷點**：啟動時自動設置 5 個關鍵 runtime 斷點
  - `main.main` - 程式入口
  - `runtime.makechan` - channel 創建
  - `runtime.newproc` - goroutine 創建
  - `runtime.chansend1` - channel 發送
  - `runtime.chanrecv1` - channel 接收
- **實現方式**：使用臨時腳本 `/tmp/gdb_cmds_test_go.txt`
- **自動清理**：GDB 退出後自動刪除臨時文件
- **用戶體驗**：進入 GDB 後直接 `run` 即可開始調試

## 程式設計

### test.go 內容
```go
package main

import (
    "fmt"
    "time"
)

func main() {
    fmt.Println("Hello, GDB!")

    // 創建 channel
    ch := make(chan int, 2)

    // 啟動 goroutine
    go worker(ch, 1)
    go worker(ch, 2)

    // 發送數據到 channel
    ch <- 100
    ch <- 200

    // 等待一下讓 goroutine 執行
    time.Sleep(time.Second)

    fmt.Println("Main finished")
}

func worker(ch chan int, id int) {
    val := <-ch
    fmt.Printf("Worker %d received: %d\n", id, val)
}
```

### 設計理念
- 包含 goroutine 創建（`go` 關鍵字）
- 包含 channel 創建（`make(chan int)`）
- 包含 channel 發送（`ch <- value`）
- 包含 channel 接收（`<-ch`）
- 所有關鍵操作都會調用 runtime 函數

## GDB 調試流程

### 快速開始（推薦）
1. `make build` - 編譯程式
2. `make debug` - 啟動 GDB（自動設置斷點）
3. `run` - 執行程式（會在斷點自動停止）
4. `continue` 或 `c` - 繼續到下個斷點
5. `list` 或 `l` - 查看 runtime 源碼
6. `bt` - 查看調用棧

### 常用 GDB 命令
- `run` 或 `r` - 執行程式
- `continue` 或 `c` - 繼續執行到下個斷點
- `step` 或 `s` - 單步執行（會進入函數內部，包括 runtime）
- `next` 或 `n` - 下一行（不進入函數）
- `list` 或 `l` - 顯示源碼
- `backtrace` 或 `bt` - 顯示調用棧
- `info locals` - 顯示局部變數
- `info args` - 顯示函數參數
- `info breakpoints` - 顯示所有斷點
- `info goroutines` - 顯示所有 goroutine（需要 Go runtime 支援）
- `quit` 或 `q` - 退出 GDB

### 關鍵 Runtime 函數斷點

#### Goroutine 相關
- `break runtime.newproc` - goroutine 創建（`go` 關鍵字）
- `break runtime.newproc1` - goroutine 創建的底層實現
- `break runtime.goexit` - goroutine 退出
- `break runtime.gopark` - goroutine 阻塞/掛起
- `break runtime.goready` - goroutine 喚醒
- `break runtime.schedule` - 調度器選擇下一個 goroutine

#### Channel 相關
- `break runtime.makechan` - channel 創建（`make(chan T)`）
- `break runtime.chansend` - channel 發送（`ch <- value`）
- `break runtime.chansend1` - 具體發送實現
- `break runtime.chanrecv` - channel 接收（`<-ch`）
- `break runtime.chanrecv1` - 具體接收實現
- `break runtime.chanrecv2` - 帶 ok 的接收（`val, ok := <-ch`）
- `break runtime.closechan` - channel 關閉

### 調試會話範例

```bash
$ make debug
啟動 GDB（自動設置斷點）...
(gdb) info breakpoints  # 查看已自動設置的斷點
Num     Type           Disp Enb Address            What
1       breakpoint     keep y   0x4b3cb3          in main.main at test.go:8
2       breakpoint     keep y   0x40d12e          in runtime.makechan at chan.go:75
3       breakpoint     keep y   <MULTIPLE>        runtime.newproc
4       breakpoint     keep y   0x40d364          in runtime.chansend1 at chan.go:160
5       breakpoint     keep y   0x40de84          in runtime.chanrecv1 at chan.go:505

(gdb) run  # 執行程式

# 在 main.main 停下
Breakpoint 1, main.main () at test.go:8
(gdb) list
(gdb) continue

# 在 runtime.makechan 停下（創建 channel）
Breakpoint 2, runtime.makechan (t=0x..., size=2) at chan.go:75
(gdb) bt     # 查看調用棧
(gdb) list   # 查看 runtime 源碼
(gdb) info args  # 查看參數
(gdb) continue

# 在 runtime.newproc 停下（啟動 goroutine）
Breakpoint 3.1, runtime.newproc () at proc.go:5077
(gdb) bt
(gdb) continue

# 在 runtime.chansend1 停下（發送到 channel）
Breakpoint 4, runtime.chansend1 () at chan.go:160
(gdb) bt
(gdb) info locals
(gdb) continue

# 繼續執行，觀察所有斷點...
```

### 進入 Runtime 的方法
1. **使用 make debug（最簡單）**：自動設置所有關鍵斷點，直接 `run` 即可
2. **通過 step**：在 `go worker(...)` 或 `ch <- val` 處使用 `step`
3. **手動設置斷點**：手動輸入 `break runtime.xxx` 命令

## 驗收標準
- [x] 程式可正常編譯執行
- [x] GDB 可正確載入 debug symbols
- [x] 可以在 main.main 設置斷點
- [x] 可以在 runtime.makechan 設置斷點（channel 創建）
- [x] 可以在 runtime.newproc 設置斷點（goroutine 創建）
- [x] 可以在 runtime.chansend1 設置斷點（channel 發送）
- [x] 可以在 runtime.chanrecv1 設置斷點（channel 接收）
- [x] 使用 step 可以進入 runtime 程式碼
- [x] README.md 包含完整的 GDB 操作指南和斷點列表
- [x] make debug 自動設置所有關鍵斷點

## 子任務拆解
1. 創建 test.go
2. 創建 Makefile
3. 測試編譯和 GDB 調試
4. 創建 README.md（GDB 操作指南）

## 注意事項
- Go runtime 程式碼位於 `$GOROOT/src/runtime/`
- GDB 需要載入 Go runtime 的輔助腳本（通常自動載入）
- 某些優化可能影響調試體驗，確保使用 `-gcflags="all=-N -l"`
