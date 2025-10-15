# 運算符重載

Rust可以讓我們對某些運算符進行重載，這其中大部分的重載都是對`std::ops`下的trait進行重載而實現的。

## 重載加法

我們現在來實現一個只支持加法的閹割版[複數](https://zh.wikipedia.org/wiki/%E5%A4%8D%E6%95%B0_%28%E6%95%B0%E5%AD%A6%29)：

```rust
use std::ops::Add;

#[derive(Debug)]
struct Complex {
    a: f64,
    b: f64,
}

impl Add for Complex {
    type Output = Complex;
    fn add(self, other: Complex) -> Complex {
        Complex {a: self.a+other.a, b: self.b+other.b}
    }
}

fn main() {
    let cp1 = Complex{a: 1f64, b: 2.0};
    let cp2 = Complex{a: 5.0, b:8.1};
    let cp3 = cp1 + cp2;
    print!("{:?}", cp3);
}
```

輸出:

```
Complex { a: 6, b: 10.1}
```

這裡我們實現了`std::ops::Add`這個trait。這時候有同學一拍腦門，原來如此，沒錯……其實Rust的大部分運算符都是`std::ops`下的trait的語法糖！

我們來看看`std::ops::Add`的具體結構

```rust
impl Add<i32> for Point {
    type Output = f64;

    fn add(self, rhs: i32) -> f64 {
        // add an i32 to a Point and get an f64
    }
}
```

## 神奇的Output以及動態分發
有的同學會問了，這個`Output`是腫麼回事？答，類型轉換喲親！
舉個不太恰當的栗子，我們在現實中會出現`0.5+0.5=1`這樣的算式，用Rust的語言來描述就是： 兩個`f32`相加得到了一個`i8`。顯而易見，Output就是為這種情況設計的。

還是看代碼：

```rust
use std::ops::Add;

#[derive(Debug)]
struct Complex {
    a: f64,
    b: f64,
}

impl Add for Complex {
    type Output = Complex;
    fn add(self, other: Complex) -> Complex {
        Complex {a: self.a+other.a, b: self.b+other.b}
    }
}

impl Add<i32> for Complex {
    type Output = f64;
    fn add(self, other: i32) -> f64 {
        self.a + self.b + (other as f64)
    }
}

fn main() {
    let cp1 = Complex{a: 1f64, b: 2.0};
    let cp2 = Complex{a: 5.0, b:8.1};
    let cp3 = Complex{a: 9.0, b:20.0};
    let complex_add_result = cp1 + cp2;
    print!("{:?}\n", complex_add_result);
    print!("{:?}", cp3 + 10i32);
}
```

輸出結果：

```
Complex { a: 6, b: 10.1 }
39
```

## 對範型的限制

Rust的運算符是基於trait系統的，同樣的，運算符可以被當成一種對範型的限制，我們可以這麼要求`範型T必須實現了trait Mul<Output=T>`。
於是，我們得到了如下的一份代碼：

```rust
use std::ops::Mul;

trait HasArea<T> {
    fn area(&self) -> T;
}

struct Square<T> {
    x: T,
    y: T,
    side: T,
}

impl<T> HasArea<T> for Square<T>
        where T: Mul<Output=T> + Copy {
    fn area(&self) -> T {
        self.side * self.side
    }
}

fn main() {
    let s = Square {
        x: 0.0f64,
        y: 0.0f64,
        side: 12.0f64,
    };

    println!("Area of s: {}", s.area());
}
```

對於trait `HasArea<T>`和 struct `Square<T>`，我們通過`where T: Mul<Output=T> + Copy` 限制了`T`必須實現乘法。同時Copy則限制了Rust不再將self.side給move到返回值裡去。

寫法簡單，輕鬆愉快。
