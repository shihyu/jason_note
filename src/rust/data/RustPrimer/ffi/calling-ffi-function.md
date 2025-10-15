# 調用ffi函數

> 下文提到的ffi皆指cffi。

**Rust**作為一門**系統**級語言，自帶對ffi調用的支持。

## Getting Start
### 引入libc庫

由於`cffi`的數據類型與`rust`不完全相同，我們需要引入`libc`庫來表達對應`ffi`函數中的類型。

在`Cargo.toml`中添加以下行:

```toml
[dependencies]
libc = "0.2.9"
```

在你的rs文件中引入庫:

```rust
extern crate libc
```

在以前`libc`庫是和`rust`一起發佈的，後來libc被移入了`crates.io`通過cargo安裝。

### 聲明你的`ffi`函數

就像`c語言`需要`#include`聲明瞭對應函數的頭文件一樣，`rust`中調用`ffi`也需要對對應函數進行聲明。

```rust
use libc::c_int;
use libc::c_void;
use libc::size_t;

#[link(name = "yourlib")]
extern {
    fn your_func(arg1: c_int, arg2: *mut c_void) -> size_t; // 聲明ffi函數
    fn your_func2(arg1: c_int, arg2: *mut c_void) -> size_t;
    static ffi_global: c_int; // 聲明ffi全局變量
}
```

聲明一個`ffi`庫需要一個標記有`#[link(name = "yourlib")]`的`extern`塊。`name`為對應的庫(`so`/`dll`/`dylib`/`a`)的名字。
如：如果你需要`snappy`庫(`libsnappy.so`/`libsnappy.dll`/`libsnappy.dylib`/`libsnappy.a`), 則對應的`name`為`snappy`。
在一個`extern塊`中你可以聲明任意多的函數和變量。

### 調用ffi函數

聲明完成後就可以進行調用了。
由於此函數來自外部的c庫，所以rust並不能保證該函數的安全性。因此，調用任何一個`ffi`函數需要一個`unsafe`塊。

```rust
let result: size_t = unsafe {
    your_func(1 as c_int, Box::into_raw(Box::new(3)) as *mut c_void)
};
```

### 封裝`unsafe`，暴露安全接口

作為一個庫作者，對外暴露不安全接口是一種非常不合格的做法。在做c庫的`rust binding`時，我們做的最多的將是將不安全的c接口封裝成一個安全接口。
通常做法是：在一個叫`ffi.rs`之類的文件中寫上所有的`extern塊`用以聲明ffi函數。在一個叫`wrapper.rs`之類的文件中進行包裝：

```rust
// ffi.rs
#[link(name = "yourlib")]
extern {
    fn your_func(arg1: c_int, arg2: *mut c_void) -> size_t;
}
```

```rust
// wrapper.rs
fn your_func_wrapper(arg1: i32, arg2: &mut i32) -> isize {
    unsafe { your_func(1 as c_int, Box::into_raw(Box::new(3)) as *mut c_void) } as isize
}
```

對外暴露(pub use) `your_func_wrapper`函數即可。

## 數據結構對應

`libc`為我們提供了很多原始數據類型，比如`c_int`, `c_float`等，但是對於自定義類型，如結構體，則需要我們自行定義。

### 結構體

`rust`中結構體默認的內存表示和c並不兼容。如果要將結構體傳給ffi函數，請為`rust`的結構體打上標記：

```rust
#[repr(C)]
struct RustObject {
    a: c_int,
    // other members
}
```

此外，如果使用`#[repr(C, packed)]`將不為此結構體填充空位用以對齊。

### Union

