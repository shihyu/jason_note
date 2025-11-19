# eBPF開發實踐：使用 user ring buffer 向內核異步發送信息

eBPF，即擴展的Berkeley包過濾器（Extended Berkeley Packet Filter），是Linux內核中的一種革命性技術，它允許開發者在內核態中運行自定義的“微程序”，從而在不修改內核代碼的情況下改變系統行為或收集系統細粒度的性能數據。

eBPF的一個獨特之處是它不僅可以在內核態運行程序，從而訪問系統底層的狀態和資源，同時也可以通過特殊的數據結構與用戶態程序進行通信。關於這方面的一個重要概念就是內核態和用戶態之間的環形隊列——ring buffer。在許多實時或高性能要求的應用中，環形隊列是一種常用的數據結構。由於它的FIFO（先進先出）特性，使得數據在生產者和消費者之間可以持續、線性地流動，從而避免了頻繁的IO操作和不必要的內存 reallocation開銷。

在eBPF中，分別提供了兩種環形隊列: user ring buffer 和 kernel ring buffer，以實現用戶態和內核態之間的高效數據通信。本文是 eBPF 開發者教程的一部分，更詳細的內容可以在這裡找到：<https://eunomia.dev/tutorials/> 源代碼在 [GitHub 倉庫](https://github.com/eunomia-bpf/bpf-developer-tutorial) 中開源。

## 用戶態和內核態環形隊列—user ring buffer和kernel ring buffer

圍繞內核態和用戶態這兩個主要運行級別，eBPF提供了兩種相應的環形隊列數據結構：用戶態環形隊列——User ring buffer和內核態環形隊列——Kernel ring buffer。

Kernel ring buffer 則由 eBPF實現，專為Linux內核設計，用於追蹤和記錄內核日誌、性能統計信息等，它的能力是內核態和用戶態數據傳輸的核心，可以從內核態向用戶態傳送數據。Kernel ring buffer 在 5.7 版本的內核中被引入，目前已經被廣泛應用於內核日誌系統、性能分析工具等。

對於內核態往用戶態發送應用場景，如內核監控事件的發送、異步通知、狀態更新通知等，ring buffer 數據結構都能夠勝任。比如，當我們需要監聽網絡服務程序的大量端口狀態時，這些端口的開啟、關閉、錯誤等狀態更新就需由內核實時傳遞到用戶空間進行處理。而Linux 內核的日誌系統、性能分析工具等，也需要頻繁地將大量數據發送到用戶空間，以支持用戶人性化地展示和分析這些數據。在這些場景中，ring buffer在內核態往用戶態發送數據中表現出了極高的效率。

User ring buffer 是基於環形緩衝器的一種新型 Map 類型，它提供了單用戶空間生產者/單內核消費者的語義。這種環形隊列的優點是對異步消息傳遞提供了優秀的支持，避免了不必要的同步操作，使得內核到用戶空間的數據傳輸可以被優化，並且降低了系統調用的系統開銷。User ring buffer 在 6.1 版本的內核中被引入，目前的使用場景相對較少。

bpftime 是一個用戶空間 eBPF 運行時，允許現有 eBPF 應用程序在非特權用戶空間使用相同的庫和工具鏈運行。它為 eBPF 提供了 Uprobe 和 Syscall 跟蹤點，與內核 Uprobe 相比，性能有了顯著提高，而且無需手動檢測代碼或重啟進程。運行時支持用戶空間共享內存中的進程間 eBPF 映射，也兼容內核 eBPF 映射，允許與內核 eBPF 基礎架構無縫運行。它包括一個適用於各種架構的高性能 LLVM JIT，以及一個適用於 x86 的輕量級 JIT 和一個解釋器。GitHub 地址：<https://github.com/eunomia-bpf/bpftime>

在 bpftime 中，我們使用 user ring buffer 來實現用戶態 eBPF 往內核態 eBPF 發送數據，並更新內核態 eBPF 對應的 maps，讓內核態和用戶態的 eBPF 一起協同工作。user ring buffer 的異步特性，可以避免系統調用不必要的同步操作，從而提高了內核態和用戶態之間的數據傳輸效率。

