# Rust錯誤處理

錯誤處理是Rust確定出錯的可能性並確認在程式碼進行編譯之前採取某些操作的機制。此機制使程式更加健壯，因為能夠在部署生產程式碼之前發現並處理錯誤。Rust程式設計語言不包含異常。

Rust中有兩種型別的錯誤：

- 不可恢復的錯誤。
- 可恢復的錯誤。

![img](https://tw511.com/upload/images/201910/20191014013935392.png)

- **可恢復的錯誤：完全停止該過程的可恢復錯誤並不嚴重。它由 可恢復錯誤的範例是「找不到檔案」。是通用引數。這是一種值，在成功的情況下返回一個'OK'變數。這是一種錯誤型別，在具有**`Result <T，E>``T＆E`
  `T->`
  `E->``Err`
- **不可恢復的錯誤：例如：「除以零」是不可恢復錯誤的範例。**`!`

#### 可恢復錯誤與不可恢復錯誤

可恢復錯誤是可以某種方式恢復的錯誤，而不可恢復錯誤是無法以任何方式恢復的錯誤。下面來看一下預期行為的情景：

```
"100".parse();
```

在上述情況下，因此，它是一個可恢復的錯誤。`"100"`

**意外的行為**

![img](https://tw511.com/upload/images/201910/20191014013935393.png)

**assert! 如果它不正確和錯誤，則程式停止執行。**

下面來看一個簡單的例子：

```rust
fn main()  
{  
    let x : bool = false;  
    assert!(x==true);  
}
```

執行上面範例程式碼，得到以下結果：

![img](https://tw511.com/upload/images/201910/20191014013935394.png)

在上面的例子中，因此，在執行時`x` `false` `assert!` `assert!` `panic!`

**unreachable! 此巨集很有用，因為編譯器無法確定無法存取的程式碼。在執行時由**

下面來看一個簡單的例子：

```rust
enum Value  
{  
  Val,  
}  

fn get_number(_:Value)->i32  
{   
   5  
}  
fn find_number(val:Value)-> &'static str  
{  
  match get_number(val)  
  {  
    7 => "seven",  
    8=> "eight",  
    _=> unreachable!()  
  }  
}  

fn main()  
{  
  println!("{}", find_number(Value::Val));  
}
```

執行上面範例程式碼，得到以下結果 -

![img](https://tw511.com/upload/images/201910/20191014013936395.png)

在上面的範例中，因此，`get_number()` `5` `unreachable!` `panic!`
