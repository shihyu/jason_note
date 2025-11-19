# eBPF 入門開發實踐教程五：在 eBPF 中使用  uprobe 捕獲 bash 的 readline 函數調用

eBPF (Extended Berkeley Packet Filter) 是 Linux 內核上的一個強大的網絡和性能分析工具，它允許開發者在內核運行時動態加載、更新和運行用戶定義的代碼。

本文是 eBPF 入門開發實踐教程的第五篇，主要介紹如何使用 uprobe 捕獲 bash 的 readline 函數調用。

## 什麼是uprobe

uprobe是一種用戶空間探針，uprobe探針允許在用戶空間程序中動態插樁，插樁位置包括：函數入口、特定偏移處，以及函數返回處。當我們定義uprobe時，內核會在附加的指令上創建快速斷點指令（x86機器上為int3指令），當程序執行到該指令時，內核將觸發事件，程序陷入到內核態，並以回調函數的方式調用探針函數，執行完探針函數再返回到用戶態繼續執行後序的指令。

uprobe基於文件，當一個二進制文件中的一個函數被跟蹤時，所有使用到這個文件的進程都會被插樁，包括那些尚未啟動的進程，這樣就可以在全系統範圍內跟蹤系統調用。

uprobe適用於在用戶態去解析一些內核態探針無法解析的流量，例如http2流量（報文header被編碼，內核無法解碼），https流量（加密流量，內核無法解密）。具體可以參考 [eBPF 實踐教程：使用 uprobe 捕獲多種庫的 SSL/TLS 明文數據](../30-sslsniff/README.md) 中的例子。

Uprobe 在內核態 eBPF 運行時，也可能產生比較大的性能開銷，這時候也可以考慮使用用戶態 eBPF 運行時，例如  [bpftime](https://github.com/eunomia-bpf/bpftime)。bpftime 是一個基於 LLVM JIT/AOT 的用戶態 eBPF 運行時，它可以在用戶態運行 eBPF 程序，和內核態的 eBPF 兼容，避免了內核態和用戶態之間的上下文切換，從而提高了 eBPF 程序的執行效率。對於 uprobe 而言，bpftime 的性能開銷比 kernel 小一個數量級。

## 使用 uprobe 捕獲 bash 的 readline 函數調用

uprobe 是一種用於捕獲用戶空間函數調用的 eBPF 的探針，我們可以通過它來捕獲用戶空間程序調用的系統函數。

例如，我們可以使用 uprobe 來捕獲 bash 的 readline 函數調用，從而獲取用戶在 bash 中輸入的命令行。示例代碼如下：

```c
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#define TASK_COMM_LEN 16
#define MAX_LINE_SIZE 80

/* Format of u[ret]probe section definition supporting auto-attach:
 * u[ret]probe/binary:function[+offset]
 *
 * binary can be an absolute/relative path or a filename; the latter is resolved to a
 * full binary path via bpf_program__attach_uprobe_opts.
 *
 * Specifying uprobe+ ensures we carry out strict matching; either "uprobe" must be
 * specified (and auto-attach is not possible) or the above format is specified for
 * auto-attach.
 */
SEC("uretprobe//bin/bash:readline")
int BPF_KRETPROBE(printret, const void *ret)
{
 char str[MAX_LINE_SIZE];
 char comm[TASK_COMM_LEN];
 u32 pid;

 if (!ret)
  return 0;

 bpf_get_current_comm(&comm, sizeof(comm));

 pid = bpf_get_current_pid_tgid() >> 32;
 bpf_probe_read_user_str(str, sizeof(str), ret);

 bpf_printk("PID %d (%s) read: %s ", pid, comm, str);

 return 0;
};

char LICENSE[] SEC("license") = "GPL";
```

這段代碼的作用是在 bash 的 readline 函數返回時執行指定的 BPF_KRETPROBE 函數，即 printret 函數。

在 printret 函數中，我們首先獲取了調用 readline 函數的進程的進程名稱和進程 ID，然後通過 bpf_probe_read_user_str 函數讀取了用戶輸入的命令行字符串，最後通過 bpf_printk 函數打印出進程 ID、進程名稱和輸入的命令行字符串。

除此之外，我們還需要通過 SEC 宏來定義 uprobe 探針，並使用 BPF_KRETPROBE 宏來定義探針函數。

在 SEC 宏中，我們需要指定 uprobe 的類型、要捕獲的二進制文件的路徑和要捕獲的函數名稱。例如，上面的代碼中的 SEC 宏的定義如下：

```c
SEC("uretprobe//bin/bash:readline")
```

這表示我們要捕獲的是 /bin/bash 二進制文件中的 readline 函數。

接下來，我們需要使用 BPF_KRETPROBE 宏來定義探針函數，例如：

```c
BPF_KRETPROBE(printret, const void *ret)
```

這裡的 printret 是探針函數的名稱，const void *ret 是探針函數的參數，它代表被捕獲的函數的返回值。

然後，我們使用了 bpf_get_current_comm 函數獲取當前任務的名稱，並將其存儲在 comm 數組中。

```c
 bpf_get_current_comm(&comm, sizeof(comm));
```

使用 bpf_get_current_pid_tgid 函數獲取當前進程的 PID，並將其存儲在 pid 變量中。

```c
 pid = bpf_get_current_pid_tgid() >> 32;
```

使用 bpf_probe_read_user_str 函數從用戶空間讀取 readline 函數的返回值，並將其存儲在 str 數組中。

```c
 bpf_probe_read_user_str(str, sizeof(str), ret);
```

最後使用 bpf_printk 函數輸出 PID、任務名稱和用戶輸入的字符串。

```c
 bpf_printk("PID %d (%s) read: %s ", pid, comm, str);
```

eunomia-bpf 是一個結合 Wasm 的開源 eBPF 動態加載運行時和開發工具鏈，它的目的是簡化 eBPF 程序的開發、構建、分發、運行。可以參考 <https://github.com/eunomia-bpf/eunomia-bpf> 下載和安裝 ecc 編譯工具鏈和 ecli 運行時。我們使用 eunomia-bpf 編譯運行這個例子。

編譯運行上述代碼：

```console
$ ecc bashreadline.bpf.c
Compiling bpf object...
Packing ebpf object and config into package.json...
$ sudo ecli run package.json
Runing eBPF program...
```

運行這段程序後，可以通過查看 /sys/kernel/debug/tracing/trace_pipe 文件來查看 eBPF 程序的輸出：

```console
$ sudo cat /sys/kernel/debug/tracing/trace_pipe
            bash-32969   [000] d..31 64001.375748: bpf_trace_printk: PID 32969 (bash) read: fff 
            bash-32969   [000] d..31 64002.056951: bpf_trace_printk: PID 32969 (bash) read: fff
```

可以看到，我們成功的捕獲了 bash 的 readline 函數調用，並獲取了用戶在 bash 中輸入的命令行。

## 總結

在上述代碼中，我們使用了 SEC 宏來定義了一個 uprobe 探針，它指定了要捕獲的用戶空間程序 (bin/bash) 和要捕獲的函數 (readline)。此外，我們還使用了 BPF_KRETPROBE 宏來定義了一個用於處理 readline 函數返回值的回調函數 (printret)。該函數可以獲取到 readline 函數的返回值，並將其打印到內核日誌中。通過這樣的方式，我們就可以使用 eBPF 來捕獲 bash 的 readline 函數調用，並獲取用戶在 bash 中輸入的命令行。

更多的例子和詳細的開發指南，請參考 eunomia-bpf 的官方文檔：<https://github.com/eunomia-bpf/eunomia-bpf>

如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。
