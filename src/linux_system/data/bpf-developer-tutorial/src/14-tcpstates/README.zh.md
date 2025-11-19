# eBPF入門實踐教程十四：記錄 TCP 連接狀態與 TCP RTT

eBPF (擴展的伯克利數據包過濾器) 是一項強大的網絡和性能分析工具，被廣泛應用在 Linux 內核上。eBPF 使得開發者能夠動態地加載、更新和運行用戶定義的代碼，而無需重啟內核或更改內核源代碼。

在我們的 eBPF 入門實踐教程系列的這一篇，我們將介紹兩個示例程序：`tcpstates` 和 `tcprtt`。`tcpstates` 用於記錄 TCP 連接的狀態變化，而 `tcprtt` 則用於記錄 TCP 的往返時間 (RTT, Round-Trip Time)。

## `tcprtt` 與 `tcpstates`

網絡質量在當前的互聯網環境中至關重要。影響網絡質量的因素有許多，包括硬件、網絡環境、軟件編程的質量等。為了幫助用戶更好地定位網絡問題，我們引入了 `tcprtt` 這個工具。`tcprtt` 可以監控 TCP 鏈接的往返時間，從而評估網絡質量，幫助用戶找出可能的問題所在。

當 TCP 鏈接建立時，`tcprtt` 會自動根據當前系統的狀況，選擇合適的執行函數。在執行函數中，`tcprtt` 會收集 TCP 鏈接的各項基本信息，如源地址、目標地址、源端口、目標端口、耗時等，並將這些信息更新到直方圖型的 BPF map 中。運行結束後，`tcprtt` 會通過用戶態代碼，將收集的信息以圖形化的方式展示給用戶。

`tcpstates` 則是一個專門用來追蹤和打印 TCP 連接狀態變化的工具。它可以顯示 TCP 連接在每個狀態中的停留時長，單位為毫秒。例如，對於一個單獨的 TCP 會話，`tcpstates` 可以打印出類似以下的輸出：

```sh
SKADDR           C-PID C-COMM     LADDR           LPORT RADDR           RPORT OLDSTATE    -> NEWSTATE    MS
ffff9fd7e8192000 22384 curl       100.66.100.185  0     52.33.159.26    80    CLOSE       -> SYN_SENT    0.000
ffff9fd7e8192000 0     swapper/5  100.66.100.185  63446 52.33.159.26    80    SYN_SENT    -> ESTABLISHED 1.373
ffff9fd7e8192000 22384 curl       100.66.100.185  63446 52.33.159.26    80    ESTABLISHED -> FIN_WAIT1   176.042
ffff9fd7e8192000 0     swapper/5  100.66.100.185  63446 52.33.159.26    80    FIN_WAIT1   -> FIN_WAIT2   0.536
ffff9fd7e8192000 0     swapper/5  100.66.100.185  63446 52.33.159.26    80    FIN_WAIT2   -> CLOSE       0.006
```

以上輸出中，最多的時間被花在了 ESTABLISHED 狀態，也就是連接已經建立並在傳輸數據的狀態，這個狀態到 FIN_WAIT1 狀態（開始關閉連接的狀態）的轉變過程中耗費了 176.042 毫秒。

在我們接下來的教程中，我們會更深入地探討這兩個工具，解釋它們的實現原理，希望這些內容對你在使用 eBPF 進行網絡和性能分析方面的工作有所幫助。

## tcpstate

由於篇幅所限，這裡我們主要討論和分析對應的 eBPF 內核態代碼實現。以下是 tcpstate 的 eBPF 代碼：

