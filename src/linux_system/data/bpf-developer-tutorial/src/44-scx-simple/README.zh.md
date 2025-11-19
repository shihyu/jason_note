# eBPF 教程：BPF 調度器入門

歡迎來到我們深入探討 eBPF 世界的教程，本教程將重點介紹 BPF 調度器！如果你希望將 eBPF 知識擴展到基礎之外，你來對地方了。在本教程中，我們將探索 **scx_simple 調度器**，這是 Linux 內核版本 `6.12` 中引入的 sched_ext 調度類的一個最小示例。我們將帶你瞭解其架構，如何利用 BPF 程序定義調度行為，並指導你編譯和運行示例。到最後，你將對如何使用 eBPF 創建和管理高級調度策略有一個堅實的理解。

## 理解可擴展的 BPF 調度器

本教程的核心是 **sched_ext** 調度類。與傳統調度器不同，sched_ext 允許通過一組 BPF 程序動態定義其行為，使其高度靈活和可定製。這意味著你可以在 sched_ext 之上實現任何調度算法，量身定製以滿足你的特定需求。

### sched_ext 的關鍵特性

- **靈活的調度算法：** 通過編寫 BPF 程序實現任何調度策略。
- **動態 CPU 分組：** BPF 調度器可以根據需要分組 CPU，無需在喚醒時將任務綁定到特定 CPU。
- **運行時控制：** 可在不重啟的情況下即時啟用或禁用 BPF 調度器。
- **系統完整性：** 即使 BPF 調度器遇到錯誤，系統也會優雅地回退到默認調度行為。
- **調試支持：** 通過 `sched_ext_dump` 跟蹤點和 SysRq 鍵序列提供全面的調試信息。

憑藉這些特性，sched_ext 為實驗和部署高級調度策略提供了堅實的基礎。

## 介紹 scx_simple：一個最小的 sched_ext 調度器

**scx_simple** 調度器是 Linux 工具中 sched_ext 調度器的一個簡明示例。它設計簡單易懂，併為更復雜的調度策略提供了基礎。scx_simple 可以在兩種模式下運行：

1. **全局加權虛擬時間 (vtime) 模式：** 根據任務的虛擬時間優先級排序，實現不同工作負載之間的公平調度。
2. **FIFO（先進先出）模式：** 基於簡單隊列的調度，任務按照到達順序執行。

### 用例和適用性

scx_simple 在具有單插槽 CPU 和統一 L3 緩存拓撲的系統上尤其有效。雖然全局 FIFO 模式可以高效處理許多工作負載，但需要注意的是，飽和線程可能會壓倒較不活躍的線程。因此，scx_simple 最適合在簡單的調度策略能夠滿足性能和公平性要求的環境中使用。

### 生產就緒性

儘管 scx_simple 功能簡潔，但在合適的條件下可以部署到生產環境中：

- **硬件約束：** 最適用於具有單插槽 CPU 和統一緩存架構的系統。
- **工作負載特性：** 適用於不需要複雜調度策略且可以受益於簡單 FIFO 或加權 vtime 調度的工作負載。

## 代碼深入：內核和用戶空間分析

讓我們深入探討 scx_simple 在內核和用戶空間中的實現。我們將首先展示完整的代碼片段，然後分解其功能。

### 內核端實現

