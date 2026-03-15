# Linux 程式追蹤技術全面比較

## 目錄
1. [技術概覽](#技術概覽)
2. [ptrace](#ptrace)
3. [eBPF + uprobes](#ebpf--uprobes)
4. [kprobes](#kprobes)
5. [USDT (User Statically Defined Tracing)](#usdt)
6. [strace / ltrace](#strace--ltrace)
7. [perf](#perf)
8. [Go 專屬方案](#go-專屬方案)
9. [完整比較表](#完整比較表)
10. [選擇指南](#選擇指南)
11. [程式碼範例](#程式碼範例)

---

## 技術概覽

```
追蹤技術的演進
─────────────────────────────────────────────────────────────
1990s       ptrace              暫停 target，切換至 tracer
2000s       USDT / DTrace       靜態埋點，效能較好
2010s       perf / kprobes      kernel 層追蹤
2014+       eBPF                kernel 內執行，近乎零開銷
─────────────────────────────────────────────────────────────

架構位置
┌──────────────────────────────────────────────────────────┐
│  User Space                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   ptrace    │  │  strace/    │  │  Go pprof/      │  │
│  │   tracer    │  │  ltrace     │  │  runtime trace  │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  USDT probes (靜態埋點在 user space binary 內)      │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
         ↕ syscall boundary
┌──────────────────────────────────────────────────────────┐
│  Kernel Space                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   uprobes   │  │   kprobes   │  │   tracepoints   │  │
│  │ (user 追蹤) │  │(kernel 追蹤)│  │  (靜態埋點)     │  │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘  │
│         └────────────────┴──────────────────┘            │
│                          │                               │
│              ┌───────────▼───────────┐                   │
│              │    eBPF Subsystem     │                   │
│              │  (安全的 kernel 內    │                   │
│              │   程式執行環境)       │                   │
│              └───────────────────────┘                   │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  perf_events subsystem                              │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

## ptrace

### 工作原理

```
每次追蹤的完整流程：

target process          kernel              tracer process
─────────────           ──────              ──────────────
執行到 breakpoint
      │
      ▼
  INT3 指令
      │
      └──────────► 發送 SIGTRAP
                   target 暫停
                        │
                        ▼
                   喚醒 tracer ◄──── context switch #1
                                          │
                                          ▼
                                    ptrace(GETREGS)  ← syscall #1
                                    讀取暫存器/記憶體
                                    分析資料
                                    ptrace(CONT)     ← syscall #2
                                          │
                        ◄─────────────────┘
                   恢復 target ────────────────► context switch #2
                        │
target 繼續執行 ◄────────┘

開銷統計（每次函數呼叫）：
  - 2 次 process context switch
  - 2 次 syscall（至少）
  - target 完全暫停期間：~1-10 μs
```

### 核心 API

```c
// 附加到目標 process
ptrace(PTRACE_ATTACH, pid, NULL, NULL);

// 在 syscall 入口/出口暫停
ptrace(PTRACE_SYSCALL, pid, NULL, NULL);

// 單步執行（每條指令暫停）
ptrace(PTRACE_SINGLESTEP, pid, NULL, NULL);

// 讀取暫存器
ptrace(PTRACE_GETREGS, pid, NULL, &regs);

// 讀取記憶體
ptrace(PTRACE_PEEKDATA, pid, addr, NULL);

// 寫入記憶體（植入 breakpoint）
ptrace(PTRACE_POKEDATA, pid, addr, 0xCC);  // INT3

// 繼續執行
ptrace(PTRACE_CONT, pid, NULL, NULL);
```

### 優缺點

```
優點：
  ✅ 不需要修改目標程式
  ✅ 可以讀寫目標記憶體
  ✅ 細粒度控制（可以單步執行）
  ✅ 所有 Linux 系統都支援
  ✅ 是 GDB、delve 等 debugger 的基礎

缺點：
  ❌ 每次事件 = 2 次 context switch（開銷大）
  ❌ 多 thread 程式需要追蹤每個 thread
  ❌ target 被暫停，改變了執行時序
  ❌ 某些程式會偵測 ptrace 並改變行為
  ❌ 不適合生產環境（效能影響 10x~100x）
```

---

## eBPF + uprobes

### 工作原理

```
uprobe 插入機制：

Binary on disk:
  0x1000: push rbp
  0x1001: mov  rbp, rsp    ← uprobe 插入點
  0x1004: ...

執行期（kernel 自動替換）：
  0x1000: push rbp
  0x1001: int3             ← 替換為 breakpoint
  0x1004: ...（原始指令保存在 trampoline）

當 target 執行到 0x1001：
  CPU → kernel trap
            │
            ├── 執行 eBPF program（在 kernel 內，不切換 process）
            │       ├── 讀取 registers
            │       ├── 讀取 memory
            │       ├── 寫入 ring buffer
            │       └── 完成（μs 級）
            │
            └── 執行原始指令（從 trampoline）
                      │
                      ▼
              target 繼續執行（從未被暫停超過 μs）

開銷統計（每次函數呼叫）：
  - 0 次 process context switch
  - 0 次 user space syscall
  - kernel trap：~100-500 ns
```

### eBPF 程式類型

```
與 tracing 相關的 eBPF program types：

┌─────────────────┬────────────────────────────────────────┐
│  Program Type   │  用途                                  │
├─────────────────┼────────────────────────────────────────┤
│  BPF_UPROBE     │  追蹤 user space 函數入口               │
│  BPF_URETPROBE  │  追蹤 user space 函數返回               │
│  BPF_KPROBE     │  追蹤 kernel 函數入口                   │
│  BPF_KRETPROBE  │  追蹤 kernel 函數返回                   │
│  BPF_TRACEPOINT │  kernel 靜態追蹤點                      │
│  BPF_PERF_EVENT │  perf 事件                              │
└─────────────────┴────────────────────────────────────────┘
```

### eBPF 安全限制

```
eBPF Verifier 在載入時檢查：

  ┌──────────────────────────────────────┐
  │  eBPF Program                        │
  │  - 禁止無限迴圈（保證終止）           │
  │  - 禁止越界存取記憶體                 │
  │  - 禁止呼叫任意 kernel function      │
  │  - 必須通過 verifier 才能執行         │
  └──────────────────────────────────────┘
              │
              ▼
      eBPF Verifier（kernel 內）
              │
      通過 → JIT 編譯 → 執行
      失敗 → 拒絕載入
```

### 優缺點

```
優點：
  ✅ target 幾乎不暫停（ns 級）
  ✅ 不需要修改目標程式
  ✅ 自動支援多 thread
  ✅ 適合生產環境
  ✅ 可追蹤 user space + kernel space
  ✅ 安全（verifier 保護 kernel）

缺點：
  ❌ 需要 Linux kernel 4.4+（完整功能需 5.x+）
  ❌ 需要 root 或 CAP_BPF 權限
  ❌ 程式設計複雜度較高
  ❌ Go 程式因無 frame pointer 預設難以 stack unwinding
     （需加 -gcflags="-e" 或用 DWARF）
```

---

## kprobes

### 工作原理

```
kprobes 與 uprobes 原理相同，但目標是 kernel 函數：

User Space：                 Kernel Space：
                        ┌────────────────────────┐
                        │  kernel function       │
                        │  do_sys_open:          │
                        │    push rbp     ← kprobe 插入
                        │    ...                 │
                        └────────────────────────┘
                                   │
                        觸發 kprobe handler
                                   │
                        eBPF program 執行
                                   │
                        繼續 kernel function
```

### kprobe vs uprobe

```
┌──────────────┬────────────────────┬────────────────────┐
│              │     kprobe         │     uprobe         │
├──────────────┼────────────────────┼────────────────────┤
│ 追蹤目標     │ kernel functions   │ user functions     │
│ 插入方式     │ kernel 記憶體      │ process 虛擬記憶體  │
│ 需要符號表   │ /proc/kallsyms     │ binary DWARF/ELF   │
│ 多 process   │ 全系統唯一         │ 每個 process 獨立  │
└──────────────┴────────────────────┴────────────────────┘
```

---

## USDT

### 靜態埋點原理

```
開發者在程式碼中手動埋點：

#include <sys/sdt.h>

void process_request(int req_id) {
    DTRACE_PROBE1(myapp, request__start, req_id);  // ← 靜態埋點
    // ... 處理邏輯 ...
    DTRACE_PROBE1(myapp, request__end, req_id);    // ← 靜態埋點
}

編譯後，埋點變成：
  - 預設：nop 指令（零開銷！）
  - 啟用時：kernel 替換為 int3（有 uprobe 開銷）

好處：
  - 未啟用時完全零開銷
  - 埋點位置由開發者決定（語義更準確）
  - 不需要 DWARF 符號（不依賴 debug info）
```

### 主要使用者

```
已內建 USDT probes 的知名軟體：
  - Python：python:function__entry / function__return
  - Node.js：node:http__server__request
  - PostgreSQL：postgresql:query__start / query__done
  - MySQL：mysql:query__start
  - OpenJDK：hotspot:method__entry
```

---

## strace / ltrace

### strace

```
strace 的實作：就是 ptrace + syscall tracking

strace ls
  │
  ├── ptrace(PTRACE_TRACEME) 或 PTRACE_ATTACH
  │
  ├── 每個 syscall：
  │   execve("/bin/ls", ...) = 0          ← syscall 入口
  │   openat(AT_FDCWD, ".", O_RDONLY) = 3 ← 記錄參數
  │   ...
  │
  └── 解析 syscall number → 符號名稱

開銷：因為用 ptrace，追蹤密集 syscall 的程式會慢 10-100 倍
```

### ltrace

```
ltrace 追蹤 library function calls（不是 syscall）：

ltrace ls
  │
  ├── 在 PLT（Procedure Linkage Table）插入 breakpoint
  │
  ├── 每次 library call：
  │   malloc(512)                    = 0x55a1b2c3d4e0
  │   strlen("hello")               = 5
  │   printf("Hello, World!\n")     = 15
  │
  └── 比 strace 更高層次的追蹤

限制：
  ❌ 靜態連結的程式無法追蹤（沒有 PLT）
  ❌ Go 程式靜態連結 → ltrace 無效
```

---

## perf

### 架構

```
perf 使用 kernel perf_events 子系統：

perf record ./my_program
      │
      ├── 設定 PMU（Performance Monitoring Unit）
      │   - CPU 硬體計數器
      │   - software events（context switch, page fault）
      │   - tracepoints
      │
      ├── 定期採樣（sampling，非 tracing）
      │   - 預設每秒 1000 次
      │   - 記錄 PC（program counter）和 call stack
      │
      └── 輸出到 perf.data

perf report
      │
      └── 分析 call graph，找出熱點函數

perf vs ptrace/eBPF：
  - perf：統計型（sampling），開銷低，但不是每次呼叫都記錄
  - ptrace：事件型，每次都記錄，開銷高
  - eBPF：事件型，每次都記錄，開銷低
```

### perf + eBPF

```
perf 可以當作 eBPF 的前端：

perf probe -x /usr/bin/python3 function__entry  # 從 USDT 建立 probe
perf record -e probe:function__entry -aR sleep 10
perf script                                      # 輸出記錄
```

---

## Go 專屬方案

### runtime/trace

```
Go 內建追蹤，不需要 ptrace 或 eBPF：

import "runtime/trace"

func main() {
    f, _ := os.Create("trace.out")
    trace.Start(f)
    defer trace.Stop()
    // ... 你的程式 ...
}

go tool trace trace.out  # 在瀏覽器開啟視覺化介面

追蹤內容：
  - Goroutine 排程（建立、結束、block、unblock）
  - GC 事件
  - Syscall 進出
  - Heap 分配
  - Processor 使用率

開銷：約 5-20%（比 ptrace 低得多）
```

### pprof

```
CPU profiling（採樣式，不是追蹤式）：

import _ "net/http/pprof"
// 或
pprof.StartCPUProfile(f)

go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

適合：找效能瓶頸（哪個函數用最多 CPU）
不適合：記錄每次函數呼叫順序
```

### delve（Go debugger）

```
delve 底層使用 ptrace，但提供 Go-aware 介面：

dlv debug ./myprogram
  (dlv) break main.processRequest   # 在函數設 breakpoint
  (dlv) trace main.processRequest   # 追蹤函數呼叫（不暫停）
  (dlv) continue

dlv trace（不暫停追蹤）：
  - 使用 uretprobe 實作（Linux）
  - 顯示函數呼叫和返回值
  - 比完整 ptrace 開銷小
```

### bpftrace（追蹤 Go 程式）

```bash
# 追蹤 Go 程式的函數呼叫（需要有 debug symbols）
bpftrace -e '
uprobe:/path/to/myprogram:main.processRequest {
    printf("called: %s\n", comm);
}
'

# 測量函數執行時間
bpftrace -e '
uprobe:/path/to/myprogram:main.processRequest { @start[tid] = nsecs; }
uretprobe:/path/to/myprogram:main.processRequest {
    @latency = hist(nsecs - @start[tid]);
    delete(@start[tid]);
}
'
```

---

## 完整比較表

```
┌─────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│                 │  ptrace  │eBPF+     │  USDT    │  strace  │  ltrace  │   perf   │ Go trace │
│                 │          │uprobes   │          │          │          │          │          │
├─────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ target 暫停     │ 每次暫停 │ 幾乎不停 │ 幾乎不停 │ 每次暫停 │ 每次暫停 │ 採樣暫停 │ 不暫停   │
│ 效能影響        │ 極高     │ 極低     │ 零/極低  │ 高       │ 高       │ 低       │ 低       │
│ 修改目標程式    │ 不需要   │ 不需要   │ 需要埋點 │ 不需要   │ 不需要   │ 不需要   │ 需要     │
│ 追蹤粒度        │ 指令級   │ 函數級   │ 自訂     │ syscall  │ library  │ 採樣     │ goroutine│
│ 追蹤 Go 程式    │ 複雜     │ 可以     │ 需埋點   │ syscall  │ 無效     │ 可以     │ 最佳     │
│ 生產環境適用    │ ❌       │ ✅       │ ✅       │ ❌       │ ❌       │ ✅       │ ✅       │
│ 需要 root       │ 部分     │ 是       │ 是       │ 部分     │ 部分     │ 部分     │ 否       │
│ kernel 版本需求 │ 無       │ 4.4+     │ 無       │ 無       │ 無       │ 3.x+     │ 無       │
│ 讀寫目標記憶體  │ ✅       │ 受限     │ ❌       │ ❌       │ ❌       │ ❌       │ ❌       │
│ 實作複雜度      │ 中       │ 高       │ 低       │ 低       │ 低       │ 中       │ 低       │
└─────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

---

## 選擇指南

```
你的需求是？
│
├── 開發/除錯階段
│   ├── Go 程式 goroutine 追蹤 → go tool trace
│   ├── 找效能瓶頸 → pprof
│   ├── 互動式除錯（設 breakpoint，檢查變數）→ delve (ptrace)
│   └── 追蹤 syscall → strace
│
├── 生產環境監控
│   ├── 低開銷函數追蹤 → eBPF + uprobes
│   ├── 應用程式有埋點 → USDT + eBPF
│   ├── CPU 效能分析 → perf
│   └── Go 程式 → pprof HTTP endpoint + go tool trace
│
├── 安全研究 / 逆向工程
│   ├── 需要讀寫目標記憶體 → ptrace
│   ├── 追蹤系統呼叫 → strace
│   └── 追蹤函數（有符號表）→ eBPF uprobes
│
└── 學習目的
    ├── 理解 OS 原理 → ptrace（最直接）
    ├── 理解現代追蹤 → eBPF + bpftrace
    └── 理解 Go runtime → go tool trace
```

---

## 程式碼範例

### ptrace tracer（Go 實作）

```go
package main

import (
    "fmt"
    "os"
    "os/exec"
    "syscall"
)

func main() {
    // 啟動目標程式並附加 ptrace
    cmd := exec.Command("/bin/ls")
    cmd.Stdin = os.Stdin
    cmd.Stdout = os.Stdout
    cmd.Stderr = os.Stderr
    cmd.SysProcAttr = &syscall.SysProcAttr{
        Ptrace: true,  // 子程式啟動時自動 TRACEME
    }

    cmd.Start()
    pid := cmd.Process.Pid

    var regs syscall.PtraceRegs
    syscallCount := 0

    for {
        // 等待子程式暫停
        var ws syscall.WaitStatus
        syscall.Wait4(pid, &ws, 0, nil)

        if ws.Exited() {
            break
        }

        // 讀取暫存器
        syscall.PtraceGetRegs(pid, &regs)
        fmt.Printf("syscall #%d: rax=%d\n", syscallCount, regs.Orig_rax)
        syscallCount++

        // 在下一個 syscall 暫停
        syscall.PtraceSyscall(pid, 0)
    }

    fmt.Printf("共追蹤到 %d 個 syscall\n", syscallCount)
}
```

### bpftrace uprobe（追蹤任意函數）

```bash
# 追蹤函數呼叫次數
bpftrace -e '
uprobe:/path/to/program:funcName {
    @calls = count();
}
interval:s:1 {
    print(@calls);
    clear(@calls);
}
'

# 追蹤函數延遲分佈
bpftrace -e '
uprobe:/path/to/program:funcName    { @start[tid] = nsecs; }
uretprobe:/path/to/program:funcName {
    @us = hist((nsecs - @start[tid]) / 1000);
    delete(@start[tid]);
}
'
```

### Go 程式內建 trace

```go
package main

import (
    "os"
    "runtime/trace"
)

func main() {
    f, _ := os.Create("trace.out")
    defer f.Close()

    trace.Start(f)
    defer trace.Stop()

    // 自訂 task 追蹤
    ctx, task := trace.NewTask(context.Background(), "processRequest")
    defer task.End()

    trace.Log(ctx, "step", "start processing")
    doWork()
    trace.Log(ctx, "step", "done")
}

// 執行後用以下指令查看：
// go tool trace trace.out
```

### eBPF Go 程式（使用 cilium/ebpf）

```go
//go:build linux

package main

import (
    "log"
    "os"
    "os/signal"

    "github.com/cilium/ebpf/link"
    "github.com/cilium/ebpf/ringbuf"
    "github.com/cilium/ebpf/rlimit"
)

func main() {
    // 移除 eBPF 記憶體限制
    rlimit.RemoveMemlock()

    // 載入編譯好的 eBPF objects
    objs := bpfObjects{}
    loadBpfObjects(&objs, nil)
    defer objs.Close()

    // 附加 uprobe 到目標函數
    ex, _ := link.OpenExecutable("/path/to/target")
    up, _ := ex.Uprobe("main.processRequest", objs.UprobeProcessRequest, nil)
    defer up.Close()

    // 從 ring buffer 讀取事件
    rd, _ := ringbuf.NewReader(objs.Events)
    defer rd.Close()

    log.Println("追蹤中... 按 Ctrl+C 停止")

    sig := make(chan os.Signal, 1)
    signal.Notify(sig, os.Interrupt)

    go func() {
        for {
            record, err := rd.Read()
            if err != nil {
                return
            }
            log.Printf("函數被呼叫: %s\n", record.RawSample)
        }
    }()

    <-sig
}
```