```c
const volatile bool filter_by_sport = false;
const volatile bool filter_by_dport = false;
const volatile short target_family = 0;

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_ENTRIES);
    __type(key, __u16);
    __type(value, __u16);
} sports SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_ENTRIES);
    __type(key, __u16);
    __type(value, __u16);
} dports SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_ENTRIES);
    __type(key, struct sock *);
    __type(value, __u64);
} timestamps SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(key_size, sizeof(__u32));
    __uint(value_size, sizeof(__u32));
} events SEC(".maps");

SEC("tracepoint/sock/inet_sock_set_state")
int handle_set_state(struct trace_event_raw_inet_sock_set_state *ctx)
{
    struct sock *sk = (struct sock *)ctx->skaddr;
    __u16 family = ctx->family;
    __u16 sport = ctx->sport;
    __u16 dport = ctx->dport;
    __u64 *tsp, delta_us, ts;
    struct event event = {};

    if (ctx->protocol != IPPROTO_TCP)
        return 0;

    if (target_family && target_family != family)
        return 0;

    if (filter_by_sport && !bpf_map_lookup_elem(&sports, &sport))
        return 0;

    if (filter_by_dport && !bpf_map_lookup_elem(&dports, &dport))
        return 0;

    tsp = bpf_map_lookup_elem(&timestamps, &sk);
    ts = bpf_ktime_get_ns();
    if (!tsp)
        delta_us = 0;
    else
        delta_us = (ts - *tsp) / 1000;

    event.skaddr = (__u64)sk;
    event.ts_us = ts / 1000;
    event.delta_us = delta_us;
    event.pid = bpf_get_current_pid_tgid() >> 32;
    event.oldstate = ctx->oldstate;
    event.newstate = ctx->newstate;
    event.family = family;
    event.sport = sport;
    event.dport = dport;
    bpf_get_current_comm(&event.task, sizeof(event.task));

    if (family == AF_INET) {
        bpf_probe_read_kernel(&event.saddr, sizeof(event.saddr), &sk->__sk_common.skc_rcv_saddr);
        bpf_probe_read_kernel(&event.daddr, sizeof(event.daddr), &sk->__sk_common.skc_daddr);
    } else { /* family == AF_INET6 */
        bpf_probe_read_kernel(&event.saddr, sizeof(event.saddr), &sk->__sk_common.skc_v6_rcv_saddr.in6_u.u6_addr32);
        bpf_probe_read_kernel(&event.daddr, sizeof(event.daddr), &sk->__sk_common.skc_v6_daddr.in6_u.u6_addr32);
    }

    bpf_perf_event_output(ctx, &events, BPF_F_CURRENT_CPU, &event, sizeof(event));

    if (ctx->newstate == TCP_CLOSE)
        bpf_map_delete_elem(&timestamps, &sk);
    else
        bpf_map_update_elem(&timestamps, &sk, &ts, BPF_ANY);

    return 0;
}
```

`tcpstates`主要依賴於 eBPF 的 Tracepoints 來捕獲 TCP 連接的狀態變化，從而跟蹤 TCP 連接在每個狀態下的停留時間。

### 定義 BPF Maps

在`tcpstates`程序中，首先定義了幾個 BPF Maps，它們是 eBPF 程序和用戶態程序之間交互的主要方式。`sports`和`dports`分別用於存儲源端口和目標端口，用於過濾 TCP 連接；`timestamps`用於存儲每個 TCP 連接的時間戳，以計算每個狀態的停留時間；`events`則是一個 perf_event 類型的 map，用於將事件數據發送到用戶態。

### 追蹤 TCP 連接狀態變化

程序定義了一個名為`handle_set_state`的函數，該函數是一個 tracepoint 類型的程序，它將被掛載到`sock/inet_sock_set_state`這個內核 tracepoint 上。每當 TCP 連接狀態發生變化時，這個 tracepoint 就會被觸發，然後執行`handle_set_state`函數。

在`handle_set_state`函數中，首先通過一系列條件判斷確定是否需要處理當前的 TCP 連接，然後從`timestamps`map 中獲取當前連接的上一個時間戳，然後計算出停留在當前狀態的時間。接著，程序將收集到的數據放入一個 event 結構體中，並通過`bpf_perf_event_output`函數將該 event 發送到用戶態。

### 更新時間戳

最後，根據 TCP 連接的新狀態，程序將進行不同的操作：如果新狀態為 TCP_CLOSE，表示連接已關閉，程序將從`timestamps`map 中刪除該連接的時間戳；否則，程序將更新該連接的時間戳。

用戶態的部分主要是通過 libbpf 來加載 eBPF 程序，然後通過 perf_event 來接收內核中的事件數據：

