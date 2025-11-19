# eBPF 示例教程：實現 `scx_nest` 調度器

在系統性能優化不斷發展的領域中，自定義和擴展內核行為的能力是非常寶貴的。實現這一目標的最強大工具之一是 eBPF（擴展的 Berkeley 包過濾器）。在本教程中，我們將探討 `scx_nest` 調度器的實現，這是一個先進的 eBPF 程序，利用了在 Linux 內核版本 `6.12` 中引入的 `sched_ext` 調度器類。在本指南結束時，您將瞭解如何構建一個複雜的調度器，該調度器根據 CPU 核心頻率和利用率動態調整任務分配。

## `sched_ext` 介紹

`sched_ext` 調度器類標誌著 Linux 內核調度能力的重大進步。與傳統調度器不同，`sched_ext` 允許通過一組 BPF（Berkeley 包過濾器）程序動態定義其行為。這種靈活性使開發人員能夠實現針對特定工作負載和系統需求量身定製的自定義調度算法。

## 理解 `scx_nest` 調度器

### 概述

`scx_nest` 調度器受 Inria Paris 論文《[OS Scheduling with Nest: Keeping Tasks Close Together on Warm Cores](https://hal.inria.fr/hal-03612592/file/paper.pdf)》的啟發。由 Meta Platforms, Inc. 開發，`scx_nest` 專注於鼓勵將任務分配到基於最近使用模式可能以更高頻率運行的 CPU 核心上。這種方法旨在通過確保任務在最有效的核心上執行來優化性能。

該調度器作為一個全局加權虛擬時間（vtime）調度器運行，類似於完全公平調度器（CFS），同時利用 Nest 算法在任務喚醒時選擇空閒核心。這種雙重策略確保任務不僅被公平分配，還被放置在能夠最有效執行它們的核心上。

`scx_nest` 旨在優化 CPU 利用率相對較低且可以受益於在少數核心上運行的工作負載。通過將任務集中在較少的核心上，調度器有助於保持這些核心的高頻率，從而提升性能。然而，對於那些在分佈到多個核心以避免緩存抖動時表現更好的工作負載，`scx_nest` 可能並不是理想選擇。評估 `scx_nest` 對特定工作負載的適用性通常需要實驗。

鑑於其設計，`scx_nest` 適用於生產環境，前提是滿足硬件限制。它在具有統一 L3 緩存拓撲的單個 CCX（核心複合體）或單插槽主機上表現最佳。雖然當前版本未實現搶佔，但所有 CPU 共享的調度隊列確保隊列前端的任務能夠及時執行，前提是有足夠的 CPU 可用。

## 高級代碼分析

`scx_nest` 調度器的實現複雜，涉及各種數據結構、映射和函數，它們協同工作以管理任務分配和 CPU 核心利用率。完整的源代碼可在 [eunomia-bpf/bpf-developer-tutorial](https://github.com/eunomia-bpf/bpf-developer-tutorial) 倉庫中找到。下面，我們將剖析調度器的核心組件，詳細解釋每個部分。

### 核心數據結構和映射

#### 任務上下文 (`task_ctx`)

系統中的每個任務都有一個關聯的上下文，用於維護與調度相關的信息。這個上下文對於基於任務的歷史和當前狀態做出明智的調度決策至關重要。

```c
/* 每個任務的調度上下文 */
struct task_ctx {
    /*
     * 用於計算任務的主掩碼和保留掩碼的臨時 cpumask。
     */
    struct bpf_cpumask __kptr *tmp_mask;

    /*
     * 任務觀察到其之前的核心不為空閒的次數。如果連續發生 r_impatient 次，
     * 將嘗試從保留 Nest 或回退 Nest 中獲取一個核心。
     */
    u32 prev_misses;

    /*
     * 任務“附加”的核心，意味著它至少連續在該核心上執行了兩次，
     * 並且在喚醒時首先嚐試遷移到該核心。任務只有在附加核心空閒且
     * 在主 Nest 中時才會遷移到附加核心。
     */
    s32 attached_core;

    /*
     * 任務上次執行的核心。這用於確定任務是否應該附加到下一個
     * 執行的核心。
     */
    s32 prev_cpu;
};
```

`task_ctx` 結構體包含一個臨時 CPU 掩碼 (`tmp_mask`)，用於計算任務的主 CPU 集合和保留 CPU 集合。`prev_misses` 計數器跟蹤任務的首選核心不為空閒的次數，影響遷移任務到不同核心的決策。`attached_core` 指示任務當前綁定的核心，確保在可能的情況下在高頻率核心上運行。最後，`prev_cpu` 記錄任務上次執行的核心，有助於維護任務與核心的親和性。

#### 每 CPU 上下文 (`pcpu_ctx`)

每個 CPU 都有一個關聯的上下文，用於管理定時器和壓縮狀態。這個上下文有助於確定何時由於不活動而將核心從主 Nest 中降級。

```c
struct pcpu_ctx {
    /* 用於從主 Nest 中壓縮核心的定時器。 */
    struct bpf_timer timer;

    /* 當前核心是否已安排進行壓縮。 */
    bool scheduled_compaction;
};
```

`pcpu_ctx` 結構體包含一個 `bpf_timer`，用於調度壓縮事件，以及一個布爾標誌 `scheduled_compaction`，指示是否已為核心安排了壓縮。

#### 映射

多個 BPF 映射用於存儲上下文和管理定時器：

```c
/* 任務存儲映射 */
struct {
    __uint(type, BPF_MAP_TYPE_TASK_STORAGE);
    __uint(map_flags, BPF_F_NO_PREALLOC);
    __type(key, int);
    __type(value, struct task_ctx);
} task_ctx_stor SEC(".maps");

/* 每 CPU 上下文 */
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1024);
    __type(key, s32);
    __type(value, struct pcpu_ctx);
} pcpu_ctxs SEC(".maps");

/* 統計定時器 */
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1);
    __type(key, u32);
    __type(value, struct stats_timer);
} stats_timer SEC(".maps");
```

- **`task_ctx_stor`:** 該映射存儲每個任務的調度上下文，使調度器能夠訪問和修改特定任務的信息。
- **`pcpu_ctxs`:** 一個數組映射，保存每個 CPU 的上下文，使調度器能夠管理每個 CPU 的定時器和壓縮狀態。
- **`stats_timer`:** 一個單條目的數組映射，用於管理用於收集調度統計信息的中央定時器。

此外，調度器維護了主 CPU 掩碼、保留 CPU 掩碼、其他 CPU 掩碼和空閒 CPU 掩碼，以及用於跟蹤各種調度器指標的統計映射。

### 核心函數

#### `stat_inc`

一個輔助函數，用於遞增調度統計數據：

```c
static __always_inline void stat_inc(u32 idx)
{
    u64 *cnt_p = bpf_map_lookup_elem(&stats, &idx);
    if (cnt_p)
        (*cnt_p)++;
}
```

此函數在 `stats` 映射中查找一個計數器，並在計數器存在時遞增它。調度器在各處使用它來跟蹤各種事件和狀態。

#### `vtime_before`

一個用於比較虛擬時間的實用函數：

```c
static inline bool vtime_before(u64 a, u64 b)
{
    return (s64)(a - b) < 0;
}
```

此函數確定虛擬時間 `a` 是否在 `b` 之前，有助於基於時間的調度決策。

#### `try_make_core_reserved`

嘗試將一個核心提升為保留 Nest：

```c
static __always_inline void
try_make_core_reserved(s32 cpu, struct bpf_cpumask * reserved, bool promotion)
{
    s32 tmp_nr_reserved;

    /*
     * 此檢查存在競爭，但沒關係。如果我們錯誤地未能將核心提升到保留，
     * 那是因為另一個上下文在這個小窗口中添加或移除了保留中的核心。
     * 這將在隨後的喚醒中平衡。
     */
    tmp_nr_reserved = nr_reserved;
    if (tmp_nr_reserved < r_max) {
        /*
         * 這裡有可能暫時超過 r_max，但隨著更多核心被降級或未能
         * 被提升到保留 Nest，應該會平衡。
         */
        __sync_fetch_and_add(&nr_reserved, 1);
        bpf_cpumask_set_cpu(cpu, reserved);
        if (promotion)
            stat_inc(NEST_STAT(PROMOTED_TO_RESERVED));
        else
            stat_inc(NEST_STAT(DEMOTED_TO_RESERVED));
    } else {
        bpf_cpumask_clear_cpu(cpu, reserved);
        stat_inc(NEST_STAT(RESERVED_AT_CAPACITY));
    }
}
```

`try_make_core_reserved` 函數嘗試將一個 CPU 核心添加到保留掩碼中。首先檢查保留核心的數量 (`nr_reserved`) 是否低於允許的最大值 (`r_max`)。如果是，則遞增 `nr_reserved` 計數器並將核心添加到保留掩碼中。根據核心是被提升還是降級，遞增相應的統計數據。如果保留容量已滿，則從保留掩碼中清除核心並更新相關統計數據。

#### `update_attached`

根據最近的執行更新任務的附加核心：

```c
static void update_attached(struct task_ctx *tctx, s32 prev_cpu, s32 new_cpu)
{
    if (tctx->prev_cpu == new_cpu)
        tctx->attached_core = new_cpu;
    tctx->prev_cpu = prev_cpu;
}
```

此函數更新任務的 `attached_core`。如果任務連續在同一核心上執行，它會將任務附加到該核心。然後更新 `prev_cpu` 以反映任務最近運行的核心。

#### `compact_primary_core`

處理主核心的壓縮，將其降級到保留 Nest：

```c
static int compact_primary_core(void *map, int *key, struct bpf_timer *timer)
{
    struct bpf_cpumask *primary, *reserve;
    s32 cpu = bpf_get_smp_processor_id();
    struct pcpu_ctx *pcpu_ctx;

    stat_inc(NEST_STAT(CALLBACK_COMPACTED));

    /*
     * 如果我們到達此回調，這意味著定時器回調從未被取消，
     * 因此需要將核心從主 Nest 中降級。
     */
    pcpu_ctx = bpf_map_lookup_elem(&pcpu_ctxs, &cpu);
    if (!pcpu_ctx) {
        scx_bpf_error("無法查找 pcpu ctx");
        return 0;
    }
    bpf_rcu_read_lock();
    primary = primary_cpumask;
    reserve = reserve_cpumask;
    if (!primary || !reserve) {
        scx_bpf_error("無法找到 primary 或 reserve");
        bpf_rcu_read_unlock();
        return 0;
    }

    bpf_cpumask_clear_cpu(cpu, primary);
    try_make_core_reserved(cpu, reserve, false);
    bpf_rcu_read_unlock();
    pcpu_ctx->scheduled_compaction = false;
    return 0;
}
```

當壓縮定時器到期時，將調用 `compact_primary_core`。它通過從主掩碼中清除當前 CPU 核心並嘗試將其添加到保留掩碼中，將當前 CPU 核心從主 Nest 降級到保留 Nest。這確保了不活動的核心得到有效管理，保持性能和資源利用之間的平衡。

#### `nest_select_cpu`

在任務喚醒時確定適當的 CPU：

```c
s32 BPF_STRUCT_OPS(nest_select_cpu, struct task_struct *p, s32 prev_cpu, u64 wake_flags)
{
    struct bpf_cpumask *p_mask, *primary, *reserve;
    s32 cpu;
    struct task_ctx *tctx;
    struct pcpu_ctx *pcpu_ctx;
    bool direct_to_primary = false, reset_impatient = true;

    tctx = bpf_task_storage_get(&task_ctx_stor, p, 0, 0);
    if (!tctx)
        return -ENOENT;

    bpf_rcu_read_lock();
    p_mask = tctx->tmp_mask;
    primary = primary_cpumask;
    reserve = reserve_cpumask;
    if (!p_mask || !primary || !reserve) {
        bpf_rcu_read_unlock();
        return -ENOENT;
    }

    tctx->prev_cpu = prev_cpu;

    bpf_cpumask_and(p_mask, p->cpus_ptr, cast_mask(primary));

    /* 首先嚐試在附加核心上喚醒任務。 */
    if (bpf_cpumask_test_cpu(tctx->attached_core, cast_mask(p_mask)) &&
        scx_bpf_test_and_clear_cpu_idle(tctx->attached_core)) {
        cpu = tctx->attached_core;
        stat_inc(NEST_STAT(WAKEUP_ATTACHED));
        goto migrate_primary;
    }

    /*
     * 如果之前的核心在主集合中，並且沒有 hypertwin，則嘗試留在之前的核心。
     * 如果之前的核心是任務附加的核心，不需要再嘗試，因為我們已經在上面嘗試過了。
     */
    if (prev_cpu != tctx->attached_core &&
        bpf_cpumask_test_cpu(prev_cpu, cast_mask(p_mask)) &&
        scx_bpf_test_and_clear_cpu_idle(prev_cpu)) {
        cpu = prev_cpu;
        stat_inc(NEST_STAT(WAKEUP_PREV_PRIMARY));
        goto migrate_primary;
    }

    if (find_fully_idle) {
        /* 然後嘗試在主集合中選擇任何完全空閒的核心。 */
        cpu = scx_bpf_pick_idle_cpu(cast_mask(p_mask),
                                    SCX_PICK_IDLE_CORE);
        if (cpu >= 0) {
            stat_inc(NEST_STAT(WAKEUP_FULLY_IDLE_PRIMARY));
            goto migrate_primary;
        }
    }

    /* 然後嘗試在主集合中選擇任何空閒的核心，即使其 hypertwin 正在活動。 */
    cpu = scx_bpf_pick_idle_cpu(cast_mask(p_mask), 0);
    if (cpu >= 0) {
        stat_inc(NEST_STAT(WAKEUP_ANY_IDLE_PRIMARY));
        goto migrate_primary;
    }

    if (r_impatient > 0 && ++tctx->prev_misses >= r_impatient) {
        direct_to_primary = true;
        tctx->prev_misses = 0;
        stat_inc(NEST_STAT(TASK_IMPATIENT));
    }

    reset_impatient = false;

    /* 然後嘗試在保留集合中選擇任何完全空閒的核心。 */
    bpf_cpumask_and(p_mask, p->cpus_ptr, cast_mask(reserve));
    if (find_fully_idle) {
        cpu = scx_bpf_pick_idle_cpu(cast_mask(p_mask),
                                    SCX_PICK_IDLE_CORE);
        if (cpu >= 0) {
            stat_inc(NEST_STAT(WAKEUP_FULLY_IDLE_RESERVE));
            goto promote_to_primary;
        }
    }

    /* 然後嘗試在保留集合中選擇任何空閒的核心，即使其 hypertwin 正在活動。 */
    cpu = scx_bpf_pick_idle_cpu(cast_mask(p_mask), 0);
    if (cpu >= 0) {
        stat_inc(NEST_STAT(WAKEUP_ANY_IDLE_RESERVE));
        goto promote_to_primary;
    }

    /* 然後嘗試在任務的 cpumask 中選擇任何空閒的核心。 */
    cpu = scx_bpf_pick_idle_cpu(p->cpus_ptr, 0);
    if (cpu >= 0) {
        /*
         * 我們找到了一個核心（我們認為它不在任何 Nest 中）。
         * 這意味著我們需要將該核心提升到保留 Nest，或者如果由於
         * 超過 r_impatient 而直接提升到主 Nest。
         *
         * 我們必須在這裡進行最後一次檢查，看看核心是否在主掩碼或保留掩碼中，
         * 因為我們可能與核心在將主掩碼和保留掩碼與 p->cpus_ptr 進行 AND
         * 運算之間更改狀態，並使用 scx_bpf_pick_idle_cpu() 原子性地保留它。
         * 這在上面的檢查中技術上也是如此，但在那些情況下我們只是直接
         * 將核心放入主掩碼中，因此問題不大。在這裡，我們要確保不會
         * 意外地將已經在主掩碼中的核心放入保留 Nest 中。這是不太可能的，
         * 但我們在應該相對冷路徑上進行了檢查。
         */
        stat_inc(NEST_STAT(WAKEUP_IDLE_OTHER));
        if (bpf_cpumask_test_cpu(cpu, cast_mask(primary)))
            goto migrate_primary;
        else if (bpf_cpumask_test_cpu(cpu, cast_mask(reserve)))
            goto promote_to_primary;
        else if (direct_to_primary)
            goto promote_to_primary;
        else
            try_make_core_reserved(cpu, reserve, true);
        bpf_rcu_read_unlock();
        return cpu;
    }

    bpf_rcu_read_unlock();
    return prev_cpu;

promote_to_primary:
    stat_inc(NEST_STAT(PROMOTED_TO_PRIMARY));
migrate_primary:
    if (reset_impatient)
        tctx->prev_misses = 0;
    pcpu_ctx = bpf_map_lookup_elem(&pcpu_ctxs, &cpu);
    if (pcpu_ctx) {
        if (pcpu_ctx->scheduled_compaction) {
            if (bpf_timer_cancel(&pcpu_ctx->timer) < 0)
                scx_bpf_error("取消 pcpu 定時器失敗");
            if (bpf_timer_set_callback(&pcpu_ctx->timer, compact_primary_core))
                scx_bpf_error("重新設置 pcpu 定時器回調失敗");
            pcpu_ctx->scheduled_compaction = false;
            stat_inc(NEST_STAT(CANCELLED_COMPACTION));
        }
    } else {
        scx_bpf_error("查找 pcpu ctx 失敗");
    }
    bpf_cpumask_set_cpu(cpu, primary);
    /*
     * 檢查 CPU 是否在保留掩碼中。如果是，這可能發生在核心在我們嘗試
     * 將當前喚醒任務分配到其上時被併發地壓縮。同樣，如果我們在
     * 由於超時直接提升到主 Nest，也會發生這種情況。
     *
     * 我們不必擔心與其他喚醒任務的競爭，因為我們已經通過（某種
     * 變體的）scx_bpf_pick_idle_cpu() 原子性地保留了該核心。
     */
    if (bpf_cpumask_test_cpu(cpu, cast_mask(reserve))) {
        __sync_sub_and_fetch(&nr_reserved, 1);
        bpf_cpumask_clear_cpu(cpu, reserve);
    }
    bpf_rcu_read_unlock();
    update_attached(tctx, prev_cpu, cpu);
    scx_bpf_dispatch(p, SCX_DSQ_LOCAL, slice_ns, 0);
    return cpu;
}
```

`nest_select_cpu` 函數是 `scx_nest` 調度器的核心。當任務喚醒時，此函數確定其執行最合適的 CPU 核心。該函數遵循一系列檢查，以確保任務被放置在高頻率、空閒的核心上，從而提升效率和性能。

最初，它從 `task_ctx_stor` 映射中檢索任務的上下文。然後，它鎖定讀拷貝更新（RCU）鎖，以安全地訪問主掩碼和保留掩碼。調度器首先嚐試將任務放置在其附加核心上，確保核心親和性。如果附加核心不空閒，它會嘗試先前的核心。根據各種條件，包括任務的急躁程度 (`r_impatient`) 和主 Nest 及保留 Nest 中空閒核心的可用性，調度器決定是否遷移任務、將核心提升到主 Nest，或將核心降級到保留 Nest。

在整個過程中，調度器更新相關統計數據，以提供對其操作的見解。使用 RCU 鎖確保調度器的決策是在不干擾其他併發操作的情況下安全做出的。

#### `nest_enqueue`

處理將任務入隊到調度隊列：

```c
void BPF_STRUCT_OPS(nest_enqueue, struct task_struct *p, u64 enq_flags)
{
    struct task_ctx *tctx;
    u64 vtime = p->scx.dsq_vtime;

    tctx = bpf_task_storage_get(&task_ctx_stor, p, 0, 0);
    if (!tctx) {
        scx_bpf_error("無法找到任務上下文");
        return;
    }

    /*
     * 將空閒任務的預算限制為一個切片。
     */
    if (vtime_before(vtime, vtime_now - slice_ns))
        vtime = vtime_now - slice_ns;

    scx_bpf_dispatch_vtime(p, FALLBACK_DSQ_ID, slice_ns, vtime, enq_flags);
}
```

`nest_enqueue` 函數管理任務的入隊，調整其虛擬時間 (`vtime`) 以確保公平性並防止任務在空閒時積累過多的執行預算。如果任務的 `vtime` 低於某個閾值，它將被調整以保持調度器內部的平衡。

#### `nest_dispatch`

管理將任務分派到 CPU 核心：

```c
void BPF_STRUCT_OPS(nest_dispatch, s32 cpu, struct task_struct *prev)
{
    struct pcpu_ctx *pcpu_ctx;
    struct bpf_cpumask *primary, *reserve;
    s32 key = cpu;
    bool in_primary;

    primary = primary_cpumask;
    reserve = reserve_cpumask;
    if (!primary || !reserve) {
        scx_bpf_error("沒有主或保留 cpumask");
        return;
    }

    pcpu_ctx = bpf_map_lookup_elem(&pcpu_ctxs, &key);
    if (!pcpu_ctx) {
        scx_bpf_error("查找 pcpu ctx 失敗");
        return;
    }

    if (!scx_bpf_consume(FALLBACK_DSQ_ID)) {
        in_primary = bpf_cpumask_test_cpu(cpu, cast_mask(primary));

        if (prev && (prev->scx.flags & SCX_TASK_QUEUED) && in_primary) {
            scx_bpf_dispatch(prev, SCX_DSQ_LOCAL, slice_ns, 0);
            return;
        }

        stat_inc(NEST_STAT(NOT_CONSUMED));
        if (in_primary) {
            /*
             * 如果主集合中的前一個任務正在死亡，立即降級主核心。
             *
             * 注意，我們選擇不壓縮掩碼中的“第一個” CPU，以鼓勵至少保留一個核心在 Nest 中。
             * 最好檢查是否僅剩一個核心在 Nest 中，但 BPF 目前沒有用於查詢
             * cpumask 權重的內核函數。
             */
            if ((prev && prev->__state == TASK_DEAD) &&
                (cpu != bpf_cpumask_first(cast_mask(primary)))) {
                stat_inc(NEST_STAT(EAGERLY_COMPACTED));
                bpf_cpumask_clear_cpu(cpu, primary);
                try_make_core_reserved(cpu, reserve, false);
            } else  {
                pcpu_ctx->scheduled_compaction = true;
                /*
                 * 核心不再被使用。設置定時器以在 p_remove 中移除核心
                 * 如果在那時仍未使用。
                 */
                bpf_timer_start(&pcpu_ctx->timer, p_remove_ns,
                               BPF_F_TIMER_CPU_PIN);
                stat_inc(NEST_STAT(SCHEDULED_COMPACTION));
            }
        }
        return;
    }
    stat_inc(NEST_STAT(CONSUMED));
}
```

`nest_dispatch` 函數負責將任務分派到 CPU 核心。它首先檢查回退調度隊列 (`FALLBACK_DSQ_ID`) 中是否有可用任務。如果沒有任務被消耗，它會評估 CPU 上的前一個任務是否已經死亡。如果是，並且 CPU 不在主掩碼中的第一個位置，調度器將核心降級到保留 Nest。否則，它會為核心安排一個壓縮定時器，以便在指定時間後可能降級該核心。如果從回退隊列成功消耗了一個任務，它會遞增相應的統計數據。

#### `nest_running`

當任務開始運行時更新全局虛擬時間：

```c
void BPF_STRUCT_OPS(nest_running, struct task_struct *p)
{
    /*
     * 全局虛擬時間在任務開始執行時總是向前推進。
     * 測試和更新可以從多個 CPU 同時執行，因此存在競爭。
     * 任何錯誤都應該是可控且暫時的。我們就這樣處理。
     */
    if (vtime_before(vtime_now, p->scx.dsq_vtime))
        vtime_now = p->scx.dsq_vtime;
}
```

`nest_running` 函數確保全局虛擬時間 (`vtime_now`) 在任務開始執行時向前推進。這一機制有助於維護調度器操作的公平性和時間一致性。

#### `nest_stopping`

處理任務停止運行，調整其虛擬時間：

```c
void BPF_STRUCT_OPS(nest_stopping, struct task_struct *p, bool runnable)
{
    /* 按權重的倒數和費用縮放執行時間 */
    p->scx.dsq_vtime += (slice_ns - p->scx.slice) * 100 / p->scx.weight;
}
```

當任務停止運行時，`nest_stopping` 根據其執行切片和權重調整其虛擬時間。這一調整確保任務在調度器的虛擬時間計算中得到公平考慮，保持平衡並防止任何單個任務壟斷 CPU 資源。

#### `nest_init_task`

初始化新任務的上下文：

```c
s32 BPF_STRUCT_OPS(nest_init_task, struct task_struct *p,
                   struct scx_init_task_args *args)
{
    struct task_ctx *tctx;
    struct bpf_cpumask *cpumask;

    /*
     * @p 是新的。確保其 task_ctx 可用。
     * 我們可以在此函數中休眠，以下內容將自動使用 GFP_KERNEL。
     */
    tctx = bpf_task_storage_get(&task_ctx_stor, p, 0,
                                BPF_LOCAL_STORAGE_GET_F_CREATE);
    if (!tctx)
        return -ENOMEM;

    cpumask = bpf_cpumask_create();
    if (!cpumask)
        return -ENOMEM;

    cpumask = bpf_kptr_xchg(&tctx->tmp_mask, cpumask);
    if (cpumask)
        bpf_cpumask_release(cpumask);

    tctx->attached_core = -1;
    tctx->prev_cpu = -1;

    return 0;
}
```

`nest_init_task` 函數為新任務初始化調度上下文。它通過從 `task_ctx_stor` 映射中檢索任務的上下文來確保任務的上下文可用，創建一個新的 `bpf_cpumask` 進行臨時計算，併為 `attached_core` 和 `prev_cpu` 設置初始值。

#### `nest_enable`

通過設置任務的虛擬時間啟用調度：

```c
void BPF_STRUCT_OPS(nest_enable, struct task_struct *p)
{
    p->scx.dsq_vtime = vtime_now;
}
```

`nest_enable` 函數通過將任務的虛擬時間 (`dsq_vtime`) 初始化為當前的全局虛擬時間 (`vtime_now`) 來激活任務的調度。這確保了任務的調度狀態與調度器的虛擬時間同步。

#### `stats_timerfn`

處理定期的統計信息收集：

```c
static int stats_timerfn(void *map, int *key, struct bpf_timer *timer)
{
    s32 cpu;
    struct bpf_cpumask *primary, *reserve;
    const struct cpumask *idle;
    stats_primary_mask = 0;
    stats_reserved_mask = 0;
    stats_other_mask = 0;
    stats_idle_mask = 0;
    long err;

    bpf_rcu_read_lock();
    primary = primary_cpumask;
    reserve = reserve_cpumask;
    if (!primary || !reserve) {
        bpf_rcu_read_unlock();
        scx_bpf_error("查找主或保留失敗");
        return 0;
    }

    idle = scx_bpf_get_idle_cpumask();
    bpf_for(cpu, 0, nr_cpus) {
        if (bpf_cpumask_test_cpu(cpu, cast_mask(primary)))
            stats_primary_mask |= (1ULL << cpu);
        else if (bpf_cpumask_test_cpu(cpu, cast_mask(reserve)))
            stats_reserved_mask |= (1ULL << cpu);
        else
            stats_other_mask |= (1ULL << cpu);

        if (bpf_cpumask_test_cpu(cpu, idle))
            stats_idle_mask |= (1ULL << cpu);
    }
    bpf_rcu_read_unlock();
    scx_bpf_put_idle_cpumask(idle);

    err = bpf_timer_start(timer, sampling_cadence_ns - 5000, 0);
    if (err)
        scx_bpf_error("啟動統計定時器失敗");

    return 0;
}
```

`stats_timerfn` 函數由中央定時器定期調用，用於收集和更新調度統計信息。它捕捉當前 CPU 核心的狀態，將它們分類到主、保留、其他和空閒掩碼中。這些信息提供了調度器如何管理 CPU 資源和任務分配的洞察。在收集統計信息後，該函數重新啟動定時器以確保持續監控。

#### `nest_init`

初始化 `scx_nest` 調度器：

```c
s32 BPF_STRUCT_OPS_SLEEPABLE(nest_init)
{
    struct bpf_cpumask *cpumask;
    s32 cpu;
    int err;
    struct bpf_timer *timer;
    u32 key = 0;

    err = scx_bpf_create_dsq(FALLBACK_DSQ_ID, NUMA_NO_NODE);
    if (err) {
        scx_bpf_error("創建回退 DSQ 失敗");
        return err;
    }

    cpumask = bpf_cpumask_create();
    if (!cpumask)
        return -ENOMEM;
    bpf_cpumask_clear(cpumask);
    cpumask = bpf_kptr_xchg(&primary_cpumask, cpumask);
    if (cpumask)
        bpf_cpumask_release(cpumask);

    cpumask = bpf_cpumask_create();
    if (!cpumask)
        return -ENOMEM;

    bpf_cpumask_clear(cpumask);
    cpumask = bpf_kptr_xchg(&reserve_cpumask, cpumask);
    if (cpumask)
        bpf_cpumask_release(cpumask);

    bpf_for(cpu, 0, nr_cpus) {
        s32 key = cpu;
        struct pcpu_ctx *ctx = bpf_map_lookup_elem(&pcpu_ctxs, &key);

        if (!ctx) {
            scx_bpf_error("查找 pcpu_ctx 失敗");
            return -ENOENT;
        }
        ctx->scheduled_compaction = false;
        if (bpf_timer_init(&ctx->timer, &pcpu_ctxs, CLOCK_BOOTTIME)) {
            scx_bpf_error("初始化 pcpu 定時器失敗");
            return -EINVAL;
        }
        err = bpf_timer_set_callback(&ctx->timer, compact_primary_core);
        if (err) {
            scx_bpf_error("設置 pcpu 定時器回調失敗");
            return -EINVAL;
        }
    }

    timer = bpf_map_lookup_elem(&stats_timer, &key);
    if (!timer) {
        scx_bpf_error("查找中央定時器失敗");
        return -ESRCH;
    }
    bpf_timer_init(timer, &stats_timer, CLOCK_BOOTTIME);
    bpf_timer_set_callback(timer, stats_timerfn);
    err = bpf_timer_start(timer, sampling_cadence_ns - 5000, 0);
    if (err)
        scx_bpf_error("啟動統計定時器失敗");

    return err;
}
```

`nest_init` 函數在系統初始化期間設置 `scx_nest` 調度器。它創建了一個回退調度隊列 (`FALLBACK_DSQ_ID`) 並初始化了主掩碼和保留掩碼。對於每個 CPU，它從 `pcpu_ctxs` 映射中檢索每 CPU 上下文，初始化壓縮定時器，並將回調設置為 `compact_primary_core`。此外，它初始化並啟動中央統計定時器 (`stats_timer`) 及其回調函數 `stats_timerfn`，確保調度器統計信息的持續監控。

#### `nest_exit`

在調度器退出時進行清理：

```c
void BPF_STRUCT_OPS(nest_exit, struct scx_exit_info *ei)
{
    UEI_RECORD(uei, ei);
}
```

`nest_exit` 函數記錄退出信息並在調度器被移除或系統關閉時執行任何必要的清理操作。這確保所有資源得到適當釋放，系統保持穩定。

#### `SCX_OPS_DEFINE`

為 `scx_nest` 調度器定義操作結構：

```c
SCX_OPS_DEFINE(nest_ops,
               .select_cpu        = (void *)nest_select_cpu,
               .enqueue            = (void *)nest_enqueue,
               .dispatch        = (void *)nest_dispatch,
               .running            = (void *)nest_running,
               .stopping        = (void *)nest_stopping,
               .init_task        = (void *)nest_init_task,
               .enable            = (void *)nest_enable,
               .init            = (void *)nest_init,
               .exit            = (void *)nest_exit,
               .flags            = 0,
               .name            = "nest");
```

`SCX_OPS_DEFINE` 宏將調度器的所有函數綁定到 `nest_ops` 結構中，`sched_ext` 框架使用該結構與調度器進行接口。這確保調度器的操作在任務調度事件期間被正確映射和調用。

### 初始化和清理

適當的初始化和清理對於調度器的穩定性和性能至關重要。

#### `nest_init` 函數

`nest_init` 函數負責在系統初始化期間設置調度器。其操作如下：

1. **創建回退調度隊列：**
   - 調用 `scx_bpf_create_dsq` 創建回退調度隊列 (`FALLBACK_DSQ_ID`)。如果失敗，記錄錯誤並退出。

2. **初始化主掩碼和保留掩碼：**
   - 創建並清除一個新的 `bpf_cpumask` 作為主掩碼。
   - 將新創建的掩碼與現有的 `primary_cpumask` 交換。如果存在舊掩碼，則釋放它。
   - 對保留掩碼重複相同的過程。

3. **初始化每 CPU 上下文：**
   - 對於每個 CPU，從 `pcpu_ctxs` 映射中檢索每 CPU 上下文。
   - 將 `scheduled_compaction` 標誌初始化為 `false`。
   - 使用 `bpf_timer_init` 初始化定時器，並使用 `bpf_timer_set_callback` 將回調設置為 `compact_primary_core`。
   - 如果任何步驟失敗，記錄錯誤並退出。

4. **初始化並啟動統計定時器：**
   - 從 `stats_timer` 映射中檢索中央統計定時器。
   - 初始化定時器並將其回調設置為 `stats_timerfn`。
   - 以 `sampling_cadence_ns - 5000` 納秒的延遲啟動定時器。
   - 如果啟動定時器失敗，記錄錯誤。

5. **返回：**
   - 函數返回定時器初始化的結果，指示成功或失敗。

這一初始化過程確保調度器的所有必要組件（包括 CPU 掩碼、定時器和調度隊列）都已正確設置。

#### `nest_exit` 函數

`nest_exit` 函數在調度器被移除或系統關閉時處理清理工作：

```c
void BPF_STRUCT_OPS(nest_exit, struct scx_exit_info *ei)
{
    UEI_RECORD(uei, ei);
}
```

此函數通過 `UEI_RECORD` 宏記錄退出信息，確保執行任何必要的清理操作。這對於保持系統穩定性和防止資源洩漏至關重要。

### 最終調度器定義

`SCX_OPS_DEFINE` 宏將調度器的所有函數綁定到單一結構中，供 `sched_ext` 框架使用：

```c
SCX_OPS_DEFINE(nest_ops,
               .select_cpu        = (void *)nest_select_cpu,
               .enqueue            = (void *)nest_enqueue,
               .dispatch        = (void *)nest_dispatch,
               .running            = (void *)nest_running,
               .stopping        = (void *)nest_stopping,
               .init_task        = (void *)nest_init_task,
               .enable            = (void *)nest_enable,
               .init            = (void *)nest_init,
               .exit            = (void *)nest_exit,
               .flags            = 0,
               .name            = "nest");
```

此結構體 `nest_ops` 有效地將調度器的操作註冊到 `sched_ext` 框架，確保調度器在各種調度事件和系統狀態下做出適當響應。

## 編譯和執行

要編譯和運行 `scx_nest` 調度器，請按照以下步驟操作：

**編譯代碼：**

使用 `make` 構建調度器。確保已安裝必要的構建工具和內核頭文件。

```bash
make
```

**運行調度器：**

執行編譯後的調度器二進制文件。根據系統配置和權限，您可能需要以提升的權限運行此命令。

```bash
./scx_nest
```

### 示例輸出

運行調度器後，您應該會看到類似以下的輸出：

```
# ./scx_nest 

喚醒統計
------------
WAKEUP_ATTACHED=150
WAKEUP_PREV_PRIMARY=61
WAKEUP_FULLY_IDLE_PRIMARY=0
WAKEUP_ANY_IDLE_PRIMARY=103
WAKEUP_FULLY_IDLE_RESERVE=0
WAKEUP_ANY_IDLE_RESERVE=216
WAKEUP_IDLE_OTHER=11


Nest 統計
----------
TASK_IMPATIENT=67
PROMOTED_TO_PRIMARY=217
PROMOTED_TO_RESERVED=8
DEMOTED_TO_RESERVED=212
RESERVED_AT_CAPACITY=6
SCHEDULED_COMPACTION=525
CANCELLED_COMPACTION=314
EAGERLY_COMPACTED=8
CALLBACK_COMPACTED=208


消耗統計
-------------
CONSUMED=166
NOT_CONSUMED=667



掩碼
-----
PRIMARY  ( 0): | -------------------------------------------------------------------------------------------------------------------------------- |
RESERVED (10): | ***-*--*--------------------------------------------------------***-*--*-------------------------------------------------------- |
OTHER    (128): | ******************************************************************************************************************************** |
IDLE     (16): | ********--------------------------------------------------------********-------------------------------------------------------- |


^C退出：已從用戶空間註銷
```

此輸出提供了有關任務喚醒、Nest 操作、消耗率和 CPU 掩碼狀態的全面統計信息。它顯示了調度器如何管理任務和 CPU 核心，展示了 `scx_nest` 算法在保持高頻率核心利用率和高效任務分配方面的有效性。

## 總結與行動呼籲

在本教程中，我們深入探討了 `scx_nest` 調度器的實現，這是一個先進的 eBPF 程序，基於核心頻率和利用率定製 CPU 調度以優化性能。通過利用 `sched_ext` 框架，`scx_nest` 展示了 eBPF 如何動態定義調度行為，提供超越傳統調度器的靈活性和控制力。

主要收穫包括：

- 理解 `sched_ext` 調度器類的靈活性和強大功能。
- 探索支撐 `scx_nest` 調度器的複雜數據結構和映射。
- 分析管理任務分配、核心壓縮和統計信息收集的核心函數。
- 學習如何編譯和執行調度器，並通過詳細統計信息觀察其影響。

`scx_nest` 調度器是一個極好的例子，展示瞭如何利用先進的 eBPF 編程以靈活和動態的方式實現複雜的系統功能。

如果您想深入瞭解 eBPF 並探索更多高級示例，請訪問我們的教程倉庫 [https://github.com/eunomia-bpf/bpf-developer-tutorial](https://github.com/eunomia-bpf/bpf-developer-tutorial) 或查看我們的網站 [https://eunomia.dev/tutorials/](https://eunomia.dev/tutorials/)。

## 參考文獻

`scx_nest` 調度器的原始源代碼可在 [sched-ext/scx](https://github.com/sched-ext/scx) 倉庫中找到。

可以增強您理解的其他資源包括：

- **Linux 內核文檔:** [Scheduler Ext 文檔](https://www.kernel.org/doc/html/next/scheduler/sched-ext.html)
- **內核源樹:** [Linux 內核 `sched_ext` 工具](https://github.com/torvalds/linux/tree/master/tools/sched_ext)
- **eBPF 官方文檔:** [https://docs.ebpf.io/](https://docs.ebpf.io/)
- **libbpf 文檔:** [https://github.com/libbpf/libbpf](https://github.com/libbpf/libbpf)

歡迎探索這些資源，擴展您的知識，繼續深入學習高級 eBPF 編程的旅程。