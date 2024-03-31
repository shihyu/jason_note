# Rust結構體方法語法

方法類似於函式，因為它們在 方法還包含引數和返回值。但是，當在 這些方法的第一個引數始終是`start``then``fn``struct``self`

## 定義方法

在`struct`

```rust
struct Square  
{  
    a : u32,  
}  
impl Square  
{  
    fn area(&self)->u32  
    {  
        self.a * self.a  
    }  
}  

fn main()  
{  
    let square = Square{a:10};  
    print!("Area of square is {}", square.area());  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Area of square is 100
```

當在`struct``impl`

```rust
impl Square  
{  
    fn area(&self)->u32  
    {  
        self.a * self.a  
    }  
}
```

第一個引數是簽名中的`self`

在這裡，使用方法語法來呼叫 方法語法是一個範例，後跟點運算子，方法名稱，引數和任何引數。`area()`

```rust
square.area();
square`是範例，`area()
```

> 注意：如果想要更改呼叫該方法的範例，那麼使用`&mut self``&self`

**方法語法的優點：**

使用方法語法而不是函式的主要優點是，與範例相關的所有資料都放在`impl``impl`