```c
static void handle_event(void* ctx, int cpu, void* data, __u32 data_sz) {
    char ts[32], saddr[26], daddr[26];
    struct event* e = data;
    struct tm* tm;
    int family;
    time_t t;

    if (emit_timestamp) {
        time(&t);
        tm = localtime(&t);
        strftime(ts, sizeof(ts), "%H:%M:%S", tm);
        printf("%8s ", ts);
    }

    inet_ntop(e->family, &e->saddr, saddr, sizeof(saddr));
    inet_ntop(e->family, &e->daddr, daddr, sizeof(daddr));
    if (wide_output) {
        family = e->family == AF_INET ? 4 : 6;
        printf(
            "%-16llx %-7d %-16s %-2d %-26s %-5d %-26s %-5d %-11s -> %-11s "
            "%.3f\n",
            e->skaddr, e->pid, e->task, family, saddr, e->sport, daddr,
            e->dport, tcp_states[e->oldstate], tcp_states[e->newstate],
            (double)e->delta_us / 1000);
    } else {
        printf(
            "%-16llx %-7d %-10.10s %-15s %-5d %-15s %-5d %-11s -> %-11s %.3f\n",
            e->skaddr, e->pid, e->task, saddr, e->sport, daddr, e->dport,
            tcp_states[e->oldstate], tcp_states[e->newstate],
            (double)e->delta_us / 1000);
    }
}
```

`handle_event`就是這樣一個回調函數，它會被 perf_event 調用，每當內核有新的事件到達時，它就會處理這些事件。

在`handle_event`函數中，我們首先通過`inet_ntop`函數將二進制的 IP 地址轉換成人類可讀的格式，然後根據是否需要輸出寬格式，分別打印不同的信息。這些信息包括了事件的時間戳、源 IP 地址、源端口、目標 IP 地址、目標端口、舊狀態、新狀態以及在舊狀態停留的時間。

這樣，用戶就可以清晰地看到 TCP 連接狀態的變化，以及每個狀態的停留時間，從而幫助他們診斷網絡問題。

總結起來，用戶態部分的處理主要涉及到了以下幾個步驟：

1. 使用 libbpf 加載並運行 eBPF 程序。
2. 設置回調函數來接收內核發送的事件。
3. 處理接收到的事件，將其轉換成人類可讀的格式並打印。

以上就是`tcpstates`程序用戶態部分的主要實現邏輯。通過這一章的學習，你應該已經對如何在用戶態處理內核事件有了更深入的理解。在下一章中，我們將介紹更多關於如何使用 eBPF 進行網絡監控的知識。

### tcprtt

在本章節中，我們將分析`tcprtt` eBPF 程序的內核態代碼。`tcprtt`是一個用於測量 TCP 往返時間(Round Trip Time, RTT)的程序，它將 RTT 的信息統計到一個 histogram 中。

```c

/// @sample {"interval": 1000, "type" : "log2_hist"}
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_ENTRIES);
    __type(key, u64);
    __type(value, struct hist);
} hists SEC(".maps");

static struct hist zero;

SEC("fentry/tcp_rcv_established")
int BPF_PROG(tcp_rcv, struct sock *sk)
{
    const struct inet_sock *inet = (struct inet_sock *)(sk);
    struct tcp_sock *ts;
    struct hist *histp;
    u64 key, slot;
    u32 srtt;

    if (targ_sport && targ_sport != inet->inet_sport)
        return 0;
    if (targ_dport && targ_dport != sk->__sk_common.skc_dport)
        return 0;
    if (targ_saddr && targ_saddr != inet->inet_saddr)
        return 0;
    if (targ_daddr && targ_daddr != sk->__sk_common.skc_daddr)
        return 0;

    if (targ_laddr_hist)
        key = inet->inet_saddr;
    else if (targ_raddr_hist)
        key = inet->sk.__sk_common.skc_daddr;
    else
        key = 0;
    histp = bpf_map_lookup_or_try_init(&hists, &key, &zero);
    if (!histp)
        return 0;
    ts = (struct tcp_sock *)(sk);
    srtt = BPF_CORE_READ(ts, srtt_us) >> 3;
    if (targ_ms)
        srtt /= 1000U;
    slot = log2l(srtt);
    if (slot >= MAX_SLOTS)
        slot = MAX_SLOTS - 1;
    __sync_fetch_and_add(&histp->slots[slot], 1);
    if (targ_show_ext) {
        __sync_fetch_and_add(&histp->latency, srtt);
        __sync_fetch_and_add(&histp->cnt, 1);
    }
    return 0;
}
```

