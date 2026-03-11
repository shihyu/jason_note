# Go 併發觀察與調試工具全覽

---

## 1. `go tool trace` — 執行追蹤視覺化

**白話說明：** 幫你錄下程式跑起來的「每一幀畫面」，像監視器一樣記錄哪個 goroutine 在哪個時間點做什麼事，最後用瀏覽器打開看時間軸。

**示意圖：**
```
時間軸 ──────────────────────────────────────>

goroutine 1  ██████░░░░░░░░░░░░░░░░██████
goroutine 2  ░░░░░░██████░░░░░░████░░░░░░
goroutine 3  ░░░░░░░░░░░░████░░░░░░░░░░░░

             ↑        ↑        ↑
           建立      阻塞    syscall

█ = 執行中  ░ = 等待/閒置
```

**安裝方式：** 內建，無需額外安裝

```go
// main.go
package main

import (
    "os"
    "runtime/trace"
    "sync"
)

func main() {
    // 建立 trace 輸出檔案
    f, _ := os.Create("trace.out")
    defer f.Close()

    // 開始錄製（程式執行期間所有事件都會被記錄）
    trace.Start(f)
    defer trace.Stop() // 程式結束時停止錄製

    var wg sync.WaitGroup
    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            // 這裡的工作會被 trace 記錄下來
        }(i)
    }
    wg.Wait()
    // 執行完畢，trace.out 已包含完整執行記錄
}
```

```bash
go run main.go              # 執行後產生 trace.out
go tool trace trace.out     # 開啟瀏覽器視覺化介面（自動在 http://127.0.0.1:PORT 開啟）
```

### 也可以轉成文字嗎？

可以，但分成兩種：

1. **事件明細文字**：把 trace 解析成一行一筆事件，適合 `grep`、存檔、快速看 goroutine / scheduler / GC 事件。
2. **pprof 風格摘要**：先從 trace 萃取一種 profile，再用 `go tool pprof -top` 看文字統計。

以下指令已在本機 repo 內的 Go 1.24.9 環境實測通過；較舊的 trace 格式對 `-d` 參數格式可能不同。

```bash
# 直接輸出解析後的事件文字
go tool trace -d=parsed trace.out > trace.txt

# 其他除錯格式
go tool trace -d=wire trace.out > trace-wire.txt
go tool trace -d=footprint trace.out > trace-footprint.txt

# 從 trace 匯出 scheduler latency profile，再看文字摘要
go tool trace -pprof=sched trace.out > sched.pprof
go tool pprof -top sched.pprof
```

`-pprof` 支援的類型：

```text
net
sync
syscall
sched
```

如果你的需求是「把 trace 內容轉成純文字保存或做命令列分析」，最直接的是 `-d=parsed`。如果你的需求是「看哪裡卡住最久」，通常先看 `-pprof=sched` 或 `-pprof=sync` 會比較快。

**可觀察：** Goroutine 生命週期、阻塞原因、Syscall、Channel 操作、GC 事件

### 延伸：`gotrace` 3D WebGL goroutine 視覺化

如果你想看更直覺、偏教學用途的 goroutine 動態視覺化，可以看 Ivan Daniluk 的 `gotrace`：

- Demo：<https://divan.dev/demos/workers2/>
- 文章：<https://divan.dev/posts/go_concurrency_visualize/>
- 原始碼：<https://github.com/divan/gotrace>

`gotrace` 不是另一套獨立追蹤格式，而是建立在 `go tool trace` 產生的 execution trace 之上，再把並發流程渲染成 3D WebGL 畫面。它特別適合拿來理解：

- worker pool / fan-out / fan-in
- ping-pong、timer、server handler 等常見並發模式
- `GOMAXPROCS` 變化下的平行度差異
- goroutine leak 長什麼樣子

這組視覺化的價值在於，你可以直接看到 goroutine 建立、阻塞、喚醒、channel 傳遞與生命週期如何在時間軸上展開，比只看文字或靜態圖更容易建立直覺。

要注意幾點：

- 這個專案的主要目標是教學，不是取代內建 trace UI。
- README 明確說它較適合小程式、短 trace；事件太多時 WebGL 視圖會變得混亂。
- 依 README，用自己的程式餵給 `gotrace` 時，通常需要搭配 patched Go runtime 或專案提供的 docker 流程。
- Repo 以 MIT license 釋出，適合拿來研究或延伸。

實務上可以這樣分工：

- 要做正式診斷、排查阻塞/GC/排程：先用 `go tool trace`
- 要教學、展示並發模式、幫新人建立心智模型：再用 `gotrace`

---

## 2. `pprof` — 效能剖析

