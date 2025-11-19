# eBPF 入門開發實踐教程九：捕獲進程調度延遲，以直方圖方式記錄

eBPF (Extended Berkeley Packet Filter) 是 Linux 內核上的一個強大的網絡和性能分析工具。它允許開發者在內核運行時動態加載、更新和運行用戶定義的代碼。

runqlat 是一個 eBPF 工具，用於分析 Linux 系統的調度性能。具體來說，runqlat 用於測量一個任務在被調度到 CPU 上運行之前在運行隊列中等待的時間。這些信息對於識別性能瓶頸和提高 Linux 內核調度算法的整體效率非常有用。

## runqlat 原理

本教程是 eBPF 入門開發實踐系列的第九部分，主題是 "捕獲進程調度延遲"。在此，我們將介紹一個名為 runqlat 的程序，其作用是以直方圖的形式記錄進程調度延遲。

Linux 操作系統使用進程來執行所有的系統和用戶任務。這些進程可能被阻塞、殺死、運行，或者正在等待運行。處在後兩種狀態的進程數量決定了 CPU 運行隊列的長度。

進程有幾種可能的狀態，如：

- 可運行或正在運行
- 可中斷睡眠
- 不可中斷睡眠
- 停止
- 殭屍進程

等待資源或其他函數信號的進程會處在可中斷或不可中斷的睡眠狀態：進程被置入睡眠狀態，直到它需要的資源變得可用。然後，根據睡眠的類型，進程可以轉移到可運行狀態，或者保持睡眠。

即使進程擁有它需要的所有資源，它也不會立即開始運行。它會轉移到可運行狀態，與其他處在相同狀態的進程一起排隊。CPU可以在接下來的幾秒鐘或毫秒內執行這些進程。調度器為 CPU 排列進程，並決定下一個要執行的進程。

根據系統的硬件配置，這個可運行隊列（稱為 CPU 運行隊列）的長度可以短也可以長。短的運行隊列長度表示 CPU 沒有被充分利用。另一方面，如果運行隊列長，那麼可能意味著 CPU 不夠強大，無法執行所有的進程，或者 CPU 的核心數量不足。在理想的 CPU 利用率下，運行隊列的長度將等於系統中的核心數量。

進程調度延遲，也被稱為 "run queue latency"，是衡量線程從變得可運行（例如，接收到中斷，促使其處理更多工作）到實際在 CPU 上運行的時間。在 CPU 飽和的情況下，你可以想象線程必須等待其輪次。但在其他奇特的場景中，這也可能發生，而且在某些情況下，它可以通過調優減少，從而提高整個系統的性能。

我們將通過一個示例來闡述如何使用 runqlat 工具。這是一個負載非常重的系統：

```shell
# runqlat
Tracing run queue latency... Hit Ctrl-C to end.
^C
     usecs               : count     distribution
         0 -> 1          : 233      |***********                             |
         2 -> 3          : 742      |************************************    |
         4 -> 7          : 203      |**********                              |
         8 -> 15         : 173      |********                                |
        16 -> 31         : 24       |*                                       |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 30       |*                                       |
       128 -> 255        : 6        |                                        |
       256 -> 511        : 3        |                                        |
       512 -> 1023       : 5        |                                        |
      1024 -> 2047       : 27       |*                                       |
      2048 -> 4095       : 30       |*                                       |
      4096 -> 8191       : 20       |                                        |
      8192 -> 16383      : 29       |*                                       |
     16384 -> 32767      : 809      |****************************************|
     32768 -> 65535      : 64       |***                                     |
```

在這個輸出中，我們看到了一個雙模分佈，一個模在0到15微秒之間，另一個模在16到65毫秒之間。這些模式在分佈（它僅僅是 "count" 列的視覺表示）中顯示為尖峰。例如，讀取一行：在追蹤過程中，809個事件落入了16384到32767微秒的範圍（16到32毫秒）。

在後續的教程中，我們將深入探討如何利用 eBPF 對此類指標進行深度跟蹤和分析，以更好地理解和優化系統性能。同時，我們也將學習更多關於 Linux 內核調度器、中斷處理和 CPU 飽

runqlat 的實現利用了 eBPF 程序，它通過內核跟蹤點和函數探針來測量進程在運行隊列中的時間。當進程被排隊時，trace_enqueue 函數會在一個映射中記錄時間戳。當進程被調度到 CPU 上運行時，handle_switch 函數會檢索時間戳，並計算當前時間與排隊時間之間的時間差。這個差值（或 delta）被用於更新進程的直方圖，該直方圖記錄運行隊列延遲的分佈。該直方圖可用於分析 Linux 內核的調度性能。

## runqlat 代碼實現

### runqlat.bpf.c

首先我們需要編寫一個源代碼文件 runqlat.bpf.c:

