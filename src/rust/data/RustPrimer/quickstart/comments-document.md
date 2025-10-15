# 註釋與文檔

## 註釋
在 Rust 裡面註釋分成兩種，行註釋和塊註釋。它的形式和 C 語言是一樣的。
兩種註釋分別是：
> 1. 行註釋使用 `//` 放在註釋前面。比如:

```
// I love Rust, but I hate Rustc.
```

> 2. 塊註釋分別使用`/*`和`*/`包裹需要註釋的內容。比如：

```
/* W-Cat 是個大胖貓，N-Cat 是個高度近視貓。*/
```

## 文檔
Rust 自帶有文檔功能的註釋，分別是`///`和`//!`。支持 Markdown 格式
1. `///`用來描述的它後面接著的項。
2. `//!`用來描述包含它的項，一般用在模塊文件的頭部。
比如在 main.rs 文件中輸入以下內容：

```
        //! # The first line
        //! The second line
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
```    

### 生成 html 文檔
* `rustdoc main.rs`

或者

* `cargo doc`
