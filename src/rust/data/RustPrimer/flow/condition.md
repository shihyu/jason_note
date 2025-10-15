# 條件分支

- if
- if let
- match

## if 表達式

Rust 中的 if 表達式基本就是如下幾種形式：

```rust
// 形式 1
if expr1 {

}

// 形式 2
if expr1 {

}
else {

}

// 形式 3
if expr1 {

}
else if expr2 {
    // else if 可多重
}
else {

}

```

相對於 C 系語言，Rust 的 if 表達式的顯著特點是：

1. 判斷條件不用小括號括起來；
2. 它是表達式，而不是語句。

鑑於上述第二點，因為是表達式，所以我們可以寫出如下代碼：

```rust
let x = 5;

let y = if x == 5 {
    10
} else {
    15
}; // y: i32
```

或者壓縮成一行：

```rust
let x = 5;

let y = if x == 5 { 10 } else { 15 }; // y: i32
```

## if let

我們在代碼中常常會看到 `if let` 成對出現，這實際上是一個 match 的簡化用法。直接舉例來說明：

```rust
let x = Some(5);

if let Some(y) = x {
    println!("{}", y);      // 這裡輸出為：5
}

let z = if let Some(y) = x {
    y
}
else {
    0
};
// z 值為 5

```

上面代碼等價於

```rust
let x = Some(5);
match x {
    Some(y) => println!("{}", y),
    None => ()
}

let z = match x {
    Some(y) => y,
    None => 0
};
```

設計這個特性的目的是，在條件判斷的時候，直接做一次模式匹配，方便代碼書寫，使代碼更緊湊。

## match

Rust 中沒有類似於 C 的 `switch` 關鍵字，但它有用於模式匹配的 `match`，能實現同樣的功能，並且強大太多。

match 的使用非常簡單，舉例如下：

```rust
let x = 5;

match x {
    1 => {
        println!("one")
    },
    2 => println!("two"),
    3 => println!("three"),
    4 => println!("four"),
    5 => println!("five"),
    _ => println!("something else"),
}
```
注意，match 也是一個表達式。match 後面會專門論述，請參見 **模式匹配** 這一章。