```c
// SPDX-License-Identifier: GPL-2.0
// Copyright (c) 2020 Wenbo Zhang
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_core_read.h>
#include <bpf/bpf_tracing.h>
#include "runqlat.h"
#include "bits.bpf.h"
#include "maps.bpf.h"
#include "core_fixes.bpf.h"

#define MAX_ENTRIES 10240
#define TASK_RUNNING  0

const volatile bool filter_cg = false;
const volatile bool targ_per_process = false;
const volatile bool targ_per_thread = false;
const volatile bool targ_per_pidns = false;
const volatile bool targ_ms = false;
const volatile pid_t targ_tgid = 0;

struct {
 __uint(type, BPF_MAP_TYPE_CGROUP_ARRAY);
 __type(key, u32);
 __type(value, u32);
 __uint(max_entries, 1);
} cgroup_map SEC(".maps");

struct {
 __uint(type, BPF_MAP_TYPE_HASH);
 __uint(max_entries, MAX_ENTRIES);
 __type(key, u32);
 __type(value, u64);
} start SEC(".maps");

static struct hist zero;

/// @sample {"interval": 1000, "type" : "log2_hist"}
struct {
 __uint(type, BPF_MAP_TYPE_HASH);
 __uint(max_entries, MAX_ENTRIES);
 __type(key, u32);
 __type(value, struct hist);
} hists SEC(".maps");

static int trace_enqueue(u32 tgid, u32 pid)
{
 u64 ts;

 if (!pid)
  return 0;
 if (targ_tgid && targ_tgid != tgid)
  return 0;

 ts = bpf_ktime_get_ns();
 bpf_map_update_elem(&start, &pid, &ts, BPF_ANY);
 return 0;
}

static unsigned int pid_namespace(struct task_struct *task)
{
 struct pid *pid;
 unsigned int level;
 struct upid upid;
 unsigned int inum;

 /*  get the pid namespace by following task_active_pid_ns(),
  *  pid->numbers[pid->level].ns
  */
 pid = BPF_CORE_READ(task, thread_pid);
 level = BPF_CORE_READ(pid, level);
 bpf_core_read(&upid, sizeof(upid), &pid->numbers[level]);
 inum = BPF_CORE_READ(upid.ns, ns.inum);

 return inum;
}

static int handle_switch(bool preempt, struct task_struct *prev, struct task_struct *next)
{
 struct hist *histp;
 u64 *tsp, slot;
 u32 pid, hkey;
 s64 delta;

 if (filter_cg && !bpf_current_task_under_cgroup(&cgroup_map, 0))
  return 0;

 if (get_task_state(prev) == TASK_RUNNING)
  trace_enqueue(BPF_CORE_READ(prev, tgid), BPF_CORE_READ(prev, pid));

 pid = BPF_CORE_READ(next, pid);

 tsp = bpf_map_lookup_elem(&start, &pid);
 if (!tsp)
  return 0;
 delta = bpf_ktime_get_ns() - *tsp;
 if (delta < 0)
  goto cleanup;

 if (targ_per_process)
  hkey = BPF_CORE_READ(next, tgid);
 else if (targ_per_thread)
  hkey = pid;
 else if (targ_per_pidns)
  hkey = pid_namespace(next);
 else
  hkey = -1;
 histp = bpf_map_lookup_or_try_init(&hists, &hkey, &zero);
 if (!histp)
  goto cleanup;
 if (!histp->comm[0])
  bpf_probe_read_kernel_str(&histp->comm, sizeof(histp->comm),
     next->comm);
 if (targ_ms)
  delta /= 1000000U;
 else
  delta /= 1000U;
 slot = log2l(delta);
 if (slot >= MAX_SLOTS)
  slot = MAX_SLOTS - 1;
 __sync_fetch_and_add(&histp->slots[slot], 1);

cleanup:
 bpf_map_delete_elem(&start, &pid);
 return 0;
}

SEC("raw_tp/sched_wakeup")
int BPF_PROG(handle_sched_wakeup, struct task_struct *p)
{
 if (filter_cg && !bpf_current_task_under_cgroup(&cgroup_map, 0))
  return 0;

 return trace_enqueue(BPF_CORE_READ(p, tgid), BPF_CORE_READ(p, pid));
}

SEC("raw_tp/sched_wakeup_new")
int BPF_PROG(handle_sched_wakeup_new, struct task_struct *p)
{
 if (filter_cg && !bpf_current_task_under_cgroup(&cgroup_map, 0))
  return 0;

 return trace_enqueue(BPF_CORE_READ(p, tgid), BPF_CORE_READ(p, pid));
}

SEC("raw_tp/sched_switch")
int BPF_PROG(handle_sched_switch, bool preempt, struct task_struct *prev, struct task_struct *next)
{
 return handle_switch(preempt, prev, next);
}

char LICENSE[] SEC("license") = "GPL";
```

