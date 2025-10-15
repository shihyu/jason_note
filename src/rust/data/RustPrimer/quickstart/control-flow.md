# 控制流(control flow)

## If

If是分支 (branch) 的一種特殊形式，也可以使用`else`和`else if`。
與C語言不同的是，邏輯條件不需要用小括號括起來，但是條件後面必須跟一個代碼塊。
Rust中的`if`是一個表達式 (expression)，可以賦給一個變量：

```rust
let x = 5;

let y = if x == 5 { 10 } else { 15 };
```

Rust是基於表達式的編程語言，有且僅有兩種語句 (statement)：

1. **聲明語句** (declaration statement)，比如進行變量綁定的`let`語句。
2. **表達式語句** (expression statement)，它通過在末尾加上分號`;`來將表達式變成語句，
丟棄該表達式的值，一律返回unit`()`。

表達式如果返回，總是返回一個值，但是語句不返回值或者返回`()`，所以以下代碼會報錯：

```rust
let y = (let x = 5);

let z: i32 = if x == 5 { 10; } else { 15; };
```

值得注意的是，在Rust中賦值 (如`x = 5`) 也是一個表達式，返回unit的值`()`。

## For

Rust中的`for`循環與C語言的風格非常不同，抽象結構如下：

```rust
for var in expression {
    code
}
```

其中`expression`是一個迭代器 (iterator)，具體的例子為`0..10` (不包含最後一個值)，
或者`[0, 1, 2].iter()`。

## While

Rust中的`while`循環與C語言中的類似。對於無限循環，Rust有一個專用的關鍵字`loop`。
如果需要提前退出循環，可以使用關鍵字`break`或者`continue`，
還允許在循環的開頭設定標籤 (同樣適用於`for`循環)：

```rust
'outer: loop {
   println!("Entered the outer loop");

   'inner: loop {
       println!("Entered the inner loop");
       break 'outer;
   }

   println!("This point will never be reached");
}

println!("Exited the outer loop");
```

## Match

Rust中的`match`表達式非常強大，首先看一個例子：

```rust
let day = 5;

match day {
  0 | 6 => println!("weekend"),
  1 ... 5 => println!("weekday"),
  _ => println!("invalid"),
}
```

其中`|`用於匹配多個值，`...`匹配一個範圍 (包含最後一個值)，並且`_`在這裡是必須的，
因為`match`強制進行窮盡性檢查 (exhaustiveness checking)，必須覆蓋所有的可能值。
如果需要得到`|`或者`...`匹配到的值，可以使用`@`綁定變量：

```rust
let x = 1;

match x {
    e @ 1 ... 5 => println!("got a range element {}", e),
    _ => println!("anything"),
}
```

使用`ref`關鍵字來得到一個引用：

```rust
let x = 5;
let mut y = 5;

match x {
    // the `r` inside the match has the type `&i32`
    ref r => println!("Got a reference to {}", r),
}

match y {
    // the `mr` inside the match has the type `&i32` and is mutable
    ref mut mr => println!("Got a mutable reference to {}", mr),
}
```

再看一個使用`match`表達式來解構元組的例子：

```rust
let pair = (0, -2);

match pair {
    (0, y) => println!("x is `0` and `y` is `{:?}`", y),
    (x, 0) => println!("`x` is `{:?}` and y is `0`", x),
    _ => println!("It doesn't matter what they are"),
}
```

`match`的這種解構同樣適用於結構體或者枚舉。如果有必要，還可以使用`..`來忽略域或者數據：

```rust
struct Point {
    x: i32,
    y: i32,
}

let origin = Point { x: 0, y: 0 };

match origin {
    Point { x, .. } => println!("x is {}", x),
}

enum OptionalInt {
    Value(i32),
    Missing,
}

let x = OptionalInt::Value(5);

match x {
    // 這裡是 match 的 if guard 表達式，我們將在以後的章節進行詳細介紹
    OptionalInt::Value(i) if i > 5 => println!("Got an int bigger than five!"),
    OptionalInt::Value(..) => println!("Got an int!"),
    OptionalInt::Missing => println!("No such luck."),
}
```

此外，Rust還引入了`if let`和`while let`進行模式匹配：

```rust
let number = Some(7);
let mut optional = Some(0);

// If `let` destructures `number` into `Some(i)`, evaluate the block.
if let Some(i) = number {
    println!("Matched {:?}!", i);
} else {
    println!("Didn't match a number!");
}

// While `let` destructures `optional` into `Some(i)`, evaluate the block.
while let Some(i) = optional {
    if i > 9 {
        println!("Greater than 9, quit!");
        optional = None;
    } else {
        println!("`i` is `{:?}`. Try again.", i);
        optional = Some(i + 1);
    }
}
```

