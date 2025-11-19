# 安裝 Rust

## Linux or Unix or MacOS

輸入下面的指令即可

```
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

若安裝完後發生問題，例如環境變數沒有自行設定好，可以輸入下面的指令

```
source $HOME/.cargo/env
```

或在 `~/.bash_profile` 輸入

```
export PATH="$HOME/.cargo/bin:$PATH"
```

## Windows

下載 [rustup.exe](https://win.rustup.rs/)

安裝需要用到 C++ build tools for VS2013 或更高的版本，可以在 Visual Studio 的官網下載軟體後，在其他的安裝選項中找到

## 更新 Rust 版本

```
rustup update
```

## 安裝 Rust 的其他版本

EX: 安裝 nightly 的版本

```
rustup install nightly
```

輸入下面指令檢查版本，如果有顯示就是代表安裝成功

```bash
rustc --version
rustc 1.67.0-nightly (e0098a5cc 2022-11-29)
```

將 nightly 版本作為 default 版本

```
rustup default nightly
```

## 切換rust版本

查看目前所以安裝的版本

```bash
ls ~/.rustup/toolchains/

nightly-x86_64-unknown-linux-gnu  
stable-x86_64-unknown-linux-gnu
```

切換預設版本

`rustup default stable-x86_64-unknown-linux-gnu`

## 解除安裝 Rust 與 rustup

```
rustup self uninstall
```

## Rust 版本的差異

- nightly: 每天的最新版本，但 bug 很多
- beta: nightly 的新 bug feature 過一段時間穩定後，會在 beta 版出現
- stable: 最穩定的版本，但相對的功能較舊



# Rustup 與 Cargo 角色介紹

## Rustup

Rustup 是 Rust 程式語言的官方工具鏈管理器，主要負責：

- 安裝與管理不同版本的 Rust 編譯器
- 切換發布渠道（stable、beta、nightly）
- 管理交叉編譯目標平臺
- 安裝或移除 Rust 組件

### Rustup 常用指令：

- `rustup install <toolchain>` - 安裝特定版本的 Rust
- `rustup update` - 更新所有已安裝的工具鏈
- `rustup default <toolchain>` - 設定默認工具鏈
- `rustup show` - 顯示目前工具鏈資訊
- `rustup component add <component>` - 安裝組件
- `rustup component remove <component>` - 移除組件
- `rustup target add <target>` - 增加交叉編譯目標
- `rustup target remove <target>` - 移除交叉編譯目標
- `rustup self update` - 更新 rustup 工具本身
- `rustup toolchain list` - 列出已安裝的工具鏈

## Cargo

Cargo 是 Rust 的套件管理器與建構系統，主要負責：

- 創建新的 Rust 專案
- 編譯與執行 Rust 專案
- 管理專案依賴關係
- 執行測試及基準測試
- 發布套件到 crates.io（Rust 的官方套件儲存庫）

### Cargo 常用指令：

- `cargo new <project>` - 創建新專案
- `cargo init` - 在現有目錄中初始化 Rust 專案
- `cargo build` - 編譯專案
- `cargo run` - 編譯並執行專案
- `cargo test` - 執行測試
- `cargo bench` - 執行基準測試
- `cargo add <crate>` - 添加依賴
- `cargo remove <crate>` - 移除依賴
- `cargo update` - 更新依賴
- `cargo check` - 檢查代碼但不生成執行檔
- `cargo doc` - 生成文檔
- `cargo publish` - 發布套件到 crates.io
- `cargo search <keyword>` - 搜尋 crates.io 上的套件
- `cargo clean` - 清除編譯生成的檔案
- `cargo fmt` - 使用 rustfmt 格式化代碼
- `cargo clippy` - 使用 clippy 進行更嚴格的代碼檢查

## 兩者關係

Rustup 與 Cargo 的關係：

- **Rustup** 管理 Rust 語言本身的安裝、版本與組件
- **Cargo** 管理 Rust 專案及其依賴

當您安裝 Rustup 時，它會自動為您安裝 Cargo。這兩個工具協同工作，提供完整的 Rust 開發環境，從語言工具鏈的安裝與管理，到專案的創建、編譯、測試與發布。


## 參考資料

- https://www.rust-lang.org/tools/install
- https://doc.rust-lang.org/book/ch01-01-installation.html

---

### 學習網站

- [Rust Room](https://github.com/rust-boom/rust-boom)
- [令狐一沖](https://github.com/anonymousGiga/learn_rust/)
- [Rust 語言之旅](https://shihyu.github.io/my_tour_of_rust/TOC_zh-tw.html)
- [Rust 程式設計語言](https://rust-lang.tw/book-tw/#rust-程式設計語言)
- [通過例子學 Rust 中文版](https://rustwiki.org/zh-CN/rust-by-example/)
- [通過例子學Rust繁體版](https://shihyu.github.io/rust_by_example)
- [RustPrimer](https://rustcc.gitbooks.io/rustprimer/content/)
- [RustPrimer繁體](https://shihyu.github.io/RustPrimerBook/)
- [Rust學習筆記](https://skyao.io/learning-rust/)
- [通過大量的鏈表學習Rust](https://weathfold.gitbooks.io/rust-too-many-lists-zhcn/content/)
- [Rust入門秘籍](https://shihyu.github.io/rust_hacks/)
- [Rust 新手村 系列](https://ithelp.ithome.com.tw/users/20129675/ironman/4260?page=1)
- [30 天深入淺出 Rust 系列](https://ithelp.ithome.com.tw/users/20111802/ironman/1742)
- [30 天快快樂樂學 Rust 系列](https://ithelp.ithome.com.tw/users/20120293/ironman/5180)
- [30天讀完《深入淺出Rust》](https://www.zhihu.com/column/c_1566579693834489856)
- [Rust 程式設計語言](https://rust-lang.tw/book-tw/title-page.html#rust-程式設計語言)
  - https://github.com/rust-tw/book-tw
- [The Embedded Rust Book](https://shihyu.github.io/rust-embedded/)

