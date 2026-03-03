# GODEBUG 環境變數與 Runtime 除錯指南

`GODEBUG` 是 Go runtime 內建的除錯開關，可用來觀察 GC、scheduler 與記憶體管理行為。

```bash
GODEBUG=name=value[,name=value...] go run main.go
```

> 不同 Go 版本支援的 `GODEBUG` 參數略有差異，實際可用選項請以 `go doc runtime` 為準。

## 最小測試範例

以下範例可直接拿來測試本文所有 `GODEBUG` 用法：

```go
package main

import "fmt"

func main() {
	fmt.Println("Hello World!")
}
```

可直接搭配：

```bash
GODEBUG=gctrace=1 go run main.go
GODEBUG=schedtrace=1000 go run main.go
GODEBUG=allocfreetrace=1 go run main.go
```

> 這個範例程式非常小，像 `gctrace`、`schedtrace`、`scheddetail`、`scavtrace` 這類參數可能不一定會印出明顯資料；若要穩定觀察 GC 或 scheduler 行為，建議改用後文較重的示範程式。

## allocfreetrace

最小測試指令：

```bash
GODEBUG=allocfreetrace=1 go run main.go
```

對每次配置與釋放輸出摘要，並列出對應堆疊。適合追查異常配置或物件生命週期問題。

## clobberfree

最小測試指令：

```bash
GODEBUG=clobberfree=1 go run main.go
```

物件被 GC 釋放後，runtime 會用特殊內容覆寫記憶體，方便提早發現 use-after-free 類型問題。

## cgocheck

最小測試指令：

```bash
GODEBUG=cgocheck=0 go run main.go
```

控制 cgo 指標檢查。

- `cgocheck=0`：停用檢查。
- `cgocheck=1`：預設值，低成本檢查。
- 更完整的檢查通常需要搭配 `GOEXPERIMENT`，不是單靠 `GODEBUG` 完成。

## efence

最小測試指令：

```bash
GODEBUG=efence=1 go run main.go
```

每個物件都配置在獨立頁面上，且位址不重用。適合追查記憶體踩踏，但效能會明顯變差。

## gccheckmark

最小測試指令：

```bash
GODEBUG=gccheckmark=1 go run main.go
```

驗證 GC 並行標記階段。若第二次標記時發現遺漏的可達物件，runtime 會直接 panic。

## gcpacertrace

最小測試指令：

```bash
GODEBUG=gcpacertrace=1 go run main.go
```

輸出 GC pacer 的內部狀態，適合分析 GC 觸發節奏與 heap 目標控制。

## gcshrinkstackoff

最小測試指令：

```bash
GODEBUG=gcshrinkstackoff=1 go run main.go
```

停用 goroutine stack shrink。開啟後 stack 只能成長，不能回縮。

## gcstoptheworld

最小測試指令：

```bash
GODEBUG=gcstoptheworld=1 go run main.go
```

- `gcstoptheworld=1`：停用並行 GC，讓每次 GC 都變成 stop-the-world。
- `gcstoptheworld=2`：另外也停用 GC 後的並行 sweep。

## gctrace

最小測試指令：

```bash
GODEBUG=gctrace=1 go run main.go
```

每次 GC 都會輸出一行摘要，是最常用的 `GODEBUG` 參數之一。

範例輸出：

```text
gc 1 @0.115s 0%: 0.067+0.92+0.003 ms clock, 0.26+0.41/0.78/0.011+0.015 ms cpu, 4->4->0 MB, 5 MB goal, 4 P
gc 2 @0.194s 0%: 0.056+1.5+0.003 ms clock, 0.22+1.3/0.27/1.6+0.012 ms cpu, 4->4->0 MB, 5 MB goal, 4 P
```

欄位大意如下：

- `gc 1`：第幾次 GC。
- `@0.115s`：程式啟動後多久發生這次 GC。
- `0%`：累計 GC 時間占執行時間比例。
- `0.067+0.92+0.003 ms clock`：STW sweep termination、並行 mark/scan、STW mark termination 的 wall-clock 時間。
- `0.26+0.41/0.78/0.011+0.015 ms cpu`：各階段 CPU 時間。
- `4->4->0 MB`：GC 前 heap、GC 後 heap、存活 heap。
- `5 MB goal`：下一次 GC 的 heap 目標值。
- `4 P`：執行時使用的 processor 數量。

若輸出最後帶有 `(forced)`，代表這次 GC 是由 `runtime.GC()` 強制觸發。

## madvdontneed

最小測試指令：

```bash
GODEBUG=madvdontneed=1 go run main.go
```

控制記憶體歸還給作業系統時使用的策略。在 Linux 上，`madvdontneed=0` 會偏向使用 `MADV_FREE`，`madvdontneed=1` 則偏向 `MADV_DONTNEED`。

## memprofilerate

最小測試指令：

```bash
GODEBUG=memprofilerate=1 go run main.go
```

調整 `runtime.MemProfileRate`。設成 `0` 可停用 memory profiling。

## invalidptr

最小測試指令：

```bash
GODEBUG=invalidptr=0 go run main.go
```

`invalidptr=1` 是預設值。若 GC 或 stack copier 在 pointer 型別欄位中看到非法指標值，程式會直接崩潰。除錯舊程式時可暫時設成 `0`，但真正修法仍是移除錯誤指標內容。

