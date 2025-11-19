# 使用 eBPF 測量函數延遲

在現代軟件系統中，瞭解函數的性能特性，尤其是那些對應用程序運行至關重要的函數的性能特性，是至關重要的。性能分析中的一個關鍵指標是**函數延遲**，即函數從開始到完成所花費的時間。通過分析函數延遲，開發人員可以識別瓶頸、優化性能，並確保系統在各種條件下高效運行。

本文將深入探討如何使用 eBPF 這一強大的工具來測量函數延遲，並展示如何在內核和用戶空間中進行跟蹤和監控。

## 什麼是 eBPF？

eBPF（擴展伯克利包過濾器）是一項革命性的技術，它允許開發人員編寫小型程序在 Linux 內核中運行。eBPF 最初是為數據包過濾設計的，但它已經發展成為一個多功能工具，用於跟蹤、監控和分析系統行為。通過 eBPF，您幾乎可以對 Linux 內核或用戶空間的任何部分進行插樁，從而收集性能數據、執行安全策略，甚至實時調試系統——這一切都無需修改內核源碼或重啟系統。

eBPF 程序在內核的沙盒環境中執行，確保了安全性和穩定性。這些程序可以附加到內核中的各種鉤子上，如系統調用、網絡事件和跟蹤點，甚至可以通過 uprobes（用戶級探針）附加到用戶空間的函數。eBPF 程序收集的數據可以導出到用戶空間進行分析，使其成為系統可觀測性的重要工具。內核模式 eBPF 運行時的 `Uprobe` 可能會帶來較大的性能開銷。在這種情況下，你也可以考慮使用用戶模式的 eBPF 運行時，例如 [bpftime](https://github.com/eunomia-bpf/bpftime)。

## 為什麼函數延遲很重要？

函數延遲是內核和用戶空間應用程序性能分析中的一個關鍵指標。它提供了關於特定函數執行時間的洞察，這對以下方面至關重要：

- **識別性能瓶頸**：高函數延遲可能表明代碼中存在需要優化的低效或問題。
- **確保系統響應能力**：在實時系統或對延遲敏感的應用程序中，理解和最小化函數延遲對於保持響應能力至關重要。
- **性能分析和基準測試**：通過測量各種函數的延遲，開發人員可以對系統進行基準測試，並比較不同實現或配置的性能。
- **調試和診斷**：當系統表現出意外行為或性能下降時，測量函數延遲可以幫助定位問題的根源。

內核空間（如系統調用、文件操作）和用戶空間（如庫函數）中的函數都可以進行延遲分析，從而提供系統性能的全面視圖。

## 用於函數延遲的 eBPF 內核代碼

以下是一個設計用於測量函數延遲的 eBPF 程序，它通過掛鉤函數的入口和出口點來實現。該程序使用 kprobes 和 kretprobes（用於內核函數）或 uprobes 和 uretprobes（用於用戶空間函數）來捕獲函數執行的開始和結束時間。

```c
// SPDX-License-Identifier: GPL-2.0
/* Copyright (c) 2021 Google LLC. */
#include "vmlinux.h"
#include <bpf/bpf_core_read.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include "funclatency.h"
#include "bits.bpf.h"

const volatile pid_t targ_tgid = 0;
const volatile int units = 0;

/* key: pid.  value: start time */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_PIDS);
    __type(key, u32);
    __type(value, u64);
} starts SEC(".maps");

__u32 hist[MAX_SLOTS] = {};

static void entry(void)
{
    u64 id = bpf_get_current_pid_tgid();
    u32 tgid = id >> 32;
    u32 pid = id;
    u64 nsec;

    if (targ_tgid && targ_tgid != tgid)
        return;
    nsec = bpf_ktime_get_ns();
    bpf_map_update_elem(&starts, &pid, &nsec, BPF_ANY);
}

SEC("kprobe/dummy_kprobe")
int BPF_KPROBE(dummy_kprobe)
{
    entry();
    return 0;
}

static void exit(void)
{
    u64 *start;
    u64 nsec = bpf_ktime_get_ns();
    u64 id = bpf_get_current_pid_tgid();
    u32 pid = id;
    u64 slot, delta;

    start = bpf_map_lookup_elem(&starts, &pid);
    if (!start)
        return;

    delta = nsec - *start;

    switch (units) {
    case USEC:
        delta /= 1000;
        break;
    case MSEC:
        delta /= 1000000;
        break;
    }

    slot = log2l(delta);
    if (slot >= MAX_SLOTS)
        slot = MAX_SLOTS - 1;
    __sync_fetch_and_add(&hist[slot], 1);
}

SEC("kretprobe/dummy_kretprobe")
int BPF_KRETPROBE(dummy_kretprobe)
{
    exit();
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
```

### 代碼解釋

1. **頭文件**：代碼首先包含了必要的頭文件，如 `vmlinux.h`（提供內核定義）和 `bpf_helpers.h`（提供 eBPF 程序的輔助函數）。

2. **全局變量**：`targ_tgid` 是目標進程 ID（或線程組 ID），`units` 確定延遲測量的時間單位（如微秒或毫秒）。

3. **BPF 映射**：定義了一個哈希映射（`starts`），用於存儲每個進程 ID 的函數執行開始時間。另一個數組（`hist`）用於存儲延遲分佈。

4. **入口函數**：`entry()` 函數在函數進入時捕獲當前時間戳，並將其存儲在以進程 ID 為鍵的 `starts` 映射中。

5. **出口函數**：`exit()` 函數通過將存儲的開始時間與當前時間相減來計算延遲。然後將結果分類到直方圖槽中，並增加該槽的計數以記錄該延遲範圍的發生次數。

6. **探針**：`kprobe` 和 `kretprobe` 用於附加到函數的入口和出口點。這些探針觸發 `entry()` 和 `exit()` 函數來測量延遲。

7. **許可證**：該程序根據 GPL 許可證發佈，以確保符合內核的許可要求。

## 運行函數延遲工具

### 用戶空間函數延遲

要跟蹤用戶空間函數（例如 `libc` 庫中的 `read` 函數）的延遲，可以運行以下命令：

```console
# ./funclatency /usr/lib/x86_64-linux-gnu/libc.so.6:read    
tracing /usr/lib/x86_64-linux-gnu/libc.so.6:read...
tracing func read in /usr/lib/x86_64-linux-gnu/libc.so.6...
Tracing /usr/lib/x86_64-linux-gnu/libc.so.6:read.  Hit Ctrl-C to exit
^C
     nsec                : count    distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
       128 -> 255        : 0        |                                        |
       512 -> 1023       : 0        |                                        |
      65536 -> 131071     : 651      |****************************************+|
    131072 -> 262143     : 107      |******                                  |
    262144 -> 524287     : 36       |**                                      |
    524288 -> 1048575    : 8        |                                        |
   8388608 -> 16777215   : 2        |                                        |
Exiting trace of /usr/lib/x86_64-linux-gnu/libc.so.6:read
```

### 內核空間函數延遲

要跟蹤內核空間函數（例如 `vfs_read`）的延遲，可以運行以下命令：

```console
# sudo ./funclatency -u vfs_read
Tracing vfs_read.  Hit Ctrl-C to exit
^C
     usec                : count    distribution
         0 -> 1          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 3397     |****************************************|
        32 -> 63         : 2175     |*************************               |
        64 -> 127        : 184      |**                                      |
       1024 -> 2047       : 0        |                                        |
       4096 -> 8191       : 5        |                                        |
   2097152 -> 

4194303    : 2        |                                        |
Exiting trace of vfs_read
```

這些命令會跟蹤指定函數（無論是在用戶空間還是內核空間）的執行，並打印出觀察到的延遲的直方圖，顯示函數執行時間的分佈。

<https://github.com/eunomia-bpf/bpf-developer-tutorial/blob/main/src/33-funclatency>

## 結論

使用 eBPF 測量函數延遲可以深入瞭解用戶空間和內核空間代碼的性能。通過了解函數延遲，開發人員可以識別性能瓶頸、提高系統響應能力，並確保其應用程序的順暢運行。

本文介紹了使用 eBPF 跟蹤函數延遲的基本知識，包括實現該跟蹤功能的 eBPF 內核代碼概述。文中提供的示例展示瞭如何運行工具以跟蹤用戶空間和內核空間函數的延遲。

如果您有興趣瞭解更多關於 eBPF 的知識，包括更多高級示例和教程，請訪問我們的[教程代碼庫](https://github.com/eunomia-bpf/bpf-developer-tutorial)或我們的網站 [Eunomia](https://eunomia.dev/tutorials/)。

如果您正在尋找一個用於函數延遲測量的生產就緒工具，您可能想查看 BCC 倉庫中的完整實現：[BCC 倉庫](https://github.com/iovisor/bcc/blob/master/libbpf-tools/funclatency.c)。
