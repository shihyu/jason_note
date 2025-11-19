# eBPF 實踐：使用 Uprobe 追蹤用戶態 Rust 應用

eBPF，即擴展的Berkeley包過濾器（Extended Berkeley Packet Filter），是Linux內核中的一種革命性技術，它允許開發者在內核態中運行自定義的“微程序”，從而在不修改內核代碼的情況下改變系統行為或收集系統細粒度的性能數據。

本文討論如何使用 Uprobe 和 eBPF 追蹤用戶態 Rust 應用，包括如何獲取符號名稱並 attach、獲取函數參數、獲取返回值等。本文是 eBPF 開發者教程的一部分，更詳細的內容可以在這裡找到：<https://eunomia.dev/tutorials/> 源代碼在 [GitHub 倉庫](https://github.com/eunomia-bpf/bpf-developer-tutorial) 中開源。

## Uprobe

Uprobe是一種用戶空間探針，uprobe探針允許在用戶空間程序中動態插樁，插樁位置包括：函數入口、特定偏移處，以及函數返回處。當我們定義uprobe時，內核會在附加的指令上創建快速斷點指令（x86機器上為int3指令），當程序執行到該指令時，內核將觸發事件，程序陷入到內核態，並以回調函數的方式調用探針函數，執行完探針函數再返回到用戶態繼續執行後序的指令。

uprobe 適用於在用戶態去解析一些內核態探針無法解析的流量，例如 http2 流量，https 流量，同時也可以分析程序運行時、業務邏輯等。關於 Uprobe 的更多信息，可以參考：

- [eBPF 實踐教程：使用 uprobe 捕獲多種庫的 SSL/TLS 明文數據](../30-sslsniff/README.md)
- [eBPF 實踐教程：使用 uprobe 捕獲 Golang 的協程切換](../31-goroutine/README.md)
- [eBPF 實踐教程：使用 uprobe 捕獲用戶態 http2 流量](../32-http2/README.md)

Uprobe 在內核態 eBPF 運行時，也可能產生比較大的性能開銷，這時候也可以考慮使用用戶態 eBPF 運行時，例如  [bpftime](https://github.com/eunomia-bpf/bpftime)。bpftime 是一個基於 LLVM JIT/AOT 的用戶態 eBPF 運行時，它可以在用戶態運行 eBPF Uprobe 程序，和內核態的 eBPF 兼容，由於避免了內核態和用戶態之間的上下文切換，bpftime 的 Uprobe 開銷比內核少約 10 倍，並且也更容易擴展。

## Rust

Rust 是一種開源的系統編程語言，注重安全、速度和並行性。它於2010年由Graydon Hoare在Mozilla研究中心開發，並於2015年發佈了第一個穩定版本。Rust 語言的設計哲學旨在提供C++的性能優勢，同時大幅減少內存安全漏洞。Rust在系統編程領域逐漸受到歡迎，特別是在需要高性能、安全性和可靠性的應用場景，例如操作系統、文件系統、遊戲引擎、網絡服務等領域。許多大型技術公司，包括Mozilla、Google、Microsoft和Amazon等，都在使用或支持Rust語言。

可以參考 [Rust 官方網站](https://www.rust-lang.org/) 瞭解更多 Rust 語言的信息，並安裝 Rust 的工具鏈。

## 最簡單的例子：Symbol name mangling

我們先來看一個簡單的例子，使用 Uprobe 追蹤 Rust 程序的 `main` 函數，代碼如下：

```rust
pub fn hello() -> i32 {
    println!("Hello, world!");
    0
}

fn main() {
    hello();
}
```

構建和嘗試獲取符號：

```console
$ cd helloworld
$ cargo build
$ nm helloworld/target/release/helloworld | grep hello
0000000000008940 t _ZN10helloworld4main17h2dce92cb81426b91E
```

我們會發現，對應的符號被轉換為了 `_ZN10helloworld4main17h2dce92cb81426b91E`，這是因為 rustc 使用 [Symbol name mangling](https://en.wikipedia.org/wiki/Name_mangling) 來為代碼生成過程中使用的符號編碼一個唯一的名稱。編碼後的名稱會被鏈接器用於將名稱與所指向的內容關聯起來。可以使用 -C symbol-mangling-version 選項來控制符號名稱的處理方法。

我們可以使用 [`rustfilt`](https://github.com/luser/rustfilt) 工具來解析和獲取對應的符號。這個工具可以通過 `cargo install rustfilt` 安裝：

```console
$ cargo install rustfilt
$ nm helloworld/target/release/helloworld > name.txt
$ rustfilt _ZN10helloworld4main17h2dce92cb81426b91E
helloworld::main
$ rustfilt -i name.txt | grep hello
0000000000008b60 t helloworld::main
```

接下來我們可以嘗試使用 bpftrace 跟蹤對應的函數：

```console
$ sudo bpftrace -e 'uprobe:helloworld/target/release/helloworld:_ZN10helloworld4main17h2dce92cb81426b91E { printf("Function hello-world called\n"); }'
Attaching 1 probe...
Function hello-world called
```

## 一個奇怪的現象：多次調用、獲取參數

對於一個更復雜的例子，包含多次調用和獲取參數：

```rust
use std::env;

pub fn hello(i: i32, len: usize) -> i32 {
    println!("Hello, world! {} in {}", i, len);
    i + len as i32
}

fn main() {
    let args: Vec<String> = env::args().collect();

    // Skip the first argument, which is the path to the binary, and iterate over the rest
    for arg in args.iter().skip(1) {
        match arg.parse::<i32>() {
            Ok(i) => {
                let ret = hello(i, args.len());
                println!("return value: {}", ret);
            }
            Err(_) => {
                eprintln!("Error: Argument '{}' is not a valid integer", arg);
            }
        }
    }
}
```

我們再次進行類似的操作，會發現一個奇怪的現象：

```console
$ sudo bpftrace -e 'uprobe:args/target/release/helloworld:_ZN10helloworld4main17h2dce92cb81426b91E { printf("Function hello-world called\n"); }'
Attaching 1 probe...
Function hello-world called
```

這時候我們希望 hello 函數運行多次，但 bpftrace 中只輸出了一次調用：

```console
$ args/target/release/helloworld 1 2 3 4
Hello, world! 1 in 5
return value: 6
Hello, world! 2 in 5
return value: 7
Hello, world! 3 in 5
return value: 8
Hello, world! 4 in 5
return value: 9
```

而且看起來 bpftrace 並不能正確獲取參數：

```console
$ sudo bpftrace -e 'uprobe:args/target/release/helloworld:_ZN10helloworld4main17h2dce92cb81426b91E { printf("Function hello-world called %d\n"
, arg0); }'
Attaching 1 probe...
Function hello-world called 63642464
```

Uretprobe 捕捉到了第一次調用的返回值：

```console
$ sudo bpftrace -e 'uretprobe:args/tar
get/release/helloworld:_ZN10helloworld4main17h2dce92
cb81426b91E { printf("Function hello-world called %d
\n", retval); }'
Attaching 1 probe...
Function hello-world called 6
```

這可能是由於 Rust 沒有穩定的 ABI。 Rust，正如它迄今為止所存在的那樣，保留了以任何它想要的方式對這些結構成員進行排序的權利。 因此，被調用者的編譯版本可能會完全按照上面的方式對成員進行排序，而調用庫的編程的編譯版本可能會認為它實際上是這樣佈局的：

TODO: 進一步分析（未完待續）

## 參考資料

- <https://doc.rust-lang.org/rustc/symbol-mangling/index.html>
