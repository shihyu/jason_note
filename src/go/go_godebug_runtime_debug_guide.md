# GODEBUG 環境變數與 Runtime 除錯指南

這份筆記以本機 `linux/amd64`、`go version go1.21.6 linux/amd64` 實測整理。

為了避免 `go run` 把編譯器自己的 runtime trace 混進輸出，本文範例一律先編譯再執行：

```bash
go build -o /tmp/godebug-demo ./tests/godebug_runtime_debug/main.go
go build -o /tmp/godebug-cgocheck ./tests/godebug_runtime_debug/cgocheck/main.go
```

如果要一次重跑本文全部範例，直接執行：

```bash
./tests/godebug_runtime_debug/verify_examples.sh
```

> 本文只覆蓋這份文件原本提到的旗標。是否支援、輸出格式、甚至行為，都可能隨 Go 版本改變；先以 `go doc runtime` 為準。

## allocfreetrace

作用：把每次配置與釋放都印出 stack trace，適合抓異常 allocation，缺點是輸出非常大。

已驗證指令：

```bash
GODEBUG=allocfreetrace=1 /tmp/godebug-demo gc 2>&1 | sed -n '1,14p'
```

實際觀察：

```text
tracealloc(0xc000030000, 0x80, *runtime.p)
goroutine 0 [idle]:
runtime.mallocgc(0x80, 0x498980, 0x1)
	/home/shihyu/go/src/runtime/malloc.go:1229 +0x707
runtime.makeslice(...)
runtime.procresize(0x10)
```

重點：這個旗標連 runtime 啟動期的 allocation 都會印，通常只適合配最小 repro。

## clobberfree

作用：GC 釋放物件時，用壞資料覆寫記憶體，目的是讓 use-after-free 類問題更早炸出來。

已驗證指令：

```bash
GODEBUG=clobberfree=1 /tmp/godebug-demo clobber
```

實際觀察：

```text
stale=41 41 41 41 41 41 41 41 41 41 41 41 41 41 41 41
```

重點：我用 `unsafe` 讀 stale pointer，沒有穩定觀察到覆寫痕跡。這類旗標比較適合搭配「原本就會偶發壞掉」的程式來放大錯誤，不適合拿 toy example 當 deterministic 證據。

## cgocheck

作用：檢查 cgo 呼叫時，是否把不合法的 Go pointer 傳進 C。

已驗證指令：

```bash
/tmp/godebug-cgocheck
GODEBUG=cgocheck=0 /tmp/godebug-cgocheck
```

實際觀察：

```text
panic: runtime error: cgo argument has Go pointer to unpinned Go pointer
```

```text
cgocheck passed
```

重點：

- `cgocheck=1` 是預設值，這個範例會直接 panic。
- `cgocheck=0` 會關掉檢查，範例可跑完。

## efence

作用：把 allocator 切到偏激模式，盡量讓物件獨立配置且位址不重用，用來追記憶體踩踏。

已驗證指令：

```bash
GODEBUG=efence=1 /tmp/godebug-demo addr
```

實際觀察：

```text
phase1_addr0=0xc000096000
phase1_addr1=0xc000098000
phase1_addr2=0xc00009a000
phase1_addr3=0xc00009c000
phase2_addr0=0xc00006c000
phase2_addr1=0xc00006e000
phase2_addr2=0xc000070000
phase2_addr3=0xc000072000
```

重點：小範例只能看到位址配置間距，真正價值在於讓原本難重現的 memory stomp 更容易變成 crash。

## gccheckmark

作用：額外驗證 concurrent mark。若第二輪檢查發現漏標記，runtime 會 panic。

已驗證指令：

```bash
GODEBUG=gccheckmark=1 /tmp/godebug-demo gc
```

實際觀察：

```text
heap_alloc=183024 heap_released=53616640 num_gc=6
```

重點：正常情況下不會多印任何東西；驗證點就是「沒 panic」。如果真的炸掉，通常代表 runtime 或 `unsafe`/cgo 互動有問題。

## gcpacertrace

作用：印出 GC pacer 內部狀態，適合看 GC 目標 heap 與 assist ratio。

已驗證指令：

```bash
GODEBUG=gcpacertrace=1 /tmp/godebug-demo gc
```

實際觀察：

```text
pacer: assist ratio=+3.130005e+000 (scan 0 MB in 4->4 MB) workers=4++0.000000e+000
pacer: 26% CPU (25 exp.) for 161952+11944+205128 B work (205128 B exp.) in 4718592 B -> 4743168 B
```

重點：這是 GC pacer 調節訊號，不是一般業務程式常看的資訊。

## gcshrinkstackoff

作用：關掉 goroutine stack shrink。stack 只會長，不會在 GC 時縮回去。

已驗證指令：

```bash
/tmp/godebug-demo stack
GODEBUG=gcshrinkstackoff=1 /tmp/godebug-demo stack
```

實際觀察：