**白話說明：** 就像健康檢查，程式跑著的同時，你可以隨時去問它「你 CPU 花在哪裡？記憶體用了多少？鎖搶成什麼樣？」透過 HTTP 端點取樣，不需要重啟程式。

**示意圖：**
```
你的程式 (port 6060)
      │
      ├── /debug/pprof/goroutine  ← 目前所有 goroutine 快照
      ├── /debug/pprof/mutex      ← 鎖競爭（誰在搶鎖？搶多久？）
      ├── /debug/pprof/block      ← 阻塞（goroutine 等 channel/鎖 多久？）
      └── /debug/pprof/profile    ← CPU 採樣（預設 30 秒）

鎖競爭示意：
  goroutine A ──▶ Lock() ─▶ 執行 ─▶ Unlock()
  goroutine B ──▶ Lock() ─▶ [等待...] ─▶ Unlock()
  goroutine C ──▶ Lock() ─▶ [等待更久...] ─▶ Unlock()
                             ↑
                         這段等待時間會出現在 mutex profile
```

```go
// pprof_demo.go
package main

import (
    "log"
    "net/http"
    _ "net/http/pprof"  // 匯入這個就會自動把 /debug/pprof 端點掛到 DefaultServeMux
    "runtime"
    "sync"
    "time"
)

func main() {
    // 預設關閉，必須手動啟用才能收集鎖競爭資料
    runtime.SetMutexProfileFraction(1) // 1 = 100% 取樣（生產環境建議調低，例如 5）
    runtime.SetBlockProfileRate(1)     // 1 奈秒採樣率（越小越詳細，但越耗 CPU）

    var mu sync.Mutex
    ch := make(chan struct{})

    // 製造 4 個 goroutine 互搶同一把鎖，讓 mutex/block profile 有資料可看
    for i := 0; i < 4; i++ {
        go func() {
            for {
                mu.Lock()
                time.Sleep(10 * time.Millisecond) // 持鎖期間睡眠 → 其他人都在等
                mu.Unlock()

                select {
                case ch <- struct{}{}: // 試著送資料到 channel
                case <-time.After(5 * time.Millisecond): // 5ms 後放棄
                }
            }
        }()
    }

    // 另起一個 goroutine 跑 HTTP server，不阻塞主流程
    go func() {
        log.Println("pprof listening on :6060")
        log.Println(http.ListenAndServe(":6060", nil))
    }()

    select {} // 讓程式永遠跑著（demo 用）
}
```

```bash
go run pprof_demo.go

# 另開一個 terminal
curl http://localhost:6060/debug/pprof/          # 確認端點正常

go tool pprof http://localhost:6060/debug/pprof/goroutine  # goroutine 快照
go tool pprof http://localhost:6060/debug/pprof/mutex      # 鎖競爭
go tool pprof http://localhost:6060/debug/pprof/block      # 阻塞分析

# pprof 互動介面常用指令
(pprof) top        # 顯示最耗資源的前幾項
(pprof) web        # 生成 SVG 圖（需安裝 graphviz：sudo apt install graphviz）
(pprof) list main  # 逐行顯示 main 函數的耗時

# CPU 採樣 10 秒（最常用）
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=10
```

`/debug/pprof/mutex` 與 `/debug/pprof/block` 需要先在程式內啟用（上方 `pprof_demo.go` 已包含）：

- `runtime.SetMutexProfileFraction(1)`
- `runtime.SetBlockProfileRate(1)`

---

## 3. `-race` 競態偵測器

**白話說明：** 兩個人同時改同一份文件，沒有先說好誰先改 → 結果可能壞掉。`-race` 就是偵測這種「沒協調好就同時讀寫」的問題，執行時自動標記警告。

**示意圖：**
```
        goroutine 1              goroutine 2
              │                       │
              ▼                       ▼
       counter++ (寫)          counter++ (寫)
              │                       │
              └──────────┬────────────┘
                         ▼
                   ❌ DATA RACE！
               （兩人同時改，誰的算數？）

正確做法（加鎖）：
  goroutine 1 ──▶ Lock ──▶ counter++ ──▶ Unlock
  goroutine 2 ──▶ [等] ──▶ Lock ──▶ counter++ ──▶ Unlock
                   ↑
              序列化，安全
```

```go
// race_example.go
package main

import "fmt"

func main() {
    counter := 0
    done := make(chan bool)

    go func() {
        counter++   // goroutine 裡寫 counter（沒有鎖保護）
        done <- true
    }()

    counter++       // 主 goroutine 也同時寫 counter（沒有鎖保護）
    <-done
    fmt.Println(counter)
    // 這兩個 counter++ 可能「同時」執行 → Data Race！
    // 結果可能是 1（某一個被覆蓋）或 2（碰巧正確）→ 不確定！
}
```

