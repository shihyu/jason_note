# eBPF 入門實踐教程十二：使用 eBPF 程序 profile 進行性能分析

本教程將指導您使用 libbpf 和 eBPF 程序進行性能分析。我們將利用內核中的 perf 機制，學習如何捕獲函數的執行時間以及如何查看性能數據。

libbpf 是一個用於與 eBPF 交互的 C 庫。它提供了創建、加載和使用 eBPF 程序所需的基本功能。本教程中，我們將主要使用 libbpf 完成開發工作。perf 是 Linux 內核中的性能分析工具，允許用戶測量和分析內核及用戶空間程序的性能，以及獲取對應的調用堆棧。它利用內核中的硬件計數器和軟件事件來收集性能數據。

## eBPF 工具：profile 性能分析示例

`profile` 工具基於 eBPF 實現，利用 Linux 內核中的 perf 事件進行性能分析。`profile` 工具會定期對每個處理器進行採樣，以便捕獲內核函數和用戶空間函數的執行。它可以顯示棧回溯的以下信息：

- 地址：函數調用的內存地址
- 符號：函數名稱
- 文件名：源代碼文件名稱
- 行號：源代碼中的行號

這些信息有助於開發人員定位性能瓶頸和優化代碼。更進一步，可以通過這些對應的信息生成火焰圖，以便更直觀的查看性能數據。

在本示例中，可以通過 libbpf 庫編譯運行它（以 Ubuntu/Debian 為例）：

