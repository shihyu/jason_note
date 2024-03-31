# Rust Deref trait

`Deref <T> trait`用於自定義解除參照運算子( 如果實現 因此，在參照上工作的程式碼也可以用在智慧指標上。`*`
`Deref <T>`

## 常規參照

常規參照是一種指向某個值的指標，該值儲存在其他地方。下面來看一個簡單的例子來建立`i32` `this`

```rust
fn main()  
{  
  let a = 20;  
  let b = &a;  
  if a==*b  
  {  
    println!("a and *b are equal");  
  }  

  else  
  {  
    println!("they are not equal");  
  }  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
a and *b are equal
```

在上面的例子中，如果使用 因此，可以比較變數 如果使用`a` `i32` `20` `b` `a` `* b` `20` `a` `* b` `&b` `* b`

## `Box <T>`作為參照

`Box <T>`指標可用作參照。

下面來看一個簡單的例子：

```rust
fn main()  
{  
  let a = 11;  
  let b = Box::new(a);  
  print!("Value of *b is {}",*b);  
}
```

輸出結果如下所示 -

```shell
Value of *b is 11
```

在上面的範例中，它們之間的唯一區別是b包含指向資料的框，而不是通過使用`Box <T>` `&`

## 智慧指標作為參照

現在，建立類似於`Box <T>`

`Box <T>`可以定義為具有一個元素的元組結構，例如 建立元組結構後，在`MyBox <T>`
`MyBox <T>`

下面來看一個簡單的例子：

```rust
struct MyBox<T>(T);  
impl<T> MyBox<T>  
{  
  fn example(y : T)->MyBox<T>  
  {  
    MyBox(y)  
  }  
}  
fn main()  
{  
  let a = 8;  
  let b = MyBox::example(a);  
  print!("Value of *b is {}",*b);  
}
```

執行上面範例程式碼，得到以下結果 -

![img](https://tw511.com/upload/images/201910/20191014013953413.png)

在上面的例子中，建立了智慧指標 因此得出結論，無法取消類似於`b` `Box <T>`

## 實現Deref Trait

- `Deref Trait`在標準庫中定義，該庫用於實現名為`deref`
- `deref`方法借用`self`

下面來看一個簡單的例子：

```rust
struct MyBox<T>  
{  
  a : T,  
}  
use :: std::ops::Deref;  
impl<T> Deref for MyBox<T>  
{  
  type Target = T;  
  fn deref(&self) ->&T  
  {  
    &self.a  
  }  
}  
fn main()  
{  
  let b = MyBox{a : 10};  
  print!("{}",*(b.deref()));  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
10
```

**程式說明**

- `Deref trait`在`MyBox`
- `Deref trait`實現`deref()` `deref()` `a`
- `type Target = T;`是 關聯型別用於宣告泛型型別引數。`Deref trait`
- 建立了`MyBox` `b`
- 通過使用`MyBox``b.deref()` `deref()` `deref()`

## Deref強制

- `Deref`強制是將實現`Deref trait` `Deref`
- `Deref`強制是對函式和方法的引數執行的。
- 當將特定型別的參照傳遞給與函式定義中的引數型別不匹配的函式時，`Deref`

下面來看一個簡單的例子：

```rust
struct MyBox<T>(T);  
use :: std::ops::Deref;  
impl<T> MyBox<T>  
{  
  fn hello(x:T)->MyBox<T>  
  {  
    MyBox(x)  
  }  
}  
impl<T> Deref for MyBox<T>  
{  
  type Target = T;  
  fn deref(&self) ->&T  
  {  
    &self.0  
  }  
}  
fn print(m : &i32)  
{  
  print!("{}",m);  
}  
fn main()  
{  
  let b = MyBox::hello(5);  

  print(&b);  
}
```

執行上面範例程式碼，得到以下結果 -

```
5
```

在上面的例子中，使用引數 在這種情況下，實現`＆b` `print(&b)` `&Box <i32>` `Deref trait` `Deref` `&Box <i32>` `&i32`

## Derif強制與可變性的相互作用

到目前為止，使用`Deref Trait` `*` `DerefMut Trait` `*`

Rust在以下三種情況下執行`Deref`

- 當T：`Deref <Target = U>` `T` `U` `&T` `&U`
- 當T：`DerefMut <Target = U>` `T` `U` `&mut T` `&mut U`
- 當T：`Deref <Target = U>` `T` `U` `&mut T` `&U`
