# 閉包的語法
## 基本形式
閉包看起來像這樣：

```rust
let plus_one = |x: i32| x + 1;

assert_eq!(2, plus_one(1));
```

我們創建了一個綁定，`plus_one`，並把它賦予一個閉包。閉包的參數位於管道（`|`）之中，而閉包體是一個表達式，在這個例子中，`x + 1`。記住`{}`是一個表達式，所以我們也可以擁有包含多行的閉包：

```rust
let plus_two = |x| {
    let mut result: i32 = x;

    result += 1;
    result += 1;

    result
};

assert_eq!(4, plus_two(2));
```

你會注意到閉包的一些方面與用`fn`定義的常規函數有點不同。第一個是我們並不需要標明閉包接收和返回參數的類型。我們可以：

```rust
let plus_one = |x: i32| -> i32 { x + 1 };

assert_eq!(2, plus_one(1));
```

不過我們並不需要這麼寫。為什麼呢？基本上，這是出於“人體工程學”的原因。因為為命名函數指定全部類型有助於像文檔和類型推斷，而閉包的類型則很少有文檔因為它們是匿名的，並且並不會產生像推斷一個命名函數的類型這樣的“遠距離錯誤”。

第二個的語法大同小異。我會增加空格來使它們看起來更像一點：

```rust
fn  plus_one_v1   (x: i32) -> i32 { x + 1 }
let plus_one_v2 = |x: i32| -> i32 { x + 1 };
let plus_one_v3 = |x: i32|          x + 1  ;
```

## 捕獲變量
之所以把它稱為“閉包”是因為它們“包含在環境中”（close over their environment）。這看起來像：

```rust
let num = 5;
let plus_num = |x: i32| x + num;

assert_eq!(10, plus_num(5));
```

這個閉包，`plus_num`，引用了它作用域中的`let`綁定：`num`。更明確的說，它借用了綁定。如果我們做一些會與這個綁定衝突的事，我們會得到一個錯誤。比如這個：

```rust
let mut num = 5;
let plus_num = |x: i32| x + num;

let y = &mut num;
```

錯誤是：

```text
error: cannot borrow `num` as mutable because it is also borrowed as immutable
    let y = &mut num;
                 ^~~
note: previous borrow of `num` occurs here due to use in closure; the immutable
  borrow prevents subsequent moves or mutable borrows of `num` until the borrow
  ends
    let plus_num = |x| x + num;
                   ^~~~~~~~~~~
note: previous borrow ends here
fn main() {
    let mut num = 5;
    let plus_num = |x| x + num;

    let y = &mut num;
}
^
```

一個囉嗦但有用的錯誤信息！如它所說，我們不能取得一個`num`的可變借用因為閉包已經借用了它。如果我們讓閉包離開作用域，我們可以：

```rust
let mut num = 5;
{
    let plus_num = |x: i32| x + num;

} // plus_num goes out of scope, borrow of num ends

let y = &mut num;
```

如果你的閉包需要它，Rust會取得所有權並移動環境：

```rust
let nums = vec![1, 2, 3];

let takes_nums = || nums;

println!("{:?}", nums);
```

這會給我們：

```text
note: `nums` moved into closure environment here because it has type
  `[closure(()) -> collections::vec::Vec<i32>]`, which is non-copyable
let takes_nums = || nums;
                    ^~~~~~~
```

`Vec<T>`擁有它內容的所有權，而且由於這個原因，當我們在閉包中引用它時，我們必須取得`nums`的所有權。這與我們傳遞`nums`給一個取得它所有權的函數一樣。

## move閉包
我們可以使用`move`關鍵字強制使我們的閉包取得它環境的所有權：

```rust
let num = 5;

let owns_num = move |x: i32| x + num;
```

現在，即便關鍵字是`move`，變量遵循正常的移動語義。在這個例子中，`5`實現了`Copy`，所以`owns_num`取得一個`5`的拷貝的所有權。那麼區別是什麼呢？

```rust
let mut num = 5;

{
    let mut add_num = |x: i32| num += x;

    add_num(5);
}

assert_eq!(10, num);
```

那麼在這個例子中，我們的閉包取得了一個`num`的可變引用，然後接著我們調用了`add_num`，它改變了其中的值，正如我們期望的。我們也需要將`add_num`聲明為`mut`，因為我們會改變它的環境。

如果我們加上`move`修飾閉包，會發生些不同：

```rust
let mut num = 5;

{
    let mut add_num = move |x: i32| num += x;

    add_num(5);
}

assert_eq!(5, num);
```

我們只會得到`5`。這次我們沒有獲取到外部的`num`的可變借用，我們實際上是把 `num` move 進了閉包。因為 `num` 具有 Copy 屬性，因此發生 move 之後，以前的變量生命週期並未結束，還可以繼續在 `assert_eq!` 中使用。我們打印的變量和閉包內的變量是獨立的兩個變量。如果我們捕獲的環境變量不是 Copy 的，那麼外部環境變量被 move 進閉包後，
它就不能繼續在原先的函數中使用了，只能在閉包內使用。

不過在我們討論獲取或返回閉包之前，我們應該更多的瞭解一下閉包實現的方法。作為一個系統語言，Rust給予你了大量的控制你代碼的能力，而閉包也是一樣。

> ### 這部分引用自[The Rust Programming Language中文版](https://github.com/KaiserY/rust-book-chinese/blob/master/content/Closures%20%E9%97%AD%E5%8C%85.md)
