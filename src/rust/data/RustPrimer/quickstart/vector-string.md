# 數組、動態數組和字符串
## 數組和動態數組
### 數組 array
Rust 使用數組存儲相同類型的數據集。
`[T; N]`表示一個擁有 T 類型，N 個元素的數組。數組的大小是固定。

**例子：**

```rust
fn main() {
    let mut array: [i32; 3] = [0; 3];

    array[1] = 1;
    array[2] = 2;

    assert_eq!([1, 2], &array[1..]);

    // This loop prints: 0 1 2
    for x in &array {
        println!("{} ", x);
    }
}
```

### 動態數組 Vec
動態數組是一種基於堆內存申請的連續動態數據類型，擁有 O(1) 時間複雜度的索引、壓入（push）、彈出（pop)。

**例子：**

```rust
//創建空Vec
let v: Vec<i32> = Vec::new();
//使用宏創建空Vec
let v: Vec<i32> = vec![];
//創建包含5個元素的Vec
let v = vec![1, 2, 3, 4, 5];
//創建十個零
let v = vec![0; 10];
//創建可變的Vec，並壓入元素3
let mut v = vec![1, 2];
v.push(3);
//創建擁有兩個元素的Vec，並彈出一個元素
let mut v = vec![1, 2];
let two = v.pop();
//創建包含三個元素的可變Vec，並索引一個值和修改一個值
let mut v = vec![1, 2, 3];
let three = v[2];
v[1] = v[1] + 5;
```

## 字符串
Rust 裡面有兩種字符串類型。`String` 和 `str`。

### &str
`str` 類型基本上不怎麼使用，通常使用 `&str` 類型，它其實是 `[u8]` 類型的切片形式 `&[u8]`。這是一種固定大小的字符串類型。
常見的的字符串字面值就是 `&'static str` 類型。這是一種帶有 `'static` 生命週期的 &str 類型。

**例子：**

```rust
// 字符串字面值
let hello = "Hello, world!";

// 附帶顯式類型標識
let hello: &'static str = "Hello, world!";
```

### String
`String` 是一個帶有的 `vec:Vec<u8>` 成員的結構體，你可以理解為 `str` 類型的動態形式。
它們的關係相當於 `[T]` 和 `Vec<T>` 的關係。
顯然 `String` 類型也有壓入和彈出。

**例子：**

```rust
// 創建一個空的字符串
let mut s = String::new();
// 從 `&str` 類型轉化成 `String` 類型
let mut hello = String::from("Hello, ");
// 壓入字符和壓入字符串切片
hello.push('w');
hello.push_str("orld!");

// 彈出字符。
let mut s = String::from("foo");
assert_eq!(s.pop(), Some('o'));
assert_eq!(s.pop(), Some('o'));
assert_eq!(s.pop(), Some('f'));
assert_eq!(s.pop(), None);
```
