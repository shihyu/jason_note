# eBPF 入門實踐教程十七：編寫 eBPF 程序統計隨機/順序磁盤 I/O

eBPF（擴展的伯克利數據包過濾器）是 Linux 內核中的一種新技術，允許用戶在內核空間中執行自定義程序，而無需更改內核代碼。這為系統管理員和開發者提供了強大的工具，可以深入瞭解和監控系統的行為，從而進行優化。

在本篇教程中，我們將探索如何使用 eBPF 編寫程序來統計隨機和順序的磁盤 I/O。磁盤 I/O 是計算機性能的關鍵指標之一，特別是在數據密集型應用中。

## 隨機/順序磁盤 I/O

隨著技術的進步和數據量的爆炸性增長，磁盤 I/O 成為了系統性能的關鍵瓶頸。應用程序的性能很大程度上取決於其如何與存儲層進行交互。因此，深入瞭解和優化磁盤 I/O，特別是隨機和順序的 I/O，變得尤為重要。

1. **隨機 I/O**：隨機 I/O 發生在應用程序從磁盤的非連續位置讀取或寫入數據時。這種 I/O 模式的主要特點是磁盤頭需要頻繁地在不同的位置之間移動，導致其通常比順序 I/O 的速度慢。典型的產生隨機 I/O 的場景包括數據庫查詢、文件系統的元數據操作以及虛擬化環境中的併發任務。

2. **順序 I/O**：與隨機 I/O 相反，順序 I/O 是當應用程序連續地讀取或寫入磁盤上的數據塊。這種 I/O 模式的優勢在於磁盤頭可以在一個方向上連續移動，從而大大提高了數據的讀寫速度。視頻播放、大型文件的下載或上傳以及連續的日誌記錄都是產生順序 I/O 的典型應用。

為了實現存儲性能的最優化，瞭解隨機和順序的磁盤 I/O 是至關重要的。例如，隨機 I/O 敏感的應用程序在 SSD 上的性能通常遠超於傳統硬盤，因為 SSD 在處理隨機 I/O 時幾乎沒有尋址延遲。相反，對於大量順序 I/O 的應用，如何最大化磁盤的連續讀寫速度則更為關鍵。

在本教程的後續部分，我們將詳細探討如何使用 eBPF 工具來實時監控和統計這兩種類型的磁盤 I/O。這不僅可以幫助我們更好地理解系統的 I/O 行為，還可以為進一步的性能優化提供有力的數據支持。

## Biopattern

Biopattern 可以統計隨機/順序磁盤I/O次數的比例。

