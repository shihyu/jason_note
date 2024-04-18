# Rust loop迴圈

如果想要多次執行語句塊，那麼迴圈概念就屬於這個角色。迴圈執行迴圈體記憶體在的程式碼直到結束，並從啟動開始立即重新開始。

Rust有三種迴圈：

- loop迴圈
- for迴圈
- while迴圈

## loop迴圈

`loop`不是條件迴圈。它是一個關鍵字，告訴Rust一次又一次地執行程式碼塊，直到除非明確地手動停止迴圈。

**loop迴圈**

```rust
loop{  
  //block statements  
}
```

在上面的語法中，塊語句被無限次執行。

迴圈流程圖：

![img](https://tw511.com/upload/images/201910/20191014013907376.png)

下面來看看一個無限迴圈的簡單例子 -

```
fn main(){
     loop  
     {  
         println!("Hello Yiibai");  
    }
}
```

執行上面範例程式碼，得到以下結果 -

```
Hello Yiibai
Hello Yiibai
Hello Yiibai
Hello Yiibai
.
.
.
infinite times
```

在這個例子中，「Hello Yiibai」字串一遍又一遍地列印，直到除非手動停止迴圈。通常，「ctrl + c」命令用於從迴圈終止。

#### 迴圈終止

```
break`關鍵字用於從迴圈終止。如果未使用`break
```

下面來看一個簡單的例子 -

```rust
fn main()  

 let mut i=1;  
 loop  
 {
       println!("Hello Yiibai");  
       if i==7   
       {  
         break;  
       }  
     i+=1;  
 }
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Hello Yiibai
Hello Yiibai
Hello Yiibai
Hello Yiibai
Hello Yiibai
Hello Yiibai
Hello Yiibai
```

在上面的例子中，`i`