```text
after_grow stack_inuse=4489216 stack_sys=4489216 num_gc=0
after_gc_while_parked stack_inuse=1507328 stack_sys=1507328 num_gc=2
after_worker_exit stack_inuse=524288 stack_sys=524288 num_gc=4
```

```text
after_grow stack_inuse=4489216 stack_sys=4489216 num_gc=0
after_gc_while_parked stack_inuse=4620288 stack_sys=4620288 num_gc=2
after_worker_exit stack_inuse=425984 stack_sys=425984 num_gc=4
```

重點：`gcshrinkstackoff=1` 時，中途 GC 後的 `stack_inuse` 幾乎不降，效果很直觀。

## gcstoptheworld

作用：把 GC 從 concurrent 模式改成 stop-the-world。

已驗證指令：

```bash
GODEBUG=gcstoptheworld=1,gctrace=1 /tmp/godebug-demo gc
GODEBUG=gcstoptheworld=2,gctrace=1 /tmp/godebug-demo gc
```

實際觀察：

```text
gc 1 @0.000s 2%: 0.006+0.081+0.002 ms clock, 0.10+0/0.15/0+0.046 ms cpu, 4->4->4 MB, 4 MB goal, 16 P
```

```text
fatal error: failed to set sweep barrier
```

重點：

- `gcstoptheworld=1` 在本機可正常跑，搭配 `gctrace=1` 最容易看。
- `gcstoptheworld=2` 在這台機器的 `go1.21.6` 上直接炸出 `failed to set sweep barrier`；這是實測結果，不要在正式環境亂開。

## gctrace

作用：每次 GC 印一行摘要，最常用。

已驗證指令：

```bash
GODEBUG=gctrace=1 /tmp/godebug-demo gc
```

實際觀察：

```text
gc 1 @0.000s 3%: 0.006+0.073+0.002 ms clock, 0.10+0.043/0.11/0+0.035 ms cpu, 4->4->4 MB, 4 MB goal, 0 MB stacks, 0 MB globals, 16 P
gc 5 @0.001s 5%: 0.012+0.041+0.002 ms clock, 0.19+0/0.067/0+0.037 ms cpu, 48->48->0 MB, 72 MB goal, 0 MB stacks, 0 MB globals, 16 P (forced)
```

欄位速讀：

- `gc 5`：第 5 次 GC。
- `@0.001s`：程式啟動後多久觸發。
- `48->48->0 MB`：GC 前 heap、GC 後 heap、live heap。
- `72 MB goal`：下一輪 GC 的 heap 目標。
- `(forced)`：這次 GC 是 `runtime.GC()` 或 `debug.FreeOSMemory()` 強制觸發。

## madvdontneed

作用：控制 Go 把記憶體還給 Linux 時，偏向用 `MADV_FREE` 還是 `MADV_DONTNEED`。

已驗證指令：

```bash
GODEBUG=madvdontneed=0 /tmp/godebug-demo rss
GODEBUG=madvdontneed=1 /tmp/godebug-demo rss
```

實際觀察：

```text
after_free VmRSS:	  269420 kB heap_released=271671296 heap_idle=271671296
```

```text
after_free VmRSS:	    7092 kB heap_released=271663104 heap_idle=271663104
```

重點：

- `madvdontneed=0` 時，RSS 幾乎不降，代表 Linux 還沒真的回收實體頁面。
- `madvdontneed=1` 時，RSS 直接掉回幾 MB，觀察最明顯。

## memprofilerate

作用：理論上會更新 `runtime.MemProfileRate`。

已驗證指令：

```bash
/tmp/godebug-demo memprofilerate
GODEBUG=memprofilerate=1 /tmp/godebug-demo memprofilerate
```

實際觀察：

```text
MemProfileRate=0
MemProfileRate=0
```

重點：這台機器的 `go1.21.6` 實測沒有看到 `GODEBUG=memprofilerate=1` 改變值，和 `go doc runtime` 敘述不一致；如果你真的要靠它做 profiling，先在目標機器再驗一次。

## invalidptr

作用：當 GC 或 stack copier 在 pointer 欄位看到非法位址時，是否直接崩潰。

已驗證指令：

```bash
/tmp/godebug-demo invalidptr
GODEBUG=invalidptr=0 /tmp/godebug-demo invalidptr
```

實際觀察：

```text
runtime: bad pointer in frame main.runInvalidPtr at 0xc00009eea0: 0x1
fatal error: invalid pointer found on stack
```

```text
forcing GC
survived
```

重點：預設值就是 `invalidptr=1`。除錯老程式可以暫時設 `0`，但根本修法還是把壞指標清掉。

## sbrk

作用：把 allocator/GC 換成超簡化版本，只拿記憶體、不回收。

已驗證指令：

```bash
GODEBUG=sbrk=1 /tmp/godebug-demo rss
```

實際觀察：

