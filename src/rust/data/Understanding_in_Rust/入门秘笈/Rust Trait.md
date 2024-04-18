# Rust Trait

Rust trait 是Rust語言的一個特性(性狀)，它描述了它可以提供的每種型別的功能。性狀類似於其他語言中定義的介面的特徵。性狀是一種對方法簽名進行分組以定義一組行為的方法。使用


`trait`

`trait`的語法：

```rust
trait trait_name  
//body of the trait.
```

在上面的例子中，宣告特徵後跟特徵(性狀)名稱。在大括號內，宣告方法簽名以描述實現特徵的型別的行為。

下面來看一個簡單的例子：

```rust
struct Triangle  
{  
  base : f64,  
  height : f64,  
}  
trait HasArea  
{  
  fn area(&self)->f64;  
}  

impl HasArea for Triangle  
{  
  fn area(&self)->f64  
  {  
    0.5*(self.base*self.height)  
  }  
}  
fn main()  
{  
  let a = Triangle{base:10.5,height:17.4};  
  let triangle_area = a.area();  
  println!("Area of a triangle is {}",triangle_area);   
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Area of a triangle is 91.35
```

在上面的例子中，宣告了一個 是在 通過使用結構的範例，即`HasArea` `area()` `HasArea` `Triangle` `a.area()` `area()`

## 性狀作為引數

特徵(性狀)也可以用作許多不同型別的引數。

上面的例子實現了 可以定義呼叫`HasArea` `area()` `area()` `calculate_area()` `HasArea` `area()`

下面來來看看語法：

```rust
fn calculate_area(item : impl HasArea)  
  println!("Area of the triangle is : {}",item.area());  
}
```

## 性狀限制了通用函式

性狀很有用，因為它們描述了不同方法的行為。但是，通用函式不遵循此約束。通過一個簡單的場景來理解這一點：

```rust
fn calculate_area<T>( item : T)  
   println!(?Area of a triangle is {}?, item.area());
```

在上面的例子中，Rust編譯器丟擲「沒有找到型別為 如果將性狀繫結到泛型`T` `T`

```rust
fn calculate_area<T : HasArea> (item : T)  
{  
    println!("Area of a triangle is {} ",item.area());  
}
```

在上面的例子中，Rust編譯器知道任何實現`<T:HasArea>` `T` `HasArea` `HasArea` `area()`

下面來看一個簡單的例子：

```rust
trait HasArea  
{  
  fn area(&self)->f64;  
}  
struct Triangle  
{  
  base : f64,  
  height : f64,  
}  

impl HasArea for Triangle  
{  
  fn area(&self)->f64  
  {  
    0.5*(self.base*self.height)  
  }  
}  
struct Square  
{  
  side : f64,  
}  

impl HasArea for Square  
{  
  fn area(&self)->f64  
  {  
     self.side*self.side  
  }  
}  
fn calculate_area<T : HasArea>(item : T)  
{  
  println!("Area is : {}",item.area());  
}  

fn main()  
{  
  let a = Triangle{base:10.5,height:17.4};  
  let b = Square{side : 4.5};  
  calculate_area(a);  
  calculate_area(b);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Area is : 91.35
Area is : 20.25
```

在上面的例子中，`calculate_area()``T`

## 實施性狀的規則

實現性狀有兩個限制：

- 如果範圍中未定義性狀，則無法在任何資料型別上實現該性狀。

下面來看一個簡單的例子：

```rust
use::std::fs::File;  
fn main()  
{  
  let mut f = File::create("hello.txt");  
  let str = "Yiibai";  
  let result = f.write(str);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
error : no method named 'write' found.
           let result = f.write(str);
```

在上面的例子中，Rust編譯器丟擲一個錯誤，即 因此，需要使用`"no method named 'write' found"` `use::std::fs::File;` `write()` `Write trait`

- 正在實現的性狀必須定義。例如：如果定義 但是，無法為型別`HasArea` `i32` `i32` `toString`

## 多個性狀界限

使用`'+'`

如果想繫結多個性狀，可使用`+`

下面來看一個簡單的例子：