```bash
go run -race race_example.go
# 輸出：WARNING: DATA RACE，並顯示是哪兩個位置在衝突

go test -race ./...   # 對整個專案跑競態測試（CI 必備）
```

### 用 Channel 正確修復 Race

**關鍵原則：讓兩個 `counter++` 有明確的先後順序。**

```go
// ✅ 修復版：goroutine 先做，主程式等通知再做
package main

import "fmt"

func main() {
    counter := 0
    done := make(chan bool)

    go func() {
        counter++      // ① goroutine 先做
        done <- true   // ② 通知主程式（send）
    }()

    <-done             // ③ 等 goroutine 完成（receive）
    counter++          // ④ 主程式才做
    fmt.Println("counter:", counter)
}
```

```bash
go run -race good.go
# 輸出：counter: 2（無任何 WARNING，race 偵測通過）
```

**為何修復有效（happens-before 鏈）：**

```
goroutine: counter++
           ↓
goroutine: done <- true    ← channel send
                    ↓
           main: <-done    ← channel receive（Go 記憶體模型保證：send happens-before receive）
                    ↓
           main: counter++
```

**❌ vs ✅ 對比：**

| | ❌ 原始版本（Race） | ✅ 修復版本（無 Race） |
|---|---|---|
| 主程式 `counter++` | 在 `<-done` **之前** | 在 `<-done` **之後** |
| 兩個 `counter++` 的關係 | 無 happens-before，同時執行 | 有明確先後順序 |
| `-race` 結果 | `WARNING: DATA RACE` | 無警告，結果穩定為 `2` |

**Race detector 輸出解讀（原始版本）：**

```
WARNING: DATA RACE
Read at 0x00c000124008 by goroutine 7:
  main.main.func1()
      bad.go:10          ← goroutine 的 counter++

Previous write at 0x00c000124008 by main goroutine:
  main.main()
      bad.go:14          ← 主程式的 counter++（幾乎同時）

Found 1 data race(s)
exit status 66
```

---

## 4. `GODEBUG` 環境變數

**白話說明：** 不改程式碼，只用環境變數就能讓 Go runtime 在跑的時候「自言自語」把內部狀態印出來。像是 Scheduler 怎麼分配工作、GC 何時觸發、停頓多久。

**示意圖（schedtrace）：**
```
SCHED 500ms: gomaxprocs=4 idleprocs=1 threads=6 runqueue=3 [2 0 1 0]
│              │             │            │          │       │
│              │             │            │          │       └── 每個 P (processor) 的本地 runqueue 長度
│              │             │            │          └── 全域 runqueue 等待的 goroutine 數
│              │             │            └── OS 執行緒總數
│              │             └── 閒置的 P 數量
│              └── 最大 P 數（=CPU 核心數）
└── 程式啟動後的時間點

gctrace 示意：
  gc 3 @0.5s 1%: 0.1+2.3+0.05 ms clock, 4->4->1 MB, 8 MB goal, 4 P
                  │   │    │              │  │   │
              STW掃描 並發 STW結束       前→後→存活  下次觸發門檻
```

```go
// godebug_demo.go — 製造 GC 壓力和 goroutine 活動，讓 GODEBUG 輸出有資料
package main

import (
    "bytes"
    "runtime"
    "time"
)

func main() {
    jobs := make(chan []byte, 1024) // 帶緩衝的工作佇列

    // 4 個 worker goroutine 消費工作
    for i := 0; i < 4; i++ {
        go func() {
            for b := range jobs {
                _ = bytes.Count(b, []byte{1}) // 做點事，消耗 CPU
                time.Sleep(2 * time.Millisecond)
            }
        }()
    }

    // 主迴圈：快速製造大量記憶體分配 → 觸發多次 GC
    for i := 0; i < 200000; i++ {
        b := make([]byte, 32*1024) // 每次分配 32KB → GC 壓力
        jobs <- b
        if i%1000 == 0 {
            runtime.Gosched() // 主動讓出 CPU，讓 worker 有機會跑
        }
    }
    close(jobs)
    time.Sleep(2 * time.Second) // 等 worker 全部結束
}
```

```bash
# Scheduler 狀態：每 500ms 印一行，觀察 goroutine 分配情況
GODEBUG=schedtrace=500 go run godebug_demo.go

# 更詳細版本（含每個 goroutine 狀態）
GODEBUG=schedtrace=1000,scheddetail=1 go run godebug_demo.go

# GC 追蹤：每次 GC 印一行，觀察 STW 暫停時間
GODEBUG=gctrace=1 go run godebug_demo.go

# 關閉異步搶占（調試特定 goroutine 卡死問題時用）
GODEBUG=asyncpreemptoff=1 go run godebug_demo.go
```

---

## 5. `runtime` 套件 — 程式內部監控

