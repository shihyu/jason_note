# 編譯器參數

本章將介紹Rust編譯器的參數。

Rust編譯器程序的名字是`rustc`，使用它的方法很簡單：

```bash
$ rustc [OPTIONS] INPUT
```

其中，`[OPTIONS]`表示編譯參數，而`INPUT`則表示輸入文件。而編譯參數有以下可選：

* `-h, --help` - 輸出幫助信息到標準輸出；

* `--cfg SPEC` - 傳入自定義的條件編譯參數，使用方法如

  ```rust
  fn main() {
      if cfg!(hello) {
          println!("world!");
      }
  }
  ```

  如上例所示，若`cfg!(hello)`成立，則運行程序就會輸出`"world"`到標準輸出。我們把這個文件保存為`hello.rs`然後編譯它

  ```bash
  $ rustc --cfg hello hello.rs
  ```

  運行它就會看到屏幕中輸出了`world!`。

* `-L [KIND=]PATH` - 往鏈接路徑中加入一個文件夾，並且可以指定這個路徑的類型（Kind），這些類型包括
  - `dependency` - 在這個路徑下找依賴的文件，比如說`mod`；
  - `crate` - 只在這個路徑下找`extern crate`中定義的庫；
  - `native` - 只在這個路徑下找Native庫；
  - `framework` - 只在OS X下有用，只在這個路徑下找Framework；
  - `all` - 默認選項。

* `-l [KIND=]NAME` - 鏈接一個庫，這個庫可以指定類型（Kind）
  - `static` - 靜態庫；
  - `dylib` - 動態庫；
  - `framework` - OS X的Framework。

  如果不傳，默認為`dylib`。

  此處舉一個例子如何手動鏈接一個庫，我們先創建一個文件叫`myhello.rs`，在裡面寫一個函數

  ```rust
  // myhello.rs

  /// 這個函數僅僅向標籤輸出打印 Hello World!
  /// 不要忘記要把它標記為 pub 哦。
  pub fn print_hello() {
      println!("Hello World!");
  }
  ```

  然後把這個文件編譯成一個靜態庫，`libmyhello.a`

  ```bash
  $ rustc --crate-type staticlib myhello.rs
  ```

  然後再創建一個`main.rs`，鏈接這個庫並打印出"Hello World!"

  ```rust
  // main.rs

  // 指定鏈接庫 myhello
  extern crate myhello;

  fn main() {
      // 調用庫函數
      myhello::print_hello();
  }
  ```

  編譯`main.rs`

  ```bash
  $ rustc -L. -lmyhello main.rs
  ```

  運行`main`，就會看到屏幕輸出"Hello World!"啦。

* `--crate-type` - 指定編譯輸出類型，它的參數包括
  - `bin` - 二進行可執行文件
  - `lib` - 編譯為庫
  - `rlib` - Rust庫
  - `dylib` - 動態鏈接庫
  - `staticlib` - 靜態鏈接庫

* `--crate-name` - 指定這個Crate的名字，默認是文件名，如`main.rs`編譯成可執行文件時默認是`main`，但你可以指定它為`foo`

  ```bash
  $ rustc --crate-name foo main.rs
  ```

  則會輸出`foo`可執行文件。

