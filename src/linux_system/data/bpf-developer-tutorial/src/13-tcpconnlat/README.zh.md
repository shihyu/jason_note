# eBPF入門開發實踐教程十三：統計 TCP 連接延時，並使用 libbpf 在用戶態處理數據

eBPF (Extended Berkeley Packet Filter) 是一項強大的網絡和性能分析工具，被應用在 Linux 內核上。eBPF 允許開發者動態加載、更新和運行用戶定義的代碼，而無需重啟內核或更改內核源代碼。

本文是 eBPF 入門開發實踐教程的第十三篇，主要介紹如何使用 eBPF 統計 TCP 連接延時，並使用 libbpf 在用戶態處理數據。

## 背景

在進行後端開發時，不論使用何種編程語言，我們都常常需要調用 MySQL、Redis 等數據庫，或執行一些 RPC 遠程調用，或者調用其他的 RESTful API。這些調用的底層，通常都是基於 TCP 協議進行的。原因是 TCP 協議具有可靠連接、錯誤重傳、擁塞控制等優點，因此在網絡傳輸層協議中，TCP 的應用廣泛程度超過了 UDP。然而，TCP 也有一些缺點，如建立連接的延時較長。因此，也出現了一些替代方案，例如 QUIC（Quick UDP Internet Connections，快速 UDP 網絡連接）。

分析 TCP 連接延時對網絡性能分析、優化以及故障排查都非常有用。

## tcpconnlat 工具概述

`tcpconnlat` 這個工具能夠跟蹤內核中執行活動 TCP 連接的函數（如通過 `connect()` 系統調用），並測量並顯示連接延時，即從發送 SYN 到收到響應包的時間。

### TCP 連接原理

TCP 連接的建立過程，常被稱為“三次握手”（Three-way Handshake）。以下是整個過程的步驟：

1. 客戶端向服務器發送 SYN 包：客戶端通過 `connect()` 系統調用發出 SYN。這涉及到本地的系統調用以及軟中斷的 CPU 時間開銷。
2. SYN 包傳送到服務器：這是一次網絡傳輸，涉及到的時間取決於網絡延遲。
3. 服務器處理 SYN 包：服務器內核通過軟中斷接收包，然後將其放入半連接隊列，併發送 SYN/ACK 響應。這主要涉及 CPU 時間開銷。
4. SYN/ACK 包傳送到客戶端：這是另一次網絡傳輸。
5. 客戶端處理 SYN/ACK：客戶端內核接收並處理 SYN/ACK 包，然後發送 ACK。這主要涉及軟中斷處理開銷。
6. ACK 包傳送到服務器：這是第三次網絡傳輸。
7. 服務器接收 ACK：服務器內核接收並處理 ACK，然後將對應的連接從半連接隊列移動到全連接隊列。這涉及到一次軟中斷的 CPU 開銷。
8. 喚醒服務器端用戶進程：被 `accept()` 系統調用阻塞的用戶進程被喚醒，然後從全連接隊列中取出來已經建立好的連接。這涉及一次上下文切換的CPU開銷。

完整的流程圖如下所示：

![tcpconnlat1](tcpconnlat1.png)

在客戶端視角，在正常情況下一次TCP連接總的耗時也就就大約是一次網絡RTT的耗時。但在某些情況下，可能會導致連接時的網絡傳輸耗時上漲、CPU處理開銷增加、甚至是連接失敗。這種時候在發現延時過長之後，就可以結合其他信息進行分析。

## tcpconnlat 的 eBPF 實現

為了理解 TCP 的連接建立過程，我們需要理解 Linux 內核在處理 TCP 連接時所使用的兩個隊列：

- 半連接隊列（SYN 隊列）：存儲那些正在進行三次握手操作的 TCP 連接，服務器收到 SYN 包後，會將該連接信息存儲在此隊列中。
- 全連接隊列（Accept 隊列）：存儲已經完成三次握手，等待應用程序調用 `accept()` 函數的 TCP 連接。服務器在收到 ACK 包後，會創建一個新的連接並將其添加到此隊列。

