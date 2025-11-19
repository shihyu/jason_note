# eBPF 入門實踐教程十六：編寫 eBPF 程序 Memleak 監控內存洩漏

eBPF（擴展的伯克利數據包過濾器）是一項強大的網絡和性能分析工具，被廣泛應用在 Linux 內核上。eBPF 使得開發者能夠動態地加載、更新和運行用戶定義的代碼，而無需重啟內核或更改內核源代碼。

在本篇教程中，我們將探討如何使用 eBPF 編寫 Memleak 程序，以監控程序的內存洩漏。

## 背景及其重要性

內存洩漏是計算機編程中的一種常見問題，其嚴重程度不應被低估。內存洩漏發生時，程序會逐漸消耗更多的內存資源，但並未正確釋放。隨著時間的推移，這種行為會導致系統內存逐漸耗盡，從而顯著降低程序及系統的整體性能。

內存洩漏有多種可能的原因。這可能是由於配置錯誤導致的，例如程序錯誤地配置了某些資源的動態分配。它也可能是由於軟件缺陷或錯誤的內存管理策略導致的，如在程序執行過程中忘記釋放不再需要的內存。此外，如果一個應用程序的內存使用量過大，那麼系統性能可能會因頁面交換（swapping）而大幅下降，甚至可能導致應用程序被系統強制終止（Linux 的 OOM killer）。

### 調試內存洩漏的挑戰

調試內存洩漏問題是一項複雜且挑戰性的任務。這涉及到詳細檢查應用程序的配置、內存分配和釋放情況，通常需要應用專門的工具來幫助診斷。例如，有一些工具可以在應用程序啟動時將 malloc() 函數調用與特定的檢測工具關聯起來，如 Valgrind memcheck，這類工具可以模擬 CPU 來檢查所有內存訪問，但可能會導致應用程序運行速度大大減慢。另一個選擇是使用堆分析器，如 libtcmalloc，它相對較快，但仍可能使應用程序運行速度降低五倍以上。此外，還有一些工具，如 gdb，可以獲取應用程序的核心轉儲並進行後處理以分析內存使用情況。然而，這些工具通常在獲取核心轉儲時需要暫停應用程序，或在應用程序終止後才能調用 free() 函數。

## eBPF 的作用

在這種背景下，eBPF 的作用就顯得尤為重要。eBPF 提供了一種高效的機制來監控和追蹤系統級別的事件，包括內存的分配和釋放。通過 eBPF，我們可以跟蹤內存分配和釋放的請求，並收集每次分配的調用堆棧。然後，我們可以分

析這些信息，找出執行了內存分配但未執行釋放操作的調用堆棧，這有助於我們找出導致內存洩漏的源頭。這種方式的優點在於，它可以實時地在運行的應用程序中進行，而無需暫停應用程序或進行復雜的前後處理。

`memleak` eBPF 工具可以跟蹤並匹配內存分配和釋放的請求，並收集每次分配的調用堆棧。隨後，`memleak` 可以打印一個總結，表明哪些調用堆棧執行了分配，但是並沒有隨後進行釋放。例如，我們運行命令：

```console
# ./memleak -p $(pidof allocs)
Attaching to pid 5193, Ctrl+C to quit.
[11:16:33] Top 2 stacks with outstanding allocations:
        80 bytes in 5 allocations from stack
                 main+0x6d [allocs]
                 __libc_start_main+0xf0 [libc-2.21.so]

[11:16:34] Top 2 stacks with outstanding allocations:
        160 bytes in 10 allocations from stack
                 main+0x6d [allocs]
                 __libc_start_main+0xf0 [libc-2.21.so]
```

運行這個命令後，我們可以看到分配但未釋放的內存來自於哪些堆棧，並且可以看到這些未釋放的內存的大小和數量。

