# Rust use關鍵字參照模組

當呼叫模組的函式時，需要指定完整的路徑。

通過下面一個例子來理解這個概念：

```rust
pub mod a  
{  
  pub mod b  
  {  
    pub mod c  
    {  
      pub fn nested_modules()  
      {  
        println!("Nested Modules");  
      }  
    }  
  }  
 }  

fn main()  
{  
 a::b::c::nested_modules();  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Nested Modules
```

在上面的例子中，通過指定完整路徑來呼叫`nested_modules()``a::b::c::nested_modules()`

## use關鍵字

在上面的場景中，看到函式呼叫非常冗長。Rust中的 關鍵字只在範圍中指定的那些模組。通過下面一個例子來理解這一點：`use``use`

```rust
pub mod a  
{  
  pub mod b  
  {  
    pub mod c  
    {  
      pub fn nested_modules()  
      {  
        println!("Nested Modules");  
      }  
    }  
  }  
 }  

use a::b::c::nested_modules;  
fn main()  
{  
  nested_modules();  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Nested Modules
```

在上面的範例中，因此，可以直接呼叫函式，而不必在呼叫函式中包含模組。`use`

列舉也是模組之類的名稱空間的一種形式。因此，可以使用 在`use``use`

通過下面一個例子來理解：

```rust
#[derive(Debug)]  
enum Flagcolor  
{  
 Orange,  
 White,  
 Green,  
}  
use Flagcolor::{Orange,White,Green};  
fn main()  
{  
  let _o= Orange;  
  let _w= White;  
  let _g= Green;  
  println!("{:?}",_o);  
  println!("{:?}",_w);  
  println!("{:?}",_g);  
}
```

執行上面範例程式碼，得到以下結果：

```shell
orange
white
green
```

在上面的範例中，因此，可以直接使用列舉變體而不使用列舉名稱和名稱空間說明符。`Flagcolor``use`

## 使用* 運算子

```
*`運算子用於將所有專案放入範圍，這也稱為 如果使用`glob``glob
```

通過下面一個例子來理解這一點：

```rust
#[derive(Debug)]  
enum Color  
{  
  Red,  
  Yellow,  
  Green,  
  Orange,  
}  

use Color::*;  
fn main()  
{  
  let _red=Red;  
  let _yellow=Yellow;  
  let _green=Green;  
  let _orange=Orange;  
  println!("{:?}",_red);  
  println!("{:?}",_yellow);   
  println!("{:?}",_green);  
  println!("{:?}",_orange);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Red
Yellow
Green
Orange
```

在上面的範例中，`*``use`

## 使用super 關鍵字

`super`關鍵字用於從當前模組存取父模組，它使能夠存取父模組的私有功能。

```rust
mod a{  
    fn x() -> u8 {  
        5  
    }  

    pub mod example {  
        use super::x;  

        pub fn foo() {  
            println!("{}",x());  
        }  
    }
}  

fn main()  
{  
  a::example::foo();  
}
```

輸出結果如下 -

```shell
2
```

在上面的範例中，模組範例使用了參照其父模組的 由於這個原因，模組範例的`super``foo()``a`
