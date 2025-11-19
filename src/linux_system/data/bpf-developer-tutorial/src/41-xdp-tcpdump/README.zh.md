# eBPF 示例教程：使用 XDP 捕獲 TCP 信息

擴展伯克利包過濾器（eBPF）是 Linux 內核中的一項革命性技術，允許開發者在內核空間內運行沙箱程序。它提供了強大的網絡、安全和跟蹤能力，無需修改內核源代碼或加載內核模塊。本教程重點介紹如何使用 eBPF 結合 Express Data Path（XDP），在數據包進入時的最早階段直接捕獲 TCP 頭信息。

## 使用 XDP 捕獲 TCP 頭信息

捕獲網絡數據包對於監控、調試和保護網絡通信至關重要。傳統工具如 `tcpdump` 在用戶空間運行，可能會帶來顯著的開銷。通過利用 eBPF 和 XDP，我們可以在內核中直接捕獲 TCP 頭信息，最小化開銷並提高性能。

在本教程中，我們將開發一個 XDP 程序，該程序攔截傳入的 TCP 數據包並提取其頭信息。我們將這些數據存儲在一個環形緩衝區中，用戶空間的程序將讀取並以可讀的格式顯示這些信息。

### 為什麼使用 XDP 進行數據包捕獲？

XDP 是 Linux 內核中一個高性能的數據路徑，允許在網絡棧的最低層進行可編程的數據包處理。通過將 eBPF 程序附加到 XDP，我們可以在數據包到達時立即處理它們，減少延遲並提高效率。

## 內核 eBPF 代碼分析

讓我們深入瞭解捕獲 TCP 頭信息的內核空間 eBPF 代碼。

### 完整的內核代碼

```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

#define ETH_P_IP 0x0800

// 定義環形緩衝區映射
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 1 << 24);  // 16 MB 緩衝區
} rb SEC(".maps");

// 檢查數據包是否為 TCP 的輔助函數
static bool is_tcp(struct ethhdr *eth, void *data_end)
{
    // 確保以太網頭在邊界內
    if ((void *)(eth + 1) > data_end)
        return false;

    // 僅處理 IPv4 數據包
    if (bpf_ntohs(eth->h_proto) != ETH_P_IP)
        return false;

    struct iphdr *ip = (struct iphdr *)(eth + 1);

    // 確保 IP 頭在邊界內
    if ((void *)(ip + 1) > data_end)
        return false;

    // 檢查協議是否為 TCP
    if (ip->protocol != IPPROTO_TCP)
        return false;

    return true;
}

SEC("xdp")
int xdp_pass(struct xdp_md *ctx)
{
    // 數據包數據指針
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    // 解析以太網頭
    struct ethhdr *eth = data;

    // 檢查數據包是否為 TCP 數據包
    if (!is_tcp(eth, data_end)) {
        return XDP_PASS;
    }

    // 轉換為 IP 頭
    struct iphdr *ip = (struct iphdr *)(eth + 1);

    // 計算 IP 頭長度
    int ip_hdr_len = ip->ihl * 4;
    if (ip_hdr_len < sizeof(struct iphdr)) {
        return XDP_PASS;
    }

    // 確保 IP 頭在數據包邊界內
    if ((void *)ip + ip_hdr_len > data_end) {
        return XDP_PASS;
    }

    // 解析 TCP 頭
    struct tcphdr *tcp = (struct tcphdr *)((unsigned char *)ip + ip_hdr_len);

    // 確保 TCP 頭在數據包邊界內
    if ((void *)(tcp + 1) > data_end) {
        return XDP_PASS;
    }

    // 定義要捕獲的 TCP 頭字節數
    const int tcp_header_bytes = 32;

    // 確保所需字節數不超過數據包邊界
    if ((void *)tcp + tcp_header_bytes > data_end) {
        return XDP_PASS;
    }

    // 在環形緩衝區中預留空間
    void *ringbuf_space = bpf_ringbuf_reserve(&rb, tcp_header_bytes, 0);
    if (!ringbuf_space) {
        return XDP_PASS;  // 如果預留失敗，跳過處理
    }

    // 將 TCP 頭字節複製到環形緩衝區
    // 使用循環以確保符合 eBPF 驗證器要求
    for (int i = 0; i < tcp_header_bytes; i++) {
        unsigned char byte = *((unsigned char *)tcp + i);
        ((unsigned char *)ringbuf_space)[i] = byte;
    }

    // 將數據提交到環形緩衝區
    bpf_ringbuf_submit(ringbuf_space, 0);

    // 可選：打印調試信息
    bpf_printk("Captured TCP header (%d bytes)", tcp_header_bytes);

    return XDP_PASS;
}

char __license[] SEC("license") = "GPL";
```

