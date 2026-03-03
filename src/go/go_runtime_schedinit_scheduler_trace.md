# Go Runtime 啟動流程與 Scheduler Trace 解析

## 整理來源

- Day 12: [簡單除錯 GO 語言程式](https://ithelp.ithome.com.tw/articles/10221613)
- Day 13: [更多除錯訊息](https://ithelp.ithome.com.tw/articles/10221931)

## 前言

這兩篇主要圍繞 `runtime.schedinit` 後半段的初始化流程，以及 `GODEBUG` 相關除錯選項如何在 Go runtime 中生效。若把內容串起來看，脈絡會是：

1. 啟動時先整理命令列參數與環境變數。
2. 解析 `GODEBUG`、`GOTRACEBACK` 等除錯設定。
3. 透過 `allocfreetrace`、`schedtrace`、`scheddetail` 觀察 runtime 行為。
4. 回頭追蹤 runtime 原始碼，確認這些 trace 是怎麼印出來的。

## `schedinit` 看到哪裡

在這一段初始化流程中，可以先聚焦幾個關鍵呼叫：

```go
...
goargs()
goenvs()
parsedebugvars()
gcinit()

sched.lastpoll = uint64(nanotime())
procs := ncpu
if n, ok := atoi32(gogetenv("GOMAXPROCS")); ok && n > 0 {
    procs = n
}
...
```

前半段處理啟動資訊，後半段則開始依據環境設定初始化 scheduler 與 GC。

## `goargs`：處理命令列參數

`goargs` 位在 `runtime/runtime1.go`：

```go
func goargs() {
    if GOOS == "windows" {
        return
    }
    argslice = make([]string, argc)
    for i := int32(0); i < argc; i++ {
        argslice[i] = gostringnocopy(argv_index(argv, i))
    }
}
```

這段邏輯很直接：

- Windows 走不同路徑，這裡直接略過。
- 先建立 `argslice`。
- 逐一從 `argv` 取出參數位置。
- 用 `gostringnocopy` 把底層 byte 資料轉成 Go 的 `string`。

`gostringnocopy` 的核心如下：

```go
func gostringnocopy(str *byte) string {
    ss := stringStruct{str: unsafe.Pointer(str), len: findnull(str)}
    s := *(*string)(unsafe.Pointer(&ss))
    return s
}
```

重點是它沒有重新複製字串內容，而是透過 `unsafe` 直接把既有記憶體包裝成 Go 字串。

## `goenvs`：處理環境變數

Linux 下的 `goenvs` 會轉呼叫 `goenvs_unix`：

```go
func goenvs_unix() {
    // TODO(austin): ppc64 in dynamic linking mode doesn't
    // guarantee env[] will immediately follow argv. Might cause
    // problems.
    n := int32(0)
    for argv_index(argv, argc+1+n) != nil {
        n++
    }

    envs = make([]string, n)
    for i := int32(0); i < n; i++ {
        envs[i] = gostring(argv_index(argv, argc+1+i))
    }
}
```

這裡依賴一個重要假設：環境變數陣列緊接在命令列參數之後。流程和 `goargs` 很像，但改用 `gostring`，不是 `gostringnocopy`。原文留下的問題也集中在這裡：

- 為什麼 Windows 不走這個處理流程？
- 為什麼環境變數這裡不用 `gostringnocopy`？

## `parsedebugvars`：解析 `GODEBUG`

`parsedebugvars` 會把 `GODEBUG` 解析成多組 `key=value`：

```go
func parsedebugvars() {
    ...
    for p := gogetenv("GODEBUG"); p != ""; {
        field := ""
        i := index(p, ",")
        if i < 0 {
            field, p = p, ""
        } else {
            field, p = p[:i], p[i+1:]
        }
        i = index(field, "=")
        if i < 0 {
            continue
        }
        key, value := field[:i], field[i+1:]
        ...
    }
}
```

這表示 `GODEBUG` 可以一次攜帶多組設定，例如：

```bash
GODEBUG=allocfreetrace=1,schedtrace=10,scheddetail=1
```

## `allocfreetrace`：觀察記憶體配置

`allocfreetrace=1` 會在配置或釋放記憶體時印出 trace。原文用 hello world 範例觀察：

```bash
GODEBUG=allocfreetrace=1 ./hw
```

輸出中會看到大量 `tracealloc(...)` 與對應 stack trace。即使只是很小的程式，輸出量也會相當可觀，執行時間也會明顯拉長。這類 trace 的價值在於：

- 可以看到記憶體配置從哪條呼叫鏈發生。
- 能快速判斷初始化階段誰在大量配置物件。
- 對照不同程式，能粗看 allocation/free 的分布差異。

> 實測註記（Go 1.21.6 / Linux amd64）：hello world 範例仍可看到 `tracealloc`，本次驗證共出現 65 次 `tracealloc`、0 次 `tracefree`；實際數量會隨 Go 版本與執行環境改變。

## `schedtrace`：觀察 scheduler 狀態

單純 hello world 幾乎看不到 scheduler 的變化，因此需要更忙碌的範例。原文設計了一個 `multi-hw.go`，讓 `n` 個 goroutine 透過 channel 互相交換訊息，強迫 scheduler 持續介入。

初始化 channel 的核心片段如下：

```go
chans := make([][]chan uint32, n)
shadow := make([]chan uint32, n*n)
for i := 0; i < n; i++ {
    chans[i] = shadow[i*n : (i+1)*n]
    for j := 0; j < n; j++ {
        chans[i][j] = make(chan uint32)
    }
}
```

再配合 `sync.WaitGroup` 等待所有 goroutine 結束：

```go
var id uint32
var wg sync.WaitGroup
wg.Add(n)

for i := 0; i < n; i++ {
    go func() {
        defer wg.Done()
        myID := atomic.AddUint32(&id, 1) - 1
        ...
    }()
}

wg.Wait()
time.Sleep(500 * time.Microsecond)
```

goroutine 之間用同步 channel 互傳資料，並以 `myID` 做出固定順序，避免 deadlock：

```go
for i = 0; i < myID; i++ {
    <-chans[i][myID]
    chans[myID][i] <- myID
}

for i = myID + 1; i < uint32(n); i++ {
    chans[myID][i] <- myID
    <-chans[i][myID]
}
```

開啟 `schedtrace` 之後：

```bash
GODEBUG=schedtrace=1 ./multi-hw 2048
```

會持續看到這類輸出：

```text
SCHED 0ms: gomaxprocs=8 idleprocs=5 threads=5 spinningthreads=1 idlethreads=0 runqueue=0 [1 0 0 0 0 0 0 0]
SCHED 1ms: gomaxprocs=8 idleprocs=6 threads=5 spinningthreads=0 idlethreads=2 runqueue=0 [0 0 0 0 0 0 0 0]
...
```

從這裡至少可以直接觀察：

- `gomaxprocs` 目前可並行執行的 P 數量。
- `idleprocs` 空閒中的 P。
- `threads` 當前 M 的總數。
- `runqueue` 全域 runnable queue 的狀態。

> 實測註記（Go 1.21.6 / Linux amd64）：目前輸出會多出 `needspinning` 等欄位，`gomaxprocs` 也會依主機 CPU 數改變；本次驗證值為 16，不會固定等於原文示例中的 8。

## `scheddetail`：展開 P / M / G 細節

如果只看 `schedtrace`，資訊會太粗。把 `scheddetail=1` 一起打開：

```bash
GODEBUG=schedtrace=10,scheddetail=1 ./multi-hw 2048
```

輸出會展開成 P、M、G 三層資訊，例如：

```text
SCHED 564ms: gomaxprocs=8 idleprocs=0 threads=9 spinningthreads=0 idlethreads=0 runqueue=0 gcwaiting=0 nmidlelocked=0 stopwait=0 sysmonwait=0
  P0: status=1 schedtick=2651 syscalltick=9 m=0 runqsize=1 gfreecnt=2
  ...
  M8: p=3 curg=1714 mallocing=0 throwing=0 preemptoff= locks=0 dying=0 spinning=false blocked=false lockedg=-1
  ...
  G142: status=2(chan send) m=5 lockedm=-1
  ...
```

這能幫助理解 runtime 當下：

- 哪些 P 正在執行、哪個 M 綁在哪個 P 上。
- 哪些 G 正卡在 `chan send` 或 `chan receive`。
- 某些 runnable 或 blocked goroutine 是否集中在特定 P/M。

但它也帶出一個現象：trace 本身是 runtime 運作當下的快照，不是完全靜止的世界，因此 P、M、G 之間的關係不保證在輸出的所有行中都完全一致。

## 這些 trace 在 runtime 怎麼生效

直接在 runtime 原始碼搜尋 `debug.schedtrace`，可以看到幾個重要位置：

```go
./runtime/runtime1.go:334: {"scheddetail", &debug.scheddetail},
./runtime/runtime1.go:335: {"schedtrace", &debug.schedtrace},
./runtime/panic.go:919:   if debug.schedtrace > 0 || debug.scheddetail > 0 {
./runtime/proc.go:4367:   if debug.schedtrace > 0 && lasttrace+int64(debug.schedtrace)*1000000 <= now {
./runtime/proc.go:4369:       schedtrace(debug.scheddetail > 0)
```

真正印出 `SCHED ...` 的函式在 `runtime/proc.go`：

```go
func schedtrace(detailed bool) {
    now := nanotime()
    if starttime == 0 {
        starttime = now
    }

    lock(&sched.lock)
    print("SCHED ", (now-starttime)/1e6, "ms: gomaxprocs=", gomaxprocs,
        " idleprocs=", sched.npidle, " threads=", mcount(),
        " spinningthreads=", sched.nmspinning, " idlethreads=", sched.nmidle,
        " runqueue=", sched.runqsize)
    if detailed {
        print(" gcwaiting=", sched.gcwaiting, " nmidlelocked=", sched.nmidlelocked,
            " stopwait=", sched.stopwait, " sysmonwait=", sched.sysmonwait, "\n")
    }
    ...
}
```

這段後面會分別掃過 `allp`、`allm`、`allg`。更關鍵的是原始碼中的註解：

```go
// We must be careful while reading data from P's, M's and G's.
// Even if we hold schedlock, most data can be changed concurrently.
```

也就是說，trace 的資料在讀取同時，scheduler 仍可能持續推進。這正是前面觀察到「P/M 看似對得上，但 G 的關聯未必完全一致」的原因。

## 綜合整理

把兩篇合起來看，可以得到一條比較完整的路徑：

1. `goargs` 和 `goenvs` 先把啟動參數、環境變數整理進 runtime。
2. `parsedebugvars` 把 `GODEBUG` 解析成多組 runtime debug 開關。
3. `allocfreetrace` 適合看 allocation 呼叫鏈。
4. `schedtrace` 適合看 scheduler 的週期性狀態。
5. `scheddetail` 則能進一步看到 P、M、G 的快照。
6. 這些 trace 都是動態觀測結果，閱讀時不能把它們當作完全靜態的一致狀態。

## 後續可追的問題

- Windows 為什麼不走 `goargs` 這條路？
- `gostringnocopy` 透過 `unsafe` 轉字串時，底層記憶體保證在哪裡？
- 為什麼 `goenvs_unix` 用 `gostring` 而不是 `gostringnocopy`？
- `schedtrace` 在真實除錯場景中最常拿來解哪一類問題？

## 小結

這兩篇其實是在做同一件事：從 runtime 啟動初始化一路接到可觀測性。前半段處理資料從哪裡來，後半段處理 runtime 願意把哪些內部狀態吐出來。把 `goargs`、`goenvs`、`parsedebugvars` 與 `schedtrace` 串起來之後，`GODEBUG` 就不再只是幾個零散選項，而是一條完整的 runtime 除錯入口。
