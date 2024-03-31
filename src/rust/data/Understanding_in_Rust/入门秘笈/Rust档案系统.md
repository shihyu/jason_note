# Rust檔案系統

------

模組形成層次結構，使專案變得更容易理解。Rust模組系統用於分割多個檔案，使得並非所有內容都位於`src/lib.rs` `src/main.rs`

檔案名：

```rust
mod A  
{  
     fn a()  
     {  
          // block of statements.  
     }  
}    
mod B  
{  
     fn b()  
     {  
            // block of statements.    
     }  
   mod C  
  {  
       fn c()  
       {  
             // block of statements.  
       }  
  }    
}
```

在上面的例子中，程式由三個模組組成，即 是`A``B``C``C``B`

給定檔案的模組層次結構是：

![img](https://tw511.com/upload/images/201910/20191014013928388.png)

如果模組包含許多函式並且函式非常冗長，則很難找到特定函式的程式碼。Rust通過提供模組系統提供了靈活性。可以擁有每個模組的單獨檔案，而不是放在同一個檔案中，即`src/lib.rs`

**要遵循的步驟：**
`A`

```rust
mod A;  
mod B  
{  
     fn b()  
     {  
            // block of statements.    
     }  
     mod C  
    {  
       fn c()  
       {  
             // block of statements.  
       }  
     }    
}
```

分號`;``A``A`

**模組A;**

```rust
mod A  
{  
     fn a()  
     {  
          // block of statements.  
     }  
}
```

現在建立包含模組A定義的外部檔案。外部檔案的名稱將命名為- 建立檔案後，在此檔案中寫入模組A的定義，該檔案先前已被刪除。

檔案名：

```rust
fn a()  
    // block of statements.
```

在這種情況下，不需要像在 並且，如果在這裡編寫`mod` `mod` `A`

Rust預設情況下會檢視`src/lib.rs`

現在，從檔案`src/lib.rs` `B` `B`

檔案名：

```rust
mod A;  
mod B;
```

**mod B;**

```rust
mod B  

    fn b()  
    {  
           // block of statements.    
    }  
  mod C  
 {  
      fn c()  
      {  
            // block of statements.  
      }  
 }
```

現在建立包含模組 外部檔案的名稱將命名為- 建立檔案後，在此檔案中寫入先前已刪除的模組`B` `src/B.rs` `B`

檔案名：`src/B.rs`

```rust
fn b()  
    {  
           // block of statements.    
    }  
      mod C  
     {  
          fn c()  
          {  
                // block of statements.  
          }  
     }
```

現在將從檔案`src/B.rs` `C` `C`

```rust
fn b()  
     {  
            // block of statements.    
     }  
mod C;
```

**mod C;**

```rust
mod C  
{  
     fn c()  
     {  
           // block of statements.  
     }  
}
```

現在建立包含模組 外部檔案的名稱將命名為 建立檔案後，在此檔案中寫入模組`C``src/C.rs``C`

檔案名稱:

```rust
fn c()  
      {  
            // block of statements.  
      }
```

> 注意：從模組B中提取模組C將導致編譯錯誤，因為 因此，`src/B.rs` `src/lib.rs` `src/B.rs` `src/B/mod.rs` `B`

**模組檔案系統規則：**

- 如果模組名為「server」且沒有子模組，則模組的所有宣告都可以放在檔案`server.rs`
- 如果名為「server」的模組包含子模組，則模組的所有宣告都將放在檔案`server/mod.rs`
