# eBPF 實踐教程：使用 eBPF 跟蹤 Go 協程狀態

Go 是 Google 創建的一種廣受歡迎的編程語言，以其強大的併發模型而著稱。Go 語言的一個重要特點是協程（goroutine）的使用——這些協程是輕量級、由 Go 運行時管理的線程，使得編寫併發程序變得非常簡單。然而，在實時環境中理解和跟蹤這些協程的執行狀態，尤其是在調試複雜系統時，可能會面臨很大的挑戰。

這時我們可以利用 eBPF（擴展伯克利包過濾器）技術。eBPF 最初設計用於網絡數據包過濾，但隨著時間的推移，eBPF 已經發展成為一個強大的工具，用於跟蹤和監控系統行為。通過使用 eBPF，我們可以深入到內核，收集有關 Go 程序運行時行為的數據，包括協程的狀態。本文將探討如何使用 eBPF 跟蹤 Go 程序中的協程狀態轉換。

## 背景：協程與 eBPF

### 協程

協程是 Go 語言的核心特性之一，它提供了一種簡單而高效的併發處理方式。與傳統的線程不同，協程由 Go 運行時管理，而不是由操作系統管理，因此更加輕量化。協程可以在以下幾種狀態之間進行轉換：

- **RUNNABLE（可運行）**：協程已準備好運行。
- **RUNNING（運行中）**：協程正在執行中。
- **WAITING（等待）**：協程正在等待某個事件（如 I/O 或定時器）。
- **DEAD（終止）**：協程執行完畢並已終止。

理解這些狀態以及協程之間的狀態轉換對於診斷性能問題、確保 Go 程序的高效運行至關重要。

### eBPF

eBPF 是一種強大的技術，它允許開發人員在不修改內核源代碼或加載內核模塊的情況下，在 Linux 內核中運行自定義程序。eBPF 最初用於數據包過濾，但現在已擴展為一種多功能工具，廣泛應用於性能監控、安全和調試。

通過編寫 eBPF 程序，開發人員可以跟蹤各種系統事件，包括系統調用、網絡事件和進程執行。在本文中，我們將重點介紹如何使用 eBPF 跟蹤 Go 程序中協程的狀態轉換。

## eBPF 內核代碼

現在，讓我們深入探討實現該跟蹤功能的 eBPF 內核代碼。

```c
#include <vmlinux.h>
#include "goroutine.h"
#include <bpf/bpf_core_read.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#define GOID_OFFSET 0x98

struct {
  __uint(type, BPF_MAP_TYPE_RINGBUF);
  __uint(max_entries, 256 * 1024);
} rb SEC(".maps");

SEC("uprobe/./go-server-http/main:runtime.casgstatus")
int uprobe_runtime_casgstatus(struct pt_regs *ctx) {
  int newval = ctx->cx;
  void *gp = ctx->ax;
  struct goroutine_execute_data *data;
  u64 goid;
  if (bpf_probe_read_user(&goid, sizeof(goid), gp + GOID_OFFSET) == 0) {
    data = bpf_ringbuf_reserve(&rb, sizeof(*data), 0);
    if (data) {
      u64 pid_tgid = bpf_get_current_pid_tgid();
      data->pid = pid_tgid;
      data->tgid = pid_tgid >> 32;
      data->goid = goid;
      data->state = newval;
      bpf_ringbuf_submit(data, 0);
    }
  }
  return 0;
}

char LICENSE[] SEC("license") = "GPL";
```

1. **頭文件**：代碼首先包含了必要的頭文件，如 `vmlinux.h`（提供內核定義）和 `bpf_helpers.h`（提供 eBPF 程序的輔助函數）。
2. **GOID_OFFSET**：`goid` 字段的偏移量被硬編碼為 `0x98`，這是特定於所跟蹤的 Go 版本和程序的。此偏移量在不同的 Go 版本或程序中可能有所不同。
3. **環形緩衝區映射**：定義了一個 BPF 環形緩衝區映射，用於存儲協程的執行數據。這個緩衝區允許內核高效地將信息傳遞到用戶空間。
4. **Uprobe**：該 eBPF 程序的核心是一個附加到 Go 程序中 `runtime.casgstatus` 函數的 uprobe（用戶級探針）。該函數負責改變協程的狀態，因此非常適合用來攔截和跟蹤狀態轉換。
5. **讀取協程 ID**：`bpf_probe_read_user` 函數從用戶空間內存中讀取協程 ID（`goid`），使用的是預定義的偏移量。
6. **提交數據**：如果成功讀取了協程 ID，則數據會與進程 ID、線程組 ID 以及協程的新狀態一起存儲在環形緩衝區中。隨後，這些數據會提交到用戶空間以供分析。

## 運行程序

要運行此跟蹤程序，請按照以下步驟操作：

1. **編譯 eBPF 代碼**：使用類似 `ecc`（eBPF 編譯集合）這樣的編譯器編譯 eBPF 程序，並生成一個可以由 eBPF 加載器加載的包。

    ```bash
    ecc goroutine.bpf.c goroutine.h
    ```

2. **運行 eBPF 程序**：使用 eBPF 加載器運行編譯後的 eBPF 程序。

    ```bash
    ecli-rs run package.json
    ```

3. **輸出**：程序將輸出協程的狀態轉換及其 `goid`、`pid` 和 `tgid`。以下是一個示例輸出：

    ```console
    TIME     STATE       GOID   PID    TGID   
    21:00:47 DEAD(6)     0      2542844 2542844
    21:00:47 RUNNABLE(1) 0      2542844 2542844
    21:00:47 RUNNING(2)  1      2542844 2542844
    21:00:47 WAITING(4)  2      2542847 2542844
    ```

完整代碼可以在 <https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/31-goroutine> 找到。

如果你想了解更多關於 eBPF 的知識和實踐，你可以訪問我們的教程代碼庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/tutorials/> 獲取更多示例和完整教程。

內核模式 eBPF 運行時的 `Uprobe` 可能會帶來較大的性能開銷。在這種情況下，你也可以考慮使用用戶模式的 eBPF 運行時，例如 [bpftime](https://github.com/eunomia-bpf/bpftime)。bpftime 是基於 LLVM JIT/AOT 的用戶模式 eBPF 運行時，它可以在用戶模式下運行 eBPF 程序，並且在處理 `uprobe` 時比內核模式 eBPF 更快。

### 結論

使用 eBPF 跟蹤協程狀態可以深入瞭解 Go 程序的執行情況，尤其是在傳統調試工具可能無法勝任的生產環境中。通過利用 eBPF，開發人員可以監控和診斷性能問題，確保 Go 應用程序高效運行。

請注意，本 eBPF 程序中使用的偏移量是特定於所跟蹤的 Go 版本和程序的。隨著 Go 的發展，這些偏移量可能會發生變化，需要對 eBPF 代碼進行更新。

在未來的探索中，我們可以將這種方法擴展到跟蹤 Go 程序或其他語言的其他方面，展示 eBPF 在現代軟件開發中的多功能性和強大作用。
