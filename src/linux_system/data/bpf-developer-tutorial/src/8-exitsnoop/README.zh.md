# eBPF 入門開發實踐教程八：在 eBPF 中使用 exitsnoop 監控進程退出事件，使用 ring buffer 向用戶態打印輸出

eBPF (Extended Berkeley Packet Filter) 是 Linux 內核上的一個強大的網絡和性能分析工具。它允許開發者在內核運行時動態加載、更新和運行用戶定義的代碼。

本文是 eBPF 入門開發實踐教程的第八篇，在 eBPF 中使用 exitsnoop 監控進程退出事件。

## ring buffer

現在有一個新的 BPF 數據結構可用，eBPF 環形緩衝區（ring buffer）。它解決了 BPF perf buffer（當今從內核向用戶空間發送數據的事實上的標準）的內存效率和事件重排問題，同時達到或超過了它的性能。它既提供了與 perf buffer 兼容以方便遷移，又有新的保留/提交API，具有更好的可用性。另外，合成和真實世界的基準測試表明，在幾乎所有的情況下，所以考慮將其作為從BPF程序向用戶空間發送數據的默認選擇。

### eBPF ringbuf vs eBPF perfbuf

只要 BPF 程序需要將收集到的數據發送到用戶空間進行後處理和記錄，它通常會使用 BPF perf buffer（perfbuf）來實現。Perfbuf 是每個CPU循環緩衝區的集合，它允許在內核和用戶空間之間有效地交換數據。它在實踐中效果很好，但由於其按CPU設計，它有兩個主要的缺點，在實踐中被證明是不方便的：內存的低效使用和事件的重新排序。

為了解決這些問題，從Linux 5.8開始，BPF提供了一個新的BPF數據結構（BPF map）。BPF環形緩衝區（ringbuf）。它是一個多生產者、單消費者（MPSC）隊列，可以同時在多個CPU上安全共享。

BPF ringbuf 支持來自 BPF perfbuf 的熟悉的功能:

- 變長的數據記錄。
- 能夠通過內存映射區域有效地從用戶空間讀取數據，而不需要額外的內存拷貝和/或進入內核的系統調用。
- 既支持epoll通知，又能以絕對最小的延遲進行忙環操作。

同時，BPF ringbuf解決了BPF perfbuf的以下問題:

- 內存開銷。
- 數據排序。
- 浪費的工作和額外的數據複製。

## exitsnoop

本文是 eBPF 入門開發實踐教程的第八篇，在 eBPF 中使用 exitsnoop 監控進程退出事件，並使用 ring buffer 向用戶態打印輸出。

使用 ring buffer 向用戶態打印輸出的步驟和 perf buffer 類似，首先需要定義一個頭文件：

頭文件：exitsnoop.h

```c
#ifndef __BOOTSTRAP_H
#define __BOOTSTRAP_H

#define TASK_COMM_LEN 16
#define MAX_FILENAME_LEN 127

struct event {
    int pid;
    int ppid;
    unsigned exit_code;
    unsigned long long duration_ns;
    char comm[TASK_COMM_LEN];
};

#endif /* __BOOTSTRAP_H */
```

源文件：exitsnoop.bpf.c

```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "exitsnoop.h"

char LICENSE[] SEC("license") = "Dual BSD/GPL";

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} rb SEC(".maps");

SEC("tp/sched/sched_process_exit")
int handle_exit(struct trace_event_raw_sched_process_template* ctx)
{
    struct task_struct *task;
    struct event *e;
    pid_t pid, tid;
    u64 id, ts, *start_ts, start_time = 0;
    
    /* get PID and TID of exiting thread/process */
    id = bpf_get_current_pid_tgid();
    pid = id >> 32;
    tid = (u32)id;

    /* ignore thread exits */
    if (pid != tid)
        return 0;

    /* reserve sample from BPF ringbuf */
    e = bpf_ringbuf_reserve(&rb, sizeof(*e), 0);
    if (!e)
        return 0;

    /* fill out the sample with data */
    task = (struct task_struct *)bpf_get_current_task();
    start_time = BPF_CORE_READ(task, start_time);

    e->duration_ns = bpf_ktime_get_ns() - start_time;
    e->pid = pid;
    e->ppid = BPF_CORE_READ(task, real_parent, tgid);
    e->exit_code = (BPF_CORE_READ(task, exit_code) >> 8) & 0xff;
    bpf_get_current_comm(&e->comm, sizeof(e->comm));

    /* send data to user-space for post-processing */
    bpf_ringbuf_submit(e, 0);
    return 0;
}
```

