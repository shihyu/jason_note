## 創建rust動態鏈接庫
- 第一、創建rust庫項目
```go
#cargo new --lib hello
```

- 第二、實現HelloWorld函數
```rust
extern crate libc;
use std::ffi::{CStr, CString};

#[no_mangle] 
pub extern "C" fn rustdemo(name: *const libc::c_char) -> *const libc::c_char {
    let cstr_name = unsafe { CStr::from_ptr(name) };
    let mut str_name = cstr_name.to_str().unwrap().to_string();
    println!("Rust get Input:  \"{}\"", str_name);
    let r_string: &str = " Rust say: Hello Go ";
    str_name.push_str(r_string);
    CString::new(str_name).unwrap().into_raw()
}
```

- 第三、依賴libc，並生成動態鏈接庫
```go
[lib]
crate-type = ["cdylib"]

[dependencies]
libc = "0.2"
```

- 第四、編譯生成動態鏈接庫
```
# cargo build 
# ll target/debug
......
-rwxr-xr-x   1 zhangyanfei  staff  463947  4 13 22:53 libhello.dylib*
```

- 最後、在lib目錄下準備頭文件，並把動態鏈接庫複製出來
libhello.h
```go
char* HelloWorld(char *name);
```

## Go調用rust動態鏈接庫
編寫Go代碼

```go
package main

/*
#cgo LDFLAGS: -L./lib -lrustdemo
#include <stdlib.h>
#include "./lib/rustdemo.h"
*/
import "C"

import (
	"fmt"
	"unsafe"
)

func main() {
	s := "Go say: Hello Rust"

	input := C.CString(s)
	defer C.free(unsafe.Pointer(input))
	o := C.HelloWorld(input)
	output := C.GoString(o)
	fmt.Printf("%s\n", output)
}
```