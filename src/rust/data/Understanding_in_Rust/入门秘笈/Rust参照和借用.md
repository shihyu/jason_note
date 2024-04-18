# Rust參照和借用

參照是作為引數傳遞給函式的地址。借用就像我們借一些東西，如果已經完成借用，需要還給原所有者。參照和借用是相互的，即當參照被釋放時，借用也結束。

## 為什麼要借用？

使用借用概念的原因如下：

- 借用允許對單個資源進行多次參照，但仍然遵守「單一所有者」。
- 參照就像C中的指標一樣。
- 參照是一個物件。參照有兩種型別，即可變參照和不可變參照。在複製不可變參照時移動可變參照。

下面通過一個例子來理解這一點。

```rust
 fn main()  
{  
 let str=String::from("Yiibai");  
 let len=calculate_length(&str);  
 println!("length of the string {}",len);  
}  
fn calculate_length(s:&String)->usize  
{  
  s.len()  
}
```

執行上面範例程式碼，得到以下結果 -

```
length of the string 6
```

在上面的範例中，`calculate_length()``str`

```rust
let str=String::from("Yiibai");  
let len=calculate_length(&str);
```

在上面的場景中，因此，即使參照超出範圍，也不會刪除參照指向的值。`&str``str`

```rust
fn calculate_length(s:&String)->usize  
s.len()
```

在上面的例子中，變數 當變數作為函式的參照而不是實際值傳遞時，不需要返回值到返回所有權。`s``main()`

下面嘗試修改借用的值。

```rust
fn main()  
{  
 let x=1;  
 value_changed(&x)  
}  
fn value_changed(y:&i32)  
{  
 *y=9;  
}
```

以下是上述程式的輸出：

![img](https://tw511.com/upload/images/201910/20191014013915384.png)

在上面的範例中，它會引發錯誤，因為 因此，無法改變`&x``y`

## 可變參照

可以通過使用可變參照來修復上述錯誤。可變參照是那些可以改變的參照。下面通過一個例子來理解這一點。

```rust
fn main()  
{  
 let mut x=1;  
 value_changed(&mut x);  
 println!("After modifying, the value of x is {}",x);  
}  
fn value_changed(y:&mut i32)  
{  
 *y=9;  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
After modifying, the value of x is 9
```

在上面的例子中，建立了一個可變參照，即 現在，可以更改 分配 因此，`&mut x``y``&i32``y``9``* y = 9``x``9`

## 可變參照的限制

只能對特定範圍內的一段資料進行一次可變參照。例如：

```rust
let mut str=String::from("Yiibai");  
let a= &mut str;  
let b= &mut str;
```

在上面的場景中，編譯器丟擲一個錯誤，因為它包含兩個在Rust語言中不可能的可變參照。如果程式中存在不可變參照，那麼程式中就不能有可變參照。例如：

```rust
let mut str=String::from("Yiibai");  
let a= &str;  
let b=&str;  
let c=&mut str;
```

在上面的場景中，編譯器丟擲一個錯誤，因為當有一個不可變參照時，不能有一個可變參照。