隨著時間的推移，很顯然，`allocs` 進程的 `main` 函數正在洩漏內存，每次洩漏 16 字節。幸運的是，我們不需要檢查每個分配，我們得到了一個很好的總結，告訴我們哪個堆棧負責大量的洩漏。

## memleak 的實現原理

在基本層面上，`memleak` 的工作方式類似於在內存分配和釋放路徑上安裝監控設備。它通過在內存分配和釋放函數中插入 eBPF 程序來達到這個目標。這意味著，當這些函數被調用時，`memleak` 就會記錄一些重要信息，如調用者的進程 ID（PID）、分配的內存地址以及分配的內存大小等。當釋放內存的函數被調用時，`memleak` 則會在其內部的映射表（map）中刪除相應的內存分配記錄。這種機制使得 `memleak` 能夠準確地追蹤到哪些內存塊已被分配但未被釋放。

對於用戶態的常用內存分配函數，如 `malloc` 和 `calloc` 等，`memleak` 利用了用戶態探測（uprobe）技術來實現監控。uprobe 是一種用於用戶空間應用程序的動態追蹤技術，它可以在運行時不修改二進制文件的情況下在任意位置設置斷點，從而實現對特定函數調用的追蹤。Uprobe 在內核態 eBPF 運行時，也可能產生比較大的性能開銷，這時候也可以考慮使用用戶態 eBPF 運行時，例如  [bpftime](https://github.com/eunomia-bpf/bpftime)。bpftime 是一個基於 LLVM JIT/AOT 的用戶態 eBPF 運行時，它可以在用戶態運行 eBPF 程序，和內核態的 eBPF 兼容，避免了內核態和用戶態之間的上下文切換，從而提高了 eBPF 程序的執行效率。對於 uprobe 而言，bpftime 的性能開銷比 kernel 小一個數量級。

對於內核態的內存分配函數，如 `kmalloc` 等，`memleak` 則選擇使用了 tracepoint 來實現監控。Tracepoint 是一種在 Linux 內核中提供的動態追蹤技術，它可以在內核運行時動態地追蹤特定的事件，而無需重新編譯內核或加載內核模塊。

## 內核態 eBPF 程序實現

## `memleak` 內核態 eBPF 程序實現

`memleak` 的內核態 eBPF 程序包含一些用於跟蹤內存分配和釋放的關鍵函數。在我們深入瞭解這些函數之前，讓我們首先觀察 `memleak` 所定義的一些數據結構，這些結構在其內核態和用戶態程序中均有使用。

```c
#ifndef __MEMLEAK_H
#define __MEMLEAK_H

#define ALLOCS_MAX_ENTRIES 1000000
#define COMBINED_ALLOCS_MAX_ENTRIES 10240

struct alloc_info {
    __u64 size;            // 分配的內存大小
    __u64 timestamp_ns;    // 分配時的時間戳，單位為納秒
    int stack_id;          // 分配時的調用堆棧ID
};

union combined_alloc_info {
    struct {
        __u64 total_size : 40;        // 所有未釋放分配的總大小
        __u64 number_of_allocs : 24;   // 所有未釋放分配的總次數
    };
    __u64 bits;    // 結構的位圖表示
};

#endif /* __MEMLEAK_H */
```

這裡定義了兩個主要的數據結構：`alloc_info` 和 `combined_alloc_info`。

`alloc_info` 結構體包含了一個內存分配的基本信息，包括分配的內存大小 `size`、分配發生時的時間戳 `timestamp_ns`，以及觸發分配的調用堆棧 ID `stack_id`。

`combined_alloc_info` 是一個聯合體（union），它包含一個嵌入的結構體和一個 `__u64` 類型的位圖表示 `bits`。嵌入的結構體有兩個成員：`total_size` 和 `number_of_allocs`，分別代表所有未釋放分配的總大小和總次數。其中 40 和 24 分別表示 total_size 和 number_of_allocs這兩個成員變量所佔用的位數，用來限制其大小。通過這樣的位數限制，可以節省combined_alloc_info結構的存儲空間。同時，由於total_size和number_of_allocs在存儲時是共用一個unsigned long long類型的變量bits，因此可以通過在成員變量bits上進行位運算來訪問和修改total_size和number_of_allocs，從而避免了在程序中定義額外的變量和函數的複雜性。

接下來，`memleak` 定義了一系列用於保存內存分配信息和分析結果的 eBPF 映射（maps）。這些映射都以 `SEC(".maps")` 的形式定義，表示它們屬於 eBPF 程序的映射部分。

```c
const volatile size_t min_size = 0;
const volatile size_t max_size = -1;
const volatile size_t page_size = 4096;
const volatile __u64 sample_rate = 1;
const volatile bool trace_all = false;
const volatile __u64 stack_flags = 0;
const volatile bool wa_missing_free = false;

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __type(key, pid_t);
    __type(value, u64);
    __uint(max_entries, 10240);
} sizes SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __type(key, u64); /* address */
    __type(value, struct alloc_info);
    __uint(max_entries, ALLOCS_MAX_ENTRIES);
} allocs SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __type(key, u64); /* stack id */
    __type(value, union combined_alloc_info);
    __uint(max_entries, COMBINED_ALLOCS_MAX_ENTRIES);
} combined_allocs SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __type(key, u64);
    __type(value, u64);
    __uint(max_entries, 10240);
} memptrs SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_STACK_TRACE);
    __type(key, u32);
} stack_traces SEC(".maps");

static union combined_alloc_info initial_cinfo;
```

這段代碼首先定義了一些可配置的參數，如 `min_size`, `max_size`, `page_size`, `sample_rate`, `trace_all`, `stack_flags` 和 `wa_missing_free`，分別表示最小分配大小、最大分配大小、頁面大小、採樣率、是否追蹤所有分配、堆棧標誌和是否工作在缺失釋放（missing free）模式。

接著定義了五個映射：

1. `sizes`：這是一個哈希類型的映射，鍵為進程 ID，值為 `u64` 類型，存儲每個進程的分配大小。
2. `allocs`：這也是一個哈希類型的映射，鍵為分配的地址，值為 `alloc_info` 結構體，存儲每個內存分配的詳細信息。
3. `combined_allocs`：這是另一個哈希類型的映射，鍵為堆棧 ID，值為 `combined_alloc_info` 聯合體，存儲所有未釋放分配的總大小和總次數。
4. `memptrs`：這也是一個哈希類型的映射，鍵和值都為 `u64` 類型，用於在用戶空間和內核空間之間傳遞內存指針。
5. `stack_traces`：這是一個堆棧追蹤類型的映射，鍵為 `u32` 類型，用於存儲堆棧 ID。

以用戶態的內存分配追蹤部分為例，主要是掛鉤內存相關的函數調用，如 `malloc`, `free`, `calloc`, `realloc`, `mmap` 和 `munmap`，以便在調用這些函數時進行數據記錄。在用戶態，`memleak` 主要使用了 uprobes 技術進行掛載。

每個函數調用被分為 "enter" 和 "exit" 兩部分。"enter" 部分記錄的是函數調用的參數，如分配的大小或者釋放的地址。"exit" 部分則主要用於獲取函數的返回值，如分配得到的內存地址。

這裡，`gen_alloc_enter`, `gen_alloc_exit`, `gen_free_enter` 是實現記錄行為的函數，他們分別用於記錄分配開始、分配結束和釋放開始的相關信息。

函數原型示例如下：

```c
SEC("uprobe")
int BPF_KPROBE(malloc_enter, size_t size)
{
    // 記錄分配開始的相關信息
    return gen_alloc_enter(size);
}

SEC("uretprobe")
int BPF_KRETPROBE(malloc_exit)
{
    // 記錄分配結束的相關信息
    return gen_alloc_exit(ctx);
}

SEC("uprobe")
int BPF_KPROBE(free_enter, void *address)
{
    // 記錄釋放開始的相關信息
    return gen_free_enter(address);
}
```

其中，`malloc_enter` 和 `free_enter` 是分別掛載在 `malloc` 和 `free` 函數入口處的探針（probes），用於在函數調用時進行數據記錄。而 `malloc_exit` 則是掛載在 `malloc` 函數的返回處的探針，用於記錄函數的返回值。

這些函數使用了 `BPF_KPROBE` 和 `BPF_KRETPROBE` 這兩個宏來聲明，這兩個宏分別用於聲明 kprobe（內核探針）和 kretprobe（內核返回探針）。具體來說，kprobe 用於在函數調用時觸發，而 kretprobe 則是在函數返回時觸發。

`gen_alloc_enter` 函數是在內存分配請求的開始時被調用的。這個函數主要負責在調用分配內存的函數時收集一些基本的信息。下面我們將深入探討這個函數的實現。

```c
static int gen_alloc_enter(size_t size)
{
    if (size < min_size || size > max_size)
        return 0;

    if (sample_rate > 1) {
        if (bpf_ktime_get_ns() % sample_rate != 0)
            return 0;
    }

    const pid_t pid = bpf_get_current_pid_tgid() >> 32;
    bpf_map_update_elem(&sizes, &pid, &size, BPF_ANY);

    if (trace_all)
        bpf_printk("alloc entered, size = %lu\n", size);

    return 0;
}

SEC("uprobe")
int BPF_KPROBE(malloc_enter, size_t size)
{
    return gen_alloc_enter(size);
}
```

首先，`gen_alloc_enter` 函數接收一個 `size` 參數，這個參數表示請求分配的內存的大小。如果這個值不在 `min_size` 和 `max_size` 之間，函數將直接返回，不再進行後續的操作。這樣可以使工具專注於追蹤特定範圍的內存分配請求，過濾掉不感興趣的分配請求。

接下來，函數檢查採樣率 `sample_rate`。如果 `sample_rate` 大於1，意味著我們不需要追蹤所有的內存分配請求，而是週期性地追蹤。這裡使用 `bpf_ktime_get_ns` 獲取當前的時間戳，然後通過取模運算來決定是否需要追蹤當前的內存分配請求。這是一種常見的採樣技術，用於降低性能開銷，同時還能夠提供一個代表性的樣本用於分析。

之後，函數使用 `bpf_get_current_pid_tgid` 函數獲取當前進程的 PID。注意這裡的 PID 實際上是進程和線程的組合 ID，我們通過右移 32 位來獲取真正的進程 ID。

函數接下來更新 `sizes` 這個 map，這個 map 以進程 ID 為鍵，以請求的內存分配大小為值。`BPF_ANY` 表示如果 key 已存在，那麼更新 value，否則就新建一個條目。

最後，如果啟用了 `trace_all` 標誌，函數將打印一條信息，說明發生了內存分配。

`BPF_KPROBE` 宏用於

最後定義了 `BPF_KPROBE(malloc_enter, size_t size)`，它會在 `malloc` 函數被調用時被 BPF uprobe 攔截執行，並通過 `gen_alloc_enter` 來記錄內存分配大小。
我們剛剛分析了內存分配的入口函數 `gen_alloc_enter`，現在我們來關注這個過程的退出部分。具體來說，我們將討論 `gen_alloc_exit2` 函數以及如何從內存分配調用中獲取返回的內存地址。

```c
static int gen_alloc_exit2(void *ctx, u64 address)
{
    const pid_t pid = bpf_get_current_pid_tgid() >> 32;
    struct alloc_info info;

    const u64* size = bpf_map_lookup_elem(&sizes, &pid);
    if (!size)
        return 0; // missed alloc entry

    __builtin_memset(&info, 0, sizeof(info));

    info.size = *size;
    bpf_map_delete_elem(&sizes, &pid);

    if (address != 0) {
        info.timestamp_ns = bpf_ktime_get_ns();

        info.stack_id = bpf_get_stackid(ctx, &stack_traces, stack_flags);

        bpf_map_update_elem(&allocs, &address, &info, BPF_ANY);

        update_statistics_add(info.stack_id, info.size);
    }

    if (trace_all) {
        bpf_printk("alloc exited, size = %lu, result = %lx\n",
                info.size, address);
    }

    return 0;
}
static int gen_alloc_exit(struct pt_regs *ctx)
{
    return gen_alloc_exit2(ctx, PT_REGS_RC(ctx));
}

SEC("uretprobe")
int BPF_KRETPROBE(malloc_exit)
{
    return gen_alloc_exit(ctx);
}
```

`gen_alloc_exit2` 函數在內存分配操作完成時被調用，這個函數接收兩個參數，一個是上下文 `ctx`，另一個是內存分配函數返回的內存地址 `address`。

首先，它獲取當前線程的 PID，然後使用這個 PID 作為鍵在 `sizes` 這個 map 中查找對應的內存分配大小。如果沒有找到（也就是說，沒有對應的內存分配操作的入口），函數就會直接返回。

接著，函數清除 `info` 結構體的內容，並設置它的 `size` 字段為之前在 map 中找到的內存分配大小。並從 `sizes` 這個 map 中刪除相應的元素，因為此時內存分配操作已經完成，不再需要這個信息。

接下來，如果 `address` 不為 0（也就是說，內存分配操作成功了），函數就會進一步收集一些額外的信息。首先，它獲取當前的時間戳作為內存分配完成的時間，並獲取當前的堆棧跟蹤。這些信息都會被儲存在 `info` 結構體中，並隨後更新到 `allocs` 這個 map 中。

最後，函數調用 `update_statistics_add` 更新統計數據，如果啟用了所有內存分配操作的跟蹤，函數還會打印一些關於內存分配操作的信息。

請注意，`gen_alloc_exit` 函數是 `gen_alloc_exit2` 的一個包裝，它將 `PT_REGS_RC(ctx)` 作為 `address` 參數傳遞給 `gen_alloc_exit2`。
在我們的討論中，我們剛剛提到在 `gen_alloc_exit2` 函數中，調用了 `update_statistics_add` 函數以更新內存分配的統計數據。下面我們詳細看一下這個函數的具體實現。

```c
static void update_statistics_add(u64 stack_id, u64 sz)
{
    union combined_alloc_info *existing_cinfo;

    existing_cinfo = bpf_map_lookup_or_try_init(&combined_allocs, &stack_id, &initial_cinfo);
    if (!existing_cinfo)
        return;

    const union combined_alloc_info incremental_cinfo = {
        .total_size = sz,
        .number_of_allocs = 1
    };

    __sync_fetch_and_add(&existing_cinfo->bits, incremental_cinfo.bits);
}
```

`update_statistics_add` 函數接收兩個參數：當前的堆棧 ID `stack_id` 以及內存分配的大小 `sz`。這兩個參數都在內存分配事件中收集到，並且用於更新內存分配的統計數據。

首先，函數嘗試在 `combined_allocs` 這個 map 中查找鍵值為當前堆棧 ID 的元素，如果找不到，就用 `initial_cinfo`（這是一個默認的 combined_alloc_info 結構體，所有字段都為零）來初始化新的元素。

接著，函數創建一個 `incremental_cinfo`，並設置它的 `total_size` 為當前內存分配的大小，設置 `number_of_allocs` 為 1。這是因為每次調用 `update_statistics_add` 函數都表示有一個新的內存分配事件發生，而這個事件的內存分配大小就是 `sz`。

最後，函數使用 `__sync_fetch_and_add` 函數原子地將 `incremental_cinfo` 的值加到 `existing_cinfo` 中。請注意這個步驟是線程安全的，即使有多個線程併發地調用 `update_statistics_add` 函數，每個內存分配事件也能正確地記錄到統計數據中。

總的來說，`update_statistics_add` 函數實現了內存分配統計的更新邏輯，通過維護每個堆棧 ID 的內存分配總量和次數，我們可以深入瞭解到程序的內存分配行為。
在我們對內存分配的統計跟蹤過程中，我們不僅要統計內存的分配，還要考慮內存的釋放。在上述代碼中，我們定義了一個名為 `update_statistics_del` 的函數，其作用是在內存釋放時更新統計信息。而 `gen_free_enter` 函數則是在進程調用 `free` 函數時被執行。

```c
static void update_statistics_del(u64 stack_id, u64 sz)
{
    union combined_alloc_info *existing_cinfo;

    existing_cinfo = bpf_map_lookup_elem(&combined_allocs, &stack_id);
    if (!existing_cinfo) {
        bpf_printk("failed to lookup combined allocs\n");
        return;
    }

    const union combined_alloc_info decremental_cinfo = {
        .total_size = sz,
        .number_of_allocs = 1
    };

    __sync_fetch_and_sub(&existing_cinfo->bits, decremental_cinfo.bits);
}
```

`update_statistics_del` 函數的參數為堆棧 ID 和要釋放的內存塊大小。函數首先在 `combined_allocs` 這個 map 中使用當前的堆棧 ID 作為鍵來查找相應的 `combined_alloc_info` 結構體。如果找不到，就輸出錯誤信息，然後函數返回。如果找到了，就會構造一個名為 `decremental_cinfo` 的 `combined_alloc_info` 結構體，設置它的 `total_size` 為要釋放的內存大小，設置 `number_of_allocs` 為 1。然後使用 `__sync_fetch_and_sub` 函數原子地從 `existing_cinfo` 中減去 `decremental_cinfo` 的值。請注意，這裡的 `number_of_allocs` 是負數，表示減少了一個內存分配。

```c
static int gen_free_enter(const void *address)
{
    const u64 addr = (u64)address;

    const struct alloc_info *info = bpf_map_lookup_elem(&allocs, &addr);
    if (!info)
        return 0;

    bpf_map_delete_elem(&allocs, &addr);
    update_statistics_del(info->stack_id, info->size);

    if (trace_all) {
        bpf_printk("free entered, address = %lx, size = %lu\n",
                address, info->size);
    }

    return 0;
}

SEC("uprobe")
int BPF_KPROBE(free_enter, void *address)
{
    return gen_free_enter(address);
}
```

接下來看 `gen_free_enter` 函數。它接收一個地址作為參數，這個地址是內存分配的結果，也就是將要釋放的內存的起始地址。函數首先在 `allocs` 這個 map 中使用這個地址作為鍵來查找對應的 `alloc_info` 結構體。如果找不到，那麼就直接返回，因為這意味著這個地址並沒有被分配過。如果找到了，那麼就刪除這個元素，並且調用 `update_statistics_del` 函數來更新統計數據。最後，如果啟用了全局追蹤，那麼還會輸出一條信息，包括這個地址以及它的大小。
在我們追蹤和統計內存分配的同時，我們也需要對內核態的內存分配和釋放進行追蹤。在Linux內核中，kmem_cache_alloc函數和kfree函數分別用於內核態的內存分配和釋放。

```c
SEC("tracepoint/kmem/kfree")
int memleak__kfree(void *ctx)
{
    const void *ptr;

    if (has_kfree()) {
        struct trace_event_raw_kfree___x *args = ctx;
        ptr = BPF_CORE_READ(args, ptr);
    } else {
        struct trace_event_raw_kmem_free___x *args = ctx;
        ptr = BPF_CORE_READ(args, ptr);
    }

    return gen_free_enter(ptr);
}
```

上述代碼片段定義了一個函數memleak__kfree，這是一個bpf程序，會在內核調用kfree函數時執行。首先，該函數檢查是否存在kfree函數。如果存在，則會讀取傳遞給kfree函數的參數（即要釋放的內存塊的地址），並保存到變量ptr中；否則，會讀取傳遞給kmem_free函數的參數（即要釋放的內存塊的地址），並保存到變量ptr中。接著，該函數會調用之前定義的gen_free_enter函數來處理該內存塊的釋放。

```c
SEC("tracepoint/kmem/kmem_cache_alloc")
int memleak__kmem_cache_alloc(struct trace_event_raw_kmem_alloc *ctx)
{
    if (wa_missing_free)
        gen_free_enter(ctx->ptr);

    gen_alloc_enter(ctx->bytes_alloc);

    return gen_alloc_exit2(ctx, (u64)(ctx->ptr));
}
```

這段代碼定義了一個函數 memleak__kmem_cache_alloc，這也是一個bpf程序，會在內核調用 kmem_cache_alloc 函數時執行。如果標記 wa_missing_free 被設置，則調用 gen_free_enter 函數處理可能遺漏的釋放操作。然後，該函數會調用 gen_alloc_enter 函數來處理內存分配，最後調用gen_alloc_exit2函數記錄分配的結果。

這兩個 bpf 程序都使用了 SEC 宏定義了對應的 tracepoint，以便在相應的內核函數被調用時得到執行。在Linux內核中，tracepoint 是一種可以在內核中插入的靜態鉤子，可以用來收集運行時的內核信息，它在調試和性能分析中非常有用。

在理解這些代碼的過程中，要注意 BPF_CORE_READ 宏的使用。這個宏用於在 bpf 程序中讀取內核數據。在 bpf 程序中，我們不能直接訪問內核內存，而需要使用這樣的宏來安全地讀取數據。

### 用戶態程序

在理解 BPF 內核部分之後，我們轉到用戶空間程序。用戶空間程序與BPF內核程序緊密配合，它負責將BPF程序加載到內核，設置和管理BPF map，以及處理從BPF程序收集到的數據。用戶態程序較長，我們這裡可以簡要參考一下它的掛載點。

```c
int attach_uprobes(struct memleak_bpf *skel)
{
    ATTACH_UPROBE_CHECKED(skel, malloc, malloc_enter);
    ATTACH_URETPROBE_CHECKED(skel, malloc, malloc_exit);

    ATTACH_UPROBE_CHECKED(skel, calloc, calloc_enter);
    ATTACH_URETPROBE_CHECKED(skel, calloc, calloc_exit);

    ATTACH_UPROBE_CHECKED(skel, realloc, realloc_enter);
    ATTACH_URETPROBE_CHECKED(skel, realloc, realloc_exit);

    ATTACH_UPROBE_CHECKED(skel, mmap, mmap_enter);
    ATTACH_URETPROBE_CHECKED(skel, mmap, mmap_exit);

    ATTACH_UPROBE_CHECKED(skel, posix_memalign, posix_memalign_enter);
    ATTACH_URETPROBE_CHECKED(skel, posix_memalign, posix_memalign_exit);

    ATTACH_UPROBE_CHECKED(skel, memalign, memalign_enter);
    ATTACH_URETPROBE_CHECKED(skel, memalign, memalign_exit);

    ATTACH_UPROBE_CHECKED(skel, free, free_enter);
    ATTACH_UPROBE_CHECKED(skel, munmap, munmap_enter);

    // the following probes are intentinally allowed to fail attachment

    // deprecated in libc.so bionic
    ATTACH_UPROBE(skel, valloc, valloc_enter);
    ATTACH_URETPROBE(skel, valloc, valloc_exit);

    // deprecated in libc.so bionic
    ATTACH_UPROBE(skel, pvalloc, pvalloc_enter);
    ATTACH_URETPROBE(skel, pvalloc, pvalloc_exit);

    // added in C11
    ATTACH_UPROBE(skel, aligned_alloc, aligned_alloc_enter);
    ATTACH_URETPROBE(skel, aligned_alloc, aligned_alloc_exit);

    return 0;
}
```

在這段代碼中，我們看到一個名為`attach_uprobes`的函數，該函數負責將uprobes（用戶空間探測點）掛載到內存分配和釋放函數上。在Linux中，uprobes是一種內核機制，可以在用戶空間程序中的任意位置設置斷點，這使得我們可以非常精確地觀察和控制用戶空間程序的行為。

這裡，每個內存相關的函數都通過兩個uprobes進行跟蹤：一個在函數入口（enter），一個在函數退出（exit）。因此，每當這些函數被調用或返回時，都會觸發一個uprobes事件，進而觸發相應的BPF程序。

在具體的實現中，我們使用了`ATTACH_UPROBE`和`ATTACH_URETPROBE`兩個宏來附加uprobes和uretprobes（函數返回探測點）。每個宏都需要三個參數：BPF程序的骨架（skel），要監視的函數名，以及要觸發的BPF程序的名稱。

這些掛載點包括常見的內存分配函數，如malloc、calloc、realloc、mmap、posix_memalign、memalign、free等，以及對應的退出點。另外，我們也觀察一些可能的分配函數，如valloc、pvalloc、aligned_alloc等，儘管它們可能不總是存在。

這些掛載點的目標是捕獲所有可能的內存分配和釋放事件，從而使我們的內存洩露檢測工具能夠獲取到儘可能全面的數據。這種方法可以讓我們不僅能跟蹤到內存分配和釋放，還能得到它們發生的上下文信息，例如調用棧和調用次數，從而幫助我們定位和修復內存洩露問題。

注意，一些內存分配函數可能並不存在或已棄用，比如valloc、pvalloc等，因此它們的附加可能會失敗。在這種情況下，我們允許附加失敗，並不會阻止程序的執行。這是因為我們更關注的是主流和常用的內存分配函數，而這些已經被棄用的函數往往在實際應用中較少使用。

完整的源代碼：<https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/16-memleak> 關於如何安裝依賴，請參考：<https://eunomia.dev/tutorials/11-bootstrap/>

## 編譯運行

```console
$ make
$ sudo ./memleak 
using default object: libc.so.6
using page size: 4096
tracing kernel: true
Tracing outstanding memory allocs...  Hit Ctrl-C to end
[17:17:27] Top 10 stacks with outstanding allocations:
1236992 bytes in 302 allocations from stack
        0 [<ffffffff812c8f43>] <null sym>
        1 [<ffffffff812c8f43>] <null sym>
        2 [<ffffffff812a9d42>] <null sym>
        3 [<ffffffff812aa392>] <null sym>
        4 [<ffffffff810df0cb>] <null sym>
        5 [<ffffffff81edc3fd>] <null sym>
        6 [<ffffffff82000b62>] <null sym>
...
```

## 總結

通過本篇 eBPF 入門實踐教程，您已經學習瞭如何編寫 Memleak eBPF 監控程序，以實時監控程序的內存洩漏。您已經瞭解了 eBPF 在內存監控方面的應用，學會了使用 BPF API 編寫 eBPF 程序，創建和使用 eBPF maps，並且明白瞭如何用 eBPF 工具監測和分析內存洩漏問題。我們展示了一個詳細的例子，幫助您理解 eBPF 代碼的運行流程和原理。

您可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。

接下來的教程將進一步探討 eBPF 的高級特性，我們會繼續分享更多有關 eBPF 開發實踐的內容。希望這些知識和技巧能幫助您更好地瞭解和使用 eBPF，以解決實際工作中遇到的問題。

參考資料：<https://github.com/iovisor/bcc/blob/master/libbpf-tools/memleak.c>
