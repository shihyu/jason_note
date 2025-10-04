可以使用稱被為宏的自定義句法形式來擴展 Rust 的功能和句法。

macro_rules 允許用戶以聲明性的(declarative)方式定義句法擴展。

每個聲明宏都有一個名稱和一條或多條規則。每條規則都有兩部分：
- 一個匹配器(matcher)，描述它匹配的句法；
- 一個轉碼器(transcriber)，描述成功匹配後將執行的替代調用句法。
  其中匹配器和轉碼器都必須由定界符(delimiter)包圍。

## 使用宏的簡單例子
如下是一個簡單的聲明宏的例子：

```rust
macro_rules! mymacro {
    () => {println!("{}","Hello World!")};
}

fn main() {
    mymacro!();
    mymacro!{};
    mymacro![];
}
```

上述代碼中，mymacro! 是一個聲明宏，它接受一個空的參數列表。

## 展開宏
對宏進行展開並觀察

```shell
#cargo install cargo-expand
#cargo expand --src main
```
或者是直接使用rustc
```
# rustc +nightly -Zunpretty=expanded use_macro.rs
```

## 聲明宏的基本結構
宏的基本結構如下：
```
macro_rules! $name {
    $rule0 ;
    $rule1 ;
    //...
    $ruleN ;
}
```
每一條rule都對應一套模式匹配和代碼生成。
`( $matcher ) => { $expansion };`

其中 () 代表空輸入。
`() => {println!("{}","Hello World!")};`

如果想匹配 [1, 2, 3]，則可以寫成：
```
 ( $( $elem: expr ),* ) => {
        // 由於我們將生成多條語句，因此必須再用 {} 包起來
        {
            ......
        }
    };
```

## rust中的try!宏與?宏
在編寫錯誤處理的代碼時，可以使用try!宏來簡化錯誤處理代碼。
如果不使用try!宏，則需要使用match語句來處理錯誤，很繁瑣。

```rust
fn myTest1() -> Result<(), Box<dyn std::error::Error>>{
    let mut f = {
        match File::open("hello.txt") {
            Ok(file) => file,
            Err(err) => return Err(From::from(err)),
        };
    };
    Ok(())
}
```
使用了try!宏後，代碼可以簡化成：
```
macro_rules! my_try {
    ($result:expr) => {
        match $result {
            Ok(v) => v,
            Err(e) => {
                return std::result::Result::Err(std::convert::From::from(e));
            }
        }
    };
}

fn myTest2() -> Result<(), Box<dyn std::error::Error>>{
    let mut f1 = my_try!(File::open("hello.txt"));
    let mut f2 = File::open("hello.txt")?;
    Ok(())
}
```

新版本的Rust中，try宏進一步簡化成了?宏。

```go
fn myTest2() -> Result<(), Box<dyn std::error::Error>>{
    let mut f2 = File::open("hello.txt")?;
    Ok(())
}
```

## 參考
- [Rust 的聲明宏機制](https://zyy.rs/post/rust-declarative-macro/)