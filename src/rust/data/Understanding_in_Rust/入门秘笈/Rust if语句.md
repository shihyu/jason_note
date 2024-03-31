# Rust if語句

```
if`語句確定條件是否為真。如果條件為`true``if``if
```

表示`if`

- if塊
- if-else塊
- if else-if階梯塊
- 巢狀if語句

## if語句

`if`語句塊的語法 -

```rust
if condition  
{  
    //block statements;  
}
```

在上面的語法中，如果條件為真，則執行塊語句，否則跳過`if`

`if`語句的流程圖 -

![img](https://tw511.com/upload/images/201910/20191014013903372.png)

**範例：**
`if`

```rust
fn main(){

 let a=1;  
 if a==1  
 {  
      println!("a is equal to 1");  
 }
}
```

執行上面範例程式碼，得到以下結果：

```
a is equal to 1
```

在這個例子中，因此，`a``1``if``println!`

## if-else語句

如果條件為真，則執行 如果條件為假，則跳過`if``else``if``else`

**if-else語句的語法**

```
if condition  
{  
   //block statements  
}else{  
    //block statements  
}
```

**if-else的流程圖**

![img](https://tw511.com/upload/images/201910/20191014013903373.png)

下面來看看一個`if-else`

```rust
fn main()  
{  
  let a=3;  
  let b=4;  
  if a>b  
  {  
     println!("a is greater than b");  
  }  
  else  
   {  
     println!("a is smaller than b");   
   }  
}
```

執行上面範例程式碼，得到以下結果 -

```
a is smaller than b
```

在該範例中，變數 因此，執行`a``3``a``b``else`

## else-if語句

如果要檢查多個條件，則可使用`else-if`

`else-if`語句的語法 -

```
if condition 1  
{  
  //block statements  
}else if condition 2  
{  
  //block statements  
}   
.  
.  
else{  
//block statements  
}
```

在上面的語法中，Rust為第一個真實條件執行塊，當匹配到第一個真條件時，它就不會執行其餘的塊。

`else if`語句塊的流程圖 -

![img](https://tw511.com/upload/images/201910/20191014013903374.png)

下面來看一個`else-if`

```rust
fn main(){

 let num= -5;  
 if num>0  
 {  
   println!("number is greater than 0");  
 }  
 else if num<0  
 {  
   println!("number is less than 0 ");  
 }  
 else  
 {  
   println!("number is not equal to 0");  
 }
}
```

執行上面範例程式碼，得到以下結果 -

```shell
number is less than 0
```

在此範例中，變數 因此，`num``-5``num``0``else if`

## 巢狀if-else語句

當 巢狀`if-else``if``else``if-else`
`if-else`

```rust
if condition 1  
{  
   // 巢狀if/else塊  
   if condition 2  
    {  
         //block statements  
    }else  
    {  
        //block statements  
    }  
}else{  
   //block statements  
}
```

下面來看一個巢狀`if-else`

```rust
fn main(){

 let a=5;  
 let b=6;  
 if a!=b  
 {  
   if a>b  
   {  
     println!("a is greater than b");  
   }else{  
      println!("a is less than b");  
   }  
 }  

 else  
 {  
      println!("a is equal to b");  
 }
}
```

執行上面範例程式碼，得到以下結果 -

```shell
a is less than b
```

在此範例中，因此，控制進入 因此，執行`a``b``if``a``b``else``if`
