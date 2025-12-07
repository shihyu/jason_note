# GDB 調試 Go Runtime 指南

使用 GDB 調試 Go 程式，深入理解 goroutine 和 channel 的 runtime 實現。

## 快速開始

```bash
# 編譯程式（帶 debug symbols）
make build

# 啟動 GDB 調試（自動設置所有關鍵斷點）
make debug

# 清理建置產物
make clean
```

**`make debug` 會自動設置以下斷點：**
- `main.main` - 程式入口
- `runtime.makechan` - channel 創建
- `runtime.newproc` - goroutine 創建
- `runtime.chansend1` - channel 發送
- `runtime.chanrecv1` - channel 接收

啟動後直接執行 `run` 即可開始調試！

## 程式說明

`test.go` 是一個簡單的 Go 程式，包含：
- **Channel 創建**：`make(chan int, 2)`
- **Goroutine 啟動**：`go worker(ch, id)`
- **Channel 發送**：`ch <- 100`
- **Channel 接收**：`val := <-ch`

## GDB 基本操作

### 啟動 GDB

```bash
gdb ./test
```

### 常用命令

| 命令 | 簡寫 | 說明 |
|------|------|------|
| `break <location>` | `b` | 設置斷點 |
| `run` | `r` | 執行程式 |
| `continue` | `c` | 繼續執行到下個斷點 |
| `step` | `s` | 單步執行（進入函數） |
| `next` | `n` | 下一行（不進入函數） |
| `list` | `l` | 顯示源碼 |
| `backtrace` | `bt` | 顯示調用棧 |
| `info locals` | | 顯示局部變數 |
| `info args` | | 顯示函數參數 |
| `info breakpoints` | `i b` | 顯示所有斷點 |
| `print <var>` | `p` | 打印變數值 |
| `quit` | `q` | 退出 GDB |

## 關鍵 Runtime 函數斷點

### Goroutine 相關

```gdb
# Goroutine 創建（go 關鍵字觸發）
break runtime.newproc

# Goroutine 創建的底層實現
break runtime.newproc1

# Goroutine 退出
break runtime.goexit

# Goroutine 阻塞/掛起
break runtime.gopark

# Goroutine 喚醒
break runtime.goready

# 調度器選擇下一個 goroutine
break runtime.schedule
```

### Channel 相關

```gdb
# Channel 創建（make(chan T) 觸發）
break runtime.makechan

# Channel 發送（ch <- value 觸發）
break runtime.chansend
break runtime.chansend1

# Channel 接收（<-ch 觸發）
break runtime.chanrecv
break runtime.chanrecv1
break runtime.chanrecv2

# Channel 關閉
break runtime.closechan
```

## 完整調試流程示範

### 方法 1：使用 make debug（推薦，最簡單）

```bash
$ make debug
啟動 GDB（自動設置斷點）...
(gdb) info breakpoints
Num     Type           Disp Enb Address            What
1       breakpoint     keep y   0x4b3cb3          in main.main at test.go:8
2       breakpoint     keep y   0x40d12e          in runtime.makechan at chan.go:75
3       breakpoint     keep y   <MULTIPLE>        runtime.newproc
4       breakpoint     keep y   0x40d364          in runtime.chansend1 at chan.go:160
5       breakpoint     keep y   0x40de84          in runtime.chanrecv1 at chan.go:505

(gdb) run
Starting program: /home/shihyu/test_go/test

Breakpoint 1, main.main () at test.go:8
8       func main() {
(gdb) continue
Hello, GDB!

Breakpoint 2, runtime.makechan (t=0x..., size=2) at chan.go:75
75      func makechan(t *chantype, size int) *hchan {
(gdb) list
...
(gdb) continue

Breakpoint 3.1, runtime.newproc () at proc.go:5077
(gdb) continue
# 依序在各個斷點停止...
```

### 方法 2：手動設置斷點，逐步跟蹤

