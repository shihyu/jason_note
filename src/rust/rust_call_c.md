# Call C dynamic library in rust



## 前言

c語言作為系統編程語言統治bit世界已經很久，留下了大量的代碼遺產。rust作為新興語言在一些冷門領域開發，真是裹足前行。rust如果可以調用c，那真是再好不過。

## 一、初始化rust工程

如果是vim寫代碼的用戶，可以直接使用，如果是ide，自行創建工程。

```bash
cargo new --bin test_rust_call_c
```

## 二、生成一個c動態庫

如果瞭解在c裡面生成動態庫的流程可不看，這個使用簡單的add函數(返回兩個入參的和)，演示流程，至於更多的類型轉化可看官方文檔。

### 1.`add.h`

```c
#ifndef _ADD_H
#ifdef __cplusplus
extern "C" {
#endif
int add(int a, int b);
#ifdef __cplusplus
}
#endif
#endif
```

### 2.`add.c`

```c
#include "add.h"
int add(int a, int b) {
    return a + b;
}
```

### 3.`add.so`

```bash
gcc -fPIC -shared add.c -o libadd.so
```

## 三、在rust裡面調用動態庫

### 1.`main.rs`內容

現在開始在rust調用c。這裡需要告訴rust編譯器，c函數原型，使用 extern "C" 包裹下。 使用c函數的地方必須用unsafe塊包裹，默認編譯器使用很嚴格的檢查標準，加上unsafe塊編譯器會把檢查權利讓給開發人員自己。

```rust
extern "C" {
    fn add(a: i32, b: i32) -> i32;
}

fn main() {
    unsafe {
        println!("{}", add(1, 2));
    }
}
```

### 2.編譯

這裡面要告訴rust編譯器要鏈接的動態庫是誰，-l add 會自動補齊然後找libadd.so的文件。-L path。下面的例子是在當前目錄下面找。

```bash
rustc src/main.rs -l add -L .
```

### 3.運行

運行時也要通過LD_LIBRARY_PATH告知動態庫的位置。剩下的就是運行。

```bash
env LD_LIBRARY_PATH=. ./main
```

## 四、優化工程，更符合rust的方式

### 使用`build.rs`編譯，和`三、2`同樣的效果

這裡對上面的編譯方式做些優化，在rust裡面一般是編寫build.rs，生成依賴，以後在生成protobuf或者grpc代碼還可以看到類似套路。

```rust
// build.rs rust的編譯腳本
fn main() {
    println!("cargo:rustc-link-search=."); // 等於rustc -L .
    println!("cargo:rustc-link-lib=dylib=add"); // 等於rustc -ladd
}
```

## 參考資料

https://doc.rust-lang.org/cargo/reference/build-scripts.html

https://zhuanlan.zhihu.com/p/70095462

http://liufuyang.github.io/2020/02/02/call-c-in-rust.html