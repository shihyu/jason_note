# eBPF 入門開發實踐教程十一：在 eBPF 中使用 libbpf 開發用戶態程序並跟蹤 exec() 和 exit() 系統調用

eBPF (Extended Berkeley Packet Filter) 是 Linux 內核上的一個強大的網絡和性能分析工具。它允許開發者在內核運行時動態加載、更新和運行用戶定義的代碼。

在本教程中，我們將瞭解內核態和用戶態的 eBPF 程序是如何協同工作的。我們還將學習如何使用原生的 libbpf 開發用戶態程序，將 eBPF 應用打包為可執行文件，實現跨內核版本分發。

## libbpf 庫，以及為什麼需要使用它

libbpf 是一個 C 語言庫，伴隨內核版本分發，用於輔助 eBPF 程序的加載和運行。它提供了用於與 eBPF 系統交互的一組 C API，使開發者能夠更輕鬆地編寫用戶態程序來加載和管理 eBPF 程序。這些用戶態程序通常用於分析、監控或優化系統性能。

使用 libbpf 庫有以下優勢：

- 它簡化了 eBPF 程序的加載、更新和運行過程。
- 它提供了一組易於使用的 API，使開發者能夠專注於編寫核心邏輯，而不是處理底層細節。
- 它能夠確保與內核中的 eBPF 子系統的兼容性，降低了維護成本。

同時，libbpf 和 BTF（BPF Type Format）都是 eBPF 生態系統的重要組成部分。它們各自在實現跨內核版本兼容方面發揮著關鍵作用。BTF（BPF Type Format）是一種元數據格式，用於描述 eBPF 程序中的類型信息。BTF 的主要目的是提供一種結構化的方式，以描述內核中的數據結構，以便 eBPF 程序可以更輕鬆地訪問和操作它們。

BTF 在實現跨內核版本兼容方面的關鍵作用如下：

- BTF 允許 eBPF 程序訪問內核數據結構的詳細類型信息，而無需對特定內核版本進行硬編碼。這使得 eBPF 程序可以適應不同版本的內核，從而實現跨內核版本兼容。
- 通過使用 BPF CO-RE（Compile Once, Run Everywhere）技術，eBPF 程序可以利用 BTF 在編譯時解析內核數據結構的類型信息，進而生成可以在不同內核版本上運行的 eBPF 程序。

結合 libbpf 和 BTF，eBPF 程序可以在各種不同版本的內核上運行，而無需為每個內核版本單獨編譯。這極大地提高了 eBPF 生態系統的可移植性和兼容性，降低了開發和維護的難度。

## 什麼是 bootstrap

Bootstrap 是一個使用 libbpf 的完整應用，它利用 eBPF 程序來跟蹤內核中的 exec() 系統調用（通過 SEC("tp/sched/sched_process_exec") handle_exec BPF 程序），這主要對應於新進程的創建（不包括 fork() 部分）。此外，它還跟蹤進程的 exit() 系統調用（通過 SEC("tp/sched/sched_process_exit") handle_exit BPF 程序），以瞭解每個進程何時退出。

這兩個 BPF 程序共同工作，允許捕獲關於新進程的有趣信息，例如二進制文件的文件名，以及測量進程的生命週期，並在進程結束時收集有趣的統計信息，例如退出代碼或消耗的資源量等。這是深入瞭解內核內部並觀察事物如何真正運作的良好起點。

Bootstrap 還使用 argp API（libc 的一部分）進行命令行參數解析，使得用戶可以通過命令行選項配置應用行為。這種方式提供了靈活性，讓用戶能夠根據實際需求自定義程序行為。雖然這些功能使用 eunomia-bpf 工具也可以實現，但是這裡我們使用 libbpf 可以在用戶態提供更高的可擴展性，不過也帶來了不少額外的複雜度。

## Bootstrap

Bootstrap 分為兩個部分：內核態和用戶態。內核態部分是一個 eBPF 程序，它跟蹤 exec() 和 exit() 系統調用。用戶態部分是一個 C 語言程序，它使用 libbpf 庫來加載和運行內核態程序，並處理從內核態程序收集的數據。

### 內核態 eBPF 程序 bootstrap.bpf.c

