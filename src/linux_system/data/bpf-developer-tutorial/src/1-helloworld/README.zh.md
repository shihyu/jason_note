# eBPF 入門開發實踐教程一：Hello World，基本框架和開發流程

在本篇博客中，我們將深入探討eBPF（Extended Berkeley Packet Filter）的基本框架和開發流程。eBPF是一種在Linux內核上運行的強大網絡和性能分析工具，它為開發者提供了在內核運行時動態加載、更新和運行用戶定義代碼的能力。這使得開發者可以實現高效、安全的內核級別的網絡監控、性能分析和故障排查等功能。

本文是eBPF入門開發實踐教程的第二篇，我們將重點關注如何編寫一個簡單的eBPF程序，並通過實際例子演示整個開發流程。在閱讀本教程之前，建議您先學習第一篇教程，以便對eBPF的基本概念有個大致的瞭解。

在開發eBPF程序時，有多種開發框架可供選擇，如 BCC（BPF Compiler Collection）libbpf、cilium/ebpf、eunomia-bpf 等。雖然不同工具的特點各異，但它們的基本開發流程大致相同。在接下來的內容中，我們將深入瞭解這些流程，並以 Hello World 程序為例，帶領讀者逐步掌握eBPF開發的基本技巧。

本教程將幫助您瞭解eBPF程序的基本結構、編譯和加載過程、用戶空間與內核空間的交互方式以及調試與優化技巧。通過學習本教程，您將掌握eBPF開發的基本知識，併為後續進一步學習和實踐奠定堅實的基礎。

## eBPF開發環境準備與基本開發流程

在開始編寫eBPF程序之前，我們需要準備一個合適的開發環境，並瞭解eBPF程序的基本開發流程。本部分將詳細介紹這些內容。

### 安裝必要的軟件和工具

要開發eBPF程序，您需要安裝以下軟件和工具：

- Linux 內核：由於eBPF是內核技術，因此您需要具備較新版本的Linux內核（至少 4.8 及以上版本，建議至少在 5.15 以上），以支持eBPF功能。
  - 建議使用最新的 Ubuntu 版本（例如 Ubuntu 23.10）以獲得最佳的學習體驗，較舊的內核 eBPF 功能支持可能相對不全。
- LLVM 和 Clang：這些工具用於編譯eBPF程序。安裝最新版本的LLVM和Clang可以確保您獲得最佳的eBPF支持。

eBPF 程序主要由兩部分構成：內核態部分和用戶態部分。內核態部分包含 eBPF 程序的實際邏輯，用戶態部分負責加載、運行和監控內核態程序。

當您選擇了合適的開發框架後，如BCC（BPF Compiler Collection）、libbpf、cilium/ebpf或eunomia-bpf等，您可以開始進行用戶態和內核態程序的開發。以BCC工具為例，我們將介紹eBPF程序的基本開發流程：

1. 安裝BCC工具：根據您的Linux發行版，按照BCC官方文檔的指南安裝BCC工具和相關依賴。
2. 編寫eBPF程序（C語言）：使用C語言編寫一個簡單的eBPF程序，例如Hello World程序。該程序可以在內核空間執行並完成特定任務，如統計網絡數據包數量。
3. 編寫用戶態程序（Python或C等）：使用Python、C等語言編寫用戶態程序，用於加載、運行eBPF程序以及與之交互。在這個程序中，您需要使用BCC提供的API來加載和操作內核態的eBPF程序。
4. 編譯eBPF程序：使用BCC工具，將C語言編寫的eBPF程序編譯成內核可以執行的字節碼。BCC會在運行時動態從源碼編譯eBPF程序。
5. 加載並運行eBPF程序：在用戶態程序中，使用BCC提供的API加載編譯好的eBPF程序到內核空間，然後運行該程序。
6. 與eBPF程序交互：用戶態程序通過BCC提供的API與eBPF程序交互，實現數據收集、分析和展示等功能。例如，您可以使用BCC API讀取eBPF程序中的map數據，以獲取網絡數據包統計信息。
7. 卸載eBPF程序：當不再需要eBPF程序時，用戶態程序應使用BCC API將其從內核空間卸載。
8. 調試與優化：使用 bpftool 等工具進行eBPF程序的調試和優化，提高程序性能和穩定性。

通過以上流程，您可以使用BCC工具開發、編譯、運行和調試eBPF程序。請注意，其他框架（如libbpf、cilium/ebpf和eunomia-bpf）的開發流程大致相似但略有不同，因此在選擇框架時，請參考相應的官方文檔和示例。

通過這個過程，你可以開發出一個能夠在內核中運行的 eBPF 程序。eunomia-bpf 是一個開源的 eBPF 動態加載運行時和開發工具鏈，它的目的是簡化 eBPF 程序的開發、構建、分發、運行。它基於 libbpf 的 CO-RE 輕量級開發框架，支持通過用戶態 WASM 虛擬機控制 eBPF 程序的加載和執行，並將預編譯的 eBPF 程序打包為通用的 JSON 或 WASM 模塊進行分發。我們會使用 eunomia-bpf 進行演示。

