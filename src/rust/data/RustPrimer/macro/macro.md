# Macro

## 簡介

學過 C 語言的人都知道 `#define` 用來定義宏(macro)，而且大學很多老師都告訴你儘量少用宏，因為 C 裡面的宏是一個很危險的東西-宏僅僅是簡單的文本替換，完全不管語法，類型，非常容易出錯。聽說過或用過 Lisp 的人覺得宏極其強大，就連美國最大的創業孵化器公司創始人 Paul Gram 也極力鼓吹 Lisp 的宏是有多麼強大。那麼宏究竟是什麼樣的東西呢？這一章通過 Rust 的宏系統帶你揭開宏(Macro)的神秘面紗。

Rust 中的宏幾乎無處不在，其實你寫的第一個 Rust 程序裡面就已經用到了宏，對，就是那個有名的 hello-world。`println!("Hello, world!")` 這句看起來很像函數調用，但是在"函數名"後面加上了感嘆號，這個是專門用來區分普通函數調用和宏調用的。另外從形式上看，與函數調用的另一個區別是參數可以用圓括號(`()`)、花括號(`{}`)、方括號(`[]`)中的任意一種括起來，比如這行也可以寫成 `println!["Hello, world!"]` 或 `println!{"Hello, world!"}`，不過對於 Rust 內置的宏都有約定俗成的括號，比如 `vec!` 用方括號，`assert_eq!` 用圓括號。

既然宏看起來與普通函數非常像，那麼使用宏有什麼好處呢？是否可以用函數取代宏呢？答案顯然是否定的，首先 Rust 的函數不能接受任意多個參數，其次函數是不能操作語法單元的，即把語法元素作為參數進行操作，從而生成代碼，例如 `mod`, `crate` 這些是 Rust 內置的關鍵詞，是不可能直接用函數去操作這些的，而宏就有這個能力。

相比函數，宏是用來生成代碼的，在調用宏的地方，編譯器會先將宏進行展開，生成代碼，然後再編譯展開後的代碼。

宏定義格式是： `macro_rules! macro_name { macro_body }`，其中 `macro_body` 與模式匹配很像， `pattern => do_something` ，所以 Rust 的宏又稱為 Macro by example (基於例子的宏)。其中 `pattern` 和 `do_something` 都是用配對的括號括起來的，括號可以是圓括號、方括號、花括號中的任意一種。匹配可以有多個分支，每個分支以分號結束。

還是先來個簡單的例子說明

```rust
macro_rules! create_function {
    ($func_name:ident) => (
        fn $func_name() {
            println!("function {:?} is called", stringify!($func_name))
        }
    )
}

fn main() {
    create_function!(foo);
	foo();
}

```

上面這個簡單的例子是用來創建函數，生成的函數可以像普通函數一樣調用，這個函數可以打印自己的名字。編譯器在看到 `create_function!(foo)` 時會從前面去找一個叫 `create_function` 的宏定義，找到之後，就會嘗試將參數 `foo` 代入 `macro_body`，對每一條模式按順序進行匹配，只要有一個匹配上，就會將 `=>` 左邊定義的參數代入右邊進行替換，如果替換不成功，編譯器就會報錯而不會往下繼續匹配，替換成功就會將右邊替換後的代碼放在宏調用的地方。這個例子中只有一個模式，即 `$func_name:ident`，表示匹配一個標識符，如果匹配上就把這個標識符賦值給 `$func_name`，宏定義裡面的變量都是以 `$` 開頭的，相應的類型也是以冒號分隔說明，這裡 `ident` 是變量 `$func_name` 的類型，表示這個變量是一個 `identifier`，這是語法層面的類型(designator)，而普通的類型如 `char, &str, i32, f64` 這些是語義層面的類型。在 `main` 函數中傳給宏調用 `create_function` 的參數 `foo` 正好是一個標識符(`ident`)，所以能匹配上，`$func_name` 就等於 `foo`，然後把 `$func_name` 的值代入 `=>` 右邊，成了下面這樣的

```rust
fn foo() {
    println!("function {:?} is called", stringify!(foo))
}
```

所以最後編譯器編譯的實際代碼是

```rust
fn main() {
    fn foo() {
	    println!("function {:?} is called", stringify!(foo))
	}
	foo();
}
```

上面定義了 `create_function` 這個宏之後，就可以隨便用來生成函數了，比如調用 `create_function!(bar)` 就得到了一個名為 `bar` 的函數

通過上面這個例子，大家對宏應該有一個大致的瞭解了。下面就具體談談宏的各個組成部分。



## 宏的結構

### 宏名

