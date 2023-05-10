## Rust 中的 bin, lib, rlib, a, so 概念介紹

出處: https://blog.51cto.com/u_15683898/5426916

在 Rust 中，常見的可執行檔和庫文件格式包括：

- **可執行檔（bin）**：在 Rust 中，可執行檔指的是一個由 Rust 編譯器直接編譯出的二進制 ELF 或 Mach-O 檔案格式文件。可執行檔不能被其他程式直接使用，而只能由終端用戶執行。在 Rust 的項目中，所有的可執行檔都位於 `src/bin` 目錄中，每個可執行檔都是一個獨立的 Rust 程式。將其命名為 `foo.rs` 將會產生一個可執行檔 `foo`。
- **函式庫（lib）**：在 Rust 中，函式庫指的是一個二進制或共享庫，它提供了一組用於更大程式中使用的函數。函式庫可以在 Rust 程式中被引用，以避免代碼重複。在 Rust 的項目中，所有的函式庫都位於 `src/lib` 目錄中。根據文件生成不同的庫類型，可以分為靜態庫（`.a`）和動態庫（`.so`）。靜態庫被編譯進可執行檔，而動態庫則僅在運行時被加載，並在多個程序之間共享。
- **靜態庫（rlib）**：在 Rust 中，靜態庫需要通過 `rustc` 生成，其文件格式為 RLIB。靜態庫（`.rlib`）是一個經過 Rust 編譯器優化並靜態鏈接的二進制文件。靜態庫可以直接與 Rust 可執行文件一起複製和發布。與函式庫（`.so`）相比，靜態庫具有更快的加載時間和更好的可移植性。在 Rust 中，編譯靜態庫需要執行以下命令： `rustc --crate-type=staticlib path/to/library.rs`。
- **動態庫（so）**：在 Rust 中，動態庫使用共享庫（`.so`）文件作為文件格式。動態庫被編譯成一個獨立的文件並可以在多個執行檔之間共享。在 Rust 項目中編譯動態庫需要使用 cargo 的 build 命令，並將 crate-type 設置為 `cdylib`。



在 Rust 中，可執行檔和函式庫都遵循 ELF（可執行和可鏈接格式）標準，該標準應用於 Linux 和其他類Unix系統。因此，這些檔案可以透明地在 Linux 系統上被解析和執行。

在 Linux 系統上，要執行 Rust 可執行檔或函式庫，必須首先確保文件已被正確編譯。對於 Rust 的可執行檔案或函式庫，您可以使用以下命令進行編譯：

- 可執行檔：將 `Cargo.toml` 中的 `bin` 選項設置為正在編譯的可執行檔，然後使用以下命令編譯：

  ```
  $ cargo build --bin your_bin_name
  ```

  或者，使用以下命令在優化模式下編譯：

  ```
  $ cargo build --release --bin your_bin_name `
  ```

- 函式庫（靜態庫或動態庫）：將 `Cargo.toml` 中的 `lib` 選項設置為正在編譯的函式庫，然後使用以下命令編譯：

  ```
  $ cargo build --lib
  ```

  或者，使用以下命令編譯動態庫（請注意，`crate-type` 選項需要設置為 `cdylib`）：

  ```
  $ cargo build --release --lib --features cdylib `
  ```

完成編譯後，您可以使用命令行運行 Rust 的可執行檔，並將函式庫鏈接到其他程式中。在 Linux 上執行 Rust 程式和函式庫與運行任何其他 ELF 文件一樣，只需確保它們是正確生成並遵循了 ELF 規範即可。



在編譯可執行檔或庫文件時，應將文件命名為該文件的用途並使用相應的擴展名，例如：將可執行檔命名為 `foo.rs` 並編譯生成可執行檔 `foo`；將靜態庫命名為 `libfoo.rs` 並執行命令 `rustc --crate-type=staticlib libfoo.rs`；將動態庫命名為 `libfoo.rs` 並執行 `cargo build --release` 命令來編譯動態庫文件 `libfoo.so`。

寫了這麼久的 Rust 程式碼了，可能很多人還對 Rust 的編譯後的檔案格式不是很清晰。本篇我們就來理一下，Rust 中的 bin, lib, rlib, a, so 是什麼，如何生成，以及其它一些細節。

從 cargo new 說起
我們建立一個新工程，通常從下面兩句入手：

```rust
cargo new foobar
```


或

```rust
cargo new --lib foobar
```


前者建立一個可執行工程，而後者建立一個庫工程。

