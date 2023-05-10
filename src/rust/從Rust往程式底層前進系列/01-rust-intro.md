Rust 簡介
=========

在介紹 Rust 以前要先來談談為什麼用 Rust ，Rust 雖說是一個相對算新的語言，跟以往介紹系統運作所使用的 C 比較來的話，不過 Rust 背後有個強大的社群提供了大量的套件，可以讓我們這系列中的實驗可以有些現成的東西能使用，雖說這些東西在 C 裡寫起來可能不難，這系列介紹的東西也有不少其實是 C 寫的函式庫，不過我還是想偷點懶，畢竟相較之下較低階的 C 語言寫起來有點麻煩，另外 Rust 中也有不少有趣的特性可以探討，這系列的前幾篇文章就是來談這個的

因為介紹 Rust 的語法並不是這系列的主題，想要學習 Rust 語法的請去參考我之前寫的[《30 天深入淺出 Rust》][rust-30-days]，這邊來談談 Rust 在這段時間的改變吧，畢竟 Rust 是個還在快速發展的語言

[rust-30-days]: https://ithelp.ithome.com.tw/users/20111802/ironman/1742

NLL
---

NLL 目前已經是預設值了，在現在的穩定版 (1.37) 中甚至你使用 Rust 2015 也會能使用用 NLL ，NLL 是個更強大的 borrow checker，能夠讓一些原本在之前明明看起來是對的，但卻無法通過檢查的也能正常編譯，比如：

```rust
fn use_mut(_x: &mut i32) {}
fn use_ref(_x: &i32) {}

fn main() {
  let mut i = 42;
  let x = &mut i;
  use_mut(x);
  use_ref(i);
}
```

上面這個範例會因為 i 還有個 `&mut` 的 borrow 所以在以前的版本編譯失敗，但現在都沒問題了，還有像：

```rust
fn main() {
    let mut v = Vec::<i32>::new();
    unsafe {
        v.set_len(v.len());
    }
}
```

當要把某個 struct 的方法所回傳的東西馬上又傳進另一個用 `&mut` 借用的方法時就特別麻煩，在以前就要非得要分成兩步驟

const fn
--------

這在之前的系列中也有介紹過，不過那時候標準函式庫中成為 const fn 的函式還不多，不過最棒的是在 const fn 穩定後有個叫 [`once_cell`][once_cell] 的函式庫把它應用在 API 裡了，於是就實現了不需要 macro 的 [`lazy_static`][lazy_static] ，簡單來說就是隻會在第一次使用到時才初始化的變數，像這樣：

```rust
use once_cell::sync::Lazy;

static FOO: Lazy<String> = Lazy::new(|| "foo".to_owned());
```

[once_cell]: https://github.com/matklad/once_cell
[lazy_static]: https://github.com/rust-lang-nursery/lazy-static.rs

因為我比較喜歡這樣的 API ，所以目前基本上都改用 `once_cell` 了， const fn 穩定後很多事就變的更方便了

`dbg!`
------

這是個讓你方便除錯的 macro ：

```rust
if dbg!(true) {
  println!("is true");
}
```

這樣在終端機就會額外印出一行包含行號與包在 `dbg!` 中的值的資訊，像這樣：

```plain
[foo.rs:12] true = true
```

Self
----

`Self` 現在變的更方便了，比如可以這樣：

```rust
enum Foo {
  A,
  B,
}

impl Foo {
  fn to_num(&self) -> i32 {
    match self {
      Self::A => 1,
      Self::B => 2,
    }
  }
}
```

原本是不行的

pin
---

這是做為接下來要講到的 async await 的一個前置的 API ，雖說如此，不過其實它的用途好像不多，它最主要的用途是用來保證一個東西在記憶體中的位置不會移動，比如 swap 這個動作之類的，應用方面應該主要就是製作自己 borrow 自己的 struct ，這也是 async await 會需要這個 API 的原因：

```rust
use std::{marker::PhantomPinned, pin::Pin};

struct Foo(PhantomPinned);

impl Foo {
    fn new() -> Self {
        Self(PhantomPinned)
    }
}

fn main() {
    let mut foo = Foo::new();
    let pinned_foo = unsafe { Pin::new_unchecked(&mut foo) };
}
```

於是 `pinned_foo` 就不該移動了，不過實際上 `Pin` 是以限制使用 `&mut` 的方式來讓使用者沒辦法隨意移動值的，所以與其說 `Pin` 是保證值不會移動的 API ，不如說 `Pin` 實際上只是個在語義上要求使用者不該移動它的 API 吧，其實 `Pin` 應該可以寫一篇文來介紹一下它的用法的

future
------

Rust 目前已經把 future 的核心部份整合進標準函式庫中了，這跟接下來的 async await 有關

async await
-----------

這是個目前還不穩定的功能，預計應該是會在 1.39 才推出的，不過可以先來試試看，如果你有寫過 js 的話應該是挺類似 js 的 async 與 await 的感覺，也是當目前的工作能暫停時就可以去執行其它的工作，在底下的範例應該可以看到執行的兩次 `print` 有同時在執行：

```rust
#![feature(async_await)]

use std::time::Duration;
use async_std::task;

async fn print(n: i32) {
  const ONE_SEC: Duration = Duration::from_secs(1);
  for i in 0..3 {
    println!("In {} hello {}", n, i);
    task::sleep(ONE_SEC).await;
  }
}

fn main() {
  task::block_on(async {
    futures::join!(print(1), print(2));
  });
}
```

這段時間實際上 Rust 還有加入不少東西，這邊只是選了幾個出來講而已，下一篇總算是要正式開始這個系列了