```c
// SPDX-License-Identifier: GPL-2.0 OR BSD-3-Clause
/* Copyright (c) 2020 Facebook */
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "bootstrap.h"

char LICENSE[] SEC("license") = "Dual BSD/GPL";

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 8192);
    __type(key, pid_t);
    __type(value, u64);
} exec_start SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} rb SEC(".maps");

const volatile unsigned long long min_duration_ns = 0;

SEC("tp/sched/sched_process_exec")
int handle_exec(struct trace_event_raw_sched_process_exec *ctx)
{
    struct task_struct *task;
    unsigned fname_off;
    struct event *e;
    pid_t pid;
    u64 ts;

    /* remember time exec() was executed for this PID */
    pid = bpf_get_current_pid_tgid() >> 32;
    ts = bpf_ktime_get_ns();
    bpf_map_update_elem(&exec_start, &pid, &ts, BPF_ANY);

    /* don't emit exec events when minimum duration is specified */
    if (min_duration_ns)
        return 0;

    /* reserve sample from BPF ringbuf */
    e = bpf_ringbuf_reserve(&rb, sizeof(*e), 0);
    if (!e)
        return 0;

    /* fill out the sample with data */
    task = (struct task_struct *)bpf_get_current_task();

    e->exit_event = false;
    e->pid = pid;
    e->ppid = BPF_CORE_READ(task, real_parent, tgid);
    bpf_get_current_comm(&e->comm, sizeof(e->comm));

    fname_off = ctx->__data_loc_filename & 0xFFFF;
    bpf_probe_read_str(&e->filename, sizeof(e->filename), (void *)ctx + fname_off);

    /* successfully submit it to user-space for post-processing */
    bpf_ringbuf_submit(e, 0);
    return 0;
}

SEC("tp/sched/sched_process_exit")
int handle_exit(struct trace_event_raw_sched_process_template* ctx)
{
    struct task_struct *task;
    struct event *e;
    pid_t pid, tid;
    u64 id, ts, *start_ts, duration_ns = 0;
    
    /* get PID and TID of exiting thread/process */
    id = bpf_get_current_pid_tgid();
    pid = id >> 32;
    tid = (u32)id;

    /* ignore thread exits */
    if (pid != tid)
        return 0;

    /* if we recorded start of the process, calculate lifetime duration */
    start_ts = bpf_map_lookup_elem(&exec_start, &pid);
    if (start_ts)
        duration_ns = bpf_ktime_get_ns() - *start_ts;
    else if (min_duration_ns)
        return 0;
    bpf_map_delete_elem(&exec_start, &pid);

    /* if process didn't live long enough, return early */
    if (min_duration_ns && duration_ns < min_duration_ns)
        return 0;

    /* reserve sample from BPF ringbuf */
    e = bpf_ringbuf_reserve(&rb, sizeof(*e), 0);
    if (!e)
        return 0;

    /* fill out the sample with data */
    task = (struct task_struct *)bpf_get_current_task();

    e->exit_event = true;
    e->duration_ns = duration_ns;
    e->pid = pid;
    e->ppid = BPF_CORE_READ(task, real_parent, tgid);
    e->exit_code = (BPF_CORE_READ(task, exit_code) >> 8) & 0xff;
    bpf_get_current_comm(&e->comm, sizeof(e->comm));

    /* send data to user-space for post-processing */
    bpf_ringbuf_submit(e, 0);
    return 0;
}
```

這段代碼是一個內核態 eBPF 程序（bootstrap.bpf.c），主要用於跟蹤 exec() 和 exit() 系統調用。它通過 eBPF 程序捕獲進程的創建和退出事件，並將相關信息發送到用戶態程序進行處理。下面是對代碼的詳細解釋。

首先，我們引入所需的頭文件，定義 eBPF 程序的許可證以及兩個 eBPF maps：exec_start 和 rb。exec_start 是一個哈希類型的 eBPF map，用於存儲進程開始執行時的時間戳。rb 是一個環形緩衝區類型的 eBPF map，用於存儲捕獲的事件數據，並將其發送到用戶態程序。

```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>
#include "bootstrap.h"

char LICENSE[] SEC("license") = "Dual BSD/GPL";

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 8192);
    __type(key, pid_t);
    __type(value, u64);
} exec_start SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} rb SEC(".maps");

const volatile unsigned long long min_duration_ns = 0;
```

接下來，我們定義了一個名為 handle_exec 的 eBPF 程序，它會在進程執行 exec() 系統調用時觸發。首先，我們從當前進程中獲取 PID，記錄進程開始執行的時間戳，然後將其存儲在 exec_start map 中。

```c
SEC("tp/sched/sched_process_exec")
int handle_exec(struct trace_event_raw_sched_process_exec *ctx)
{
    // ...
    pid = bpf_get_current_pid_tgid() >> 32;
    ts = bpf_ktime_get_ns();
    bpf_map_update_elem(&exec_start, &pid, &ts, BPF_ANY);

    // ...
}
```