#### 常量與全局變量

代碼中定義了一些常量和 volatile 全局變量，用於過濾對應的追蹤目標。這些變量包括：

```c
#define MAX_ENTRIES 10240
#define TASK_RUNNING  0

const volatile bool filter_cg = false;
const volatile bool targ_per_process = false;
const volatile bool targ_per_thread = false;
const volatile bool targ_per_pidns = false;
const volatile bool targ_ms = false;
const volatile pid_t targ_tgid = 0;
```

- `MAX_ENTRIES`:  map 條目最大數量
- `TASK_RUNNING`: 任務狀態值
- `filter_cg`, `targ_per_process`, `targ_per_thread`, `targ_per_pidns`, `targ_ms`, `targ_tgid`: 用於過濾選項和目標選項的布爾變量。這些選項可以通過用戶空間程序設置來自定義eBPF程序的行為。

#### eBPF Maps 映射

接下來，定義了一些 eBPF 映射：

```c
struct {
 __uint(type, BPF_MAP_TYPE_CGROUP_ARRAY);
 __type(key, u32);
 __type(value, u32);
 __uint(max_entries, 1);
} cgroup_map SEC(".maps");

struct {
 __uint(type, BPF_MAP_TYPE_HASH);
 __uint(max_entries, MAX_ENTRIES);
 __type(key, u32);
 __type(value, u64);
} start SEC(".maps");

static struct hist zero;

struct {
 __uint(type, BPF_MAP_TYPE_HASH);
 __uint(max_entries, MAX_ENTRIES);
 __type(key, u32);
 __type(value, struct hist);
} hists SEC(".maps");
```

這些映射包括：

- `cgroup_map` 用於過濾 cgroup；
- `start` 用於存儲進程入隊時的時間戳；
- `hists` 用於存儲直方圖數據，記錄進程調度延遲。

#### 輔助函數

接下來是一些輔助函數：

- `trace_enqueue`: 此功能用於記錄進程入隊時的時間戳。它將 `tgid` 和 `pid` 值作為參數。如果`pid`值是0或者`targ_tgid`值不是0且不等於`tgid`，函數返回0。否則，它使用 `bpf_ktime_get_ns` 獲取當前時間戳，並使用 `pid` 鍵和時間戳值更新 `start` 映射。

```c
static int trace_enqueue(u32 tgid, u32 pid)
{
 u64 ts;

 if (!pid)
  return 0;
 if (targ_tgid && targ_tgid != tgid)
  return 0;

 ts = bpf_ktime_get_ns();
 bpf_map_update_elem(&start, &pid, &ts, BPF_ANY);
 return 0;
}
```

- `pid_namespace` : 此函數用於獲取進程的PID命名空間。它接受一個`task_struct`指針作為參數，並返回進程的PID命名空間。該函數通過`task_active_pid_ns()`和`pid->numbers[pid->level].ns`來檢索PID命名空間。

```c
static unsigned int pid_namespace(struct task_struct *task)
{
 struct pid *pid;
 unsigned int level;
 struct upid upid;
 unsigned int inum;

 /*  get the pid namespace by following task_active_pid_ns(),
  *  pid->numbers[pid->level].ns
  */
 pid = BPF_CORE_READ(task, thread_pid);
 level = BPF_CORE_READ(pid, level);
 bpf_core_read(&upid, sizeof(upid), &pid->numbers[level]);
 inum = BPF_CORE_READ(upid.ns, ns.inum);

 return inum;
}
```

`handle_switch` 函數是核心部分，用於處理調度切換事件，計算進程調度延遲並更新直方圖數據：

```c
static int handle_switch(bool preempt, struct task_struct *prev, struct task_struct *next)
{
 ...
}
```

首先，函數根據 `filter_cg` 的設置判斷是否需要過濾 cgroup。然後，如果之前的進程狀態為 `TASK_RUNNING`，則調用 `trace_enqueue` 函數記錄進程的入隊時間。接著，函數查找下一個進程的入隊時間戳，如果找不到，直接返回。計算調度延遲（delta），並根據不同的選項設置（targ_per_process，targ_per_thread，targ_per_pidns），確定直方圖映射的鍵（hkey）。然後查找或初始化直方圖映射，更新直方圖數據，最後刪除進程的入隊時間戳記錄。

接下來是 eBPF 程序的入口點。程序使用三個入口點來捕獲不同的調度事件：

- `handle_sched_wakeup`：用於處理 `sched_wakeup` 事件，當一個進程從睡眠狀態被喚醒時觸發。
- `handle_sched_wakeup_new`：用於處理 `sched_wakeup_new` 事件，當一個新創建的進程被喚醒時觸發。
- `handle_sched_switch`：用於處理 `sched_switch` 事件，當調度器選擇一個新的進程運行時觸發。

