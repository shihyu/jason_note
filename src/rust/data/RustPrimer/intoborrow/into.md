# Into/From 及其在 String 和 &str 互轉上的應用

`std::convert` 下面，有兩個 Trait，`Into/From`，它們是一對孿生姐妹。它們的作用是配合泛型，進行一些設計上的歸一化處理。

它們的基本形式為： `From<T>` 和 `Into<T>`。

## From<T>

對於類型為 `U` 的對象 `foo`，如果它實現了 `From<T>`，那麼，可以通過 `let foo = U::from(bar)` 來生成自己。這裡，`bar` 是類型為 `T` 的對象。

下面舉一例，因為 `String` 實現了 `From<&str>`，所以 `String` 可以從 `&str` 生成。

```rust
let string = "hello".to_string();
let other_string = String::from("hello");

assert_eq!(string, other_string);
```

## Into<T>

對於一個類型為 `U: Into<T>` 的對象 `foo`，`Into` 提供了一個函數：`.into(self) -> T`，調用 `foo.into()` 會消耗自己（轉移資源所有權），生成類型為 `T` 的另一個新對象 `bar`。

這句話，說起來有點抽象。下面拿一個具體的實例來輔助理解。

```rust
fn is_hello<T: Into<Vec<u8>>>(s: T) {
   let bytes = b"hello".to_vec();
   assert_eq!(bytes, s.into());
}

let s = "hello".to_string();
is_hello(s);
```

因為 `String` 類型實現了 `Into<Vec<u8>>`。

下面拿一個實際生產中字符串作為函數參數的例子來說明。

在我們設計庫的 `API` 的時候，經常會遇到一個惱人的問題，函數參數如果定為 `String`，則外部傳入實參的時候，對字符串字面量，必須要做 `.to_string()` 或 `.to_owned()` 轉換，參數一多，就是一件又乏味又醜的事情。（而反過來設計的話，對初學者來說，又會遇到一些生命週期的問題，比較麻煩，這個後面論述）

那存不存在一種方法，能夠使傳參又能夠接受 `String` 類型，又能夠接受 `&str` 類型呢？答案就是**泛型**。而僅是泛型的話，太寬泛。因此，標準庫中，提供了 `Into<T>` 來為其做約束，以便方便而高效地達到我們的目的。

比如，我們有如下結構體：

```rust
struct Person {
    name: String,
}

impl Person {
    fn new (name: String) -> Person {
        Person { name: name }
    }
}
```

我們在調用的時候，是這樣的：

```rust
let name = "Herman".to_string();
let person = Person::new(name);
```

如果直接寫成：

```rust
let person = Person::new("Herman");
```

就會報類型不匹配的錯誤。

好了，下面 `Into` 出場。我們可以定義結構體為

```rust
struct Person {
    name: String,
}

impl Person {
    fn new<S: Into<String>>(name: S) -> Person {
        Person { name: name.into() }
    }
}
```

然後，調用的時候，下面兩種寫法都是可以的：

```rust
fn main() {
    let person = Person::new("Herman");
    let person = Person::new("Herman".to_string());
}
```

我們來仔細分析一下這一塊的寫法

```rust
impl Person {
    fn new<S: Into<String>>(name: S) -> Person {
        Person { name: name.into() }
    }
}
```

參數類型為 `S`， 是一個泛型參數，表示可以接受不同的類型。`S: Into<String>` 表示 `S` 類型必須實現了 `Into<String>`（約束）。而 `&str` 類型，符合這個要求。因此 `&str` 類型可以直接傳進來。

而 `String` 本身也是實現了 `Into<String>` 的。當然也可以直接傳進來。

然後，下面 `name: name.into()` 這裡也挺神秘的。它的作用是將 `name` 轉換成 `String` 類型的另一個對象。當 name 是 `&str` 時，它會轉換成 `String` 對象，會做一次字符串的拷貝（內存的申請、複製）。而當 name 本身是 `String` 類型時，`name.into()` 不會做任何轉換，代價為零（有沒有恍然大悟）。

根據參考資料，上述內容通過下面三式獲得：

```rust
impl<'a> From<&'a str> for String {}
impl<T> From<T> for T {}
impl<T, U> Into<U> for T where U: From<T> {}
```

更多內容，請參考：

- [http://doc.rust-lang.org/std/convert/trait.Into.html](http://doc.rust-lang.org/std/convert/trait.Into.html)
- [http://doc.rust-lang.org/std/convert/trait.From.html](http://doc.rust-lang.org/std/convert/trait.From.html)
- [http://hermanradtke.com/2015/05/06/creating-a-rust-function-that-accepts-string-or-str.html](http://hermanradtke.com/2015/05/06/creating-a-rust-function-that-accepts-string-or-str.html)