然後，我們從環形緩衝區 map rb 中預留一個事件結構，並填充相關數據，如進程 ID、父進程 ID、進程名等。之後，我們將這些數據發送到用戶態程序進行處理。

```c
    // reserve sample from BPF ringbuf
    e = bpf_ringbuf_reserve(&rb, sizeof(*e), 0);
    if (!e)
        return 0;

    // fill out the sample with data
    task = (struct task_struct *)bpf_get_current_task();

    e->exit_event = false;
    e->pid = pid;
    e->ppid = BPF_CORE_READ(task, real_parent, tgid);
    bpf_get_current_comm(&e->comm, sizeof(e->comm));

    fname_off = ctx->__data_loc_filename & 0xFFFF;
    bpf_probe_read_str(&e->filename, sizeof(e->filename), (void *)ctx + fname_off);

    // successfully submit it to user-space for post-processing
    bpf_ringbuf_submit(e, 0);
    return 0;
```

最後，我們定義了一個名為 handle_exit 的 eBPF 程序，它會在進程執行 exit() 系統調用時觸發。首先，我們從當前進程中獲取 PID 和 TID（線程 ID）。如果 PID 和 TID 不相等，說明這是一個線程退出，我們將忽略此事件。

```c
SEC("tp/sched/sched_process_exit")
int handle_exit(struct trace_event_raw_sched_process_template* ctx)
{
    // ...
    id = bpf_get_current_pid_tgid();
    pid = id >> 32;
    tid = (u32)id;

    /* ignore thread exits */
    if (pid != tid)
        return 0;

    // ...
}
```

接著，我們查找之前存儲在 exec_start map 中的進程開始執行的時間戳。如果找到了時間戳，我們將計算進程的生命週期（持續時間），然後從 exec_start map 中刪除該記錄。如果未找到時間戳且指定了最小持續時間，則直接返回。

```c
    // if we recorded start of the process, calculate lifetime duration
    start_ts = bpf_map_lookup_elem(&exec_start, &pid);
    if (start_ts)
        duration_ns = bpf_ktime_get_ns() - *start_ts;
    else if (min_duration_ns)
        return 0;
    bpf_map_delete_elem(&exec_start, &pid);

    // if process didn't live long enough, return early
    if (min_duration_ns && duration_ns < min_duration_ns)
        return 0;
```

然後，我們從環形緩衝區 map rb 中預留一個事件結構，並填充相關數據，如進程 ID、父進程 ID、進程名、進程持續時間等。最後，我們將這些數據發送到用戶態程序進行處理。

```c
    /* reserve sample from BPF ringbuf */
    e = bpf_ringbuf_reserve(&rb, sizeof(*e), 0);
    if (!e)
        return 0;

    /* fill out the sample with data */
    task = (struct task_struct *)bpf_get_current_task();

    e->exit_event = true;
    e->duration_ns = duration_ns;
    e->pid = pid;
    e->ppid = BPF_CORE_READ(task, real_parent, tgid);
    e->exit_code = (BPF_CORE_READ(task, exit_code) >> 8) & 0xff;
    bpf_get_current_comm(&e->comm, sizeof(e->comm));

    /* send data to user-space for post-processing */
    bpf_ringbuf_submit(e, 0);
    return 0;
}
```

這樣，當進程執行 exec() 或 exit() 系統調用時，我們的 eBPF 程序會捕獲相應的事件，並將詳細信息發送到用戶態程序進行後續處理。這使得我們可以輕鬆地監控進程的創建和退出，並獲取有關進程的詳細信息。

除此之外，在 bootstrap.h 中，我們還定義了和用戶態交互的數據結構：

```c
/* SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause) */
/* Copyright (c) 2020 Facebook */
#ifndef __BOOTSTRAP_H
#define __BOOTSTRAP_H

#define TASK_COMM_LEN 16
#define MAX_FILENAME_LEN 127

struct event {
    int pid;
    int ppid;
    unsigned exit_code;
    unsigned long long duration_ns;
    char comm[TASK_COMM_LEN];
    char filename[MAX_FILENAME_LEN];
    bool exit_event;
};

#endif /* __BOOTSTRAP_H */
```

### 用戶態，bootstrap.c

