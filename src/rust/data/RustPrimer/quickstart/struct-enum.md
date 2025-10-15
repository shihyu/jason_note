# 結構體與枚舉

## 結構體

結構體 (struct) 是一種記錄類型，所包含的每個域 (field) 都有一個名稱。
每個結構體也都有一個名稱，通常以大寫字母開頭，使用駝峰命名法。
元組結構體 (tuple struct) 是由元組和結構體混合構成，元組結構體有名稱，
但是它的域沒有。當元組結構體只有一個域時，稱為新類型 (newtype)。
沒有任何域的結構體，稱為類單元結構體 (unit-like struct)。
結構體中的值默認是不可變的，需要給結構體加上`mut`使其可變。

```rust
// structs
struct Point {
  x: i32,
  y: i32,
}
let point = Point { x: 0, y: 0 };

// tuple structs
struct Color(u8, u8, u8);
let android_green = Color(0xa4, 0xc6, 0x39);
let Color(red, green, blue) = android_green;

// A tuple struct’s constructors can be used as functions.
struct Digit(i32);
let v = vec![0, 1, 2];
let d: Vec<Digit> = v.into_iter().map(Digit).collect();

// newtype: a tuple struct with only one element
struct Inches(i32);
let length = Inches(10);
let Inches(integer_length) = length;

// unit-like structs
struct EmptyStruct;
let empty = EmptyStruct;
```

一個包含`..`的`struct`可以用來從其它結構體拷貝一些值或者在解構時忽略一些域：

```rust
#[derive(Default)]
struct Point3d {
    x: i32,
    y: i32,
    z: i32,
}

let origin = Point3d::default();
let point = Point3d { y: 1, ..origin };
let Point3d { x: x0, y: y0, .. } = point;
```

需要注意，Rust在語言級別不支持域可變性 (field mutability)，所以不能這麼寫：

```rust
struct Point {
    mut x: i32,
    y: i32,
}
```

這是因為可變性是綁定的一個屬性，而不是結構體自身的。可以使用`Cell<T>`來模擬：

```rust
use std::cell::Cell;

struct Point {
    x: i32,
    y: Cell<i32>,
}

let point = Point { x: 5, y: Cell::new(6) };

point.y.set(7);
```

此外，結構體的域對其所在模塊 (mod) 之外默認是私有的，可以使用`pub`關鍵字將其設置成公開。

```rust
mod graph {
    #[derive(Default)]
    pub struct Point {
        pub x: i32,
        y: i32,
    }

    pub fn inside_fn() {
        let p = Point {x:1, y:2};
        println!("{}, {}", p.x, p.y);
    }
}

fn outside_fn() {
    let p = graph::Point::default();
    println!("{}", p.x);
    // println!("{}", p.y);
    // field `y` of struct `graph::Point` is private
}
```

## 枚舉
Rust有一個集合類型，稱為枚舉 (enum)，代表一系列子數據類型的集合。
其中子數據結構可以為空-如果全部子數據結構都是空的，就等價於C語言中的enum。
我們需要使用`::`來獲得每個元素的名稱。

```rust
// enums
enum Message {
    Quit,
    ChangeColor(i32, i32, i32),
    Move { x: i32, y: i32 },
    Write(String),
}

let x: Message = Message::Move { x: 3, y: 4 };
```

與結構體一樣，枚舉中的元素默認不能使用關係運算符進行比較 (如`==`, `!=`, `>=`)，
也不支持像`+`和`*`這樣的雙目運算符，需要自己實現，或者使用`match`進行匹配。

枚舉默認也是私有的，如果使用`pub`使其變為公有，則它的元素也都是默認公有的。
這一點是與結構體不同的：即使結構體是公有的，它的域仍然是默認私有的。這裡的共有/私有仍然
是針對其定義所在的模塊之外。此外，枚舉和結構體也可以是遞歸的 (recursive)。
