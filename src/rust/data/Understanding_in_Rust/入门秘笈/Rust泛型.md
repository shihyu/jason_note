# Rust泛型

當要建立多種形式的功能時，即，函式的引數可以接受多種型別的資料。這可以通過泛型來實現。泛型也稱為「引數多型」，其中多型是多重的，而變形是形式。

有兩種方法可以提供通用程式碼：

- `Option<T>`
- `Result<T, E>`

![img](https://tw511.com/upload/images/201910/20191014013943403.png)

1. 它提供了一種型別的泛型。`Option<T>` `Option` `'T'`

```rust
enum Option<T>  
{  
    Some(T),  
    None,  
}
```

在上面的例子中，可以用任何資料型別替換 下面來看看這幾個範例：`enum` `<T>` `T`

```rust
let x : Option<i32> = Some(10);  // 'T' is of type i32.  
let x : Option<bool> = Some(true);  // 'T' is of type bool.  
let x : Option<f64> = Some(10.5); // 'T' is of type f64.  
let x : Option<char> = Some('b'); // 'T' is of type char.
```

在上面的例子中，觀察到 但是，如果左側的型別與右側的值不匹配，則會發生錯誤。如下範例：`'T'` `i32` `bool` `f64` `char`

```rust
let x : Option<i32> = Some(10.8);
```

在上述情況下，左側的型別是 因此，錯誤發生「型別不匹配」。`i32` `f64`

1. `Result <T,E>`： Rust標準庫提供了另一種資料型別`Result <T，E>` `T＆E`

```rust
enum Result<T,E>  
   {  
      OK(T),  
        Err(E),  
}
```

> 注意：不得不使用`'T'` `'E'`

#### 泛型函式

泛型可以在函式中使用，將泛型放在函式的簽名中，其中指定引數的資料型別和返回值。

- 當函式包含型別為`T`

**語法**

```rust
fn function_name<T>(x:T)   
// body of the function.
```

上面的語法包含兩部分：

- `<T>` : 給定的函式是一種型別的泛型。
- `(x : T)`: x 是型別`T`

當函式包含多個相同型別的引數時。

```rust
fn function_name<T>(x:T, y:T)   
// body of the function.
```

當函式包含多個型別的引數時。

```rust
fn function_name<T,U>(x:T, y:U)  
// Body of the function.
```

完整程式碼 -

```rust
 fn main()  
{  
  let a = vec![1,2,3,4,5];  
  let b = vec![2.3,3.3,4.3,5.3];  
  let result = add(&a);  
  let result1 = add(&b);  
  println!("The value of result is {}",result);  
  println!("The value of result1 is {}",result1);  
}  

fn add<T>(list:&[T])->T  
{  
  let mut c =0;  
  for &item in list.iter()  
  {  
    c= c+item;  
  }  
}
```

## 結構定義

結構也可以使用`<>`

**語法：**

```rust
struct structure_name<T>   
// Body of the structure.
```

在上面的語法中，在`struct_name` `struct`

下面我們來看一個簡單的例子：

```rust
struct Value<T>  
{  
  a:T,  
  b:T,  
}  
fn main()  
{  
  let integer = Value{a:2,b:3};  
  let float = Value{a:7.8,b:12.3};  
  println!("integer values : {},{}",integer.a,integer.b);  
  println!("Float values :{},{}",float.a,float.b);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
integer values : 2,3
Float values : 7.8,12.3
```

在上面的範例中，建立兩個範例 包含`Value <T>` `a` `b` `integer` `float` `Integer` `i32` `float` `f64`

下面來看另一個簡單的例子。

```rust
struct Value<T>  
{  
  a:T,  
  b:T,  
}  
fn main()  
{  
  let c = Value{a:2,b:3.6};  
  println!("c values : {},{}",c.a,c.b);  
}
```

執行上面範例程式碼，得到以下結果：



![img](https://tw511.com/upload/images/201910/20191014013943404.png)

在上面的範例中，建立了一個 包含不同型別的值，即 因此，Rust編譯器會丟擲「不匹配的錯誤」。`Value <T>` `a` `b` `c` `c` `i32` `f64`

## 列舉定義

列舉也可以使用通用資料型別。Rust標準庫提供了 是一個列舉，其中`Option <T>` `Option <T>` `T`

- `Option<T>`

它由兩個變體組成，即`Some(T)` `None`

![img](https://tw511.com/upload/images/201910/20191014013943405.png)

其中`Some(T)` `T` `None`

看看下面一段範例程式碼：

```rust
enum Option<T>  
{  
    Some(T),  
    None,  
}
```

在上面的例子中，它由兩個變體`Option` `T` `Some(T)` `None`

```
Result<T, E>`：可以建立多種型別的泛型，這可以通過`Result <T，E>
enum Result<T,E>  
{  
    OK(T),  
    Err(E),  
}
```

在上面的例子中，`Result <T，E>` `OK(T)` `Err(E)`

`OK(T)`保持型別`T` `Err(E)` `E`

## 方法定義

可以在結構和列舉上實現這些方法。下來看看一個簡單的例子：

```rust
struct Program<T> {  
    a: T,  
    b: T,  
}  
impl<T> Program<T>   
{  
    fn a(&self) -> &T   
{  
       &self.a  
    }  
}

fn main() {  
    let p = Program{ a: 5, b: 10 };  

    println!("p.a() is {}", p.a());  
}
```

輸出結果如下 -

```shell
p.a() is 5
```

在上面的例子中，在 在`Program <T>` `a` `a` `impl` `T` `Program <T>`

## 解決歧義

Rust編譯器自動推斷通用引數。下面通過一個簡單的場景來理解：

```rust
Let mut v = Vec::new();   // creating a vector.  
v.push(10); // inserts integer value into the vector. Therefore, v is of i32 type.  
println!("{:?}", v); // prints the value of v.
```

在上面的例子中，將整數值插入向量中。因此，Rust編譯器知道向量`v``i32`

如果刪除第二行，現在程式碼如下所示 -

```rust
Let mut v = Vec::new();   // creating a vector.  
println!("{:?}", v); // prints the value of v.
```

上面的情況將丟擲「它無法推斷出T的型別」的錯誤。

可以通過兩種方式解決上述問題：

1. 使用以下注釋：

```rust
let v : Vec<bool> = Vec::new();  
println!("{:?}",v) ;
```

2. 使用`'turbofish':: <>``'T'`

```rust
let v = Vec :: <bool> :: new();  
println!("{:?}",v) ;
```
