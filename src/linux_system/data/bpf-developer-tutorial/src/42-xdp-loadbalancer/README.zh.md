# eBPF 開發者教程： 簡單的 XDP 負載均衡器

在本教程中，我們將指導您如何使用eBPF（擴展的Berkeley Packet Filter）實現一個簡單的XDP（eXpress Data Path）負載均衡器。只需使用C語言和libbpf庫，無需外部依賴，這是一個適合開發者的實踐指南，幫助您充分利用Linux內核的強大功能來構建高效的網絡應用程序。

## 為什麼選擇XDP？

`XDP`（eXpress Data Path）是Linux中的一個高速、內核級網絡框架，它允許在網絡堆棧的最早階段，即在網絡接口卡（NIC）上處理數據包。這使得XDP可以進行超低延遲和高吞吐量的數據包處理，非常適合用於負載均衡、DDoS保護和流量過濾等任務。

XDP的關鍵特性:

1. **快速數據包處理**：XDP直接在網絡接口卡（NIC）級別處理數據包，減少了延遲，並通過避免通常的網絡堆棧開銷來提高性能。
2. **高效**：由於在數據包進入內核之前處理它們，XDP最大限度地減少了CPU使用率，能夠在高流量負載下保持系統的快速響應。
3. **可定製的eBPF**：XDP程序使用eBPF編寫，允許您為特定的用例創建自定義的數據包處理邏輯，例如丟棄、重定向或轉發數據包。
4. **低CPU開銷**：支持零拷貝數據包轉發，XDP佔用更少的系統資源，非常適合在最少CPU負載的情況下處理高流量。
5. **簡單操作**：XDP程序返回預定義的操作，例如丟棄、通過或重定向數據包，提供對流量處理的控制。

### 使用XDP的項目

- `Cilium` 是一個為雲原生環境（如Kubernetes）設計的開源網絡工具。它使用XDP高效處理數據包過濾和負載均衡，提升了高流量網絡中的性能。
- `Katran` 由Facebook開發，是一個負載均衡器，它使用XDP處理數百萬的連接，且CPU使用率低。它高效地將流量分發到服務器，在Facebook內部被用於大規模的網絡環境。
- `Cloudflare` 使用XDP來防禦DDoS攻擊。通過在NIC級別過濾惡意流量，Cloudflare可以在攻擊數據包進入內核之前將其丟棄，最大限度地減少對網絡的影響。

### 為什麼選擇XDP而不是其他方法？

與傳統工具如`iptables`或`tc`相比，XDP具有以下優勢：

- **速度**：它直接在NIC驅動程序中操作，數據包處理速度遠快於傳統方法。
- **靈活性**：通過eBPF，您可以編寫自定義的數據包處理邏輯，以滿足特定需求。
- **效率**：XDP使用更少的資源，非常適合需要處理高流量而不使系統過載的環境。

## 項目：構建一個簡單的負載均衡器

在本項目中，我們將專注於使用XDP構建一個負載均衡器。負載均衡器通過將傳入的網絡流量高效地分發到多個後端服務器，防止單個服務器過載。結合XDP和eBPF，我們可以構建一個運行在Linux網絡堆棧邊緣的負載均衡器，確保即使在高流量情況下也能保持高性能。

我們將實現的負載均衡器將具備以下功能：

- 監聽傳入的網絡數據包。
- 根據數據包的源IP和端口計算哈希值，從而將流量分發到多個後端服務器。
- 根據計算出的哈希值將數據包轉發到相應的後端服務器。

我們將保持設計簡單但強大，向您展示如何利用eBPF的能力來創建一個輕量級的負載均衡解決方案。

## kernel eBPF code

