# Rust Box<T>

`Box <T>`是一個智慧指標，指向在型別為T的堆上分配的資料。允許將資料儲存在堆而不是堆疊上。是一個擁有的指標。除了將資料儲存在堆上之外，當`Box <T>`

`Box <T>`
`Box`
`Box`

使用 主要是，下面通過一個簡單的例子來理解這一點：`Box <T>`
`Box <T>`

```rust
fn main()  
{  
  let a = Box :: new(1);  
  print!("value of a is : {}",a);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
value of a is : 1
```

在上面的例子中，如果存取 當程式結束時，儲存在堆疊中，它指向的資料儲存在堆上。`a``1``Box``Box``Box``Box`

下面來看看上面例子的圖解表示：

![img](https://tw511.com/upload/images/201910/20191014013950410.png)

**Cons列表**

- `Cons`代表「構造功能」。
- `Cons`列表是一個資料結構，用於從兩個引數構造一個新對，這對稱為`List`
- 假設有兩個元素`x` `y` `cons` `cons 「x到y」` `x` `y`
- `Cons`列表包含兩個元素，即當前項和最後一項。由於`Nil` `Nil`

現在，建立包含`cons`

```rust
enum List  
{  
   cons(i32, List),  
   Nil,  
}
```

在上面的程式碼中，建立了`List` `i32` `cons`

現在，在以下範例中使用上面的`List`

```rust
enum List {  
    Cons(i32, List),  
    Nil,  
}  
use List::{Cons, Nil};  
fn main()  
{  
  let list = List::Cons(1,Cons(2,Cons(3,Nil)));  
  for i in list.iter()  
  {  
    print!("{}",i);  
  }  
}
```

執行上範例程式碼，得到以下結果 -

![img](https://tw511.com/upload/images/201910/20191014013951411.png)

在上面的範例中，Rust編譯器丟擲錯誤「具有無限大小」，因為List型別包含遞迴的變體。因此，Rust無法找出儲存List值所需的空間。使用`Box <T>`

## 使用`Box <T>`

Rust無法確定儲存遞迴資料型別需要多少空間。Rust編譯器在前一種情況下顯示錯誤：

```shell
= help: insert indirection (e.g., a 'Box', 'Rc', or '&') at some point to make 'List' representable
```

在上面的例子中，可以使用 指標的大小在程式執行期間不會改變。指標指向將儲存在堆上而不是 指標可以直接放在`Box <T>` `Box <T>` `Box <T>` `Box <T>` `cons` `Box <T>` `cons`

![img](https://tw511.com/upload/images/201910/20191014013951412.png)

下面來看一個簡單的例子 -

```rust
#[derive(Debug)]   
enum List {  
    Cons(i32, Box<List>),  
    Nil,  
}  
use List::{Cons, Nil};  
fn main()  
{  
  let list = Cons(1,Box::new(Cons(2,Box::new(Cons(3,Box::new(Nil))))));  

    print!("{:?}",list);  

}
```

執行上面範例程式碼，得到以輸出結果如下 -
```
  Cons(1, Cons(2, Cons(3, Nil)))
```
