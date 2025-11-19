# eBPF 入門開發實踐教程六：捕獲進程發送信號的系統調用集合，使用 hash map 保存狀態

eBPF (Extended Berkeley Packet Filter) 是 Linux 內核上的一個強大的網絡和性能分析工具，它允許開發者在內核運行時動態加載、更新和運行用戶定義的代碼。

本文是 eBPF 入門開發實踐教程的第六篇，主要介紹如何實現一個 eBPF 工具，捕獲進程發送信號的系統調用集合，使用 hash map 保存狀態。

## sigsnoop

示例代碼如下：

```c
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#define MAX_ENTRIES 10240
#define TASK_COMM_LEN 16

struct event {
 unsigned int pid;
 unsigned int tpid;
 int sig;
 int ret;
 char comm[TASK_COMM_LEN];
};

struct {
 __uint(type, BPF_MAP_TYPE_HASH);
 __uint(max_entries, MAX_ENTRIES);
 __type(key, __u32);
 __type(value, struct event);
} values SEC(".maps");


static int probe_entry(pid_t tpid, int sig)
{
 struct event event = {};
 __u64 pid_tgid;
 __u32 tid;

 pid_tgid = bpf_get_current_pid_tgid();
 tid = (__u32)pid_tgid;
 event.pid = pid_tgid >> 32;
 event.tpid = tpid;
 event.sig = sig;
 bpf_get_current_comm(event.comm, sizeof(event.comm));
 bpf_map_update_elem(&values, &tid, &event, BPF_ANY);
 return 0;
}

static int probe_exit(void *ctx, int ret)
{
 __u64 pid_tgid = bpf_get_current_pid_tgid();
 __u32 tid = (__u32)pid_tgid;
 struct event *eventp;

 eventp = bpf_map_lookup_elem(&values, &tid);
 if (!eventp)
  return 0;

 eventp->ret = ret;
 bpf_printk("PID %d (%s) sent signal %d ",
           eventp->pid, eventp->comm, eventp->sig);
 bpf_printk("to PID %d, ret = %d",
           eventp->tpid, ret);

cleanup:
 bpf_map_delete_elem(&values, &tid);
 return 0;
}

SEC("tracepoint/syscalls/sys_enter_kill")
int kill_entry(struct trace_event_raw_sys_enter *ctx)
{
 pid_t tpid = (pid_t)ctx->args[0];
 int sig = (int)ctx->args[1];

 return probe_entry(tpid, sig);
}

SEC("tracepoint/syscalls/sys_exit_kill")
int kill_exit(struct trace_event_raw_sys_exit *ctx)
{
 return probe_exit(ctx, ctx->ret);
}

char LICENSE[] SEC("license") = "Dual BSD/GPL";
```

上面的代碼定義了一個 eBPF 程序，用於捕獲進程發送信號的系統調用，包括 kill、tkill 和 tgkill。它通過使用 tracepoint 來捕獲系統調用的進入和退出事件，並在這些事件發生時執行指定的探針函數，例如 probe_entry 和 probe_exit。

在探針函數中，我們使用 bpf_map 存儲捕獲的事件信息，包括髮送信號的進程 ID、接收信號的進程 ID、信號值和進程的可執行文件名稱。在系統調用退出時，我們將獲取存儲在 bpf_map 中的事件信息，並使用 bpf_printk 打印進程 ID、進程名稱、發送的信號和系統調用的返回值。

最後，我們還需要使用 SEC 宏來定義探針，並指定要捕獲的系統調用的名稱，以及要執行的探針函數。

eunomia-bpf 是一個結合 Wasm 的開源 eBPF 動態加載運行時和開發工具鏈，它的目的是簡化 eBPF 程序的開發、構建、分發、運行。可以參考 <https://github.com/eunomia-bpf/eunomia-bpf> 下載和安裝 ecc 編譯工具鏈和 ecli 運行時。我們使用 eunomia-bpf 編譯運行這個例子。

編譯運行上述代碼：

```shell
docker run -it -v `pwd`/:/src/ ghcr.io/eunomia-bpf/ecc-`uname -m`:latest
```

或者

```console
$ ecc sigsnoop.bpf.c
Compiling bpf object...
Generating export types...
Packing ebpf object and config into package.json...
$ sudo ecli run package.json
Runing eBPF program...
```

運行這段程序後，可以通過查看 /sys/kernel/debug/tracing/trace_pipe 文件來查看 eBPF 程序的輸出：

```console
$ sudo cat /sys/kernel/debug/tracing/trace_pipe
    systemd-journal-363     [000] d...1   672.563868: bpf_trace_printk: PID 363 (systemd-journal) sent signal 0
     systemd-journal-363     [000] d...1   672.563869: bpf_trace_printk: to PID 1400, ret = 0
     systemd-journal-363     [000] d...1   672.563870: bpf_trace_printk: PID 363 (systemd-journal) sent signal 0
     systemd-journal-363     [000] d...1   672.563870: bpf_trace_printk: to PID 1527, ret = -3
```

## 總結

本文主要介紹如何實現一個 eBPF 工具，捕獲進程發送信號的系統調用集合，使用 hash map 保存狀態。使用 hash map 需要定義一個結構體：

```c
struct {
 __uint(type, BPF_MAP_TYPE_HASH);
 __uint(max_entries, MAX_ENTRIES);
 __type(key, __u32);
 __type(value, struct event);
} values SEC(".maps");
```

並使用一些對應的 API 進行訪問，例如 bpf_map_lookup_elem、bpf_map_update_elem、bpf_map_delete_elem 等。

更多的例子和詳細的開發指南，請參考 eunomia-bpf 的官方文檔：<https://github.com/eunomia-bpf/eunomia-bpf>

如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。