```c
// xdp_lb.bpf.c
#include <bpf/bpf_endian.h>
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/in.h>
#include <linux/tcp.h>
#include "xx_hash.h"

struct backend_config {
    __u32 ip;
    unsigned char mac[ETH_ALEN];
};

// Backend IP and MAC address map
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 2);  // Two backends
    __type(key, __u32);
    __type(value, struct backend_config);
} backends SEC(".maps");

int client_ip = bpf_htonl(0xa000001);  
unsigned char client_mac[ETH_ALEN] = {0xDE, 0xAD, 0xBE, 0xEF, 0x0, 0x1};
int load_balancer_ip = bpf_htonl(0xa00000a);
unsigned char load_balancer_mac[ETH_ALEN] = {0xDE, 0xAD, 0xBE, 0xEF, 0x0, 0x10};

static __always_inline __u16
csum_fold_helper(__u64 csum)
{
    int i;
    for (i = 0; i < 4; i++)
    {
        if (csum >> 16)
            csum = (csum & 0xffff) + (csum >> 16);
    }
    return ~csum;
}

static __always_inline __u16
iph_csum(struct iphdr *iph)
{
    iph->check = 0;
    unsigned long long csum = bpf_csum_diff(0, 0, (unsigned int *)iph, sizeof(struct iphdr), 0);
    return csum_fold_helper(csum);
}

SEC("xdp")
int xdp_load_balancer(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;

    bpf_printk("xdp_load_balancer received packet");

    // Ethernet header
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;

    // Check if the packet is IP (IPv4)
    if (eth->h_proto != __constant_htons(ETH_P_IP))
        return XDP_PASS;

    // IP header
    struct iphdr *iph = (struct iphdr *)(eth + 1);
    if ((void *)(iph + 1) > data_end)
        return XDP_PASS;

    // Check if the protocol is TCP or UDP
    if (iph->protocol != IPPROTO_TCP)
        return XDP_PASS;
    
    bpf_printk("Received Source IP: 0x%x", bpf_ntohl(iph->saddr));
    bpf_printk("Received Destination IP: 0x%x", bpf_ntohl(iph->daddr));
    bpf_printk("Received Source MAC: %x:%x:%x:%x:%x:%x", eth->h_source[0], eth->h_source[1], eth->h_source[2], eth->h_source[3], eth->h_source[4], eth->h_source[5]);
    bpf_printk("Received Destination MAC: %x:%x:%x:%x:%x:%x", eth->h_dest[0], eth->h_dest[1], eth->h_dest[2], eth->h_dest[3], eth->h_dest[4], eth->h_dest[5]);

    if (iph->saddr == client_ip)
    {
        bpf_printk("Packet from client");

        __u32 key = xxhash32((const char*)iph, sizeof(struct iphdr), 0) % 2;

        struct backend_config *backend = bpf_map_lookup_elem(&backends, &key);
        if (!backend)
            return XDP_PASS;
        
        iph->daddr = backend->ip;
        __builtin_memcpy(eth->h_dest, backend->mac, ETH_ALEN);
    }
    else
    {
        bpf_printk("Packet from backend");
        iph->daddr = client_ip;
        __builtin_memcpy(eth->h_dest, client_mac, ETH_ALEN);
    }

    // Update IP source address to the load balancer's IP
    iph->saddr = load_balancer_ip;
    // Update Ethernet source MAC address to the current lb's MAC
    __builtin_memcpy(eth->h_source, load_balancer_mac, ETH_ALEN);

    // Recalculate IP checksum
    iph->check = iph_csum(iph);

    bpf_printk("Redirecting packet to new IP 0x%x from IP 0x%x", 
                bpf_ntohl(iph->daddr), 
                bpf_ntohl(iph->saddr)
            );
    bpf_printk("New Dest MAC: %x:%x:%x:%x:%x:%x", eth->h_dest[0], eth->h_dest[1], eth->h_dest[2], eth->h_dest[3], eth->h_dest[4], eth->h_dest[5]);
    bpf_printk("New Source MAC: %x:%x:%x:%x:%x:%x\n", eth->h_source[0], eth->h_source[1], eth->h_source[2], eth->h_source[3], eth->h_source[4], eth->h_source[5]);
    // Return XDP_TX to transmit the modified packet back to the network
    return XDP_TX;
}

char _license[] SEC("license") = "GPL";
```

