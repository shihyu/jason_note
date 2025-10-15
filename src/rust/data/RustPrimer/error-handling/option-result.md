# 17.錯誤處理
錯誤處理是保證程序健壯性的前提，在編程語言中錯誤處理的方式大致分為兩種：拋出異常（exceptions）和作為值返回。

**Rust** 將錯誤作為值返回並且提供了原生的優雅的錯誤處理方案。

熟練掌握錯誤處理是軟件工程中非常重要的環節，讓我一起來看看**Rust**展現給我們的錯誤處理藝術。

## 17.1 Option和Result
謹慎使用`panic`：

```rust
fn guess(n: i32) -> bool {
    if n < 1 || n > 10 {
        panic!("Invalid number: {}", n);
    }
    n == 5
}

fn main() {
    guess(11);
}
```

`panic`會導致當前線程結束，甚至是整個程序的結束，這往往是不被期望看到的結果。（編寫示例或者簡短代碼的時候`panic`不失為一個好的建議）


### Option

```rust
enum Option<T> {
    None,
    Some(T),
}
```

**Option** 是Rust的系統類型，用來表示值不存在的可能，這在編程中是一個好的實踐，它強制**Rust**檢測和處理值不存在的情況。例如：

```rust
fn find(haystack: &str, needle: char) -> Option<usize> {
    for (offset, c) in haystack.char_indices() {
        if c == needle {
            return Some(offset);
        }
    }
    None
}
```

`find`在字符串`haystack`中查找`needle`字符，事實上結果會出現兩種可能，有（`Some(usize)`)或無（`None`）。

```rust
fn main() {
    let file_name = "foobar.rs";
    match find(file_name, '.') {
        None => println!("No file extension found."),
        Some(i) => println!("File extension: {}", &file_name[i+1..]),
    }
}
```

**Rust** 使用模式匹配來處理返回值，調用者必須處理結果為`None`的情況。這往往是一個好的編程習慣，可以減少潛在的bug。**Option** 包含一些方法來簡化模式匹配，畢竟過多的`match`會使代碼變得臃腫，這也是滋生bug的原因之一。

#### unwrap

```rust
impl<T> Option<T> {
    fn unwrap(self) -> T {
        match self {
            Option::Some(val) => val,
            Option::None =>
              panic!("called `Option::unwrap()` on a `None` value"),
        }
    }
}
```

`unwrap`當遇到`None`值時會panic，如前面所說這不是一個好的工程實踐。不過有些時候卻非常有用：

* **在例子和簡單快速的編碼中** 有的時候你只是需要一個小例子或者一個簡單的小程序，輸入輸出已經確定，你根本沒必要花太多時間考慮錯誤處理，使用`unwrap`變得非常合適。
* **當程序遇到了致命的bug，panic是最優選擇**


#### map

假如我們要在一個字符串中找到文件的擴展名，比如`foo.rs`中的`rs`， 我們可以這樣：

```rust
fn extension_explicit(file_name: &str) -> Option<&str> {
    match find(file_name, '.') {
        None => None,
        Some(i) => Some(&file_name[i+1..]),
    }
}

fn main() {
    match extension_explicit("foo.rs") {
        None => println!("no extension"),
        Some(ext) =>  assert_eq!(ext, "rs"),
    }
}
```

我們可以使用`map`簡化：

```rust
// map是標準庫中的方法
fn map<F, T, A>(option: Option<T>, f: F) -> Option<A> where F: FnOnce(T) -> A {
    match option {
        None => None,
        Some(value) => Some(f(value)),
    }
}
// 使用map去掉match
fn extension(file_name: &str) -> Option<&str> {
    find(file_name, '.').map(|i| &file_name[i+1..])
}
```

`map`如果有值`Some(T)`會執行`f`，反之直接返回`None`。

#### unwrap_or

```rust
fn unwrap_or<T>(option: Option<T>, default: T) -> T {
    match option {
        None => default,
        Some(value) => value,
    }
}
```
`unwrap_or`提供了一個默認值`default`，當值為`None`時返回`default`：
```rust
fn main() {
    assert_eq!(extension("foo.rs").unwrap_or("rs"), "rs");
    assert_eq!(extension("foo").unwrap_or("rs"), "rs");
}
```

#### and_then

```rust
fn and_then<F, T, A>(option: Option<T>, f: F) -> Option<A>
        where F: FnOnce(T) -> Option<A> {
    match option {
        None => None,
        Some(value) => f(value),
    }
}
```