eBPF 的雙向環形隊列也和 io_uring 在某些方面有相似之處，但它們的設計初衷和應用場景有所不同：

- **設計焦點**：io_uring主要專注於提高異步I/O操作的性能和效率，而eBPF的環形隊列更多關注於內核和用戶空間之間的數據通信和事件傳輸。
- **應用範圍**：io_uring主要用於文件I/O和網絡I/O的場景，而eBPF的環形隊列則更廣泛，不限於I/O操作，還包括系統調用跟蹤、網絡數據包處理等。
- **靈活性和擴展性**：eBPF提供了更高的靈活性和擴展性，允許用戶定義複雜的數據處理邏輯，並在內核態執行。

下面，我們將通過一段代碼示例，詳細展示如何利用 user ring buffer，實現從用戶態向內核傳送數據，並以 kernel ring buffer 相應地從內核態向用戶態傳送數據。

## 一、實現：在用戶態和內核態間使用 ring buffer 傳送數據

藉助新的 BPF MAP，我們可以實現在用戶態和內核態間通過環形緩衝區傳送數據。在這個示例中，我們將詳細說明如何在用戶空間創建一個 "用戶環形緩衝區" (user ring buffer) 並向其寫入數據，然後在內核空間中通過 `bpf_user_ringbuf_drain` 函數來消費這些數據。同時，我們也會使用 "內核環形緩衝區" (kernel ring buffer) 來從內核空間反饋數據到用戶空間。為此，我們需要在用戶空間和內核空間分別創建並操作這兩個環形緩衝區。

完整的代碼可以在 <https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/35-user-ringbuf> 中找到。

### 創建環形緩衝區

在內核空間，我們創建了一個類型為 `BPF_MAP_TYPE_USER_RINGBUF` 的 `user_ringbuf`，以及一個類型為 `BPF_MAP_TYPE_RINGBUF` 的 `kernel_ringbuf`。在用戶空間，我們創建了一個 `struct ring_buffer_user` 結構體的實例，並通過 `ring_buffer_user__new` 函數和對應的操作來管理這個用戶環形緩衝區。

```c
    /* Set up ring buffer polling */
    rb = ring_buffer__new(bpf_map__fd(skel->maps.kernel_ringbuf), handle_event, NULL, NULL);
    if (!rb)
    {
        err = -1;
        fprintf(stderr, "Failed to create ring buffer\n");
        goto cleanup;
    }
    user_ringbuf = user_ring_buffer__new(bpf_map__fd(skel->maps.user_ringbuf), NULL);
```

### 編寫內核態程序

我們定義一個 `kill_exit` 的 tracepoint 程序，每當有進程退出時，它會通過 `bpf_user_ringbuf_drain` 函數讀取 `user_ringbuf` 中的用戶數據，然後通過 `bpf_ringbuf_reserve` 函數在 `kernel_ringbuf` 中創建一個新的記錄，並寫入相關信息。最後，通過 `bpf_ringbuf_submit` 函數將這個記錄提交，使得該記錄能夠被用戶空間讀取。

```c
// SPDX-License-Identifier: GPL-2.0
/* Copyright (c) 2022 Meta Platforms, Inc. and affiliates. */

#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "user_ringbuf.h"

char _license[] SEC("license") = "GPL";

struct
{
    __uint(type, BPF_MAP_TYPE_USER_RINGBUF);
    __uint(max_entries, 256 * 1024);
} user_ringbuf SEC(".maps");

struct
{
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} kernel_ringbuf SEC(".maps");

int read = 0;

static long
do_nothing_cb(struct bpf_dynptr *dynptr, void *context)
{
    struct event *e;
    pid_t pid;
    /* get PID and TID of exiting thread/process */
    pid = bpf_get_current_pid_tgid() >> 32;

    /* reserve sample from BPF ringbuf */
    e = bpf_ringbuf_reserve(&kernel_ringbuf, sizeof(*e), 0);
    if (!e)
        return 0;

    e->pid = pid;
    bpf_get_current_comm(&e->comm, sizeof(e->comm));

    /* send data to user-space for post-processing */
    bpf_ringbuf_submit(e, 0);
    __sync_fetch_and_add(&read, 1);
    return 0;
}

SEC("tracepoint/syscalls/sys_exit_kill")
int kill_exit(struct trace_event_raw_sys_exit *ctx)
{
    long num_samples;
    int err = 0;
    
    // receive data from userspace
    num_samples = bpf_user_ringbuf_drain(&user_ringbuf, do_nothing_cb, NULL, 0);

    return 0;
}
```

