Before the main 2
=================

前一篇看完了 Rust 本身加在 `main` 前的程式碼，對了，前一篇中好像沒有提到 Rust 程式中的那個 C 的 `int main(int, char **)` 函式是怎麼來的，那段程式碼是由編譯器產生的，位於 [`librustc_codegen_ssa/base.rs#L414`][codegen-base] ，而再接下來還有其它的程式碼，這些程式碼則可以說是使用 `libc` ，也就是 C 的標準函式庫所需要的

[codegen-base]: https://github.com/rust-lang/rust/blob/master/src/librustc_codegen_ssa/base.rs#L414

明明是 Rust 的程式為什麼會跟 C 的標準函式庫扯上關係呢？ 但實際上很多程式語言底下都還是會用到 C 的標準函式庫，畢竟 C 發展的久， C 的標準函式庫早就提供了基本需要的東西，還有和作業系統溝通的介面，現在 Linux 下用的實作叫 `glibc` ，但實際上還有其它實作，比如 uclibc ，還有你可能會看到有些 Rust 的程式是跟 musl 編譯在一起的， musl 是個著重在體積小可靜態連結的 C 函式庫，但它不一定快就是了，只是如果將程式與 musl 連結就可以在一些比較特殊的環境執行，比如缺乏 C 函式庫的嵌入式系統

所以程式是到底是從哪邊開始的，我們一樣用 `gdb` 的 `bt` 來看吧：

```plain
#0  main () at demo.c:1
#1  0x00007ffff77feb97 in __libc_start_main (main=0x5555555545fa <main>, argc=1, argv=0x7fffffffc0c8, init=<optimized out>, fini=<optimized out>, rtld_fini=<optimized out>, stack_end=0x7fffffffc0b8) at ../csu/libc-start.c:310
#2  0x000055555555451a in _start ()
```

程式最初的起點 `_start`
-----------------------

從上面的 backtrace 中，可以看出 `_start` 是第一個被呼叫的位置，它的程式碼在 [`sysdeps/x86_64/start.S`][start-s] ，是一段組語寫成的程式，不過它其實並不長，只是做些準備工作就去呼叫上面所看到的第二個函式 `__libc_start_main` ，順帶一提，在同一個資料夾下還可以看到 C 函式庫中的 `strcmp` 、 `strchr` 等等的函式實作，這些函式為了速度都是用組語寫成的

[start-s]: https://github.molgen.mpg.de/git-mirror/glibc/blob/master/sysdeps/x86_64/start.S

`__libc_start_main`
------------------

接下來就是重點的部份了，這份程式碼則是定義在 [`csu/libc-start.c`][libc-start] ，不過這邊並沒有打算像前一篇一樣一行一行的讀，這邊只大概介紹概念

[libc-start]: https://github.molgen.mpg.de/git-mirror/glibc/blob/master/csu/libc-start.c

它做的事情有：

1. 初始化 pthread
2. 註冊 finit 的函式，讓它在程式結束時被執行
3. 執行 init 的函式
4. 呼叫 main
5. 呼叫 exit

其中比較有趣的就是 init 與 finit 這兩個東西可以讓你的程式在被載入時，或是程式結束時執行些什麼東西，雖說 C 語言好像沒有什麼東西需要在執行前做初始化的，不過像 C++ 就有了，當你把物件宣告在全域的空間時，程式就必須保證在使用者的程式開始執行前將物件初始化好，如果物件有解構子的話，也必須在程式結束後執行，而 init 與 finit 就被用來做這部份的工作，但實際上還不只這些，在 C 語言中，也有個必須要在程式開始執行前準備的東西，那就是 gprof ，是個 profiling 的工具，它跟編譯器整合在一起，能夠在你的程式跑完時產生一份關於執行時的資訊的一份報告，讓你再去用這個工具去分析

順帶一提， Rust 有個 crate 叫 [`ctor`][ctor] ，它就是利用了 init 來在程式的 `main` 開始前執行程式碼的，它可以像這樣子

[ctor]: https://github.com/mmastrac/rust-ctor

```rust
#[ctor::ctor]
fn before_main() {
  println!("Hello before main");
}

#[ctor::dtor]
fn after_main() {
  extern "C" {
    fn puts(s: *const u8);
  }
  unsafe {
    // 這邊沒辦法用 println ，因為 Rust 已經把這部份的資源釋放掉了
    puts("Hello after main\0".as_ptr());
  }
}

fn main() {
    println!("Hello, world!");
}
```

結果我想應該很容易就可以猜到

另外一個比較有趣的是，實際上程式如果要結束是要呼叫 `exit` 來通知作業系統把處理緒結束掉的，當程式呼叫這個系統呼叫時作業系統就會把執行一個程式的資源釋放掉，另外因為上面提到的 finit 是由 C 的函式庫在 `main` 結束後呼叫，所以如果直接使用 `exit` 這個系統呼叫的話就不會執行，它在 C 的函式庫中的名字是 `_exit` ，這是為了要跟有處理 finit 的 `exit` 做區隔

```rust
#[ctor::dtor]
fn after_main() {
  extern "C" {
    fn puts(s: *const u8);
  }
  unsafe {
    puts("Hello after main\0".as_ptr());
  }
}

fn main() {
  extern "C" {
    fn _exit(status: i32) -> !;
  }
  println!("Hello, world!");
  unsafe {
    _exit(0);
  }
}
```

所以可能會造成一些東西沒有辦法正常釋放掉，這函式沒必要還是不要用吧，如果把上面的 `_exit` 改成 `std::process::exit` 或是 libc 的 `exit` 的話 `Hello after main` 就又可以正常印出來了，不過 Rust 的 `std::process::exit` 也有做一些額外的事情，所以在 Rust 還是別用 libc 的 `exit` 吧
