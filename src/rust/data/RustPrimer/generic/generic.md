# 泛型


我們在編程中，通常有這樣的需求，為多種類型的數據編寫一個功能相同的函數，如兩個數的加法，希望這個函數既支持i8、i16、 i32 ....float64等等，甚至自定義類型，在不支持泛型的編程語言中，我們通常要為每一種類型都編寫一個函數，而且通常情況下函數名還必須不同，例如：

```rust
fn add_i8(a:i8, b:i8) -> i8 {
	a + b
}
fn add_i16(a:i16, b:i16) -> i16 {
	a + b
}
fn add_f64(a:f64, b:f64) -> f64 {
	a + b
}

// 各種其他add函數
// ...

fn main() {
	println!("add i8: {}", add_i8(2i8, 3i8));
	println!("add i16: {}", add_i16(20i16, 30i16));
	println!("add f64: {}", add_f64(1.23, 1.23));
}
```

如果有很多地方都需要支持多種類型，那麼代碼量就會非常大，而且代碼也會非常臃腫，編程就真的變成了苦逼搬磚的工作，枯燥而乏味:D。
學過C++的人也許很容易理解泛型，但本教程面向的是Rust初學者，所以不會拿C++的泛型、多態和Rust進行對比，以免增加學習的複雜度和不必要的困擾，從而讓Rust初學者更容易理解和接受Rust泛型。


## 概念

泛型程序設計是程序設計語言的一種風格或範式。允許程序員在強類型程序設計語言中編寫代碼時使用一些以後才指定的類型，在實例化時（instantiate）作為參數指明這些類型（在Rust中，有的時候類型還可以被編譯器推導出來）。各種程序設計語言和其編譯器、運行環境對泛型的支持均不一樣。Ada, Delphi, Eiffel, Java, C#, F#, Swift, and Visual Basic .NET稱之為泛型（generics）；ML, Scala and Haskell稱之為參數多態（parametric polymorphism）；C++與D稱之為模板。具有廣泛影響的1994年版的《Design Patterns》一書稱之為參數化類型（parameterized type）。