看起來`and_then`和`map`差不多，不過`map`只是把值為`Some(t)`重新映射了一遍，`and_then`則會返回另一個`Option`。如果我們在一個文件路徑中找到它的擴展名，這時候就會變得尤為重要：

```rust
use std::path::Path;
fn file_name(file_path: &str) -> Option<&str> {
    let path = Path::new(file_path);
    path.file_name().to_str()
}
fn file_path_ext(file_path: &str) -> Option<&str> {
    file_name(file_path).and_then(extension)
}
```

### Result

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

`Result`是`Option`的更通用的版本，比起`Option`結果為`None`它解釋了結果錯誤的原因，所以：

```rust
type Option<T> = Result<T, ()>;
```

這樣的別名是一樣的（`()`標示空元組，它既是`()`類型也可以是`()`值）
#### unwrap

```rust
impl<T, E: ::std::fmt::Debug> Result<T, E> {
    fn unwrap(self) -> T {
        match self {
            Result::Ok(val) => val,
            Result::Err(err) =>
              panic!("called `Result::unwrap()` on an `Err` value: {:?}", err),
        }
    }
}
```

沒錯和`Option`一樣，事實上它們擁有很多類似的方法，不同的是，`Result`包括了錯誤的詳細描述，這對於調試人員來說，這是友好的。

#### Result我們從例子開始

```rust
fn double_number(number_str: &str) -> i32 {
    2 * number_str.parse::<i32>().unwrap()
}

fn main() {
    let n: i32 = double_number("10");
    assert_eq!(n, 20);
}
```

`double_number`從一個字符串中解析出一個`i32`的數字並`*2`，`main`中調用看起來沒什麼問題，但是如果把`"10"`換成其他解析不了的字符串程序便會panic

```rust
impl str {
    fn parse<F: FromStr>(&self) -> Result<F, F::Err>;
}

```

`parse`返回一個`Result`，但讓我們也可以返回一個`Option`，畢竟一個字符串要麼能解析成一個數字要麼不能，但是`Result`給我們提供了更多的信息（要麼是一個空字符串，一個無效的數位，太大或太小），這對於使用者是友好的。當你面對一個Option和Result之間的選擇時。如果你可以提供詳細的錯誤信息，那麼大概你也應該提供。

這裡需要理解一下`FromStr`這個**trait**:

```rust
pub trait FromStr {
    type Err;
    fn from_str(s: &str) -> Result<Self, Self::Err>;
}

impl FromStr for i32 {
    type Err = ParseIntError;
    fn from_str(src: &str) -> Result<i32, ParseIntError> {

    }
}
```

`number_str.parse::<i32>()`事實上調用的是`i32`的`FromStr`實現。

我們需要改寫這個例子：

```rust
use std::num::ParseIntError;

fn double_number(number_str: &str) -> Result<i32, ParseIntError> {
    number_str.parse::<i32>().map(|n| 2 * n)
}

fn main() {
    match double_number("10") {
        Ok(n) => assert_eq!(n, 20),
        Err(err) => println!("Error: {:?}", err),
    }
}
```

不僅僅是`map`，`Result`同樣包含了`unwrap_or`和`and_then`。也有一些特有的針對錯誤類型的方法`map_err`和`or_else`。

#### Result別名
在**Rust**的標準庫中會經常出現Result的別名，用來默認確認其中`Ok(T)`或者`Err(E)`的類型，這能減少重複編碼。比如`io::Result`

```rust
use std::num::ParseIntError;
use std::result;

type Result<T> = result::Result<T, ParseIntError>;

fn double_number(number_str: &str) -> Result<i32> {
    unimplemented!();
}
```

### 組合Option和Result
`Option`的方法`ok_or`：

```rust
fn ok_or<T, E>(option: Option<T>, err: E) -> Result<T, E> {
    match option {
        Some(val) => Ok(val),
        None => Err(err),
    }
}
```

可以在值為`None`的時候返回一個`Result::Err(E)`，值為`Some(T)`的時候返回`Ok(T)`，利用它我們可以組合`Option`和`Result`：

```rust
use std::env;

fn double_arg(mut argv: env::Args) -> Result<i32, String> {
    argv.nth(1)
        .ok_or("Please give at least one argument".to_owned())
        .and_then(|arg| arg.parse::<i32>().map_err(|err| err.to_string()))
        .map(|n| 2 * n)
}

fn main() {
    match double_arg(env::args()) {
        Ok(n) => println!("{}", n),
        Err(err) => println!("Error: {}", err),
    }
}
```

