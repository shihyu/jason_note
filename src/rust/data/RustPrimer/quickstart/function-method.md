# 函數與方法

## 函數

要聲明一個函數，需要使用關鍵字`fn`，後面跟上函數名，比如

```rust
fn add_one(x: i32) -> i32 {
    x + 1
}
```

其中函數參數的類型不能省略，可以有多個參數，但是最多隻能返回一個值，
提前返回使用`return`關鍵字。Rust編譯器會對未使用的函數提出警告，
可以使用屬性`#[allow(dead_code)]`禁用無效代碼檢查。

Rust有一個特殊特性適用於發散函數 (diverging function)，它不返回：

```rust
fn diverges() -> ! {
    panic!("This function never returns!");
}
```

其中`panic!`是一個宏，使當前執行線程崩潰並打印給定信息。返回類型`!`可用作任何類型：

```rust
let x: i32 = diverges();
let y: String = diverges();
```

## 匿名函數

Rust使用閉包 (closure) 來創建匿名函數：

```rust
let num = 5;
let plus_num = |x: i32| x + num;
```

其中閉包`plus_num`借用了它作用域中的`let`綁定`num`。如果要讓閉包獲得所有權，
可以使用`move`關鍵字：

```rust
let mut num = 5;

{
    let mut add_num = move |x: i32| num += x;   // 閉包通過move獲取了num的所有權

    add_num(5);
}

// 下面的num在被move之後還能繼續使用是因為其實現了Copy特性
// 具體可見所有權(Owership)章節
assert_eq!(5, num);
```

## 高階函數

Rust 還支持高階函數 (high order function)，允許把閉包作為參數來生成新的函數：

```rust
fn add_one(x: i32) -> i32 { x + 1 }

fn apply<F>(f: F, y: i32) -> i32
    where F: Fn(i32) -> i32
{
    f(y) * y
}

fn factory(x: i32) -> Box<Fn(i32) -> i32> {
    Box::new(move |y| x + y)
}

fn main() {
    let transform: fn(i32) -> i32 = add_one;
    let f0 = add_one(2i32) * 2;
    let f1 = apply(add_one, 2);
    let f2 = apply(transform, 2);
    println!("{}, {}, {}", f0, f1, f2);

    let closure = |x: i32| x + 1;
    let c0 = closure(2i32) * 2;
    let c1 = apply(closure, 2);
    let c2 = apply(|x| x + 1, 2);
    println!("{}, {}, {}", c0, c1, c2);

    let box_fn = factory(1i32);
    let b0 = box_fn(2i32) * 2;
    let b1 = (*box_fn)(2i32) * 2;
    let b2 = (&box_fn)(2i32) * 2;
    println!("{}, {}, {}", b0, b1, b2);

    let add_num = &(*box_fn);
    let translate: &Fn(i32) -> i32 = add_num;
    let z0 = add_num(2i32) * 2;
    let z1 = apply(add_num, 2);
    let z2 = apply(translate, 2);
    println!("{}, {}, {}", z0, z1, z2);
}
```

## 方法

Rust通過`impl`關鍵字在`struct`、`enum`或者`trait`對象上實現方法調用語法 (method call syntax)。
關聯函數 (associated function) 的第一個參數通常為`self`參數，有3種變體：
* `self`，允許實現者移動和修改對象，對應的閉包特性為`FnOnce`。
* `&self`，既不允許實現者移動對象也不允許修改，對應的閉包特性為`Fn`。
* `&mut self`，允許實現者修改對象但不允許移動，對應的閉包特性為`FnMut`。

不含`self`參數的關聯函數稱為靜態方法 (static method)。

```rust
struct Circle {
    x: f64,
    y: f64,
    radius: f64,
}

impl Circle {
    fn new(x: f64, y: f64, radius: f64) -> Circle {
        Circle {
            x: x,
            y: y,
            radius: radius,
        }
    }

    fn area(&self) -> f64 {
        std::f64::consts::PI * (self.radius * self.radius)
    }
}

fn main() {
    let c = Circle { x: 0.0, y: 0.0, radius: 2.0 };
    println!("{}", c.area());

    // use associated function and method chaining
    println!("{}", Circle::new(0.0, 0.0, 2.0).area());
}
```