**NOTE:** 首先需要安裝 `cargo` 才能編譯得到 `profile`, 安裝方法可以參考[Cargo 手冊](https://rustwiki.org/en/cargo/getting-started/installation.html)  

```console
$ git submodule update --init --recursive
$ sudo apt install clang libelf1 libelf-dev zlib1g-dev
$ make
$ sudo ./profile 
COMM: chronyd (pid=156) @ CPU 1
Kernel:
  0 [<ffffffff81ee9f56>] _raw_spin_lock_irqsave+0x16
  1 [<ffffffff811527b4>] remove_wait_queue+0x14
  2 [<ffffffff8132611d>] poll_freewait+0x3d
  3 [<ffffffff81326d3f>] do_select+0x7bf
  4 [<ffffffff81327af2>] core_sys_select+0x182
  5 [<ffffffff81327f3a>] __x64_sys_pselect6+0xea
  6 [<ffffffff81ed9e38>] do_syscall_64+0x38
  7 [<ffffffff82000099>] entry_SYSCALL_64_after_hwframe+0x61
Userspace:
  0 [<00007fab187bfe09>]
  1 [<000000000ee6ae98>]

COMM: profile (pid=9843) @ CPU 6
No Kernel Stack
Userspace:
  0 [<0000556deb068ac8>]
  1 [<0000556dec34cad0>]
```

## 實現原理

profile 工具由兩個部分組成，內核態中的 eBPF 程序和用戶態中的 `profile` 符號處理程序。`profile` 符號處理程序負責加載 eBPF 程序，以及處理 eBPF 程序輸出的數據。

### 內核態部分

內核態 eBPF 程序的實現邏輯主要是藉助 perf event，對程序的堆棧進行定時採樣，從而捕獲程序的執行流程。

```c
// SPDX-License-Identifier: GPL-2.0 OR BSD-3-Clause
/* Copyright (c) 2022 Meta Platforms, Inc. */
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#include "profile.h"

char LICENSE[] SEC("license") = "Dual BSD/GPL";

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

SEC("perf_event")
int profile(void *ctx)
{
    int pid = bpf_get_current_pid_tgid() >> 32;
    int cpu_id = bpf_get_smp_processor_id();
    struct stacktrace_event *event;
    int cp;

    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return 1;

    event->pid = pid;
    event->cpu_id = cpu_id;

    if (bpf_get_current_comm(event->comm, sizeof(event->comm)))
        event->comm[0] = 0;

    event->kstack_sz = bpf_get_stack(ctx, event->kstack, sizeof(event->kstack), 0);

    event->ustack_sz = bpf_get_stack(ctx, event->ustack, sizeof(event->ustack), BPF_F_USER_STACK);

    bpf_ringbuf_submit(event, 0);

    return 0;
}
```

接下來，我們將重點講解內核態代碼的關鍵部分。

1. 定義 eBPF maps `events`：

    ```c

    struct {
        __uint(type, BPF_MAP_TYPE_RINGBUF);
        __uint(max_entries, 256 * 1024);
    } events SEC(".maps");
    ```

    這裡定義了一個類型為 `BPF_MAP_TYPE_RINGBUF` 的 eBPF  maps 。Ring Buffer 是一種高性能的循環緩衝區，用於在內核和用戶空間之間傳輸數據。`max_entries` 設置了 Ring Buffer 的最大大小。

2. 定義 `perf_event` eBPF 程序：

    ```c
    SEC("perf_event")
    int profile(void *ctx)
    ```

    這裡定義了一個名為 `profile` 的 eBPF 程序，它將在 perf 事件觸發時執行。

3. 獲取進程 ID 和 CPU ID：

    ```c
    int pid = bpf_get_current_pid_tgid() >> 32;
    int cpu_id = bpf_get_smp_processor_id();
    ```

    `bpf_get_current_pid_tgid()` 函數返回當前進程的 PID 和 TID，通過右移 32 位，我們得到 PID。`bpf_get_smp_processor_id()` 函數返回當前 CPU 的 ID。

4. 預留 Ring Buffer 空間：

    ```c
    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return 1;
    ```

    通過 `bpf_ringbuf_reserve()` 函數預留 Ring Buffer 空間，用於存儲採集的棧信息。若預留失敗，返回錯誤.

5. 獲取當前進程名：

    ```c

    if (bpf_get_current_comm(event->comm, sizeof(event->comm)))
        event->comm[0] = 0;
    ```

    使用 `bpf_get_current_comm()` 函數獲取當前進程名並將其存儲到 `event->comm`。

6. 獲取內核棧信息：

    ```c

    event->kstack_sz = bpf_get_stack(ctx, event->kstack, sizeof(event->kstack), 0);
    ```

    使用 `bpf_get_stack()` 函數獲取內核棧信息。將結果存儲在 `event->kstack`，並將其大小存儲在 `event->kstack_sz`。

7. 獲取用戶空間棧信息：

    ```c
    event->ustack_sz = bpf_get_stack(ctx, event->ustack, sizeof(event->ustack), BPF_F_USER_STACK);
    ```

    同樣使用 `bpf_get_stack()` 函數，但傳遞 `BPF_F_USER_STACK` 標誌以獲取用戶空間棧信息。將結果存儲在 `event->ustack`，並將其大小存儲在 `event->ustack_sz`。

8. 將事件提交到 Ring Buffer：

    ```c
    bpf_ringbuf_submit(event, 0);
    ```

    最後，使用 `bpf_ringbuf_submit()` 函數將事件提交到 Ring Buffer，以便用戶空間程序可以讀取和處理。

    這個內核態 eBPF 程序通過定期採樣程序的內核棧和用戶空間棧來捕獲程序的執行流程。這些數據將存儲在 Ring Buffer 中，以便用戶態的 `profile` 程序能讀取。

### 用戶態部分

這段代碼主要負責為每個在線 CPU 設置 perf event 並附加 eBPF 程序：

```c
static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid,
                int cpu, int group_fd, unsigned long flags)
{
    int ret;

    ret = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
    return ret;
}

int main(){
    ...
    for (cpu = 0; cpu < num_cpus; cpu++) {
        /* skip offline/not present CPUs */
        if (cpu >= num_online_cpus || !online_mask[cpu])
            continue;

        /* Set up performance monitoring on a CPU/Core */
        pefd = perf_event_open(&attr, pid, cpu, -1, PERF_FLAG_FD_CLOEXEC);
        if (pefd < 0) {
            fprintf(stderr, "Fail to set up performance monitor on a CPU/Core\n");
            err = -1;
            goto cleanup;
        }
        pefds[cpu] = pefd;

        /* Attach a BPF program on a CPU */
        links[cpu] = bpf_program__attach_perf_event(skel->progs.profile, pefd);
        if (!links[cpu]) {
            err = -1;
            goto cleanup;
        }
    }
    ...
}
```

`perf_event_open` 這個函數是一個對 perf_event_open 系統調用的封裝。它接收一個 perf_event_attr 結構體指針，用於指定 perf event 的類型和屬性。pid 參數用於指定要監控的進程 ID（-1 表示監控所有進程），cpu 參數用於指定要監控的 CPU。group_fd 參數用於將 perf event 分組，這裡我們使用 -1，表示不需要分組。flags 參數用於設置一些標誌，這裡我們使用 PERF_FLAG_FD_CLOEXEC 以確保在執行 exec 系列系統調用時關閉文件描述符。

在 main 函數中：

```c
for (cpu = 0; cpu < num_cpus; cpu++) {
    // ...
}
```

這個循環針對每個在線 CPU 設置 perf event 並附加 eBPF 程序。首先，它會檢查當前 CPU 是否在線，如果不在線則跳過。然後，使用 perf_event_open() 函數為當前 CPU 設置 perf event，並將返回的文件描述符存儲在 pefds 數組中。最後，使用 bpf_program__attach_perf_event() 函數將 eBPF 程序附加到 perf event。links 數組用於存儲每個 CPU 上的 BPF 鏈接，以便在程序結束時銷燬它們。

通過這種方式，用戶態程序為每個在線 CPU 設置 perf event，並將 eBPF 程序附加到這些 perf event 上，從而實現對系統中所有在線 CPU 的監控。

以下這兩個函數分別用於顯示棧回溯和處理從 ring buffer 接收到的事件：

```c
static void show_stack_trace(__u64 *stack, int stack_sz, pid_t pid)
{
    const struct blazesym_result *result;
    const struct blazesym_csym *sym;
    sym_src_cfg src;
    int i, j;

    if (pid) {
        src.src_type = SRC_T_PROCESS;
        src.params.process.pid = pid;
    } else {
        src.src_type = SRC_T_KERNEL;
        src.params.kernel.kallsyms = NULL;
        src.params.kernel.kernel_image = NULL;
    }

    result = blazesym_symbolize(symbolizer, &src, 1, (const uint64_t *)stack, stack_sz);

    for (i = 0; i < stack_sz; i++) {
        if (!result || result->size <= i || !result->entries[i].size) {
            printf("  %d [<%016llx>]\n", i, stack[i]);
            continue;
        }

        if (result->entries[i].size == 1) {
            sym = &result->entries[i].syms[0];
            if (sym->path && sym->path[0]) {
                printf("  %d [<%016llx>] %s+0x%llx %s:%ld\n",
                       i, stack[i], sym->symbol,
                       stack[i] - sym->start_address,
                       sym->path, sym->line_no);
            } else {
                printf("  %d [<%016llx>] %s+0x%llx\n",
                       i, stack[i], sym->symbol,
                       stack[i] - sym->start_address);
            }
            continue;
        }

        printf("  %d [<%016llx>]\n", i, stack[i]);
        for (j = 0; j < result->entries[i].size; j++) {
            sym = &result->entries[i].syms[j];
            if (sym->path && sym->path[0]) {
                printf("        %s+0x%llx %s:%ld\n",
                       sym->symbol, stack[i] - sym->start_address,
                       sym->path, sym->line_no);
            } else {
                printf("        %s+0x%llx\n", sym->symbol,
                       stack[i] - sym->start_address);
            }
        }
    }

    blazesym_result_free(result);
}

/* Receive events from the ring buffer. */
static int event_handler(void *_ctx, void *data, size_t size)
{
    struct stacktrace_event *event = data;

    if (event->kstack_sz <= 0 && event->ustack_sz <= 0)
        return 1;

    printf("COMM: %s (pid=%d) @ CPU %d\n", event->comm, event->pid, event->cpu_id);

    if (event->kstack_sz > 0) {
        printf("Kernel:\n");
        show_stack_trace(event->kstack, event->kstack_sz / sizeof(__u64), 0);
    } else {
        printf("No Kernel Stack\n");
    }

    if (event->ustack_sz > 0) {
        printf("Userspace:\n");
        show_stack_trace(event->ustack, event->ustack_sz / sizeof(__u64), event->pid);
    } else {
        printf("No Userspace Stack\n");
    }

    printf("\n");
    return 0;
}
```

`show_stack_trace()` 函數用於顯示內核或用戶空間的棧回溯。它接收一個 stack 參數，是一個指向內核或用戶空間棧的指針，stack_sz 參數表示棧的大小，pid 參數表示要顯示的進程的 ID（當顯示內核棧時，設置為 0）。函數中首先根據 pid 參數確定棧的來源（內核或用戶空間），然後調用 blazesym_symbolize() 函數將棧中的地址解析為符號名和源代碼位置。最後，遍歷解析結果，輸出符號名和源代碼位置信息。

`event_handler()` 函數用於處理從 ring buffer 接收到的事件。它接收一個 data 參數，指向 ring buffer 中的數據，size 參數表示數據的大小。函數首先將 data 指針轉換為 stacktrace_event 結構體指針，然後檢查內核和用戶空間棧的大小。如果棧為空，則直接返回。接下來，函數輸出進程名稱、進程 ID 和 CPU ID 信息。然後分別顯示內核棧和用戶空間棧的回溯。調用 show_stack_trace() 函數時，分別傳入內核棧和用戶空間棧的地址、大小和進程 ID。

這兩個函數作為 eBPF profile 工具的一部分，用於顯示和處理 eBPF 程序收集到的棧回溯信息，幫助用戶瞭解程序的運行情況和性能瓶頸。

### 總結

通過本篇 eBPF 入門實踐教程，我們學習瞭如何使用 eBPF 程序進行性能分析。在這個過程中，我們詳細講解了如何創建 eBPF 程序，監控進程的性能，並從 ring buffer 中獲取數據以分析棧回溯。我們還學習瞭如何使用 perf_event_open() 函數設置性能監控，並將 BPF 程序附加到性能事件上。在本教程中，我們還展示瞭如何編寫 eBPF 程序來捕獲進程的內核和用戶空間棧信息，進而分析程序性能瓶頸。通過這個例子，您可以瞭解到 eBPF 在性能分析方面的強大功能。

如果您希望學習更多關於 eBPF 的知識和實踐，請查閱 eunomia-bpf 的官方文檔：<https://github.com/eunomia-bpf/eunomia-bpf> 。您還可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。

接下來的教程將進一步探討 eBPF 的高級特性，我們會繼續分享更多有關 eBPF 開發實踐的內容，幫助您更好地理解和掌握 eBPF 技術，希望這些內容對您在 eBPF 開發道路上的學習和實踐有所幫助。
