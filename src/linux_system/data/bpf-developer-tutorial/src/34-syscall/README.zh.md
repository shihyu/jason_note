# eBPF 開發實踐：使用 eBPF 修改系統調用參數

eBPF（擴展的伯克利數據包過濾器）是 Linux 內核中的一個強大功能，可以在無需更改內核源代碼或重啟內核的情況下，運行、加載和更新用戶定義的代碼。這種功能讓 eBPF 在網絡和系統性能分析、數據包過濾、安全策略等方面有了廣泛的應用。

本教程介紹瞭如何使用 eBPF 修改正在進行的系統調用參數。這種技術可以用作安全審計、系統監視、或甚至惡意行為。然而需要特別注意，篡改系統調用參數可能對系統的穩定性和安全性帶來負面影響，因此必須謹慎使用。實現這個功能需要使用到 eBPF 的 `bpf_probe_write_user` 功能，它可以修改用戶空間的內存，因此能用來修改系統調用參數，在內核讀取用戶空間內存之前，將其修改為我們想要的值。

本文的完整代碼可以在 <https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/34-syscall/> 找到。

## 修改 open 系統調用的文件名

此功能用於修改 `openat` 系統調用的參數，讓它打開一個不同的文件。這個功能可能可以用於：

1. **文件訪問審計**：在對法律合規性和數據安全性有嚴格要求的環境中，審計員可能需要記錄所有對敏感文件的訪問行為。通過修改 `openat` 系統調用參數，可以將所有嘗試訪問某個敏感文件的行為重定向到一個備份文件或者日誌文件。
2. **安全沙盒**：在開發早期階段，可能希望監控應用程序嘗試打開的文件。通過更改 `openat` 調用，可以讓應用在一個安全的沙盒環境中運行，所有文件操作都被重定向到一個隔離的文件系統路徑。
3. **敏感數據保護**：對於存儲有敏感信息的文件，例如配置文件中包含有數據庫密碼，一個基於 eBPF 的系統可以將這些調用重定向到一個加密的或暫存的位置，以增強數據安全性。

如果該技術被惡意軟件利用，攻擊者可以重定向文件操作，導致數據洩漏或者破壞數據完整性。例如，程序寫入日誌文件時，攻擊者可能將數據重定向到控制的文件中，干擾審計跟蹤。

內核態代碼（部分，完整內容請參考 Github bpf-developer-tutorial）：

```c
SEC("tracepoint/syscalls/sys_enter_openat")
int tracepoint__syscalls__sys_enter_openat(struct trace_event_raw_sys_enter *ctx)
{
    u64 pid = bpf_get_current_pid_tgid() >> 32;
    /* use kernel terminology here for tgid/pid: */
    if (target_pid && pid != target_pid) {
        return 0;
    }
    /* store arg info for later lookup */
    // since we can manually specify the attach process in userspace,
    // we don't need to check the process allowed here

    struct args_t args = {};
    args.fname = (const char *)ctx->args[1];
    args.flags = (int)ctx->args[2];
    if (rewrite) {
        bpf_probe_write_user((char*)ctx->args[1], "hijacked", 9);
    }
    bpf_map_update_elem(&start, &pid, &args, 0);
    return 0;
}
```

分析內核態代碼：

- `bpf_get_current_pid_tgid()` 獲取當前進程ID。
- 如果指定了 `target_pid` 並且不匹配當前進程ID，函數直接返回。
- 我們創建一個 `args_t` 結構來存儲文件名和標誌。
- 使用 `bpf_probe_write_user` 修改用戶空間內存中的文件名為 "hijacked"。

eunomia-bpf 是一個開源的 eBPF 動態加載運行時和開發工具鏈，它的目的是簡化 eBPF 程序的開發、構建、分發、運行。可以參考 <https://github.com/eunomia-bpf/eunomia-bpf> 或 <https://eunomia.dev/tutorials/1-helloworld/> 下載和安裝 ecc 編譯工具鏈和 ecli 運行時。我們使用 eunomia-bpf 編譯運行這個例子。

編譯：

```bash
./ecc open_modify.bpf.c open_modify.h
```

使用 make 構建一個簡單的 victim 程序，用來測試：

```c
int main()
{
    char filename[100] = "my_test.txt";
    // print pid
    int pid = getpid();
    std::cout << "current pid: " << pid << std::endl;
    system("echo \"hello\" > my_test.txt");
    system("echo \"world\" >> hijacked");
    while (true) {
        std::cout << "Opening my_test.txt" << std::endl;

        int fd = open(filename, O_RDONLY);
        assert(fd != -1);

        std::cout << "test.txt opened, fd=" << fd << std::endl;
        usleep(1000 * 300);
        // print the file content
        char buf[100] = {0};
        int ret = read(fd, buf, 5);
        std::cout << "read " << ret << " bytes: " << buf << std::endl;
        std::cout << "Closing test.txt..." << std::endl;
        close(fd);
        std::cout << "test.txt closed" << std::endl;
    }
    return 0;
}
```