首先，確保你已經正確安裝了 libbpf 和相關的工具集，可以在這裡找到對應的源代碼：[bpf-developer-tutorial](https://github.com/eunomia-bpf/bpf-developer-tutorial) 關於如何安裝依賴，請參考：<https://eunomia.dev/tutorials/11-bootstrap/>

導航到 `biopattern` 的源代碼目錄，並使用 `make` 命令進行編譯：

```bash
cd ~/bpf-developer-tutorial/src/17-biopattern
make
```

編譯成功後，你應該可以在當前目錄下看到 `biopattern` 的可執行文件。基本的運行命令如下：

```bash
sudo ./biopattern [interval] [count]
```

例如，要每秒打印一次輸出，並持續10秒，你可以運行：

```console
$ sudo ./biopattern 1 10
Tracing block device I/O requested seeks... Hit Ctrl-C to end.
DISK     %RND  %SEQ    COUNT     KBYTES
sr0         0   100        3          0
sr1         0   100        8          0
sda         0   100        1          4
sda       100     0       26        136
sda         0   100        1          4
```

輸出列的含義如下：

- `DISK`：被追蹤的磁盤名稱。
- `%RND`：隨機 I/O 的百分比。
- `%SEQ`：順序 I/O 的百分比。
- `COUNT`：在指定的時間間隔內的 I/O 請求次數。
- `KBYTES`：在指定的時間間隔內讀寫的數據量（以 KB 為單位）。

從上述輸出中，我們可以得出以下結論：

- `sr0` 和 `sr1` 設備在觀測期間主要進行了順序 I/O，但數據量很小。
- `sda` 設備在某些時間段內只進行了隨機 I/O，而在其他時間段內只進行了順序 I/O。

這些信息可以幫助我們瞭解系統的 I/O 模式，從而進行針對性的優化。

## eBPF Biopattern 實現原理

首先，讓我們看一下 biopattern 的核心 eBPF 內核態代碼：

```c
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include "biopattern.h"
#include "maps.bpf.h"
#include "core_fixes.bpf.h"

const volatile bool filter_dev = false;
const volatile __u32 targ_dev = 0;

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 64);
    __type(key, u32);
    __type(value, struct counter);
} counters SEC(".maps");

SEC("tracepoint/block/block_rq_complete")
int handle__block_rq_complete(void *args)
{
    struct counter *counterp, zero = {};
    sector_t sector;
    u32 nr_sector;
    u32 dev;

    if (has_block_rq_completion()) {
        struct trace_event_raw_block_rq_completion___x *ctx = args;
        sector = BPF_CORE_READ(ctx, sector);
        nr_sector = BPF_CORE_READ(ctx, nr_sector);
        dev = BPF_CORE_READ(ctx, dev);
    } else {
        struct trace_event_raw_block_rq_complete___x *ctx = args;
        sector = BPF_CORE_READ(ctx, sector);
        nr_sector = BPF_CORE_READ(ctx, nr_sector);
        dev = BPF_CORE_READ(ctx, dev);
    }

    if (filter_dev && targ_dev != dev)
        return 0;

    counterp = bpf_map_lookup_or_try_init(&counters, &dev, &zero);
    if (!counterp)
        return 0;
    if (counterp->last_sector) {
        if (counterp->last_sector == sector)
            __sync_fetch_and_add(&counterp->sequential, 1);
        else
            __sync_fetch_and_add(&counterp->random, 1);
        __sync_fetch_and_add(&counterp->bytes, nr_sector * 512);
    }
    counterp->last_sector = sector + nr_sector;
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
```

1. 全局變量定義

```c
    const volatile bool filter_dev = false;
    const volatile __u32 targ_dev = 0;
```

這兩個全局變量用於設備過濾。`filter_dev` 決定是否啟用設備過濾，而 `targ_dev` 是我們想要追蹤的目標設備的標識符。

BPF map 定義：

```c
    struct {
        __uint(type, BPF_MAP_TYPE_HASH);
        __uint(max_entries, 64);
        __type(key, u32);
        __type(value, struct counter);
    } counters SEC(".maps");
```

這部分代碼定義了一個 BPF map，類型為哈希表。該映射的鍵是設備的標識符，而值是一個 `counter` 結構體，用於存儲設備的 I/O 統計信息。

追蹤點函數：

```c
    SEC("tracepoint/block/block_rq_complete")
    int handle__block_rq_complete(void *args)
    {
        struct counter *counterp, zero = {};
        sector_t sector;
        u32 nr_sector;
        u32 dev;

        if (has_block_rq_completion()) {
            struct trace_event_raw_block_rq_completion___x *ctx = args;
            sector = BPF_CORE_READ(ctx, sector);
            nr_sector = BPF_CORE_READ(ctx, nr_sector);
            dev = BPF_CORE_READ(ctx, dev);
        } else {
            struct trace_event_raw_block_rq_complete___x *ctx = args;
            sector = BPF_CORE_READ(ctx, sector);
            nr_sector = BPF_CORE_READ(ctx, nr_sector);
            dev = BPF_CORE_READ(ctx, dev);
        }

        if (filter_dev && targ_dev != dev)
            return 0;

        counterp = bpf_map_lookup_or_try_init(&counters, &dev, &zero);
        if (!counterp)
            return 0;
        if (counterp->last_sector) {
            if (counterp->last_sector == sector)
                __sync_fetch_and_add(&counterp->sequential, 1);
            else
                __sync_fetch_and_add(&counterp->random, 1);
            __sync_fetch_and_add(&counterp->bytes, nr_sector * 512);
        }
        counterp->last_sector = sector + nr_sector;
        return 0;
    }
```

在 Linux 中，每次塊設備的 I/O 請求完成時，都會觸發一個名為 `block_rq_complete` 的追蹤點。這為我們提供了一個機會，通過 eBPF 來捕獲這些事件，並進一步分析 I/O 的模式。

主要邏輯分析：

- **提取 I/O 請求信息**：從傳入的參數中獲取 I/O 請求的相關信息。這裡有兩種可能的上下文結構，取決於 `has_block_rq_completion` 的返回值。這是因為不同版本的 Linux 內核可能會有不同的追蹤點定義。無論哪種情況，我們都從上下文中提取出扇區號 (`sector`)、扇區數量 (`nr_sector`) 和設備標識符 (`dev`)。
- **設備過濾**：如果啟用了設備過濾 (`filter_dev` 為 `true`)，並且當前設備不是目標設備 (`targ_dev`)，則直接返回。這允許用戶只追蹤特定的設備，而不是所有設備。
- **統計信息更新**：
      - **查找或初始化統計信息**：使用 `bpf_map_lookup_or_try_init` 函數查找或初始化與當前設備相關的統計信息。如果映射中沒有當前設備的統計信息，它會使用 `zero` 結構體進行初始化。
      - **判斷 I/O 模式**：根據當前 I/O 請求與上一個 I/O 請求的扇區號，我們可以判斷當前請求是隨機的還是順序的。如果兩次請求的扇區號相同，那麼它是順序的；否則，它是隨機的。然後，我們使用 `__sync_fetch_and_add` 函數更新相應的統計信息。這是一個原子操作，確保在併發環境中數據的一致性。
      - **更新數據量**：我們還更新了該設備的總數據量，這是通過將扇區數量 (`nr_sector`) 乘以 512（每個扇區的字節數）來實現的。
      - **更新最後一個 I/O 請求的扇區號**：為了下一次的比較，我們更新了 `last_sector` 的值。

在 Linux 內核的某些版本中，由於引入了一個新的追蹤點 `block_rq_error`，追蹤點的命名和結構發生了變化。這意味著，原先的 `block_rq_complete` 追蹤點的結構名稱從 `trace_event_raw_block_rq_complete` 更改為 `trace_event_raw_block_rq_completion`。這種變化可能會導致 eBPF 程序在不同版本的內核上出現兼容性問題。

為了解決這個問題，`biopattern` 工具引入了一種機制來動態檢測當前內核使用的是哪種追蹤點結構，即 `has_block_rq_completion` 函數。

1. **定義兩種追蹤點結構**：

```c
    struct trace_event_raw_block_rq_complete___x {
        dev_t dev;
        sector_t sector;
        unsigned int nr_sector;
    } __attribute__((preserve_access_index));

    struct trace_event_raw_block_rq_completion___x {
        dev_t dev;
        sector_t sector;
        unsigned int nr_sector;
    } __attribute__((preserve_access_index));
```

這裡定義了兩種追蹤點結構，分別對應於不同版本的內核。每種結構都包含設備標識符 (`dev`)、扇區號 (`sector`) 和扇區數量 (`nr_sector`)。

**動態檢測追蹤點結構**：

```c
    static __always_inline bool has_block_rq_completion()
    {
        if (bpf_core_type_exists(struct trace_event_raw_block_rq_completion___x))
            return true;
        return false;
    }
```

`has_block_rq_completion` 函數使用 `bpf_core_type_exists` 函數來檢測當前內核是否存在 `trace_event_raw_block_rq_completion___x` 結構。如果存在，函數返回 `true`，表示當前內核使用的是新的追蹤點結構；否則，返回 `false`，表示使用的是舊的結構。在對應的 eBPF 代碼中，會根據兩種不同的定義分別進行處理，這也是適配不同內核版本之間的變更常見的方案。

### 用戶態代碼

`biopattern` 工具的用戶態代碼負責從 BPF 映射中讀取統計數據，並將其展示給用戶。通過這種方式，系統管理員可以實時監控每個設備的 I/O 模式，從而更好地理解和優化系統的 I/O 性能。

主循環：

```c
    /* main: poll */
    while (1) {
        sleep(env.interval);

        err = print_map(obj->maps.counters, partitions);
        if (err)
            break;

        if (exiting || --env.times == 0)
            break;
    }
```

這是 `biopattern` 工具的主循環，它的工作流程如下：

- **等待**：使用 `sleep` 函數等待指定的時間間隔 (`env.interval`)。
- **打印映射**：調用 `print_map` 函數打印 BPF 映射中的統計數據。
- **退出條件**：如果收到退出信號 (`exiting` 為 `true`) 或者達到指定的運行次數 (`env.times` 達到 0)，則退出循環。

打印映射函數：

```c
    static int print_map(struct bpf_map *counters, struct partitions *partitions)
    {
        __u32 total, lookup_key = -1, next_key;
        int err, fd = bpf_map__fd(counters);
        const struct partition *partition;
        struct counter counter;
        struct tm *tm;
        char ts[32];
        time_t t;

        while (!bpf_map_get_next_key(fd, &lookup_key, &next_key)) {
            err = bpf_map_lookup_elem(fd, &next_key, &counter);
            if (err < 0) {
                fprintf(stderr, "failed to lookup counters: %d\n", err);
                return -1;
            }
            lookup_key = next_key;
            total = counter.sequential + counter.random;
            if (!total)
                continue;
            if (env.timestamp) {
                time(&t);
                tm = localtime(&t);
                strftime(ts, sizeof(ts), "%H:%M:%S", tm);
                printf("%-9s ", ts);
            }
            partition = partitions__get_by_dev(partitions, next_key);
            printf("%-7s %5ld %5ld %8d %10lld\n",
                partition ? partition->name : "Unknown",
                counter.random * 100L / total,
                counter.sequential * 100L / total, total,
                counter.bytes / 1024);
        }

        lookup_key = -1;
        while (!bpf_map_get_next_key(fd, &lookup_key, &next_key)) {
            err = bpf_map_delete_elem(fd, &next_key);
            if (err < 0) {
                fprintf(stderr, "failed to cleanup counters: %d\n", err);
                return -1;
            }
            lookup_key = next_key;
        }

        return 0;
    }
```

`print_map` 函數負責從 BPF 映射中讀取統計數據，並將其打印到控制檯。其主要邏輯如下：

- **遍歷 BPF 映射**：使用 `bpf_map_get_next_key` 和 `bpf_map_lookup_elem` 函數遍歷 BPF 映射，獲取每個設備的統計數據。
- **計算總數**：計算每個設備的隨機和順序 I/O 的總數。
- **打印統計數據**：如果啟用了時間戳 (`env.timestamp` 為 `true`)，則首先打印當前時間。接著，打印設備名稱、隨機 I/O 的百分比、順序 I/O 的百分比、總 I/O 數量和總數據量（以 KB 為單位）。
- **清理 BPF 映射**：為了下一次的統計，使用 `bpf_map_get_next_key` 和 `bpf_map_delete_elem` 函數清理 BPF 映射中的所有條目。

## 總結

在本教程中，我們深入探討了如何使用 eBPF 工具 biopattern 來實時監控和統計隨機和順序的磁盤 I/O。我們首先了解了隨機和順序磁盤 I/O 的重要性，以及它們對系統性能的影響。接著，我們詳細介紹了 biopattern 的工作原理，包括如何定義和使用 BPF maps，如何處理不同版本的 Linux 內核中的追蹤點變化，以及如何在 eBPF 程序中捕獲和分析磁盤 I/O 事件。

您可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。

- 完整代碼：<https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/17-biopattern>
- bcc 工具：<https://github.com/iovisor/bcc/blob/master/libbpf-tools/biopattern.c>
