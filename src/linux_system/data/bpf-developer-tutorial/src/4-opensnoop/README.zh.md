# eBPF 入門開發實踐教程四：在 eBPF 中捕獲進程打開文件的系統調用集合，使用全局變量過濾進程 pid

eBPF（Extended Berkeley Packet Filter）是一種內核執行環境，它可以讓用戶在內核中運行一些安全的、高效的程序。它通常用於網絡過濾、性能分析、安全監控等場景。eBPF 之所以強大，是因為它能夠在內核運行時捕獲和修改數據包或者系統調用，從而實現對操作系統行為的監控和調整。

本文是 eBPF 入門開發實踐教程的第四篇，主要介紹如何捕獲進程打開文件的系統調用集合，並使用全局變量在 eBPF 中過濾進程 pid。

在 Linux 系統中，進程與文件之間的交互是通過系統調用來實現的。系統調用是用戶態程序與內核態程序之間的接口，它們允許用戶態程序請求內核執行特定操作。在本教程中，我們關注的是 sys_openat 系統調用，它用於打開文件。

當進程打開一個文件時，它會向內核發出 sys_openat 系統調用，並傳遞相關參數（例如文件路徑、打開模式等）。內核會處理這個請求，並返回一個文件描述符（file descriptor），這個描述符將在後續的文件操作中用作引用。通過捕獲 sys_openat 系統調用，我們可以瞭解進程在什麼時候以及如何打開文件。

## 在 eBPF 中捕獲進程打開文件的系統調用集合

首先，我們需要編寫一段 eBPF 程序來捕獲進程打開文件的系統調用，具體實現如下：

```c
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>

/// @description "Process ID to trace"
const volatile int pid_target = 0;

SEC("tracepoint/syscalls/sys_enter_openat")
int tracepoint__syscalls__sys_enter_openat(struct trace_event_raw_sys_enter* ctx)
{
    u64 id = bpf_get_current_pid_tgid();
    u32 pid = id >> 32;

    if (pid_target && pid_target != pid)
        return false;
    // Use bpf_printk to print the process information
    bpf_printk("Process ID: %d enter sys openat\n", pid);
    return 0;
}

/// "Trace open family syscalls."
char LICENSE[] SEC("license") = "GPL";
```

這段 eBPF 程序實現了：

1. 引入頭文件：<vmlinux.h> 包含了內核數據結構的定義，<bpf/bpf_helpers.h> 包含了 eBPF 程序所需的輔助函數。
2. 定義全局變量 `pid_target`，用於過濾指定進程 ID。這裡設為 0 表示捕獲所有進程的 sys_openat 調用。
3. 使用 `SEC` 宏定義一個 eBPF 程序，關聯到 tracepoint "tracepoint/syscalls/sys_enter_openat"。這個 tracepoint 會在進程發起 `sys_openat` 系統調用時觸發。
4. 實現 eBPF 程序 `tracepoint__syscalls__sys_enter_openat`，它接收一個類型為 `struct trace_event_raw_sys_enter` 的參數 `ctx`。這個結構體包含了關於系統調用的信息。
5. 使用 `bpf_get_current_pid_tgid()` 函數獲取當前進程的 PID 和 TID（線程 ID）。由於我們只關心 PID，所以將其值右移 32 位賦值給 `u32` 類型的變量 `pid`。
6. 檢查 `pid_target` 變量是否與當前進程的 pid 相等。如果 `pid_target` 不為 0 且與當前進程的 pid 不相等，則返回 `false`，不對該進程的 `sys_openat` 調用進行捕獲。
7. 使用 `bpf_printk()` 函數打印捕獲到的進程 ID 和 `sys_openat` 調用的相關信息。這些信息可以在用戶空間通過 BPF 工具查看。
8. 將程序許可證設置為 "GPL"，這是運行 eBPF 程序的必要條件。

這個 eBPF 程序可以通過 libbpf 或 eunomia-bpf 等工具加載到內核並執行。它將捕獲指定進程（或所有進程）的 sys_openat 系統調用，並在用戶空間輸出相關信息。

eunomia-bpf 是一個結合 Wasm 的開源 eBPF 動態加載運行時和開發工具鏈，它的目的是簡化 eBPF 程序的開發、構建、分發、運行。可以參考 <https://github.com/eunomia-bpf/eunomia-bpf> 下載和安裝 ecc 編譯工具鏈和 ecli 運行時。我們使用 eunomia-bpf 編譯運行這個例子。完整代碼請查看 <https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/4-opensnoop> 。

