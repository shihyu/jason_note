# 變量綁定與原生類型

## 變量綁定
Rust 通過 let 關鍵字進行變量綁定。

```rust
fn main() {
    let a1 = 5;
    let a2:i32 = 5;
    assert_eq!(a1, a2);
    //let 綁定 整數變量默認類型推斷是 i32

    let b1:u32 = 5;
    //assert_eq!(a1, b1);
    //去掉上面的註釋會報錯，因為類型不匹配
    //errer: mismatched types
}
```

這裡的 assert_eq! 宏的作用是判斷兩個參數是不是相等的，但如果是兩個不匹配的類型，就算字面值相等也會報錯。

## 可變綁定
rust 在聲明變量時，在變量前面加入 mut 關鍵字，變量就會成為可變綁定的變量。

```rust
fn main() {
    let mut a: f64 = 1.0;
    let b = 2.0f32;

    //改變 a 的綁定
    a = 2.0;
    println!("{:?}", a);

    //重新綁定為不可變
    let a = a;

    //不能賦值
    //a = 3.0;

    //類型不匹配
    //assert_eq!(a, b);
}
```

這裡的 b 變量，綁定了 2.0f32。這是 Rust 裡面值類型顯式標記的語法，規定為`value`+`type`的形式。

**例如：**
固定大小類型：
> 1u8 1i8  
> 1u16 1i16  
> 1u32 1i32  
> 1u64 1i64

可變大小類型：
> 1usize 1isize

浮點類型：
> 1f32 1f64

## let解構
為什麼在 Rust 裡面聲明一個變量的時候要採用 let 綁定表達式？
那是因為 let 綁定表達式的表達能力更強，而且 let 表達式實際上是一種模式匹配。

**例如：**

```rust
fn main() {
    let (a, mut b): (bool,bool) = (true, false);
    println!("a = {:?}, b = {:?}", a, b);
    //a 不可變綁定
    //a = false;

    //b 可變綁定
    b = true;
    assert_eq!(a, b);
}
```

這裡使用了 bool，只有true和false兩個值，通常用來做邏輯判斷的類型。

## 原生類型

Rust內置的原生類型 (primitive types) 有以下幾類：

* 布爾類型：有兩個值`true`和`false`。
* 字符類型：表示單個Unicode字符，存儲為4個字節。
* 數值類型：分為有符號整數 (`i8`, `i16`, `i32`, `i64`, `isize`)、
無符號整數 (`u8`, `u16`, `u32`, `u64`, `usize`) 以及浮點數 (`f32`, `f64`)。
* 字符串類型：最底層的是不定長類型`str`，更常用的是字符串切片`&str`和堆分配字符串`String`，
其中字符串切片是靜態分配的，有固定的大小，並且不可變，而堆分配字符串是可變的。
* 數組：具有固定大小，並且元素都是同種類型，可表示為`[T; N]`。
* 切片：引用一個數組的部分數據並且不需要拷貝，可表示為`&[T]`。
* 元組：具有固定大小的有序列表，每個元素都有自己的類型，通過解構或者索引來獲得每個元素的值。
* 指針：最底層的是裸指針`*const T`和`*mut T`，但解引用它們是不安全的，必須放到`unsafe`塊裡。
* 函數：具有函數類型的變量實質上是一個函數指針。
* 元類型：即`()`，其唯一的值也是`()`。

```rust
// boolean type
let t = true;
let f: bool = false;

// char type
let c = 'c';

// numeric types
let x = 42;
let y: u32 = 123_456;
let z: f64 = 1.23e+2;
let zero = z.abs_sub(123.4);
let bin = 0b1111_0000;
let oct = 0o7320_1546;
let hex = 0xf23a_b049;

// string types
let str = "Hello, world!";
let mut string = str.to_string();

// arrays and slices
let a = [0, 1, 2, 3, 4];
let middle = &a[1..4];
let mut ten_zeros: [i64; 10] = [0; 10];

// tuples
let tuple: (i32, &str) = (50, "hello");
let (fifty, _) = tuple;
let hello = tuple.1;

// raw pointers
let x = 5;
let raw = &x as *const i32;
let points_at = unsafe { *raw };

// functions
fn foo(x: i32) -> i32 { x }
let bar: fn(i32) -> i32 = foo;
```

有幾點是需要特別注意的：

* 數值類型可以使用`_`分隔符來增加可讀性。
* Rust還支持單字節字符`b'H'`以及單字節字符串`b"Hello"`，僅限制於ASCII字符。
此外，還可以使用`r#"..."#`標記來表示原始字符串，不需要對特殊字符進行轉義。
* 使用`&`符號將`String`類型轉換成`&str`類型很廉價，
但是使用`to_string()`方法將`&str`轉換到`String`類型涉及到分配內存，
除非很有必要否則不要這麼做。
* 數組的長度是不可變的，動態的數組稱為Vec (vector)，可以使用宏`vec!`創建。
* 元組可以使用`==`和`!=`運算符來判斷是否相同。
* 不多於32個元素的數組和不多於12個元素的元組在值傳遞時是自動複製的。
* Rust不提供原生類型之間的隱式轉換，只能使用`as`關鍵字顯式轉換。
* 可以使用`type`關鍵字定義某個類型的別名，並且應該採用駝峰命名法。

```rust
// explicit conversion
let decimal = 65.4321_f32;
let integer = decimal as u8;
let character = integer as char;

// type aliases
type NanoSecond = u64;
type Point = (u8, u8);
```
