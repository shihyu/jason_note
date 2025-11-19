# eBPF 入門實踐教程二十：使用 eBPF 進行 tc 流量控制

## 背景

Linux 的流量控制子系統（Traffic Control, tc）在內核中存在了多年，類似於 iptables 和 netfilter 的關係，tc 也包括一個用戶態的 tc 程序和內核態的 trafiic control 框架，主要用於從速率、順序等方面控制數據包的發送和接收。從 Linux 4.1 開始，tc 增加了一些新的掛載點，並支持將 eBPF 程序作為 filter 加載到這些掛載點上。

## tc 概述

從協議棧上看，tc 位於鏈路層，其所在位置已經完成了 sk_buff 的分配，要晚於 xdp。為了實現對數據包發送和接收的控制，tc 使用隊列結構來臨時保存並組織數據包，在 tc 子系統中對應的數據結構和算法控制機制被抽象為 qdisc（Queueing discipline），其對外暴露數據包入隊和出隊的兩個回調接口，並在內部隱藏排隊算法實現。在 qdisc 中我們可以基於 filter 和 class 實現複雜的樹形結構，其中 filter 被掛載到 qdisc 或 class 上用於實現具體的過濾邏輯，返回值決定了該數據包是否屬於特定 class。

當數據包到達頂層 qdisc 時，其入隊接口被調用，其上掛載的 filter 被依次執行直到一個 filter 匹配成功；此後數據包被送入該 filter 指向的 class，進入該 class 配置的 qdisc 處理流程中。tc 框架提供了所謂 classifier-action 機制，即在數據包匹配到特定 filter 時執行該 filter 所掛載的 action 對數據包進行處理，實現了完整的數據包分類和處理機制。

現有的 tc 為 eBPF 提供了 direct-action 模式，它使得一個作為 filter 加載的 eBPF 程序可以返回像 `TC_ACT_OK` 等 tc action 的返回值，而不是像傳統的 filter 那樣僅僅返回一個 classid 並把對數據包的處理交給 action 模塊。現在，eBPF 程序可以被掛載到特定的 qdisc 上，並完成對數據包的分類和處理動作。

## 編寫 eBPF 程序

```c
#include <vmlinux.h>
#include <bpf/bpf_endian.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#define TC_ACT_OK 0
#define ETH_P_IP 0x0800 /* Internet Protocol packet */

/// @tchook {"ifindex":1, "attach_point":"BPF_TC_INGRESS"}
/// @tcopts {"handle":1, "priority":1}
SEC("tc")
int tc_ingress(struct __sk_buff *ctx)
{
    void *data_end = (void *)(__u64)ctx->data_end;
    void *data = (void *)(__u64)ctx->data;
    struct ethhdr *l2;
    struct iphdr *l3;

    if (ctx->protocol != bpf_htons(ETH_P_IP))
        return TC_ACT_OK;

    l2 = data;
    if ((void *)(l2 + 1) > data_end)
        return TC_ACT_OK;

    l3 = (struct iphdr *)(l2 + 1);
    if ((void *)(l3 + 1) > data_end)
        return TC_ACT_OK;

    bpf_printk("Got IP packet: tot_len: %d, ttl: %d", bpf_ntohs(l3->tot_len), l3->ttl);
    return TC_ACT_OK;
}

char __license[] SEC("license") = "GPL";
```

這段代碼定義了一個 eBPF 程序，它可以通過 Linux TC（Transmission Control）來捕獲數據包並進行處理。在這個程序中，我們限定了只捕獲 IPv4 協議的數據包，然後通過 bpf_printk 函數打印出數據包的總長度和 Time-To-Live（TTL）字段的值。

需要注意的是，我們在代碼中使用了一些 BPF 庫函數，例如 bpf_htons 和 bpf_ntohs 函數，它們用於進行網絡字節序和主機字節序之間的轉換。此外，我們還使用了一些註釋來為 TC 提供附加點和選項信息。例如，在這段代碼的開頭，我們使用了以下注釋：

```c
/// @tchook {"ifindex":1, "attach_point":"BPF_TC_INGRESS"}
/// @tcopts {"handle":1, "priority":1}
```

這些註釋告訴 TC 將 eBPF 程序附加到網絡接口的 ingress 附加點，並指定了 handle 和 priority 選項的值。關於 libbpf 中 tc 相關的 API 可以參考 [patchwork](https://patchwork.kernel.org/project/netdevbpf/patch/20210512103451.989420-3-memxor@gmail.com/) 中的介紹。

總之，這段代碼實現了一個簡單的 eBPF 程序，用於捕獲數據包並打印出它們的信息。

## 編譯運行

通過容器編譯：

```console
docker run -it -v `pwd`/:/src/ ghcr.io/eunomia-bpf/ecc-`uname -m`:latest
```

或是通過 `ecc` 編譯：

```console
$ ecc tc.bpf.c
Compiling bpf object...
Packing ebpf object and config into package.json...
```

並通過 `ecli` 運行：

```shell
sudo ecli run ./package.json
```

可以通過如下方式查看程序的輸出：

```console
$ sudo cat /sys/kernel/debug/tracing/trace_pipe
            node-1254811 [007] ..s1 8737831.671074: 0: Got IP packet: tot_len: 79, ttl: 64
            sshd-1254728 [006] ..s1 8737831.674334: 0: Got IP packet: tot_len: 79, ttl: 64
            sshd-1254728 [006] ..s1 8737831.674349: 0: Got IP packet: tot_len: 72, ttl: 64
            node-1254811 [007] ..s1 8737831.674550: 0: Got IP packet: tot_len: 71, ttl: 64
```

## 總結

本文介紹瞭如何向 TC 流量控制子系統掛載 eBPF 類型的 filter 來實現對鏈路層數據包的排隊處理。基於 eunomia-bpf 提供的通過註釋向 libbpf 傳遞參數的方案，我們可以將自己編寫的 tc BPF 程序以指定選項掛載到目標網絡設備，並藉助內核的 sk_buff 結構對數據包進行過濾處理。

如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。

## 參考

+ <http://just4coding.com/2022/08/05/tc/>
+ <https://arthurchiao.art/blog/understanding-tc-da-mode-zh/>
