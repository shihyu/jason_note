# eBPF 入門實踐教程十五：使用 USDT 捕獲用戶態 Java GC 事件耗時

eBPF (擴展的伯克利數據包過濾器) 是一項強大的網絡和性能分析工具，被廣泛應用在 Linux 內核上。eBPF 使得開發者能夠動態地加載、更新和運行用戶定義的代碼，而無需重啟內核或更改內核源代碼。這個特性使得 eBPF 能夠提供極高的靈活性和性能，使其在網絡和系統性能分析方面具有廣泛的應用。此外，eBPF 還支持使用 USDT (用戶級靜態定義跟蹤點) 捕獲用戶態的應用程序行為。

在我們的 eBPF 入門實踐教程系列的這一篇，我們將介紹如何使用 eBPF 和 USDT 來捕獲和分析 Java 的垃圾回收 (GC) 事件的耗時。

## USDT 介紹

USDT 是一種在應用程序中插入靜態跟蹤點的機制，它允許開發者在程序的關鍵位置插入可用於調試和性能分析的探針。這些探針可以在運行時被 DTrace、SystemTap 或 eBPF 等工具動態激活，從而在不重啟應用程序或更改程序代碼的情況下，獲取程序的內部狀態和性能指標。USDT 在很多開源軟件，如 MySQL、PostgreSQL、Ruby、Python 和 Node.js 等都有廣泛的應用。

### 用戶層面的追蹤機制：用戶級動態跟蹤和 USDT

在用戶層面進行動態跟蹤，即用戶級動態跟蹤（User-Level Dynamic Tracing）允許我們對任何用戶級別的代碼進行插樁。比如，我們可以通過在 MySQL 服務器的 `dispatch_command()` 函數上進行插樁，來跟蹤服務器的查詢請求：

```bash
# ./uprobe 'p:cmd /opt/bin/mysqld:_Z16dispatch_command19enum_server_commandP3THDPcj +0(%dx):string'
Tracing uprobe cmd (p:cmd /opt/bin/mysqld:0x2dbd40 +0(%dx):string). Ctrl-C to end.
  mysqld-2855  [001] d... 19957757.590926: cmd: (0x6dbd40) arg1="show tables"
  mysqld-2855  [001] d... 19957759.703497: cmd: (0x6dbd40) arg1="SELECT * FROM numbers"
[...]
```

這裡我們使用了 `uprobe` 工具，它利用了 Linux 的內置功能：ftrace（跟蹤器）和 uprobes（用戶級動態跟蹤，需要較新的 Linux 版本，例如 4.0 左右）。其他的跟蹤器，如 perf_events 和 SystemTap，也可以實現此功能。

許多其他的 MySQL 函數也可以被跟蹤以獲取更多的信息。我們可以列出和計算這些函數的數量：

```bash
# ./uprobe -l /opt/bin/mysqld | more
account_hash_get_key
add_collation
add_compiled_collation
add_plugin_noargs
adjust_time_range
[...]
# ./uprobe -l /opt/bin/mysqld | wc -l
21809
```

這有 21,000 個函數。我們也可以跟蹤庫函數，甚至是單個的指令偏移。

用戶級動態跟蹤的能力是非常強大的，它可以解決無數的問題。然而，使用它也有一些困難：需要確定需要跟蹤的代碼，處理函數參數，以及應對代碼的更改。

用戶級靜態定義跟蹤（User-level Statically Defined Tracing, USDT）則可以在某種程度上解決這些問題。USDT 探針（或者稱為用戶級 "marker"）是開發者在代碼的關鍵位置插入的跟蹤宏，提供穩定且已經過文檔說明的 API。這使得跟蹤工作變得更加簡單。

使用 USDT，我們可以簡單地跟蹤一個名為 `mysql:query__start` 的探針，而不是去跟蹤那個名為 `_Z16dispatch_command19enum_server_commandP3THDPcj` 的 C++ 符號，也就是 `dispatch_command()` 函數。當然，我們仍然可以在需要的時候去跟蹤 `dispatch_command()` 以及其他 21,000 個 mysqld 函數，但只有當 USDT 探針無法解決問題的時候我們才需要這麼做。

在 Linux 中的 USDT，無論是哪種形式的靜態跟蹤點，其實都已經存在了幾十年。它最近由於 Sun 的 DTrace 工具的流行而再次受到關注，這使得許多常見的應用程序，包括 MySQL、PostgreSQL、Node.js、Java 等都加入了 USDT。SystemTap 則開發了一種可以消費這些 DTrace 探針的方式。