### 代碼解釋

#### 定義環形緩衝區映射

我們定義了一個名為 `rb` 的環形緩衝區映射，用於高效地將數據從內核傳遞到用戶空間。

```c
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 1 << 24);  // 16 MB 緩衝區
} rb SEC(".maps");
```

#### 數據包解析與驗證

`is_tcp` 輔助函數通過驗證以太網和 IP 頭，檢查傳入的數據包是否為 TCP 數據包。

```c
static bool is_tcp(struct ethhdr *eth, void *data_end)
{
    // ...（檢查內容略）
}
```

#### 捕獲 TCP 頭信息

在 `xdp_pass` 函數中，我們：

1. 解析以太網、IP 和 TCP 頭。
2. 確保所有頭信息在數據包邊界內，以防止無效內存訪問。
3. 在環形緩衝區中預留空間以存儲 TCP 頭。
4. 將 TCP 頭字節複製到環形緩衝區。
5. 提交數據到環形緩衝區，供用戶空間使用。

```c
// 在環形緩衝區中預留空間
void *ringbuf_space = bpf_ringbuf_reserve(&rb, tcp_header_bytes, 0);
if (!ringbuf_space) {
    return XDP_PASS;
}

// 複製 TCP 頭字節
for (int i = 0; i < tcp_header_bytes; i++) {
    unsigned char byte = *((unsigned char *)tcp + i);
    ((unsigned char *)ringbuf_space)[i] = byte;
}

// 提交到環形緩衝區
bpf_ringbuf_submit(ringbuf_space, 0);
```

#### 使用 bpf_printk 進行調試

`bpf_printk` 函數將消息記錄到內核的跟蹤管道，對於調試非常有用。

```c
bpf_printk("Captured TCP header (%d bytes)", tcp_header_bytes);
```

## 用戶空間代碼分析

讓我們查看用戶空間程序，該程序從環形緩衝區中讀取捕獲的 TCP 頭信息並顯示。

### 完整的用戶空間代碼

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <net/if.h>

#include <bpf/libbpf.h>
#include <bpf/bpf.h>

#include "xdp-tcpdump.skel.h"  // 生成的骨架頭文件

