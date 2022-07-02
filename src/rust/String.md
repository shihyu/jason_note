

# 理解 Rust 字符串



Rust 中有多種表示字符串的數據類型，其中最常用的是 str 和 String 兩種類型。

**str 類型**

Rust 中有一個表示字符串的原始（primitive）類型 str。str 是字符串切片（slice），每個字符串切片具有固定的大小並且是不可變的。通常不能直接訪問 str ，因為切片屬於動態大小類型（DST）。所以，只能通過引用（&str）間接訪問字符串切片。關於這一點，會在以後的文章中介紹。在下面的內容將不加區分的使用 str 和 &str。

可以通過字符串字面量構造 &str 類型的對象：

```rust
let s = "Hello, world!";
```

在 Rust 中，字符串字面量的類型是 & 'static str，因為它是被直接儲存在編譯後的二進制文件中的。

還可以使用切片的語法，從一個&str 對象構造出另一個 &str 對象：

```rust
let ss = &s[..3];
```

也可以將切片轉換成相應的指針類型：

```rust
let p = s as *const str;
```

**String 類型**

像大部分常見的編程語言一樣，String 是一個分配在堆上的可增長的字符串類型，它的定義如下：

```rust
struct String { 
    vec: Vec<u8> 
}
```

從源碼可以看出，String 是對 Vec<u8> 的簡單包裝。

String 保存的總是有效的 UTF-8 編碼的字節序列。

構造一個空字符串：

```rust
let s = String::new();
```

還可以通過字符串字面量構造 String 類型的對象：

```rust
let hello = String::from("Hello, world!");
```

String 和 &str 之間有著非常緊密的關系，後者可以用來表示前者的被借用（Borrowed）的副本。

**str 和 String 類型的轉換**

前面已經看到，字符串字面量可以轉換成 String。反過來，String 也可以轉換成str。這是通過解引用操作實現的：

```rust
impl Deref for String { 
    fn deref(&self) -> &str { 
        unsafe { str::from_utf8_unchecked(&self.vec) } 
    } 
} 
```

利用解引用操作就可以將 String 轉換成 str：

```rust
let s: String = String::from("Hello");
let ss: &str = &s;
```

String 還可以連接一個 str 字符串：

```rust
let s = String::from("Hello"); 
let b = ", world!"; 
let f = s + b; // f == "Hello, world!"
```

如果要連接兩個 String 對象，不能簡單地直接相加。必須先通過解引用將後一個對象轉換為 &str 才能進行連接：

```rust
let s = String::from("Hello");
let b = String::from(", world!");
let f = s + &b; // f == "Hello, world!"
```

注意這裡字符串連接之後，s的所有權發生了轉移，而b的內容復制到了新的字符串中。

從 String 到 str 的轉換是廉價的，反之，從 str 轉為 String 需要分配新的內存。

一般來說，當定義函數的參數時， &str 會比 String 更加通用：因為此時既可以傳遞 &str 對象也可以傳遞 String 對象。