**白話說明：** 直接在程式碼裡問 runtime「現在幾個 goroutine？記憶體用多少？」不需要外部工具，適合加在健康檢查 API 裡。

**示意圖：**
```
你的程式
   │
   ▼
runtime.NumGoroutine()  ──▶ 42     ← 現在有 42 個 goroutine 活著
runtime.NumCPU()        ──▶ 8      ← 機器有 8 個 CPU
runtime.GOMAXPROCS(0)   ──▶ 8      ← Go 最多用 8 個 P（0 = 只查詢不修改）
runtime.ReadMemStats()  ──▶ {
                               HeapAlloc: 4MB   ← 目前 heap 使用量
                               HeapSys:   8MB   ← 向 OS 借了多少
                               NumGC:     12    ← 已跑過幾次 GC
                            }
```

```go
// runtime_stats.go
package main

import (
    "fmt"
    "runtime"
)

func printStats() {
    fmt.Println("Goroutine 數量:", runtime.NumGoroutine()) // 所有活著的 goroutine
    fmt.Println("CPU 核心數:", runtime.NumCPU())           // 物理 CPU 數
    fmt.Println("GOMAXPROCS:", runtime.GOMAXPROCS(0))      // 傳 0 = 查詢當前值，不修改

    var ms runtime.MemStats
    runtime.ReadMemStats(&ms)  // 讀取記憶體統計（會短暫 STW，生產環境謹慎使用）
    fmt.Printf("Heap 使用: %v MB\n", ms.HeapAlloc/1024/1024) // 目前 heap 活著的物件佔用量
}

func main() {
    printStats()
}
```

```bash
go run runtime_stats.go
# 輸出範例：
# Goroutine 數量: 1
# CPU 核心數: 8
# GOMAXPROCS: 8
# Heap 使用: 0 MB
```

---

## 6. `goleak` — Goroutine 洩漏偵測 ⭐

**白話說明：** 測試結束時，goroutine 應該要全部結束。`goleak` 就是在測試結束時數人頭，如果還有 goroutine 沒退場，就報錯告訴你是哪個。

**示意圖：**
```
TestLeakyFunc 執行：
  ┌─────────────────────────────┐
  │ 測試開始                     │
  │   go func() {               │
  │     time.Sleep(1 hour)  ←── │── 這個 goroutine 永遠不結束
  │   }()                       │
  │                             │
  │ 測試結束                     │
  │   goleak.VerifyNone(t) ←── 數人頭：還有 1 個沒結束！
  └─────────────────────────────┘
  ❌ FAIL：找到洩漏的 goroutine

TestCleanFunc 執行：
  ┌─────────────────────────────┐
  │ go func() { close(done) }() │
  │ <-done  ← 等 goroutine 結束  │
  │ goleak.VerifyNone(t) ← 全部結束，OK
  └─────────────────────────────┘
  ✅ PASS
```

```bash
mkdir -p /tmp/go-goleak-demo && cd /tmp/go-goleak-demo
go mod init example.com/goleak-demo
go get go.uber.org/goleak
```

```go
// leak_test.go
package leakdemo

import (
    "testing"
    "time"
    "go.uber.org/goleak"
)

// 洩漏範例：測試結束時 goroutine 還活著 → 測試失敗
func TestLeakyFunc(t *testing.T) {
    defer goleak.VerifyNone(t) // 測試結束時自動檢查

    go func() {
        time.Sleep(time.Hour) // 這個 goroutine 不會在測試期間結束 → 洩漏！
    }()
    // 測試函數到這裡就結束了，但上面的 goroutine 還活著
}

// 正確範例：等 goroutine 結束再回傳
func TestCleanFunc(t *testing.T) {
    defer goleak.VerifyNone(t) // 測試結束時自動檢查

    done := make(chan struct{})
    go func() {
        defer close(done) // goroutine 結束時關閉 channel
        // 做完事情就結束，不會永遠等待
    }()
    <-done // 主動等 goroutine 結束，確保乾淨
}
```

```bash
go test -run TestLeakyFunc -v   # 看洩漏報告
go test -run TestCleanFunc -v   # 這個會通過

# TestLeakyFunc 輸出：
# --- FAIL: TestLeakyFunc
#     goleak.go:XX: found unexpected goroutines:
#     [Goroutine 7 in state sleep, with time.Sleep on top of the stack:...]
```

---

## 7. `dlv` (Delve) — Go 專用 Debugger ⭐

**白話說明：** 像在程式裡插眼線，可以暫停程式、看每個 goroutine 現在在做什麼、切換到不同 goroutine 看它的 call stack。特別適合調試「某個 goroutine 卡在哪裡」。

