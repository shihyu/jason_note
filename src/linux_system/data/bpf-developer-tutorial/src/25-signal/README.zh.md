# eBPF 入門實踐教程：用 bpf_send_signal 發送信號終止惡意進程

eBPF (擴展的伯克利數據包過濾器) 是 Linux 內核的一種革命性技術，允許用戶在內核空間執行自定義程序，而不需要修改內核源代碼或加載任何內核模塊。這使得開發人員可以非常靈活地對 Linux 系統進行觀測、修改和控制。

本文介紹瞭如何使用 eBPF 的 bpf_send_signal 功能，向指定的進程發送信號進行干預。本文完整的源代碼和更多的教程文檔，請參考 <https://github.com/eunomia-bpf/bpf-developer-tutorial>

## 使用場景

**1. 性能分析:**  
在現代軟件生態系統中，優化應用程序的性能是開發人員和系統管理員的一個核心任務。當應用程序，如 hhvm，出現運行緩慢或資源利用率異常高時，它可能會對整個系統產生不利影響。因此，定位這些性能瓶頸並及時解決是至關重要的。

**2. 異常檢測與響應:**  
任何運行在生產環境中的系統都可能面臨各種異常情況，從簡單的資源洩露到複雜的惡意軟件攻擊。在這些情況下，系統需要能夠迅速、準確地檢測到這些異常，並採取適當的應對措施。

**3. 動態系統管理:**  
隨著雲計算和微服務架構的普及，能夠根據當前系統狀態動態調整資源配置和應用行為已經成為了一個關鍵需求。例如，根據流量波動自動擴容或縮容，或者在檢測到系統過熱時降低 CPU 頻率。

### 現有方案的不足

為了滿足上述使用場景的需求，傳統的技術方法如下：

- 安裝一個 bpf 程序，該程序會持續監視系統，同時對一個 map 進行輪詢。
- 當某個事件觸發了 bpf 程序中定義的特定條件時，它會將相關數據寫入此 map。
- 接著，外部分析工具會從該 map 中讀取數據，並根據讀取到的信息向目標進程發送信號。

儘管這種方法在很多場景中都是可行的，但它存在一個主要的缺陷：從事件發生到外部工具響應的時間延遲可能相對較大。這種延遲可能會影響到事件的響應速度，從而使得性能分析的結果不準確或者在面對惡意活動時無法及時作出反應。

### 新方案的優勢

為了克服傳統方法的這些限制，Linux 內核提供了 `bpf_send_signal` 和 `bpf_send_signal_thread` 這兩個 helper 函數。

這兩個函數帶來的主要優勢包括：

**1. 實時響應:**  
通過直接從內核空間發送信號，避免了用戶空間的額外開銷，這確保了信號能夠在事件發生後立即被髮送，大大減少了延遲。

**2. 準確性:**  
得益於減少的延遲，現在我們可以獲得更準確的系統狀態快照，這對於性能分析和異常檢測尤其重要。

**3. 靈活性:**  
這些新的 helper 函數為開發人員提供了更多的靈活性，他們可以根據不同的使用場景和需求來自定義信號的發送邏輯，從而更精確地控制和管理系統行為。

## 內核態代碼分析

在現代操作系統中，一種常見的安全策略是監控和控制進程之間的交互。尤其在Linux系統中，`ptrace` 系統調用是一個強大的工具，它允許一個進程觀察和控制另一個進程的執行，並修改其寄存器和內存。這使得它成為了調試和跟蹤工具（如 `strace` 和 `gdb`）的主要機制。然而，惡意的 `ptrace` 使用也可能導致安全隱患。

這個程序的目標是在內核態監控 `ptrace` 的調用，當滿足特定的條件時，它會發送一個 `SIGKILL` 信號終止調用進程。此外，為了調試或審計目的，該程序會記錄這種干預並將相關信息發送到用戶空間。

## 代碼分析

### 1. 數據結構定義 (`signal.h`)

signal.h

```c
// Simple message structure to get events from eBPF Programs
// in the kernel to user space
#define TASK_COMM_LEN 16
struct event {
    int pid;
    char comm[TASK_COMM_LEN];
    bool success;
};
```

這部分定義了一個簡單的消息結構，用於從內核的 eBPF 程序傳遞事件到用戶空間。結構包括進程ID、命令名和一個標記是否成功發送信號的布爾值。

### 2. eBPF 程序 (`signal.bpf.c`)

signal.bpf.c