// 處理環形緩衝區事件的回調函數
static int handle_event(void *ctx, void *data, size_t data_sz)
{
    if (data_sz < 20) {  // 最小 TCP 頭大小
        fprintf(stderr, "Received incomplete TCP header\n");
        return 0;
    }

    // 解析原始 TCP 頭字節
    struct tcphdr {
        uint16_t source;
        uint16_t dest;
        uint32_t seq;
        uint32_t ack_seq;
        uint16_t res1:4,
                 doff:4,
                 fin:1,
                 syn:1,
                 rst:1,
                 psh:1,
                 ack:1,
                 urg:1,
                 ece:1,
                 cwr:1;
        uint16_t window;
        uint16_t check;
        uint16_t urg_ptr;
        // 可能還有選項和填充
    } __attribute__((packed));

    if (data_sz < sizeof(struct tcphdr)) {
        fprintf(stderr, "Data size (%zu) less than TCP header size\n", data_sz);
        return 0;
    }

    struct tcphdr *tcp = (struct tcphdr *)data;

    // 將字段從網絡字節序轉換為主機字節序
    uint16_t source_port = ntohs(tcp->source);
    uint16_t dest_port = ntohs(tcp->dest);
    uint32_t seq = ntohl(tcp->seq);
    uint32_t ack_seq = ntohl(tcp->ack_seq);
    uint16_t window = ntohs(tcp->window);

    // 提取標誌位
    uint8_t flags = 0;
    flags |= (tcp->fin) ? 0x01 : 0x00;
    flags |= (tcp->syn) ? 0x02 : 0x00;
    flags |= (tcp->rst) ? 0x04 : 0x00;
    flags |= (tcp->psh) ? 0x08 : 0x00;
    flags |= (tcp->ack) ? 0x10 : 0x00;
    flags |= (tcp->urg) ? 0x20 : 0x00;
    flags |= (tcp->ece) ? 0x40 : 0x00;
    flags |= (tcp->cwr) ? 0x80 : 0x00;

    printf("Captured TCP Header:\n");
    printf("  源端口: %u\n", source_port);
    printf("  目的端口: %u\n", dest_port);
    printf("  序列號: %u\n", seq);
    printf("  確認號: %u\n", ack_seq);
    printf("  數據偏移: %u\n", tcp->doff);
    printf("  標誌位: 0x%02x\n", flags);
    printf("  窗口大小: %u\n", window);
    printf("\n");

    return 0;
}

int main(int argc, char **argv)
{
    struct xdp_tcpdump_bpf *skel;
    struct ring_buffer *rb = NULL;
    int ifindex;
    int err;

    if (argc != 2)
    {
        fprintf(stderr, "Usage: %s <ifname>\n", argv[0]);
        return 1;
    }

    const char *ifname = argv[1];
    ifindex = if_nametoindex(ifname);
    if (ifindex == 0)
    {
        fprintf(stderr, "Invalid interface name %s\n", ifname);
        return 1;
    }

    /* 打開並加載 BPF 應用 */
    skel = xdp_tcpdump_bpf__open();
    if (!skel)
    {
        fprintf(stderr, "Failed to open BPF skeleton\n");
        return 1;
    }

    /* 加載並驗證 BPF 程序 */
    err = xdp_tcpdump_bpf__load(skel);
    if (err)
    {
        fprintf(stderr, "Failed to load and verify BPF skeleton: %d\n", err);
        goto cleanup;
    }

    /* 附加 XDP 程序 */
    err = xdp_tcpdump_bpf__attach(skel);
    if (err)
    {
        fprintf(stderr, "Failed to attach BPF skeleton: %d\n", err);
        goto cleanup;
    }

    /* 將 XDP 程序附加到指定的接口 */
    skel->links.xdp_pass = bpf_program__attach_xdp(skel->progs.xdp_pass, ifindex);
    if (!skel->links.xdp_pass)
    {
        err = -errno;
        fprintf(stderr, "Failed to attach XDP program: %s\n", strerror(errno));
        goto cleanup;
    }

    printf("成功將 XDP 程序附加到接口 %s\n", ifname);

    /* 設置環形緩衝區輪詢 */
    rb = ring_buffer__new(bpf_map__fd(skel->maps.rb), handle_event, NULL, NULL);
    if (!rb)
    {
        fprintf(stderr, "Failed to create ring buffer\n");
        err = -1;
        goto cleanup;
    }

    printf("開始輪詢環形緩衝區\n");

    /* 輪詢環形緩衝區 */
    while (1)
    {
        err = ring_buffer__poll(rb, -1);
        if (err == -EINTR)
            continue;
        if (err < 0)
        {
            fprintf(stderr, "Error polling ring buffer: %d\n", err);
            break;
        }
    }

cleanup:
    ring_buffer__free(rb);
    xdp_tcpdump_bpf__destroy(skel);
    return -err;
}
```

### 代碼解釋

#### 處理環形緩衝區事件

`handle_event` 函數處理從環形緩衝區接收到的 TCP 頭數據。

```c
static int handle_event(void *ctx, void *data, size_t data_sz)
{
    // 驗證數據大小
    if (data_sz < 20) {
        fprintf(stderr, "Received incomplete TCP header\n");
        return 0;
    }

    // 解析 TCP 頭
    // ...（解析代碼）
}
```

#### 解析 TCP 頭

我們定義了一個本地的 `tcphdr` 結構來解釋原始字節。

```c
struct tcphdr {
    uint16_t source;
    uint16_t dest;
    uint32_t seq;
    uint32_t ack_seq;
    // ...（其他字段）
} __attribute__((packed));
```

#### 顯示捕獲的信息

解析後，我們以可讀的格式打印 TCP 頭字段。

```c
printf("Captured TCP Header:\n");
printf("  源端口: %u\n", source_port);
printf("  目的端口: %u\n", dest_port);
// ...（其他字段）
```

#### 設置 eBPF 骨架

我們使用生成的骨架 `xdp-tcpdump.skel.h` 來加載和附加 eBPF 程序。

```c
/* 打開並加載 BPF 應用 */
skel = xdp_tcpdump_bpf__open();
if (!skel) {
    fprintf(stderr, "Failed to open BPF skeleton\n");
    return 1;
}

