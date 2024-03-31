# Rust字串

Rust包含兩種型別的字串：`&str` `String`

**String**

- 字串被編碼為UTF-8序列。
- 在堆記憶體上分配一個字串。
- 字串的大小可以增長。
- 它不是以空(`null`

**&str**

- `&str`也稱為字串切片。
- 它由`&[u8]`
- `＆str`用於檢視字串中的資料。
- 它的大小是固定的，即它不能調整大小。

**String 和&str 的區別**

- `String`是一個可變參照，而`&str` `String` `&str`
- `String`包含其資料的所有權，而`&str`

## 建立一個新的字串

在建立向量時類似地建立`String`

建立一個空字串：

```rust
Let mut s = String::new();
```

在上面的宣告中，現在，如果想在宣告時初始化String，可以通過使用`String` `new()` `to_string()`

在資料上實現`to_string()`

```rust
let a = "Yiibai";  
let s = a.to_string();
```

也可以直接在字串文字上實現`to_string`

```rust
let s = "Yiibai".to_string();
```

下面通過一個例子來理解這一點：

```rust
fn main()  
{
 let data="Yiibai";  
 let s=data.to_string();  
 print!("{} ",s);  
 let str="tutorial".to_string();  
 print!("{}",str);
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Yiibai tutorial
```

建立 下面通過一個簡單的例子來理解這一點：`String``String::from``String::new()`

```rust
fn main()  
{  
    let str = String::from("Yiibai tutorial");  
    print!("{}",str);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Yiibai tutorial
```

## 更新字串

可以通過將更多資料推播到 也可以使用格式巨集的`String``String``String``+`

![img](https://tw511.com/upload/images/201910/20191014013934391.png)

使用 它將內容附加在字串的末尾。假設`push_str`  `push` `push_str()` `push_str()` `s1` `s2` `s3` `s4`

```rust
s1.push_str(s2);
```

通過一個簡單的例子來理解這一點：

```rust
fn main()  
{  
  let mut s=String::from("java is a");  
  s.push_str(" programming language");  
  print!("{}",s);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
java is a programming language
```

`push_str()`函式不接受引數的所有權。下面通過一個簡單的例子來理解。

```rust
fn main()  
{  
  let mut s1 = String::from("Hello");  
  let s2 = "World";  
  s1.push_str(s2);  
  print!("{}",s2);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
World
```

如果`push_str()` `s2`

`push()`：假設字串是`push()` `s1 ` `ch` `s1`

```
s1.push(ch);
```

下面來看一個簡單的範例

```rust
fn main()  
{  
  let mut s = String::from("java");  
  s.push('c');  
  print!("{}",s);  
}
```

執行上面範例程式碼，得到以下結果-

```shell
javac
```

- 使用 下面來看一個範例程式碼：`+` `+` `+`

```rust
let s1 = String::from("Yiibai ");  
let s2 = String::from("tutorial!!");  
let s3 = s1+&s2;
```

再來看看一個簡單的程式碼：

```rust
fn main()  
{  
 let s1 = String::from("Yiibai");  
 let s2 = String::from(" tutorial!!");  
 let s3 = s1+&s2;   
 print!("{}",s3);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Yiibai tutorial!!
```

在上面的例子中，不再有效，使用 運算子呼叫`s3` `"Yiibai tutorial!!"` `s1` `s2` `&s2` `+` `+` `add()`

```rust
fn add(self,s:&str)->String  
{  
}
```

首先，根據 但是根據 但是，仍然可以在 因此，當呼叫`s2` `&` `s1` `add()` `&str` `String` `add()` `s2` `&String` `&str` `add` `s2` `&string` `&str` `add()`

其次，這意味著在語句`add()` `self` `add()` `self` `let s3 = s1 +&s2` `s1`

下面通過一個簡單的例子來理解這一點：

```rust
fn main()  
{  
 let s1 = String::from("C");  
 let s2 = String::from("is");  
 let s3 = String::from("a");  
 let s4 = String::from("programming");  
 let s5 = String::from("language.");  
 let s = format!("{} {} {} {} {}",s1,s2,s3,s4,s5);  
 print!("{}",s);  
}
```

執行上面範例程式碼，得到以下結果：

```shell
C is a programming language.
```

## 字串中的索引

`String`以 因此，字串無法編入索引。下面通過一個例子來理解這個概念：`UTF-8`

```
fn main()   
{  
    let s = String::from("Yiibai");  
    print!("{}",s[1]);  
}
```

執行上面範例程式碼，得到類似以下的結果 -

```shell
error[E0277]: the trait bound `std::string::String: std::ops::Index<{integer}>` is not satisfied
 --> jdoodle.rs:4:17
  |
4 |     print!("{}",s[1]);
  |                 ^^^^ the type `std::string::String` cannot be indexed by `{integer}`
  |
  = help: the trait `std::ops::Index<{integer}>` is not implemented for `std::string::String`

error: aborting due to previous error
```

通過索引存取非常快。但是，字串以`UTF-8``n`

## 字串切片

字串中未提供索引，因為不知道索引操作的返回型別應具有位元組值，字元或字串切片。Rust提供了一種更具體的方法來索引字串，方法是在`[]`

**範例：**

```rust
let s = "Hello World";  
let a = &s[1..4];
```

在上面的場景中，這裡指定`s` `"Hello World"` `[1..4]` `1` `3`

```rust
fn main() {  

    let s = "Hello World";  
    let a = &s[1..4];  
    print!("{}",a);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
ell
```

## 疊代字串的方法

也可以通過其他方式存取字串。使用`chars()`

下面來看一個簡單的例子：

```
fn main()   
{  
    let s = "C is a programming language";  
    for i in s.chars()  
    {  
      print!("{}",i);  
    }  
}
```

執行上面範例程式碼，得到以下結果 -

```
C is a programming language
```