```rust
use std::fmt::{Debug, Display};  
fn compare_prints<T: Debug + Display>(t: &T)  
{  
    println!("Debug: '{:?}'", t);  
    println!("Display: '{}'", t);  
}  

fn main() {  
    let string = "Yiibai";  
    compare_prints(&string);  
}
```

執行上面範例程式碼，輸出結果如下 -

```shell
Debug: ' "Yiibai"'
Display: ' Yiibai'
```

在上面的範例中，`Display` `Debug` `+` `T`

使用`where`

- 使用出現在括號`{` `where`
- `where`子句也可以應用於任意型別。
- 當使用`where`

如下程式碼 -

```rust
fn fun<T: Display+Debug, V: Clone+Debug>(t:T,v:V)->i32  
//block of code;
```

在上述情況下使用`where`

```rust
fn fun<T, V>(t:T, v:V)->i32  
  where T : Display+ Debug,   
             V : Clone+ Debug  

       //block of code;
```

在上面的例子中，使用`where`

下面來看看一個簡單的例子：

```rust
trait Perimeter  
{  
  fn a(&self)->f64;  
}  
struct Square  
{  
  side : f64,  
}  
impl Perimeter for Square  
{  
  fn a(&self)->f64  
  {  
    4.0*self.side  
  }  
}  
struct Rectangle  
{  
 length : f64,  
 breadth : f64,  
}  
impl Perimeter for Rectangle  

{  
 fn a(&self)->f64  
 {  
   2.0*(self.length+self.breadth)  
 }  
}  
fn print_perimeter<Square,Rectangle>(s:Square,r:Rectangle)  
  where Square : Perimeter,  
        Rectangle : Perimeter  
        {  
          let r1 = s.a();  
          let r2 = r.a();  
          println!("Perimeter of a square is {}",r1);  
          println!("Perimeter of a rectangle is {}",r2);  
        }  
fn main()  
{  
    let sq = Square{side : 6.2};  
    let rect = Rectangle{length : 3.2,breadth:5.6};  
    print_perimeter(sq,rect);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Perimeter of a square is 24.8
Perimeter of a rectangle is 17.6
```

## 預設方法

可以將預設方法新增到性狀定義的方法定義為已知。範例程式碼：

```rust
trait Sample  

  fn a(&self);  
  fn b(&self)  
  {  
      println!("Print b");  
  }
```

在上面的例子中，預設行為被新增到性狀定義中。還可以覆蓋預設行為。下面通過一個例子看看這個場景：

```rust
trait Sample  
{  
 fn a(&self);  
 fn b(&self)  
 {  
   println!("Print b");  
 }   
}   

struct Example  
{  
 a:i32,  
 b:i32,  
}  



impl Sample for Example  
{  
  fn a(&self)  
  {  
    println!("Value of a is {}",self.a);  
  }  

  fn b(&self)  
  {  
    println!("Value of b is {}",self.b);  
  }  
}  
fn main()  
{  
  let r = Example{a:5,b:7};  
  r.a();  
  r.b();    
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Value of a is : 5
Value of b is : 7
```

在上面的例子中，因此得出結論，可覆蓋性狀中定義的方法。`b()`

## 繼承

從另一個性狀派生的性狀稱為繼承。有時，有必要實現另一個性狀的性狀。如果想從'A'性狀繼承'B'性狀，那麼它看起來像：

```rust
trait B : A;
```

參考以下一段完整的程式碼 -

```rust
trait A  
{  
  fn f(&self);  
}  
trait B : A  
{  
  fn t(&self);  
}  
struct Example  
{  
  first : String,  
  second : String,  
}  
impl A for Example  
{  
  fn f(&self)  
  {  

   print!("{} ",self.first);  
  }  

 }  
 impl B for Example  
 {  
  fn t(&self)  
  {  
    print!("{}",self.second);  
  }  
}  
fn main()  
{  
  let s = Example{first:String::from("Yiibai"),second:String::from("tutorial")};  
  s.f();  
  s.t();  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Yiibai tutorial
```

在上面的例子中，程式實現'B'性狀。因此，它還需要實現'A'性狀。如果程式沒有實現'A'性狀，則Rust編譯器會丟擲錯誤。
