# Rust切片

切片(Slice)是一種沒有所有權的資料型別。切片參照連續的記憶體分配而不是整個集合。它允許安全，高效地存取陣列而無需複製。切片不是直接建立的，而是從現有變數建立的。切片由長度組成，並且可以是可變的或不可變的。切片的行為與陣列相同。

## 字串切片

字串切片指的是字串的一部分。切片看起來像：

```rust
let str=String::from("Tw511.com tutorial");  
let yiibai=&str[0..10];  
let tutorial=&str[11,18];
```

如果想要取一部分字串，而不是整個字串。語法是一個從開始但不包括結束的範圍。因此，可以通過指定括號內的範圍來建立切片，例如 如果想要包含字串的結尾，那麼必須使用`[start..end]``[start..end]``start``end``..=``..`

```rust
let str= String::from("tw511.com tutorial");  
let yiibai = &str[0..=9];  
let tutorial= &str[11..=18] ;
```

圖解表示：

![img](https://tw511.com/upload/images/201910/20191014013916385.png)

如果要從 看起來如下：`0`

```rust
let str= String::from("hello world");  
let hello = &str[0..5];  
let hello=&str[..5];
```

如果 看起來如下：`slice`

```rust
let str= String::from("hello world") ;  
let hello=&str[6..len];  
let world = &str[6..];
```

下面來看一個字串切片的簡單範例：

```rust
fn main(){

    let str=String::from("Tw511.com tutorial");  
    let yiibai=&str[..=9];  
    println!("first word of the given string is {}",yiibai);
}
```

執行上面範例程式碼，得到以下結果 -

```shell
first word of the given string is Tw511.com
```

**字串切片是文字**

字串文字儲存在二進位制檔案中，字串文字僅作為字串切片。如下：

```rust
let str = "Hello Yiibai" ;
str`的型別是 字串文字是不可變的，`&str``&str
```

## 字串切片作為引數

如果有一個字串切片，那麼可以直接傳遞它作為引數。將字串切片作為引數傳遞給函式，而不是傳遞參照，以使API更通用和有用，而不會失去其功能。

```rust
 fn main()  
{  
let str= String:: from("Computer Science");  
let first_word=  first_word(&str[..]); //first_word function finds the first word of the string.  
let s="Computer Science" ; //string literal  
let first_word=first_word(&s[..]); // first_word function finds the first word of the string.  
let first_word=first_word(s) ; //string slice is same as string literal. Therefore, it can also be written in this way also.                             
}
```

## 其他切片

陣列也可以視為切片。它們的行為類似於字串切片。切片的型別為 它們通過將參照儲存為第一個元素並將長度儲存為第二個元素，類似於字串切片。`[&i32]`

考慮下面一個陣列：

```rust
let arr = [100,200,300,400,500];  // array initialization  
let a = &arr[1..=3]; // retrieving second,third and fourth element
```

下面來看一個簡單的例子。

```rust
fn main()  

    let arr = [100,200,300,400,500,600];  
    let mut i=0;  
    let a=&arr[1..=3];  
    let len=a.len();  
    println!("Elements of 'a' array:");  
    while i<len  
    {  
     println!("{}",a[i]);  
     i=i+1;  
    }  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Elements of 'a' array:
200
300
400
```