理解了這兩個隊列的用途，我們就可以開始探究 tcpconnlat 的具體實現。tcpconnlat 的實現可以分為內核態和用戶態兩個部分，其中包括了幾個主要的跟蹤點：`tcp_v4_connect`, `tcp_v6_connect` 和 `tcp_rcv_state_process`。

這些跟蹤點主要位於內核中的 TCP/IP 網絡棧。當執行相關的系統調用或內核函數時，這些跟蹤點會被激活，從而觸發 eBPF 程序的執行。這使我們能夠捕獲和測量 TCP 連接建立的整個過程。

讓我們先來看一下這些掛載點的源代碼：

```c
SEC("kprobe/tcp_v4_connect")
int BPF_KPROBE(tcp_v4_connect, struct sock *sk)
{
 return trace_connect(sk);
}

SEC("kprobe/tcp_v6_connect")
int BPF_KPROBE(tcp_v6_connect, struct sock *sk)
{
 return trace_connect(sk);
}

SEC("kprobe/tcp_rcv_state_process")
int BPF_KPROBE(tcp_rcv_state_process, struct sock *sk)
{
 return handle_tcp_rcv_state_process(ctx, sk);
}
```

這段代碼展示了三個內核探針（kprobe）的定義。`tcp_v4_connect` 和 `tcp_v6_connect` 在對應的 IPv4 和 IPv6 連接被初始化時被觸發，調用 `trace_connect()` 函數，而 `tcp_rcv_state_process` 在內核處理 TCP 連接狀態變化時被觸發，調用 `handle_tcp_rcv_state_process()` 函數。

接下來的部分將分為兩大塊：一部分是對這些掛載點內核態部分的分析，我們將解讀內核源代碼來詳細說明這些函數如何工作；另一部分是用戶態的分析，將關注 eBPF 程序如何收集這些掛載點的數據，以及如何與用戶態程序進行交互。

### tcp_v4_connect 函數解析

`tcp_v4_connect`函數是Linux內核處理TCP的IPv4連接請求的主要方式。當用戶態程序通過`socket`系統調用創建了一個套接字後，接著通過`connect`系統調用嘗試連接到遠程服務器，此時就會觸發`tcp_v4_connect`函數。