宏名字的解析與函數略微有些不同，宏的定義必須出現在宏調用之前，即與 C 裡面的函數類似--函數定義或聲明必須在函數調用之前，只不過 Rust 宏沒有單純的聲明，所以宏在調用之前需要先定義，而 Rust 函數則可以定義在函數調用後面。宏調用與宏定義順序相關性包括從其它模塊中引入的宏，所以引入其它模塊中的宏時要特別小心，這個稍後會詳細討論。

下面這個例子宏定義在宏調用後面，編譯器會報錯說找不到宏定義，而函數則沒問題

```rust
fn main() {
    let a = 42;
    foo(a);
	bar!(a);
}

fn foo(x: i32) {
	println!("The argument you passed to function is {}", x);
}

macro_rules! bar {
	($x:ident) => { println!("The argument you passed to macro is {}", $x); }
}
```

上面例子中把宏定義挪到 `main` 函數之前或者 `main` 函數里面 `bar!(a)` 調用上面，就可以正常編譯運行。

宏調用雖然與函數調用很像，但是宏的名字與函數名字是處於不同命名空間的，之所以提出來是因為在有些編程語言裡面宏和函數是在同一個命名空間之下的。看過下面的例子就會明白

```rust
fn foo(x: i32) -> i32 {
    x * x
}

macro_rules! foo {
    ($x:ident) => { println!("{:?}", $x); }
}
fn main() {
    let a = 5;
	foo!(a);
    println!("{}", foo(a));
}
```

### 指示符(designator)

宏裡面的變量都是以 `$` 開頭的，其餘的都是按字面去匹配，以 `$` 開頭的變量都是用來表示語法(syntactic)元素，為了限定匹配什麼類型的語法元素，需要用指示符(designator)加以限定，就跟普通的變量綁定一樣用冒號將變量和類型分開，當前宏支持以下幾種指示符：

* ident: 標識符，用來表示函數或變量名
* expr: 表達式
* block: 代碼塊，用花括號包起來的多個語句
* pat: 模式，普通模式匹配（非宏本身的模式）中的模式，例如 `Some(t)`, `(3, 'a', _)`
* path: 路徑，注意這裡不是操作系統中的文件路徑，而是用雙冒號分隔的限定名(qualified name)，如 `std::cmp::PartialOrd`
* tt: 單個語法樹
* ty: 類型，語義層面的類型，如 `i32`, `char`
* item: 條目，
* meta: 元條目
* stmt: 單條語句，如 `let a = 42;`

加上這些類型限定後，宏在進行匹配時才不會漫無目的的亂匹配，例如在要求標識符的地方是不允許出現表達式的，否則編譯器就會報錯。而 C/C++ 語言中的宏則僅僅是簡單的文本替換，沒有語法層面的考慮，所以非常容易出錯。

### 重複(repetition)

宏相比函數一個很大的不同是宏可以接受任意多個參數，例如 `println!` 和 `vec!`。這是怎麼做到的呢？

沒錯，就是重複(repetition)。模式的重複不是通過程序裡面的循環(for/while)去控制的，而是指定了兩個特殊符號 `+` 和 `*`，類似於正則表達式，因為正則表達式也是不關心具體匹配對象是一個人名還是一個國家名。與正則表達式一樣， `+` 表示一次或多次（至少一次），而 `*` 表示零次或多次。重複的模式需要用括號括起來，外面再加上 `$`，例如 `$(...)*`, `$(...)+`。需要說明的是這裡的括號和宏裡面其它地方一樣都可以是三種括號中的任意一種，因為括號在這裡僅僅是用來標記一個模式的開始和結束，大部分情況重複的模式是用逗號或分號分隔的，所以你會經常看到 `$(...),*`, `$(...);*`, `$(...),+`, `$(...);+` 這樣的用來表示重複。

還是來看一個例子

```rust
macro_rules! vector {
	($($x:expr),*) => {
		{
			let mut temp_vec = Vec::new();
			$(temp_vec.push($x);)*
			temp_vec
		}
	};
}

fn main() {
	let a = vector![1, 2, 4, 8];
	println!("{:?}", a);
}
```

這個例子初看起來比較複雜，我們來分析一下。

首先看 `=>` 左邊，最外層是圓括號，前面說過這個括號可以是圓括號、方括號、花括號中的任意一種，只要是配對的就行。然後再看括號裡面 `$(...),*` 正是剛才提到的重複模式，重複的模式是用逗號分隔的，重複的內容是 `$x:expr`，即可以匹配零次或多次用逗號分隔的表達式，例如 `vector![]` 和 `vector![3, x*x, s-t]` 都可以匹配成功。

