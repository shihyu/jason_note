# eBPF 入門開發實踐教程十：在 eBPF 中使用 hardirqs 或 softirqs 捕獲中斷事件

eBPF (Extended Berkeley Packet Filter) 是 Linux 內核上的一個強大的網絡和性能分析工具。它允許開發者在內核運行時動態加載、更新和運行用戶定義的代碼。

本文是 eBPF 入門開發實踐教程的第十篇，在 eBPF 中使用 hardirqs 或 softirqs 捕獲中斷事件。
hardirqs 和 softirqs 是 Linux 內核中兩種不同類型的中斷處理程序。它們用於處理硬件設備產生的中斷請求，以及內核中的異步事件。在 eBPF 中，我們可以使用同名的 eBPF 工具 hardirqs 和 softirqs 來捕獲和分析內核中與中斷處理相關的信息。

## hardirqs 和 softirqs 是什麼？

hardirqs 是硬件中斷處理程序。當硬件設備產生一箇中斷請求時，內核會將該請求映射到一個特定的中斷向量，然後執行與之關聯的硬件中斷處理程序。硬件中斷處理程序通常用於處理設備驅動程序中的事件，例如設備數據傳輸完成或設備錯誤。

softirqs 是軟件中斷處理程序。它們是內核中的一種底層異步事件處理機制，用於處理內核中的高優先級任務。softirqs 通常用於處理網絡協議棧、磁盤子系統和其他內核組件中的事件。與硬件中斷處理程序相比，軟件中斷處理程序具有更高的靈活性和可配置性。

## 實現原理

在 eBPF 中，我們可以通過掛載特定的 kprobe 或者 tracepoint 來捕獲和分析 hardirqs 和 softirqs。為了捕獲 hardirqs 和 softirqs，需要在相關的內核函數上放置 eBPF 程序。這些函數包括：

- 對於 hardirqs：irq_handler_entry 和 irq_handler_exit。
- 對於 softirqs：softirq_entry 和 softirq_exit。

當內核處理 hardirqs 或 softirqs 時，這些 eBPF 程序會被執行，從而收集相關信息，如中斷向量、中斷處理程序的執行時間等。收集到的信息可以用於分析內核中的性能問題和其他與中斷處理相關的問題。

為了捕獲 hardirqs 和 softirqs，可以遵循以下步驟：

1. 在 eBPF 程序中定義用於存儲中斷信息的數據結構和映射。
2. 編寫 eBPF 程序，將其掛載到相應的內核函數上，以捕獲 hardirqs 或 softirqs。
3. 在 eBPF 程序中，收集中斷處理程序的相關信息，並將這些信息存儲在映射中。
4. 在用戶空間應用程序中，讀取映射中的數據以分析和展示中斷處理信息。

通過上述方法，我們可以在 eBPF 中使用 hardirqs 和 softirqs 捕獲和分析內核中的中斷事件，以識別潛在的性能問題和與中斷處理相關的問題。

## hardirqs 代碼實現

hardirqs 程序的主要目的是獲取中斷處理程序的名稱、執行次數和執行時間，並以直方圖的形式展示執行時間的分佈。讓我們一步步分析這段代碼。

```c
// SPDX-License-Identifier: GPL-2.0
// Copyright (c) 2020 Wenbo Zhang
#include <vmlinux.h>
#include <bpf/bpf_core_read.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include "hardirqs.h"
#include "bits.bpf.h"
#include "maps.bpf.h"

#define MAX_ENTRIES 256

const volatile bool filter_cg = false;
const volatile bool targ_dist = false;
const volatile bool targ_ns = false;
const volatile bool do_count = false;

struct {
 __uint(type, BPF_MAP_TYPE_CGROUP_ARRAY);
 __type(key, u32);
 __type(value, u32);
 __uint(max_entries, 1);
} cgroup_map SEC(".maps");

struct {
 __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
 __uint(max_entries, 1);
 __type(key, u32);
 __type(value, u64);
} start SEC(".maps");

struct {
 __uint(type, BPF_MAP_TYPE_HASH);
 __uint(max_entries, MAX_ENTRIES);
 __type(key, struct irq_key);
 __type(value, struct info);
} infos SEC(".maps");

static struct info zero;

static int handle_entry(int irq, struct irqaction *action)
{
 if (filter_cg && !bpf_current_task_under_cgroup(&cgroup_map, 0))
  return 0;

 if (do_count) {
  struct irq_key key = {};
  struct info *info;

  bpf_probe_read_kernel_str(&key.name, sizeof(key.name), BPF_CORE_READ(action, name));
  info = bpf_map_lookup_or_try_init(&infos, &key, &zero);
  if (!info)
   return 0;
  info->count += 1;
  return 0;
 } else {
  u64 ts = bpf_ktime_get_ns();
  u32 key = 0;

  if (filter_cg && !bpf_current_task_under_cgroup(&cgroup_map, 0))
   return 0;

  bpf_map_update_elem(&start, &key, &ts, BPF_ANY);
  return 0;
 }
}

static int handle_exit(int irq, struct irqaction *action)
{
 struct irq_key ikey = {};
 struct info *info;
 u32 key = 0;
 u64 delta;
 u64 *tsp;

 if (filter_cg && !bpf_current_task_under_cgroup(&cgroup_map, 0))
  return 0;

 tsp = bpf_map_lookup_elem(&start, &key);
 if (!tsp)
  return 0;

 delta = bpf_ktime_get_ns() - *tsp;
 if (!targ_ns)
  delta /= 1000U;

 bpf_probe_read_kernel_str(&ikey.name, sizeof(ikey.name), BPF_CORE_READ(action, name));
 info = bpf_map_lookup_or_try_init(&infos, &ikey, &zero);
 if (!info)
  return 0;

 if (!targ_dist) {
  info->count += delta;
 } else {
  u64 slot;

  slot = log2(delta);
  if (slot >= MAX_SLOTS)
   slot = MAX_SLOTS - 1;
  info->slots[slot]++;
 }

 return 0;
}

SEC("tp_btf/irq_handler_entry")
int BPF_PROG(irq_handler_entry_btf, int irq, struct irqaction *action)
{
 return handle_entry(irq, action);
}

SEC("tp_btf/irq_handler_exit")
int BPF_PROG(irq_handler_exit_btf, int irq, struct irqaction *action)
{
 return handle_exit(irq, action);
}

SEC("raw_tp/irq_handler_entry")
int BPF_PROG(irq_handler_entry, int irq, struct irqaction *action)
{
 return handle_entry(irq, action);
}

SEC("raw_tp/irq_handler_exit")
int BPF_PROG(irq_handler_exit, int irq, struct irqaction *action)
{
 return handle_exit(irq, action);
}

char LICENSE[] SEC("license") = "GPL";
```

