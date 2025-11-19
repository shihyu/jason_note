# 10.1 trait關鍵字

## trait與具體類型

使用**trait**定義一個特徵：

```rust
trait HasArea {
    fn area(&self) -> f64;
}
```

**trait**裡面的函數可以沒有函數體，實現代碼交給具體實現它的類型去補充：

```rust
struct Circle {
    x: f64,
    y: f64,
    radius: f64,
}

impl HasArea for Circle {
    fn area(&self) -> f64 {
        std::f64::consts::PI * (self.radius * self.radius)
    }
}

fn main() {
    let c = Circle {
        x: 0.0f64,
        y: 0.0f64,
        radius: 1.0f64,
    };
    println!("circle c has an area of {}", c.area());
}
```

**注**: **&self**表示的是**area**這個函數會將調用者的借代引用作為參數

這個程序會輸出：

```
circle c has an area of 3.141592653589793
```

## trait與泛型

> 我們瞭解了Rust中trait的定義和使用，接下來我們介紹一下它的使用場景，從中我們可以窺探出接口這特性帶來的驚喜

我們知道泛型可以指任意類型，但有時這不是我們想要的，需要給它一些約束。

#### 泛型的trait約束

```rust
use std::fmt::Debug;
fn foo<T: Debug>(s: T) {
    println!("{:?}", s);
}
```

`Debug`是**Rust**內置的一個trait，為"{:?}"實現打印內容，函數`foo`接受一個泛型作為參數，並且約定其需要實現`Debug`

#### 多trait約束

可以使用多個trait對泛型進行約束：

```rust
use std::fmt::Debug;
fn foo<T: Debug + Clone>(s: T) {
    s.clone();
    println!("{:?}", s);
}
```

`<T: Debug + Clone>`中`Debug`和`Clone`使用`+`連接，標示泛型`T`需要同時實現這兩個trait。

#### where關鍵字

約束的trait增加後，代碼看起來就變得詭異了，這時候需要使用`where`從句：

```rust
use std::fmt::Debug;
fn foo<T: Clone, K: Clone + Debug>(x: T, y: K) {
    x.clone();
    y.clone();
    println!("{:?}", y);
}

// where 從句
fn foo<T, K>(x: T, y: K) where T: Clone, K: Clone + Debug {
    x.clone();
    y.clone();
    println!("{:?}", y);
}

// 或者
fn foo<T, K>(x: T, y: K)
    where T: Clone,
          K: Clone + Debug {
    x.clone();
    y.clone();
    println!("{:?}", y);
}
```

## trait與內置類型

內置類型如：`i32`, `i64`等也可以添加trait實現，為其定製一些功能：

```rust
trait HasArea {
    fn area(&self) -> f64;
}

impl HasArea for i32 {
    fn area(&self) -> f64 {
        *self as f64
    }
}

5.area();
```

這樣的做法是有限制的。Rust 有一個“孤兒規則”：當你為某類型實現某 trait 的時候，必須要求類型或者 trait 至少有一個是在當前 crate 中定義的。你不能為第三方的類型實現第三方的 trait 。

在調用 trait 中定義的方法的時候，一定要記得讓這個 trait 可被訪問。

```rust
let mut f = std::fs::File::open("foo.txt").ok().expect("Couldn’t open foo.txt");
let buf = b"whatever"; //  buf: &[u8; 8]
let result = f.write(buf);
# result.unwrap();
```

這裡是錯誤：

```
error: type `std::fs::File` does not implement any method in scope named `write`
let result = f.write(buf);
               ^~~~~~~~~~
```

我們需要先use這個Write trait：

```rust
use std::io::Write;

let mut f = std::fs::File::open("foo.txt").expect("Couldn’t open foo.txt");
let buf = b"whatever";
let result = f.write(buf);
# result.unwrap(); // ignore the error
```

這樣就能無錯誤地編譯了。


## trait的默認方法


```rust
trait Foo {
    fn is_valid(&self) -> bool;

    fn is_invalid(&self) -> bool { !self.is_valid() }
}
```

`is_invalid`是默認方法，`Foo`的實現者並不要求實現它，如果選擇實現它，會覆蓋掉它的默認行為。

## trait的繼承

```rust
trait Foo {
    fn foo(&self);
}

trait FooBar : Foo {
    fn foobar(&self);
}
```

這樣`FooBar`的實現者也要同時實現`Foo`：

```rust
struct Baz;

impl Foo for Baz {
    fn foo(&self) { println!("foo"); }
}

impl FooBar for Baz {
    fn foobar(&self) { println!("foobar"); }
}
```

## derive屬性

**Rust**提供了一個屬性`derive`來自動實現一些trait，這樣可以避免重複繁瑣地實現他們，能被`derive`使用的trait包括：`Clone`, `Copy`, `Debug`, `Default`, `Eq`, `Hash`, `Ord`, `PartialEq`, `PartialOrd`

```rust
#[derive(Debug)]
struct Foo;

fn main() {
    println!("{:?}", Foo);
}
```

## impl Trait
在版本1.26 開始，Rust提供了`impl Trait`的寫法，作為和Scala 對等的`既存型別(Existential Type)`的寫法。

在下面這個寫法中，`fn foo()`將返回一個實作了`Trait`的trait。

```rust
//before
fn foo() -> Box<Trait> {
    // ...
}

//after
fn foo() -> impl Trait {
    // ...
}
```

相較於1.25 版本以前的寫法，新的寫法會在很多場閤中更有利於開發和執行效率。

#### impl Trait 的普遍用例

```rust
trait Trait {
    fn method(&self);
}

impl Trait for i32 {
    // implementation goes here
}

impl Trait for f32 {
    // implementation goes here
}
```

利用Box 會意味：即便回傳的內容是固定的，但也會使用到動態內存分配。利用`impl Trait` 的寫法可以避免便用Box。

```rust
//before
fn foo() -> Box<Trait> {
    Box::new(5) as Box<Trait>
}

//after
fn foo() -> impl Trait {
    5
}
```

#### 其他受益的用例

閉包:
```rust
// before
fn foo() -> Box<Fn(i32) -> i32> {
    Box::new(|x| x + 1)
}

// after
fn foo() -> impl Fn(i32) -> i32 {
    |x| x + 1
}
```

傳參：
```rust
// before
fn foo<T: Trait>(x: T) {

// after
fn foo(x: impl Trait) {
```
