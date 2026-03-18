# bpftrace 入門：認識 eBPF 的四種追蹤機制

[`bpftrace`](https://github.com/bpftrace/bpftrace) 是一個讓我們能快速實踐 eBPF 追蹤的工具。它本身是一種高階 eBPF 追蹤語言，具備以下特點：

- 語法簡潔，類似 Linux 上常見的 `awk`，容易上手
- 可即時執行，腳本會自動編譯成 eBPF bytecode，不需要手動編譯
- 支援多種追蹤機制，包含 Tracepoints、Kprobes、Uprobes、USDT
- 內建聚合函式，例如 `count()`、`hist()`、`avg()` 等統計功能

如果不使用 `bpftrace`，又不想直接撰寫 bytecode，那麼以 C 搭配 `libbpf` 函式庫，也是常見的 eBPF 開發方式之一。相較之下，`bpftrace` 語法更精簡、開發速度更快，特別適合用於快速分析與除錯。本文也會以 `bpftrace` 作為 eBPF 操作範例。

## 安裝 bpftrace

詳細的環境需求與安裝步驟，可以參考 [官方安裝文件](https://github.com/bpftrace/bpftrace/blob/master/INSTALL.md)。本文以 Ubuntu 24.04 作為示範環境：

```bash
sudo apt-get install -y bpftrace
```

安裝完成後，就可以先用最簡單的指令確認 `bpftrace` 是否正常運作：

```bash
sudo bpftrace -e 'BEGIN { printf("Hello, bpftrace!\n"); }'
```

執行後，會看到 probe 被動態掛載，並印出 `Hello, bpftrace!`：

```text
Attaching 1 probe...
Hello, bpftrace!
```

## bpftrace 語法參考

`bpftrace` 提供相當完整的語法與內建函式。若想進一步查詢特定語法，可參考：

- [Reference Guide](https://github.com/bpftrace/bpftrace/blob/master/docs/reference_guide.md)

此外，`bpftrace` 本身也提供實用的查詢指令：

```bash
# 查看所有可用的內建函式和變數
man bpftrace

# 列出所有 probe 類型
sudo bpftrace -l

# 查看特定 tracepoint 的參數
sudo bpftrace -lv tracepoint:syscalls:sys_enter_openat
```

## eBPF 的四種追蹤機制

eBPF 提供多種追蹤機制，讓我們能依不同情境選擇合適的追蹤方式：

![eBPF 的四種追蹤機制](images/bpftrace-tracing-mechanisms.png)

### 1. Kernel Tracepoint

Kernel Tracepoint 是核心開發者在程式碼中預先埋設的追蹤點。這些追蹤點允許 eBPF 程式掛載到特定的 kernel event，藉此捕獲相關資料，進行分析與監控。

我們也可以透過 `bpftrace` 找出核心中已存在的 tracepoint：

```bash
# 列出所有 tracepoints
sudo bpftrace -l 'tracepoint:*' | head

# 查看 syscalls 相關 tracepoints
sudo bpftrace -l 'tracepoint:syscalls:*' | head
```

### 2. USDT (User Statically Defined Tracing)

USDT 類似 Kernel Tracepoint，只是追蹤點是預先埋設在使用者空間程式中。例如 Python 就內建了一些 USDT probes，可用來追蹤函式呼叫、GC 事件等。

### 3. Kprobes (Kernel Probes)

即使核心內部函式沒有預先埋入 tracepoint，也可以透過 Kprobes，將 eBPF 動態掛載到幾乎任何 kernel 函式上。若要確認有哪些函式可被動態掛載，可執行：

```bash
sudo bpftrace -l 'kprobe:*tcp*' | head
```

這會列出可用於 Kprobes 追蹤的函式，例如：

```text
kprobe:__arm64_sys_getcpu
kprobe:__bpf_tcp_ca_init
kprobe:__bpf_tcp_ca_release
kprobe:__mptcp_check_push
kprobe:__mptcp_clean_una
kprobe:__mptcp_close
kprobe:__mptcp_close_ssk
kprobe:__mptcp_data_acked
kprobe:__mptcp_destroy_sock
kprobe:__mptcp_error_report
```

例如，我們可以把 Kprobe 掛載到 kernel 內部的 `tcp_connect` 函式上，以觀察比 syscall 層更深入的網路行為：

```bash
sudo bpftrace -e '
kprobe:tcp_connect {
    printf("%s (PID %d) initiated TCP connection\n", comm, pid);
}'
```

在另一個終端機使用 `telnet` 發起 TCP 連線後，eBPF 就能捕捉到相關資訊：

```text
Attaching 1 probe...
telnet (PID 2976) initiated TCP connection
```

### 4. Uprobes (User Probes)

Uprobes 與 Kprobes 類似，差別在於 Kprobes 掛載在 kernel space 的函式上，而 Uprobes 掛載在 user space 的函式上。因此，我們可以使用 Uprobes 追蹤應用程式或函式庫。

常見的應用場景包括：

- 追蹤資料庫查詢
- 追蹤 OpenSSL 加密函式，以進行 SSL/TLS 監控
- 追蹤 `malloc`、`free` 等函式，以進行記憶體分析

例如，我們可以使用 Uprobe 追蹤 Bash 的 `readline` 函式，觀察使用者輸入的完整指令：

```bash
sudo bpftrace -e '
uretprobe:/bin/bash:readline {
    printf("Command: %s\n", str(retval));
}'
```

當使用者在另一個終端機輸入指令時，Uprobe 便能成功捕捉：

```text
Attaching 1 probe...
Command: ls
Command: pwd
```

## 結語

透過 `bpftrace`，我們可以用簡潔的語法快速驗證想法，不需要自己寫 C，也不需要手動編譯。理解 eBPF 的各種追蹤機制後，就能根據不同場景選擇合適的方法，進一步分析系統行為。

下一篇可以接著探討如何把 `bpftrace` 收集到的資料轉換成 OTLP 格式，補上觀測資料輸出的最後一段流程。

## 參考資料

- [bpftrace](https://github.com/bpftrace/bpftrace)
- [eBPF 學習實踐系列（一）: 初識 eBPF](https://xiaodongq.github.io/2024/06/06/ebpf_learn/)
- [eBPF 學習實踐系列（六）: bpftrace 學習與使用](https://xiaodongq.github.io/2024/06/28/ebpf-bpftrace-learn/)