接著看 `=>` 右邊，最外層也是一個括號，末尾是分號表示這個分支結束。裡面是花括號包起來的代碼塊，最後一行沒有分號，說明這個 macro 的值是一個表達式，`temp_vec` 作為表達式的值返回。第一條語句就是普通的用 `Vec::new()` 生成一個空 vector，然後綁定到可變的變量 `temp_vec` 上面，第二句比較特殊，跟 `=>` 左邊差不多，也是用來表示重複的模式，而且是跟左邊是一一對應的，即左邊匹配到一個表達式(`expr`)，這裡就會將匹配到的表達式用在 `temp_vec.push($x);` 裡面，所以 `vector![3, x*x, s-t]` 調用就會展開成

```rust
{
	let mut temp_vec = Vec::new();
	temp_vec.push(3);
	temp_vec.push(x*x);
	temp_vec.push(s-t);
	temp_vec
}
```

看著很複雜的宏，細細分析下來是不是很簡單，不要被這些符號干擾了

### 遞歸(recursion)

除了重複之外，宏還支持遞歸，即在宏定義時調用其自身，類似於遞歸函數。因為rust的宏本身是一種模式匹配，而模式匹配裡面包含遞歸則是函數式語言裡面最常見的寫法了，有函數式編程經驗的對這個應該很熟悉。下面看一個簡單的例子：

```rust
macro_rules! find_min {
    ($x:expr) => ($x);
    ($x:expr, $($y:expr),+) => (
        std::cmp::min($x, find_min!($($y),+))
    )
}

fn main() {
    println!("{}", find_min!(1u32));
    println!("{}", find_min!(1u32 + 2 , 2u32));
    println!("{}", find_min!(5u32, 2u32 * 3, 4u32));
}
```

因為模式匹配是按分支順序匹配的，一旦匹配成功就不會再往下進行匹配（即使後面也能匹配上），所以模式匹配中的遞歸都是在第一個分支裡寫最簡單情況，越往下包含的情況越多。這裡也是一樣，第一個分支 `($x:expr)` 只匹配一個表達式，第二個分支匹配兩個或兩個以上表達式，注意加號表示匹配一個或多個，然後裡面是用標準庫中的 `min` 比較兩個數的大小，第一個表達式和剩餘表達式中最小的一個，其中剩餘表達式中最小的一個是遞歸調用 `find_min!` 宏，與遞歸函數一樣，每次遞歸都是從上往下匹配，只到匹配到基本情況。我們來寫寫 `find_min!(5u32, 2u32 * 3, 4u32)` 宏展開過程

1. `std::cmp::min(5u32, find_min!(2u32 * 3, 4u32))`
2. `std::cmp::min(5u32, std::cmp::min(2u32 * 3, find_min!(4u32)))`
3. `std::cmp::min(5u32, std::cmp::min(2u32 * 3, 4u32))`

分析起來與遞歸函數一樣，也比較簡單。

### 衛生(hygienic Macro)

有了重複和遞歸，組合起來就是一個很強大的武器，可以解決很多普通函數無法抽象的東西。但是這裡面會有一個安全問題，也是 C/C++ 裡面宏最容易出錯的地方，不過 Rust 像 Scheme 一樣引入了衛生(Hygiene)宏，有效地避免了這類問題的發生。

C/C++ 裡面的宏僅僅是簡單的文本替換，下面的 C 經過宏預處理後，宏外面定義的變量 `a` 就會與裡面定義的混在一起，從而按作用域 shadow 外層的定義，這會導致一些非常詭異的問題，不去看宏具體定義仔細分析的話，很難發現這類 bug。這樣的宏是不衛生的，不過也有些奇葩的 Hacker 覺得這是一個非常棒的特性，例如 CommanLisp 語言裡面的宏本身很強大，但不是衛生的，而某些 Hacker 還以這個為傲，搞一些奇技淫巧故意製造出這樣的 shadow 行為實現一些很 fancy 的效果。這裡不做過多評論，對 C 比較熟悉的同學可以分析一下下面這段代碼運行結果與第一印象是否一樣。

```c
#define INCI(i) {int a=0; ++i;}
int main(void)
{
    int a = 0, b = 0;
    INCI(a);
    INCI(b);
    printf("a is now %d, b is now %d\n", a, b);
    return 0;
}
```

衛生宏最開始是由 Scheme 語言引入的，後來好多語言基本都採用衛生宏，即編譯器或運行時會保證宏裡面定義的變量或函數不會與外面的衝突，在宏裡面以普通方式定義的變量作用域不會跑到宏外面。

