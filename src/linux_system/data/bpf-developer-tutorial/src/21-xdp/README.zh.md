# eBPF 入門實踐教程二十一： 使用 XDP 進行可編程數據包處理

在本教程中，我們將介紹 XDP（eXpress Data Path），並通過一個簡單的例子幫助你入門。之後，我們將探討更高級的 XDP 應用，例如負載均衡器、防火牆及其他實際應用。如果你對 eBPF 或 XDP 感興趣，請在 [Github](https://github.com/eunomia-bpf/bpf-developer-tutorial) 上為我們點贊！

## 什麼是 XDP？

XDP 是 Linux 內核中的一種高性能可編程數據路徑，專為網絡接口級的數據包處理而設計。通過將 eBPF 程序直接附加到網絡設備驅動程序上，XDP 能夠在數據包到達內核網絡棧之前攔截並處理它們。這使得 XDP 能夠進行極低延遲和高效的數據包處理，非常適合如 DDoS 防護、負載均衡和流量過濾等任務。實際上，XDP 每核心的吞吐量可以高達 **每秒 2400 萬包（Mpps）**。

### 為什麼選擇 XDP？

XDP 運行在比傳統 Linux 網絡組件（如 cBPF）更低的層級，在網絡設備驅動程序的軟中斷上下文中執行。它能夠在數據包被內核標準網絡棧處理之前對其進行處理，避免了創建 Linux 中表示網絡數據包的 `skb_buff` 結構。這種早期處理為簡單但頻繁的操作（如丟棄惡意數據包或負載均衡服務器）帶來了顯著的性能提升。

與其他數據包處理機制相比，XDP 在性能和可用性之間取得了平衡，它利用了 Linux 內核的安全性和可靠性，同時通過可編程的 eBPF 提供了靈活性。

## XDP 與其他方法的比較

在 XDP 出現之前，一些解決方案通過完全繞過內核來加速數據包處理。其中一個顯著的例子是 **DPDK**（數據平面開發工具包）。DPDK 允許用戶空間應用程序直接控制網絡設備，從而實現非常高的性能。然而，這種方法也存在一些權衡：

1. **缺乏內核集成**：DPDK 及其他內核繞過解決方案無法利用現有的內核網絡功能，開發者必須在用戶空間重新實現許多協議和功能。

2. **安全邊界**：這些繞過技術破壞了內核的安全模型，使得難以利用內核提供的安全工具。
3. **用戶空間與內核的轉換開銷**：當用戶空間數據包處理需要與傳統內核網絡交互時（例如基於套接字的應用程序），數據包必須重新注入到內核中，增加了開銷和複雜性。
4. **專用 CPU 使用**：為了處理高流量，DPDK 和類似解決方案通常需要專用的 CPU 核心來處理數據包，這限制了通用系統的可擴展性和效率。

另一個替代 XDP 的方法是使用 Linux 網絡棧中的 **內核模塊** 或 **掛鉤**。雖然這種方法可以很好地集成現有的內核功能，但它需要大量的內核修改，且由於在數據包處理管道的後期運行，無法提供與 XDP 相同的性能優勢。

### XDP + eBPF 的優勢

XDP 與 eBPF 結合提供了介於內核繞過方案（如 DPDK）和內核集成方案之間的中間地帶。以下是 XDP + eBPF 脫穎而出的原因：

- **高性能**：通過在網絡接口卡（NIC）驅動程序級別攔截數據包，XDP 可以實現接近線速的性能，用於丟棄、重定向或負載均衡數據包，同時保持低資源消耗。
  
- **內核集成**：與 DPDK 不同，XDP 在 Linux 內核中工作，允許與現有的內核網絡棧和工具（如 `iptables`、`nftables` 或套接字）無縫交互。無需在用戶空間重新實現網絡協議。

- **安全性**：eBPF 虛擬機確保用戶定義的 XDP 程序是被隔離的，不會對內核造成不穩定影響。eBPF 的安全模型防止惡意或有缺陷的代碼損害系統，提供了一個安全的可編程數據包處理環境。

- **不需要專用 CPU**：XDP 允許數據包處理而無需將整個 CPU 核心專用於網絡任務。這提高了系統的整體效率，允許更靈活的資源分配。

總的來說，XDP + eBPF 提供了一種強大的可編程數據包處理解決方案，結合了高性能與內核集成的靈活性和安全性。它消除了完全繞過內核方案的缺點，同時保留了內核安全性和功能的優勢。

## XDP 的項目和應用案例

XDP 已經在許多高調的項目中得到應用，這些項目展示了它在實際網絡場景中的強大功能和靈活性：

### 1. **Cilium**

- **描述**：Cilium 是一個為雲原生環境（尤其是 Kubernetes）設計的開源網絡、安全和可觀測性工具。它利用 XDP 實現高性能的數據包過濾和負載均衡。
- **應用案例**：Cilium 將數據包過濾和安全策略卸載到 XDP，實現高吞吐量和低延遲的容器化環境流量管理，同時不犧牲可擴展性。
- **鏈接**：[Cilium](https://cilium.io/)

### 2. **Katran**

- **描述**：Katran 是由 Facebook 開發的第 4 層負載均衡器，優化了高可擴展性和性能。它使用 XDP 處理數據包轉發，開銷極小。
- **應用案例**：Katran 每秒處理數百萬個數據包，高效地將流量分配到後端服務器上，利用 XDP 在大規模數據中心中實現低延遲和高性能的負載均衡。
- **鏈接**：[Katran GitHub](https://github.com/facebookincubator/katran)

### 3. **Cloudflare 的 XDP DDoS 保護**

- **描述**：Cloudflare 已經實現了基於 XDP 的實時 DDoS 緩解。通過在 NIC 級別處理數據包，Cloudflare 能夠在惡意流量進入網絡棧之前過濾掉攻擊流量，最小化 DDoS 攻擊對其系統的影響。
- **應用案例**：Cloudflare 利用 XDP 在管道早期丟棄惡意數據包，保護其基礎設施免受大規模 DDoS 攻擊，同時保持對合法流量的高可用性。
- **鏈接**：[Cloudflare 博客關於 XDP](https://blog.cloudflare.com/l4drop-xdp-ebpf-based-ddos-mitigations/)

這些項目展示了 XDP 在不同領域的可擴展和高效的數據包處理能力，從安全和負載均衡到雲原生網絡。

### 為什麼選擇 XDP 而不是其他方法？

與傳統方法（如 `iptables`、`nftables` 或 `tc`）相比，XDP 提供了幾個明顯的優勢：

- **速度與低開銷**：XDP 直接在 NIC 驅動程序中運行，繞過了內核的大部分開銷，使數據包處理更快。
  
- **可定製性**：XDP 允許開發人員通過 eBPF 創建自定義的數據包處理程序，提供比傳統工具（如 `iptables`）更大的靈活性和細粒度控制。

- **資源效率**：XDP 不需要像 DPDK 等用戶空間解決方案那樣將整個 CPU 核心專用於數據包處理，因此它是高性能網絡的更高效選擇。

## 編寫 eBPF 程序

```C
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>

/// @ifindex 1
/// @flags 0
/// @xdpopts {"old_prog_fd":0}
SEC("xdp")
int xdp_pass(struct xdp_md* ctx) {
    void* data = (void*)(long)ctx->data;
    void* data_end = (void*)(long)ctx->data_end;
    int pkt_sz = data_end - data;

    bpf_printk("packet size is %d", pkt_sz);
    return XDP_PASS;
}

char __license[] SEC("license") = "GPL";
```

這是一段 C 語言實現的 eBPF 內核側代碼，它能夠通過 xdp 捕獲所有經過目標網絡設備的數據包，計算其大小並輸出到 `trace_pipe` 中。

值得注意的是，在代碼中我們使用了以下注釋：

```C
/// @ifindex 1
/// @flags 0
/// @xdpopts {"old_prog_fd":0}
```

這是由 eunomia-bpf 提供的功能，我們可以通過這樣的註釋告知 eunomia-bpf 加載器此 xdp 程序想要掛載的目標網絡設備編號，掛載的標誌和選項。

這些變量的設計基於 libbpf 提供的 API，可以通過 [patchwork](https://patchwork.kernel.org/project/netdevbpf/patch/20220120061422.2710637-2-andrii@kernel.org/#24705508) 查看接口的詳細介紹。

`SEC("xdp")` 宏指出 BPF 程序的類型，`ctx` 是此 BPF 程序執行的上下文，用於包處理流程。

在程序的最後，我們返回了 `XDP_PASS`，這表示我們的 xdp 程序會將經過目標網絡設備的包正常交付給內核的網絡協議棧。可以通過 [XDP actions](https://prototype-kernel.readthedocs.io/en/latest/networking/XDP/implementation/xdp_actions.html) 瞭解更多 xdp 的處理動作。

## 編譯運行

通過容器編譯：

```console
docker run -it -v `pwd`/:/src/ ghcr.io/eunomia-bpf/ecc-`uname -m`:latest
```

或是通過 `ecc` 編譯：

```console
$ ecc xdp.bpf.c
Compiling bpf object...
Packing ebpf object and config into package.json...
```

並通過 `ecli` 運行：

```console
sudo ecli run package.json
```

可以通過如下方式查看程序的輸出：

```console
$ sudo cat /sys/kernel/tracing/trace_pipe
            node-1939    [000] d.s11  1601.190413: bpf_trace_printk: packet size is 177
            node-1939    [000] d.s11  1601.190479: bpf_trace_printk: packet size is 66
     ksoftirqd/1-19      [001] d.s.1  1601.237507: bpf_trace_printk: packet size is 66
            node-1939    [000] d.s11  1601.275860: bpf_trace_printk: packet size is 344
```

## 總結

本文介紹瞭如何使用 xdp 來處理經過特定網絡設備的包，基於 eunomia-bpf 提供的通過註釋向 libbpf 傳遞參數的方案，我們可以將自己編寫的 xdp BPF 程序以指定選項掛載到目標設備，並在網絡包進入內核網絡協議棧之前就對其進行處理，從而獲取高性能的可編程包處理能力。

如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。

## 參考資料

- <http://arthurchiao.art/blog/xdp-paper-acm-2018-zh/>
- <http://arthurchiao.art/blog/linux-net-stack-implementation-rx-zh/>
- <https://github.com/xdp-project/xdp-tutorial/tree/master/basic01-xdp-pass>