```c
// SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause)
/* Copyright (c) 2020 Facebook */
#include <argp.h>
#include <signal.h>
#include <stdio.h>
#include <time.h>
#include <sys/resource.h>
#include <bpf/libbpf.h>
#include "bootstrap.h"
#include "bootstrap.skel.h"

static struct env {
    bool verbose;
    long min_duration_ms;
} env;

const char *argp_program_version = "bootstrap 0.0";
const char *argp_program_bug_address = "<bpf@vger.kernel.org>";
const char argp_program_doc[] =
"BPF bootstrap demo application.\n"
"\n"
"It traces process start and exits and shows associated \n"
"information (filename, process duration, PID and PPID, etc).\n"
"\n"
"USAGE: ./bootstrap [-d <min-duration-ms>] [-v]\n";

static const struct argp_option opts[] = {
    { "verbose", 'v', NULL, 0, "Verbose debug output" },
    { "duration", 'd', "DURATION-MS", 0, "Minimum process duration (ms) to report" },
    {},
};

static error_t parse_arg(int key, char *arg, struct argp_state *state)
{
    switch (key) {
    case 'v':
        env.verbose = true;
        break;
    case 'd':
        errno = 0;
        env.min_duration_ms = strtol(arg, NULL, 10);
        if (errno || env.min_duration_ms <= 0) {
            fprintf(stderr, "Invalid duration: %s\n", arg);
            argp_usage(state);
        }
        break;
    case ARGP_KEY_ARG:
        argp_usage(state);
        break;
    default:
        return ARGP_ERR_UNKNOWN;
    }
    return 0;
}

static const struct argp argp = {
    .options = opts,
    .parser = parse_arg,
    .doc = argp_program_doc,
};

static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args)
{
    if (level == LIBBPF_DEBUG && !env.verbose)
        return 0;
    return vfprintf(stderr, format, args);
}

static volatile bool exiting = false;

static void sig_handler(int sig)
{
    exiting = true;
}

static int handle_event(void *ctx, void *data, size_t data_sz)
{
    const struct event *e = data;
    struct tm *tm;
    char ts[32];
    time_t t;

    time(&t);
    tm = localtime(&t);
    strftime(ts, sizeof(ts), "%H:%M:%S", tm);

    if (e->exit_event) {
        printf("%-8s %-5s %-16s %-7d %-7d [%u]",
               ts, "EXIT", e->comm, e->pid, e->ppid, e->exit_code);
        if (e->duration_ns)
            printf(" (%llums)", e->duration_ns / 1000000);
        printf("\n");
    } else {
        printf("%-8s %-5s %-16s %-7d %-7d %s\n",
               ts, "EXEC", e->comm, e->pid, e->ppid, e->filename);
    }

    return 0;
}

int main(int argc, char **argv)
{
    struct ring_buffer *rb = NULL;
    struct bootstrap_bpf *skel;
    int err;

    /* Parse command line arguments */
    err = argp_parse(&argp, argc, argv, 0, NULL, NULL);
    if (err)
        return err;

    /* Set up libbpf errors and debug info callback */
    libbpf_set_print(libbpf_print_fn);

    /* Cleaner handling of Ctrl-C */
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    /* Load and verify BPF application */
    skel = bootstrap_bpf__open();
    if (!skel) {
        fprintf(stderr, "Failed to open and load BPF skeleton\n");
        return 1;
    }

    /* Parameterize BPF code with minimum duration parameter */
    skel->rodata->min_duration_ns = env.min_duration_ms * 1000000ULL;

    /* Load & verify BPF programs */
    err = bootstrap_bpf__load(skel);
    if (err) {
        fprintf(stderr, "Failed to load and verify BPF skeleton\n");
        goto cleanup;
    }

    /* Attach tracepoints */
    err = bootstrap_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "Failed to attach BPF skeleton\n");
        goto cleanup;
    }

    /* Set up ring buffer polling */
    rb = ring_buffer__new(bpf_map__fd(skel->maps.rb), handle_event, NULL, NULL);
    if (!rb) {
        err = -1;
        fprintf(stderr, "Failed to create ring buffer\n");
        goto cleanup;
    }

    /* Process events */
    printf("%-8s %-5s %-16s %-7s %-7s %s\n",
           "TIME", "EVENT", "COMM", "PID", "PPID", "FILENAME/EXIT CODE");
    while (!exiting) {
        err = ring_buffer__poll(rb, 100 /* timeout, ms */);
        /* Ctrl-C will cause -EINTR */
        if (err == -EINTR) {
            err = 0;
            break;
        }
        if (err < 0) {
            printf("Error polling perf buffer: %d\n", err);
            break;
        }
    }

cleanup:
    /* Clean up */
    ring_buffer__free(rb);
    bootstrap_bpf__destroy(skel);

    return err < 0 ? -err : 0;
}
```

這個用戶態程序主要用於加載、驗證、附加 eBPF 程序，以及接收 eBPF 程序收集的事件數據，並將其打印出來。我們將分析一些關鍵部分。

首先，我們定義了一個 env 結構，用於存儲命令行參數：

