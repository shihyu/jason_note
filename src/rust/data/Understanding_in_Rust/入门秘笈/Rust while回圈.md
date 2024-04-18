# Rust while迴圈

`while-loop`是一個條件迴圈。當程式需要評估條件時，則使用條件迴圈。當條件為真時，它執行迴圈，否則它終止迴圈。

**while迴圈的語法**

```
while condition  
//block statements;
```

在上面的語法中，如果條件為真，則執行塊語句，否則終止迴圈。Rust提供了這個內建構造，可以與`while``loop``if``else``break`

**while迴圈流程圖**

![img](https://tw511.com/upload/images/201910/20191014013910377.png)

下面來看一個簡單的例子 -

```rust
 fn main()  
{  
  let mut i=1;  
  while i<=10  
    {  
       print!("{}", i);  
       print!(" ");  
       i=i+1;  
    }  
}
```

執行上面範例程式碼，得到以下輸出結果 -

```
1 2 3 4 5 6 7 8 9 10
```

在上面的例子中，迴圈執行直到`i``i``while``i``10``10`

下面來看一個簡單的例子

```rust
fn main()  
{  
  let array=[10,20,30,40,50,60];  
  let mut i=0;  
  while i<6  
  {  
    print!("{}",array[i]);  
    print!(" ");  
    i=i+1;  
  }  
}
```

輸出結果 -

```
10 20 30 40 50 60
```

在上面的範例中，使用`while`

`while`迴圈的缺點：

- 如果索引長度不正確，迴圈可能會導致問題。
- 當編譯器新增執行時程式碼以通過此迴圈對每次疊代執行條件檢查時，它也很慢。