```c
#include <scx/common.bpf.h>

char _license[] SEC("license") = "GPL";

const volatile bool fifo_sched;

static u64 vtime_now;
UEI_DEFINE(uei);

/*
 * 內置 DSQ 如 SCX_DSQ_GLOBAL 不能用作優先級隊列
 * （意味著，不能用 scx_bpf_dispatch_vtime() 分派）。因此，我們
 * 創建一個 ID 為 0 的單獨 DSQ 來分派和消費。如果 scx_simple
 * 只支持全局 FIFO 調度，那麼我們可以直接使用 SCX_DSQ_GLOBAL。
 */
#define SHARED_DSQ 0

struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __uint(key_size, sizeof(u32));
    __uint(value_size, sizeof(u64));
    __uint(max_entries, 2);   /* [local, global] */
} stats SEC(".maps");

static void stat_inc(u32 idx)
{
    u64 *cnt_p = bpf_map_lookup_elem(&stats, &idx);
    if (cnt_p)
        (*cnt_p)++;
}

static inline bool vtime_before(u64 a, u64 b)
{
    return (s64)(a - b) < 0;
}

s32 BPF_STRUCT_OPS(simple_select_cpu, struct task_struct *p, s32 prev_cpu, u64 wake_flags)
{
    bool is_idle = false;
    s32 cpu;

    cpu = scx_bpf_select_cpu_dfl(p, prev_cpu, wake_flags, &is_idle);
    if (is_idle) {
        stat_inc(0); /* 統計本地隊列 */
        scx_bpf_dispatch(p, SCX_DSQ_LOCAL, SCX_SLICE_DFL, 0);
    }

    return cpu;
}

void BPF_STRUCT_OPS(simple_enqueue, struct task_struct *p, u64 enq_flags)
{
    stat_inc(1); /* 統計全局隊列 */

    if (fifo_sched) {
        scx_bpf_dispatch(p, SHARED_DSQ, SCX_SLICE_DFL, enq_flags);
    } else {
        u64 vtime = p->scx.dsq_vtime;

        /*
         * 限制空閒任務可積累的預算量為一個切片。
         */
        if (vtime_before(vtime, vtime_now - SCX_SLICE_DFL))
            vtime = vtime_now - SCX_SLICE_DFL;

        scx_bpf_dispatch_vtime(p, SHARED_DSQ, SCX_SLICE_DFL, vtime,
                       enq_flags);
    }
}

void BPF_STRUCT_OPS(simple_dispatch, s32 cpu, struct task_struct *prev)
{
    scx_bpf_consume(SHARED_DSQ);
}

void BPF_STRUCT_OPS(simple_running, struct task_struct *p)
{
    if (fifo_sched)
        return;

    /*
     * 全局 vtime 隨著任務開始執行而總是向前推進。測試和更新可以
     * 從多個 CPU 併發執行，因此存在競爭。如果有錯誤，應當被
     * 限制並且是臨時的。讓我們接受它。
     */
    if (vtime_before(vtime_now, p->scx.dsq_vtime))
        vtime_now = p->scx.dsq_vtime;
}

void BPF_STRUCT_OPS(simple_stopping, struct task_struct *p, bool runnable)
{
    if (fifo_sched)
        return;

    /*
     * 按照權重和費用的倒數縮放執行時間。
     *
     * 注意，默認的讓出實現通過將 @p->scx.slice 設置為零來讓出，
     * 以下操作將會將讓出的任務視為已消耗所有切片。如果這對
     * 讓出任務的懲罰過大，請通過顯式時間戳來確定執行時間，
     * 而不是依賴於 @p->scx.slice。
     */
    p->scx.dsq_vtime += (SCX_SLICE_DFL - p->scx.slice) * 100 / p->scx.weight;
}

void BPF_STRUCT_OPS(simple_enable, struct task_struct *p)
{
    p->scx.dsq_vtime = vtime_now;
}

s32 BPF_STRUCT_OPS_SLEEPABLE(simple_init)
{
    return scx_bpf_create_dsq(SHARED_DSQ, -1);
}

void BPF_STRUCT_OPS(simple_exit, struct scx_exit_info *ei)
{
    UEI_RECORD(uei, ei);
}

SCX_OPS_DEFINE(simple_ops,
           .select_cpu  = (void *)simple_select_cpu,
           .enqueue   = (void *)simple_enqueue,
           .dispatch  = (void *)simple_dispatch,
           .running   = (void *)simple_running,
           .stopping  = (void *)simple_stopping,
           .enable   = (void *)simple_enable,
           .init   = (void *)simple_init,
           .exit   = (void *)simple_exit,
           .name   = "simple");
```

#### 內核端分解

scx_simple 的內核端實現定義瞭如何選擇、入隊、分派和管理任務。以下是高層次的概述：

1. **初始化和許可：**
   - 調度器的許可證為 GPL。
   - 全局變量 `fifo_sched` 決定調度模式（FIFO 或加權 vtime）。

2. **分派隊列（DSQ）管理：**
   - 創建一個共享的 DSQ（`SHARED_DSQ`，ID 為 0）用於任務分派。
   - 使用 `stats` 映射跟蹤本地和全局隊列中的任務數量。

3. **CPU 選擇 (`simple_select_cpu`)：**
   - 為喚醒任務選擇 CPU。
   - 如果選擇的 CPU 處於空閒狀態，任務將立即分派到本地 DSQ。