## sbrk

最小測試指令：

```bash
GODEBUG=sbrk=1 go run main.go
```

以極簡配置器取代一般記憶體配置器與 GC，向作業系統要記憶體後不再回收。只適合特殊除錯情境。

## scavenge

最小測試指令：

```bash
GODEBUG=scavenge=1 go run main.go
```

啟用 scavenger 除錯模式，用來觀察 heap scavenger 的工作狀態。

## scavtrace

最小測試指令：

```bash
GODEBUG=scavtrace=1 go run main.go
```

大約每個 GC 週期輸出一行 scavenger 摘要，例如背景回收量、主動回收量、已歸還給 OS 的位址空間，以及實體記憶體使用率估計。

## scheddetail

`scheddetail=1` 需要搭配 `schedtrace=X` 一起使用：

最小測試指令：

```bash
GODEBUG=schedtrace=1000,scheddetail=1 go run main.go
```

範例程式：

```go
package main

import "sync"

func main() {
	var wg sync.WaitGroup
	wg.Add(10)

	for i := 0; i < 10; i++ {
		go func(wg *sync.WaitGroup) {
			defer wg.Done()

			var counter int
			for j := 0; j < 1e7; j++ {
				counter++
			}
		}(&wg)
	}

	wg.Wait()
}
```

範例輸出：

```text
SCHED 0ms: gomaxprocs=4 idleprocs=2 threads=6 spinningthreads=1 idlethreads=2 runqueue=0 gcwaiting=0 nmidlelocked=0 stopwait=0 sysmonwait=0
  P0: status=1 schedtick=1 syscalltick=0 m=0 runqsize=0 gfreecnt=0 timerslen=0
  P1: status=0 schedtick=2 syscalltick=0 m=-1 runqsize=0 gfreecnt=0 timerslen=0
  M0: p=0 curg=1 mallocing=0 throwing=0 preemptoff= locks=3 dying=0 spinning=false blocked=false lockedg=1
  G1: status=2(chan receive) m=0 lockedm=0
```

這類輸出會把 scheduler、`P`、`M`、`G` 的狀態全部攤開：

- `P`：processor，負責執行 goroutine 的邏輯處理器。
- `M`：machine，對應 OS thread。
- `G`：goroutine。

常見欄位：

- `status`：目前狀態。
- `schedtick`：調度次數。
- `syscalltick`：系統呼叫次數。
- `runqsize`：本地 run queue 長度。
- `spinning`：thread 是否處於自旋狀態。
- `lockedg` / `lockedm`：是否被綁定。

## schedtrace

最小測試指令：

```bash
GODEBUG=schedtrace=1000 go run main.go
```

每隔 `X` 毫秒輸出一行 scheduler 摘要。

範例輸出：

```text
SCHED 0ms: gomaxprocs=4 idleprocs=2 threads=4 spinningthreads=1 idlethreads=0 runqueue=0 [1 0 0 0]
SCHED 10ms: gomaxprocs=4 idleprocs=1 threads=7 spinningthreads=1 idlethreads=1 runqueue=0 [7 7 0 0]
SCHED 24ms: gomaxprocs=4 idleprocs=0 threads=8 spinningthreads=0 idlethreads=1 runqueue=0 [0 0 0 0]
```

欄位大意如下：

- `gomaxprocs`：目前可同時運作的 `P` 數量。
- `idleprocs`：閒置中的 `P` 數量。
- `threads`：OS thread 總數。
- `spinningthreads`：正在自旋尋找工作的 thread 數量。
- `idlethreads`：閒置 thread 數量。
- `runqueue`：全域 run queue 長度。
- `[1 0 0 0]`：各 `P` 本地 run queue 的 goroutine 數量。

如果需要更細的內容，直接搭配 `scheddetail=1` 即可。

## tracebackancestors

最小測試指令：

```bash
GODEBUG=tracebackancestors=5 go run main.go
```

讓 traceback 額外帶出 goroutine 建立時的祖先堆疊，`N` 代表最多往上追幾層。

## asyncpreemptoff

最小測試指令：

```bash
GODEBUG=asyncpreemptoff=1 go run main.go
```

停用訊號式非同步搶占。這會讓部分長迴圈變成長時間不可搶占，可能拖慢 GC 與 scheduler，但很適合用來隔離特定 preemption 相關問題。

## 常用組合

最常見的幾個參數如下：

- `gctrace=1`：看 GC 觸發頻率、停頓時間與 heap 變化。
- `schedtrace=1000`：看 scheduler 摘要。
- `schedtrace=1000,scheddetail=1`：看完整 G/P/M 狀態。
- `asyncpreemptoff=1`：排查搶占與 GC 交互影響。

另外，`net`、`net/http`、`crypto/tls` 等套件也有部份除錯行為會參考 `GODEBUG`，需要時可再查各套件文件。

## 參考資料

- [runtime package documentation](https://pkg.go.dev/runtime)
- [Go runtime source: `schedtrace`](https://github.com/golang/go/blob/go1.21.6/src/runtime/proc.go)
- [GODEBUG: A guide to Go debugging](https://blog.csdn.net/EDDYCJY/article/details/102426078)
