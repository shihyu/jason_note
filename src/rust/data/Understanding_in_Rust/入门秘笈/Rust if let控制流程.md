# Rust if let控制流程

```
if let`語法用於組合 運算子和`if``let``「match」``「if let」
```

**匹配運算子的範例**

```rust
fn main()  
{  
    let a = Some(5);  
    match a {  
    Some(5) => println!("five"),  
    _ => (),  
}}
```

執行上面範例程式碼，得到以下結果 -

```
five
```

在上面的範例中，匹配運算子在值等於 執行第一個變數後，如果使用`Some(5)``_ =>()``if``match`

**if let範例**

```rust
fn main()  
{  
    let a=Some(3);  
    if let Some(3)=a{  
     println!("three");  
    }
}
```

執行上面範例程式碼，得到以下結果 -
```shell
three
```