## 內核代碼關鍵部分解讀

### 1. **頭文件和數據結構**

代碼首先包含了一些必要的頭文件，例如 `<bpf/bpf_helpers.h>`、`<linux/if_ether.h>`、`<linux/ip.h>` 等。這些頭文件提供了處理以太網幀、IP 數據包以及 BPF 輔助函數的定義。

`backend_config` 結構體被定義用於存儲後端服務器的 IP 和 MAC 地址。這將在負載均衡邏輯中用於根據流量分配規則路由數據包。

```c
struct backend_config {
    __u32 ip;
    unsigned char mac[ETH_ALEN];
};
```

### 2. **後端和負載均衡器配置**

代碼定義了一個名為 `backends` 的 eBPF map，用於存儲兩個後端的 IP 和 MAC 地址。`BPF_MAP_TYPE_ARRAY` 類型用於存儲後端的配置信息，`max_entries` 設置為 2，表示該負載均衡器將把流量分配給兩個後端服務器。

```c
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 2);
    __type(key, __u32);
    __type(value, struct backend_config);
} backends SEC(".maps");
```

同時也預定義了客戶端和負載均衡器的 IP 地址和 MAC 地址：

```c
int client_ip = bpf_htonl(0xa000001);  
unsigned char client_mac[ETH_ALEN] = {0xDE, 0xAD, 0xBE, 0xEF, 0x0, 0x1};
int load_balancer_ip = bpf_htonl(0xa00000a);
unsigned char load_balancer_mac[ETH_ALEN] = {0xDE, 0xAD, 0xBE, 0xEF, 0x0, 0x10};
```

### 3. **校驗和函數**

`iph_csum()` 函數在修改數據包內容後重新計算 IP 頭的校驗和。在對頭部進行任何修改時，確保 IP 數據包的完整性是至關重要的。

```c
static __always_inline __u16 iph_csum(struct iphdr *iph) {
    iph->check = 0;
    unsigned long long csum = bpf_csum_diff(0, 0, (unsigned int *)iph, sizeof(struct iphdr), 0);
    return csum_fold_helper(csum);
}
```

### 4. **XDP 程序邏輯**

XDP 負載均衡器的核心邏輯在 `xdp_load_balancer` 函數中實現，該函數附加到 XDP 鉤子上。它處理傳入的數據包，並根據不同情況將數據包轉發到後端或回傳給客戶端。

- **初始檢查**：
  函數首先驗證數據包是否是以太網幀，接著檢查它是否是 IP 數據包（IPv4）並且使用了 TCP 協議。

  ```c
  if (eth->h_proto != __constant_htons(ETH_P_IP))
      return XDP_PASS;
  if (iph->protocol != IPPROTO_TCP)
      return XDP_PASS;
  ```

- **客戶端數據包處理**：
  如果源 IP 與客戶端 IP 匹配，代碼使用 `xxhash32` 對 IP 頭進行哈希處理，以確定相應的後端（基於 key 對 2 取模）。

  ```c
  if (iph->saddr == client_ip) {
      __u32 key = xxhash32((const char*)iph, sizeof(struct iphdr), 0) % 2;
      struct backend_config *backend = bpf_map_lookup_elem(&backends, &key);
  ```

  之後將目標 IP 和 MAC 替換為選定的後端的值，並將數據包轉發到後端。

- **後端數據包處理**：
  如果數據包來自後端服務器，代碼將目標設置為客戶端的 IP 和 MAC 地址，確保後端的響應數據包被正確地轉發回客戶端。

  ```c
  iph->daddr = client_ip;
  __builtin_memcpy(eth->h_dest, client_mac, ETH_ALEN);
  ```

