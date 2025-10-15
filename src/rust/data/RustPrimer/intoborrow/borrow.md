# Borrow, BorrowMut, ToOwned

## Borrow<T>

`use std::borrow::Borrow;`

`Borrow` 提供了一個方法 `.borrow()`。

對於一個類型為 `T` 的值 `foo`，如果 `T` 實現了 `Borrow<U>`，那麼，`foo` 可執行 `.borrow()` 操作，即 `foo.borrow()`。操作的結果，我們得到了一個類型為 `&U` 的新引用。

`Borrow` 可以認為是 `AsRef` 的嚴格版本，它對普適引用操作的前後類型之間附加了一些其它限制。

`Borrow` 的前後類型之間要求必須有內部等價性。不具有這個等價性的兩個類型之間，不能實現 `Borrow`。

`AsRef` 更通用，更普遍，覆蓋類型更多，是 `Borrow` 的超集。

舉例：

```rust
use std::borrow::Borrow;

fn check<T: Borrow<str>>(s: T) {
    assert_eq!("Hello", s.borrow());
}

let s = "Hello".to_string();

check(s);

let s = "Hello";

check(s);
```

## BorrowMut<T>

`use std::borrow::BorrowMut;`

`BorrowMut<T>` 提供了一個方法 `.borrow_mut()`。它是 `Borrow<T>` 的可變（mutable）引用版本。

對於一個類型為 `T` 的值 `foo`，如果 `T` 實現了 `BorrowMut<U>`，那麼，`foo` 可執行 `.borrow_mut()` 操作，即 `foo.borrow_mut()`。操作的結果我們得到類型為 `&mut U` 的一個可變（mutable）引用。

注：在轉換的過程中，`foo` 會被可變（mutable）借用。

## ToOwned

`use std::borrow::ToOwned;`

`ToOwned` 為 `Clone` 的普適版本。它提供了 `.to_owned()` 方法，用於類型轉換。

有些實現了 `Clone` 的類型 `T` 可以從引用狀態實例 `&T` 通過 `.clone()` 方法，生成具有所有權的 `T` 的實例。但是它只能由 `&T` 生成 `T`。而對於其它形式的引用，`Clone` 就無能為力了。

而 `ToOwned` trait 能夠從任意引用類型實例，生成具有所有權的類型實例。

## 參考

- [http://doc.rust-lang.org/std/borrow/trait.Borrow.html](http://doc.rust-lang.org/std/borrow/trait.Borrow.html)