4. **任務入隊 (`simple_enqueue`)：**
   - 根據 `fifo_sched` 標誌，將任務分派到共享 DSQ 的 FIFO 模式或基於虛擬時間的優先級隊列。
   - 虛擬時間 (`vtime`) 通過考慮任務執行時間和權重，確保公平調度。

5. **任務分派 (`simple_dispatch`)：**
   - 從共享 DSQ 消費任務並將其分配給 CPU。

6. **運行和停止任務 (`simple_running` & `simple_stopping`)：**
   - 管理任務的虛擬時間進度，確保調度決策的公平和平衡。

7. **啟用和退出：**
   - 處理調度器的啟用，並記錄退出信息以便調試。

這種模塊化結構使得 scx_simple 既簡單又有效，提供了一個清晰的示例，展示如何使用 eBPF 實現自定義調度策略。

### 用戶空間實現

```c
static void read_stats(struct scx_simple *skel, __u64 *stats)
{
    int nr_cpus = libbpf_num_possible_cpus();
    __u64 cnts[2][nr_cpus];
    __u32 idx;

    memset(stats, 0, sizeof(stats[0]) * 2);

    for (idx = 0; idx < 2; idx++) {
        int ret, cpu;

        ret = bpf_map_lookup_elem(bpf_map__fd(skel->maps.stats),
                      &idx, cnts[idx]);
        if (ret < 0)
            continue;
        for (cpu = 0; cpu < nr_cpus; cpu++)
            stats[idx] += cnts[idx][cpu];
    }
}

int main(int argc, char **argv)
{
    struct scx_simple *skel;
    struct bpf_link *link;
    __u32 opt;
    __u64 ecode;

    libbpf_set_print(libbpf_print_fn);
    signal(SIGINT, sigint_handler);
    signal(SIGTERM, sigint_handler);
restart:
    skel = SCX_OPS_OPEN(simple_ops, scx_simple);

    while ((opt = getopt(argc, argv, "fvh")) != -1) {
        switch (opt) {
        case 'f':
            skel->rodata->fifo_sched = true;
            break;
        case 'v':
            verbose = true;
            break;
        default:
            fprintf(stderr, help_fmt, basename(argv[0]));
            return opt != 'h';
        }
    }

    SCX_OPS_LOAD(skel, simple_ops, scx_simple, uei);
    link = SCX_OPS_ATTACH(skel, simple_ops, scx_simple);

    while (!exit_req && !UEI_EXITED(skel, uei)) {
        __u64 stats[2];

        read_stats(skel, stats);
        printf("local=%llu global=%llu\n", stats[0], stats[1]);
        fflush(stdout);
        sleep(1);
    }

    bpf_link__destroy(link);
    ecode = UEI_REPORT(skel, uei);
    scx_simple__destroy(skel);

    if (UEI_ECODE_RESTART(ecode))
        goto restart;
    return 0;
}
```

#### 用戶空間分解

用戶空間組件負責與 BPF 調度器交互，管理其生命週期，並監控其性能。`read_stats` 函數通過讀取 BPF 映射中的本地和全局隊列任務數量來收集統計數據，並跨所有 CPU 聚合這些統計數據以進行報告。

在 `main` 函數中，程序初始化 libbpf，處理信號中斷，並打開 scx_simple BPF 骨架。它處理命令行選項以切換 FIFO 調度和詳細模式，加載 BPF 程序，並將其附加到調度器。監控循環每秒連續讀取並打印調度統計數據，提供調度器行為的實時洞察。終止時，程序通過銷燬 BPF 鏈接並根據退出代碼處理潛在的重啟來清理資源。

這個用戶空間程序提供了一個簡潔的接口，用於監控和控制 scx_simple 調度器，使得更容易實時理解其行為。

## 關鍵概念深入

為了充分理解 scx_simple 的運行機制，讓我們探討一些基礎概念和機制：

### 分派隊列（DSQs）

DSQs 是 sched_ext 運行的核心，充當任務在被分派到 CPU 之前的緩衝區。它們可以根據虛擬時間作為 FIFO 隊列或優先級隊列運行。

- **本地 DSQs (`SCX_DSQ_LOCAL`)：** 每個 CPU 都有自己的本地 DSQ，確保任務可以高效地分派和消費，而不會發生爭用。
- **全局 DSQ (`SCX_DSQ_GLOBAL`)：** 一個共享隊列，來自所有 CPU 的任務可以被排隊，當本地隊列為空時提供回退。
- **自定義 DSQs：** 開發者可以使用 `scx_bpf_create_dsq()` 創建額外的 DSQs，以滿足更專業的調度需求。

