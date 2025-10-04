
## 標量變量類型

布爾類型
```rs
fn main() {
    let x = true;
    let y:bool = false;
    println!("x is {}", x);
    println!("y is {}", y);
}
```

整數類型，默認是i32

```rs
fn main() {
    let x = 32;
    let y:u32 = 10000;
    let z = x*y;
    println!("x is {}", x);
    println!("y is {}", y);
    println!("z is {}", z);
}
```

浮點數類型，默認會使用f64

```rs
fn main() {
    let x:f64 = 2.0;
    let y:f64 = 3.5;
    let z = x*y;
    println!("x is {}", x);
    println!("y is {}", y);
    println!("z is {}", z);
}
```
注意：整數和浮點數不能直接相乘，因為它們的數據類型不同。

字符類型
```rs
fn main() {
    let x = 'a';
    println!("x is {}", x);
}
```