你可能正在運行一個已經包含了 USDT 探針的 Linux 應用程序，或者可能需要重新編譯（通常是 --enable-dtrace）。你可以使用 `readelf` 來進行檢查，例如對於 Node.js：

```bash
# readelf -n node
[...]
Notes at offset 0x00c43058 with length 0x00000494:
  Owner                 Data size   Description
  stapsdt              0x0000003c   NT_STAPSDT (SystemTap probe descriptors)
    Provider: node
    Name: gc__start
    Location: 0x0000000000bf44b4, Base: 0x0000000000f22464, Semaphore: 0x0000000001243028
    Arguments: 4@%esi 4@%edx 8@%rdi
[...]
  stapsdt              0x00000082       NT_STAPSDT (SystemTap probe descriptors)
    Provider: node
    Name: http__client__request
    Location: 0x0000000000bf48ff, Base: 0x0000000000f22464, Semaphore: 0x0000000001243024
    Arguments: 8@%rax 8@%rdx 8@-136(%rbp) -4@-140(%rbp) 8@-72(%rbp) 8@-80(%rbp) -4@-144(%rbp)
[...]
```

這就是使用 --enable-dtrace 重新編譯的 node，以及安裝了提供 "dtrace" 功能來構建 USDT 支持的 systemtap-sdt-dev 包。這裡顯示了兩個探針：node:gc__start（開始進行垃圾回收）和 node:http__client__request。

在這一點上，你可以使用 SystemTap 或者 LTTng 來跟蹤這些探針。然而，內置的 Linux 跟蹤器，比如 ftrace 和 perf_events，目前還無法做到這一點（儘管 perf_events 的支持正在開發中）。

