# eBPF 入門實踐教程七：捕獲進程執行事件，通過 perf event array 向用戶態打印輸出

eBPF (Extended Berkeley Packet Filter) 是 Linux 內核上的一個強大的網絡和性能分析工具，它允許開發者在內核運行時動態加載、更新和運行用戶定義的代碼。

本文是 eBPF 入門開發實踐教程的第七篇，主要介紹如何捕獲 Linux 內核中進程執行的事件，並且通過 perf event array 向用戶態命令行打印輸出，不需要再通過查看 /sys/kernel/debug/tracing/trace_pipe 文件來查看 eBPF 程序的輸出。通過 perf event array 向用戶態發送信息之後，可以進行復雜的數據處理和分析。

## perf buffer

eBPF 提供了兩個環形緩衝區，可以用來將信息從 eBPF 程序傳輸到用戶區控制器。第一個是perf環形緩衝區，，它至少從內核v4.15開始就存在了。第二個是後來引入的 BPF 環形緩衝區。本文只考慮perf環形緩衝區。

## execsnoop

通過 perf event array 向用戶態命令行打印輸出，需要編寫一個頭文件，一個 C 源文件。示例代碼如下：

頭文件：execsnoop.h

```c
#ifndef __EXECSNOOP_H
#define __EXECSNOOP_H

#define TASK_COMM_LEN 16

struct event {
    int pid;
    int ppid;
    int uid;
    int retval;
    bool is_exit;
    char comm[TASK_COMM_LEN];
};

#endif /* __EXECSNOOP_H */
```

源文件：execsnoop.bpf.c

```c
// SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause)
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_core_read.h>
#include "execsnoop.h"

struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(u32));
    __uint(value_size, sizeof(u32));
} events SEC(".maps");

SEC("tracepoint/syscalls/sys_enter_execve")
int tracepoint__syscalls__sys_enter_execve(struct trace_event_raw_sys_enter* ctx)
{
    u64 id;
    pid_t pid, tgid;
    struct event event={0};
    struct task_struct *task;

    uid_t uid = (u32)bpf_get_current_uid_gid();
    id = bpf_get_current_pid_tgid();
    tgid = id >> 32;

    event.pid = tgid;
    event.uid = uid;
    task = (struct task_struct*)bpf_get_current_task();
    event.ppid = BPF_CORE_READ(task, real_parent, tgid);
    char *cmd_ptr = (char *) BPF_CORE_READ(ctx, args[0]);
    bpf_probe_read_str(&event.comm, sizeof(event.comm), cmd_ptr);
    bpf_perf_event_output(ctx, &events, BPF_F_CURRENT_CPU, &event, sizeof(event));
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
```

這段代碼定義了個 eBPF 程序，用於捕獲進程執行 execve 系統調用的入口。

在入口程序中，我們首先獲取了當前進程的進程 ID 和用戶 ID，然後通過 bpf_get_current_task 函數獲取了當前進程的 task_struct 結構體，並通過 bpf_probe_read_str 函數讀取了進程名稱。最後，我們通過 bpf_perf_event_output 函數將進程執行事件輸出到 perf buffer。

使用這段代碼，我們就可以捕獲 Linux 內核中進程執行的事件, 並分析進程的執行情況。

eunomia-bpf 是一個結合 Wasm 的開源 eBPF 動態加載運行時和開發工具鏈，它的目的是簡化 eBPF 程序的開發、構建、分發、運行。可以參考 <https://github.com/eunomia-bpf/eunomia-bpf> 下載和安裝 ecc 編譯工具鏈和 ecli 運行時。我們使用 eunomia-bpf 編譯運行這個例子。

使用容器編譯：

```shell
docker run -it -v `pwd`/:/src/ ghcr.io/eunomia-bpf/ecc-`uname -m`:latest
```

或者使用 ecc 編譯：

```shell
ecc execsnoop.bpf.c execsnoop.h
```

運行

```console
$ sudo ./ecli run package.json 
TIME     PID     PPID    UID     COMM    
21:28:30  40747  3517    1000    node
21:28:30  40748  40747   1000    sh
21:28:30  40749  3517    1000    node
21:28:30  40750  40749   1000    sh
21:28:30  40751  3517    1000    node
21:28:30  40752  40751   1000    sh
21:28:30  40753  40752   1000    cpuUsage.sh
```

## 總結

本文介紹瞭如何捕獲 Linux 內核中進程執行的事件，並且通過 perf event array 向用戶態命令行打印輸出，通過 perf event array 向用戶態發送信息之後，可以進行復雜的數據處理和分析。在 libbpf 對應的內核態代碼中，定義這樣一個結構體和對應的頭文件：

```c
struct {
 __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
 __uint(key_size, sizeof(u32));
 __uint(value_size, sizeof(u32));
} events SEC(".maps");
```

就可以往用戶態直接發送信息。

更多的例子和詳細的開發指南，請參考 eunomia-bpf 的官方文檔：<https://github.com/eunomia-bpf/eunomia-bpf>

如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。
