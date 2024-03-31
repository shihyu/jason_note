# Rust if in a let語句

在`let``if``if``let`

**if in a let語法**

```rust
Let variable_name= if condition{  
 //code blocks  
}else{  
 //code block  
}
```

在上面的語法中，如果條件為真，則將`if``false``else`

![img](https://tw511.com/upload/images/201910/20191014013905375.png)

**範例1**

下面來看一個簡單的例子。

```rust
fn main(){

 let a=if true  
       {  
          1  
       }  
       else  
       {  
           2  
       };  
 println!("value of a is: {}", a);
}
```

執行上面範例程式碼，得到以下結果 -

```shell
value of a is: 1
```

在此範例中，條件為真。因此，現在，`a``if``a``1`

下面再來看一個另一個簡單的例子。

```rust
fn main(){

 let a=if false  
       {  
          9  
       }  
       else  
       {  
           "yiibai"  
       };  
 println!("value of a is: {}", a);
}
```

執行上面範例程式碼，得到以下結果 -

```
Some errors occurred:E0308
```

在此範例中，因此，該程式丟擲錯誤，因為兩個塊都包含不同型別的值。`if``else`