```c
/* This will initiate an outgoing connection. */
int tcp_v4_connect(struct sock *sk, struct sockaddr *uaddr, int addr_len)
{
  struct sockaddr_in *usin = (struct sockaddr_in *)uaddr;
  struct inet_timewait_death_row *tcp_death_row;
  struct inet_sock *inet = inet_sk(sk);
  struct tcp_sock *tp = tcp_sk(sk);
  struct ip_options_rcu *inet_opt;
  struct net *net = sock_net(sk);
  __be16 orig_sport, orig_dport;
  __be32 daddr, nexthop;
  struct flowi4 *fl4;
  struct rtable *rt;
  int err;

  if (addr_len < sizeof(struct sockaddr_in))
    return -EINVAL;

  if (usin->sin_family != AF_INET)
    return -EAFNOSUPPORT;

  nexthop = daddr = usin->sin_addr.s_addr;
  inet_opt = rcu_dereference_protected(inet->inet_opt,
               lockdep_sock_is_held(sk));
  if (inet_opt && inet_opt->opt.srr) {
    if (!daddr)
      return -EINVAL;
    nexthop = inet_opt->opt.faddr;
  }

  orig_sport = inet->inet_sport;
  orig_dport = usin->sin_port;
  fl4 = &inet->cork.fl.u.ip4;
  rt = ip_route_connect(fl4, nexthop, inet->inet_saddr,
            sk->sk_bound_dev_if, IPPROTO_TCP, orig_sport,
            orig_dport, sk);
  if (IS_ERR(rt)) {
    err = PTR_ERR(rt);
    if (err == -ENETUNREACH)
      IP_INC_STATS(net, IPSTATS_MIB_OUTNOROUTES);
    return err;
  }

  if (rt->rt_flags & (RTCF_MULTICAST | RTCF_BROADCAST)) {
    ip_rt_put(rt);
    return -ENETUNREACH;
  }

  if (!inet_opt || !inet_opt->opt.srr)
    daddr = fl4->daddr;

  tcp_death_row = &sock_net(sk)->ipv4.tcp_death_row;

  if (!inet->inet_saddr) {
    err = inet_bhash2_update_saddr(sk,  &fl4->saddr, AF_INET);
    if (err) {
      ip_rt_put(rt);
      return err;
    }
  } else {
    sk_rcv_saddr_set(sk, inet->inet_saddr);
  }

  if (tp->rx_opt.ts_recent_stamp && inet->inet_daddr != daddr) {
    /* Reset inherited state */
    tp->rx_opt.ts_recent    = 0;
    tp->rx_opt.ts_recent_stamp = 0;
    if (likely(!tp->repair))
      WRITE_ONCE(tp->write_seq, 0);
  }

  inet->inet_dport = usin->sin_port;
  sk_daddr_set(sk, daddr);

  inet_csk(sk)->icsk_ext_hdr_len = 0;
  if (inet_opt)
    inet_csk(sk)->icsk_ext_hdr_len = inet_opt->opt.optlen;

  tp->rx_opt.mss_clamp = TCP_MSS_DEFAULT;

  /* Socket identity is still unknown (sport may be zero).
   * However we set state to SYN-SENT and not releasing socket
   * lock select source port, enter ourselves into the hash tables and
   * complete initialization after this.
   */
  tcp_set_state(sk, TCP_SYN_SENT);
  err = inet_hash_connect(tcp_death_row, sk);
  if (err)
    goto failure;

  sk_set_txhash(sk);

  rt = ip_route_newports(fl4, rt, orig_sport, orig_dport,
             inet->inet_sport, inet->inet_dport, sk);
  if (IS_ERR(rt)) {
    err = PTR_ERR(rt);
    rt = NULL;
    goto failure;
  }
  /* OK, now commit destination to socket.  */
  sk->sk_gso_type = SKB_GSO_TCPV4;
  sk_setup_caps(sk, &rt->dst);
  rt = NULL;

  if (likely(!tp->repair)) {
    if (!tp->write_seq)
      WRITE_ONCE(tp->write_seq,
           secure_tcp_seq(inet->inet_saddr,
              inet->inet_daddr,
              inet->inet_sport,
              usin->sin_port));
    tp->tsoffset = secure_tcp_ts_off(net, inet->inet_saddr,
             inet->inet_daddr);
  }

  inet->inet_id = get_random_u16();

  if (tcp_fastopen_defer_connect(sk, &err))
    return err;
  if (err)
    goto failure;

  err = tcp_connect(sk);

  if (err)
    goto failure;

  return 0;

failure:
  /*
   * This unhashes the socket and releases the local port,
   * if necessary.
   */
  tcp_set_state(sk, TCP_CLOSE);
  inet_bhash2_reset_saddr(sk);
  ip_rt_put(rt);
  sk->sk_route_caps = 0;
  inet->inet_dport = 0;
  return err;
}
EXPORT_SYMBOL(tcp_v4_connect);
```

參考鏈接：<https://elixir.bootlin.com/linux/latest/source/net/ipv4/tcp_ipv4.c#L340>

接下來，我們一步步分析這個函數：

首先，這個函數接收三個參數：一個套接字指針`sk`，一個指向套接字地址結構的指針`uaddr`和地址的長度`addr_len`。

```c
int tcp_v4_connect(struct sock *sk, struct sockaddr *uaddr, int addr_len)
```

函數一開始就進行了參數檢查，確認地址長度正確，而且地址的協議族必須是IPv4。不滿足這些條件會導致函數返回錯誤。

接下來，函數獲取目標地址，如果設置了源路由選項（這是一個高級的IP特性，通常不會被使用），那麼它還會獲取源路由的下一跳地址。

```c
nexthop = daddr = usin->sin_addr.s_addr;
inet_opt = rcu_dereference_protected(inet->inet_opt,
             lockdep_sock_is_held(sk));
if (inet_opt && inet_opt->opt.srr) {
  if (!daddr)
    return -EINVAL;
  nexthop = inet_opt->opt.faddr;
}
```

