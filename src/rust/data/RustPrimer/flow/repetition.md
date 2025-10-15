# 循環

- for
- while
- loop
- break 與 continue
- label


## for

for 語句用於遍歷一個迭代器。

```rust
for var in iterator {
    code
}
```

Rust 迭代器返回一系列的元素，每個元素是循環中的一次重複。然後它的值與 var 綁定，它在循環體中有效。每當循環體執行完後，我們從迭代器中取出下一個值，然後我們再重複一遍。當迭代器中不再有值時，for 循環結束。

比如：

```rust
for x in 0..10 {
    println!("{}", x); // x: i32
}
```

輸出

```
0
1
2
3
4
5
6
7
8
9
```

不熟悉迭代器概念的同學可能傻眼了，下面不妨用 C 形式的 for 語句做下對比：

```rust
// C 語言的 for 循環例子
for (x = 0; x < 10; x++) {
    printf( "%d\n", x );
}
```

兩者輸出是相同的，那麼，為何 Rust 要這樣來設計 for 語句呢？

1. 簡化邊界條件的確定，減少出錯；
2. 減少運行時邊界檢查，提高性能。

即使對於有經驗的 C 語言開發者來說，要手動控制要循環的每個元素也都是複雜並且易於出錯的。

for 語句就是迭代器遍歷的語法糖。

上述迭代器的形式雖好，但是好像在循環過程中，少了索引信息。Rust 考慮到了這一點，當你需要記錄你已經循環了多少次了的時候，你可以使用 `.enumerate()` 函數。比如：

```rust
for (i,j) in (5..10).enumerate() {
    println!("i = {} and j = {}", i, j);
}
```

輸出：

```
i = 0 and j = 5
i = 1 and j = 6
i = 2 and j = 7
i = 3 and j = 8
i = 4 and j = 9
```

再比如：

```rust
let lines = "Content of line one
Content of line two
Content of line three
Content of line four".lines();
for (linenumber, line) in lines.enumerate() {
    println!("{}: {}", linenumber, line);
}
```

輸出：

```
0: Content of line one
1: Content of line two
2: Content of line three
3: Content of line four
```

關於迭代器的知識，詳見 **迭代器** 章節。

## while

Rust 提供了 while 語句，條件表達式為真時，執行語句體。當你不確定應該循環多少次時可選擇 while。

```rust
while expression {
    code
}
```

比如：

```rust
let mut x = 5; // mut x: i32
let mut done = false; // mut done: bool

while !done {
    x += x - 3;

    println!("{}", x);

    if x % 5 == 0 {
        done = true;
    }
}
```

## loop

有一種情況，我們經常會遇到，就是寫一個無限循環：

```rust
while true {
    // do something
}
```

針對這種情況，Rust 專門優化提供了一個語句 loop。

```rust
loop {
    // do something
}
```

`loop` 與 `while true` 的主要區別在編譯階段的靜態分析。

比如說，如下代碼：

```rust
let mut a;
loop {
     a = 1;
     // ... break ...
}
do_something(a)
```

如果是`loop`循環，編譯器會正確分析出變量`a`會被正確初始化，而如果換成`while true`，則會發生編譯錯誤。這個微小的區別也會影響生命週期分析。

## break 和 continue

與 C 語言類似，Rust 也提供了 break 和 continue 兩個關鍵字用來控制循環的流程。

- break 用來跳出當前層的循環；
- continue 用來執行當前層的下一次迭代。

像上面那個 while 例子：

```rust
let mut x = 5;
let mut done = false;

while !done {
    x += x - 3;

    println!("{}", x);

    if x % 5 == 0 {
        done = true;
    }
}
```

可以優化成：

```rust
let mut x = 5;

loop {
    x += x - 3;

    println!("{}", x);

    if x % 5 == 0 { break; }
}
```

這樣感覺更直觀一點。

下面這個例子演示 continue 的用法：

```rust
for x in 0..10 {
    if x % 2 == 0 { continue; }

    println!("{}", x);
}
```

它的作用是打印出 `0~9` 的奇數。結果如下：

```
1
3
5
7
9
```

## label

你也許會遇到這樣的情形，當你有嵌套的循環而希望指定你的哪一個 break 或 continue 該起作用。就像大多數語言，默認 break 或 continue 將會作用於當前層的循環。當你想要一個 break 或 continue 作用於一個外層循環，你可以使用標籤來指定你的 break 或 continue 語句作用的循環。

如下代碼只會在 x 和 y 都為奇數時打印他們：

```rust
'outer: for x in 0..10 {
    'inner: for y in 0..10 {
        if x % 2 == 0 { continue 'outer; } // continues the loop over x
        if y % 2 == 0 { continue 'inner; } // continues the loop over y
        println!("x: {}, y: {}", x, y);
    }
}
```
