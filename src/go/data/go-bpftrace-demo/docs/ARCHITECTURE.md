# go-bpftrace-demo 架構與原理說明

## 目錄

1. [bpftrace 是什麼](#bpftrace-是什麼)
2. [uprobe 原理](#uprobe-原理)
3. [Go 函數與符號表](#go-函數與符號表)
4. [防止 inline 的兩種方法](#防止-inline-的兩種方法)
5. [追蹤 Go Runtime 函數](#追蹤-go-runtime-函數)
6. [系統整體架構](#系統整體架構)
7. [資料流程](#資料流程)
8. [範例程式結構](#範例程式結構)
9. [Makefile 目標說明](#makefile-目標說明)
10. [詳細使用方法](#詳細使用方法)
11. [bpftrace 腳本語法詳解](#bpftrace-腳本語法詳解)
12. [輸出範例](#輸出範例)

---

## bpftrace 是什麼

`bpftrace` 是 Linux 上基於 **eBPF (extended Berkeley Packet Filter)** 的高階追蹤工具，讓你在不修改程式碼、不重新編譯、不重啟程序的情況下，動態觀察任何正在執行的程序。

```
傳統觀察方式（需要改動程式）：
  程式碼 ──> 加 printf/log ──> 重新編譯 ──> 重啟程序 ──> 觀察輸出

bpftrace 方式（零侵入）：
  程式照常執行 ──> bpftrace 掛載 probe ──> 核心攔截函數 ──> 輸出資訊
```

### eBPF 核心機制

```
使用者空間                        核心空間
┌──────────────────┐             ┌──────────────────────────────┐
│                  │             │                              │
│  bpftrace 腳本   │──編譯──────>│  eBPF 字節碼                 │
│                  │             │  ┌──────────────────────┐    │
│  uprobe:./myapp  │             │  │ Verifier (安全檢查)   │    │
│  :main.Step1 {   │             │  │ JIT Compiler (最佳化) │    │
│    printf(...)   │             │  └──────────────────────┘    │
│  }               │             │             │                │
│                  │             │             v                │
│                  │<──輸出──────│  掛載到 uprobe 點            │
└──────────────────┘             └──────────────────────────────┘
```

---

## uprobe 原理

**uprobe (User-space Probe)** 是 Linux 核心提供的機制，用來在使用者空間程序的任意位址插入「偵測點」。

### 插入機制

```
程式二進位檔 (ELF)
┌─────────────────────────────────────┐
│ .text section                       │
│                                     │
│  0x1234: PUSH rbp          <── 原始指令
│  0x1235: MOV rbp, rsp               │
│  0x1237: ...                        │
│                                     │
│       uprobe 掛載後                 │
│                                     │
│  0x1234: INT3 (斷點指令)   <── 替換為中斷
│  0x1235: MOV rbp, rsp               │
│  0x1237: ...                        │
└─────────────────────────────────────┘
         │
         │ 程式執行到此處
         v
┌─────────────────────────────────────┐
│ 核心處理                            │
│  1. 攔截 INT3 中斷                  │
│  2. 執行 eBPF handler               │
│  3. 還原原始指令並繼續執行           │
└─────────────────────────────────────┘
```

### uretprobe（函數返回點追蹤）

```
函數執行時序：

  uprobe ──> [函數開始]──────────────>[函數結束] ──> uretprobe
     │                                                    │
     │  記錄進入時間 t1                    記錄離開時間 t2 │
     │                                                    │
     └────────────── 耗時 = t2 - t1 ─────────────────────┘
```

---

## Go 函數與符號表

Go 編譯後的二進位檔保留完整的函數符號，bpftrace 可以直接用函數名稱定位。

```
Go 原始碼                    編譯產物 (ELF)
┌─────────────────┐         ┌────────────────────────────┐
│ package main    │         │ Symbol Table (.symtab)     │
│                 │ 編譯    │                            │
│ func Step1(...) │───────> │ main.Step1  @ 0x4a1230    │
│ func Step2(...) │         │ main.Step2  @ 0x4a1290    │
│ func main()     │         │ main.main   @ 0x4a12f0    │
│                 │         │                            │
└─────────────────┘         └────────────────────────────┘
```

### `//go:noinline` 的重要性

```go
//go:noinline          // ← 關鍵指令
func Step1(msg string) {
    fmt.Println("執行步驟 1:", msg)
}
```

```
沒有 noinline（函數被內聯展開）：
  main.main:
    ├── fmt.Println("執行步驟 1: Hello")  ← Step1 的程式碼被直接嵌入
    └── fmt.Println("執行步驟 2，次數: 42")

  ↓ bpftrace 找不到 main.Step1 符號！

加上 noinline（函數保留獨立符號）：
  main.main:
    ├── CALL main.Step1    ← 真正的函數呼叫
    └── CALL main.Step2

  ↓ bpftrace 可以成功掛載 uprobe:./myapp:main.Step1
```

---

## 防止 inline 的兩種方法

Go 編譯器預設會將小函數內聯展開（inline），導致函數符號從二進位檔消失，bpftrace 無法掛載 uprobe。有兩種方法可以防止這件事。

### 實測驗證

以下測試移除 `//go:noinline` 後，分別用三種方式編譯，透過 `nm` 與 `bpftrace -l` 確認符號是否存在。

**情況 1：有 `//go:noinline`（原始狀態）**

```bash
go build -o myapp_noinline .
nm myapp_noinline | grep -E "main\.(Step1|Step2)"
```

```
0000000000491de0 T main.Step1
0000000000491e80 T main.Step2
```

**情況 2：無任何保護，預設編譯**

```bash
go build -gcflags='-m' -o myapp_inline .
# 輸出：
#   ./main.go:8:6:  can inline Step1
#   ./main.go:18:8: inlining call to Step1   ← 被展開進 main()
nm myapp_inline | grep -E "main\.(Step1|Step2)"
# （無輸出）← 符號消失
```

**情況 3：無 `//go:noinline`，加 `-gcflags='-l'`**

```bash
go build -gcflags='-l' -o myapp_gcflag .
nm myapp_gcflag | grep -E "main\.(Step1|Step2)"
```

```
0000000000491e40 T main.Step1
0000000000491ee0 T main.Step2
```

### bpftrace probe 驗證結果

```bash
sudo bpftrace -l 'uprobe:./myapp_noinline:main.*' | grep -E "Step1|Step2"
# uprobe:./myapp_noinline:main.Step1
# uprobe:./myapp_noinline:main.Step2   ✅

sudo bpftrace -l 'uprobe:./myapp_inline:main.*' | grep -E "Step1|Step2"
# （無輸出）                            ❌ 無法追蹤

sudo bpftrace -l 'uprobe:./myapp_gcflag:main.*' | grep -E "Step1|Step2"
# uprobe:./myapp_gcflag:main.Step1
# uprobe:./myapp_gcflag:main.Step2     ✅
```

### 兩種方法比較

| | `//go:noinline` | `-gcflags='-l'` |
|---|---|---|
| 作用範圍 | 僅指定函數 | 全專案所有函數 |
| 效能影響 | 僅該函數略降 | 整體效能下降 |
| 修改原始碼 | 需要 | 不需要 |
| 意圖明確性 | 高（讀 code 即知） | 低（需看 build 指令） |
| 適合情境 | production + trace 並存 | 臨時 debug / 分析 |

```
//go:noinline（精準）              -gcflags='-l'（全域）
────────────────────────────────   ────────────────────────────────
只有目標函數保留符號                所有函數都保留符號（含標準函式庫）
其餘函數仍可被最佳化                全程式禁止 inline，效能全面下降
長期維護首選                        不改原始碼的臨時追蹤首選
```

> **結論**：需要長期維護的程式用 `//go:noinline`；臨時追蹤不想動原始碼則用 `go build -gcflags='-l'`。

---

## 追蹤 Go Runtime 函數

Go 二進位檔靜態連結 runtime，編譯後包含 **1291 個** `runtime.*` 符號，全部都可用 uprobe 追蹤，無需任何額外設定。

```bash
nm ./myapp | grep -c "T runtime."
# 1291
```

### Go 1.17+ Register ABI 注意事項

Go 1.17 起改用暫存器傳遞參數（register-based calling convention），bpftrace 讀取函數參數時不能用 `arg0`，要改用 `reg("ax")`。

```
Go 1.16 以前（stack ABI）   Go 1.17 以後（register ABI）
────────────────────────    ────────────────────────────
arg0 = 第一個參數            reg("ax") = 第一個整數參數
arg1 = 第二個參數            reg("bx") = 第二個整數參數
...                          ...

bpftrace: arg0 ✅            bpftrace: arg0 ❌ → reg("ax") ✅
```

### 可追蹤的 Runtime 類別

```
runtime.*  （1291 個符號）
├── goroutine  runtime.newproc / runtime.goexit0 / runtime.gopark / runtime.schedule
├── GC         runtime.gcStart / runtime.gcMarkTermination / runtime.mallocgc
├── 記憶體      runtime.mallocgc / runtime.(*fixalloc).alloc
├── 排程器      runtime.schedule / runtime.preemptone / runtime.park_m
└── 系統呼叫    runtime.entersyscall / runtime.exitsyscall

time.*     （4 個符號）
└── time.Sleep / time.Now / time.runtimeNano
```

### 實測範例

#### 1. 追蹤 goroutine 排程

```bash
sudo bpftrace -e '
uprobe:./myapp:runtime.schedule {
    printf("schedule: tid=%d\n", curtask->pid);
}
'
```

```
Attaching 1 probe...
schedule: tid=1063282
schedule: tid=1063286
schedule: tid=1063287
```

#### 2. 追蹤 Heap 記憶體分配（mallocgc）

> Go 1.17+ 用 `reg("ax")` 讀取 size 參數

```bash
sudo bpftrace -e '
uprobe:./myapp:runtime.mallocgc {
    @alloc_size = hist(reg("ax"));
}
END { print(@alloc_size); }
'
```

```
@alloc_size:
[16, 32)               5 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[32, 64)               2 |@@@@@@@@@@@@@@@@@@@@                                |
[128, 256)             2 |@@@@@@@@@@@@@@@@@@@@                                |
```

#### 3. 追蹤 time.Sleep 實際參數

```bash
sudo bpftrace -e '
uprobe:./myapp:time.Sleep {
    printf("[time.Sleep] duration=%lld ms\n", reg("ax") / 1000000);
}
'
```

```
Attaching 1 probe...
[time.Sleep] duration=2000 ms
[time.Sleep] duration=2000 ms
```

#### 4. 綜合追蹤：App 函數 + Runtime 統計

```bash
sudo bpftrace -e '
uprobe:./myapp:main.Step1       { printf("[app]     Step1  elapsed=%llu ms\n", elapsed/1000000); }
uprobe:./myapp:main.Step2       { printf("[app]     Step2  elapsed=%llu ms\n", elapsed/1000000); }
uprobe:./myapp:time.Sleep       { printf("[runtime] Sleep %lld ms\n", reg("ax")/1000000); }
uprobe:./myapp:runtime.schedule { @sched_count = count(); }
uprobe:./myapp:runtime.mallocgc { @alloc_bytes = sum(reg("ax")); }
END {
    print(@sched_count);
    print(@alloc_bytes);
}
'
```

```
Attaching 6 probes...
[app]     Step1  elapsed=915 ms
[app]     Step2  elapsed=916 ms
[runtime] Sleep 2000 ms
[app]     Step1  elapsed=2916 ms
[app]     Step2  elapsed=2916 ms
[runtime] Sleep 2000 ms

--- 統計 ---
@sched_count: 5
@alloc_bytes: 336
```

### 常用 Runtime Probe 速查表

| Probe | 說明 | 參數（register ABI） |
|-------|------|----------------------|
| `runtime.mallocgc` | heap 分配 | `reg("ax")` = size (bytes) |
| `runtime.schedule` | goroutine 排程點 | — |
| `runtime.newproc` | 建立新 goroutine | — |
| `runtime.goexit0` | goroutine 結束 | — |
| `runtime.gopark` | goroutine 進入等待 | — |
| `runtime.gcStart` | GC 開始 | — |
| `runtime.gcMarkTermination` | GC STW 結束 | — |
| `time.Sleep` | 程式呼叫 Sleep | `reg("ax")` = duration (ns) |

---

## 系統整體架構

```
┌─────────────────────────────────────────────────────────────┐
│                       使用者空間                             │
│                                                             │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │   myapp (目標程序)    │    │   bpftrace (觀察者)      │  │
│  │                      │    │                          │  │
│  │  main() ─────────────┼────┼──> uprobe:main.main      │  │
│  │    │                 │    │                          │  │
│  │    ├── Step1("Hello")┼────┼──> uprobe:main.Step1     │  │
│  │    │        │        │    │    uretprobe:main.Step1  │  │
│  │    │      stdout     │    │                          │  │
│  │    │                 │    │                          │  │
│  │    └── Step2(42) ────┼────┼──> uprobe:main.Step2     │  │
│  │             │        │    │    uretprobe:main.Step2  │  │
│  │           stdout     │    │                          │  │
│  │                      │    │    printf() ─────────────┼──┼──> 終端機輸出
│  │  time.Sleep(2s)      │    │                          │  │
│  └──────────────────────┘    └──────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                     eBPF 機制 (核心)
                            │
┌─────────────────────────────────────────────────────────────┐
│                         核心空間                             │
│                                                             │
│   uprobe handler ──> eBPF VM ──> map/printf ──> perf buffer│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 資料流程

### 正常執行流程

```
make run
  │
  └──> ./myapp 啟動
         │
         v
    ┌────────────────────────┐
    │  main() 無限迴圈        │
    │  ┌──────────────────┐  │
    │  │  1. Step1("Hello")│  │──> stdout: "執行步驟 1: Hello"
    │  │  2. Step2(42)    │  │──> stdout: "執行步驟 2，次數: 42"
    │  │  3. Sleep(2s)    │  │
    │  └──────────────────┘  │
    │         重複             │
    └────────────────────────┘
```

### bpftrace trace-smoke 自動化流程

```
make trace-smoke
  │
  ├──1. make run-bg ──> ./myapp 在背景執行
  │         │               └──> PID 寫入 tmp/myapp.pid
  │         │               └──> stdout 導向 tmp/myapp_stdout.log
  │         v
  ├──2. bpftrace 開始追蹤 (3 秒)
  │         │
  │         │   uprobe 命中 ──> printf 輸出
  │         │
  │         └──> 3 秒後 timeout 自動結束
  │               └──> 結果寫入 tmp/trace_smoke.log
  │
  ├──3. make stop-bg ──> 讀 PID ──> kill -9 ──> 刪除 PID 檔
  │
  └──4. cat tmp/trace_smoke.log  ──> 顯示 trace 結果
```

### 耗時追蹤資料流 (trace-latency)

```
Step1 函數進入
  │
  ├──> uprobe 觸發
  │       └──> @step1[tid] = nsecs   (記錄進入時間戳，以 thread ID 為 key)
  │
  │    [函數執行中...]
  │
  └──> uretprobe 觸發
          └──> 耗時 = nsecs - @step1[tid]
          └──> printf("Step1 耗時: %llu us\n", 耗時 / 1000)
          └──> delete(@step1[tid])   (清除 map 條目)
```

---

## 範例程式結構

```
go-bpftrace-demo/
├── main.go              # 主程式：Step1/Step2/Allocate/Worker + goroutine
├── main_test.go         # 行為測試：驗證四個函數的輸出
├── Makefile             # 建置 + app/runtime bpftrace 追蹤目標
├── go.mod               # Go 模組定義
├── plan.md              # 專案計畫
├── README.md            # 快速說明
└── docs/
    ├── ARCHITECTURE.md  # 本文件：架構與原理
    └── (tmp/ 由 Makefile 在執行時自動建立)
```

### main.go 核心設計

每個函數都對應一個可觀察的 runtime 行為：

```go
//go:noinline  // 保留符號供 uprobe 使用
func Step1(msg string) {
    fmt.Println("執行步驟 1:", msg)       // → uprobe:main.Step1
}

//go:noinline
func Step2(count int) {
    fmt.Println("執行步驟 2，次數:", count) // → uprobe:main.Step2
}

// Allocate 明確觸發 runtime.mallocgc，供 bpftrace 觀察 heap 分配
//go:noinline
func Allocate(n int) []byte {
    buf := make([]byte, n)               // → uprobe:runtime.mallocgc
    fmt.Printf("分配記憶體: %d bytes\n", n)
    return buf
}

// Worker 在獨立 goroutine 執行，觸發 runtime.newproc 可被觀察
//go:noinline
func Worker() {
    fmt.Println("Worker goroutine 執行中") // → uprobe:main.Worker
}

func main() {
    // 啟動背景 goroutine → 觸發 runtime.newproc
    go func() {
        for {
            Worker()
            time.Sleep(3 * time.Second)  // → time.Sleep duration=3000ms
        }
    }()

    for {
        Step1("Hello")
        Step2(42)
        _ = Allocate(256)               // → runtime.mallocgc size=256
        time.Sleep(2 * time.Second)     // → time.Sleep duration=2000ms
    }
}
```

### 函數 ↔ 可觀察 Runtime 事件對應表

| 函數 | 觸發的 Runtime 事件 | bpftrace probe |
|------|---------------------|----------------|
| `Step1` | — | `uprobe:main.Step1` |
| `Step2` | — | `uprobe:main.Step2` |
| `Allocate` | heap 分配 | `uprobe:runtime.mallocgc` |
| `Worker` | goroutine 執行 | `uprobe:main.Worker` |
| `go func(){}()` | goroutine 建立 | `uprobe:runtime.newproc` |
| `time.Sleep(2s/3s)` | goroutine 掛起 | `uprobe:time.Sleep` |
| 排程器 | goroutine 切換 | `uprobe:runtime.schedule` |

---

## Makefile 目標說明

### 基本操作

| 目標 | 說明 | 需要 sudo |
|------|------|-----------|
| `make` | 顯示說明 | 否 |
| `make build` | 編譯成 `./myapp` | 否 |
| `make run` | 前景執行 | 否 |
| `make test` | 執行行為測試 | 否 |
| `make clean` | 清除產物與暫存 | 否 |

### App 層追蹤

| 目標 | 說明 | 需要 sudo |
|------|------|-----------|
| `make trace-list` | 列出所有 `main.*` probe 符號 | 是 |
| `make trace-main` | 追蹤 `main.main` | 是 |
| `make trace-step1` | 追蹤 `main.Step1` | 是 |
| `make trace-step2` | 追蹤 `main.Step2` | 是 |
| `make trace-flow` | 追蹤所有 `main.*` 函數 | 是 |
| `make trace-latency` | 統計 Step1/Step2 微秒耗時 | 是 |
| `make trace-count` | 統計函數命中次數（Ctrl+C 結束） | 是 |
| `make trace-stack` | 顯示 Step1 呼叫堆疊 | 是 |

### Runtime 層追蹤

| 目標 | 說明 | 觀察對象 | 需要 sudo |
|------|------|----------|-----------|
| `make trace-alloc` | heap 分配大小分布 + Allocate 呼叫時間 | `main.Allocate` + `runtime.mallocgc` | 是 |
| `make trace-goroutine` | goroutine 建立與 Worker 執行 | `runtime.newproc` + `main.Worker` + `runtime.goexit0` | 是 |
| `make trace-sleep` | time.Sleep 實際 duration（區分兩個 goroutine） | `time.Sleep` | 是 |
| `make trace-runtime` | 綜合：app 函數 + 排程次數 + 分配總量 | 8 個 probe 同時 | 是 |

### 自動化

| 目標 | 說明 | 需要 sudo |
|------|------|-----------|
| `make run-bg` | 背景啟動並記錄 PID | 否 |
| `make stop-bg` | 停止背景程序 | 否 |
| `make trace-smoke` | 自動化：啟動 + trace 5 秒 + 停止 | 是 |

---

## 詳細使用方法

### 環境需求

```bash
# 確認 bpftrace 已安裝
bpftrace --version

# 確認 Linux 核心 >= 4.9（支援 uprobe + eBPF）
uname -r

# 安裝（Ubuntu/Debian）
sudo apt install bpftrace

# 安裝（RHEL/CentOS）
sudo dnf install bpftrace
```

### 步驟 1：編譯程式

```bash
make build
# 輸出：go build -o myapp .
# 產生 ./myapp
```

### 步驟 2：前景執行並觀察基本輸出

```bash
make run
```

```
執行步驟 1: Hello
執行步驟 2，次數: 42
執行步驟 1: Hello
執行步驟 2，次數: 42
...（Ctrl+C 中止）
```

### 步驟 3：列出可用 probe 符號

```bash
sudo make trace-list
```

```
uprobe:./myapp:main.Step1
uprobe:./myapp:main.Step2
uprobe:./myapp:main.main
uprobe:./myapp:main.init
...
```

### 步驟 4：雙終端機手動追蹤

**終端機 1**（執行目標程序）：
```bash
make run
```

**終端機 2**（同時執行追蹤）：

追蹤單一函數：
```bash
sudo make trace-step1
```
```
時間: 3821 ms | 函數: uprobe:./myapp:main.Step1
時間: 5822 ms | 函數: uprobe:./myapp:main.Step1
```

追蹤所有函數：
```bash
sudo make trace-flow
```
```
時間: 3821 ms | 函數: uprobe:./myapp:main.main
時間: 3821 ms | 函數: uprobe:./myapp:main.Step1
時間: 3822 ms | 函數: uprobe:./myapp:main.Step2
時間: 5822 ms | 函數: uprobe:./myapp:main.main
...
```

### 步驟 5：耗時統計

```bash
# 一個終端機執行 myapp，另一個終端機執行：
sudo make trace-latency
```

```
Step1 耗時: 12 us
Step2 耗時: 8 us
Step1 耗時: 11 us
Step2 耗時: 9 us
```

### 步驟 6：命中次數統計

```bash
sudo make trace-count
# 執行一段時間後按 Ctrl+C
```

```
@[uprobe:./myapp:main.main]: 5
@[uprobe:./myapp:main.Step1]: 5
@[uprobe:./myapp:main.Step2]: 5
```

### 步驟 7：呼叫堆疊

```bash
sudo make trace-stack
```

```
命中 uprobe:./myapp:main.Step1

        main.Step1+0
        main.main+45
        runtime.main+277
        runtime.goexit.abi0+1
```

### 步驟 8：Runtime 追蹤

#### trace-alloc：heap 分配觀察

```bash
sudo make trace-alloc
```

```
Attaching 3 probes...
[Allocate] elapsed=932 ms
[Allocate] elapsed=2933 ms
[Allocate] elapsed=4934 ms
@size:
[8, 16)                3 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                     |
[16, 32)               5 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[32, 64)               2 |@@@@@@@@@@@@@@@@@@@@                                |
[256, 512)             3 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                     |
```

> 256-512 bucket 就是 `Allocate(256)` 的 256 bytes 分配，其他較小的是 `fmt.Printf` 的內部分配。

#### trace-goroutine：goroutine 生命週期

```bash
sudo make trace-goroutine
```

```
Attaching 3 probes...
[Worker]  goroutine 執行 elapsed=1944 ms
[Worker]  goroutine 執行 elapsed=4946 ms
[Worker]  goroutine 執行 elapsed=7946 ms
```

#### trace-sleep：區分兩個 goroutine 的 Sleep

```bash
sudo make trace-sleep
```

```
Attaching 1 probe...
[time.Sleep] duration=2000 ms tid=1234   ← main goroutine
[time.Sleep] duration=3000 ms tid=1235   ← Worker goroutine
[time.Sleep] duration=2000 ms tid=1234
[time.Sleep] duration=3000 ms tid=1235
```

> 兩個不同 `tid` 對應兩個 goroutine，可清楚區分 2s 和 3s 的 Sleep。

#### trace-runtime：綜合追蹤（8 個 probe）

```bash
sudo make trace-runtime
```

```
Attaching 8 probes...
[app] Step1    elapsed=954 ms
[app] Step2    elapsed=954 ms
[app] Allocate elapsed=954 ms
[runtime] Sleep 2000 ms tid=1069749
[app] Worker   elapsed=1953 ms
[runtime] Sleep 3000 ms tid=1069754
[app] Step1    elapsed=2955 ms
...

--- 統計 ---
@sched: 9
@alloc_bytes: 1424
```

### 步驟 10：自動化 Smoke Test

無需手動開兩個終端機，一鍵完成：

```bash
sudo make trace-smoke
```

```
背景程式 PID: 12345
時間: 1024 ms | 函數: uprobe:./myapp:main.Step1
時間: 1025 ms | 函數: uprobe:./myapp:main.Step2
時間: 3026 ms | 函數: uprobe:./myapp:main.Step1
已停止背景程式: 12345
```

### 執行測試

```bash
make test
```

```
=== RUN   TestDemoPrintsStepMessages
--- PASS: TestDemoPrintsStepMessages (2.05s)
PASS
ok      go-bpftrace-demo        2.052s
```

### 清理

```bash
make clean
# 刪除 ./myapp 與 tmp/ 目錄
```

---

## bpftrace 腳本語法詳解

### 基本結構

```
probe名稱 / 篩選條件 / {
    動作
}
```

### 本專案使用的語法元素

| 語法 | 說明 | 範例 |
|------|------|------|
| `uprobe:檔案:符號` | 在函數入口掛載 | `uprobe:./myapp:main.Step1` |
| `uretprobe:檔案:符號` | 在函數返回點掛載 | `uretprobe:./myapp:main.Step1` |
| `uprobe:檔案:前綴.*` | 萬用字元，匹配所有符合前綴的符號 | `uprobe:./myapp:main.*` |
| `probe` | 當前命中的 probe 完整名稱 | `printf("%s", probe)` |
| `elapsed` | 程序啟動後的奈秒數 | `elapsed / 1000000` 換算毫秒 |
| `nsecs` | 系統啟動後的奈秒數 | 用於計算耗時 |
| `tid` | Thread ID | 用作 map key 追蹤耗時 |
| `@map[key]` | eBPF map（關聯陣列） | `@step1[tid] = nsecs` |
| `count()` | 累計計數 | `@[probe] = count()` |
| `ustack()` | 使用者空間呼叫堆疊 | `print(ustack())` |
| `/條件/` | 篩選器（Guard） | `/@step1[tid]/` 確保 key 存在 |
| `delete(@map[key])` | 刪除 map 條目 | `delete(@step1[tid])` |
| `printf(格式, 參數...)` | 格式化輸出 | `printf("%llu us\n", 耗時)` |

### trace-latency 腳本解析

```bpftrace
uprobe:./myapp:main.Step1 {
    @step1[tid] = nsecs;      // 函數入口：記錄當前時間到 map（key=thread ID）
}

uretprobe:./myapp:main.Step1
/@step1[tid]/ {               // Guard：確保 @step1[tid] 存在（避免孤立的 uretprobe）
    printf("Step1 耗時: %llu us\n",
           (nsecs - @step1[tid]) / 1000);  // 計算耗時（奈秒 → 微秒）
    delete(@step1[tid]);      // 清除 map 避免記憶體洩漏
}
```

---

## 輸出範例

### myapp 正常輸出

```
執行步驟 1: Hello
執行步驟 2，次數: 42
分配記憶體: 256 bytes
Worker goroutine 執行中
執行步驟 1: Hello
執行步驟 2，次數: 42
分配記憶體: 256 bytes
...
```

### trace-flow 輸出

```
Attaching 8 probes...
時間: 12043 ms | 函數: uprobe:./myapp:main.main
時間: 12043 ms | 函數: uprobe:./myapp:main.Step1
時間: 12044 ms | 函數: uprobe:./myapp:main.Step2
時間: 14045 ms | 函數: uprobe:./myapp:main.main
時間: 14045 ms | 函數: uprobe:./myapp:main.Step1
時間: 14046 ms | 函數: uprobe:./myapp:main.Step2
```

### trace-latency 輸出

```
Attaching 4 probes...
Step1 耗時: 14 us
Step2 耗時: 9 us
Step1 耗時: 12 us
Step2 耗時: 8 us
```

### trace-count 輸出（Ctrl+C 後）

```
Attaching 8 probes...
^C
@[uprobe:./myapp:main.Step2]: 3
@[uprobe:./myapp:main.Step1]: 3
@[uprobe:./myapp:main.main]: 3
```

### trace-stack 輸出

```
Attaching 1 probe...
命中 uprobe:./myapp:main.Step1

        main.Step1+0
        main.main+45
        runtime.main+277
        runtime.goexit.abi0+1
```