測試代碼編譯並運行:

```sh
$ ./victim
test.txt opened, fd=3
read 5 bytes: hello
Closing test.txt...
test.txt closed
```

可以使用以下命令指定應修改其 `openat` 系統調用參數的目標進程ID：

```bash
sudo ./ecli run package.json --rewrite --target_pid=$(pidof victim)
```

然後就會發現輸出變成了 world，可以看到我們原先想要打開 "my_test.txt" 文件，但是實際上被劫持打開了 hijacked 文件：

```console
test.txt opened, fd=3
read 5 bytes: hello
Closing test.txt...
test.txt closed
Opening my_test.txt
test.txt opened, fd=3
read 5 bytes: world
Closing test.txt...
test.txt closed
Opening my_test.txt
test.txt opened, fd=3
read 5 bytes: world
```

包含測試用例的完整代碼可以在 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 找到。

## 修改 bash execve 的進程名稱

這段功能用於當 `execve` 系統調用進行時修改執行程序名稱。在一些審計或監控場景，這可能用於記錄特定進程的行為或修改其行為。然而，此類篡改可能會造成混淆，使得用戶或管理員難以確定系統實際執行的程序是什麼。最嚴重的風險是，如果惡意用戶能夠控制 eBPF 程序，他們可以將合法的系統命令重定向到惡意軟件，造成嚴重的安全威脅。

```c
SEC("tp/syscalls/sys_enter_execve")
int handle_execve_enter(struct trace_event_raw_sys_enter *ctx)
{
    size_t pid_tgid = bpf_get_current_pid_tgid();
    // Check if we're a process of interest
    if (target_ppid != 0) {
        struct task_struct *task = (struct task_struct *)bpf_get_current_task();
        int ppid = BPF_CORE_READ(task, real_parent, tgid);
        if (ppid != target_ppid) {
            return 0;
        }
    }

    // Read in program from first arg of execve
    char prog_name[TASK_COMM_LEN];
    char prog_name_orig[TASK_COMM_LEN];
    __builtin_memset(prog_name, '\x00', TASK_COMM_LEN);
    bpf_probe_read_user(&prog_name, TASK_COMM_LEN, (void*)ctx->args[0]);
    bpf_probe_read_user(&prog_name_orig, TASK_COMM_LEN, (void*)ctx->args[0]);
    prog_name[TASK_COMM_LEN-1] = '\x00';
    bpf_printk("[EXECVE_HIJACK] %s\n", prog_name);

    // Program can't be less than out two-char name
    if (prog_name[1] == '\x00') {
        bpf_printk("[EXECVE_HIJACK] program name too small\n");
        return 0;
    }

    // Attempt to overwrite with hijacked binary path
    prog_name[0] = '/';
    prog_name[1] = 'a';
    for (int i = 2; i < TASK_COMM_LEN ; i++) {
        prog_name[i] = '\x00';
    }
    long ret = bpf_probe_write_user((void*)ctx->args[0], &prog_name, 3);

    // Send an event
    struct event *e;
    e = bpf_ringbuf_reserve(&rb, sizeof(*e), 0);
    if (e) {
        e->success = (ret == 0);
        e->pid = (pid_tgid >> 32);
        for (int i = 0; i < TASK_COMM_LEN; i++) {
            e->comm[i] = prog_name_orig[i];
        }
        bpf_ringbuf_submit(e, 0);
    }

    return 0;
}
```

分析內核態代碼：

- 執行 `bpf_get_current_pid_tgid` 獲取當前進程ID和線程組ID。
- 如果設置了 `target_ppid`，代碼會檢查當前進程的父進程ID是否匹配。
- 讀取第一個 `execve` 參數到 `prog_name`，這通常是將要執行的程序的路徑。
- 通過 `bpf_probe_write_user` 重寫這個參數，使得系統實際執行的是一個不同的程序。

這種做法的風險在於它可以被用於劫持軟件的行為，導致系統運行惡意代碼。同樣也可以使用 ecc 和 ecli 編譯運行：

```bash
./ecc exechijack.bpf.c exechijack.h
sudo ./ecli run package.json
```

## 總結

eBPF 提供了強大的能力來實現對正在運行的系統進行實時監控和干預。在合適的監管和安全策略配合下，這可以帶來諸多好處，如安全增強、性能優化和運維便利。然而，這項技術的使用必須非常小心，因為錯誤的操作或濫用可能會對系統的正常運作造成破壞或者引發嚴重的安全事件。實踐中，應確保只有授權用戶和程序能夠部署和管理 eBPF 程序，並且應當在隔離的測試環境中驗證這些eBPF程序的行為，在充分理解其影響後才能將其應用到生產環境中。

您還可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。