### 虛擬時間（vtime）

虛擬時間是一種確保調度公平性的機制，通過跟蹤任務相對於其權重消耗了多少時間來實現。在 scx_simple 的加權 vtime 模式下，權重較高的任務消耗虛擬時間的速度較慢，允許權重較低的任務更頻繁地運行。這種方法基於預定義的權重平衡任務執行，確保沒有單個任務壟斷 CPU 資源。

### 調度週期

理解調度週期對於修改或擴展 scx_simple 至關重要。以下步驟詳細說明了喚醒任務的調度和執行過程：

1. **任務喚醒和 CPU 選擇：**
   - 當一個任務被喚醒時，首先調用 `ops.select_cpu()`。
   - 該函數有兩個目的：
     - **CPU 選擇優化提示：** 提供建議的 CPU 供任務運行。雖然這是一個優化提示而非綁定，但如果 `ops.select_cpu()` 返回的 CPU 與任務最終運行的 CPU 匹配，可以帶來性能提升。
     - **喚醒空閒 CPU：** 如果選擇的 CPU 處於空閒狀態，`ops.select_cpu()` 可以喚醒它，為執行任務做好準備。
   - 注意：如果 CPU 選擇無效（例如，超出任務允許的 CPU 掩碼），調度器核心將忽略該選擇。

2. **從 `ops.select_cpu()` 立即分派：**
   - 任務可以通過調用 `scx_bpf_dispatch()` 直接從 `ops.select_cpu()` 分派到分派隊列（DSQ）。
   - 如果分派到 `SCX_DSQ_LOCAL`，任務將被放入 `ops.select_cpu()` 返回的 CPU 的本地 DSQ。
   - 直接從 `ops.select_cpu()` 分派將導致跳過 `ops.enqueue()` 回調，可能減少調度延遲。

3. **任務入隊 (`ops.enqueue()`)：**
   - 如果任務未在上一步被分派，`ops.enqueue()` 將被調用。
   - `ops.enqueue()` 可以做出以下幾種決定：
     - **立即分派：** 通過調用 `scx_bpf_dispatch()` 將任務分派到全局 DSQ（`SCX_DSQ_GLOBAL`）、本地 DSQ（`SCX_DSQ_LOCAL`）或自定義 DSQ。
     - **在 BPF 端排隊：** 在 BPF 程序中排隊任務，以便進行自定義調度邏輯。

4. **CPU 調度準備：**
   - 當 CPU 準備好調度時，它按照以下順序進行：
     - **檢查本地 DSQ：** CPU 首先檢查其本地 DSQ 是否有任務。
     - **檢查全局 DSQ：** 如果本地 DSQ 為空，則檢查全局 DSQ。
     - **調用 `ops.dispatch()`：** 如果仍然沒有找到任務，調用 `ops.dispatch()` 來填充本地 DSQ。
       - 在 `ops.dispatch()` 內，可以使用以下函數：
         - `scx_bpf_dispatch()`：將任務調度到任何 DSQ（本地、全局或自定義）。注意，該函數目前不能在持有 BPF 鎖時調用。
         - `scx_bpf_consume()`：將任務從指定的非本地 DSQ 轉移到分派 DSQ。該函數不能在持有任何 BPF 鎖時調用，並且會在嘗試消費指定 DSQ 之前刷新待分派的任務。

5. **任務執行決策：**
   - `ops.dispatch()` 返回後，如果本地 DSQ 中有任務，CPU 將運行第一個任務。
   - 如果本地 DSQ 仍為空，CPU 將執行以下步驟：
     - **消費全局 DSQ：** 嘗試使用 `scx_bpf_consume()` 從全局 DSQ 消費任務。如果成功，執行該任務。
     - **重試分派：** 如果 `ops.dispatch()` 已經分派了任何任務，CPU 將重試檢查本地 DSQ。
     - **執行前一個任務：** 如果前一個任務是 SCX 任務且仍然可運行，CPU 將繼續執行它（參見 `SCX_OPS_ENQ_LAST`）。
     - **進入空閒狀態：** 如果沒有可用任務，CPU 將進入空閒狀態。

這種調度週期確保任務高效調度，同時保持公平性和響應性。通過理解每一步，開發者可以修改或擴展 scx_simple，以實現滿足特定需求的自定義調度行為。

