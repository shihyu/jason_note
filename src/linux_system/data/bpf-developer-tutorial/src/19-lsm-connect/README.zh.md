# eBPF 入門實踐教程：使用 LSM 進行安全檢測防禦

eBPF (擴展的伯克利數據包過濾器) 是一項強大的網絡和性能分析工具，被廣泛應用在 Linux 內核上。eBPF 使得開發者能夠動態地加載、更新和運行用戶定義的代碼，而無需重啟內核或更改內核源代碼。這個特性使得 eBPF 能夠提供極高的靈活性和性能，使其在網絡和系統性能分析方面具有廣泛的應用。安全方面的 eBPF 應用也是如此，本文將介紹如何使用 eBPF LSM（Linux Security Modules）機制實現一個簡單的安全檢查程序。

## 背景

LSM 從 Linux 2.6 開始成為官方內核的一個安全框架，基於此的安全實現包括 SELinux 和 AppArmor 等。在 Linux 5.7 引入 BPF LSM 後，系統開發人員已經能夠自由地實現函數粒度的安全檢查能力，本文就提供了這樣一個案例：限制通過 socket connect 函數對特定 IPv4 地址進行訪問的 BPF LSM 程序。（可見其控制精度是很高的）

## LSM 概述

LSM（Linux Security Modules）是 Linux 內核中用於支持各種計算機安全模型的框架。LSM 在 Linux 內核安全相關的關鍵路徑上預置了一批 hook 點，從而實現了內核和安全模塊的解耦，使不同的安全模塊可以自由地在內核中加載/卸載，無需修改原有的內核代碼就可以加入安全檢查功能。

在過去，使用 LSM 主要通過配置已有的安全模塊（如 SELinux 和 AppArmor）或編寫自己的內核模塊；而在 Linux 5.7 引入 BPF LSM 機制後，一切都變得不同了：現在，開發人員可以通過 eBPF 編寫自定義的安全策略，並將其動態加載到內核中的 LSM 掛載點，而無需配置或編寫內核模塊。

現在 LSM 支持的 hook 點包括但不限於：

+ 對文件的打開、創建、刪除和移動等；
+ 文件系統的掛載；
+ 對 task 和 process 的操作；
+ 對 socket 的操作（創建、綁定 socket，發送和接收消息等）；