* `--emit` - 指定編譯器的輸出。編譯器默認是輸出一個可執行文件或庫文件，但你可以選擇輸出一些其它的東西用於Debug

  - `asm` - 輸出彙編
  - `llvm-bc` - [LLVM Bitcode](http://llvm.org/docs/BitCodeFormat.html)；
  - `llvm-ir` - [LLVM IR](http://llvm.org/docs/LangRef.html)，即LLVM中間碼（LLVM Intermediate Representation）；
  - `obj` - Object File（就是`*.o`文件）；
  - `link` - 這個是要結合其它`--emit`參數使用，會執行Linker再輸出結果；
  - `dep-info` - 文件依賴關係（Debug用，類似於Makefile一樣的依賴）。

  以上參數可以同時使用，使用逗號分割，如

  ```bash
  $ rustc --emit asm,llvm-ir,obj main.rs
  ```

  同時，在最後可以加一個`=PATH`來指定輸出到一個特定文件，如

  ```bash
  $ rustc --emit asm=output.S,llvm-ir=output.ir main.rs
  ```

  這樣會把彙編生成到`output.S`文件中，把LLVM中間碼輸出到`output.ir`中。

* `--print` - 打印一些信息，參數有
  - `crate-name` - 編譯目標名；
  - `file-names` - 編譯的文件名；
  - `sysroot` - 打印Rust工具鏈的根目錄地址。

* `-g` - 在目標文件中保存符號，這個參數等同於`-C debuginfo=2`。

* `-O` - 開啟優化，這個參數等同於`-C opt-level=2`。

* `-o FILENAME` - 指定輸出文件名，同樣適用於`--emit`的輸出。

* `--out-dir DIR` - 指定輸出的文件夾，默認是當前文件夾，且會忽略`-o`配置。

* `--explain OPT` - 解釋某一個編譯錯誤，比如

  若你寫了一個`main.rs`，使用了一個未定義變量`f`

  ```rust
  fn main() {
      f
  }
  ```

  編譯它時編譯器會報錯：

  ```
  main.rs:2:5: 2:6 error: unresolved name `f` [E0425]
  main.rs:2     f
                ^
  main.rs:2:5: 2:6 help: run `rustc --explain E0425` to see a detailed explanation
  error: aborting due to previous error
  ```

  雖然錯誤已經很明顯，但是你也可以讓編譯器解釋一下，什麼是`E0425`錯誤：

  ```bash
  $ rustc --explain E0425
  // 編譯器打印的說明
  ```

* `--test` - 編譯成一個單元測試可執行文件

* `--target TRIPLE` - 指定目標平臺，基本格式是`cpu-manufacturer-kernel[-os]`，例如

  ```bash
  ## 64位OS X
  $ rustc --target x86_64-apple-darwin
  ```

* `-W help` - 打印Linter的所有可配置選項和默認值。

* `-W OPT, --warn OPT` - 設置某一個Linter選項為Warning。
* `-A OPT, --allow OPT` - 設置某一個Linter選項為Allow。
* `-D OPT, --deny OPT` - 設置某一個Linter選項為Deny。
* `-F OPT, --forbit OPT` - 設置某一個Linter選項為Forbit。

* `-C FLAG[=VAL], --codegen FLAG[=VAL]` - 目標代碼生成的的相關參數，可以用`-C help`來查看配置，值得關注的幾個是
  - `linker=val` - 指定鏈接器；
  - `linker-args=val` - 指定鏈接器的參數；
  - `prefer-dynamic` - 默認Rust編譯是靜態鏈接，選擇這個配置將改為動態鏈接；
  - `debug-info=level` - Debug信息級數，`0` = 不生成，`1` = 只生成文件行號表，`2` = 全部生成；
  - `opt-level=val` - 優化級數，可選`0-3`；
  - `debug_assertion` - 顯式開啟`cfg(debug_assertion)`條件。

* `-V, --version` - 打印編譯器版本號。

* `-v, --verbose` - 開啟囉嗦模式（打印編譯器執行的日誌）。

* `--extern NAME=PATH` - 用來指定外部的Rust庫（`*.rlib`）名字和路徑，名字應該與`extern crate`中指定的一樣。

* `--sysroot PATH` - 指定工具鏈根目錄。

* `-Z flag` - 編譯器Debug用的參數，可以用`-Z help`來查看可用參數。

* `--color auto|always|never` - 輸出時對日誌加顏色
  - `auto` - 自動選擇加還是不加，如果輸出目標是虛擬終端（TTY）的話就加，否則就不加；
  - `always` - 給我加！
  - `never` - 你敢加？
