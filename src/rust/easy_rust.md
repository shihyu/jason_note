## 更新

![example workflow name](https://github.com/kumakichi/easy_rust_chs/workflows/github%20pages/badge.svg)

2021年2月1日: [Youtube視頻](https://www.youtube.com/playlist?list=PLfllocyHVgsRwLkTAhG0E-2QxCf-ozBkk)

2021年1月4日: 支持在線查看 [點擊閱讀](https://kumakichi.github.io/easy_rust_chs)

## 介紹

Rust是一種新的語言，已經有了很好的教科書。但是有時候它的教材很難，因為它的教材是給以英語為母語的人看的。現在很多公司和人學習Rust，如果有一本英語簡單的書，他們可以學得更快。這本教材就是給這些公司和人用簡單的英語來學習Rust的。

Rust是一門很新的語言，但已經非常流行。它之所以受歡迎，是因為它給你提供了C或C++的速度和控制力，但也給你提供了Python等其他較新語言的內存安全。它用一些新的想法來實現這一點，這些想法有時與其他語言不同。這意味著有一些新的東西需要學習，你不能只是 "邊走邊想"。Rust是一門語言，你必須思考一段時間才能理解。但如果你懂其他語言的話，它看起來還是很熟悉的，它是為了幫助你寫好代碼而生的。

## 我是誰？

我是一個生活在韓國的加拿大人，我在寫Easy Rust的同時，也在思考如何讓這裡的公司開始使用它。我希望其他不以英語為第一語言的國家也能使用它。

## 簡單英語學Rust

*簡單英語學Rust*寫於2020年7月至8月，長達400多頁。如果你有任何問題，可以在這裡或[在LinkedIn上](https://www.linkedin.com/in/davemacleod)或[在Twitter上](https://twitter.com/mithridates)聯繫我。如果你發現有什麼不對的地方，或者要提出pull request，請繼續。已經有超過20人幫助我們修復了代碼中的錯別字和問題，所以你也可以。我不是世界上最好的Rust專家，所以我總是喜歡聽到新的想法，或者看看哪裡可以讓這本書變得更好。

- [第1部分 - 瀏覽器中的Rust](#第1部分---瀏覽器中的Rust)
  - [Rust Playground](#rust-playground)
  - [🚧 and ⚠️](#和%EF%B8%8F)
  - [註釋](#註釋)
  - [類型](#類型)
    - [原始類型](#原始類型)
  - [類型推導](#類型推導)
    - [浮點數](#浮點數)
  - [打印hello, world!](#打印hello-world)
    - [聲明變量和代碼塊](#聲明變量和代碼塊)
  - [顯示和調試](#顯示和調試)
    - [最小和最大的數](#最小和最大的數)
  - [可變性](#可變性)
    - [遮蔽](#遮蔽)
  - [棧，堆和指針](#棧堆和指針)
  - [關於打印的更多信息](#關於打印的更多信息)
  - [字符串](#字符串)
  - [const和static](#const和static)
  - [關於引用的更多信息](#關於引用的更多信息)
  - [可變引用](#可變引用)
    - [再談shadowing](#再談shadowing)
  - [函數的引用](#函數的引用)
  - [拷貝類型](#拷貝類型)
    - [無值變量](#無值變量)
  - [集合類型](#集合類型)
    - [數組](#數組)
  - [向量](#向量)
  - [元組](#元組)
  - [控制流](#控制流)
  - [結構體](#結構體)
  - [枚舉](#枚舉)
    - [使用多種類型的枚舉](#使用多種類型的枚舉)
  - [循環](#循環)
  - [實現結構和枚舉](#實現結構和枚舉)
  - [解構](#解構)
  - [引用和點運算符](#引用和點運算符)
  - [泛型](#泛型)
  - [選項和結果](#選項和結果)
    - [選項](#選項)
    - [結果](#結果)
  - [其他集合類型](#其他集合類型)
    - [HashMap和BTreeMap](#HashMap和BTreeMap)
    - [HashSet和BTreeSet](#hashset和btreeset)
    - [二叉堆](#二叉堆)
    - [VecDeque](#vecdeque)
  - [?操作符](#操作符)
    - [When panic and unwrap are good](#when-panic-and-unwrap-are-good)
  - [trait](#trait)
    - [From trait](#from-trait)
    - [在函數中使用字符串和&str](#在函數中使用字符串和&str)
  - [鏈式方法](#鏈式方法)
  - [迭代器](#迭代器)
    - [迭代器如何工作](#迭代器如何工作)
  - [閉包](#閉包)
    - [閉包中的_](#閉包中的_)
    - [閉包和迭代器的有用方法](#閉包和迭代器的有用方法)
  - [dbg! 宏和.檢查器](#dbg宏和inspect)
  - [&str的類型](#str的類型)
  - [生命期](#生命期)
  - [內部可變性](#內部可變性)
    - [Cell](#cell)
    - [RefCell](#refcell)
    - [Mutex](#mutex)
    - [RwLock](#rwlock)
  - [Cow](#cow)
  - [類型別名](#類型別名)
    - [在函數中導入和重命名](#在函數中導入和重命名)
  - [todo!宏](#todo宏)
  - [Rc](#rc)
  - [多線程](#多線程)
  - [函數中的閉包](#函數中的閉包)
  - [impl Trait](#impl-trait)
  - [Arc](#arc)
  - [Channels](#channels)
  - [閱讀Rust文檔](#閱讀Rust文檔)
    - [assert_eq! ](#assert_eq)
    - [搜索](#搜索)
    - [[src]按鈕](#src-按鈕)
    - [trait信息](#trait信息)
  - [屬性](#屬性)
  - [Box](#box)
  - [Box around traits](#box-around-traits)
  - [默認值和建造者模式](#默認值和建造者模式)
  - [Deref和DerefMut](#Deref和DerefMut)
  - [Crate和模塊](#Crate和模塊)
  - [測試](#測試)
    - [測試驅動的開發](#測試驅動的開發)
  - [外部crate](#外部crate)
    - [rand](#rand)
    - [rayon](#rayon)
    - [serde](#serde)
    - [regex](#regex)
    - [chrono](#chrono)
  - [標準庫之旅](#標準庫之旅)
    - [數組](#數組-1)
    - [char](#char)
    - [Integer](#integers)
    - [Floats](#floats)
    - [Bool](#bool)
    - [Vec](#vec)
    - [String](#string)
    - [OsString和CString](#OsString和CString)
    - [Mem](#mem)
    - [Prelude](#prelude)
    - [Time](#time)
    - [其他宏](#其他宏)
    - [編寫宏](#編寫宏)
- [第2部分 - 電腦上的Rust](#第2部分---電腦上的Rust)
  - [cargo](#cargo)
  - [接受用戶輸入](#接受用戶輸入)
  - [使用文件](#使用文件)
  - [cargo文檔](#cargo文檔)
  - [結束了嗎？](#結束了嗎？)

# 第1部分 - 瀏覽器中的Rust

本書有兩個部分。第1部分，你將在瀏覽器中就能學到儘可能多的Rust知識。實際上你幾乎可以在不安裝Rust的情況下學到所有你需要知道的東西，所以第1部分非常長。最後是第二部分。它要短得多，是關於電腦上的Rust。在這裡，你將學習到其他一切你需要知道的、只能在瀏覽器之外進行的事情。例如:處理文件、接受用戶輸入、圖形和個人設置。希望在第一部分結束時，你會喜歡Rust，以至於你會安裝它。如果你不喜歡，也沒問題--第一部分教了你很多，你不會介意的。

## Rust Playground

也許你還不想安裝Rust，這也沒關係。你可以去[https://play.rust-lang.org/](https://play.rust-lang.org/)，在不離開瀏覽器的情況下開始寫Rust。你可以在那裡寫下你的代碼，然後點擊Run來查看結果。你可以在瀏覽器的Playground裡面運行本書中的大部分示例。只有在接近結尾的時候，你才會看到無法在Playground運行的示例(比如打開文件)。

以下是使用Rust Playground時的一些提示。

- 用"Run"來運行你的代碼

- 如果你想讓你的代碼更快，就把Debug改為Release。Debug:編譯速度更快，運行速度更慢，包含調試信息。Release:編譯速度更慢，運行速度更快，刪除調試信息。
- 點擊Share，得到一個網址鏈接，你可以用它來分享你的代碼。如果你需要幫助，可以用它來分享你的代碼。點擊分享後，你可以點擊`Open a new thread in the Rust user forum`，馬上向那裡的人尋求幫助。
- Rustfmt工具: Rustfmt會很好地格式化你的代碼。
- TOOLS: Rustfmt會很好地格式化你的代碼。Clippy會給你額外的信息，告訴你如何讓你的代碼更好。
- CONFIG: 在這裡你可以把你的主題改成黑暗模式，這樣你就可以在晚上工作了，還有很多其他配置。

如果你想安裝Rust，請到這裡[https://www.rust-lang.org/tools/install](https://www.rust-lang.org/tools/install)，然後按照說明操作。通常你會使用`rustup`來安裝和更新Rust。

## 🚧和⚠️

有時書中的代碼例子不能用。如果一個例子不工作，它將會有一個🚧或⚠️在裡面。🚧就像 "正在建設中"一樣:它意味著代碼不完整。Rust需要一個`fn main()`(一個主函數)來運行，但有時我們只是想看一些小的代碼，所以它不會有`fn main()`。這些例子是正確的，但需要一個`fn main()`讓你運行。而有些代碼示例向你展示了一個問題，我們將解決這個問題。那些可能有一個`fn main()`，但會產生一個錯誤，所以它們會有一個⚠️。

## 註釋

註釋是給程序員看的，而不是給電腦看的。寫註釋是為了幫助別人理解你的代碼。 這也有利於幫助你以後理解你的代碼。 (很多人寫了很好的代碼，但後來卻忘記了他們為什麼要寫它。)在Rust中寫註釋，你通常使用 `//`．

```rust
fn main() {
    // Rust programs start with fn main()
    // You put the code inside a block. It starts with { and ends with }
    let some_number = 100; // We can write as much as we want here and the compiler won't look at it
}
```

當你這樣做時，編譯器不會看`//`右邊的任何東西。

還有一種註釋，你用`/*`開始寫，`*/`結束寫。這個寫在你的代碼中間很有用。

```rust
fn main() {
    let some_number/*: i16*/ = 100;
}
```

對編譯器來說，`let some_number/*: i16*/ = 100;`看起來像`let some_number = 100;`。

`/* */`形式對於超過一行的非常長的註釋也很有用。在這個例子中，你可以看到你需要為每一行寫`//`。但是如果您輸入 `/*`，它不會停止，直到您用 `*/` 完成它。

```rust
fn main() {
    let some_number = 100; /* Let me tell you
    a little about this number.
    It's 100, which is my favourite number.
    It's called some_number but actually I think that... */

    let some_number = 100; // Let me tell you
    // a little about this number.
    // It's 100, which is my favourite number.
    // It's called some_number but actually I think that...
}
```

## 類型

Rust有很多類型，讓你可以處理數字、字符等。有些類型很簡單，有些類型比較複雜，你甚至可以創建自己的類型。

### 原始類型

Rust有簡單的類型，這些類型被稱為**原始類型**(原始=非常基本)。我們將從整數和`char`(字符)開始。整數是沒有小數點的整數。整數有兩種類型。

- 有符號的整數
- 無符號整數

符號是指`+`(加號)和`-`(減號)，所以有符號的整數可以是正數，也可以是負數(如+8，-8)。但無符號整數只能是正數，因為它們沒有符號。

有符號的整數是 `i8`, `i16`, `i32`, `i64`, `i128`, 和 `isize`。

無符號的整數是 `u8`, `u16`, `u32`, `u64`, `u128`, 和 `usize`。

i或u後面的數字表示該數字的位數，所以位數多的數字可以大一些。8位=一個字節，所以`i8`是一個字節，`i64`是8個字節，以此類推。尺寸較大的數字類型可以容納更大的數字。例如，`u8`最多可以容納255，但`u16`最多可以容納65535。而`u128`最多可以容納340282366920938463463374607431768211455。

那麼什麼是`isize`和`usize`呢？這表示你電腦的位數。(你的電腦上的位數叫做你電腦的**架構**)。所以32位計算機上的`isize`和`usize`就像`i32`和`u32`，64位計算機上的`isize`和`usize`就像`i64`和`u64`。

整數類型不同的原因有很多。其中一個原因是計算機性能:較小的字節數處理速度更快。例如，數字-10作為`i8`是`11110110`，但作為`i128`是`11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111110110`。但這裡還有一些其他用法。

Rust中的字符叫做`char`. 每一個`char`都有一個數字:字母`A`是數字65，而字符`友`(中文的 "朋友")是數字21451。這個數字列表被稱為 "Unicode"。Unicode對使用較多的字符使用較小的數字，如A到Z，或0到9的數字，或空格。

```rust
fn main() {
    let first_letter = 'A';
    let space = ' '; // A space inside ' ' is also a char
    let other_language_char = 'Ꮔ'; // Thanks to Unicode, other languages like Cherokee display just fine too
    let cat_face = '😺'; // Emojis are chars too
}
```

使用最多的字符的數字小於256，它們可以裝進`u8`。記住，`u8`是0加上255以內的所有數字，總共256個。這意味著 Rust 可以使用 `as` 將 `u8` 安全地 **cast**成 `char`。("把 `u8` cast成 `char`"意味著 "把 `u8` 假裝成 `char`")

用 `as` cast是有用的，因為 Rust 是非常嚴格的。它總是需要知道類型。
 而不會讓你同時使用兩種不同的類型，即使它們都是整數。例如，這將無法工作:

```rust
fn main() { // main() is where Rust programs start to run. Code goes inside {} (curly brackets)

    let my_number = 100; // We didn't write a type of integer,
                         // so Rust chooses i32. Rust always
                         // chooses i32 for integers if you don't
                         // tell it to use a different type

    println!("{}", my_number as char); // ⚠️
}
```

原因是這樣的:

```text
error[E0604]: only `u8` can be cast as `char`, not `i32`
 --> src\main.rs:3:20
  |
3 |     println!("{}", my_number as char);
  |                    ^^^^^^^^^^^^^^^^^
```

幸運的是，我們可以用`as`輕鬆解決這個問題。我們不能把`i32`轉成`char`，但我們可以把`i32`轉成`u8`，然後把`u8`轉換成`char`。所以在一行中，我們使用 `as` 將 my_number 變為 `u8`，再將其變為 `char`。現在可以編譯了。

```rust
fn main() {
    let my_number = 100;
    println!("{}", my_number as u8 as char);
}
```

它打印的是`d`，因為那是100對應的`char`。

然而，更簡單的方法是告訴 Rust `my_number` 是 `u8`。下面是你的做法。

```rust
fn main() {
    let my_number: u8 = 100; //  change my_number to my_number: u8
    println!("{}", my_number as char);
}
```

所以這就是Rust中所有不同數字類型的兩個原因。這裡還有一個原因:`usize`是Rust用於*索引*的大小。(索引的意思是 "哪項是第一"，"哪項是第二"等等)`usize`是索引的最佳大小，因為:

- 索引不能是負數，所以它需要是一個帶u的數字
- 它應該是大的，因為有時你需要索引很多東西，但。
- 不可能是u64，因為32位電腦不能使用u64。

所以Rust使用了`usize`，這樣你的計算機就可以得到它能讀到的最大的數字進行索引。



我們再來瞭解一下`char`。你看到`char`總是一個字符，並且使用`''`而不是`""`。

所有的 `字符` 都使用4個字節的內存，因為4個字節足以容納任何種類的字符:
- 基本字母和符號通常需要4個字節中的1個：`a b 1 2 + - = $ @`
- 其他字母，如德語的 Umlauts 或重音，需要4個字節中的2個： `ä ö ü ß è é à ñ`
- 韓文、日文或中文字符需要3或4個字節： `國 안 녕`

當使用字符作為字符串的一部分時，字符串被編碼以使用每個字符所需的最小內存量。

我們可以用`.len()`來看一下。

```rust
fn main() {
    println!("Size of a char: {}", std::mem::size_of::<char>()); // 4 bytes
    println!("Size of string containing 'a': {}", "a".len()); // .len() gives the size of the string in bytes
    println!("Size of string containing 'ß': {}", "ß".len());
    println!("Size of string containing '國': {}", "國".len());
    println!("Size of string containing '𓅱': {}", "𓅱".len());
}
```

這樣打印出來。

```text
Size of a char: 4
Size of string containing 'a': 1
Size of string containing 'ß': 2
Size of string containing '國': 3
Size of string containing '𓅱': 4
```

可以看到，`a`是一個字節，德文的`ß`是兩個字節，日文的`國`是三個字節，古埃及的`𓅱`是4個字節。

```rust
fn main() {
    let slice = "Hello!";
    println!("Slice is {} bytes.", slice.len());
    let slice2 = "안녕!"; // Korean for "hi"
    println!("Slice2 is {} bytes.", slice2.len());
}
```

這個打印:

```text
Slice is 6 bytes.
Slice2 is 7 bytes.
```

`slice`的長度是6個字符，6個字節，但`slice2`的長度是3個字符，7個字節。

如果`.len()`給出的是以字節為單位的大小，那麼以字符為單位的大小呢？這些方法我們後面會學習，但你只要記住`.chars().count()`就可以了。`.chars().count()` 將你寫的東西變成字符，然後計算有多少個字符。


```rust
fn main() {
    let slice = "Hello!";
    println!("Slice is {} bytes and also {} characters.", slice.len(), slice.chars().count());
    let slice2 = "안녕!";
    println!("Slice2 is {} bytes but only {} characters.", slice2.len(), slice2.chars().count());
}
```

這就打印出來了。

```text
Slice is 6 bytes and also 6 characters.
Slice2 is 7 bytes but only 3 characters.
```

## 類型推導

類型推導的意思是，如果你不告訴編譯器類型，但它可以自己決定，它就會決定。編譯器總是需要知道變量的類型，但你並不總是需要告訴它。實際上，通常你不需要告訴它。例如，對於`let my_number = 8`，`my_number`將是一個`i32`。這是因為如果你不告訴它，編譯器會選擇i32作為整數。但是如果你說`let my_number: u8 = 8`，它就會把`my_number`變成`u8`，因為你告訴它`u8`。

通常編譯器都能猜到。但有時你需要告訴它，原因有兩個。

1) 你正在做一些非常複雜的事情，而編譯器不知道你想要的類型。
2) 你想要一個不同的類型(例如，你想要一個`i128`，而不是`i32`)。

要指定一個類型，請在變量名後添加一個冒號。

```rust
fn main() {
    let small_number: u8 = 10;
}
```

對於數字，你可以在數字後面加上類型。你不需要空格--只需要在數字後面直接輸入。

```rust
fn main() {
    let small_number = 10u8; // 10u8 = 10 of type u8
}
```

如果你想讓數字便於閱讀，也可以加上`_`。

```rust
fn main() {
    let small_number = 10_u8; // This is easier to read
    let big_number = 100_000_000_i32; // 100 million is easy to read with _
}
```

`_`不會改變數字。它只是為了讓你方便閱讀。而且你用多少個`_`都沒有關係。

```rust
fn main() {
    let number = 0________u8;
    let number2 = 1___6______2____4______i32;
    println!("{}, {}", number, number2);
}
```

這樣打印出的是`0, 1624`。

### 浮點數

浮點數是帶有小數點的數字。5.5是一個浮點數，6是一個整數。5.0也是一個浮點數，甚至5.也是一個浮點數。

```rust
fn main() {
    let my_float = 5.; // Rust sees . and knows that it is a float
}
```

但類型不叫`float`，叫`f32`和`f64`。這和整數一樣:`f`後面的數字顯示的是位數。如果你不寫類型，Rust會選擇`f64`。

當然，只有同一類型的浮點數可以一起使用。所以你不能把`f32`加到`f64`上。

```rust
fn main() {
    let my_float: f64 = 5.0; // This is an f64
    let my_other_float: f32 = 8.5; // This is an f32

    let third_float = my_float + my_other_float; // ⚠️
}
```

當你嘗試運行這個時，Rust會說。

```text
error[E0308]: mismatched types
 --> src\main.rs:5:34
  |
5 |     let third_float = my_float + my_other_float;
  |                                  ^^^^^^^^^^^^^^ expected `f64`, found `f32`
```

當你使用錯誤的類型時，編譯器會寫 "expected (type), found (type)"。它這樣讀取你的代碼。

```rust
fn main() {
    let my_float: f64 = 5.0; // The compiler sees an f64
    let my_other_float: f32 = 8.5; // The compiler sees an f32. It is a different type.
    let third_float = my_float + // You want to add my_float to something, so it must be an f64 plus another f64. Now it expects an f64...
    let third_float = my_float + my_other_float;  // ⚠️ but it found an f32. It can't add them.
}
```

所以，當你看到 "expected(type)，found(type)"時，你必須找到為什麼編譯器預期的是不同的類型。

當然，用簡單的數字很容易解決。你可以用`as`把`f32`轉成`f64`。

```rust
fn main() {
    let my_float: f64 = 5.0;
    let my_other_float: f32 = 8.5;

    let third_float = my_float + my_other_float as f64; // my_other_float as f64 = use my_other_float like an f64
}
```

或者更簡單，去掉類型聲明。("聲明一個類型"="告訴Rust使用該類型")Rust會選擇可以加在一起的類型。

```rust
fn main() {
    let my_float = 5.0; // Rust will choose f64
    let my_other_float = 8.5; // Here again it will choose f64

    let third_float = my_float + my_other_float;
}
```

Rust編譯器很聰明，如果你需要f32，就不會選擇f64。

```rust
fn main() {
    let my_float: f32 = 5.0;
    let my_other_float = 8.5; // Usually Rust would choose f64,

    let third_float = my_float + my_other_float; // but now it knows that you need to add it to an f32. So it chooses f32 for my_other_float too
}
```

## 打印hello, world!

當你啟動一個新的Rust程序時，它總是有這樣的代碼。

```rust
fn main() {
    println!("Hello, world!");
}
```

- `fn`的意思是函數。
- `main`是啟動程序的函數。

- `()`表示我們沒有給函數任何變量來啟動。

`{}`被稱為**代碼塊**。這是代碼所在的空間。

`println!`是一個**宏**，打印到控制檯。一個**宏**就像一個函數，為你寫代碼。宏後面有一個`!`。我們以後會學習如何創建宏。現在，請記住，`!`表示它是一個宏。

為了學習`;`，我們將創建另一個函數。首先，在`main`中，我們將打印一個數字8。

```rust
fn main() {
    println!("Hello, world number {}!", 8);
}
```

`println!`中的`{}`的意思是 "把變量放在這裡面"。這樣就會打印出`Hello, world number 8!`。


我們可以像之前一樣，放更多的東西進去。

```rust
fn main() {
    println!("Hello, worlds number {} and {}!", 8, 9);
}
```

這將打印出 `Hello, worlds number 8 and 9!`。

現在我們來創建函數。

```rust
fn number() -> i32 {
    8
}

fn main() {
    println!("Hello, world number {}!", number());
}
```

這也會打印出 `Hello, world number 8!`。當Rust查看`number()`時，它看到一個函數。這個函數:

- 沒有參數(因為它有`()`)
- 返回一個`i32`。`->`(稱為 "瘦箭")顯示了函數返回的內容

函數內部只有`8`。因為沒有`;`，所以這就是它返回的值。如果它有一個`;`，它將不會返回任何東西(它會返回一個`()`)。如果它有 `;`，Rust 不會編譯通過，因為需要返回的是 `i32`，而 `;` 返回 `()`，不是 `i32`。

```rust
fn main() {
    println!("Hello, world number {}", number());
}

fn number() -> i32 {
    8;  // ⚠️
}
```

```text
5 | fn number() -> i32 {
  |    ------      ^^^ expected `i32`, found `()`
  |    |
  |    implicitly returns `()` as its body has no tail or `return` expression
6 |     8;
  |      - help: consider removing this semicolon
```

這意味著 "你告訴我`number()`返回的是`i32`，但你加了一個`;`，所以它什麼都不返回"。所以編譯器建議去掉分號。

你也可以寫`return 8;`，但在Rust中，正常情況下只需將`;`改為`return`即可。

當你想給一個函數賦予變量時，把它們放在`()`裡面。你必須給它們起個名字，寫上類型。

```rust
fn multiply(number_one: i32, number_two: i32) { // Two i32s will enter the function. We will call them number_one and number_two.
    let result = number_one * number_two;
    println!("{} times {} is {}", number_one, number_two, result);
}

fn main() {
    multiply(8, 9); // We can give the numbers directly
    let some_number = 10; // Or we can declare two variables
    let some_other_number = 2;
    multiply(some_number, some_other_number); // and put them in the function
}
```

我們也可以返回一個`i32`。只要把最後的分號去掉就可以了:

```rust
fn multiply(number_one: i32, number_two: i32) -> i32 {
    let result = number_one * number_two;
    println!("{} times {} is {}", number_one, number_two, result);
    result // this is the i32 that we return
}

fn main() {
    let multiply_result = multiply(8, 9); // We used multiply() to print and to give the result to multiply_result
}
```

### 聲明變量和代碼塊

使用`let`聲明一個變量(聲明一個變量=告訴Rust創建一個變量)。

```rust
fn main() {
    let my_number = 8;
    println!("Hello, number {}", my_number);
}
```

變量在代碼塊`{}`內開始和結束。在這個例子中，`my_number`在我們調用`println!`之前結束，因為它在自己的代碼塊裡面。

```rust
fn main() {
    {
        let my_number = 8; // my_number starts here
                           // my_number ends here!
    }

    println!("Hello, number {}", my_number); // ⚠️ there is no my_number and
                                             // println!() can't find it
}
```

你可以使用代碼塊來返回一個值。

```rust
fn main() {
    let my_number = {
    let second_number = 8;
        second_number + 9 // No semicolon, so the code block returns 8 + 9.
                          // It works just like a function
    };

    println!("My number is: {}", my_number);
}
```

如果在代碼塊內部添加分號，它將返回 `()` (無)。

```rust
fn main() {
    let my_number = {
    let second_number = 8; // declare second_number,
        second_number + 9; // add 9 to second_number
                           // but we didn't return it!
                           // second_number dies now
    };

    println!("My number is: {:?}", my_number); // my_number is ()
}
```

那麼為什麼我們要寫`{:?}`而不是`{}`呢？我們現在就來談談這個問題。

## 顯示和調試

Rust中簡單的變量可以用`{}`裡面的`println!`打印。但是有些變量不能，你需要**debug print**。Debug打印是給程序員打印的，因為它通常會顯示更多的信息。Debug有時看起來並不漂亮，因為它有額外的信息來幫助你。

你怎麼知道你是否需要`{:?}`而不是`{}`？編譯器會告訴你。比如說

```rust
fn main() {
    let doesnt_print = ();
    println!("This will not print: {}", doesnt_print); // ⚠️
}
```

當我們運行這個時，編譯器會說:

```text
error[E0277]: `()` doesn't implement `std::fmt::Display`
 --> src\main.rs:3:41
  |
3 |     println!("This will not print: {}", doesnt_print);
  |                                         ^^^^^^^^^^^^ `()` cannot be formatted with the default formatter
  |
  = help: the trait `std::fmt::Display` is not implemented for `()`
  = note: in format strings you may be able to use `{:?}` (or {:#?} for pretty-print) instead
  = note: required by `std::fmt::Display::fmt`
  = note: this error originates in a macro (in Nightly builds, run with -Z macro-backtrace for more info)
```

信息比較多，但重要的部分是 `you may be able to use {:?} (or {:#?} for pretty-print) instead`. 這意味著你可以試試`{:?}`，也可以試試`{:#?}` `{:#?}`叫做 "漂亮打印"。它和`{:?}`一樣，但是在更多的行上打印出不同的格式。

所以Display就是用`{}`打印，Debug就是用`{:?}`打印。

還有一點:如果你不想要新的一行，你也可以使用`print!`而不用`ln`。

```rust
fn main() {
    print!("This will not print a new line");
    println!(" so this will be on the same line");
}
```

這將打印`This will not print a new line so this will be on the same line`。

### 最小和最大的數

如果你想看最小和最大的數字，你可以用MIN和MAX。`std`的意思是 "標準庫"，擁有Rust的所有主要函數等。我們將在以後學習標準庫。但與此同時，你可以記住，這就是你如何獲得一個類型的最小和最大的數字。

```rust
fn main() {
    println!("The smallest i8 is {} and the biggest i8 is {}.", std::i8::MIN, std::i8::MAX); // hint: printing std::i8::MIN means "print MIN inside of the i8 section in the standard library"
    println!("The smallest u8 is {} and the biggest u8 is {}.", std::u8::MIN, std::u8::MAX);
    println!("The smallest i16 is {} and the biggest i16 is {}.", std::i16::MIN, std::i16::MAX);
    println!("The smallest u16 is {} and the biggest u16 is {}.", std::u16::MIN, std::u16::MAX);
    println!("The smallest i32 is {} and the biggest i32 is {}.", std::i32::MIN, std::i32::MAX);
    println!("The smallest u32 is {} and the biggest u32 is {}.", std::u32::MIN, std::u32::MAX);
    println!("The smallest i64 is {} and the biggest i64 is {}.", std::i64::MIN, std::i64::MAX);
    println!("The smallest u64 is {} and the biggest u64 is {}.", std::u64::MIN, std::u64::MAX);
    println!("The smallest i128 is {} and the biggest i128 is {}.", std::i128::MIN, std::i128::MAX);
    println!("The smallest u128 is {} and the biggest u128 is {}.", std::u128::MIN, std::u128::MAX);

}
```

將會打印:

```text
The smallest i8 is -128 and the biggest i8 is 127.
The smallest u8 is 0 and the biggest u8 is 255.
The smallest i16 is -32768 and the biggest i16 is 32767.
The smallest u16 is 0 and the biggest u16 is 65535.
The smallest i32 is -2147483648 and the biggest i32 is 2147483647.
The smallest u32 is 0 and the biggest u32 is 4294967295.
The smallest i64 is -9223372036854775808 and the biggest i64 is 9223372036854775807.
The smallest u64 is 0 and the biggest u64 is 18446744073709551615.
The smallest i128 is -170141183460469231731687303715884105728 and the biggest i128 is 170141183460469231731687303715884105727.
The smallest u128 is 0 and the biggest u128 is 340282366920938463463374607431768211455.
```

## 可變性

當你用`let`聲明一個變量時，它是不可改變的(不能改變)。

這將無法工作:

```rust
fn main() {
    let my_number = 8;
    my_number = 10; // ⚠️
}
```

編譯器說:`error[E0384]: cannot assign twice to immutable variable my_number`。這是因為如果你只寫`let`，變量是不可變的。

但有時你想改變你的變量。要創建一個可以改變的變量，就在`let`後面加上`mut`。

```rust
fn main() {
    let mut my_number = 8;
    my_number = 10;
}
```

現在沒有問題了。

但是，你不能改變類型:甚至`mut`也不能讓你這樣做:這將無法工作。

```rust
fn main() {
    let mut my_variable = 8; // it is now an i32. That can't be changed
    my_variable = "Hello, world!"; // ⚠️
}
```

你會看到編譯器發出的同樣的 "預期"信息。`expected integer, found &str`. `&str`是一個字符串類型，我們很快就會知道。

### 遮蔽

shadowing是指使用`let`聲明一個與另一個變量同名的新變量。它看起來像可變性，但完全不同。shadowing看起來是這樣的:

```rust
fn main() {
    let my_number = 8; // This is an i32
    println!("{}", my_number); // prints 8
    let my_number = 9.2; // This is an f64 with the same name. But it's not the first my_number - it is completely different!
    println!("{}", my_number) // Prints 9.2
}
```

這裡我們說我們用一個新的 "let綁定"對`my_number`進行了 "shadowing"。

那麼第一個`my_number`是否被銷燬了呢？沒有，但是當我們調用`my_number`時，我們現在得到`my_number`的`f64`。因為它們在同一個作用域塊中(同一個 `{}`)，我們不能再看到第一個 `my_number`。

但如果它們在不同的塊中，我們可以同時看到兩個。
 例如:

```rust
fn main() {
    let my_number = 8; // This is an i32
    println!("{}", my_number); // prints 8
    {
        let my_number = 9.2; // This is an f64. It is not my_number - it is completely different!
        println!("{}", my_number) // Prints 9.2
                                  // But the shadowed my_number only lives until here.
                                  // The first my_number is still alive!
    }
    println!("{}", my_number); // prints 8
}
```

因此，當你對一個變量進行shadowing處理時，你不會破壞它。你**屏蔽**了它。

那麼shadowing的好處是什麼呢？當你需要經常改變一個變量的時候，shadowing是很好的。想象一下，你想用一個變量做很多簡單的數學運算。

```rust
fn times_two(number: i32) -> i32 {
    number * 2
}

fn main() {
    let final_number = {
        let y = 10;
        let x = 9; // x starts at 9
        let x = times_two(x); // shadow with new x: 18
        let x = x + y; // shadow with new x: 28
        x // return x: final_number is now the value of x
    };
    println!("The number is now: {}", final_number)
}
```

如果沒有shadowing，你將不得不考慮不同的名稱，儘管你並不關心x。

```rust
fn times_two(number: i32) -> i32 {
    number * 2
}

fn main() {
    // Pretending we are using Rust without shadowing
    let final_number = {
        let y = 10;
        let x = 9; // x starts at 9
        let x_twice = times_two(x); // second name for x
        let x_twice_and_y = x_twice + y; // third name for x!
        x_twice_and_y // too bad we didn't have shadowing - we could have just used x
    };
    println!("The number is now: {}", final_number)
}
```

一般來說，你在Rust中看到的shadowing就是這種情況。它發生在你想快速取用變量，對它做一些事情，然後再做其他事情的地方。而你通常將它用於那些你不太關心的快速變量。

## 棧、堆和指針

棧、堆和指針在Rust中非常重要。

棧和堆是計算機中保存內存的兩個地方。重要的區別是:

棧的速度非常快, 但堆的速度就不那麼快了. 它也不是超慢，但棧總是更快。但是你不能一直使用棧，因為:
- Rust需要在編譯時知道一個變量的大小。所以像`i32`這樣的簡單變量就放在堆棧上，因為我們知道它們的確切大小。你總是知道`i32`要4字節，因為32位=4字節。所以`i32`總是可以放在棧上。
- 但有些類型在編譯時不知道大小。但是棧需要知道確切的大小。那麼你該怎麼做呢？首先你把數據放在堆中，因為堆中可以有任何大小的數據。然後為了找到它，一個指針就會進入棧。這很好，因為我們總是知道指針的大小。所以，計算機就會先去棧，讀取指針，然後跟著指針到數據所在的堆。

指針聽起來很複雜，但它們很容易。指針就像一本書的目錄。想象一下這本書。

```text
MY BOOK

TABLE OF CONTENTS

Chapter                        Page
Chapter 1: My life              1
Chapter 2: My cat               15
Chapter 3: My job               23
Chapter 4: My family            30
Chapter 5: Future plans         43
```

所以這就像五個指針。你可以閱讀它們，找到它們所說的信息。"我的生活"這一章在哪裡？在第1頁(它*指向*第1頁)。"我的工作"這一章在哪裡？它在第23頁。

在Rust中通常看到的指針叫做**引用**。這是重要的部分，要知道:一個引用指向另一個值的內存。引用意味著你*借*了這個值，但你並不擁有它。這和我們的書一樣:目錄並不擁有信息。章節才是信息的主人。在Rust中，引用文獻的前面有一個`&`。所以:

- `let my_variable = 8`是一個普通的變量，但是:
- `let my_reference = &my_variable`是一個引用。

你把 `my_reference = &my_variable` 讀成這樣: "my_reference是對my_variable的引用". 或者:"my_reference是對my_variable的引用"。

這意味著`my_reference`只看`my_variable`的數據。`my_variable`仍然擁有它的數據。

你也可以有一個引用的引用，或者任何數量的引用。

```rust
fn main() {
    let my_number = 15; // This is an i32
    let single_reference = &my_number; //  This is a &i32
    let double_reference = &single_reference; // This is a &&i32
    let five_references = &&&&&my_number; // This is a &&&&&i32
}
```

這些都是不同的類型，就像 "朋友的朋友"和 "朋友"不同一樣。

## 關於打印的更多信息

在Rust中，你幾乎可以用任何你想要的方式打印東西。這裡有一些關於打印的事情需要知道。

添加 `\n` 將會產生一個新行，而 `\t` 將會產生一個標籤。

```rust
fn main() {
    // Note: this is print!, not println!
    print!("\t Start with a tab\nand move to a new line");
}
```

這樣就可以打印了。

```text
         Start with a tab
and move to a new line
```

`""`裡面可以寫過很多行都沒有問題，但是要注意間距。

```rust
fn main() {
    // Note: After the first line you have to start on the far left.
    // If you write directly under println!, it will add the spaces
    println!("Inside quotes
you can write over
many lines
and it will print just fine.");

    println!("If you forget to write
    on the left side, the spaces
    will be added when you print.");
}
```

這個打印出來的。

```text
Inside quotes
you can write over
many lines
and it will print just fine.
If you forget to write
    on the left side, the spaces
    will be added when you print.
```

如果你想打印`\n`這樣的字符(稱為 "轉義字符")，你可以多加一個`\`。

```rust
fn main() {
    println!("Here are two escape characters: \\n and \\t");
}
```

這樣就可以打印了。

```text
Here are two escape characters: \n and \t
```

有時你有太多的 `"` 和轉義字符，並希望 Rust 忽略所有的字符。要做到這一點，您可以在開頭添加 `r#`，在結尾添加 `#`。

```rust
fn main() {
    println!("He said, \"You can find the file at c:\\files\\my_documents\\file.txt.\" Then I found the file."); // We used \ five times here
    println!(r#"He said, "You can find the file at c:\files\my_documents\file.txt." Then I found the file."#)
}
```

這打印的是同樣的東西，但使用 `r#` 使人類更容易閱讀。

```text
He said, "You can find the file at c:\files\my_documents\file.txt." Then I found the file.
He said, "You can find the file at c:\files\my_documents\file.txt." Then I found the file.
```

如果你需要在裡面打印`#`，那麼你可以用`r##`開頭，用`##`結尾。如果你需要打印多個連續的`#`，可以在每邊多加一個#。

下面是四個例子。

```rust
fn main() {

    let my_string = "'Ice to see you,' he said."; // single quotes
    let quote_string = r#""Ice to see you," he said."#; // double quotes
    let hashtag_string = r##"The hashtag #IceToSeeYou had become very popular."##; // Has one # so we need at least ##
    let many_hashtags = r####""You don't have to type ### to use a hashtag. You can just use #.""####; // Has three ### so we need at least ####

    println!("{}\n{}\n{}\n{}\n", my_string, quote_string, hashtag_string, many_hashtags);

}
```

這將打印:

```text
'Ice to see you,' he said.
"Ice to see you," he said.
The hashtag #IceToSeeYou had become very popular.
"You don't have to type ### to use a hashtag. You can just use #."
```

`r#`還有另一個用途:使用它，你可以使用關鍵字(如`let`、`fn`等)作為變量名。

```rust
fn main() {
    let r#let = 6; // The variable's name is let
    let mut r#mut = 10; // This variable's name is mut
}
```

`r#`之所以有這個功能，是因為舊版本的Rust的關鍵字比現在的Rust少。所以有了`r#`就可以避免以前不是關鍵字的變量名的錯誤。

又或者因為某些原因，你*確實*需要一個函數的名字，比如`return`。那麼你可以這樣寫:

```rust
fn r#return() -> u8 {
    println!("Here is your number.");
    8
}

fn main() {
    let my_number = r#return();
    println!("{}", my_number);
}
```

這樣打印出來的結果是:

```text
Here is your number.
8
```

所以你可能不需要它，但是如果你真的需要為一個變量使用一個關鍵字，那麼你可以使用`r#`。



如果你想打印`&str`或`char`的字節，你可以在字符串前寫上`b`就可以了。這適用於所有ASCII字符。這些是所有的ASCII字符。

```text
☺☻♥♦♣♠♫☼►◄↕‼¶§▬↨↑↓→∟↔▲▼123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~
```

所以，當你打印這個

```rust
fn main() {
    println!("{:?}", b"This will look like numbers");
}
```

這就是結果:

```text
[84, 104, 105, 115, 32, 119, 105, 108, 108, 32, 108, 111, 111, 107, 32, 108, 105, 107, 101, 32, 110, 117, 109, 98, 101, 114, 115]
```

對於`char`來說，這叫做一個*字節*，對於`&str`來說，這叫做一個*字節字符串*。



如果你需要的話，也可以把`b`和`r`放在一起。

```rust
fn main() {
    println!("{:?}", br##"I like to write "#"."##);
}
```

這將打印出 `[73, 32, 108, 105, 107, 101, 32, 116, 111, 32, 119, 114, 105, 116, 101, 32, 34, 35, 34, 46]`。



還有一個Unicode轉義，可以讓你在字符串中打印任何Unicode字符: `\u{}`。`{}`裡面有一個十六進制數字可以打印。下面是一個簡短的例子，說明如何獲得Unicode數字，以及如何再次打印它。

```rust
fn main() {
    println!("{:X}", '행' as u32); // Cast char as u32 to get the hexadecimal value
    println!("{:X}", 'H' as u32);
    println!("{:X}", '居' as u32);
    println!("{:X}", 'い' as u32);

    println!("\u{D589}, \u{48}, \u{5C45}, \u{3044}"); // Try printing them with unicode escape \u
}
```



我們知道，`println!`可以和`{}`(用於顯示)或`{:?}`(用於調試)一起打印，再加上`{:#?}`就可以進行漂亮的打印。但是還有很多其他的打印方式。

例如，如果你有一個引用，你可以用`{:p}`來打印*指針地址*。指針地址指的是電腦內存中的位置。

```rust
fn main() {
    let number = 9;
    let number_ref = &number;
    println!("{:p}", number_ref);
}
```

這可以打印`0xe2bc0ffcfc`或其他地址。每次可能都不一樣，這取決於你的計算機存儲的位置。

或者你可以打印二進制、十六進制和八進制。

```rust
fn main() {
    let number = 555;
    println!("Binary: {:b}, hexadecimal: {:x}, octal: {:o}", number, number, number);
}
```

這將打印出`Binary: 1000101011, hexadecimal: 22b, octal: 1053`。

或者你可以添加數字來改變順序。第一個變量將在索引0中，下一個在索引1中，以此類推。

```rust
fn main() {
    let father_name = "Vlad";
    let son_name = "Adrian Fahrenheit";
    let family_name = "Țepeș";
    println!("This is {1} {2}, son of {0} {2}.", father_name, son_name, family_name);
}
```

`father_name`在0位，`son_name`在1位，`family_name`在2位。所以它打印的是`This is Adrian Fahrenheit Țepeș, son of Vlad Țepeș`。


也許你有一個非常複雜的字符串要打印，`{}`大括號內有太多的變量。或者你需要不止一次的打印一個變量。那麼在`{}`中添加名稱就會有幫助。

```rust
fn main() {
    println!(
        "{city1} is in {country} and {city2} is also in {country},
but {city3} is not in {country}.",
        city1 = "Seoul",
        city2 = "Busan",
        city3 = "Tokyo",
        country = "Korea"
    );
}
```

這樣就可以打印了。

```text
Seoul is in Korea and Busan is also in Korea,
but Tokyo is not in Korea.
```


如果你願意，也可以在Rust中進行非常複雜的打印。下面展示怎樣做：

{variable:padding alignment minimum.maximum}

要理解這一點，請看

1) 你想要一個變量名嗎？先寫出來，就像我們上面寫{country}一樣。
(如果你想做更多的事情，就在後面加一個`:`)
2) 你想要一個填充字符嗎？例如，55加上三個 "填充零"就像00055。
3) padding的對齊方式(左/中/右)？
4) 你想要一個最小長度嗎？(寫一個數字就可以了) 
5) 你想要一個最大長度嗎？(寫一個數字，前面有一個`.`)

例如，我想寫 "a"，左邊有五個ㅎ，右邊有五個ㅎ。

```rust
fn main() {
    let letter = "a";
    println!("{:ㅎ^11}", letter);
}
```

這樣打印出來的結果是`ㅎㅎㅎㅎㅎaㅎㅎㅎㅎㅎ`。我們看看1)到5)的這個情況，就能明白編譯器是怎麼解讀的：

- 你要不要變量名？`{:ㅎ^11}`沒有變量名。`:`之前沒有任何內容。
- 你需要一個填充字符嗎？`{:ㅎ^11}` 是的:ㅎ"在`:`後面，有一個`^`。`<`表示變量在填充字符左邊，`>`表示在填充字符右邊，`^`表示在填充字符中間。
- 要不要設置最小長度？`{:ㅎ^11}`是:後面有一個11。
- 你想要一個最大長度嗎？`{:ㅎ^11}` 不是:前面沒有`.`的數字。

下面是多種類型的格式化的例子:


```rust
fn main() {
    let title = "TODAY'S NEWS";
    println!("{:-^30}", title); // no variable name, pad with -, put in centre, 30 characters long
    let bar = "|";
    println!("{: <15}{: >15}", bar, bar); // no variable name, pad with space, 15 characters each, one to the left, one to the right
    let a = "SEOUL";
    let b = "TOKYO";
    println!("{city1:-<15}{city2:->15}", city1 = a, city2 = b); // variable names city1 and city2, pad with -, one to the left, one to the right
}
```

它打印出來了。

```text
---------TODAY'S NEWS---------
|                            |
SEOUL--------------------TOKYO
```

## 字符串

Rust有兩種主要類型的字符串。`String`和`&str`. 有什麼區別呢？

- `&str`是一個簡單的字符串。當你寫`let my_variable = "Hello, world!"`時，你會創建一個`&str`。`&str`是非常快的。
- `String`是一個更復雜的字符串。它比較慢，但它有更多的功能。`String`是一個指針，數據在堆上。

另外注意，`&str`前面有`&`，因為你需要一個引用來使用`str`。這是因為我們上面看到的原因:堆需要知道大小。所以我們給它一個`&`，它知道大小，然後它就高興了。另外，因為你用一個`&`與一個`str`交互，你並不擁有它。但是一個`String`是一個*擁有*的類型。我們很快就會知道為什麼這一點很重要。

`&str`和`String`都是UTF-8。例如，你可以寫

```rust
fn main() {
    let name = "서태지"; // This is a Korean name. No problem, because a &str is UTF-8.
    let other_name = String::from("Adrian Fahrenheit Țepeș"); // Ț and ș are no problem in UTF-8.
}
```

你可以在`String::from("Adrian Fahrenheit Țepeș")`中看到，很容易從`&str`中創建一個`String`。這兩種類型雖然不同，但聯繫非常緊密。

你甚至可以寫表情符號，這要感謝UTF-8。

```rust
fn main() {
    let name = "😂";
    println!("My name is actually {}", name);
}
```

在你的電腦上，會打印`My name is actually 😂`，除非你的命令行不能打印。那麼它會顯示`My name is actually �`。但Rust對emojis或其他Unicode沒有問題。

我們再來看看`str`使用`&`的原因，以確保我們理解。

- `str`是一個動態大小的類型(動態大小=大小可以不同)。比如 "서태지"和 "Adrian Fahrenheit Țepeș"這兩個名字的大小是不一樣的。

```rust
fn main() {

    println!("A String is always {:?} bytes. It is Sized.", std::mem::size_of::<String>()); // std::mem::size_of::<Type>() gives you the size in bytes of a type
    println!("And an i8 is always {:?} bytes. It is Sized.", std::mem::size_of::<i8>());
    println!("And an f64 is always {:?} bytes. It is Sized.", std::mem::size_of::<f64>());
    println!("But a &str? It can be anything. '서태지' is {:?} bytes. It is not Sized.", std::mem::size_of_val("서태지")); // std::mem::size_of_val() gives you the size in bytes of a variable
    println!("And 'Adrian Fahrenheit Țepeș' is {:?} bytes. It is not Sized.", std::mem::size_of_val("Adrian Fahrenheit Țepeș"));
}
```

這個打印:

```text
A String is always 24 bytes. It is Sized.
And an i8 is always 1 bytes. It is Sized.
And an f64 is always 8 bytes. It is Sized.
But a &str? It can be anything. '서태지' is 9 bytes. It is not Sized.
And 'Adrian Fahrenheit Țepeș' is 25 bytes. It is not Sized.
```

這就是為什麼我們需要一個 &，因為 `&` 是一個指針，而 Rust 知道指針的大小。所以指針會放在棧中。如果我們寫`str`，Rust就不知道該怎麼做了，因為它不知道指針的大小。



有很多方法可以創建`String`。下面是一些。

- `String::from("This is the string text");` 這是String的一個方法，它接受文本並創建一個String.
- `"This is the string text".to_string()`. 這是&str的一個方法，使其成為一個String。
- `format!` 宏。
 這和`println!`一樣，只是它創建了一個字符串，而不是打印。所以你可以這樣做:

```rust
fn main() {
    let my_name = "Billybrobby";
    let my_country = "USA";
    let my_home = "Korea";

    let together = format!(
        "I am {} and I come from {} but I live in {}.",
        my_name, my_country, my_home
    );
}
```

現在我們有了一個一起命名的字符串，但還沒有打印出來。

還有一種創建String的方法叫做`.into()`，但它有點不同，因為`.into()`並不只是用來創建`String`。有些類型可以很容易地使用`From`和`.into()`轉換為另一種類型，並從另一種類型轉換出來。而如果你有`From`，那麼你也有`.into()`。`From` 更加清晰，因為你已經知道了類型:你知道 `String::from("Some str")` 是一個來自 `&str` 的 `String`。但是對於`.into()`，有時候編譯器並不知道。

```rust
fn main() {
    let my_string = "Try to make this a String".into(); // ⚠️
}
```

Rust不知道你要的是什麼類型，因為很多類型都可以從一個`&str`創建出來。它說:"我可以把一個&str做成很多東西。你想要哪一種？"

```text
error[E0282]: type annotations needed
 --> src\main.rs:2:9
  |
2 |     let my_string = "Try to make this a String".into();
  |         ^^^^^^^^^ consider giving `my_string` a type
```

所以你可以這樣做:

```rust
fn main() {
    let my_string: String = "Try to make this a String".into();
}
```

現在你得到了一個字符串。

## const和static

有兩種聲明值的方法，不僅僅是用`let`。它們是`const`和`static`。另外，Rust不會使用類型推理：你需要為它們編寫類型。這些都是用於不改變的值（`const`意味著常量）。區別在於:

- `const`是用於不改變的值，當使用它時，名字會被替換成值。
- `static`與`const`類似，但有一個固定的內存位置，可以作為一個全局變量使用。

所以它們幾乎是一樣的。Rust程序員幾乎總是使用`const`。

一般用全大寫字母作為名字，而且通常在`main`之外，這樣它們就可以在整個程序中生存。

兩個例子是 `const NUMBER_OF_MONTHS: u32 = 12;` 和 `static SEASONS: [&str; 4] = ["Spring", "Summer", "Fall", "Winter"];`

## 關於引用的更多信息

引用在Rust中非常重要。Rust使用引用來確保所有的內存訪問是安全的。我們知道，我們使用`&`來創建一個引用。

```rust
fn main() {
    let country = String::from("Austria");
    let ref_one = &country;
    let ref_two = &country;

    println!("{}", ref_one);
}
```

這樣就會打印出`Austria`。

在代碼中，`country`是一個`String`。然後我們創建了兩個`country`的引用。它們的類型是`&String`，你說這是一個 "字符串的引用"。我們可以創建三個引用或者一百個對 `country` 的引用，這都沒有問題。

但這是一個問題。

```rust
fn return_str() -> &str {
    let country = String::from("Austria");
    let country_ref = &country;
    country_ref // ⚠️
}

fn main() {
    let country = return_str();
}
```

`return_str()`函數創建了一個String，然後它創建了一個對String的引用。然後它試圖返回引用。但是`country`這個String只活在函數裡面，然後它就死了。一旦一個變量消失了，計算機就會清理內存，並將其用於其他用途。所以在函數結束後，`country_ref`引用的是已經消失的內存，這是不對的。Rust防止我們在這裡犯內存的錯誤。

這就是我們上面講到的 "擁有"類型的重要部分。因為你擁有一個`String`，你可以把它傳給別人。但是如果 `&String` 的 `String` 死了，那麼 `&String` 就會死掉，所以你不能把它的 "所有權"傳給別人。

## 可變引用

如果您想使用一個引用來改變數據，您可以使用一個可變引用。對於可變引用，您可以寫 `&mut` 而不是 `&`。

```rust
fn main() {
    let mut my_number = 8; // don't forget to write mut here!
    let num_ref = &mut my_number;
}
```

那麼這兩種類型是什麼呢？`my_number`是`i32`，`num_ref`是`&mut i32`(我們說是 "可變引用`i32`")。

所以我們用它來給my_number加10。但是你不能寫`num_ref += 10`，因為`num_ref`不是`i32`的值，它是一個`&i32`。其實這個值就在`i32`裡面。為了達到值所在的地方，我們用`*`。`*`的意思是 "我不要引用，我要引用對應的值"。換句話說，一個`*`與`&`是相反的。另外，一個`*`抹去了一個`&`。

```rust
fn main() {
    let mut my_number = 8;
    let num_ref = &mut my_number;
    *num_ref += 10; // Use * to change the i32 value.
    println!("{}", my_number);

    let second_number = 800;
    let triple_reference = &&&second_number;
    println!("Second_number = triple_reference? {}", second_number == ***triple_reference);
}
```

這個打印:

```text
18
Second_number = triple_reference? true
```

因為使用`&`叫做 "引用"，所以使用`*`叫做 "**de**referencing"。

Rust有兩個規則，分別是可變引用和不可變引用。它們非常重要，但也很容易記住，因為它們很有意義。

- **規則1**。如果你只有不可變引用，你可以有任意多的引用。1個也行，3個也行，1000個也行，沒問題。
- **規則2**: 如果你有一個可變引用，你只能有一個。另外，你不能同時使用一個不可變引用**和**一個可變引用。

這是因為可變引用可以改變數據。如果你在其他引用讀取數據時改變數據，你可能會遇到問題。


一個很好的理解方式是思考一個Powerpoint演示。

情況一是關於**只有一個可變引用**

情境一 一個員工正在編寫一個Powerpoint演示文稿，他希望他的經理能幫助他。他希望他的經理能幫助他。該員工將自己的登錄信息提供給經理，並請他幫忙進行編輯。現在，經理對該員工的演示文稿有了一個 "可變引用"。經理可以做任何他想做的修改，然後把電腦還給他。這很好，因為沒有人在看這個演示文稿。

情況二是關於**只有不可變引用**

情況二 該員工要給100個人做演示。現在這100個人都可以看到該員工的數據。
 他們都有一個 "不可改變的引用"，即員工的介紹。這很好，因為他們可以看到它，但沒有人可以改變數據。

情況三是**有問題的情況**

情況三 員工把他的登錄信息給了經理 他的經理現在有了一個 "可變引用"。然後員工去給100個人做演示，但是經理還是可以登錄。這是不對的，因為經理可以登錄，可以做任何事情。也許他的經理會登錄電腦，然後開始給他的母親打一封郵件! 現在這100人不得不看著經理給他母親寫郵件，而不是演示。這不是他們期望看到的。

下面是一個可變借用與不可變借用的例子:

```rust
fn main() {
    let mut number = 10;
    let number_ref = &number;
    let number_change = &mut number;
    *number_change += 10;
    println!("{}", number_ref); // ⚠️
}
```

編譯器打印了一個有用的信息來告訴我們問題所在。

```text
error[E0502]: cannot borrow `number` as mutable because it is also borrowed as immutable
 --> src\main.rs:4:25
  |
3 |     let number_ref = &number;
  |                      ------- immutable borrow occurs here
4 |     let number_change = &mut number;
  |                         ^^^^^^^^^^^ mutable borrow occurs here
5 |     *number_change += 10;
6 |     println!("{}", number_ref);
  |                    ---------- immutable borrow later used here
```

然而，這段代碼可以工作。為什麼會這樣？

```rust
fn main() {
    let mut number = 10;
    let number_change = &mut number; // create a mutable reference
    *number_change += 10; // use mutable reference to add 10
    let number_ref = &number; // create an immutable reference
    println!("{}", number_ref); // print the immutable reference
}
```

它打印出`20`沒有問題。它能工作是因為編譯器足夠聰明，能夠理解我們的代碼。它知道我們使用了`number_change`來改變`number`，但沒有再使用它。所以這裡沒有問題。我們並沒有將不可變和可變引用一起使用。

早期在Rust中，這種代碼實際上會產生錯誤，但現在的編譯器更聰明瞭。它不僅能理解我們輸入的內容，還能理解我們如何使用所有的東西。

### 再談shadowing

還記得我們說過，shadowing不會**破壞**一個值，而是**屏蔽**它嗎？現在我們可以用引用來看看這個問題。

```rust
fn main() {
    let country = String::from("Austria");
    let country_ref = &country;
    let country = 8;
    println!("{}, {}", country_ref, country);
}
```

這是打印`Austria, 8`還是`8, 8`？它打印的是`Austria, 8`。首先我們聲明一個`String`，叫做`country`。然後我們給這個字符串創建一個引用`country_ref`。然後我們用8來shadowing國家，這是一個`i32`。但是第一個`country`並沒有被銷燬，所以`country_ref`仍然寫著 "Austria"，而不是 "8"。下面是同樣的代碼，並加了一些註釋來說明它的工作原理。

```rust
fn main() {
    let country = String::from("Austria"); // Now we have a String called country
    let country_ref = &country; // country_ref is a reference to this data. It's not going to change
    let country = 8; // Now we have a variable called country that is an i8. But it has no relation to the other one, or to country_ref
    println!("{}, {}", country_ref, country); // country_ref still refers to the data of String::from("Austria") that we gave it.
}
```

## 函數的引用

引用對函數非常有用。Rust中關於值的規則是:一個值只能有一個所有者。

這段代碼將無法工作:

```rust
fn print_country(country_name: String) {
    println!("{}", country_name);
}

fn main() {
    let country = String::from("Austria");
    print_country(country); // We print "Austria"
    print_country(country); // ⚠️ That was fun, let's do it again!
}
```

它不能工作，因為`country`被破壞了。下面是如何操作的。

- 第一步，我們創建`String`，稱為`country`。`country`是所有者。
- 第二步:我們把`country`給`print_country`。`print_country`沒有`->`，所以它不返回任何東西。`print_country`完成後，我們的`String`現在已經死了。
- 第三步:我們嘗試把`country`給`print_country`，但我們已經這樣做了。我們已經沒有`country`可以給了。

我們可以讓`print_country`給`String`回來，但是有點尷尬。

```rust
fn print_country(country_name: String) -> String {
    println!("{}", country_name);
    country_name // return it here
}

fn main() {
    let country = String::from("Austria");
    let country = print_country(country); // we have to use let here now to get the String back
    print_country(country);
}
```

現在打印出來了。

```text
Austria
Austria
```

更好的解決方法是增加`&`。

```rust
fn print_country(country_name: &String) {
    println!("{}", country_name);
}

fn main() {
    let country = String::from("Austria");
    print_country(&country); // We print "Austria"
    print_country(&country); // That was fun, let's do it again!
}
```

現在 `print_country()` 是一個函數，它接受 `String` 的引用: `&String`。另外，我們給country一個引用，寫作`&country`。這表示 "你可以看它，但我要保留它"。

現在讓我們用一個可變引用來做類似的事情。下面是一個使用可變變量的函數的例子:

```rust
fn add_hungary(country_name: &mut String) { // first we say that the function takes a mutable reference
    country_name.push_str("-Hungary"); // push_str() adds a &str to a String
    println!("Now it says: {}", country_name);
}

fn main() {
    let mut country = String::from("Austria");
    add_hungary(&mut country); // we also need to give it a mutable reference.
}
```

此打印`Now it says: Austria-Hungary`。

所以得出結論:

- `fn function_name(variable: String)`接收了`String`，並擁有它。如果它不返回任何東西，那麼這個變量就會在函數裡面死亡。
- `fn function_name(variable: &String)` 借用 `String` 並可以查看它
- `fn function_name(variable: &mut String)`借用`String`，可以更改。

下面是一個看起來像可變引用的例子，但它是不同的。

```rust
fn main() {
    let country = String::from("Austria"); // country is not mutable, but we are going to print Austria-Hungary. How?
    adds_hungary(country);
}

fn adds_hungary(mut country: String) { // Here's how: adds_hungary takes the String and declares it mutable!
    country.push_str("-Hungary");
    println!("{}", country);
}
```

這怎麼可能呢？因為`mut country`不是引用。`adds_hungary`現在擁有`country`。(記住，它佔用的是`String`而不是`&String`)。當你調用`adds_hungary`的那一刻，它就完全成了country的主人。`country`與`String::from("Austria")`沒有關係了。所以，`adds_hungary`可以把`country`當作可變的，這樣做是完全安全的。

還記得我們上面的員工Powerpoint和經理的情況嗎？在這種情況下，就好比員工只是把自己的整臺電腦交給了經理。員工不會再碰它，所以經理可以對它做任何他想做的事情。

## 拷貝類型

Rust中的一些類型非常簡單。它們被稱為**拷貝類型**。這些簡單的類型都在棧中，編譯器知道它們的大小。這意味著它們非常容易複製，所以當你把它發送到一個函數時，編譯器總是會複製。它總是複製，因為它們是如此的小而簡單，沒有理由不復制。所以你不需要擔心這些類型的所有權問題。

這些簡單的類型包括:整數、浮點數、布爾值(`true`和`false`)和`char`。

如何知道一個類型是否**實現**複製？(實現 = 能夠使用)你可以查看文檔。例如，這裡是 char 的文檔:

[https://doc.rust-lang.org/std/primitive.char.html](https://doc.rust-lang.org/std/primitive.char.html)

在左邊你可以看到**Trait Implementations**。例如你可以看到**Copy**, **Debug**, 和 **Display**。所以你知道，當你把一個`char`:

- 當你把它發送到一個函數(**Copy**)時，它就被複制了。
- 可以用`{}`打印(**Display**)
- 可以用`{:?}`打印(**Debug**)

```rust
fn prints_number(number: i32) { // There is no -> so it's not returning anything
                             // If number was not copy type, it would take it
                             // and we couldn't use it again
    println!("{}", number);
}

fn main() {
    let my_number = 8;
    prints_number(my_number); // Prints 8. prints_number gets a copy of my_number
    prints_number(my_number); // Prints 8 again.
                              // No problem, because my_number is copy type!
}
```

但是如果你看一下String的文檔，它不是拷貝類型。

[https://doc.rust-lang.org/std/string/struct.String.html](https://doc.rust-lang.org/std/string/struct.String.html)

在左邊的**Trait Implementations**中，你可以按字母順序查找。A、B、C......C中沒有**Copy**，但是有**Clone**。**Clone**和**Copy**類似，但通常需要更多的內存。另外，你必須用`.clone()`來調用它--它不會自己克隆。

在這個例子中，`prints_country()`打印的是國家名稱，一個`String`。我們想打印兩次，但我們不能。

```rust
fn prints_country(country_name: String) {
    println!("{}", country_name);
}

fn main() {
    let country = String::from("Kiribati");
    prints_country(country);
    prints_country(country); // ⚠️
}
```

但現在我們明白了這個信息。

```text
error[E0382]: use of moved value: `country`
 --> src\main.rs:4:20
  |
2 |     let country = String::from("Kiribati");
  |         ------- move occurs because `country` has type `std::string::String`, which does not implement the `Copy` trait
3 |     prints_country(country);
  |                    ------- value moved here
4 |     prints_country(country);
  |                    ^^^^^^^ value used here after move
```

重要的部分是`which does not implement the Copy trait`。但是在文檔中我們看到String實現了`Clone`的特性。所以我們可以在代碼中添加`.clone()`。這樣就創建了一個克隆，然後我們將克隆發送到函數中。現在 `country` 還活著，所以我們可以使用它。

```rust
fn prints_country(country_name: String) {
    println!("{}", country_name);
}

fn main() {
    let country = String::from("Kiribati");
    prints_country(country.clone()); // make a clone and give it to the function. Only the clone goes in, and country is still alive
    prints_country(country);
}
```

當然，如果`String`非常大，`.clone()`就會佔用很多內存。一個`String`可以是一整本書的長度，我們每次調用`.clone()`都會複製這本書。所以，如果可以的話，使用`&`來做引用是比較快的。例如，這段代碼將`&str`推送到`String`上，然後每次在函數中使用時都會進行克隆。

```rust
fn get_length(input: String) { // Takes ownership of a String
    println!("It's {} words long.", input.split_whitespace().count()); // splits to count the number of words
}

fn main() {
    let mut my_string = String::new();
    for _ in 0..50 {
        my_string.push_str("Here are some more words "); // push the words on
        get_length(my_string.clone()); // gives it a clone every time
    }
}
```

它的打印。

```text
It's 5 words long.
It's 10 words long.
...
It's 250 words long.
```

這就是50個克隆。這裡是用引用代替更好:

```rust
fn get_length(input: &String) {
    println!("It's {} words long.", input.split_whitespace().count());
}

fn main() {
    let mut my_string = String::new();
    for _ in 0..50 {
        my_string.push_str("Here are some more words ");
        get_length(&my_string);
    }
}
```

不是50個克隆，而是0個。



### 無值變量

一個沒有值的變量叫做 "未初始化"變量。未初始化的意思是 "還沒有開始"。它們很簡單:只需寫上`let`和變量名。

```rust
fn main() {
    let my_variable; // ⚠️
}
```

但是你還不能使用它，如果任何東西都沒有被初始化，Rust就不會編譯。

但有時它們會很有用。一個很好的例子是當:

- 你有一個代碼塊，而你的變量值就在裡面，並且
- 變量需要活在代碼塊之外。

```rust
fn loop_then_return(mut counter: i32) -> i32 {
    loop {
        counter += 1;
        if counter % 50 == 0 {
            break;
        }
    }
    counter
}

fn main() {
    let my_number;

    {
        // Pretend we need to have this code block
        let number = {
            // Pretend there is code here to make a number
            // Lots of code, and finally:
            57
        };

        my_number = loop_then_return(number);
    }

    println!("{}", my_number);
}
```

這將打印出 `100`。

你可以看到 `my_number` 是在 `main()` 函數中聲明的，所以它一直活到最後。但是它的值是在循環裡面得到的。然而，這個值和`my_number`一樣長，因為`my_number`有這個值。而如果你在塊裡面寫了`let my_number = loop_then_return(number)`，它就會馬上死掉。

如果你簡化代碼，對想象是有幫助的。`loop_then_return(number)`給出的結果是100，所以我們刪除它，改寫`100`。另外，現在我們不需要 `number`，所以我們也刪除它。現在它看起來像這樣:

```rust
fn main() {
    let my_number;
    {
        my_number = 100;
    }

    println!("{}", my_number);
}
```

所以說`let my_number = { 100 };`差不多。

另外注意，`my_number`不是`mut`。我們在給它50之前並沒有給它一個值，所以它的值一直沒有改變。最後，`my_number`的真正代碼只是`let my_number = 100;`。

## 集合類型

Rust有很多類型用於創建集合。當你需要在一個地方有多個值時，就可以使用集合。例如，你可以在一個變量中包含你所在國家的所有城市的信息。我們先從數組開始，數組的速度最快，但功能也最少。它們在這方面有點像`&str`。

### 數組

數組是方括號內的數據。`[]`. 數組:

- 不能改變其大小。
- 必須只包含相同的類型。

但是，它們的速度非常快。

數組的類型是:`[type; number]`。例如，`["One", "Two"]`的類型是`[&str; 2]`。這意味著，即使這兩個數組也有不同的類型。

```rust
fn main() {
    let array1 = ["One", "Two"]; // This one is type [&str; 2]
    let array2 = ["One", "Two", "Five"]; // But this one is type [&str; 3]. Different type!
}
```

這裡有一個很好的提示:要想知道一個變量的類型，你可以通過給編譯器下壞指令來 "詢問"它。比如說

```rust
fn main() {
    let seasons = ["Spring", "Summer", "Autumn", "Winter"];
    let seasons2 = ["Spring", "Summer", "Fall", "Autumn", "Winter"];
    seasons.ddd(); // ⚠️
    seasons2.thd(); // ⚠️ as well
}
```

編譯器說:"什麼？seasons沒有`.ddd()`的方法，seasons2也沒有`.thd()`的方法！！"你可以看到:

```text
error[E0599]: no method named `ddd` found for array `[&str; 4]` in the current scope
 --> src\main.rs:4:13
  |
4 |     seasons.ddd(); // 
  |             ^^^ method not found in `[&str; 4]`

error[E0599]: no method named `thd` found for array `[&str; 5]` in the current scope
 --> src\main.rs:5:14
  |
5 |     seasons2.thd(); // 
  |              ^^^ method not found in `[&str; 5]`
```

所以它告訴你`` method not found in `[&str; 4]` ``，這就是類型。

如果你想要一個數值都一樣的數組，你可以這樣聲明。

```rust
fn main() {
    let my_array = ["a"; 10];
    println!("{:?}", my_array);
}
```

這樣就打印出了`["a", "a", "a", "a", "a", "a", "a", "a", "a", "a"]`。

這個方法經常用來創建緩衝區。例如，`let mut buffer = [0; 640]`創建一個640個零的數組。然後我們可以將零改為其他數字，以便添加數據。

你可以用[]來索引(獲取)數組中的條目。第一個條目是[0]，第二個是[1]，以此類推。

```rust
fn main() {
    let my_numbers = [0, 10, -20];
    println!("{}", my_numbers[1]); // prints 10
}
```

你可以得到一個數組的一個片斷(一塊)。首先你需要一個&，因為編譯器不知道大小。然後你可以使用`..`來顯示範圍。

例如，讓我們使用這個數組。`[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`.

```rust
fn main() {
    let array_of_ten = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

    let three_to_five = &array_of_ten[2..5];
    let start_at_two = &array_of_ten[1..];
    let end_at_five = &array_of_ten[..5];
    let everything = &array_of_ten[..];

    println!("Three to five: {:?}, start at two: {:?}, end at five: {:?}, everything: {:?}", three_to_five, start_at_two, end_at_five, everything);
}
```

記住這一點。

- 索引號從0開始(不是1)
- 索引範圍是**不包含的**(不包括最後一個數字)。

所以`[0..2]`是指第一個指數和第二個指數(0和1)。或者你也可以稱它為 "零點和第一"指數。它沒有第三項，也就是索引2。

你也可以有一個**包含的**範圍，這意味著它也包括最後一個數字。要做到這一點。
 添加`=`，寫成`..=`，而不是`..`。所以，如果你想要第一項、第二項和第三項，可以寫成`[0..=2]`，而不是`[0..2]`。

## 向量

就像我們有`&str`和`String`一樣，我們有數組和向量。數組的功能少了就快，向量的功能多了就慢。(當然，Rust的速度一直都是非常快的，所以向量並不慢，只是比數組慢*一點*)。類型寫成`Vec`，你也可以直接叫它 "vec"。

向量的聲明主要有兩種方式。一種是像`String`一樣使用`new`:

```rust
fn main() {
    let name1 = String::from("Windy");
    let name2 = String::from("Gomesy");

    let mut my_vec = Vec::new();
    // If we run the program now, the compiler will give an error.
    // It doesn't know the type of vec.

    my_vec.push(name1); // Now it knows: it's Vec<String>
    my_vec.push(name2);
}
```

你可以看到`Vec`裡面總是有其他東西，這就是`<>`(角括號)的作用。`Vec<String>`是一個有一個或多個`String`的向量。你還可以在裡面有更多的類型。比如說

- `Vec<(i32, i32)>` 這是一個 `Vec` 其中每個元素是一個元組。`(i32, i32)`.
- `Vec<Vec<String>>`這是一個`Vec`，其中有`Vec`的`Strings`。比如說你想把你喜歡的書保存為`Vec<String>`。然後你再用另一本書來做，就會得到另一個`Vec<String>`。為了保存這兩本書，你會把它們放入另一個`Vec`中，這就是`Vec<Vec<String>>`。

與其使用 `.push()` 讓 Rust 決定類型，不如直接聲明類型。

```rust
fn main() {
    let mut my_vec: Vec<String> = Vec::new(); // The compiler knows the type
                                              // so there is no error.
}
```

你可以看到，向量中的元素必須具有相同的類型。

另一個創建向量的簡單方法是使用 `vec!` 宏。它看起來像一個數組聲明，但前面有 `vec!`。

```rust
fn main() {
    let mut my_vec = vec![8, 10, 10];
}
```

類型是`Vec<i32>`。你稱它為 "i32的Vec"。而`Vec<String>`是 "String的Vec"。`Vec<Vec<String>>`是 "String的Vec的Vec"。

你也可以對一個向量進行分片，就像在數組中一樣。

```rust
fn main() {
    let vec_of_ten = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    // Everything is the same as above except we added vec!.
    let three_to_five = &vec_of_ten[2..5];
    let start_at_two = &vec_of_ten[1..];
    let end_at_five = &vec_of_ten[..5];
    let everything = &vec_of_ten[..];

    println!("Three to five: {:?},
start at two: {:?}
end at five: {:?}
everything: {:?}", three_to_five, start_at_two, end_at_five, everything);
}
```

因為Vector比數組慢，我們可以用一些方法讓它更快。一個vec有一個**容量**，也就是給向量的空間。當你在向量上推送一個新的元素時，它會越來越接近容量。然後，如果你超過了容量，它將使其容量翻倍，並將元素複製到新的空間。這就是所謂的重新分配。我們將使用一種名為`.capacity()`的方法來查看向量的容量，在我們向它添加元素時。

例如，我們將使用名為`.capacity()`的方法來觀察一個向量的容量。

```rust
fn main() {
    let mut num_vec = Vec::new();
    println!("{}", num_vec.capacity()); // 0 elements: prints 0
    num_vec.push('a'); // add one character
    println!("{}", num_vec.capacity()); // 1 element: prints 4. Vecs with 1 item always start with capacity 4
    num_vec.push('a'); // add one more
    num_vec.push('a'); // add one more
    num_vec.push('a'); // add one more
    println!("{}", num_vec.capacity()); // 4 elements: still prints 4.
    num_vec.push('a'); // add one more
    println!("{}", num_vec.capacity()); // prints 8. We have 5 elements, but it doubled 4 to 8 to make space
}
```

這個打印:

```text
0
4
4
8
```

所以這個向量有兩次重分配: 0到4，4到8。我們可以讓它更快:

```rust
fn main() {
    let mut num_vec = Vec::with_capacity(8); // Give it capacity 8
    num_vec.push('a'); // add one character
    println!("{}", num_vec.capacity()); // prints 8
    num_vec.push('a'); // add one more
    println!("{}", num_vec.capacity()); // prints 8
    num_vec.push('a'); // add one more
    println!("{}", num_vec.capacity()); // prints 8.
    num_vec.push('a'); // add one more
    num_vec.push('a'); // add one more // Now we have 5 elements
    println!("{}", num_vec.capacity()); // Still 8
}
```

這個向量有0個重分配，這是比較好的。所以如果你認為你知道你需要多少元素，你可以使用`Vec::with_capacity()`來使它更快。

你記得你可以用`.into()`把`&str`變成`String`。你也可以用它把一個數組變成`Vec`。你必須告訴 `.into()` 你想要一個 `Vec`，但你不必選擇 `Vec` 的類型。如果你不想選擇，你可以寫`Vec<_>`。

```rust
fn main() {
    let my_vec: Vec<u8> = [1, 2, 3].into();
    let my_vec2: Vec<_> = [9, 0, 10].into(); // Vec<_> means "choose the Vec type for me"
                                             // Rust will choose Vec<i32>
}
```

## 元組

Rust中的元組使用`()`。我們已經見過很多空元組了，因為函數中的*nothing*實際上意味著一個空元組。

```text
fn do_something() {}
```

其實是它的簡寫:

```text
fn do_something() -> () {}
```

這個函數什麼也得不到(一個空元組)，也不返回什麼(一個空元組)。所以我們已經經常使用元組了。當你在一個函數中不返回任何東西時，你實際上返回的是一個空元組。

```rust
fn just_prints() {
    println!("I am printing"); // Adding ; means we return an empty tuple
}

fn main() {}
```

但是元組可以容納很多東西，也可以容納不同的類型。元組裡面的元素也是用數字0、1、2等來做索引的，但要訪問它們，你要用`.`而不是`[]`。讓我們把一大堆類型放到一個元組中。

```rust
fn main() {
    let random_tuple = ("Here is a name", 8, vec!['a'], 'b', [8, 9, 10], 7.7);
    println!(
        "Inside the tuple is: First item: {:?}
Second item: {:?}
Third item: {:?}
Fourth item: {:?}
Fifth item: {:?}
Sixth item: {:?}",
        random_tuple.0,
        random_tuple.1,
        random_tuple.2,
        random_tuple.3,
        random_tuple.4,
        random_tuple.5,
    )
}
```

這個打印:

```text
Inside the tuple is: First item: "Here is a name"
Second item: 8
Third item: ['a']
Fourth item: 'b'
Fifth item: [8, 9, 10]
Sixth item: 7.7
```

這個元組的類型是 `(&str, i32, Vec<char>, char, [i32; 3], f64)`。


你可以使用一個元組來創建多個變量。看看這段代碼。

```rust
fn main() {
    let str_vec = vec!["one", "two", "three"];
}
```

`str_vec`裡面有三個元素。如果我們想把它們拉出來呢？這時我們可以使用元組。

```rust
fn main() {
    let str_vec = vec!["one", "two", "three"];

    let (a, b, c) = (str_vec[0], str_vec[1], str_vec[2]); // call them a, b, and c
    println!("{:?}", b);
}
```

這就打印出`"two"`，也就是`b`。這就是所謂的*解構*。這是因為首先變量是在結構體裡面的，但是我們又做了`a`、`b`、`c`這些不是在結構體裡面的變量。

如果你需要解構，但又不想要所有的變量，你可以使用`_`。

```rust
fn main() {
    let str_vec = vec!["one", "two", "three"];

    let (_, _, variable) = (str_vec[0], str_vec[1], str_vec[2]);
}
```

現在它只創建了一個叫`variable`的變量，但沒有為其他值做變量。

還有很多集合類型，還有很多使用數組、vec和tuple的方法。我們也將學習更多關於它們的知識，但首先我們將學習控制流。

## 控制流

控制流的意思是告訴你的代碼在不同的情況下該怎麼做。最簡單的控制流是`if`。

```rust
fn main() {
    let my_number = 5;
    if my_number == 7 {
        println!("It's seven");
    }
}
```

另外注意，你用的是`==`而不是`=`。`==`是用來比較的，`=`是用來*賦值*的(給一個值)。另外注意，我們寫的是`if my_number == 7`而不是`if (my_number == 7)`。在Rust中，你不需要用`if`的括號。

`else if`和`else`給你更多的控制:

```rust
fn main() {
    let my_number = 5;
    if my_number == 7 {
        println!("It's seven");
    } else if my_number == 6 {
        println!("It's six")
    } else {
        println!("It's a different number")
    }
}
```

這打印出`It's a different number`，因為它不等於7或6。


您可以使用 `&&`(和)和 `||`(或)添加更多條件。

```rust
fn main() {
    let my_number = 5;
    if my_number % 2 == 1 && my_number > 0 { // % 2 means the number that remains after diving by two
        println!("It's a positive odd number");
    } else if my_number == 6 {
        println!("It's six")
    } else {
        println!("It's a different number")
    }
}
```

這打印出的是`It's a positive odd number`，因為當你把它除以2時，你有一個1的餘數，它大於0。


你可以看到，過多的`if`、`else`和`else if`會很難讀。在這種情況下，你可以使用`match`來代替，它看起來更乾淨。但是您必須為每一個可能的結果進行匹配。例如，這將無法工作:

```rust
fn main() {
    let my_number: u8 = 5;
    match my_number {
        0 => println!("it's zero"),
        1 => println!("it's one"),
        2 => println!("it's two"),
        // ⚠️
    }
}
```

編譯器說:

```text
error[E0004]: non-exhaustive patterns: `3u8..=std::u8::MAX` not covered
 --> src\main.rs:3:11
  |
3 |     match my_number {
  |           ^^^^^^^^^ pattern `3u8..=std::u8::MAX` not covered
```

這就意味著 "你告訴我0到2，但`u8`可以到255。那3呢？那4呢？5呢？" 以此類推。所以你可以加上`_`，意思是 "其他任何東西"。

```rust
fn main() {
    let my_number: u8 = 5;
    match my_number {
        0 => println!("it's zero"),
        1 => println!("it's one"),
        2 => println!("it's two"),
        _ => println!("It's some other number"),
    }
}
```

那打印`It's some other number`。

記住匹配的規則:

- 你寫下`match`，然後創建一個`{}`的代碼塊。
- 在左邊寫上*模式*，用`=>`胖箭頭說明匹配時該怎麼做。
- 每一行稱為一個 "arm"。
- 在arm之間放一個逗號(不是分號)。

你可以用匹配來聲明一個值。

```rust
fn main() {
    let my_number = 5;
    let second_number = match my_number {
        0 => 0,
        5 => 10,
        _ => 2,
    };
}
```

`second_number`將是10。你看到最後的分號了嗎？那是因為，在match結束後，我們實際上告訴了編譯器這個信息:`let second_number = 10;`


你也可以在更復雜的事情上進行匹配。你用一個元組來做。

```rust
fn main() {
    let sky = "cloudy";
    let temperature = "warm";

    match (sky, temperature) {
        ("cloudy", "cold") => println!("It's dark and unpleasant today"),
        ("clear", "warm") => println!("It's a nice day"),
        ("cloudy", "warm") => println!("It's dark but not bad"),
        _ => println!("Not sure what the weather is."),
    }
}
```

這打印了`It's dark but not bad`，因為它與`sky`和`temperature`的 "多雲"和 "溫暖"相匹配。

你甚至可以把`if`放在`match`裡面。這就是所謂的 "match guard"。

```rust
fn main() {
    let children = 5;
    let married = true;

    match (children, married) {
        (children, married) if married == false => println!("Not married with {} children", children),
        (children, married) if children == 0 && married == true => println!("Married but no children"),
        _ => println!("Married? {}. Number of children: {}.", married, children),
    }
}
```

這將打印`Married? true. Number of children: 5.`

在一次匹配中，你可以隨意使用 _ 。在這個關於顏色的匹配中，我們有三個顏色，但一次只能選中一個。

```rust
fn match_colours(rbg: (i32, i32, i32)) {
    match rbg {
        (r, _, _) if r < 10 => println!("Not much red"),
        (_, b, _) if b < 10 => println!("Not much blue"),
        (_, _, g) if g < 10 => println!("Not much green"),
        _ => println!("Each colour has at least 10"),
    }
}

fn main() {
    let first = (200, 0, 0);
    let second = (50, 50, 50);
    let third = (200, 50, 0);

    match_colours(first);
    match_colours(second);
    match_colours(third);

}
```

這個將打印:

```text
Not much blue
Each colour has at least 10
Not much green
```

這也說明瞭`match`語句的作用，因為在第一個例子中，它只打印了`Not much blue`。但是`first`也沒有多少綠色。`match`語句總是在找到一個匹配項時停止，而不檢查其他的。這就是一個很好的例子，代碼編譯得很好，但不是你想要的代碼。

你可以創建一個非常大的 `match` 語句來解決這個問題，但是使用 `for` 循環可能更好。我們將很快討論循環。

匹配必須返回相同的類型。所以你不能這樣做:

```rust
fn main() {
    let my_number = 10;
    let some_variable = match my_number {
        10 => 8,
        _ => "Not ten", // ⚠️
    };
}
```

編譯器告訴你:

```text
error[E0308]: `match` arms have incompatible types
  --> src\main.rs:17:14
   |
15 |       let some_variable = match my_number {
   |  _________________________-
16 | |         10 => 8,
   | |               - this is found to be of type `{integer}`
17 | |         _ => "Not ten",
   | |              ^^^^^^^^^ expected integer, found `&str`
18 | |     };
   | |_____- `match` arms have incompatible types
```

這樣也不行，原因同上。

```rust
fn main() {
    let some_variable = if my_number == 10 { 8 } else { "something else "}; // ⚠️
}
```

但是這樣就可以了，因為不是`match`，所以你每次都有不同的`let`語句。

```rust
fn main() {
    let my_number = 10;

    if my_number == 10 {
        let some_variable = 8;
    } else {
        let some_variable = "Something else";
    }
}
```

你也可以使用 `@` 給 `match` 表達式的值起一個名字，然後你就可以使用它。在這個例子中，我們在一個函數中匹配一個 `i32` 輸入。如果是4或13，我們要在`println!`語句中使用這個數字。否則，我們不需要使用它。

```rust
fn match_number(input: i32) {
    match input {
    number @ 4 => println!("{} is an unlucky number in China (sounds close to 死)!", number),
    number @ 13 => println!("{} is unlucky in North America, lucky in Italy! In bocca al lupo!", number),
    _ => println!("Looks like a normal number"),
    }
}

fn main() {
    match_number(50);
    match_number(13);
    match_number(4);
}
```

這個打印:

```text
Looks like a normal number
13 is unlucky in North America, lucky in Italy! In bocca al lupo!
4 is an unlucky number in China (sounds close to 死)!
```

## 結構體

有了結構體，你可以創建自己的類型。在 Rust 中，你會一直使用結構體，因為它們非常方便。結構體是用關鍵字 `struct` 創建的。結構體的名稱應該用UpperCamelCase(每個字用大寫字母，不要用空格)。如果你用全小寫的結構，編譯器會告訴你。

有三種類型的結構。一種是 "單元結構"。單元的意思是 "沒有任何東西"。對於一個單元結構，你只需要寫名字和一個分號。

```rust
struct FileDirectory;
fn main() {}
```

接下來是一個元組結構，或者說是一個未命名結構。之所以是 "未命名"，是因為你只需要寫類型，而不是字段名。當你需要一個簡單的結構，並且不需要記住名字時，元組結構是很好的選擇。

```rust
struct Colour(u8, u8, u8);

fn main() {
    let my_colour = Colour(50, 0, 50); // Make a colour out of RGB (red, green, blue)
    println!("The second part of the colour is: {}", my_colour.1);
}
```

這時打印出`The second part of the colour is: 0`。

第三種類型是命名結構。這可能是最常見的結構。在這個結構中，你在一個 `{}` 代碼塊中聲明字段名和類型。請注意，在命名結構後面不要寫分號，因為後面有一整個代碼塊。

```rust
struct Colour(u8, u8, u8); // Declare the same Colour tuple struct

struct SizeAndColour {
    size: u32,
    colour: Colour, // And we put it in our new named struct
}

fn main() {
    let my_colour = Colour(50, 0, 50);

    let size_and_colour = SizeAndColour {
        size: 150,
        colour: my_colour
    };
}
```

在一個命名結構中，你也可以用逗號來分隔字段。對於最後一個字段，你可以加一個逗號或不加--這取決於你。`SizeAndColour` 在 `colour` 後面有一個逗號。

```rust
struct Colour(u8, u8, u8); // Declare the same Colour tuple struct

struct SizeAndColour {
    size: u32,
    colour: Colour, // And we put it in our new named struct
}

fn main() {}
```

但你不需要它。但總是放一個逗號可能是個好主意，因為有時你會改變字段的順序。

```rust
struct Colour(u8, u8, u8); // Declare the same Colour tuple struct

struct SizeAndColour {
    size: u32,
    colour: Colour // No comma here
}

fn main() {}
```

然後我們決定改變順序...

```rust
struct SizeAndColour {
    colour: Colour // ⚠️ Whoops! Now this doesn't have a comma.
    size: u32,
}

fn main() {}
```

但無論哪種方式都不是很重要，所以你可以選擇是否使用逗號。


我們創建一個`Country`結構來舉例說明。`Country`結構有`population`、`capital`和`leader_name`三個字段。

```rust
struct Country {
    population: u32,
    capital: String,
    leader_name: String
}

fn main() {
    let population = 500_000;
    let capital = String::from("Elista");
    let leader_name = String::from("Batu Khasikov");

    let kalmykia = Country {
        population: population,
        capital: capital,
        leader_name: leader_name,
    };
}
```

你有沒有注意到，我們把同樣的東西寫了兩次？我們寫了`population: population`、`capital: capital`和`leader_name: leader_name`。實際上，你不需要這樣做:如果字段名和變量名是一樣的，你就不用寫兩次。

```rust
struct Country {
    population: u32,
    capital: String,
    leader_name: String
}

fn main() {
    let population = 500_000;
    let capital = String::from("Elista");
    let leader_name = String::from("Batu Khasikov");

    let kalmykia = Country {
        population,
        capital,
        leader_name,
    };
}
```

## 枚舉

`enum`是enumerations的簡稱。它們看起來與結構體非常相似，但又有所不同。這就是區別:

- 當你想要一個東西**和**另一個東西時，使用`struct`.
- 當你想要一個東西**或**另一個東西時，請使用 `enum`。

所以，結構體是用於**多個事物**在一起，而枚舉則是用於**多個選擇**在一起。


要聲明一個枚舉，請寫`enum`，並使用一個包含選項的代碼塊，用逗號分隔。就像 `struct` 一樣，最後一部分可以有逗號，也可以沒有。我們將創建一個名為 `ThingsInTheSky` 的枚舉。

```rust
enum ThingsInTheSky {
    Sun,
    Stars,
}

fn main() {}
```

這是一個枚舉，因為你可以看到太陽，**或**星星:你必須選擇一個。這些叫做**變體**。

```rust
// create the enum with two choices
enum ThingsInTheSky {
    Sun,
    Stars,
}

// With this function we can use an i32 to create ThingsInTheSky.
fn create_skystate(time: i32) -> ThingsInTheSky {
    match time {
        6..=18 => ThingsInTheSky::Sun, // Between 6 and 18 hours we can see the sun
        _ => ThingsInTheSky::Stars, // Otherwise, we can see stars
    }
}

// With this function we can match against the two choices in ThingsInTheSky.
fn check_skystate(state: &ThingsInTheSky) {
    match state {
        ThingsInTheSky::Sun => println!("I can see the sun!"),
        ThingsInTheSky::Stars => println!("I can see the stars!")
    }
}

fn main() {
    let time = 8; // it's 8 o'clock
    let skystate = create_skystate(time); // create_skystate returns a ThingsInTheSky
    check_skystate(&skystate); // Give it a reference so it can read the variable skystate
}
```

這將打印出`I can see the sun!`。

你也可以將數據添加到一個枚舉中。

```rust
enum ThingsInTheSky {
    Sun(String), // Now each variant has a string
    Stars(String),
}

fn create_skystate(time: i32) -> ThingsInTheSky {
    match time {
        6..=18 => ThingsInTheSky::Sun(String::from("I can see the sun!")), // Write the strings here
        _ => ThingsInTheSky::Stars(String::from("I can see the stars!")),
    }
}

fn check_skystate(state: &ThingsInTheSky) {
    match state {
        ThingsInTheSky::Sun(description) => println!("{}", description), // Give the string the name description so we can use it
        ThingsInTheSky::Stars(n) => println!("{}", n), // Or you can name it n. Or anything else - it doesn't matter
    }
}

fn main() {
    let time = 8; // it's 8 o'clock
    let skystate = create_skystate(time); // create_skystate returns a ThingsInTheSky
    check_skystate(&skystate); // Give it a reference so it can read the variable skystate
}
```

這樣打印出來的結果是一樣的:`I can see the sun!`。

你也可以 "導入"一個枚舉，這樣你就不用打那麼多字了。下面是一個例子，我們每次在心情上匹配時都要輸入 `Mood::`。

```rust
enum Mood {
    Happy,
    Sleepy,
    NotBad,
    Angry,
}

fn match_mood(mood: &Mood) -> i32 {
    let happiness_level = match mood {
        Mood::Happy => 10, // Here we type Mood:: every time
        Mood::Sleepy => 6,
        Mood::NotBad => 7,
        Mood::Angry => 2,
    };
    happiness_level
}

fn main() {
    let my_mood = Mood::NotBad;
    let happiness_level = match_mood(&my_mood);
    println!("Out of 1 to 10, my happiness is {}", happiness_level);
}
```

它打印的是`Out of 1 to 10, my happiness is 7`。讓我們導入，這樣我們就可以少打點字了。要導入所有的東西，寫`*`。注意:它和`*`的解引用鍵是一樣的，但完全不同。

```rust
enum Mood {
    Happy,
    Sleepy,
    NotBad,
    Angry,
}

fn match_mood(mood: &Mood) -> i32 {
    use Mood::*; // We imported everything in Mood. Now we can just write Happy, Sleepy, etc.
    let happiness_level = match mood {
        Happy => 10, // We don't have to write Mood:: anymore
        Sleepy => 6,
        NotBad => 7,
        Angry => 2,
    };
    happiness_level
}

fn main() {
    let my_mood = Mood::Happy;
    let happiness_level = match_mood(&my_mood);
    println!("Out of 1 to 10, my happiness is {}", happiness_level);
}
```


`enum` 的部分也可以變成一個整數。這是因為 Rust 給 `enum` 的每個arm提供了一個以 0 開頭的數字，供它自己使用。如果你的枚舉中沒有任何其他數據，你可以用它來做一些事情。

```rust
enum Season {
    Spring, // If this was Spring(String) or something it wouldn't work
    Summer,
    Autumn,
    Winter,
}

fn main() {
    use Season::*;
    let four_seasons = vec![Spring, Summer, Autumn, Winter];
    for season in four_seasons {
        println!("{}", season as u32);
    }
}
```

這個打印:

```text
0
1
2
3
```

不過如果你想的話，你可以給它一個不同的數字--Rust並不在意，可以用同樣的方式來使用它。只需在你想要的變體上加一個 `=` 和你的數字。你不必給所有的都分配一個數字。但如果你不這樣做，Rust就會從前一個arm加1來賦值給當前arm。

```rust
enum Star {
    BrownDwarf = 10,
    RedDwarf = 50,
    YellowStar = 100,
    RedGiant = 1000,
    DeadStar, // Think about this one. What number will it have?
}

fn main() {
    use Star::*;
    let starvec = vec![BrownDwarf, RedDwarf, YellowStar, RedGiant];
    for star in starvec {
        match star as u32 {
            size if size <= 80 => println!("Not the biggest star."), // Remember: size doesn't mean anything. It's just a name we chose so we can print it
            size if size >= 80 => println!("This is a good-sized star."),
            _ => println!("That star is pretty big!"),
        }
    }
    println!("What about DeadStar? It's the number {}.", DeadStar as u32);
}
```

這個打印:


```text
Not the biggest star.
Not the biggest star.
This is a good-sized star.
This is a good-sized star.
What about DeadStar? It's the number 1001.
```

`DeadStar`本來是4號，但現在是1001。

### 使用多種類型的枚舉

你知道`Vec`、數組等中的元素都需要相同的類型(只有tuple不同)。但其實你可以用一個枚舉來放不同的類型。想象一下，我們想有一個`Vec`，有`u32`或`i32`。當然，你可以創建一個`Vec<(u32, i32)>`(一個帶有`(u32, i32)`元組的vec)，但是我們每次只想要一個。所以這裡可以使用一個枚舉。下面是一個簡單的例子。

```rust
enum Number {
    U32(u32),
    I32(i32),
}

fn main() {}
```

所以有兩個變體:`U32`變體裡面有`u32`，`I32`變體裡面有`i32`。`U32`和`I32`只是我們起的名字。它們可能是`UThirtyTwo`或`IThirtyTwo`或其他任何東西。

現在，如果我們把它們放到 `Vec` 中，我們就會有一個 `Vec<Number>`，編譯器很高興，因為都是同一個類型。編譯器並不在乎我們有 `u32` 或 `i32`，因為它們都在一個叫做 `Number` 的單一類型裡面。因為它是一個枚舉，你必須選擇一個，這就是我們想要的。我們將使用`.is_positive()`方法來挑選。如果是 `true`，那麼我們將選擇 `U32`，如果是 `false`，那麼我們將選擇 `I32`。

現在的代碼是這樣的。

```rust
enum Number {
    U32(u32),
    I32(i32),
}

fn get_number(input: i32) -> Number {
    let number = match input.is_positive() {
        true => Number::U32(input as u32), // change it to u32 if it's positive
        false => Number::I32(input), // otherwise just give the number because it's already i32
    };
    number
}


fn main() {
    let my_vec = vec![get_number(-800), get_number(8)];

    for item in my_vec {
        match item {
            Number::U32(number) => println!("It's a u32 with the value {}", number),
            Number::I32(number) => println!("It's an i32 with the value {}", number),
        }
    }
}
```

這就打印出了我們想看到的東西。

```text
It's an i32 with the value -800
It's a u32 with the value 8
```


## 循環

有了循環，你可以告訴 Rust 繼續某事，直到你想讓它停止。您使用 `loop` 來啟動一個不會停止的循環，除非您告訴它何時`break`。

```rust
fn main() { // This program will never stop
    loop {

    }
}
```

所以，我們要告訴編譯器什麼時候能停止:

```rust
fn main() {
    let mut counter = 0; // set a counter to 0
    loop {
        counter +=1; // increase the counter by 1
        println!("The counter is now: {}", counter);
        if counter == 5 { // stop when counter == 5
            break;
        }
    }
}
```

這將打印:

```text
The counter is now: 1
The counter is now: 2
The counter is now: 3
The counter is now: 4
The counter is now: 5
```

如果你在一個循環裡面有一個循環，你可以給它們命名。有了名字，你可以告訴 Rust 要從哪個循環中 `break` 出來。使用 `'` (稱為 "tick") 和 `:` 來給它命名。

```rust
fn main() {
    let mut counter = 0;
    let mut counter2 = 0;
    println!("Now entering the first loop.");

    'first_loop: loop {
        // Give the first loop a name
        counter += 1;
        println!("The counter is now: {}", counter);
        if counter > 9 {
            // Starts a second loop inside this loop
            println!("Now entering the second loop.");

            'second_loop: loop {
                // now we are inside 'second_loop
                println!("The second counter is now: {}", counter2);
                counter2 += 1;
                if counter2 == 3 {
                    break 'first_loop; // Break out of 'first_loop so we can exit the program
                }
            }
        }
    }
}
```

這將打印:

```text
Now entering the first loop.
The counter is now: 1
The counter is now: 2
The counter is now: 3
The counter is now: 4
The counter is now: 5
The counter is now: 6
The counter is now: 7
The counter is now: 8
The counter is now: 9
The counter is now: 10
Now entering the second loop.
The second counter is now: 0
The second counter is now: 1
The second counter is now: 2
```

`while`循環是指在某件事情還在`true`時繼續的循環。每一次循環，Rust 都會檢查它是否仍然是 `true`。如果變成`false`，Rust會停止循環。

```rust
fn main() {
    let mut counter = 0;

    while counter < 5 {
        counter +=1;
        println!("The counter is now: {}", counter);
    }
}
```

`for`循環可以讓你告訴Rust每次要做什麼。但是在 `for` 循環中，循環會在一定次數後停止。`for`循環經常使用**範圍**。你使用 `..` 和 `..=` 來創建一個範圍。

- `..`創建一個**排他的**範圍:`0..3`創建了`0, 1, 2`.
- `..=`創建一個**包含的**範圍: `0..=3`創建`0, 1, 2`。`0..=3` = `0, 1, 2, 3`.

```rust
fn main() {
    for number in 0..3 {
        println!("The number is: {}", number);
    }

    for number in 0..=3 {
        println!("The next number is: {}", number);
    }
}
```

這個將打印:

```text
The number is: 0
The number is: 1
The number is: 2
The next number is: 0
The next number is: 1
The next number is: 2
The next number is: 3
```

同時注意到，`number`成為0..3的變量名。我們可以把它叫做 `n`，或者 `ntod_het___hno_f`，或者任何名字。然後，我們可以在`println!`中使用這個名字。

如果你不需要變量名，就用`_`。

```rust
fn main() {
    for _ in 0..3 {
        println!("Printing the same thing three times");
    }
}
```

這個打印:

```text
Printing the same thing three times
Printing the same thing three times
Printing the same thing three times
```

因為我們每次都沒有給它任何數字來打印。

而實際上，如果你給了一個變量名卻不用，Rust會告訴你:

```rust
fn main() {
    for number in 0..3 {
        println!("Printing the same thing three times");
    }
}
```

這打印的內容和上面一樣。程序編譯正常，但Rust會提醒你沒有使用`number`:

```text
warning: unused variable: `number`
 --> src\main.rs:2:9
  |
2 |     for number in 0..3 {
  |         ^^^^^^ help: if this is intentional, prefix it with an underscore: `_number`
```

Rust 建議寫 `_number` 而不是 `_`。在變量名前加上 `_` 意味著 "也許我以後會用到它"。但是隻用`_`意味著 "我根本不關心這個變量"。所以，如果你以後會使用它們，並且不想讓編譯器告訴你，你可以在變量名前面加上`_`。

你也可以用`break`來返回一個值。
 你把值寫在 `break` 之後，並使用 `;`。下面是一個用 `loop` 和一個斷點給出 `my_number` 值的例子。

```rust
fn main() {
    let mut counter = 5;
    let my_number = loop {
        counter +=1;
        if counter % 53 == 3 {
            break counter;
        }
    };
    println!("{}", my_number);
}
```

這時打印出`56`。`break counter;`的意思是 "中斷並返回計數器的值"。而且因為整個塊以`let`開始，所以`my_number`得到值。

現在我們知道了如何使用循環，這裡有一個更好的解決方案來解決我們之前的顏色 "匹配"問題。這是一個更好的解決方案，因為我們要比較所有的東西，而 "for"循環會查看每一項。

```rust
fn match_colours(rbg: (i32, i32, i32)) {
    println!("Comparing a colour with {} red, {} blue, and {} green:", rbg.0, rbg.1, rbg.2);
    let new_vec = vec![(rbg.0, "red"), (rbg.1, "blue"), (rbg.2, "green")]; // Put the colours in a vec. Inside are tuples with the colour names
    let mut all_have_at_least_10 = true; // Start with true. We will set it to false if one colour is less than 10
    for item in new_vec {
        if item.0 < 10 {
            all_have_at_least_10 = false; // Now it's false
            println!("Not much {}.", item.1) // And we print the colour name.
        }
    }
    if all_have_at_least_10 { // Check if it's still true, and print if true
        println!("Each colour has at least 10.")
    }
    println!(); // Add one more line
}

fn main() {
    let first = (200, 0, 0);
    let second = (50, 50, 50);
    let third = (200, 50, 0);

    match_colours(first);
    match_colours(second);
    match_colours(third);
}
```

這個打印:

```text
Comparing a colour with 200 red, 0 blue, and 0 green:
Not much blue.
Not much green.

Comparing a colour with 50 red, 50 blue, and 50 green:
Each colour has at least 10.

Comparing a colour with 200 red, 50 blue, and 0 green:
Not much green.
```

## 實現結構體和枚舉

在這裡你可以開始賦予你的結構體和枚舉一些真正的力量。要調用 `struct` 或 `enum` 上的函數，請使用 `impl` 塊。這些函數被稱為**方法**。`impl`塊中有兩種方法。

- 方法：這些方法取**self**（或 **&self** 或 **&mut self** ）。常規方法使用"."（一個句號）。`.clone()`是一個常規方法的例子。
- 關聯函數（在某些語言中被稱為 "靜態 "方法）：這些函數不使用self。關聯的意思是 "與之相關"。它們的書寫方式不同，使用`::`。`String::from()`是一個關聯函數，`Vec::new()`也是。你看到的關聯函數最常被用來創建新的變量。

在我們的例子中，我們將創建Animal並打印它們。

對於新的`struct`或`enum`，如果你想使用`{:?}`來打印，你需要給它**Debug**，所以我們將這樣做:如果你在結構體或枚舉上面寫了`#[derive(Debug)]`，那麼你就可以用`{:?}`來打印。這些帶有`#[]`的信息被稱為**屬性**。你有時可以用它們來告訴編譯器給你的結構體一個能力，比如`Debug`。屬性有很多，我們以後會學習它們。但是`derive`可能是最常見的，你經常在結構體和枚舉上面看到它。

```rust
#[derive(Debug)]
struct Animal {
    age: u8,
    animal_type: AnimalType,
}

#[derive(Debug)]
enum AnimalType {
    Cat,
    Dog,
}

impl Animal {
    fn new() -> Self {
        // Self means Animal.
        //You can also write Animal instead of Self

        Self {
            // When we write Animal::new(), we always get a cat that is 10 years old
            age: 10,
            animal_type: AnimalType::Cat,
        }
    }

    fn change_to_dog(&mut self) { // because we are inside Animal, &mut self means &mut Animal
                                  // use .change_to_dog() to change the cat to a dog
                                  // with &mut self we can change it
        println!("Changing animal to dog!");
        self.animal_type = AnimalType::Dog;
    }

    fn change_to_cat(&mut self) {
        // use .change_to_cat() to change the dog to a cat
        // with &mut self we can change it
        println!("Changing animal to cat!");
        self.animal_type = AnimalType::Cat;
    }

    fn check_type(&self) {
        // we want to read self
        match self.animal_type {
            AnimalType::Dog => println!("The animal is a dog"),
            AnimalType::Cat => println!("The animal is a cat"),
        }
    }
}



fn main() {
    let mut new_animal = Animal::new(); // Associated function to create a new animal
                                        // It is a cat, 10 years old
    new_animal.check_type();
    new_animal.change_to_dog();
    new_animal.check_type();
    new_animal.change_to_cat();
    new_animal.check_type();
}
```

這個打印:

```text
The animal is a cat
Changing animal to dog!
The animal is a dog
Changing animal to cat!
The animal is a cat
```


記住，Self(類型Self)和self(變量self)是縮寫。(縮寫=簡寫方式)

所以，在我們的代碼中，Self = Animal。另外，`fn change_to_dog(&mut self)`的意思是`fn change_to_dog(&mut Animal)`。

下面再舉一個小例子。這次我們將在`enum`上使用`impl`。

```rust
enum Mood {
    Good,
    Bad,
    Sleepy,
}

impl Mood {
    fn check(&self) {
        match self {
            Mood::Good => println!("Feeling good!"),
            Mood::Bad => println!("Eh, not feeling so good"),
            Mood::Sleepy => println!("Need sleep NOW"),
        }
    }
}

fn main() {
    let my_mood = Mood::Sleepy;
    my_mood.check();
}
```

打印出`Need sleep NOW`。

## 解構

我們再來看一些解構。你可以通過使用`let`倒過來從一個結構體或枚舉中獲取值。我們瞭解到這是`destructuring`，因為你得到的變量不是結構體的一部分。現在你分別得到了它們的值。首先是一個簡單的例子。

```rust
struct Person { // make a simple struct for a person
    name: String,
    real_name: String,
    height: u8,
    happiness: bool
}

fn main() {
    let papa_doc = Person { // create variable papa_doc
        name: "Papa Doc".to_string(),
        real_name: "Clarence".to_string(),
        height: 170,
        happiness: false
    };

    let Person { // destructure papa_doc
        name: a,
        real_name: b,
        height: c,
        happiness: d
    } = papa_doc;

    println!("They call him {} but his real name is {}. He is {} cm tall and is he happy? {}", a, b, c, d);
}
```

這個打印:`They call him Papa Doc but his real name is Clarence. He is 170 cm tall and is he happy? false`

你可以看到，這是倒過來的。首先我們說`let papa_doc = Person { fields }`來創建結構。然後我們說 `let Person { fields } = papa_doc` 來解構它。

你不必寫`name: a`--你可以直接寫`name`。但這裡我們寫 `name: a` 是因為我們想使用一個名字為 `a` 的變量。

現在再舉一個更大的例子。在這個例子中，我們有一個 `City` 結構。我們給它一個`new`函數來創建它。然後我們有一個 `process_city_values` 函數來處理這些值。在函數中，我們只是創建了一個 `Vec`，但你可以想象，我們可以在解構它之後做更多的事情。

```rust
struct City {
    name: String,
    name_before: String,
    population: u32,
    date_founded: u32,
}

impl City {
    fn new(name: String, name_before: String, population: u32, date_founded: u32) -> Self {
        Self {
            name,
            name_before,
            population,
            date_founded,
        }
    }
}

fn process_city_values(city: &City) {
    let City {
        name,
        name_before,
        population,
        date_founded,
    } = city;
        // now we have the values to use separately
    let two_names = vec![name, name_before];
    println!("The city's two names are {:?}", two_names);
}

fn main() {
    let tallinn = City::new("Tallinn".to_string(), "Reval".to_string(), 426_538, 1219);
    process_city_values(&tallinn);
}
```

這將打印出`The city's two names are ["Tallinn", "Reval"]`。


## 引用和點運算符

我們瞭解到，當你有一個引用時，你需要使用`*`來獲取值。引用是一種不同的類型，所以這是無法運行的:

```rust
fn main() {
    let my_number = 9;
    let reference = &my_number;

    println!("{}", my_number == reference); // ⚠️
}
```

編譯器打印。

```text
error[E0277]: can't compare `{integer}` with `&{integer}`
 --> src\main.rs:5:30
  |
5 |     println!("{}", my_number == reference);
  |                              ^^ no implementation for `{integer} == &{integer}`
```

所以我們把第5行改成`println!("{}", my_number == *reference);`，現在打印的是`true`，因為現在是`i32` == `i32`，而不是`i32` == `&i32`。這就是所謂的解引用。

但是當你使用一個方法時，Rust會為你解除引用。方法中的 `.` 被稱為點運算符，它可以免費進行遞歸。

首先，讓我們創建一個有一個 `u8` 字段的結構。然後，我們將對它進行引用，並嘗試進行比較。它將無法工作。

```rust
struct Item {
    number: u8,
}

fn main() {
    let item = Item {
        number: 8,
    };

    let reference_number = &item.number; // reference number type is &u8

    println!("{}", reference_number == 8); // ⚠️ &u8 and u8 cannot be compared
}
```

為了讓它工作，我們需要取消定義。`println!("{}", *reference_number == 8);`.

但如果使用點運算符，我們不需要`*`。例如

```rust
struct Item {
    number: u8,
}

fn main() {
    let item = Item {
        number: 8,
    };

    let reference_item = &item;

    println!("{}", reference_item.number == 8); // we don't need to write *reference_item.number
}
```

現在讓我們為 `Item` 創建一個方法，將 `number` 與另一個數字進行比較。我們不需要在任何地方使用 `*`。

```rust
struct Item {
    number: u8,
}

impl Item {
    fn compare_number(&self, other_number: u8) { // takes a reference to self
        println!("Are {} and {} equal? {}", self.number, other_number, self.number == other_number);
            // We don't need to write *self.number
    }
}

fn main() {
    let item = Item {
        number: 8,
    };

    let reference_item = &item; // This is type &Item
    let reference_item_two = &reference_item; // This is type &&Item

    item.compare_number(8); // the method works
    reference_item.compare_number(8); // it works here too
    reference_item_two.compare_number(8); // and here

}
```

所以只要記住:當你使用`.`運算符時，你不需要擔心`*`。


## 泛型

在函數中，你要寫出採取什麼類型作為輸入。

```rust
fn return_number(number: i32) -> i32 {
    println!("Here is your number.");
    number
}

fn main() {
    let number = return_number(5);
}
```

但是如果你想用的不僅僅是`i32`呢？你可以用泛型來解決。Generics的意思是 "也許是一種類型，也許是另一種類型"。

對於泛型，你可以使用角括號，裡面加上類型，像這樣。`<T>` 這意味著 "任何類型你都可以放入函數中" 通常情況下，generics使用一個大寫字母的類型(T、U、V等)，儘管你不必只使用一個字母。

這就是你如何改變函數使其通用的方法。

```rust
fn return_number<T>(number: T) -> T {
    println!("Here is your number.");
    number
}

fn main() {
    let number = return_number(5);
}
```

重要的部分是函數名後的`<T>`。如果沒有這個，Rust會認為T是一個具體的(具體的=不是通用的)類型。
 如`String`或`i8`。

如果我們寫出一個類型名，這就更容易理解了。看看我們把 `T` 改成 `MyType` 會發生什麼。

```rust
fn return_number(number: MyType) -> MyType { // ⚠️
    println!("Here is your number.");
    number
}
```

大家可以看到，`MyType`是具體的，不是通用的。所以我們需要寫這個，所以現在就可以了。

```rust
fn return_number<MyType>(number: MyType) -> MyType {
    println!("Here is your number.");
    number
}

fn main() {
    let number = return_number(5);
}
```

所以單字母`T`是人的眼睛，但函數名後面的部分是編譯器的 "眼睛"。沒有了它，就不通用了。

現在我們再回到類型`T`，因為Rust代碼通常使用`T`。

你會記得Rust中有些類型是**Copy**，有些是**Clone**，有些是**Display**，有些是**Debug**，等等。用**Debug**，我們可以用`{:?}`來打印。所以現在大家可以看到，我們如果要打印`T`就有問題了。

```rust
fn print_number<T>(number: T) {
    println!("Here is your number: {:?}", number); // ⚠️
}

fn main() {
    print_number(5);
}
```

`print_number`需要**Debug**打印`number`，但是`T`與`Debug`是一個類型嗎？也許不是。也許它沒有`#[derive(Debug)]`，誰知道呢？編譯器也不知道，所以它給出了一個錯誤。

```text
error[E0277]: `T` doesn't implement `std::fmt::Debug`
  --> src\main.rs:29:43
   |
29 |     println!("Here is your number: {:?}", number);
   |                                           ^^^^^^ `T` cannot be formatted using `{:?}` because it doesn't implement `std::fmt::Debug`
```

T沒有實現**Debug**。那麼我們是否要為T實現Debug呢？不，因為我們不知道T是什麼。但是我們可以告訴函數。"別擔心，因為任何T類型的函數都會有Debug"

```rust
use std::fmt::Debug; // Debug is located at std::fmt::Debug. So now we can just write 'Debug'.

fn print_number<T: Debug>(number: T) { // <T: Debug> is the important part
    println!("Here is your number: {:?}", number);
}

fn main() {
    print_number(5);
}
```

所以現在編譯器知道:"好的，這個類型T要有Debug"。現在代碼工作了，因為`i32`有Debug。現在我們可以給它很多類型。`String`, `&str`, 等等，因為它們都有Debug.

現在我們可以創建一個結構，並用#[derive(Debug)]給它Debug，所以現在我們也可以打印它。我們的函數可以取`i32`，Animal結構等。

```rust
use std::fmt::Debug;

#[derive(Debug)]
struct Animal {
    name: String,
    age: u8,
}

fn print_item<T: Debug>(item: T) {
    println!("Here is your item: {:?}", item);
}

fn main() {
    let charlie = Animal {
        name: "Charlie".to_string(),
        age: 1,
    };

    let number = 55;

    print_item(charlie);
    print_item(number);
}
```

這個打印:

```text
Here is your item: Animal { name: "Charlie", age: 1 }
Here is your item: 55
```

有時候，我們在一個通用函數中需要不止一個類型。我們必須寫出每個類型的名稱，並考慮如何使用它。在這個例子中，我們想要兩個類型。首先我們要打印一個類型為T的語句。用`{}`打印比較好，所以我們會要求用`Display`來打印`T`。

其次是類型U，`num_1`和`num_2`這兩個變量的類型為U(U是某種數字)。我們想要比較它們，所以我們需要`PartialOrd`。這個特性讓我們可以使用`<`、`>`、`==`等。我們也想打印它們，所以我們也需要`Display`來打印`U`。

```rust
use std::fmt::Display;
use std::cmp::PartialOrd;

fn compare_and_display<T: Display, U: Display + PartialOrd>(statement: T, num_1: U, num_2: U) {
    println!("{}! Is {} greater than {}? {}", statement, num_1, num_2, num_1 > num_2);
}

fn main() {
    compare_and_display("Listen up!", 9, 8);
}
```

這就打印出了`Listen up!! Is 9 greater than 8? true`。

所以`fn compare_and_display<T: Display, U: Display + PartialOrd>(statement: T, num_1: U, num_2: U)`說。

- 函數名稱是`compare_and_display`,
- 第一個類型是T，它是通用的。它必須是一個可以用{}打印的類型。
- 下一個類型是U，它是通用的。它必須是一個可以用{}打印的類型。另外，它必須是一個可以比較的類型(使用 `>`、`<` 和 `==`)。

現在我們可以給`compare_and_display`不同的類型。`statement`可以是一個`String`，一個`&str`，任何有Display的類型。

為了讓通用函數更容易讀懂，我們也可以這樣寫，在代碼塊之前就寫上`where`。

```rust
use std::cmp::PartialOrd;
use std::fmt::Display;

fn compare_and_display<T, U>(statement: T, num_1: U, num_2: U)
where
    T: Display,
    U: Display + PartialOrd,
{
    println!("{}! Is {} greater than {}? {}", statement, num_1, num_2, num_1 > num_2);
}

fn main() {
    compare_and_display("Listen up!", 9, 8);
}
```

當你有很多通用類型時，使用`where`是一個好主意。

還要注意。

- 如果你有一個類型T和另一個類型T，它們必須是相同的。
- 如果你有一個類型T和另一個類型U，它們可以是不同的。但它們也可以是相同的。

比如說

```rust
use std::fmt::Display;

fn say_two<T: Display, U: Display>(statement_1: T, statement_2: U) { // Type T needs Display, type U needs Display
    println!("I have two things to say: {} and {}", statement_1, statement_2);
}

fn main() {

    say_two("Hello there!", String::from("I hate sand.")); // Type T is a &str, but type U is a String.
    say_two(String::from("Where is Padme?"), String::from("Is she all right?")); // Both types are String.
}
```

這個打印:

```text
I have two things to say: Hello there! and I hate sand.
I have two things to say: Where is Padme? and Is she all right?
```

## Option和Result

我們現在理解了枚舉和泛型，所以我們可以理解`Option`和`Result`。Rust使用這兩個枚舉來使代碼更安全。

我們將從`Option`開始。

### Option

當你有一個可能存在，也可能不存在的值時，你就用`Option`。當一個值存在的時候就是`Some(value)`，不存在的時候就是`None`，下面是一個壞代碼的例子，可以用`Option`來改進。

```rust
    // ⚠️
fn take_fifth(value: Vec<i32>) -> i32 {
    value[4]
}

fn main() {
    let new_vec = vec![1, 2];
    let index = take_fifth(new_vec);
}
```

當我們運行這段代碼時，它崩潰。以下是信息。

```text
thread 'main' panicked at 'index out of bounds: the len is 2 but the index is 4', src\main.rs:34:5
```

崩潰的意思是，程序在問題發生之前就停止了。Rust看到函數想要做一些不可能的事情，就會停止。它 "解開堆棧"(從堆棧中取值)，並告訴你 "對不起，我不能這樣做"。

所以現在我們將返回類型從`i32`改為`Option<i32>`。這意味著 "如果有的話給我一個`Some(i32)`，如果沒有的話給我一個`None`"。我們說`i32`是 "包"在一個`Option`裡面，也就是說它在一個`Option`裡面。你必須做一些事情才能把這個值弄出來。

```rust
fn take_fifth(value: Vec<i32>) -> Option<i32> {
    if value.len() < 5 { // .len() gives the length of the vec.
                         // It must be at least 5.
        None
    } else {
        Some(value[4])
    }
}

fn main() {
    let new_vec = vec![1, 2];
    let bigger_vec = vec![1, 2, 3, 4, 5];
    println!("{:?}, {:?}", take_fifth(new_vec), take_fifth(bigger_vec));
}
```

這個打印的是`None, Some(5)`。這下好了，因為現在我們再也不崩潰了。但是我們如何得到5的值呢？

我們可以用 `.unwrap()` 在一個Option中獲取值，但要小心 `.unwrap()`。這就像拆禮物一樣:也許裡面有好東西，也許裡面有一條憤怒的蛇。只有在你確定的情況下，你才會想要`.unwrap()`。如果你拆開一個`None`的值，程序就會崩潰。

```rust
// ⚠️
fn take_fifth(value: Vec<i32>) -> Option<i32> {
    if value.len() < 5 {
        None
    } else {
        Some(value[4])
    }
}

fn main() {
    let new_vec = vec![1, 2];
    let bigger_vec = vec![1, 2, 3, 4, 5];
    println!("{:?}, {:?}",
        take_fifth(new_vec).unwrap(), // this one is None. .unwrap() will panic!
        take_fifth(bigger_vec).unwrap()
    );
}
```

消息是: 
```text
thread 'main' panicked at 'called `Option::unwrap()` on a `None` value', src\main.rs:14:9
```

但我們不需要使用`.unwrap()`。我們可以使用`match`。那麼我們就可以把我們有`Some`的值打印出來，如果有`None`的值就不要碰。比如說

```rust
fn take_fifth(value: Vec<i32>) -> Option<i32> {
    if value.len() < 5 {
        None
    } else {
        Some(value[4])
    }
}

fn handle_option(my_option: Vec<Option<i32>>) {
  for item in my_option {
    match item {
      Some(number) => println!("Found a {}!", number),
      None => println!("Found a None!"),
    }
  }
}

fn main() {
    let new_vec = vec![1, 2];
    let bigger_vec = vec![1, 2, 3, 4, 5];
    let mut option_vec = Vec::new(); // Make a new vec to hold our options
                                     // The vec is type: Vec<Option<i32>>. That means a vec of Option<i32>.

    option_vec.push(take_fifth(new_vec)); // This pushes "None" into the vec
    option_vec.push(take_fifth(bigger_vec)); // This pushes "Some(5)" into the vec

    handle_option(option_vec); // handle_option looks at every option in the vec.
                               // It prints the value if it is Some. It doesn't touch it if it is None.
}
```

這個打印:

```text
Found a None!
Found a 5!
```


因為我們知道泛型，所以我們能夠讀懂`Option`的代碼。它看起來是這樣的:

```rust
enum Option<T> {
    None,
    Some(T),
}

fn main() {}
```

要記住的重要一點是:有了`Some`，你就有了一個類型為`T`的值(任何類型)。還要注意的是，`enum`名字後面的角括號圍繞著`T`是告訴編譯器它是通用的。它沒有`Display`這樣的trait或任何東西來限制它，所以它可以是任何東西。但是對於`None`，你什麼都沒有。

所以在`match`語句中，對於Option，你不能說。

```rust
// 🚧
Some(value) => println!("The value is {}", value),
None(value) => println!("The value is {}", value),
```

因為`None`只是`None`。

當然，還有更簡單的方法來使用Option。在這段代碼中，我們將使用一個叫做 `.is_some()` 的方法來告訴我們是否是 `Some`。(是的，還有一個叫做`.is_none()`的方法。)在這個更簡單的方法中，我們不需要`handle_option()`了。我們也不需要Option的vec了。

```rust
fn take_fifth(value: Vec<i32>) -> Option<i32> {
    if value.len() < 5 {
        None
    } else {
        Some(value[4])
    }
}

fn main() {
    let new_vec = vec![1, 2];
    let bigger_vec = vec![1, 2, 3, 4, 5];
    let vec_of_vecs = vec![new_vec, bigger_vec];
    for vec in vec_of_vecs {
        let inside_number = take_fifth(vec);
        if inside_number.is_some() {
            // .is_some() returns true if we get Some, false if we get None
            println!("We got: {}", inside_number.unwrap()); // now it is safe to use .unwrap() because we already checked
        } else {
            println!("We got nothing.");
        }
    }
}
```

這個將打印:

```text
We got nothing.
We got: 5
```

### Result

Result和Option類似，但這裡的區別是。

- Option大約是`Some`或`None`(有值或無值)。
- Result大約是`Ok`或`Err`(還好的結果，或錯誤的結果)。

所以，`Option`是如果你在想:"也許會有，也許不會有。"也許會有一些東西，也許不會有。" 但`Result`是如果你在想: "也許會失敗"

比較一下，這裡是Option和Result的簽名。

```rust
enum Option<T> {
    None,
    Some(T),
}

enum Result<T, E> {
    Ok(T),
    Err(E),
}

fn main() {}
```

所以Result在 "Ok "裡面有一個值，在 "Err "裡面有一個值。這是因為錯誤通常包含描述錯誤的信息。

`Result<T, E>`的意思是你要想好`Ok`要返回什麼，`Err`要返回什麼。其實，你可以決定任何事情。甚至這個也可以。

```rust
fn check_error() -> Result<(), ()> {
    Ok(())
}

fn main() {
    check_error();
}
```

`check_error`說 "如果得到`Ok`就返回`()`，如果得到`Err`就返回`()`"。然後我們用`()`返回`Ok`。

編譯器給了我們一個有趣的警告。

```text
warning: unused `std::result::Result` that must be used
 --> src\main.rs:6:5
  |
6 |     check_error();
  |     ^^^^^^^^^^^^^^
  |
  = note: `#[warn(unused_must_use)]` on by default
  = note: this `Result` may be an `Err` variant, which should be handled
```

這是真的:我們只返回了`Result`，但它可能是一個`Err`。所以讓我們稍微處理一下這個錯誤，儘管我們仍然沒有真正做任何事情。

```rust
fn give_result(input: i32) -> Result<(), ()> {
    if input % 2 == 0 {
        return Ok(())
    } else {
        return Err(())
    }
}

fn main() {
    if give_result(5).is_ok() {
        println!("It's okay, guys")
    } else {
        println!("It's an error, guys")
    }
}
```

打印出`It's an error, guys`。所以我們只是處理了第一個錯誤。

記住，輕鬆檢查的四種方法是`.is_some()`、`is_none()`、`is_ok()`和`is_err()`。


有時，一個帶有Result的函數會用`String`來表示`Err`的值。這不是最好的方法，但比我們目前所做的要好一些。

```rust
fn check_if_five(number: i32) -> Result<i32, String> {
    match number {
        5 => Ok(number),
        _ => Err("Sorry, the number wasn't five.".to_string()), // This is our error message
    }
}

fn main() {
    let mut result_vec = Vec::new(); // Create a new vec for the results

    for number in 2..7 {
        result_vec.push(check_if_five(number)); // push each result into the vec
    }

    println!("{:?}", result_vec);
}
```

我們的Vec打印:

```text
[Err("Sorry, the number wasn\'t five."), Err("Sorry, the number wasn\'t five."), Err("Sorry, the number wasn\'t five."), Ok(5),
Err("Sorry, the number wasn\'t five.")]
```

就像Option一樣，在`Err`上用`.unwrap()`就會崩潰。

```rust
    // ⚠️
fn main() {
    let error_value: Result<i32, &str> = Err("There was an error"); // Create a Result that is already an Err
    println!("{}", error_value.unwrap()); // Unwrap it
}
```

程序崩潰，打印。

```text
thread 'main' panicked at 'called `Result::unwrap()` on an `Err` value: "There was an error"', src\main.rs:30:20
```

這些信息可以幫助你修正你的代碼。`src\main.rs:30:20`的意思是 "在目錄src的main.rs內，第30行和第20列"。所以你可以去那裡查看你的代碼並修復問題。

你也可以創建自己的錯誤類型，標準庫中的Result函數和其他人的代碼通常都會這樣做。例如，標準庫中的這個函數。

```rust
// 🚧
pub fn from_utf8(vec: Vec<u8>) -> Result<String, FromUtf8Error>
```

這個函數接收一個字節向量(`u8`)，並嘗試創建一個`String`，所以Result的成功情況是`String`，錯誤情況是`FromUtf8Error`。你可以給你的錯誤類型起任何你想要的名字。

使用 `match` 與 `Option` 和 `Result` 有時需要很多代碼。例如，`.get()` 方法在 `Vec` 上返回 `Option`。

```rust
fn main() {
    let my_vec = vec![2, 3, 4];
    let get_one = my_vec.get(0); // 0 to get the first number
    let get_two = my_vec.get(10); // Returns None
    println!("{:?}", get_one);
    println!("{:?}", get_two);
}
```

此打印

```text
Some(2)
None
```

所以現在我們可以匹配得到數值。讓我們使用0到10的範圍，看看是否符合`my_vec`中的數字。

```rust
fn main() {
    let my_vec = vec![2, 3, 4];

    for index in 0..10 {
      match my_vec.get(index) {
        Some(number) => println!("The number is: {}", number),
        None => {}
      }
    }
}
```

這是好的，但是我們對`None`不做任何處理，因為我們不關心。這裡我們可以用`if let`把代碼變小。`if let`的意思是 "符合就做，不符合就不做"。`if let`是在你不要求對所有的東西都匹配的時候使用。

```rust
fn main() {
    let my_vec = vec![2, 3, 4];

    for index in 0..10 {
      if let Some(number) = my_vec.get(index) {
        println!("The number is: {}", number);
      }
    }
}
```

**重要的是要記住**。`if let Some(number) = my_vec.get(index)`的意思是 "如果你從`my_vec.get(index)`得到`Some(number)`"。

另外注意:它使用的是一個`=`。它不是一個布爾值。

`while let`就像`if let`的一個while循環。想象一下，我們有這樣的氣象站數據。

```text
["Berlin", "cloudy", "5", "-7", "78"]
["Athens", "sunny", "not humid", "20", "10", "50"]
```

我們想得到數字，但不想得到文字。對於數字，我們可以使用一個叫做 `parse::<i32>()` 的方法。`parse()`是方法，`::<i32>`是類型。它將嘗試把 `&str` 變成 `i32`，如果可以的話就把它給我們。它返回一個 `Result`，因為它可能無法工作(比如你想讓它解析 "Billybrobby"--那不是一個數字)。

我們還將使用 `.pop()`。這將從向量中取出最後一項。

```rust
fn main() {
    let weather_vec = vec![
        vec!["Berlin", "cloudy", "5", "-7", "78"],
        vec!["Athens", "sunny", "not humid", "20", "10", "50"],
    ];
    for mut city in weather_vec {
        println!("For the city of {}:", city[0]); // In our data, every first item is the city name
        while let Some(information) = city.pop() {
            // This means: keep going until you can't pop anymore
            // When the vector reaches 0 items, it will return None
            // and it will stop.
            if let Ok(number) = information.parse::<i32>() {
                // Try to parse the variable we called information
                // This returns a result. If it's Ok(number), it will print it
                println!("The number is: {}", number);
            }  // We don't write anything here because we do nothing if we get an error. Throw them all away
        }
    }
}
```

這將打印:

```text
For the city of Berlin:
The number is: 78
The number is: -7
The number is: 5
For the city of Athens:
The number is: 50
The number is: 10
The number is: 20
```

## 其他集合類型

Rust還有很多集合類型。你可以在標準庫中的 https://doc.rust-lang.org/beta/std/collections/ 看到它們。那個頁面對為什麼要使用一種類型有很好的解釋，所以如果你不知道你想要什麼類型，就去那裡。這些集合都在標準庫的`std::collections`裡面。使用它們的最好方法是使用 `use` 語句。
 就像我們的`enums`一樣。我們將從`HashMap`開始，這是很常見的。

### HashMap和BTreeMap

HashMap是由*keys*和*values*組成的集合。你使用鍵來查找與鍵匹配的值。你可以只用`HashMap::new()`創建一個新的`HashMap`，並使用`.insert(key, value)`來插入元素。

`HashMap`是沒有順序的，所以如果你把`HashMap`中的每一個鍵都打印在一起，可能會打印出不同的結果。我們可以在一個例子中看到這一點。

```rust
use std::collections::HashMap; // This is so we can just write HashMap instead of std::collections::HashMap every time

struct City {
    name: String,
    population: HashMap<u32, u32>, // This will have the year and the population for the year
}

fn main() {

    let mut tallinn = City {
        name: "Tallinn".to_string(),
        population: HashMap::new(), // So far the HashMap is empty
    };

    tallinn.population.insert(1372, 3_250); // insert three dates
    tallinn.population.insert(1851, 24_000);
    tallinn.population.insert(2020, 437_619);


    for (year, population) in tallinn.population { // The HashMap is HashMap<u32, u32> so it returns a two items each time
        println!("In the year {} the city of {} had a population of {}.", year, tallinn.name, population);
    }
}
```

這個打印:

```text
In the year 1372 the city of Tallinn had a population of 3250.
In the year 2020 the city of Tallinn had a population of 437619.
In the year 1851 the city of Tallinn had a population of 24000.
```

或者可能會打印。

```text
In the year 1851 the city of Tallinn had a population of 24000.
In the year 2020 the city of Tallinn had a population of 437619.
In the year 1372 the city of Tallinn had a population of 3250.
```

你可以看到，它不按順序排列。

如果你想要一個可以排序的`HashMap`，你可以用`BTreeMap`。其實它們之間是非常相似的，所以我們可以快速的把我們的`HashMap`改成`BTreeMap`來看看。大家可以看到，這幾乎是一樣的代碼。

```rust
use std::collections::BTreeMap; // Just change HashMap to BTreeMap

struct City {
    name: String,
    population: BTreeMap<u32, u32>, // Just change HashMap to BTreeMap
}

fn main() {

    let mut tallinn = City {
        name: "Tallinn".to_string(),
        population: BTreeMap::new(), // Just change HashMap to BTreeMap
    };

    tallinn.population.insert(1372, 3_250);
    tallinn.population.insert(1851, 24_000);
    tallinn.population.insert(2020, 437_619);

    for (year, population) in tallinn.population {
        println!("In the year {} the city of {} had a population of {}.", year, tallinn.name, population);
    }
}
```

現在會一直打印。

```text
In the year 1372 the city of Tallinn had a population of 3250.
In the year 1851 the city of Tallinn had a population of 24000.
In the year 2020 the city of Tallinn had a population of 437619.
```

現在我們再來看看`HashMap`。

只要把鍵放在`[]`的方括號裡，就可以得到`HashMap`的值。在接下來的這個例子中，我們將帶出`Bielefeld`這個鍵的值，也就是`Germany`。但是要注意，因為如果沒有鍵，程序會崩潰。比如你寫了`println!("{:?}", city_hashmap["Bielefeldd"]);`，那麼就會崩潰，因為`Bielefeldd`不存在。

如果你不確定會有一個鍵，你可以使用`.get()`，它返回一個`Option`。如果它存在，將是`Some(value)`，如果不存在，你將得到`None`，而不是使程序崩潰。這就是為什麼 `.get()` 是從 `HashMap` 中獲取一個值的比較安全的方法。

```rust
use std::collections::HashMap;

fn main() {
    let canadian_cities = vec!["Calgary", "Vancouver", "Gimli"];
    let german_cities = vec!["Karlsruhe", "Bad Doberan", "Bielefeld"];

    let mut city_hashmap = HashMap::new();

    for city in canadian_cities {
        city_hashmap.insert(city, "Canada");
    }
    for city in german_cities {
        city_hashmap.insert(city, "Germany");
    }

    println!("{:?}", city_hashmap["Bielefeld"]);
    println!("{:?}", city_hashmap.get("Bielefeld"));
    println!("{:?}", city_hashmap.get("Bielefeldd"));
}
```

這個打印:

```text
"Germany"
Some("Germany")
None
```

這是因為*Bielefeld*存在，但*Bielefeldd*不存在。

如果`HashMap`已經有一個鍵，當你試圖把它放進去時，它將覆蓋它的值。

```rust
use std::collections::HashMap;

fn main() {
    let mut book_hashmap = HashMap::new();

    book_hashmap.insert(1, "L'Allemagne Moderne");
    book_hashmap.insert(1, "Le Petit Prince");
    book_hashmap.insert(1, "섀도우 오브 유어 스마일");
    book_hashmap.insert(1, "Eye of the World");

    println!("{:?}", book_hashmap.get(&1));
}
```

這將打印出 `Some("Eye of the World")`，因為它是你最後使用 `.insert()` 的條目。

檢查一個條目是否存在是很容易的，因為你可以用 `.get()` 檢查，它給出了 `Option`。

```rust
use std::collections::HashMap;

fn main() {
    let mut book_hashmap = HashMap::new();

    book_hashmap.insert(1, "L'Allemagne Moderne");

    if book_hashmap.get(&1).is_none() { // is_none() returns a bool: true if it's None, false if it's Some
        book_hashmap.insert(1, "Le Petit Prince");
    }

    println!("{:?}", book_hashmap.get(&1));
}
```

這個打印`Some("L\'Allemagne Moderne")`是因為已經有了key為`1`的，所以我們沒有插入`Le Petit Prince`。

`HashMap`有一個非常有趣的方法，叫做`.entry()`，你一定要試試。有了它，你可以在沒有鍵的情況下，用如`.or_insert()`這類方法來插入值。有趣的是，它還給出了一個可變引用，所以如果你想的話，你可以改變它。首先是一個例子，我們只是在每次插入書名到`HashMap`時插入一個`true`。

讓我們假設我們有一個圖書館，並希望跟蹤我們的書籍。

```rust
use std::collections::HashMap;

fn main() {
    let book_collection = vec!["L'Allemagne Moderne", "Le Petit Prince", "Eye of the World", "Eye of the World"]; // Eye of the World appears twice

    let mut book_hashmap = HashMap::new();

    for book in book_collection {
        book_hashmap.entry(book).or_insert(true);
    }
    for (book, true_or_false) in book_hashmap {
        println!("Do we have {}? {}", book, true_or_false);
    }
}
```

這個將打印:

```text
Do we have Eye of the World? true
Do we have Le Petit Prince? true
Do we have L'Allemagne Moderne? true
```

但這並不是我們想要的。也許最好是數一下書的數量，這樣我們就知道*世界之眼* 有兩本。首先讓我們看看`.entry()`做了什麼，以及`.or_insert()`做了什麼。`.entry()`其實是返回了一個名為`Entry`的`enum`。

```rust
pub fn entry(&mut self, key: K) -> Entry<K, V> // 🚧
```


[Entry文檔頁](https://doc.rust-lang.org/std/collections/hash_map/enum.Entry.html)。下面是其代碼的簡單版本。`K`表示key，`V`表示value。

```rust
// 🚧
use std::collections::hash_map::*;

enum Entry<K, V> {
    Occupied(OccupiedEntry<K, V>),
    Vacant(VacantEntry<K, V>),
}
```

然後當我們調用`.or_insert()`時，它就會查看枚舉，並決定該怎麼做。

```rust
fn or_insert(self, default: V) -> &mut V { // 🚧
    match self {
        Occupied(entry) => entry.into_mut(),
        Vacant(entry) => entry.insert(default),
    }
}
```

有趣的是，它返回一個`mut`的引用。`&mut V`. 這意味著你可以使用`let`將其附加到一個變量上，並改變變量來改變`HashMap`中的值。所以對於每本書，如果沒有條目，我們就會插入一個0。而如果有的話，我們將在引用上使用`+= 1`來增加數字。現在它看起來像這樣:

```rust
use std::collections::HashMap;

fn main() {
    let book_collection = vec!["L'Allemagne Moderne", "Le Petit Prince", "Eye of the World", "Eye of the World"];

    let mut book_hashmap = HashMap::new();

    for book in book_collection {
        let return_value = book_hashmap.entry(book).or_insert(0); // return_value is a mutable reference. If nothing is there, it will be 0
        *return_value +=1; // Now return_value is at least 1. And if there was another book, it will go up by 1
    }

    for (book, number) in book_hashmap {
        println!("{}, {}", book, number);
    }
}
```


重要的部分是`let return_value = book_hashmap.entry(book).or_insert(0);`。如果去掉 `let`，你會得到 `book_hashmap.entry(book).or_insert(0)`。如果沒有`let`，它什麼也不做:它插入了0，沒有獲取指向0的可變引用。所以我們把它綁定到`return_value`上，這樣我們就可以保留0。然後我們把值增加1，這樣`HashMap`中的每本書都至少有1。然後當`.entry()`再看*世界之眼*時，它不會插入任何東西，但它給我們一個可變的1。然後我們把它增加到2，所以它才會打印出這樣的結果。

```text
L'Allemagne Moderne, 1
Le Petit Prince, 1
Eye of the World, 2
```


你也可以用`.or_insert()`做一些事情，比如插入一個vec，然後推入數據。讓我們假設我們問街上的男人和女人他們對一個政治家的看法。他們給出的評分從0到10。然後我們要把這些數字放在一起，看看這個政治家是更受男人歡迎還是女人歡迎。它可以是這樣的。


```rust
use std::collections::HashMap;

fn main() {
    let data = vec![ // This is the raw data
        ("male", 9),
        ("female", 5),
        ("male", 0),
        ("female", 6),
        ("female", 5),
        ("male", 10),
    ];

    let mut survey_hash = HashMap::new();

    for item in data { // This gives a tuple of (&str, i32)
        survey_hash.entry(item.0).or_insert(Vec::new()).push(item.1); // This pushes the number into the Vec inside
    }

    for (male_or_female, numbers) in survey_hash {
        println!("{:?}: {:?}", male_or_female, numbers);
    }
}
```

這個打印:

```text
"female", [5, 6, 5]
"male", [9, 0, 10]
```

重要的一行是:`survey_hash.entry(item.0).or_insert(Vec::new()).push(item.1);`，所以如果它看到 "女"，就會檢查`HashMap`中是否已經有 "女"。如果沒有，它就會插入一個`Vec::new()`，然後把數字推入。如果它看到 "女性"已經在`HashMap`中，它將不會插入一個新的Vec，而只是將數字推入其中。

### HashSet和BTreeSet

`HashSet`實際上是一個只有key的`HashMap`。在[HashSet的頁面](https://doc.rust-lang.org/std/collections/struct.HashSet.html)上面有解釋。


`A hash set implemented as a HashMap where the value is ().` 所以這是一個`HashMap`，有鍵，沒有值。

如果你只是想知道一個鍵是否存在，或者不存在，你經常會使用`HashSet`。

想象一下，你有100個隨機數，每個數字在1和100之間。如果你這樣做，有些數字會出現不止一次，而有些數字根本不會出現。如果你把它們放到`HashSet`中，那麼你就會有一個所有出現的數字的列表。

```rust
use std::collections::HashSet;

fn main() {
    let many_numbers = vec![
        94, 42, 59, 64, 32, 22, 38, 5, 59, 49, 15, 89, 74, 29, 14, 68, 82, 80, 56, 41, 36, 81, 66,
        51, 58, 34, 59, 44, 19, 93, 28, 33, 18, 46, 61, 76, 14, 87, 84, 73, 71, 29, 94, 10, 35, 20,
        35, 80, 8, 43, 79, 25, 60, 26, 11, 37, 94, 32, 90, 51, 11, 28, 76, 16, 63, 95, 13, 60, 59,
        96, 95, 55, 92, 28, 3, 17, 91, 36, 20, 24, 0, 86, 82, 58, 93, 68, 54, 80, 56, 22, 67, 82,
        58, 64, 80, 16, 61, 57, 14, 11];

    let mut number_hashset = HashSet::new();

    for number in many_numbers {
        number_hashset.insert(number);
    }

    let hashset_length = number_hashset.len(); // The length tells us how many numbers are in it
    println!("There are {} unique numbers, so we are missing {}.", hashset_length, 100 - hashset_length);

    // Let's see what numbers we are missing
    let mut missing_vec = vec![];
    for number in 0..100 {
        if number_hashset.get(&number).is_none() { // If .get() returns None,
            missing_vec.push(number);
        }
    }

    print!("It does not contain: ");
    for number in missing_vec {
        print!("{} ", number);
    }
}
```

這個打印:

```text
There are 66 unique numbers, so we are missing 34.
It does not contain: 1 2 4 6 7 9 12 21 23 27 30 31 39 40 45 47 48 50 52 53 62 65 69 70 72 75 77 78 83 85 88 97 98 99
```

`BTreeSet`與`HashSet`相似，就像`BTreeMap`與`HashMap`相似一樣。如果我們把`HashSet`中的每一項都打印出來，就不知道順序是什麼了。

```rust
for entry in number_hashset { // 🚧
    print!("{} ", entry);
}
```

也許它能打印出這個。`67 28 42 25 95 59 87 11 5 81 64 34 8 15 13 86 10 89 63 93 49 41 46 57 60 29 17 22 74 43 32 38 36 76 71 18 14 84 61 16 35 90 56 54 91 19 94 44 3 0 68 80 51 92 24 20 82 26 58 33 55 96 37 66 79 73`. 但它幾乎不會再以同樣的方式打印。

在這裡也一樣，如果你決定需要訂購的話，很容易把你的`HashSet`改成`BTreeSet`。在我們的代碼中，我們只需要做兩處改動，就可以從`HashSet`切換到`BTreeSet`。

```rust
use std::collections::BTreeSet; // Change HashSet to BTreeSet

fn main() {
    let many_numbers = vec![
        94, 42, 59, 64, 32, 22, 38, 5, 59, 49, 15, 89, 74, 29, 14, 68, 82, 80, 56, 41, 36, 81, 66,
        51, 58, 34, 59, 44, 19, 93, 28, 33, 18, 46, 61, 76, 14, 87, 84, 73, 71, 29, 94, 10, 35, 20,
        35, 80, 8, 43, 79, 25, 60, 26, 11, 37, 94, 32, 90, 51, 11, 28, 76, 16, 63, 95, 13, 60, 59,
        96, 95, 55, 92, 28, 3, 17, 91, 36, 20, 24, 0, 86, 82, 58, 93, 68, 54, 80, 56, 22, 67, 82,
        58, 64, 80, 16, 61, 57, 14, 11];

    let mut number_btreeset = BTreeSet::new(); // Change HashSet to BTreeSet

    for number in many_numbers {
        number_btreeset.insert(number);
    }
    for entry in number_btreeset {
        print!("{} ", entry);
    }
}
```

現在會按順序打印。`0 3 5 8 10 11 13 14 15 16 17 18 19 20 22 24 25 26 28 29 32 33 34 35 36 37 38 41 42 43 44 46 49 51 54 55 56 57 58 59 60 61 63 64 66 67 68 71 73 74 76 79 80 81 82 84 86 87 89 90 91 92 93 94 95 96`.

### 二叉堆

`BinaryHeap`是一種有趣的集合類型，因為它大部分是無序的，但也有一點秩序。它把最大的元素放在前面，但其他元素是按任何順序排列的。

我們將用另一個元素列表來舉例，但這次數據少些。

```rust
use std::collections::BinaryHeap;

fn show_remainder(input: &BinaryHeap<i32>) -> Vec<i32> { // This function shows the remainder in the BinaryHeap. Actually an iterator would be
                                                         // faster than a function - we will learn them later.
    let mut remainder_vec = vec![];
    for number in input {
        remainder_vec.push(*number)
    }
    remainder_vec
}

fn main() {
    let many_numbers = vec![0, 5, 10, 15, 20, 25, 30]; // These numbers are in order

    let mut my_heap = BinaryHeap::new();

    for number in many_numbers {
        my_heap.push(number);
    }

    while let Some(number) = my_heap.pop() { // .pop() returns Some(number) if a number is there, None if not. It pops from the front
        println!("Popped off {}. Remaining numbers are: {:?}", number, show_remainder(&my_heap));
    }
}
```

這個打印:

```text
Popped off 30. Remaining numbers are: [25, 15, 20, 0, 10, 5]
Popped off 25. Remaining numbers are: [20, 15, 5, 0, 10]
Popped off 20. Remaining numbers are: [15, 10, 5, 0]
Popped off 15. Remaining numbers are: [10, 0, 5]
Popped off 10. Remaining numbers are: [5, 0]
Popped off 5. Remaining numbers are: [0]
Popped off 0. Remaining numbers are: []
```

你可以看到，0指數的數字總是最大的。25, 20, 15, 10, 5, 然後是0.

使用`BinaryHeap<(u8, &str)>`的一個好方法是用於一個事情的集合。這裡我們創建一個`BinaryHeap<(u8, &str)>`，其中`u8`是任務重要性的數字。`&str`是對要做的事情的描述。

```rust
use std::collections::BinaryHeap;

fn main() {
    let mut jobs = BinaryHeap::new();

    // Add jobs to do throughout the day
    jobs.push((100, "Write back to email from the CEO"));
    jobs.push((80, "Finish the report today"));
    jobs.push((5, "Watch some YouTube"));
    jobs.push((70, "Tell your team members thanks for always working hard"));
    jobs.push((30, "Plan who to hire next for the team"));

    while let Some(job) = jobs.pop() {
        println!("You need to: {}", job.1);
    }
}
```

這將一直打印:

```text
You need to: Write back to email from the CEO
You need to: Finish the report today
You need to: Tell your team members thanks for always working hard
You need to: Plan who to hire next for the team
You need to: Watch some YouTube
```

### VecDeque

`VecDeque`就是一個`Vec`，既能從前面彈出item，又能從後面彈出item。Rust有`VecDeque`是因為`Vec`很適合從後面(最後一個元素)彈出，但從前面彈出就不那麼好了。當你在`Vec`上使用`.pop()`的時候，它只是把右邊最後一個item取下來，其他的都不會動。但是如果你把它從其他部分取下來，右邊的所有元素都會向左移動一個位置。你可以在`.remove()`的描述中看到這一點。


```text
Removes and returns the element at position index within the vector, shifting all elements after it to the left.
```

所以如果你這樣做:

```rust
fn main() {
    let mut my_vec = vec![9, 8, 7, 6, 5];
    my_vec.remove(0);
}
```

它將刪除 `9`。索引1中的`8`將移到索引0，索引2中的`7`將移到索引1，以此類推。想象一下，一個大停車場，每當有一輛車離開時，右邊所有的車都要移過來。

比如說，這對計算機來說是一個*很大*的工作量。事實上，如果你在playground上運行它，它可能會因為工作太多而直接放棄。

```rust
fn main() {
    let mut my_vec = vec![0; 600_000];
    for i in 0..600000 {
        my_vec.remove(0);
    }
}
```

這是60萬個零的`Vec`。每次你用`remove(0)`，它就會把每個零向左移動一個空格。然後它就會做60萬次。

用`VecDeque`就不用擔心這個問題了。它通常比`Vec`慢一點，但如果你要在兩端都做事情，那麼它就快多了。你可以直接用`VecDeque::from`與`Vec`來創建一個。那麼我們上面的代碼就是這樣的。

```rust
use std::collections::VecDeque;

fn main() {
    let mut my_vec = VecDeque::from(vec![0; 600000]);
    for i in 0..600000 {
        my_vec.pop_front(); // pop_front is like .pop but for the front
    }
}
```

現在速度快了很多，在playground上，它在一秒內完成，而不是放棄。

在接下來的這個例子中，我們在一個`Vec`上做一些事。我們創建一個`VecDeque`，用`.push_front()`把它們放在前面，所以我們添加的第一個元素會在右邊。但是我們推送的每一個元素都是一個`(&str, bool)`:`&str`是描述, `false`表示還沒有完成。我們用`done()`函數從後面彈出一個元素，但是我們不想刪除它。相反，我們把`false`改成`true`，然後把它推到前面，這樣我們就可以保留它。

它看起來是這樣的:

```rust
use std::collections::VecDeque;

fn check_remaining(input: &VecDeque<(&str, bool)>) { // Each item is a (&str, bool)
    for item in input {
        if item.1 == false {
            println!("You must: {}", item.0);
        }
    }
}

fn done(input: &mut VecDeque<(&str, bool)>) {
    let mut task_done = input.pop_back().unwrap(); // pop off the back
    task_done.1 = true;                            // now it's done - mark as true
    input.push_front(task_done);                   // put it at the front now
}

fn main() {
    let mut my_vecdeque = VecDeque::new();
    let things_to_do = vec!["send email to customer", "add new product to list", "phone Loki back"];

    for thing in things_to_do {
        my_vecdeque.push_front((thing, false));
    }

    done(&mut my_vecdeque);
    done(&mut my_vecdeque);

    check_remaining(&my_vecdeque);

    for task in my_vecdeque {
        print!("{:?} ", task);
    }
}
```

這個打印:

```text
You must: phone Loki back
("add new product to list", true) ("send email to customer", true) ("phone Loki back", false)
```

## ?操作符

有一種更短的方法來處理`Result`(和`Option`)，它比`match`和`if let`更短。它叫做 "問號運算符"，就是`?`。在返回結果的函數後，可以加上`?`。這樣就會:

- 如果是`Ok`，返回`Result`裡面的內容。
- 如果是`Err`，則將錯誤傳回。

換句話說，它幾乎為你做了所有的事情。

我們可以用 `.parse()` 再試一次。我們將編寫一個名為 `parse_str` 的函數，試圖將 `&str` 變成 `i32`。它看起來像這樣:

```rust
use std::num::ParseIntError;

fn parse_str(input: &str) -> Result<i32, ParseIntError> {
    let parsed_number = input.parse::<i32>()?; // Here is the question mark
    Ok(parsed_number)
}

fn main() {}
```

這個函數接收一個 `&str`。如果是 `Ok`，則給出一個 `i32`，包裹在 `Ok` 中。如果是 `Err`，則返回 `ParseIntError`。然後我們嘗試解析這個數字，並加上`?`。也就是 "檢查是否錯誤，如果沒問題就給出Result裡面的內容"。如果有問題，就會返回錯誤並結束。但如果沒問題，就會進入下一行。下一行是`Ok()`裡面的數字。我們需要用`Ok`來包裝，因為返回的是`Result<i32, ParseIntError>`，而不是`i32`。

現在，我們可以試試我們的函數。讓我們看看它對`&str`的vec有什麼作用。


```rust
fn parse_str(input: &str) -> Result<i32, std::num::ParseIntError> {
    let parsed_number = input.parse::<i32>()?;
    Ok(parsed_number)
}

fn main() {
    let str_vec = vec!["Seven", "8", "9.0", "nice", "6060"];
    for item in str_vec {
        let parsed = parse_str(item);
        println!("{:?}", parsed);
    }
}
```

這個打印:

```text
Err(ParseIntError { kind: InvalidDigit })
Ok(8)
Err(ParseIntError { kind: InvalidDigit })
Err(ParseIntError { kind: InvalidDigit })
Ok(6060)
```

我們是怎麼找到`std::num::ParseIntError`的呢？一個簡單的方法就是再 "問"一下編譯器。

```rust
fn main() {
    let failure = "Not a number".parse::<i32>();
    failure.rbrbrb(); // ⚠️ Compiler: "What is rbrbrb()???"
}
```

編譯器不懂，說。

```text
error[E0599]: no method named `rbrbrb` found for enum `std::result::Result<i32, std::num::ParseIntError>` in the current scope
 --> src\main.rs:3:13
  |
3 |     failure.rbrbrb();
  |             ^^^^^^ method not found in `std::result::Result<i32, std::num::ParseIntError>`
```

所以`std::result::Result<i32, std::num::ParseIntError>`就是我們需要的簽名。

我們不需要寫 `std::result::Result`，因為 `Result` 總是 "在範圍內"(在範圍內 = 準備好使用)。Rust對我們經常使用的所有類型都是這樣做的，所以我們不必寫`std::result::Result`、`std::collections::Vec`等。

我們現在還沒有處理文件這樣的東西，所以?操作符看起來還不是太有用。但這裡有一個無用但快速的例子，說明你如何在單行上使用它。與其用 `.parse()` 創建一個 `i32`，不如做更多。我們將創建一個 `u16`，然後把它變成 `String`，再變成 `u32`，然後再變成 `String`，最後變成 `i32`。

```rust
use std::num::ParseIntError;

fn parse_str(input: &str) -> Result<i32, ParseIntError> {
    let parsed_number = input.parse::<u16>()?.to_string().parse::<u32>()?.to_string().parse::<i32>()?; // Add a ? each time to check and pass it on
    Ok(parsed_number)
}

fn main() {
    let str_vec = vec!["Seven", "8", "9.0", "nice", "6060"];
    for item in str_vec {
        let parsed = parse_str(item);
        println!("{:?}", parsed);
    }
}
```

這打印出同樣的東西，但這次我們在一行中處理了三個`Result`。稍後我們將對文件進行處理，因為它們總是返回`Result`，因為很多事情都可能出錯。

想象一下:你想打開一個文件，向它寫入，然後關閉它。首先你需要成功找到這個文件(這就是一個`Result`)。然後你需要成功地寫入它(那是一個`Result`)。對於`?`，你可以在一行上完成。

### When panic and unwrap are good

Rust有一個`panic!`的宏，你可以用它來讓程序崩潰。它使用起來很方便。

```rust
fn main() {
    panic!("Time to panic!");
}
```

運行程序時，會顯示信息`"Time to panic!"`。`thread 'main' panicked at 'Time to panic!', src\main.rs:2:3`

你會記得`src\main.rs`是目錄和文件名，`2:3`是行名和列名。有了這些信息，你就可以找到代碼並修復它。

`panic!`是一個很好用的宏，以確保你知道什麼時候有變化。例如，這個叫做`prints_three_things`的函數總是從一個向量中打印出索引[0]、[1]和[2]。這沒關係，因為我們總是給它一個有三個元素的向量。

```rust
fn prints_three_things(vector: Vec<i32>) {
    println!("{}, {}, {}", vector[0], vector[1], vector[2]);
}

fn main() {
    let my_vec = vec![8, 9, 10];
    prints_three_things(my_vec);
}
```

它打印出`8, 9, 10`，一切正常。

但試想一下，後來我們寫的代碼越來越多，忘記了`my_vec`只能有三個元素。現在`my_vec`在這部分有六個元素。

```rust
fn prints_three_things(vector: Vec<i32>) {
  println!("{}, {}, {}", vector[0], vector[1], vector[2]);
}

fn main() {
  let my_vec = vec![8, 9, 10, 10, 55, 99]; // Now my_vec has six things
  prints_three_things(my_vec);
}
```

不會發生錯誤，因為[0]和[1]和[2]都在這個較長的`Vec`裡面。但如果只能有三個元素呢？我們就不會知道有問題了，因為程序不會崩潰。我們應該這樣做:

```rust
fn prints_three_things(vector: Vec<i32>) {
    if vector.len() != 3 {
        panic!("my_vec must always have three items") // will panic if the length is not 3
    }
    println!("{}, {}, {}", vector[0], vector[1], vector[2]);
}

fn main() {
    let my_vec = vec![8, 9, 10];
    prints_three_things(my_vec);
}
```

現在我們知道，如果向量有6個元素，它應該要崩潰:

```rust
    // ⚠️
fn prints_three_things(vector: Vec<i32>) {
    if vector.len() != 3 {
        panic!("my_vec must always have three items")
    }
    println!("{}, {}, {}", vector[0], vector[1], vector[2]);
}

fn main() {
    let my_vec = vec![8, 9, 10, 10, 55, 99];
    prints_three_things(my_vec);
}
```

這樣我們就得到了`thread 'main' panicked at 'my_vec must always have three items', src\main.rs:8:9`。多虧了`panic!`，我們現在記得`my_vec`應該只有三個元素。所以`panic!`是一個很好的宏，可以在你的代碼中創建提醒。

還有三個與`panic!`類似的宏，你在測試中經常使用。它們分別是 `assert!`, `assert_eq!`, 和 `assert_ne!`.

下面是它們的意思。

- `assert!()`: 如果`()`裡面的部分不是真的, 程序就會崩潰.
- `assert_eq!()`:`()`裡面的兩個元素必須相等。
- `assert_ne!()`:`()`裡面的兩個元素必須不相等。(*ne*表示不相等)

一些例子。

```rust
fn main() {
    let my_name = "Loki Laufeyson";

    assert!(my_name == "Loki Laufeyson");
    assert_eq!(my_name, "Loki Laufeyson");
    assert_ne!(my_name, "Mithridates");
}
```

這不會有任何作用，因為三個斷言宏都沒有問題。(這就是我們想要的)

如果你願意，還可以加個提示信息。

```rust
fn main() {
    let my_name = "Loki Laufeyson";

    assert!(
        my_name == "Loki Laufeyson",
        "{} should be Loki Laufeyson",
        my_name
    );
    assert_eq!(
        my_name, "Loki Laufeyson",
        "{} and Loki Laufeyson should be equal",
        my_name
    );
    assert_ne!(
        my_name, "Mithridates",
        "You entered {}. Input must not equal Mithridates",
        my_name
    );
}
```

這些信息只有在程序崩潰時才會顯示。所以如果你運行這個。

```rust
fn main() {
    let my_name = "Mithridates";

    assert_ne!(
        my_name, "Mithridates",
        "You enter {}. Input must not equal Mithridates",
        my_name
    );
}
```

它將顯示:

```text
thread 'main' panicked at 'assertion failed: `(left != right)`
  left: `"Mithridates"`,
 right: `"Mithridates"`: You entered Mithridates. Input must not equal Mithridates', src\main.rs:4:5
```

所以它說 "你說左!=右，但左==右"。而且它顯示我們的信息說`You entered Mithridates. Input must not equal Mithridates`。

當你在寫程序的時候，想讓它在出現問題的時候崩潰，`unwrap`是個好注意。當你的代碼寫完後，把`unwrap`改成其他不會崩潰的東西就好了。

你也可以用`expect`，它和`unwrap`一樣，但是更好一些，因為它支持用戶自定義信息。教科書通常會給出這樣的建議:"如果你經常使用`.unwrap()`, 至少也要用`.expect()`來獲得更好的錯誤信息."

這樣會崩潰的:

```rust
   // ⚠️
fn get_fourth(input: &Vec<i32>) -> i32 {
    let fourth = input.get(3).unwrap();
    *fourth
}

fn main() {
    let my_vec = vec![9, 0, 10];
    let fourth = get_fourth(&my_vec);
}
```

錯誤信息是`thread 'main' panicked at 'called Option::unwrap() on a None value', src\main.rs:7:18`。

現在我們用`expect`來寫自己的信息。

```rust
   // ⚠️
fn get_fourth(input: &Vec<i32>) -> i32 {
    let fourth = input.get(3).expect("Input vector needs at least 4 items");
    *fourth
}

fn main() {
    let my_vec = vec![9, 0, 10];
    let fourth = get_fourth(&my_vec);
}
```

又崩潰了，但錯誤比較多。`thread 'main' panicked at 'Input vector needs at least 4 items', src\main.rs:7:18`. `.expect()`因為這個原因比`.unwrap()`要好一點，但是在`None`上還是會崩潰。現在這裡有一個錯誤的案例，一個函數試圖unwrap兩次。它需要一個`Vec<Option<i32>>`，所以可能每個部分都會有一個`Some<i32>`，也可能是一個`None`。

```rust
fn try_two_unwraps(input: Vec<Option<i32>>) {
    println!("Index 0 is: {}", input[0].unwrap());
    println!("Index 1 is: {}", input[1].unwrap());
}

fn main() {
    let vector = vec![None, Some(1000)]; // This vector has a None, so it will panic
    try_two_unwraps(vector);
}
```

消息是:``thread 'main' panicked at 'called `Option::unwrap()` on a `None` value', src\main.rs:2:32``。我們不檢查行號，就不知道是第一個`.unwrap()`還是第二個`.unwrap()`。最好是檢查一下長度，也不要unwrap。不過有了`.expect()`至少會好*一點*。下面是`.expect()`的情況：

```rust
fn try_two_unwraps(input: Vec<Option<i32>>) {
    println!("Index 0 is: {}", input[0].expect("The first unwrap had a None!"));
    println!("Index 1 is: {}", input[1].expect("The second unwrap had a None!"));
}

fn main() {
    let vector = vec![None, Some(1000)];
    try_two_unwraps(vector);
}
```

所以，這是好一點的。`thread 'main' panicked at 'The first unwrap had a None!', src\main.rs:2:32`. 我們也有行號，所以我們可以找到它。


如果你想一直有一個你想選擇的值，也可以用`unwrap_or`。如果你這樣做，它永遠不會崩潰。就是這樣的。


- 1)好，因為你的程序不會崩潰，但
- 2)如果你想讓程序在出現問題時崩潰，也許不好。

但通常我們都不希望自己的程序崩潰，所以`unwrap_or`是個不錯的方法。

```rust
fn main() {
    let my_vec = vec![8, 9, 10];

    let fourth = my_vec.get(3).unwrap_or(&0); // If .get doesn't work, we will make the value &0.
                                              // .get returns a reference, so we need &0 and not 0
                                              // You can write "let *fourth" with a * if you want fourth to be
                                              // a 0 and not a &0, but here we just print so it doesn't matter

    println!("{}", fourth);
}
```

這將打印出 `0`，因為 `.unwrap_or(&0)` 給出了一個 0，即使它是 `None`。

## 特性

我們以前見過trait:`Debug`、`Copy`、`Clone`都是trait。要給一個類型一個trait，就必須實現它。因為`Debug`和其他的trait都很常見，所以我們有自動實現的屬性。這就是當你寫下`#[derive(Debug)]`所發生的事情:你自動實現了`Debug`。

```rust
#[derive(Debug)]
struct MyStruct {
    number: usize,
}

fn main() {}
```

但是其他的特性就比較困難了，所以需要用`impl`手動實現。例如，`Add`(在`std::ops::Add`處找到)是用來累加兩個東西的。但是Rust並不知道你到底要怎麼累加，所以你必須告訴它。

```rust
struct ThingsToAdd {
    first_thing: u32,
    second_thing: f32,
}

fn main() {}
```

我們可以累加`first_thing`和`second_thing`，但我們需要提供更多信息。也許我們想要一個`f32`，所以像這樣:

```rust
// 🚧
let result = self.second_thing + self.first_thing as f32
```

但也許我們想要一個整數，所以像這樣:

```rust
// 🚧
let result = self.second_thing as u32 + self.first_thing
```

或者我們想把`self.first_thing`放在`self.second_thing`旁邊，這樣加。所以如果我們把55加到33.4，我們要看到的是5533.4，而不是88.4。

所以首先我們看一下如何創建一個trait。關於`trait`，要記住的重要一點是，它們是關於行為的。要創建一個trait，寫下單詞`trait`，然後創建一些函數。

```rust
struct Animal { // A simple struct - an Animal only has a name
    name: String,
}

trait Dog { // The dog trait gives some functionality
    fn bark(&self) { // It can bark
        println!("Woof woof!");
    }
    fn run(&self) { // and it can run
        println!("The dog is running!");
    }
}

impl Dog for Animal {} // Now Animal has the trait Dog

fn main() {
    let rover = Animal {
        name: "Rover".to_string(),
    };

    rover.bark(); // Now Animal can use bark()
    rover.run();  // and it can use run()
}
```

這個是可以的，但是我們不想打印 "狗在跑"。如果你想的話，你可以改變`trait`給你的方法，但你必須有相同的簽名。這意味著它需要接受同樣的東西，並返回同樣的東西。例如，我們可以改變 `.run()` 的方法，但我們必須遵循簽名。簽名說

```rust
// 🚧
fn run(&self) {
    println!("The dog is running!");
}
```

`fn run(&self)`的意思是 "fn `run()`以`&self`為參數，不返回任何內容"。所以你不能這樣做:

```rust
fn run(&self) -> i32 { // ⚠️
    5
}
```

Rust會說。

```text
   = note: expected fn pointer `fn(&Animal)`
              found fn pointer `fn(&Animal) -> i32`
```

但我們可以做到這一點。

```rust
struct Animal { // A simple struct - an Animal only has a name
    name: String,
}

trait Dog { // The dog trait gives some functionality
    fn bark(&self) { // It can bark
        println!("Woof woof!");
    }
    fn run(&self) { // and it can run
        println!("The dog is running!");
    }
}

impl Dog for Animal {
    fn run(&self) {
        println!("{} is running!", self.name);
    }
}

fn main() {
    let rover = Animal {
        name: "Rover".to_string(),
    };

    rover.bark(); // Now Animal can use bark()
    rover.run();  // and it can use run()
}
```

現在它打印的是 `Rover is running!`。這是好的，因為我們返回的是 `()`，或者說什麼都沒有，這就是trait所說的。


當你寫一個trait的時候，你可以直接寫函數簽名，但如果你這樣做，用戶將不得不寫函數實現。我們來試試。現在我們把`bark()`和`run()`改成只說`fn bark(&self);`和`fn run(&self);`。這不是一個完整的函數實現，所以必須由用戶來寫。

```rust
struct Animal {
    name: String,
}

trait Dog {
    fn bark(&self); // bark() says it needs a &self and returns nothing
    fn run(&self); // run() says it needs a &self and returns nothing.
                   // So now we have to write them ourselves.
}

impl Dog for Animal {
    fn bark(&self) {
        println!("{}, stop barking!!", self.name);
    }
    fn run(&self) {
        println!("{} is running!", self.name);
    }
}

fn main() {
    let rover = Animal {
        name: "Rover".to_string(),
    };

    rover.bark();
    rover.run();
}
```

所以，當你創建一個trait時，你必須思考:"我應該寫哪些功能？而用戶應該寫哪些函數？" 如果你認為用戶每次使用函數的方式應該是一樣的，那麼就把函數寫出來。如果你認為用戶會以不同的方式使用，那就寫出函數簽名即可。

所以，讓我們嘗試為我們的struct實現Display特性。首先我們將創建一個簡單的結構體:

```rust
struct Cat {
    name: String,
    age: u8,
}

fn main() {
    let mr_mantle = Cat {
        name: "Reggie Mantle".to_string(),
        age: 4,
    };
}
```

現在我們要打印`mr_mantle`。調試很容易得出。

```rust
#[derive(Debug)]
struct Cat {
    name: String,
    age: u8,
}

fn main() {
    let mr_mantle = Cat {
        name: "Reggie Mantle".to_string(),
        age: 4,
    };

    println!("Mr. Mantle is a {:?}", mr_mantle);
}
```

但Debug打印不是最漂亮的方式，因為它看起來是這樣的:

```text
Mr. Mantle is a Cat { name: "Reggie Mantle", age: 4 }
```

因此，如果我們想要更好的打印，就需要實現`Display`為`Cat`。在[https://doc.rust-lang.org/std/fmt/trait.Display.html](https://doc.rust-lang.org/std/fmt/trait.Display.html)上我們可以看到Display的信息，還有一個例子。它說

```rust
use std::fmt;

struct Position {
    longitude: f32,
    latitude: f32,
}

impl fmt::Display for Position {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({}, {})", self.longitude, self.latitude)
    }
}

fn main() {}
```

有些部分我們還不明白，比如`<'_>`和`f`在做什麼。但我們理解`Position`結構體:它只是兩個`f32`。我們也明白，`self.longitude`和`self.latitude`是結構體中的字段。所以，也許我們的結構體就可以用這個代碼，用`self.name`和`self.age`。另外，`write!`看起來很像`println!`，所以很熟悉。所以我們這樣寫。

```rust
use std::fmt;

struct Cat {
    name: String,
    age: u8,
}

impl fmt::Display for Cat {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} is a cat who is {} years old.", self.name, self.age)
    }
}

fn main() {}
```

讓我們添加一個`fn main()`。現在我們的代碼是這樣的。

```rust
use std::fmt;

struct Cat {
    name: String,
    age: u8,
}

impl fmt::Display for Cat {
  fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
      write!(f, "{} is a cat who is {} years old.", self.name, self.age)
  }
}

fn main() {
    let mr_mantle = Cat {
        name: "Reggie Mantle".to_string(),
        age: 4,
    };

    println!("{}", mr_mantle);
}
```

成功了! 現在，當我們使用`{}`打印時，我們得到`Reggie Mantle is a cat who is 4 years old.`。這看起來好多了。


順便說一下，如果你實現了`Display`，那麼你就可以免費得到`ToString`的特性。這是因為你使用`format!`宏來實現`.fmt()`函數，這讓你可以用`.to_string()`來創建一個`String`。所以我們可以做這樣的事情，我們把`reggie_mantle`傳給一個想要`String`的函數，或者其他任何東西。

```rust
use std::fmt;
struct Cat {
    name: String,
    age: u8,
}

impl fmt::Display for Cat {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} is a cat who is {} years old.", self.name, self.age)
    }
}

fn print_cats(pet: String) {
    println!("{}", pet);
}

fn main() {
    let mr_mantle = Cat {
        name: "Reggie Mantle".to_string(),
        age: 4,
    };

    print_cats(mr_mantle.to_string()); // Turn him into a String here
    println!("Mr. Mantle's String is {} letters long.", mr_mantle.to_string().chars().count()); // Turn him into chars and count them
}
```

這個打印:

```text
Reggie Mantle is a cat who is 4 years old.
Mr. Mantle's String is 42 letters long.
```




關於trait，要記住的是，它們是關於某些東西的行為。你的`struct`是如何行動的？它能做什麼？這就是trait的作用。如果你想想我們到目前為止所看到的一些trait，它們都是關於行為的:`Copy`是一個類型可以做的事情。`Display`也是一個類型能做的事情。`ToString`是另一個trait，它也是一個類型可以做的事情:它可以變化成一個`String`。在我們的 `Dog` trait中，*Dog*這個詞並不意味著你能做的事情，但它給出了一些讓它做事情的方法。
 你也可以為 `struct Poodle` 或 `struct Beagle` 實現它，它們都會得到 `Dog` 方法。


讓我們再看一個與單純行為聯繫更緊密的例子。我們將想象一個有一些簡單角色的幻想遊戲。一個是`Monster`，另外兩個是`Wizard`和`Ranger`。`Monster`只是有`health`，所以我們可以攻擊它，其他兩個還沒有什麼。但是我們做了兩個trait。一個叫`FightClose`，讓你近身作戰。另一個是`FightFromDistance`，讓你在遠處戰鬥。只有`Ranger`可以使用`FightFromDistance`。下面是它的樣子:

```rust
struct Monster {
    health: i32,
}

struct Wizard {}
struct Ranger {}

trait FightClose {
    fn attack_with_sword(&self, opponent: &mut Monster) {
        opponent.health -= 10;
        println!(
            "You attack with your sword. Your opponent now has {} health left.",
            opponent.health
        );
    }
    fn attack_with_hand(&self, opponent: &mut Monster) {
        opponent.health -= 2;
        println!(
            "You attack with your hand. Your opponent now has {} health left.",
            opponent.health
        );
    }
}
impl FightClose for Wizard {}
impl FightClose for Ranger {}

trait FightFromDistance {
    fn attack_with_bow(&self, opponent: &mut Monster, distance: u32) {
        if distance < 10 {
            opponent.health -= 10;
            println!(
                "You attack with your bow. Your opponent now has {} health left.",
                opponent.health
            );
        }
    }
    fn attack_with_rock(&self, opponent: &mut Monster, distance: u32) {
        if distance < 3 {
            opponent.health -= 4;
        }
        println!(
            "You attack with your rock. Your opponent now has {} health left.",
            opponent.health
        );
    }
}
impl FightFromDistance for Ranger {}

fn main() {
    let radagast = Wizard {};
    let aragorn = Ranger {};

    let mut uruk_hai = Monster { health: 40 };

    radagast.attack_with_sword(&mut uruk_hai);
    aragorn.attack_with_bow(&mut uruk_hai, 8);
}
```

這個打印:

```text
You attack with your sword. Your opponent now has 30 health left.
You attack with your bow. Your opponent now has 20 health left.
```

我們在trait裡面一直傳遞`self`，但是我們現在不能用它做什麼。那是因為 Rust 不知道什麼類型會使用它。它可能是一個 `Wizard`，也可能是一個 `Ranger`，也可能是一個叫做 `Toefocfgetobjtnode` 的新結構，或者其他任何東西。為了讓`self`具有一定的功能，我們可以在trait中添加必要的trait。比如說，如果我們想用`{:?}`打印，那麼我們就需要`Debug`。你只要把它寫在`:`(冒號)後面，就可以把它添加到trait中。現在我們的代碼是這樣的。


```rust
struct Monster {
    health: i32,
}

#[derive(Debug)] // Now Wizard has Debug
struct Wizard {
    health: i32, // Now Wizard has health
}
#[derive(Debug)] // So does Ranger
struct Ranger {
    health: i32, // So does Ranger
}

trait FightClose: std::fmt::Debug { // Now a type needs Debug to use FightClose
    fn attack_with_sword(&self, opponent: &mut Monster) {
        opponent.health -= 10;
        println!(
            "You attack with your sword. Your opponent now has {} health left. You are now at: {:?}", // We can now print self with {:?} because we have Debug
            opponent.health, &self
        );
    }
    fn attack_with_hand(&self, opponent: &mut Monster) {
        opponent.health -= 2;
        println!(
            "You attack with your hand. Your opponent now has {} health left.  You are now at: {:?}",
            opponent.health, &self
        );
    }
}
impl FightClose for Wizard {}
impl FightClose for Ranger {}

trait FightFromDistance: std::fmt::Debug { // We could also do trait FightFromDistance: FightClose because FightClose needs Debug
    fn attack_with_bow(&self, opponent: &mut Monster, distance: u32) {
        if distance < 10 {
            opponent.health -= 10;
            println!(
                "You attack with your bow. Your opponent now has {} health left.  You are now at: {:?}",
                opponent.health, self
            );
        }
    }
    fn attack_with_rock(&self, opponent: &mut Monster, distance: u32) {
        if distance < 3 {
            opponent.health -= 4;
        }
        println!(
            "You attack with your rock. Your opponent now has {} health left.  You are now at: {:?}",
            opponent.health, self
        );
    }
}
impl FightFromDistance for Ranger {}

fn main() {
    let radagast = Wizard { health: 60 };
    let aragorn = Ranger { health: 80 };

    let mut uruk_hai = Monster { health: 40 };

    radagast.attack_with_sword(&mut uruk_hai);
    aragorn.attack_with_bow(&mut uruk_hai, 8);
}
```

現在這個打印:

```text
You attack with your sword. Your opponent now has 30 health left. You are now at: Wizard { health: 60 }
You attack with your bow. Your opponent now has 20 health left.  You are now at: Ranger { health: 80 }
```

在真實的遊戲中，可能最好為每個類型重寫這個，因為`You are now at: Wizard { health: 60 }`看起來有點可笑。這也是為什麼trait裡面的方法通常很簡單，因為你不知道什麼類型會使用它。例如，你不能寫出 `self.0 += 10` 這樣的東西。但是這個例子表明，我們可以在我們正在寫的trait裡面使用其他的trait。當我們這樣做的時候，我們會得到一些我們可以使用的方法。



另外一種使用trait的方式是使用所謂的`trait bounds`。意思是 "通過一個trait進行限制"。trait限制很簡單，因為一個trait實際上不需要任何方法，或者說根本不需要任何東西。讓我們用類似但不同的東西重寫我們的代碼。這次我們的trait沒有任何方法，但我們有其他需要trait使用的函數。

```rust
use std::fmt::Debug;  // So we don't have to write std::fmt::Debug every time now

struct Monster {
    health: i32,
}

#[derive(Debug)]
struct Wizard {
    health: i32,
}
#[derive(Debug)]
struct Ranger {
    health: i32,
}

trait Magic{} // No methods for any of these traits. They are just trait bounds
trait FightClose {}
trait FightFromDistance {}

impl FightClose for Ranger{} // Each type gets FightClose,
impl FightClose for Wizard {}
impl FightFromDistance for Ranger{} // but only Ranger gets FightFromDistance
impl Magic for Wizard{}  // and only Wizard gets Magic

fn attack_with_bow<T: FightFromDistance + Debug>(character: &T, opponent: &mut Monster, distance: u32) {
    if distance < 10 {
        opponent.health -= 10;
        println!(
            "You attack with your bow. Your opponent now has {} health left.  You are now at: {:?}",
            opponent.health, character
        );
    }
}

fn attack_with_sword<T: FightClose + Debug>(character: &T, opponent: &mut Monster) {
    opponent.health -= 10;
    println!(
        "You attack with your sword. Your opponent now has {} health left. You are now at: {:?}",
        opponent.health, character
    );
}

fn fireball<T: Magic + Debug>(character: &T, opponent: &mut Monster, distance: u32) {
    if distance < 15 {
        opponent.health -= 20;
        println!("You raise your hands and cast a fireball! Your opponent now has {} health left. You are now at: {:?}",
    opponent.health, character);
    }
}

fn main() {
    let radagast = Wizard { health: 60 };
    let aragorn = Ranger { health: 80 };

    let mut uruk_hai = Monster { health: 40 };

    attack_with_sword(&radagast, &mut uruk_hai);
    attack_with_bow(&aragorn, &mut uruk_hai, 8);
    fireball(&radagast, &mut uruk_hai, 8);
}
```

這個打印出來的東西幾乎是一樣的。

```text
You attack with your sword. Your opponent now has 30 health left. You are now at: Wizard { health: 60 }
You attack with your bow. Your opponent now has 20 health left.  You are now at: Ranger { health: 80 }
You raise your hands and cast a fireball! Your opponent now has 0 health left. You are now at: Wizard { health: 60 }
```

所以你可以看到，當你使用traits時，有很多方法可以做同樣的事情。這一切都取決於什麼對你正在編寫的程序最有意義。

現在讓我們來看看如何實現一些在Rust中使用的主要trait。

### From trait

*From*是一個非常方便的trait，你知道這一點，因為你已經看到了很多。使用*From*，你可以從一個`&str`創建一個`String`，你也可以用許多其他類型創建多種類型。例如，Vec使用*From*來創建以下類型:

```text
From<&'_ [T]>
From<&'_ mut [T]>
From<&'_ str>
From<&'a Vec<T>>
From<[T; N]>
From<BinaryHeap<T>>
From<Box<[T]>>
From<CString>
From<Cow<'a, [T]>>
From<String>
From<Vec<NonZeroU8>>
From<Vec<T>>
From<VecDeque<T>>
```

這裡有很多`Vec::from()`我們還沒有用過。我們來做幾個，看看會怎麼樣:

```rust
use std::fmt::Display; // We will make a generic function to print them so we want Display

fn print_vec<T: Display>(input: &Vec<T>) { // Take any Vec<T> if type T has Display
    for item in input {
        print!("{} ", item);
    }
    println!();
}

fn main() {

    let array_vec = Vec::from([8, 9, 10]); // Try from an array
    print_vec(&array_vec);

    let str_vec = Vec::from("What kind of vec will I be?"); // An array from a &str? This will be interesting
    print_vec(&str_vec);

    let string_vec = Vec::from("What kind of vec will a String be?".to_string()); // Also from a String
    print_vec(&string_vec);
}
```

它打印的內容如下。

```text
8 9 10
87 104 97 116 32 107 105 110 100 32 111 102 32 118 101 99 32 119 105 108 108 32 73 32 98 101 63
87 104 97 116 32 107 105 110 100 32 111 102 32 118 101 99 32 119 105 108 108 32 97 32 83 116 114 105 110 103 32 98 101 63
```

如果從類型上看，第二個和第三個向量是`Vec<u8>`，也就是`&str`和`String`的字節。所以你可以看到`From`是非常靈活的，用的也很多。我們用自己的類型來試試。

我們將創建兩個結構體，然後為其中一個結構體實現`From`。一個結構體將是`City`，另一個結構體將是`Country`。我們希望能夠做到這一點。`let country_name = Country::from(vector_of_cities)`.

它看起來是這樣的:

```rust
#[derive(Debug)] // So we can print City
struct City {
    name: String,
    population: u32,
}

impl City {
    fn new(name: &str, population: u32) -> Self { // just a new function
        Self {
            name: name.to_string(),
            population,
        }
    }
}
#[derive(Debug)] // Country also needs to be printed
struct Country {
    cities: Vec<City>, // Our cities go in here
}

impl From<Vec<City>> for Country { // Note: we don't have to write From<City>, we can also do
                                   // From<Vec<City>>. So we can also implement on a type that
                                   // we didn't create
    fn from(cities: Vec<City>) -> Self {
        Self { cities }
    }
}

impl Country {
    fn print_cities(&self) { // function to print the cities in Country
        for city in &self.cities {
            // & because Vec<City> isn't Copy
            println!("{:?} has a population of {:?}.", city.name, city.population);
        }
    }
}

fn main() {
    let helsinki = City::new("Helsinki", 631_695);
    let turku = City::new("Turku", 186_756);

    let finland_cities = vec![helsinki, turku]; // This is the Vec<City>
    let finland = Country::from(finland_cities); // So now we can use From

    finland.print_cities();
}
```

這個將打印:

```text
"Helsinki" has a population of 631695.
"Turku" has a population of 186756.
```

你可以看到，`From`很容易從你沒有創建的類型中實現，比如`Vec`、`i32`等等。這裡還有一個例子，我們創建一個有兩個向量的向量。第一個向量存放偶數，第二個向量存放奇數。對於`From`，你可以給它一個`i32`的向量，它會把它變成`Vec<Vec<i32>>`:一個容納`i32`的向量。

```rust
use std::convert::From;

struct EvenOddVec(Vec<Vec<i32>>);

impl From<Vec<i32>> for EvenOddVec {
    fn from(input: Vec<i32>) -> Self {
        let mut even_odd_vec: Vec<Vec<i32>> = vec![vec![], vec![]]; // A vec with two empty vecs inside
                                                                    // This is the return value but first we must fill it
        for item in input {
            if item % 2 == 0 {
                even_odd_vec[0].push(item);
            } else {
                even_odd_vec[1].push(item);
            }
        }
        Self(even_odd_vec) // Now it is done so we return it as Self (Self = EvenOddVec)
    }
}

fn main() {
    let bunch_of_numbers = vec![8, 7, -1, 3, 222, 9787, -47, 77, 0, 55, 7, 8];
    let new_vec = EvenOddVec::from(bunch_of_numbers);

    println!("Even numbers: {:?}\nOdd numbers: {:?}", new_vec.0[0], new_vec.0[1]);
}
```

這個打印:

```text
Even numbers: [8, 222, 0, 8]
Odd numbers: [7, -1, 3, 9787, -47, 77, 55, 7]
```

像 `EvenOddVec` 這樣的類型可能最好是通用 `T`，這樣我們就可以使用許多數字類型。如果你想練習的話，你可以試著把這個例子做成通用的。

### 在函數中使用字符串和&str

有時你想讓一個函數可以同時接受 `String` 和 `&str`。你可以通過泛型和 `AsRef` 特性來實現這一點。`AsRef` 用於從一個類型向另一個類型提供引用。如果你看看 `String` 的文檔，你可以看到它對許多類型都有 `AsRef`。

[https://doc.rust-lang.org/std/string/struct.String.html](https://doc.rust-lang.org/std/string/struct.String.html)

下面是它們的一些函數簽名。

`AsRef<str>`:

```rust
// 🚧
impl AsRef<str> for String

fn as_ref(&self) -> &str
```

`AsRef<[u8]>`:

```rust
// 🚧
impl AsRef<[u8]> for String

fn as_ref(&self) -> &[u8]
```

`AsRef<OsStr>`:

```rust
// 🚧
impl AsRef<OsStr> for String

fn as_ref(&self) -> &OsStr
```

你可以看到，它需要`&self`，並給出另一個類型的引用。這意味著，如果你有一個通用類型T，你可以說它需要`AsRef<str>`。如果你這樣做，它將能夠使用一個`&str`和一個`String`。

我們先說說泛型函數。這個還不能用。

```rust
fn print_it<T>(input: T) {
    println!("{}", input) // ⚠️
}

fn main() {
    print_it("Please print me");
}
```

Rust說`error[E0277]: T doesn't implement std::fmt::Display`。所以我們會要求T實現Display。

```rust
use std::fmt::Display;

fn print_it<T: Display>(input: T) {
    println!("{}", input)
}

fn main() {
    print_it("Please print me");
}
```

現在可以用了，打印出`Please print me`。這是好的，但T仍然可以是多種類型。
可以是`i8`，也可以是`f32`，或者其他任何實現了`Display`的類型。我們加上`AsRef<str>`，現在T需要`AsRef<str>`和`Display`。

```rust
use std::fmt::Display;

fn print_it<T: AsRef<str> + Display>(input: T) {
    println!("{}", input)
}

fn main() {
    print_it("Please print me");
    print_it("Also, please print me".to_string());
    // print_it(7); <- This will not print
}
```

現在，它不會接受`i8`這樣的類型。

不要忘了，當函數變長時，你可以用`where`來寫不同的函數。如果我們加上Debug，那麼就會變成`fn print_it<T: AsRef<str> + Display + Debug>(input: T)`，這一行就很長了。所以我們可以這樣寫。

```rust
use std::fmt::{Debug, Display}; // add Debug

fn print_it<T>(input: T) // Now this line is easy to read
where
    T: AsRef<str> + Debug + Display, // and these traits are easy to read
{
    println!("{}", input)
}

fn main() {
    print_it("Please print me");
    print_it("Also, please print me".to_string());
}
```

## 鏈式方法

Rust是一種系統編程語言，就像C和C++一樣，它的代碼可以寫成獨立的命令，單獨成行，但它也有函數式風格。兩種風格都可以，但函數式通常比較短。下面以非函數式(稱為 "命令式")為例，讓`Vec`從1到10。

```rust
fn main() {
    let mut new_vec = Vec::new();
    let mut counter = 1;

    while counter < 11 {
        new_vec.push(counter);
        counter += 1;
    }

    println!("{:?}", new_vec);
}
```

這個打印`[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`。

而這裡是函數式風格的例子:

```rust
fn main() {
    let new_vec = (1..=10).collect::<Vec<i32>>();
    // Or you can write it like this:
    // let new_vec: Vec<i32> = (1..=10).collect();
    println!("{:?}", new_vec);
}
```

`.collect()`可以為很多類型做集合，所以我們要告訴它類型。

用函數式可以鏈接方法。"鏈接方法"的意思是把很多方法放在一個語句中。下面是一個很多方法鏈在一起的例子。

```rust
fn main() {
    let my_vec = vec![0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

    let new_vec = my_vec.into_iter().skip(3).take(4).collect::<Vec<i32>>();

    println!("{:?}", new_vec);
}
```

這樣就創建了一個`[3, 4, 5, 6]`的Vec。這一行的信息量很大，所以把每個方法放在新的一行上會有幫助。讓我們這樣做，以使其更容易閱讀。

```rust
fn main() {
    let my_vec = vec![0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

    let new_vec = my_vec
        .into_iter() // "iterate" over the items (iterate = work with each item inside it). into_iter() gives us owned values, not references
        .skip(3) // skip over three items: 0, 1, and 2
        .take(4) // take the next four: 3, 4, 5, and 6
        .collect::<Vec<i32>>(); // put them in a new Vec<i32>

    println!("{:?}", new_vec);
}
```

當你瞭解閉包和迭代器時，你可以最好地使用這種函數式。所以我們接下來將學習它們。

## 迭代器

迭代器是一個構造，它可以給你集合中的元素，一次一個。實際上，我們已經使用了很多迭代器:`for`循環給你一個迭代器。當你想在其他時候使用迭代器時，你必須選擇什麼樣的迭代器:

- `.iter()` 引用的迭代器
- `.iter_mut()` 可變引用的迭代器
- `.into_iter()` 值的迭代器(不是引用)

`for`循環其實只是一個擁有值的迭代器。這就是為什麼可以讓它變得可變，然後你可以在使用的時候改變值。

我們可以這樣使用迭代器。

```rust
fn main() {
    let vector1 = vec![1, 2, 3]; // we will use .iter() and .into_iter() on this one
    let vector1_a = vector1.iter().map(|x| x + 1).collect::<Vec<i32>>();
    let vector1_b = vector1.into_iter().map(|x| x * 10).collect::<Vec<i32>>();

    let mut vector2 = vec![10, 20, 30]; // we will use .iter_mut() on this one
    vector2.iter_mut().for_each(|x| *x +=100);

    println!("{:?}", vector1_a);
    println!("{:?}", vector2);
    println!("{:?}", vector1_b);
}
```

這個將打印:

```text
[2, 3, 4]
[110, 120, 130]
[10, 20, 30]
```

前兩個我們用了一個叫`.map()`的方法。這個方法可以讓你對每一個元素做一些事情，然後把它傳遞下去。最後我們用的是一個叫`.for_each()`的方法。這個方法只是讓你對每一個元素做一些事情。`.iter_mut()`加上`for_each()`基本上就是一個`for`的循環。在每一個方法裡面，我們可以給每一個元素起一個名字(我們剛才叫它 `x`)，然後用它來改變它。這些被稱為閉包，我們將在下一節學習它們。

讓我們再來看看它們，一次一個。

首先我們用`.iter()`對`vector1`進行引用。我們給每個元素都加了1，並使其成為一個新的Vec。`vector1`還活著，因為我們只用了引用:我們沒有按值取。現在我們有 `vector1`，還有一個新的 Vec 叫 `vector1_a`。因為`.map()`只是傳遞了它，所以我們需要使用`.collect()`把它變成一個`Vec`。

然後我們用`into_iter`從`vector1`中按值得到一個迭代器。這樣就破壞了`vector1`，因為這就是`into_iter()`的作用。所以我們做了`vector1_b`之後，就不能再使用`vector1`了。

最後我們在`vector2`上使用`.iter_mut()`。它是可變的，所以我們不需要使用`.collect()`來創建一個新的Vec。相反，我們用可變引用改變同一Vec中的值。所以`vector2`仍然存在。因為我們不需要一個新的Vec，我們使用`for_each`:它就像一個`for`循環。


### 迭代器如何工作

迭代器的工作原理是使用一個叫做 `.next()` 的方法，它給出一個 `Option`。當你使用迭代器時，Rust會一遍又一遍地調用`next()`。如果得到 `Some`，它就會繼續前進。如果得到 `None`，它就停止。

你還記得 `assert_eq!` 宏嗎？在文檔中，你經常看到它。這裡它展示了迭代器的工作原理。

```rust
fn main() {
    let my_vec = vec!['a', 'b', '거', '柳']; // Just a regular Vec

    let mut my_vec_iter = my_vec.iter(); // This is an Iterator type now, but we haven't called it yet

    assert_eq!(my_vec_iter.next(), Some(&'a'));  // Call the first item with .next()
    assert_eq!(my_vec_iter.next(), Some(&'b'));  // Call the next
    assert_eq!(my_vec_iter.next(), Some(&'거')); // Again
    assert_eq!(my_vec_iter.next(), Some(&'柳')); // Again
    assert_eq!(my_vec_iter.next(), None);        // Nothing is left: just None
    assert_eq!(my_vec_iter.next(), None);        // You can keep calling .next() but it will always be None
}
```

為自己的struct或enum實現`Iterator`並不難。首先我們創建一個書庫，想一想。

```rust
#[derive(Debug)] // we want to print it with {:?}
struct Library {
    library_type: LibraryType, // this is our enum
    books: Vec<String>, // list of books
}

#[derive(Debug)]
enum LibraryType { // libraries can be city libraries or country libraries
    City,
    Country,
}

impl Library {
    fn add_book(&mut self, book: &str) { // we use add_book to add new books
        self.books.push(book.to_string()); // we take a &str and turn it into a String, then add it to the Vec
    }

    fn new() -> Self { // this creates a new Library
        Self {
            library_type: LibraryType::City, // most are in the city so we'll choose City
                                             // most of the time
            books: Vec::new(),
        }
    }
}

fn main() {
    let mut my_library = Library::new(); // make a new library
    my_library.add_book("The Doom of the Darksword"); // add some books
    my_library.add_book("Demian - die Geschichte einer Jugend");
    my_library.add_book("구운몽");
    my_library.add_book("吾輩は貓である");

    println!("{:?}", my_library.books); // we can print our list of books
}
```

這很好用。現在我們想為庫實現`Iterator`，這樣我們就可以在`for`循環中使用它。現在如果我們嘗試 `for` 循環，它就無法工作。

```rust
for item in my_library {
    println!("{}", item); // ⚠️
}
```

它說:

```text
error[E0277]: `Library` is not an iterator
  --> src\main.rs:47:16
   |
47 |    for item in my_library {
   |                ^^^^^^^^^^ `Library` is not an iterator
   |
   = help: the trait `std::iter::Iterator` is not implemented for `Library`
   = note: required by `std::iter::IntoIterator::into_iter`
```

但是我們可以用`impl Iterator for Library`把庫做成迭代器。`Iterator`trait的信息在標準庫中。[https://doc.rust-lang.org/std/iter/trait.Iterator.html](https://doc.rust-lang.org/std/iter/trait.Iterator.html)

在頁面的左上方寫著:`Associated Types: Item`和`Required Methods: next`。"關聯類型"的意思是 "一起使用的類型"。我們的關聯類型將是`String`，因為我們希望迭代器給我們提供String。

在頁面中，它有一個看起來像這樣的例子。

```rust
// an iterator which alternates between Some and None
struct Alternate {
    state: i32,
}

impl Iterator for Alternate {
    type Item = i32;

    fn next(&mut self) -> Option<i32> {
        let val = self.state;
        self.state = self.state + 1;

        // if it's even, Some(i32), else None
        if val % 2 == 0 {
            Some(val)
        } else {
            None
        }
    }
}

fn main() {}
```

你可以看到`impl Iterator for Alternate`下面寫著`type Item = i32`。這就是關聯類型。我們的迭代器將針對我們的書籍列表，這是一個`Vec<String>`。當我們調用next的時候。
 它將給我們一個`String`。所以我們就寫`type Item = String;`。這就是關聯項。

為了實現 `Iterator`，你需要寫 `fn next()` 函數。這是你決定迭代器應該做什麼的地方。對於我們的 `Library`，我們首先希望它給我們最後一本書。所以我們將`match`與`.pop()`一起，如果是`Some`的話，就把最後一項去掉。我們還想為每個元素打印 "is found!"。現在它看起來像這樣:

```rust
#[derive(Debug, Clone)]
struct Library {
    library_type: LibraryType,
    books: Vec<String>,
}

#[derive(Debug, Clone)]
enum LibraryType {
    City,
    Country,
}

impl Library {
    fn add_book(&mut self, book: &str) {
        self.books.push(book.to_string());
    }

    fn new() -> Self {
        Self {
            library_type: LibraryType::City,
            // most of the time
            books: Vec::new(),
        }
    }
}

impl Iterator for Library {
    type Item = String;

    fn next(&mut self) -> Option<String> {
        match self.books.pop() {
            Some(book) => Some(book + " is found!"), // Rust allows String + &str
            None => None,
        }
    }
}

fn main() {
    let mut my_library = Library::new();
    my_library.add_book("The Doom of the Darksword");
    my_library.add_book("Demian - die Geschichte einer Jugend");
    my_library.add_book("구운몽");
    my_library.add_book("吾輩は貓である");

    for item in my_library.clone() { // we can use a for loop now. Give it a clone so Library won't be destroyed
        println!("{}", item);
    }
}
```

這個打印:

```text
吾輩は貓である is found!
구운몽 is found!
Demian - die Geschichte einer Jugend is found!
The Doom of the Darksword is found!
```

## 閉包

閉包就像快速函數，不需要名字。有時它們被稱為lambda。Closures很容易辨識，因為它們使用`||`而不是`()`。它們在 Rust 中非常常見，一旦你學會了使用它們，你就會愛不釋手。

你可以將一個閉包綁定到一個變量上，然後當你使用它時，它看起來就像一個函數一樣。

```rust
fn main() {
    let my_closure = || println!("This is a closure");
    my_closure();
}
```

所以這個閉包什麼都不需要:`||`，並打印一條信息。`This is a closure`.

在`||`之間我們可以添加輸入變量和類型，就像在`()`裡面添加函數一樣。

```rust
fn main() {
    let my_closure = |x: i32| println!("{}", x);

    my_closure(5);
    my_closure(5+5);
}
```

這個打印:

```text
5
10
```

當閉包變得更復雜時，你可以添加一個代碼塊。那就可以隨心所欲的長。

```rust
fn main() {
    let my_closure = || {
        let number = 7;
        let other_number = 10;
        println!("The two numbers are {} and {}.", number, other_number);
          // This closure can be as long as we want, just like a function.
    };

    my_closure();
}
```

但是閉包是特殊的，因為它可以接受閉包之外的變量，即使你只寫`||`。所以你可以這樣做:

```rust
fn main() {
    let number_one = 6;
    let number_two = 10;

    let my_closure = || println!("{}", number_one + number_two);
    my_closure();
}
```

所以這就打印出了`16`。你不需要在 `||` 中放入任何東西，因為它可以直接取 `number_one` 和 `number_two` 並添加它們。

順便說一下，這就是**closure**這個名字的由來，因為它們會取變量並將它們 "包圍"在裡面。如果你想很正確的說。

- 一個`||`如果不把變量從外面包圍起來 那就是一個 "匿名函數". 匿名的意思是 "沒有名字"。它的工作原理更像一個普通函數。
- `||` 從外部包圍變量的函數是 "closure"。它把周圍的變量 "封閉"起來使用。

但是人們經常會把所有的`||`函數都叫做閉包，所以你不用擔心名字的問題。我們只對任何帶有`||`的函數說 "closure"，但請記住，它可能意味著一個 "匿名函數"。

為什麼要知道這兩者的區別呢？因為匿名函數其實和有名字的函數做的機器代碼是一樣的。它們給人的感覺是 "高層抽象"，所以有時候大家會覺得機器代碼會很複雜。但是Rust用它生成的機器碼和普通函數一樣快。


所以我們再來看看閉包能做的一些事情。你也可以這樣做:

```rust
fn main() {
    let number_one = 6;
    let number_two = 10;

    let my_closure = |x: i32| println!("{}", number_one + number_two + x);
    my_closure(5);
}
```

這個閉包取`number_one`和`number_two`。我們還給了它一個新的變量 `x`，並說 `x` 是 5.然後它把這三個加在一起打印 `21`。

通常在Rust中，你會在一個方法裡面看到閉包，因為裡面有一個閉包是非常方便的。我們在上一節的 `.map()` 和 `.for_each()` 中看到了閉包。在那一節中，我們寫了 `|x|` 來引入迭代器中的下一個元素，這就是一個閉包。

下面再舉一個例子:我們知道，如果`unwrap`不起作用，可以用`unwrap_or`方法給出一個值。之前我們寫的是:`let fourth = my_vec.get(3).unwrap_or(&0);`。但是還有一個`unwrap_or_else`方法，裡面有一個閉包。所以你可以這樣做:

```rust
fn main() {
    let my_vec = vec![8, 9, 10];

    let fourth = my_vec.get(3).unwrap_or_else(|| { // try to unwrap. If it doesn't work,
        if my_vec.get(0).is_some() {               // see if my_vec has something at index [0]
            &my_vec[0]                             // Give the number at index 0 if there is something
        } else {
            &0 // otherwise give a &0
        }
    });

    println!("{}", fourth);
}
```

當然，閉包也可以很簡單。例如，你可以只寫`let fourth = my_vec.get(3).unwrap_or_else(|| &0);`。你不需要總是因為有一個閉包就使用`{}`並寫出複雜的代碼。只要你把`||`放進去，編譯器就知道你放了你需要的閉包。

最常用的閉包方法可能是`.map()`。我們再來看看它。下面是一種使用方法。

```rust
fn main() {
    let num_vec = vec![2, 4, 6];

    let double_vec = num_vec        // take num_vec
        .iter()                     // iterate over it
        .map(|number| number * 2)   // for each item, multiply by two
        .collect::<Vec<i32>>();     // then make a new Vec from this
    println!("{:?}", double_vec);
}
```

另一個很好的例子是在`.enumerate()`之後使用`.for_each()`。`.enumerate()`方法給出一個帶有索引號和元素的迭代器。例如:`[10, 9, 8]`變成`(0, 10), (1, 9), (2, 8)`。這裡每個項的類型是`(usize, i32)`。所以你可以這樣做:

```rust
fn main() {
    let num_vec = vec![10, 9, 8];

    num_vec
        .iter()      // iterate over num_vec
        .enumerate() // get (index, number)
        .for_each(|(index, number)| println!("Index number {} has number {}", index, number)); // do something for each one
}
```

這個將打印:

```text
Index number 0 has number 10
Index number 1 has number 9
Index number 2 has number 8
```

在這種情況下，我們用`for_each`代替`map`。`map`是用於對**每個元素做一些事情，並將其傳遞出去，而`for_each`是當你看到每個元素**時做一些事情。另外，`map`不做任何事情，除非你使用`collect`這樣的方法。

其實，這就是迭代器的有趣之處。如果你嘗試`map`而不使用`collect`這樣的方法，編譯器會告訴你，它什麼也不做。它不會崩潰，但編譯器會告訴你，你什麼都沒做。

```rust
fn main() {
    let num_vec = vec![10, 9, 8];

    num_vec
        .iter()
        .enumerate()
        .map(|(index, number)| println!("Index number {} has number {}", index, number));

}
```

它說:

```text
warning: unused `std::iter::Map` that must be used
 --> src\main.rs:4:5
  |
4 | /     num_vec
5 | |         .iter()
6 | |         .enumerate()
7 | |         .map(|(index, number)| println!("Index number {} has number {}", index, number));
  | |_________________________________________________________________________________________^
  |
  = note: `#[warn(unused_must_use)]` on by default
  = note: iterators are lazy and do nothing unless consumed
```

這是一個**警告**，所以這不是一個錯誤:程序運行正常。但是為什麼num_vec沒有任何作用呢？我們可以看看類型就知道了。

- `let num_vec = vec![10, 9, 8];` 現在是一個`Vec<i32>`。
- `.iter()` 現在是一個 `Iter<i32>`。所以它是一個迭代器，其元素為 `i32`。

- `.enumerate()`現在是一個`Enumerate<Iter<i32>>`型。所以它是`Enumerate`型的`Iter`型的`i32`。
- `.map()`現在是一個`Map<Enumerate<Iter<i32>>>`的類型。所以它是一個類型`Map`的類型`Enumerate`的類型`Iter`的類型`i32`。

我們所做的只是做了一個越來越複雜的結構。所以這個`Map<Enumerate<Iter<i32>>>`是一個準備好了的結構，但只有當我們告訴它要做什麼的時候，它才會去做。Rust這樣做是因為它需要保證足夠快。它不想這樣做:

- 遍歷Vec中所有的`i32`
- 然後從迭代器中枚舉出所有的`i32`
- 然後將所有列舉的`i32`映射過來

Rust 只想做一次計算，所以它創建結構並等待。然後，如果我們說`.collect::<Vec<i32>>()`，它知道該怎麼做，並開始移動。這就是`iterators are lazy and do nothing unless consumed`的意思。迭代器在你 "消耗"它們(用完它們)之前不會做任何事情。


你甚至可以用`.collect()`創建像`HashMap`這樣複雜的東西，所以它非常強大。下面是一個如何將兩個向量放入`HashMap`的例子。首先我們把兩個向量創建出來，然後我們會對它們使用`.into_iter()`來得到一個值的迭代器。然後我們使用`.zip()`方法。這個方法將兩個迭代器連接在一起，就像拉鍊一樣。最後，我們使用`.collect()`來創建`HashMap`。

下面是代碼。

```rust
use std::collections::HashMap;

fn main() {
    let some_numbers = vec![0, 1, 2, 3, 4, 5]; // a Vec<i32>
    let some_words = vec!["zero", "one", "two", "three", "four", "five"]; // a Vec<&str>

    let number_word_hashmap = some_numbers
        .into_iter()                 // now it is an iter
        .zip(some_words.into_iter()) // inside .zip() we put in the other iter. Now they are together.
        .collect::<HashMap<_, _>>();

    println!("For key {} we get {}.", 2, number_word_hashmap.get(&2).unwrap());
}
```

這個將打印:

```text
For key 2 we get two.
```

你可以看到，我們寫了 `<HashMap<_, _>>`，因為這足以讓 Rust 決定 `HashMap<i32, &str>` 的類型。如果你想寫 `.collect::<HashMap<i32, &str>>();`也行，也可以這樣寫:

```rust
use std::collections::HashMap;

fn main() {
    let some_numbers = vec![0, 1, 2, 3, 4, 5]; // a Vec<i32>
    let some_words = vec!["zero", "one", "two", "three", "four", "five"]; // a Vec<&str>
    let number_word_hashmap: HashMap<_, _> = some_numbers  // Because we tell it the type here...
        .into_iter()
        .zip(some_words.into_iter())
        .collect(); // we don't have to tell it here
}
```

還有一種方法，就像`.enumerate()`的`char`。`char_indices()`. (Indices的意思是 "索引")。你用它的方法是一樣的。假設我們有一個由3位數組成的大字符串。

```rust
fn main() {
    let numbers_together = "140399923481800622623218009598281";

    for (index, number) in numbers_together.char_indices() {
        match (index % 3, number) {
            (0..=1, number) => print!("{}", number), // just print the number if there is a remainder
            _ => print!("{}\t", number), // otherwise print the number with a tab space
        }
    }
}
```

打印`140     399     923     481     800     622     623     218     009     598    281`。


### 閉包中的|_|

有時你會在一個閉包中看到 `|_|`。這意味著這個閉包需要一個參數(比如 `x`)，但你不想使用它。所以 `|_|` 意味著 "好吧，這個閉包需要一個參數，但我不會給它一個名字，因為我不關心它"。

下面是一個錯誤的例子，當你不這樣做的時候。

```rust
fn main() {
    let my_vec = vec![8, 9, 10];

    println!("{:?}", my_vec.iter().for_each(|| println!("We didn't use the variables at all"))); // ⚠️
}
```

Rust說

```text
error[E0593]: closure is expected to take 1 argument, but it takes 0 arguments
  --> src\main.rs:28:36
   |
28 |     println!("{:?}", my_vec.iter().for_each(|| println!("We didn't use the variables at all")));
   |                                    ^^^^^^^^ -- takes 0 arguments
   |                                    |
   |                                    expected closure that takes 1 argument
```

編譯器其實給你一些幫助。

```text
help: consider changing the closure to take and ignore the expected argument
   |
28 |     println!("{:?}", my_vec.iter().for_each(|_| println!("We didn't use the variables at all")));
```

這是很好的建議。如果你把`||`改成`|_|`就可以了。

### 閉包和迭代器的有用方法

一旦你熟悉了閉包，Rust就會成為一種非常有趣的語言。有了閉包，你可以將方法互相*鏈接*起來，用很少的代碼做很多事情。下面是一些我們還沒有見過的閉包和使用閉包的方法。

`.filter()`: 這可以讓你在迭代器中保留你想保留的元素。讓我們過濾一年中的月份。

```rust
fn main() {
    let months = vec!["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

    let filtered_months = months
        .into_iter()                         // make an iter
        .filter(|month| month.len() < 5)     // We don't want months more than 5 bytes in length.
                                             // We know that each letter is one byte so .len() is fine
        .filter(|month| month.contains("u")) // Also we only like months with the letter u
        .collect::<Vec<&str>>();

    println!("{:?}", filtered_months);
}
```

這個打印`["June", "July"]`。



`.filter_map()`. 這個叫做`filter_map()`，因為它做了`.filter()`和`.map()`。閉包必須返回一個 `Option<T>`，然後對每個`Option`, 如果是 `Some`, `filter_map()`將取出它的值。所以比如說你`.filter_map()`一個`vec![Some(2), None, Some(3)]`，它就會返回`[2, 3]`。

我們將用一個`Company`結構體來寫一個例子。每個公司都有一個`name`，所以這個字段是`String`，但是CEO可能最近已經辭職了。所以`ceo`字段是`Option<String>`。我們會`.filter_map()`過一些公司，只保留CEO名字。

```rust
struct Company {
    name: String,
    ceo: Option<String>,
}

impl Company {
    fn new(name: &str, ceo: &str) -> Self {
        let ceo = match ceo {
            "" => None,
            name => Some(name.to_string()),
        }; // ceo is decided, so now we return Self
        Self {
            name: name.to_string(),
            ceo,
        }
    }

    fn get_ceo(&self) -> Option<String> {
        self.ceo.clone() // Just returns a clone of the CEO (struct is not Copy)
    }
}

fn main() {
    let company_vec = vec![
        Company::new("Umbrella Corporation", "Unknown"),
        Company::new("Ovintiv", "Doug Suttles"),
        Company::new("The Red-Headed League", ""),
        Company::new("Stark Enterprises", ""),
    ];

    let all_the_ceos = company_vec
        .into_iter()
        .filter_map(|company| company.get_ceo()) // filter_map needs Option<T>
        .collect::<Vec<String>>();

    println!("{:?}", all_the_ceos);
}
```

這就打印出了`["Unknown", "Doug Suttles"]`。

既然 `.filter_map()` 需要 `Option`，那麼 `Result` 呢？沒問題:有一個叫做 `.ok()` 的方法，可以把 `Result` 變成 `Option`。之所以叫`.ok()`，是因為它能發送的只是`Ok`的結果(`Err`的信息沒有了)。你記得`Option`是`Option<T>`，而`Result`是`Result<T, E>`，同時有`Ok`和`Err`的信息。所以當你使用`.ok()`時，任何`Err`的信息都會丟失，變成`None`。

使用 `.parse()` 是一個很簡單的例子，我們嘗試解析一些用戶輸入。`.parse()`在這裡接受一個`&str`，並試圖把它變成一個`f32`。它返回一個 `Result`，但我們使用的是 `filter_map()`，所以我們只需拋出錯誤。`Err`的任何內容都會變成`None`，並被`.filter_map()`過濾掉。

```rust
fn main() {
    let user_input = vec!["8.9", "Nine point nine five", "8.0", "7.6", "eleventy-twelve"];

    let actual_numbers = user_input
        .into_iter()
        .filter_map(|input| input.parse::<f32>().ok())
        .collect::<Vec<f32>>();

    println!("{:?}", actual_numbers);
}
```

將打印: `[8.9, 8.0, 7.6]`。

與`.ok()`相對的是`.ok_or()`和`ok_or_else()`。這樣就把`Option`變成了`Result`。之所以叫`.ok_or()`，是因為`Result`給出了一個`Ok`**或**`Err`，所以你必須讓它知道`Err`的值是多少。這是因為`None`中的`Option`沒有任何信息。另外，你現在可以看到，這些方法名稱中的*else*部分意味著它有一個閉包。

我們可以把我們的`Option`從`Company`結構中取出來，然後這樣把它變成一個`Result`。對於長期的錯誤處理，最好是創建自己的錯誤類型。
 但是現在我們只是給它一個錯誤信息，所以它就變成了`Result<String, &str>`。

```rust
// Everything before main() is exactly the same
struct Company {
    name: String,
    ceo: Option<String>,
}

impl Company {
    fn new(name: &str, ceo: &str) -> Self {
        let ceo = match ceo {
            "" => None,
            name => Some(name.to_string()),
        };
        Self {
            name: name.to_string(),
            ceo,
        }
    }

    fn get_ceo(&self) -> Option<String> {
        self.ceo.clone()
    }
}

fn main() {
    let company_vec = vec![
        Company::new("Umbrella Corporation", "Unknown"),
        Company::new("Ovintiv", "Doug Suttles"),
        Company::new("The Red-Headed League", ""),
        Company::new("Stark Enterprises", ""),
    ];

    let mut results_vec = vec![]; // Pretend we need to gather error results too

    company_vec
        .iter()
        .for_each(|company| results_vec.push(company.get_ceo().ok_or("No CEO found")));

    for item in results_vec {
        println!("{:?}", item);
    }
}
```

這行是最大的變化:

```rust
// 🚧
.for_each(|company| results_vec.push(company.get_ceo().ok_or("No CEO found")));
```

它的意思是:"每家公司，用`get_ceo()`. 如果你得到了，那就把`Ok`裡面的數值傳給你。如果沒有，就在`Err`裡面傳遞 "沒有找到CEO"。然後把這個推到vec裡。"

所以當我們打印`results_vec`的時候，就會得到這樣的結果。

```text
Ok("Unknown")
Ok("Doug Suttles")
Err("No CEO found")
Err("No CEO found")
```

所以現在我們有了所有四個條目。現在讓我們使用 `.ok_or_else()`，這樣我們就可以使用一個閉包，並得到一個更好的錯誤信息。現在我們有空間使用`format!`來創建一個`String`，並將公司名稱放在其中。然後我們返回`String`。

```rust
// Everything before main() is exactly the same
struct Company {
    name: String,
    ceo: Option<String>,
}

impl Company {
    fn new(name: &str, ceo: &str) -> Self {
        let ceo = match ceo {
            "" => None,
            name => Some(name.to_string()),
        };
        Self {
            name: name.to_string(),
            ceo,
        }
    }

    fn get_ceo(&self) -> Option<String> {
        self.ceo.clone()
    }
}

fn main() {
    let company_vec = vec![
        Company::new("Umbrella Corporation", "Unknown"),
        Company::new("Ovintiv", "Doug Suttles"),
        Company::new("The Red-Headed League", ""),
        Company::new("Stark Enterprises", ""),
    ];

    let mut results_vec = vec![];

    company_vec.iter().for_each(|company| {
        results_vec.push(company.get_ceo().ok_or_else(|| {
            let err_message = format!("No CEO found for {}", company.name);
            err_message
        }))
    });

    for item in results_vec {
        println!("{:?}", item);
    }
}
```

這樣一來，我們就有了。

```text
Ok("Unknown")
Ok("Doug Suttles")
Err("No CEO found for The Red-Headed League")
Err("No CEO found for Stark Enterprises")
```


`.and_then()`是一個有用的方法，它接收一個`Option`，然後讓你對它的值做一些事情，並把它傳遞出去。所以它的輸入是一個 `Option`，輸出也是一個 `Option`。這有點像一個安全的 "解包，然後做一些事情，然後再包"。

一個簡單的例子是，我們使用 `.get()` 從一個 vec 中得到一個數字，因為它返回一個 `Option`。現在我們可以把它傳給 `and_then()`，如果它是 `Some`，我們可以對它做一些數學運算。如果是`None`，那麼`None`就會被傳遞過去。

```rust
fn main() {
    let new_vec = vec![8, 9, 0]; // just a vec with numbers

    let number_to_add = 5;       // use this in the math later
    let mut empty_vec = vec![];  // results go in here


    for index in 0..5 {
        empty_vec.push(
            new_vec
               .get(index)
                .and_then(|number| Some(number + 1))
                .and_then(|number| Some(number + number_to_add))
        );
    }
    println!("{:?}", empty_vec);
}
```

這就打印出了`[Some(14), Some(15), Some(6), None, None]`。你可以看到`None`並沒有被過濾掉，只是傳遞了。




`.and()`有點像`Option`的`bool`。你可以匹配很多個`Option`，如果它們都是`Some`，那麼它會給出最後一個。而如果其中一個是`None`，那麼就會給出`None`。

首先這裡有一個`bool`的例子來幫助想象。你可以看到，如果你用的是`&&`(和)，哪怕是一個`false`，也會讓一切`false`。

```rust
fn main() {
    let one = true;
    let two = false;
    let three = true;
    let four = true;

    println!("{}", one && three); // prints true
    println!("{}", one && two && three && four); // prints false
}
```

現在這裡的`.and()`也是一樣的。想象一下，我們做了五次操作，並把結果放在一個Vec<Option<&str>>中。如果我們得到一個值，我們就把`Some("success!")`推到Vec中。然後我們再做兩次這樣的操作。之後我們用`.and()`每次只顯示得到`Some`的索引。

```rust
fn main() {
    let first_try = vec![Some("success!"), None, Some("success!"), Some("success!"), None];
    let second_try = vec![None, Some("success!"), Some("success!"), Some("success!"), Some("success!")];
    let third_try = vec![Some("success!"), Some("success!"), Some("success!"), Some("success!"), None];

    for i in 0..first_try.len() {
        println!("{:?}", first_try[i].and(second_try[i]).and(third_try[i]));
    }
}
```

這個打印:

```text
None
None
Some("success!")
Some("success!")
None
```

第一個(索引0)是`None`，因為在`second_try`中有一個`None`為索引0。第二個是`None`，因為在`first_try`中有一個`None`。其次是`Some("success!")`，因為`first_try`、`second try`、`third_try`中沒有`None`。



`.any()`和`.all()`在迭代器中非常容易使用。它們根據你的輸入返回一個`bool`。在這個例子中，我們做了一個非常大的vec(大約20000個元素)，包含了從`'a'`到`'働'`的所有字符。然後我們創建一個函數來檢查是否有字符在其中。

接下來我們創建一個更小的vec，問它是否都是字母(用`.is_alphabetic()`方法)。然後我們問它是不是所有的字符都小於韓文字符`'행'`。

還要注意放一個參照物，因為`.iter()`給了一個參照物，你需要一個`&`和另一個`&`進行比較。

```rust
fn in_char_vec(char_vec: &Vec<char>, check: char) {
    println!("Is {} inside? {}", check, char_vec.iter().any(|&char| char == check));
}

fn main() {
    let char_vec = ('a'..'働').collect::<Vec<char>>();
    in_char_vec(&char_vec, 'i');
    in_char_vec(&char_vec, '뷁');
    in_char_vec(&char_vec, '鑿');

    let smaller_vec = ('A'..'z').collect::<Vec<char>>();
    println!("All alphabetic? {}", smaller_vec.iter().all(|&x| x.is_alphabetic()));
    println!("All less than the character 행? {}", smaller_vec.iter().all(|&x| x < '행'));
}
```

這個打印:

```text
Is i inside? true
Is 뷁 inside? false
Is 鑿 inside? false
All alphabetic? false
All less than the character 행? true
```

順便說一下，`.any()`只檢查到一個匹配的元素，然後就停止了。如果它已經找到了一個匹配項，它不會檢查所有的元素。如果您要在 `Vec` 上使用 `.any()`，最好把可能匹配的元素推到前面。或者你可以在 `.iter()` 之後使用 `.rev()` 來反向迭代。這裡有一個這樣的vec。

```rust
fn main() {
    let mut big_vec = vec![6; 1000];
    big_vec.push(5);
}
```

所以這個`Vec`有1000個`6`，後面還有一個`5`。我們假設我們要用`.any()`來看看它是否包含5。首先讓我們確定`.rev()`是有效的。記住，一個`Iterator`總是有`.next()`，讓你每次都檢查它的工作。

```rust
fn main() {
    let mut big_vec = vec![6; 1000];
    big_vec.push(5);

    let mut iterator = big_vec.iter().rev();
    println!("{:?}", iterator.next());
    println!("{:?}", iterator.next());
}
```

它的打印。

```text
Some(5)
Some(6)
```

我們是對的:有一個`Some(5)`，然後1000個`Some(6)`開始。所以我們可以這樣寫。

```rust
fn main() {
    let mut big_vec = vec![6; 1000];
    big_vec.push(5);

    println!("{:?}", big_vec.iter().rev().any(|&number| number == 5));
}
```

而且因為是`.rev()`，所以它只調用`.next()`一次就停止了。如果我們不用`.rev()`，那麼它將調用`.next()` 1001次才停止。這段代碼顯示了它。

```rust
fn main() {
    let mut big_vec = vec![6; 1000];
    big_vec.push(5);

    let mut counter = 0; // Start counting
    let mut big_iter = big_vec.into_iter(); // Make it an Iterator

    loop {
        counter +=1;
        if big_iter.next() == Some(5) { // Keep calling .next() until we get Some(5)
            break;
        }
    }
    println!("Final counter is: {}", counter);
}
```

這將打印出 `Final counter is: 1001`，所以我們知道它必須調用 `.next()` 1001 次才能找到 5。




`.find()` 告訴你一個迭代器是否有東西，而 `.position()` 告訴你它在哪裡。`.find()`與`.any()`不同，因為它返回一個`Option`，裡面有值(或`None`)。同時，`.position()`也是一個帶有位置號的`Option`，或`None`。換句話說

- `.find()`: "我儘量幫你拿"
- `.position()`:"我幫你找找看在哪裡"

下面是一個簡單的例子。

```rust
fn main() {
    let num_vec = vec![10, 20, 30, 40, 50, 60, 70, 80, 90, 100];

    println!("{:?}", num_vec.iter().find(|&number| number % 3 == 0)); // find takes a reference, so we give it &number
    println!("{:?}", num_vec.iter().find(|&number| number * 2 == 30));

    println!("{:?}", num_vec.iter().position(|&number| number % 3 == 0));
    println!("{:?}", num_vec.iter().position(|&number| number * 2 == 30));

}
```

這個打印:

```text
Some(30) // This is the number itself
None // No number inside times 2 == 30
Some(2) // This is the position
None
```



使用 `.cycle()` 你可以創建一個永遠循環的迭代器。這種類型的迭代器與 `.zip()` 很好地結合在一起，可以創建新的東西，就像這個例子，它創建了一個 `Vec<(i32, &str)>`。

```rust
fn main() {
    let even_odd = vec!["even", "odd"];

    let even_odd_vec = (0..6)
        .zip(even_odd.into_iter().cycle())
        .collect::<Vec<(i32, &str)>>();
    println!("{:?}", even_odd_vec);
}
```

所以，即使`.cycle()`可能永遠不會結束，但當把它們壓縮在一起時，另一個迭代器只運行了6次。
 也就是說，`.cycle()`所做的迭代器不會再被`.next()`調用，所以六次之後就完成了。輸出的結果是

```
[(0, "even"), (1, "odd"), (2, "even"), (3, "odd"), (4, "even"), (5, "odd")]
```

類似的事情也可以用一個沒有結尾的範圍來完成。如果你寫`0..`，那麼你就創建了一個永不停止的範圍。你可以很容易地使用這個方法。

```rust
fn main() {
    let ten_chars = ('a'..).take(10).collect::<Vec<char>>();
    let skip_then_ten_chars = ('a'..).skip(1300).take(10).collect::<Vec<char>>();

    println!("{:?}", ten_chars);
    println!("{:?}", skip_then_ten_chars);
}
```

兩者都是打印十個字符，但第二個跳過1300位，打印的是亞美尼亞語的十個字母。

```
['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
['յ', 'ն', 'շ', 'ո', 'չ', 'պ', 'ջ', 'ռ', 'ս', 'վ']
```


另一種流行的方法叫做`.fold()`。這個方法經常用於將迭代器中的元素加在一起，但你也可以做更多的事情。它與`.for_each()`有些類似。在 `.fold()` 中，你首先添加一個起始值 (如果你是把元素加在一起，那麼就是 0)，然後是一個逗號，然後是閉包。結尾給你兩個元素:到目前為止的總數，和下一個元素。首先這裡有一個簡單的例子，顯示`.fold()`將元素加在一起。

```rust
fn main() {
    let some_numbers = vec![9, 6, 9, 10, 11];

    println!("{}", some_numbers
        .iter()
        .fold(0, |total_so_far, next_number| total_so_far + next_number)
    );
}
```

所以，在第1步中，它從0開始，再加上下一個數字:9。

- 第1步，從0開始，加上下一個數字9
- 然後把9加上6: 15。
- 然後把15加上9: 24。
- 然後取24，再加上10: 34。
- 最後取34，再加上11: 45。所以它的打印結果是`45`.


但是你不需要只用它來添加東西。下面是一個例子，我們在每一個字符上加一個'-'，就會變成`String`。

```rust
fn main() {
    let a_string = "I don't have any dashes in me.";

    println!(
        "{}",
        a_string
            .chars() // Now it's an iterator
            .fold("-".to_string(), |mut string_so_far, next_char| { // Start with a String "-". Bring it in as mutable each time along with the next char
                string_so_far.push(next_char); // Push the char on, then '-'
                string_so_far.push('-');
                string_so_far} // Don't forget to pass it on to the next loop
            ));
}
```

這個打印:

```text
-I- -d-o-n-'-t- -h-a-v-e- -a-n-y- -d-a-s-h-e-s- -i-n- -m-e-.-
```



還有很多其他方便的方法，比如

- `.take_while()`，只要得到`true`，就會帶入一個迭代器(例如`take while x > 5`)
- `.cloned()`，它在迭代器內做了一個克隆。這將一個引用變成了一個值。
- `.by_ref()`，它使迭代器取一個引用。這很好的保證了你使用`Vec`或類似的方法來創建迭代器後可以使用它。
- 許多其他的`_while`方法:`.skip_while()`、`.map_while()`等等。
- `.sum()`:就是把所有的東西加在一起。



`.chunks()`和`.windows()`是將矢量切割成你想要的尺寸的兩種方法。你把你想要的尺寸放在括號裡。比如說你有一個有10個元素的矢量，你想要一個3的尺寸，它的工作原理是這樣的。

- `.chunks()`會給你4個切片: [0, 1, 2], 然後是[3, 4, 5], 然後是[6, 7, 8], 最後是[9]. 所以它會嘗試用三個元素創建一個切片，但如果它沒有三個元素，那麼它就不會崩潰。它只會給你剩下的東西。

- `.windows()`會先給你一個[0, 1, 2]的切片。然後它將移過一片，給你[1, 2, 3]。它將一直這樣做，直到最後到達3的最後一片，然後停止。

所以讓我們在一個簡單的數字向量上使用它們。它看起來像這樣:

```rust
fn main() {
    let num_vec = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 0];

    for chunk in num_vec.chunks(3) {
        println!("{:?}", chunk);
    }
    println!();
    for window in num_vec.windows(3) {
        println!("{:?}", window);
    }
}
```

這個打印:

```text
[1, 2, 3]
[4, 5, 6]
[7, 8, 9]
[0]

[1, 2, 3]
[2, 3, 4]
[3, 4, 5]
[4, 5, 6]
[5, 6, 7]
[6, 7, 8]
[7, 8, 9]
[8, 9, 0]
```

順便說一下，如果你什麼都不給它，`.chunks()`會崩潰。你可以為一個只有一項的向量寫`.chunks(1000)`，但你不能為任何長度為0的東西寫`.chunks()`。 如果你點擊[src]，你可以在函數中看到這一點，因為它說`assert!(chunk_size != 0);`。



`.match_indices()` 讓你把 `String` 或 `&str` 裡面所有符合你的輸入的東西都提取出來，並給你索引。它與 `.enumerate()` 類似，因為它返回一個包含兩個元素的元組。

```rust
fn main() {
    let rules = "Rule number 1: No fighting. Rule number 2: Go to bed at 8 pm. Rule number 3: Wake up at 6 am.";
    let rule_locations = rules.match_indices("Rule").collect::<Vec<(_, _)>>(); // This is Vec<usize, &str> but we just tell Rust to do it
    println!("{:?}", rule_locations);
}
```

這個打印:

```text
[(0, "Rule"), (28, "Rule"), (62, "Rule")]
```



`.peekable()` 讓你創建一個迭代器，在那裡你可以看到 (窺視) 下一個元素。它就像調用 `.next()` (它給出了一個 `Option`)，除了迭代器不會移動，所以你可以隨意使用它。實際上，你可以把peekable看成是 "可停止"的，因為你可以想停多久就停多久。下面是一個例子，我們對每個元素都使用`.peek()`三次。我們可以永遠使用`.peek()`，直到我們使用`.next()`移動到下一個元素。

```rust
fn main() {
    let just_numbers = vec![1, 5, 100];
    let mut number_iter = just_numbers.iter().peekable(); // This actually creates a type of iterator called Peekable

    for _ in 0..3 {
        println!("I love the number {}", number_iter.peek().unwrap());
        println!("I really love the number {}", number_iter.peek().unwrap());
        println!("{} is such a nice number", number_iter.peek().unwrap());
        number_iter.next();
    }
}
```

這個打印:

```text
I love the number 1
I really love the number 1
1 is such a nice number
I love the number 5
I really love the number 5
5 is such a nice number
I love the number 100
I really love the number 100
100 is such a nice number
```

下面是另一個例子，我們使用`.peek()`對一個元素進行匹配。使用完後，我們調用`.next()`。


```rust
fn main() {
    let locations = vec![
        ("Nevis", 25),
        ("Taber", 8428),
        ("Markerville", 45),
        ("Cardston", 3585),
    ];
    let mut location_iter = locations.iter().peekable();
    while location_iter.peek().is_some() {
        match location_iter.peek() {
            Some((name, number)) if *number < 100 => { // .peek() gives us a reference so we need *
                println!("Found a hamlet: {} with {} people", name, number)
            }
            Some((name, number)) => println!("Found a town: {} with {} people", name, number),
            None => break,
        }
        location_iter.next();
    }
}
```

這個打印:

```text
Found a hamlet: Nevis with 25 people
Found a town: Taber with 8428 people
Found a hamlet: Markerville with 45 people
Found a town: Cardston with 3585 people
```

最後，這裡有一個例子，我們也使用`.match_indices()`。在這個例子中，我們根據`&str`中的空格數，將名字放入`struct`中。

```rust
#[derive(Debug)]
struct Names {
    one_word: Vec<String>,
    two_words: Vec<String>,
    three_words: Vec<String>,
}

fn main() {
    let vec_of_names = vec![
        "Caesar",
        "Frodo Baggins",
        "Bilbo Baggins",
        "Jean-Luc Picard",
        "Data",
        "Rand Al'Thor",
        "Paul Atreides",
        "Barack Hussein Obama",
        "Bill Jefferson Clinton",
    ];

    let mut iter_of_names = vec_of_names.iter().peekable();

    let mut all_names = Names { // start an empty Names struct
        one_word: vec![],
        two_words: vec![],
        three_words: vec![],
    };

    while iter_of_names.peek().is_some() {
        let next_item = iter_of_names.next().unwrap(); // We can use .unwrap() because we know it is Some
        match next_item.match_indices(' ').collect::<Vec<_>>().len() { // Create a quick vec using .match_indices and check the length
            0 => all_names.one_word.push(next_item.to_string()),
            1 => all_names.two_words.push(next_item.to_string()),
            _ => all_names.three_words.push(next_item.to_string()),
        }
    }

    println!("{:?}", all_names);
}
```

這將打印:

```text
Names { one_word: ["Caesar", "Data"], two_words: ["Frodo Baggins", "Bilbo Baggins", "Jean-Luc Picard", "Rand Al\'Thor", "Paul Atreides"], three_words:
["Barack Hussein Obama", "Bill Jefferson Clinton"] }
```


## dbg! 宏和.inspect

`dbg!`是一個非常有用的宏，可以快速打印信息。它是 `println!` 的一個很好的替代品，因為它的輸入速度更快，提供的信息更多。

```rust
fn main() {
    let my_number = 8;
    dbg!(my_number);
}
```

這樣就可以打印出`[src\main.rs:4] my_number = 8`。

但實際上，你可以把`dbg!`放在其他很多地方，甚至可以把代碼包在裡面。比如看這段代碼。

```rust
fn main() {
    let mut my_number = 9;
    my_number += 10;

    let new_vec = vec![8, 9, 10];

    let double_vec = new_vec.iter().map(|x| x * 2).collect::<Vec<i32>>();
}
```

這段代碼創建了一個新的可變數字，並改變了它。然後創建一個vec，並使用`iter`和`map`以及`collect`創建一個新的vec。在這段代碼中，我們幾乎可以把`dbg!`放在任何地方。`dbg!`問編譯器："此刻你在做什麼？"，然後告訴你:

```rust
fn main() {
    let mut my_number = dbg!(9);
    dbg!(my_number += 10);

    let new_vec = dbg!(vec![8, 9, 10]);

    let double_vec = dbg!(new_vec.iter().map(|x| x * 2).collect::<Vec<i32>>());

    dbg!(double_vec);
}
```

所以這個打印:

```text
[src\main.rs:3] 9 = 9
```

和：

```text
[src\main.rs:4] my_number += 10 = ()
```

和：

```text
[src\main.rs:6] vec![8, 9, 10] = [
    8,
    9,
    10,
]
```

而這個，甚至可以顯示出表達式的值。

```text
[src\main.rs:8] new_vec.iter().map(|x| x * 2).collect::<Vec<i32>>() = [
    16,
    18,
    20,
]
```

和：

```text
[src\main.rs:10] double_vec = [
    16,
    18,
    20,
]
```


`.inspect` 與 `dbg!` 有點類似，就像在迭代器中使用`map`一樣使用它。它給了你迭代項，你可以打印它或者做任何你想做的事情。例如，我們再看看我們的 `double_vec`。

```rust
fn main() {
    let new_vec = vec![8, 9, 10];

    let double_vec = new_vec
        .iter()
        .map(|x| x * 2)
        .collect::<Vec<i32>>();
}
```

我們想知道更多關於代碼的信息。所以我們在兩個地方添加`inspect()`。

```rust
fn main() {
    let new_vec = vec![8, 9, 10];

    let double_vec = new_vec
        .iter()
        .inspect(|first_item| println!("The item is: {}", first_item))
        .map(|x| x * 2)
        .inspect(|next_item| println!("Then it is: {}", next_item))
        .collect::<Vec<i32>>();
}
```

這個打印:

```text
The item is: 8
Then it is: 16
The item is: 9
Then it is: 18
The item is: 10
Then it is: 20
```

而且因為`.inspect`採取的是封閉式，所以我們可以隨意寫。

```rust
fn main() {
    let new_vec = vec![8, 9, 10];

    let double_vec = new_vec
        .iter()
        .inspect(|first_item| {
            println!("The item is: {}", first_item);
            match **first_item % 2 { // first item is a &&i32 so we use **
                0 => println!("It is even."),
                _ => println!("It is odd."),
            }
            println!("In binary it is {:b}.", first_item);
        })
        .map(|x| x * 2)
        .collect::<Vec<i32>>();
}
```

這個打印:

```text
The item is: 8
It is even.
In binary it is 1000.
The item is: 9
It is odd.
In binary it is 1001.
The item is: 10
It is even.
In binary it is 1010.
```

## &str的類型

`&str`的類型不止一種。我們有。

- 字符串： 當你寫`let my_str = "I am a &str"`的時候，你就會產生這些字符。它們在整個程序中持續存在，因為它們是直接寫進二進制中的，它們的類型是 `&'static str`。`'`的意思是它的生命期，字符串字元有一個叫`static`的生命期。
- 借用str：這是常規的 `&str` 形式，沒有 `static` 生命期。如果你創建了一個`String`，並得到了它的引用，當你需要它時，Rust會把它轉換為`&str`。比如說

```rust
fn prints_str(my_str: &str) { // it can use &String like a &str
    println!("{}", my_str);
}

fn main() {
    let my_string = String::from("I am a string");
    prints_str(&my_string); // we give prints_str a &String
}
```

那麼什麼是lifetime呢？我們現在就來瞭解一下。

## 生命期

生命期的意思是 "變量的生命期有多長"。你只需要考慮引用的生命期。這是因為引用的生命期不能比它們來自的對象更長。例如，這個函數就不能用。

```rust
fn returns_reference() -> &str {
    let my_string = String::from("I am a string");
    &my_string // ⚠️
}

fn main() {}
```

問題是`my_string`只存在於`returns_reference`中。我們試圖返回 `&my_string`，但是 `&my_string` 不能沒有 `my_string`。所以編譯器說不行。

這個代碼也不行。

```rust
fn returns_str() -> &str {
    let my_string = String::from("I am a string");
    "I am a str" // ⚠️
}

fn main() {
    let my_str = returns_str();
    println!("{}", my_str);
}
```

但幾乎是成功的。編譯器說:

```text
error[E0106]: missing lifetime specifier
 --> src\main.rs:6:21
  |
6 | fn returns_str() -> &str {
  |                     ^ expected named lifetime parameter
  |
  = help: this function's return type contains a borrowed value, but there is no value for it to be borrowed from
help: consider using the `'static` lifetime
  |
6 | fn returns_str() -> &'static str {
  |                     ^^^^^^^^
```

`missing lifetime specifier`的意思是，我們需要加一個`'`的生命期。然後說它`contains a borrowed value, but there is no value for it to be borrowed from`。也就是說，`I am a str`不是借來的。它寫`&'static str`就說`consider using the 'static lifetime`。所以它認為我們應該嘗試說這是一個字符串的文字。

現在它工作了。

```rust
fn returns_str() -> &'static str {
    let my_string = String::from("I am a string");
    "I am a str"
}

fn main() {
    let my_str = returns_str();
    println!("{}", my_str);
}
```

這是因為我們返回了一個 `&str`，生命期為 `static`。同時，`my_string`只能以`String`的形式返回:我們不能返回對它的引用，因為它將在下一行死亡。

所以現在`fn returns_str() -> &'static str`告訴Rust， "別擔心，我們只會返回一個字符串字面量". 字符串字面量在整個程序中都是有效的，所以Rust很高興。你會注意到，這與泛型類似。當我們告訴編譯器類似 `<T: Display>` 的東西時，我們承諾我們將只使用實現了 `Display` 的輸入。生命期也類似:我們並沒有改變任何變量的生命期。我們只是告訴編譯器輸入的生命期是多少。

但是`'static`並不是唯一的生命期。實際上，每個變量都有一個生命期，但通常我們不必寫出來。編譯器很聰明，一般都能自己算出來。只有在編譯器不知道的時候，我們才需要寫出生命期。

下面是另一個生命期的例子。想象一下，我們想創建一個`City`結構，並給它一個`&str`的名字。我們可能想這樣做，因為這樣做的性能比用`String`快。所以我們這樣寫，但還不能用。

```rust
#[derive(Debug)]
struct City {
    name: &str, // ⚠️
    date_founded: u32,
}

fn main() {
    let my_city = City {
        name: "Ichinomiya",
        date_founded: 1921,
    };
}
```

編譯器說:

```text
error[E0106]: missing lifetime specifier
 --> src\main.rs:3:11
  |
3 |     name: &str,
  |           ^ expected named lifetime parameter
  |
help: consider introducing a named lifetime parameter
  |
2 | struct City<'a> {
3 |     name: &'a str,
  |
```

Rust 需要 `&str` 的生命期，因為 `&str` 是一個引用。如果`name`指向的值被丟棄了會怎樣？那就不安全了。

`'static`呢，能用嗎？我們以前用過。我們試試吧。

```rust
#[derive(Debug)]
struct City {
    name: &'static str, // change &str to &'static str
    date_founded: u32,
}

fn main() {
    let my_city = City {
        name: "Ichinomiya",
        date_founded: 1921,
    };

    println!("{} was founded in {}", my_city.name, my_city.date_founded);
}
```

好的，這就可以了。也許這就是你想要的結構。但是，請注意，我們只能接受 "字符串字面量"，所以不能接受對其他東西的引用。所以這將無法工作。

```rust
#[derive(Debug)]
struct City {
    name: &'static str, // must live for the whole program
    date_founded: u32,
}

fn main() {
    let city_names = vec!["Ichinomiya".to_string(), "Kurume".to_string()]; // city_names does not live for the whole program

    let my_city = City {
        name: &city_names[0], // ⚠️ This is a &str, but not a &'static str. It is a reference to a value inside city_names
        date_founded: 1921,
    };

    println!("{} was founded in {}", my_city.name, my_city.date_founded);
}
```

編譯器說:

```text
error[E0597]: `city_names` does not live long enough
  --> src\main.rs:12:16
   |
12 |         name: &city_names[0],
   |                ^^^^^^^^^^
   |                |
   |                borrowed value does not live long enough
   |                requires that `city_names` is borrowed for `'static`
...
18 | }
   | - `city_names` dropped here while still borrowed
```

這一點很重要，因為我們給它的引用其實已經夠長壽了。但是我們承諾只給它一個`&'static str`，這就是問題所在。

所以現在我們就試試之前編譯器的建議。它說嘗試寫`struct City<'a>`和`name: &'a str`。這就意味著，只有當`name`活到`City`一樣壽命的情況下，它才會接受`name`的引用。

```rust
#[derive(Debug)]
struct City<'a> { // City has lifetime 'a
    name: &'a str, // and name also has lifetime 'a.
    date_founded: u32,
}

fn main() {
    let city_names = vec!["Ichinomiya".to_string(), "Kurume".to_string()];

    let my_city = City {
        name: &city_names[0],
        date_founded: 1921,
    };

    println!("{} was founded in {}", my_city.name, my_city.date_founded);
}
```

另外記住，如果你願意，你可以寫任何東西來代替`'a`。這也和泛型類似，我們寫`T`和`U`，但實際上可以寫任何東西。

```rust
#[derive(Debug)]
struct City<'city> { // The lifetime is now called 'city
    name: &'city str, // and name has the 'city lifetime
    date_founded: u32,
}

fn main() {}
```

所以一般都會寫`'a, 'b, 'c`等，因為這樣寫起來比較快，也是常用的寫法。但如果你想的話，你可以隨時更改。有一個很好的建議是，如果代碼非常複雜，把生命期改成一個 "人類可讀"的名字可以幫助你閱讀代碼。

我們再來看看與trait的比較，對於泛型。比如說

```rust
use std::fmt::Display;

fn prints<T: Display>(input: T) {
    println!("T is {}", input);
}

fn main() {}
```

當你寫`T: Display`的時候，它的意思是 "只有當T有Display時，才取T"。
而不是說: "我把Display給T".

對於生命期也是如此。當你在這裡寫 'a:

```rust
#[derive(Debug)]
struct City<'a> {
    name: &'a str,
    date_founded: u32,
}

fn main() {}
```

意思是 "如果`name`的生命期至少與`City`一樣長，才接受`name`的輸入"。
它的意思不是說: "我會讓`name`的輸入與`City`一樣長壽"。


現在我們可以瞭解一下之前看到的`<'_>`。這被稱為 "匿名生命期"，是使用引用的一個指標。例如，當你在實現結構時，Rust會向你建議使用。這裡有一個幾乎可以工作的結構體，但還不能工作：

```rust
    // ⚠️
struct Adventurer<'a> {
    name: &'a str,
    hit_points: u32,
}

impl Adventurer {
    fn take_damage(&mut self) {
        self.hit_points -= 20;
        println!("{} has {} hit points left!", self.name, self.hit_points);
    }
}

fn main() {}
```

所以我們對`struct`做了我們需要做的事情:首先我們說`name`來自於一個`&str`。這就意味著我們需要lifetime，所以我們給了它`<'a>`。然後我們必須對`struct`做同樣的處理，以證明它們至少和這個生命期一樣長。但是Rust卻告訴我們要這樣做:

```text
error[E0726]: implicit elided lifetime not allowed here
 --> src\main.rs:6:6
  |
6 | impl Adventurer {
  |      ^^^^^^^^^^- help: indicate the anonymous lifetime: `<'_>`
```

它想讓我們加上那個匿名的生命期，以表明有一個引用被使用。所以如果我們這樣寫，它就會很高興。

```rust
struct Adventurer<'a> {
    name: &'a str,
    hit_points: u32,
}

impl Adventurer<'_> {
    fn take_damage(&mut self) {
        self.hit_points -= 20;
        println!("{} has {} hit points left!", self.name, self.hit_points);
    }
}

fn main() {}
```

這個生命期是為了讓你不必總是寫諸如`impl<'a> Adventurer<'a>`這樣的東西，因為結構已經顯示了生命期。

在Rust中，生命期是很困難的，但這裡有一些技巧可以避免對它們太過緊張。

- 你可以繼續使用自有類型，使用克隆等，如果你想暫時避免它們。
- 很多時候，當編譯器想要lifetime的時候，你只要在這裡和那裡寫上<'a>就可以了。這只是一種 "別擔心，我不會給你任何不夠長壽的東西"的說法。
- 你可以每次只探索一下生命期。寫一些擁有值的代碼，然後把一個代碼變成一個引用。編譯器會開始抱怨，但也會給出一些建議。如果它變得太複雜，你可以撤銷它，下次再試。

讓我們用我們的代碼來做這個，看看編譯器怎麼說。首先我們回去把生命期拿出來，同時實現`Display`。`Display`就打印`Adventurer`的名字。

```rust
// ⚠️
struct Adventurer {
    name: &str,
    hit_points: u32,
}

impl Adventurer {
    fn take_damage(&mut self) {
        self.hit_points -= 20;
        println!("{} has {} hit points left!", self.name, self.hit_points);
    }
}

impl std::fmt::Display for Adventurer {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            write!(f, "{} has {} hit points.", self.name, self.hit_points)
        }
}

fn main() {}
```

第一個抱怨就是這個:

```text
error[E0106]: missing lifetime specifier
 --> src\main.rs:2:11
  |
2 |     name: &str,
  |           ^ expected named lifetime parameter
  |
help: consider introducing a named lifetime parameter
  |
1 | struct Adventurer<'a> {
2 |     name: &'a str,
  |
```

它建議怎麼做:在Adventurer後面加上`<'a>`，以及`&'a str`。所以我們就這麼做。

```rust
// ⚠️
struct Adventurer<'a> {
    name: &'a str,
    hit_points: u32,
}

impl Adventurer {
    fn take_damage(&mut self) {
        self.hit_points -= 20;
        println!("{} has {} hit points left!", self.name, self.hit_points);
    }
}

impl std::fmt::Display for Adventurer {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            write!(f, "{} has {} hit points.", self.name, self.hit_points)
        }
}

fn main() {}
```

現在它對這些部分很滿意，但對`impl`塊感到奇怪。它希望我們提到它在使用引用。

```text
error[E0726]: implicit elided lifetime not allowed here
 --> src\main.rs:6:6
  |
6 | impl Adventurer {
  |      ^^^^^^^^^^- help: indicate the anonymous lifetime: `<'_>`

error[E0726]: implicit elided lifetime not allowed here
  --> src\main.rs:12:28
   |
12 | impl std::fmt::Display for Adventurer {
   |                            ^^^^^^^^^^- help: indicate the anonymous lifetime: `<'_>`
```

好了，我們將這些寫進去......現在它工作了！現在我們可以創建一個`Adventurer`，然後用它做一些事情:

```rust
struct Adventurer<'a> {
    name: &'a str,
    hit_points: u32,
}

impl Adventurer<'_> {
    fn take_damage(&mut self) {
        self.hit_points -= 20;
        println!("{} has {} hit points left!", self.name, self.hit_points);
    }
}

impl std::fmt::Display for Adventurer<'_> {

        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            write!(f, "{} has {} hit points.", self.name, self.hit_points)
        }
}

fn main() {
    let mut billy = Adventurer {
        name: "Billy",
        hit_points: 100_000,
    };
    println!("{}", billy);
    billy.take_damage();
}
```

這個將打印:

```text
Billy has 100000 hit points.
Billy has 99980 hit points left!
```

所以你可以看到，lifetimes往往只是編譯器想要確定。而且它通常很聰明，幾乎可以猜到你想要的生命期，只需要你告訴它，它就可以確定了。

## 內部可變性

### Cell

**內部可變性**的意思是在內部有一點可變性。還記得在Rust中，你需要用`mut`來改變一個變量嗎？也有一些方法可以不用`mut`這個詞來改變它們。這是因為Rust有一些方法可以讓你安全地在一個不可變的結構裡面改變值。每一種方法都遵循一些規則，確保改變值仍然是安全的。

首先，讓我們看一個簡單的例子，我們會想要這樣做:想象一下，一個叫`PhoneModel`的結構體有很多字段:

```rust
struct PhoneModel {
    company_name: String,
    model_name: String,
    screen_size: f32,
    memory: usize,
    date_issued: u32,
    on_sale: bool,
}

fn main() {
    let super_phone_3000 = PhoneModel {
        company_name: "YY Electronics".to_string(),
        model_name: "Super Phone 3000".to_string(),
        screen_size: 7.5,
        memory: 4_000_000,
        date_issued: 2020,
        on_sale: true,
    };

}
```

`PhoneModel`中的字段最好是不可變的，因為我們不希望數據改變。比如說`date_issued`和`screen_size`永遠不會變。

但是裡面有一個字段叫`on_sale`。一個手機型號先是會有銷售(`true`)，但是後來公司會停止銷售。我們能不能只讓這一個字段可變？因為我們不想寫`let mut super_phone_3000`。如果我們這樣做，那麼每個字段都會變得可變。

Rust有很多方法可以讓一些不可變的東西里面有一些安全的可變性，最簡單的方法叫做`Cell`。首先我們使用`use std::cell::Cell`，這樣我們就可以每次只寫`Cell`而不是`std::cell::Cell`。

然後我們把`on_sale: bool`改成`on_sale: Cell<bool>`。現在它不是一個bool:它是一個`Cell`，容納了一個`bool`。

`Cell`有一個叫做`.set()`的方法，在這裡你可以改變值。我們用`.set()`把`on_sale: true`改為`on_sale: Cell::new(true)`。

```rust
use std::cell::Cell;

struct PhoneModel {
    company_name: String,
    model_name: String,
    screen_size: f32,
    memory: usize,
    date_issued: u32,
    on_sale: Cell<bool>,
}

fn main() {
    let super_phone_3000 = PhoneModel {
        company_name: "YY Electronics".to_string(),
        model_name: "Super Phone 3000".to_string(),
        screen_size: 7.5,
        memory: 4_000_000,
        date_issued: 2020,
        on_sale: Cell::new(true),
    };

    // 10 years later, super_phone_3000 is not on sale anymore
    super_phone_3000.on_sale.set(false);
}
```

`Cell` 適用於所有類型，但對簡單的 Copy 類型效果最好，因為它給出的是值，而不是引用。`Cell`有一個叫做`get()`的方法，它只對Copy類型有效。

另一個可以使用的類型是 `RefCell`。

### RefCell

`RefCell`是另一種無需聲明`mut`而改變值的方法。它的意思是 "引用單元格"，就像 `Cell`，但使用引用而不是副本。

我們將創建一個 `User` 結構。到目前為止，你可以看到它與 `Cell` 類似。

```rust
use std::cell::RefCell;

#[derive(Debug)]
struct User {
    id: u32,
    year_registered: u32,
    username: String,
    active: RefCell<bool>,
    // Many other fields
}

fn main() {
    let user_1 = User {
        id: 1,
        year_registered: 2020,
        username: "User 1".to_string(),
        active: RefCell::new(true),
    };

    println!("{:?}", user_1.active);
}
```

這樣就可以打印出`RefCell { value: true }`。

`RefCell`的方法有很多。其中兩種是`.borrow()`和`.borrow_mut()`。使用這些方法，你可以做與`&`和`&mut`相同的事情。規則都是一樣的:

- 多個不可變借用可以
- 一個可變的借用可以
- 但可變和不可變借用在一起是不行的

所以改變`RefCell`中的值是非常容易的。

```rust
// 🚧
user_1.active.replace(false);
println!("{:?}", user_1.active);
```

而且還有很多其他的方法，比如`replace_with`使用的是閉包。

```rust
// 🚧
let date = 2020;

user_1
    .active
    .replace_with(|_| if date < 2000 { true } else { false });
println!("{:?}", user_1.active);
```


但是你要小心使用`RefCell`，因為它是在運行時而不是編譯時檢查借用。運行時是指程序實際運行的時候(編譯後)。所以這將會被編譯，即使它是錯誤的。

```rust
use std::cell::RefCell;

#[derive(Debug)]
struct User {
    id: u32,
    year_registered: u32,
    username: String,
    active: RefCell<bool>,
    // Many other fields
}

fn main() {
    let user_1 = User {
        id: 1,
        year_registered: 2020,
        username: "User 1".to_string(),
        active: RefCell::new(true),
    };

    let borrow_one = user_1.active.borrow_mut(); // first mutable borrow - okay
    let borrow_two = user_1.active.borrow_mut(); // second mutable borrow - not okay
}
```

但如果你運行它，它就會立即崩潰。

```text
thread 'main' panicked at 'already borrowed: BorrowMutError', C:\Users\mithr\.rustup\toolchains\stable-x86_64-pc-windows-msvc\lib/rustlib/src/rust\src\libcore\cell.rs:877:9
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
error: process didn't exit successfully: `target\debug\rust_book.exe` (exit code: 101)
```

`already borrowed: BorrowMutError`是重要的部分。所以當你使用`RefCell`時，好編譯**並**運行檢查。

### Mutex

`Mutex`是另一種改變數值的方法，不需要聲明`mut`。Mutex的意思是`mutual exclusion`，也就是 "一次只能改一個"。這就是為什麼`Mutex`是安全的，因為它每次只讓一個進程改變它。為了做到這一點，它使用了`.lock()`。`Lock`就像從裡面鎖上一扇門。你進入一個房間，鎖上門，現在你可以在房間裡面改變東西。別人不能進來阻止你，因為你把門鎖上了。

`Mutex`通過例子更容易理解:

```rust
use std::sync::Mutex;

fn main() {
    let my_mutex = Mutex::new(5); // A new Mutex<i32>. We don't need to say mut
    let mut mutex_changer = my_mutex.lock().unwrap(); // mutex_changer is a MutexGuard
                                                     // It has to be mut because we will change it
                                                     // Now it has access to the Mutex
                                                     // Let's print my_mutex to see:

    println!("{:?}", my_mutex); // This prints "Mutex { data: <locked> }"
                                // So we can't access the data with my_mutex now,
                                // only with mutex_changer

    println!("{:?}", mutex_changer); // This prints 5. Let's change it to 6.

    *mutex_changer = 6; // mutex_changer is a MutexGuard<i32> so we use * to change the i32

    println!("{:?}", mutex_changer); // Now it says 6
}
```

但是`mutex_changer`做完後還是有鎖。我們該如何阻止它呢？`Mutex`在`MutexGuard`超出範圍時就會被解鎖。"超出範圍"表示該代碼塊已經完成。比如說:

```rust
use std::sync::Mutex;

fn main() {
    let my_mutex = Mutex::new(5);
    {
        let mut mutex_changer = my_mutex.lock().unwrap();
        *mutex_changer = 6;
    } // mutex_changer goes out of scope - now it is gone. It is not locked anymore

    println!("{:?}", my_mutex); // Now it says: Mutex { data: 6 }
}
```

如果你不想使用不同的`{}`代碼塊，你可以使用`std::mem::drop(mutex_changer)`。`std::mem::drop`的意思是 "讓這個超出範圍"。

```rust
use std::sync::Mutex;

fn main() {
    let my_mutex = Mutex::new(5);
    let mut mutex_changer = my_mutex.lock().unwrap();
    *mutex_changer = 6;
    std::mem::drop(mutex_changer); // drop mutex_changer - it is gone now
                                   // and my_mutex is unlocked

    println!("{:?}", my_mutex); // Now it says: Mutex { data: 6 }
}
```

你必須小心使用 `Mutex`，因為如果另一個變量試圖 `lock`它，它會等待。

```rust
use std::sync::Mutex;

fn main() {
    let my_mutex = Mutex::new(5);
    let mut mutex_changer = my_mutex.lock().unwrap(); // mutex_changer has the lock
    let mut other_mutex_changer = my_mutex.lock().unwrap(); // other_mutex_changer wants the lock
                                                            // the program is waiting
                                                            // and waiting
                                                            // and will wait forever.

    println!("This will never print...");
}
```

還有一種方法是`try_lock()`。然後它會試一次，如果沒能鎖上就會放棄。`try_lock().unwrap()`就不要做了，因為如果不成功它就會崩潰。`if let`或`match`比較好。

```rust
use std::sync::Mutex;

fn main() {
    let my_mutex = Mutex::new(5);
    let mut mutex_changer = my_mutex.lock().unwrap();
    let mut other_mutex_changer = my_mutex.try_lock(); // try to get the lock

    if let Ok(value) = other_mutex_changer {
        println!("The MutexGuard has: {}", value)
    } else {
        println!("Didn't get the lock")
    }
}
```

另外，你不需要創建一個變量來改變`Mutex`。你可以直接這樣做:

```rust
use std::sync::Mutex;

fn main() {
    let my_mutex = Mutex::new(5);

    *my_mutex.lock().unwrap() = 6;

    println!("{:?}", my_mutex);
}
```

`*my_mutex.lock().unwrap() = 6;`的意思是 "解鎖my_mutex並使其成為6"。沒有任何變量來保存它，所以你不需要調用 `std::mem::drop`。如果你願意，你可以做100次--這並不重要。

```rust
use std::sync::Mutex;

fn main() {
    let my_mutex = Mutex::new(5);

    for _ in 0..100 {
        *my_mutex.lock().unwrap() += 1; // locks and unlocks 100 times
    }

    println!("{:?}", my_mutex);
}
```

### RwLock

`RwLock`的意思是 "讀寫鎖"。它像`Mutex`，但也像`RefCell`。你用`.write().unwrap()`代替`.lock().unwrap()`來改變它。但你也可以用`.read().unwrap()`來獲得讀權限。它和`RefCell`一樣，遵循這些規則:

- 很多`.read()`變量可以
- 一個`.write()`變量可以
- 但多個`.write()`或`.read()`與`.write()`一起是不行的

如果在無法訪問的情況下嘗試`.write()`，程序將永遠運行。

```rust
use std::sync::RwLock;

fn main() {
    let my_rwlock = RwLock::new(5);

    let read1 = my_rwlock.read().unwrap(); // one .read() is fine
    let read2 = my_rwlock.read().unwrap(); // two .read()s is also fine

    println!("{:?}, {:?}", read1, read2);

    let write1 = my_rwlock.write().unwrap(); // uh oh, now the program will wait forever
}
```

所以我們用`std::mem::drop`，就像用`Mutex`一樣。

```rust
use std::sync::RwLock;
use std::mem::drop; // We will use drop() many times

fn main() {
    let my_rwlock = RwLock::new(5);

    let read1 = my_rwlock.read().unwrap();
    let read2 = my_rwlock.read().unwrap();

    println!("{:?}, {:?}", read1, read2);

    drop(read1);
    drop(read2); // we dropped both, so we can use .write() now

    let mut write1 = my_rwlock.write().unwrap();
    *write1 = 6;
    drop(write1);
    println!("{:?}", my_rwlock);
}
```

而且你也可以使用`try_read()`和`try_write()`。

```rust
use std::sync::RwLock;

fn main() {
    let my_rwlock = RwLock::new(5);

    let read1 = my_rwlock.read().unwrap();
    let read2 = my_rwlock.read().unwrap();

    if let Ok(mut number) = my_rwlock.try_write() {
        *number += 10;
        println!("Now the number is {}", number);
    } else {
        println!("Couldn't get write access, sorry!")
    };
}
```

## Cow

Cow是一個非常方便的枚舉。它的意思是 "寫時克隆"，如果你不需要`String`，可以返回一個`&str`，如果你需要，可以返回一個`String`。(它也可以對數組與Vec等做同樣的處理)。

為了理解它，我們看一下簽名。它說

```rust
pub enum Cow<'a, B>
where
    B: 'a + ToOwned + ?Sized,
 {
    Borrowed(&'a B),
    Owned(<B as ToOwned>::Owned),
}

fn main() {}
```

你馬上就知道，`'a`意味著它可以和引用一起工作。`ToOwned`的特性意味著它是一個可以變成擁有類型的類型。例如，`str`通常是一個引用(`&str`)，你可以把它變成一個擁有的`String`。

接下來是`?Sized`。這意味著 "也許是Sized，但也許不是"。Rust中幾乎每個類型都是Sized的，但像`str`這樣的類型卻不是。這就是為什麼我們需要一個 `&` 來代替 `str`，因為編譯器不知道大小。所以，如果你想要一個可以使用 `str` 這樣的trait，你可以添加 `?Sized.`

接下來是`enum`的變種。它們是 `Borrowed` 和 `Owned`。

想象一下，你有一個返回 `Cow<'static, str>` 的函數。如果你告訴函數返回`"My message".into()`，它就會查看類型:"My message"是`str`. 這是一個`Borrowed`的類型，所以它選擇`Borrowed(&'a B)`。所以它就變成了`Cow::Borrowed(&'static str)`。

而如果你給它一個`format!("{}", "My message").into()`，那麼它就會查看類型。這次是一個`String`，因為`format!`創建了`String`。所以這次會選擇 "Owned"。

下面是一個測試`Cow`的例子。我們將把一個數字放入一個函數中，返回一個`Cow<'static, str>`。根據這個數字，它會創建一個`&str`或`String`。然後它使用`.into()`將其變成`Cow`。這樣做的時候，它就會選擇`Cow::Borrowed`或者`Cow::Owned`。那我們就匹配一下，看看它選的是哪一個。

```rust
use std::borrow::Cow;

fn modulo_3(input: u8) -> Cow<'static, str> {
    match input % 3 {
        0 => "Remainder is 0".into(),
        1 => "Remainder is 1".into(),
        remainder => format!("Remainder is {}", remainder).into(),
    }
}

fn main() {
    for number in 1..=6 {
        match modulo_3(number) {
            Cow::Borrowed(message) => println!("{} went in. The Cow is borrowed with this message: {}", number, message),
            Cow::Owned(message) => println!("{} went in. The Cow is owned with this message: {}", number, message),
        }
    }
}
```

這個打印:

```text
1 went in. The Cow is borrowed with this message: Remainder is 1
2 went in. The Cow is owned with this message: Remainder is 2
3 went in. The Cow is borrowed with this message: Remainder is 0
4 went in. The Cow is borrowed with this message: Remainder is 1
5 went in. The Cow is owned with this message: Remainder is 2
6 went in. The Cow is borrowed with this message: Remainder is 0
```

`Cow`還有一些其他的方法，比如`into_owned` 或者 `into_borrowed`，這樣如果你需要的話，你可以改變它。

## 類型別名

類型別名的意思是 "給某個類型一個新的名字"。類型別名非常簡單。通常，當您有一個很長的類型，而又不想每次都寫它時，您就會使用它們。當您想給一個類型起一個更好的名字，便於記憶時，也可以使用它。下面是兩個類型別名的例子。

這裡是一個不難的類型，但是你想讓你的代碼更容易被其他人(或者你)理解。

```rust
type CharacterVec = Vec<char>;

fn main() {}
```


這是一種非常難讀的類型:

```rust
// this return type is extremely long
fn returns<'a>(input: &'a Vec<char>) -> std::iter::Take<std::iter::Skip<std::slice::Iter<'a, char>>> {
    input.iter().skip(4).take(5)
}

fn main() {}
```

所以你可以改成這樣。

```rust
type SkipFourTakeFive<'a> = std::iter::Take<std::iter::Skip<std::slice::Iter<'a, char>>>;

fn returns<'a>(input: &'a Vec<char>) -> SkipFourTakeFive {
    input.iter().skip(4).take(5)
}

fn main() {}
```

當然，你也可以導入元素，讓類型更短:

```rust
use std::iter::{Take, Skip};
use std::slice::Iter;

fn returns<'a>(input: &'a Vec<char>) -> Take<Skip<Iter<'a, char>>> {
    input.iter().skip(4).take(5)
}

fn main() {}
```

所以你可以根據自己的喜好來決定在你的代碼中什麼是最好看的。

請注意，這並沒有創建一個實際的新類型。它只是一個代替現有類型的名稱。所以如果你寫了 `type File = String;`，編譯器只會看到 `String`。所以這將打印出 `true`。

```rust
type File = String;

fn main() {
    let my_file = File::from("I am file contents");
    let my_string = String::from("I am file contents");
    println!("{}", my_file == my_string);
}
```

那麼如果你想要一個實際的新類型呢？

如果你想要一個新的文件類型，而編譯器看到的是`File`，你可以把它放在一個結構中。

```rust
struct File(String); // File is a wrapper around String

fn main() {
    let my_file = File(String::from("I am file contents"));
    let my_string = String::from("I am file contents");
}
```

現在這樣就不行了，因為它們是兩種不同的類型。

```rust
struct File(String); // File is a wrapper around String

fn main() {
    let my_file = File(String::from("I am file contents"));
    let my_string = String::from("I am file contents");
    println!("{}", my_file == my_string);  // ⚠️ cannot compare File with String
}
```

如果你想比較裡面的String，可以用my_file.0:

```rust
struct File(String);

fn main() {
    let my_file = File(String::from("I am file contents"));
    let my_string = String::from("I am file contents");
    println!("{}", my_file.0 == my_string); // my_file.0 is a String, so this prints true
}
```

### 在函數中導入和重命名

通常你會在程序的頂部寫上`use`，像這樣。

```rust
use std::cell::{Cell, RefCell};

fn main() {}
```

但我們看到，你可以在任何地方這樣做，特別是在函數中使用名稱較長的enum。下面是一個例子:

```rust
enum MapDirection {
    North,
    NorthEast,
    East,
    SouthEast,
    South,
    SouthWest,
    West,
    NorthWest,
}

fn main() {}

fn give_direction(direction: &MapDirection) {
    match direction {
        MapDirection::North => println!("You are heading north."),
        MapDirection::NorthEast => println!("You are heading northeast."),
        // So much more left to type...
        // ⚠️ because we didn't write every possible variant
    }
}
```

所以現在我們要在函數裡面導入MapDirection。也就是說，在函數裡面你可以直接寫`North`等。

```rust
enum MapDirection {
    North,
    NorthEast,
    East,
    SouthEast,
    South,
    SouthWest,
    West,
    NorthWest,
}

fn main() {}

fn give_direction(direction: &MapDirection) {
    use MapDirection::*; // Import everything in MapDirection
    let m = "You are heading";

    match direction {
        North => println!("{} north.", m),
        NorthEast => println!("{} northeast.", m),
        // This is a bit better
        // ⚠️
    }
}
```

我們已經看到`::*`的意思是 "導入::之後的所有內容"。在我們的例子中，這意味著`North`，`NorthEast`......一直到`NorthWest`。當你導入別人的代碼時，你也可以這樣做，但如果代碼非常大，你可能會有問題。如果它有一些元素和你的代碼是一樣的呢？所以一般情況下最好不要一直使用`::*`，除非你有把握。很多時候你在別人的代碼裡看到一個叫`prelude`的部分，裡面有你可能需要的所有主要元素。那麼你通常會這樣使用:`name::prelude::*`。 我們將在 `modules` 和 `crates` 的章節中更多地討論這個問題。

您也可以使用 `as` 來更改名稱。例如，也許你正在使用別人的代碼，而你不能改變枚舉中的名稱。

```rust
enum FileState {
    CannotAccessFile,
    FileOpenedAndReady,
    NoSuchFileExists,
    SimilarFileNameInNextDirectory,
}

fn main() {}
```

那麼你就可以
1) 導入所有的東西
2) 更改名稱

```rust
enum FileState {
    CannotAccessFile,
    FileOpenedAndReady,
    NoSuchFileExists,
    SimilarFileNameInNextDirectory,
}

fn give_filestate(input: &FileState) {
    use FileState::{
        CannotAccessFile as NoAccess,
        FileOpenedAndReady as Good,
        NoSuchFileExists as NoFile,
        SimilarFileNameInNextDirectory as OtherDirectory
    };
    match input {
        NoAccess => println!("Can't access file."),
        Good => println!("Here is your file"),
        NoFile => println!("Sorry, there is no file by that name."),
        OtherDirectory => println!("Please check the other directory."),
    }
}

fn main() {}
```

所以現在你可以寫`OtherDirectory`而不是`FileState::SimilarFileNameInNextDirectory`。

## todo!宏

有時你想粗略寫點寫代碼幫助你想象你的項目。例如，想象一個簡單的項目，用書籍做一些事情。下面是你寫的時候的想法:

```rust
struct Book {} // Okay, first I need a book struct.
               // Nothing in there yet - will add later

enum BookType { // A book can be hardcover or softcover, so add an enum
    HardCover,
    SoftCover,
}

fn get_book(book: &Book) -> Option<String> {} // ⚠️ get_book should take a &Book and return an Option<String>

fn delete_book(book: Book) -> Result<(), String> {} // delete_book should take a Book and return a Result...
                                                    // TODO: impl block and make these functions methods...
fn check_book_type(book_type: &BookType) { // Let's make sure the match statement works
    match book_type {
        BookType::HardCover => println!("It's hardcover"),
        BookType::SoftCover => println!("It's softcover"),
    }
}

fn main() {
    let book_type = BookType::HardCover;
    check_book_type(&book_type); // Okay, let's check this function!
}
```

但Rust對`get_book`和`delete_book`不滿意。它說

```text
error[E0308]: mismatched types
  --> src\main.rs:32:29
   |
32 | fn get_book(book: &Book) -> Option<String> {}
   |    --------                 ^^^^^^^^^^^^^^ expected enum `std::option::Option`, found `()`
   |    |
   |    implicitly returns `()` as its body has no tail or `return` expression
   |
   = note:   expected enum `std::option::Option<std::string::String>`
           found unit type `()`

error[E0308]: mismatched types
  --> src\main.rs:34:31
   |
34 | fn delete_book(book: Book) -> Result<(), String> {}
   |    -----------                ^^^^^^^^^^^^^^^^^^ expected enum `std::result::Result`, found `()`
   |    |
   |    implicitly returns `()` as its body has no tail or `return` expression
   |
   = note:   expected enum `std::result::Result<(), std::string::String>`
           found unit type `()`
```

但是你現在不關心`get_book`和`delete_book`。這時你可以使用`todo!()`。如果你把這個加到函數中，Rust不會抱怨，而且會編譯。

```rust
struct Book {}

fn get_book(book: &Book) -> Option<String> {
    todo!() // todo means "I will do it later, please be quiet"
}

fn delete_book(book: Book) -> Result<(), String> {
    todo!()
}

fn main() {}
```

所以現在代碼編譯，你可以看到`check_book_type`的結果:`It's hardcover`。

但是要小心，因為它只是編譯--你不能使用函數。如果你調用裡面有`todo!()`的函數，它就會崩潰。

另外，`todo!()`函數仍然需要真實的輸入和輸出類型。如果你只寫這個，它將無法編譯。

```rust
struct Book {}

fn get_book(book: &Book) -> WorldsBestType { // ⚠️
    todo!()
}

fn main() {}
```

它會說

```text
error[E0412]: cannot find type `WorldsBestType` in this scope
  --> src\main.rs:32:29
   |
32 | fn get_book(book: &Book) -> WorldsBestType {
   |                             ^^^^^^^^^^^^^^ not found in this scope
```

`todo!()`其實和另一個宏一樣：`unimplemented!()`。程序員們經常使用 `unimplemented!()`，但打字時太長了，所以他們創建了 `todo!()`，它比較短。

## Rc

Rc的意思是 "reference counter"(引用計數器)。你知道在Rust中，每個變量只能有一個所有者。這就是為什麼這個不能工作的原因:

```rust
fn takes_a_string(input: String) {
    println!("It is: {}", input)
}

fn also_takes_a_string(input: String) {
    println!("It is: {}", input)
}

fn main() {
    let user_name = String::from("User MacUserson");

    takes_a_string(user_name);
    also_takes_a_string(user_name); // ⚠️
}
```

`takes_a_string`取了`user_name`之後，你就不能再使用了。這裡沒有問題:你可以直接給它`user_name.clone()`。但有時一個變量是一個結構的一部分，也許你不能克隆這個結構；或者`String`真的很長，你不想克隆它。這些都是`Rc`的一些原因，它讓你擁有多個所有者。`Rc`就像一個優秀的辦公人員。`Rc`寫下誰擁有所有權，以及有多少個。然後一旦所有者的數量下降到0，這個變量就可以消失了。

下面是如何使用`Rc`。首先想象兩個結構:一個叫 `City`，另一個叫 `CityData`。`City`有一個城市的信息，而`CityData`把所有的城市都放在`Vec`中。

```rust
#[derive(Debug)]
struct City {
    name: String,
    population: u32,
    city_history: String,
}

#[derive(Debug)]
struct CityData {
    names: Vec<String>,
    histories: Vec<String>,
}

fn main() {
    let calgary = City {
        name: "Calgary".to_string(),
        population: 1_200_000,
           // Pretend that this string is very very long
        city_history: "Calgary began as a fort called Fort Calgary that...".to_string(),
    };

    let canada_cities = CityData {
        names: vec![calgary.name], // This is using calgary.name, which is short
        histories: vec![calgary.city_history], // But this String is very long
    };

    println!("Calgary's history is: {}", calgary.city_history);  // ⚠️
}
```

當然，這是不可能的，因為`canada_cities`現在擁有數據，而`calgary`沒有。它說:

```text
error[E0382]: borrow of moved value: `calgary.city_history`
  --> src\main.rs:27:42
   |
24 |         histories: vec![calgary.city_history], // But this String is very long
   |                         -------------------- value moved here
...
27 |     println!("Calgary's history is: {}", calgary.city_history);  // ⚠️
   |                                          ^^^^^^^^^^^^^^^^^^^^ value borrowed here after move
   |
   = note: move occurs because `calgary.city_history` has type `std::string::String`, which does not implement the `Copy` trait
```

我們可以克隆名稱:`names: vec![calgary.name.clone()]`，但是我們不想克隆`city_history`，因為它很長。所以我們可以用一個`Rc`。

增加`use`的聲明。

```rust
use std::rc::Rc;

fn main() {}
```

然後用`Rc`把`String`包圍起來:

```rust
use std::rc::Rc;

#[derive(Debug)]
struct City {
    name: String,
    population: u32,
    city_history: Rc<String>,
}

#[derive(Debug)]
struct CityData {
    names: Vec<String>,
    histories: Vec<Rc<String>>,
}

fn main() {}
```

要添加一個新的引用，你必須`clone` `Rc`。但是等一下，我們不是想避免使用`.clone()`嗎？不完全是:我們不想克隆整個String。但是一個`Rc`的克隆只是克隆了指針--它基本上是沒有開銷的。這就像在一盒書上貼上一個名字貼紙，以表明有兩個人擁有它，而不是做一盒全新的書。

你可以用`item.clone()`或者用`Rc::clone(&item)`來克隆一個叫`item`的`Rc`。所以calgary.city_history有兩個所有者。
 我們可以用`Rc::strong_count(&item)`查詢擁有者數量。另外我們再增加一個新的所有者。現在我們的代碼是這樣的:

```rust
use std::rc::Rc;

#[derive(Debug)]
struct City {
    name: String,
    population: u32,
    city_history: Rc<String>, // String inside an Rc
}

#[derive(Debug)]
struct CityData {
    names: Vec<String>,
    histories: Vec<Rc<String>>, // A Vec of Strings inside Rcs
}

fn main() {
    let calgary = City {
        name: "Calgary".to_string(),
        population: 1_200_000,
           // Pretend that this string is very very long
        city_history: Rc::new("Calgary began as a fort called Fort Calgary that...".to_string()), // Rc::new() to make the Rc
    };

    let canada_cities = CityData {
        names: vec![calgary.name],
        histories: vec![calgary.city_history.clone()], // .clone() to increase the count
    };

    println!("Calgary's history is: {}", calgary.city_history);
    println!("{}", Rc::strong_count(&calgary.city_history));
    let new_owner = calgary.city_history.clone();
}
```

這就打印出了`2`。而`new_owner`現在是`Rc<String>`。現在如果我們用`println!("{}", Rc::strong_count(&calgary.city_history));`，我們得到`3`。

那麼，如果有強指針，是否有弱指針呢？是的，有。弱指針是有用的，因為如果兩個`Rc`互相指向對方，它們就不會死。這就是所謂的 "引用循環"。如果第1項對第2項有一個Rc，而第2項對第1項有一個Rc，它們不能到0，在這種情況下，要使用弱引用。那麼`Rc`就會對引用進行計數，但如果只有弱引用，那麼它就會死掉。你使用`Rc::downgrade(&item)`而不是`Rc::clone(&item)`來創建弱引用。另外，需要用`Rc::weak_count(&item)`來查看弱引用數。

## 多線程

如果你使用多個線程，你可以同時做很多事情。現代計算機有一個以上的核心，所以它們可以同時做多件事情，Rust讓你使用它們。Rust使用的線程被稱為 "OS線程"。OS線程意味著操作系統在不同的核上創建線程。(其他一些語言使用 "green threads"，功能較少)


你用`std::thread::spawn`創建線程，然後用一個閉包來告訴它該怎麼做。線程很有趣，因為它們同時運行，你可以測試它，看看會發生什麼。下面是一個簡單的例子。

```rust
fn main() {
    std::thread::spawn(|| {
        println!("I am printing something");
    });
}
```

如果你運行這個，每次都會不一樣。有時會打印，有時不會打印(這也取決於你的電腦速度)。這是因為有時`main()`在線程完成之前就完成了。而當`main()`完成後，程序就結束了。這在`for`循環中更容易看到。

```rust
fn main() {
    for _ in 0..10 { // set up ten threads
        std::thread::spawn(|| {
            println!("I am printing something");
        });
    }   // Now the threads start.
}       // How many can finish before main() ends here?
```

通常在`main`結束之前，大約會打印出四條線程，但總是不一樣。如果你的電腦速度比較快，那麼可能就不會打印了。另外，有時線程會崩潰。

```text
thread 'thread 'I am printing something
thread '<unnamed><unnamed>thread '' panicked at '<unnamed>I am printing something
' panicked at 'thread '<unnamed>cannot access stdout during shutdown' panicked at '<unnamed>thread 'cannot access stdout during
shutdown
```

這是在程序關閉時，線程試圖做一些正確的事情時出現的錯誤。

你可以給電腦做一些事情，這樣它就不會馬上關閉了。

```rust
fn main() {
    for _ in 0..10 {
        std::thread::spawn(|| {
            println!("I am printing something");
        });
    }
    for _ in 0..1_000_000 { // make the program declare "let x = 9" one million times
                            // It has to finish this before it can exit the main function
        let _x = 9;
    }
}
```

但這是一個讓線程有時間完成的愚蠢方法。更好的方法是將線程綁定到一個變量上。如果你加上 `let`，你就能創建一個 `JoinHandle`。你可以在`spawn`的簽名中看到這一點:

```text
pub fn spawn<F, T>(f: F) -> JoinHandle<T>
where
    F: FnOnce() -> T,
    F: Send + 'static,
    T: Send + 'static,
```

(`f`是閉包--我們將在後面學習如何將閉包放入我們的函數中)

所以現在我們每次都有`JoinHandle`。

```rust
fn main() {
    for _ in 0..10 {
        let handle = std::thread::spawn(|| {
            println!("I am printing something");
        });

    }
}
```

`handle`現在是`JoinHandle`。我們怎麼處理它呢？我們使用一個叫做 `.join()` 的方法。這個方法的意思是 "等待所有線程完成"(它等待線程加入它)。所以現在只要寫`handle.join()`，它就會等待每個線程完成。

```rust
fn main() {
    for _ in 0..10 {
        let handle = std::thread::spawn(|| {
            println!("I am printing something");
        });

        handle.join(); // Wait for the threads to finish
    }
}
```

現在我們就來瞭解一下三種類型的閉包。這三種類型是

- `FnOnce`: 取整個值
- `FnMut`: 取一個可變引用
- `Fn`: 取一個普通引用

如果可以的話，閉包會盡量使用`Fn`。但如果它需要改變值，它將使用 `FnMut`，而如果它需要取整個值，它將使用 `FnOnce`。`FnOnce`是個好名字，因為它解釋了它的作用:它取一次值，然後就不能再取了。

下面是一個例子。

```rust
fn main() {
    let my_string = String::from("I will go into the closure");
    let my_closure = || println!("{}", my_string);
    my_closure();
    my_closure();
}
```

`String`沒有實現`Copy`，所以`my_closure()`是`Fn`: 它拿到一個引用

如果我們改變`my_string`，它變成`FnMut`。

```rust
fn main() {
    let mut my_string = String::from("I will go into the closure");
    let mut my_closure = || {
        my_string.push_str(" now");
        println!("{}", my_string);
    };
    my_closure();
    my_closure();
}
```

這個打印:

```text
I will go into the closure now
I will go into the closure now now
```

而如果按值獲取，則是`FnOnce`。

```rust
fn main() {
    let my_vec: Vec<i32> = vec![8, 9, 10];
    let my_closure = || {
        my_vec
            .into_iter() // into_iter takes ownership
            .map(|x| x as u8) // turn it into u8
            .map(|x| x * 2) // multiply by 2
            .collect::<Vec<u8>>() // collect into a Vec
    };
    let new_vec = my_closure();
    println!("{:?}", new_vec);
}
```

我們是按值取的，所以我們不能多跑`my_closure()`次。這就是名字的由來。

那麼現在回到線程。讓我們試著從外部引入一個值:

```rust
fn main() {
    let mut my_string = String::from("Can I go inside the thread?");

    let handle = std::thread::spawn(|| {
        println!("{}", my_string); // ⚠️
    });

    handle.join();
}
```

編譯器說這個不行。

```text
error[E0373]: closure may outlive the current function, but it borrows `my_string`, which is owned by the current function
  --> src\main.rs:28:37
   |
28 |     let handle = std::thread::spawn(|| {
   |                                     ^^ may outlive borrowed value `my_string`
29 |         println!("{}", my_string);
   |                        --------- `my_string` is borrowed here
   |
note: function requires argument type to outlive `'static`
  --> src\main.rs:28:18
   |
28 |       let handle = std::thread::spawn(|| {
   |  __________________^
29 | |         println!("{}", my_string);
30 | |     });
   | |______^
help: to force the closure to take ownership of `my_string` (and any other referenced variables), use the `move` keyword
   |
28 |     let handle = std::thread::spawn(move || {
   |                                     ^^^^^^^
```

這條信息很長，但很有用:它說到``use the `move` keyword``。問題是我們可以在線程使用`my_string`時對它做任何事情，但線程並不擁有它。這將是不安全的。

讓我們試試其他行不通的東西。

```rust
fn main() {
    let mut my_string = String::from("Can I go inside the thread?");

    let handle = std::thread::spawn(|| {
        println!("{}", my_string); // now my_string is being used as a reference
    });

    std::mem::drop(my_string);  // ⚠️ We try to drop it here. But the thread still needs it.

    handle.join();
}
```

所以你要用`move`來取值，現在安全了:

```rust
fn main() {
    let mut my_string = String::from("Can I go inside the thread?");

    let handle = std::thread::spawn(move|| {
        println!("{}", my_string);
    });

    std::mem::drop(my_string);  // ⚠️ we can't drop, because handle has it. So this won't work

    handle.join();
}
```

所以我們把`std::mem::drop`刪掉，現在就可以了。`handle`取`my_string`，我們的代碼就安全了。

```rust
fn main() {
    let mut my_string = String::from("Can I go inside the thread?");

    let handle = std::thread::spawn(move|| {
        println!("{}", my_string);
    });

    handle.join();
}
```

所以只要記住:如果你在線程中需要一個來自線程外的值，你需要使用`move`。



## 函數中的閉包

閉包是偉大的。那麼我們如何把它們放到自己的函數中呢？

你可以創建自己的函數來接受閉包，但是在函數裡面就不那麼自由了，你必須決定類型。在函數外部，一個閉包可以在`Fn`、`FnMut`和`FnOnce`之間自行決定，但在函數內部你必須選擇一個。最好的理解方式是看幾個函數簽名。
 這裡是`.all()`的那個。我們記得，它檢查一個迭代器，看看所有的東西是否是`true`(取決於你決定是`true`還是`false`)。它的部分簽名是這樣說的。


```rust
    fn all<F>(&mut self, f: F) -> bool    // 🚧
    where
        F: FnMut(Self::Item) -> bool,
```

`fn all<F>`:這告訴你有一個通用類型`F`。一個閉包總是泛型，因為每次都是不同的類型。

`(&mut self, f: F)`:`&mut self`告訴你這是一個方法。`f: F`通常你看到的是一個閉包:這是變量名和類型。 當然，`f`和`F`並沒有什麼特別之處，它們可以是不同的名字。如果你願意，你可以寫`my_closure: Closure`--這並不重要。但在簽名中，你幾乎總是看到`f: F`。

接下來是關於閉包的部分:`F: FnMut(Self::Item) -> bool`。在這裡，它決定了閉包是 `FnMut`，所以它可以改變值。它改變了`Self::Item`的值，這是它所取的迭代器。而且它必須返回 `true` 或 `false`。

這裡是一個更簡單的簽名，有一個閉包。

```rust
fn do_something<F>(f: F)    // 🚧
where
    F: FnOnce(),
{
    f();
}
```

這只是說它接受一個閉包，取值(`FnOnce`=取值)，而不返回任何東西。所以現在我們可以調用這個什麼都不取的閉包，做我們喜歡做的事情。我們將創建一個 `Vec`，然後對它進行迭代，只是為了展示我們現在可以做什麼。

```rust
fn do_something<F>(f: F)
where
    F: FnOnce(),
{
    f();
}

fn main() {
    let some_vec = vec![9, 8, 10];
    do_something(|| {
        some_vec
            .into_iter()
            .for_each(|x| println!("The number is: {}", x));
    })
}
```

一個更真實的例子，我們將再次創建一個 `City` 結構體。這次 `City` 結構體有更多關於年份和人口的數據。它有一個 `Vec<u32>` 來表示所有的年份，還有一個 `Vec<u32>` 來表示所有的人口。

`City`有兩個方法:`new()`用於創建一個新的`City`, `.city_data()`有個閉包參數。當我們使用 `.city_data()` 時，它給我們提供了年份和人口以及一個閉包，所以我們可以對數據做我們想做的事情。閉包類型是 `FnMut`，所以我們可以改變數據。它看起來像這樣:

```rust
#[derive(Debug)]
struct City {
    name: String,
    years: Vec<u32>,
    populations: Vec<u32>,
}

impl City {
    fn new(name: &str, years: Vec<u32>, populations: Vec<u32>) -> Self {

        Self {
            name: name.to_string(),
            years,
            populations,
        }
    }

    fn city_data<F>(&mut self, mut f: F) // We bring in self, but only f is generic F. f is the closure

    where
        F: FnMut(&mut Vec<u32>, &mut Vec<u32>), // The closure takes mutable vectors of u32
                                                // which are the year and population data
    {
        f(&mut self.years, &mut self.populations) // Finally this is the actual function. It says
                                                  // "use a closure on self.years and self.populations"
                                                  // We can do whatever we want with the closure
    }
}

fn main() {
    let years = vec![
        1372, 1834, 1851, 1881, 1897, 1925, 1959, 1989, 2000, 2005, 2010, 2020,
    ];
    let populations = vec![
        3_250, 15_300, 24_000, 45_900, 58_800, 119_800, 283_071, 478_974, 400_378, 401_694,
        406_703, 437_619,
    ];
    // Now we can create our city
    let mut tallinn = City::new("Tallinn", years, populations);

    // Now we have a .city_data() method that has a closure. We can do anything we want.

    // First let's put the data for 5 years together and print it.
    tallinn.city_data(|city_years, city_populations| { // We can call the input anything we want
        let new_vec = city_years
            .into_iter()
            .zip(city_populations.into_iter()) // Zip the two together
            .take(5)                           // but only take the first 5
            .collect::<Vec<(_, _)>>(); // Tell Rust to decide the type inside the tuple
        println!("{:?}", new_vec);
    });

    // Now let's add some data for the year 2030
    tallinn.city_data(|x, y| { // This time we just call the input x and y
        x.push(2030);
        y.push(500_000);
    });

    // We don't want the 1834 data anymore
    tallinn.city_data(|x, y| {
        let position_option = x.iter().position(|x| *x == 1834);
        if let Some(position) = position_option {
            println!(
                "Going to delete {} at position {:?} now.",
                x[position], position
            ); // Confirm that we delete the right item
            x.remove(position);
            y.remove(position);
        }
    });

    println!(
        "Years left are {:?}\nPopulations left are {:?}",
        tallinn.years, tallinn.populations
    );
}
```

這將打印出我們調用`.city_data().`的所有時間的結果:

```text
[(1372, 3250), (1834, 15300), (1851, 24000), (1881, 45900), (1897, 58800)]
Going to delete 1834 at position 1 now.
Years left are [1372, 1851, 1881, 1897, 1925, 1959, 1989, 2000, 2005, 2010, 2020, 2030]
Populations left are [3250, 24000, 45900, 58800, 119800, 283071, 478974, 400378, 401694, 406703, 437619, 500000]
```


## impl Trait

`impl Trait`與泛型類似。你還記得，泛型使用一個類型 `T`(或任何其他名稱)，然後在程序編譯時決定。首先我們來看一個具體的類型:

```rust
fn gives_higher_i32(one: i32, two: i32) {
    let higher = if one > two { one } else { two };
    println!("{} is higher.", higher);
}

fn main() {
    gives_higher_i32(8, 10);
}
```

這個打印:`10 is higher.`.

但是這個只接受`i32`，所以現在我們要把它做成通用的。我們需要比較，我們需要用`{}`打印，所以我們的類型T需要`PartialOrd`和`Display`。記住，這意味著 "只接受已經實現`PartialOrd`和`Display`的類型"。

```rust
use std::fmt::Display;

fn gives_higher_i32<T: PartialOrd + Display>(one: T, two: T) {
    let higher = if one > two { one } else { two };
    println!("{} is higher.", higher);
}

fn main() {
    gives_higher_i32(8, 10);
}
```

現在我們來看看`impl Trait`，它也是類似的。我們可以引入一個類型 `impl Trait`，而不是 `T`。然後它將帶入一個實現該特性的類型。這幾乎是一樣的。

```rust
fn prints_it(input: impl Into<String> + std::fmt::Display) { // Takes anything that can turn into a String and has Display
    println!("You can print many things, including {}", input);
}

fn main() {
    let name = "Tuon";
    let string_name = String::from("Tuon");
    prints_it(name);
    prints_it(string_name);
}
```

然而，更有趣的是，我們可以返回 `impl Trait`，這讓我們可以返回閉包，因為它們的函數簽名是trait。你可以在有它們的方法的簽名中看到這一點。例如，這是 `.map()` 的簽名。

```rust
fn map<B, F>(self, f: F) -> Map<Self, F>     // 🚧
    where
        Self: Sized,
        F: FnMut(Self::Item) -> B,
    {
        Map::new(self, f)
    }
```

`fn map<B, F>(self, f: F)`的意思是，它需要兩個通用類型。`F`是指從實現`.map()`的容器中取一個元素的函數，`B`是該函數的返回類型。然後在`where`之後，我們看到的是trait bound。("trait bound"的意思是 "它必須有這個trait"。)一個是`Sized`，接下來是閉包簽名。它必須是一個 `FnMut`，並在 `Self::Item` 上做閉包，也就是你給它的迭代器。然後它返回`B`。

所以我們可以用同樣的方法來返回一個閉包。要返回一個閉包，使用 `impl`，然後是閉包簽名。一旦你返回它，你就可以像使用一個函數一樣使用它。下面是一個函數的小例子，它根據你輸入的文本給出一個閉包。如果你輸入 "double "或 "triple"，那麼它就會把它乘以2或3，否則就會返給你相同的數字。因為它是一個閉包，我們可以做任何我們想做的事情，所以我們也打印一條信息。

```rust
fn returns_a_closure(input: &str) -> impl FnMut(i32) -> i32 {
    match input {
        "double" => |mut number| {
            number *= 2;
            println!("Doubling number. Now it is {}", number);
            number
        },
        "triple" => |mut number| {
            number *= 40;
            println!("Tripling number. Now it is {}", number);
            number
        },
        _ => |number| {
            println!("Sorry, it's the same: {}.", number);
            number
        },
    }
}

fn main() {
    let my_number = 10;

    // Make three closures
    let mut doubles = returns_a_closure("double");
    let mut triples = returns_a_closure("triple");
    let mut quadruples = returns_a_closure("quadruple");

    doubles(my_number);
    triples(my_number);
    quadruples(my_number);
}
```

下面是一個比較長的例子。讓我們想象一下，在一個遊戲中，你的角色面對的是晚上比較強的怪物。我們可以創建一個叫`TimeOfDay`的枚舉來記錄一天的情況。你的角色叫西蒙，有一個叫`character_fear`的數字，也就是`f64`。它晚上上升，白天下降。我們將創建一個`change_fear`函數，改變他的恐懼，但也做其他事情，如寫消息。它大概是這樣的:


```rust
enum TimeOfDay { // just a simple enum
    Dawn,
    Day,
    Sunset,
    Night,
}

fn change_fear(input: TimeOfDay) -> impl FnMut(f64) -> f64 { // The function takes a TimeOfDay. It returns a closure.
                                                             // We use impl FnMut(64) -> f64 to say that it needs to
                                                             // change the value, and also gives the same type back.
    use TimeOfDay::*; // So we only have to write Dawn, Day, Sunset, Night
                      // Instead of TimeOfDay::Dawn, TimeOfDay::Day, etc.
    match input {
        Dawn => |x| { // This is the variable character_fear that we give it later
            println!("The morning sun has vanquished the horrible night. You no longer feel afraid.");
            println!("Your fear is now {}", x * 0.5);
            x * 0.5
        },
        Day => |x| {
            println!("What a nice day. Maybe put your feet up and rest a bit.");
            println!("Your fear is now {}", x * 0.2);
            x * 0.2
        },
        Sunset => |x| {
            println!("The sun is almost down! This is no good.");
            println!("Your fear is now {}", x * 1.4);
            x * 1.4
        },
        Night => |x| {
            println!("What a horrible night to have a curse.");
            println!("Your fear is now {}", x * 5.0);
            x * 5.0
        },
    }
}

fn main() {
    use TimeOfDay::*;
    let mut character_fear = 10.0; // Start Simon with 10

    let mut daytime = change_fear(Day); // Make four closures here to call every time we want to change Simon's fear.
    let mut sunset = change_fear(Sunset);
    let mut night = change_fear(Night);
    let mut morning = change_fear(Dawn);

    character_fear = daytime(character_fear); // Call the closures on Simon's fear. They give a message and change the fear number.
                                              // In real life we would have a Character struct and use it as a method instead,
                                              // like this: character_fear.daytime()
    character_fear = sunset(character_fear);
    character_fear = night(character_fear);
    character_fear = morning(character_fear);
}
```

這個打印:

```text
What a nice day. Maybe put your feet up and rest a bit.
Your fear is now 2
The sun is almost down! This is no good.
Your fear is now 2.8
What a horrible night to have a curse.
Your fear is now 14
The morning sun has vanquished the horrible night. You no longer feel afraid.
Your fear is now 7
```

## Arc

你還記得我們用`Rc`來給一個變量一個以上的所有者。如果我們在線程中做同樣的事情，我們需要一個 `Arc`。`Arc`的意思是 "atomic reference counter"(原子引用計數器)。原子的意思是它使用計算機的處理器，所以每次只寫一次數據。這一點很重要，因為如果兩個線程同時寫入數據，你會得到錯誤的結果。例如，想象一下，如果你能在Rust中做到這一點。

```rust
// 🚧
let mut x = 10;

for i in 0..10 { // Thread 1
    x += 1
}
for i in 0..10 { // Thread 2
    x += 1
}
```


如果線程1和線程2一起啟動，也許就會出現這種情況。

- 線程1看到10，寫下11，然後線程2看到11，寫下12 然後線程2看到11，寫入12。到目前為止沒有問題。
- 線程1看到12。同時，線程2看到12。線程一看到13，寫下13 線程2也寫了13 現在我們有13個，但應該是14個 Now we have 13, but it should be 14. 這是個大問題。

`Arc`使用處理器來確保這種情況不會發生，所以當你有線程時必須使用這種方法。不過不建議單線程上用`Arc`，因為`Rc`更快一些。

不過你不能只用一個`Arc`來改變數據。所以你用一個`Mutex`把數據包起來，然後用一個`Arc`把`Mutex`包起來。

所以我們用一個`Mutex`在一個`Arc`裡面來改變一個數字的值。首先我們設置一個線程。

```rust
fn main() {

    let handle = std::thread::spawn(|| {
        println!("The thread is working!") // Just testing the thread
    });

    handle.join().unwrap(); // Make the thread wait here until it is done
    println!("Exiting the program");
}
```

到目前為止，這個只打印:

```text
The thread is working!
Exiting the program
```

很好，現在讓我們把它放在`for`的循環中，進行`0..5`。

```rust
fn main() {

    let handle = std::thread::spawn(|| {
        for _ in 0..5 {
            println!("The thread is working!")
        }
    });

    handle.join().unwrap();
    println!("Exiting the program");
}
```

這也是可行的。我們得到以下結果:

```text
The thread is working!
The thread is working!
The thread is working!
The thread is working!
The thread is working!
Exiting the program
```

現在我們再加一個線程。每個線程都會做同樣的事情。你可以看到，這些線程是在同一時間工作的。有時會先打印`Thread 1 is working!`，但其他時候`Thread 2 is working!`先打印。這就是所謂的**併發**，也就是 "一起運行"的意思。

```rust
fn main() {

    let thread1 = std::thread::spawn(|| {
        for _ in 0..5 {
            println!("Thread 1 is working!")
        }
    });

    let thread2 = std::thread::spawn(|| {
        for _ in 0..5 {
            println!("Thread 2 is working!")
        }
    });

    thread1.join().unwrap();
    thread2.join().unwrap();
    println!("Exiting the program");
}
```

這將打印:

```text
Thread 1 is working!
Thread 1 is working!
Thread 1 is working!
Thread 1 is working!
Thread 1 is working!
Thread 2 is working!
Thread 2 is working!
Thread 2 is working!
Thread 2 is working!
Thread 2 is working!
Exiting the program
```

現在我們要改變`my_number`的數值。現在它是一個`i32`。我們將把它改為 `Arc<Mutex<i32>>`:一個可以改變的 `i32`，由 `Arc` 保護。

```rust
// 🚧
let my_number = Arc::new(Mutex::new(0));
```

現在我們有了這個，我們可以克隆它。每個克隆可以進入不同的線程。我們有兩個線程，所以我們將做兩個克隆。

```rust
// 🚧
let my_number = Arc::new(Mutex::new(0));

let my_number1 = Arc::clone(&my_number); // This clone goes into Thread 1
let my_number2 = Arc::clone(&my_number); // This clone goes into Thread 2
```

現在，我們已經將安全克隆連接到`my_number`，我們可以將它們`move`到其他線程中，沒有問題。

```rust
use std::sync::{Arc, Mutex};

fn main() {
    let my_number = Arc::new(Mutex::new(0));

    let my_number1 = Arc::clone(&my_number);
    let my_number2 = Arc::clone(&my_number);

    let thread1 = std::thread::spawn(move || { // Only the clone goes into Thread 1
        for _ in 0..10 {
            *my_number1.lock().unwrap() +=1; // Lock the Mutex, change the value
        }
    });

    let thread2 = std::thread::spawn(move || { // Only the clone goes into Thread 2
        for _ in 0..10 {
            *my_number2.lock().unwrap() += 1;
        }
    });

    thread1.join().unwrap();
    thread2.join().unwrap();
    println!("Value is: {:?}", my_number);
    println!("Exiting the program");
}
```

程序打印:

```text
Value is: Mutex { data: 20 }
Exiting the program
```

所以這是一個成功的案例。

然後我們可以將兩個線程連接在一起，形成一個`for`循環，並使代碼更短。

我們需要保存句柄，這樣我們就可以在循環外對每個線程調用`.join()`。如果我們在循環內這樣做，它將等待第一個線程完成後再啟動新的線程。

```rust
use std::sync::{Arc, Mutex};

fn main() {
    let my_number = Arc::new(Mutex::new(0));
    let mut handle_vec = vec![]; // JoinHandles will go in here

    for _ in 0..2 { // do this twice
        let my_number_clone = Arc::clone(&my_number); // Make the clone before starting the thread
        let handle = std::thread::spawn(move || { // Put the clone in
            for _ in 0..10 {
                *my_number_clone.lock().unwrap() += 1;
            }
        });
        handle_vec.push(handle); // save the handle so we can call join on it outside of the loop
                                 // If we don't push it in the vec, it will just die here
    }

    handle_vec.into_iter().for_each(|handle| handle.join().unwrap()); // call join on all handles
    println!("{:?}", my_number);
}
```

最後這個打印`Mutex { data: 20 }`。

這看起來很複雜，但`Arc<Mutex<SomeType>>>`在Rust中使用的頻率很高，所以它變得很自然。另外，你也可以隨時寫你的代碼，讓它更乾淨。這裡是同樣的代碼，多了一條`use`語句和兩個函數。這些函數並沒有做任何新的事情，但是它們把一些代碼從`main()`中移出。如果你很難讀懂的話，可以嘗試重寫這樣的代碼。

```rust
use std::sync::{Arc, Mutex};
use std::thread::spawn; // Now we just write spawn

fn make_arc(number: i32) -> Arc<Mutex<i32>> { // Just a function to make a Mutex in an Arc
    Arc::new(Mutex::new(number))
}

fn new_clone(input: &Arc<Mutex<i32>>) -> Arc<Mutex<i32>> { // Just a function so we can write new_clone
    Arc::clone(&input)
}

// Now main() is easier to read
fn main() {
    let mut handle_vec = vec![]; // each handle will go in here
    let my_number = make_arc(0);

    for _ in 0..2 {
        let my_number_clone = new_clone(&my_number);
        let handle = spawn(move || {
            for _ in 0..10 {
                let mut value_inside = my_number_clone.lock().unwrap();
                *value_inside += 1;
            }
        });
        handle_vec.push(handle);    // the handle is done, so put it in the vector
    }

    handle_vec.into_iter().for_each(|handle| handle.join().unwrap()); // Make each one wait

    println!("{:?}", my_number);
}
```

## Channels

A channel is an easy way to use many threads that send to one place.它們相當流行，因為它們很容易組合在一起。你可以在Rust中用`std::sync::mpsc`創建一個channel。`mpsc`的意思是 "多個生產者，單個消費者"，所以 "many threads sending to one place"。要啟動一個通道，你可以使用 `channel()`。這將創建一個 `Sender` 和一個 `Receiver`，它們被綁在一起。你可以在函數簽名中看到這一點。

```rust
// 🚧
pub fn channel<T>() -> (Sender<T>, Receiver<T>)
```

所以你要選擇一個發送者的名字和一個接收者的名字。通常你會看到像`let (sender, receiver) = channel();`這樣的開頭。因為它是泛型函數，如果你只寫這個，Rust不會知道類型。

```rust
use std::sync::mpsc::channel;

fn main() {
    let (sender, receiver) = channel(); // ⚠️
}
```

編譯器說:

```text
error[E0282]: type annotations needed for `(std::sync::mpsc::Sender<T>, std::sync::mpsc::Receiver<T>)`
  --> src\main.rs:30:30
   |
30 |     let (sender, receiver) = channel();
   |         ------------------   ^^^^^^^ cannot infer type for type parameter `T` declared on the function `channel`
   |         |
   |         consider giving this pattern the explicit type `(std::sync::mpsc::Sender<T>, std::sync::mpsc::Receiver<T>)`, where
the type parameter `T` is specified
```

它建議為`Sender`和`Receiver`添加一個類型。如果你願意的話，可以這樣做:

```rust
use std::sync::mpsc::{channel, Sender, Receiver}; // Added Sender and Receiver here

fn main() {
    let (sender, receiver): (Sender<i32>, Receiver<i32>) = channel();
}
```

但你不必這樣做: 一旦你開始使用`Sender`和`Receiver`，Rust就能猜到類型。

所以我們來看一下最簡單的使用通道的方法。

```rust
use std::sync::mpsc::channel;

fn main() {
    let (sender, receiver) = channel();

    sender.send(5);
    receiver.recv(); // recv = receive, not "rec v"
}
```

現在編譯器知道類型了。`sender`是`Result<(), SendError<i32>>`，`receiver`是`Result<i32, RecvError>`。所以你可以用`.unwrap()`來看看發送是否有效，或者使用更好的錯誤處理。我們加上`.unwrap()`，也加上`println!`，看看得到什麼。

```rust
use std::sync::mpsc::channel;

fn main() {
    let (sender, receiver) = channel();

    sender.send(5).unwrap();
    println!("{}", receiver.recv().unwrap());
}
```

這樣就可以打印出`5`。

`channel`就像`Arc`一樣，因為你可以克隆它，並將克隆的內容發送到其他線程中。讓我們創建兩個線程，並將值發送到`receiver`。這段代碼可以工作，但它並不完全是我們想要的。

```rust
use std::sync::mpsc::channel;

fn main() {
    let (sender, receiver) = channel();
    let sender_clone = sender.clone();

    std::thread::spawn(move|| { // move sender in
        sender.send("Send a &str this time").unwrap();
    });

    std::thread::spawn(move|| { // move sender_clone in
        sender_clone.send("And here is another &str").unwrap();
    });

    println!("{}", receiver.recv().unwrap());
}
```

兩個線程開始發送，然後我們`println!`。它可能會打印 `Send a &str this time` 或 `And here is another &str`，這取決於哪個線程先完成。讓我們創建一個join句柄來等待它們完成。

```rust
use std::sync::mpsc::channel;

fn main() {
    let (sender, receiver) = channel();
    let sender_clone = sender.clone();
    let mut handle_vec = vec![]; // Put our handles in here

    handle_vec.push(std::thread::spawn(move|| {  // push this into the vec
        sender.send("Send a &str this time").unwrap();
    }));

    handle_vec.push(std::thread::spawn(move|| {  // and push this into the vec
        sender_clone.send("And here is another &str").unwrap();
    }));

    for _ in handle_vec { // now handle_vec has 2 items. Let's print them
        println!("{:?}", receiver.recv().unwrap());
    }
}
```

這個將打印:

```text
"Send a &str this time"
"And here is another &str"
```

現在我們不打印，我們創建一個`results_vec`。

```rust
use std::sync::mpsc::channel;

fn main() {
    let (sender, receiver) = channel();
    let sender_clone = sender.clone();
    let mut handle_vec = vec![];
    let mut results_vec = vec![];

    handle_vec.push(std::thread::spawn(move|| {
        sender.send("Send a &str this time").unwrap();
    }));

    handle_vec.push(std::thread::spawn(move|| {
        sender_clone.send("And here is another &str").unwrap();
    }));

    for _ in handle_vec {
        results_vec.push(receiver.recv().unwrap());
    }

    println!("{:?}", results_vec);
}
```

現在結果在我們的vec中:`["Send a &str this time", "And here is another &str"]`。

現在讓我們假設我們有很多工作要做，並且想要使用線程。我們有一個大的VEC，裡面有1百萬個元素，都是0，我們想把每個0都變成1，我們將使用10個線程，每個線程將做十分之一的工作。我們將創建一個新的VEC，並使用`.extend()`來收集結果。

```rust
use std::sync::mpsc::channel;
use std::thread::spawn;

fn main() {
    let (sender, receiver) = channel();
    let hugevec = vec![0; 1_000_000];
    let mut newvec = vec![];
    let mut handle_vec = vec![];

    for i in 0..10 {
        let sender_clone = sender.clone();
        let mut work: Vec<u8> = Vec::with_capacity(hugevec.len() / 10); // new vec to put the work in. 1/10th the size
        work.extend(&hugevec[i*100_000..(i+1)*100_000]); // first part gets 0..100_000, next gets 100_000..200_000, etc.
        let handle =spawn(move || { // make a handle

            for number in work.iter_mut() { // do the actual work
                *number += 1;
            };
            sender_clone.send(work).unwrap(); // use the sender_clone to send the work to the receiver
        });
        handle_vec.push(handle);
    }

    for handle in handle_vec { // stop until the threads are done
        handle.join().unwrap();
    }

    while let Ok(results) = receiver.try_recv() {
        newvec.push(results); // push the results from receiver.recv() into the vec
    }

    // Now we have a Vec<Vec<u8>>. To put it together we can use .flatten()
    let newvec = newvec.into_iter().flatten().collect::<Vec<u8>>(); // Now it's one vec of 1_000_000 u8 numbers

    println!("{:?}, {:?}, total length: {}", // Let's print out some numbers to make sure they are all 1
        &newvec[0..10], &newvec[newvec.len()-10..newvec.len()], newvec.len() // And show that the length is 1_000_000 items
    );

    for number in newvec { // And let's tell Rust that it can panic if even one number is not 1
        if number != 1 {
            panic!();
        }
    }
}
```

## 閱讀Rust文檔

知道如何閱讀Rust中的文檔是很重要的，這樣你就可以理解其他人寫的東西。這裡有一些Rust文檔中需要知道的事情。

### assert_eq!


你在做測試的時候看到`assert_eq!`是用的。你把兩個元素放在函數裡面，如果它們不相等，程序就會崩潰。下面是一個簡單的例子，我們需要一個偶數。

```rust
fn main() {
    prints_number(56);
}

fn prints_number(input: i32) {
    assert_eq!(input % 2, 0); // number must be equal.
                              // If number % 2 is not 0, it panics
    println!("The number is not odd. It is {}", input);
}
```

也許你沒有任何計劃在你的代碼中使用`assert_eq!`，但它在Rust文檔中隨處可見。這是因為在一個文檔中，你需要很大的空間來`println!`一切。另外，你會需要`Display`或`Debug`來打印你想打印的東西。這就是為什麼文檔中到處都有`assert_eq!`的原因。下面是這裡的一個例子[https://doc.rust-lang.org/std/vec/struct.Vec.html](https://doc.rust-lang.org/std/vec/struct.Vec.html)，展示瞭如何使用Vec。

```rust
fn main() {
    let mut vec = Vec::new();
    vec.push(1);
    vec.push(2);

    assert_eq!(vec.len(), 2);
    assert_eq!(vec[0], 1);

    assert_eq!(vec.pop(), Some(2));
    assert_eq!(vec.len(), 1);

    vec[0] = 7;
    assert_eq!(vec[0], 7);

    vec.extend([1, 2, 3].iter().copied());

    for x in &vec {
        println!("{}", x);
    }
    assert_eq!(vec, [7, 1, 2, 3]);
}
```

在這些例子中，你可以只把`assert_eq!(a, b)`看成是在說 "a是b"。現在看看右邊帶有註釋的同一個例子。註釋顯示了它的實際含義。

```rust
fn main() {
    let mut vec = Vec::new();
    vec.push(1);
    vec.push(2);

    assert_eq!(vec.len(), 2); // "The vec length is 2"
    assert_eq!(vec[0], 1); // "vec[0] is 1"

    assert_eq!(vec.pop(), Some(2)); // "When you use .pop(), you get Some()"
    assert_eq!(vec.len(), 1); // "The vec length is now 1"

    vec[0] = 7;
    assert_eq!(vec[0], 7); // "Vec[0] is 7"

    vec.extend([1, 2, 3].iter().copied());

    for x in &vec {
        println!("{}", x);
    }
    assert_eq!(vec, [7, 1, 2, 3]); // "The vec now has [7, 1, 2, 3]"
}
```

### 搜索

Rust 文檔的頂部欄是搜索欄。它在你輸入時顯示結果。當你往下翻時，你不能再看到搜索欄，但如果你按鍵盤上的**s**鍵，你可以再次搜索。所以在任何地方按**s**鍵可以讓你馬上搜索。

### [src] 按鈕

通常一個方法、結構體等的代碼不會是完整的。這是因為你通常不需要看到完整的源碼就能知道它是如何工作的，而完整的代碼可能會讓人困惑。但如果你想知道更多，你可以點擊[src]就可以看到所有的內容。例如，在`String`的頁面上，你可以看到`.with_capacity()`的這個簽名。

```rust
// 🚧
pub fn with_capacity(capacity: usize) -> String
```

好了，你輸入一個數字，它給你一個`String`。這很簡單，但也許我們很好奇，想看更多。如果你點擊[src]你可以看到這個。

```rust
// 🚧
pub fn with_capacity(capacity: usize) -> String {
    String { vec: Vec::with_capacity(capacity) }
}
```

有趣的是，現在你可以看到，字符串是`Vec`的一種。而實際上一個`String`是一個`u8`字節的向量，這很有意思。你不需要知道，就可以使用`with_capacity`的方法，你只有點擊[src]才能看到。所以如果文檔沒有太多細節，而你又想知道更多的話，點擊[src]是個好主意。

### trait信息

trait文檔的重要部分是左邊的 "Required Methods"。如果你看到 "Required Methods"，可能意味著你必須自己編寫方法。例如，對於 `Iterator`，你需要寫 `.next()` 方法。而對於`From`，你需要寫`.from()`方法。但是有些trait只需要一個**屬性**就可以實現，比如我們在`#[derive(Debug)]`中看到的。`Debug`需要`.fmt()`方法，但通常你只需要使用`#[derive(Debug)]`，除非你想自己做。這就是為什麼在`std::fmt::Debug`的頁面上說 "一般來說，你應該直接派生出一個Debug實現"。

## 屬性

你以前見過`#[derive(Debug)]`這樣的代碼:這種類型的代碼叫做*屬性*。這些屬性是給編譯器提供信息的小段代碼。它們不容易創建，但使用起來非常方便。如果你只用`#`寫一個屬性，那麼它將影響下一行的代碼。但如果你用`#!`來寫，那麼它將影響自己空間裡的一切。

下面是一些你會經常看到的屬性。

`#[allow(dead_code)]` 和 `#[allow(unused_variables)]`。 如果你寫了不用的代碼，Rust仍然會編譯，但會讓你知道。例如，這裡有一個結構體，裡面什麼都沒有，只有一個變量。我們不使用它們中的任何一個。

```rust
struct JustAStruct {}

fn main() {
    let some_char = 'ん';
}
```

如果你這樣寫，Rust會提醒你，你沒有使用它們。

```text
warning: unused variable: `some_char`
 --> src\main.rs:4:9
  |
4 |     let some_char = 'ん';
  |         ^^^^^^^^^ help: if this is intentional, prefix it with an underscore: `_some_char`
  |
  = note: `#[warn(unused_variables)]` on by default

warning: struct is never constructed: `JustAStruct`
 --> src\main.rs:1:8
  |
1 | struct JustAStruct {}
  |        ^^^^^^^^^^^
  |
  = note: `#[warn(dead_code)]` on by default
```

我們知道，可以在名字前寫一個`_`，讓編譯器安靜下來。

```rust
struct _JustAStruct {}

fn main() {
    let _some_char = 'ん';
}
```

但你也可以使用屬性。你會注意到在消息中，它使用了`#[warn(unused_variables)]`和`#[warn(dead_code)]`。在我們的代碼中，`JustAStruct`是死代碼，而`some_char`是一個未使用的變量。`warn`的反義詞是`allow`，所以我們可以這樣寫，它不會說什麼。

```rust
#![allow(dead_code)]
#![allow(unused_variables)]

struct Struct1 {} // Create five structs
struct Struct2 {}
struct Struct3 {}
struct Struct4 {}
struct Struct5 {}

fn main() {
    let char1 = 'ん'; // and four variables. We don't use any of them but the compiler is quiet
    let char2 = ';';
    let some_str = "I'm just a regular &str";
    let some_vec = vec!["I", "am", "just", "a", "vec"];
}
```

當然，處理死代碼和未使用的變量是很重要的。但有時你希望編譯器安靜一段時間。或者您可能需要展示一些代碼或教人們Rust，但又不想用編譯器的信息來迷惑他們。

`#[derive(TraitName)]`讓你可以為你創建的結構和枚舉派生一些trait。這適用於許多可以自動派生的常見trait。有些像 `Display` 這樣的特性不能自動衍生，因為對於 `Display`，你必須選擇如何顯示。

```rust
// ⚠️
#[derive(Display)]
struct HoldsAString {
    the_string: String,
}

fn main() {
    let my_string = HoldsAString {
        the_string: "Here I am!".to_string(),
    };
}
```

錯誤信息會告訴你:

```text
error: cannot find derive macro `Display` in this scope
 --> src\main.rs:2:10
  |
2 | #[derive(Display)]
  |
```

但是對於可以自動推導出的trait，你可以隨心所欲的放進去。讓我們給`HoldsAString`在一行中加入七個trait，只是為了好玩，儘管它只需要一個。

```rust
#[derive(Debug, PartialEq, Eq, Ord, PartialOrd, Hash, Clone)]
struct HoldsAString {
    the_string: String,
}

fn main() {
    let my_string = HoldsAString {
        the_string: "Here I am!".to_string(),
    };
    println!("{:?}", my_string);
}
```

另外，如果(也只有在)它的字段都實現了`Copy`的情況下，你才可以創建一個`Copy`結構。`HoldsAString`包含`String`，它沒有實現`Copy`，所以你不能對它使用`#[derive(Copy)]`。但是對下面這個結構你可以:

```rust
#[derive(Clone, Copy)] // You also need Clone to use Copy
struct NumberAndBool {
    number: i32, // i32 is Copy
    true_or_false: bool // bool is also Copy. So no problem
}

fn does_nothing(input: NumberAndBool) {

}

fn main() {
    let number_and_bool = NumberAndBool {
        number: 8,
        true_or_false: true
    };

    does_nothing(number_and_bool);
    does_nothing(number_and_bool); // If it didn't have copy, this would make an error
}
```


`#[cfg()]`的意思是配置，告訴編譯器是否運行代碼。它通常是這樣的:`#[cfg(test)]`。你在寫測試函數的時候用這個，這樣它就知道除非你在測試，否則不要運行它們。那麼你可以在你的代碼附近寫測試，但編譯器不會運行它們，除非你告訴編譯器。

還有一個使用`cfg`的例子是`#[cfg(target_os = "windows")]`。有了它，你可以告訴編譯器只在Windows，Linux或其他平臺則不能運行代碼。

`#![no_std]`是一個有趣的屬性，它告訴Rust不要引入標準庫。這意味著你沒有`Vec`，`String`，以及標準庫中的其他任何東西。你會在那些沒有多少內存或空間的小型設備的代碼中看到這個。

你可以在[這裡](https://doc.rust-lang.org/reference/attributes.html)看到更多的屬性。


## Box

`Box` 是 Rust 中一個非常方便的類型。當你使用`Box`時，你可以把一個類型放在堆上而不是棧上。要創建一個新的 `Box`，只需使用 `Box::new()` 並將元素放在裡面即可。

```rust
fn just_takes_a_variable<T>(item: T) {} // Takes anything and drops it.

fn main() {
    let my_number = 1; // This is an i32
    just_takes_a_variable(my_number);
    just_takes_a_variable(my_number); // Using this function twice is no problem, because it's Copy

    let my_box = Box::new(1); // This is a Box<i32>
    just_takes_a_variable(my_box.clone()); // Without .clone() the second function would make an error
    just_takes_a_variable(my_box); // because Box is not Copy
}
```

一開始很難想象在哪裡使用它，但你在Rust中經常使用它。你記得`&`是用於`str`的，因為編譯器不知道`str`的大小:它可以是任何長度。但是`&`的引用總是相同的長度，所以編譯器可以使用它。`Box`也是類似的。另外，你也可以在`Box`上使用`*`來獲取值，就像使用`&`一樣。

```rust
fn main() {
    let my_box = Box::new(1); // This is a Box<i32>
    let an_integer = *my_box; // This is an i32
    println!("{:?}", my_box);
    println!("{:?}", an_integer);
}
```

這就是為什麼Box被稱為 "智能指針"的原因，因為它就像`&`的引用(指針的一種)，但可以做更多的事情。

你也可以使用Box來創建裡面有相同結構的結構體。這些結構被稱為*遞歸*，這意味著在Struct A裡面也許是另一個Struct A，有時你可以使用Box來創建鏈表，儘管這在Rust中並不十分流行。但如果你想創建一個遞歸結構，你可以使用`Box`。如果你試著不用 `Box` 會發生什麼:


```rust
struct List {
    item: Option<List>, // ⚠️
}
```

這個簡單的`List`有一項，可能是`Some<List>`(另一個列表)，也可能是`None`。因為你可以選擇`None`，所以它不會永遠遞歸。但是編譯器還是不知道大小。

```text
error[E0072]: recursive type `List` has infinite size
  --> src\main.rs:16:1
   |
16 | struct List {
   | ^^^^^^^^^^^ recursive type has infinite size
17 |     item: Option<List>,
   |     ------------------ recursive without indirection
   |
   = help: insert indirection (e.g., a `Box`, `Rc`, or `&`) at some point to make `List` representable
```

你可以看到，它甚至建議嘗試`Box`。所以我們用`Box`把List包裹起來。

```rust
struct List {
    item: Option<Box<List>>,
}
fn main() {}
```

現在編譯器用`List`就可以了，因為所有的東西都在`Box`後面，而且它知道`Box`的大小。那麼一個非常簡單的列表可能是這樣的:

```rust
struct List {
    item: Option<Box<List>>,
}

impl List {
    fn new() -> List {
        List {
            item: Some(Box::new(List { item: None })),
        }
    }
}

fn main() {
    let mut my_list = List::new();
}
```

即使沒有數據也有點複雜，Rust並不怎麼使用這種類型的模式。這是因為Rust對借用和所有權有嚴格的規定，你知道的。但如果你想啟動一個這樣的列表(鏈表)，`Box`可以幫助你。

`Box`還可以讓你在上面使用`std::mem::drop`，因為它在堆上。這有時會很方便。

## 用Box包裹trait

`Box`對於返回trait非常有用。你可以像這個例子一樣用泛型函數寫trait:

```rust
use std::fmt::Display;

struct DoesntImplementDisplay {}

fn displays_it<T: Display>(input: T) {
    println!("{}", input);
}

fn main() {}
```

這個只能接受`Display`的東西，所以它不能接受我們的`DoesntImplementDisplay`結構。但是它可以接受很多其他的東西，比如`String`。

你也看到了，我們可以使用 `impl Trait` 來返回其他的trait，或者閉包。`Box`也可以用類似的方式使用。你可以使用 `Box`，否則編譯器將不知道值的大小。這個例子表明，trait可以用在任何大小的東西上:

```rust
#![allow(dead_code)] // Tell the compiler to be quiet
use std::mem::size_of; // This gives the size of a type

trait JustATrait {} // We will implement this on everything

enum EnumOfNumbers {
    I8(i8),
    AnotherI8(i8),
    OneMoreI8(i8),
}
impl JustATrait for EnumOfNumbers {}

struct StructOfNumbers {
    an_i8: i8,
    another_i8: i8,
    one_more_i8: i8,
}
impl JustATrait for StructOfNumbers {}

enum EnumOfOtherTypes {
    I8(i8),
    AnotherI8(i8),
    Collection(Vec<String>),
}
impl JustATrait for EnumOfOtherTypes {}

struct StructOfOtherTypes {
    an_i8: i8,
    another_i8: i8,
    a_collection: Vec<String>,
}
impl JustATrait for StructOfOtherTypes {}

struct ArrayAndI8 {
    array: [i8; 1000], // This one will be very large
    an_i8: i8,
    in_u8: u8,
}
impl JustATrait for ArrayAndI8 {}

fn main() {
    println!(
        "{}, {}, {}, {}, {}",
        size_of::<EnumOfNumbers>(),
        size_of::<StructOfNumbers>(),
        size_of::<EnumOfOtherTypes>(),
        size_of::<StructOfOtherTypes>(),
        size_of::<ArrayAndI8>(),
    );
}
```

當我們打印這些東西的size的時候，我們得到`2, 3, 32, 32, 1002`。所以如果你像下面這樣做的話，會得到一個錯誤：

```rust
// ⚠️
fn returns_just_a_trait() -> JustATrait {
    let some_enum = EnumOfNumbers::I8(8);
    some_enum
}
```

它說：

```text
error[E0746]: return type cannot have an unboxed trait object
  --> src\main.rs:53:30
   |
53 | fn returns_just_a_trait() -> JustATrait {
   |                              ^^^^^^^^^^ doesn't have a size known at compile-time
```

而這是真的，因為size可以是2，3，32，1002，或者其他任何東西。所以我們把它放在一個`Box`中。在這裡我們還要加上`dyn`這個關鍵詞。`dyn`這個詞告訴你，你說的是一個trait，而不是一個結構體或其他任何東西。

所以你可以把函數改成這樣。

```rust
// 🚧
fn returns_just_a_trait() -> Box<dyn JustATrait> {
    let some_enum = EnumOfNumbers::I8(8);
    Box::new(some_enum)
}
```

現在它工作了，因為在棧上只是一個`Box`，我們知道`Box`的大小。

你會經常看到`Box<dyn Error>`這種形式，因為有時你可能會有多個可能的錯誤。

我們可以快速創建兩個錯誤類型來顯示這一點。要創建一個正式的錯誤類型，你必須為它實現`std::error::Error`。這部分很容易:只要寫出 `impl std::error::Error {}`。但錯誤還需要`Debug`和`Display`，這樣才能給出問題的信息。`Debug`只要加上`#[derive(Debug)]`就行，很容易，但`Display`需要`.fmt()`方法。我們之前做過一次。

代碼是這樣的:

```rust
use std::error::Error;
use std::fmt;

#[derive(Debug)]
struct ErrorOne;

impl Error for ErrorOne {} // Now it is an error type with Debug. Time for Display:

impl fmt::Display for ErrorOne {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "You got the first error!") // All it does is write this message
    }
}


#[derive(Debug)] // Do the same thing with ErrorTwo
struct ErrorTwo;

impl Error for ErrorTwo {}

impl fmt::Display for ErrorTwo {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "You got the second error!")
    }
}

// Make a function that just returns a String or an error
fn returns_errors(input: u8) -> Result<String, Box<dyn Error>> { // With Box<dyn Error> you can return anything that has the Error trait

    match input {
        0 => Err(Box::new(ErrorOne)), // Don't forget to put it in a box
        1 => Err(Box::new(ErrorTwo)),
        _ => Ok("Looks fine to me".to_string()), // This is the success type
    }

}

fn main() {

    let vec_of_u8s = vec![0_u8, 1, 80]; // Three numbers to try out

    for number in vec_of_u8s {
        match returns_errors(number) {
            Ok(input) => println!("{}", input),
            Err(message) => println!("{}", message),
        }
    }
}
```

這將打印:

```text
You got the first error!
You got the second error!
Looks fine to me
```

如果我們沒有`Box<dyn Error>`，寫了這個，我們就有問題了。

```rust
// ⚠️
fn returns_errors(input: u8) -> Result<String, Error> {
    match input {
        0 => Err(ErrorOne),
        1 => Err(ErrorTwo),
        _ => Ok("Looks fine to me".to_string()),
    }
}
```

它會告訴你。

```text
21  | fn returns_errors(input: u8) -> Result<String, Error> {
    |                                 ^^^^^^^^^^^^^^^^^^^^^ doesn't have a size known at compile-time
```

這並不奇怪，因為我們知道，一個trait可以作用於很多東西，而且它們各自有不同的大小。

## 默認值和建造者模式


你可以實現 `Default` trait，給你認為最常見的 `struct` 或 `enum` 賦值。建造者模式可以很好地與之配合，讓用戶在需要時輕鬆地進行修改。首先我們來看看`Default`。實際上，Rust中的大多數通用類型已經有`Default`。它們並不奇怪。0, ""(空字符串), `false`, 等等。

```rust
fn main() {
    let default_i8: i8 = Default::default();
    let default_str: String = Default::default();
    let default_bool: bool = Default::default();

    println!("'{}', '{}', '{}'", default_i8, default_str, default_bool);
}
```

這將打印`'0', '', 'false'`。

所以`Default`就像`new`函數一樣，除了你不需要輸入任何東西。首先我們要創建一個`struct`，它還沒有實現`Default`。它有一個`new`函數，我們用它來創建一個名為Billy的角色，並提供一些統計信息。

```rust
struct Character {
    name: String,
    age: u8,
    height: u32,
    weight: u32,
    lifestate: LifeState,
}

enum LifeState {
    Alive,
    Dead,
    NeverAlive,
    Uncertain
}

impl Character {
    fn new(name: String, age: u8, height: u32, weight: u32, alive: bool) -> Self {
        Self {
            name,
            age,
            height,
            weight,
            lifestate: if alive { LifeState::Alive } else { LifeState::Dead },
        }
    }
}

fn main() {
    let character_1 = Character::new("Billy".to_string(), 15, 170, 70, true);
}
```

但也許在我們的世界裡，我們希望大部分角色都叫比利，年齡15歲，身高170，體重70，還活著。我們可以實現`Default`，這樣我們就可以直接寫`Character::default()`。它看起來是這樣的:

```rust
#[derive(Debug)]
struct Character {
    name: String,
    age: u8,
    height: u32,
    weight: u32,
    lifestate: LifeState,
}

#[derive(Debug)]
enum LifeState {
    Alive,
    Dead,
    NeverAlive,
    Uncertain,
}

impl Character {
    fn new(name: String, age: u8, height: u32, weight: u32, alive: bool) -> Self {
        Self {
            name,
            age,
            height,
            weight,
            lifestate: if alive {
                LifeState::Alive
            } else {
                LifeState::Dead
            },
        }
    }
}

impl Default for Character {
    fn default() -> Self {
        Self {
            name: "Billy".to_string(),
            age: 15,
            height: 170,
            weight: 70,
            lifestate: LifeState::Alive,
        }
    }
}

fn main() {
    let character_1 = Character::default();

    println!(
        "The character {:?} is {:?} years old.",
        character_1.name, character_1.age
    );
}
```

打印出`The character "Billy" is 15 years old.`，簡單多了!

現在我們來看建造者模式。我們會有很多Billy，所以我們會保留默認的。但是很多其他角色只會有一點不同。建造者模式讓我們可以把小方法鏈接起來，每次改變一個值。這裡是一個`Character`的方法:

```rust
fn height(mut self, height: u32) -> Self {    // 🚧
    self.height = height;
    self
}
```

一定要注意，它取的是`mut self`。我們之前看到過一次，它不是一個可變引用(`&mut self`)。它佔用了`Self`的所有權，有了`mut`，它將是可變的，即使它之前不是可變的。這是因為`.height()`擁有完全的所有權，別人不能碰它，所以它是安全的，可變。它只是改變`self.height`，然後返回`Self`(就是`Character`)。

所以我們有三個這樣的構建方法。它們幾乎是一樣的:

```rust
fn height(mut self, height: u32) -> Self {     // 🚧
    self.height = height;
    self
}

fn weight(mut self, weight: u32) -> Self {
    self.weight = weight;
    self
}

fn name(mut self, name: &str) -> Self {
    self.name = name.to_string();
    self
}
```

每一個都會改變一個變量，並回饋給`Self`:這就是你在建造者模式中看到的。所以現在我們類似這樣寫來創建一個角色:`let character_1 = Character::default().height(180).weight(60).name("Bobby");`。如果你正在構建一個庫給別人使用，這可以讓他們很容易用起來。對最終用戶來說很容易，因為它幾乎看起來像自然的英語。"給我一個默認角色，身高為180，體重為60，名字為Bobby." 到目前為止，我們的代碼看起來是這樣的:

```rust
#[derive(Debug)]
struct Character {
    name: String,
    age: u8,
    height: u32,
    weight: u32,
    lifestate: LifeState,
}

#[derive(Debug)]
enum LifeState {
    Alive,
    Dead,
    NeverAlive,
    Uncertain,
}

impl Character {
    fn new(name: String, age: u8, height: u32, weight: u32, alive: bool) -> Self {
        Self {
            name,
            age,
            height,
            weight,
            lifestate: if alive {
                LifeState::Alive
            } else {
                LifeState::Dead
            },
        }
    }

    fn height(mut self, height: u32) -> Self {
        self.height = height;
        self
    }

    fn weight(mut self, weight: u32) -> Self {
        self.weight = weight;
        self
    }

    fn name(mut self, name: &str) -> Self {
        self.name = name.to_string();
        self
    }
}

impl Default for Character {
    fn default() -> Self {
        Self {
            name: "Billy".to_string(),
            age: 15,
            height: 170,
            weight: 70,
            lifestate: LifeState::Alive,
        }
    }
}

fn main() {
    let character_1 = Character::default().height(180).weight(60).name("Bobby");

    println!("{:?}", character_1);
}
```

最後一個要添加的方法通常叫`.build()`。這個方法是一種最終檢查。當你給用戶提供一個像`.height()`這樣的方法時，你可以確保他們只輸入一個`u32()`，但是如果他們輸入5000的身高怎麼辦？這在你正在做的遊戲中可能就不對了。我們最後將使用一個名為`.build()`的方法，返回一個`Result`。在它裡面我們將檢查用戶輸入是否正常，如果正常，我們將返回一個 `Ok(Self)`。

不過首先我們要改變`.new()`方法。我們不希望用戶再自由創建任何一種角色。所以我們將把`impl Default`的值移到`.new()`。而現在`.new()`不接受任何輸入。

```rust
    fn new() -> Self {    // 🚧
        Self {
            name: "Billy".to_string(),
            age: 15,
            height: 170,
            weight: 70,
            lifestate: LifeState::Alive,
        }
    }
```

這意味著我們不再需要`impl Default`了，因為`.new()`有所有的默認值。所以我們可以刪除`impl Default`。

現在我們的代碼是這樣的。

```rust
#[derive(Debug)]
struct Character {
    name: String,
    age: u8,
    height: u32,
    weight: u32,
    lifestate: LifeState,
}

#[derive(Debug)]
enum LifeState {
    Alive,
    Dead,
    NeverAlive,
    Uncertain,
}

impl Character {
    fn new() -> Self {
        Self {
            name: "Billy".to_string(),
            age: 15,
            height: 170,
            weight: 70,
            lifestate: LifeState::Alive,
        }
    }

    fn height(mut self, height: u32) -> Self {
        self.height = height;
        self
    }

    fn weight(mut self, weight: u32) -> Self {
        self.weight = weight;
        self
    }

    fn name(mut self, name: &str) -> Self {
        self.name = name.to_string();
        self
    }
}

fn main() {
    let character_1 = Character::new().height(180).weight(60).name("Bobby");

    println!("{:?}", character_1);
}
```

這樣打印出來的結果是一樣的:`Character { name: "Bobby", age: 15, height: 180, weight: 60, lifestate: Alive }`。

我們幾乎已經準備好寫`.build()`方法了，但是有一個問題:如何讓用戶使用它？現在用戶可以寫`let x = Character::new().height(76767);`，然後得到一個`Character`。有很多方法可以做到這一點，也許你能想出自己的方法。但是我們會在`Character`中增加一個`can_use: bool`的值。

```rust
#[derive(Debug)]       // 🚧
struct Character {
    name: String,
    age: u8,
    height: u32,
    weight: u32,
    lifestate: LifeState,
    can_use: bool, // Set whether the user can use the character
}

\\ Cut other code

    fn new() -> Self {
        Self {
            name: "Billy".to_string(),
            age: 15,
            height: 170,
            weight: 70,
            lifestate: LifeState::Alive,
            can_use: true, // .new() always gives a good character, so it's true
        }
    }
```

而對於其他的方法，比如`.height()`，我們會將`can_use`設置為`false`。只有`.build()`會再次設置為`true`，所以現在用戶要用`.build()`做最後的檢查。我們要確保`height`不高於200，`weight`不高於300。另外，在我們的遊戲中，有一個不好的字叫`smurf`，我們不希望任何角色使用它。

我們的`.build()`方法是這樣的:

```rust
fn build(mut self) -> Result<Character, String> {      // 🚧
    if self.height < 200 && self.weight < 300 && !self.name.to_lowercase().contains("smurf") {
        self.can_use = true;
        Ok(self)
    } else {
        Err("Could not create character. Characters must have:
1) Height below 200
2) Weight below 300
3) A name that is not Smurf (that is a bad word)"
            .to_string())
    }
}
```

`!self.name.to_lowercase().contains("smurf")` 確保用戶不會寫出類似 "SMURF"或 "IamSmurf"的字樣。它讓整個 `String` 都變成小寫(小字母)，並檢查 `.contains()` 而不是 `==`。而前面的`!`表示 "不是"。

如果一切正常，我們就把`can_use`設置為`true`，然後把`Ok`裡面的字符給用戶。

現在我們的代碼已經完成了，我們將創建三個不工作的角色，和一個工作的角色。最後的代碼是這樣的。

```rust
#[derive(Debug)]
struct Character {
    name: String,
    age: u8,
    height: u32,
    weight: u32,
    lifestate: LifeState,
    can_use: bool, // Here is the new value
}

#[derive(Debug)]
enum LifeState {
    Alive,
    Dead,
    NeverAlive,
    Uncertain,
}

impl Character {
    fn new() -> Self {
        Self {
            name: "Billy".to_string(),
            age: 15,
            height: 170,
            weight: 70,
            lifestate: LifeState::Alive,
            can_use: true,  // .new() makes a fine character, so it is true
        }
    }

    fn height(mut self, height: u32) -> Self {
        self.height = height;
        self.can_use = false; // Now the user can't use the character
        self
    }

    fn weight(mut self, weight: u32) -> Self {
        self.weight = weight;
        self.can_use = false;
        self
    }

    fn name(mut self, name: &str) -> Self {
        self.name = name.to_string();
        self.can_use = false;
        self
    }

    fn build(mut self) -> Result<Character, String> {
        if self.height < 200 && self.weight < 300 && !self.name.to_lowercase().contains("smurf") {
            self.can_use = true;   // Everything is okay, so set to true
            Ok(self)               // and return the character
        } else {
            Err("Could not create character. Characters must have:
1) Height below 200
2) Weight below 300
3) A name that is not Smurf (that is a bad word)"
                .to_string())
        }
    }
}

fn main() {
    let character_with_smurf = Character::new().name("Lol I am Smurf!!").build(); // This one contains "smurf" - not okay
    let character_too_tall = Character::new().height(400).build(); // Too tall - not okay
    let character_too_heavy = Character::new().weight(500).build(); // Too heavy - not okay
    let okay_character = Character::new()
        .name("Billybrobby")
        .height(180)
        .weight(100)
        .build();   // This character is okay. Name is fine, height and weight are fine

    // Now they are not Character, they are Result<Character, String>. So let's put them in a Vec so we can see them:
    let character_vec = vec![character_with_smurf, character_too_tall, character_too_heavy, okay_character];

    for character in character_vec { // Now we will print the character if it's Ok, and print the error if it's Err
        match character {
            Ok(character_info) => println!("{:?}", character_info),
            Err(err_info) => println!("{}", err_info),
        }
        println!(); // Then add one more line
    }
}
```

這將打印:

```text
Could not create character. Characters must have:
1) Height below 200
2) Weight below 300
3) A name that is not Smurf (that is a bad word)

Could not create character. Characters must have:
1) Height below 200
2) Weight below 300
3) A name that is not Smurf (that is a bad word)

Could not create character. Characters must have:
1) Height below 200
2) Weight below 300
3) A name that is not Smurf (that is a bad word)

Character { name: "Billybrobby", age: 15, height: 180, weight: 100, lifestate: Alive, can_use: true }
```



## Deref和DerefMut

`Deref`是讓你用`*`來解引用某些東西的trait。我們知道，一個引用和一個值是不一樣的。

```rust
// ⚠️
fn main() {
    let value = 7; // This is an i32
    let reference = &7; // This is a &i32
    println!("{}", value == reference);
}
```

而Rust連`false`都不給，因為它甚至不會比較兩者。

```text
error[E0277]: can't compare `{integer}` with `&{integer}`
 --> src\main.rs:4:26
  |
4 |     println!("{}", value == reference);
  |                          ^^ no implementation for `{integer} == &{integer}`
```

當然，這裡的解法是使用`*`。所以這將打印出`true`。

```rust
fn main() {
    let value = 7;
    let reference = &7;
    println!("{}", value == *reference);
}
```


現在讓我們想象一下一個簡單的類型，它只是容納一個數字。它就像一個`Box`，我們有一些想法為它提供一些額外的功能。但如果我們只是給它一個數字，
 它就不能做那麼多了。

我們不能像使用`Box`那樣使用`*`:

```rust
// ⚠️
struct HoldsANumber(u8);

fn main() {
    let my_number = HoldsANumber(20);
    println!("{}", *my_number + 20);
}
```

錯誤信息是:

```text
error[E0614]: type `HoldsANumber` cannot be dereferenced
  --> src\main.rs:24:22
   |
24 |     println!("{:?}", *my_number + 20);
```

我們當然可以做到這一點。`println!("{:?}", my_number.0 + 20);`. 但是這樣的話，我們就是在20的基礎上再單獨加一個`u8`。如果我們能把它們加在一起就更好了。`cannot be dereferenced`這個消息給了我們一個線索:我們需要實現`Deref`。實現`Deref`的簡單東西有時被稱為 "智能指針"。一個智能指針可以指向它的元素，有它的信息，並且可以使用它的方法。因為現在我們可以添加`my_number.0`，這是一個`u8`，但我們不能用`HoldsANumber`做其他的事情:到目前為止，它只有`Debug`。

有趣的是:`String`其實是`&str`的智能指針，`Vec`是數組(或其他類型)的智能指針。所以我們其實從一開始就在使用智能指針。

實現`Deref`並不難，標準庫中的例子也很簡單。[下面是標準庫中的示例代碼](https://doc.rust-lang.org/std/ops/trait.Deref.html)。

```rust
use std::ops::Deref;

struct DerefExample<T> {
    value: T
}

impl<T> Deref for DerefExample<T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &self.value
    }
}

fn main() {
    let x = DerefExample { value: 'a' };
    assert_eq!('a', *x);
}
```


所以我們按照這個來，現在我們的`Deref`是這樣的。

```rust
// 🚧
impl Deref for HoldsANumber {
    type Target = u8; // Remember, this is the "associated type": the type that goes together.
                      // You have to use the right type Target = (the type you want to return)

    fn deref(&self) -> &Self::Target { // Rust calls .deref() when you use *. We just defined Target as a u8 so this is easy to understand
        &self.0   // We chose &self.0 because it's a tuple struct. In a named struct it would be something like "&self.number"
    }
}
```

所以現在我們可以用`*`來做:

```rust
use std::ops::Deref;
#[derive(Debug)]
struct HoldsANumber(u8);

impl Deref for HoldsANumber {
    type Target = u8;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

fn main() {
    let my_number = HoldsANumber(20);
    println!("{:?}", *my_number + 20);
}
```

所以，這樣就可以打印出`40`，我們不需要寫`my_number.0`。這意味著我們得到了 `u8` 的方法，我們可以為 `HoldsANumber` 寫出我們自己的方法。我們將添加自己的簡單方法，並使用我們從`u8`中得到的另一個方法，稱為`.checked_sub()`。`.checked_sub()`方法是一個安全的減法，它能返回一個`Option`。如果它能做減法，那麼它就會在`Some`裡面給你，如果它不能做減法，那麼它就會給出一個`None`。記住，`u8`不能是負數，所以還是`.checked_sub()`比較安全，這樣就不會崩潰了。

```rust
use std::ops::Deref;

struct HoldsANumber(u8);

impl HoldsANumber {
    fn prints_the_number_times_two(&self) {
        println!("{}", self.0 * 2);
    }
}

impl Deref for HoldsANumber {
    type Target = u8;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

fn main() {
    let my_number = HoldsANumber(20);
    println!("{:?}", my_number.checked_sub(100)); // This method comes from u8
    my_number.prints_the_number_times_two(); // This is our own method
}
```

這個打印:

```text
None
40
```

我們也可以實現`DerefMut`，這樣我們就可以通過`*`來改變數值。它看起來幾乎是一樣的。在實現`DerefMut`之前，你需要先實現`Deref`。

```rust
use std::ops::{Deref, DerefMut};

struct HoldsANumber(u8);

impl HoldsANumber {
    fn prints_the_number_times_two(&self) {
        println!("{}", self.0 * 2);
    }
}

impl Deref for HoldsANumber {
    type Target = u8;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl DerefMut for HoldsANumber { // You don't need type Target = u8; here because it already knows thanks to Deref
    fn deref_mut(&mut self) -> &mut Self::Target { // Everything else is the same except it says mut everywhere
        &mut self.0
    }
}

fn main() {
    let mut my_number = HoldsANumber(20);
    *my_number = 30; // DerefMut lets us do this
    println!("{:?}", my_number.checked_sub(100));
    my_number.prints_the_number_times_two();
}
```

所以你可以看到，`Deref`給你的類型提供了強大的力量。

這也是為什麼標準庫說:`Deref should only be implemented for smart pointers to avoid confusion`。這是因為對於一個複雜的類型，你可以用 `Deref` 做一些奇怪的事情。讓我們想象一個非常混亂的例子來理解它們的含義。我們將從一個遊戲的 `Character` 結構開始。一個新的`Character`需要一些數據，比如智力和力量。所以這裡是我們的第一個角色。

```rust
struct Character {
    name: String,
    strength: u8,
    dexterity: u8,
    health: u8,
    intelligence: u8,
    wisdom: u8,
    charm: u8,
    hit_points: i8,
    alignment: Alignment,
}

impl Character {
    fn new(
        name: String,
        strength: u8,
        dexterity: u8,
        health: u8,
        intelligence: u8,
        wisdom: u8,
        charm: u8,
        hit_points: i8,
        alignment: Alignment,
    ) -> Self {
        Self {
            name,
            strength,
            dexterity,
            health,
            intelligence,
            wisdom,
            charm,
            hit_points,
            alignment,
        }
    }
}

enum Alignment {
    Good,
    Neutral,
    Evil,
}

fn main() {
    let billy = Character::new("Billy".to_string(), 9, 8, 7, 10, 19, 19, 5, Alignment::Good);
}
```

現在讓我們想象一下，我們要把人物的hit points放在一個大的vec裡。也許我們會把怪物數據也放進去，把它放在一起。由於 `hit_points` 是一個 `i8`，我們實現了 `Deref`，所以我們可以對它進行各種計算。但是看看現在我們的`main()`函數中，它看起來多麼奇怪。


```rust
use std::ops::Deref;

// All the other code is the same until after the enum Alignment
struct Character {
    name: String,
    strength: u8,
    dexterity: u8,
    health: u8,
    intelligence: u8,
    wisdom: u8,
    charm: u8,
    hit_points: i8,
    alignment: Alignment,
}

impl Character {
    fn new(
        name: String,
        strength: u8,
        dexterity: u8,
        health: u8,
        intelligence: u8,
        wisdom: u8,
        charm: u8,
        hit_points: i8,
        alignment: Alignment,
    ) -> Self {
        Self {
            name,
            strength,
            dexterity,
            health,
            intelligence,
            wisdom,
            charm,
            hit_points,
            alignment,
        }
    }
}

enum Alignment {
    Good,
    Neutral,
    Evil,
}

impl Deref for Character { // impl Deref for Character. Now we can do any integer math we want!
    type Target = i8;

    fn deref(&self) -> &Self::Target {
        &self.hit_points
    }
}



fn main() {
    let billy = Character::new("Billy".to_string(), 9, 8, 7, 10, 19, 19, 5, Alignment::Good); // Create two characters, billy and brandy
    let brandy = Character::new("Brandy".to_string(), 9, 8, 7, 10, 19, 19, 5, Alignment::Good);

    let mut hit_points_vec = vec![]; // Put our hit points data in here
    hit_points_vec.push(*billy);     // Push *billy?
    hit_points_vec.push(*brandy);    // Push *brandy?

    println!("{:?}", hit_points_vec);
}
```

這隻打印了`[5, 5]`。我們的代碼現在讓人讀起來感覺非常奇怪。我們可以在`main()`上面看到`Deref`，然後弄清楚`*billy`的意思是`i8`，但是如果有很多代碼呢？可能我們的代碼有2000行，突然要弄清楚為什麼要`.push()` `*billy`。`Character`當然不僅僅是`i8`的智能指針。

當然，寫`hit_points_vec.push(*billy)`並不違法，但這讓代碼看起來非常奇怪。也許一個簡單的`.get_hp()`方法會好得多，或者另一個存放角色的結構體。然後你可以迭代並推送每個角色的 `hit_points`。`Deref`提供了很多功能，但最好確保代碼的邏輯性。



## Crate和模塊

每次你在 Rust 中寫代碼時，你都是在 `crate` 中寫的。`crate`是一個或多個文件，一起為你的代碼服務。在你寫的文件裡面，你也可以創建一個`mod`。`mod`是存放函數、結構體等的空間，因為這些原因被使用:

- 構建你的代碼:它可以幫助你思考代碼的總體結構。當你的代碼越來越大時，這一點可能很重要。
- 閱讀你的代碼:人們可以更容易理解你的代碼。例如，`std::collections::HashMap`這個名字告訴你，它在`std`的模塊`collections`裡面。這給了你一個提示，也許`collections`裡面還有更多的集合類型，你可以嘗試一下。
- 私密性:所有的東西一開始都是私有的。這樣可以讓你不讓用戶直接使用函數。

要創建一個`mod`，只需要寫`mod`，然後用`{}`開始一個代碼塊。我們將創建一個名為`print_things`的mod，它有一些打印相關的功能。

```rust
mod print_things {
    use std::fmt::Display;

    fn prints_one_thing<T: Display>(input: T) { // Print anything that implements Display
        println!("{}", input)
    }
}

fn main() {}
```

你可以看到，我們把`use std::fmt::Display;`寫在`print_things`裡面，因為它是一個獨立的空間。如果你把`use std::fmt::Display;`寫在`main()`裡面，那沒用。而且，我們現在也不能從`main()`裡面調用。如果在`fn`前面沒有`pub`這個關鍵字，它就會保持私密性。讓我們試著在沒有`pub`的情況下調用它。這裡有一種寫法。

```rust
// 🚧
fn main() {
    crate::print_things::prints_one_thing(6);
}
```


`crate`的意思是 "在這個項目裡"，但對於我們簡單的例子來說，它和 "在這個文件裡面"是一樣的。接著是`print_things`這個mod，最後是`prints_one_thing()`函數。你可以每次都寫這個，也可以寫`use`來導入。現在我們可以看到說它是私有的錯誤:

```rust
// ⚠️
mod print_things {
    use std::fmt::Display;

    fn prints_one_thing<T: Display>(input: T) {
        println!("{}", input)
    }
}

fn main() {
    use crate::print_things::prints_one_thing;

    prints_one_thing(6);
    prints_one_thing("Trying to print a string...".to_string());
}
```

這是錯誤的。

```text
error[E0603]: function `prints_one_thing` is private
  --> src\main.rs:10:30
   |
10 |     use crate::print_things::prints_one_thing;
   |                              ^^^^^^^^^^^^^^^^ private function
   |
note: the function `prints_one_thing` is defined here
  --> src\main.rs:4:5
   |
4  |     fn prints_one_thing<T: Display>(input: T) {
   |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```
很容易理解，函數`print_one_thing`是私有的。它還用`src\main.rs:4:5`告訴我們在哪裡可以找到這個函數。這很有幫助，因為你不僅可以在一個文件中寫`mod`，還可以在很多文件中寫`mod`。

現在我們只需要寫`pub fn`而不是`fn`，一切就都可以了。

```rust
mod print_things {
    use std::fmt::Display;

    pub fn prints_one_thing<T: Display>(input: T) {
        println!("{}", input)
    }
}

fn main() {
    use crate::print_things::prints_one_thing;

    prints_one_thing(6);
    prints_one_thing("Trying to print a string...".to_string());
}
```

這個打印:

```text
6
Trying to print a string...
```

`pub`對結構體、枚舉、trait或模塊有什麼作用？`pub`對它們來說是這樣的:

- `pub`對於一個結構：它使結構公開，但成員不是公開的。要想讓一個成員公開，你也要為每個成員寫`pub`。
- `pub` 對於一個枚舉或trait：所有的東西都變成了公共的。這是有意義的，因為traits是給事物賦予相同的行為。而枚舉是值之間的選擇，你需要看到所有的枚舉值才能做選擇。
- `pub`對於一個模塊來說：一個頂層的模塊會是`pub`，因為如果它不是pub，那麼根本沒有人可以使用裡面的任何東西。但是模塊裡面的模塊需要使用`pub`才能成為公共的。

我們在`print_things`裡面放一個名為`Billy`的結構體。這個結構體幾乎都會是public的，但也不盡然。這個結構是公共的，所以它這樣寫：`pub struct Billy`。裡面會有一個 `name` 和 `times_to_print`。`name`不會是公共的，因為我們只想讓用戶創建名為`"Billy".to_string()`的結構。但是用戶可以選擇打印的次數，所以這將是公開的。它的是這樣的:

```rust
mod print_things {
    use std::fmt::{Display, Debug};

    #[derive(Debug)]
    pub struct Billy { // Billy is public
        name: String, // but name is private.
        pub times_to_print: u32,
    }

    impl Billy {
        pub fn new(times_to_print: u32) -> Self { // That means the user needs to use new to create a Billy. The user can only change the number of times_to_print
            Self {
                name: "Billy".to_string(), // We choose the name - the user can't
                times_to_print,
            }
        }

        pub fn print_billy(&self) { // This function prints a Billy
            for _ in 0..self.times_to_print {
                println!("{:?}", self.name);
            }
        }
    }

    pub fn prints_one_thing<T: Display>(input: T) {
        println!("{}", input)
    }
}

fn main() {
    use crate::print_things::*; // Now we use *. This imports everything from print_things

    let my_billy = Billy::new(3);
    my_billy.print_billy();
}
```

這將打印:

```text
"Billy"
"Billy"
"Billy"
```

對了，導入一切的`*`叫做 "glob運算符"。Glob的意思是 "全局"，所以它意味著一切。

在`mod`裡面你可以創建其他mod。一個子 mod(mod裡的mod)總是可以使用父 mod 內部的任何東西。你可以在下一個例子中看到這一點，我們在 `mod province` 裡面有一個 `mod city`，而`mod province`在 `mod country` 裡面。

你可以這樣想:即使你在一個國家，你可能不在一個省。而即使你在一個省，你也可能不在一個市。但如果你在一個城市，你就在這個城市的省份和它的國家。


```rust
mod country { // The main mod doesn't need pub
    fn print_country(country: &str) { // Note: this function isn't public
        println!("We are in the country of {}", country);
    }
    pub mod province { // Make this mod public

        fn print_province(province: &str) { // Note: this function isn't public
            println!("in the province of {}", province);
        }

        pub mod city { // Make this mod public
            pub fn print_city(country: &str, province: &str, city: &str) {  // This function is public though
                crate::country::print_country(country);
                crate::country::province::print_province(province);
                println!("in the city of {}", city);
            }
        }
    }
}

fn main() {
    crate::country::province::city::print_city("Canada", "New Brunswick", "Moncton");
}
```

有趣的是，`print_city`可以訪問`print_province`和`print_country`。這是因為`mod city`在其他mod裡面。它不需要在`print_province`前面添加`pub`之後才能使用。這也是有道理的:一個城市不需要做什麼，它本來就在一個省裡，在一個國家裡。

你可能注意到，`crate::country::province::print_province(province);`非常長。當我們在一個模塊裡面的時候，我們可以用`super`從上面引入元素。其實super這個詞本身就是"上面"的意思，比如 "上級"。在我們的例子中，我們只用了一次函數，但是如果你用的比較多的話，那麼最好是導入。如果它能讓你的代碼更容易閱讀，那也是個好主意，即使你只用了一次函數。現在的代碼幾乎是一樣的，但更容易閱讀一些。

```rust
mod country {
    fn print_country(country: &str) {
        println!("We are in the country of {}", country);
    }
    pub mod province {
        fn print_province(province: &str) {
            println!("in the province of {}", province);
        }

        pub mod city {
            use super::super::*; // use everything in "above above": that means mod country
            use super::*;        // use everything in "above": that means mod province

            pub fn print_city(country: &str, province: &str, city: &str) {
                print_country(country);
                print_province(province);
                println!("in the city of {}", city);
            }
        }
    }
}

fn main() {
    use crate::country::province::city::print_city; // bring in the function

    print_city("Canada", "New Brunswick", "Moncton");
    print_city("Korea", "Gyeonggi-do", "Gwangju"); // Now it's less work to use it again
}
```



## 測試

現在我們已經瞭解了模塊,就可以談談測試了。在Rust中測試你的代碼是非常容易的，因為你可以在你的代碼旁邊寫測試。

開始測試的最簡單的方法是在一個函數上面添加`#[test]`。下面是一個簡單的例子。

```rust
#[test]
fn two_is_two() {
    assert_eq!(2, 2);
}
```

但如果你試圖在playground中運行它，它給出了一個錯誤。``error[E0601]: `main` function not found in crate `playground``. 這是因為你不使用 _Run_ 來進行測試，你使用 _Test_ 。另外，你不使用 `main()` 函數進行測試 - 它們在外面運行。要在Playground中運行這個，點擊 _RUN_ 旁邊的`···`，然後把它改為 _Test_ 。現在如果你點擊它，它將運行測試。(如果你已經安裝了 Rust，你將輸入 `cargo test` 來做這個測試)

這裡是輸出:

```text
running 1 test
test two_is_two ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

讓我們把`assert_eq!(2, 2)`改成`assert_eq!(2, 3)`，看看會有什麼結果。當測試失敗時，你會得到更多的信息。

```text
running 1 test
test two_is_two ... FAILED

failures:

---- two_is_two stdout ----
thread 'two_is_two' panicked at 'assertion failed: `(left == right)`
  left: `2`,
 right: `3`', src/lib.rs:3:5
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    two_is_two

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out
```

`assert_eq!(left, right)`是Rust中測試一個函數的主要方法。如果它不工作，它將顯示不同的值:左邊有2，但右邊有3。

`RUST_BACKTRACE=1`是什麼意思？這是計算機上的一個設置，可以提供更多關於錯誤的信息。幸好playground也有:點擊`STABLE`旁邊的`···`，然後設置回溯為`ENABLED`。如果你這樣做，它會給你*很多*的信息。

```text
running 1 test
test two_is_two ... FAILED

failures:

---- two_is_two stdout ----
thread 'two_is_two' panicked at 'assertion failed: 2 == 3', src/lib.rs:3:5
stack backtrace:
   0: backtrace::backtrace::libunwind::trace
             at /cargo/registry/src/github.com-1ecc6299db9ec823/backtrace-0.3.46/src/backtrace/libunwind.rs:86
   1: backtrace::backtrace::trace_unsynchronized
             at /cargo/registry/src/github.com-1ecc6299db9ec823/backtrace-0.3.46/src/backtrace/mod.rs:66
   2: std::sys_common::backtrace::_print_fmt
             at src/libstd/sys_common/backtrace.rs:78
   3: <std::sys_common::backtrace::_print::DisplayBacktrace as core::fmt::Display>::fmt
             at src/libstd/sys_common/backtrace.rs:59
   4: core::fmt::write
             at src/libcore/fmt/mod.rs:1076
   5: std::io::Write::write_fmt
             at /rustc/c367798cfd3817ca6ae908ce675d1d99242af148/src/libstd/io/mod.rs:1537
   6: std::io::impls::<impl std::io::Write for alloc::boxed::Box<W>>::write_fmt
             at src/libstd/io/impls.rs:176
   7: std::sys_common::backtrace::_print
             at src/libstd/sys_common/backtrace.rs:62
   8: std::sys_common::backtrace::print
             at src/libstd/sys_common/backtrace.rs:49
   9: std::panicking::default_hook::{{closure}}
             at src/libstd/panicking.rs:198
  10: std::panicking::default_hook
             at src/libstd/panicking.rs:215
  11: std::panicking::rust_panic_with_hook
             at src/libstd/panicking.rs:486
  12: std::panicking::begin_panic
             at /rustc/c367798cfd3817ca6ae908ce675d1d99242af148/src/libstd/panicking.rs:410
  13: playground::two_is_two
             at src/lib.rs:3
  14: playground::two_is_two::{{closure}}
             at src/lib.rs:2
  15: core::ops::function::FnOnce::call_once
             at /rustc/c367798cfd3817ca6ae908ce675d1d99242af148/src/libcore/ops/function.rs:232
  16: <alloc::boxed::Box<F> as core::ops::function::FnOnce<A>>::call_once
             at /rustc/c367798cfd3817ca6ae908ce675d1d99242af148/src/liballoc/boxed.rs:1076
  17: <std::panic::AssertUnwindSafe<F> as core::ops::function::FnOnce<()>>::call_once
             at /rustc/c367798cfd3817ca6ae908ce675d1d99242af148/src/libstd/panic.rs:318
  18: std::panicking::try::do_call
             at /rustc/c367798cfd3817ca6ae908ce675d1d99242af148/src/libstd/panicking.rs:297
  19: std::panicking::try
             at /rustc/c367798cfd3817ca6ae908ce675d1d99242af148/src/libstd/panicking.rs:274
  20: std::panic::catch_unwind
             at /rustc/c367798cfd3817ca6ae908ce675d1d99242af148/src/libstd/panic.rs:394
  21: test::run_test_in_process
             at src/libtest/lib.rs:541
  22: test::run_test::run_test_inner::{{closure}}
             at src/libtest/lib.rs:450
note: Some details are omitted, run with `RUST_BACKTRACE=full` for a verbose backtrace.


failures:
    two_is_two

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out
```

除非你真的找不到問題所在，否則你不需要使用回溯。但幸運的是你也不需要全部理解。 如果你繼續閱讀，你最終會看到第13行，那裡寫著`playground`--那是它提到的你的代碼的位置。其他的都是關於Rust為了運行你的程序,在其他庫中所做的事情。但是這兩行告訴你，它看的是playground的第2行和第3行，這是一個提示，要檢查那裡。這裡是那個部分:

```text
  13: playground::two_is_two
             at src/lib.rs:3
  14: playground::two_is_two::{{closure}}
             at src/lib.rs:2
```

編輯：Rust在2021年初改進了其回溯信息，只顯示最有意義的信息。現在它更容易閱讀。

```text
failures:

---- two_is_two stdout ----
thread 'two_is_two' panicked at 'assertion failed: `(left == right)`
  left: `2`,
 right: `3`', src/lib.rs:3:5
stack backtrace:
   0: rust_begin_unwind
             at /rustc/cb75ad5db02783e8b0222fee363c5f63f7e2cf5b/library/std/src/panicking.rs:493:5
   1: core::panicking::panic_fmt
             at /rustc/cb75ad5db02783e8b0222fee363c5f63f7e2cf5b/library/core/src/panicking.rs:92:14
   2: playground::two_is_two
             at ./src/lib.rs:3:5
   3: playground::two_is_two::{{closure}}
             at ./src/lib.rs:2:1
   4: core::ops::function::FnOnce::call_once
             at /rustc/cb75ad5db02783e8b0222fee363c5f63f7e2cf5b/library/core/src/ops/function.rs:227:5
   5: core::ops::function::FnOnce::call_once
             at /rustc/cb75ad5db02783e8b0222fee363c5f63f7e2cf5b/library/core/src/ops/function.rs:227:5
note: Some details are omitted, run with `RUST_BACKTRACE=full` for a verbose backtrace.


failures:
    two_is_two

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.02s
```

現在我們再把回溯關閉，回到常規測試。現在我們要寫一些其他函數，並使用測試函數來測試它們。這裡有幾個:

```rust
fn return_two() -> i8 {
    2
}
# [test]
fn it_returns_two() {
    assert_eq!(return_two(), 2);
}

fn return_six() -> i8 {
    4 + return_two()
}
# [test]
fn it_returns_six() {
    assert_eq!(return_six(), 6)
}
```

現在，都能運行:

```text
running 2 tests
test it_returns_two ... ok
test it_returns_six ... ok

test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

這不是太難。

通常你會想把你的測試放在自己的模塊中。要做到這一點，請使用相同的 `mod` 關鍵字，並在其上方添加 `#[cfg(test)]`(記住:`cfg` 的意思是 "配置")。你還要在每個測試上面繼續寫`#[test]`。這是因為以後當你安裝Rust時，你可以做更復雜的測試。你將可以運行一個測試，或者所有的測試，或者運行幾個測試。另外別忘了寫`use super::*;`，因為測試模塊需要使用上面的函數。現在它看起來會是這樣的。

```rust
fn return_two() -> i8 {
    2
}
fn return_six() -> i8 {
    4 + return_two()
}

# [cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_returns_six() {
        assert_eq!(return_six(), 6)
    }
    #[test]
    fn it_returns_two() {
        assert_eq!(return_two(), 2);
    }
}
```

### 測試驅動的開發

在閱讀Rust或其他語言時，你可能會看到 "測試驅動開發"這個詞。這是編寫程序的一種方式，有些人喜歡它，而有些人則喜歡其他的方式。"測試驅動開發"的意思是 "先寫測試，再寫代碼"。當你這樣做的時候，你會有很多關於你想要你的代碼做的所有事情的測試代碼。然後你開始寫代碼，並運行測試，看看你是否做對了。然後，當你添加和重寫代碼時，如果有什麼地方出了問題，測試代碼會一直在那裡向你展示。這在Rust中是非常容易的，因為編譯器給出了很多待修復內容的信息。讓我們寫一個測試驅動開發的小例子，看看它是什麼樣子的。

讓我們想象一個接受用戶輸入的計算器。它可以加(+)，也可以減(-)。如果用戶寫 "5+6"，它應該返回11，如果用戶寫 "5+6-7"，它應該返回4，以此類推。所以我們先從測試函數開始。你也可以看到，測試中的函數名通常都相當長。這是因為你可能會運行很多測試，你想了解哪些測試失敗了。

我們想象一下，一個名為`math()`的函數就可以完成所有的工作。它將返回一個 `i32`(我們不會使用浮點數)。因為它需要返回一些東西，所以我們每次都只返回 `6`。然後我們將寫三個測試函數。當然，它們都會失敗。現在的代碼是這樣的。

```rust
fn math(input: &str) -> i32 {
    6
}

# [cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn one_plus_one_is_two() {
        assert_eq!(math("1 + 1"), 2);
    }
    #[test]
    fn one_minus_two_is_minus_one() {
        assert_eq!(math("1 - 2"), -1);
    }
    #[test]
    fn one_minus_minus_one_is_two() {
        assert_eq!(math("1 - -1"), 2);
    }
}
```

它給了我們這個信息。

```text
running 3 tests
test tests::one_minus_minus_one_is_two ... FAILED
test tests::one_minus_two_is_minus_one ... FAILED
test tests::one_plus_one_is_two ... FAILED
```

以及``thread 'tests::one_plus_one_is_two' panicked at 'assertion failed: `(left == right)` ``的所有信息。我們不需要在這裡全部打印出來。

現在要考慮如何創建計算器。我們將接受任何數字，以及符號`+-`。我們將允許空格，但不允許其他任何東西。所以，讓我們從包含所有數值的`const`開始。然後我們將使用 `.chars()` 按字符進行迭代，並使用 `.all()` 確保它們都在裡面。

然後，我們將添加一個會崩潰的測試。要做到這一點，添加 `#[should_panic]` 屬性:現在如果它崩潰，測試將成功。

現在代碼看起來像這樣:

```rust
const OKAY_CHARACTERS: &str = "1234567890+- "; // Don't forget the space at the end

fn math(input: &str) -> i32 {
    if !input.chars().all(|character| OKAY_CHARACTERS.contains(character)) {
        panic!("Please only input numbers, +-, or spaces");
    }
    6 // we still return a 6 for now
}

# [cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn one_plus_one_is_two() {
        assert_eq!(math("1 + 1"), 2);
    }
    #[test]
    fn one_minus_two_is_minus_one() {
        assert_eq!(math("1 - 2"), -1);
    }
    #[test]
    fn one_minus_minus_one_is_two() {
        assert_eq!(math("1 - -1"), 2);
    }

    #[test]
    #[should_panic]  // Here is our new test - it should panic
    fn panics_when_characters_not_right() {
        math("7 + seven");
    }
}
```

現在，當我們運行測試時，我們得到這樣的結果。

```text
running 4 tests
test tests::one_minus_two_is_minus_one ... FAILED
test tests::one_minus_minus_one_is_two ... FAILED
test tests::panics_when_characters_not_right ... ok
test tests::one_plus_one_is_two ... FAILED
```

一個成功了! 我們的`math()`函數現在只能接受好的輸入了。


下一步是編寫實際的計算器。這就是先有測試的有趣之處:實際的代碼要晚很多。首先，我們將把計算器的邏輯放在一起。我們要做到以下幾點。

- 所有的空位都應該被刪除。這在`.filter()`中很容易實現。
- 所有輸入應該變成一個`Vec`。`+`不需要成為輸入，但是當程序看到`+`時，應該知道這個數字已經完成了。例如，輸入`+`應該這樣做:
    1) 看到`1`，把它推到一個空字符串中。
    2) 看到另一個1，把它推入字符串中(現在是 "11")。
    3) 看到一個`+`，知道這個數字已經結束。它會把字符串推入vec中，然後清空字符串。
- 程序必須計算出`-`的數量。奇數(1，3，5...)表示減法，偶數(2，4，6...)表示加法。所以 "1--9"應該是10，而不是-8。
- 程序應該刪除最後一個數字後面的任何東西。`5+5+++++----`是由`OKAY_CHARACTERS`中的所有字符組成的，但它應該變成`5+5`。`.trim_end_matches()`就很簡單了，你把`&str`末尾符合的東西都去掉。

順便說一下，`.trim_end_matches()`和`.trim_start_matches()`曾經是`trim_right_matches()`和`trim_left_matches()`。但後來人們注意到有些語言是從右到左(波斯語、希伯來語等)，所以左右都是錯的。你可能還能在一些代碼中看到舊的名字，但它們是一樣的)。)

首先我們只想通過所有的測試。通過測試後，我們就可以 "重構"了。重構的意思是讓代碼變得更好，通常是通過結構、枚舉和方法等方式。下面是我們使測試通過的代碼。

```rust
const OKAY_CHARACTERS: &str = "1234567890+- ";

fn math(input: &str) -> i32 {
    if !input.chars().all(|character| OKAY_CHARACTERS.contains(character)) ||
       !input.chars().take(2).any(|character| character.is_numeric())
    {
        panic!("Please only input numbers, +-, or spaces.");
    }

    let input = input.trim_end_matches(|x| "+- ".contains(x)).chars().filter(|x| *x != ' ').collect::<String>(); // Remove + and - at the end, and all spaces
    let mut result_vec = vec![]; // Results go in here
    let mut push_string = String::new(); // This is the string we push in every time. We will keep reusing it in the loop.
    for character in input.chars() {
        match character {
            '+' => {
                if !push_string.is_empty() { // If the string is empty, we don't want to push "" into result_vec
                    result_vec.push(push_string.clone()); // But if it's not empty, it will be a number. Push it into the vec
                    push_string.clear(); // Then clear the string
                }
            },
            '-' => { // If we get a -,
                if push_string.contains('-') || push_string.is_empty() { // check to see if it's empty or has a -
                    push_string.push(character) // if so, then push it in
                } else { // otherwise, it will contain a number
                result_vec.push(push_string.clone()); // so push the number into result_vec, clear it and then push -
                push_string.clear();
                push_string.push(character);
                }
            },
            number => { // number here means "anything else that matches". We selected the name here
                if push_string.contains('-') { // We might have some - characters to push in first
                    result_vec.push(push_string.clone());
                    push_string.clear();
                    push_string.push(number);
                } else { // But if we don't, that means we can push the number in
                    push_string.push(number);
                }
            },
        }
    }
    result_vec.push(push_string); // Push one last time after the loop is over. Don't need to .clone() because we don't use it anymore

    let mut total = 0; // Now it's time to do math. Start with a total
    let mut adds = true; // true = add, false = subtract
    let mut math_iter = result_vec.into_iter();
    while let Some(entry) = math_iter.next() { // Iter through the items
        if entry.contains('-') { // If it has a - character, check if it's even or odd
            if entry.chars().count() % 2 == 1 {
                adds = match adds {
                    true => false,
                    false => true
                };
                continue; // Go to the next item
            } else {
                continue;
            }
        }
        if adds == true {
            total += entry.parse::<i32>().unwrap(); // If there is no '-', it must be a number. So we are safe to unwrap
        } else {
            total -= entry.parse::<i32>().unwrap();
            adds = true;  // After subtracting, reset adds to true.
        }
    }
    total // Finally, return the total
}
   /// We'll add a few more tests just to make sure

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn one_plus_one_is_two() {
        assert_eq!(math("1 + 1"), 2);
    }
    #[test]
    fn one_minus_two_is_minus_one() {
        assert_eq!(math("1 - 2"), -1);
    }
    #[test]
    fn one_minus_minus_one_is_two() {
        assert_eq!(math("1 - -1"), 2);
    }
    #[test]
    fn nine_plus_nine_minus_nine_minus_nine_is_zero() {
        assert_eq!(math("9+9-9-9"), 0); // This is a new test
    }
    #[test]
    fn eight_minus_nine_plus_nine_is_eight_even_with_characters_on_the_end() {
        assert_eq!(math("8  - 9     +9-----+++++"), 8); // This is a new test
    }
    #[test]
    #[should_panic]
    fn panics_when_characters_not_right() {
        math("7 + seven");
    }
}
```

現在測試通過了!

```text
running 6 tests
test tests::one_minus_minus_one_is_two ... ok
test tests::nine_plus_nine_minus_nine_minus_nine_is_zero ... ok
test tests::one_minus_two_is_minus_one ... ok
test tests::eight_minus_nine_plus_nine_is_eight_even_with_characters_on_the_end ... ok
test tests::one_plus_one_is_two ... ok
test tests::panics_when_characters_not_right ... ok

test result: ok. 6 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

你可以看到，在測試驅動的開發中，有一個來回的過程。它是這樣的。

- 首先你要寫出所有你能想到的測試
- 然後你開始寫代碼。
- 當你寫代碼的時候，你會有其他測試的想法。
- 你添加測試，你的測試隨著你的發展而增長。你的測試越多，你的代碼被檢查的次數就越多。

當然，測試並不能檢查所有的東西，認為 "通過所有測試=代碼是完美的"是錯誤的。但是，測試對於你修改代碼的時候是非常好的。如果你以後修改了代碼，然後運行測試，如果其中一個測試不成功，你就會知道該怎麼修復。

現在我們可以重寫(重構)一下代碼。一個好的方法是用clippy開始。如果你安裝了Rust，那麼你可以輸入`cargo clippy`，如果你使用的是Playground，那麼點擊`TOOLS`，選擇Clippy。Clippy會查看你的代碼，並給你提示，讓你的代碼更簡單。我們的代碼沒有任何錯誤，但它可以更好。

Clippy會告訴我們兩件事。

```text
warning: this loop could be written as a `for` loop
  --> src/lib.rs:44:5
   |
44 |     while let Some(entry) = math_iter.next() { // Iter through the items
   |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ help: try: `for entry in math_iter`
   |
   = note: `#[warn(clippy::while_let_on_iterator)]` on by default
   = help: for further information visit https://rust-lang.github.io/rust-clippy/master/index.html#while_let_on_iterator

warning: equality checks against true are unnecessary
  --> src/lib.rs:53:12
   |
53 |         if adds == true {
   |            ^^^^^^^^^^^^ help: try simplifying it as shown: `adds`
   |
   = note: `#[warn(clippy::bool_comparison)]` on by default
   = help: for further information visit https://rust-lang.github.io/rust-clippy/master/index.html#bool_comparison
```

這是真的:`for entry in math_iter`比`while let Some(entry) = math_iter.next()`簡單得多。而`for`循環實際上是一個迭代器，所以我們沒有任何理由寫`.iter()`。謝謝你，clippy! 而且我們也不需要做`math_iter`:我們可以直接寫`for entry in result_vec`。

現在我們將開始一些真正的重構。我們將創建一個 `Calculator` 結構體，而不是單獨的變量。這將擁有我們使用的所有變量。我們將改變兩個名字以使其更加清晰。`result_vec`將變成`results`，`push_string`將變成`current_input`(current的意思是 "現在")。而到目前為止，它只有一種方法:new。

```rust
// 🚧
#[derive(Clone)]
struct Calculator {
    results: Vec<String>,
    current_input: String,
    total: i32,
    adds: bool,
}

impl Calculator {
    fn new() -> Self {
        Self {
            results: vec![],
            current_input: String::new(),
            total: 0,
            adds: true,
        }
    }
}
```

現在我們的代碼其實比較長，但更容易讀懂。比如，`if adds`現在是`if calculator.adds`，這就跟讀英文完全一樣。它的樣子是這樣的:

```rust
#[derive(Clone)]
struct Calculator {
    results: Vec<String>,
    current_input: String,
    total: i32,
    adds: bool,
}

impl Calculator {
    fn new() -> Self {
        Self {
            results: vec![],
            current_input: String::new(),
            total: 0,
            adds: true,
        }
    }
}

const OKAY_CHARACTERS: &str = "1234567890+- ";

fn math(input: &str) -> i32 {
    if !input.chars().all(|character| OKAY_CHARACTERS.contains(character)) ||
       !input.chars().take(2).any(|character| character.is_numeric()) {
        panic!("Please only input numbers, +-, or spaces");
    }

    let input = input.trim_end_matches(|x| "+- ".contains(x)).chars().filter(|x| *x != ' ').collect::<String>();
    let mut calculator = Calculator::new();

    for character in input.chars() {
        match character {
            '+' => {
                if !calculator.current_input.is_empty() {
                    calculator.results.push(calculator.current_input.clone());
                    calculator.current_input.clear();
                }
            },
            '-' => {
                if calculator.current_input.contains('-') || calculator.current_input.is_empty() {
                    calculator.current_input.push(character)
                } else {
                calculator.results.push(calculator.current_input.clone());
                calculator.current_input.clear();
                calculator.current_input.push(character);
                }
            },
            number => {
                if calculator.current_input.contains('-') {
                    calculator.results.push(calculator.current_input.clone());
                    calculator.current_input.clear();
                    calculator.current_input.push(number);
                } else {
                    calculator.current_input.push(number);
                }
            },
        }
    }
    calculator.results.push(calculator.current_input);

    for entry in calculator.results {
        if entry.contains('-') {
            if entry.chars().count() % 2 == 1 {
                calculator.adds = match calculator.adds {
                    true => false,
                    false => true
                };
                continue;
            } else {
                continue;
            }
        }
        if calculator.adds {
            calculator.total += entry.parse::<i32>().unwrap();
        } else {
            calculator.total -= entry.parse::<i32>().unwrap();
            calculator.adds = true;
        }
    }
    calculator.total
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn one_plus_one_is_two() {
        assert_eq!(math("1 + 1"), 2);
    }
    #[test]
    fn one_minus_two_is_minus_one() {
        assert_eq!(math("1 - 2"), -1);
    }
    #[test]
    fn one_minus_minus_one_is_two() {
        assert_eq!(math("1 - -1"), 2);
    }
    #[test]
    fn nine_plus_nine_minus_nine_minus_nine_is_zero() {
        assert_eq!(math("9+9-9-9"), 0);
    }
    #[test]
    fn eight_minus_nine_plus_nine_is_eight_even_with_characters_on_the_end() {
        assert_eq!(math("8  - 9     +9-----+++++"), 8);
    }
    #[test]
    #[should_panic]
    fn panics_when_characters_not_right() {
        math("7 + seven");
    }
}
```

最後我們增加兩個新方法。一個叫做 `.clear()`，清除 `current_input()`。另一個叫做 `push_char()`，把輸入推到 `current_input()` 上。這是我們重構後的代碼。

```rust
#[derive(Clone)]
struct Calculator {
    results: Vec<String>,
    current_input: String,
    total: i32,
    adds: bool,
}

impl Calculator {
    fn new() -> Self {
        Self {
            results: vec![],
            current_input: String::new(),
            total: 0,
            adds: true,
        }
    }

    fn clear(&mut self) {
        self.current_input.clear();
    }

    fn push_char(&mut self, character: char) {
        self.current_input.push(character);
    }
}

const OKAY_CHARACTERS: &str = "1234567890+- ";

fn math(input: &str) -> i32 {
    if !input.chars().all(|character| OKAY_CHARACTERS.contains(character)) ||
       !input.chars().take(2).any(|character| character.is_numeric()) {
        panic!("Please only input numbers, +-, or spaces");
    }

    let input = input.trim_end_matches(|x| "+- ".contains(x)).chars().filter(|x| *x != ' ').collect::<String>();
    let mut calculator = Calculator::new();

    for character in input.chars() {
        match character {
            '+' => {
                if !calculator.current_input.is_empty() {
                    calculator.results.push(calculator.current_input.clone());
                    calculator.clear();
                }
            },
            '-' => {
                if calculator.current_input.contains('-') || calculator.current_input.is_empty() {
                    calculator.push_char(character)
                } else {
                calculator.results.push(calculator.current_input.clone());
                calculator.clear();
                calculator.push_char(character);
                }
            },
            number => {
                if calculator.current_input.contains('-') {
                    calculator.results.push(calculator.current_input.clone());
                    calculator.clear();
                    calculator.push_char(number);
                } else {
                    calculator.push_char(number);
                }
            },
        }
    }
    calculator.results.push(calculator.current_input);

    for entry in calculator.results {
        if entry.contains('-') {
            if entry.chars().count() % 2 == 1 {
                calculator.adds = match calculator.adds {
                    true => false,
                    false => true
                };
                continue;
            } else {
                continue;
            }
        }
        if calculator.adds {
            calculator.total += entry.parse::<i32>().unwrap();
        } else {
            calculator.total -= entry.parse::<i32>().unwrap();
            calculator.adds = true;
        }
    }
    calculator.total
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn one_plus_one_is_two() {
        assert_eq!(math("1 + 1"), 2);
    }
    #[test]
    fn one_minus_two_is_minus_one() {
        assert_eq!(math("1 - 2"), -1);
    }
    #[test]
    fn one_minus_minus_one_is_two() {
        assert_eq!(math("1 - -1"), 2);
    }
    #[test]
    fn nine_plus_nine_minus_nine_minus_nine_is_zero() {
        assert_eq!(math("9+9-9-9"), 0);
    }
    #[test]
    fn eight_minus_nine_plus_nine_is_eight_even_with_characters_on_the_end() {
        assert_eq!(math("8  - 9     +9-----+++++"), 8);
    }
    #[test]
    #[should_panic]
    fn panics_when_characters_not_right() {
        math("7 + seven");
    }
}
```

現在大概已經夠好了。我們可以寫更多的方法，但是像`calculator.results.push(calculator.current_input.clone());`這樣的行已經很清楚了。重構最好是在你完成後還能輕鬆閱讀代碼的時候。你不希望只是為了讓代碼變短而重構:例如，`clc.clr()`就比`calculator.clear()`差很多。



## 外部crate

外部crate的意思是 "別人的crate"。

在本節中，你*差不多*需要安裝Rust，但我們仍然可以只使用Playground。現在我們要學習如何導入別人寫的crate。這在Rust中很重要，原因有二。

- 導入其他的crate很容易，並且...
- Rust標準庫是相當小的。

這意味著，在Rust中，很多基本功能都需要用到外部Crate，這很正常。我們的想法是，如果使用外部Crate很方便，那麼你可以選擇最好的一個。也許一個人會為一個功能創建一個crate，然後其他人會創建一個更好的crate。

在本書中，我們只看最流行的crate，也就是每個使用Rust的人都知道的crate。

要開始學習外部Crate，我們將從最常見的Crate開始。`rand`.

### rand

你有沒有注意到，我們還沒有使用任何隨機數？那是因為隨機數不在標準庫中。但是有很多crate "幾乎是標準庫"，因為大家都在使用它們。在任何情況下，帶入一個 crate 是非常容易的。如果你的電腦上有Rust，有一個叫`Cargo.toml`的文件，裡面有這些信息。`Cargo.toml`文件在你啟動時是這樣的。

```text
[package]
name = "rust_book"
version = "0.1.0"
authors = ["David MacLeod"]
edition = "2018"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
```

現在，如果你想添加`rand` crate，在`crates.io`上搜索它，這是所有crate的去處。這將帶你到`https://crates.io/crates/rand`。當你點擊那個，你可以看到一個屏幕，上面寫著`Cargo.toml   rand = "0.7.3"`。你所要做的就是在[dependencies]下添加這樣的內容:

```text
[package]
name = "rust_book"
version = "0.1.0"
authors = ["David MacLeod"]
edition = "2018"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
rand = "0.7.3"
```

然後Cargo會幫你完成剩下的工作。然後你就可以在`rand`文檔網站上開始編寫像[本例代碼](https://docs.rs/rand/0.7.3/rand/)這樣的代碼。要想進入文檔，你可以點擊[crates.io上的頁面](https://crates.io/crates/rand)中的`docs`按鈕。

關於Cargo的介紹就到這裡了:我們現在使用的還只是playground。幸運的是，playground已經安裝了前100個crate。所以你還不需要寫進`Cargo.toml`。在playground上，你可以想象，它有一個這樣的長長的列表，有100個crate。


```text
[dependencies]
rand = "0.7.3"
some_other_crate = "0.1.0"
another_nice_crate = "1.7"
```


也就是說，如果要使用`rand`，你可以直接這樣做:

```rust
use rand; // This means the whole crate rand
          // On your computer you can't just write this;
          // you need to write in the Cargo.toml file first

fn main() {
    for _ in 0..5 {
        let random_u16 = rand::random::<u16>();
        print!("{} ", random_u16);
    }
}
```

每次都會打印不同的`u16`號碼，比如`42266 52873 56528 46927 6867`。



`rand`中的主要功能是`random`和`thread_rng`(rng的意思是 "隨機數發生器")。而實際上如果你看`random`，它說:"這只是`thread_rng().gen()`的一個快捷方式"。所以其實是`thread_rng`基本做完了一切。

下面是一個簡單的例子，從1到10的數字。為了得到這些數字，我們在1到11之間使用`.gen_range()`。

```rust
use rand::{thread_rng, Rng}; // Or just use rand::*; if we are lazy

fn main() {
    let mut number_maker = thread_rng();
    for _ in 0..5 {
        print!("{} ", number_maker.gen_range(1, 11));
    }
}
```

這將打印出`7 2 4 8 6`這樣的東西。

用隨機數我們可以做一些有趣的事情，比如為遊戲創建角色。我們將使用`rand`和其他一些我們知道的東西來創建它們。在這個遊戲中，我們的角色有六種狀態，用一個d6來表示他們。d6是一個立方體，當你投擲它時，它能給出1、2、3、4、5或6。每個角色都會擲三次d6，所以每個統計都在3到18之間。

但是有時候如果你的角色有一些低的東西，比如3或4，那就不公平了。比如說你的力量是3，你就不能拿東西。所以還有一種方法是用d6四次。你擲四次，然後扔掉最低的數字。所以如果你擲3，3，1，6，那麼你保留3，3，6=12。我們也會把這個方法做出來，所以遊戲的主人可以決定。

這是我們簡單的角色創建器。我們為數據統計創建了一個`Character`結構，甚至還實現了`Display`來按照我們想要的方式打印。

```rust
use rand::{thread_rng, Rng}; // Or just use rand::*; if we are lazy
use std::fmt; // Going to impl Display for our character


struct Character {
    strength: u8,
    dexterity: u8,    // This means "body quickness"
    constitution: u8, // This means "health"
    intelligence: u8,
    wisdom: u8,
    charisma: u8, // This means "popularity with people"
}

fn three_die_six() -> u8 { // A "die" is the thing you throw to get the number
    let mut generator = thread_rng(); // Create our random number generator
    let mut stat = 0; // This is the total
    for _ in 0..3 {
        stat += generator.gen_range(1..=6); // Add each time
    }
    stat // Return the total
}

fn four_die_six() -> u8 {
    let mut generator = thread_rng();
    let mut results = vec![]; // First put the numbers in a vec
    for _ in 0..4 {
        results.push(generator.gen_range(1..=6));
    }
    results.sort(); // Now a result like [4, 3, 2, 6] becomes [2, 3, 4, 6]
    results.remove(0); // Now it would be [3, 4, 6]
    results.iter().sum() // Return this result
}

enum Dice {
    Three,
    Four
}

impl Character {
    fn new(dice: Dice) -> Self { // true for three dice, false for four
        match dice {
            Dice::Three => Self {
                strength: three_die_six(),
                dexterity: three_die_six(),
                constitution: three_die_six(),
                intelligence: three_die_six(),
                wisdom: three_die_six(),
                charisma: three_die_six(),
            },
            Dice::Four => Self {
                strength: four_die_six(),
                dexterity: four_die_six(),
                constitution: four_die_six(),
                intelligence: four_die_six(),
                wisdom: four_die_six(),
                charisma: four_die_six(),
            },
        }
    }
    fn display(&self) { // We can do this because we implemented Display below
        println!("{}", self);
        println!();
    }
}

impl fmt::Display for Character { // Just follow the code for in https://doc.rust-lang.org/std/fmt/trait.Display.html and change it a bit
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "Your character has these stats:
strength: {}
dexterity: {}
constitution: {}
intelligence: {}
wisdom: {}
charisma: {}",
            self.strength,
            self.dexterity,
            self.constitution,
            self.intelligence,
            self.wisdom,
            self.charisma
        )
    }
}



fn main() {
    let weak_billy = Character::new(Dice::Three);
    let strong_billy = Character::new(Dice::Four);
    weak_billy.display();
    strong_billy.display();
}
```

它會打印出這樣的東西。

```rust
Your character has these stats:
strength: 9
dexterity: 15
constitution: 15
intelligence: 8
wisdom: 11
charisma: 9

Your character has these stats:
strength: 9
dexterity: 13
constitution: 14
intelligence: 16
wisdom: 16
charisma: 10
```

有四個骰子的角色通常在大多數事情上都會好一點。


### rayon

`rayon` 是一個流行的crate，它可以讓你加快 Rust 代碼的速度。它之所以受歡迎，是因為它無需像 `thread::spawn` 這樣的東西就能創建線程。換句話說，它之所以受歡迎是因為它既有效又容易編寫。比如說

- `.iter()`, `.iter_mut()`, `into_iter()`在rayon中是這樣寫的:
- `.par_iter()`, `.par_iter_mut()`, `par_into_iter()`. 所以你只要加上`par_`，你的代碼就會變得快很多。(par的意思是 "並行")

其他方法也一樣:`.chars()`就是`.par_chars()`，以此類推。

這裡舉個例子，一段簡單的代碼，卻讓計算機做了很多工作。
```rust
fn main() {
    let mut my_vec = vec![0; 200_000];
    my_vec.iter_mut().enumerate().for_each(|(index, number)| *number+=index+1);
    println!("{:?}", &my_vec[5000..5005]);
}
```

它創建了一個有20萬項的向量:每一項都是0，然後調用`.enumerate()`來獲取每個數字的索引，並將0改為索引號。它的打印時間太長，所以我們只打印5000到5004項。這在Rust中還是非常快的，但如果你願意，你可以用Rayon讓它更快。代碼幾乎是一樣的。

```rust
use rayon::prelude::*; // Import rayon

fn main() {
    let mut my_vec = vec![0; 200_000];
    my_vec.par_iter_mut().enumerate().for_each(|(index, number)| *number+=index+1); // add par_ to iter_mut
    println!("{:?}", &my_vec[5000..5005]);
}
```

就這樣了。`rayon`還有很多其他的方法來定製你想做的事情，但最簡單的就是 "添加`_par`，讓你的程序更快"。

### serde

`serde`是一個流行的crate，它可以在JSON、YAML等格式間相互轉換。最常見的使用方法是通過創建一個`struct`，上面有兩個屬性。[它看起來是這樣的](https://serde.rs/)。

```rust
#[derive(Serialize, Deserialize, Debug)]
struct Point {
    x: i32,
    y: i32,
}
```

`Serialize`和`Deserialize`trait是使轉換變得簡單的原因。(這也是`serde`這個名字的由來)如果你的結構體上有這兩個trait，那麼你只需要調用一個方法就可以把它轉化為JSON或其他任何東西。

### regex

[regex](https://crates.io/crates/regex) crate 可以讓你使用 [正則表達式](https://en.wikipedia.org/wiki/Regular_expression) 搜索文本。有了它，你可以通過一次搜索得到諸如 `colour`, `color`, `colours` 和 `colors` 的匹配信息。正則表達式是另一門語言，如果你想使用它們，也必須學會。

### chrono

[chrono](https://crates.io/crates/chrono)是為那些需要更多時間功能的人準備的主要crate。我們現在來看一下標準庫，它有時間的功能，但是如果你需要更多的功能，那麼這個crate是一個不錯的選擇。


## 標準庫之旅

現在你已經知道了很多Rust的知識，你將能夠理解標準庫裡面的大部分東西。它裡面的代碼已經不是那麼可怕了。讓我們來看看它裡面一些我們還沒有學過的部分。本篇遊記將介紹標準庫的大部分部分，你不需要安裝Rust。我們將重溫很多我們已經知道的內容，這樣我們就可以更深入地學習它們。

### 數組

關於數組需要注意的一點是，它們沒有實現`Iterator.`。這意味著，如果你有一個數組，你不能使用`for`。但是你可以對它們使用 `.iter()` 這樣的方法。或者你可以使用`&`來得到一個切片。實際上，如果你嘗試使用`for`，編譯器會準確地告訴你。

```rust
fn main() {
    // ⚠️
    let my_cities = ["Beirut", "Tel Aviv", "Nicosia"];

    for city in my_cities {
        println!("{}", city);
    }
}
```

消息是:

```text
error[E0277]: `[&str; 3]` is not an iterator
 --> src\main.rs:5:17
  |
  |                 ^^^^^^^^^ borrow the array with `&` or call `.iter()` on it to iterate over it
```

所以讓我們試試這兩種方法。它們的結果是一樣的。

```rust
fn main() {
    let my_cities = ["Beirut", "Tel Aviv", "Nicosia"];

    for city in &my_cities {
        println!("{}", city);
    }
    for city in my_cities.iter() {
        println!("{}", city);
    }
}
```

這個打印:

```text
Beirut
Tel Aviv
Nicosia
Beirut
Tel Aviv
Nicosia
```



如果你想從一個數組中獲取變量，你可以把它們的名字放在 `[]` 中來解構它。這與在 `match` 語句中使用元組或從結構體中獲取變量是一樣的。

```rust
fn main() {
    let my_cities = ["Beirut", "Tel Aviv", "Nicosia"];
    let [city1, city2, city3] = my_cities;
    println!("{}", city1);
}
```

打印出`Beirut`.

### char

您可以使用`.escape_unicode()`的方法來獲取`char`的Unicode號碼。

```rust
fn main() {
    let korean_word = "청춘예찬";
    for character in korean_word.chars() {
        print!("{} ", character.escape_unicode());
    }
}
```


這將打印出 `u{ccad} u{cd98} u{c608} u{cc2c}`。


你可以使用 `From` trait從 `u8` 中得到一個字符，但對於 `u32`，你使用 `TryFrom`，因為它可能無法工作。`u32`中的數字比Unicode中的字符多很多。我們可以通過一個簡單的演示來瞭解。

```rust
use std::convert::TryFrom; // You need to bring TryFrom in to use it
use rand::prelude::*;      // We will use random numbers too

fn main() {
    let some_character = char::from(99); // This one is easy - no need for TryFrom
    println!("{}", some_character);

    let mut random_generator = rand::thread_rng();
    // This will try 40,000 times to make a char from a u32.
    // The range is 0 (std::u32::MIN) to u32's highest number (std::u32::MAX). If it doesn't work, we will give it '-'.
    for _ in 0..40_000 {
        let bigger_character = char::try_from(random_generator.gen_range(std::u32::MIN..std::u32::MAX)).unwrap_or('-');
        print!("{}", bigger_character)
    }
}
```

幾乎每次都會生成一個`-`。這是你會看到的那種輸出的一部分。

```text
------------------------------------------------------------------------𤒰---------------------
-----------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
-------------------------------------------------------------춗--------------------------------
-----------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------
------------򇍜----------------------------------------------------
```

所以，你要用`TryFrom`是件好事。

另外，從2020年8月底開始，你現在可以從`char`中得到一個`String`。(`String`實現了`From<char>`)只要寫`String::from()`，然後在裡面放一個`char`。


### 整數

這些類型的數學方法有很多，另外還有一些其他的方法。下面是一些最有用的。



`.checked_add()`, `.checked_sub()`, `.checked_mul()`, `.checked_div()`. 如果你認為你可能會得到一個不適合類型的數字，這些都是不錯的方法。它們會返回一個 `Option`，這樣你就可以安全地檢查你的數學計算是否正常，而不會讓程序崩潰。

```rust
fn main() {
    let some_number = 200_u8;
    let other_number = 200_u8;

    println!("{:?}", some_number.checked_add(other_number));
    println!("{:?}", some_number.checked_add(1));
}
```

這個打印:

```text
None
Some(201)
```


你會注意到，在整數的頁面上，經常說`rhs`。這意味著 "右邊"，也就是你做一些數學運算時的右操作數。比如在`5 + 6`中，`5`在左邊，`6`在右邊，所以`6`就是`rhs`。這個不是關鍵詞，但是你會經常看到，所以知道就好。

說到這裡，我們來學習一下如何實現`Add`。在你實現了`Add`之後，你可以在你創建的類型上使用`+`。你需要自己實現`Add`，因為add可以表達很多意思。這是標準庫頁面中的例子。

```rust
use std::ops::Add; // first bring in Add

#[derive(Debug, Copy, Clone, PartialEq)] // PartialEq is probably the most important part here. You want to be able to compare numbers
struct Point {
    x: i32,
    y: i32,
}

impl Add for Point {
    type Output = Self; // Remember, this is called an "associated type": a "type that goes together".
                        // In this case it's just another Point

    fn add(self, other: Self) -> Self {
        Self {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }
}
```

現在讓我們為自己的類型實現`Add`。讓我們想象一下，我們想把兩個國家加在一起，這樣我們就可以比較它們的經濟。它看起來像這樣:

```rust
use std::fmt;
use std::ops::Add;

#[derive(Clone)]
struct Country {
    name: String,
    population: u32,
    gdp: u32, // This is the size of the economy
}

impl Country {
    fn new(name: &str, population: u32, gdp: u32) -> Self {
        Self {
            name: name.to_string(),
            population,
            gdp,
        }
    }
}

impl Add for Country {
    type Output = Self;

    fn add(self, other: Self) -> Self {
        Self {
            name: format!("{} and {}", self.name, other.name), // We will add the names together,
            population: self.population + other.population, // and the population,
            gdp: self.gdp + other.gdp,   // and the GDP
        }
    }
}

impl fmt::Display for Country {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "In {} are {} people and a GDP of ${}", // Then we can print them all with just {}
            self.name, self.population, self.gdp
        )
    }
}

fn main() {
    let nauru = Country::new("Nauru", 10_670, 160_000_000);
    let vanuatu = Country::new("Vanuatu", 307_815, 820_000_000);
    let micronesia = Country::new("Micronesia", 104_468, 367_000_000);

    // We could have given Country a &str instead of a String for the name. But we would have to write lifetimes everywhere
    // and that would be too much for a small example. Better to just clone them when we call println!.
    println!("{}", nauru.clone());
    println!("{}", nauru.clone() + vanuatu.clone());
    println!("{}", nauru + vanuatu + micronesia);
}
```

這個打印:

```text
In Nauru are 10670 people and a GDP of $160000000
In Nauru and Vanuatu are 318485 people and a GDP of $980000000
In Nauru and Vanuatu and Micronesia are 422953 people and a GDP of $1347000000
```

以後在這段代碼中，我們可以把`.fmt()`改成更容易閱讀的數字顯示。

另外三個叫`Sub`、`Mul`和`Div`，實現起來基本一樣。`+=`、`-=`、`*=`和`/=`，只要加上`Assign`:`AddAssign`、`SubAssign`、`MulAssign`和`DivAssign`即可。你可以看到完整的列表[這裡](https://doc.rust-lang.org/std/ops/index.html#structs)，因為還有很多。例如 `%` 被稱為 `Rem`, `-` 被稱為 `Neg`, 等等。


### 浮點數

`f32`和`f64`有非常多的方法，你在做數學計算的時候會用到。我們不看這些，但這裡有一些你可能會用到的方法。它們分別是 `.floor()`, `.ceil()`, `.round()`, 和 `.trunc()`. 所有這些方法都返回一個 `f32` 或 `f64`，它像一個整數，小數點後面是 `0`。它們是這樣做的。

- `.floor()`: 給你下一個最低的整數.
- `.ceil()`: 給你下一個最高的整數。
- `.round()`: 如果小數部分大於等於0.5，返回數值加1;如果小數部分小於0.5，返回相同數值。這就是所謂的四捨五入，因為它給你一個 "舍入"的數字(一個數字的簡短形式)。
- `.trunc()`:只是把小數點號後的部分截掉。Truncate是 "截斷"的意思。

這裡有一個簡單的函數來打印它們。

```rust
fn four_operations(input: f64) {
    println!(
"For the number {}:
floor: {}
ceiling: {}
rounded: {}
truncated: {}\n",
        input,
        input.floor(),
        input.ceil(),
        input.round(),
        input.trunc()
    );
}

fn main() {
    four_operations(9.1);
    four_operations(100.7);
    four_operations(-1.1);
    four_operations(-19.9);
}
```

這個打印:

```text
For the number 9.1:
floor: 9
ceiling: 10
rounded: 9 // because less than 9.5
truncated: 9

For the number 100.7:
floor: 100
ceiling: 101
rounded: 101 // because more than 100.5
truncated: 100

For the number -1.1:
floor: -2
ceiling: -1
rounded: -1
truncated: -1

For the number -19.9:
floor: -20
ceiling: -19
rounded: -20
truncated: -19
```

`f32` 和 `f64` 有一個叫做 `.max()` 和 `.min()` 的方法，可以得到兩個數字中較大或較小的數字。(對於其他類型，你可以直接使用`std::cmp::max`和`std::cmp::min`。)下面是用`.fold()`來得到最高或最低數的方法。你又可以看到，`.fold()`不僅僅是用來加數字的。

```rust
fn main() {
    let my_vec = vec![8.0_f64, 7.6, 9.4, 10.0, 22.0, 77.345, 10.22, 3.2, -7.77, -10.0];
    let maximum = my_vec.iter().fold(f64::MIN, |current_number, next_number| current_number.max(*next_number)); // Note: start with the lowest possible number for an f64.
    let minimum = my_vec.iter().fold(f64::MAX, |current_number, next_number| current_number.min(*next_number)); // And here start with the highest possible number
    println!("{}, {}", maximum, minimum);
}
```

### bool

在 Rust 中，如果你願意，你可以把 `bool` 變成一個整數，因為這樣做是安全的。但你不能反過來做。如你所見，`true`變成了1，`false`變成了0。

```rust
fn main() {
    let true_false = (true, false);
    println!("{} {}", true_false.0 as u8, true_false.1 as i32);
}
```

這將打印出`1 0`。如果你告訴編譯器類型，也可以使用 `.into()`。

```rust
fn main() {
    let true_false: (i128, u16) = (true.into(), false.into());
    println!("{} {}", true_false.0, true_false.1);
}
```

這打印的是一樣的東西。

從Rust 1.50(2021年2月發佈)開始，有一個叫做 `then()`的方法，它將一個 `bool`變成一個 `Option`。使用`then()`時需要一個閉包，如果item是`true`，閉包就會被調用。同時，無論從閉包中返回什麼，都會進入`Option`中。下面是一個小例子:

```rust
fn main() {

    let (tru, fals) = (true.then(|| 8), false.then(|| 8));
    println!("{:?}, {:?}", tru, fals);
}
```

這個打印 `Some(8), None`。

下面是一個較長的例子:

```rust
fn main() {
    let bool_vec = vec![true, false, true, false, false];

    let option_vec = bool_vec
        .iter()
        .map(|item| {
            item.then(|| { // Put this inside of map so we can pass it on
                println!("Got a {}!", item);
                "It's true, you know" // This goes inside Some if it's true
                                      // Otherwise it just passes on None
            })
        })
        .collect::<Vec<_>>();

    println!("Now we have: {:?}", option_vec);

    // That printed out the Nones too. Let's filter map them out in a new Vec.
    let filtered_vec = option_vec.into_iter().filter_map(|c| c).collect::<Vec<_>>();

    println!("And without the Nones: {:?}", filtered_vec);
}
```

將打印:

```text
Got a true!
Got a true!
Now we have: [Some("It\'s true, you know"), None, Some("It\'s true, you know"), None, None]
And without the Nones: ["It\'s true, you know", "It\'s true, you know"]
```

### Vec

Vec有很多方法我們還沒有看。先說說`.sort()`。`.sort()`一點都不奇怪。它使用`&mut self`來對一個向量進行排序。

```rust
fn main() {
    let mut my_vec = vec![100, 90, 80, 0, 0, 0, 0, 0];
    my_vec.sort();
    println!("{:?}", my_vec);
}
```

這樣打印出來的是`[0, 0, 0, 0, 0, 80, 90, 100]`。但還有一種更有趣的排序方式叫`.sort_unstable()`，它通常更快。它之所以更快，是因為它不在乎排序前後相同數字的先後順序。在常規的`.sort()`中，你知道最後的`0, 0, 0, 0, 0`會在`.sort()`之後的順序相同。但是`.sort_unstable()`可能會把最後一個0移到索引0，然後把第三個最後的0移到索引2，等等。


`.dedup()`的意思是 "去重複"。它將刪除一個向量中相同的元素，但只有當它們彼此相鄰時才會刪除。接下來這段代碼不會只打印`"sun", "moon"`。

```rust
fn main() {
    let mut my_vec = vec!["sun", "sun", "moon", "moon", "sun", "moon", "moon"];
    my_vec.dedup();
    println!("{:?}", my_vec);
}
```


它只是把另一個 "sun"旁邊的 "sun"去掉，然後把一個 "moon"旁邊的 "moon"去掉，再把另一個 "moon"旁邊的 "moon"去掉。結果是 `["sun", "moon", "sun", "moon"]`.

如果你想把每個重複的東西都去掉，就先`.sort()`:

```rust
fn main() {
    let mut my_vec = vec!["sun", "sun", "moon", "moon", "sun", "moon", "moon"];
    my_vec.sort();
    my_vec.dedup();
    println!("{:?}", my_vec);
}
```

結果:`["moon", "sun"]`.


### String

你會記得，`String`有點像`Vec`。它很像`Vec`，你可以調用很多相同的方法。比如說，你可以用`String::with_capacity()`創建一個，如果你需要多次用`.push()`推一個`char`，或者用`.push_str()`推一個`&str`。下面是一個有多次內存分配的`String`的例子。

```rust
fn main() {
    let mut push_string = String::new();
    let mut capacity_counter = 0; // capacity starts at 0
    for _ in 0..100_000 { // Do this 100,000 times
        if push_string.capacity() != capacity_counter { // First check if capacity is different now
            println!("{}", push_string.capacity()); // If it is, print it
            capacity_counter = push_string.capacity(); // then update the counter
        }
        push_string.push_str("I'm getting pushed into the string!"); // and push this in every time
    }
}
```

這個打印:

```text
35
70
140
280
560
1120
2240
4480
8960
17920
35840
71680
143360
286720
573440
1146880
2293760
4587520
```

我們不得不重新分配(把所有東西複製過來)18次。但既然我們知道了最終的容量，我們可以馬上設置容量，不需要重新分配:只設置一次`String`容量就夠了。

```rust
fn main() {
    let mut push_string = String::with_capacity(4587520); // We know the exact number. Some different big number could work too
    let mut capacity_counter = 0;
    for _ in 0..100_000 {
        if push_string.capacity() != capacity_counter {
            println!("{}", push_string.capacity());
            capacity_counter = push_string.capacity();
        }
        push_string.push_str("I'm getting pushed into the string!");
    }
}
```

而這個打印`4587520`。完美的! 我們再也不用分配了。

當然，實際長度肯定比這個小。如果你試了100001次，101000次等等，還是會說`4587520`。這是因為每次的容量都是之前的2倍。不過我們可以用`.shrink_to_fit()`來縮小它(和`Vec`一樣)。我們的`String`已經非常大了，我們不想再給它增加任何東西，所以我們可以把它縮小一點。但是隻有在你有把握的情況下才可以這樣做:下面是原因。

```rust
fn main() {
    let mut push_string = String::with_capacity(4587520);
    let mut capacity_counter = 0;
    for _ in 0..100_000 {
        if push_string.capacity() != capacity_counter {
            println!("{}", push_string.capacity());
            capacity_counter = push_string.capacity();
        }
        push_string.push_str("I'm getting pushed into the string!");
    }
    push_string.shrink_to_fit();
    println!("{}", push_string.capacity());
    push_string.push('a');
    println!("{}", push_string.capacity());
    push_string.shrink_to_fit();
    println!("{}", push_string.capacity());
}
```

這個打印:

```text
4587520
3500000
7000000
3500001
```

所以首先我們的大小是`4587520`，但我們沒有全部使用。我們用了`.shrink_to_fit()`，然後把大小降到了`3500000`。但是我們忘記了我們需要推上一個 `a`。當我們這樣做的時候，Rust 看到我們需要更多的空間，給了我們雙倍的空間:現在是 `7000000`。Whoops! 所以我們又調用了`.shrink_to_fit()`，現在又回到了`3500001`。

`.pop()`對`String`有用，就像對`Vec`一樣。

```rust
fn main() {
    let mut my_string = String::from(".daer ot drah tib elttil a si gnirts sihT");
    loop {
        let pop_result = my_string.pop();
        match pop_result {
            Some(character) => print!("{}", character),
            None => break,
        }
    }
}
```

這打印的是`This string is a little bit hard to read.`，因為它是從最後一個字符開始的。

`.retain()`是一個使用閉包的方法，這對`String`來說是罕見的。就像在迭代器上的`.filter()`一樣。

```rust
fn main() {
    let mut my_string = String::from("Age: 20 Height: 194 Weight: 80");
    my_string.retain(|character| character.is_alphabetic() || character == ' '); // Keep if a letter or a space
    dbg!(my_string); // Let's use dbg!() for fun this time instead of println!
}
```

這個打印:

```text
[src\main.rs:4] my_string = "Age  Height  Weight "
```


### OsString和CString

`std::ffi`是`std`的一部分，它幫助你將Rust與其他語言或操作系統一起使用。它有`OsString`和`CString`這樣的類型，它們就像操作系統的`String`或語言C的`String`一樣，它們各自也有自己的`&str`類型:`OsStr`和`CStr`。`ffi`的意思是 "foreign function interface"(外部函數接口)。

當你必須與一個沒有Unicode的操作系統一起工作時，你可以使用`OsString`。所有的Rust字符串都是unicode，但不是每個操作系統支持。下面是標準庫中關於為什麼我們有`OsString`的簡單英文解釋。

- Unix系統(Linux等)上的字符串可能是很多沒有0的字節組合在一起。而且有時你會把它們讀成Unicode UTF-8。
- Windows上的字符串可能是由隨機的16位值組成的，沒有0。有時你會把它們讀成Unicode UTF-16。
- 在Rust中，字符串總是有效的UTF-8，其中可能包含0。

所以，`OsString`被設計為支持它們讀取。

你可以用一個`OsString`做所有常規的事情，比如`OsString::from("Write something here")`。它還有一個有趣的方法，叫做 `.into_string()`，試圖把自己變成一個常規的 `String`。它返回一個 `Result`，但 `Err` 部分只是原來的 `OsString`。

```rust
// 🚧
pub fn into_string(self) -> Result<String, OsString>
```

所以如果不行的話，那你就把它找回來。你不能調用`.unwrap()`，因為它會崩潰，但是你可以使用`match`來找回`OsString`。我們通過調用不存在的方法來測試一下。

```rust
use std::ffi::OsString;

fn main() {
    // ⚠️
    let os_string = OsString::from("This string works for your OS too.");
    match os_string.into_string() {
        Ok(valid) => valid.thth(),           // Compiler: "What's .thth()??"
        Err(not_valid) => not_valid.occg(),  // Compiler: "What's .occg()??"
    }
}
```

然後編譯器準確地告訴我們我們想知道的東西。

```text
error[E0599]: no method named `thth` found for struct `std::string::String` in the current scope
 --> src/main.rs:6:28
  |
6 |         Ok(valid) => valid.thth(),
  |                            ^^^^ method not found in `std::string::String`

error[E0599]: no method named `occg` found for struct `std::ffi::OsString` in the current scope
 --> src/main.rs:7:37
  |
7 |         Err(not_valid) => not_valid.occg(),
  |                                     ^^^^ method not found in `std::ffi::OsString`
```

我們可以看到，`valid`的類型是`String`，`not_valid`的類型是`OsString`。

### Mem

`std::mem`有一些非常有趣的方法。我們已經看到了一些，比如`.size_of()`、`.size_of_val()`和`.drop()`。


```rust
use std::mem;

fn main() {
    println!("{}", mem::size_of::<i32>());
    let my_array = [8; 50];
    println!("{}", mem::size_of_val(&my_array));
    let mut some_string = String::from("You can drop a String because it's on the heap");
    mem::drop(some_string);
    // some_string.clear();   If we did this it would panic
}
```

這個打印:

```text
4
200
```

下面是`mem`中的一些其他方法。

`swap()`: 用這個方法你可以交換兩個變量之間的值。你可以通過為每個變量創建一個可變引用來做。當你有兩個東西想交換，而Rust因為借用規則不讓你交換時，這很有幫助。或者只是當你想快速切換兩個東西的時候。

這裡有一個例子。

```rust
use std::{mem, fmt};

struct Ring { // Create a ring from Lord of the Rings
    owner: String,
    former_owner: String,
    seeker: String, // seeker means "person looking for it"
}

impl Ring {
    fn new(owner: &str, former_owner: &str, seeker: &str) -> Self {
        Self {
            owner: owner.to_string(),
            former_owner: former_owner.to_string(),
            seeker: seeker.to_string(),
        }
    }
}

impl fmt::Display for Ring { // Display to show who has it and who wants it
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            write!(f, "{} has the ring, {} used to have it, and {} wants it", self.owner, self.former_owner, self.seeker)
        }
}

fn main() {
    let mut one_ring = Ring::new("Frodo", "Gollum", "Sauron");
    println!("{}", one_ring);
    mem::swap(&mut one_ring.owner, &mut one_ring.former_owner); // Gollum got the ring back for a second
    println!("{}", one_ring);
}
```

這將打印:

```text
Frodo has the ring, Gollum used to have it, and Sauron wants it
Gollum has the ring, Frodo used to have it, and Sauron wants it
```

`replace()`:這個就像swap一樣，其實裡面也用了swap，你可以看到。

```rust
pub fn replace<T>(dest: &mut T, mut src: T) -> T {
    swap(dest, &mut src);
    src
}
```

所以它只是做了一個交換，然後返回另一個元素。有了這個，你就用你放進去的其他東西來替換這個值。因為它返回的是舊的值，所以你應該用`let`來使用它。下面是一個簡單的例子。

```rust
use std::mem;

struct City {
    name: String,
}

impl City {
    fn change_name(&mut self, name: &str) {
        let old_name = mem::replace(&mut self.name, name.to_string());
        println!(
            "The city once called {} is now called {}.",
            old_name, self.name
        );
    }
}

fn main() {
    let mut capital_city = City {
        name: "Constantinople".to_string(),
    };
    capital_city.change_name("Istanbul");
}
```

這樣就會打印出`The city once called Constantinople is now called Istanbul.`。

有一個函數叫`.take()`，和`.replace()`一樣，但它在元素中留下了默認值。
 你會記得，默認值通常是0、""之類的東西。這裡是簽名。

```rust
// 🚧
pub fn take<T>(dest: &mut T) -> T
where
    T: Default,
```

所以你可以做這樣的事情。

```rust
use std::mem;

fn main() {
    let mut number_vec = vec![8, 7, 0, 2, 49, 9999];
    let mut new_vec = vec![];

    number_vec.iter_mut().for_each(|number| {
        let taker = mem::take(number);
        new_vec.push(taker);
    });

    println!("{:?}\n{:?}", number_vec, new_vec);
}
```

你可以看到，它將所有數字都替換為0:沒有刪除任何索引。

```text
[0, 0, 0, 0, 0, 0]
[8, 7, 0, 2, 49, 9999]
```


當然，對於你自己的類型，你可以把`Default`實現成任何你想要的類型。我們來看一個例子，我們有一個`Bank`和一個`Robber`。每次他搶了`Bank`，他就會在桌子上拿到錢。但是辦公桌可以隨時從後面拿錢，所以它永遠有50。我們將為此自制一個類型，所以它將永遠有50。下面是它的工作原理。

```rust
use std::mem;
use std::ops::{Deref, DerefMut}; // We will use this to get the power of u32

struct Bank {
    money_inside: u32,
    money_at_desk: DeskMoney, // This is our "smart pointer" type. It has its own default, but it will use u32
}

struct DeskMoney(u32);

impl Default for DeskMoney {
    fn default() -> Self {
        Self(50) // default is always 50, not 0
    }
}

impl Deref for DeskMoney { // With this we can access the u32 using *
    type Target = u32;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl DerefMut for DeskMoney { // And with this we can add, subtract, etc.
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}

impl Bank {
    fn check_money(&self) {
        println!(
            "There is ${} in the back and ${} at the desk.\n",
            self.money_inside, *self.money_at_desk // Use * so we can just print the u32
        );
    }
}

struct Robber {
    money_in_pocket: u32,
}

impl Robber {
    fn check_money(&self) {
        println!("The robber has ${} right now.\n", self.money_in_pocket);
    }

    fn rob_bank(&mut self, bank: &mut Bank) {
        let new_money = mem::take(&mut bank.money_at_desk); // Here it takes the money, and leaves 50 because that is the default
        self.money_in_pocket += *new_money; // Use * because we can only add u32. DeskMoney can't add
        bank.money_inside -= *new_money;    // Same here
        println!("She robbed the bank. She now has ${}!\n", self.money_in_pocket);
    }
}

fn main() {
    let mut bank_of_klezkavania = Bank { // Set up our bank
        money_inside: 5000,
        money_at_desk: DeskMoney(50),
    };
    bank_of_klezkavania.check_money();

    let mut robber = Robber { // Set up our robber
        money_in_pocket: 50,
    };
    robber.check_money();

    robber.rob_bank(&mut bank_of_klezkavania); // Rob, then check money
    robber.check_money();
    bank_of_klezkavania.check_money();

    robber.rob_bank(&mut bank_of_klezkavania); // Do it again
    robber.check_money();
    bank_of_klezkavania.check_money();

}
```

這將打印:

```text
There is $5000 in the back and $50 at the desk.

The robber has $50 right now.

She robbed the bank. She now has $100!

The robber has $100 right now.

There is $4950 in the back and $50 at the desk.

She robbed the bank. She now has $150!

The robber has $150 right now.

There is $4900 in the back and $50 at the desk.
```

你可以看到桌子上總是有50美元。


### Prelude

標準庫也有一個prelude，這就是為什麼你不用寫`use std::vec::Vec`這樣的東西來創建一個`Vec`。你可以[在這裡](https://doc.rust-lang.org/std/prelude/index.html#prelude-contents)看到所有這些元素，並且大致瞭解:

- `std::marker::{Copy, Send, Sized, Sync, Unpin}`. 你以前沒有見過`Unpin`，因為幾乎每一種類型都會用到它(比如`Sized`，也很常見)。"Pin"的意思是不讓東西動。在這種情況下，`Pin`意味著它在內存中不能移動，但大多數元素都有`Unpin`，所以你可以移動。這就是為什麼像`std::mem::replace`這樣的函數能用，因為它們沒有被釘住。
- `std::ops::{Drop, Fn, FnMut, FnOnce}`.
- `std::mem::drop`
- `std::boxed::Box`.
- `std::borrow::ToOwned`. 你之前用`Cow`看到過一點，它可以把借來的內容變成自己的。它使用`.to_owned()`來實現這個功能。你也可以在`&str`上使用`.to_owned()`，得到一個`String`，對於其他借來的值也是一樣。
- `std::clone::Clone`
- `std::cmp::{PartialEq, PartialOrd, Eq, Ord}`.
- `std::convert::{AsRef, AsMut, Into, From}`.
- `std::default::Default`.
- `std::iter::{Iterator, Extend, IntoIterator, DoubleEndedIterator, ExactSizeIterator}`. 我們之前用`.rev()`來做迭代器:這實際上是做了一個`DoubleEndedIterator`。`ExactSizeIterator`只是類似於`0..10`的東西:它已經知道自己的`.len()`是10。其他迭代器不知道它們的長度是肯定的。
- `std::option::Option::{self, Some, None}`.
- `std::result::Result::{self, Ok, Err}`.
- `std::string::{String, ToString}`.
- `std::vec::Vec`.

如果你因為某些原因不想要這個prelude怎麼辦？就加屬性`#![no_implicit_prelude]`。我們來試一試，看編譯器的抱怨。

```rust
// ⚠️
#![no_implicit_prelude]
fn main() {
    let my_vec = vec![8, 9, 10];
    let my_string = String::from("This won't work");
    println!("{:?}, {}", my_vec, my_string);
}
```

現在Rust根本不知道你想做什麼。

```text
error: cannot find macro `println` in this scope
 --> src/main.rs:5:5
  |
5 |     println!("{:?}, {}", my_vec, my_string);
  |     ^^^^^^^

error: cannot find macro `vec` in this scope
 --> src/main.rs:3:18
  |
3 |     let my_vec = vec![8, 9, 10];
  |                  ^^^

error[E0433]: failed to resolve: use of undeclared type or module `String`
 --> src/main.rs:4:21
  |
4 |     let my_string = String::from("This won't work");
  |                     ^^^^^^ use of undeclared type or module `String`

error: aborting due to 3 previous errors
```

因此，對於這個簡單的代碼，你需要告訴Rust使用`extern`(外部)crate，叫做`std`，然後是你想要的元素。這裡是我們要做的一切，只是為了創建一個Vec和一個String，並打印它。

```rust
#![no_implicit_prelude]

extern crate std; // Now you have to tell Rust that you want to use a crate called std
use std::vec; // We need the vec macro
use std::string::String; // and string
use std::convert::From; // and this to convert from a &str to the String
use std::println; // and this to print

fn main() {
    let my_vec = vec![8, 9, 10];
    let my_string = String::from("This won't work");
    println!("{:?}, {}", my_vec, my_string);
}
```

現在終於成功了，打印出`[8, 9, 10], This won't work`。所以你可以明白為什麼Rust要用prelude了。但如果你願意，你不需要使用它。而且你甚至可以使用`#![no_std]`(我們曾經看到過)，用於你連堆棧內存這種東西都用不上的時候。但大多數時候，你根本不用考慮不用prelude或`std`。

那麼為什麼之前我們沒有看到`extern`這個關鍵字呢？是因為你已經不需要它了。以前，當帶入外部crate時，你必須使用它。所以以前要使用`rand`，你必須要寫成:

```rust
extern crate rand;
```

然後用 `use` 語句來表示你想使用的修改、trait等。但現在Rust編譯器已經不需要這些幫助了--你只需要使用`use`，rust就知道在哪裡可以找到它。所以你幾乎再也不需要`extern crate`了，但在其他人的Rust代碼中，你可能仍然會在頂部看到它。



### Time

`std::time`是你可以找到時間函數的地方。(如果你想要更多的功能，`chrono`這樣的crate也可以。)最簡單的功能就是用`Instant::now()`獲取系統時間即可。

```rust
use std::time::Instant;

fn main() {
    let time = Instant::now();
    println!("{:?}", time);
}
```

如果你打印出來，你會得到這樣的東西。`Instant { tv_sec: 2738771, tv_nsec: 685628140 }`. 這說的是秒和納秒，但用處不大。比如你看2738771秒(寫於8月)，就是31.70天。這和月份、日子沒有任何關係。但是`Instant`的頁面告訴我們，它本身不應該有用。它說它是 "不透明的，只有和Duration一起才有用"。Opaque的意思是 "你搞不清楚"，而Duration的意思是 "過了多少時間"。所以它只有在做比較時間這樣的事情時才有用。

如果你看左邊的trait，其中一個是`Sub<Instant>`。也就是說我們可以用`-`來減去一個。而當我們點擊[src]看它的作用時，頁面顯示：

```rust
impl Sub<Instant> for Instant {
    type Output = Duration;

    fn sub(self, other: Instant) -> Duration {
        self.duration_since(other)
    }
}
```

因此，它需要一個`Instant`，並使用`.duration_since()`給出一個`Duration`。讓我們試著打印一下。我們將創建兩個相鄰的 `Instant::now()`，然後讓程序忙活一會兒，再創建一個 `Instant::now()`。然後我們再創建一個`Instant::now()`. 最後，我們來看看用了多長時間。

```rust
use std::time::Instant;

fn main() {
    let time1 = Instant::now();
    let time2 = Instant::now(); // These two are right next to each other

    let mut new_string = String::new();
    loop {
        new_string.push('წ'); // Make Rust push this Georgian letter onto the String
        if new_string.len() > 100_000 { //  until it is 100,000 bytes long
            break;
        }
    }
    let time3 = Instant::now();
    println!("{:?}", time2 - time1);
    println!("{:?}", time3 - time1);
}
```

這將打印出這樣的東西。

```text
1.025µs
683.378µs
```

所以，這只是1微秒多與683毫秒。我們可以看到，Rust確實花了一些時間來做。

不過我們可以用一個`Instant`做一件有趣的事情。
 我們可以把它變成`String`與`format!("{:?}", Instant::now());`。它的樣子是這樣的:

```rust
use std::time::Instant;

fn main() {
    let time1 = format!("{:?}", Instant::now());
    println!("{}", time1);
}
```

這樣就會打印出類似`Instant { tv_sec: 2740773, tv_nsec: 632821036 }`的東西。這是沒有用的，但是如果我們使用 `.iter()` 和 `.rev()` 以及 `.skip(2)`，我們可以跳過最後的 `}` 和 ` `。我們可以用它來創建一個隨機數發生器。

```rust
use std::time::Instant;

fn bad_random_number(digits: usize) {
    if digits > 9 {
        panic!("Random number can only be up to 9 digits");
    }
    let now = Instant::now();
    let output = format!("{:?}", now);

    output
        .chars()
        .rev()
        .skip(2)
        .take(digits)
        .for_each(|character| print!("{}", character));
    println!();
}

fn main() {
    bad_random_number(1);
    bad_random_number(1);
    bad_random_number(3);
    bad_random_number(3);
}
```

這樣就會打印出類似這樣的內容:

```text
6
4
967
180
```

這個函數被稱為`bad_random_number`，因為它不是一個很好的隨機數生成器。Rust有更好的crate，可以用比`rand`更少的代碼創建隨機數，比如`fastrand`。但這是一個很好的例子，你可以利用你的想象力用`Instant`來做一些事情。

當你有一個線程時，你可以使用`std::thread::sleep`使它停止一段時間。當你這樣做時，你必須給它一個duration。你不必創建多個線程來做這件事，因為每個程序至少在一個線程上。`sleep`雖然需要一個`Duration`，所以它可以知道要睡多久。你可以這樣選單位:`Duration::from_millis()`, `Duration::from_secs`, 等等。這裡舉一個例子:

```rust
use std::time::Duration;
use std::thread::sleep;

fn main() {
    let three_seconds = Duration::from_secs(3);
    println!("I must sleep now.");
    sleep(three_seconds);
    println!("Did I miss anything?");
}
```

這將只打印

```text
I must sleep now.
Did I miss anything?
```

但線程在三秒鐘內什麼也不做。當你有很多線程需要經常嘗試一些事情時，比如連接，你通常會使用`.sleep()`。你不希望線程在一秒鐘內使用你的處理器嘗試10萬次，而你只是想讓它有時檢查一下。所以，你就可以設置一個`Duration`，它就會在每次醒來的時候嘗試做它的任務。


### 其他宏


我們再來看看其他一些宏。

`unreachable!()`

這個宏有點像`todo!()`，除了它是針對你永遠不會用的代碼。也許你在一個枚舉中有一個`match`，你知道它永遠不會選擇其中的一個分支，所以代碼永遠無法達到那個分支。如果是這樣，你可以寫`unreachable!()`，這樣編譯器就知道可以忽略這部分。

例如，假設你有一個程序，當你選擇一個地方居住時，它會寫一些東西。在烏克蘭，除了切爾諾貝利，其他地方都不錯。你的程序不讓任何人選擇切爾諾貝利，因為它現在不是一個好地方。但是這個枚舉是很早以前在別人的代碼裡做的，你無法更改。所以在`match`的分支中，你可以用這個宏。它是這樣的:

```rust
enum UkrainePlaces {
    Kiev,
    Kharkiv,
    Chernobyl, // Pretend we can't change the enum - Chernobyl will always be here
    Odesa,
    Dnipro,
}

fn choose_city(place: &UkrainePlaces) {
    use UkrainePlaces::*;
    match place {
        Kiev => println!("You will live in Kiev"),
        Kharkiv => println!("You will live in Kharkiv"),
        Chernobyl => unreachable!(),
        Odesa => println!("You will live in Odesa"),
        Dnipro => println!("You will live in Dnipro"),
    }
}

fn main() {
    let user_input = UkrainePlaces::Kiev; // Pretend the user input is made from some other function. The user can't choose Chernobyl, no matter what
    choose_city(&user_input);
}
```

這將打印出 `You will live in Kiev`。

`unreachable!()`對你來說也很好讀，因為它提醒你代碼的某些部分是不可訪問的。不過你必須確定代碼確實是不可訪問的。如果編譯器調用`unreachable!()`，程序就會崩潰。

此外，如果你曾經有不可達的代碼，而編譯器知道，它會告訴你。下面是一個簡單的例子:

```rust
fn main() {
    let true_or_false = true;

    match true_or_false {
        true => println!("It's true"),
        false => println!("It's false"),
        true => println!("It's true"), // Whoops, we wrote true again
    }
}
```

它會說

```text
warning: unreachable pattern
 --> src/main.rs:7:9
  |
7 |         true => println!("It's true"),
  |         ^^^^
  |
```

但是`unreachable!()`是用於編譯器無法知道的時候，就像我們另一個例子。



`column!`, `line!`, `file!`, `module_path!`

這四個宏有點像`dbg!()`，因為你只是把它們放進代碼去給你調試信息。但是它們不需要任何變量--你只需要用它們和括號一起使用，而沒有其他的東西。它們放到一起很容易學:

- `column!()`給你寫的那一列
- `file!()`給你寫的文件的名稱
- `line!()`給你寫的那行字，然後是
- `module_path!()`給你模塊的位置。

接下來的代碼在一個簡單的例子中展示了這三者。我們將假裝有更多的代碼(mod裡面的mod)，因為這就是我們要使用這些宏的原因。你可以想象一個大的Rust程序,它有許多mod和文件。

```rust
pub mod something {
    pub mod third_mod {
        pub fn print_a_country(input: &mut Vec<&str>) {
            println!(
                "The last country is {} inside the module {}",
                input.pop().unwrap(),
                module_path!()
            );
        }
    }
}

fn main() {
    use something::third_mod::*;
    let mut country_vec = vec!["Portugal", "Czechia", "Finland"];

    // do some stuff
    println!("Hello from file {}", file!());

    // do some stuff
    println!(
        "On line {} we got the country {}",
        line!(),
        country_vec.pop().unwrap()
    );

    // do some more stuff

    println!(
        "The next country is {} on line {} and column {}.",
        country_vec.pop().unwrap(),
        line!(),
        column!(),
    );

    // lots more code

    print_a_country(&mut country_vec);
}
```

它打印的是這樣的。

```text
Hello from file src/main.rs
On line 23 we got the country Finland
The next country is Czechia on line 32 and column 9.
The last country is Portugal inside the module rust_book::something::third_mod
```



`cfg!`

我們知道，你可以使用 `#[cfg(test)]` 和 `#[cfg(windows)]` 這樣的屬性來告訴編譯器在某些情況下該怎麼做。當你有`test`時，當你在測試模式下運行Rust時，它會運行代碼(如果是在電腦上，你輸入`cargo test`)。而當你使用`windows`時，如果用戶使用的是Windows，它就會運行代碼。但也許你只是想根據不同操作系統對依賴系統的代碼做很小的修改。這時候這個宏就很有用了。它返回一個`bool`。

```rust
fn main() {
    let helpful_message = if cfg!(target_os = "windows") { "backslash" } else { "slash" };

    println!(
        "...then in your hard drive, type the directory name followed by a {}. Then you...",
        helpful_message
    );
}
```

這將以不同的方式打印，取決於你的系統。Rust Playground在Linux上運行，所以會打印:

```text
...then in your hard drive, type the directory name followed by a slash. Then you...
```

`cfg!()`適用於任何一種配置。下面是一個例子，當你在測試中使用一個函數時，它的運行方式會有所不同。

```rust
#[cfg(test)] // cfg! will know to look for the word test
mod testing {
    use super::*;
    #[test]
    fn check_if_five() {
        assert_eq!(bring_number(true), 5); // This bring_number() function should return 5
    }
}

fn bring_number(should_run: bool) -> u32 { // This function takes a bool as to whether it should run
    if cfg!(test) && should_run { // if it should run and has the configuration test, return 5
        5
    } else if should_run { // if it's not a test but it should run, print something. When you run a test it ignores println! statements
        println!("Returning 5. This is not a test");
        5
    } else {
        println!("This shouldn't run, returning 0."); // otherwise return 0
        0
    }
}

fn main() {
    bring_number(true);
    bring_number(false);
}
```

現在根據配置的不同，它的運行方式也會不同。如果你只是運行程序，它會給你這樣的結果:

```text
Returning 5. This is not a test
This shouldn't run, returning 0.
```

但如果你在測試模式下運行它(`cargo test`，用於電腦上的Rust)，它實際上會運行測試。因為在這種情況下，測試總是返回5，所以它會通過。

```text
running 1 test
test testing::check_if_five ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```



## 編寫宏

編寫宏是非常複雜的。你可能永遠都不需要寫宏，但有時你可能會想寫，因為它們非常方便。寫宏很有趣，因為它們幾乎是不同的語言。要寫一個宏，你實際上是用另一個叫`macro_rules!`的宏。然後你添加你的宏名稱，並打開一個`{}`塊。裡面有點像`match`語句。

這裡有一個只取`()`，然後返回6:

```rust
macro_rules! give_six {
    () => {
        6
    };
}

fn main() {
    let six = give_six!();
    println!("{}", six);
}
```

但這和`match`語句是不一樣的，因為宏實際上不會編譯任何東西。它只是接受一個輸入並給出一個輸出。然後編譯器會檢查它是否有意義。這就是為什麼宏就像 "寫代碼的代碼"。你會記得，一個真正的`match`語句需要給出相同的類型，所以這不會工作:

```rust
fn main() {
// ⚠️
    let my_number = 10;
    match my_number {
        10 => println!("You got a ten"),
        _ => 10,
    }
}
```

它會抱怨你在一種情況下要返回`()`，在另一種情況下要返回`i32`。

```text
error[E0308]: `match` arms have incompatible types
 --> src\main.rs:5:14
  |
3 | /     match my_number {
4 | |         10 => println!("You got a ten"),
  | |               ------------------------- this is found to be of type `()`
5 | |         _ => 10,
  | |              ^^ expected `()`, found integer
6 | |     }
  | |_____- `match` arms have incompatible types
```

但宏並不關心，因為它只是給出一個輸出。它不是一個編譯器--它是代碼前的代碼。所以你可以這樣做:

```rust
macro_rules! six_or_print {
    (6) => {
        6
    };
    () => {
        println!("You didn't give me 6.");
    };
}

fn main() {
    let my_number = six_or_print!(6);
    six_or_print!();
}
```

這個就好辦了，打印的是`You didn't give me 6.`。你也可以看到，這不是匹配分支，因為沒有`_`行。我們只能給它`(6)`，或者`()`，其他的都會出錯。而我們給它的`6`甚至不是`i32`，只是一個輸入6。其實你可以設置任何東西作為宏的輸入，因為它只是看輸入，看得到什麼。比如說:

```rust
macro_rules! might_print {
    (THis is strange input 하하はは哈哈 but it still works) => {
        println!("You guessed the secret message!")
    };
    () => {
        println!("You didn't guess it");
    };
}

fn main() {
    might_print!(THis is strange input 하하はは哈哈 but it still works);
    might_print!();
}
```

所以這個奇怪的宏只響應兩件事。`()`和`(THis is strange input 하하はは哈哈 but it still works)`. 沒有其他的東西。它打印的是:

```text
You guessed the secret message!
You didn't guess it
```

所以宏不完全是Rust語法。但是宏也可以理解你給它的不同類型的輸入。拿這個例子來說。

```rust
macro_rules! might_print {
    ($input:expr) => {
        println!("You gave me: {}", $input);
    }
}

fn main() {
    might_print!(6);
}
```

這將打印`You gave me: 6`。`$input:expr`部分很重要。它的意思是 "對於一個表達式，給它起一個變量名$input"。在宏中，變量以`$`開頭。在這個宏中，如果你給它一個表達式，它就會打印出來。我們再來試一試。

```rust
macro_rules! might_print {
    ($input:expr) => {
        println!("You gave me: {:?}", $input); // Now we'll use {:?} because we will give it different kinds of expressions
    }
}

fn main() {
    might_print!(()); // give it a ()
    might_print!(6); // give it a 6
    might_print!(vec![8, 9, 7, 10]); // give it a vec
}
```

這將打印:

```text
You gave me: ()
You gave me: 6
You gave me: [8, 9, 7, 10]
```

另外注意，我們寫了`{:?}`，但它不會檢查`&input`是否實現了`Debug`。它只會寫代碼，並嘗試讓它編譯，如果沒有，那麼它就會給出一個錯誤。

那麼除了`expr`，宏還能看到什麼呢？它們是 `block | expr | ident | item | lifetime | literal  | meta | pat | path | stmt | tt | ty | vis`. 這就是複雜的部分。你可以在[這裡](https://doc.rust-lang.org/beta/reference/macros-by-example.html)看到它們各自的意思，這裡說:

```text
item: an Item
block: a BlockExpression
stmt: a Statement without the trailing semicolon (except for item statements that require semicolons)
pat: a Pattern
expr: an Expression
ty: a Type
ident: an IDENTIFIER_OR_KEYWORD
path: a TypePath style path
tt: a TokenTree (a single token or tokens in matching delimiters (), [], or {})
meta: an Attr, the contents of an attribute
lifetime: a LIFETIME_TOKEN
vis: a possibly empty Visibility qualifier
literal: matches -?LiteralExpression
```

另外有一個很好的網站叫cheats.rs，在[這裡](https://cheats.rs/#macros-attributes)解釋了它們，並且每個都給出了例子。

然而，對於大多數宏，你只會用到 `expr`、`ident` 和 `tt`。`ident` 表示標識符，用於變量或函數名稱。`tt`表示token樹，和任何類型的輸入。讓我們嘗試用這兩個詞創建一個簡單的宏。

```rust
macro_rules! check {
    ($input1:ident, $input2:expr) => {
        println!(
            "Is {:?} equal to {:?}? {:?}",
            $input1,
            $input2,
            $input1 == $input2
        );
    };
}

fn main() {
    let x = 6;
    let my_vec = vec![7, 8, 9];
    check!(x, 6);
    check!(my_vec, vec![7, 8, 9]);
    check!(x, 10);
}
```

所以這將取一個`ident`(像一個變量名)和一個表達式，看看它們是否相同。它的打印結果是

```text
Is 6 equal to 6? true
Is [7, 8, 9] equal to [7, 8, 9]? true
Is 6 equal to 10? false
```

而這裡有一個宏，輸入`tt`，然後把它打印出來。它先用一個叫`stringify!`的宏創建一個字符串。

```rust
macro_rules! print_anything {
    ($input:tt) => {
        let output = stringify!($input);
        println!("{}", output);
    };
}

fn main() {
    print_anything!(ththdoetd);
    print_anything!(87575oehq75onth);
}
```

這個將打印:

```text
ththdoetd
87575oehq75onth
```

但是如果我們給它一些帶有空格、逗號等的東西，它就不會打印。它會認為我們給了它不止一個元素或額外的信息，所以它會感到困惑。

這就是宏開始變得困難的地方。

要一次給宏提供多個元素，我們必須使用不同的語法。不要用`$input`，而是`$($input1),*`。這意味著零或更多(這是 * 的意思)，用逗號分隔。如果你想要一個或多個，請使用 `+` 而不是 `*`。

現在我們的宏看起來是這樣的。

```rust
macro_rules! print_anything {
    ($($input1:tt),*) => {
        let output = stringify!($($input1),*);
        println!("{}", output);
    };
}


fn main() {
    print_anything!(ththdoetd, rcofe);
    print_anything!();
    print_anything!(87575oehq75onth, ntohe, 987987o, 097);
}
```

所以它接受任何用逗號隔開的token樹，並使用 `stringify!` 把它變成一個字符串。然後打印出來。它的打印結果是:

```text
ththdoetd, rcofe

87575oehq75onth, ntohe, 987987o, 097
```

如果我們使用`+`而不是`*`，它會給出一個錯誤，因為有一次我們沒有給它輸入。所以`*`是一個比較安全的選擇。

所以現在我們可以開始看到宏的威力了。在接下來的這個例子中，我們實際上可以創建我們自己的函數:

```rust
macro_rules! make_a_function {
    ($name:ident, $($input:tt),*) => { // First you give it one name for the function, then it checks everything else
        fn $name() {
            let output = stringify!($($input),*); // It makes everything else into a string
            println!("{}", output);
        }
    };
}


fn main() {
    make_a_function!(print_it, 5, 5, 6, I); // We want a function called print_it() that prints everything else we give it
    print_it();
    make_a_function!(say_its_nice, this, is, really, nice); // Same here but we change the function name
    say_its_nice();
}
```

這個打印:

```text
5, 5, 6, I
this, is, really, nice
```


所以現在我們可以開始瞭解其他的宏了。你可以看到，我們已經使用的一些宏非常簡單。這裡是我們用來寫入文件的`write!`的那個:

```rust
macro_rules! write {
    ($dst:expr, $($arg:tt)*) => ($dst.write_fmt($crate::format_args!($($arg)*)))
}
```

要使用它，你就輸入這個:

- 一個表達式(`expr`) 得到變量名`$dst`.
- 之後的一切。如果它寫的是`$arg:tt`，那麼它只會取1個，但是因為它寫的是`$($arg:tt)*`，所以它取0，1，或者任意多個。

然後它取`$dst`，並對它使用了一個叫做`write_fmt`的方法。在這裡面，它使用了另一個叫做`format_args!`的宏，它接受所有的`$($arg)*`，或者我們輸入的所有參數。



現在我們來看一下`todo!`這個宏。當你想讓程序編譯但還沒有寫出你的代碼時，就會用到這個宏。它看起來像這樣:

```rust
macro_rules! todo {
    () => (panic!("not yet implemented"));
    ($($arg:tt)+) => (panic!("not yet implemented: {}", $crate::format_args!($($arg)+)));
}
```

這個有兩個選項:你可以輸入`()`，也可以輸入一些token樹(`tt`)。

- 如果你輸入`()`，它只是`panic!`，並加上一個信息。所以其實你可以直接寫`panic!("not yet implemented")`，而不是`todo!`，這也是一樣的。
- 如果你輸入一些參數，它會嘗試打印它們。你可以看到裡面有同樣的`format_args!`宏，它的工作原理和`println!`一樣。

所以，如果你寫了這個，它也會工作:

```rust
fn not_done() {
    let time = 8;
    let reason = "lack of time";
    todo!("Not done yet because of {}. Check back in {} hours", reason, time);
}

fn main() {
    not_done();
}
```

這將打印:

```text
thread 'main' panicked at 'not yet implemented: Not done yet because of lack of time. Check back in 8 hours', src/main.rs:4:5
```


在一個宏裡面，你甚至可以調用同一個宏。這裡有一個。

```rust
macro_rules! my_macro {
    () => {
        println!("Let's print this.");
    };
    ($input:expr) => {
        my_macro!();
    };
    ($($input:expr),*) => {
        my_macro!();
    }
}

fn main() {
    my_macro!(vec![8, 9, 0]);
    my_macro!(toheteh);
    my_macro!(8, 7, 0, 10);
    my_macro!();
}
```

這個可以取`()`，也可以取一個表達式，也可以取很多表達式。但是不管你放什麼表達式，它都會忽略所有的表達式，只是在`()`上調用`my_macro!`。所以輸出的只是`Let's print this`，四次。

在`dbg!`宏中也可以看到同樣的情況，也是調用自己。

```rust
macro_rules! dbg {
    () => {
        $crate::eprintln!("[{}:{}]", $crate::file!(), $crate::line!()); //$crate means the crate that it's in.
    };
    ($val:expr) => {
        // Use of `match` here is intentional because it affects the lifetimes
        // of temporaries - https://stackoverflow.com/a/48732525/1063961
        match $val {
            tmp => {
                $crate::eprintln!("[{}:{}] {} = {:#?}",
                    $crate::file!(), $crate::line!(), $crate::stringify!($val), &tmp);
                tmp
            }
        }
    };
    // Trailing comma with single argument is ignored
    ($val:expr,) => { $crate::dbg!($val) };
    ($($val:expr),+ $(,)?) => {
        ($($crate::dbg!($val)),+,)
    };
}
```

(`eprintln!`與`println!`相同，只打印到`io::stderr`而不是`io::stdout`。還有`eprint!`不增加一行)。)

所以我們可以自己去試一試。

```rust
fn main() {
    dbg!();
}
```

這與第一分支相匹配，所以它會用`file!`和`line!`宏打印文件名和行名。它打印的是`[src/main.rs:2]`。

我們用這個來試試。

```rust
fn main() {
    dbg!(vec![8, 9, 10]);
}
```

這將匹配下一個分支，因為它是一個表達式。然後它將調用輸入`tmp`並使用這個代碼。` $crate::eprintln!("[{}:{}] {} = {:#?}", $crate::file!(), $crate::line!(), $crate::stringify!($val), &tmp);`. 所以它會用`file!`和`line!`來打印，然後把`$val`做成`String`，用`{:#?}`來漂亮的打印`tmp`。所以對於我們的輸入，它會這樣寫。

```text
[src/main.rs:2] vec![8, 9, 10] = [
    8,
    9,
    10,
]
```

剩下的部分，即使你多加了一個逗號，它也只是自己調用`dbg!`。

正如你所看到的，宏是非常複雜的！通常你只想讓一個宏自動完成一些簡單函數不能很好完成的事情。學習宏的最好方法是看其他宏的例子。沒有多少人能夠快速寫出宏而不出問題。所以不要認為你需要知道宏的一切，才能知道如何在Rust中寫。但如果你讀了其他宏，並稍加修改，你就可以很容易地借用它們的力量。然後你可能會開始適應寫自己的宏。


# 第2部分 - 電腦上的Rust

你看到了，我們幾乎可以使用Playground學習Rust中的任何東西。但如果你到目前為止已經學了這麼多，現在你可能會想要在你的電腦上使用Rust。總有一些事情是你不能用Playground做的，比如使用文件或代碼在多個文件中。其他如輸入和flags也需要在電腦上安裝Rust。但最重要的是，在你的電腦上有了Rust，你可以使用Crate。我們已經瞭解了crate，但在playground中你只能使用最流行的crate。但在你的電腦上，你可以在程序中使用任何crate。

## cargo

`rustc`的意思是Rust編譯器，實際的編譯工作由它完成。一個rust文件的結尾是`.rs`。但大多數人不會寫出類似 `rustc main.rs` 的東西來編譯。他們使用的是名為 `cargo` 的東西，它是 Rust 的主包管理器。

關於這個名字的一個說明: 之所以叫`cargo`，是因為當你把crate放在一起時，你會得到cargo。Crate就是你在船上或卡車上看到的木箱，但你記住，每個Rust項目也叫Crate。那麼當你把它們放在一起時，你就會得到整個cargo。

當你使用cargo來運行一個項目時，你可以看到這一點。讓我們用 `rand` 試試簡單的東西:我們只是在八個字母之間隨機選擇。

```rust
use rand::seq::SliceRandom; // Use this for .choose over slices

fn main() {

    let my_letters = vec!['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];

    let mut rng = rand::thread_rng();
    for _ in 0..6 {
        print!("{} ", my_letters.choose(&mut rng).unwrap());
    }
}
```

這樣就會打印出`b c g h e a`這樣的東西。但我們想先看看`cargo`的作用。要使用 `cargo` 並運行我們的程序，通常我們輸入 `cargo run`。這樣就可以構建我們的程序，併為我們運行它。當它開始編譯的時候，會做這樣的事情:

```text
   Compiling getrandom v0.1.14
   Compiling cfg-if v0.1.10
   Compiling ppv-lite86 v0.2.8
   Compiling rand_core v0.5.1
   Compiling rand_chacha v0.2.2
   Compiling rand v0.7.3
   Compiling rust_book v0.1.0 (C:\Users\mithr\OneDrive\Documents\Rust\rust_book)
    Finished dev [unoptimized + debuginfo] target(s) in 13.13s
     Running `C:\Users\mithr\OneDrive\Documents\Rust\rust_book\target\debug\rust_book.exe`
g f c f h b
```

所以看起來不只是引入了`rand`，還引入了一些其他的crate。這是因為我們的crate需要`rand`，但`rand`也有一些代碼也需要其他crate。所以`cargo`會找到我們需要的所有crate，並把它們放在一起。在我們的案例中，只有7個，但在非常大的項目中，你可能會有200個或更多的crate要引入。

這就是你可以看到Rust的權衡的地方。Rust的速度非常快，因為它提前編譯。它通過查看代碼，看你寫的代碼到底做了什麼。例如，你可能會寫這樣的泛型代碼:

```rust
use std::fmt::Display;

fn print_and_return_thing<T: Display>(input: T) -> T {
    println!("You gave me {} and now I will give it back.", input);
    input
}

fn main() {
    let my_name = print_and_return_thing("Windy");
    let small_number = print_and_return_thing(9.0);
}
```

這個函數可以用任何實現了`Display`的作為參數，所以我們給它一個`&str`，接下來給它一個`f64`，這對我們來說是沒有問題的。但是編譯器不看泛型，因為它不想在運行時做任何事情。它想把一個能運行的程序儘可能快地組裝起來。所以當它看第一部分的`"Windy"`時，它沒有看到`fn print_and_return_thing<T: Display>(input: T) -> T`，它看到的是`fn print_and_return_thing(input: &str) -> &str`這樣的東西。而接下來它看到的是`fn print_and_return_thing(input: f64) -> f64`。所有關於trait的檢查等等都是在編譯時完成的。這就是為什麼泛型需要更長的時間來編譯，因為它需要弄清楚它們，並使之具體化。

還有一點:Rust 2020正在努力處理編譯時間問題，因為這部分需要的時間最長。每一個版本的Rust在編譯時都會快一點，而且還有一些其他的計劃來加快它的速度。但與此同時，以下是你應該知道的:

- `cargo build`會構建你的程序，這樣你就可以運行它了。
- `cargo run`將建立你的程序並運行它。
- `cargo build --release`和`cargo run --release`發佈模式下有同樣的效果。什麼是發佈模式？當你的代碼最終完成後就可以用發佈模式了。Rust會花更多的時間來編譯，但它這樣做是因為它使用了它所知道的一切，來使編譯出的程序運行更快。Release模式實際上比常規模式*快的多*，常規模式被稱為debug模式。那是因為它的編譯速度更快，而且有更多的調試信息。常規的`cargo build`叫做 "debug build"，`cargo build --release`叫做 "release build"。
- `cargo check`是一種檢查代碼的方式。它就像編譯一樣，只不過它不會真正地創建你的程序。這是一個很好的檢查你的代碼的方法，因為它不像`build`或`run`那樣需要很長時間。

對了，命令中的`--release`部分叫做`flag`。這意味著命令中的額外信息。

其他一些你需要知道的事情是:

- `cargo new`. 這樣做是為了創建一個新的Rust項目。`new`之後，寫上項目的名稱，`cargo`將會創建所有你需要的文件和文件夾。
- `cargo clean`. 當你把crate添加到`Cargo.toml`時，電腦會下載所有需要的文件，它們會佔用很多空間。如果你不想再讓它們在你的電腦上，輸入`cargo clean`。

關於編譯器還有一點:只有當你第一次使用`cargo build`或`cargo run`時，它才會花費最多的時間。之後它就會記住，它又會快速編譯。但如果你使用 `cargo clean`，然後運行 `cargo build`，它將不得不再慢慢地編譯一次。


## 接受用戶輸入

一個簡單的方法是用`std::io::stdin`來接受用戶的輸入。這意味著 "標準輸入"，也就是來自鍵盤的輸入。用`stdin()`可以獲得用戶的輸入，但是接下來你就會想用`.read_line()`把它放到`&mut String`中。下面是一個簡單的例子，但它既能工作，也不能工作:

```rust
use std::io;

fn main() {
    println!("Please type something, or x to escape:");
    let mut input_string = String::new();

    while input_string != "x" { // This is the part that doesn't work right
        input_string.clear(); // First clear the String. Otherwise it will keep adding to it
        io::stdin().read_line(&mut input_string).unwrap(); // Get the stdin from the user, and put it in read_string
        println!("You wrote {}", input_string);
    }
    println!("See you later!");
}
```

下面是一個輸出輸出的樣子。

```text
Please type something, or x to escape:
something
You wrote something

Something else
You wrote Something else

x
You wrote x

x
You wrote x

x
You wrote x
```

它接受我們的輸入，然後把它還給我們，它甚至知道我們輸入了`x`。但它並沒有退出程序。唯一的辦法是關閉窗口，或者輸入ctrl和c。讓我們把`println!`中的`{}`改為`{:?}`，以獲得更多的信息(如果你喜歡那個宏，也可以使用`dbg!(&input_string)`)。現在它說

```text
Please type something, or x to escape:
something
You wrote "something\r\n"
Something else
You wrote "Something else\r\n"
x
You wrote "x\r\n"
x
You wrote "x\r\n"
```



這是因為鍵盤輸入其實不只是`something`，而是`something`和`Enter`鍵。有一個簡單的方法可以解決這個問題，叫做`.trim()`，它可以把所有的空白都去掉。順便說一下，[這些字符](https://doc.rust-lang.org/reference/whitespace.html)都是空白字符。

```text
U+0009 (horizontal tab, '\t')
U+000A (line feed, '\n')
U+000B (vertical tab)
U+000C (form feed)
U+000D (carriage return, '\r')
U+0020 (space, ' ')
U+0085 (next line)
U+200E (left-to-right mark)
U+200F (right-to-left mark)
U+2028 (line separator)
U+2029 (paragraph separator)
```

這樣就可以把`x\r\n`變成只剩`x`了。現在它可以工作了:

```rust
use std::io;

fn main() {
    println!("Please type something, or x to escape:");
    let mut input_string = String::new();

    while input_string.trim() != "x" {
        input_string.clear();
        io::stdin().read_line(&mut input_string).unwrap();
        println!("You wrote {}", input_string);
    }
    println!("See you later!");
}
```

現在可以打印了:

```text
Please type something, or x to escape:
something
You wrote something

Something
You wrote Something

x
You wrote x

See you later!
```



還有一種用戶輸入叫`std::env::Args`(env是環境的意思)。`Args`是用戶啟動程序時輸入的內容。其實在一個程序中總是至少有一個`Arg`。我們寫一個程序，只用`std::env::args()`來打印它們，看看它們是什麼。

```rust
fn main() {
    println!("{:?}", std::env::args());
}
```

如果我們寫`cargo run`，那麼它的打印結果是這樣的:

```text
Args { inner: ["target\\debug\\rust_book.exe"] }
```

讓我們給它更多的輸入，看看它的作用。我們輸入 `cargo run but with some extra words` 。 它給我們:

```text
Args { inner: ["target\\debug\\rust_book.exe", "but", "with", "some", "extra", "words"] }
```

有意思。而當我們查看[Args的頁面](https://doc.rust-lang.org/std/env/struct.Args.html)時，我們看到它實現了`IntoIterator`。這意味著我們可以.用所有我們知道的關於迭代器的方法來讀取和改變它。讓我們試試這個:

```rust
use std::env::args;

fn main() {
    let input = args();

    for entry in input {
        println!("You entered: {}", entry);
    }
}
```

現在它說:

```text
You entered: target\debug\rust_book.exe
You entered: but
You entered: with
You entered: some
You entered: extra
You entered: words
```

你可以看到，第一個參數總是程序名，所以你經常會想跳過它，比如這樣:

```rust
use std::env::args;

fn main() {
    let input = args();

    input.skip(1).for_each(|item| {
        println!("You wrote {}, which in capital letters is {}", item, item.to_uppercase());
    })
}
```

這將打印:

```text
You wrote but, which in capital letters is BUT
You wrote with, which in capital letters is WITH
You wrote some, which in capital letters is SOME
You wrote extra, which in capital letters is EXTRA
You wrote words, which in capital letters is WORDS
```

`Args`的一個常見用途是用於用戶設置。你可以確保用戶寫出你需要的輸入，只有在正確的情況下才運行程序。這裡有一個小程序，可以讓字母變大(大寫)或變小(小寫)。

```rust
use std::env::args;

enum Letters {
    Capitalize,
    Lowercase,
    Nothing,
}

fn main() {
    let mut changes = Letters::Nothing;
    let input = args().collect::<Vec<_>>();

    if input.len() > 2 {
        match input[1].as_str() {
            "capital" => changes = Letters::Capitalize,
            "lowercase" => changes = Letters::Lowercase,
            _ => {}
        }
    }

    for word in input.iter().skip(2) {
      match changes {
        Letters::Capitalize => println!("{}", word.to_uppercase()),
        Letters::Lowercase => println!("{}", word.to_lowercase()),
        _ => println!("{}", word)
      }
    }

}
```

下面是它給出的一些例子。

輸入: `cargo run please make capitals`:

```text
make capitals
```

輸入:`cargo run capital`:

```text
// Nothing here...
```

輸入:`cargo run capital I think I understand now`:

```text
I
THINK
I
UNDERSTAND
NOW
```

輸入:`cargo run lowercase Does this work too?`

```text
does
this
work
too?
```



除了用戶給出的 `Args`，在 `std::env::args()` 中可用，還有系統變量`Vars`。這些都是用戶沒有輸入的程序的基本設置。你可以用`std::env::vars()`把它們都看成一個`(String, String)`。這個有非常多，比如說:

```rust
fn main() {
    for item in std::env::vars() {
        println!("{:?}", item);
    }
}
```

運行這段代碼，就能顯示出你的用戶會話的所有信息。它將顯示這樣的信息:

```text
("CARGO", "/playground/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo")
("CARGO_HOME", "/playground/.cargo")
("CARGO_MANIFEST_DIR", "/playground")
("CARGO_PKG_AUTHORS", "The Rust Playground")
("CARGO_PKG_DESCRIPTION", "")
("CARGO_PKG_HOMEPAGE", "")
("CARGO_PKG_NAME", "playground")
("CARGO_PKG_REPOSITORY", "")
("CARGO_PKG_VERSION", "0.0.1")
("CARGO_PKG_VERSION_MAJOR", "0")
("CARGO_PKG_VERSION_MINOR", "0")
("CARGO_PKG_VERSION_PATCH", "1")
("CARGO_PKG_VERSION_PRE", "")
("DEBIAN_FRONTEND", "noninteractive")
("HOME", "/playground")
("HOSTNAME", "f94c15b8134b")
("LD_LIBRARY_PATH", "/playground/target/debug/build/backtrace-sys-3ec4c973f371c302/out:/playground/target/debug/build/libsqlite3-sys-fbddfbb9b241dacb/out:/playground/target/debug/build/ring-cadba5e583648abb/out:/playground/target/debug/deps:/playground/target/debug:/playground/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib:/playground/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib")
("PATH", "/playground/.cargo/bin:/playground/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")
("PLAYGROUND_EDITION", "2018")
("PLAYGROUND_TIMEOUT", "10")
("PWD", "/playground")
("RUSTUP_HOME", "/playground/.rustup")
("RUSTUP_TOOLCHAIN", "stable-x86_64-unknown-linux-gnu")
("RUST_RECURSION_COUNT", "1")
("SHLVL", "1")
("SSL_CERT_DIR", "/usr/lib/ssl/certs")
("SSL_CERT_FILE", "/usr/lib/ssl/certs/ca-certificates.crt")
("USER", "playground")
("_", "/usr/bin/timeout")
```

所以如果你需要這些信息，`Vars`就是你想要的。

獲得單個`Var'的最簡單方法是使用`env!`宏。你只要給它變量的名字，它就會給你一個`&str'的值。如果變量拼寫錯誤或不存在，它就不起作用，所以如果你不確定，就用`option_env!`代替。如果我們在Playground上寫這個:

```rust
fn main() {
    println!("{}", env!("USER"));
    println!("{}", option_env!("ROOT").unwrap_or("Can't find ROOT"));
    println!("{}", option_env!("CARGO").unwrap_or("Can't find CARGO"));
}
```

然後我們得到輸出:

```text
playground
Can't find ROOT
/playground/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo
```

所以`option_env!`永遠是比較安全的宏。如果你真的想讓程序在找不到環境變量時崩潰，那麼`env!`會更好。



## 使用文件

現在我們在電腦上使用Rust，我們可以開始處理文件了。你會注意到，現在我們會開始在代碼中越來越多的看到`Result`。這是因為一旦你開始處理文件和類似的事情，很多事情都會出錯。一個文件可能不在那裡，或者計算機無法讀取它。

你可能還記得，如果你想使用`?`運算符，調用它的函數必須返回一個`Result`。如果你記不住錯誤類型，你可以什麼都不給它，讓編譯器告訴你。讓我們用一個試圖用`.parse()`創建一個數字的函數來試試。

```rust
// ⚠️
fn give_number(input: &str) -> Result<i32, ()> {
    input.parse::<i32>()
}

fn main() {
    println!("{:?}", give_number("88"));
    println!("{:?}", give_number("5"));
}
```

編譯器告訴我們到底該怎麼做。

```text
error[E0308]: mismatched types
 --> src\main.rs:4:5
  |
3 | fn give_number(input: &str) -> Result<i32, ()> {
  |                                --------------- expected `std::result::Result<i32, ()>` because of return type
4 |     input.parse::<i32>()
  |     ^^^^^^^^^^^^^^^^^^^^ expected `()`, found struct `std::num::ParseIntError`
  |
  = note: expected enum `std::result::Result<_, ()>`
             found enum `std::result::Result<_, std::num::ParseIntError>`
```

很好! 所以我們只要把返回值改成編譯器說的就可以了:

```rust
use std::num::ParseIntError;

fn give_number(input: &str) -> Result<i32, ParseIntError> {
    input.parse::<i32>()
}

fn main() {
    println!("{:?}", give_number("88"));
    println!("{:?}", give_number("5"));
}
```

現在程序可以運行了!

```text
Ok(88)
Ok(5)
```

所以現在我們想用`?`，如果能用就直接給我們數值，如果不能用就給錯誤。但是如何在`fn main()`中做到這一點呢？如果我們嘗試在main中使用`?`，那就不行了。

```rust
// ⚠️
use std::num::ParseIntError;

fn give_number(input: &str) -> Result<i32, ParseIntError> {
    input.parse::<i32>()
}

fn main() {
    println!("{:?}", give_number("88")?);
    println!("{:?}", give_number("5")?);
}
```

它說:

```text
error[E0277]: the `?` operator can only be used in a function that returns `Result` or `Option` (or another type that implements `std::ops::Try`)
  --> src\main.rs:8:22
   |
7  | / fn main() {
8  | |     println!("{:?}", give_number("88")?);
   | |                      ^^^^^^^^^^^^^^^^^^ cannot use the `?` operator in a function that returns `()`
9  | |     println!("{:?}", give_number("5")?);
10 | | }
   | |_- this function should return `Result` or `Option` to accept `?`
```

但實際上`main()`可以返回一個`Result`，就像其他函數一樣。如果我們的函數能工作，我們不想返回任何東西(main()並沒有給其他任何東西)。而如果它不工作，我們將錯誤返回。所以我們可以這樣寫:

```rust
use std::num::ParseIntError;

fn give_number(input: &str) -> Result<i32, ParseIntError> {
    input.parse::<i32>()
}

fn main() -> Result<(), ParseIntError> {
    println!("{:?}", give_number("88")?);
    println!("{:?}", give_number("5")?);
    Ok(())
}
```

不要忘了最後的`Ok(())`:這在Rust中是很常見的，它的意思是`Ok`，裡面是`()`，也就是我們的返回值。現在它打印出來了:

```text
88
5
```


只用`.parse()`的時候不是很有用，但是用文件就很有用。這是因為`?`也為我們改變了錯誤類型。下面是用簡單英語寫的[?運算符頁面](https://doc.rust-lang.org/std/macro.try.html):

```text
If you get an `Err`, it will get the inner error. Then `?` does a conversion using `From`. With that it can change specialized errors to more general ones. The error it gets is then returned.
```

另外，Rust在使用`File`s和類似的東西時，有一個方便的`Result`類型。它叫做`std::io::Result`，當你在使用`?`對文件進行打開和操作時，通常在`main()`中看到的就是這個。這其實是一個類型別名。它的樣子是這樣的:

```text
type Result<T> = Result<T, Error>;
```

所以這是一個`Result<T, Error>`，但我們只需要寫出`Result<T>`部分。

現在讓我們第一次嘗試使用文件。`std::fs`是處理文件的方法所在，有了`std::io::Write`，你就可以寫。有了它，我們就可以用`.write_all()`來寫進文件。

```rust
use std::fs;
use std::io::Write;

fn main() -> std::io::Result<()> {
    let mut file = fs::File::create("myfilename.txt")?; // Create a file with this name.
                                                        // CAREFUL! If you have a file with this name already,
                                                        // it will delete everything in it.
    file.write_all(b"Let's put this in the file")?;     // Don't forget the b in front of ". That's because files take bytes.
    Ok(())
}
```

然後如果你打開新文件`myfilename.txt`，會看到內容`Let's put this in the file`。

不過我們不需要寫兩行，因為我們有`?`操作符。如果有效，它就會傳遞我們想要的結果，有點像在迭代器上很多方法一樣。這時候`?`就變得非常方便了。

```rust
use std::fs;
use std::io::Write;

fn main() -> std::io::Result<()> {
    fs::File::create("myfilename.txt")?.write_all(b"Let's put this in the file")?;
    Ok(())
}
```

所以這是說 "請嘗試創建一個文件，然後檢查是否成功。如果成功了，那就使用`.write_all()`，然後檢查是否成功。"

而事實上，也有一個函數可以同時做這兩件事。它叫做`std::fs::write`。在它裡面，你給它你想要的文件名，以及你想放在裡面的內容。再次強調，要小心! 如果該文件已經存在，它將刪除其中的所有內容。另外，它允許你寫一個`&str`，前面不寫`b`，因為這個:

```rust
pub fn write<P: AsRef<Path>, C: AsRef<[u8]>>(path: P, contents: C) -> Result<()>
```

`AsRef<[u8]>`就是為什麼你可以給它任何一個。

很簡單的:

```rust
use std::fs;

fn main() -> std::io::Result<()> {
    fs::write("calvin_with_dad.txt", 
"Calvin: Dad, how come old photographs are always black and white? Didn't they have color film back then?
Dad: Sure they did. In fact, those photographs *are* in color. It's just the *world* was black and white then.
Calvin: Really?
Dad: Yep. The world didn't turn color until sometimes in the 1930s...")?;

    Ok(())
}
```

所以這就是我們要用的文件。這是一個名叫Calvin的漫畫人物和他爸爸的對話，他爸爸對他的問題並不認真。有了這個，每次我們都可以創建一個文件來使用。



打開一個文件和創建一個文件一樣簡單。你只要用`open()`代替`create()`就可以了。之後(如果它找到了你的文件)，你就可以做`read_to_string()`這樣的事情。要做到這一點，你可以創建一個可變的 `String`，然後把文件讀到那裡。它看起來像這樣:

```rust
use std::fs;
use std::fs::File;
use std::io::Read; // this is to use the function .read_to_string()

fn main() -> std::io::Result<()> {
     fs::write("calvin_with_dad.txt", 
"Calvin: Dad, how come old photographs are always black and white? Didn't they have color film back then?
Dad: Sure they did. In fact, those photographs *are* in color. It's just the *world* was black and white then.
Calvin: Really?
Dad: Yep. The world didn't turn color until sometimes in the 1930s...")?;


    let mut calvin_file = File::open("calvin_with_dad.txt")?; // Open the file we just made
    let mut calvin_string = String::new(); // This String will hold it
    calvin_file.read_to_string(&mut calvin_string)?; // Read the file into it

    calvin_string.split_whitespace().for_each(|word| print!("{} ", word.to_uppercase())); // Do things with the String now

    Ok(())
}
```

會打印:

```rust
CALVIN: DAD, HOW COME OLD PHOTOGRAPHS ARE ALWAYS BLACK AND WHITE? DIDN'T THEY HAVE COLOR FILM BACK THEN? DAD: SURE THEY DID. IN 
FACT, THOSE PHOTOGRAPHS *ARE* IN COLOR. IT'S JUST THE *WORLD* WAS BLACK AND WHITE THEN. CALVIN: REALLY? DAD: YEP. THE WORLD DIDN'T TURN COLOR UNTIL SOMETIMES IN THE 1930S...
```

好吧，如果我們想創建一個文件，但如果已經有另一個同名的文件就不做了怎麼辦？也許你不想為了創建一個新的文件而刪除已經存在的其他文件。要做到這一點，有一個結構叫`OpenOptions`。其實，我們一直在用`OpenOptions`，卻不知道。看看`File::open`的源碼吧。

```rust
pub fn open<P: AsRef<Path>>(path: P) -> io::Result<File> {
        OpenOptions::new().read(true).open(path.as_ref())
    }
```

有意思，這好像是我們學過的建造者模式。`File::create`也是如此。

```rust
pub fn create<P: AsRef<Path>>(path: P) -> io::Result<File> {
        OpenOptions::new().write(true).create(true).truncate(true).open(path.as_ref())
    }
```

如果你去[OpenOptions的頁面](https://doc.rust-lang.org/std/fs/struct.OpenOptions.html)，你可以看到所有可以選擇的方法。大多數採取`bool`。


- `append()`: 意思是 "添加到已經存在的內容中，而不是刪除"。
- `create()`: 這讓 `OpenOptions` 創建一個文件。
- `create_new()`: 意思是隻有在文件不存在的情況下才會創建文件。
- `read()`: 如果你想讓它讀取文件，就把這個設置為 `true`。
- `truncate()`: 如果你想在打開文件時把文件內容剪為0(刪除內容)，就把這個設置為true。
- `write()`: 這可以讓它寫入一個文件。

然後在最後你用`.open()`加上文件名，就會得到一個`Result`。我們來看一個例子。

```rust
// ⚠️
use std::fs;
use std::fs::OpenOptions;

fn main() -> std::io::Result<()> {
     fs::write("calvin_with_dad.txt", 
"Calvin: Dad, how come old photographs are always black and white? Didn't they have color film back then?
Dad: Sure they did. In fact, those photographs *are* in color. It's just the *world* was black and white then.
Calvin: Really?
Dad: Yep. The world didn't turn color until sometimes in the 1930s...")?;

    let calvin_file = OpenOptions::new().write(true).create_new(true).open("calvin_with_dad.txt")?;

    Ok(())
}
```

首先我們用`new`做了一個`OpenOptions`(總是以`new`開頭)。然後我們給它的能力是`write`。之後我們把`create_new()`設置為`true`，然後試著打開我們做的文件。打不開，這是我們想要的。

```text
Error: Os { code: 80, kind: AlreadyExists, message: "The file exists." }
```

讓我們嘗試使用`.append()`，這樣我們就可以向一個文件寫入。為了寫入文件，我們可以使用 `.write_all()`，這是一個嘗試寫入你給它的一切內容的方法。

另外，我們將使用 `write!` 宏來做同樣的事情。你會記得這個宏，我們在為結構體做`impl Display`的時候用到過。這次我們是在文件上使用它，而不是在緩衝區上。

```rust
use std::fs;
use std::fs::OpenOptions;
use std::io::Write;

fn main() -> std::io::Result<()> {
    fs::write("calvin_with_dad.txt", 
"Calvin: Dad, how come old photographs are always black and white? Didn't they have color film back then?
Dad: Sure they did. In fact, those photographs *are* in color. It's just the *world* was black and white then.
Calvin: Really?
Dad: Yep. The world didn't turn color until sometimes in the 1930s...")?;

    let mut calvin_file = OpenOptions::new()
        .append(true) // Now we can write without deleting it
        .read(true)
        .open("calvin_with_dad.txt")?;
    calvin_file.write_all(b"And it was a pretty grainy color for a while too.\n")?;
    write!(&mut calvin_file, "That's really weird.\n")?;
    write!(&mut calvin_file, "Well, truth is stranger than fiction.")?;

    println!("{}", fs::read_to_string("calvin_with_dad.txt")?);

    Ok(())
}
```

這個打印:

```text
Calvin: Dad, how come old photographs are always black and white? Didn't they have color film back then?
Dad: Sure they did. In fact, those photographs *are* in color. It's just the *world* was black and white then.
Calvin: Really?
Dad: Yep. The world didn't turn color until sometimes in the 1930s...And it was a pretty grainy color for a while too.
That's really weird.
Well, truth is stranger than fiction.
```

## cargo文檔

你可能已經注意到，Rust文檔看起來總是幾乎一樣。在左邊你可以看到`struct`和`trait`，代碼例子在右邊等等。這是因為你只要輸入`cargo doc`就可以自動創建文檔。

即使是創建一個什麼都不做的項目，也可以幫助你瞭解Rust中的特性。例如，這裡有兩個幾乎什麼都不做的結構體，以及一個也什麼都不做的`fn main()`。

```rust
struct DoesNothing {}
struct PrintThing {}

impl PrintThing {
    fn prints_something() {
        println!("I am printing something");
    }
}

fn main() {}
```


但如果你輸入`cargo doc --open`，你可以看到比你想象中更多的信息。首先它給你顯示的是這樣的:

```text
Crate rust_book

Structs
DoesNothing
PrintThing

Functions
main
```

但是如果你點擊其中的一個結構，會讓你看到很多你沒有想到的trait。

```text
Struct rust_book::DoesNothing
[+] Show declaration
Auto Trait Implementations
impl RefUnwindSafe for DoesNothing
impl Send for DoesNothing
impl Sync for DoesNothing
impl Unpin for DoesNothing
impl UnwindSafe for DoesNothing
Blanket Implementations
impl<T> Any for T
where
    T: 'static + ?Sized,
[src]
[+]
impl<T> Borrow<T> for T
where
    T: ?Sized,
[src]
[+]
impl<T> BorrowMut<T> for T
where
    T: ?Sized,
[src]
[+]
impl<T> From<T> for T
[src]
[+]
impl<T, U> Into<U> for T
where
    U: From<T>,
[src]
[+]
impl<T, U> TryFrom<U> for T
where
    U: Into<T>,
[src]
[+]
impl<T, U> TryInto<U> for T
where
    U: TryFrom<T>,
```

這是因為Rust自動為每個類型實現的所有trait。

那麼如果我們添加一些文檔註釋，當你輸入`cargo doc`的時候就可以看到。

```rust
/// This is a struct that does nothing
struct DoesNothing {}
/// This struct only has one method.
struct PrintThing {}
/// It just prints the same message.
impl PrintThing {
    fn prints_something() {
        println!("I am printing something");
    }
}

fn main() {}
```


現在會打印:

```text
Crate rust_book
Structs
DoesNothing This is a struct that does nothing
PrintThing  This struct only has one method.
Functions
main
```

當你使用很多別人的crate時，`cargo doc`是非常好的。因為這些crate都在不同的網站上，可能需要一些時間來搜索所有的crate。但如果你使用`cargo doc`，你就會把它們都放在你硬盤的同一個地方。

## 結束了嗎？

簡單英語學Rust就這樣結束了。但是我還在這裡，如果你有什麼問題可以告訴我。歡迎[在Twitter上聯繫我](https://twitter.com/mithridates)或者添加一個pull request、issue等。如果有些地方不容易理解，你也可以告訴我。簡單英語學Rust需要非常容易理解，所以請告訴我英語太難的地方。當然，Rust本身也可能是很難理解的，但我們至少可以確保英語是容易的。