```gdb
$ gdb ./test
(gdb) break main.main
Breakpoint 1 at 0x4b3cb3: file /home/shihyu/test_go/test.go, line 8.

(gdb) run
Starting program: /home/shihyu/test_go/test
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
[New Thread 0x7ffff7c79640 (LWP xxxxx)]

Breakpoint 1, main.main () at /home/shihyu/test_go/test.go:8

(gdb) list
8       func main() {
9           fmt.Println("Hello, GDB!")
10
11          // 創建 channel
12          ch := make(chan int, 2)
13
14          // 啟動 goroutine
15          go worker(ch, 1)
16          go worker(ch, 2)

(gdb) next
Hello, GDB!

(gdb) next  # 執行到 ch := make(chan int, 2)

(gdb) step  # 進入 runtime.makechan
runtime.makechan (t=0x..., size=2) at .../src/runtime/chan.go:75

(gdb) list
70      func makechan(t *chantype, size int) *hchan {
71          elem := t.Elem
72
73          // compiler checks this but be safe.
74          if elem.Size_ >= 1<<16 {
75              throw("makechan: invalid channel element type")
76          }
...

(gdb) backtrace
#0  runtime.makechan (t=0x..., size=2) at .../src/runtime/chan.go:75
#1  0x00000000004b3cd8 in main.main () at /home/shihyu/test_go/test.go:12

(gdb) continue
```

### 方法 3：手動設置多個 runtime 斷點

```gdb
$ gdb ./test
(gdb) break main.main
(gdb) break runtime.makechan
(gdb) break runtime.newproc
(gdb) break runtime.chansend1
(gdb) break runtime.chanrecv1

(gdb) info breakpoints
Num     Type           Disp Enb Address            What
1       breakpoint     keep y   0x4b3cb3          in main.main at test.go:8
2       breakpoint     keep y   0x40d12e          in runtime.makechan at chan.go:75
3       breakpoint     keep y   <MULTIPLE>
4       breakpoint     keep y   0x40d364          in runtime.chansend1 at chan.go:160
5       breakpoint     keep y   0x40de84          in runtime.chanrecv1 at chan.go:505

(gdb) run
# 程式會在各個斷點停下，可以查看 runtime 源碼和變數
```

### 觀察執行順序

執行程式時，會依序觸發以下斷點：

1. `main.main` → 程式入口
2. `runtime.makechan` → 創建 channel (line 12)
3. `runtime.newproc` → 創建 goroutine 1 (line 15)
4. `runtime.newproc` → 創建 goroutine 2 (line 16)
5. `runtime.chansend1` → 發送 100 到 channel (line 19)
6. `runtime.chansend1` → 發送 200 到 channel (line 20)
7. `runtime.chanrecv1` → worker 1 接收數據
8. `runtime.chanrecv1` → worker 2 接收數據

## 實用技巧

### 1. 查看 Runtime 源碼位置

斷點觸發後，使用 `list` 查看 runtime 源碼：

```gdb
(gdb) list
75      func makechan(t *chantype, size int) *hchan {
76          elem := t.Elem
77          ...
```

### 2. 查看函數參數

```gdb
(gdb) info args
t = 0x4e2a80
size = 2
```

### 3. 查看調用棧

```gdb
(gdb) backtrace
#0  runtime.makechan (...) at .../runtime/chan.go:75
#1  main.main () at test.go:12
```

### 4. 條件斷點

只在特定條件下停止：

```gdb
break runtime.chansend1 if size > 100
```

### 5. 臨時斷點

執行一次後自動刪除：

```gdb
tbreak runtime.makechan
```

## Runtime 源碼位置

Go runtime 源碼位於 `$GOROOT/src/runtime/`，主要檔案：

- `chan.go` - Channel 實現
- `proc.go` - Goroutine 和調度器
- `runtime2.go` - 資料結構定義
- `select.go` - Select 實現

## 驗收檢查清單

- [x] 程式可正常編譯執行
- [x] GDB 可正確載入 debug symbols
- [x] 可在 `main.main` 設置斷點
- [x] 可在 `runtime.makechan` 設置斷點（channel 創建）
- [x] 可在 `runtime.newproc` 設置斷點（goroutine 創建）
- [x] 可在 `runtime.chansend1` 設置斷點（channel 發送）
- [x] 可在 `runtime.chanrecv1` 設置斷點（channel 接收）
- [x] 使用 step 可進入 runtime 程式碼

## 參考資料

- [GDB 官方文檔](https://sourceware.org/gdb/current/onlinedocs/gdb/)
- [Go Runtime Source](https://github.com/golang/go/tree/master/src/runtime)
- [Debugging Go Code with GDB](https://go.dev/doc/gdb)