## 下載安裝 eunomia-bpf 開發工具

可以通過以下步驟下載和安裝 eunomia-bpf：

下載 ecli 工具，用於運行 eBPF 程序：

```console
$ wget https://aka.pw/bpf-ecli -O ecli && chmod +x ./ecli
$ ./ecli -h
Usage: ecli [--help] [--version] [--json] [--no-cache] url-and-args
```

下載編譯器工具鏈，用於將 eBPF 內核代碼編譯為 config 文件或 WASM 模塊：

```console
$ wget https://github.com/eunomia-bpf/eunomia-bpf/releases/latest/download/ecc && chmod +x ./ecc
$ ./ecc -h
eunomia-bpf compiler
Usage: ecc [OPTIONS] <SOURCE_PATH> [EXPORT_EVENT_HEADER]
```

注：假如在 aarch64 平臺上，請從 release 下載 [ecc-aarch64](https://github.com/eunomia-bpf/eunomia-bpf/releases/latest/download/ecc-aarch64) 和 [ecli-aarch64](https://github.com/eunomia-bpf/eunomia-bpf/releases/latest/download/ecli-aarch64).

也可以使用 docker 鏡像進行編譯：

```console
$ docker run -it -v `pwd`/:/src/ ghcr.io/eunomia-bpf/ecc-`uname -m`:latest # 使用 docker 進行編譯。`pwd` 應該包含 *.bpf.c 文件和 *.h 文件。
export PATH=PATH:~/.eunomia/bin
Compiling bpf object...
Packing ebpf object and config into /src/package.json...
```

## Hello World - minimal eBPF program

我們會先從一個簡單的 eBPF 程序開始，它會在內核中打印一條消息。我們會使用 eunomia-bpf 的編譯器工具鏈將其編譯為 bpf 字節碼文件，然後使用 ecli 工具加載並運行該程序。作為示例，我們可以暫時省略用戶態程序的部分。

```c
/* SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause) */
#define BPF_NO_GLOBAL_DATA
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

typedef unsigned int u32;
typedef int pid_t;
const pid_t pid_filter = 0;

char LICENSE[] SEC("license") = "Dual BSD/GPL";

SEC("tp/syscalls/sys_enter_write")
int handle_tp(void *ctx)
{
 pid_t pid = bpf_get_current_pid_tgid() >> 32;
 if (pid_filter && pid != pid_filter)
  return 0;
 bpf_printk("BPF triggered sys_enter_write from PID %d.\n", pid);
 return 0;
}
```

這段程序通過定義一個 handle_tp 函數並使用 SEC 宏把它附加到 sys_enter_write tracepoint（即在進入 write 系統調用時執行）。該函數通過使用 bpf_get_current_pid_tgid 和 bpf_printk 函數獲取調用 write 系統調用的進程 ID，並在內核日誌中打印出來。

- `bpf_printk()`： 一種將信息輸出到trace_pipe(/sys/kernel/debug/tracing/trace_pipe)簡單機制。 在一些簡單用例中這樣使用沒有問題， but它也有一些限制：最多3 參數； 第一個參數必須是%s(即字符串)；同時trace_pipe在內核中全局共享，其他並行使用trace_pipe的程序有可能會將 trace_pipe 的輸出擾亂。 一個更好的方式是通過 BPF_PERF_OUTPUT(), 稍後將會講到。
- `void *ctx`：ctx本來是具體類型的參數， 但是由於我們這裡沒有使用這個參數，因此就將其寫成void *類型。
- `return 0`;：必須這樣，返回0 (如果要知道why, 參考 #139  <https://github.com/iovisor/bcc/issues/139>)。

要編譯和運行這段程序，可以使用 ecc 工具和 ecli 命令。首先在 Ubuntu/Debian 上，執行以下命令：

```shell
sudo apt install clang llvm
```

使用 ecc 編譯程序：

```console
$ ./ecc minimal.bpf.c
Compiling bpf object...
Packing ebpf object and config into package.json...
```

或使用 docker 鏡像進行編譯：

```shell
docker run -it -v `pwd`/:/src/ ghcr.io/eunomia-bpf/ecc-`uname -m`:latest
```

然後使用 ecli 運行編譯後的程序：

```console
$ sudo ./ecli run package.json
Running eBPF program...
```

運行這段程序後，可以通過查看 /sys/kernel/debug/tracing/trace_pipe 文件來查看 eBPF 程序的輸出：

```console
$ sudo cat /sys/kernel/debug/tracing/trace_pipe | grep "BPF triggered sys_enter_write"
           <...>-3840345 [010] d... 3220701.101143: bpf_trace_printk: write system call from PID 3840345.
           <...>-3840345 [010] d... 3220701.101143: bpf_trace_printk: write system call from PID 3840345.
```

按 Ctrl+C 停止 ecli 進程之後，可以看到對應的輸出也停止。

注意：如果正在使用的 Linux 發行版（例如 Ubuntu ）默認情況下沒有啟用跟蹤子系統可能看不到任何輸出，使用以下指令打開這個功能：

```console
$ sudo su
# echo 1 > /sys/kernel/debug/tracing/tracing_on
```

## eBPF 程序的基本框架

如上所述， eBPF 程序的基本框架包括：

- 包含頭文件：需要包含 <linux/bpf.h> 和 <bpf/bpf_helpers.h> 等頭文件。
- 定義許可證：需要定義許可證，通常使用 "Dual BSD/GPL"。
- 定義 BPF 函數：需要定義一個 BPF 函數，例如其名稱為 handle_tp，其參數為 void *ctx，返回值為 int。通常用 C 語言編寫。
- 使用 BPF 助手函數：在例如 BPF 函數中，可以使用 BPF 助手函數 bpf_get_current_pid_tgid() 和 bpf_printk()。
- 返回值

## tracepoints

跟蹤點（tracepoints）是內核靜態插樁技術，在技術上只是放置在內核源代碼中的跟蹤函數，實際上就是在源碼中插入的一些帶有控制條件的探測點，這些探測點允許事後再添加處理函數。比如在內核中，最常見的靜態跟蹤方法就是 printk，即輸出日誌。又比如：在系統調用、調度程序事件、文件系統操作和磁盤 I/O 的開始和結束時都有跟蹤點。跟蹤點於 2009 年在 Linux 2.6.32 版本中首次提供。跟蹤點是一種穩定的 API，數量有限。

## GitHub 模板：輕鬆構建 eBPF 項目和開發環境

面對創建一個 eBPF 項目，您是否對如何開始搭建環境以及選擇編程語言感到困惑？別擔心，我們為您準備了一系列 GitHub 模板，以便您快速啟動一個全新的eBPF項目。只需在GitHub上點擊 `Use this template` 按鈕，即可開始使用。

- <https://github.com/eunomia-bpf/libbpf-starter-template>：基於C語言和 libbpf 框架的eBPF項目模板
- <https://github.com/eunomia-bpf/cilium-ebpf-starter-template>：基於Go語言和cilium/ebpf框架的eBPF項目模板
- <https://github.com/eunomia-bpf/libbpf-rs-starter-template>：基於Rust語言和libbpf-rs框架的eBPF項目模板
- <https://github.com/eunomia-bpf/eunomia-template>：基於C語言和eunomia-bpf框架的eBPF項目模板

這些啟動模板包含以下功能：

- 一個 Makefile，讓您可以一鍵構建項目
- 一個 Dockerfile，用於為您的 eBPF 項目自動創建一個容器化環境併發布到 Github Packages
- GitHub Actions，用於自動化構建、測試和發佈流程
- eBPF 開發所需的所有依賴項

> 通過將現有倉庫設置為模板，您和其他人可以快速生成具有相同基礎結構的新倉庫，從而省去了手動創建和配置的繁瑣過程。藉助 GitHub 模板倉庫，開發者可以專注於項目的核心功能和邏輯，而無需為基礎設置和結構浪費時間。更多關於模板倉庫的信息，請參閱官方文檔：<https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository>

## 總結

eBPF 程序的開發和使用流程可以概括為如下幾個步驟：

- 定義 eBPF 程序的接口和類型：這包括定義 eBPF 程序的接口函數，定義和實現 eBPF 內核映射（maps）和共享內存（perf events），以及定義和使用 eBPF 內核幫助函數（helpers）。
- 編寫 eBPF 程序的代碼：這包括編寫 eBPF 程序的主要邏輯，實現 eBPF 內核映射的讀寫操作，以及使用 eBPF 內核幫助函數。
- 編譯 eBPF 程序：這包括使用 eBPF 編譯器（例如 clang）將 eBPF 程序代碼編譯為 eBPF 字節碼，並生成可執行的 eBPF 內核模塊。ecc 本質上也是調用 clang 編譯器來編譯 eBPF 程序。
- 加載 eBPF 程序到內核：這包括將編譯好的 eBPF 內核模塊加載到 Linux 內核中，並將 eBPF 程序附加到指定的內核事件上。
- 使用 eBPF 程序：這包括監測 eBPF 程序的運行情況，並使用 eBPF 內核映射和共享內存進行數據交換和共享。
- 在實際開發中，還可能需要進行其他的步驟，例如配置編譯和加載參數，管理 eBPF 內核模塊和內核映射，以及使用其他高級功能等。

需要注意的是，BPF 程序的執行是在內核空間進行的，因此需要使用特殊的工具和技術來編寫、編譯和調試 BPF 程序。eunomia-bpf 是一個開源的 BPF 編譯器和工具包，它可以幫助開發者快速和簡單地編寫和運行 BPF 程序。

您還可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 以獲取更多示例和完整的教程，全部內容均已開源。我們會繼續分享更多有關 eBPF 開發實踐的內容，幫助您更好地理解和掌握 eBPF 技術。

> 原文地址：<https://eunomia.dev/zh/tutorials/1-helloworld/> 轉載請註明出處。
