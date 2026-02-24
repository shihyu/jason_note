# 如何標準Rust程式碼與Criterion

## 什麼是基準測試？

基準測試是測試您的程式碼性能的做法，以查看它能做多快（延遲）或多少（吞吐量）工作。 這在軟體開發中常被忽視的步驟是建立和維護快速和高性能程式碼的關鍵。 基準測試為開發人員提供了必要的指標，用於理解他們的程式碼在各種工作負載和條件下的表現如何。 出於防止功能回歸的同樣原因，你應該編寫測試以防止性能回歸。 性能問題也是問題！

## 用 Rust 編寫 FizzBuzz

為了編寫基準測試，我們需要一些原始碼來進行基準測試。 首先，我們將編寫一個非常簡單的程序， [FizzBuzz](https://en.wikipedia.org/wiki/Fizz_buzz#Programming)。

FizzBuzz的規則如下：

> 寫一個程序，列印從 `1` 到 `100` 的整數（包含）：
>
> - 對於三的倍數，列印 `Fizz`
> - 對於五的倍數，列印 `Buzz`
> - 對於既是三的倍數又是五的倍數的數，列印 `FizzBuzz`
> - 對於所有其他數，列印這個數字

有[許多種編寫FizzBuzz的方法](https://rosettacode.org/wiki/FizzBuzz)。 所以我們會選擇我最喜歡的一種：

```rust
fn main() {
    for i in 1..=100 {
        match (i % 3, i % 5) {
            (0, 0) => println!("FizzBuzz"),
            (0, _) => println!("Fizz"),
            (_, 0) => println!("Buzz"),
            (_, _) => println!("{i}"),
        }
    }
}
```

- 建立一個 `main` 函數
- 從 `1` 迭代到 `100`（含）。
- 對於每個數字，分別計算 `3` 和 `5` 的取餘（除後餘數）。
- 對兩個餘數進行模式匹配。 如果餘數為 `0`，那麼這個數就是給定因素的倍數。
- 如果 `3` 和 `5` 的餘數都為 `0`，則列印 `FizzBuzz`。
- 如果只有 `3` 的餘數為 `0`，則列印 `Fizz`。
- 如果只有 `5` 的餘數為 `0`，則列印 `Buzz`。
- 否則，就列印這個數字。

### 按步驟操作

為了與本教學進行同步學習，您需要 [安裝 Rust](https://rustup.rs/)。

> 🐰 這篇文章的原始碼在 [GitHub 上可以找到](https://github.com/bencherdev/bencher/tree/main/examples/rust/bench)

安裝好 Rust 後，您可以打開一個終端窗口，然後輸入：`cargo init game`

然後導航至新建立的 `game` 目錄。

```
game
├── Cargo.toml
└── src
    └── main.rs
```

你應該能看到一個名為 `src` 的目錄，其中有一個名為 `main.rs` 的檔案：

```rust
fn main() {
    println!("Hello, world!");
}
```

將其內容取代為上述的 FizzBuzz 實現。然後運行 `cargo run`。 輸出結果應該像這樣：

```
$ cargo run   Compiling playground v0.0.1 (/home/bencher)    Finished dev [unoptimized + debuginfo] target(s) in 0.44s     Running `target/debug/game`
12Fizz4BuzzFizz78FizzBuzz11Fizz1314FizzBuzz...9798FizzBuzz
```

> 🐰 砰！你正在破解程式設計面試！

應該生成了一個新的 `Cargo.lock` 檔案：

```
game
├── Cargo.lock
├── Cargo.toml
└── src
    └── main.rs
```

在進一步探討之前，有必要討論微基準測試和宏碁準測試之間的區別。

## 微基準測試 vs 宏碁準測試

有兩大類軟體基準測試：微基準測試和宏碁準測試。 微基準測試的操作層次和單元測試類似。 例如，為一個確定單個數字是 `Fizz`、 `Buzz`，還是 `FizzBuzz` 的函數設立的基準測試，就是一個微基準測試。 宏碁準測試的操作層次和整合測試類似。 例如，為一函數設立的基準測試，該函數可以玩完整個 FizzBuzz 遊戲，從 `1` 到 `100`，這就是一個宏碁準測試。

通常，儘可能在最低的抽象等級進行測試是最好的。 在基準測試的情況下，這使得它們更易於維護， 並有助於減少測量中的噪聲。 然而，就像有一些端到端測試對於健全性檢查整個系統根據預期組合在一起非常有用一樣， 擁有宏碁準測試對於確保您的軟體中的關鍵路徑保持高性能也非常有用。

## 在 Rust 中進行基準測試

在 Rust 中常用的基準測試工具有三種： [libtest bench](https://bencher.dev/learn/benchmarking/rust/libtest-bench/)， [Criterion](https://bencher.dev/learn/benchmarking/rust/criterion/)， 以及 [Iai](https://bencher.dev/learn/benchmarking/rust/iai/)。

libtest 是 Rust 的內建單元測試和基準測試框架。 儘管 libtest bench 是 Rust 標準庫的一部分，但它仍被認為是不穩定的， 所以它只在 `nightly` 編譯器版本中可用。 要在穩定的 Rust 編譯器上工作， 需要使用 [單獨的基準測試框架](https://github.com/bluss/bencher)。 然而，這兩者都不在積極開發中。

在 Rust 生態系統中，維護最積極的基準測試框架是 Criterion。 它既可以在穩定的 Rust 編譯器版本上運行，也可以在 `nightly`版本上運行， 它已經成為了 Rust 社區的事實標準。 與 libtest bench 相比，Criterion 還提供了更多的功能。

Criterion 的實驗性替代品是 Iai，它和 Criterion 的創作者是同一個人。 然而，它使用指令數量而不是牆鐘時間： CPU 指令，L1 訪問，L2 訪問以及 RAM 訪問。 這使得它可以進行單次基準測試，因為這些指標在運行間應該保持幾乎一致。

三者都是[由Bencher支援的](https://bencher.dev/zh/docs/explanation/adapters/)。那麼為什麼要選擇Criterion呢？ Criterion是Rust社區的事實標準基準測試工具。 我推薦使用Criterion來測試你的程式碼的延遲。 也就是說，Criterion非常適合測量時鐘時間。

### 重構 FizzBuzz

為了測試我們的 FizzBuzz 應用，我們需要將邏輯從程序的 `main` 函數中解耦出來。 基準測試工具無法對 `main` 函數進行基準測試。為了做到這一點，我們需要做一些改動。

在 `src` 下，建立一個新的名為 `lib.rs` 的檔案：

```
game
├── Cargo.lock
├── Cargo.toml
└── src
    └── lib.rs
    └── main.rs
```

將以下程式碼新增到 `lib.rs`：

```rust
pub fn play_game(n: u32, print: bool) {
    let result = fizz_buzz(n);
    if print {
        println!("{result}");
    }
}
pub fn fizz_buzz(n: u32) -> String {
    match (n % 3, n % 5) {
        (0, 0) => "FizzBuzz".to_string(),
        (0, _) => "Fizz".to_string(),
        (_, 0) => "Buzz".to_string(),
        (_, _) => n.to_string(),
    }
}

```

- `play_game`：接受一個無符號整數 `n`，用該數字呼叫 `fizz_buzz`，如果 `print` 為 `true`，則列印結果。
- `fizz_buzz`：接受一個無符號整數 `n`，執行實際的 `Fizz`、`Buzz`、`FizzBuzz` 或數字邏輯，然後將結果作為字串返回。

然後更新 `main.rs`，使其看起來像這樣：

```rust
use game::play_game;
fn main() {
    for i in 1..=100 {
        play_game(i, true);
    }
}
```

- `game::play_game`：從我們剛剛用 `lib.rs` 建立的 `game` 包中匯入 `play_game`。
- `main`：我們程序的主入口點，遍歷從 `1` 到 `100` 的數字，對每個數字呼叫 `play_game`，並將 `print` 設為 `true`。

## 對FizzBuzz的基準測試

為了對我們的程式碼進行基準測試，我們需要建立一個`benches`目錄，並新增一個檔案來包含我們的基準測試，`play_game.rs`：

```
game
├── Cargo.lock
├── Cargo.toml
└── benches
    └── play_game.rs
└── src
    └── lib.rs
    └── main.rs
```

在`play_game.rs`中增加下列程式碼：

```rust
use criterion::{criterion_group, criterion_main, Criterion};
use game::play_game;
fn bench_play_game(c: &mut Criterion) {
    c.bench_function("bench_play_game", |b| {
        b.iter(|| {
            std::hint::black_box(for i in 1..=100 {
                play_game(i, false)
            });
        });
    });
}
criterion_group!(benches, bench_play_game,);
criterion_main!(benches);
```

- 匯入`Criterion`基準測試運行器。
- 從我們的`game`包中匯入`play_game`函數。
- 建立一個名為`bench_play_game`的函數，它接受一個對`Criterion`的可變引用。
- 使用`Criterion`實例（`c`）來建立一個名為`bench_play_game`的基準測試。
- 然後使用基準測試運行器（`b`）來多次運行我們的宏碁準測試。
- 在一個”黑箱”中運行我們的宏碁準測試，這樣編譯器就不會最佳化我們的程式碼。
- 從`1`到`100`包括，進行迭代。
- 對於每一個數字，呼叫`play_game`，設定`print`為`false`。

現在我們需要組態`game`包來運行我們的基準測試。

在你的`Cargo.toml`檔案的底部新增以下內容：

```
[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "play_game"
harness = false
```

- `criterion`：將`criterion`新增為開發依賴，因為我們只在性能測試中使用它。
- `bench`：註冊`play_game`作為一個基準測試，並設定`harness`為`false`，因為我們將使用Criterion作為我們的基準測試工具。

現在我們已經準備好進行基準測試了，運行`cargo bench`：

```shell
$ cargo bench
   Compiling playground v0.0.1 (/home/bencher)
    Finished bench [optimized] target(s) in 4.79s
     Running unittests src/main.rs (target/release/deps/game-68f58c96f4025bd4)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running unittests src/main.rs (target/release/deps/game-043972c4132076a9)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running benches/play_game.rs (target/release/deps/play_game-e0857103eb02eb56)
bench_play_game         time:   [3.0020 µs 3.0781 µs 3.1730 µs]
Found 12 outliers among 100 measurements (12.00%)
  2 (2.00%) high mild
  10 (10.00%) high severe
```

> 🐰 讓我們調高節拍！我們已經得到了第一個基準測試指標！

最後，我們可以讓我們疲倦的開發者頭腦得到休息… 開玩笑，我們的使用者想要一個新功能！

## 用 Rust 編寫 FizzBuzzFibonacci

我們的關鍵績效指標（KPI）下降了，所以我們的產品經理（PM）希望我們新增新功能。 經過多次頭腦風暴和許多使用者採訪後，我們決定光有 FizzBuzz 已經不夠了。 現在的孩子們希望有一個新的遊戲，FizzBuzzFibonacci。

FizzBuzzFibonacci的規則如下：

> 編寫一個程序，列印從 `1` 到 `100` 的整數（包括）：
>
> - 對於三的倍數，列印 `Fizz`
> - 對於五的倍數，列印 `Buzz`
> - 對於既是三的倍數又是五的倍數的，列印 `FizzBuzz`
> - 對於是斐波那契數列的數字，只列印 `Fibonacci`
> - 對於所有其他的，列印該數

[斐波那契數列](https://zh.wikipedia.org/wiki/斐波那契數列)是一個每個數字是前兩個數字之和的序列。 例如，從 `0` 和 `1`開始，斐波那契數列的下一個數字將是 `1`。 後面是：`2`, `3`, `5`, `8` 等等。 斐波那契數列的數字被稱為斐波那契數。所以我們將不得不編寫一個檢測斐波那契數的函數。

有[許多方法可以編寫斐波那契數列](https://rosettacode.org/wiki/Fibonacci_sequence)，同樣也有許多方法可以檢測一個斐波那契數。 所以我們將採用我的最愛：

```rust
fn is_fibonacci_number(n: u32) -> bool {
    for i in 0..=n {
        let (mut previous, mut current) = (0, 1);
        while current < i {
            let next = previous + current;
            previous = current;
            current = next;
        }
        if current == n {
            return true;
        }
    }
    false
}
```

- 建立一個名為 `is_fibonacci_number` 的函數，該函數接收一個無符號整數，並返回一個布林值。
- 遍歷從 `0` 到我們給定的數 `n`（包含 `n`）的所有數字。
- 用 `0` 和 `1` 分別作為`前一個` 和 `當前` 數字來初始化我們的斐波那契序列。
- 當`當前`數字小於當前迭代 `i` 時持續迭代。
- 新增`前一個` 和 `當前` 數字來獲得 `下一個` 數字。
- 將 `前一個` 數字更新為 `當前` 數字。
- 將 `當前` 數字更新為 `下一個` 數字。
- 一旦 `當前` 大於或等於給定數字 `n`，我們將退出循環。
- 檢查 `當前` 數字是否等於給定數字 `n`，如果是，則返回 `true`。
- 否則，返回 `false`。

現在我們需要更新我們的 `fizz_buzz` 功能：

```rust
pub fn fizz_buzz_fibonacci(n: u32) -> String {
    if is_fibonacci_number(n) {
        "Fibonacci".to_string()
    } else {
        match (n % 3, n % 5) {
            (0, 0) => "FizzBuzz".to_string(),
            (0, _) => "Fizz".to_string(),
            (_, 0) => "Buzz".to_string(),
            (_, _) => n.to_string(),
        }
    }
}
```

- 將 `fizz_buzz` 功能重新命名為 `fizz_buzz_fibonacci` 以使其更具描述性。
- 呼叫我們的 `is_fibonacci_number` 輔助函數。
- 如果 `is_fibonacci_number` 的結果為 `true`，則返回 `Fibonacci`。
- 如果 `is_fibonacci_number` 的結果為 `false`，則執行相同的 `Fizz`、`Buzz`、`FizzBuzz` 或數字邏輯，並返回結果。

因為我們將 `fizz_buzz` 重新命名為 `fizz_buzz_fibonacci`，我們也需要更新我們的 `play_game` 功能：

```rust
pub fn play_game(n: u32, print: bool) {
    let result = fizz_buzz_fibonacci(n);
    if print {
        println!("{result}");
    }
}
```

我們的 `main` 和 `bench_play_game` 功能可以保持完全相同。

## 對FizzBuzzFibonacci的基準測試

現在我們可以重新運行我們的基準測試了：

```
$ cargo bench
   Compiling playground v0.0.1 (/home/bencher)
    Finished bench [optimized] target(s) in 4.79s
     Running unittests src/main.rs (target/release/deps/game-68f58c96f4025bd4)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running unittests src/main.rs (target/release/deps/game-043972c4132076a9)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running benches/play_game.rs (target/release/deps/play_game-e0857103eb02eb56)
bench_play_game         time:   [20.067 µs 20.107 µs 20.149 µs]
                        change: [+557.22% +568.69% +577.93%] (p = 0.00 < 0.05)
                        Performance has regressed.
Found 6 outliers among 100 measurements (6.00%)
  4 (4.00%) high mild
  2 (2.00%) high severe
```

哦哦！Criterion向我們顯示了FizzBuzz和FizzBuzzFibonacci遊戲之間性能差距為`+568.69%`。 你的數字會比我的稍微有些不同。 然而，兩者之間的差距可能在`5x`的範圍內。 這對我來說看起來是比較好的結果！特別是考慮到我們將像_Fibonacci_這樣的花哨功能新增到我們的遊戲中。 孩子們會喜歡的！

## 在 Rust 中展開 FizzBuzzFibonacci

我們的遊戲很受歡迎！孩子們確實喜歡玩 FizzBuzzFibonacci。 為此，高層下達了他們想要續集的消息。 但這是現代世界，我們需要的是年度循環收入（ARR），而不是一次性購買！ 我們遊戲的新願景是開放性的，不再固定在 `1` 和 `100` 之間（即使是包含在內的）。 不，我們正在開拓新的疆域！

Open World FizzBuzzFibonacci的規則如下：

> 編寫一個程序，它接受_任何_正整數並列印：
>
> - 對於三的倍數，列印 `Fizz`
> - 對於五的倍數，列印 `Buzz`
> - 對於同時是三和五的倍數的，則列印 `FizzBuzz`
> - 對於是斐波那契數列的數字，只列印 `Fibonacci`
> - 對於其他所有數字，列印該數字

為了讓我們的遊戲適應任何數字，我們需要接受一個命令列參數。 將 `main` 函數更新為如下形式：

```rust
fn main() {
    let args: Vec<String> = std::env::args().collect();
    let i = args
        .get(1)
        .map(|s| s.parse::<u32>())
        .unwrap_or(Ok(15))
        .unwrap_or(15);
    play_game(i, true);
}
```

- 收集所有從命令列傳遞給我們遊戲的參數（`args`）。
- 獲取傳遞給我們遊戲的第一個參數，並將其解析為無符號整數 `i`。
- 如果解析失敗或沒有傳入參數，就默認以 `15` 作為輸入運行我們的遊戲。
- 最後，用新解析的無符號整數 `i` 來玩我們的遊戲。

現在我們可以用任何數字來玩我們的遊戲了！ 使用 `cargo run` 後跟 `--` 將參數傳遞給我們的遊戲：

```
$ cargo run -- 9
   Compiling playground v0.0.1 (/home/bencher)
    Finished dev [unoptimized + debuginfo] target(s) in 0.44s
     Running `target/debug/game 9`
Fizz
$ cargo run -- 10
    Finished dev [unoptimized + debuginfo] target(s) in 0.03s
     Running `target/debug/game 10`
Buzz
$ cargo run -- 13
    Finished dev [unoptimized + debuginfo] target(s) in 0.04s
     Running `target/debug/game 13`
Fibonacci
```

如果我們省略或提供了無效的數字：

```
$ cargo run
    Finished dev [unoptimized + debuginfo] target(s) in 0.03s
     Running `target/debug/game`
FizzBuzz
$ cargo run -- bad
    Finished dev [unoptimized + debuginfo] target(s) in 0.05s
     Running `target/debug/game bad`
FizzBuzz
```

哇，這是一個仔細的測試過程！CI 通過了。我們的上司非常高興。 讓我們發佈吧！🚀

## 結束

![海綿寶寶三週後](images/three-weeks-later.jpeg)

![一切正常的模因](images/this-is-fine.jpg)

> 🐰 … 也許這是你的職業生涯的結束？

## 開玩笑的！其實一切都在燃燒！🔥

起初，一切看似進行得順利。 但在週六早上02:07，我的尋呼機響了起來：

> 📟 你的遊戲起火了！🔥

從床上匆忙爬起來後，我試圖弄清楚發生了什麼。 我試圖搜尋日誌，但這非常困難，因為一切都在不停地崩潰。 最後，我發現了問題。孩子們！他們非常喜歡我們的遊戲，以至於玩了高達一百萬次！ 在一股靈感的閃現中，我新增了兩個新的基準測試：

```rust
fn bench_play_game_100(c: &mut Criterion) {
    c.bench_function("bench_play_game_100", |b| {
        b.iter(|| std::hint::black_box(play_game(100, false)));
    });
}
fn bench_play_game_1_000_000(c: &mut Criterion) {
    c.bench_function("bench_play_game_1_000_000", |b| {
        b.iter(|| std::hint::black_box(play_game(1_000_000, false)));
    });
}
```

- 一個用於玩遊戲並輸入數字一百（`100`）的微基準測試`bench_play_game_100`。
- 一個用於玩遊戲並輸入數字一百萬（`1_000_000`）的微基準測試`bench_play_game_1_000_000`。
    
當我運行它時，我得到了這個：

```
$ cargo bench
   Compiling playground v0.0.1 (/home/bencher)
    Finished bench [optimized] target(s) in 4.79s
     Running unittests src/main.rs (target/release/deps/game-68f58c96f4025bd4)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running unittests src/main.rs (target/release/deps/game-043972c4132076a9)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running benches/play_game.rs (target/release/deps/play_game-e0857103eb02eb56)
bench_play_game         time:   [20.024 µs 20.058 µs 20.096 µs]
                        change: [-0.0801% +0.1431% +0.3734%] (p = 0.21 > 0.05)
                        No change in performance detected.
Found 17 outliers among 100 measurements (17.00%)
  9 (9.00%) high mild
  8 (8.00%) high severe

bench_play_game_100     time:   [403.00 ns 403.57 ns 404.27 ns]
Found 13 outliers among 100 measurements (13.00%)
  6 (6.00%) high mild
  7 (7.00%) high severe
```

等待一下… 等待一下…

```
bench_play_game_1_000_000
                        time:   [9.5865 ms 9.5968 ms 9.6087 ms]
Found 16 outliers among 100 measurements (16.00%)
  8 (8.00%) high mild
  8 (8.00%) high severe
```

什麼！`403.57 ns` x `1,000` 應該是 `403,570 ns` 而不是 `9,596,800 ns` (`9.5968 ms` x `1_000_000 ns/1 ms`) 🤯 儘管我的斐波那契數列程式碼功能上是正確的，我必須在某個地方有一個性能bug。

## 修復 Rust 中的 FizzBuzzFibonacci

讓我們再次看一下 `is_fibonacci_number` 函數：

```rust
fn is_fibonacci_number(n: u32) -> bool {
    for i in 0..=n {
        let (mut previous, mut current) = (0, 1);
        while current < i {
            let next = previous + current;
            previous = current;
            current = next;
        }
        if current == n {
            return true;
        }
    }
    false
}
```

現在我在考慮性能，我意識到我有一個不必要的，額外的循環。 我們可以完全擺脫 `for i in 0..=n {}` 循環， 只需直接比較 `current` 值和給定的數字 (`n`) 🤦

```rust
fn is_fibonacci_number(n: u32) -> bool {
    let (mut previous, mut current) = (0, 1);
    while current < n {
        let next = previous + current;
        previous = current;
        current = next;
    }
    current == n
}
```

- 更新您的 `is_fibonacci_number` 函數。
- 用 `0` 和 `1` 初始化我們的斐波那契序列作為 `previous` 和 `current` 數字。
- 當 `current` 數字小於 *給定數字* `n` 時迭代。
- 將 `previous` 和 `current` 數字相加以獲得 `next` 數字。
- 把 `previous` 數字更新為 `current` 數字。
- 把 `current` 數字更新為 `next` 數字。
- 一旦 `current` 大於或等於給定的數字 `n`，我們將退出循環。
- 檢查 `current` 數字是否等於給定的數字 `n` 並返回該結果。

現在，讓我們重新運行這些基準測試，看看我們做得如何：

```
$ cargo bench
   Compiling playground v0.0.1 (/home/bencher)
    Finished bench [optimized] target(s) in 4.79s
     Running unittests src/main.rs (target/release/deps/game-68f58c96f4025bd4)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running unittests src/main.rs (target/release/deps/game-043972c4132076a9)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running benches/play_game.rs (target/release/deps/play_game-e0857103eb02eb56)
bench_play_game         time:   [3.1201 µs 3.1772 µs 3.2536 µs]
                        change: [-84.469% -84.286% -84.016%] (p = 0.00 < 0.05)
                        Performance has improved.
Found 5 outliers among 100 measurements (5.00%)
  1 (1.00%) high mild
  4 (4.00%) high severe

bench_play_game_100     time:   [24.460 ns 24.555 ns 24.650 ns]
                        change: [-93.976% -93.950% -93.927%] (p = 0.00 < 0.05)
                        Performance has improved.

bench_play_game_1_000_000
                        time:   [30.260 ns 30.403 ns 30.564 ns]
                        change: [-100.000% -100.000% -100.000%] (p = 0.00 < 0.05)
                        Performance has improved.
Found 4 outliers among 100 measurements (4.00%)
  1 (1.00%) high mild
  3 (3.00%) high severe
```

哦哇！我們的`bench_play_game`基準測試回落到原來FizzBuzz測試的附近位置。 我希望我能記住那個得分是多少。但是已經過了三個星期了。 我的終端歷史記錄沒有回溯這麼遠。 而Criterion只會和最近的結果進行比較。 但我認為這是很接近的！

`bench_play_game_100`基準測試的結果下降了近10倍，`-93.950%`。 和`bench_play_game_1_000_000`基準測試的結果下降了超過10,000倍！從`9,596,800 ns`降到`30.403 ns`！ 我們甚至讓Criterion的改變計數器達到了最大值，它只會達到`-100.000%`！

> 🐰 嘿，至少我們在性能bug趕到生產環境之前抓住了它… 哦，對了。算了…

## 在 CI 中捕獲性能回歸

由於我那個小小的性能錯誤，我們的遊戲收到了大量的負面評論，這讓高管們非常不滿。 他們告訴我不要讓這種情況再次發生，而當我詢問如何做到時，他們只是告訴我不要再犯。 我該如何管理這個問題呢‽

幸運的是，我找到了這款叫做 Bencher 的超棒開源工具。 它有一個非常慷慨的免費層，因此我可以在我的個人項目中使用 [Bencher Cloud](https://bencher.dev/)。 而在工作中需要在我們的私有雲內，我已經開始使用 [Bencher Self-Hosted](https://bencher.dev/zh/docs/tutorial/docker/)。

Bencher有一個[內建的介面卡](https://bencher.dev/zh/docs/explanation/adapters/)， 所以很容易整合到 CI 中。在[遵循快速開始指南](https://bencher.dev/zh/docs/tutorial/quick-start/)後， 我能夠運行我的基準測試並用 Bencher 追蹤它們。

```
$ bencher run --project game "cargo bench"
    Finished bench [optimized] target(s) in 0.07s
     Running unittests src/lib.rs (target/release/deps/game-13f4bad779fbfde4)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running unittests src/main.rs (target/release/deps/game-043972c4132076a9)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running benches/play_game.rs (target/release/deps/play_game-e0857103eb02eb56)
Gnuplot not found, using plotters backend
bench_play_game         time:   [3.0713 µs 3.0902 µs 3.1132 µs]
Found 16 outliers among 100 measurements (16.00%)
  3 (3.00%) high mild
  13 (13.00%) high severe

bench_play_game_100     time:   [23.938 ns 23.970 ns 24.009 ns]
Found 15 outliers among 100 measurements (15.00%)
  5 (5.00%) high mild
  10 (10.00%) high severe

bench_play_game_1_000_000
                        time:   [30.004 ns 30.127 ns 30.279 ns]
Found 5 outliers among 100 measurements (5.00%)
  1 (1.00%) high mild
  4 (4.00%) high severe

Bencher New Report:
...
View results:
- bench_play_game (Latency): https://bencher.dev/console/projects/game/perf?measures=52507e04-ffd9-4021-b141-7d4b9f1e9194&branches=3a27b3ce-225c-4076-af7c-75adbc34ef9a&testbeds=bc05ed88-74c1-430d-b96a-5394fdd18bb0&benchmarks=077449e5-5b45-4c00-bdfb-3a277413180d&start_time=1697224006000&end_time=1699816009000&upper_boundary=true
- bench_play_game_100 (Latency): https://bencher.dev/console/projects/game/perf?measures=52507e04-ffd9-4021-b141-7d4b9f1e9194&branches=3a27b3ce-225c-4076-af7c-75adbc34ef9a&testbeds=bc05ed88-74c1-430d-b96a-5394fdd18bb0&benchmarks=96508869-4fa2-44ac-8e60-b635b83a17b7&start_time=1697224006000&end_time=1699816009000&upper_boundary=true
- bench_play_game_1_000_000 (Latency): https://bencher.dev/console/projects/game/perf?measures=52507e04-ffd9-4021-b141-7d4b9f1e9194&branches=3a27b3ce-225c-4076-af7c-75adbc34ef9a&testbeds=bc05ed88-74c1-430d-b96a-5394fdd18bb0&benchmarks=ff014217-4570-42ea-8813-6ed0284500a4&start_time=1697224006000&end_time=1699816009000&upper_boundary=true
```

使用這個由一個友善的兔子給我的巧妙的時間旅行裝置， 我能夠回到過去，重演如果我們一直都在使用Bencher的情況下會發生什麼。 你可以看到我們首次推出存在問題的FizzBuzzFibonacci實現的位置。 我馬上在我的拉取請求評論中得到了CI的失敗資訊。 就在那天，我修復了性能問題，擺脫了那不必要的額外循環。 沒有火災。顧客都非常開心。

<iframe title="如何用Criterion對Rust進行基準測試" width="100%" height="800px" src="https://bencher.dev/perf/game/embed?reports_per_page=4&amp;reports_page=1&amp;branches_per_page=8&amp;branches_page=1&amp;testbeds_per_page=8&amp;testbeds_page=1&amp;benchmarks_per_page=8&amp;benchmarks_page=1&amp;clear=true&amp;tab=benchmarks&amp;measures=52507e04-ffd9-4021-b141-7d4b9f1e9194&amp;branches=3a27b3ce-225c-4076-af7c-75adbc34ef9a&amp;testbeds=bc05ed88-74c1-430d-b96a-5394fdd18bb0&amp;benchmarks=077449e5-5b45-4c00-bdfb-3a277413180d&amp;upper_boundary=true&amp;start_time=1697414400000" style="box-sizing: inherit; margin: 0px; padding: 0px; border: 1rem solid rgb(237, 103, 4); color: rgb(74, 74, 74); font-family: BlinkMacSystemFont, -apple-system, &quot;Segoe UI&quot;, Roboto, Oxygen, Ubuntu, Cantarell, &quot;Fira Sans&quot;, &quot;Droid Sans&quot;, &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif; font-size: 16px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 400; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; white-space: normal; background-color: rgb(255, 255, 255); text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial;"></iframe>



## [Bencher](https://bencher.dev/pricing): 持續性能基準測試

[![🐰 Bencher](https://bencher.dev/wordmark.svg)](https://bencher.dev/pricing)

[Bencher](https://bencher.dev/pricing)是一套持續型的性能基準測試工具。 你是否曾經因為性能回歸影響到了你的使用者？ Bencher可以防止這種情況的發生。 Bencher讓你有能力在性能回歸進入生產環境 *之前* 就進行檢測和預防。

- **運行**: 使用你喜愛的基準測試工具在本地或CI中執行你的基準測試。`bencher` CLI簡單地包裝了你現有的基準測驗裝置並儲存其結果。
- **追蹤**: 追蹤你的基準測試結果的趨勢。根據源分支、測試床和度量，使用Bencher web控制檯來監視、查詢和繪製結果圖表。
- **捕獲**: 在CI中捕獲性能回歸。Bencher使用最先進的、可定製的分析技術在它們進入生產環境之前就檢測到性能回歸。

基於防止功能回歸的原因，在CI中運行單元測試，我們也應該使用Bencher在CI中運行基準測試以防止性能回歸。性能問題就是錯誤！

開始在CI中捕捉性能回歸 — [免費試用Bencher Cloud](https://bencher.dev/pricing)。
