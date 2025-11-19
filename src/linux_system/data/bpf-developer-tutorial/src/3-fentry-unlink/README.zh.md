# eBPF 入門開發實踐教程三：在 eBPF 中使用 fentry 監測捕獲 unlink 系統調用

eBPF (Extended Berkeley Packet Filter) 是 Linux 內核上的一個強大的網絡和性能分析工具。它允許開發者在內核運行時動態加載、更新和運行用戶定義的代碼。

本文是 eBPF 入門開發實踐教程的第三篇，在 eBPF 中使用 fentry 捕獲 unlink 系統調用。

## Fentry

fentry（function entry）和 fexit（function exit）是 eBPF（擴展的伯克利包過濾器）中的兩種探針類型，用於在 Linux 內核函數的入口和退出處進行跟蹤。它們允許開發者在內核函數執行的特定階段收集信息、修改參數或觀察返回值。這種跟蹤和監控功能在性能分析、故障排查和安全分析等場景中非常有用。

與 kprobes 相比，fentry 和 fexit 程序有更高的性能和可用性。在這個例子中，我們可以直接訪問函數的指針參數，就像在普通的 C 代碼中一樣，而不需要使用各種讀取幫助程序。fexit 和 kretprobe 程序最大的區別在於，fexit 程序可以訪問函數的輸入參數和返回值，而 kretprobe 只能訪問返回值。從 5.5 內核開始，fentry 和 fexit 對 eBPF 程序可用。

> arm64 內核版本需要 6.0
>
> 參考 learning eBPF 文檔：
>
> 從內核版本 5.5 開始（適用於 x86 處理器；*BPF trampoline* 支持在 Linux 6.0 之前不適用於 ARM 處理器），引入了一種更高效的機制來跟蹤進入和退出內核函數的方式以及 *BPF trampoline* 的概念。如果您正在使用足夠新的內核，fentry/fexit 現在是首選的跟蹤進入或退出內核函數的方法。
> 
> 參考：https://kernelnewbies.org/Linux_6.0#ARM





```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

char LICENSE[] SEC("license") = "Dual BSD/GPL";

SEC("fentry/do_unlinkat")
int BPF_PROG(do_unlinkat, int dfd, struct filename *name)
{
    pid_t pid;

    pid = bpf_get_current_pid_tgid() >> 32;
    bpf_printk("fentry: pid = %d, filename = %s\n", pid, name->name);
    return 0;
}

SEC("fexit/do_unlinkat")
int BPF_PROG(do_unlinkat_exit, int dfd, struct filename *name, long ret)
{
    pid_t pid;

    pid = bpf_get_current_pid_tgid() >> 32;
    bpf_printk("fexit: pid = %d, filename = %s, ret = %ld\n", pid, name->name, ret);
    return 0;
}
```

這段程序是用 C 語言編寫的 eBPF（擴展的伯克利包過濾器）程序，它使用 BPF 的 fentry 和 fexit 探針來跟蹤 Linux 內核函數 `do_unlinkat`。在這個教程中，我們將以這段程序作為示例，讓您學會如何在 eBPF 中使用 fentry 監測捕獲 unlink 系統調用。

程序包含以下部分：

1. 包含頭文件：包括 vmlinux.h（用於訪問內核數據結構）、bpf/bpf_helpers.h（包含eBPF幫助函數）、bpf/bpf_tracing.h（用於eBPF跟蹤相關功能）。
2. 定義許可證：這裡定義了一個名為 `LICENSE` 的字符數組，包含許可證信息“Dual BSD/GPL”。
3. 定義 fentry 探針：我們定義了一個名為 `BPF_PROG(do_unlinkat)` 的 fentry 探針，該探針在 `do_unlinkat` 函數的入口處被觸發。這個探針獲取當前進程的 PID（進程ID）並將其與文件名一起打印到內核日誌。
4. 定義 fexit 探針：我們還定義了一個名為 `BPF_PROG(do_unlinkat_exit)` 的 fexit 探針，該探針在 `do_unlinkat` 函數的退出處被觸發。與 fentry 探針類似，這個探針也會獲取當前進程的 PID 並將其與文件名和返回值一起打印到內核日誌。

通過這個示例，您可以學習如何在 eBPF 中使用 fentry 和 fexit 探針來監控和捕獲內核函數調用，例如在本教程中的 unlink 系統調用。

eunomia-bpf 是一個結合 Wasm 的開源 eBPF 動態加載運行時和開發工具鏈，它的目的是簡化 eBPF 程序的開發、構建、分發、運行。可以參考 <https://github.com/eunomia-bpf/eunomia-bpf> 下載和安裝 ecc 編譯工具鏈和 ecli 運行時。我們使用 eunomia-bpf 編譯運行這個例子。

編譯運行上述代碼：

```console
$ ecc fentry-link.bpf.c
Compiling bpf object...
Packing ebpf object and config into package.json...
$ sudo ecli run package.json
Runing eBPF program...
```

在另外一個窗口中：

```shell
touch test_file
rm test_file
touch test_file2
rm test_file2
```

運行這段程序後，可以通過查看 `/sys/kernel/debug/tracing/trace_pipe` 文件來查看 eBPF 程序的輸出：

```console
$ sudo cat /sys/kernel/debug/tracing/trace_pipe
              rm-9290    [004] d..2  4637.798698: bpf_trace_printk: fentry: pid = 9290, filename = test_file
              rm-9290    [004] d..2  4637.798843: bpf_trace_printk: fexit: pid = 9290, filename = test_file, ret = 0
              rm-9290    [004] d..2  4637.798698: bpf_trace_printk: fentry: pid = 9290, filename = test_file2
              rm-9290    [004] d..2  4637.798843: bpf_trace_printk: fexit: pid = 9290, filename = test_file2, ret = 0
```

## 總結

這段程序是一個 eBPF 程序，通過使用 fentry 和 fexit 捕獲 `do_unlinkat` 和 `do_unlinkat_exit` 函數，並通過使用 `bpf_get_current_pid_tgid` 和 `bpf_printk` 函數獲取調用 do_unlinkat 的進程的 ID、文件名和返回值，並在內核日誌中打印出來。

編譯這個程序可以使用 ecc 工具，運行時可以使用 ecli 命令，並通過查看 `/sys/kernel/debug/tracing/trace_pipe` 文件查看 eBPF 程序的輸出。更多的例子和詳細的開發指南，請參考 eunomia-bpf 的官方文檔：<https://github.com/eunomia-bpf/eunomia-bpf>

如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。
