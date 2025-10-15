
# 包和模塊

## 包（crate）

Rust 中，`crate` 是一個獨立的可編譯單元。具體說來，就是一個或一批文件（如果是一批文件，那麼有一個文件是這個 crate 的入口）。它編譯後，會對應著生成一個可執行文件或一個庫。

執行 `cargo new foo`，會得到如下目錄層級：

```
foo
├── Cargo.toml
└── src
    └── lib.rs
```

這裡，`lib.rs` 就是一個 crate（入口），它編譯後是一個庫。一個工程下可以包含不止一個 crate，本工程只有一個。

執行 `cargo new --bin bar`，會得到如下目錄層級：

```
bar
├── Cargo.toml
└── src
    └── main.rs
```

這裡，`main.rs` 就是一個 crate（入口），它編譯後是一個可執行文件。


## 模塊（module）

Rust 提供了一個關鍵字 `mod`，它可以在一個文件中定義一個模塊，或者引用另外一個文件中的模塊。

關於模塊的一些要點：

1. 每個 crate 中，默認實現了一個隱式的 `根模塊（root module）`；
2. 模塊的命名風格也是 `lower_snake_case`，跟其它的 Rust 的標識符一樣；
3. 模塊可以嵌套；
4. 模塊中可以寫任何合法的 Rust 代碼；

### 在文件中定義一個模塊

比如，在上述 `lib.rs` 中，我們寫上如下代碼：

```rust
mod aaa {
    const X: i32 = 10;

    fn print_aaa() {
        println!("{}", 42);
    }
}
```

我們可以繼續寫如下代碼：

```rust
mod aaa {
    const X: i32 = 10;

    fn print_aaa() {
        println!("{}", 42);
    }

    mod BBB {
        fn print_bbb() {
            println!("{}", 37);
        }
    }
}
```

還可以繼續寫：

```rust
mod aaa {
    const X: i32 = 10;

    fn print_aaa() {
        println!("{}", 42);
    }

    mod bbb {
        fn print_bbb() {
            println!("{}", 37);
        }
    }
}

mod ccc {
    fn print_ccc() {
        println!("{}", 25);
    }

}

```

### 模塊的可見性

我們前面寫了一些模塊，但實際上，我們寫那些模塊，目前是沒有什麼作用的。寫模塊的目的一是為了分隔邏輯塊，二是為了提供適當的函數，或對象，供外部訪問。而模塊中的內容，默認是私有的，只有模塊內部能訪問。

為了讓外部能使用模塊中 item，需要使用 `pub` 關鍵字。外部引用的時候，使用 `use` 關鍵字。例如：

```rust
mod ccc {
    pub fn print_ccc() {
        println!("{}", 25);
    }
}

fn main() {
    use ccc::print_ccc;

    print_ccc();
    // 或者
    ccc::print_ccc();
}
```

規則很簡單，一個 item（函數，綁定，Trait 等），前面加了 `pub`，那麼就它變成對外可見（訪問，調用）的了。


### 引用外部文件模塊

通常，我們會在單獨的文件中寫模塊內容，然後使用 `mod` 關鍵字來加載那個文件作為我們的模塊。

比如，我們在 `src` 下新建了文件 `aaa.rs`。現在目錄結構是下面這樣子：

```
foo
├── Cargo.toml
└── src
    └── aaa.rs
    └── main.rs
```

我們在 `aaa.rs` 中，寫上：

```rust
pub fn print_aaa() {
    println!("{}", 25);
}
```

在 `main.rs` 中，寫上：

```rust
mod aaa;

use self::aaa::print_aaa;

fn main () {
    print_aaa();
}
```

編譯後，生成一個可執行文件。

細心的朋友會發現，`aaa.rs` 中，沒有使用 `mod xxx {}` 這樣包裹起來，是因為 `mod xxx;` 相當於把 `xxx.rs` 文件用 `mod xxx {}` 包裹起來了。初學者往往會多加一層，請注意。


### 多文件模塊的層級關係

Rust 的模塊支持層級結構，但這種層級結構本身與文件系統目錄的層級結構是解耦的。

`mod xxx;` 這個 `xxx` 不能包含 `::` 號。也即在這個表達形式中，是沒法引用多層結構下的模塊的。也即，你不可能直接使用 `mod a::b::c::d;` 的形式來引用 `a/b/c/d.rs` 這個模塊。

那麼，Rust 的多層模塊遵循如下兩條規則：

1. 優先查找`xxx.rs` 文件
    1.  `main.rs`、`lib.rs`、`mod.rs`中的`mod xxx;` 默認優先查找同級目錄下的 `xxx.rs` 文件；
    2.  其他文件`yyy.rs`中的`mod xxx;`默認優先查找同級目錄的`yyy`目錄下的 `xxx.rs` 文件；