### 編寫用戶態程序

在用戶空間，我們通過 `ring_buffer_user__reserve` 函數在 ring buffer 中預留出一段空間，這段空間用於寫入我們希望傳遞給內核的信息。然後，通過 `ring_buffer_user__submit` 函數提交數據，之後這些數據就可以在內核態被讀取。

```c
static int write_samples(struct user_ring_buffer *ringbuf)
{
    int i, err = 0;
    struct user_sample *entry;

    entry = user_ring_buffer__reserve(ringbuf, sizeof(*entry));
    if (!entry)
    {
        err = -errno;
        goto done;
    }

    entry->i = getpid();
    strcpy(entry->comm, "hello");

    int read = snprintf(entry->comm, sizeof(entry->comm), "%u", i);
    if (read <= 0)
    {
        /* Assert on the error path to avoid spamming logs with
         * mostly success messages.
         */
        err = read;
        user_ring_buffer__discard(ringbuf, entry);
        goto done;
    }

    user_ring_buffer__submit(ringbuf, entry);

done:
    drain_current_samples();

    return err;
}
```

### 初始化環形緩衝區並輪詢

最後，對 ring buffer 進行初始化並定時輪詢，這樣我們就可以實時得知內核態的數據消費情況，我們還可以在用戶空間對 `user_ringbuf` 進行寫入操作，然後在內核態對其進行讀取和處理。

```c
    write_samples(user_ringbuf);

    /* Process events */
    printf("%-8s %-5s %-16s %-7s %-7s %s\n",
           "TIME", "EVENT", "COMM", "PID", "PPID", "FILENAME/EXIT CODE");
    while (!exiting)
    {
        err = ring_buffer__poll(rb, 100 /* timeout, ms */);
        /* Ctrl-C will cause -EINTR */
        if (err == -EINTR)
        {
            err = 0;
            break;
        }
        if (err < 0)
        {
            printf("Error polling perf buffer: %d\n", err);
            break;
        }
    }
```

通過以上步驟，我們實現了用戶態與內核態間環形緩衝區的雙向數據傳輸。

## 二、編譯和運行代碼

為了編譯和運行以上代碼，我們可以通過以下命令來實現：

```sh
make
```

關於如何安裝依賴，請參考：<https://eunomia.dev/tutorials/11-bootstrap/>

運行結果將展示如何使用 user ring buffer 和 kernel ringbuffer 在用戶態和內核態間進行高效的數據傳輸:

```console
$ sudo ./user_ringbuf
Draining current samples...
TIME     EVENT COMM             PID   
16:31:37 SIGN  node             1707   
Draining current samples...
16:31:38 SIGN  node             1981   
Draining current samples...
16:31:38 SIGN  node             1707   
Draining current samples...
16:31:38 SIGN  node             1707   
Draining current samples...
```

## 總結

在本篇文章中，我們介紹瞭如何使用eBPF的user ring buffer和kernel ring buffer在用戶態和內核態之間進行數據傳輸。通過這種方式，我們可以有效地將用戶態的數據傳送給內核，或者將內核生成的數據反饋給用戶，從而實現了內核態和用戶態的雙向通信。

如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。

參考資料：

1. [https://lwn.net/Articles/907056/](https://lwn.net/Articles/907056/)

> 原文地址：<https://eunomia.dev/zh/tutorials/35-user-ringbuf/> 轉載請註明出處。
