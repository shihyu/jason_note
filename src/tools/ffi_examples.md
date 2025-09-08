# FFI 跨語言程式設計範例指南

## 目錄
- [簡介](#簡介)
- [完整範例專案](#完整範例專案)
- [1. C 函數庫（基礎）](#1-c-函數庫基礎)
- [2. Python 調用 C](#2-python-調用-c)
- [3. Rust 調用 C](#3-rust-調用-c)
- [4. Rust 創建函式庫供 Python 調用](#4-rust-創建函式庫供-python-調用)
- [5. C++ 與 C 的互操作](#5-c-與-c-的互操作)
- [重要注意事項](#重要注意事項)
- [編譯指令總結](#編譯指令總結)

## 簡介

FFI (Foreign Function Interface) 是一種讓不同程式語言之間能夠相互調用的機制。本文檔展示 C/C++、Rust 和 Python 三種語言之間的互操作範例。

## 完整範例專案

**📁 完整可執行的範例代碼已放在 `data/ffi_examples/` 目錄中！**

### 快速開始

```bash
# 進入範例目錄
cd data/ffi_examples

# 編譯所有函式庫並執行測試
make all

# 只編譯
make build

# 只測試
make test

# 查看幫助
make help
```

### 專案結構

```
data/ffi_examples/
├── c_libs/              # C/C++ 函式庫
│   ├── math_lib.c      # C 函式庫實作（擴展版）
│   ├── math_lib.h      # C 函式庫標頭檔
│   └── cpp_wrapper.cpp # C++ 封裝與擴展
├── python/              # Python 範例
│   ├── python_ffi.py        # Python 調用 C（完整測試）
│   ├── python_call_rust.py  # Python 調用 Rust（完整測試）
│   └── python_call_cpp.py   # Python 調用 C++（完整測試）
├── rust_libs/           # Rust 程式
│   ├── rust_ffi/       # Rust 調用 C 範例
│   └── rust_lib/       # Rust 函式庫供其他語言調用
├── Makefile            # 自動化編譯腳本（支援所有平台）
└── README.md           # 詳細說明文件
```

### 範例特色

1. **完整的測試案例**：每個範例都包含完整的測試函數
2. **錯誤處理**：展示正確的錯誤處理方式
3. **記憶體管理**：示範跨語言邊界的記憶體管理
4. **結構體傳遞**：展示複雜數據結構的傳遞
5. **字串處理**：處理不同語言的字串編碼問題
6. **自動化編譯**：Makefile 支援一鍵編譯和測試

## 1. C 函數庫（基礎）

首先創建一個簡單的 C 函數庫作為被調用方：

### math_lib.c
```c
#include <stdio.h>

// 簡單的加法函數
int add(int a, int b) {
    return a + b;
}

// 計算階乘
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// 打印訊息
void say_hello(const char* name) {
    printf("Hello, %s from C!\n", name);
}
```

### math_lib.h
```c
#ifndef MATH_LIB_H
#define MATH_LIB_H

int add(int a, int b);
int factorial(int n);
void say_hello(const char* name);

#endif
```

### 編譯指令
```bash
# Linux/Mac
gcc -shared -fPIC -o libmath.so math_lib.c

# Windows
gcc -shared -o math.dll math_lib.c
```

## 2. Python 調用 C

### python_ffi.py
```python
import ctypes
import os

# 載入 C 函式庫
if os.name == 'nt':  # Windows
    lib = ctypes.CDLL('./math.dll')
else:  # Linux/Mac
    lib = ctypes.CDLL('./libmath.so')

# 定義函數簽名
lib.add.argtypes = (ctypes.c_int, ctypes.c_int)
lib.add.restype = ctypes.c_int

lib.factorial.argtypes = (ctypes.c_int,)
lib.factorial.restype = ctypes.c_int

lib.say_hello.argtypes = (ctypes.c_char_p,)
lib.say_hello.restype = None

# 使用 C 函數
result = lib.add(10, 20)
print(f"10 + 20 = {result}")

fact = lib.factorial(5)
print(f"5! = {fact}")

lib.say_hello(b"Python")
```

### 執行
```bash
python python_ffi.py
```

### 預期輸出
```
10 + 20 = 30
5! = 120
Hello, Python from C!
```

## 3. Rust 調用 C

### 專案結構
```
rust_ffi/
├── Cargo.toml
└── src/
    └── main.rs
```

### Cargo.toml
```toml
[package]
name = "rust_ffi"
version = "0.1.0"
edition = "2021"

[dependencies]
libc = "0.2"
```

### src/main.rs
```rust
use std::ffi::CString;
use std::os::raw::{c_char, c_int};

// 聲明外部 C 函數
#[link(name = "math")]
extern "C" {
    fn add(a: c_int, b: c_int) -> c_int;
    fn factorial(n: c_int) -> c_int;
    fn say_hello(name: *const c_char);
}

fn main() {
    unsafe {
        // 調用 add 函數
        let result = add(10, 20);
        println!("10 + 20 = {}", result);
        
        // 調用 factorial 函數
        let fact = factorial(5);
        println!("5! = {}", fact);
        
        // 調用 say_hello 函數
        let name = CString::new("Rust").unwrap();
        say_hello(name.as_ptr());
    }
}
```

### 編譯與執行
```bash
# 設置函式庫路徑
export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH

# 編譯並執行
cargo build
cargo run
```

## 4. Rust 創建函式庫供 Python 調用

### 專案結構
```
rust_lib/
├── Cargo.toml
└── src/
    └── lib.rs
```

### Cargo.toml
```toml
[package]
name = "rust_lib"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
```

### src/lib.rs
```rust
use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_int};

#[no_mangle]
pub extern "C" fn rust_add(a: c_int, b: c_int) -> c_int {
    a + b
}

#[no_mangle]
pub extern "C" fn rust_multiply(a: c_int, b: c_int) -> c_int {
    a * b
}

#[no_mangle]
pub extern "C" fn rust_greet(name: *const c_char) -> *mut c_char {
    unsafe {
        let name_str = CStr::from_ptr(name).to_str().unwrap();
        let greeting = format!("Hello, {} from Rust!", name_str);
        CString::new(greeting).unwrap().into_raw()
    }
}

#[no_mangle]
pub extern "C" fn free_string(s: *mut c_char) {
    unsafe {
        if s.is_null() { return; }
        CString::from_raw(s);
    }
}
```

### 編譯 Rust 函式庫
```bash
cargo build --release
```

### Python 調用 Rust (python_call_rust.py)
```python
import ctypes
import platform

# 載入 Rust 函式庫
system = platform.system()
if system == "Linux":
    lib = ctypes.CDLL('./target/release/librust_lib.so')
elif system == "Darwin":  # macOS
    lib = ctypes.CDLL('./target/release/librust_lib.dylib')
elif system == "Windows":
    lib = ctypes.CDLL('./target/release/rust_lib.dll')

# 定義函數簽名
lib.rust_add.argtypes = (ctypes.c_int, ctypes.c_int)
lib.rust_add.restype = ctypes.c_int

lib.rust_multiply.argtypes = (ctypes.c_int, ctypes.c_int)
lib.rust_multiply.restype = ctypes.c_int

lib.rust_greet.argtypes = (ctypes.c_char_p,)
lib.rust_greet.restype = ctypes.c_char_p

lib.free_string.argtypes = (ctypes.c_char_p,)

# 使用 Rust 函數
print(f"Rust: 5 + 3 = {lib.rust_add(5, 3)}")
print(f"Rust: 4 * 7 = {lib.rust_multiply(4, 7)}")

# 字串處理
greeting = lib.rust_greet(b"World")
print(greeting.decode('utf-8'))
lib.free_string(greeting)  # 釋放記憶體
```

## 5. C++ 與 C 的互操作

### cpp_wrapper.cpp
```cpp
#include <iostream>
#include <string>

extern "C" {
    #include "math_lib.h"
}

// C++ 類別
class Calculator {
public:
    int multiply(int a, int b) {
        return a * b;
    }
    
    // 使用 C 函數
    int add_and_factorial(int a, int b) {
        int sum = add(a, b);  // 調用 C 函數
        return factorial(sum); // 調用 C 函數
    }
};

// 導出 C 介面供其他語言使用
extern "C" {
    Calculator* Calculator_new() { 
        return new Calculator(); 
    }
    
    void Calculator_delete(Calculator* calc) { 
        delete calc; 
    }
    
    int Calculator_multiply(Calculator* calc, int a, int b) {
        return calc->multiply(a, b);
    }
    
    int Calculator_add_and_factorial(Calculator* calc, int a, int b) {
        return calc->add_and_factorial(a, b);
    }
}
```

### 編譯 C++ 函式庫
```bash
g++ -shared -fPIC -o libcpp_wrapper.so cpp_wrapper.cpp -L. -lmath
```

### Python 調用 C++ (python_call_cpp.py)
```python
import ctypes

# 載入 C++ 函式庫
lib = ctypes.CDLL('./libcpp_wrapper.so')

# 定義 Calculator 類別的函數
lib.Calculator_new.restype = ctypes.c_void_p

lib.Calculator_delete.argtypes = (ctypes.c_void_p,)

lib.Calculator_multiply.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
lib.Calculator_multiply.restype = ctypes.c_int

lib.Calculator_add_and_factorial.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
lib.Calculator_add_and_factorial.restype = ctypes.c_int

# 創建 Calculator 實例
calc = lib.Calculator_new()

# 使用 C++ 方法
result = lib.Calculator_multiply(calc, 6, 7)
print(f"C++: 6 * 7 = {result}")

# 使用混合 C/C++ 功能
result = lib.Calculator_add_and_factorial(calc, 3, 2)
print(f"C++/C: factorial(3 + 2) = {result}")

# 清理記憶體
lib.Calculator_delete(calc)
```

## 重要注意事項

### 1. C ABI 相容性
- 所有語言都支援 C ABI (Application Binary Interface)
- C++ 需要使用 `extern "C"` 來確保 C 相容性
- Rust 使用 `#[no_mangle]` 和 `extern "C"` 屬性

### 2. 類型映射

| C 類型 | Python (ctypes) | Rust |
|--------|----------------|------|
| int | c_int | c_int |
| char* | c_char_p | *const c_char |
| void | None | () |
| float | c_float | c_float |
| double | c_double | c_double |

### 3. 記憶體管理
- **誰分配，誰釋放**：同一語言分配的記憶體應由同一語言釋放
- Rust 的 `CString::into_raw()` 需要對應的 `CString::from_raw()` 來釋放
- Python 的 ctypes 自動管理簡單類型，但複雜類型需要手動管理

### 4. 字串處理
- C 使用 null-terminated 字串
- Python 字串需要編碼為 bytes (使用 `b"string"` 或 `.encode()`)
- Rust 需要使用 `CString` 和 `CStr` 進行轉換

### 5. 錯誤處理
- FFI 邊界不能傳遞異常
- 建議使用錯誤碼或結果結構體
- Rust 的 panic 不應該跨越 FFI 邊界

## 編譯指令總結

### C 函式庫
```bash
# Linux/Mac
gcc -shared -fPIC -o libmath.so math_lib.c

# Windows
gcc -shared -o math.dll math_lib.c
```

### Rust 函式庫
```bash
cargo build --release
```

### C++ 函式庫
```bash
# Linux/Mac
g++ -shared -fPIC -o libcpp_wrapper.so cpp_wrapper.cpp -L. -lmath

# Windows
g++ -shared -o cpp_wrapper.dll cpp_wrapper.cpp -L. -lmath
```

### 設置函式庫路徑
```bash
# Linux
export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH

# macOS
export DYLD_LIBRARY_PATH=.:$DYLD_LIBRARY_PATH

# Windows
set PATH=%PATH%;.
```

## 專案結構建議

```
ffi_project/
├── c_libs/
│   ├── math_lib.c
│   ├── math_lib.h
│   └── cpp_wrapper.cpp
├── rust_libs/
│   ├── rust_ffi/
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── main.rs
│   └── rust_lib/
│       ├── Cargo.toml
│       └── src/
│           └── lib.rs
├── python/
│   ├── python_ffi.py
│   ├── python_call_rust.py
│   └── python_call_cpp.py
├── build.sh
└── README.md
```

## 建置腳本範例 (build.sh)

```bash
#!/bin/bash

echo "Building C library..."
gcc -shared -fPIC -o libmath.so c_libs/math_lib.c

echo "Building C++ wrapper..."
g++ -shared -fPIC -o libcpp_wrapper.so c_libs/cpp_wrapper.cpp -L. -lmath

echo "Building Rust library..."
cd rust_libs/rust_lib
cargo build --release
cd ../..

echo "Copying libraries to root..."
cp rust_libs/rust_lib/target/release/librust_lib.so .

echo "Build complete!"
```

## 結語

FFI 是強大的工具，讓你能夠：
- 重用現有的 C/C++ 函式庫
- 在效能關鍵部分使用系統語言
- 在高階語言中使用低階功能
- 建立多語言的軟體架構

記住始終注意記憶體安全、類型相容性和錯誤處理，這些是 FFI 程式設計的關鍵挑戰。