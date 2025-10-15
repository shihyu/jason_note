# trait對象 （trait object）

trait對象在**Rust**中是指使用指針封裝了的 trait，比如 `&SomeTrait` 和 `Box<SomeTrait>`。

```rust
trait Foo { fn method(&self) -> String; }

impl Foo for u8 { fn method(&self) -> String { format!("u8: {}", *self) } }
impl Foo for String { fn method(&self) -> String { format!("string: {}", *self) } }

fn do_something(x: &Foo) {
    x.method();
}

fn main() {
    let x = "Hello".to_string();
    do_something(&x);
    let y = 8u8;
    do_something(&y);
}
```

`x: &Foo`其中`x`是一個trait對象，這裡用指針是因為`x`可以是任意實現`Foo`的類型實例，內存大小並不確定，但指針的大小是固定的。

## trait對象的實現

`&SomeTrait` 類型和普通的指針類型`&i32`不同。它不僅包括指向真實對象的指針，還包括一個指向虛函數表的指針。它的內部實現定義在在`std::raw`模塊中：

```rust
pub struct TraitObject {
    pub data: *mut (),
    pub vtable: *mut (),
}
```

其中`data`是一個指向實際類型實例的指針， `vtable`是一個指向實際類型對於該trait的實現的虛函數表：

`Foo`的虛函數表類型：

```rust
struct FooVtable {
    destructor: fn(*mut ()),
    size: usize,
    align: usize,
    method: fn(*const ()) -> String,
}
```

之前的代碼可以解讀為：

```rust
// u8:
// 這個函數只會被指向u8的指針調用
fn call_method_on_u8(x: *const ()) -> String {
    let byte: &u8 = unsafe { &*(x as *const u8) };

    byte.method()
}

static Foo_for_u8_vtable: FooVtable = FooVtable {
    destructor: /* compiler magic */,
    size: 1,
    align: 1,

    method: call_method_on_u8 as fn(*const ()) -> String,
};


// String:
// 這個函數只會被指向String的指針調用
fn call_method_on_String(x: *const ()) -> String {
    let string: &String = unsafe { &*(x as *const String) };

    string.method()
}

static Foo_for_String_vtable: FooVtable = FooVtable {
    destructor: /* compiler magic */,
    size: 24,
    align: 8,

    method: call_method_on_String as fn(*const ()) -> String,
};


let a: String = "foo".to_string();
let x: u8 = 1;

// let b: &Foo = &a;
let b = TraitObject {
    // data存儲實際值的引用
    data: &a,
    // vtable存儲實際類型實現Foo的方法
    vtable: &Foo_for_String_vtable
};

// let y: &Foo = x;
let y = TraitObject {
    data: &x,
    vtable: &Foo_for_u8_vtable
};

// b.method();
(b.vtable.method)(b.data);

// y.method();
(y.vtable.method)(y.data);
```

## 對象安全

並不是所有的trait都能作為trait對象使用的，比如：

```rust
let v = vec![1, 2, 3];
let o = &v as &Clone;
```

會有一個錯誤：

```
error: cannot convert to a trait object because trait `core::clone::Clone` is not object-safe [E0038]
let o = &v as &Clone;
        ^~
note: the trait cannot require that `Self : Sized`
let o = &v as &Clone;
        ^~
```
讓我來分析一下錯誤的原因：

```rust
pub trait Clone: Sized {
    fn clone(&self) -> Self;

    fn clone_from(&mut self, source: &Self) { ... }
}
```

雖然`Clone`本身繼承了`Sized`這個trait，但是它的方法`fn clone(&self) -> Self`和`fn clone_from(&mut self, source: &Self) { ... }`含有`Self`類型，而在使用trait對象方法的時候**Rust**是動態派發的，我們根本不知道這個trait對象的實際類型，它可以是任何一個實現了該trait的類型的值，所以`Self`在這裡的大小不是`Self: Sized`的，這樣的情況在**Rust**中被稱為`object-unsafe`或者`not object-safe`，這樣的trait是不能成為trait對象的。

總結：

如果一個`trait`方法是`object safe`的，它需要滿足：

* 方法有`Self: Sized`約束， 或者
* 同時滿足以下所有條件：
  * 沒有泛型參數
  * 不是靜態函數
  * 除了`self`之外的其它參數和返回值不能使用`Self`類型

如果一個`trait`是`object-safe`的，它需要滿足：

* 所有的方法都是`object-safe`的，並且
* trait 不要求 `Self: Sized` 約束

參考[stackoverflow](http://stackoverflow.com/questions/29985153/trait-object-is-not-object-safe-error)
[object safe rfc](https://github.com/rust-lang/rfcs/blob/master/text/0255-object-safety.md)
