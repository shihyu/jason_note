# 複合類型

## 元組(Tuple)

在別的語言裡，你可能聽過元組這個詞，它表示一個大小、類型固定的有序數據組。在 Rust 中，情況並沒有什麼本質上的不同。不過 Rust 為我們提供了一系列簡單便利的語法來讓我們能更好的使用他。

```rust
let y = (2, "hello world");
let x: (i32, &str) = (3, "world hello");

// 然後呢，你能用很簡單的方式去訪問他們：

// 用 let 表達式
let (w, z) = y; // w=2, z="hello world"

// 用下標

let f = x.0; // f = 3
let e = x.1; // e = "world hello"
```

## 結構體(struct)

在Rust中，結構體是一個跟 `tuple` 類似 的概念。我們同樣可以將一些常用的數據、屬性聚合在一起，就形成了一個結構體。

所不同的是，Rust的結構體有三種最基本的形式。

### 具名結構體

這種結構體呢，他可以大致看成這樣的一個聲明形式:

```rust
struct A {
    attr1: i32,
    atrr2: String,
}
```

內部每個成員都有自己的名字和類型。

### 元組類型結構體

元組類型結構體使用小括號，類似 `tuple` 。

```rust
struct B(i32, u16, bool);
```

它可以看作是一個有名字的元組，具體使用方法和一般的元組基本類似。

### 空結構體

結構體內部也可以沒有任何成員。

```rust
struct D;
```

空結構體的內存佔用為0。但是我們依然可以針對這樣的類型實現它的“成員函數”。

不過到目前為止，在 1.9 版本之前的版本，空結構體後面不能加大括號。
如果這麼寫，則會導致這部分的老編譯器編譯錯誤：

```rust
struct C {

}
```

### 實現結構體(impl)

Rust沒有繼承，它和Golang不約而同的選擇了trait(Golang叫Interface)作為其實現多態的基礎。可是，如果我們要想對一個結構體寫一些專門的成員函數那應該怎麼寫呢？

答： impl

talk is cheap ,舉個栗子：

```rust
struct Person {
    name: String,
}

impl Person {
    fn new(n: &str) -> Person {
        Person {
            name: n.to_string(),
        }
    }

    fn greeting(&self) {
        println!("{} say hello .", self.name);
    }
}

fn main() {
    let peter = Person::new("Peter");
    peter.greeting();
}
```

看見了 `self`，Python程序員不厚道的笑了。

我們來分析一下，上面的`impl`中，new 被 Person 這個結構體自身所調用，其特徵是 `::` 的調用，Java程序員站出來了：類函數！ 而帶有 `self` 的 `greeting` ，更像是一個成員函數。

恩，回答正確，然而不加分。

### 關於各種ref的討論

Rust 對代碼有著嚴格的安全控制，因此對一個變量也就有了所有權和借用的概念。所有權同一時間只能一人持有，可變引用也只能同時被一個實例持有，不可變引用則可以被多個實例持有。同時所有權能被轉移，在Rust中被稱為 `move` 。

以上是所有權的基本概念，事實上，在整個軟件的運行週期內，所有權的轉換是一件極其惱人和煩瑣的事情，尤其對那些初學 Rust 的同學來說。同樣的，Rust 的結構體作為其類型系統的基石，也有著比較嚴格的所有權控制限制。具體來說，關於結構體的所有權，有兩種你需要考慮的情況。

#### 字段的 ref 和 owner

在以上的結構體中，我們定義了不少結構體，但是如你所見，結構體的每個字段都是完整的屬於自己的。也就是說，每個字段的 owner 都是這個結構體。每個字段的生命週期最終都不會超過這個結構體。

但是有些時候，我只是想要持有一個(可變)引用的值怎麼辦？
如下代碼：

```rust
struct RefBoy {
    loc: &i32,
}
```

這時候你會得到一個編譯錯誤：

```
<anon>:6:14: 6:19 error: missing lifetime specifier [E0106]
<anon>:6         loc: & i32,
```

這種時候，你將持有一個值的引用，因為它本身的生命週期在這個結構體之外，所以對這個結構體而言，它無法準確的判斷獲知這個引用的生命週期，這在 Rust 編譯器而言是不被接受的。
因此，這個時候就需要我們給這個結構體人為的寫上一個生命週期，並顯式地表明這個引用的生命週期。寫法如下：

```rust
struct RefBoy<'a> {
    loc: &'a i32,
}
```

這裡解釋一下這個符號 `<>`，它表示的是一個 `屬於` 的關係，無論其中描述的是 *生命週期* 還是 *泛型* 。即： `RefBoy in 'a `。最終我們可以得出個結論，`RefBoy` 這個結構體，其生命週期一定不能比 `'a` 更長才行。

寫到這裡，可能有的人還是對生命週期比較迷糊，不明白其中緣由，其實你只需要知道兩點即可：

1. 結構體裡的引用字段必須要有顯式的生命週期
2. 一個被顯式寫出生命週期的結構體，其自身的生命週期一定小於等於其顯式寫出的任意一個生命週期

關於第二點，其實生命週期是可以寫多個的，用 `,` 分隔。

注：生命週期和泛型都寫在 `<>` 裡，先生命週期後泛型，用`,`分隔。

#### impl中的三種self

前面我們知道，Rust中，通過impl可以對一個結構體添加成員方法。同時我們也看到了`self`這樣的關鍵字，同時，這個self也有好幾種需要你仔細記憶的情況。

