# 超越 eBPF 的極限：在內核模塊中定義自定義 kfunc

你是否曾經覺得 eBPF 的能力有限？也許你遇到了現有 eBPF 功能無法實現目標的情況。或許你需要與內核進行更深層次的交互，或者標準 eBPF 運行時無法解決的性能問題。如果你曾經希望在 eBPF 程序中擁有更多的靈活性和強大功能，那麼本教程正適合你。

## 引言：添加 `strstr` kfunc 以突破 eBPF 運行時的限制

**eBPF（擴展伯克利包過濾器）** 通過允許開發者在內核中運行受沙箱限制的程序，徹底改變了 Linux 系統編程。它在網絡、安全和可觀測性方面具有革命性的作用，能夠實現強大的功能，而無需修改內核源代碼或加載傳統的內核模塊。

但儘管 eBPF 非常強大，它也並非沒有侷限性：

- **功能差距：** 有時，eBPF 運行時的現有功能無法提供你所需的特定能力。
- **複雜需求：** 某些任務需要更復雜的內核交互，而 eBPF 無法開箱即用地處理這些需求。
- **性能問題：** 在某些情況下，eBPF 運行時的開銷會引入延遲，或者在高性能需求下效率不夠。

這些挑戰源於**整個 eBPF 運行時的限制**，而不僅僅是其輔助函數。那麼，如何在不修改內核本身的情況下克服這些障礙呢？

引入**kfunc（BPF 內核函數）**。通過在內核模塊中定義你自己的 kfunc，可以將 eBPF 的能力擴展到默認限制之外。這種方法讓你能夠：

- **增強功能：** 引入標準 eBPF 運行時中不可用的新操作。
- **定製行為：** 根據你的特定需求定製內核交互。
- **提升性能：** 通過在內核上下文中直接執行自定義代碼，優化關鍵路徑。

**在本教程中，我們將特別添加一個 `strstr` kfunc。** 由於 eBPF 的驗證器限制，直接在 eBPF 中實現字符串搜索是具有挑戰性的，而將其定義為 kfunc 則允許我們安全高效地繞過這些限制，執行更復雜的操作。

最棒的是，你可以在不修改核心內核的情況下實現這一目標，保持系統的穩定性和代碼的安全性。

在本教程中，我們將展示如何定義自定義 kfunc 以填補 eBPF 功能的任何空白。我們將逐步講解如何創建一個引入新 kfunc 的內核模塊，並演示如何在 eBPF 程序中使用它們。無論你是希望克服性能瓶頸，還是需要 eBPF 運行時未提供的功能，自定義 kfunc 都能為你的項目解鎖新的可能性。

## 理解 kfunc：擴展 eBPF 超越輔助函數

### 什麼是 kfunc？

**BPF 內核函數（kfuncs）** 是 Linux 內核中的專用函數，供 eBPF 程序使用。與標準的 eBPF 輔助函數不同，kfuncs 沒有穩定的接口，並且在不同的內核版本之間可能有所變化。這種可變性意味著使用 kfuncs 的 BPF 程序需要與內核更新同步更新，以保持兼容性和穩定性。

### 為什麼使用 kfuncs？

1. **擴展功能：** kfuncs 允許執行標準 eBPF 輔助函數無法完成的操作。
2. **定製化：** 定義針對特定用例量身定製的邏輯，增強 eBPF 程序的靈活性。
3. **安全與穩定：** 通過將 kfuncs 封裝在內核模塊中，避免直接修改核心內核，保持系統完整性。

### kfuncs 在 eBPF 中的角色

kfuncs 作為 eBPF 程序與更深層次內核功能之間的橋樑。它們允許 eBPF 程序執行更復雜的操作，通過暴露現有內核函數或引入專為 eBPF 交互設計的新包裝函數。這種集成在確保 eBPF 程序保持安全和可維護的同時，促進了更深入的內核交互。