**示意圖：**
```
dlv debug .
   │
   ▼
程式暫停在入口點
   │
(dlv) goroutines        ← 列出所有 goroutine
   │
   │  [1] main.main() ← goroutine 1（主）
   │  [7] worker(1)   ← goroutine 7
   │  [8] worker(2)   ← goroutine 8
   │
(dlv) goroutine 7       ← 切換到 goroutine 7
(dlv) bt                ← 看它的 call stack（現在卡在哪行）
   │
   │  > main.worker() dlv_demo.go:8
   │    main.main()   dlv_demo.go:15
```

```go
// dlv_demo.go
package main

import (
    "fmt"
    "time"
)

func worker(id int) {
    for i := 0; i < 3; i++ {
        fmt.Printf("worker=%d i=%d\n", id, i)
        time.Sleep(500 * time.Millisecond) // 這裡可以設斷點觀察
    }
}

func main() {
    go worker(1) // 背景 goroutine
    worker(0)    // 主 goroutine 跑 worker(0)
}
```

```bash
go install github.com/go-delve/delve/cmd/dlv@latest

dlv debug .           # 啟動調試（自動設斷點在 main.main）
dlv attach <PID>      # 附加到已在跑的程式（不中斷服務）

# Delve 互動指令
(dlv) goroutines        # 列出所有 goroutine 及其狀態
(dlv) goroutine 18      # 切換到 goroutine 18
(dlv) bt                # 當前 goroutine 的 stack trace（卡在哪行）
(dlv) goroutines -t     # 所有 goroutine 的 stack trace（一次全看）
(dlv) break main.worker # 在 worker 函數設斷點
(dlv) continue          # 繼續執行到下一個斷點
(dlv) print id          # 印出變數 id 的值
```

---

## 8. `context` 超時監控模式 ⭐

**白話說明：** 給 goroutine 設一個「倒數計時器」，時間到了就通知它停下來。就像你叫外送，5 分鐘到了還沒來就取消訂單，不要一直傻等。

**示意圖：**
```
main()
  │
  ├── context.WithTimeout(5秒) ──▶ ctx（5秒後自動過期）
  │
  └── doWork(ctx)
        │
        ├── go func() {          ← 工作 goroutine
        │     sleep(10秒)         ← 需要 10 秒
        │     close(done)
        │   }()
        │
        └── select {
              case <-done:        ← 工作提早結束（這次不會發生）
                  return nil
              case <-ctx.Done():  ← 5 秒到了！
                  return error    ← 回傳超時錯誤
            }

時間軸：
  0s ──▶ 1s ──▶ 2s ──▶ 3s ──▶ 4s ──▶ 5s ──▶ ...
                                         ↑
                                   ctx.Done() 觸發
                                   工作被取消，不等 10s
```

```go
// context_timeout.go
package main

import (
    "context"
    "fmt"
    "log"
    "time"
)

// doWork 執行一個可能超時的工作
func doWork(ctx context.Context) error {
    done := make(chan struct{})

    go func() {
        // 實際工作（這裡故意模擬一個慢操作）
        time.Sleep(10 * time.Second) // 需要 10 秒，但 ctx 只給 5 秒
        close(done)
    }()

    select {
    case <-done:
        // 工作正常完成
        return nil
    case <-ctx.Done():
        // ctx 超時或被取消（ctx.Err() 說明原因）
        return fmt.Errorf("goroutine timeout: %w", ctx.Err())
    }
}

func main() {
    // 建立一個 5 秒後自動取消的 context
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel() // 養成好習慣：函數結束時一定呼叫 cancel，釋放資源

    if err := doWork(ctx); err != nil {
        log.Println("偵測到超時或卡死:", err)
        // 輸出：偵測到超時或卡死: goroutine timeout: context deadline exceeded
    }
}
```

```bash
go run context_timeout.go
# 預期輸出（約 5 秒後）：
# 偵測到超時或卡死: goroutine timeout: context deadline exceeded
```

---

## 9. `go test` 整合剖析 — 測試期間直接採樣

**白話說明：** 跑測試或 Benchmark 的時候，順手把效能資料錄下來。是定位「這段程式碼為什麼慢」最直接的方法，不需要另外改程式。

**示意圖：**
```
go test -bench=. -cpuprofile=cpu.prof
   │
   ├── 執行 BenchmarkWorker N 次
   │     ├── 第 1 次：worker(0)
   │     ├── 第 2 次：worker(1)
   │     └── 第 N 次：worker(N-1)
   │
   └── 同時採樣 CPU（每 10ms 記錄一次 call stack）
         │
         ▼
       cpu.prof
         │
go tool pprof cpu.prof
         │
(pprof) top ──▶ 顯示哪個函數最耗 CPU
   sha256.Sum256  45%   ← 這裡花最多時間！
   fmt.Sprintf    30%
   ...
```

