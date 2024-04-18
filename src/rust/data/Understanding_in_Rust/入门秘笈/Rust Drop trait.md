# Rust Drop trait

`drop trait`用於在值超出範圍時釋放檔案或網路連線等資源。
`drop trait`用於釋放`Box <T>`指向的堆上的空間。
`drop trait`用於實現`drop()`方法，方法該對`self`進行可變參照。

下面來看一個簡單的例子：

```rust
struct Example  
{  
  a : i32,  
 }  
      impl Drop for Example  
{  
  fn drop(&mut self)  
  {  
    println!("Dropping the instance of Example with data : {}", self.a);  
  }  
}  
      fn main()  
{  
  let a1 = Example{a : 10};  
  let b1 = Example{a: 20};  
  println!("Instances of Example type are created");  
}
```

執行上面的示例程序碼，得到以下結果 -

```shell
Instances of Example type are created
Dropping the instance of Example with data : 20
Dropping the instance of Example with data : 10
```

**程式程式碼說明**

- 在類型`Example`上實現了`Drop trait`，並在`Drop trait`的實現中定義了`drop()`方法。
- 在`main()`函式中，建立了式樣的範例，`Example`並且在`main()`函式的範圍，範例遠處了。
- 當範例移出作用域時，鐵鏽會隱式呼叫`drop()`方法來刪除`Example`類型範例。首先，刪除範例`b1`，然後刪除範例`a1`。

> **注意**：無需顯式呼叫`drop()`方法。因此，可以說當超出範圍時，鏽蝕隱式呼叫`drop()`方法。

#### 使用std::mem::drop刪除刪除值

有時，有必要在範圍結束之前刪除該值。如果想提前刪除該值，則使用`std::mem::drop`函式來刪除該值。

下面來看一個手動刪除值的簡單例子：

```rust
struct Example  
{  
  a : String,  
}  
impl Drop for Example  
{  
  fn drop(&mut self)  
  {  
    println!("Dropping the instance of Example with data : {}", self.a);  
  }  
}  
fn main()  
{  
  let a1 = Example{a : String::from("Hello")};  
  a1.drop();  
  let b1 = Example{a: String::from("World")};  
  println!("Instances of Example type are created");  
}
```

執行上面的示例程序碼，得到以下結果 -

![img](https://tw511.com/upload/images/201910/20191014013954414.png)

在上面的例子中，呼叫手動`drop()`方法。防鏽編譯器丟擲一個錯誤，顯不允許式呼叫`drop()`方法。顯不是式呼叫`drop()`方法，呼叫而是`std::mem::drop`函式在值超出範圍之前刪除它。

`std::mem::drop`的函式語法與`Drop trait`中定義的`drop()`。函式不同`std::mem::drop`。函式包含作為引數傳遞的值，值該在超出範圍之前將被刪除
下面來看一個簡單的例子：

```rust
 struct Example  
{  
  a : String,  
}  

impl Drop for Example  
{  
  fn drop(&mut self)  
  {  
    println!("Dropping the instance of Example with data : {}", self.a);  
  }  
}  

fn main()  
{  
  let a1 = Example{a : String::from("Hello")};  
  drop(a1);  
  let b1 = Example{a: String::from("World")};  
  println!("Instances of Example type are created");  
}
```

執行上面的示例程序碼，得到以下結果——

```shell
Dropping the instance of Example with data : Hello
Instances of Example type are created
Dropping the instance of Example with data : World
```

在上面的例子中，通過在`drop(a1)`式中將例子`a1`作為引數傳來的例子`a1`。
