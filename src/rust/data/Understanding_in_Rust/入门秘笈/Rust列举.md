# Rust列舉

列舉是一種自定義資料型別，包含一些確定的值。它在列舉名稱之前使用 它還包括方法。`enum`

列舉的語法：

```rust
enum enum_name  
{  
  variant1,  
  variant2,  
  .
  .
}
```

在上面的語法中，`enum_name``variant1``variant2``..`

例如：

```rust
enum Computer_language{
  C,  
  C++,  
 Java,
}
```

在上面的例子中，`computer_language``C``C++``Java``computer_language`

## 列舉值

下面建立每個變數的範例，如下所示：

```rust
let c = Computer_language::C;  
let cplus = Computer_language::C++;  
let java = Computer_language::Java;
```

在上面的場景中，分別建立了包含值 列舉的每個變體都在其識別符號下命名，並使用雙冒號。這很有用，因為`C``C++``Java``c``cplus``java``Computer_language::C``Computer_language::C++``Computer_language::Java``Computer_language`

還可以在特定範例上定義函式，定義採用`Computer_language`

```rust
fn language_type(language_name::Computer_language);
```

任何變體都可以呼叫此函式：

```rust
language_type(Computer_language::C++);
```

通過一個例子來理解。

```c
enum Employee {  
    Name(String),  
    Id(i32),  
    Profile(String),  
}  
fn main() {  

    let n = Employee::Name("Hema".to_string());  
    let i = Employee::Id(2);  
    let p = Employee::Profile("Computer Engineer".to_string());  
    println!(" {:?} s {:?} b {:?}", n,i,p);  
}
```

執行上面範例程式碼，得到以下結果 -

```shell
Name("Hema") s Id(2) b Profile("Computer Engineer")
```

在上面的範例中，`Employee``Name(String)``Id(i32)``Profile(String)``:?`