## 編譯和運行 scx_simple

要運行 scx_simple，需要設置必要的工具鏈並正確配置內核。以下是編譯和執行示例調度器的方法。

### 工具鏈依賴

在編譯 scx_simple 之前，請確保已安裝以下工具：

1. **clang >= 16.0.0**  
   編譯 BPF 程序所需。雖然 GCC 正在開發 BPF 支持，但它缺乏某些必要功能，如 BTF 類型標籤。

2. **pahole >= 1.25**  
   用於從 DWARF 生成 BTF，對於 BPF 程序中的類型信息至關重要。

3. **rust >= 1.70.0**  
   如果你正在使用基於 Rust 的調度器，請確保擁有適當的 Rust 工具鏈版本。

此外，還需要 `make` 等工具來構建示例。

### 內核配置

要啟用和使用 sched_ext，請確保設置了以下內核配置選項：

```plaintext
CONFIG_BPF=y
CONFIG_SCHED_CLASS_EXT=y
CONFIG_BPF_SYSCALL=y
CONFIG_BPF_JIT=y
CONFIG_DEBUG_INFO_BTF=y
CONFIG_BPF_JIT_ALWAYS_ON=y
CONFIG_BPF_JIT_DEFAULT_ON=y
CONFIG_PAHOLE_HAS_SPLIT_BTF=y
CONFIG_PAHOLE_HAS_BTF_TAG=y
```

這些配置啟用了 BPF 調度所需的功能，並確保 sched_ext 正常運行。

### 構建 scx_simple

導航到內核的 `tools/sched_ext/` 目錄並運行：

```bash
make
```

此命令將編譯 scx_simple 調度器及其依賴項。

### 運行 scx_simple

編譯完成後，可以執行用戶空間程序來加載和監控調度器：

```bash
./scx_simple -f
```

`-f` 標誌啟用 FIFO 調度模式。你還可以使用 `-v` 進行詳細輸出，或使用 `-h` 獲取幫助。當程序運行時，它將每秒顯示本地和全局隊列中的任務數量：

```plaintext
local=123 global=456
local=124 global=457
...
```

### 在 sched_ext 和 CFS 之間切換

sched_ext 與默認的完全公平調度器（CFS）並行運行。你可以通過加載或卸載 scx_simple 程序動態切換 sched_ext 和 CFS。

- **啟用 sched_ext：** 使用 scx_simple 加載 BPF 調度器。
- **禁用 sched_ext：** 終止 scx_simple 程序，將所有任務恢復到 CFS。

此外，使用 SysRq 鍵序列如 `SysRq-S` 可以幫助管理調度器的狀態，並使用 `SysRq-D` 觸發調試轉儲。

## 總結與下一步

在本教程中，我們介紹了 **sched_ext** 調度類，並通過一個最小示例 **scx_simple** 展示瞭如何使用 eBPF 程序定義自定義調度行為。我們涵蓋了架構、關鍵概念如 DSQs 和虛擬時間，並提供了編譯和運行調度器的分步說明。

掌握 scx_simple 後，你將具備設計和實現更復雜調度策略的能力，以滿足特定需求。無論你是優化性能、公平性，還是針對特定工作負載特性，sched_ext 和 eBPF 都提供了實現目標所需的靈活性和強大功能。

> 準備好將你的 eBPF 技能提升到新的水平了嗎？深入探索我們的教程並通過訪問我們的 [教程倉庫 https://github.com/eunomia-bpf/bpf-developer-tutorial](https://github.com/eunomia-bpf/bpf-developer-tutorial) 或 [網站 https://eunomia.dev/tutorials/](https://eunomia.dev/tutorials/) 探索更多示例。

## 參考資料

- **sched_ext 倉庫：** [https://github.com/sched-ext/scx](https://github.com/sched-ext/scx)
- **Linux 內核文檔：** [Scheduler Ext Documentation](https://www.kernel.org/doc/html/next/scheduler/sched-ext.html)
- **內核源代碼樹：** [Linux Kernel sched_ext Tools](https://github.com/torvalds/linux/tree/master/tools/sched_ext)
- **eBPF 官方文檔：** [https://docs.ebpf.io/](https://docs.ebpf.io/)
- **libbpf 文檔：** [https://github.com/libbpf/libbpf](https://github.com/libbpf/libbpf)