impl中的self,常見的有三種形式：`self`、 `&self`、`&mut self` ，我們分別來說。

##### 被move的self

正如上面例子中的impl，我們實現了一個以 `self` 為第一個參數的函數，但是這樣的函數實際上是有問題的。
問題在於Rust的所有權轉移機制。

我曾經見過一個關於Rust的笑話："你調用了一下別人，然後你就不屬於你了"。

比如下面代碼就會報出一個錯誤：

```rust
struct A {
    a: i32,
}
impl A {
    pub fn show(self) {
        println!("{}", self.a);
    }
}

fn main() {
    let ast = A{a: 12i32};
    ast.show();
    println!("{}", ast.a);
}
```

錯誤：

```
13:25 error: use of moved value: `ast.a` [E0382]
<anon>:13     println!("{}", ast.a);
```

為什麼呢？因為 Rust 本身，在你調用一個函數的時候，如果傳入的不是一個引用，那麼無疑，這個參數將被這個函數吃掉，即其 owner 將被 move 到這個函數的參數上。同理，`impl` 中的 `self` ，如果你寫的不是一個引用的話，也是會被默認的 move 掉喲！

那麼如何避免這種情況呢？答案是 `Copy` 和 `Clone` ：

```rust
#[derive(Copy, Clone)]
struct A {
    a: i32,
}
```

這麼寫的話，會使編譯通過。但是這麼寫實際上也是有其缺陷的。其缺陷就是： `Copy` 或者 `Clone` ，都會帶來一定的運行時開銷！事實上，被move的 `self` 其實是相對少用的一種情況，更多的時候，我們需要的是 `ref` 和 `ref mut` 。

###### ref 和 ref mut

關於 `ref` 和 `mut ref` 的寫法和被 move 的 `self` 寫法類似，只不過多了一個引用修飾符號，上面有例子，不多說。

需要注意的一點是，你不能在一個 `&self` 的方法裡調用一個 `&mut ref` ，任何情況下都不行！

但是，反過來是可以的。代碼如下：

```rust
#[derive(Copy, Clone)]
struct A {
    a: i32,
}
impl A {
    pub fn show(&self) {
        println!("{}", self.a);
        // compile error: cannot borrow immutable borrowed content `*self` as mutable
        // self.add_one();
    }
    pub fn add_two(&mut self) {
        self.add_one();
        self.add_one();
        self.show();
    }
    pub fn add_one(&mut self) {
        self.a += 1;
    }
}

fn main() {
    let mut ast = A{a: 12i32};
    ast.show();
    ast.add_two();
}
```

需要注意的是，一旦你的結構體持有一個可變引用，你，只能在 `&mut self` 的實現裡去改變他！

Rust允許我們靈活的對一個 struct 進行你想要的實現，在編程的自由度上無疑有了巨大的提高。

至於更高級的關於 trait 和泛型的用法，我們將在以後的章節進行詳細介紹。

## 枚舉類型 enum

Rust的枚舉(`enum`)類型，跟C語言的枚舉有點接近，然而更強大，事實上它是一種代數數據類型(Algebraic Data Type)。

比如說，這是一個代表東南西北四個方向的枚舉：

```rust
enum Direction {
    West,
    North,
    South,
    East,
}
```

但是，rust 的枚舉能做到的，比 C 語言的更多。
比如，枚舉裡面居然能包含一些你需要的，特定的數據信息！
這是常規的枚舉所無法做到的，更像枚舉類，不是麼？

```rust
enum SpecialPoint {
    Point(i32, i32),
    Special(String),
}
```

你還可以給裡面的字段命名，如

```rust
enum SpecialPoint {
    Point {
        x: i32,
        y: i32,
    },
    Special(String),
}
```

### 使用枚舉

和struct的成員訪問符號 `.` 不同的是，枚舉類型要想訪問其成員，幾乎無一例外的要用到模式匹配。並且， 你可以寫一個 `Direction::West`，但是你現在還不能寫成 `Direction.West`, 除非你顯式的 `use` 它 。雖然編譯器足夠聰明能發現你這個粗心的毛病。


關於模式匹配，我不會說太多，還是舉個栗子

```rust
enum SpecialPoint {
    Point(i32, i32),
    Special(String),
}

fn main() {
    let sp = SpecialPoint::Point(0, 0);
    match sp {
        SpecialPoint::Point(x, y) => {
            println!("I'am SpecialPoint(x={}, y={})", x, y);
        }
        SpecialPoint::Special(why) => {
            println!("I'am Special because I am {}", why);
        }
    }
}
```

吶吶吶，這就是模式匹配取值啦。
當然了， `enum` 其實也是可以 `impl` 的，一般人我不告訴他！

對於帶有命名字段的枚舉，模式匹配時可指定字段名

```rust
match sp {
    SpecialPoint::Point { x: x, y: y } => {
        // ...
    },
    SpecialPoint::Special(why) => {}
}
```

對於帶有字段名的枚舉類型，其模式匹配語法與匹配 `struct` 時一致。如

```rust
struct Point {
    x: i32,
    y: i32,
}

let point = Point { x: 1, y: 2 };

let Point { x: x, y: y } = point;
// 或
let Point { x, y } = point;
// 或
let Point { x: x, .. } = point;
```

模式匹配的語法與 `if let` 和 `let` 是一致的，所以在後面的內容中看到的也支持同樣的語法。