更多 hook 點可以參考 [lsm_hooks.h](https://github.com/torvalds/linux/blob/master/include/linux/lsm_hooks.h)。

## 確認 BPF LSM 是否可用

首先，請確認內核版本高於 5.7。接下來，可以通過

```console
$ cat /boot/config-$(uname -r) | grep BPF_LSM
CONFIG_BPF_LSM=y
```

判斷是否內核是否支持 BPF LSM。上述條件都滿足的情況下，可以通過

```console
$ cat /sys/kernel/security/lsm
ndlock,lockdown,yama,integrity,apparmor
```

查看輸出是否包含 bpf 選項，如果輸出不包含（像上面的例子），可以通過修改 `/etc/default/grub`：

```conf
GRUB_CMDLINE_LINUX="lsm=ndlock,lockdown,yama,integrity,apparmor,bpf"
```

並通過 `update-grub2` 命令更新 grub 配置（不同系統的對應命令可能不同），然後重啟系統。

## 編寫 eBPF 程序

```C
// lsm-connect.bpf.c
#include "vmlinux.h"
#include <bpf/bpf_core_read.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

char LICENSE[] SEC("license") = "GPL";

#define EPERM 1
#define AF_INET 2

const __u32 blockme = 16843009; // 1.1.1.1 -> int

SEC("lsm/socket_connect")
int BPF_PROG(restrict_connect, struct socket *sock, struct sockaddr *address, int addrlen, int ret)
{
    // Satisfying "cannot override a denial" rule
    if (ret != 0)
    {
        return ret;
    }

    // Only IPv4 in this example
    if (address->sa_family != AF_INET)
    {
        return 0;
    }

    // Cast the address to an IPv4 socket address
    struct sockaddr_in *addr = (struct sockaddr_in *)address;

    // Where do you want to go?
    __u32 dest = addr->sin_addr.s_addr;
    bpf_printk("lsm: found connect to %d", dest);

    if (dest == blockme)
    {
        bpf_printk("lsm: blocking %d", dest);
        return -EPERM;
    }
    return 0;
}

```

這是一段 C 實現的 eBPF 內核側代碼，它會阻礙所有試圖通過 socket 對 1.1.1.1 的連接操作，其中：

+ `SEC("lsm/socket_connect")` 宏指出該程序期望的掛載點；
+ 程序通過 `BPF_PROG` 宏定義（詳情可查看 [tools/lib/bpf/bpf_tracing.h](https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/tree/tools/lib/bpf/bpf_tracing.h)）；
+ `restrict_connect` 是 `BPF_PROG` 宏要求的程序名；
+ `ret` 是該掛載點上（潛在的）當前函數之前的 LSM 檢查程序的返回值；

整個程序的思路不難理解：

+ 首先，若其他安全檢查函數返回值不為 0（不通過），則無需檢查，直接返回不通過；
+ 接下來，判斷是否為 IPV4 的連接請求，並比較試圖連接的地址是否為 1.1.1.1；
+ 若請求地址為 1.1.1.1 則拒絕連接，否則允許連接；

在程序運行期間，所有通過 socket 的連接操作都會被輸出到 `/sys/kernel/debug/tracing/trace_pipe`。

## 編譯運行

通過容器編譯：

```console
docker run -it -v `pwd`/:/src/ ghcr.io/eunomia-bpf/ecc-`uname -m`:latest
```

或是通過 `ecc` 編譯：

```console
$ ecc lsm-connect.bpf.c
Compiling bpf object...
Packing ebpf object and config into package.json...
```

並通過 `ecli` 運行：

```shell
sudo ecli run package.json
```

接下來，可以打開另一個 terminal，並嘗試訪問 1.1.1.1：

```console
$ ping 1.1.1.1
ping: connect: Operation not permitted
$ curl 1.1.1.1
curl: (7) Couldn't connect to server
$ wget 1.1.1.1
--2023-04-23 08:41:18--  (try: 2)  http://1.1.1.1/
Connecting to 1.1.1.1:80... failed: Operation not permitted.
Retrying.
```

同時，我們可以查看 `bpf_printk` 的輸出：

```console
$ sudo cat /sys/kernel/debug/tracing/trace_pipe
            ping-7054    [000] d...1  6313.430872: bpf_trace_printk: lsm: found connect to 16843009
            ping-7054    [000] d...1  6313.430874: bpf_trace_printk: lsm: blocking 16843009
            curl-7058    [000] d...1  6316.346582: bpf_trace_printk: lsm: found connect to 16843009
            curl-7058    [000] d...1  6316.346584: bpf_trace_printk: lsm: blocking 16843009
            wget-7061    [000] d...1  6318.800698: bpf_trace_printk: lsm: found connect to 16843009
            wget-7061    [000] d...1  6318.800700: bpf_trace_printk: lsm: blocking 16843009
```

完整源代碼：<https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/19-lsm-connect>

## 總結

本文介紹瞭如何使用 BPF LSM 來限制通過 socket 對特定 IPv4 地址的訪問。我們可以通過修改 GRUB 配置文件來開啟 LSM 的 BPF 掛載點。在 eBPF 程序中，我們通過 `BPF_PROG` 宏定義函數，並通過 `SEC` 宏指定掛載點；在函數實現上，遵循 LSM 安全檢查模塊中 "cannot override a denial" 的原則，並根據 socket 連接請求的目的地址對該請求進行限制。

如果您希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。

## 參考

+ <https://github.com/leodido/demo-cloud-native-ebpf-day>
+ <https://aya-rs.dev/book/programs/lsm/#writing-lsm-bpf-program>
