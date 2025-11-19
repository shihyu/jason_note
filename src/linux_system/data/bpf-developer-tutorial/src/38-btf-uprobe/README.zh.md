# 藉助 eBPF 和 BTF，讓用戶態也能一次編譯、到處運行

在現代 Linux 系統中，eBPF（擴展的 Berkeley Packet Filter）是一項強大而靈活的技術。它允許在內核中運行沙盒化程序，類似於虛擬機環境，為擴展內核功能提供了一種既安全又不會導致系統崩潰或安全風險的方法。

eBPF 中的 “co-re” 代表“一次編譯、到處運行”。這是其關鍵特徵之一，用於解決 eBPF 程序在不同內核版本間兼容性的主要挑戰。eBPF 的 CO-RE 功能可以實現在不同的內核版本上運行同一 eBPF 程序，而無需重新編譯。

利用 eBPF 的 Uprobe 功能，可以追蹤用戶空間應用程序並訪問其內部數據結構。然而，用戶空間應用程序的 CO-RE 實踐目前尚不完善。本文將介紹一種新方法，利用 CO-RE 為用戶空間應用程序確保 eBPF 程序在不同應用版本間的兼容性，從而避免了多次編譯的需求。例如，在從加密流量中捕獲 SSL/TLS 明文數據時，你或許不需要為每個版本的 OpenSSL 維護一個單獨的 eBPF 程序。

為了在用戶空間應用程序中實現eBPF的“一次編譯、到處運行”(Co-RE)特性，我們需要利用BPF類型格式(BTF)來克服傳統eBPF程序的一些限制。這種方法的關鍵在於為用戶空間程序提供與內核類似的類型信息和兼容性支持，從而使得eBPF程序能夠更靈活地應對不同版本的用戶空間應用和庫。

