# 模塊與屬性

Rust有兩個與模塊 (module) 系統相關的獨特術語：`crate`和`module`，
其中包裝箱 (crate) 與其它語言中的 libary 或者 package 作用一樣。
每個包裝箱都有一個隱藏的根模塊，在根模塊下可以定義一個子模塊樹，
其路徑採用`::`作為分隔符。包裝箱由條目 (item) 構成，多個條目通過模塊組織在一起。

## 定義模塊

使用`mod`關鍵字定義我們的模塊：

```rust
// in src/lib.rs

mod chinese {
    mod greetings {

    }

    mod farewells {

    }
}

mod english {
    mod greetings {

    }

    mod farewells {

    }
}
```
定義了四個子模塊`chinese::{greetings, farewells}`和`english::{greetings, farewells}`。
模塊默認是私有的，可以使用`pub`關鍵字將其設置成公開，只有公開的條目才允許在模塊外部訪問。

實踐中更好的組織方式是將一個包裝箱分拆到多個文件：

```rust
// in src/lib.rs

pub mod chinese;

pub mod english;
```
這兩句聲明告訴Rust查看`src/chinese.rs`和`src/english.rs`，
或者`src/chinese/mod.rs`和`src/english/mod.rs`。
先添加一些函數：

```rust
// in src/chinese/greetings.rs

pub fn hello() -> String {
    "你好！".to_string()
}
```

```rust
// in src/chinese/farewells.rs

pub fn goodbye() -> String {
    "再見！".to_string()
}
```

```rust
// in src/english/greetings.rs

pub fn hello() -> String {
    "Hello!".to_string()
}
```

```rust
// in src/english/farewells.rs

pub fn goodbye() -> String {
    "Goodbye!".to_string()
}
```
函數默認也是私有的，為了後面的使用我們需要`pub`關鍵字使其成為公有。

## 導入 crate

為了使用我們前面創建的名為`phrases`的包裝箱，需要先聲明導入

```rust
// in src/main.rs

extern crate phrases;

fn main() {
    println!("Hello in Chinese: {}", phrases::chinese::greetings::hello());
}
```

Rust還有一個`use`關鍵字，允許我們導入包裝箱中的條目到當前的作用域內：

```rust
// in src/main.rs

extern crate phrases;

use phrases::chinese::greetings;
use phrases::chinese::farewells::goodbye;

fn main() {
    println!("Hello in Chinese: {}", greetings::hello());
    println!("Goodbye in Chinese: {}", goodbye());
}
```
但是，我們不推薦直接導入函數，這樣更容易導致命名空間衝突，只導入模塊是更好的做法。
如果要導入來自同一模塊的多個條目，可以使用大括號簡寫：

```rust
use phrases::chinese::{greetings, farewells};
```
如果是導入全部，可以使用通配符`*`。重命名可以使用`as`關鍵字：

```rust
use phrases::chinese::greetings as chinese_greetings;
```

有時我們需要將外部包裝箱裡面的函數導入到另一個模塊內，
這時可以使用`pub use`來提供擴展接口而不映射代碼層級結構。
比如

```rust
// in src/english/mod.rs

pub use self::greetings::hello;
pub use self::farewells::goodbye;

mod greetings;

mod farewells;
```
其中`pub use`聲明將函數帶入了當前模塊中，
使得我們現在有了`phrases::english::hello()`函數和`phrases::english::goodbye()`函數，
即使它們的定義位於`phrases::english::greetings::hello()`
和`phrases::english::farewells::goodbye()`中，
內部代碼的組織結構不能反映我們的擴展接口。

默認情況下，`use`聲明表示從根包裝箱開始的絕對路徑。
此外，我們可以使用`use self::`表示相對於當前模塊的位置，
`use super::`表示當前位置的上一級，以`::`為前綴的路徑表示根包裝箱路徑。

```rust
use foo::baz::foobaz; // foo is at the root of the crate

mod foo {
    use foo::bar::foobar; // foo is at crate root
    use self::baz::foobaz; // self refers to module 'foo'

    pub mod bar {
        pub fn foobar() { }
    }

    pub mod baz {
        use super::bar::foobar; // super refers to module 'foo'
        pub fn foobaz() { }
    }
}
```

## 屬性

在Rust中，屬性 (attribute) 是應用於包裝箱、模塊或者條目的元數據 (metadata)，
主要用於：

* 實現條件編譯 (conditional compilation)
* 設置包裝箱名字、版本以及類型
* 取消可疑代碼的警告
* 設置編譯器選項
* 鏈接外部庫
* 標記測試函數

屬性有兩種用法：`#![crate_attribute]`應用於整個包裝箱，
而`#[crate_attribute]`應用於緊鄰的一個模塊或者條目。
屬性的參數也有三種不同的形式：

* `#[attribute = "value"]`
* `#[attribute(key = "value")]`
* `#[attribute(value)]`

下面列舉幾個經常用到的屬性：

* `#[path="foo.rs"]`用於設置一個模塊需要載入的文件路徑。
* `#[allow(dead_code)]`用於取消對死代碼的默認lint檢查。
* `#[derive(PartialEq, Clone)]`用於自動推導`PartialEq`和`Clone`這兩個特性的實現。

