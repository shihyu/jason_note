# libbpf 架構解析與 xgotop 實作說明

## 目錄

- [1. libbpf 是什麼](#1-libbpf-是什麼)
- [2. 整體架構](#2-整體架構)
- [3. libbpf 核心功能](#3-libbpf-核心功能)
- [4. xgotop 中的實際應用](#4-xgotop-中的實際應用)
- [5. BCC vs libbpf 比較](#5-bcc-vs-libbpf-比較)
- [6. vmlinux.h 的角色](#6-vmlinuxh-的角色)
- [7. CO-RE 機制詳解](#7-co-re-機制詳解)

---

## 1. libbpf 是什麼

**libbpf** 是一個 **userspace library**，負責在用戶空間（userspace）和 Linux kernel 之間橋接 eBPF 程式。

### 核心定位

```
┌──────────────────────────────────────────┐
│         Your Application                 │
│         (xgotop Go 程式)                 │
│  - 業務邏輯                              │
│  - 資料處理                              │
│  - UI/API                                │
└────────────────┬─────────────────────────┘
                 │
                 │ 使用 libbpf API
                 ↓
┌─────────────────────────────────────────┐
│         libbpf Library                  │  ← 這裡！
│  (xgotop 使用 cilium/ebpf - Go 版本)    │
│                                         │
│  功能：                                 │
│  1. 載入 eBPF 程式到 kernel             │
│  2. Attach probe 到函數                 │
│  3. 管理 eBPF maps (kernel-user 通訊)   │
│  4. 讀取 ringbuffer/perf buffer         │
│  5. BTF 重定位 (CO-RE)                  │
└────────────────┬────────────────────────┘
                 │
                 │ syscall: bpf()
                 ↓
┌──────────────────────────────────────────┐
│         Linux Kernel                     │
│                                          │
│  - eBPF 虛擬機執行程式                   │
│  - eBPF maps 儲存                        │
│  - Ringbuffer                            │
│  - Verifier (安全性驗證)                 │
└──────────────────────────────────────────┘
```

---

## 2. 整體架構

### 2.1 開發流程

```
┌─────────────── 開發時 ──────────────┐
│                                     │
│  1. 生成 vmlinux.h                  │
│     bpftool btf dump file           │
│     /sys/kernel/btf/vmlinux         │
│            ↓                        │
│  2. 編寫 eBPF C 程式                │
│     #include "vmlinux.h"            │
│     xgotop.bpf.c                    │
│            ↓                        │
│  3. 編譯成 .bpf.o                   │
│     clang -target bpf               │
│     含 BTF 型別資訊                 │
│            ↓                        │
│  4. 產生 Go binding                 │
│     bpf2go (cilium/ebpf)            │
│     生成 ebpfObjects 結構           │
│                                     │
└─────────────────────────────────────┘
                 │
                 │ 部署
                 ↓
┌─────────────── 運行時 ──────────────┐
│                                     │
│  1. libbpf 載入 .bpf.o              │
│     loadEbpfObjects()               │
│            ↓                        │
│  2. BTF 重定位 (CO-RE)              │
│     讀取 /sys/kernel/btf/vmlinux    │
│     調整 offset                     │
│            ↓                        │
│  3. Kernel verifier 驗證            │
│     安全性檢查                      │
│            ↓                        │
│  4. JIT 編譯並執行                  │
│     eBPF bytecode → native code     │
│            ↓                        │
│  5. Attach probe                    │
│     ex.Uprobe(symbol, prog)         │
│            ↓                        │
│  6. 事件流動                        │
│     Kernel → Ringbuffer → libbpf    │
│            → Application            │
│                                     │
└─────────────────────────────────────┘
```

### 2.2 資料流動

```
Go Runtime (目標程式)
     │
     │ goroutine 事件發生
     │ (create/exit/alloc)
     ↓
┌──────────────────────────┐
│ eBPF Uprobe Hook         │
│ runtime.casgstatus()     │  ← xgotop.bpf.c
│ runtime.newproc1()       │
│ runtime.makeslice()      │
│ ...                      │
└────────┬─────────────────┘
         │
         │ 收集資料
         ↓
┌──────────────────────────┐
│ eBPF Program             │
│ - 讀取 g struct          │
│ - 記錄 goid, timestamp   │
│ - 檢查 sampling rate     │
└────────┬─────────────────┘
         │
         │ 寫入
         ↓
┌──────────────────────────┐
│ eBPF Ringbuffer          │  ← Kernel space
│ (環形緩衝區)             │
└────────┬─────────────────┘
         │
         │ libbpf 讀取
         │ ringbuf.NewReader()
         ↓
┌──────────────────────────┐
│ xgotop Userspace         │
│ - Event readers (goroutines)
│ - Event processors       │
└────────┬─────────────────┘
         │
         ├─→ Storage (Protobuf/JSONL)
         │
         └─→ WebSocket → Web UI
```

---

## 3. libbpf 核心功能

### 3.1 六大功能模組

| 功能 | 說明 | API 範例 | xgotop 使用位置 |
|------|------|---------|----------------|
| **Load** | 載入 `.bpf.o` 到 kernel | `loadEbpfObjects()` | main.go:168 |
| **Verify** | 協助 kernel verifier | 自動執行 | - |
| **Relocate** | BTF-based CO-RE 重定位 | 自動執行 | - |
| **Attach** | 附加到 hook 點 | `ex.Uprobe()` | main.go:215 |
| **Maps** | 管理 kernel-user 通訊 | `map.Update()` | main.go:182 |
| **Data I/O** | Ringbuffer/Perf buffer | `ringbuf.NewReader()` | main.go:220 |

### 3.2 功能詳解

#### 3.2.1 Load - 載入 eBPF 物件

```go
// cmd/xgotop/main.go:167-170
objs := ebpfObjects{}
err = loadEbpfObjects(&objs, nil)  // ← libbpf API
must(err, "loading objects")
defer objs.Close()
```

**背後發生的事：**
```
loadEbpfObjects()
    ↓
1. 讀取 xgotop.bpf.o 檔案
2. 解析 ELF sections
3. 提取 eBPF 程式碼和 BTF 資訊
4. 呼叫 bpf(BPF_PROG_LOAD, ...)
5. Kernel verifier 驗證程式安全性
6. 初始化 eBPF maps
7. 回傳 objs 結構（包含所有程式和 maps）
```

#### 3.2.2 Attach - 附加到目標函數

```go
// cmd/xgotop/main.go:205-218
ex, err := link.OpenExecutable(executablePath)

uprobeOpts := &link.UprobeOptions{}
if *pid != 0 {
    uprobeOpts.PID = *pid  // 只監控特定 PID
}

probes := map[string]*ebpf.Program{
    "runtime.casgstatus": objs.UprobeCasgstatus,
    "runtime.makeslice":  objs.UprobeMakeslice,
    "runtime.newproc1":   objs.UprobeNewproc1,
    // ...
}

for symbol, probe := range probes {
    uprobe, err := ex.Uprobe(symbol, probe, uprobeOpts)
    //              ↑ libbpf attach API
    must(err, "attaching uprobe at "+symbol)
    defer uprobe.Close()
}
```

**Uprobe 原理：**
```
目標 binary (testserver)
    ↓
1. 找到 runtime.casgstatus 的位址
2. 在該位址設置 breakpoint
3. 當執行到該位址時：
   → 觸發 uprobe
   → 執行 eBPF 程式
   → 記錄事件
   → 繼續執行原程式
```

#### 3.2.3 Maps - Kernel-Userspace 通訊

```go
// cmd/xgotop/main.go:179-187
if objs.SamplingRates != nil {
    for eventType, rate := range rates {
        key := uint32(eventType)
        err := objs.SamplingRates.Update(&key, &rate, ebpf.UpdateAny)
        //                             ↑ userspace → kernel
        if err != nil {
            log.Fatalf("Failed to update sampling rate: %v", err)
        }
    }
}
```

**Maps 類型：**
```c
// xgotop.h 中的 map 定義
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 16);
    __type(key, u32);
    __type(value, u32);
} sampling_rates SEC(".maps");
```

**雙向通訊：**
```
Userspace                    Kernel
    │                           │
    │  map.Update(key, value)   │
    │ ────────────────────────> │  eBPF 程式讀取
    │                           │  map_lookup_elem()
    │                           │
    │  map.Lookup(&key, &val)   │
    │ <──────────────────────── │  eBPF 程式寫入
    │                           │  map_update_elem()
```

#### 3.2.4 Ringbuffer - 高效事件傳輸

```go
// cmd/xgotop/main.go:220-222
rd, err := ringbuf.NewReader(objs.Events)
must(err, "creating events ringbuf reader")
defer rd.Close()

// 讀取事件
for {
    record, err := rd.Read()
    if err != nil {
        break
    }
    // 處理 record.RawSample
}
```

**Ringbuffer 優勢：**
```
傳統 Perf Buffer              Ringbuffer (現代)
    │                              │
    ├─ 每個 CPU 一個 buffer        ├─ 全域共享 buffer
    ├─ 需要輪詢所有 CPU            ├─ 單一讀取點
    ├─ 可能 reorder                ├─ 保證順序
    └─ 較高 overhead               └─ 更高效
```

---

## 4. xgotop 中的實際應用

### 4.1 完整初始化流程

```go
// cmd/xgotop/main.go 簡化版

func main() {
    // 1. 移除記憶體鎖定限制
    err := rlimit.RemoveMemlock()
    // 允許 eBPF 鎖定記憶體，避免被 swap

    // 2. 載入 eBPF 物件
    objs := ebpfObjects{}
    err = loadEbpfObjects(&objs, nil)
    defer objs.Close()

    // 3. 設定 sampling rates (透過 map)
    for eventType, rate := range rates {
        key := uint32(eventType)
        objs.SamplingRates.Update(&key, &rate, ebpf.UpdateAny)
    }

    // 4. Attach uprobes
    ex, err := link.OpenExecutable(executablePath)
    for symbol, probe := range probes {
        uprobe, err := ex.Uprobe(symbol, probe, nil)
        defer uprobe.Close()
    }

    // 5. 建立 ringbuffer reader
    rd, err := ringbuf.NewReader(objs.Events)
    defer rd.Close()

    // 6. 啟動 event readers (goroutines)
    for i := 0; i < *readWorkers; i++ {
        go readEvents(rd, eventCh)
    }

    // 7. 啟動 event processors
    for i := 0; i < *processWorkers; i++ {
        go processEvents(eventCh, eventStore)
    }
}
```

### 4.2 事件處理流程

```
[Kernel] eBPF Hook 觸發
    ↓
[Kernel] 寫入 Ringbuffer
    ↓
[User] ringbuf.NewReader().Read()  ← libbpf
    ↓
[User] readEvents() goroutine
    ↓ 放入 channel
[User] eventCh := make(chan *ebpfGoRuntimeEventT, 1_000_000)
    ↓
[User] processEvents() goroutine
    ↓
[User] Storage (Protobuf/JSONL)
    ↓
[User] WebSocket → Web UI
```

### 4.3 生成的 Go Binding

```bash
# gen.go
//go:generate go run github.com/cilium/ebpf/cmd/bpf2go \
    -type go_runtime_event_t \
    -target arm64 \
    -output-dir cmd/xgotop \
    ebpf xgotop.bpf.c
```

**生成檔案：**
```
cmd/xgotop/
├── ebpf_arm64_bpfeb.go     ← Big-endian
├── ebpf_arm64_bpfel.go     ← Little-endian
└── ebpf_arm64_bpfel.o      ← eBPF bytecode
```

**自動生成的結構：**
```go
// ebpf_arm64_bpfel.go (自動生成)

type ebpfObjects struct {
    // Programs
    UprobeCasgstatus *ebpf.Program
    UprobeMakeslice  *ebpf.Program
    UprobeNewproc1   *ebpf.Program
    // ...

    // Maps
    Events         *ebpf.Map  // Ringbuffer
    SamplingRates  *ebpf.Map  // Array map
}

func loadEbpfObjects(obj *ebpfObjects, opts *ebpf.CollectionOptions) error {
    // 自動生成的載入邏輯
}
```

---

## 5. BCC vs libbpf 比較

### 5.1 開發方法對比

#### BCC 方法（傳統）

```python
# BCC Python 範例
from bcc import BPF

bpf_text = """
#include <linux/sched.h>      // ← 使用 kernel headers
#include <linux/fs.h>

int trace_open(struct pt_regs *ctx) {
    struct task_struct *task =
        (struct task_struct *)bpf_get_current_task();
    bpf_trace_printk("PID: %d\\n", task->pid);
    return 0;
}
"""

b = BPF(text=bpf_text)  # ← 運行時編譯
b.attach_kprobe(event="do_sys_open", fn_name="trace_open")
```

**特點：**
- ❌ 不需要 vmlinux.h
- ✅ 使用 kernel headers (`/usr/include/linux/*`)
- 🔄 **運行時編譯**（每次執行都編譯）
- 📦 需要安裝 LLVM/Clang
- 🐍 Python API（易學）

#### libbpf + CO-RE 方法（現代，xgotop 使用）

```c
// xgotop.bpf.c
#include "vmlinux.h"           // ← 使用 vmlinux.h
#include <bpf/bpf_helpers.h>

SEC("uprobe/runtime.casgstatus")
int uprobe_casgstatus(struct pt_regs *ctx) {
    struct go_runtime_g g;
    bpf_probe_read(&g, sizeof(g), gp);
    return 0;
}
```

```bash
# 開發機器：預先編譯
clang -target bpf -c xgotop.bpf.c -o xgotop.bpf.o

# 目標機器：直接執行
./xgotop  # 不需要編譯器
```

**特點：**
- ✅ **需要 vmlinux.h**
- ❌ 不使用 kernel headers
- ⚡ **預先編譯** (Compile Once, Run Everywhere)
- 📦 只需要目標機器支援 BTF
- 🚀 啟動快速、部署輕量

### 5.2 完整對比表

| 項目 | BCC | libbpf + CO-RE |
|------|-----|----------------|
| **vmlinux.h** | ❌ 不需要 | ✅ **需要** |
| **Kernel Headers** | ✅ 需要 | ❌ 不需要 |
| **LLVM/Clang** | 運行時需要 | 編譯時需要 |
| **編譯時機** | 運行時 | 開發時 |
| **啟動速度** | 慢（5-10秒） | 快（<1秒） |
| **部署大小** | 大（需要 headers） | 小（單一 binary） |
| **學習曲線** | 簡單（Python） | 較陡（C + BTF） |
| **適用場景** | 快速開發、實驗 | 生產環境 |
| **跨版本相容** | 差 | 好（CO-RE） |
| **效能 overhead** | 較高 | 較低 |

### 5.3 編譯流程對比

**BCC：**
```
運行時（目標機器）
┌──────────────────────────────┐
│ 1. Python 腳本執行           │
│ 2. 讀取 kernel headers       │ ← 需要安裝
│    /usr/include/linux/*      │
│ 3. LLVM 即時編譯             │ ← 每次都編譯
│ 4. 載入到 kernel             │
└──────────────────────────────┘
   啟動時間：5-10 秒
```

**libbpf + CO-RE：**
```
開發時（開發機器）              運行時（目標機器）
┌──────────────────────┐       ┌───────────────────┐
│ 1. 生成 vmlinux.h    │       │ 1. 載入 .bpf.o    │
│ 2. clang 編譯        │  ──>  │ 2. BTF 重定位     │ ← 自動適配
│ 3. 產生 .bpf.o       │       │ 3. 執行           │
└──────────────────────┘       └───────────────────┘
                               啟動時間：<1 秒
```

---

## 6. vmlinux.h 的角色

### 6.1 為什麼需要 vmlinux.h

**問題：Kernel 版本差異**

```c
// Kernel 5.10
struct task_struct {
    int field_a;      // offset 0
    long field_b;     // offset 4
};

// Kernel 6.14
struct task_struct {
    long new_field;   // offset 0  ← 新增！
    int field_a;      // offset 8  ← offset 改變！
    long field_b;     // offset 12
};
```

如果寫死 offset，程式會在不同 kernel 版本上**讀到錯誤資料**。

### 6.2 vmlinux.h 生成流程

```bash
# Makefile
vmlinux:
    bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h
```

**流程圖：**
```
/sys/kernel/btf/vmlinux
    ↓ (二進位 BTF 格式)
    │ 包含 kernel 所有型別資訊
    ↓
bpftool btf dump
    ↓ (轉換成 C header)
    │ 產生 3.8MB 的 header
    ↓
vmlinux.h
    ↓ (包含所有結構定義)
    │ struct task_struct { ... }
    │ struct pt_regs { ... }
    │ ...（數千個結構）
    ↓
#include "vmlinux.h"  ← xgotop.h
```

### 6.3 在 xgotop 的使用

```c
// xgotop.h:4
#include "vmlinux.h"

// 使用 vmlinux.h 中的定義
struct pt_regs {  // ← 來自 vmlinux.h
    unsigned long regs[31];
    unsigned long sp;
    unsigned long pc;
    // ...
};

// xgotop.bpf.c 中使用
SEC("uprobe/runtime.casgstatus")
int BPF_KPROBE(uprobe_casgstatus,
               const void *gp,
               const u32 oldval,
               const u32 newval) {
    struct go_runtime_g g;
    // pt_regs 透過 ctx 傳入，型別來自 vmlinux.h
}
```

---

## 7. CO-RE 機制詳解

### 7.1 CO-RE 架構

**CO-RE = Compile Once, Run Everywhere**

```
┌─────────── 編譯時 ───────────┐
│                              │
│  vmlinux.h (開發機器)        │
│  struct task_struct {        │
│      int pid;  // offset 123 │  ← BTF 記錄
│  }                           │
│         ↓                    │
│  clang -target bpf           │
│         ↓                    │
│  xgotop.bpf.o                │
│  + BTF relocations           │  ← 記住 "pid" 這個欄位名稱
│                              │
└──────────────────────────────┘
            │
            │ 部署
            ↓
┌─────────── 運行時 ───────────┐
│                              │
│  /sys/kernel/btf/vmlinux     │
│  (目標機器實際 kernel)       │
│  struct task_struct {        │
│      long new_field;         │
│      int pid;  // offset 456 │  ← 不同 offset！
│  }                           │
│         ↓                    │
│  libbpf 重定位引擎           │
│         ↓                    │
│  找到 "pid" 欄位             │
│  offset 123 → 456            │  ← 自動調整
│         ↓                    │
│  載入到 kernel               │
│                              │
└──────────────────────────────┘
```

### 7.2 BTF (BPF Type Format)

**BTF 儲存的資訊：**

```c
// 原始結構
struct task_struct {
    int pid;           // offset 456, size 4
    char comm[16];     // offset 460, size 16
};
```

**BTF 格式：**
```
BTF Type #123: struct task_struct {
    member: pid
        type: int
        offset: 456 bits
        size: 32 bits
    member: comm
        type: char[16]
        offset: 460 bits
        size: 128 bits
}
```

### 7.3 libbpf 重定位過程

```
1. 讀取 .bpf.o 的 BTF section
   → 知道程式想存取 task_struct.pid
   → 編譯時 offset = 123

2. 讀取 /sys/kernel/btf/vmlinux
   → 找到 task_struct 定義
   → 運行時 offset = 456

3. 修改程式碼中的 offset
   → mov r1, [r0 + 123]  改成
   → mov r1, [r0 + 456]

4. 載入到 kernel
```

### 7.4 CO-RE Helper 巨集

```c
// xgotop.h:6
#include <bpf/bpf_core_read.h>

// 使用 CO-RE helper
if (bpf_core_type_exists(struct trace_event_raw_bpf_trace_printk___x)) {
    // 檢查結構是否存在於當前 kernel
    // 不存在則跳過，避免 crash
}

// 讀取欄位（自動處理 offset）
int pid = BPF_CORE_READ(task, pid);
//        ↑ 展開成 bpf_probe_read + offset calculation
```

---

## 8. 實戰範例：追蹤流程

### 8.1 從 Hook 到顯示的完整路徑

```
[Step 1] Go 程式執行
testserver 的 runtime.casgstatus() 被呼叫

    ↓

[Step 2] Uprobe 觸發
xgotop attach 的 eBPF 程式執行

    ↓

[Step 3] eBPF 程式執行
// xgotop.bpf.c:4-30
SEC("uprobe/runtime.casgstatus")
int BPF_KPROBE(uprobe_casgstatus, ...) {
    struct go_runtime_g g;
    bpf_probe_read(&g, sizeof(g), gp);  // 讀取 goroutine 結構

    // 組裝事件
    struct go_runtime_event event = {
        .event_type = EVENT_TYPE_CASGSTATUS,
        .timestamp = bpf_ktime_get_ns(),
        .goid = g.goid,
        // ...
    };

    // 寫入 ringbuffer
    bpf_ringbuf_output(&events, &event, sizeof(event), 0);
}

    ↓

[Step 4] Ringbuffer → Userspace (libbpf)
// main.go:220
rd, err := ringbuf.NewReader(objs.Events)

// 多個 reader goroutines
for i := 0; i < *readWorkers; i++ {
    go func() {
        for {
            record, err := rd.Read()  // ← libbpf API
            eventCh <- parseEvent(record.RawSample)
        }
    }()
}

    ↓

[Step 5] Event Processing
// main.go:processEvents
go func() {
    for event := range eventCh {
        // 處理事件
        processedEvent := transform(event)

        // 儲存到 storage
        eventStore.Write(processedEvent)

        // 發送到 WebSocket
        apiServer.Broadcast(processedEvent)
    }
}()

    ↓

[Step 6] Storage & Web UI
Protobuf/JSONL 寫入磁碟
WebSocket 推送到瀏覽器
Timeline 視覺化顯示
```

### 8.2 效能指標追蹤

```go
// main.go:234-238
var probeDurationNsSum atomic.Int64     // LAT: eBPF hook 時間
var processingTimeNsSum atomic.Int64    // PRC: 處理時間

var readEventCount atomic.Uint64        // RPS: 讀取速率
var procEventCount atomic.Uint64        // PPS: 處理速率

eventCh := make(chan *ebpfGoRuntimeEventT, 1_000_000)
// ↑ EWP: len(eventCh) = 等待處理的事件數
```

**計算公式：**
```
LAT = probeDurationNsSum / probeDurationNsCount
RPS = readEventCount / 時間間隔
PPS = procEventCount / 時間間隔
EWP = len(eventCh)
PRC = processingTimeNsSum / processingTimeNsCount
```

---

## 9. 總結

### 9.1 關鍵概念回顧

```
vmlinux.h
    ↓ 提供 kernel 型別定義
    ↓
eBPF C 程式 (xgotop.bpf.c)
    ↓ clang 編譯 + BTF
    ↓
.bpf.o (eBPF bytecode)
    ↓ libbpf 載入
    ↓
Kernel (執行)
    ↓ Ringbuffer
    ↓
libbpf 讀取
    ↓
Application (xgotop)
```

### 9.2 libbpf 的價值

| 沒有 libbpf | 有 libbpf |
|------------|----------|
| 手動 syscall(__NR_bpf, ...) | `loadEbpfObjects()` |
| 手動解析 BTF | 自動重定位 |
| 手動管理 maps | `map.Update()` |
| 手動讀取 ringbuffer | `ringbuf.NewReader()` |
| 數百行 boilerplate | 幾行程式碼 |

### 9.3 開發建議

**使用 BCC 當：**
- 快速原型開發
- 一次性除錯任務
- 學習 eBPF 基礎

**使用 libbpf + CO-RE 當：**
- 生產環境工具
- 需要跨 kernel 版本分發
- 效能要求高
- 最小化部署依賴

### 9.4 參考資源

- **cilium/ebpf**: https://github.com/cilium/ebpf
- **libbpf 官方文檔**: https://github.com/libbpf/libbpf
- **BPF CO-RE 介紹**: https://nakryiko.com/posts/bpf-portability-and-co-re/
- **xgotop 專案**: https://github.com/sazak-io/xgotop

---

**文件版本**: 1.0
**最後更新**: 2026-01-01
**適用於**: xgotop (arm64), Linux kernel 5.2+
