# Rust模組

模組是一個名稱空間，包含函式或其型別的定義。模組是函式，結構，特徵，預設情況下，模組的修飾符是私有的，但可以使用`impl``pub``public`

以下是模組中使用的關鍵字：

- **mod關鍵字**`mod`
- **pub關鍵字 關鍵字使可見性修飾符成為公共，因此，它們可在名稱空間外部存取。**`pub`
- **use關鍵字**`use`

## 模組定義

模組由`mod`

模組的語法：

```rust
mod module_name  
// body inside the module.
```

模組可以通過三種方式分類：

**1.單個模組：**

通過下面一個例子來理解這一點：

```rust
mod a  
{  
     pub fn single_module()  
    {  
      println!("Single module");  
    }  
}  
fn main()  
{  
  a::single_module();  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Single module
```

在上面的範例中，定義了一個模組- 可以使用模組名稱後跟名稱空間然後使用函式名稱來呼叫模組`a``a``a`

也可以使用單獨的檔案來執行上面的範例：

```rust
mod module;  
fn main()  
{  
  module::single_module();  
}
pub fn single_module()  
{  
    println!("Single module");  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Single module
```

在上面兩個例子中，檢查`mod X``X.rs``X/mod.rs`

**2.子模組：假設庫名稱是-**`language``C``Cplus`

下面給出了`language`

![img](https://tw511.com/upload/images/201910/20191014013926387.png)

通過下面一個例子來理解：

```rust
mod c  
{  
  pub fn c()  
  {  
    println!("C is a structured programming language");  
  }  
}  
mod cplus  
{  
 pub fn cplus()  
 {  
    println!("C++ is an object-oriented programming language");  
 }  
}  
fn main()  
{  
  c::c();  
  cplus::cplus();  
}
```

執行上面範例程式碼，得到以下結果：

```shell
C is a structured programming language
C++ is an object-oriented programming language
```

在上面的例子中，程式由兩個模組組成，即`c``cplus``c::c()``cplus::cplus()`

**3.巢狀模組：**

通過下面一個例子來理解這一點：

```rust
mod a  
{  
 pub fn a()  
 {  
   println!("a module");  
 }  
 pub mod b  
 {  
   pub fn a()  
   {  
     println!("b module");  
   }  
 }  
}  
fn main()  
{  
 a::a();  
 a::b::b();  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
a module
b module
```

在上面的例子中，程式由兩個模組組成，即 這兩個模組都包含具有相同名稱但功能不同。這兩個函式分別使用 它們都不會相互衝突，因為它們屬於不同的名稱空間。`a``b``b``a``a::a()``a::b::b()`