```c
static struct env {
    bool verbose;
    long min_duration_ms;
} env;
```

接下來，我們使用 argp 庫來解析命令行參數：

```c
static const struct argp_option opts[] = {
    { "verbose", 'v', NULL, 0, "Verbose debug output" },
    { "duration", 'd', "DURATION-MS", 0, "Minimum process duration (ms) to report" },
    {},
};

static error_t parse_arg(int key, char *arg, struct argp_state *state)
{
    // ...
}

static const struct argp argp = {
    .options = opts,
    .parser = parse_arg,
    .doc = argp_program_doc,
};
```

main() 函數中，首先解析命令行參數，然後設置 libbpf 的打印回調函數 libbpf_print_fn，以便在需要時輸出調試信息：

```c
err = argp_parse(&argp, argc, argv, 0, NULL, NULL);
if (err)
    return err;

libbpf_set_print(libbpf_print_fn);
```

接下來，我們打開 eBPF 腳手架（skeleton）文件，將最小持續時間參數傳遞給 eBPF 程序，並加載和附加 eBPF 程序：

```c
skel = bootstrap_bpf__open();
if (!skel) {
    fprintf(stderr, "Failed to open and load BPF skeleton\n");
    return 1;
}

skel->rodata->min_duration_ns = env.min_duration_ms * 1000000ULL;

err = bootstrap_bpf__load(skel);
if (err) {
    fprintf(stderr, "Failed to load and verify BPF skeleton\n");
    goto cleanup;
}

err = bootstrap_bpf__attach(skel);
if (err) {
    fprintf(stderr, "Failed to attach BPF skeleton\n");
    goto cleanup;
}
```

然後，我們創建一個環形緩衝區（ring buffer），用於接收 eBPF 程序發送的事件數據：

```c
rb = ring_buffer__new(bpf_map__fd(skel->maps.rb), handle_event, NULL, NULL);
if (!rb) {
    err = -1;
    fprintf(stderr, "Failed to create ring buffer\n");
    goto cleanup;
}
```

handle_event() 函數會處理從 eBPF 程序收到的事件。根據事件類型（進程執行或退出），它會提取並打印事件信息，如時間戳、進程名、進程 ID、父進程 ID、文件名或退出代碼等。

最後，我們使用 ring_buffer__poll() 函數輪詢環形緩衝區，處理收到的事件數據：

```c
while (!exiting) {
    err = ring_buffer__poll(rb, 100 /* timeout, ms */);
    // ...
}
```

當程序收到 SIGINT 或 SIGTERM 信號時，它會最後完成清理、退出操作，關閉和卸載 eBPF 程序：

```c
cleanup:
 /* Clean up */
 ring_buffer__free(rb);
 bootstrap_bpf__destroy(skel);

 return err < 0 ? -err : 0;
}
```

## 安裝依賴

構建示例需要 clang、libelf 和 zlib。包名在不同的發行版中可能會有所不同。

在 Ubuntu/Debian 上，你需要執行以下命令：

```shell
sudo apt install clang libelf1 libelf-dev zlib1g-dev
```

在 CentOS/Fedora 上，你需要執行以下命令：

```shell
sudo dnf install clang elfutils-libelf elfutils-libelf-devel zlib-devel
```

## 編譯運行

編譯運行上述代碼：

```console
$ git submodule update --init --recursive
$ make
  BPF      .output/bootstrap.bpf.o
  GEN-SKEL .output/bootstrap.skel.h
  CC       .output/bootstrap.o
  BINARY   bootstrap
$ sudo ./bootstrap 
[sudo] password for yunwei: 
TIME     EVENT COMM             PID     PPID    FILENAME/EXIT CODE
03:16:41 EXEC  sh               110688  80168   /bin/sh
03:16:41 EXEC  which            110689  110688  /usr/bin/which
03:16:41 EXIT  which            110689  110688  [0] (0ms)
03:16:41 EXIT  sh               110688  80168   [0] (0ms)
03:16:41 EXEC  sh               110690  80168   /bin/sh
03:16:41 EXEC  ps               110691  110690  /usr/bin/ps
03:16:41 EXIT  ps               110691  110690  [0] (49ms)
03:16:41 EXIT  sh               110690  80168   [0] (51ms)
```

## 總結

通過這個實例，我們瞭解瞭如何將 eBPF 程序與用戶態程序結合使用。這種結合為開發者提供了一個強大的工具集，可以實現跨內核和用戶空間的高效數據收集和處理。通過使用 eBPF 和 libbpf，您可以構建更高效、可擴展和安全的監控和性能分析工具。

如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。