- **重寫 IP 和 MAC 地址**：
  對於所有的出站數據包，源 IP 和 MAC 地址會被更新為負載均衡器的值，以確保在客戶端與後端之間通信時，負載均衡器作為源進行標識。

  ```c
  iph->saddr = load_balancer_ip;
  __builtin_memcpy(eth->h_source, load_balancer_mac, ETH_ALEN);
  ```

- **重新計算校驗和**：
  修改 IP 頭之後，使用之前定義的 `iph_csum()` 函數重新計算校驗和。

  ```c
  iph->check = iph_csum(iph);
  ```

- **最終動作**：
  使用 `XDP_TX` 動作發送數據包，這指示網卡將修改後的數據包傳輸出去。

  ```c
  return XDP_TX;
  ```

### 5. **結論**

在這部分博客中，可以解釋負載均衡器是如何通過檢查源 IP、進行哈希計算來分配流量，並通過修改目標 IP 和 MAC 來確保數據包的轉發。`XDP_TX` 動作是實現 eBPF 在 XDP 層中高速數據包處理的關鍵。

這一解釋可以幫助讀者理解數據包的流轉過程，以及代碼中每個部分在實現多個後端之間負載均衡的過程中所起的作用。


## Userspace code

```c
// xdp_lb.c
#include <arpa/inet.h>
#include <bpf/bpf.h>
#include <bpf/libbpf.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <net/if.h>
#include "xdp_lb.skel.h"  // The generated skeleton

struct backend_config {
    __u32 ip;
    unsigned char mac[6];
};

static int parse_mac(const char *str, unsigned char *mac) {
    if (sscanf(str, "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx",
               &mac[0], &mac[1], &mac[2], &mac[3], &mac[4], &mac[5]) != 6) {
        fprintf(stderr, "Invalid MAC address format\n");
        return -1;
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc != 6) {
        fprintf(stderr, "Usage: %s <ifname> <backend1_ip> <backend1_mac> <backend2_ip> <backend2_mac>\n", argv[0]);
        return 1;
    }

    const char *ifname = argv[1];
    struct backend_config backend[2];

    // Parse backend 1
    if (inet_pton(AF_INET, argv[2], &backend[0].ip) != 1) {
        fprintf(stderr, "Invalid backend 1 IP address\n");
        return 1;
    }
    if (parse_mac(argv[3], backend[0].mac) < 0) {
        return 1;
    }

    // Parse backend 2
    if (inet_pton(AF_INET, argv[4], &backend[1].ip) != 1) {
        fprintf(stderr, "Invalid backend 2 IP address\n");
        return 1;
    }
    if (parse_mac(argv[5], backend[1].mac) < 0) {
        return 1;
    }

    // Load and attach the BPF program
    struct xdp_lb_bpf *skel = xdp_lb_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Failed to open and load BPF skeleton\n");
        return 1;
    }

    int ifindex = if_nametoindex(ifname);
    if (ifindex < 0) {
        perror("if_nametoindex");
        xdp_lb_bpf__destroy(skel);
        return 1;
    }

    if (bpf_program__attach_xdp(skel->progs.xdp_load_balancer, ifindex) < 0) {
        fprintf(stderr, "Failed to attach XDP program\n");
        xdp_lb_bpf__destroy(skel);
        return 1;
    }

    // Update backend configurations
    for (int i = 0; i < 2; i++) {
        if (bpf_map_update_elem(bpf_map__fd(skel->maps.backends), &i, &backend[i], 0) < 0) {
            perror("bpf_map_update_elem");
            xdp_lb_bpf__destroy(skel);
            return 1;
        }
    }

    printf("XDP load balancer configured with backends:\n");
    printf("Backend 1 - IP: %s, MAC: %s\n", argv[2], argv[3]);
    printf("Backend 2 - IP: %s, MAC: %s\n", argv[4], argv[5]);

    printf("Press Ctrl+C to exit...\n");
    while (1) {
        sleep(1);  // Keep the program running
    }

    // Cleanup and detach
    bpf_xdp_detach(ifindex, 0, NULL);
    xdp_lb_bpf__detach(skel);
    xdp_lb_bpf__destroy(skel);
    return 0;
}
```

