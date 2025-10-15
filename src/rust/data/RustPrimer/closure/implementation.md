# 閉包的實現

Rust 的閉包實現與其它語言有些許不同。它們實際上是trait的語法糖。在這以前你會希望閱讀[trait章節](https://doc.rust-lang.org/stable/book/traits.html)，和[trait對象](https://doc.rust-lang.org/stable/book/trait-objects.html)。

都理解嗎？很好。

理解閉包底層是如何工作的關鍵有點奇怪：使用`()`調用函數，像`foo()`，是一個可重載的運算符。到此，其它的一切都會明瞭。在Rust中，我們使用trait系統來重載運算符。調用函數也不例外。我們有三個trait來分別重載：

```rust
# mod foo {
pub trait Fn<Args> : FnMut<Args> {
    extern "rust-call" fn call(&self, args: Args) -> Self::Output;
}

pub trait FnMut<Args> : FnOnce<Args> {
    extern "rust-call" fn call_mut(&mut self, args: Args) -> Self::Output;
}

pub trait FnOnce<Args> {
    type Output;

    extern "rust-call" fn call_once(self, args: Args) -> Self::Output;
}
# }
```

你會注意到這些 trait 之間的些許區別，不過一個大的區別是`self`：`Fn`獲取`&self`，`FnMut`獲取`&mut self`，而`FnOnce`獲取`self`。這包含了所有3種通過通常函數調用語法的`self`。不過我們將它們分在 3 個 trait 裡，而不是單獨的 1 個。這給了我們大量的對於我們可以使用哪種閉包的控制。

閉包的`|| {}`語法是上面 3 個 trait 的語法糖。Rust 將會為了環境創建一個結構體，`impl`合適的 trait，並使用它。

> ### 這部分引用自[The Rust Programming Language中文版](https://github.com/KaiserY/rust-book-chinese/blob/master/content/Closures%20%E9%97%AD%E5%8C%85.md)