```rust
macro_rules! foo {
    () => (let x = 3);
}

macro_rules! bar {
    ($v:ident) => (let $v = 3);
}

fn main() {
    foo!();
    println!("{}", x);
	bar!(a);
	println!("{}", a);
}
```

上面代碼中宏 `foo!` 裡面的變量 `x` 是按普通方式定義的，所以其作用域限定在宏裡面，宏調用結束後再引用 `x` 編譯器就會報錯。要想讓宏裡面定義的變量在宏調用結束後仍然有效，需要按 `bar!` 裡面那樣定義。不過對於 `item` 規則就有些不同，例如函數在宏裡面以普通方式定義後，宏調用之後，這個函數依然可用，下面代碼就可以正常編譯。

```rust
macro_rules! foo {
    () => (fn x() { });
}

fn main() {
    foo!();
    x();
}
```

## 導入導出(import/export)

前面提到宏名是按順序解析的，所以從其它模塊中導入宏時與導入函數、trait 的方式不太一樣，宏導入導出用 `#[macro_use]` 和 `#[macro_export]`。父模塊中定義的宏對其下的子模塊是可見的，要想子模塊中定義的宏在其後面的父模塊中可用，需要使用 `#[macro_use]`。

```rust
macro_rules! m1 { () => (()) }

// 宏 m1 在這裡可用

mod foo {
    // 宏 m1 在這裡可用

    #[macro_export]
    macro_rules! m2 { () => (()) }

    // 宏 m1 和 m2 在這裡可用
}

// 宏 m1 在這裡可用
#[macro_export]
macro_rules! m3 { () => (()) }

// 宏 m1 和 m3 在這裡可用

#[macro_use]
mod bar {
    // 宏 m1 和 m3 在這裡可用

    macro_rules! m4 { () => (()) }

    // 宏 m1, m3, m4 在這裡均可用
}

// 宏 m1, m3, m4 均可用
```

crate 之間只有被標為 `#[macro_export]` 的宏可以被其它 crate 導入。假設上面例子是 `foo` crate 中的部分代碼，則只有 `m2` 和 `m3` 可以被其它 crate 導入。導入方式是在 `extern crate foo;` 前面加上 `#[macro_use]`

```rust
#[macro_use]
extern crate foo;
// foo 中 m2, m3 都被導入
```

如果只想導入 `foo` crate 中某個宏，比如 `m3`，就給 `#[macro_use]` 加上參數
```rust
#[macro_use(m3)]
extern crate foo;
// foo 中只有 m3 被導入
```

## 調試

雖然宏功能很強大，但是調試起來要比普通代碼困難，因為編譯器默認情況下給出的提示都是對宏展開之後的，而不是你寫的原程序，要想在編譯器錯誤與原程序之間建立聯繫比較困難，因為這要求你大腦能夠人肉編譯展開宏代碼。不過還好編譯器為我們提供了 `--pretty=expanded` 選項，能讓我們看到展開後的代碼，通過這個展開後的代碼，往上靠就與你自己寫的原程序有個直接對應關係，往下靠與編譯器給出的錯誤也是直接對應關係。

目前將宏展開需要使用 unstable option，通過 `rustc -Z unstable-options --pretty=expanded hello.rs` 可以查看宏展開後的代碼，如果是使用的 cargo 則通過 `cargo rustc -- -Z unstable-options --pretty=expanded` 將項目裡面的宏都展開。不過目前是沒法只展開部分宏的，而且由於 hygiene 的原因，會對宏裡面的名字做些特殊的處理(mangle)，所以程序裡面的宏全部展開後代碼的可讀性比較差，不過依然比依靠大腦展開靠譜。

下面可以看看最簡單的 hello-word 程序裡面的 `println!("Hello, world!")` 展開結果，為了 hygiene 這裡內部臨時變量用了 `__STATIC_FMTSTR` 這樣的名字以避免名字衝突，即使這簡單的一句展開後看起來也還是不那麼直觀的，具體這裡就不詳細分析了。

```
$ rustc -Z unstable-options --pretty expanded hello.rs
#![feature(prelude_import)]
#![no_std]
#[prelude_import]
use std::prelude::v1::*;
#[macro_use]
extern crate std as std;
fn main() {
    ::std::io::_print(::std::fmt::Arguments::new_v1({
                                                        static __STATIC_FMTSTR:
                                                               &'static [&'static str]
                                                               =
                                                            &["Hello, world!\n"];
                                                        __STATIC_FMTSTR
                                                    },
                                                    &match () { () => [], }));
}
```