然後，使用這些信息來尋找一個路由到目標地址的路由項。如果不能找到路由項或者路由項指向一個多播或廣播地址，函數返回錯誤。

接下來，它更新了源地址，處理了一些TCP時間戳選項的狀態，並設置了目標端口和地址。之後，它更新了一些其他的套接字和TCP選項，並設置了連接狀態為`SYN-SENT`。

然後，這個函數使用`inet_hash_connect`函數嘗試將套接字添加到已連接的套接字的散列表中。如果這步失敗，它會恢復套接字的狀態並返回錯誤。

如果前面的步驟都成功了，接著，使用新的源和目標端口來更新路由項。如果這步失敗，它會清理資源並返回錯誤。

接下來，它提交目標信息到套接字，併為之後的分段偏移選擇一個安全的隨機值。

然後，函數嘗試使用TCP Fast Open（TFO）進行連接，如果不能使用TFO或者TFO嘗試失敗，它會使用普通的TCP三次握手進行連接。

最後，如果上面的步驟都成功了，函數返回成功，否則，它會清理所有資源並返回錯誤。

總的來說，`tcp_v4_connect`函數是一個處理TCP連接請求的複雜函數，它處理了很多情況，包括參數檢查、路由查找、源地址選擇、源路由、TCP選項處理、TCP Fast Open，等等。它的主要目標是儘可能安全和有效地建立TCP連接。

### 內核態代碼

```c
// SPDX-License-Identifier: GPL-2.0
// Copyright (c) 2020 Wenbo Zhang
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_core_read.h>
#include <bpf/bpf_tracing.h>
#include "tcpconnlat.h"

#define AF_INET    2
#define AF_INET6   10

const volatile __u64 targ_min_us = 0;
const volatile pid_t targ_tgid = 0;

struct piddata {
  char comm[TASK_COMM_LEN];
  u64 ts;
  u32 tgid;
};

struct {
  __uint(type, BPF_MAP_TYPE_HASH);
  __uint(max_entries, 4096);
  __type(key, struct sock *);
  __type(value, struct piddata);
} start SEC(".maps");

struct {
  __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
  __uint(key_size, sizeof(u32));
  __uint(value_size, sizeof(u32));
} events SEC(".maps");

static int trace_connect(struct sock *sk)
{
  u32 tgid = bpf_get_current_pid_tgid() >> 32;
  struct piddata piddata = {};

  if (targ_tgid && targ_tgid != tgid)
    return 0;

  bpf_get_current_comm(&piddata.comm, sizeof(piddata.comm));
  piddata.ts = bpf_ktime_get_ns();
  piddata.tgid = tgid;
  bpf_map_update_elem(&start, &sk, &piddata, 0);
  return 0;
}

static int handle_tcp_rcv_state_process(void *ctx, struct sock *sk)
{
  struct piddata *piddatap;
  struct event event = {};
  s64 delta;
  u64 ts;

  if (BPF_CORE_READ(sk, __sk_common.skc_state) != TCP_SYN_SENT)
    return 0;

  piddatap = bpf_map_lookup_elem(&start, &sk);
  if (!piddatap)
    return 0;

  ts = bpf_ktime_get_ns();
  delta = (s64)(ts - piddatap->ts);
  if (delta < 0)
    goto cleanup;

  event.delta_us = delta / 1000U;
  if (targ_min_us && event.delta_us < targ_min_us)
    goto cleanup;
  __builtin_memcpy(&event.comm, piddatap->comm,
      sizeof(event.comm));
  event.ts_us = ts / 1000;
  event.tgid = piddatap->tgid;
  event.lport = BPF_CORE_READ(sk, __sk_common.skc_num);
  event.dport = BPF_CORE_READ(sk, __sk_common.skc_dport);
  event.af = BPF_CORE_READ(sk, __sk_common.skc_family);
  if (event.af == AF_INET) {
    event.saddr_v4 = BPF_CORE_READ(sk, __sk_common.skc_rcv_saddr);
    event.daddr_v4 = BPF_CORE_READ(sk, __sk_common.skc_daddr);
  } else {
    BPF_CORE_READ_INTO(&event.saddr_v6, sk,
        __sk_common.skc_v6_rcv_saddr.in6_u.u6_addr32);
    BPF_CORE_READ_INTO(&event.daddr_v6, sk,
        __sk_common.skc_v6_daddr.in6_u.u6_addr32);
  }
  bpf_perf_event_output(ctx, &events, BPF_F_CURRENT_CPU,
      &event, sizeof(event));

cleanup:
  bpf_map_delete_elem(&start, &sk);
  return 0;
}

SEC("kprobe/tcp_v4_connect")
int BPF_KPROBE(tcp_v4_connect, struct sock *sk)
{
  return trace_connect(sk);
}

SEC("kprobe/tcp_v6_connect")
int BPF_KPROBE(tcp_v6_connect, struct sock *sk)
{
  return trace_connect(sk);
}

SEC("kprobe/tcp_rcv_state_process")
int BPF_KPROBE(tcp_rcv_state_process, struct sock *sk)
{
  return handle_tcp_rcv_state_process(ctx, sk);
}

SEC("fentry/tcp_v4_connect")
int BPF_PROG(fentry_tcp_v4_connect, struct sock *sk)
{
  return trace_connect(sk);
}

SEC("fentry/tcp_v6_connect")
int BPF_PROG(fentry_tcp_v6_connect, struct sock *sk)
{
  return trace_connect(sk);
}

SEC("fentry/tcp_rcv_state_process")
int BPF_PROG(fentry_tcp_rcv_state_process, struct sock *sk)
{
  return handle_tcp_rcv_state_process(ctx, sk);
}

char LICENSE[] SEC("license") = "GPL";
```

