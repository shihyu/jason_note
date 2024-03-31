# Rust生命週期

生命週期定義了參照有效的範圍。生命週期是隱含的和推斷的。Rust使用通用生命週期引數來確保使用有效的實際參照。

## 預防與生命週期的懸空參照

當程式試圖存取無效參照時稱為懸空參照，所指向無效資源的指標稱為懸空指標。

看看一個簡單的例子：

```rust
fn main()  
{  
  let a;  
  {  
    let b = 10;  
     a = &b;  
  }  
  println!("a : {}",a);  
}
```

輸出結果如下 -

![img](https://tw511.com/upload/images/201910/20191014013947406.png)

在上面的範例中，外部作用域包含 內部範圍包含變數 變數的參照儲存在變數 當內部範圍結束時，嘗試存取 Rust編譯器將丟擲一個編譯錯誤，因為 Rust將使用借用檢查器確定程式碼無效。`a` `b` `10` `b` `a` `a` `a`

## 借用檢查器

借用檢查器用於解決懸掛參照的問題。借用檢查器用於比較範圍以確定它們是否有效。

![img](https://tw511.com/upload/images/201910/20191014013947407.png)

在上面的例子中，註釋了 在編譯時，Rust將拒絕該程式，因為 可以修復上面的程式碼，以便不會發生編譯器錯誤。`a` `a` `b` `b` `a` `b`

![img](https://tw511.com/upload/images/201910/20191014013947408.png)

在上面的例子中，因此，上面的程式碼執行時沒有任何編譯錯誤。`a` `b`

## 生命週期註釋語法

- 生命週期註釋不會改變任何參照的生存時間。
- 函式還可以使用泛型生存期引數接受任何生命週期的參照。
- 生命週期註釋描述了多個引數的生命週期之間的關係。

**生命週期註釋語法應遵循的步驟：**

- 生命週期引數的名稱應以(`'`
- 它們主要是小寫和簡寫。例如：`'a`
- 生命週期引數註釋放在參照的`&`

**生命週期註釋語法的一些範例：**

- `&i32` // reference
- `& 'a i32` // reference with a given lifetime.
- `& 'a mut i32` // mutable reference with a given lifetime.

## 函式簽名中的生命週期註釋

```
'a`代表參考的生命週期。每個參考都有與之相關的生命週期。也可以在函式簽名中使用生命週期註釋。通用生命週期引數在角括號`<>
```

範例 -

```rust
fn fun<'a>(...);
```

在上面的例子中，如果函式包含兩個具有兩個不同生命週期的參考引數，則它可以表示為：`fun` `'a`

```rust
fn fun<'a,'b>(...);
```

如果`'y'`

```rust
fn fun<'a>(y : & 'a i32);
```

如果`'y'`

```rust
fn fun<'a>(y : & 'a mut i32);
```

兩個 唯一的區別是`&'a i32``&'a mut i32``'a``&``mut`

`&mut i32`的意思是「對i32的可變參照」。表示「對具有生命週期'的
`&'a mut i32` `i32`

## 結構中的生命週期註釋

也可以在結構中使用顯式生命週期，就像在函式中使用的一樣。

下面來看看一個範例：

```rust
struct Example  
   x : & 'a i32,  //  x is a variable of type i32 that has the lifetime 'a.
```

下面來看一個簡單的例子：

```rust
struct Example<'a> {  
    x: &'a i32,  
}  
fn main() {  
    let y = &9;   
    let b = Example{ x: y };  
    println!("{}", b.x);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
9
```

### impl塊

可以實現具有生命週期`'a` `impl`

下面來看一個簡單的例子：

```rust
struct Example<'a> {  
    x: &'a i32,  
}  
impl<'a> Example<'a>  
{  
fn display(&self)  
{  
  print!("Value of x is : {}",self.x);  
}  
}  
fn main() {  
    let y = &90;   
    let b = Example{ x: y };  
    b.display();  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Value of x is : 90
```

## 多個生命週期

有兩種可能性：

- 多個參照具有相同的生命週期。
- 多個參照具有不同的生命週期。

當參照具有相同的生命週期時。

```rust
fn fun <'a>(x: & 'a i32 , y: & 'a i32) -> & 'a i32  

   //block of code.
```

在上述情況下，參照`x` `y` `'a`

當參照具有不同的生命週期時。如下 -

```rust
fn fun<'a , 'b>(x: & 'a i32 , y: & 'b i32)   

   // block of code.
```

在上述情況下，參考`x` `y` `'a` `'b`

**'static**

`'static`的生命週期是特殊的生命週期。它表示某些東西具有生命週期 主要是 具有「靜態生命週期」的參照對整個程式有效。`'static` `'static`

範例：

```rust
let s : & 'static str = "Yiibai tutorial" ;
```

## 生命週期橢圓

生命週期橢圓是一種推理演算法，它使常見的模式更符合人體工程學。生命週期橢圓使一個程式被淘汰。

生命週期橢圓可以在任何地方使用：

- `& 'a T`
- `& 'a mut T`
- `T<'a>`

生命週期橢圓可以以兩種方式出現：

- **輸入生命週期**
- **輸出生存期**

範例 -
```rust
fn fun<'a>( x : & 'a i32);                       // input lifetime  
fn fun<'a>() -> & 'a i32;                      // output lifetime  
fn fun<'a>(x : & 'a i32)-> & 'a i32;      // Both input and output lifetime.
```