首先，我們定義了一個 hash 類型的 eBPF map，名為`hists`，它用來存儲 RTT 的統計信息。在這個 map 中，鍵是 64 位整數，值是一個`hist`結構，這個結構包含了一個數組，用來存儲不同 RTT 區間的數量。

接著，我們定義了一個 eBPF 程序，名為`tcp_rcv`，這個程序會在每次內核中處理 TCP 收包的時候被調用。在這個程序中，我們首先根據過濾條件（源/目標 IP 地址和端口）對 TCP 連接進行過濾。如果滿足條件，我們會根據設置的參數選擇相應的 key（源 IP 或者目標 IP 或者 0），然後在`hists` map 中查找或者初始化對應的 histogram。

接下來，我們讀取 TCP 連接的`srtt_us`字段，這個字段表示了平滑的 RTT 值，單位是微秒。然後我們將這個 RTT 值轉換為對數形式，並將其作為 slot 存儲到 histogram 中。

如果設置了`show_ext`參數，我們還會將 RTT 值和計數器累加到 histogram 的`latency`和`cnt`字段中。

通過以上的處理，我們可以對每個 TCP 連接的 RTT 進行統計和分析，從而更好地理解網絡的性能狀況。

總結起來，`tcprtt` eBPF 程序的主要邏輯包括以下幾個步驟：

1. 根據過濾條件對 TCP 連接進行過濾。
2. 在`hists` map 中查找或者初始化對應的 histogram。
3. 讀取 TCP 連接的`srtt_us`字段，並將其轉換為對數形式，存儲到 histogram 中。
4. 如果設置了`show_ext`參數，將 RTT 值和計數器累加到 histogram 的`latency`和`cnt`字段中。

tcprtt 掛載到了內核態的 tcp_rcv_established 函數上：

```c
void tcp_rcv_established(struct sock *sk, struct sk_buff *skb);
```

這個函數是在內核中處理TCP接收數據的主要函數，主要在TCP連接處於`ESTABLISHED`狀態時被調用。這個函數的處理邏輯包括一個快速路徑和一個慢速路徑。快速路徑在以下幾種情況下會被禁用：

- 我們宣佈了一個零窗口 - 零窗口探測只能在慢速路徑中正確處理。
- 收到了亂序的數據包。
- 期待接收緊急數據。
- 沒有剩餘的緩衝區空間。
- 接收到了意外的TCP標誌/窗口值/頭部長度（通過檢查TCP頭部與預設標誌進行檢測）。
- 數據在兩個方向上都在傳輸。快速路徑只支持純發送者或純接收者（這意味著序列號或確認值必須保持不變）。
- 接收到了意外的TCP選項。

當這些條件不滿足時，它會進入一個標準的接收處理過程，這個過程遵循RFC793來處理所有情況。前三種情況可以通過正確的預設標誌設置來保證，剩下的情況則需要內聯檢查。當一切都正常時，快速處理過程會在`tcp_data_queue`函數中被開啟。

## 編譯運行

對於 tcpstates，可以通過以下命令編譯和運行 libbpf 應用：