這個eBPF（Extended Berkeley Packet Filter）程序主要用來監控並收集TCP連接的建立時間，即從發起TCP連接請求(`connect`系統調用)到連接建立完成(SYN-ACK握手過程完成)的時間間隔。這對於監測網絡延遲、服務性能分析等方面非常有用。

首先，定義了兩個eBPF maps：`start`和`events`。`start`是一個哈希表，用於存儲發起連接請求的進程信息和時間戳，而`events`是一個`PERF_EVENT_ARRAY`類型的map，用於將事件數據傳輸到用戶態。

```c
struct {
  __uint(type, BPF_MAP_TYPE_HASH);
  __uint(max_entries, 4096);
  __type(key, struct sock *);
  __type(value, struct piddata);
} start SEC(".maps");

struct {
  __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
  __uint(key_size, sizeof(u32));
  __uint(value_size, sizeof(u32));
} events SEC(".maps");
```

在`tcp_v4_connect`和`tcp_v6_connect`的kprobe處理函數`trace_connect`中，會記錄下發起連接請求的進程信息（進程名、進程ID和當前時間戳），並以socket結構作為key，存儲到`start`這個map中。

```c
static int trace_connect(struct sock *sk)
{
  u32 tgid = bpf_get_current_pid_tgid() >> 32;
  struct piddata piddata = {};

  if (targ_tgid && targ_tgid != tgid)
    return 0;

  bpf_get_current_comm(&piddata.comm, sizeof(piddata.comm));
  piddata.ts = bpf_ktime_get_ns();
  piddata.tgid = tgid;
  bpf_map_update_elem(&start, &sk, &piddata, 0);
  return 0;
}
```

當TCP狀態機處理到SYN-ACK包，即連接建立的時候，會觸發`tcp_rcv_state_process`的kprobe處理函數`handle_tcp_rcv_state_process`。在這個函數中，首先檢查socket的狀態是否為`SYN-SENT`，如果是，會從`start`這個map中查找socket對應的進程信息。然後計算出從發起連接到現在的時間間隔，將該時間間隔，進程信息，以及TCP連接的詳細信息（源端口，目標端口，源IP，目標IP等）作為event，通過`bpf_perf_event_output`函數發送到用戶態。