### 用戶空間代碼概述

提供的用戶空間代碼負責設置和配置在內核中運行的 XDP 負載均衡器程序。它接受命令行參數，加載 eBPF 程序，將其附加到網絡接口，並更新後端服務器的配置信息。

### 1. **解析命令行參數和設置後端服務器**

程序期望五個命令行參數：網絡接口的名稱 (`ifname`)、兩個後端服務器的 IP 地址和 MAC 地址。它通過 `inet_pton()` 函數解析 IP 地址，並使用 `parse_mac()` 函數解析 MAC 地址，確保提供的 MAC 地址格式正確。解析後的後端信息存儲在 `backend_config` 結構體中。

### 2. **加載並附加 BPF 程序**

BPF skeleton（通過 `xdp_lb.skel.h` 生成）用於打開並將 XDP 程序加載到內核中。程序通過 `if_nametoindex()` 將網絡接口名稱轉換為索引，然後使用 `bpf_program__attach_xdp()` 將加載的 BPF 程序附加到此接口上。

### 3. **配置後端服務器信息**

後端的 IP 和 MAC 地址被寫入 `backends` BPF map 中，使用 `bpf_map_update_elem()` 函數。此步驟確保 BPF 程序能夠訪問後端配置，從而基於內核代碼中的邏輯將數據包路由到正確的後端服務器。

### 4. **程序循環與清理**

程序進入無限循環（`while (1) { sleep(1); }`），使 XDP 程序保持運行。當用戶通過按下 Ctrl+C 退出時，BPF 程序從網絡接口上卸載，並通過調用 `xdp_lb_bpf__destroy()` 清理資源。

總的來說，這段用戶空間代碼負責配置和管理 XDP 負載均衡器的生命週期，使得可以動態更新後端配置，並確保負載均衡器正確附加到網絡接口上。

### 測試環境拓撲

拓撲結構表示一個測試環境，其中本地機器通過負載均衡器與兩個後端節點（h2 和 h3）通信。通過虛擬以太網對（veth0 到 veth6），本地機器與負載均衡器相連，在受控環境中模擬網絡連接。每個虛擬接口都有自己的 IP 和 MAC 地址，代表不同的實體。

```txt
    +---------------------------+          
    |      本地機器              |
    |  IP: 10.0.0.1 (veth0)      |
    |  MAC: DE:AD:BE:EF:00:01    |
    +------------+---------------+
             |
             | (veth1)
             |
    +--------+---------------+       
    |    負載均衡器           |
    |  IP: 10.0.0.10 (veth6) |
    |  MAC: DE:AD:BE:EF:00:10|
    +--------+---------------+       
             | 
   +---------+----------------------------+            
   |                                      |
(veth2)                                (veth4)    
   |                                      | 
+--+---------------+             +--------+---------+
| h2               |             | h3               |
| IP:              |             | IP:              |
|10.0.0.2 (veth3)  |             |10.0.0.3 (veth5)  |
| MAC:             |             | MAC:             |
|DE:AD:BE:EF:00:02 |             |DE:AD:BE:EF:00:03 |
+------------------+             +------------------+
```

這個設置可以通過腳本（`setup.sh`）輕鬆初始化，並通過另一個腳本（`teardown.sh`）刪除。

> 如果您對本教程感興趣，請幫助我們創建一個容器化的版本，簡化設置和拓撲結構！目前的設置和刪除過程基於網絡命名空間，容器化的版本會更加友好。

初始化：

```sh
sudo ./setup.sh
```

刪除：

```sh
sudo ./teardown.sh
```