需要注意的是，Linux 內核已經包含了大量的 kfuncs。這些內置的 kfuncs 覆蓋了廣泛的功能，大多數開發者無需定義新的 kfuncs 就能完成任務。然而，在現有 kfuncs 無法滿足特定需求的情況下，定義自定義 kfuncs 就變得必要。本教程將演示如何定義新的 kfuncs 以填補任何空白，確保你的 eBPF 程序能夠利用你所需的確切功能。eBPF 也可以擴展到用戶空間。在用戶空間 eBPF 運行時 [bpftime](https://github.com/eunomia-bpf/bpftime) 中，我們也在實現 ufuncs，它們類似於 kfuncs，但擴展了用戶空間應用程序。

## kfuncs 及其演變概述

要理解 kfuncs 的重要性，必須瞭解它們與 eBPF 輔助函數的演變關係。

![累計輔助函數和 kfunc 時間線](https://raw.githubusercontent.com/eunomia-bpf/code-survey/main/imgs/cumulative_helper_kfunc_timeline.png)

**關鍵要點：**

- **輔助函數的穩定性：** eBPF 輔助函數保持了高度的穩定性，新增內容較少。
- **kfuncs 的快速增長：** kfuncs 的採用和創建顯著增加，表明社區有興趣通過 kfuncs 擴展內核交互。
- **向更深層次內核集成的轉變：** 自 2023 年以來，新的用例主要利用 kfuncs 影響內核行為，顯示出通過 kfuncs 實現更深層次內核集成的趨勢。

這一趨勢凸顯了社區通過 kfuncs 更深入地與內核集成，推動 eBPF 能力邊界的決心。

## 定義你自己的 kfunc：分步指南

為了利用 kfuncs 的強大功能，你需要在內核模塊中定義它們。這個過程確保你的自定義函數能夠安全地暴露給 eBPF 程序，而無需修改核心內核。

### 編寫內核模塊

讓我們從創建一個簡單的內核模塊開始，該模塊定義一個 `strstr` kfunc。這個 kfunc 將執行子字符串搜索操作，作為理解機制的基礎。

#### **文件：`hello.c`**

```c
#include <linux/init.h>       // 模塊初始化宏
#include <linux/module.h>     // 加載模塊的核心頭文件
#include <linux/kernel.h>     // 內核日誌宏
#include <linux/bpf.h>
#include <linux/btf.h>
#include <linux/btf_ids.h>

/* 聲明 kfunc 原型 */
__bpf_kfunc int bpf_strstr(const char *str, u32 str__sz, const char *substr, u32 substr__sz);

/* 開始 kfunc 定義 */
__bpf_kfunc_start_defs();

/* 定義 bpf_strstr kfunc */
__bpf_kfunc int bpf_strstr(const char *str, u32 str__sz, const char *substr, u32 substr__sz)
{
    // 邊界情況：如果 substr 為空，返回 0（假設空字符串在開始處找到）
    if (substr__sz == 0)
    {
        return 0;
    }
    // 邊界情況：如果子字符串比主字符串長，則無法找到
    if (substr__sz > str__sz)
    {
        return -1; // 返回 -1 表示未找到
    }
    // 遍歷主字符串，考慮大小限制
    for (size_t i = 0; i <= str__sz - substr__sz; i++)
    {
        size_t j = 0;
        // 將子字符串與當前主字符串位置進行比較
        while (j < substr__sz && str[i + j] == substr[j])
        {
            j++;
        }
        // 如果整個子字符串都匹配
        if (j == substr__sz)
        {
            return i; // 返回第一次匹配的索引
        }
    }
    // 如果未找到子字符串，返回 -1
    return -1;
}

/* 結束 kfunc 定義 */
__bpf_kfunc_end_defs();

/* 定義 BTF kfuncs ID 集 */
BTF_KFUNCS_START(bpf_kfunc_example_ids_set)
BTF_ID_FLAGS(func, bpf_strstr)
BTF_KFUNCS_END(bpf_kfunc_example_ids_set)

/* 註冊 kfunc ID 集 */
static const struct btf_kfunc_id_set bpf_kfunc_example_set = {
    .owner = THIS_MODULE,
    .set = &bpf_kfunc_example_ids_set,
};

/* 模塊加載時執行的函數 */
static int __init hello_init(void)
{
    int ret;

    printk(KERN_INFO "Hello, world!\n");
    /* 註冊 BPF_PROG_TYPE_KPROBE 的 BTF kfunc ID 集 */
    ret = register_btf_kfunc_id_set(BPF_PROG_TYPE_KPROBE, &bpf_kfunc_example_set);
    if (ret)
    {
        pr_err("bpf_kfunc_example: 註冊 BTF kfunc ID 集失敗\n");
        return ret;
    }
    printk(KERN_INFO "bpf_kfunc_example: 模塊加載成功\n");
    return 0; // 成功返回 0
}

/* 模塊卸載時執行的函數 */
static void __exit hello_exit(void)
{
    /* 取消註冊 BTF kfunc ID 集 */
    unregister_btf_kfunc_id_set(BPF_PROG_TYPE_KPROBE, &bpf_kfunc_example_set);
    printk(KERN_INFO "再見，世界！\n");
}

/* 定義模塊的初始化和退出點的宏 */
module_init(hello_init);
module_exit(hello_exit);

MODULE_LICENSE("GPL");                 // 許可證類型（GPL）
MODULE_AUTHOR("Your Name");            // 模塊作者
MODULE_DESCRIPTION("一個簡單的模塊"); // 模塊描述
MODULE_VERSION("1.0");                 // 模塊版本
```

**代碼解釋：**

- **聲明 kfunc：** `__bpf_kfunc` 宏聲明一個 eBPF 程序可以調用的函數。在這裡，`bpf_strstr` 執行給定字符串中的子字符串搜索。
  
- **BTF 定義：** `__bpf_kfunc_start_defs` 和 `__bpf_kfunc_end_defs` 宏標示 kfunc 定義的開始和結束。`BTF_KFUNCS_START` 及相關宏幫助將 kfuncs 註冊到 BPF 類型格式（BTF）。
  
- **模塊初始化：** `hello_init` 函數註冊 kfunc ID 集，使 `bpf_strstr` 可用於 `BPF_PROG_TYPE_KPROBE` 類型的 eBPF 程序。
  
- **模塊清理：** `hello_exit` 函數確保在模塊移除時取消註冊 kfunc ID 集，保持系統整潔。

#### **文件：`Makefile`**

```makefile
obj-m += hello.o  # hello.o 是目標

# 啟用 BTF 生成
KBUILD_CFLAGS += -g -O2

all:
    make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
    make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
```

**Makefile 解釋：**

- **目標定義：** `obj-m += hello.o` 指定 `hello.o` 是要構建的模塊。
  
- **BTF 生成標誌：** `KBUILD_CFLAGS += -g -O2` 啟用調試信息和優化，便於 BTF 生成。
  
- **構建命令：**
  - **`all`:** 通過調用內核構建系統編譯內核模塊。
  - **`clean`:** 清理構建產物。

**注意：** 提供的代碼在 Linux 內核版本 **6.11** 上進行了測試。如果你使用的是較早的版本，可能需要實現一些變通方法，例如引用 `compact.h`。

### 編譯內核模塊

在內核模塊源代碼和 Makefile 就位後，按照以下步驟編譯模塊：

1. **導航到模塊目錄：**

   ```bash
   cd /path/to/bpf-developer-tutorial/src/43-kfuncs/module/
   ```

2. **編譯模塊：**

   ```bash
   make
   ```

   該命令將生成一個名為 `hello.ko` 的文件，即編譯後的內核模塊。

### 加載內核模塊

要將編譯好的模塊插入內核，使用 `insmod` 命令：

```bash
sudo insmod hello.ko
```

### 驗證模塊加載

加載模塊後，通過檢查內核日誌驗證其是否成功插入：

```bash
dmesg | tail
```

**預期輸出：**

```txt
[ 1234.5678] Hello, world!
[ 1234.5679] bpf_kfunc_example: 模塊加載成功
```

### 移除內核模塊

當不再需要該模塊時，使用 `rmmod` 命令卸載它：

```bash
sudo rmmod hello
```

**驗證移除：**

```bash
dmesg | tail
```

**預期輸出：**

```txt
[ 1234.9876] 再見，世界！
```

## 處理編譯錯誤

在編譯過程中，可能會遇到以下錯誤：

```txt
Skipping BTF generation for /root/bpf-developer-tutorial/src/43-kfuncs/module/hello.ko due to unavailability of vmlinux
```

**解決方案：**

1. **安裝 `dwarves` 包：**

   `dwarves` 包提供了生成 BTF 所需的工具。

   ```sh
   sudo apt install dwarves
   ```

2. **複製 `vmlinux` 文件：**

   確保包含 BTF 信息的 `vmlinux` 文件在構建目錄中可用。

   ```sh
   sudo cp /sys/kernel/btf/vmlinux /usr/lib/modules/$(uname -r)/build/
   ```

   該命令將 `vmlinux` 文件複製到適當的構建目錄，確保成功生成 BTF。

本教程的完整代碼可在 [bpf-developer-tutorial 倉庫](https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/43-kfuncs) 的 GitHub 上找到。此代碼在 Linux 內核版本 6.11 上進行了測試，對於較低版本，可能需要參考 `compact.h` 進行一些修改。

## 在 eBPF 程序中使用自定義 kfunc

有了定義自定義 `strstr` kfunc 的內核模塊後，下一步是創建一個利用此函數的 eBPF 程序。此交互展示了 kfuncs 引入的增強功能。

### 編寫 eBPF 程序

創建一個附加到 `do_unlinkat` 內核函數並使用自定義 `bpf_strstr` kfunc 的 eBPF 程序。

#### **文件：`kfunc.c`**

```c
/* SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause) */
#define BPF_NO_GLOBAL_DATA
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

typedef unsigned int u32;
typedef long long s64;

/* 聲明外部 kfunc */
extern int bpf_strstr(const char *str, u32 str__sz, const char *substr, u32 substr__sz) __ksym;

char LICENSE[] SEC("license") = "Dual BSD/GPL";

SEC("kprobe/do_unlinkat")
int handle_kprobe(struct pt_regs *ctx)
{
    pid_t pid = bpf_get_current_pid_tgid() >> 32;
    char str[] = "Hello, world!";
    char substr[] = "wor";
    int result = bpf_strstr(str, sizeof(str) - 1, substr, sizeof(substr) - 1);
    if (result != -1)
    {
        bpf_printk("'%s' found in '%s' at index %d\n", substr, str, result);
    }
    bpf_printk("Hello, world! (pid: %d) bpf_strstr %d\n", pid, result);
    return 0;
}
```

**eBPF 代碼解釋：**

- **外部 kfunc 聲明：** `extern` 關鍵字聲明 `bpf_strstr` 函數，使其在 eBPF 程序中可用。
  
- **Kprobe 附加：** `SEC("kprobe/do_unlinkat")` 宏將 eBPF 程序附加到 `do_unlinkat` 內核函數。每次調用 `do_unlinkat` 時，`handle_kprobe` 函數都會執行。
  
- **使用 kfunc：** 在 `handle_kprobe` 中，eBPF 程序調用 `bpf_strstr`，傳入四個參數：
  - `str`: 要搜索的主字符串。
  - `str__sz`: 主字符串的大小。
  - `substr`: 要搜索的子字符串。
  - `substr__sz`: 子字符串的大小。

  結果（子字符串在主字符串中的首次出現索引，或 -1 表示未找到）然後通過 `bpf_printk` 打印，顯示 PID 和結果。

**重要提示：** 由於驗證器限制，直接在 eBPF 中實現類似 `strstr` 的函數具有挑戰性，因為這限制了循環和複雜的內存訪問。通過將 `strstr` 實現為 kfunc，我們繞過了這些限制，使得在 eBPF 程序中執行更復雜和高效的字符串操作成為可能。

### 編譯 eBPF 程序

要編譯 eBPF 程序，確保你已安裝必要的工具，如 `clang` 和 `llvm`。以下是編譯程序的步驟：

1. **導航到 eBPF 程序目錄：**

   ```bash
   cd /path/to/bpf-developer-tutorial/src/43-kfuncs/
   ```

2. **為 eBPF 程序創建一個 `Makefile`：**

   ```makefile
   # 文件：Makefile

   CLANG ?= clang
   LLVM_STRIP ?= llvm-strip
   BPF_TARGET := bpf

   CFLAGS := -O2 -g -target $(BPF_TARGET) -Wall -Werror -I/usr/include

   all: kfunc.o

   kfunc.o: kfunc.c
       $(CLANG) $(CFLAGS) -c $< -o $@

   clean:
       rm -f kfunc.o
   ```

3. **編譯 eBPF 程序：**

   ```bash
   make
   ```

   該命令將生成一個名為 `kfunc.o` 的文件，即編譯後的 eBPF 對象文件。

### 運行 eBPF 程序

假設你有一個用戶空間應用程序或工具來加載和附加 eBPF 程序，你可以執行它以觀察 eBPF 程序與自定義 kfunc 之間的交互。

**示例輸出：**

```bash
# sudo ./kfunc
BPF 程序已加載併成功附加。按 Ctrl-C 退出。
```

然後，當調用 `do_unlinkat` 函數時（例如，當文件被取消鏈接時），你可以檢查內核日誌：

```bash
dmesg | tail
```

**預期輸出：**

```txt
[ 1234.5678] 'wor' found in 'Hello, world!' at index 7
[ 1234.5679] Hello, world! (pid: 2075) bpf_strstr 7
```

**輸出解釋：**

每次內核調用 `do_unlinkat` 函數時，eBPF 程序都會打印一條消息，指示進程的 PID 以及 kfunc 調用的結果。在此示例中，子字符串 `"wor"` 在字符串 `"Hello, world!"` 的索引 `7` 處被找到。

## 總結與結論

在本教程中，我們深入探討了通過定義和使用自定義內核函數（kfuncs）來擴展 eBPF 的能力。以下是我們涵蓋的內容回顧：

- **理解 kfuncs：** 理解了 kfuncs 的概念及其在標準輔助函數之外增強 eBPF 的角色。
- **定義 kfuncs：** 創建了一個內核模塊，定義了自定義的 `strstr` kfunc，確保其能夠安全地暴露給 eBPF 程序，而無需修改核心內核。
- **編寫包含 kfuncs 的 eBPF 程序：** 開發了一個利用自定義 kfunc 的 eBPF 程序，展示了增強的功能。
- **編譯與執行：** 提供了逐步指南，編譯、加載並運行內核模塊和 eBPF 程序，確保你可以在自己的系統上覆制設置。
- **錯誤處理：** 解決了潛在的編譯問題，並提供瞭解決方案，確保順利的開發體驗。

**關鍵要點：**

- **克服輔助函數的限制：** kfuncs 彌合了標準 eBPF 輔助函數留下的空白，提供了針對特定需求的擴展功能。
- **維護系統穩定性：** 通過將 kfuncs 封裝在內核模塊中，確保系統穩定性，而無需對內核進行侵入性更改。
- **社區驅動的演變：** kfuncs 的快速增長和採用凸顯了 eBPF 社區致力於通過 kfuncs 推動內核級編程可能性的決心。
- **利用現有 kfuncs：** 在定義新的 kfuncs 之前，探索內核提供的現有 kfuncs。它們涵蓋了廣泛的功能，減少了除非絕對必要，否則無需創建自定義函數的需求。

**準備好進一步提升你的 eBPF 技能了嗎？** [訪問我們的教程倉庫](https://github.com/eunomia-bpf/bpf-developer-tutorial)並[探索我們網站上的更多教程](https://eunomia.dev/tutorials/)。深入豐富的示例，深化你的理解，併為 eBPF 的動態世界做出貢獻！

祝你在 eBPF 的旅程中愉快！

## 參考資料

- [BPF 內核函數文檔](https://docs.kernel.org/bpf/kfuncs.html)
- [eBPF kfuncs 指南](https://docs.ebpf.io/linux/kfuncs/)

## 附加資源

如果你想了解更多關於 eBPF 的知識和實踐，可以訪問我們的開源教程代碼倉庫 [bpf-developer-tutorial](https://github.com/eunomia-bpf/bpf-developer-tutorial) 或訪問我們的網站 [eunomia.dev/tutorials](https://eunomia.dev/tutorials/) 以獲取更多示例和完整代碼。
