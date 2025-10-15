# 輸入輸出流
**輸入輸出**是人機交互的一種方式。最常見的輸入輸出是標準輸入輸出和文件輸入輸出（當然還有數據庫輸入輸出，本節不討論這部分）。

## 標準輸入
標準輸入也叫作控制檯輸入，是常見輸入的一種。

**例子1：**

```rust
use std::io;

fn read_input() -> io::Result<()> {
    let mut input = String::new();

    try!(io::stdin().read_line(&mut input));

    println!("You typed: {}", input.trim());

    Ok(())
}

fn main() {
    read_input();
}
```

**例子2：**

```rust
use std::io;
fn main() {
    let mut input = String::new();

    io::stdin().read_line(&mut input).expect("WTF!");

    println!("You typed: {}", input.trim());
}
```

這裡體現了常見的標準輸入的處理方式。兩個例子都是聲明瞭一個可變的字符串來保存輸入的數據。
他們的不同之處在在於處理潛在輸入異常的方式。

1. 例子 1 使用了 `try!` 宏。這個宏會返回 `Result<(), io::Error>` 類型，`io::Result<()>` 就是這個類型的別名。所以例子 1 需要單獨使用一個 `read_input` 函數來接收這個類型，而不是在 `main` 函數里面，因為 `main` 函數並沒有接收 `io::Result<()>` 作為返回類型。

2. 例子 2 使用了 `Result<(), io::Error>` 類型的 `expect` 方法來接收 `io::stdin().read_line` 的返回類型。並處理可能潛在的 io 異常。

## 標準輸出
標準輸出也叫控制檯輸出，Rust 裡面常見的標準輸出宏有 `print!` 和 `println!`。它們的區別是後者比前者在末尾多輸出一個換行符。

**例子1：**

```rust
fn main() {
    print!("this ");
    print!("will ");
    print!("be ");
    print!("on ");
    print!("the ");
    print!("same ");
    print!("line ");

    print!("this string has a newline, why not choose println! instead?\n");
}
```

**例子2：**

```rust
fn main() {
    println!("hello there!");
    println!("format {} arguments", "some");
}
```

這裡兩個例子都比較簡單。讀者可以運行一下查看輸出結果對比一下他們的區別。
值得注意的是例子 2 中，`{ }` 會被 `"some"` 所替換。這是 rust 裡面的一種格式化輸出。

標準化的輸出是行緩衝(line-buffered)的,這就導致標準化的輸出在遇到一個新行之前並不會被隱式刷新。
換句話說  `print!` 和 `println!` 二者的效果並不總是相同的。
如果說得更簡單明瞭一點就是，您不能把 `print!` 當做是C語言中的 `printf` 譬如：

```rust
use std::io;
fn main() {
    print!("請輸入一個字符串：");
    let mut input = String::new();
    io::stdin()
        .read_line(&mut input)
        .expect("讀取失敗");
    print!("您輸入的字符串是：{}\n", input);
}
```

在這段代碼運行時則不會先出現預期的提示字符串，因為行沒有被刷新。
如果想要達到預期的效果就要顯示的刷新：

```rust
use std::io::{self, Write};
fn main() {
    print!("請輸入一個字符串：");
    io::stdout().flush().unwrap();
    let mut input = String::new();
    io::stdin()
        .read_line(&mut input)
        .expect("讀取失敗");
    print!("您輸入的字符串是：{}\n", input);
}
```

## 文件輸入

文件輸入和標準輸入都差不多，除了輸入流指向了文件而不是控制檯。下面例子採用了模式匹配來處理潛在的輸入錯誤

**例子：**

```rust
use std::error::Error;
use std::fs::File;
use std::io::prelude::*;
use std::path::Path;

fn main() {
    // 創建一個文件路徑
    let path = Path::new("hello.txt");
    let display = path.display();

    // 打開文件只讀模式, 返回一個 `io::Result<File>` 類型
    let mut file = match File::open(&path) {
        // 處理打開文件可能潛在的錯誤
        Err(why) => panic!("couldn't open {}: {}", display,
                                                   Error::description(&why)),
        Ok(file) => file,
    };

    // 文件輸入數據到字符串，並返回 `io::Result<usize>` 類型
    let mut s = String::new();
    match file.read_to_string(&mut s) {
        Err(why) => panic!("couldn't read {}: {}", display,
                                                   Error::description(&why)),
        Ok(_) => print!("{} contains:\n{}", display, s),
    }
}
```

## 文件輸出
文件輸出和標準庫輸出也差不多，只不過是把輸出流重定向到文件中。下面詳細看例子。

**例子：**

```rust
// 輸出文本
static LOREM_IPSUM: &'static str =
"Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
";

use std::error::Error;
use std::io::prelude::*;
use std::fs::File;
use std::path::Path;

fn main() {
    let path = Path::new("out/lorem_ipsum.txt");
    let display = path.display();

    // 用只寫模式打開一個文件，並返回 `io::Result<File>` 類型
    let mut file = match File::create(&path) {
        Err(why) => panic!("couldn't create {}: {}",
                           display,
                           Error::description(&why)),
        Ok(file) => file,
    };

    // 寫入 `LOREM_IPSUM` 字符串到文件中, 並返回 `io::Result<()>` 類型
    match file.write_all(LOREM_IPSUM.as_bytes()) {
        Err(why) => {
            panic!("couldn't write to {}: {}", display,
                                               Error::description(&why))
        },
        Ok(_) => println!("successfully wrote to {}", display),
    }
}
```
