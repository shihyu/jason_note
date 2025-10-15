# 前期準備

## 下載 Rust 源代碼（供 racer 使用）

### 從github下載

`git clone https://github.com/rust-lang/rust.git`

### 從官網下載源代碼包

下載地址： `https://static.rust-lang.org/dist/rustc-nightly-src.tar.gz`

### 使用rustup下載（推薦）

使用rustup獲取源碼最大的好處在於可以使用`rustup update`隨時獲取最新版源碼，~~而且特別省事,~~執行以下命令獲取源碼
```
rustup component add rust-src
```
## racer
racer是一個由rust的愛好者提供的rust自動補全和語法分析工具，被用來提供基本的補全功能和定義跳轉功能。其本身完全由rust寫成，補全功能已經比較完善了。

我們可以通過如下的方式獲取它：

### cargo自動安裝
在rust 1.5版本以後，其安裝包自帶的cargo工具已經支持了cargo install命令，這個命令可以幫助我們通過簡單的方式獲取到`racer`的最新版。

你可以通過以下命令安裝`racer`最新版，目前已知在Linux、Unix和Windows上適用

```
cargo install racer
```

### 編譯安裝

事實上我更推薦有條件的用戶通過這種方式安裝，因為自己實戰操作一遍總是有些收穫的。~~(帥氣可愛的DCjanus表示懷疑)~~

#### 下載源碼

首先，我們需要下載racer的源碼

```
git clone https://github.com/phildawes/racer.git
```

#### 進行編譯

然後，進入目錄然後進行編譯

```
cd racer && cargo build --release
```

這樣，我們會得到racer的二進制文件在 `target/release/racer`目錄

#### 設置環境變量

為了對Rust標準庫進行補全，racer需要獲取Rust源碼路徑。

設置名為`RUST_SRC_PATH`的環境變量為`[path_to_your_rust_source]/src`

其中`[path_to_your_rust_source]`表示源碼所在文件夾，使用rustup獲取Rust源碼的情況下`[path_to_your_rust_source]`默認為`~/.multirust/toolchains/[your-toolchain]/lib/rustlib/src/rust/src`

### 測試

請重新打開終端，並進入到關閉之前的路徑。
執行如下代碼：
linux:

```
./target/release/racer complete std::io::B
```

windows:

```
target\release\racer complete std::io::B
```

你將會看到racer的提示，這表示racer已經執行完成了。


## 安裝 rustfmt

`cargo install rustfmt`

## Rust Langular Server (RLS)

`Rust Langular Server`(下文簡稱`RLS`)可以為很多IDE或編輯器提供包括不限於自動補全、跳轉定義、重命名、跳轉類型的功能支持。

使用rustup安裝步驟如下:

1. 保證`rustup`為最新版
```
rustup self update
```
2. 升級工具鏈(並不要求設置`nightly`為默認，但需要保證安裝了`nightly`工具鏈)
```
rustup update nightly
```
3. 正式安裝RLS
```
rustup component add rls --toolchain nightly
rustup component add rust-analysis --toolchain nightly
rustup component add rust-src --toolchain nightly
```
4. 設置環境變量
如果在安裝Racer時沒有設置名為`RUST_SRC_PATH`的環境變量，請參考前文進行設置。

**截至當前(2017年7月15日)，`RLS`仍然處於alpha階段，隨著項目變動，安裝步驟可能會由較大變化，本文中提及的RLS安裝方法可能在較短的時間內過時，建議跟隨官方安裝指導進行安裝。**

**該項目託管地址:[https://github.com/rust-lang-nursery/rls](https://github.com/rust-lang-nursery/rls)**