USDT 在內核態 eBPF 運行時，也可能產生比較大的性能開銷，這時候也可以考慮使用用戶態 eBPF 運行時，例如  [bpftime](https://github.com/eunomia-bpf/bpftime)。bpftime 是一個基於 LLVM JIT/AOT 的用戶態 eBPF 運行時，它可以在用戶態運行 eBPF 程序，和內核態的 eBPF 兼容，避免了內核態和用戶態之間的上下文切換，從而提高了 eBPF 程序的執行效率。對於 uprobe 而言，bpftime 的性能開銷比 kernel 小一個數量級。

## Java GC 介紹

Java 作為一種高級編程語言，其自動垃圾回收（GC）是其核心特性之一。Java GC 的目標是自動地回收那些不再被程序使用的內存空間，從而減輕程序員在內存管理方面的負擔。然而，GC 過程可能會引發應用程序的停頓，對程序的性能和響應時間產生影響。因此，對 Java GC 事件進行監控和分析，對於理解和優化 Java 應用的性能是非常重要的。

在接下來的教程中，我們將演示如何使用 eBPF 和 USDT 來監控和分析 Java GC 事件的耗時，希望這些內容對你在使用 eBPF 進行應用性能分析方面的工作有所幫助。

## eBPF 實現機制

Java GC 的 eBPF 程序分為內核態和用戶態兩部分，我們會分別介紹這兩部分的實現機制。

### 內核態程序

```c
/* SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause) */
/* Copyright (c) 2022 Chen Tao */
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_core_read.h>
#include <bpf/usdt.bpf.h>
#include "javagc.h"

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 100);
    __type(key, uint32_t);
    __type(value, struct data_t);
} data_map SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __type(key, int);
    __type(value, int);
} perf_map SEC(".maps");

__u32 time;

static int gc_start(struct pt_regs *ctx)
{
    struct data_t data = {};

    data.cpu = bpf_get_smp_processor_id();
    data.pid = bpf_get_current_pid_tgid() >> 32;
    data.ts = bpf_ktime_get_ns();
    bpf_map_update_elem(&data_map, &data.pid, &data, 0);
    return 0;
}

static int gc_end(struct pt_regs *ctx)
{
    struct data_t data = {};
    struct data_t *p;
    __u32 val;

    data.cpu = bpf_get_smp_processor_id();
    data.pid = bpf_get_current_pid_tgid() >> 32;
    data.ts = bpf_ktime_get_ns();
    p = bpf_map_lookup_elem(&data_map, &data.pid);
    if (!p)
        return 0;

    val = data.ts - p->ts;
    if (val > time) {
        data.ts = val;
        bpf_perf_event_output(ctx, &perf_map, BPF_F_CURRENT_CPU, &data, sizeof(data));
    }
    bpf_map_delete_elem(&data_map, &data.pid);
    return 0;
}

SEC("usdt")
int handle_gc_start(struct pt_regs *ctx)
{
    return gc_start(ctx);
}

SEC("usdt")
int handle_gc_end(struct pt_regs *ctx)
{
    return gc_end(ctx);
}

SEC("usdt")
int handle_mem_pool_gc_start(struct pt_regs *ctx)
{
    return gc_start(ctx);
}

SEC("usdt")
int handle_mem_pool_gc_end(struct pt_regs *ctx)
{
    return gc_end(ctx);
}

char LICENSE[] SEC("license") = "Dual BSD/GPL";
```

首先，我們定義了兩個映射（map）：

- `data_map`：這個 hashmap 存儲每個進程 ID 的垃圾收集開始時間。`data_t` 結構體包含進程 ID、CPU ID 和時間戳。
- `perf_map`：這是一個 perf event array，用於將數據發送回用戶態程序。

然後，我們有四個處理函數：`gc_start`、`gc_end` 和兩個 USDT 處理函數 `handle_mem_pool_gc_start` 和 `handle_mem_pool_gc_end`。這些函數都用 BPF 的 `SEC("usdt")` 宏註解，以便在 Java 進程中捕獲到與垃圾收集相關的 USDT 事件。

`gc_start` 函數在垃圾收集開始時被調用。它首先獲取當前的 CPU ID、進程 ID 和時間戳，然後將這些數據存入 `data_map`。

`gc_end` 函數在垃圾收集結束時被調用。它執行與 `gc_start` 類似的操作，但是它還從 `data_map` 中檢索開始時間，並計算垃圾收集的持續時間。如果持續時間超過了設定的閾值（變量 `time`），那麼它將數據發送回用戶態程序。

`handle_gc_start` 和 `handle_gc_end` 是針對垃圾收集開始和結束事件的處理函數，它們分別調用了 `gc_start` 和 `gc_end`。

`handle_mem_pool_gc_start` 和 `handle_mem_pool_gc_end` 是針對內存池的垃圾收集開始和結束事件的處理函數，它們也分別調用了 `gc_start` 和 `gc_end`。

最後，我們有一個 `LICENSE` 數組，聲明瞭該 BPF 程序的許可證，這是加載 BPF 程序所必需的。

### 用戶態程序

用戶態程序的主要目標是加載和運行eBPF程序，以及處理來自內核態程序的數據。它是通過 libbpf 庫來完成這些操作的。這裡我們省略了一些通用的加載和運行 eBPF 程序的代碼，只展示了與 USDT 相關的部分。

第一個函數 `get_jvmso_path` 被用來獲取運行的Java虛擬機（JVM）的 `libjvm.so` 庫的路徑。首先，它打開了 `/proc/<pid>/maps` 文件，該文件包含了進程地址空間的內存映射信息。然後，它在文件中搜索包含 `libjvm.so` 的行，然後複製該行的路徑到提供的參數中。

```c
static int get_jvmso_path(char *path)
{
    char mode[16], line[128], buf[64];
    size_t seg_start, seg_end, seg_off;
    FILE *f;
    int i = 0;

    sprintf(buf, "/proc/%d/maps", env.pid);
    f = fopen(buf, "r");
    if (!f)
        return -1;

    while (fscanf(f, "%zx-%zx %s %zx %*s %*d%[^\n]\n",
            &seg_start, &seg_end, mode, &seg_off, line) == 5) {
        i = 0;
        while (isblank(line[i]))
            i++;
        if (strstr(line + i, "libjvm.so")) {
            break;
        }
    }

    strcpy(path, line + i);
    fclose(f);

    return 0;
}
```

接下來，我們看到的是將 eBPF 程序（函數 `handle_gc_start` 和 `handle_gc_end`）附加到Java進程的相關USDT探針上。每個程序都通過調用 `bpf_program__attach_usdt` 函數來實現這一點，該函數的參數包括BPF程序、進程ID、二進制路徑以及探針的提供者和名稱。如果探針掛載成功，`bpf_program__attach_usdt` 將返回一個鏈接對象，該對象將存儲在skeleton的鏈接成員中。如果掛載失敗，程序將打印錯誤消息並進行清理。

```c
    skel->links.handle_mem_pool_gc_start = bpf_program__attach_usdt(skel->progs.handle_gc_start, env.pid,
                                    binary_path, "hotspot", "mem__pool__gc__begin", NULL);
    if (!skel->links.handle_mem_pool_gc_start) {
        err = errno;
        fprintf(stderr, "attach usdt mem__pool__gc__begin failed: %s\n", strerror(err));
        goto cleanup;
    }

    skel->links.handle_mem_pool_gc_end = bpf_program__attach_usdt(skel->progs.handle_gc_end, env.pid,
                                binary_path, "hotspot", "mem__pool__gc__end", NULL);
    if (!skel->links.handle_mem_pool_gc_end) {
        err = errno;
        fprintf(stderr, "attach usdt mem__pool__gc__end failed: %s\n", strerror(err));
        goto cleanup;
    }

    skel->links.handle_gc_start = bpf_program__attach_usdt(skel->progs.handle_gc_start, env.pid,
                                    binary_path, "hotspot", "gc__begin", NULL);
    if (!skel->links.handle_gc_start) {
        err = errno;
        fprintf(stderr, "attach usdt gc__begin failed: %s\n", strerror(err));
        goto cleanup;
    }

    skel->links.handle_gc_end = bpf_program__attach_usdt(skel->progs.handle_gc_end, env.pid,
                binary_path, "hotspot", "gc__end", NULL);
    if (!skel->links.handle_gc_end) {
        err = errno;
        fprintf(stderr, "attach usdt gc__end failed: %s\n", strerror(err));
        goto cleanup;
    }
```

最後一個函數 `handle_event` 是一個回調函數，用於處理從perf event array收到的數據。這個函數會被 perf event array 觸發，並在每次接收到新的事件時調用。函數首先將數據轉換為 `data_t` 結構體，然後將當前時間格式化為字符串，並打印出事件的時間戳、CPU ID、進程 ID，以及垃圾回收的持續時間。

```c
static void handle_event(void *ctx, int cpu, void *data, __u32 data_sz)
{
    struct data_t *e = (struct data_t *)data;
    struct tm *tm = NULL;
    char ts[16];
    time_t t;

    time(&t);
    tm = localtime(&t);
    strftime(ts, sizeof(ts), "%H:%M:%S", tm);
    printf("%-8s %-7d %-7d %-7lld\n", ts, e->cpu, e->pid, e->ts/1000);
}
```

## 安裝依賴

構建示例需要 clang、libelf 和 zlib。包名在不同的發行版中可能會有所不同。

在 Ubuntu/Debian 上，你需要執行以下命令：

```shell
sudo apt install clang libelf1 libelf-dev zlib1g-dev
```

在 CentOS/Fedora 上，你需要執行以下命令：

```shell
sudo dnf install clang elfutils-libelf elfutils-libelf-devel zlib-devel
```

## 編譯運行

在對應的目錄中，運行 Make 即可編譯運行上述代碼：

```console
$ make
$ sudo ./javagc -p 12345
Tracing javagc time... Hit Ctrl-C to end.
TIME     CPU     PID     GC TIME
10:00:01 10%     12345   50ms
10:00:02 12%     12345   55ms
10:00:03 9%      12345   47ms
10:00:04 13%     12345   52ms
10:00:05 11%     12345   50ms
```

完整源代碼：

- <https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/15-javagc>

參考資料：

- <https://www.brendangregg.com/blog/2015-07-03/hacking-linux-usdt-ftrace.html>
- <https://github.com/iovisor/bcc/blob/master/libbpf-tools/javagc.c>

## 總結

通過本篇 eBPF 入門實踐教程，我們學習瞭如何使用 eBPF 和 USDT 動態跟蹤和分析 Java 的垃圾回收(GC)事件。我們瞭解瞭如何在用戶態應用程序中設置 USDT 跟蹤點，以及如何編寫 eBPF 程序來捕獲這些跟蹤點的信息，從而更深入地理解和優化 Java GC 的行為和性能。

此外，我們也介紹了一些關於 Java GC、USDT 和 eBPF 的基礎知識和實踐技巧，這些知識和技巧對於想要在網絡和系統性能分析領域深入研究的開發者來說是非常有價值的。

如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。

> The original link of this article: <https://eunomia.dev/tutorials/15-javagc>
