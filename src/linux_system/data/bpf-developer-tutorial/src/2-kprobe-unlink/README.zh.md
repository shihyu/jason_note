# eBPF 入門開發實踐教程二：在 eBPF 中使用 kprobe 監測捕獲 unlink 系統調用

eBPF (Extended Berkeley Packet Filter) 是 Linux 內核上的一個強大的網絡和性能分析工具。它允許開發者在內核運行時動態加載、更新和運行用戶定義的代碼。

本文是 eBPF 入門開發實踐教程的第二篇，在 eBPF 中使用 kprobe 捕獲 unlink 系統調用。本文會先講解關於 kprobes 的基本概念和技術背景，然後介紹如何在 eBPF 中使用 kprobe 捕獲 unlink 系統調用。

## kprobes 技術背景

開發人員在內核或者模塊的調試過程中，往往會需要要知道其中的一些函數有無被調用、何時被調用、執行是否正確以及函數的入參和返回值是什麼等等。比較簡單的做法是在內核代碼對應的函數中添加日誌打印信息，但這種方式往往需要重新編譯內核或模塊，重新啟動設備之類的，操作較為複雜甚至可能會破壞原有的代碼執行過程。

而利用 kprobes 技術，用戶可以定義自己的回調函數，然後在內核或者模塊中幾乎所有的函數中（有些函數是不可探測的，例如kprobes自身的相關實現函數，後文會有詳細說明）動態地插入探測點，當內核執行流程執行到指定的探測函數時，會調用該回調函數，用戶即可收集所需的信息了，同時內核最後還會回到原本的正常執行流程。如果用戶已經收集足夠的信息，不再需要繼續探測，則同樣可以動態地移除探測點。因此 kprobes 技術具有對內核執行流程影響小和操作方便的優點。

kprobes 技術包括的3種探測手段分別時 kprobe、jprobe 和 kretprobe。首先 kprobe 是最基本的探測方式，是實現後兩種的基礎，它可以在任意的位置放置探測點（就連函數內部的某條指令處也可以），它提供了探測點的調用前、調用後和內存訪問出錯3種回調方式，分別是 `pre_handler`、`post_handler` 和 `fault_handler`，其中 `pre_handler` 函數將在被探測指令被執行前回調，`post_handler` 會在被探測指令執行完畢後回調（注意不是被探測函數），`fault_handler` 會在內存訪問出錯時被調用；jprobe 基於 kprobe 實現，它用於獲取被探測函數的入參值；最後 kretprobe 從名字中就可以看出其用途了，它同樣基於 kprobe 實現，用於獲取被探測函數的返回值。

kprobes 的技術原理並不僅僅包含純軟件的實現方案，它也需要硬件架構提供支持。其中涉及硬件架構相關的是 CPU 的異常處理和單步調試技術，前者用於讓程序的執行流程陷入到用戶註冊的回調函數中去，而後者則用於單步執行被探測點指令，因此並不是所有的架構均支持 kprobes。目前 kprobes 技術已經支持多種架構，包括 i386、x86_64、ppc64、ia64、sparc64、arm、ppc 和 mips（有些架構實現可能並不完全，具體可參考內核的 Documentation/kprobes.txt）。

kprobes 的特點與使用限制：

