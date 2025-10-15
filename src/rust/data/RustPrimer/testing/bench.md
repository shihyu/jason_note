# 性能測試

單元測試是用來校驗程序的正確性的，然而，程序能正常運行後，往往還需要測試程序（一部分）的執行速度，這時，f就需要用到性能測試。
通常來講，所謂性能測試，指的是測量程序運行的速度，即運行一次要多少時間（通常是執行多次求平均值）。Rust 竟然連這個特性都集成在語言基礎特性中，真的是一門很重視工程性的語言。

下面直接說明如何使用。

```
cargo new benchit
cd benchit
```

編輯 `src/lib.rs` 文件，在裡面添加如下代碼：

```rust
#![feature(test)]

extern crate test;

pub fn add_two(a: i32) -> i32 {
    a + 2
}

#[cfg(test)]
mod tests {
    use super::*;
    use test::Bencher;

    #[test]
    fn it_works() {
        assert_eq!(4, add_two(2));
    }

    #[bench]
    fn bench_add_two(b: &mut Bencher) {
        b.iter(|| add_two(2));
    }
}
```

注意：

1. 這裡雖然使用了 `extern crate test;`，但是項目的 `Cargo.toml` 文件中依賴區並不需要添加對 `test` 的依賴；
2. 評測函數 `fn bench_add_two(b: &mut Bencher) {}` 上面使用 `#[bench]` 做標註，同時函數接受一個參數，`b` 就是 Rust 提供的評測器。這個寫法是固定的。

然後，在工程根目錄下，執行

```
cargo bench
```

輸出結果類似如下：

```
$ cargo bench
   Compiling benchit v0.0.1 (file:///home/mike/tmp/benchit)
     Running target/release/benchit-91b3e234d4ed382a

running 2 tests
test tests::it_works ... ignored
test tests::bench_add_two ... bench:         1 ns/iter (+/- 0)

test result: ok. 0 passed; 0 failed; 1 ignored; 1 measured
```

可以看到，Rust 的性能測試是以納秒 ns 為單位。

寫測評代碼的時候，需要注意以下一些點：

1. 只把你需要做性能測試的代碼（函數）放在評測函數中；
2. 對於參與做性能測試的代碼（函數），要求每次測試做同樣的事情，不要做累積和改變外部狀態的操作；
3. 參數性能測試的代碼（函數），執行時間不要太長。太長的話，最好分成幾個部分測試。這也方便找出性能瓶頸所在地方。

