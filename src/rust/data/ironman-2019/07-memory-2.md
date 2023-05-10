再看記憶體
==========

在上一篇中講到了資料段 (`.data`) ，今天來講講在記憶體中到底放了些什麼，首先，有個很重要的觀念要知道，程式也是資料：

```rust
use std::slice;

fn main() {
  let data = unsafe { slice::from_raw_parts(main as *const u8, 10) };
  println!("{:#x?}", data);
}
```

這邊把 `main` 函式的前十個 byte 印出來了，那就有個有趣的問題了，如果我們把函式的內容複製到別的地方存著，再去把它當成函式呼叫會發生什麼事，能執行嗎？

但還是不要直接複製 `main` 來執行比較好，先準備個簡單的函式

```rust
fn hello() {
  println!("Hello world");
}
```

接下來我們碰到了下個問題， `hello` 這個函式有多大，這邊我們直接用 Linux 下的一個工具 - `readelf` 來看函式編譯好後有多大吧，這邊用的是 debug build：

```shell
$ readelf -sW | grep hello | c++filt
    53: 0000000000004160    55 FUNC    LOCAL  DEFAULT   14 demo::hello
```

這邊解釋一下指令的用途：

- `readelf`: 依照參數讀取執行檔中各式各樣的資訊， `-s` 是讀取符號 (函式、或是全域變數等等) ， `-W` 是讓它完整顯示
- `grep`： 找出有指定東西的行
- `c++filt`： 原本是把 C++ 的經過名稱修飾 (mangle) 的函式名稱還原回原本的名稱的，不過因為 Rust 的修飾規則與 C++ 挺像的，所以也可以用

其中的 `55` 就是我們要的函式大小了，如果不放心的話你還可以用另一個指令 `objdump` 把檔案反組譯後去數一下，雖說我有實際去數過了，但這邊就先不貼出反組譯的結果了，畢竟我們已經有大小了，就先來試試如果複製一份會發生什麼事吧：

```rust
// 在我的電腦上是 55 ，如果你要自己試的請先用 readelf 確認大小，然後來修正這個數字
const CODE_SIZE: usize = 55;

fn main() {
  let bytes = unsafe { slice::from_raw_parts(hello as *const u8, CODE_SIZE) };
  let mut buf = [0u8; CODE_SIZE];
  buf.clone_from_slice(&bytes);
  let f = unsafe { mem::transmute::<_, fn()>(&buf) };
  f();
}
```

編譯，執行…，嗯， `segmentation fault` ，這是預期的結果，對了，還有另一個問題，明明你我都知道，程式與資料都存在記憶體中，為什麼程式不會修改到其它程式的資料呢？這要從作業系統對於記憶體的管理機制 - 分頁來開始講起了

分頁屬性
--------

作業系統把記憶體以一定的大小分割來管理，這樣一塊記憶體就叫一個「分頁」，一般 linux 下預設是 4096 byte 也就是 4K 的大小，這些分頁都可以有不同的屬性，包含可讀、可寫、可執行等等，這做為一個保護機制在確保你不會在不該寫入或不該執行程式的地方寫入或執行，所以我們在上面把程式複製到 stack 上才無法執行的

那如果要讓之前的程式能順利執行有可能嗎？有的：

```rust
use std::{mem, slice};

fn print() {
    println!("Hello world");
}

fn hello(f: fn()) {
    f();
}

const CODE_SIZE: usize = 10;

fn main() {
  // 取得一個分頁的大小
  let page_size = unsafe { libc::sysconf(libc::_SC_PAGE_SIZE) };
  let bytes = unsafe { slice::from_raw_parts(hello as *const u8, CODE_SIZE) };
  let mut buf = [0u8; CODE_SIZE];
  buf.clone_from_slice(&bytes);
  // 取得分頁的開頭
  let p = buf.as_ptr() as usize & (-page_size) as usize;
  unsafe {
    // 修改分頁的屬性
    libc::mprotect(
      p as *mut libc::c_void,
      buf.as_ptr() as usize - p + mem::size_of::<u8>() * 55,
      libc::PROT_READ | libc::PROT_WRITE | libc::PROT_EXEC,
    );
  }
  let f = unsafe { mem::transmute::<_, fn(f: fn())>(&buf) };
  f(print);
}
```

這邊我用 `mprotect` 改掉了 stack 的保護屬性，讓 stack 上的東西能夠執行

「咦，你怎麼改掉 `hello` 這個函式了」，因為原本裡面要呼叫其它函式，但現在程式為了支援 ASLR 的關係，都用相對位置呼叫函式了，為了避免這個問題，才把函式另外用函式指標的方式傳進去，關於 ASLR 跟相對位置什麼的，之後我們再來談

