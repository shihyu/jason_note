dynamic link
============

動態連結是讓程式能載入動態函式庫，這些函式庫在 Linux 下一般都是以 `.so` 的副檔名做結尾，這些檔案能在程式執行起來後才由動態連結器載入程式的記憶體空間供程式呼叫，這樣的設計有些好處：

1. 節省編譯的時間
2. 可以分開來更新
3. 共用同一個函式庫可以節省檔案大小，想像一下如果每個程式都自帶一份 `libc` 的話電腦中會存在幾份同樣的 `libc`

Rust 建立動態函式庫
-------------------

用 Rust 要建立動態函式庫其實不難，只要指定 `crate-type` 就可以了，如果是直接使用 `rustc` 的話：

```shell
$ rustc --crate-type=cdylib demo.rs
$
```

這邊的 `cdylib` 是為了支援其它語言的一個格式，另外為了要給其它語言使用的話，函式名稱也要注意不要使用 mangle ，同時使用 C 的 ABI 比較好：

```rust
// 不要 mangle
#[no_mangle]
// 使用 C 的 ABI
extern "C" fn foo() {
  println!("Hello world");
}
// 這樣在其它語言中就可以用 `foo` 這個名字了
```

`.dynamic` section
----------------

接著如果有其它的程式使用到了這個 `.so` 檔，編譯器就會在使用到的程式的 `.dynamic` 中記錄使用到的動態函式庫，這可以用 `readelf` 來看：

```shell
$ readelf -d hello

Dynamic section at offset 0xda8 contains 29 entries:
  Tag        Type                         Name/Value
 0x0000000000000001 (NEEDED)             Shared library: [libdemo.so]
 0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
 0x000000000000001d (RUNPATH)            Library runpath: [.]
...
```

> 另外這邊我還有設定 `rpath` ，就是上面的 `RUNPATH` 讓它可以在執行時找到動態函式庫，不然預設動態連結器只會找系統的函式庫存放的位置而已

於是動態連結器就會去讀這個表，找出這個程式相依的函式庫，並把函式庫所相依的函式庫也一一找出來，這樣才能找出這個程式總共需要哪些動態函式庫，這部份可以用 `ldd` 這個指令來找：

```shell
$ ldd hello
  linux-vdso.so.1 (0x00007fff59d7d000)
  libdemo.so => ./libdemo.so (0x00007f2c962d1000)
  libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f2c95ee0000)
  libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f2c95cdc000)
  librt.so.1 => /lib/x86_64-linux-gnu/librt.so.1 (0x00007f2c95ad4000)
  libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007f2c958b5000)
  libgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007f2c9569d000)
  /lib64/ld-linux-x86-64.so.2 (0x00007f2c96702000)
```

上面顯示除了我們自己的 `libdemo.so` 與一般都會用到的 `libc.so` 外還有幾個其它的東西，其中 `vdso` 是個虛擬的動態函式庫，這之後有機會再來聊，另外還有 `ld-linux-x86-64.so.2` 這個是動態連結器，一般稱為 `ld.so` ，其它的函式庫是 Rust 使用到的

動態連結器
----------

若是 64 位元的系統的話，動態連結器一般會放在 `/lib64` 下一個以 `ld` 開頭的 `.so` 檔，它負責把動態函式庫載入，以及重定址的工作，雖說是重定址，不過主要是把用到的函式的位置找出來填上去，另外 Linux 下的動態連結器其實有個挺有趣的特性：

```shell
$ /lib64/ld-linux-x86-64.so.2
Usage: ld.so [OPTION]... EXECUTABLE-FILE [ARGS-FOR-PROGRAM...]
You have invoked `ld.so', the helper program for shared library executables.
This program usually lives in the file `/lib/ld.so', and special directives
in executable files using ELF shared libraries tell the system's program
loader to load the helper program from this file.  This helper program loads
the shared libraries needed by the program executable, prepares the program
to run, and runs it.  You may invoke this helper program directly from the
command line to load and run an ELF executable file; this is like executing
that file itself, but always uses this helper program from the file you
specified, instead of the helper program file specified in the executable
file you run.  This is mostly of use for maintainers to test new versions
of this helper program; chances are you did not intend to run this program.

  --list                list all dependencies and how they are resolved
  --verify              verify that given object really is a dynamically linked
                        object we can handle
  --inhibit-cache       Do not use /etc/ld.so.cache
  --library-path PATH   use given PATH instead of content of the environment
                        variable LD_LIBRARY_PATH
  --inhibit-rpath LIST  ignore RUNPATH and RPATH information in object names
                        in LIST
  --audit LIST          use objects named in LIST as auditors
```

它是個 `.so` 檔卻可以執行，事實上上面的 `ldd` 指令不過是個 `ld.so` 的包裝而已，那個輸出就是 `ld.so` 平常在找出程式的相依性時做的事

`ld.so` 對於程式而言是非常重要的，關於這邊可以看到在程式的分段中，甚至有個專門的分段是用來存 `ld.so` 的位置用的：

```shell
$ objdump -s hello
...

Contents of section .interp:
 0238 2f6c6962 36342f6c 642d6c69 6e75782d  /lib64/ld-linux-
 0248 7838362d 36342e73 6f2e3200           x86-64.so.2.
 ...
```

如果符號 (函式) 的名稱重覆
--------------------------

那又會發生什麼事呢？我們準備兩個檔案分別叫 `file1.rs` 與 `file2.rs` 分別編譯成兩個 `.so` 檔，並在裡面準備同名的函式，然後準備個主程式進行連結的話：

```shell
$ rustc -C link-args=-Wl,-rpath,. demo.rs -l file1 -l file2 -L .
$
```

然後執行：

```shell
$ ./demo
Hello from file1
```

印出了從 `file1` 來的訊息呢，如果把上面的順序換一下的話

```shell
$ rustc -C link-args=-Wl,-rpath,. demo.rs -l file1 -l file2 -L .
$ ./demo
Hello from file2
```

變成從 `file2` 來的訊息了，動態連結時，如果發生名稱重覆的問題，後面的是不會覆蓋前面的，因為這個特性，之後將會提到一個與這有關的東西，這篇就先介紹到這了

參考資料
--------

- http://ccckmit.wikidot.com/lk:dynamiclinking
