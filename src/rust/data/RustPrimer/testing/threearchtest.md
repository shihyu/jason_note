# 測試

> 程序測試是一種找到缺陷的有效方式，但是它對證明沒有缺陷卻無能為力。
>
>    Edsger W. Dijkstra, "The Humble Programmer" (1972)

作為軟件工程質量保障體系的重要一環，測試是應該引起我們充分注意並重視的事情。前面說過，Rust 語言的設計集成了最近十多年中總結出來的大量最佳工程實踐，而對測試的原生集成也正體現了這一點。下面來看 Rust 是怎麼設計測試特性的。

Rust 的測試特性按精細度劃分，分為 3 個層次：

1. 函數級；
2. 模塊級；
3. 工程級；

另外，Rust 還支持對文檔進行測試。

## 函數級測試

在本章中，我們用創建一個庫的實操來講解測試的內容。我們先用 cargo 建立一個庫工程：`adder`

```
$ cargo new adder
$ cd adder
```

### `#[test]` 標識
打開 `src/lib.rs` 文件，可以看到如下代碼

```rust
#[test]
fn it_works() {
    // do test work
}
```

Rust 中，只需要在一個函數的上面，加上 `#[test]` 就標明這是一個測試用的函數。

有了這個屬性之後，在使用 `cargo build` 編譯時，就會忽略這些函數。使用 `cargo test` 可以運行這些函數。類似於如下效果：

```
$ cargo test
   Compiling adder v0.0.1 (file:///home/you/projects/adder)
     Running target/adder-91b3e234d4ed382a

running 1 test
test it_works ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured
```

Rust 提供了兩個宏來執行測試斷言：

```rust
assert!(expr)               測試表達式是否為 true 或 false
assert_eq!(expr, expr)      測試兩個表達式的結果是否相等
```
比如

```rust
#[test]
fn it_works() {
    assert!(false);
}
```

運行 `cargo test`，你會得到類似下面這樣的提示

```
$ cargo test
   Compiling adder v0.0.1 (file:///home/you/projects/adder)
     Running target/adder-91b3e234d4ed382a

running 1 test
test it_works ... FAILED

failures:

---- it_works stdout ----
        thread 'it_works' panicked at 'assertion failed: false', /home/steve/tmp/adder/src/lib.rs:3



failures:
    it_works

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured

thread '<main>' panicked at 'Some tests failed', /home/steve/src/rust/src/libtest/lib.rs:247
```

### `#[should_panic]` 標識

如果你的測試函數沒完成，或沒有更新，或是故意讓它崩潰，但為了讓測試能夠順利完成，我們主動可以給測試函數加上 `#[should_panic]` 標識，就不會讓 `cargo test` 報錯了。

如

```rust
#[test]
#[should_panic]
fn it_works() {
    assert!(false);
}
```

運行 `cargo test`，結果類似如下：

```
$ cargo test
   Compiling adder v0.0.1 (file:///home/you/projects/adder)
     Running target/adder-91b3e234d4ed382a

running 1 test
test it_works ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured
```

### `#[ignore]` 標識

有時候，某個測試函數非常耗時，或暫時沒更新，我們想不讓它參與測試，但是又不想刪除它，這時， `#[ignore]` 就派上用場了。

```rust
#[test]
#[ignore]
fn expensive_test() {
    // code that takes an hour to run
}
```

寫上這個，運行 `cargo test` 的時候，就不會測試這個函數。

## 模塊級測試

有時，我們會組織一批測試用例，這時，模塊化的組織結構就有助於建立結構性的測試體系。Rust 中，可以類似如下寫法：

```rust
pub fn add_two(a: i32) -> i32 {
    a + 2
}

#[cfg(test)]
mod tests {
    use super::add_two;

    #[test]
    fn it_works() {
        assert_eq!(4, add_two(2));
    }
}
```

也即在 `mod` 的上面寫上 `#[cfg(test)]` ，表明這個模塊是個測試模塊。一個測試模塊中，可以包含若干測試函數，測試模塊中還可以繼續包含測試模塊，即模塊的嵌套。

如此，就形式了結構化的測試體系，甚是方便。


## 工程級測試

函數級和模塊級的測試，代碼是與要測試的模塊（編譯單元）寫在相同的文件中，一般做的是白盒測試。工程級的測試，一般做的就是黑盒集成測試了。

我們看一個工程的目錄，在這個目錄下，有一個 `tests` 文件夾（沒有的話，就手動建立）

```
Cargo.toml
Cargo.lock
examples
src
tests
```

我們在 tests 目錄下，建立一個文件 `testit.rs` ，名字隨便取皆可。內容為：

```rust
extern crate adder;

#[test]
fn it_works() {
    assert_eq!(4, adder::add_two(2));
}
```

這裡，比如，我們 src 中，寫了一個庫，提供了一個 `add_two` 函數，現在進行集成測試。

首先，用 `extern crate` 的方式，引入這個庫，由於是同一個項目，cargo 會自動找。引入後，就按模塊的使用方法調用就行了，其它的測試標識與前面相同。

寫完後，運行一下 `cargo test`，提示類似如下：

```
$ cargo test
   Compiling adder v0.0.1 (file:///home/you/projects/adder)
     Running target/adder-91b3e234d4ed382a

running 1 test
test tests::it_works ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured

     Running target/lib-c18e7d3494509e74

running 1 test
test it_works ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured
```

## 文檔級測試

Rust 對文檔的哲學，是不要單獨寫文檔，一是代碼本身是文檔，二是代碼的註釋就是文檔。Rust 不但可以自動抽取代碼中的文檔，形成標準形式的文檔集合，還可以對文檔中的示例代碼進行測試。

比如，我們給上面庫加點文檔：

``````rust
//! The `adder` crate provides functions that add numbers to other numbers.
//!
//! # Examples
//!
//! ```
//! assert_eq!(4, adder::add_two(2));
//! ```

/// This function adds two to its argument.
///
/// # Examples
///
/// ```
/// use adder::add_two;
///
/// assert_eq!(4, add_two(2));
/// ```

pub fn add_two(a: i32) -> i32 {
   a + 2
}

#[cfg(test)]
mod tests {
   use super::*;

   #[test]
   fn it_works() {
      assert_eq!(4, add_two(2));
   }
}
``````


運行 `cargo test`，結果如下：

```
$ cargo test
   Compiling adder v0.0.1 (file:///home/steve/tmp/adder)
     Running target/adder-91b3e234d4ed382a

running 1 test
test tests::it_works ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured

     Running target/lib-c18e7d3494509e74

running 1 test
test it_works ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured

   Doc-tests adder

running 2 tests
test add_two_0 ... ok
test _0 ... ok

test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured
```

看到了吧，多了些測試結果。

## 結語

我們可以看到，Rust 對測試，對文檔，對文檔中的示例代碼測試，都有特性支持。從這些細節之處，可以看出 Rust 設計的周密性和嚴謹性。

但是，光有好工具是不夠的，工程的質量更重要的是寫代碼的人決定的。我們應該在 Rust 嚴謹之風的薰陶下，養成良好的編碼和編寫測試的習慣，掌握一定的分析方法，把質量要求貫徹到底。
