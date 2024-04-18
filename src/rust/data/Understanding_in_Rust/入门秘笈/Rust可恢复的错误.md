# Rust可恢復的錯誤

可恢復的錯誤是那些完全停止程式並不嚴重的錯誤。可以處理的錯誤稱為可恢復錯誤。它由 結果
`Result <T，E>` `<T，E>` `OK <T>` `Err <E>`

```
OK <T>`：'T'是一種值，它在成功情況下時返回 ：'E'是一種錯誤，它在失敗情況下時返回`OK`
`Err <E>``ERR
Enum Result<T,E>  
{  
    OK<T>,  
    Err<E>,  
}
```

- 在上面的例子中，`Result` `OK <T>＆Err <E>` `'T'` `'E'`
- `'T'`是一種值，它將在成功的情況下返回，而`'E'`
- `Result`包含泛型型別引數，因此在成功和失敗值可能不同的許多不同情況下使用標準庫中定義的結果型別和函式。

下面來看一個返回`Result`

```rust
use std::fs::File;  
 fn main()   
{  
     let f:u32 = File::open("vector.txt");  
}
```

執行上面範例程式碼，得到以下結果 -

![img](https://tw511.com/upload/images/201910/20191014013940399.png)

在上面的範例中，Rust編譯器顯示該型別不匹配。是 上面的輸出顯示成功值的型別是`'f'` `u32` `File::open` `Result <T，E>` `std::fs::File` `std::io::Error`

**注意：**

- `File::open`返回型別是成功值或失敗值。如果 結果列舉提供此資訊。`File::open` `File::open`
- 如果`File::open` `f` `OK` `File::open` `Err`

## 匹配表示式以處理結果變體

下面來看看一個匹配表示式的簡單範例：

```c
use std::fs::File;  
fn main()  
{  
   let f = File::open("vector.txt");  
   match f   
   {  
       Ok(file) => file,  
       Err(error) => {  
       panic!("There was a problem opening the file: {:?}", error)  
     },  
   }; 
}
```

執行上面範例程式碼，得到以下結果 -

![img](https://tw511.com/upload/images/201910/20191014013940400.png)

**程式說明**

- 在上面的範例中，可以直接存取列舉變體，而無需在`OK` `Err` `Result::`
- 如果結果正常，則返回檔案並將其儲存在 在匹配之後，可以在檔案中執行讀取或寫入操作。`'f'`
- 匹配對 如果`Err` `Result` `Error` `panic!`

#### 出錯時Error:unwrap()

- 結果 其中一種方法是 方法是匹配表示式的快捷方法。方法和匹配表示式的工作方式是一樣的。`<T，E>``unwrap()``unwrap()``unwrap()`
- 如果`Result` `OK` `unwrap()` `OK`
- 如果`Result` `Err` `unwrap()` `panic!`

下面來看一個簡單的範例：

```rust
use std::fs::File;  

fn main()  
{  
     File::open("hello.txt").unwrap();  
}
```

執行上面範例程式碼，得到以下結果：

![img](https://tw511.com/upload/images/201910/20191014013940401.png)

在上面的例子中，`unwrap()` `panic!`

#### Error: expect()

- `expect()`方法的行為方式與`unwrap()` `panic!`
- `expect()`和 因此，可以說`unwrap()` `expect()` `unwrap()` `expect()` `panic!`

下面看看一個簡單範例 -

```shell
use std::fs::File;  
fn main()  
{  
     File::open("hello.txt").expect("Not able to find the file hello.txt");  
}
```

執行上面範例程式碼，得到以下結果 -

![img](https://tw511.com/upload/images/201910/20191014013940402.png)

在上面的輸出中，錯誤訊息顯示在程式中指定的輸出螢幕上，即 如果包含多個`「無法找到檔案hello.txt」` `unwrap()` `unwrap()` `panic!`

## 傳播錯誤

傳播錯誤是一種將錯誤從一個函式轉發到另一個函式的機制。錯誤傳播到呼叫函式，其中有更多資訊可用，以便可以處理錯誤。假設有一個名為 想要建立一個程式來讀取檔案，先參考下面一個簡單的例子：

```rust
use std::io;  
use std::io::Read;  
use std::fs::File;  
fn main()  
{  
  let a = read_username_from_file();  
  print!("{:?}",a);  
}  
fn read_username_from_file() -> Result<String, io::Error>   
{  
    let f = File::open("a.txt");  
    let mut f = match f {  
    Ok(file) => file,  
    Err(e) => return Err(e),  
    };  
    let mut s = String::new();  
    match f.read_to_string(&mut s) {  
        Ok(_) => Ok(s),  
        Err(e) => Err(e),  
    }  
}
```

程式說明 -

- `read_username_from_file()`函式返回`Result <T，E>` `'T'` `String` `'E'` `io` `Error`
- 如果函式成功，則返回一個包含`String` `OK` `Err`
- 函式中首先呼叫 如果`File::open` `File::open` `Err` `File::open``f`
- 如果 如果`File::open` `String` `read_to_string()`
- 假設我們有一個名為 因此，該程式讀取檔案

#### 傳播錯誤的捷徑：`?`

使用 運算子是匹配表示式的替換意味著 假設有一個名為 想要建立一個程式來對該檔案執行讀取操作。`?` `?` `?` `「yiibai」`

看看下面一個簡單的例子。

```c
use std::io;  
use std::io::Read;  
use std::fs::File;  
fn main()  
{  
  let a = read_username_from_file();  
  print!("{:?}",a);  
}  
fn read_username_from_file() -> Result<String, io::Error>   
{  
   let mut f = File::open("a.txt")?;  
   let mut s = String::new();  
   f.read_to_string(&mut s)?;  
  Ok(s)  
}
```

在上面的例子中，如果`?` `Result` `Result` `OK` `OK` `Result` `Err`

#### ?運算子和匹配表示式的區別

- 使用`?` `from trait`
- 當`?`
- 如果沒有錯誤發生，那麼`?` `OK` `Err`
- 它使函式的實現更簡單。

#### 鏈方法在？運算子之後呼叫

甚至可以通過在`?`

下面來看一個簡單的例子：

```rust
use std::io;  
use std::io::Read;  
use std::fs::File;  
fn main()  
{  
  let a = read_username_from_file();  
  print!("{:?}",a);  
}  
fn read_username_from_file() -> Result<String, io::Error>   
{  
    let mut s = String::new();  
   File::open("a.txt")?.read_to_string(&mut s)?;  
   Ok(s)  
}
```

**程式說明**

在上面的例子中，將 如果兩個函式(即`read_to_string()` `File::open("a.txt")?` `read_to_string()` `File::open("a.txt")` `OK`

#### ?運算子的限制

`?`運算子只能在返回 運算子與匹配表示式的工作方式類似。匹配表示式僅適用於`Result` `?` `Result`

下面通過一個簡單的例子來理解這一點。

```rust
use std::fs::File;  
fn main()   
{  
    let f = File::open("a.txt")?;  
}
```