本文是eBPF開發者教程的一部分，詳細內容可訪問[https://eunomia.dev/tutorials/](https://eunomia.dev/tutorials/)。本文完整的代碼請查看 <https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/38-btf-uprobe> 。

## 為什麼我們需要CO-RE？

- **內核依賴性**：傳統的eBPF程序和它們被編譯的特定Linux內核版本緊密耦合。這是因為它們依賴於內核的特定內部數據結構和API，這些可能在內核版本間變化。
- **可移植性問題**：如果你想在帶有不同內核版本的不同Linux系統上運行一個eBPF程序，你通常需要為每個內核版本重新編譯eBPF程序，這是一個麻煩而低效的過程。

### Co-RE的解決方案

- **抽象內核依賴性**：Co-RE使eBPF程序更具可移植性，通過使用BPF類型格式(BTF)和重定位來抽象特定的內核依賴。
- **BPF類型格式（BTF）**：BTF提供了關於內核中數據結構和函數的豐富類型信息。這些元數據允許eBPF程序在運行時理解內核結構的佈局。
- **重定位**：編譯支持Co-RE的eBPF程序包含在加載時解析的重定位。這些重定位根據運行內核的實際佈局和地址調整程序對內核數據結構和函數的引用。

### Co-RE的優點

1. **編寫一次，任何地方運行**：編譯有Co-RE的eBPF程序可以在不同的內核版本上運行，無需重新編譯。這大大簡化了在多樣環境中部署和維護eBPF程序。
2. **安全和穩定**：Co-RE保持了eBPF的安全性，確保程序不會導致內核崩潰，遵守安全約束。
3. **簡單的開發**：開發者不需要關注每個內核版本的具體情況，這簡化了eBPF程序的開發。

## 用戶空間應用程序CO-RE的問題

eBPF也支持追蹤用戶空間應用程序。Uprobe是一個用戶空間探針，允許對用戶空間程序進行動態儀表裝置。探針位置包括函數入口、特定偏移和函數返回。

BTF是為內核設計的，生成自vmlinux，它可以幫助eBPF程序方便地兼容不同的內核版本。但是，用戶空間應用程序也需要CO-RE。例如，SSL/TLS uprobe被廣泛用於從加密流量中捕獲明文數據。它是用用戶空間庫實現的，如OpenSSL、GnuTLS、NSS等。用戶空間應用程序和庫也有各種版本，如果我們需要為每個版本編譯和維護eBPF程序，那就會很複雜。

下面是一些新的工具和方法，可以幫助我們為用戶空間應用程序啟用CO-RE。

## 用戶空間程序的BTF

這是一個簡單的uprobe例子，它可以捕獲用戶空間程序的`add_test`函數的調用和參數。你可以在`uprobe.bpf.c`中添加`#define BPF_NO_PRESERVE_ACCESS_INDEX`來確保eBPF程序可以在沒有`struct data`的BTF的情況下編譯。

```c
#define BPF_NO_GLOBAL_DATA
#define BPF_NO_PRESERVE_ACCESS_INDEX
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

struct data {
        int a;
        int c;
        int d;
};

SEC("uprobe/examples/btf-base:add_test")
int BPF_UPROBE(add_test, struct data *d)
{
    int a = 0, c = 0;
    bpf_probe_read_user(&a, sizeof(a), &d->a);
    bpf_probe_read_user(&c, sizeof(c), &d->c);
    bpf_printk("add_test(&d) %d + %d = %d\n", a, c,  a + c);
    return a + c;
}

char LICENSE[] SEC("license") = "Dual BSD/GPL";
```

然後，我們有兩個不同版本的用戶空間程序，`examples/btf-base`和`examples/btf-base-new`。兩個版本中的struct `data`是不同的。

`examples/btf-base`：

```c
// use a different struct
struct data {
        int a;
        int c;
        int d;
};

int add_test(struct data *d) {
    return d->a + d->c;
}

int main(int argc, char **argv) {
    struct data d = {1, 3, 4};
    printf("add_test(&d) = %d\n", add_test(&d));
    return 0;
}
```

`examples/btf-base-new`：

```c
struct data {
        int a;
        int b;
        int c;
        int d;
};

int add_test(struct data *d) {
    return d->a + d->c;
}

int main(int argc, char **argv) {
    struct data d = {1, 2, 3, 4};
    printf("add_test(&d) = %d\n", add_test(&d));
    return 0;
}
```

我們可以使用pahole和clang來生成每個版本的btf。製作示例並生成btf:

```sh
make -C examples # it's like: pahole --btf_encode_detached base.btf btf-base.o
```

然後我們執行eBPF程序和用戶空間程序。 對於 `btf-base`：

```sh
sudo ./uprobe examples/btf-base 
```

也是用戶空間程序：

```console
$ examples/btf-base
add_test(&d) = 4
```

我們將看到：

```console
$ sudo cat /sys/kernel/debug/tracing/trace_pipe\
           <...>-25458   [000] ...11 27694.081465: bpf_trace_printk: add_test(&d) 1 + 3 = 4
```

對於 `btf-base-new`：

```sh
sudo ./uprobe examples/btf-base-new
```

同時也是用戶空間程序：

```console
$ examples/btf-base-new
add_test(&d) = 4
```

但我們可以看到：

```console
$ sudo cat /sys/kernel/debug/tracing/trace_pipe\
           <...>-25809   [001] ...11 27828.314224: bpf_trace_printk: add_test(&d) 1 + 2 = 3
```

結果是不同的，因為兩個版本中的struct `data`是不同的。eBPF程序無法與不同版本的用戶空間程序兼容，我們獲取到了錯誤的結構體偏移量，也會導致我們追蹤失敗。

## 使用用戶空間程序的BTF

在`uprobe.bpf.c`中註釋掉`#define BPF_NO_PRESERVE_ACCESS_INDEX` ，以確保eBPF程序可以以`struct data`的BTF編譯。

```c
#define BPF_NO_GLOBAL_DATA
// #define BPF_NO_PRESERVE_ACCESS_INDEX
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#ifndef BPF_NO_PRESERVE_ACCESS_INDEX
#pragma clang attribute push (__attribute__((preserve_access_index)), apply_to = record)
#endif

struct data {
        int a;
        int c;
        int d;
};

#ifndef BPF_NO_PRESERVE_ACCESS_INDEX
#pragma clang attribute pop
#endif

SEC("uprobe/examples/btf-base:add_test")
int BPF_UPROBE(add_test, struct data *d)
{
    int a = 0, c = 0;
    bpf_probe_read_user(&a, sizeof(a), &d->a);
    bpf_probe_read_user(&c, sizeof(c), &d->c);
    bpf_printk("add_test(&d) %d + %d = %d\n", a, c,  a + c);
    return a + c;
}

char LICENSE[] SEC("license") = "Dual BSD/GPL";
```

`struct data`的記錄在eBPF程序中被保留下來。然後，我們可以使用 `btf-base.btf`來編譯eBPF程序。

這時，如果未提供用戶態的 BTF 信息，會導致驗證失敗：

```console
# ./uprobe examples/btf-base 
.....
; int BPF_UPROBE(add_test, struct data *d) @ uprobe.bpf.c:23
0: (79) r6 = *(u64 *)(r1 +112)        ; R1=ctx() R6_w=scalar()
1: (b7) r7 = 0                        ; R7_w=0
; int a = 0, c = 0; @ uprobe.bpf.c:25
2: (63) *(u32 *)(r10 -4) = r7         ; R7_w=0 R10=fp0 fp-8=0000????
3: (63) *(u32 *)(r10 -8) = r7         ; R7_w=0 R10=fp0 fp-8=00000
4: <invalid CO-RE relocation>
failed to resolve CO-RE relocation <byte_off> [17] struct data.a (0:0 @ offset 0)
processed 5 insns (limit 1000000) max_states_per_insn 0 total_states 0 peak_states 0 mark_read 0
-- END PROG LOAD LOG --
libbpf: prog 'add_test': failed to load: -22
libbpf: failed to load object 'uprobe_bpf'
libbpf: failed to load BPF skeleton 'uprobe_bpf': -22
Failed to load and verify BPF skeleton
```

將用戶btf與內核btf合併，這樣我們就有了一個完整的內核和用戶空間的btf:

```sh
./merge-btf /sys/kernel/btf/vmlinux examples/base.btf target-base.btf
```

然後我們使用用戶空間程序執行eBPF程序。 對於 `btf-base`：

```console
$ sudo ./uprobe examples/btf-base target-base.btf
...
libbpf: prog 'add_test': relo #1: patched insn #4 (ALU/ALU64) imm 0 -> 0
libbpf: prog 'add_test': relo #2: <byte_off> [7] struct data.c (0:1 @ offset 4)
libbpf: prog 'add_test': relo #2: matching candidate #0 <byte_off> [133110] struct data.c (0:1 @ offset 4)
libbpf: prog 'add_test': relo #2: patched insn #11 (ALU/ALU64) imm 4 -> 4
...
```

執行用戶空間程序並獲取結果：

```console
$ sudo cat /sys/kernel/debug/tracing/trace_pipe
[sudo] password for yunwei37: 
           <...>-26740   [001] ...11 28180.156220: bpf_trace_printk: add_test(&d) 1 + 3 = 4
```

還可以對另一個版本的用戶空間程序`btf-base-new`做同樣的操作:

```console
$ ./merge-btf /sys/kernel/btf/vmlinux examples/base-new.btf target-base-new.btf
$ sudo ./uprobe examples/btf-base-new target-base-new.btf
....
libbpf: sec 'uprobe/examples/btf-base:add_test': found 3 CO-RE relocations
libbpf: CO-RE relocating [2] struct pt_regs: found target candidate [357] struct pt_regs in [vmlinux]
libbpf: prog 'add_test': relo #0: <byte_off> [2] struct pt_regs.di (0:14 @ offset 112)
libbpf: prog 'add_test': relo #0: matching candidate #0 <byte_off> [357] struct pt_regs.di (0:14 @ offset 112)
libbpf: prog 'add_test': relo #0: patched insn #0 (LDX/ST/STX) off 112 -> 112
libbpf: CO-RE relocating [7] struct data: found target candidate [133110] struct data in [vmlinux]
libbpf: prog 'add_test': relo #1: <byte_off> [7] struct data.a (0:0 @ offset 0)
libbpf: prog 'add_test': relo #1: matching candidate #0 <byte_off> [133110] struct data.a (0:0 @ offset 0)
libbpf: prog 'add_test': relo #1: patched insn #4 (ALU/ALU64) imm 0 -> 0
libbpf: prog 'add_test': relo #2: <byte_off> [7] struct data.c (0:1 @ offset 4)
libbpf: prog 'add_test': relo #2: matching candidate #0 <byte_off> [133110] struct data.c (0:2 @ offset 8)
libbpf: prog 'add_test': relo #2: patched insn #11 (ALU/ALU64) imm 4 -> 8
libbpf: elf: symbol address match for 'add_test' in 'examples/btf-base-new': 0x1140
Successfully started! Press Ctrl+C to stop.
```

結果是正確的：

```console
$ sudo cat /sys/kernel/debug/tracing/trace_pipe
[sudo] password for yunwei37: 
           <...>-26740   [001] ...11 28180.156220: bpf_trace_printk: add_test(&d) 1 + 3 = 4
```

我們的 eBPF 追蹤程序也幾乎不需要進行任何修改，只需要把包含 kernel 和用戶態結構體偏移量的 BTF 加載進來即可。這和舊版本內核上沒有 btf 信息的使用方式是一樣的:

```c
 LIBBPF_OPTS(bpf_object_open_opts , opts,
 );
 LIBBPF_OPTS(bpf_uprobe_opts, uprobe_opts);
 if (argc != 3 && argc != 2) {
  fprintf(stderr, "Usage: %s <example-name> [<external-btf>]\n", argv[0]);
  return 1;
 }
 if (argc == 3)
  opts.btf_custom_path = argv[2];

 /* Set up libbpf errors and debug info callback */
 libbpf_set_print(libbpf_print_fn);

 /* Cleaner handling of Ctrl-C */
 signal(SIGINT, sig_handler);
 signal(SIGTERM, sig_handler);

 /* Load and verify BPF application */
 skel = uprobe_bpf__open_opts(&opts);
 if (!skel) {
  fprintf(stderr, "Failed to open and load BPF skeleton\n");
  return 1;
 }
```

實際上，btf 實現重定向需要兩個部分，一個是 bpf 程序帶的編譯時的 btf 信息，一個是內核的 btf 信息。在實際加載 ebpf 程序的時候，libbpf 會根據當前內核上準確的 btf 信息，來修改可能存在錯誤的 ebpf 指令，確保在不同內核版本上能夠兼容。

有趣的是，實際上 libbpf 並不區分這些 btf 信息來自用戶態程序還是內核，因此我們只要把用戶態的重定向信息一起提供給 libbpf 進行重定向，問題就解決了。

本文的工具和完整的代碼在 <https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/38-btf-uprobe> 開源。

## 結論

- **靈活性和兼容性**：在用戶空間eBPF程序中使用 BTF 大大增強了它們在不同版本的用戶空間應用程序和庫之間的靈活性和兼容性。
- **簡化了複雜性**：這種方法顯著減少了維護不同版本的用戶空間應用程序的eBPF程序的複雜性，因為它消除了需要多個程序版本的需要。
- **更廣泛的應用**：這種方法在性能監控、安全和用戶空間應用程序的調試等方面也可能能有更廣泛的應用。bpftime（<https://github.com/eunomia-bpf/bpftime> ） 是一個開源的基於 LLVM JIT/AOT 的用戶態 eBPF 運行時，它可以在用戶態運行 eBPF 程序，和內核態的 eBPF 兼容。它在支持 uprobe、syscall trace 和一般的插件擴展的同時，避免了內核態和用戶態之間的上下文切換，從而提高了 uprobe 程序的執行效率。藉助 libbpf 和 btf 的支持，bpftime 也可以更加動態的擴展用戶態應用程序，實現在不同用戶態程序版本之間的兼容性。

這個示例展示了 eBPF 在實踐中可以將其強大的 CO-RE 功能擴展到更動態地處理用戶空間應用的不同版本變化。

如果你想了解更多關於eBPF知識和實踐，你可以訪問我們的教程代碼庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或者網站 <https://eunomia.dev/tutorials/> 獲得更多示例和完整教程。