```console
$ make
...
  BPF      .output/tcpstates.bpf.o
  GEN-SKEL .output/tcpstates.skel.h
  CC       .output/tcpstates.o
  BINARY   tcpstates
$ sudo ./tcpstates 
SKADDR           PID     COMM       LADDR           LPORT RADDR           RPORT OLDSTATE    -> NEWSTATE    MS
ffff9bf61bb62bc0 164978  node       192.168.88.15   0     52.178.17.2     443   CLOSE       -> SYN_SENT    0.000
ffff9bf61bb62bc0 0       swapper/0  192.168.88.15   41596 52.178.17.2     443   SYN_SENT    -> ESTABLISHED 225.794
ffff9bf61bb62bc0 0       swapper/0  192.168.88.15   41596 52.178.17.2     443   ESTABLISHED -> CLOSE_WAIT  901.454
ffff9bf61bb62bc0 164978  node       192.168.88.15   41596 52.178.17.2     443   CLOSE_WAIT  -> LAST_ACK    0.793
ffff9bf61bb62bc0 164978  node       192.168.88.15   41596 52.178.17.2     443   LAST_ACK    -> LAST_ACK    0.086
ffff9bf61bb62bc0 228759  kworker/u6 192.168.88.15   41596 52.178.17.2     443   LAST_ACK    -> CLOSE       0.193
ffff9bf6d8ee88c0 229832  redis-serv 0.0.0.0         6379  0.0.0.0         0     CLOSE       -> LISTEN      0.000
ffff9bf6d8ee88c0 229832  redis-serv 0.0.0.0         6379  0.0.0.0         0     LISTEN      -> CLOSE       1.763
ffff9bf7109d6900 88750   node       127.0.0.1       39755 127.0.0.1       50966 ESTABLISHED -> FIN_WAIT1   0.000
```

對於 tcprtt，我們可以使用 eunomia-bpf 編譯運行這個例子：

Compile:

```shell
docker run -it -v `pwd`/:/src/ ghcr.io/eunomia-bpf/ecc-`uname -m`:latest
```

或者

```console
$ ecc tcprtt.bpf.c tcprtt.h
Compiling bpf object...
Generating export types...
Packing ebpf object and config into package.json...
```

運行：

```console
$ sudo ecli run package.json -h
A simple eBPF program


Usage: package.json [OPTIONS]

Options:
      --verbose                  Whether to show libbpf debug information
      --targ_laddr_hist          Set value of `bool` variable targ_laddr_hist
      --targ_raddr_hist          Set value of `bool` variable targ_raddr_hist
      --targ_show_ext            Set value of `bool` variable targ_show_ext
      --targ_sport <targ_sport>  Set value of `__u16` variable targ_sport
      --targ_dport <targ_dport>  Set value of `__u16` variable targ_dport
      --targ_saddr <targ_saddr>  Set value of `__u32` variable targ_saddr
      --targ_daddr <targ_daddr>  Set value of `__u32` variable targ_daddr
      --targ_ms                  Set value of `bool` variable targ_ms
  -h, --help                     Print help
  -V, --version                  Print version

Built with eunomia-bpf framework.
See https://github.com/eunomia-bpf/eunomia-bpf for more information.

$ sudo ecli run package.json
key =  0
latency = 0
cnt = 0

     (unit)              : count    distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 0        |                                        |
       256 -> 511        : 0        |                                        |
       512 -> 1023       : 4        |********************                    |
      1024 -> 2047       : 1        |*****                                   |
      2048 -> 4095       : 0        |                                        |
      4096 -> 8191       : 8        |****************************************|

key =  0
latency = 0
cnt = 0

     (unit)              : count    distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 0        |                                        |
       256 -> 511        : 0        |                                        |
       512 -> 1023       : 11       |***************************             |
      1024 -> 2047       : 1        |**                                      |
      2048 -> 4095       : 0        |                                        |
      4096 -> 8191       : 16       |****************************************|
      8192 -> 16383      : 4        |**********                              |
```

完整源代碼：

- <https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/14-tcpstates>

參考資料：

- [tcpstates](https://github.com/iovisor/bcc/blob/master/tools/tcpstates_example.txt)
- [tcprtt](https://github.com/iovisor/bcc/blob/master/tools/tcprtt.py)
- [libbpf-tools/tcpstates](<https://github.com/iovisor/bcc/blob/master/libbpf-tools/tcpstates.bpf.c>)

## 總結

通過本篇 eBPF 入門實踐教程，我們學習瞭如何使用tcpstates和tcprtt這兩個 eBPF 示例程序，監控和分析 TCP 的連接狀態和往返時間。我們瞭解了tcpstates和tcprtt的工作原理和實現方式，包括如何使用 BPF map 存儲數據，如何在 eBPF 程序中獲取和處理 TCP 連接信息，以及如何在用戶態應用程序中解析和顯示 eBPF 程序收集的數據。

如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。接下來的教程將進一步探討 eBPF 的高級特性，我們會繼續分享更多有關 eBPF 開發實踐的內容。