1. kprobes 允許在同一個被探測位置註冊多個 kprobe，但是目前 jprobe 卻不可以；同時也不允許以其他的 jprobe 回調函數和 kprobe 的 `post_handler` 回調函數作為被探測點。
2. 一般情況下，可以探測內核中的任何函數，包括中斷處理函數。不過在 kernel/kprobes.c 和 arch/*/kernel/kprobes.c 程序中用於實現 kprobes 自身的函數是不允許被探測的，另外還有`do_page_fault` 和 `notifier_call_chain`；
3. 如果以一個內聯函數為探測點，則 kprobes 可能無法保證對該函數的所有實例都註冊探測點。由於 gcc 可能會自動將某些函數優化為內聯函數，因此可能無法達到用戶預期的探測效果；
4. 一個探測點的回調函數可能會修改被探測函數的運行上下文，例如通過修改內核的數據結構或者保存與`struct pt_regs`結構體中的觸發探測器之前寄存器信息。因此 kprobes 可以被用來安裝 bug 修復代碼或者注入故障測試代碼；
5. kprobes 會避免在處理探測點函數時再次調用另一個探測點的回調函數，例如在`printk()`函數上註冊了探測點，而在它的回調函數中可能會再次調用`printk`函數，此時將不再觸發`printk`探測點的回調，僅僅是增加了`kprobe`結構體中`nmissed`字段的數值；
6. 在 kprobes 的註冊和註銷過程中不會使用 mutex 鎖和動態的申請內存；
7. kprobes 回調函數的運行期間是關閉內核搶佔的，同時也可能在關閉中斷的情況下執行，具體要視CPU架構而定。因此不論在何種情況下，在回調函數中不要調用會放棄 CPU 的函數（如信號量、mutex 鎖等）；
8. kretprobe 通過替換返回地址為預定義的 trampoline 的地址來實現，因此棧回溯和 gcc 內嵌函數`__builtin_return_address()`調用將返回 trampoline 的地址而不是真正的被探測函數的返回地址；
9. 如果一個函數的調用次數和返回次數不相等，則在類似這樣的函數上註冊 kretprobe 將可能不會達到預期的效果，例如`do_exit()`函數會存在問題，而`do_execve()`函數和`do_fork()`函數不會；
10. 當在進入和退出一個函數時，如果 CPU 運行在非當前任務所有的棧上，那麼往該函數上註冊 kretprobe 可能會導致不可預料的後果，因此，kprobes 不支持在 X86_64 的結構下為`__switch_to()`函數註冊 kretprobe，將直接返回`-EINVAL`。

## kprobe 示例

完整代碼如下：

```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

char LICENSE[] SEC("license") = "Dual BSD/GPL";

SEC("kprobe/do_unlinkat")
int BPF_KPROBE(do_unlinkat, int dfd, struct filename *name)
{
    pid_t pid;
    const char *filename;

    pid = bpf_get_current_pid_tgid() >> 32;
    filename = BPF_CORE_READ(name, name);
    bpf_printk("KPROBE ENTRY pid = %d, filename = %s\n", pid, filename);
    return 0;
}

SEC("kretprobe/do_unlinkat")
int BPF_KRETPROBE(do_unlinkat_exit, long ret)
{
    pid_t pid;

    pid = bpf_get_current_pid_tgid() >> 32;
    bpf_printk("KPROBE EXIT: pid = %d, ret = %ld\n", pid, ret);
    return 0;
}
```

這段代碼是一個簡單的 eBPF 程序，用於監測和捕獲在 Linux 內核中執行的 unlink 系統調用。unlink 系統調用的功能是刪除一個文件，這個 eBPF 程序通過使用 kprobe（內核探針）在`do_unlinkat`函數的入口和退出處放置鉤子，實現對該系統調用的跟蹤。

首先，我們導入必要的頭文件，如 vmlinux.h，bpf_helpers.h，bpf_tracing.h 和 bpf_core_read.h。接著，我們定義許可證，以允許程序在內核中運行。

```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

char LICENSE[] SEC("license") = "Dual BSD/GPL";
```

接下來，我們定義一個名為`BPF_KPROBE(do_unlinkat)`的 kprobe，當進入`do_unlinkat`函數時，它會被觸發。該函數接受兩個參數：`dfd`（文件描述符）和`name`（文件名結構體指針）。在這個 kprobe 中，我們獲取當前進程的 PID（進程標識符），然後讀取文件名。最後，我們使用`bpf_printk`函數在內核日誌中打印 PID 和文件名。

```c
SEC("kprobe/do_unlinkat")
int BPF_KPROBE(do_unlinkat, int dfd, struct filename *name)
{
    pid_t pid;
    const char *filename;

    pid = bpf_get_current_pid_tgid() >> 32;
    filename = BPF_CORE_READ(name, name);
    bpf_printk("KPROBE ENTRY pid = %d, filename = %s\n", pid, filename);
    return 0;
}
```

接下來，我們定義一個名為`BPF_KRETPROBE(do_unlinkat_exit)`的 kretprobe，當從`do_unlinkat`函數退出時，它會被觸發。這個 kretprobe 的目的是捕獲函數的返回值（ret）。我們再次獲取當前進程的 PID，並使用`bpf_printk`函數在內核日誌中打印 PID 和返回值。

```c
SEC("kretprobe/do_unlinkat")
int BPF_KRETPROBE(do_unlinkat_exit, long ret)
{
    pid_t pid;

    pid = bpf_get_current_pid_tgid() >> 32;
    bpf_printk("KPROBE EXIT: pid = %d, ret = %ld\n", pid, ret);
    return 0;
}
```

eunomia-bpf 是一個結合 Wasm 的開源 eBPF 動態加載運行時和開發工具鏈，它的目的是簡化 eBPF 程序的開發、構建、分發、運行。可以參考 <https://github.com/eunomia-bpf/eunomia-bpf> 下載和安裝 ecc 編譯工具鏈和 ecli 運行時。

要編譯這個程序，請使用 ecc 工具：

```console
$ ecc kprobe-link.bpf.c
Compiling bpf object...
Packing ebpf object and config into package.json...
```

然後運行：

```console
sudo ecli run package.json
```

在另外一個窗口中：

```shell
touch test1
rm test1
touch test2
rm test2
```

在 /sys/kernel/debug/tracing/trace_pipe 文件中，應該能看到類似下面的 kprobe 演示輸出：

```shell
$ sudo cat /sys/kernel/debug/tracing/trace_pipe
              rm-9346    [005] d..3  4710.951696: bpf_trace_printk: KPROBE ENTRY pid = 9346, filename = test1
              rm-9346    [005] d..4  4710.951819: bpf_trace_printk: KPROBE EXIT: ret = 0
              rm-9346    [005] d..3  4710.951852: bpf_trace_printk: KPROBE ENTRY pid = 9346, filename = test2
              rm-9346    [005] d..4  4710.951895: bpf_trace_printk: KPROBE EXIT: ret = 0
```

## 總結

通過本文的示例，我們學習瞭如何使用 eBPF 的 kprobe 和 kretprobe 捕獲 unlink 系統調用。更多的例子和詳細的開發指南，請參考 eunomia-bpf 的官方文檔：<https://github.com/eunomia-bpf/eunomia-bpf>

本文是 eBPF 入門開發實踐教程的第二篇。下一篇文章將介紹如何在 eBPF 中使用 fentry 監測捕獲 unlink 系統調用。

如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。