```c
// SPDX-License-Identifier: BSD-3-Clause
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "common.h"

char LICENSE[] SEC("license") = "Dual BSD/GPL";

// Ringbuffer Map to pass messages from kernel to user
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} rb SEC(".maps");

// Optional Target Parent PID
const volatile int target_ppid = 0;

SEC("tp/syscalls/sys_enter_ptrace")
int bpf_dos(struct trace_event_raw_sys_enter *ctx)
{
    long ret = 0;
    size_t pid_tgid = bpf_get_current_pid_tgid();
    int pid = pid_tgid >> 32;

    // if target_ppid is 0 then we target all pids
    if (target_ppid != 0) {
        struct task_struct *task = (struct task_struct *)bpf_get_current_task();
        int ppid = BPF_CORE_READ(task, real_parent, tgid);
        if (ppid != target_ppid) {
            return 0;
        }
    }

    // Send signal. 9 == SIGKILL
    ret = bpf_send_signal(9);

    // Log event
    struct event *e;
    e = bpf_ringbuf_reserve(&rb, sizeof(*e), 0);
    if (e) {
        e->success = (ret == 0);
        e->pid = pid;
        bpf_get_current_comm(&e->comm, sizeof(e->comm));
        bpf_ringbuf_submit(e, 0);
    }

    return 0;
}
```

- **許可證聲明**

  聲明瞭程序的許可證為 "Dual BSD/GPL"，這是為了滿足 Linux 內核對 eBPF 程序的許可要求。

- **Ringbuffer Map**

  這是一個 ring buffer 類型的 map，允許 eBPF 程序在內核空間產生的消息被用戶空間程序高效地讀取。

- **目標父進程ID**

  `target_ppid` 是一個可選的父進程ID，用於限制哪些進程受到影響。如果它被設置為非零值，只有與其匹配的進程才會被目標。

- **主函數 `bpf_dos`**

  - **進程檢查**  
    程序首先獲取當前進程的ID。如果設置了 `target_ppid`，它還會獲取當前進程的父進程ID並進行比較。如果兩者不匹配，則直接返回。

  - **發送信號**  
    使用 `bpf_send_signal(9)` 來發送 `SIGKILL` 信號。這將終止調用 `ptrace` 的進程。

  - **記錄事件**  
    使用 ring buffer map 記錄這個事件。這包括了是否成功發送信號、進程ID以及進程的命令名。

總結：這個 eBPF 程序提供了一個方法，允許系統管理員或安全團隊在內核級別監控和干預 `ptrace` 調用，提供了一個對抗潛在惡意活動或誤操作的額外層次。

## 編譯運行

eunomia-bpf 是一個結合 Wasm 的開源 eBPF 動態加載運行時和開發工具鏈，它的目的是簡化 eBPF 程序的開發、構建、分發、運行。可以參考 <https://github.com/eunomia-bpf/eunomia-bpf> 下載和安裝 ecc 編譯工具鏈和 ecli 運行時。我們使用 eunomia-bpf 編譯運行這個例子。

編譯：

```bash
./ecc signal.bpf.c signal.h
```

使用方式：

```console
$ sudo ./ecli package.json
TIME     PID    COMM   SUCCESS
```

這個程序會對任何試圖使用 `ptrace` 系統調用的程序，例如 `strace`，發出 `SIG_KILL` 信號。
一旦 eBPF 程序開始運行，你可以通過運行以下命令進行測試：

```bash
$ strace /bin/whoami
Killed
```

原先的 console 中會輸出：

```txt
INFO [bpf_loader_lib::skeleton] Running ebpf program...
TIME     PID    COMM   SUCCESS 
13:54:45  8857  strace true
```

完整的源代碼可以參考：<https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/25-signal>

## 總結

通過這個實例，我們深入瞭解瞭如何將 eBPF 程序與用戶態程序相結合，實現對系統調用的監控和干預。eBPF 提供了一種在內核空間執行程序的機制，這種技術不僅限於監控，還可用於性能優化、安全防禦、系統診斷等多種場景。對於開發者來說，這為Linux系統的性能調優和故障排查提供了一種強大且靈活的工具。

最後，如果您對 eBPF 技術感興趣，並希望進一步瞭解和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 和教程網站 <https://eunomia.dev/zh/tutorials/>

## 參考資料

- <https://github.com/pathtofile/bad-bpf>
- <https://www.mail-archive.com/netdev@vger.kernel.org/msg296358.html>