```text
before_alloc VmRSS:	    1752 kB
after_alloc VmRSS:	  264028 kB
after_free VmRSS:	  264376 kB
```

重點：即使把大物件放掉並強制 GC，RSS 也幾乎不掉，符合「拿了就不還」的描述。

## scavenge

作用：這是舊文章裡常見的名稱，但在本機 `go1.21.6` 的 `go doc runtime` 裡沒有 `scavenge` 這個 `GODEBUG` 項目。

已驗證指令：

```bash
go doc runtime | rg -n 'scavtrace|scavenge'
```

實際觀察：

```text
162:    scavtrace: setting scavtrace=1 causes the runtime to emit a single line to standard
```

重點：目前請改查 `scavtrace`，不要把 `scavenge=1` 當成現行文件支援的正式旗標。

## scavtrace

作用：每個 GC 週期附近印一行 scavenger 摘要。

已驗證指令：

```bash
GODEBUG=scavtrace=1 /tmp/godebug-demo rss
```

實際觀察：

```text
scav 0 KiB work (bg), 239576 KiB work (eager), 265352 KiB now, 96% util (forced)
after_free VmRSS:	    7108 kB heap_released=271687680 heap_idle=271704064
```

重點：`bg` 是背景回收，`eager` 是主動回收；最後的 `(forced)` 代表這輪是 `debug.FreeOSMemory()` 逼出來的。

## scheddetail

作用：和 `schedtrace=X` 搭配，列出 `P`、`M`、`G` 詳細狀態。

已驗證指令：

```bash
GODEBUG=schedtrace=500,scheddetail=1 /tmp/godebug-demo sched
```

實際觀察：

```text
SCHED 508ms: gomaxprocs=4 idleprocs=4 threads=5 spinningthreads=0 needspinning=0 idlethreads=3 runqueue=0 gcwaiting=false
  P0: status=0 schedtick=8 syscalltick=0 m=nil runqsize=0 gfreecnt=1 timerslen=1
  M0: p=nil curg=nil mallocing=0 throwing=0 preemptoff= locks=0 dying=0 spinning=false blocked=true lockedg=nil
  G1: status=4(sleep) m=nil lockedm=nil
```

重點：

- `P`：邏輯 processor。
- `M`：OS thread。
- `G`：goroutine。
- 這個輸出很長，通常只在 scheduler 問題才開。

## schedtrace

作用：每隔 `X` 毫秒印一行 scheduler 摘要。

已驗證指令：

```bash
GODEBUG=schedtrace=500 /tmp/godebug-demo sched
```

實際觀察：

```text
SCHED 508ms: gomaxprocs=4 idleprocs=4 threads=5 spinningthreads=0 needspinning=0 idlethreads=3 runqueue=0 [0 0 0 0]
SCHED 1015ms: gomaxprocs=4 idleprocs=4 threads=5 spinningthreads=0 needspinning=0 idlethreads=3 runqueue=0 [0 0 0 0]
```

重點：看整體 scheduler 壓力先開它，不夠再升級到 `scheddetail=1`。

## tracebackancestors

作用：讓 panic/traceback 額外帶出 goroutine 是被誰建立的。

已驗證指令：

```bash
GODEBUG=tracebackancestors=5 /tmp/godebug-demo traceback
```

實際觀察：

```text
panic: traceback demo

goroutine 8 [running]:
main.levelTwo.func1()
created by main.levelTwo in goroutine 7
[originating from goroutine 7]:
main.levelTwo(...)
created by main.levelOne
[originating from goroutine 6]:
main.levelOne(...)
```

重點：排 goroutine 泄漏、背景 worker 建立鏈時非常好用。

## asyncpreemptoff

作用：關掉 signal-based asynchronous preemption。CPU-bound loop 會變得更不容易被搶占。

已驗證指令：

```bash
/tmp/godebug-demo asyncpreempt
GODEBUG=asyncpreemptoff=1 /tmp/godebug-demo asyncpreempt
```

實際觀察：

```text
secondary=34ms
loop=218ms
```

```text
loop=214ms
secondary=224ms
```

重點：預設情況下，第二個 goroutine 會在 busy loop 結束前搶到 CPU；`asyncpreemptoff=1` 之後，它被拖到 loop 結束後才跑。

## 常用組合

- `gctrace=1`：先看 GC 頻率與 pause。
- `gcpacertrace=1`：GC pacing 問題再往下看。
- `schedtrace=500`：先看 scheduler 摘要。
- `schedtrace=500,scheddetail=1`：追 goroutine/thread 狀態。
- `tracebackancestors=5`：panic 時追 goroutine 建立鏈。
- `madvdontneed=1`：看 RSS 是否真的掉下來。
- `asyncpreemptoff=1`：隔離 preemption 相關問題。

## 參考

- `go doc runtime`
- `tests/godebug_runtime_debug/main.go`
- `tests/godebug_runtime_debug/cgocheck/main.go`
- `tests/godebug_runtime_debug/verify_examples.sh`