```go
// profile_bench_test.go
package profiledemo

import (
    "crypto/sha256"
    "fmt"
    "testing"
)

// worker 是我們要剖析的函數
func worker(n int) [32]byte {
    return sha256.Sum256([]byte(fmt.Sprintf("job-%d", n)))
}

// BenchmarkWorker：測量 worker 的效能
// b.N 由 Go 自動決定要跑幾次（讓結果穩定）
func BenchmarkWorker(b *testing.B) {
    for i := 0; i < b.N; i++ {
        _ = worker(i) // _ 避免編譯器優化掉這個呼叫
    }
}

// TestWorker：確保 worker 功能正確
func TestWorker(t *testing.T) {
    got := worker(1)
    if got == ([32]byte{}) { // 確保不是空的 hash
        t.Fatal("unexpected zero hash")
    }
}
```

```bash
# CPU 剖析 + Benchmark（最常用）
go test -bench=. -benchmem -cpuprofile=cpu.prof ./...
go tool pprof cpu.prof
(pprof) top 10          # 前 10 個耗時函數
(pprof) top -cum        # 按累計時間排序（含子呼叫）
(pprof) list worker     # 逐行顯示 worker 函數的耗時
(pprof) web             # 生成 SVG 火焰圖（需 graphviz）

# Memory 剖析（看誰在大量配置記憶體）
go test -bench=. -memprofile=mem.prof ./...
go tool pprof -alloc_space mem.prof   # 所有分配（含已釋放的）
go tool pprof -inuse_space mem.prof   # 當前佔用

# 執行追蹤（輸出給 go tool trace 看時間軸）
go test -trace=trace.out ./...
go tool trace trace.out

# 同時開多種剖析（一次跑完，節省時間）
go test -bench=BenchmarkWorker -cpuprofile=cpu.prof -memprofile=mem.prof -trace=trace.out ./...
```

**可觀察：** 測試中的 CPU 熱點、記憶體分配來源、鎖競爭位置

---

## 10. `runtime/debug` + `runtime.Stack()` — 程式內 Stack Dump

**白話說明：** 程式卡死或崩潰時，你可以讓它「印出所有 goroutine 現在在哪裡、做什麼」。就像拍一張當下的快照。支援按 Ctrl+\ 或 kill -QUIT 觸發，生產環境必備。

**示意圖：**
```
正常情況：
  PID 1234 跑著...

按下 Ctrl+\ 或 kill -QUIT 1234：
  ↓
  SIGQUIT 信號
  ↓
  installSIGQUITDump() 的 goroutine 收到
  ↓
  印出所有 goroutine stack：

=== goroutine dump ===
goroutine 1 [running]:
main.main(...)
  /tmp/demo/main.go:45

goroutine 7 [sleep]:          ← goroutine 7 在睡覺
time.Sleep(0x77359400)
  /usr/local/go/src/runtime/time.go:195
main.main.func1(0x0)          ← 是哪個函數建立的
  /tmp/demo/main.go:32

goroutine 8 [sleep]:          ← goroutine 8 也在睡覺
...
```

```go
// stack_dump_demo.go
package main

import (
    "fmt"
    "os"
    "os/signal"
    "runtime"
    "runtime/debug"
    "syscall"
    "time"
)

// crashHandler：崩潰時印出當前 goroutine 的 stack（放在 recover 裡用）
func crashHandler() {
    debug.PrintStack() // 只印當前 goroutine 的 stack，直接輸出到 stderr
}

// dumpAllGoroutines：一次印出所有 goroutine 的 stack
func dumpAllGoroutines() {
    buf := make([]byte, 1<<20) // 準備 1 MB 緩衝區（goroutine 多的程式要夠大）
    n := runtime.Stack(buf, true) // true = 抓所有 goroutine（false = 只抓當前）
    fmt.Printf("=== goroutine dump ===\n%s\n", buf[:n])
}

// installSIGQUITDump：收到 SIGQUIT（Ctrl+\）時自動 dump
// 這是生產環境標準做法，不需要重啟程式就能看 goroutine 狀態
func installSIGQUITDump() {
    go func() {
        c := make(chan os.Signal, 1)
        signal.Notify(c, syscall.SIGQUIT)
        for range c { // 每次收到 SIGQUIT 都 dump 一次
            buf := make([]byte, 1<<20)
            n := runtime.Stack(buf, true)
            fmt.Fprintf(os.Stderr, "%s", buf[:n])
        }
    }()
}

func main() {
    installSIGQUITDump() // 安裝信號處理器

    // 控制 runtime 行為
    debug.SetMaxThreads(1000) // 最多 1000 個 OS 執行緒（超過 → panic，預設 10000）
    debug.SetGCPercent(50)    // heap 成長 50% 就觸發 GC（預設 100，即翻倍才觸發）

    // 製造一些 goroutine，方便 dump 時看到多個
    for i := 0; i < 3; i++ {
        go func(id int) {
            for {
                time.Sleep(2 * time.Second) // 這些 goroutine 會出現在 dump 裡
                fmt.Println("worker", id, "alive")
            }
        }(i)
    }

    time.Sleep(200 * time.Millisecond) // 等 goroutine 都跑起來
    crashHandler()       // 示範：印當前 goroutine stack
    dumpAllGoroutines()  // 示範：印所有 goroutine stack
    runtime.GC()         // 手動觸發 GC（搭配 debug.SetGCPercent 示範）

    if info, ok := debug.ReadBuildInfo(); ok {
        fmt.Println("Module:", info.Main.Path) // 印出 module 名稱
    }

    fmt.Println("PID:", os.Getpid(), "（可用 kill -QUIT <PID> 再次 dump）")
    select {} // 保持程式存活
}
```