/* 加載並驗證 BPF 程序 */
err = xdp_tcpdump_bpf__load(skel);
if (err) {
    fprintf(stderr, "Failed to load and verify BPF skeleton: %d\n", err);
    goto cleanup;
}
```

#### 附加到網絡接口

我們通過接口名稱將 XDP 程序附加到指定的網絡接口。

```c
/* 將 XDP 程序附加到指定的接口 */
skel->links.xdp_pass = bpf_program__attach_xdp(skel->progs.xdp_pass, ifindex);
if (!skel->links.xdp_pass) {
    err = -errno;
    fprintf(stderr, "Failed to attach XDP program: %s\n", strerror(errno));
    goto cleanup;
}
```

## 編譯和執行說明

### 前提條件

- 支持 eBPF 和 XDP 的 Linux 系統內核。
- 安裝了 libbpf 庫。
- 具有 eBPF 支持的編譯器（如 clang）。

### 構建程序

假設您已從 [GitHub](https://github.com/eunomia-bpf/bpf-developer-tutorial) 克隆了倉庫，請導航到 `bpf-developer-tutorial/src/41-xdp-tcpdump` 目錄。

```bash
cd bpf-developer-tutorial/src/41-xdp-tcpdump
make
```

此命令將編譯內核 eBPF 代碼和用戶空間應用程序。

### 運行程序

首先，識別您的網絡接口：

```bash
ifconfig
```

示例輸出：

```
wlp0s20f3: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.1.10  netmask 255.255.255.0  broadcast 192.168.1.255
        ether 00:1a:2b:3c:4d:5e  txqueuelen 1000  (Ethernet)
```

使用所需的網絡接口運行用戶空間程序：

```bash
sudo ./xdp-tcpdump wlp0s20f3
```

示例輸出：

```
成功將 XDP 程序附加到接口 wlp0s20f3
開始輪詢環形緩衝區
Captured TCP Header:
  源端口: 443
  目的端口: 53500
  序列號: 572012449
  確認號: 380198588
  數據偏移: 8
  標誌位: 0x10
  窗口大小: 16380
```

### 完整的源代碼和資源

- **源代碼倉庫:** [GitHub - bpf-developer-tutorial](https://github.com/eunomia-bpf/bpf-developer-tutorial)
- **教程網站:** [eunomia.dev Tutorials](https://eunomia.dev/tutorials/)

## 總結與結論

在本教程中，我們探討了如何使用 eBPF 和 XDP 在 Linux 內核中直接捕獲 TCP 頭信息。通過分析內核 eBPF 代碼和用戶空間應用程序，我們學習瞭如何攔截數據包、提取關鍵的 TCP 字段，並使用環形緩衝區高效地將這些數據傳遞到用戶空間。

這種方法為傳統的數據包捕獲方法提供了一種高性能的替代方案，對系統資源的影響最小。它是網絡監控、安全分析和調試的強大技術。

如果您想了解更多關於 eBPF 的內容，請訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或我們的網站 <https://eunomia.dev/tutorials/>

編程愉快！