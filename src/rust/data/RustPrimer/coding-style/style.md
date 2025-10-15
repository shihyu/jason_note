# 代碼風格

## 空白

* 每行不能超出99個字符。
* 縮進只用空格，不用TAB。
* 行和文件末尾不要有空白。

### 空格

* 二元運算符左右加空格，包括屬性裡的等號：

``` rust
#[deprecated = "Use `bar` instead."]
fn foo(a: usize, b: usize) -> usize {
    a + b
}
```

* 在分號和逗號後面加空格：

``` rust
fn foo(a: Bar);

MyStruct { foo: 3, bar: 4 }

foo(bar, baz);
```

* 在單行語句塊或`struct`表達式的開始大括號之後和結束大括號之前加空格：

``` rust
spawn(proc() { do_something(); })

Point { x: 0.1, y: 0.3 }
```

### 折行

* 對於多行的函數簽名，每個新行和第一個參數對齊。允許每行多個參數：

``` rust
fn frobnicate(a: Bar, b: Bar,
              c: Bar, d: Bar)
              -> Bar {
    ...
}

fn foo<T: This,
       U: That>(
       a: Bar,
       b: Bar)
       -> Baz {
    ...
}
```

* 多行函數調用一般遵循和簽名統一的規則。然而，如果最後的參數開始了一個語句塊，塊的內容可以開始一個新行，縮進一層：

``` rust
fn foo_bar(a: Bar, b: Bar,
           c: |Bar|) -> Bar {
    ...
}

// 可以在同一行：
foo_bar(x, y, |z| { z.transpose(y) });

// 也可以在新一行縮進函數體：
foo_bar(x, y, |z| {
    z.quux();
    z.rotate(x)
})
```


### 對齊

常見代碼不必在行中用多餘的空格來對齊。


``` rust
// 好
struct Foo {
    short: f64,
    really_long: f64,
}

// 壞
struct Bar {
    short:       f64,
    really_long: f64,
}

// 好
let a = 0;
let radius = 7;

// 壞
let b        = 0;
let diameter = 7;
```

### 避免塊註釋

使用行註釋：

``` rust
// 等待主線程返回，並設置過程錯誤碼
// 明顯地。
```

而不是：

``` rust
/*
 * 等待主線程返回，並設置過程錯誤碼
 * 明顯地。
 */
```

## 文檔註釋