實際上，你去探索上述命令列生成的檔案，發現它們的 Cargo.toml 完全一樣，區別僅在於 src 目錄下，可執行工程是一個 main.rs，而庫工程是一個 lib.rs。

這是因為 main.rs 和 lib.rs 對於一個 crate 來講，是兩個特殊的檔案名稱。rustc 內建了對這兩個特殊檔案名稱的處理（當然也可以通過 Cargo.toml 進行組態，不詳談），我們可以認為它們就是一個 crate 的入口。

可執行 crate 和庫 crate 是兩種不同的 crate。下面我們就來一併說一下它們的兄弟姐妹及其之間的異同。

### crate type

執行

```sh
rustc --help|grep crate-type
```


可得到如下輸出

```sh
--crate-type [bin|lib|rlib|dylib|cdylib|staticlib|proc-macro]
```


才發現，原來有這麼多種 crate type。下面挨個看一下。

### bin
二進制可執行 crate，編譯出的檔案為二進制可執行檔案。必須要有 main 函數作為入口。這種 crate 不需要在 Cargo.toml 中或 --crate-type 命令列參數中指定，會自動識別。

### lib
庫 crate。它其實並不是一種具體的庫，它指代後面各種庫 crate 中的一種，可以認為是一個代理名稱（alias）。

通常來講，如果什麼都不組態，默認指的是 rlib, 會生成 .rlib 的檔案。

### rlib
rlib 是 Rust Library 特定靜態中間庫格式。如果只是純 Rust 程式碼項目之間的依賴和呼叫，那麼，用 rlib 就能完全滿足使用需求。

rlib 實現為一個 ar 歸檔檔案。

> file target/debug/libfoobar.rlib
> target/debug/libfoobar.rlib: current ar archive
> 1.
> 2.
> rlib 中包含很多 metadata 資訊（比如可能的上游依賴資訊），用來做後面的 linkage。

在 Cargo.toml 中組態：

```toml
[lib]
name = "foobar"
crate-type = ["rlib"]
```

可以指定生成 rlib，但是一般沒必要設定，因為默認 lib 就是 rlib。

rlib 是平臺（Linux, MacOS, Windows ...）無關的。

dylib
動態庫。

在 Cargo.toml 中組態：

```toml
[lib]
name = "foobar"
crate-type = ["dylib"]
```


會在編譯的時候，生成動態庫（Linux 上為 .so, MacOS 上為 .dylib, Windows 上為 .dll）。

動態庫是平臺相關的庫。動態庫在被依賴並連結時，不會被連結到目標檔案中。這種動態庫只能被 Rust 寫的程序(或遵循 Rust 內部不穩定的規範的程序)呼叫。這個動態庫可能依賴於其它動態庫（比如，Linux 下用 C 語言寫的 PostgreSQL 的 libpq.so，或者另一個編譯成 "dylib" 的 Rust 動態庫）。

### cdylib
C規範動態庫。

在 Cargo.toml 中組態：

```toml
[lib]
name = "foobar"
crate-type = ["cdylib"]
```


與 dylib 類似，也會生成 .so, .dylib 或 .dll 檔案。但是這種動態庫可以被其它語言呼叫（因為幾乎所有語言都有遵循 C 規範的 FFI 實現），也就是跨語言 FFI 使用。這個動態庫可能依賴於其它動態庫（比如，Linux 下用 C 語言寫的 PostgreSQL 的 libpq.so）。

### staticlib
靜態庫。

在 Cargo.toml 中組態：

```toml
[lib]
name = "foobar"
crate-type = ["staticlib"]
```


編譯會生成`.a` 檔案（在 Linux 和 MacOS 上），或 .lib 檔案（在 Windows 上）。

編譯器會把所有實現的 Rust 庫程式碼以及依賴的庫程式碼全部編譯到一個靜態庫檔案中，也就是對外界不產生任何依賴了。這特別適合將 Rust 實現的功能封裝好給第三方應用使用。

### proc-macro
過程宏 crate.

在 Cargo.toml 中組態：

```toml
[lib]
name = "foobar"
crate-type = ["proc-macro"]
```


這種 crate 裡面只能匯出過程宏，被匯出的過程宏可以被其它 crate 引用。

Crate type 以及它們之間的區別就介紹到這裡了，有些細節還是需要仔細理解的。本篇意在闡述一些基礎知識，而不打算成為一篇完整的參考檔案，如要查看 Rust Linkage 的詳細內容，直接訪問 Rust Reference。

 https://doc.rust-lang.org/reference/linkage.html

這一篇帖子非常有用：

 https://users.rust-lang.org/t/what-is-the-difference-between-dylib-and-cdylib/28847

