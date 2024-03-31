# Rust公開函式

`pub`關鍵字用於宣告的開頭，以便外部函式可以存取該函式。

**以下是私有規則：**

- 如果任何函式或模組是公共的，則任何父模組都可以存取它。
- 如果任何函式或模組是私有的，則可以通過其直接父模組或父項的子模組來存取它。
- 通過下面一個簡單的例子來理解這一點：

```rust
mod outer  
{  
   pub fn a()  
   {  
     println!("function a");          
   }  
   fn b()  
   {  
      println!("function b");  
   }  

mod inner  
{  
  pub fn c()  
  {  
    println!("function c");  
  }  
  fn d()  
  {  
    println!("function d");  
  }  
}  
}  
fn main()  
{  
  outer::a();  
  outer::b();  
  outer::inner::c();  
  outer::inner::d();  
}
```

執行上面範例程式碼，得到以下結果 -

![img](https://tw511.com/upload/images/201910/20191014013929389.png)

在上面的範例中，因此，`main()``outer``main()``outer`

函式`a()``outer::a()``main()``outer::b()`

```
main()`函式無法存取內部模組，因為它是私有的。模組沒有子模組，因此只能由其父模組(即`inner``outer
```