這段代碼是一個 eBPF 程序，用於捕獲和分析內核中硬件中斷處理程序（hardirqs）的執行信息。程序的主要目的是獲取中斷處理程序的名稱、執行次數和執行時間，並以直方圖的形式展示執行時間的分佈。讓我們一步步分析這段代碼。

1. 包含必要的頭文件和定義數據結構：

    ```c
    #include <vmlinux.h>
    #include <bpf/bpf_core_read.h>
    #include <bpf/bpf_helpers.h>
    #include <bpf/bpf_tracing.h>
    #include "hardirqs.h"
    #include "bits.bpf.h"
    #include "maps.bpf.h"
    ```

    該程序包含了 eBPF 開發所需的標準頭文件，以及用於定義數據結構和映射的自定義頭文件。

2. 定義全局變量和映射：

    ```c

    #define MAX_ENTRIES 256

    const volatile bool filter_cg = false;
    const volatile bool targ_dist = false;
    const volatile bool targ_ns = false;
    const volatile bool do_count = false;

    ...
    ```

    該程序定義了一些全局變量，用於配置程序的行為。例如，`filter_cg` 控制是否過濾 cgroup，`targ_dist` 控制是否顯示執行時間的分佈等。此外，程序還定義了三個映射，分別用於存儲 cgroup 信息、開始時間戳和中斷處理程序的信息。

3. 定義兩個輔助函數 `handle_entry` 和 `handle_exit`：

    這兩個函數分別在中斷處理程序的入口和出口處被調用。`handle_entry` 記錄開始時間戳或更新中斷計數，`handle_exit` 計算中斷處理程序的執行時間，並將結果存儲到相應的信息映射中。

4. 定義 eBPF 程序的入口點：

    ```c

    SEC("tp_btf/irq_handler_entry")
    int BPF_PROG(irq_handler_entry_btf, int irq, struct irqaction *action)
    {
    return handle_entry(irq, action);
    }

    SEC("tp_btf/irq_handler_exit")
    int BPF_PROG(irq_handler_exit_btf, int irq, struct irqaction *action)
    {
    return handle_exit(irq, action);
    }

    SEC("raw_tp/irq_handler_entry")
    int BPF_PROG(irq_handler_entry, int irq, struct irqaction *action)
    {
    return handle_entry(irq, action);
    }

    SEC("raw_tp/irq_handler_exit")
    int BPF_PROG(irq_handler_exit, int irq, struct irqaction *action)
    {
    return handle_exit(irq, action);
    }
    ```

    這裡定義了四個 eBPF 程序入口點，分別用於捕獲中斷處理程序的入口和出口事件。`tp_btf` 和 `raw_tp` 分別代表使用 BPF Type Format（BTF）和原始 tracepoints 捕獲事件。這樣可以確保程序在不同內核版本上可以移植和運行。

Softirq 代碼也類似，這裡就不再贅述了。

## 運行代碼

eunomia-bpf 是一個結合 Wasm 的開源 eBPF 動態加載運行時和開發工具鏈，它的目的是簡化 eBPF 程序的開發、構建、分發、運行。可以參考 <https://github.com/eunomia-bpf/eunomia-bpf> 下載和安裝 ecc 編譯工具鏈和 ecli 運行時。我們使用 eunomia-bpf 編譯運行這個例子。

要編譯這個程序，請使用 ecc 工具：

```console
$ ecc hardirqs.bpf.c
Compiling bpf object...
Packing ebpf object and config into package.json...
```

然後運行：

```console
sudo ecli run ./package.json
```

## 總結

在本章節（eBPF 入門開發實踐教程十：在 eBPF 中使用 hardirqs 或 softirqs 捕獲中斷事件）中，我們學習瞭如何使用 eBPF 程序捕獲和分析內核中硬件中斷處理程序（hardirqs）的執行信息。我們詳細講解了示例代碼，包括如何定義數據結構、映射以及 eBPF 程序入口點，以及如何在中斷處理程序的入口和出口處調用輔助函數來記錄執行信息。

通過學習本章節內容，您應該已經掌握瞭如何在 eBPF 中使用 hardirqs 或 softirqs 捕獲中斷事件的方法，以及如何分析這些事件以識別內核中的性能問題和其他與中斷處理相關的問題。這些技能對於分析和優化 Linux 內核的性能至關重要。

為了更好地理解和實踐 eBPF 編程，我們建議您閱讀 eunomia-bpf 的官方文檔：<https://github.com/eunomia-bpf/eunomia-bpf> 。此外，我們還為您提供了完整的教程和源代碼，您可以在 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 中查看和學習。希望本教程能夠幫助您順利入門 eBPF 開發，併為您的進一步學習和實踐提供有益的參考。
