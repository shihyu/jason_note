# Deref

`Deref` 是 `deref` 操作符 `*` 的 trait，比如 `*v`。

一般理解，`*v` 操作，是 `&v` 的反向操作，即試圖由資源的引用獲取到資源的拷貝（如果資源類型實現了 `Copy`），或所有權（資源類型沒有實現 `Copy`）。

Rust 中，本操作符行為可以重載。這也是 Rust 操作符的基本特點。本身沒有什麼特別的。

## 強制隱式轉換（coercion）

`Deref` 神奇的地方並不在本身 `解引` 這個意義上，Rust 的設計者在它之上附加了一個特性：`強制隱式轉換`，這才是它神奇之處。

這種隱式轉換的規則為：

一個類型為 `T` 的對象 `foo`，如果 `T: Deref<Target=U>`，那麼，相關 `foo` 的某個智能指針或引用（比如 `&foo`）在應用的時候會自動轉換成 `&U`。

粗看這條規則，貌似有點類似於 `AsRef`，而跟 `解引` 似乎風馬牛不相及。實際裡面有些玄妙之處。

Rust 編譯器會在做 `*v` 操作的時候，自動先把 `v` 做引用歸一化操作，即轉換成內部通用引用的形式 `&v`，整個表達式就變成 `*&v`。這裡面有兩種情況：

1. 把其它類型的指針（比如在庫中定義的，`Box`, `Rc`, `Arc`, `Cow` 等），轉成內部標準形式 `&v`；
2. 把多重 `&` （比如：`&&&&&&&v`），簡化成 `&v`（通過插入足夠數量的 `*` 進行解引）。

所以，它實際上在解引用之前做了一個引用的歸一化操作。

為什麼要轉呢？ 因為編譯器設計的能力是，只能夠對 `&v` 這種引用進行解引用。其它形式的它不認識，所以要做引用歸一化操作。

使用引用進行過渡也是為了能夠防止不必要的拷貝。

下面舉一些例子：

```rust
fn foo(s: &str) {
    // borrow a string for a second
}

// String implements Deref<Target=str>
let owned = "Hello".to_string();

// therefore, this works:
foo(&owned);
```

因為 `String` 實現了 `Deref<Target=str>`。

```rust
use std::rc::Rc;

fn foo(s: &str) {
    // borrow a string for a second
}

// String implements Deref<Target=str>
let owned = "Hello".to_string();
let counted = Rc::new(owned);

// therefore, this works:
foo(&counted);
```
因為 `Rc<T>` 實現了 `Deref<Target=T>`。

```rust
fn foo(s: &[i32]) {
    // borrow a slice for a second
}

// Vec<T> implements Deref<Target=[T]>
let owned = vec![1, 2, 3];

foo(&owned);
```

因為 `Vec<T>` 實現了 `Deref<Target=[T]>`。

```rust
struct Foo;

impl Foo {
    fn foo(&self) { println!("Foo"); }
}

let f = &&Foo;

f.foo();
(&f).foo();
(&&f).foo();
(&&&&&&&&f).foo();
```

上面那幾種函數的調用，效果是一樣的。


`coercion` 的設計，是 Rust 中僅有的類型隱式轉換，設計它的目的，是為了簡化程序的書寫，讓代碼不至於過於繁瑣。把人從無盡的類型細節中解脫出來，讓書寫 Rust 代碼變成一件快樂的事情。
