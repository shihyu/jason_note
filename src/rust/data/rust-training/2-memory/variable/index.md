
## 變量的可變性
變量默認是 immutable 的。 例如下面的變量 x 是無法被修改的
```rs
fn main() {
    let x = 5;
    println!("x is {}", x);
}
```

如果變量是 mutable 的，那麼就可以被修改。 

```rs
fn main() {
    let mut x = 5;
    x = 6;
    println!("x is {}", x);
}
```

## 隱藏
重複使用 let 關鍵字可以創建一個新的變量。如果新變量和之前的變量名相同，則可以達到隱藏前一個變量的效果。 
例如下面的代碼中，變量 x 隱藏了前一個變量 x。

```rs
fn main() {
    let x = 5;
    let x = 6;
    println!("x is {}", x);
}
```

隱藏變量也可以是不同的變量類型。

```rs
fn main() {
    let x = 5;
    let x = "hello";
    println!("x is {}", x);
}
```

