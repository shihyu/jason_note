# String

這章我們來著重介紹一下字符串。

剛剛學習Rust的同學可能會被Rust的字符串搞混掉，比如`str`，`String`， `OsStr`， `CStr`，`CString`等等……
事實上，如果你不做FFI的話，常用的字符串類型就只有前兩種。我們就來著重研究一下Rust的前兩種字符串。

你要明白的是，Rust中的字符串實際上是被編碼成UTF-8的一個字節數組。這麼說比較拗口，簡單來說，Rust字符串內部存儲的是一個u8數組，但是這個數組是Unicode字符經過UTF-8編碼得來的。因此，可以看成Rust原生就支持Unicode字符集（Python2的碼農淚流滿面）。

## str

首先我們先來看一下`str`， 從字面意思上，Rust的string被表達為： `&'static str`(看不懂這個表達式沒關係，&表示引用你知道吧，static表示靜態你知道吧，好了，齊了)，即，你在代碼裡寫的，所有的用`""`包裹起來的字符串，都被聲明成了一個不可變，靜態的字符串。而我們的如下語句：

```rust
let x = "Hello";
let x:&'static str = "Hello";
```

實際上是將 `"Hello"` 這個靜態變量的引用傳遞給了`x`。同時，這裡的字符串不可變！

字符串也支持轉義字符：
比如如下：

```rust
let z = "foo
bar";
let w = "foo\nbar";
assert_eq!(z, w);
```

也可以在字符串字面量前加上`r`來避免轉義

    //沒有轉義序列
    let d: &'static str = r"abc \n abc";
    //等價於
    let c: &'static str = "abc \\n abc";

## String

光有`str`，確實不夠什麼卵用，畢竟我們在實際應用中要的更多的還是一個可變的，不定長的字符串。這時候，一種在堆上聲明的字符串`String`被設計了出來。
它能動態的去增長或者縮減，那麼怎麼聲明它呢？我們先介紹一種簡單的方式，從`str`中轉換：

```rust
let x:&'static str = "hello";

let mut y:String = x.to_string();
println!("{}", y);
y.push_str(", world");
println!("{}", y);
```

我知道你一定會問：——
    那麼如何將一個`String`重新變成`&str`呢？
    答：用 `&*` 符號

```rust
fn use_str(s: &str) {
    println!("I am: {}", s);
}

fn main() {
    let s = "Hello".to_string();
    use_str(&*s);
}
```

我們來分析一下，以下部分將涉及到部分`Deref`的知識，可能需要你預習一下，如果不能理解大可跳過下一段：

首先呢， `&*`是兩個符號`&`和`*`的組合，按照Rust的運算順序，先對`String`進行`Deref`,也就是`*`操作。

由於`String`實現了 `impl Deref<Target=str> for String`，這相當於一個運算符重載，所以你就能通過`*`獲得一個`str`類型。但是我們知道，單獨的`str`是不能在Rust裡直接存在的，因此，我們需要先給他進行`&`操作取得`&str`這個結果。

有人說了，我發現只要用`&`一個操作符就能將使上面的編譯通過。
這其實是一個編譯器的鍋，因為Rust的編譯器會在`&`後面插入足夠多的`*`來儘可能滿足`Deref`這個特性。這個特性會在某些情況下失效，因此，為了不給自己找麻煩，還是將操作符寫全為好。


需要知道的是，將`String`轉換成`&str`是非常輕鬆的，幾乎沒有任何開銷。但是反過來，將`&str`轉換成`String`是需要在堆上請求內存的，因此，要慎重。

我們還可以將一個UTF-8編碼的字節數組轉換成String，如

```rust
// 存儲在Vec裡的一些字節
let miao = vec![229,150,181];

// 我們知道這些字節是合法的UTF-8編碼字符串，所以直接unwrap()
let meow = String::from_utf8(miao).unwrap();

assert_eq!("喵", meow);
```

## 索引訪問

有人會把Rust中的字符串和其慣用的字符串等同起來，於是就出現瞭如下代碼

```rust
let x = "hello".to_string();
x[1]; //編譯錯誤！
```

Rust的字符串實際上是不支持通過下標訪問的，但是呢，我們可以通過將其轉變成數組的方式訪問

```rust
let x = "哎喲我去".to_string();
for i in x.as_bytes() {
    print!("{} ", i);
}

println!("");

for i in x.chars() {
    print!("{}", i);
}

x.chars().nth(2);
```

## 字符串切片

對字符串切片是一件非常危險的事，雖然Rust支持，但是我並不推薦。因為Rust的字符串Slice實際上是切的bytes。這也就造成了一個嚴重後果，如果你切片的位置正好是一個Unicode字符的內部，Rust會發生Runtime的panic，導致整個程序崩潰。
因為這個操作是如此的危險，所以我就不演示了……