比較遺憾的是，rust到目前為止(2016-03-31)還沒有一個很好的應對c的union的方法。只能通過一些hack來實現。([對應rfc](https://github.com/rust-lang/rfcs/pull/1444))

### Enum

和`struct`一樣，添加`#[repr(C)]`標記即可。

### 回調函數

和c庫打交道時，我們經常會遇到一個函數接受另一個回調函數的情況。將一個`rust`函數轉變成c可執行的回調函數非常簡單：在函數前面加上`extern "C"`:

```rust
extern "C" fn callback(a: c_int) { // 這個函數是傳給c調用的
    println!("hello {}!", a);
}

#[link(name = "yourlib")]
extern {
   fn run_callback(data: i32, cb: extern fn(i32));
}

fn main() {
    unsafe {
        run_callback(1 as i32, callback); // 打印 1
    }
}
```

對應c庫代碼:

```c
typedef void (*rust_callback)(int32_t);

void run_callback(int32_t data, rust_callback callback) {
    callback(data); // 調用傳過來的回調函數
}
```

### 字符串

rust為了應對不同的情況，有很多種字符串類型。其中`CStr`和`CString`是專用於`ffi`交互的。

#### CStr

對於產生於c的字符串(如在c程序中使用`malloc`產生)，rust使用`CStr`來表示，和`str`類型對應，表明我們並不擁有這個字符串。

```rust
use std::ffi::CStr;
use libc::c_char;
#[link(name = "yourlib")]
extern {
    fn char_func() -> *mut c_char;
}

fn get_string() -> String {
    unsafe {
        let raw_string: *mut c_char = char_func();
        let cstr = CStr::from_ptr(my_string());
        cstr.to_string_lossy().into_owned()
    }
}
```

在這裡`get_string`使用`CStr::from_ptr`從c的`char*`獲取一個字符串，並且轉化成了一個String.

* 注意to_string_lossy()的使用：因為在rust中一切字符都是採用utf8表示的而c不是，
  因此如果要將c的字符串轉換到rust字符串的話，需要檢查是否都為有效`utf-8`字節。`to_string_lossy`將返回一個`Cow<str>`類型，
  即如果c字符串都為有效`utf-8`字節，則將其0開銷地轉換成一個`&str`類型，若不是，rust會將其拷貝一份並且將非法字節用`U+FFFD`填充。

#### CString

和`CStr`表示從c中來，rust不擁有歸屬權的字符串相反，`CString`表示由rust分配，用以傳給c程序的字符串。

```rust
use std::ffi::CString;
use std::os::raw::c_char;

extern {
    fn my_printer(s: *const c_char);
}

let c_to_print = CString::new("Hello, world!").unwrap();
unsafe {
    my_printer(c_to_print.as_ptr()); // 使用 as_ptr 將CString轉化成char指針傳給c函數
}
```

注意c字符串中並不能包含`\0`字節(因為`\0`用來表示c字符串的結束符),因此`CString::new`將返回一個`Result`，
如果輸入有`\0`的話則為`Error(NulError)`。

### 不透明結構體

C庫存在一種常見的情況：庫作者並不想讓使用者知道一個數據類型的具體內容，因此常常提供了一套工具函數，並使用`void*`或不透明結構體傳入傳出進行操作。
比較典型的是`ncurse`庫中的`WINDOW`類型。

當參數是`void*`時，在rust中可以和c一樣，使用對應類型`*mut libc::c_void`進行操作。如果參數為不透明結構體，rust中可以使用空白`enum`進行代替:

```rust
enum OpaqueStruct {}

extern "C" {
    pub fn foo(arg: *mut OpaqueStruct);
}
```

C代碼：

```c
struct OpaqueStruct;
void foo(struct OpaqueStruct *arg);
```

### 空指針

另一種很常見的情況是需要一個空指針。請使用`0 as *const _` 或者 `std::ptr::null()`來生產一個空指針。

## 內存安全

由於`ffi`跨越了rust邊界，rust編譯器此時無法保障代碼的安全性，所以在涉及ffi操作時要格外注意。

### 析構問題

在涉及ffi調用時最常見的就是析構問題：這個對象由誰來析構？是否會洩露或use after free？
有些情況下c庫會把一類類型`malloc`了以後傳出來，然後不再關係它的析構。因此在做ffi操作時請為這些類型實現析構(`Drop Trait`).

### 可空指針優化

當`rust`的一個`enum`為一種特殊結構：它有兩種實例，一種為空，另一種只有一個數據域的時候，rustc會開啟空指針優化將其優化成一個指針。
比如`Option<extern "C" fn(c_int) -> c_int>`會被優化成一個可空的函數指針。

### ownership處理

在rust中，由於編譯器會自動插入析構代碼到塊的結束位置，在使用`owned`類型時要格外的注意。

```rust
extern {
    pub fn foo(arg: extern fn() -> *const c_char);
}

extern "C" fn danger() -> *const c_char {
    let cstring = CString::new("I'm a danger string").unwrap();
    cstring.as_ptr()
}  // 由於CString是owned類型，在這裡cstring被rust free掉了。USE AFTER FREE! too young!

fn main() {
  unsafe {
        foo(danger); // boom !!
    }
}
```

由於`as_ptr`接受一個`&self`作為參數(`fn as_ptr(&self) -> *const c_char`)，`as_ptr`以後`ownership`仍然歸rust所有。因此rust會在函數退出時進行析構。
正確的做法是使用`into_raw()`來代替`as_ptr()`。由於`into_raw`的簽名為`fn into_raw(self) -> *mut c_char`，接受的是`self`,產生了`ownership`轉移，
因此`danger`函數就不會將`cstring`析構了。

### panic

由於在`ffi`中`panic`是未定義行為，切忌在`cffi`時`panic`包括直接調用`panic!`,`unimplemented!`,以及強行`unwrap`等情況。
當你寫`cffi`時，記住：你寫下的每個單詞都可能是發射**核彈**的密碼！

## 靜態庫/動態庫

前面提到了聲明一個外部庫的方式--`#[link]`標記，此標記默認為動態庫。但如果是靜態庫，可以使用`#[link(name = "foo", kind = "static")]`來標記。
此外，對於osx的一種特殊庫--`framework`, 還可以這樣標記`#[link(name = "CoreFoundation", kind = "framework")]`.

## 調用約定

前面看到，聲明一個被c調用的函數時，採用`extern "C" fn`的語法。此處的`"C"`即為c調用約定的意思。此外，rust還支持：

* stdcall
* aapcs
* cdecl
* fastcall
* vectorcall //這種call約定暫時需要開啟abi_vectorcall feature gate.
* Rust
* rust-intrinsic
* system
* C
* win64

## bindgen

是不是覺得把一個個函數和全局變量在`extern塊`中去聲明，對應的數據結構去手動創建特別麻煩？沒關係，`rust-bindgen`來幫你搞定。
`rust-bindgen`是一個能從對應c頭文件自動生成函數聲明和數據結構的工具。創建一個綁定只需要`./bindgen [options] input.h`即可。
[項目地址](https://github.com/crabtw/rust-bindgen)
