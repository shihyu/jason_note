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

將 nightly 版本作為 default 版本

```
rustup default nightly
```

## 解除安裝 Rust 與 rustup

```
rustup self uninstall
```

## Rust 版本的差異

- nightly: 每天的最新版本，但 bug 很多
- beta: nightly 的新 bug feature 過一段時間穩定後，會在 beta 版出現
- stable: 最穩定的版本，但相對的功能較舊

## 參考資料

- https://www.rust-lang.org/tools/install
- https://doc.rust-lang.org/book/ch01-01-installation.html

---

### 學習網站

- [令狐一沖](https://github.com/anonymousGiga/learn_rust/)
- [Rust 語言之旅](https://shihyu.github.io/my_tour_of_rust/TOC_zh-tw.html)
- [Rust 程式設計語言](https://rust-lang.tw/book-tw/#rust-程式設計語言)
- [通過例子學 Rust 中文版](https://rustwiki.org/zh-CN/rust-by-example/)
- [通過例子學Rust繁體版](https://shihyu.github.io/rust_by_example)
- [RustPrimer](https://rustcc.gitbooks.io/rustprimer/content/)
- [RustPrimer繁體](https://shihyu.github.io/RustPrimerBook/)
- [Rust學習筆記](https://skyao.io/learning-rust/)
- [通过大量的链表学习Rust](https://weathfold.gitbooks.io/rust-too-many-lists-zhcn/content/)
- [Rust入門祕籍](https://shihyu.github.io/rust_hacks/)
- [Rust 程式設計語言](https://rust-lang.tw/book-tw/title-page.html#rust-程式設計語言)
  - https://github.com/rust-tw/book-tw

