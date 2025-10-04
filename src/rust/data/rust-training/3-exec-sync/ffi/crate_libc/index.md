
源碼地址：https://github.com/rust-lang/libc
文檔地址：https://docs.rs/libc/0.2.69/libc/index.html

使用方法

```toml
[dependencies]
libc = "0.2"
```

libc導出底層 C 庫的
- C 類型，比如 typedefs, 原生類型，枚舉，結構體等等
- C 常量，比如使用 #define 指令定義的那些常量
- C 靜態變量
- C 函數（按它們的頭文件中定義的函數簽名來導出）
- C 宏，在 Rust 中會實現為 #[inline] 函數

另外，libc 中導出的所有 C struct 都已經實現了 Copy 和 Clone trait.

可以通過 libc crate 來使用 C 標準庫中的函數。例如，使用 fork 來創建線程。

```go
fn main() {
    unsafe {
        let pid = libc::fork();

        if pid > 0 {
            println!("Hello, I am parent thread: {}", libc::getpid());
        }
        else if pid == 0 {
            println!("Hello, I am child thread: {}", libc::getpid());
            println!("My parent thread: {}", libc::getppid());
        }
        else {
            println!("Fork creation failed!");
        }
    }
}
```


## 參考
- [Rust FFI 編程 - libc crate](https://cloud.tencent.com/developer/article/1620862)