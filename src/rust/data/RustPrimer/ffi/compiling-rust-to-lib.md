# 將Rust編譯成庫
上一章講述瞭如何從rust中調用c庫，這一章我們講如何把rust編譯成庫讓別的語言通過cffi調用。

## 調用約定和mangle
正如上一章講述的，為了能讓rust的函數通過ffi被調用，需要加上`extern "C"`對函數進行修飾。

但由於rust支持重載，所以函數名會被編譯器進行混淆，就像c++一樣。因此當你的函數被編譯完畢後，函數名會帶上一串表明函數簽名的字符串。

比如：`fn test() {}`會變成`_ZN4test20hf06ae59e934e5641haaE`.
這樣的函數名為ffi調用帶來了困難，因此，rust提供了`#[no_mangle]`屬性為函數修飾。
對於帶有`#[no_mangle]`屬性的函數，rust編譯器不會為它進行函數名混淆。如：

```rust
#[no_mangle]
extern "C" fn test() {}
```

在nm中觀察到為

```
...
00000000001a7820 T test
...
```

至此，`test`函數將能夠被正常的由`cffi`調用。
## 指定`crate`類型
`rustc`默認編譯產生`rust`自用的`rlib`格式庫，要讓`rustc`產生動態鏈接庫或者靜態鏈接庫，需要顯式指定。

1. 方法1: 在文件中指定。
   在文件頭加上`#![crate_type = "foo"]`, 其中`foo`的可選類型有`bin`, `lib`, `rlib`, `dylib`, `staticlib`.分別對應可執行文件，
   默認(將由`rustc`自己決定), `rlib`格式，動態鏈接庫，靜態鏈接庫。
2. 方法2: 編譯時給rustc 傳`--crate-type`參數。參數內容同上。
3. 方法3: 使用cargo，指定`crate-type = ["foo"] `, `foo`可選類型同1

## 小技巧: `Any`

由於在跨越`ffi`過程中，`rust`類型信息會丟失，比如當用`rust`提供一個`OpaqueStruct`給別的語言時：

```rust
use std::mem::transmute;

#[derive(Debug)]
struct Foo<T> {
  t: T
}

#[no_mangle]
extern "C" fn new_foo_vec() -> *const c_void {
    Box::into_raw(Box::new(Foo {t: vec![1,2,3]})) as *const c_void
}

#[no_mangle]
extern "C" fn new_foo_int() -> *const c_void {
    Box::into_raw(Box::new(Foo {t: 1})) as *const c_void
}

fn push_foo_element(t: &mut Foo<Vec<i32>>) {
    t.t.push(1);
}

#[no_mangle]
extern "C" fn push_foo_element_c(foo: *mut c_void){
    let foo2 = unsafe {
        &mut *(foo as *mut Foo<Vec<i32>>) // 這麼確定是Foo<Vec<i32>>? 萬一foo是Foo<i32>怎麼辦？
    };
    push_foo_element(foo3);
}
```

以上代碼中完全不知道`foo`是一個什麼東西。安全也無從說起了，只能靠文檔。
因此在`ffi`調用時往往會喪失掉`rust`類型系統帶來的方便和安全。在這裡提供一個小技巧:使用`Box<Box<Any>>`來包裝你的類型。

`rust`的`Any`類型為`rust`帶來了運行時反射的能力，使用`Any`跨越`ffi`邊界將極大提高程序安全性。

```rust
use std::any::Any;

#[derive(Debug)]
struct Foo<T> {
  t: T
}

#[no_mangle]
extern "C" fn new_foo_vec() -> *const c_void {
    Box::into_raw(Box::new(Box::new(Foo {t: vec![1,2,3]}) as Box<Any>)) as *const c_void
}

#[no_mangle]
extern "C" fn new_foo_int() -> *const c_void {
    Box::into_raw(Box::new(Box::new(Foo {t: 1}) as Box<Any>)) as *const c_void
}

fn push_foo_element(t: &mut Foo<Vec<i32>>) {
    t.t.push(1);
}

#[no_mangle]
extern "C" fn push_foo_element_c(foo: *mut c_void){
    let foo2 = unsafe {
        &mut *(foo as *mut Box<Any>)
    };
    let foo3: Option<&mut Foo<Vec<i32>>> = foo2.downcast_mut(); // 如果foo2不是*const Box<Foo<Vec<i32>>>, 則foo3將會是None
    if let Some(value) = foo3 {
      push_foo_element(value);
    }
}
```

這樣一來，就非常不容易出錯了。