總之我們這邊用 `mprotect` 這個系統呼叫改掉了存放我們複製的程式碼的那段 stack 的分頁屬性，讓它變成可以執行了，這樣我們在上執行程式碼也不會觸發 segmentation fault 啦

對了，在 Linux 下我們可以到 `/proc/[pid]/maps` 看目前記憶體分配的情況 (其中的 `[pid]` 就是指程式的 `pid`)

```plain
562831495000-5628314c7000 r-xp 00000000 00:2f 7072                       demo
5628316c7000-5628316ca000 r--p 00032000 00:2f 7072                       demo
5628316ca000-5628316cb000 rw-p 00035000 00:2f 7072                       demo
562832108000-562832129000 rw-p 00000000 00:00 0                          [heap]
7fe00a65e000-7fe00a845000 r-xp 00000000 08:04 4073218                    /lib/x86_64-linux-gnu/libc-2.27.so
7fe00a845000-7fe00aa45000 ---p 001e7000 08:04 4073218                    /lib/x86_64-linux-gnu/libc-2.27.so
7fe00aa45000-7fe00aa49000 r--p 001e7000 08:04 4073218                    /lib/x86_64-linux-gnu/libc-2.27.so
7fe00aa49000-7fe00aa4b000 rw-p 001eb000 08:04 4073218                    /lib/x86_64-linux-gnu/libc-2.27.so
...
7ffff9424000-7ffff9425000 rwxp 00000000 00:00 0                          [stack]
```

這是我某次執行的結果，為什麼說某次呢，這就是 ASLR 的效果，詳細還是之後再談，你可以看到底下的 `[stack]` 部份，在第二欄的權限部份變成了 `rwx`，意思是可讀可寫可執行，這就是上面用 `mprotect` 修改的結果

虛擬記憶體
----------

程式所看到的記憶體空間實際上是虛擬出來的，為了讓程式認為自己有個完整的連續記憶體，這減少了程式設計師的負擔，讓我們不用去擔心會不小心修改到別人的資料，同時也比較好處理資料，你能想像當你讀進一個大檔案時，因為記憶體中間被其它資料佔據而不得不分成兩段嗎？不會動到別的程式的資料也同時增加了安全性

而且這些分頁其實也不用真的存在於記憶體之中，作業系統可以只在必要時才把分頁載入記憶體，也可以把暫時用不到的分頁移到硬碟中暫存之類的，這就是 Linux 下的 swap 分割區，或是 Windows 下的分頁檔的功能，它們就是這些暫時用不到的分頁所存放的地方

另外還有所謂的「寫時複製 (Copy on Write 簡稱 COW)」，Linux 下若使用 `fork` 這個系統呼叫會將處理緒複製一個，但如果這時也要把記憶體中的資料也都複製一份的話也太沒效率了，所以系統可以透過將可寫的分頁設定成唯讀，這樣就能在程式嘗試寫入時偵測到，這時才去實際的將分頁複製一份，就能避免不必要的複製了，在上面的 `maps` 檔案中，權限最後的那個 `p` 代表的是這個分頁是屬於私有的，也就是假如在 `fork` 之後發生了寫入的情況，這個分頁是必須要複製的

順帶一提， Rust 中有個叫 [`Cow`][cow-doc] 的型態，當你嘗試修改時，也就是呼叫它的 `to_mut` 時，才會檢查是不是擁有的型態，並做必要的複製，也可以說是類似的機制呢

[cow-doc]: https://doc.rust-lang.org/stable/std/borrow/enum.Cow.html

所以之前說的為什麼 stack 的位置離的那麼遠，為什麼 heap 分配的資料與全域變數比較近，其實在上面提到的 `maps` 檔案裡都有答案了，程式被分成三個段載入到記憶體中：

1. 程式碼區段 (.text) ，故名思議，放程式的
  562831495000-5628314c7000 r-xp 00000000 00:2f 7072                       demo
2. 唯讀資料區段 (.rodata) ，用來放全域不可以更改的變數，比如字串常數
  5628316c7000-5628316ca000 r--p 00032000 00:2f 7072                       demo
3. 可寫資料段 (.data, .bss) ，放可寫的全域變數
  5628316ca000-5628316cb000 rw-p 00035000 00:2f 7072                       demo

區段後面的英文名稱，之後再來解釋，另外 Rust 中的 const 變數其實並不一定是放在唯讀資料的那邊， Rust 中真的對應到唯讀資料的應該是沒有加上 `mut` 的 `static` 變數，與字串常數

