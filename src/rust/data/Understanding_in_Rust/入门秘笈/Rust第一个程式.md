# Rust第一個程式

在本文中，使用Rust語言編寫簡單的程式，以瞭解如何編寫，儲存和編譯Rust程式。現在，開啟記事本檔案並編寫以下程式碼：

```rs
fn main(){
    println!("Hello, world!");
}
```

將上面內容儲存到一個檔案：`rustc hello.rs`

```shell
Hello, world!
```

- `main()`：函式用大括號 函式不包含任何引數，也不返回任何值。`main()``main()``{}``main()`
- `println!`：這是一個Rust巨集。如果它呼叫該函式，則它不包含符號：`'!'`
- `"Hello World"`：它是作為引數傳遞給`println!`

## 建立，編譯和執行程式的過程

1. 開啟記事本檔案並將程式碼寫入記事本檔案中。
2. 使用`.rs`
3. 開啟命令提示字元
4. 設定目錄的路徑，假設專案位於`/home/hema/worsp/rust`
5. 使用`rustc`
6. 最後，使用命令`./filename`

```shell
hema@yiibai:~/worsp/rust$ rustc hello.rs && ./hello
Hello World!
```

> 注：如果有遇到「error: could not exec the linker`link.exe`