這些入口點分別處理不同的調度事件，但都會調用 handle_switch 函數來計算進程的調度延遲並更新直方圖數據。

最後，程序包含一個許可證聲明：

```c
char LICENSE[] SEC("license") = "GPL";
```

這一聲明指定了 eBPF 程序的許可證類型，這裡使用的是 "GPL"。這對於許多內核功能是必需的，因為它們要求 eBPF 程序遵循 GPL 許可證。

### runqlat.h

然後我們需要定義一個頭文件`runqlat.h`，用來給用戶態處理從內核態上報的事件：

```c
/* SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause) */
#ifndef __RUNQLAT_H
#define __RUNQLAT_H

#define TASK_COMM_LEN 16
#define MAX_SLOTS 26

struct hist {
 __u32 slots[MAX_SLOTS];
 char comm[TASK_COMM_LEN];
};

#endif /* __RUNQLAT_H */
```

## 編譯運行

eunomia-bpf 是一個結合 Wasm 的開源 eBPF 動態加載運行時和開發工具鏈，它的目的是簡化 eBPF 程序的開發、構建、分發、運行。可以參考 <https://github.com/eunomia-bpf/eunomia-bpf> 下載和安裝 ecc 編譯工具鏈和 ecli 運行時。我們使用 eunomia-bpf 編譯運行這個例子。

Compile:

```shell
docker run -it -v `pwd`/:/src/ ghcr.io/eunomia-bpf/ecc-`uname -m`:latest
```

或者

```console
$ ecc runqlat.bpf.c runqlat.h
Compiling bpf object...
Generating export types...
Packing ebpf object and config into package.json...
```

Run:

```console
$ sudo ecli run examples/bpftools/runqlat/package.json -h
Usage: runqlat_bpf [--help] [--version] [--verbose] [--filter_cg] [--targ_per_process] [--targ_per_thread] [--targ_per_pidns] [--targ_ms] [--targ_tgid VAR]

A simple eBPF program

Optional arguments:
  -h, --help            shows help message and exits 
  -v, --version         prints version information and exits 
  --verbose             prints libbpf debug information 
  --filter_cg           set value of bool variable filter_cg 
  --targ_per_process    set value of bool variable targ_per_process 
  --targ_per_thread     set value of bool variable targ_per_thread 
  --targ_per_pidns      set value of bool variable targ_per_pidns 
  --targ_ms             set value of bool variable targ_ms 
  --targ_tgid           set value of pid_t variable targ_tgid 

Built with eunomia-bpf framework.
See https://github.com/eunomia-bpf/eunomia-bpf for more information.

$ sudo ecli run examples/bpftools/runqlat/package.json
key =  4294967295
comm = rcu_preempt

     (unit)              : count    distribution
         0 -> 1          : 9        |****                                    |
         2 -> 3          : 6        |**                                      |
         4 -> 7          : 12       |*****                                   |
         8 -> 15         : 28       |*************                           |
        16 -> 31         : 40       |*******************                     |
        32 -> 63         : 83       |****************************************|
        64 -> 127        : 57       |***************************             |
       128 -> 255        : 19       |*********                               |
       256 -> 511        : 11       |*****                                   |
       512 -> 1023       : 2        |                                        |
      1024 -> 2047       : 2        |                                        |
      2048 -> 4095       : 0        |                                        |
      4096 -> 8191       : 0        |                                        |
      8192 -> 16383      : 0        |                                        |
     16384 -> 32767      : 1        |                                        |

$ sudo ecli run examples/bpftools/runqlat/package.json --targ_per_process
key =  3189
comm = cpptools

     (unit)              : count    distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 1        |***                                     |
        16 -> 31         : 2        |*******                                 |
        32 -> 63         : 11       |****************************************|
        64 -> 127        : 8        |*****************************           |
       128 -> 255        : 3        |**********                              |
```

完整源代碼請見：<https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/9-runqlat>

參考資料：

- <https://www.brendangregg.com/blog/2016-10-08/linux-bcc-runqlat.html>
- <https://github.com/iovisor/bcc/blob/master/libbpf-tools/runqlat.c>

## 總結

runqlat 是一個 Linux 內核 BPF 程序，通過柱狀圖來總結調度程序運行隊列延遲，顯示任務等待運行在 CPU 上的時間長度。編譯這個程序可以使用 ecc 工具，運行時可以使用 ecli 命令。

runqlat 是一種用於監控Linux內核中進程調度延遲的工具。它可以幫助您瞭解進程在內核中等待執行的時間，並根據這些信息優化進程調度，提高系統的性能。可以在 libbpf-tools 中找到最初的源代碼：<https://github.com/iovisor/bcc/blob/master/libbpf-tools/runqlat.bpf.c>

如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。
