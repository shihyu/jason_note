# Rust for迴圈

```
for`迴圈是條件迴圈，即迴圈執行特定次數。Rust語言中 執行`for``for
```

for迴圈的語法 -

```rust
for var in expression  
{  
    //block statements  
}
```

在上面的語法中，表示式可以轉換為疊代器，疊代器遍歷資料結構的元素。在每次疊代中，都從疊代器中獲取值。當沒有剩餘值被提取時，迴圈結束。

下面來看一個簡單的例子。

```rust
 fn main()  
{  

  for i in 1..11  
  {  
    print!("{} ",i);  
  }   
}
```

執行上面範例程式碼，得到以下結果 -

```shell
1 2 3 4 5 6 7 8 9 10
```

在上面的範例中，上限是不包含的，因此迴圈將列印`1..11``1``10`

下面再來看一個簡單的例子。

```rust
fn main()  
{  
    let mut result;  
    for i in 1..11  
    {  
        result=2*i;  
        println!("2*{}={}",i,result);  
    }  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
2*1=2
2*2=4
2*3=6
2*4=8
2*5=10
2*6=12
2*7=14
2*8=16
2*9=18
2*10=20
```

在上面的例子中，`for``2`

下面來看另一個簡單的例子。

```rust
fn main(){
 let fruits=["mango","apple","banana","litchi","watermelon"];  
 for a in fruits.iter()  
 {  
   print!("{} ",a);  
 }
}
```

執行上面範例程式碼，得到以下結果 -

```
mango apple banana litchi watermelon
```

在上面的例子中，當它到達陣列的最後一個元素，那麼迴圈就結束了。`iter()``fruits`

**while迴圈和for迴圈的區別：因此，可以說**
`while``for``for`