>提示：
>以上概念摘自[《維基百科-泛型》](https://zh.wikipedia.org/wiki/%E6%B3%9B%E5%9E%8B)

在編程的時候，我們經常利用多態。通俗的講，多態就是好比坦克的炮管，既可以發射普通彈藥，也可以發射制導炮彈（導彈），也可以發射貧鈾穿甲彈，甚至發射子母彈，大家都不想為每一種炮彈都在坦克上分別安裝一個專用炮管，即使生產商願意，炮手也不願意，累死人啊。所以在編程開發中，我們也需要這樣“通用的炮管”，這個“通用的炮管”就是多態。

需要知道的是，泛型就是一種多態。

泛型主要目的是為程序員提供了編程的便利，減少代碼的臃腫,同時極大豐富了語言本身的表達能力, 為程序員提供了一個合適的炮管。想想，一個函數，代替了幾十個，甚至數百個函數，是一件多麼讓人興奮的事情。
泛型，可以理解為具有某些功能共性的集合類型，如i8、i16、u8、f32等都可以支持add，甚至兩個struct Point類型也可以add形成一個新的Point。

先讓我們來看看標準庫中常見的泛型Option<T>，它的原型定義：

```rust
enum Option<T> {
	Some(T),
	None,
}
```

T就是泛型參數，這裡的T可以換成A-Z任何你自己喜歡的字母。不過習慣上，我們用T表示Type，用E表示Error。T在具體使用的時候才會被實例化：

```rust
let a = Some(100.111f32);
```

編譯器會自行推導出a為Option<f32>類型，也就是說Option中的T在這裡是f32類型。

當然，你也可以顯式聲明a的類型，但必須保證和右值的類型一樣，不然編譯器會報"mismatched types"類型不匹配錯誤。

```rust
let a:Option<f32> = Some(100.111);  //編譯自動推導右值中的100.111為f32類型。
let b:Option<f32> = Some(100.111f32);
let c:Option<f64> = Some(100.111);
let d:Option<f64> = Some(100.111f64);
```


### 泛型函數
至此，我們已經瞭解到泛型的定義和簡單的使用了。
現在讓我們用函數重寫add操作：

```rust
use std::ops::Add;

fn add<T: Add<T, Output=T>>(a:T, b:T) -> T {
	a + b
}

fn main() {
	println!("{}", add(100i32, 1i32));
	println!("{}", add(100.11f32, 100.22f32));
}
```

>**輸出:**
>101
>200.33

```add<T: Add<T, Output=T>>(a:T, b:T) -> T```就是我們泛型函數，返回值也是泛型T，Add<>中的含義可以暫時忽略，大體意思就是隻要參數類型實現了Add trait，就可以被傳入到我們的add函數，因為我們的add函數中有相加+操作，所以要求傳進來的參數類型必須是可相加的，也就是必須實現了Add trait（具體參考std::ops::Add）。

### 自定義類型
上面的例子，add的都是語言內置的基礎數據類型，當然我們也可以為自己自定義的數據結構類型實現add操作。

```rust
use std::ops::Add;

#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

// 為Point實現Add trait
impl Add for Point {
    type Output = Point; //執行返回值類型為Point
    fn add(self, p: Point) -> Point {
        Point{
            x: self.x + p.x,
            y: self.y + p.y,
        }
    }
}

fn add<T: Add<T, Output=T>>(a:T, b:T) -> T {
	a + b
}

fn main() {
	println!("{}", add(100i32, 1i32));
	println!("{}", add(100.11f32, 100.22f32));

	let p1 = Point{x: 1, y: 1};
	let p2 = Point{x: 2, y: 2};
	println!("{:?}", add(p1, p2));
}
```

>**輸出:**
>101
200.33
Point { x: 3, y: 3 }

上面的例子稍微更復雜些了，只是我們增加了自定義的類型，然後讓add函數依然可以在上面工作。如果對trait不熟悉，請查閱trait相關章節。

大家可能會疑問，那我們是否可以讓Point也變成泛型的，這樣Point的x和y也能夠支持float類型或者其他類型，答案當然是可以的。

```rust
use std::ops::Add;

#[derive(Debug)]
struct Point<T: Add<T, Output = T>> { //限制類型T必須實現了Add trait，否則無法進行+操作。
    x: T,
    y: T,
}

impl<T: Add<T, Output = T>> Add for Point<T> {
    type Output = Point<T>;

    fn add(self, p: Point<T>) -> Point<T> {
        Point{
            x: self.x + p.x,
            y: self.y + p.y,
        }
    }
}

fn add<T: Add<T, Output=T>>(a:T, b:T) -> T {
	a + b
}

fn main() {
	let p1 = Point{x: 1.1f32, y: 1.1f32};
	let p2 = Point{x: 2.1f32, y: 2.1f32};
	println!("{:?}", add(p1, p2));

	let p3 = Point{x: 1i32, y: 1i32};
	let p4 = Point{x: 2i32, y: 2i32};
	println!("{:?}", add(p3, p4));
}
```

>**輸出：**
>Point { x: 3.2, y: 3.2 }
Point { x: 3, y: 3 }

上面的列子更復雜了些，我們不僅讓自定義的Point類型支持了add操作，同時我們也為Point做了泛型化。

當```let p1 = Point{x: 1.1f32, y: 1.1f32};```時，Point的T推導為f32類型，這樣Point的x和y屬性均成了f32類型。因為p1.x+p2.x，所以T類型必須支持Add trait。

### 總結
上面區區幾十行的代碼，卻實現了非泛型語言百行甚至千行代碼才能達到的效果，足見泛型的強大。

### 習題

#### 1. Generic lines iterator

##### 問題描述
有時候我們可能做些文本分析工作, 數據可能來源於外部或者程序內置的文本.

請實現一個 `parse` 函數, 只接收一個 lines iterator 為參數, 並輸出每行.

要求既能輸出內置的文本, 也能輸出文件內容.

##### 調用方式及輸出參考

```
let lines = "some\nlong\ntext".lines()
parse(do_something_or_nothing(lines))
```

```
some
long
text
```

```
use std::fs:File;
use std::io::prelude::*;
use std::io::BufReader;
let lines = BufReader::new(File::open("/etc/hosts").unwrap()).lines()
parse(do_some_other_thing_or_nothing(lines))
```

```
127.0.0.1       localhost.localdomain   localhost
::1             localhost.localdomain   localhost
...
```

##### Hint
本書`類型系統中的幾個常見 trait`章節中介紹的 AsRef, Borrow 等 trait 應該能派上用場.