```bash
go run stack_dump_demo.go

# 另開 terminal，用 PID 觸發 dump
kill -QUIT <PID>
# 或在前景程式按 Ctrl+\
```

**可觀察：** 所有 goroutine 當前 stack、GC 行為調整、執行緒上限控制

---

## 11. `expvar` — 輕量級即時監控

**白話說明：** 在程式裡掛一個 HTTP 端點，可以隨時用 `curl` 查「現在有幾個 goroutine？任務完成了幾個？佇列還有多少？」輸出是 JSON，比 pprof 輕量，適合生產環境長期開著。

**示意圖：**
```
你的程式 (port 6060)
    │
    └── GET /debug/vars ──▶ {
          "goroutine_count": 12,      ← 即時 goroutine 數
          "tasks_done": 1543,         ← 累計完成任務數
          "tasks_failed": 2,          ← 累計失敗數
          "queue_depth": 8,           ← 當前佇列深度
          "worker_status": {
            "worker_0": "running",    ← worker 0 忙碌中
            "worker_1": "idle"        ← worker 1 閒置
          },
          "memstats": { ... }         ← 自動附帶的記憶體統計
        }

更新頻率：變數值改變就立刻反映，curl 每次都拿最新值
```

```go
// expvar_demo.go
package main

import (
    "fmt"
    "expvar"
    "log"
    "net/http"
    "runtime"
    "time"
    _ "net/http/pprof" // 同時掛載 pprof，一個 port 兩用
)

// 在 package 層級宣告監控變數（全域，任何地方都能更新）
var (
    goroutineCount = expvar.NewInt("goroutine_count")   // 整數計數器
    tasksDone      = expvar.NewInt("tasks_done")         // 整數計數器
    tasksFailed    = expvar.NewInt("tasks_failed")       // 整數計數器
    queueDepth     = expvar.NewInt("queue_depth")        // 整數計數器
    workerStatus   = expvar.NewMap("worker_status")      // key-value map（可動態新增 key）
)

func worker(id int, jobs <-chan int) {
    // 設定 worker 狀態為 "running"（用 Func 讓值可以動態計算）
    workerStatus.Set(fmt.Sprintf("worker_%d", id), expvar.Func(func() any {
        return "running"
    }))

    for j := range jobs {
        _ = j
        tasksDone.Add(1) // 原子操作，不需要加鎖
    }

    // jobs channel 關閉後，worker 結束，更新狀態
    workerStatus.Set(fmt.Sprintf("worker_%d", id), expvar.Func(func() any {
        return "idle"
    }))
}

func main() {
    jobs := make(chan int, 16)

    // 啟動 2 個 worker
    for i := 0; i < 2; i++ {
        go worker(i, jobs)
    }

    // 生產者：持續丟工作進去
    go func() {
        for i := 0; ; i++ {
            jobs <- i
            queueDepth.Set(int64(len(jobs))) // 即時更新佇列深度
            if i%10 == 0 {
                tasksFailed.Add(1) // 模擬每 10 個任務有 1 個失敗
            }
            time.Sleep(100 * time.Millisecond)
        }
    }()

    // 定期更新 goroutine 計數（每秒更新）
    go func() {
        for {
            goroutineCount.Set(int64(runtime.NumGoroutine()))
            queueDepth.Set(int64(len(jobs)))
            time.Sleep(time.Second)
        }
    }()

    log.Println("expvar + pprof listening on :6060")
    log.Fatal(http.ListenAndServe(":6060", nil))
}
```

```bash
go run expvar_demo.go

# 另開 terminal 查詢指標
curl -s http://localhost:6060/debug/vars | jq '.goroutine_count, .tasks_done, .worker_status'
# 輸出：
# 12
# 1543
# {"worker_0": "running", "worker_1": "idle"}
```