### 運行負載均衡器

要運行 XDP 負載均衡器，執行以下命令，指定接口和後端服務器的 IP 和 MAC 地址：

```console
sudo ip netns exec lb ./xdp_lb veth6 10.0.0.2 de:ad:be:ef:00:02 10.0.0.3 de:ad:be:ef:00:03
```

這將配置負載均衡器並輸出後端服務器的詳細信息：

```console
XDP load balancer configured with backends:
Backend 1 - IP: 10.0.0.2, MAC: de:ad:be:ef:00:02
Backend 2 - IP: 10.0.0.3, MAC: de:ad:be:ef:00:03
Press Ctrl+C to exit...
```

### 測試設置

您可以通過在兩個後端命名空間（`h2` 和 `h3`）啟動 HTTP 服務器，並從本地機器向負載均衡器發送請求來測試設置：

在 `h2` 和 `h3` 上啟動服務器：

```sh
sudo ip netns exec h2 python3 -m http.server
sudo ip netns exec h3 python3 -m http.server
```

然後，向負載均衡器 IP 發送請求：

```sh
curl 10.0.0.10:8000
```

負載均衡器將根據哈希函數將流量分配到後端服務器（`h2` 和 `h3`）。

### 使用 `bpf_printk` 進行監控

您可以通過查看 `bpf_printk` 日誌來監控負載均衡器的活動。BPF 程序在處理每個數據包時會打印診斷消息。您可以使用以下命令查看這些日誌：

```console
sudo cat /sys/kernel/debug/tracing/trace_pipe
```

日誌示例：

```console
<idle>-0       [004] ..s2. 24174.812722: bpf_trace_printk: xdp_load_balancer received packet
<idle>-0       [004] .Ns2. 24174.812729: bpf_trace_printk: Received Source IP: 0xa000001
<idle>-0       [004] .Ns2. 24174.812729: Received Destination IP: 0xa00000a
<idle>-0       [004] .Ns2. 24174.812731: Received Source MAC: de:ad:be:ef:0:1
<idle>-0       [004] .Ns2. 24174.812732: Received Destination MAC: de:ad:be:ef:0:10
<idle>-0       [004] .Ns2. 24174.812732: Packet from client
<idle>-0       [004] .Ns2. 24174.812734: bpf_trace_printk: Redirecting packet to new IP 0xa000002 from IP 0xa00000a
<idle>-0       [004] .Ns2. 24174.812735: New Dest MAC: de:ad:be:ef:0:2
<idle>-0       [004] .Ns2. 24174.812735: New Source MAC: de:ad:be:ef:0:10
```

### 調試問題

某些系統可能會因為類似於此[博客文章](https://fedepaol.github.io/blog/2023/09/11/xdp-ate-my-packets-and-how-i-debugged-it/)中描述的問題而導致數據包丟失或轉發失敗。您可以使用 `bpftrace` 跟蹤 XDP 錯誤進行調試：

```sh
sudo bpftrace -e 'tracepoint:xdp:xdp_bulk_tx{@redir_errno[-args->err] = count();}'
```

如果輸出如下所示：

```sh
@redir_errno[6]: 3
```

這表明與 XDP 數據包轉發相關的錯誤。錯誤代碼 `6` 通常指向可以進一步調查的特定轉發問題。

### 結論

本教程展示瞭如何使用 eBPF 設置一個簡單的 XDP 負載均衡器，以實現高效的流量分發。對於那些想了解更多關於 eBPF 知識的用戶，包括更高級的示例和教程，請訪問我們的 [https://github.com/eunomia-bpf/bpf-developer-tutorial](https://github.com/eunomia-bpf/bpf-developer-tutorial) 或我們的網站 [https://eunomia.dev/tutorials/](https://eunomia.dev/tutorials/)。

### 參考文獻

- [XDP 編程實踐教程](https://github.com/xdp-project/xdp-tutorial)