# 註釋

Rust 代碼文件中，通常我們可以看到 3 種註釋。

- 行註釋
- 文檔註釋
- 模塊註釋

## 行註釋

 `//` 後的，直到行尾，都屬於註釋，不會影響程序的行為。

```rust
// 創建一個綁定
let x = 5;

let y = 6; // 創建另一個綁定
```

## 文檔註釋

文檔註釋使用 ```///```，一般用於函數或結構體（字段）的說明，置於要說明的對象上方。文檔註釋內部可使用markdown格式的標記語法，可用於 rustdoc 工具的自動文檔提取。

    /// Adds one to the number given.
    ///
    /// # Examples
    ///
    /// ```
    /// let five = 5;
    ///
    /// assert_eq!(6, add_one(5));
    /// # fn add_one(x: i32) -> i32 {
    /// #     x + 1
    /// # }
    /// ```
    fn add_one(x: i32) -> i32 {
        x + 1
    }


## 模塊註釋

模塊註釋使用 ```//!```，用於說明本模塊的功能。一般置於模塊文件的頭部。

```rust
//! # The Rust Standard Library
//!
//! The Rust Standard Library provides the essential runtime
//! functionality for building portable Rust software.
```

PS: 相對於 `///`, `//!` 用來註釋包含它的項（也就是說，crate，模塊或者函數），而不是位於它之後的項。


## 其它：兼容C語言的註釋

Rust 也支持兼容 C 的塊註釋寫法：`/* */`。但是不推薦使用，請儘量不要使用這種註釋風格（會被鄙視的）。

```rust
/*
    let x = 42;
    println!("{}", x);
*/
```
