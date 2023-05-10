

# Rust 中的 bin, lib, rlib, a, so 概念介紹

出處:https://cloud.tencent.com/developer/article/1583081



寫了這麼久的 Rust 程式碼了，可能很多人還對 Rust 的編譯後的檔案格式不是很清晰。本篇我們就來理一下，Rust 中的 bin, lib, rlib, a, so 是什麼，如何生成，以及其它一些細節。

### **從 cargo new 說起**

我們建立一個新工程，通常從下面兩句入手：

```javascript
cargo new foobar
```

複製

或

```javascript
cargo new --lib foobar
```

複製

前者建立一個可執行工程，而後者建立一個庫工程。

實際上，你去探索上述命令列生成的檔案，發現它們的 Cargo.toml 完全一樣，區別僅在於 src 目錄下，可執行工程是一個 main.rs，而庫工程是一個 lib.rs。

這是因為 main.rs 和 lib.rs 對於一個 crate 來講，是兩個特殊的檔案名稱。rustc 內建了對這兩個特殊檔案名稱的處理（當然也可以通過 Cargo.toml 進行組態，不詳談），我們可以認為它們就是一個 crate 的入口。

可執行 crate 和庫 crate 是兩種不同的 crate。下面我們就來一併說一下它們的兄弟姐妹及其之間的異同。

### **crate type**

執行

```javascript
rustc --help|grep crate-type
```

複製

可得到如下輸出

```javascript
       --crate-type [bin|lib|rlib|dylib|cdylib|staticlib|proc-macro]
```

複製

才發現，原來有這麼多種 crate type。下面挨個看一下。

#### **bin**

二進制可執行 crate，編譯出的檔案為二進制可執行檔案。必須要有 main 函數作為入口。這種 crate 不需要在 Cargo.toml 中或 --crate-type 命令列參數中指定，會自動識別。

#### **lib**

庫 crate。它其實並不是一種具體的庫，它指代後面各種庫 crate 中的一種，可以認為是一個代理名稱（alias）。

通常來講，如果什麼都不組態，默認指的是 rlib, 會生成 .rlib 的檔案。

#### **rlib**

rlib 是 Rust Library 特定靜態中間庫格式。如果只是純 Rust 程式碼項目之間的依賴和呼叫，那麼，用 rlib 就能完全滿足使用需求。

rlib 實現為一個 ar 歸檔檔案。

```javascript
> file target/debug/libfoobar.rlib
target/debug/libfoobar.rlib: current ar archive
```

複製

rlib 中包含很多 metadata 資訊（比如可能的上游依賴資訊），用來做後面的 linkage。

在 Cargo.toml 中組態：

```javascript
[lib]
name = "foobar"
crate-type = ["rlib"]
```

複製

可以指定生成 rlib，但是一般沒必要設定，因為默認 lib 就是 rlib。

rlib 是平臺（Linux, MacOS, Windows ...）無關的。

#### **dylib**

動態庫。

在 Cargo.toml 中組態：

```javascript
[lib]
name = "foobar"
crate-type = ["dylib"]
```

複製

會在編譯的時候，生成動態庫（Linux 上為 .so, MacOS 上為 .dylib, Windows 上為 .dll）。

動態庫是平臺相關的庫。動態庫在被依賴並連結時，不會被連結到目標檔案中。這種動態庫只能被 Rust 寫的程序(或遵循 Rust 內部不穩定的規範的程序)呼叫。這個動態庫可能依賴於其它動態庫（比如，Linux 下用 C 語言寫的 [PostgreSQL](https://cloud.tencent.com/product/postgresql?from=10680) 的 libpq.so，或者另一個編譯成 "dylib" 的 Rust 動態庫）。

#### **cdylib**

C規範動態庫。

在 Cargo.toml 中組態：

```javascript
[lib]
name = "foobar"
crate-type = ["cdylib"]
```

複製

與 dylib 類似，也會生成 .so, .dylib 或 .dll 檔案。但是這種動態庫可以被其它語言呼叫（因為幾乎所有語言都有遵循 C 規範的 FFI 實現），也就是跨語言 FFI 使用。這個動態庫可能依賴於其它動態庫（比如，Linux 下用 C 語言寫的 PostgreSQL 的 libpq.so）。

#### **staticlib**

靜態庫。

在 Cargo.toml 中組態：

```javascript
[lib]
name = "foobar"
crate-type = ["staticlib"]
```

複製

編譯會生成 .a 檔案（在 Linux 和 MacOS 上），或 .lib 檔案（在 Windows 上）。

編譯器會把所有實現的 Rust 庫程式碼以及依賴的庫程式碼全部編譯到一個靜態庫檔案中，也就是對外界不產生任何依賴了。這特別適合將 Rust 實現的功能封裝好給第三方應用使用。

#### **proc-macro**

過程宏 crate.

在 Cargo.toml 中組態：

```javascript
[lib]
name = "foobar"
crate-type = ["proc-macro"]
```

複製

這種 crate 裡面只能匯出過程宏，被匯出的過程宏可以被其它 crate 引用。

------

Crate type 以及它們之間的區別就介紹到這裡了，有些細節還是需要仔細理解的。本篇意在闡述一些基礎知識，而不打算成為一篇完整的參考檔案，如要查看 Rust Linkage 的詳細內容，直接訪問 Rust Reference。

https://doc.rust-lang.org/reference/linkage.html

這一篇帖子非常有用：

https://users.rust-lang.org/t/what-is-the-difference-between-dylib-and-cdylib/28847