`double_arg`將傳入的命令行參數轉化為數字並翻倍，`ok_or`將`Option`類型轉換成`Result`，`map_err`當值為`Err(E)`時調用作為參數的函數處理錯誤

#### 複雜的例子

```rust
use std::fs::File;
use std::io::Read;
use std::path::Path;

fn file_double<P: AsRef<Path>>(file_path: P) -> Result<i32, String> {
    File::open(file_path)
         .map_err(|err| err.to_string())
         .and_then(|mut file| {
              let mut contents = String::new();
              file.read_to_string(&mut contents)
                  .map_err(|err| err.to_string())
                  .map(|_| contents)
         })
         .and_then(|contents| {
              contents.trim().parse::<i32>()
                      .map_err(|err| err.to_string())
         })
         .map(|n| 2 * n)
}

fn main() {
    match file_double("foobar") {
        Ok(n) => println!("{}", n),
        Err(err) => println!("Error: {}", err),
    }
}
```

`file_double`從文件中讀取內容並將其轉化成`i32`類型再翻倍。
這個例子看起來已經很複雜了，它使用了多個組合方法，我們可以使用傳統的`match`和`if let`來改寫它：

```rust
use std::fs::File;
use std::io::Read;
use std::path::Path;

fn file_double<P: AsRef<Path>>(file_path: P) -> Result<i32, String> {
    let mut file = match File::open(file_path) {
        Ok(file) => file,
        Err(err) => return Err(err.to_string()),
    };
    let mut contents = String::new();
    if let Err(err) = file.read_to_string(&mut contents) {
        return Err(err.to_string());
    }
    let n: i32 = match contents.trim().parse() {
        Ok(n) => n,
        Err(err) => return Err(err.to_string()),
    };
    Ok(2 * n)
}

fn main() {
    match file_double("foobar") {
        Ok(n) => println!("{}", n),
        Err(err) => println!("Error: {}", err),
    }
}
```

這兩種方法個人認為都是可以的，依具體情況來取捨。

### try!

```rust
macro_rules! try {
    ($e:expr) => (match $e {
        Ok(val) => val,
        Err(err) => return Err(::std::convert::From::from(err)),
    });
}

```

`try!`事實上就是`match Result`的封裝，當遇到`Err(E)`時會提早返回，
`::std::convert::From::from(err)`可以將不同的錯誤類型返回成最終需要的錯誤類型，因為所有的錯誤都能通過`From`轉化成`Box<Error>`，所以下面的代碼是正確的：

```rust
use std::error::Error;
use std::fs::File;
use std::io::Read;
use std::path::Path;

fn file_double<P: AsRef<Path>>(file_path: P) -> Result<i32, Box<Error>> {
    let mut file = try!(File::open(file_path));
    let mut contents = String::new();
    try!(file.read_to_string(&mut contents));
    let n = try!(contents.trim().parse::<i32>());
    Ok(2 * n)
}

```

#### 組合自定義錯誤類型

```rust
use std::fs::File;
use std::io::{self, Read};
use std::num;
use std::io;
use std::path::Path;

// We derive `Debug` because all types should probably derive `Debug`.
// This gives us a reasonable human readable description of `CliError` values.
#[derive(Debug)]
enum CliError {
    Io(io::Error),
    Parse(num::ParseIntError),
}

impl From<io::Error> for CliError {
    fn from(err: io::Error) -> CliError {
        CliError::Io(err)
    }
}

impl From<num::ParseIntError> for CliError {
    fn from(err: num::ParseIntError) -> CliError {
        CliError::Parse(err)
    }
}

fn file_double_verbose<P: AsRef<Path>>(file_path: P) -> Result<i32, CliError> {
    let mut file = try!(File::open(file_path).map_err(CliError::Io));
    let mut contents = String::new();
    try!(file.read_to_string(&mut contents).map_err(CliError::Io));
    let n: i32 = try!(contents.trim().parse().map_err(CliError::Parse));
    Ok(2 * n)
}
```

`CliError`分別為`io::Error`和`num::ParseIntError`實現了`From`這個trait，所有調用`try!`的時候這兩種錯誤類型都能轉化成`CliError`。

### 總結

熟練使用`Option`和`Result`是編寫 **Rust** 代碼的關鍵，**Rust** 優雅的錯誤處理離不開值返回的錯誤形式，編寫代碼時提供給使用者詳細的錯誤信息是值得推崇的。