```c
static int handle_tcp_rcv_state_process(void *ctx, struct sock *sk)
{
  struct piddata *piddatap;
  struct event event = {};
  s64 delta;
  u64 ts;

  if (BPF_CORE_READ(sk, __sk_common.skc_state) != TCP_SYN_SENT)
    return 0;

  piddatap = bpf_map_lookup_elem(&start, &sk);
  if (!piddatap)
    return 0;

  ts = bpf_ktime_get_ns();
  delta = (s64)(ts - piddatap->ts);
  if (delta < 0)
    goto cleanup;

  event.delta_us = delta / 1000U;
  if (targ_min_us && event.delta_us < targ_min_us)
    goto

 cleanup;
  __builtin_memcpy(&event.comm, piddatap->comm,
      sizeof(event.comm));
  event.ts_us = ts / 1000;
  event.tgid = piddatap->tgid;
  event.lport = BPF_CORE_READ(sk, __sk_common.skc_num);
  event.dport = BPF_CORE_READ(sk, __sk_common.skc_dport);
  event.af = BPF_CORE_READ(sk, __sk_common.skc_family);
  if (event.af == AF_INET) {
    event.saddr_v4 = BPF_CORE_READ(sk, __sk_common.skc_rcv_saddr);
    event.daddr_v4 = BPF_CORE_READ(sk, __sk_common.skc_daddr);
  } else {
    BPF_CORE_READ_INTO(&event.saddr_v6, sk,
        __sk_common.skc_v6_rcv_saddr.in6_u.u6_addr32);
    BPF_CORE_READ_INTO(&event.daddr_v6, sk,
        __sk_common.skc_v6_daddr.in6_u.u6_addr32);
  }
  bpf_perf_event_output(ctx, &events, BPF_F_CURRENT_CPU,
      &event, sizeof(event));

cleanup:
  bpf_map_delete_elem(&start, &sk);
  return 0;
}
```

理解這個程序的關鍵在於理解Linux內核的網絡棧處理流程，以及eBPF程序的運行模式。Linux內核網絡棧對TCP連接建立的處理過程是，首先調用`tcp_v4_connect`或`tcp_v6_connect`函數（根據IP版本不同）發起TCP連接，然後在收到SYN-ACK包時，通過`tcp_rcv_state_process`函數來處理。eBPF程序通過在這兩個關鍵函數上設置kprobe，可以在關鍵時刻得到通知並執行相應的處理代碼。

一些關鍵概念說明：

- kprobe：Kernel Probe，是Linux內核中用於動態追蹤內核行為的機制。可以在內核函數的入口和退出處設置斷點，當斷點被觸發時，會執行與kprobe關聯的eBPF程序。
- map：是eBPF程序中的一種數據結構，用於在內核態和用戶態之間共享數據。
- socket：在Linux網絡編程中，socket是一個抽象概念，表示一個網絡連接的端點。內核中的`struct sock`結構就是對socket的實現。

### 用戶態數據處理

用戶態數據處理是使用`perf_buffer__poll`來接收並處理從內核發送到用戶態的eBPF事件。`perf_buffer__poll`是libbpf庫提供的一個便捷函數，用於輪詢perf event buffer並處理接收到的數據。

首先，讓我們詳細看一下主輪詢循環：

```c
    /* main: poll */
    while (!exiting) {
        err = perf_buffer__poll(pb, PERF_POLL_TIMEOUT_MS);
        if (err < 0 && err != -EINTR) {
            fprintf(stderr, "error polling perf buffer: %s\n", strerror(-err));
            goto cleanup;
        }
        /* reset err to return 0 if exiting */
        err = 0;
    }
```

這段代碼使用一個while循環來反覆輪詢perf event buffer。如果輪詢出錯（例如由於信號中斷），會打印出錯誤消息。這個輪詢過程會一直持續，直到收到一個退出標誌`exiting`。

接下來，讓我們來看看`handle_event`函數，這個函數將處理從內核發送到用戶態的每一個eBPF事件：