2. 如果 `xxx.rs` 不存在，則查找 `xxx/mod.rs` 文件，即 `xxx` 目錄下的 `mod.rs` 文件。

上述兩種情況，加載成模塊後，效果是相同的。Rust 就憑這兩條規則，通過迭代使用，結合 `pub` 關鍵字，實現了對深層目錄下模塊的加載；

下面舉個例子，現在我們建了一個測試工程，目錄結構如下：

```
src
├── a
│   ├── b
│   │   ├── c
│   │   │   ├── d.rs
│   │   │   └── mod.rs
│   │   └── mod.rs
│   └── mod.rs
└── main.rs

```

`a/b/c/d.rs` 文件內容：

```rust
pub fn print_ddd() {
    println!("i am ddd.");
}
```

`a/b/c/mod.rs` 文件內容：

```rust
pub mod d;
```

`a/b/mod.rs` 文件內容：

```rust
pub mod c;
```

`a/mod.rs` 文件內容：

```rust
pub mod b;
```

`main.rs` 文件內容：

```rust
mod a;

use self::a::b::c::d;

fn main() {
    d::print_ddd();
}

```
輸出結果為：`i am ddd.`

仔細理解本例子，就明白 Rust 的層級結構模塊的用法了。

至於為何 Rust 要這樣設計，有幾下幾個原因：

1. Rust 本身模塊的設計是與操作系統文件系統目錄解耦的，因為 Rust 本身可用於操作系統的開發；
2. Rust 中的一個文件內，可包含多個模塊，直接將 `a::b::c::d` 映射到 `a/b/c/d.rs` 會引起一些歧義；
3. Rust 一切從安全性、顯式化立場出發，要求引用路徑中的每一個節點，都是一個有效的模塊，比如上例，`d` 是一個有效的模塊的話，那麼，要求 `c, b, a` 分別都是有效的模塊，可單獨引用。


### 路徑

前面我們提到，一個 crate 是一個獨立的可編譯單元。它有一個入口文件，這個入口文件是這個 crate（裡面可能包含若干個 module）的模塊根路徑。整個模塊的引用，形成一個鏈，每個模塊，都可以用一個精確的路徑（比如：`a::b::c::d`）來表示；

與文件系統概念類似，模塊路徑也有相對路徑和絕對路徑的概念。為此，Rust 提供了 `self` 和 `super` 兩個關鍵字。

`self` 在路徑中，有兩種意思：

1. `use self::xxx` 表示，加載當前模塊中的 `xxx`。此時 self 可省略；
2. `use xxx::{self, yyy}`，表示，加載當前路徑下模塊 `xxx` 本身，以及模塊 `xxx` 下的 `yyy`；

`super` 表示，當前模塊路徑的上一級路徑，可以理解成父模塊。
```rust
use super::xxx;
```
表示引用父模塊中的 `xxx`。

另外，還有一種特殊的路徑形式：
```rust
::xxx::yyy
```
它表示，引用根路徑下的 `xxx::yyy`，這個根路徑，指的是當前 crate 的根路徑。

路徑中的 `*` 符號：
```rust
use xxx::*;
```
表示導入 `xxx` 模塊下的所有可見 item（加了 pub 標識的 item）。

### Re-exporting

我們可以結合使用 `pub use` 來實現 `Re-exporting`。`Re-exporting` 的字面意思就是 `重新導出`。它的意思是這樣的，把深層的 item 導出到上層目錄中，使調用的時候，更方便。接口設計中會大量用到這個技術。

還是舉上面那個 `a::b::c::d` 的例子。我們在 `main.rs` 中，要調用 `d`，得使用 `use a::b::c::d;` 來調用。而如果我們修改 `a/mod.rs` 文件為：
`a/mod.rs` 文件內容：

```rust
pub mod b;
pub use b::c::d;
```

那麼，我們在 `main.rs` 中，就可以使用 `use a::d;` 來調用了。從這個例子來看沒覺得方便多少。但是如果開發的一個庫中有大量的內容，而且是在不同層次的模塊中。那麼，通過統一導出到一個地方，就能大大方便接口使用者。

### 加載外部 crate

前面我們講的，都是在當前 crate 中的技術。真正我們在開發時，會大量用到外部庫。外部庫是通過

```rust
extern crate xxx;
```

這樣來引入的。

注：要使上述引用生效，還必須在 `Cargo.toml` 的 `dependecies` 段，加上 `xxx="version num"` 這種依賴說明，詳情見 `Cargo 項目管理` 這一章。

引入後，就相當於引入了一個符號 `xxx`，後面可以直接以這個 `xxx` 為根引用這個 crate 中的 item：

```rust
extern crate xxx;

use xxx::yyy::zzz;
```

引入的時候，可以通過 `as` 關鍵字重命名。

```rust
extern crate xxx as foo;

use foo::yyy::zzz;
```
