# Rust向量

向量是一種單一資料結構，可以在記憶體中彼此相鄰地儲存多個值。當有一個專案列表(例如：購物車中的資料項)時，向量很有用。

**要點：**

- 向量用於儲存相同型別的值。
- 向量由`Vec <T>`
- `Vec <T>`由標準庫提供，它可以儲存任何型別的資料，其中`T`
- 向量的資料在堆上分配。
- 向量是一個可增長的陣列意味著可以在執行時新增新元素。

`Vec <T>` ：當向量保持特定型別時，它在角括號中表示。

## 如何建立向量？

可以使用`Vec::new()`

```rust
Let v : Vec<i32> = Vec::new();
```

在上面的宣告中，`v``i32``Vec::new()`

還有另一種建立向量的方法：

Rust提供`vec!`

例如：

```rust
let v = vec![10,20,30,40,50];
```

注意：如果想重複向量的初始值，那麼還有另一種實現`vec`

```rust
let v = vec![2 ; i];
```

在上面的宣告中，向量`v``2``i`

## 存取元素

可以使用下標運算子`[]`

通過下面一個例子來理解：

```rust
fn main()  
{  
    let v =vec![20,30,40,50];  
    println!("first element of a vector is :{}",v[0]);  
    println!("Second element of a vector is :{}",v[1]);  
    println!("Third element of a vector is :{}",v[2]);  
    println!("Fourth element of a vector is :{}",v[3]);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
first element of a vector is :20
Second element of a vector is :30
Third element of a vector is :40
Fourth element of a vector is :50
```

存取向量元素的第二種方法是使用`get(index)``vector``Option <＆t>`

看下面一個範例程式碼 -

```rust
fn value(n:Option<&i32>)  
{  
    match n  
    {  
        Some(n)=>println!("Fourth element of a vector is {}",n),  
        None=>println!("None"),  
    }  
}  
fn main()  
{  
    let v =vec![20,30,40,50];  
    let a: Option<&i32>=v.get(3);  
    value(a);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Fourth element of a vector is 50
```

在上面的範例中，`get()`

## []和get()方法的區別：

當使用 因此，當嘗試存取不存在的元素時，程式就會崩潰。如果嘗試使用`[]``get()``None`

通過下面一個例子來理解這一點：

- get(index)函式

```rust
fn value(n:Option<&i32>)  
{  
 match n  
 {  
   Some(n)=>println!("Fourth element of a vector is {}",n),  
   None=>println!("None"),  
 }  
}  
fn main()  
{  
    let v =vec![20,30,40,50];  
    let a: Option<&i32>=v.get(7);  
    value(a);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
None
```

- []運算子

```rust
fn main()  
{  
    let v =vec![20,30,40,50];  
    println!("{}",v[8]);  
}
```

執行上面範例程式碼，得到以下結果 -

![img](https://tw511.com/upload/images/201910/20191014013932390.png)

## 疊代向量中的值

如果想要存取向量的每個元素，那麼可以疊代向量的元素，而不是使用索引來存取向量的特定元素。

可以使用`for`

下面來看一個不可變參照的簡單範例：

```rust
fn main()  
{  
    let v =vec![20,30,40,50];  
    print!("Elements of vector are :");  
    for i in v  
    {  
        print!("{} ",i);  
    }  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Elements of vector are :20 30 40 50
```

下面來看一個可變參照的簡單範例：

```rust
fn main()  
{  
    let mut v =vec![20,30,40,50];  
    print!("Elements of vector are :");  
    for i in &mut v  
    {  
        *i+=20;  
        print!("{} ",i);  
    }  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Elements of vector are :20 30 40 50
```

在上面的例子中，改變向量的值。因此，向量是可變參考。在`i``*``v`

## 更新向量

當建立向量時，使用 在向量的末尾插入新元素。`push()``push()`

下面來看看一個簡單的例子：

```rust
fn main()  
{  
  let mut v=Vec::new();  
  v.push('j');  
  v.push('a');  
  v.push('v');  
  v.push('a');  
  for i in v  
  {  
    print!("{}",i);  
  }  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
java
```

在上面的範例中，向量`push()``v`

## 刪除向量

當向量超出範圍時，它會自動刪除或從記憶體中釋放。通過一個簡單的場景來理解這一點：

```rust
fn main()  
{  
   let v = !vec[30,40,50];  
} # => v 在這裡被釋放，因為它超出了範圍。
```

在上面的場景中，當向量超出範圍時釋放向量意味著將移除向量中存在的所有元素。

## 使用Enum儲存多種型別

向量可以儲存相同型別的元素，這是向量的一個很大的缺點。列舉是一種自定義資料型別，它包含相同列舉名稱下的各種型別的變體。當想要將元素儲存在不同型別的向量中時，使用列舉型別。

下面通過一個例子來理解這一點：

```rust
#[derive(Debug)]  
enum Values {  
   A(i32),  
   B(f64),   
   C(String),  
}  

fn main()   
{  
     let v = vec![Values::A(5),   
     Values::B(10.7),Values::C(String::from("Yiibai"))];  
     for i in v  
    {  
       println!("{:?}",i);  
     }  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
A(5)
B(10.7)
C(Yiibai)
```

**在向量中使用列舉的優點：**

- Rust在編譯時知道向量元素的型別，以確定每個元素需要多少記憶體。
- 當向量由一個或多個型別的元素組成時，對元素執行的操作將導致錯誤，但使用帶有匹配的列舉將確保可以在執行時處理每個可能的情況。