**可觀察：** 自訂業務指標、即時 goroutine 數量、任務佇列深度，無額外 CPU 開銷

---

## 12. `go vet` — 靜態分析偵測併發陷阱

**白話說明：** 不跑程式，只看程式碼，自動找出常見的錯誤寫法。就像 code review 的自動化版本，特別擅長抓「Mutex 被複製」、「context cancel 沒呼叫」這類容易被人眼漏掉的問題。

**示意圖：**
```
copylocks 問題：
  type Worker struct { mu sync.Mutex }

  process(w Worker)     ← 傳值 = 複製整個 Worker，包括 mu 的狀態！
     │
     └── w.mu.Lock()   ← 鎖住的是「副本」，原本的 mu 完全不受影響
                           → 根本沒有保護到任何東西！

  ✅ 正確：process(w *Worker) ← 傳指標，操作同一個 mu

lostcancel 問題：
  ctx, _ := context.WithCancel(parent)  ← cancel 函數被 _ 丟掉了！
  return ctx
     │
     └── ctx 永遠不會被 cancel，資源洩漏！

  ✅ 正確：ctx, cancel := context.WithCancel(parent)
            defer cancel()
```

```go
// copylocks_demo.go
package vetdemo

import "sync"

type Worker struct {
    mu sync.Mutex
}

// ❌ 傳值：Worker 被複製，mu 的鎖狀態也被複製
//    go vet 會警告：passes lock by value: vetdemo.Worker contains sync.Mutex
func process(w Worker) {
    w.mu.Lock()
    defer w.mu.Unlock()
    // 注意：這鎖的是「複製品」，不是原本的 Worker！
}

// ✅ 傳指標：操作的是同一個 Worker，mu 正確共享
func processPtr(w *Worker) {
    w.mu.Lock()
    defer w.mu.Unlock()
}
```

```go
// lostcancel_demo.go
package vetdemo

import "context"

// ❌ cancel 被丟棄（用 _ 忽略），context 永遠無法被取消
//    go vet 會警告：the cancel function is not used on all paths
func leakedContext(parent context.Context) context.Context {
    ctx, _ := context.WithCancel(parent) // _ 丟掉了 cancel！
    return ctx
    // ctx 的 cancel 再也無法被呼叫 → 資源洩漏
}

// ✅ 正確做法：把 cancel 往上傳，讓呼叫者決定何時取消
func cleanContext(parent context.Context) (context.Context, context.CancelFunc) {
    return context.WithCancel(parent)
}
```

```go
// channel 方向錯誤（編譯期就報錯，不需要 go vet）
package main

// <-chan int 表示「只能從這個 channel 接收」
func send(ch <-chan int) {
    ch <- 1 // compile error: send to receive-only channel
}
```

```bash
go vet ./...          # 分析整個專案
go vet -v ./...       # 顯示執行了哪些分析器

# 預期看到：
# ./copylocks_demo.go:8:16: passes lock by value: vetdemo.Worker contains sync.Mutex
# ./lostcancel_demo.go:7:8: the cancel function is not used on all paths

# 進階：staticcheck（業界標準第三方工具，比 go vet 更嚴格）
go install honnef.co/go/tools/cmd/staticcheck@latest
staticcheck ./...
```

**可觀察：** Mutex 複製、lost cancel、部分併發誤用模式

---

## 工具選用速查表

| 問題場景 | 推薦工具 |
|---|---|
| Goroutine 執行順序異常 | `go tool trace` |
| 懷疑有 Data Race | `-race` |
| 鎖競爭嚴重，CPU 高 | `pprof mutex/block`、`go test -mutexprofile` |
| Goroutine 數量一直增長 | `goleak` + `runtime.NumGoroutine()` |
| 想暫停程序看 goroutine 狀態 | `dlv` |
| 生產環境即時監控 | `pprof HTTP endpoint` + `expvar` + `GODEBUG` |
| Goroutine 疑似卡死 | `context.WithTimeout` + `runtime.Stack()` |
| GC 暫停影響延遲 | `GODEBUG=gctrace=1` |
| Benchmark 效能問題 | `go test -cpuprofile` + `go test -trace` |
| 程式崩潰時抓 stack | `runtime.Stack()` + SIGQUIT handler |
| 程式碼靜態問題 | `go vet` + `staticcheck` |
| 低開銷業務指標監控 | `expvar` |

---

> 最常用的黃金組合：**`-race` + `pprof` + `go tool trace`**，三者涵蓋了從正確性到效能的完整調試需求。
>
> 生產環境推薦組合：**`expvar` + `pprof HTTP endpoint` + SIGQUIT `runtime.Stack()` handler**，零侵入持續可觀測。
