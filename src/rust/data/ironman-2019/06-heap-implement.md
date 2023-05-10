Heap Implement
==============

> 本系列的程式碼都有在 Ubuntu 18.04 下以目前的穩定版 Rust 1.37 測試過

> 這次的程式碼在 https://github.com/DanSnow/ironman-2019/tree/master/heap

今天來嘗試自己實作 heap ，也就是自己來實作 C 裡的 malloc 與 free

首先要來看看 Rust 中要如何換掉 allocator ，因為 Rust 中的空間分配都已經包裝在 `Box`, `Vec` 等等的 API 之內了，事實上在 [`std::alloc`][alloc-doc] 模組的介紹中就有要如何換掉 allocator 了，只要透過 `#[global_allocator]` 標註在要當 allocator 的全域變數上就行了：

[alloc-doc]: https://doc.rust-lang.org/stable/std/alloc/index.html

```rust
use std::alloc::System;

// 這邊變數的名字其實不太重要
#[global_allocator]
static GLOBAL: System = System;
```

`System` 是內建的 allocator，但我們今天是要實作自己的 allocator ，於是我們要來實作 [`GlobalAlloc`][global-alloc] 這個 trait ，我們要實作兩個方法， `alloc` 與 `dealloc` ，就是分配記憶體與釋放記憶體，但首先，我們先來看看 malloc 做了什麼事

[global-alloc]: https://doc.rust-lang.org/stable/std/alloc/trait.GlobalAlloc.html

`brk` - 取得更多記憶體
--------------------

`brk` 是個系統呼叫，根據 manpage 上的說明，它實際的功能是修改 data 段的大小，什麼是 data 段我們之後會再來說明，總之先理解它是一塊可以寫入的記憶體，我們把它大小擴大後就有記憶體可以來分配了，至於這東西要怎麼使用呢，我正好在 ithelp 上找到一篇[文章][brk]

[brk]: https://ithelp.ithome.com.tw/articles/10186995

這兩個系統呼叫的函式原型是這樣的：

```c
int brk(void *addr);
void *sbrk(intptr_t increment);
```

`brk` 會嘗試把代表 data 段結尾的指標設定至 `addr` 的位置，而 `sbrk` 則是根據 `increment` 來增加 data 段的大小，並回傳之前的結尾位置，有趣的是，如果傳入 0 給 `sbrk` ，則可以用來知道目前的結尾在哪，有了這兩個系統呼叫，我們實作 heap 所需的第一步，取得可以用來分配的記憶體就完成了

順帶一提，如果你去看 `brk` 的 manpage 的話，你會發現底下直接叫你用 `malloc` 就好

heap 的資料結構
---------------

既然原本系統中就有提供 `malloc` 這麼好用的東西了，那我們直接參考一下它的實作吧，稍微找一下可以找到一篇 [wiki][malloc-internal] 在介紹 `malloc` 內部的實作，總之我們先做個簡單的版本來試試看

[malloc-internal]: https://sourceware.org/glibc/wiki/MallocInternals

`malloc` 中是以記憶體區塊 (chunk) 做為分配的單位的，區塊分成兩種，一種是已經分配出去而被使用中的，另一種則是可分配的，兩種內容不太一樣，其中可分配的區塊是這樣的：

```plain
+-------------------+
| size (with flags) |
+-------------------+
| fwd               |
+-------------------+
| bck               |
+-------------------+
```

- size: 記錄區塊的大小，同時也有用最後幾個 bit 來存一些 flag
- fwd: 下一個 free chunk 的位置
- bck: 前一個 free chunk 的位置

其實就是雙向連結串列 (doubly linked list) 的資料結構，一般到這邊我們就可以開始實作了，不過其實還有個問題

對齊 (aligned)
--------------

Rust 在分記憶體時傳入的 `Layout` 除了 `.size()` 外還有另一個 `.align()` ，為了存取的效率上的問題， Rust 大部份的 API 都是預期你的資料是對齊的，比如像 `std::ptr::copy` ，為了滿足這個條件，我們必須處理對齊的問題，也就是說我們的 allocator 分配出來的記憶體位置，要能被 `Layout` 的 `.align()` 回傳的值整除，事實上 Rust 在這邊有提供我們一個 API 可以去計算可以對齊的位置是多少，那就是 [`pointer::align_offset`][align_offset-doc]

[align_offset-doc]: https://doc.rust-lang.org/stable/std/primitive.pointer.html#method.align_offset

另外原本的 `malloc` 其實並沒有處理記憶體對齊的設計，因為它根本不知道你的資料該怎麼對齊，於是現在又有了 `posix_memalign` 與 `aligned_alloc` 這兩個 API 可以用來分配有經過對齊的記憶體， Rust 預設的 allocator 中用的正是 `posix_memalign`

> 正確來說 `malloc` 還是有對齊記憶體，只是它是對齊到 pointer 的大小，而無法讓你自己決定

實作
----

有了上面這些資訊後我們就可以來實作自己的記憶體分配器了，這次要實作的只是一個很簡化的版本，它只能簡單的分配由 `brk` 取得的記憶體，它沒辦法：

- 分配較大的記憶體 (這需要用到 `mmap`)
- 合併空的記憶體空間
- 像 `malloc` 一樣用 cache 加速分配
- `brk` 的空間用完了就沒辦法分配了

因為這個實作大部份其實是在處理修改每個記憶體區塊前的中介資料，我只在這邊大概講解一部份的程式碼，另外我並沒有利用 size 後面的空間來放 `flag`

```rust
pub struct MyAlloc {
  start: Cell<*mut usize>,
  head: Cell<*mut usize>,
}

// 讓編譯器以為我們的 allocator 是可以多執行緒同時存取的，實際上並不是就是了
unsafe impl Sync for MyAlloc {}

unsafe fn init_arena() -> *mut usize {
  // 取得 data 段的結尾位置
  let start = libc::sbrk(0);
  // 用 brk 來取得空間
  if libc::brk(start.add(DEFAULT_SIZE)) != 0 {
      panic!("brk fail");
  }
  // 初始化中介資料
  let start = start as *mut usize;
  ptr::write(start, DEFAULT_SIZE - META_SIZE);
  ptr::write(start.add(1), 0); // unused
  ptr::write(start.add(2), 0); // next
  ptr::write(start.add(3), 0); // prev
  start
}
```

其它部份就是處理分配與回收空間的部份了，這部份我用文字描述作法

分配：

1. 從串列中找到一塊夠大的區塊
2. 分割區塊，把新的空區塊串上原本的串列，然後回傳使用者要的區塊

回收：

1. 從串列中找到應該插入的位置
2. 把節點插入，並更新上面的中介資料，標記為未使用，與加上前後的指標

其它實作細節請參考我上面貼出來的 repo 吧

不過其實我想一下，回收的部份好像沒有一定要照順序串在一起就是了，這次實作的分配器只能讓簡單的程式動起來而已，我在 `main` 中也只是分配了一個字串而已：

```rust
#[global_allocator]
static ALLOC: v1::MyAlloc = v1::MyAlloc::new();

fn main() {
  println!("{}", "Hello world".to_owned());
}
```

但在實作的期間就注意到了， Rust 的程式在呼叫 `main` 之前就會有記憶體分配了，另外還有 `panic` 也會分配記憶體，這部份之後也會來研究呢

參考資料
--------

- https://sourceware.org/glibc/wiki/MallocInternals
- https://ithelp.ithome.com.tw/articles/10186995
