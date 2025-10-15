# Rust旅程

## HelloWorld
按照編程語言的傳統，學習第一門編程語言的第一個程序都是打印 Hello World！
下面根據我們的步驟創建 Rust 的 Hello World！程序：

**下面的命令操作，如果沒有特別說明，都是在shell下運行。本文為了簡單統一，所有例子都在 win10 的 powershell 下運行，所有命令都運行在`ps:`標識符之後**

- 創建一個 Doing 目錄和 helloworld.rs 文件

> ps: mkdir ~/Doing  
> ps: cd ~/Doing  
> ps: notepad helloworld.rs # 作者偏向於使用 sublime 作為編輯器  
> ps: subl helloworld.rs # 本章以後使用 subl 代替 notepad  

注意這裡用的後綴名是.rs，一般編程語言的代碼文件都有慣用的後綴名，比如：
    C語言是.c，java是.java，python是.py等等，**請務必記住Rust語言的慣用後綴名是.rs**（雖然用別的後綴名也能通過rustc的編譯）。

- 在 helloworld.rs 文件中輸入 Rust 代碼

```rust
fn main() {
    println!("Hello World!");
}
```

- 編譯 helloworld.rs 文件

> ps: rustc helloworld.rs  
> ps: rustc helloworld.rs -O # 也可以選擇優化編譯  

- 運行程序

> ps: ./helloworld.exe # windows 平臺下需要加 .exe 後綴  
> Hello World!  

沒有`ps:`前綴的表示為控制檯打印輸出。

我們已經用rust編寫第一個可執行程序，打印出了'hello world!'，很酷，對吧！
但是這段代碼到底是什麼意思呢，作為新手的你一定雲裡霧裡吧，讓我們先看一下這個程序：

1. 第一行中 fn 表示定義一個**函數**，main是這個函數的名字，花括號{}裡的語句則表示這個函數的內容。
2. 名字叫做**main**的函數有特殊的用途，那就是作為程序的入口，也就是說程序每次都從這個函數開始運行。
3. 函數中只有一句 ```println!("Hello World!");```，這裡```println!```是一個Rust語言自帶的**宏**，
這個宏的功能就是打印文本(結尾會換行)，而"Hello World!"這個用引號包起來的東西是一個**字符串**，就是我們要打印的文本。
4. 你一定注意到了```;```吧， 在Rust語言中，分號```;```用來把語句分隔開，也就是說語句的末尾一般用分號做為結束標誌。

## HelloRust

- 創建項目 hellorust

> ps: cargo new hellorust --bin

- 查看目錄結構

> ps: tree # win10 powershell 自帶有 tree 查看文件目錄結構的功能  
> └─hellorust  
> ----└─src

這裡顯示的目錄結構，在hellorust目錄下有 src 文件夾和 Cargo.toml 文件，同時這個目錄會初始化為 git 項目

- 查看Cargo.toml文件

> ps: cat Cargo.toml  
> [package]  
name = "hellorust"  
version = "0.1."  
authors = ["YourName <YourEmail>"]  
[dependencies]  

- 編輯src目錄下的main.rs文件

> ps: subl ./src/main.rs

cargo 創建的項目，在src目錄下會有一個初始化的main.rs文件，內容為：

```rust
fn main() {
    println!("Hello, world!");
}
```

現在我們編輯這個文件，改為：

```rust
fn main() {
    let rust = "Rust";
    println!("Hello, {}!", rust);
}
```

這裡的 `let rust = "Rust"` 是把 rust 變量綁定為 "Rust" ，
`println!("Hello, {}!", rust);`裡把 rust 變量的值代入到`"Hello, {}!"`中的`{}`。

- 編譯和運行

> ps: cargo build  
> ps: cargo build --release # 這個屬於優化編譯  
> ps: ./target/debug/hellorust.exe  
> ps: ./target/release/hellorust.exe # 如果前面是優化編譯，則這樣運行  
> ps: cargo run # 編譯和運行合在一起  
> ps: cargo run --release # 同上，區別是是優化編譯的  