編譯運行上述代碼：

```console
$ ecc opensnoop.bpf.c
Compiling bpf object...
Packing ebpf object and config into package.json...
$ sudo ecli run package.json
Runing eBPF program...
```

運行這段程序後，可以通過查看 `/sys/kernel/debug/tracing/trace_pipe` 文件來查看 eBPF 程序的輸出：

```console
$ sudo cat /sys/kernel/debug/tracing/trace_pipe
           <...>-3840345 [010] d... 3220701.101179: bpf_trace_printk: Process ID: 3840345 enter sys openat
           <...>-3840345 [010] d... 3220702.158000: bpf_trace_printk: Process ID: 3840345 enter sys openat
```

此時，我們已經能夠捕獲進程打開文件的系統調用了。

## 使用全局變量在 eBPF 中過濾進程 pid

全局變量在 eBPF 程序中充當一種數據共享機制，它們允許用戶態程序與 eBPF 程序之間進行數據交互。這在過濾特定條件或修改 eBPF 程序行為時非常有用。這種設計使得用戶態程序能夠在運行時動態地控制 eBPF 程序的行為。

在我們的例子中，全局變量 `pid_target` 用於過濾進程 PID。用戶態程序可以設置此變量的值，以便在 eBPF 程序中只捕獲與指定 PID 相關的 `sys_openat` 系統調用。

使用全局變量的原理是，全局變量在 eBPF 程序的數據段（data section）中定義並存儲。當 eBPF 程序加載到內核並執行時，這些全局變量會保持在內核中，可以通過 BPF 系統調用進行訪問。用戶態程序可以使用 BPF 系統調用中的某些特性，如 `bpf_obj_get_info_by_fd` 和 `bpf_obj_get_info`，獲取 eBPF 對象的信息，包括全局變量的位置和值。

可以通過執行 ecli -h 命令來查看 opensnoop 的幫助信息：

```console
$ ecli package.json -h
Usage: opensnoop_bpf [--help] [--version] [--verbose] [--pid_target VAR]

Trace open family syscalls.

Optional arguments:
  -h, --help    shows help message and exits 
  -v, --version prints version information and exits 
  --verbose     prints libbpf debug information 
  --pid_target  Process ID to trace 

Built with eunomia-bpf framework.
See https://github.com/eunomia-bpf/eunomia-bpf for more information.
```

可以通過 `--pid_target` 選項來指定要捕獲的進程的 pid，例如：

```console
$ sudo ./ecli run package.json --pid_target 618
Runing eBPF program...
```

運行這段程序後，可以通過查看 `/sys/kernel/debug/tracing/trace_pipe` 文件來查看 eBPF 程序的輸出：

```console
$ sudo cat /sys/kernel/debug/tracing/trace_pipe
           <...>-3840345 [010] d... 3220701.101179: bpf_trace_printk: Process ID: 618 enter sys openat
           <...>-3840345 [010] d... 3220702.158000: bpf_trace_printk: Process ID: 618 enter sys openat
```

## 總結

本文介紹瞭如何使用 eBPF 程序來捕獲進程打開文件的系統調用。在 eBPF 程序中，我們可以通過定義 `tracepoint__syscalls__sys_enter_open` 和 `tracepoint__syscalls__sys_enter_openat` 函數並使用 `SEC` 宏把它們附加到 sys_enter_open 和 sys_enter_openat 兩個 tracepoint 來捕獲進程打開文件的系統調用。我們可以使用 `bpf_get_current_pid_tgid` 函數獲取調用 open 或 openat 系統調用的進程 ID，並使用 `bpf_printk` 函數在內核日誌中打印出來。在 eBPF 程序中，我們還可以通過定義一個全局變量 `pid_target` 來指定要捕獲的進程的 pid，從而過濾輸出，只輸出指定的進程的信息。

通過學習本教程，您應該對如何在 eBPF 中捕獲和過濾特定進程的系統調用有了更深入的瞭解。這種方法在系統監控、性能分析和安全審計等場景中具有廣泛的應用。

更多的例子和詳細的開發指南，請參考 eunomia-bpf 的官方文檔：<https://github.com/eunomia-bpf/eunomia-bpf>

如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。