文檔註釋前面加三個斜線(`///`)而且提示你希望將註釋包含在 Rustdoc 的輸出裡。
它們支持 [Markdown 語言](https://en.wikipedia.org/wiki/Markdown)
而且是註釋你的公開API的主要方式。

支持的 markdown 功能包括列在 [GitHub Flavored Markdown](https://help.github.com/articles/github-flavored-markdown) 文檔中的所有擴展，加上上角標。

### 總結行

任何文檔註釋中的第一行應該是一行總結代碼的單行短句。該行用於在 Rustdoc 輸出中的一個簡短的總結性描述，所以，讓它短比較好。

### 句子結構

所有的文檔註釋，包括總結行，一個以大寫字母開始，以句號、問號，或者感嘆號結束。最好使用完整的句子而不是片段。

總結行應該以 [第三人稱單數陳述句形式](http://en.wikipedia.org/wiki/English_verbs#Third_person_singular_present) 來寫。
基本上，這意味著用 "Returns" 而不是 "Return"。

例如：

``` rust
/// 根據編譯器提供的參數，設置一個缺省的運行時配置。
///
/// 這個函數將阻塞直到整個 M:N 調度器池退出了。
/// 這個函數也要求一個本地的線程可用。
///
/// # 參數
///
/// * `argc` 和 `argv` - 參數向量。在 Unix 系統上，該信息被`os::args`使用。
///
/// * `main` - 運行在 M:N 調度器池內的初始過程。
///            一旦這個過程退出，調度池將開始關閉。
///            整個池（和這個函數）將只有在所有子線程完成執行後。
///
/// # 返回值
///
/// 返回值被用作進程返回碼。成功是 0，101 是錯誤。
```

### 避免文檔內註釋

內嵌文檔註釋 _只用於_ 註釋 crates 和文件級的模塊：

``` rust
//! 核心庫。
//!
//! 核心庫是...
```

### 解釋上下文

Rust 沒有特定的構造器，只有返回新實例的函數。
這些在自動生成的類型文檔中是不可見的，因此你應該專門鏈接到它們：

``` rust
/// An iterator that yields `None` forever after the underlying iterator
/// yields `None` once.
///
/// These can be created through
/// [`iter.fuse()`](trait.Iterator.html#method.fuse).
pub struct Fuse<I> {
    // ...
}
```

### 開始的大括號總是出現的同一行。

``` rust
fn foo() {
    ...
}

fn frobnicate(a: Bar, b: Bar,
              c: Bar, d: Bar)
              -> Bar {
    ...
}

trait Bar {
    fn baz(&self);
}

impl Bar for Baz {
    fn baz(&self) {
        ...
    }
}

frob(|x| {
    x.transpose()
})
```

### `match` 分支有大括號，除非是單行表達式。

``` rust
match foo {
    bar => baz,
    quux => {
        do_something();
        do_something_else()
    }
}
```

### `return` 語句有分號。

``` rust
fn foo() {
    do_something();

    if condition() {
        return;
    }

    do_something_else();
}
```

### 行尾的逗號

```rust
Foo { bar: 0, baz: 1 }

Foo {
    bar: 0,
    baz: 1,
}

match a_thing {
    None => 0,
    Some(x) => 1,
}
```

### 一般命名約定

通常，Rust 傾向於為“類型級”結構(類型和 traits)使用 `CamelCase` 而為“值級”結構使用 `snake_case` 。更確切的約定：

| 條目 | 約定 |
| ---- | ---------- |
| Crates | `snake_case` (但傾向於單個詞) |
| Modules | `snake_case` |
| Types | `CamelCase` |
| Traits | `CamelCase` |
| Enum variants | `CamelCase` |
| Functions | `snake_case` |
| Methods | `snake_case` |
| General constructors | `new` 或 `with_more_details` |
| Conversion constructors | `from_some_other_type` |
| Local variables | `snake_case` |
| Static variables | `SCREAMING_SNAKE_CASE` |
| Constant variables | `SCREAMING_SNAKE_CASE` |
| Type parameters | 簡潔 `CamelCase`，通常單個大寫字母：`T` |
| Lifetimes | 短的小寫: `'a` |

<p>
在 `CamelCase`中, 首字母縮略詞被當成一個單詞：用 `Uuid` 而不是
`UUID`。在 `snake_case` 中，首字母縮略詞全部是小寫： `is_xid_start`。

在 `snake_case` 或 `SCREAMING_SNAKE_CASE` 中，“單詞”永遠不應該只包含一個字母，
除非是最後一個“單詞”。所以，我們有`btree_map` 而不是 `b_tree_map`，`PI_2` 而不是 `PI2`。

### 引用函數/方法名中的類型

函數名經常涉及類型名，最常見的約定例子像 `as_slice`。如果類型有一個純粹的文本名字（忽略參數），
在類型約定和函數約定之間轉換是直截了當的：

類型名 | 方法中的文本
--------- | ---------------
`String`  | `string`
`Vec<T>`  | `vec`
`YourType`| `your_type`

涉及記號的類型遵循以下約定。這些規則有重疊；應用最適用的規則：

類型名 | 方法中的文本
--------- | ---------------
`&str`    | `str`
`&[T]`    | `slice`
`&mut [T]`| `mut_slice`
`&[u8]`   | `bytes`
`&T`      | `ref`
`&mut T`  | `mut`
`*const T`| `ptr`
`*mut T`  | `mut_ptr`

### 避免冗餘的前綴

一個模塊中的條目的名字不應拿模塊的名字做前綴：

傾向於

``` rust
mod foo {
    pub struct Error { ... }
}
```

而不是

``` rust
mod foo {
    pub struct FooError { ... }
}
```

這個約定避免了口吃（像 `io::IoError`）。庫客戶端可以在導入時重命名以避免衝突。

### Getter/setter 方法

一些數據類型不希望提供對它們的域的直接訪問，但是提供了 "getter" 和 "setter" 方法用於操縱域狀態
（經常提供檢查或其他功能）。

域 `foo: T` 的約定是：

* 方法 `foo(&self) -> &T` 用於獲得該域的當前值。
* 方法 `set_foo(&self, val: T)` 用於設置域。（這裡的 `val` 參數可能取 `&T` 或其他類型，取決於上下文。）

請注意，這個約定是關於通常數據類型的 getters/setters， *不是* 關於構建者對象的。

### 斷言

* 簡單的布爾斷言應該加上 `is_` 或者其他的簡短問題單詞作為前綴，e.g.， `is_empty`。
* 常見的例外： `lt`， `gt`，和其他已經確認的斷言名。

### 導入

一個 crate/模塊的導入應該按順序包括下面各個部分，之間以空行分隔：

* `extern crate` 指令
* 外部 `use` 導入
* 本地 `use` 導入
* `pub use` 導入

例如：

```rust
// Crates.
extern crate getopts;
extern crate mylib;

// 標準庫導入。
use getopts::{optopt, getopts};
use std::os;

// 從一個我們寫的庫導入。
use mylib::webserver;

// 當我們導入這個模塊時會被重新導出。
pub use self::types::Webdata;
```

### 避免 `use *`，除非在測試裡

Glob 導入有幾個缺點：
* 更難知道名字在哪裡綁定。
* 它們前向不兼容，因為新的上流導出可能與現存的名字衝突。

在寫 `test` 子模塊時，為方便導入 `super::*` 是合適的。

### 當模塊限定函數時，傾向於完全導入類型/traits。

例如：

```rust
use option::Option;
use mem;

let i: isize = mem::transmute(Option(0));
```

### 在 crate 級重新導出最重要的類型。

Crates `pub use` 最常見的類型為方便，因此，客戶端不必記住或寫 crate 的模塊結構以使用這些類型。

### 類型和操作在一起定義。

類型定義和使用它們的函數/模塊應該在同一模塊中定義，類型出現在函數/模塊前面。