這段代碼展示瞭如何使用 exitsnoop 監控進程退出事件並使用 ring buffer 向用戶態打印輸出：

1. 首先，我們引入所需的頭文件和 exitsnoop.h。
2. 定義一個名為 "LICENSE" 的全局變量，內容為 "Dual BSD/GPL"，這是 eBPF 程序的許可證要求。
3. 定義一個名為 rb 的 BPF_MAP_TYPE_RINGBUF 類型的映射，它將用於將內核空間的數據傳輸到用戶空間。指定 max_entries 為 256 * 1024，代表 ring buffer 的最大容量。
4. 定義一個名為 handle_exit 的 eBPF 程序，它將在進程退出事件觸發時執行。傳入一個名為 ctx 的 trace_event_raw_sched_process_template 結構體指針作為參數。
5. 使用 bpf_get_current_pid_tgid() 函數獲取當前任務的 PID 和 TID。對於主線程，PID 和 TID 相同；對於子線程，它們是不同的。我們只關心進程（主線程）的退出，因此在 PID 和 TID 不同時返回 0，忽略子線程退出事件。
6. 使用 bpf_ringbuf_reserve 函數為事件結構體 e 在 ring buffer 中預留空間。如果預留失敗，返回 0。
7. 使用 bpf_get_current_task() 函數獲取當前任務的 task_struct 結構指針。
8. 將進程相關信息填充到預留的事件結構體 e 中，包括進程持續時間、PID、PPID、退出代碼以及進程名稱。
9. 最後，使用 bpf_ringbuf_submit 函數將填充好的事件結構體 e 提交到 ring buffer，之後在用戶空間進行處理和輸出。

這個示例展示瞭如何使用 exitsnoop 和 ring buffer 在 eBPF 程序中捕獲進程退出事件並將相關信息傳輸到用戶空間。這對於分析進程退出原因和監控系統行為非常有用。

## Compile and Run

eunomia-bpf 是一個結合 Wasm 的開源 eBPF 動態加載運行時和開發工具鏈，它的目的是簡化 eBPF 程序的開發、構建、分發、運行。可以參考 <https://github.com/eunomia-bpf/eunomia-bpf> 下載和安裝 ecc 編譯工具鏈和 ecli 運行時。我們使用 eunomia-bpf 編譯運行這個例子。

Compile:

```shell
docker run -it -v `pwd`/:/src/ ghcr.io/eunomia-bpf/ecc-`uname -m`:latest
```

Or

```console
$ ecc exitsnoop.bpf.c exitsnoop.h
Compiling bpf object...
Generating export types...
Packing ebpf object and config into package.json...
```

Run:

```console
$ sudo ./ecli run package.json 
TIME     PID     PPID    EXIT_CODE  DURATION_NS  COMM    
21:40:09  42050  42049   0          0            which
21:40:09  42049  3517    0          0            sh
21:40:09  42052  42051   0          0            ps
21:40:09  42051  3517    0          0            sh
21:40:09  42055  42054   0          0            sed
21:40:09  42056  42054   0          0            cat
21:40:09  42057  42054   0          0            cat
21:40:09  42058  42054   0          0            cat
21:40:09  42059  42054   0          0            cat
```

## 總結

本文介紹瞭如何使用 eunomia-bpf 開發一個簡單的 BPF 程序，該程序可以監控 Linux 系統中的進程退出事件, 並將捕獲的事件通過 ring buffer 發送給用戶空間程序。在本文中，我們使用 eunomia-bpf 編譯運行了這個例子。

為了更好地理解和實踐 eBPF 編程，我們建議您閱讀 eunomia-bpf 的官方文檔：<https://github.com/eunomia-bpf/eunomia-bpf> 。此外，我們還為您提供了完整的教程和源代碼，您可以在 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 中查看和學習。希望本教程能夠幫助您順利入門 eBPF 開發，併為您的進一步學習和實踐提供有益的參考。