```c
void handle_event(void* ctx, int cpu, void* data, __u32 data_sz) {
    const struct event* e = data;
    char src[INET6_ADDRSTRLEN];
    char dst[INET6_ADDRSTRLEN];
    union {
        struct in_addr x4;
        struct in6_addr x6;
    } s, d;
    static __u64 start_ts;

    if (env.timestamp) {
        if (start_ts == 0)
            start_ts = e->ts_us;
        printf("%-9.3f ", (e->ts_us - start_ts) / 1000000.0);
    }
    if (e->af == AF_INET) {
        s.x4.s_addr = e->saddr_v4;
        d.x4.s_addr = e->daddr_v4;
    } else if (e->af == AF_INET6) {
        memcpy(&s.x6.s6_addr, e->saddr_v6, sizeof(s.x6.s6_addr));
        memcpy(&d.x6.s6_addr, e->daddr_v6, sizeof(d.x6.s6_addr));
    } else {
        fprintf(stderr, "broken event: event->af=%d", e->af);
        return;
    }

    if (env.lport) {
        printf("%-6d %-12.12s %-2d %-16s %-6d %-16s %-5d %.2f\n", e->tgid,
               e->comm, e->af == AF_INET ? 4 : 6,
               inet_ntop(e->af, &s, src, sizeof(src)), e->lport,
               inet_ntop(e->af, &d, dst, sizeof(dst)), ntohs(e->dport),
               e->delta_us / 1000.0);
    } else {
        printf("%-6d %-12.12s %-2d %-16s %-16s %-5d %.2f\n", e->tgid, e->comm,
               e->af == AF_INET ? 4 : 6, inet_ntop(e->af, &s, src, sizeof(src)),
               inet_ntop(e->af, &d, dst, sizeof(dst)), ntohs(e->dport),
               e->delta_us / 1000.0);
    }
}
```

`handle_event`函數的參數包括了CPU編號、指向數據的指針以及數據的大小。數據是一個`event`結構體，包含了之前在內核態計算得到的TCP連接的信息。

首先，它將接收到的事件的時間戳和起始時間戳（如果存在）進行對比，計算出事件的相對時間，並打印出來。接著，根據IP地址的類型（IPv4或IPv6），將源地址和目標地址從網絡字節序轉換為主機字節序。

最後，根據用戶是否選擇了顯示本地端口，將進程ID、進程名稱、IP版本、源IP地址、本地端口（如果有）、目標IP地址、目標端口以及連接建立時間打印出來。這個連接建立時間是我們在內核態eBPF程序中計算併發送到用戶態的。

## 編譯運行

```console
$ make
...
  BPF      .output/tcpconnlat.bpf.o
  GEN-SKEL .output/tcpconnlat.skel.h
  CC       .output/tcpconnlat.o
  BINARY   tcpconnlat
$ sudo ./tcpconnlat 
PID    COMM         IP SADDR            DADDR            DPORT LAT(ms)
222564 wget         4  192.168.88.15    110.242.68.3     80    25.29
222684 wget         4  192.168.88.15    167.179.101.42   443   246.76
222726 ssh          4  192.168.88.15    167.179.101.42   22    241.17
222774 ssh          4  192.168.88.15    1.15.149.151     22    25.31
```

源代碼：<https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/13-tcpconnlat> 關於如何安裝依賴，請參考：<https://eunomia.dev/tutorials/11-bootstrap/>

參考資料：

- [tcpconnlat](https://github.com/iovisor/bcc/blob/master/libbpf-tools/tcpconnlat.c)

## 總結

通過本篇 eBPF 入門實踐教程，我們學習瞭如何使用 eBPF 來跟蹤和統計 TCP 連接建立的延時。我們首先深入探討了 eBPF 程序如何在內核態監聽特定的內核函數，然後通過捕獲這些函數的調用，從而得到連接建立的起始時間和結束時間，計算出延時。

我們還進一步瞭解瞭如何使用 BPF maps 來在內核態存儲和查詢數據，從而在 eBPF 程序的多個部分之間共享數據。同時，我們也探討了如何使用 perf events 來將數據從內核態發送到用戶態，以便進一步處理和展示。

在用戶態，我們介紹瞭如何使用 libbpf 庫的 API，例如 perf_buffer__poll，來接收和處理內核態發送過來的數據。我們還講解了如何對這些數據進行解析和打印，使得它們能以人類可讀的形式顯示出來。

如果您希望學習更多關於 eBPF 的知識和實踐，請查閱 eunomia-bpf 的官方文檔：<https://github.com/eunomia-bpf/eunomia-bpf> 。您還可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。
