# Rust json處理

JSON是一種比較重要的格式，尤其是現在的web開發領域，JSON相比於傳統的XML更加容易操作和減小傳輸。

Rust中的JSON處理依賴 cargo 中的rustc-serialize模塊

###先簡單的創建一個Rust項目工程

``` rust
$ cargo new json_data --bin
```

生成文件樹：

```shell
vagrant@ubuntu-14:~/tmp/test/rustprimer$ tree
.
`-- json_data
    |-- Cargo.toml
    `-- src
        `-- main.rs


```

生成項目`json_data`,項目下文件介紹：

- Caogo.toml ，文件中填寫一些項目的相關信息，比如版本號，聯繫人，項目名，文件的內容如下：

```toml
[package]
name = "json_data"
version = "0.1.0"
authors = ["wangxxx <xxxxx@qq.com>"]

[dependencies]

```

- src 中放置項目的源代碼，main.rs 為項目的入口文件。

###一些必要的瞭解

rustc-serialize 這個是第三方的模塊，需要從[cargo](https://crates.io/crates/rustc-serialize)下載。
下載很簡單，只需修改一下cargo.toml文件就行了.

```toml
[package]
name = "json_data"
version = "0.1.0"
authors = ["wangxxx <xxxxx@qq.com>"]

[dependencies]
rustc-serialize = "0.3.18"

```

然後執行在當前目錄執行:

```
$ cargo build
```

*注意一個問題由於國內網絡訪問github不穩定，這些第三方庫很多託管在github上，所以可能需要修改你的
網絡訪問*

1. 在安裝Rust之後，會在你的用戶目錄之下生成一個`.cargo`文件夾，進入這個文件夾
2. 在`.cargo`文件夾下，創建一個`config`文件，在文件中填寫中科大軟件源，可能以後會出現其他的源，先用這個
3. `config`文件內容如下

```toml
[registry]
index = "git://crates.mirrors.ustc.edu.cn/index"

```

cargo build 執行之後的提示信息

```
   Updating registry `git://crates.mirrors.ustc.edu.cn/index`
 Downloading rustc-serialize v0.3.18 (registry git://crates.mirrors.ustc.edu.cn/index)
   Compiling rustc-serialize v0.3.18 (registry git://crates.mirrors.ustc.edu.cn/index)
   Compiling json_data v0.1.0 (file:///home/vagrant/tmp/test/rustprimer/json_data)
```

再次執行tree命令:

```
.
|-- Cargo.lock
|-- Cargo.toml
|-- src
|   `-- main.rs
`-- target
    `-- debug
        |-- build
        |-- deps
        |   `-- librustc_serialize-d27006e102b906b6.rlib
        |-- examples
        |-- json_data
        `-- native

```

可以看到多了很多文件，重點關注`cargo.lock`,開打文件:

```toml
[root]
name = "json_data"
version = "0.1.0"
dependencies = [
 "rustc-serialize 0.3.18 (registry+git://crates.mirrors.ustc.edu.cn/index)",
]

[[package]]
name = "rustc-serialize"
version = "0.3.18"
source = "registry+git://crates.mirrors.ustc.edu.cn/index"

```

是關於項目編譯的一些依賴信息

還有生成了target文件夾，生成了可執行文件json_data,因為main.rs中的執行結果就是打印`hello world`

```
$ cargo run

Hello, world!
```

###開始寫代碼
直接使用官方的 [rustc_serialize 中的例子](https://doc.rust-lang.org/rustc-serialize/rustc_serialize/json/index.html#using-autoserialization)：

``` rust
extern crate rustc_serialize;
// 引入rustc_serialize模塊
use rustc_serialize::json;

// Automatically generate `RustcDecodable` and `RustcEncodable` trait
// implementations
// 定義TestStruct
#[derive(RustcDecodable, RustcEncodable)]
pub struct TestStruct  {
    data_int: u8,
    data_str: String,
    data_vector: Vec<u8>,
}

fn main() {
    // 初始化TestStruct
    let object = TestStruct {
        data_int: 1,
        data_str: "homura".to_string(),
        data_vector: vec![2,3,4,5],
    };

    // Serialize using `json::encode`
    // 將TestStruct轉意為字符串
    let encoded = json::encode(&object).unwrap();
    println!("{}",encoded);
    // Deserialize using `json::decode`
    // 將json字符串中的數據轉化成TestStruct對應的數據，相當於初始化
    let decoded: TestStruct = json::decode(&encoded).unwrap();
    println!("{:?}",decoded.data_vector);
}

```

當然我們也可以在文本中作為api的返回結果使用，下來的章節中，我們將討論這個問題
