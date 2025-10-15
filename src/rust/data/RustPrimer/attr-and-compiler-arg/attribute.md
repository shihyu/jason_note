## 屬性

屬性（Attribute）是一種通用的用於表達元數據的特性，借鑑ECMA-334(C#)的語法來實現ECMA-335中描述的Attributes。屬性只能應用於Item（元素、項），
例如 `use` 聲明、模塊、函數等。

### 元素

在Rust中，Item是Crate（庫）的一個組成部分。它包括

* `extern crate`聲明
* `use`聲明
* 模塊（模塊是一個Item的容器）
* 函數
* `type`定義
* 結構體定義
* 枚舉類型定義
* 常量定義
* 靜態變量定義
* Trait定義
* 實現（Impl）

這些Item是可以互相嵌套的，比如在一個函數中定義一個靜態變量、在一個模塊中使用`use`聲明或定義一個結構體。這些定義在某個作用域裡面的Item跟你把
它寫到最外層作用域所實現的功能是一樣的，只不過你要訪問這些嵌套的Item就必須使用路徑（Path），如`a::b::c`。但一些外層的Item不允許你使用路徑去
訪問它的子Item，比如函數，在函數中定義的靜態變量、結構體等，是不可以通過路徑來訪問的。

### 屬性的語法

屬性的語法借鑑於C#，看起來像是這樣子的

```rust
#[name(arg1, arg2 = "param")]
```

它是由一個`#`開啟，後面緊接著一個`[]`，裡面便是屬性的具體內容，它可以有如下幾種寫法：

* 單個標識符代表的屬性名，如`#[unix]`
* 單個標識符代表屬性名，後面緊跟著一個`=`，然後再跟著一個字面量（Literal），組成一個鍵值對，如`#[link(name = "openssl")]`
* 單個標識符代表屬性名，後面跟著一個逗號隔開的子屬性的列表，如`#[cfg(and(unix, not(windows)))]`

在`#`後面還可以緊跟一個`!`，比如`#![feature(box_syntax)]`，這表示這個屬性是應用於它所在的這個Item。而如果沒有`!`則表示這個屬性僅應用於緊接著的那個Item。

例如：

```rust
// 為這個crate開啟box_syntax這個新特性
#![feature(box_syntax)]

// 這是一個單元測試函數
#[test]
fn test_foo() {
    /* ... */
}

// 條件編譯，只會在編譯目標為Linux時才會生效
#[cfg(target_os="linux")]
mod bar {
    /* ... */
}

// 為以下的這個type定義關掉non_camel_case_types的編譯警告
#[allow(non_camel_case_types)]
type int8_t = i8;
```

### 應用於Crate的屬性

* `crate_name` - 指定Crate的名字。如`#[crate_name = "my_crate"]`則可以讓編譯出的庫名字為`libmy_crate.rlib`。
* `crate_type` - 指定Crate的類型，有以下幾種選擇
    - `"bin"` - 編譯為可執行文件；
    - `"lib"` - 編譯為庫；
    - `"dylib"` - 編譯為動態鏈接庫；
    - `"staticlib"` - 編譯為靜態鏈接庫；
    - `"rlib"` - 編譯為Rust特有的庫文件，它是一種特殊的靜態鏈接庫格式，它裡面會含有一些元數據供編譯器使用，最終會靜態鏈接到目標文件之中。

  例`#![crate_type = "dylib"]`。
* `feature` - 可以開啟一些不穩定特性，只可在nightly版的編譯器中使用。
* `no_builtins` - 去掉內建函數。
* `no_main`- 不生成`main`這個符號，當你需要鏈接的庫中已經定義了`main`函數時會用到。
* `no_start` - 不鏈接自帶的`native`庫。
* `no_std` - 不鏈接自帶的`std`庫。
* `plugin` - 加載編譯器插件，一般用於加載自定義的編譯器插件庫。用法是

  ```rust
  // 加載foo, bar兩個插件
  #![plugin(foo, bar)]
  // 或者給插件傳入必要的初始化參數
  #![plugin(foo(arg1, arg2))]
  ```

* `recursive_limit` - 設置在編譯期最大的遞歸層級。比如自動解引用、遞歸定義的宏等。默認設置是`#![recursive_limit = "64"]`

### 應用於模塊的屬性

* `no_implicit_prelude` - 取消自動插入`use std::prelude::*`。
* `path` - 設置此`mod`的文件路徑。

  如聲明`mod a;`，則尋找
    - 本文件夾下的`a.rs`文件
    - 本文件夾下的`a/mod.rs`文件

  ```rust
  #[cfg(unix)]
  #[path = "sys/unix.rs"]
  mod sys;

  #[cfg(windows)]
  #[path = "sys/windows.rs"]
  mod sys;
  ```

### 應用於函數的屬性

* `main` - 把這個函數作為入口函數，替代`fn main`，會被入口函數（Entry Point）調用。
* `plugin_registrar` - 編寫編譯器插件時用，用於定義編譯器插件的入口函數。
* `start` - 把這個函數作為入口函數（Entry Point），改寫 `start` language item。
* `test` - 指明這個函數為單元測試函數，在非測試環境下不會被編譯。
* `should_panic` - 指明這個單元測試函數必然會panic。
* `cold` - 指明這個函數很可能是不會被執行的，因此優化的時候特別對待它。

```rust
// 把`my_main`作為主函數
#[main]
fn my_main() {

}

// 把`plugin_registrar`作為此編譯器插件的入口函數
#[plugin_registrar]
pub fn plugin_registrar(reg: &mut Registry) {
    reg.register_macro("rn", expand_rn);
}

// 把`entry_point`作為入口函數，不再執行標準庫中的初始化流程
#[start]
fn entry_point(argc: isize, argv: *const *const u8) -> isize {

}

// 定義一個單元測試
// 這個單元測試一定會panic
#[test]
#[should_panic]
fn my_test() {
    panic!("I expected to be panicked");
}

// 這個函數很可能是不會執行的，
// 所以優化的時候就換種方式
#[cold]
fn unlikely_to_be_executed() {

}
```

### 應用於全局靜態變量的屬性

* `thread_local` - 只可用於`static mut`，表示這個變量是thread local的。

### 應用於FFI的屬性

`extern`塊可以應用以下屬性

* `link_args` - 指定鏈接時給鏈接器的參數，平臺和實現相關。
* `link` - 說明這個塊需要鏈接一個native庫，它有以下參數：
    - `name` - 庫的名字，比如`libname.a`的名字是`name`；
    - `kind` - 庫的類型，它包括
        * `dylib` - 動態鏈接庫
        * `static` - 靜態庫
        * `framework` - OS X裡的Framework

  ```rust
  #[link(name = "readline")]
  extern {

  }

  #[link(name = "CoreFoundation", kind = "framework")]
  extern {

  }
  ```

在`extern`塊裡面，可以使用

* `link_name` - 指定這個鏈接的外部函數的名字或全局變量的名字；
* `linkage` - 對於全局變量，可以指定一些LLVM的鏈接類型（ http://llvm.org/docs/LangRef.html#linkage-types ）。

對於`enum`類型，可以使用

* `repr` - 目前接受`C`，`C`表示兼容C ABI。

```rust
#[repr(C)]
enum eType {
    Operator,
    Indicator,
}
```

對於`struct`類型，可以使用

* `repr` - 目前只接受`C`和`packed`，`C`表示結構體兼容C ABI，`packed`表示移除字段間的padding。

### 用於宏的屬性

* `macro_use` - 把模塊或庫中定義的宏導出來
    - 應用於`mod`上，則把此模塊內定義的宏導出到它的父模塊中
    - 應用於`extern crate`上，則可以接受一個列表，如

      ```rust
      #[macro_use(debug, trace)]
      extern crate log;
      ```

      則可以只導入列表中指定的宏，若不指定則導入所有的宏。

* `macro_reexport` - 應用於`extern crate`上，可以再把這些導入的宏再輸出出去給別的庫使用。

* `macro_export` - 應於在宏上，可以使這個宏可以被導出給別的庫使用。

* `no_link` - 應用於`extern crate`上，表示即使我們把它裡面的庫導入進來了，但是不要把這個庫鏈接到目標文件中。

### 其它屬性

* `export_function` - 用於靜態變量或函數，指定它們在目標文件中的符號名。

* `link_section` - 用於靜態變量或函數，表示應該把它們放到哪個段中去。

* `no_mangle` - 可以應用於任意的Item，表示取消對它們進行命名混淆，直接把它們的名字作為符號寫到目標文件中。

* `simd` - 可以用於元組結構體上，並自動實現了數值運算符，這些操作會生成相應的SIMD指令。

* `doc` - 為這個Item綁定文檔，跟`///`的功能一樣，用法是

  ```rust
  #[doc = "This is a doc"]
  struct Foo {}
  ```

### 條件編譯

有時候，我們想針對不同的編譯目標來生成不同的代碼，比如在編寫跨平臺模塊時，針對Linux和Windows分別使用不同的代碼邏輯。

條件編譯基本上就是使用`cfg`這個屬性，直接看例子

```rust
#[cfg(target_os = "macos")]
fn cross_platform() {
    // Will only be compiled on Mac OS, including Mac OS X
}

#[cfg(target_os = "windows")]
fn cross_platform() {
    // Will only be compiled on Windows
}

// 若條件`foo`或`bar`任意一個成立，則編譯以下的Item
#[cfg(any(foo, bar))]
fn need_foo_or_bar() {

}

// 針對32位的Unix系統
#[cfg(all(unix, target_pointer_width = "32"))]
fn on_32bit_unix() {

}

// 若`foo`不成立時編譯
#[cfg(not(foo))]
fn needs_not_foo() {

}
```

其中，`cfg`可接受的條件有

* `debug_assertions` - 若沒有開啟編譯優化時就會成立。

* `target_arch = "..."` - 目標平臺的CPU架構，包括但不限於`x86`, `x86_64`, `mips`, `powerpc`, `arm`或`aarch64`。

* `target_endian = "..."` - 目標平臺的大小端，包括`big`和`little`。

* `target_env = "..."` - 表示使用的運行庫，比如`musl`表示使用的是MUSL的libc實現, `msvc`表示使用微軟的MSVC，`gnu`表示使用GNU的實現。
  但在部分平臺這個數據是空的。

* `target_family = "..."` - 表示目標操作系統的類別，比如`windows`和`unix`。這個屬性可以直接作為條件使用，如`#[unix]`，`#[cfg(unix)]`。

* `target_os = "..."` - 目標操作系統，包括但不限於`windows`, `macos`, `ios`, `linux`, `android`, `freebsd`, `dragonfly`, `bitrig`, `openbsd`, `netbsd`。

* `target_pointer_width = "..."` - 目標平臺的指針寬度，一般就是`32`或`64`。

* `target_vendor = "..."` - 生產商，例如`apple`, `pc`或大多數Linux系統的`unknown`。

* `test` - 當啟動了單元測試時（即編譯時加了`--test`參數，或使用`cargo test`）。

還可以根據一個條件去設置另一個條件，使用`cfg_attr`，如

```rust
#[cfg_attr(a, b)]
```

這表示若`a`成立，則這個就相當於`#[cfg(b)]`。

條件編譯屬性只可以應用於Item，如果想應用在非Item中怎麼辦呢？可以使用`cfg!`宏，如

```rust
if cfg!(target_arch = "x86") {

} else if cfg!(target_arch = "x86_64") {

} else if cfg!(target_arch = "mips") {

} else {

}
```

這種方式不會產生任何運行時開銷，因為不成立的條件相當於裡面的代碼根本不可能被執行，編譯時會直接被優化掉。

### Linter參數

目前的Rust編譯器已自帶的Linter，它可以在編譯時靜態幫你檢測不用的代碼、死循環、編碼風格等等。Rust提供了一系列的屬性用於控制Linter的行為

* `allow(C)` - 編譯器將不會警告對於`C`條件的檢查錯誤。
* `deny(C)` - 編譯器遇到違反`C`條件的錯誤將直接當作編譯錯誤。
* `forbit(C)` - 行為與`deny(C)`一樣，但這個將不允許別人使用`allow(C)`去修改。
* `warn(C)` - 編譯器將對於`C`條件的檢查錯誤輸出警告。

編譯器支持的Lint檢查可以通過執行`rustc -W help`來查看。

### 內聯參數

內聯函數即建議編譯器可以考慮把整個函數拷貝到調用者的函數體中，而不是生成一個`call`指令調用過去。這種優化對於短函數非常有用，有利於提高性能。

編譯器自己會根據一些默認的條件來判斷一個函數是不是應該內聯，若一個不應該被內聯的函數被內聯了，實際上會導致整個程序更慢。

可選的屬性有：

* `#[inline]` - 建議編譯器內聯這個函數
* `#[inline(always)]` - 要求編譯器必須內聯這個函數
* `#[inline(never)]` - 要求編譯器不要內聯這個函數

內聯會導致在一個庫裡面的代碼被插入到另一個庫中去。

### 自動實現Trait

編譯器提供一個編譯器插件叫作`derive`，它可以幫你去生成一些代碼去實現（impl）一些特定的Trait，如

```rust
#[derive(PartialEq, Clone)]
struct Foo<T> {
    a: i32,
    b: T,
}
```

編譯器會自動為你生成以下的代碼

```rust
impl<T: PartialEq> PartialEq for Foo<T> {
    fn eq(&self, other: &Foo<T>) -> bool {
        self.a == other.a && self.b == other.b
    }

    fn ne(&self, other: &Foo<T>) -> bool {
        self.a != other.a || self.b != other.b
    }
}

impl<T: Clone> Clone for Foo<T> {
    fn clone(&self) -> Foo<T> {
        Foo {
            a: self.a.clone(),
            b: self.b.clone(),
        }
    }
}
```

目前`derive`僅支持標準庫中部分的Trait。

### 編譯器特性

在非穩定版的Rust編譯器中，可以使用一些不穩定的功能，比如一些還在討論中的新功能、正在實現中的功能等。Rust編譯器提供一個應用於Crate的屬性`feature`來啟用這些不穩定的功能，如

```rust
#![feature(advanced_slice_patterns, box_syntax, asm)]
```

具體可使用的編譯器特性會因編譯器版本的發佈而不同，具體請閱讀官方文檔。
