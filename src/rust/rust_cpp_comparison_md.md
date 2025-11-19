# Rust vs C++ 詳細對比指南

## 前言

Rust 和 C++ 都是系統級程式語言，但設計哲學截然不同。C++ 給你完全的控制權，但需要你自己管理記憶體；Rust 則通過編譯時檢查來確保記憶體安全。

---

## 第1篇 Rust基礎知識

### 第1章 Rust入門

#### 1.1 Rust簡介

**白話解釋：**
- **C++**: 像是一把瑞士刀，功能強大但容易割傷自己
- **Rust**: 像是一把智能刀，有安全鎖，不讓你割傷自己，但學會使用需要時間

**設計理念對比：**
- **C++**: "信任程序員，給他們所有控制權"
- **Rust**: "幫助程序員寫出安全的程式碼"

#### 1.2 第1個程式

**C++ Hello World:**
```cpp
#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    return 0;
}
```

**Rust Hello World:**
```rust
fn main() {
    println!("Hello, World!");
}
```

**差異說明：**
- C++ 需要 `#include` 和 `return 0`
- Rust 更簡潔，`println!` 是宏（macro）
- Rust 不需要明確返回值

#### 1.3 Rust基礎語法

##### 1.3.1 註釋與打印文本

**C++:**
```cpp
// 單行註釋
/* 多行註釋 */
cout << "Hello" << endl;
printf("格式化: %d", 42);
```

**Rust:**
```rust
// 單行註釋
/* 多行註釋 */
println!("Hello");
println!("格式化: {}", 42);
```

**白話解釋：**
- Rust 的 `println!` 更安全，會在編譯時檢查格式
- C++ 的 `printf` 在運行時才檢查，容易出錯

##### 1.3.2 變量和變量可變性

**C++:**
```cpp
int x = 5;          // 可變
const int y = 10;   // 不可變
x = 6;              // OK
// y = 11;          // 編譯錯誤
```

**Rust:**
```rust
let x = 5;          // 不可變（預設）
let mut y = 10;     // 可變
let z = 15;         // 不可變
// x = 6;           // 編譯錯誤
y = 11;             // OK
```

**白話解釋：**
- **C++**: 變數預設可變，要不可變需要加 `const`
- **Rust**: 變數預設不可變，要可變需要加 `mut`
- 這個設計讓程式更安全，因為大部分時候我們不需要改變變數

##### 1.3.3 常量

**C++:**
```cpp
const int MAX_SIZE = 100;
#define PI 3.14159
```

**Rust:**
```rust
const MAX_SIZE: i32 = 100;
const PI: f64 = 3.14159;
```

**差異：**
- Rust 的常量必須指定類型
- Rust 沒有 `#define`，所有常量都是類型安全的

##### 1.3.4 運算符

基本運算符兩者相似，但有一些差異：

**C++:**
```cpp
int a = 5, b = 2;
int result = a / b;  // 整數除法 = 2
```

**Rust:**
```rust
let a = 5;
let b = 2;
let result = a / b;  // 整數除法 = 2
// let mixed = a / 2.0;  // 編譯錯誤！類型不匹配
```

**白話解釋：**
- Rust 不允許不同類型直接運算，需要明確轉換
- 這避免了意外的類型轉換錯誤

##### 1.3.5 流程控制語句

**C++ if 語句:**
```cpp
int x = 5;
if (x > 0) {
    cout << "正數" << endl;
} else if (x < 0) {
    cout << "負數" << endl;
} else {
    cout << "零" << endl;
}
```

**Rust if 語句:**
```rust
let x = 5;
if x > 0 {
    println!("正數");
} else if x < 0 {
    println!("負數");
} else {
    println!("零");
}
```

**Rust 的 if 是表達式:**
```rust
let x = 5;
let description = if x > 0 { "正數" } else { "非正數" };
```

**迴圈比較:**

**C++:**
```cpp
// for 迴圈
for (int i = 0; i < 5; i++) {
    cout << i << endl;
}

// while 迴圈
int i = 0;
while (i < 5) {
    cout << i << endl;
    i++;
}
```

**Rust:**
```rust
// for 迴圈
for i in 0..5 {
    println!("{}", i);
}

// while 迴圈
let mut i = 0;
while i < 5 {
    println!("{}", i);
    i += 1;
}

// loop 迴圈（無限迴圈）
let mut count = 0;
loop {
    println!("{}", count);
    count += 1;
    if count >= 5 {
        break;
    }
}
```

#### 1.4 Rust數據類型

##### 1.4.1 標量類型

**C++:**
```cpp
int a = 42;
float b = 3.14f;
double c = 3.14159;
char d = 'A';
bool e = true;
```

**Rust:**
```rust
let a: i32 = 42;        // 32位整數
let b: f32 = 3.14;      // 32位浮點數
let c: f64 = 3.14159;   // 64位浮點數
let d: char = 'A';      // Unicode字符
let e: bool = true;     // 布林值
```

**白話解釋：**
- Rust 的整數類型更明確：`i8`, `i16`, `i32`, `i64`, `i128`
- Rust 的 `char` 是 4 位元組，支援所有 Unicode 字符
- C++ 的 `char` 只有 1 位元組

##### 1.4.2 複合數據類型

**陣列比較:**

**C++:**
```cpp
int arr[5] = {1, 2, 3, 4, 5};
int arr2[] = {1, 2, 3};  // 大小自動推斷
```

**Rust:**
```rust
let arr: [i32; 5] = [1, 2, 3, 4, 5];
let arr2 = [1, 2, 3];  // 類型推斷為 [i32; 3]
let arr3 = [0; 5];     // [0, 0, 0, 0, 0]
```

**元組比較:**

**C++ (C++11後):**
```cpp
#include <tuple>
std::tuple<int, double, char> tup = std::make_tuple(1, 2.5, 'A');
auto [x, y, z] = tup;  // C++17 結構化綁定
```

**Rust:**
```rust
let tup: (i32, f64, char) = (1, 2.5, 'A');
let (x, y, z) = tup;  // 解構
let first = tup.0;    // 通過索引訪問
```

##### 1.4.3 字符串

這是 Rust 和 C++ 最大的差異之一！

**C++:**
```cpp
#include <string>
std::string s1 = "Hello";
char s2[] = "World";
const char* s3 = "C++";
```

**Rust:**
```rust
let s1 = "Hello";           // &str (字符串切片)
let s2 = String::from("World"); // String (擁有所有權)
let s3 = "Rust".to_string();    // 另一種創建String的方式
```

**白話解釋：**
- **C++**: 字符串類型複雜，容易混淆
- **Rust**: 
  - `&str` 是借用的字符串切片（類似C++的`const char*`）
  - `String` 是擁有所有權的字符串（類似C++的`std::string`）

#### 1.5 函數與閉包

##### 1.5.1 函數

**C++:**
```cpp
int add(int a, int b) {
    return a + b;
}

void greet(const std::string& name) {
    std::cout << "Hello, " << name << std::endl;
}
```

**Rust:**
```rust
fn add(a: i32, b: i32) -> i32 {
    a + b  // 最後一個表達式是返回值
}

fn greet(name: &str) {
    println!("Hello, {}", name);
}
```

**白話解釋：**
- Rust 函數最後一個表達式自動成為返回值
- 如果有分號，就不是返回值了

##### 1.5.2 閉包

**C++ (C++11後):**
```cpp
auto add = [](int a, int b) -> int {
    return a + b;
};

int x = 10;
auto add_x = [x](int a) -> int {
    return a + x;
};
```

**Rust:**
```rust
let add = |a: i32, b: i32| -> i32 {
    a + b
};

let x = 10;
let add_x = |a| a + x;  // 類型推斷
```

**白話解釋：**
- Rust 的閉包語法更簡潔
- Rust 的閉包會自動捕獲環境變量

#### 1.6 類型系統

##### 1.6.1 泛型

**C++:**
```cpp
template<typename T>
T max(T a, T b) {
    return (a > b) ? a : b;
}
```

**Rust:**
```rust
fn max<T: std::cmp::PartialOrd>(a: T, b: T) -> T {
    if a > b { a } else { b }
}
```

**白話解釋：**
- C++ 的模板在實例化時才檢查約束
- Rust 的泛型在定義時就檢查約束（`T: PartialOrd`）

##### 1.6.2 trait

**C++（使用介面）:**
```cpp
class Drawable {
public:
    virtual void draw() = 0;
};

class Circle : public Drawable {
public:
    void draw() override {
        std::cout << "Drawing a circle" << std::endl;
    }
};
```

**Rust:**
```rust
trait Drawable {
    fn draw(&self);
}

struct Circle;

impl Drawable for Circle {
    fn draw(&self) {
        println!("Drawing a circle");
    }
}
```

**白話解釋：**
- C++ 用繼承實現多態
- Rust 用 trait 實現多態，更靈活

##### 1.6.3 類型轉換

**C++:**
```cpp
int x = 42;
double y = static_cast<double>(x);  // 顯式轉換
double z = x;  // 隱式轉換
```

**Rust:**
```rust
let x = 42i32;
let y = x as f64;  // 顯式轉換
// let z: f64 = x;  // 編譯錯誤！無隱式轉換
```

**白話解釋：**
- Rust 不允許隱式類型轉換，避免意外錯誤
- 所有轉換都必須明確

---

## 第2章 Rust基礎

### 2.1 所有權系統

這是 Rust 最獨特的特性！

##### 2.1.1 所有權機制

**C++（手動管理）:**
```cpp
void example() {
    int* ptr = new int(42);
    // 使用 ptr
    delete ptr;  // 必須手動釋放
}
```

**Rust（自動管理）:**
```rust
fn example() {
    let data = Box::new(42);
    // 使用 data
    // 自動釋放，無需手動管理
}
```

**白話解釋：**
- **C++**: "你負責清理你創建的東西"
- **Rust**: "我幫你自動清理，你不用擔心"

##### 2.1.2 引用和借用

**C++:**
```cpp
void function(int& ref) {  // 引用
    ref = 42;
}

void function2(const int& ref) {  // 常量引用
    // ref = 42;  // 錯誤
}
```

**Rust:**
```rust
fn function(r: &mut i32) {  // 可變借用
    *r = 42;
}

fn function2(r: &i32) {  // 不可變借用
    // *r = 42;  // 錯誤
}
```

**借用規則（Rust獨有）:**
```rust
let mut x = 5;
let r1 = &x;        // 不可變借用
let r2 = &x;        // 可以有多個不可變借用
// let r3 = &mut x; // 錯誤！不能同時有可變和不可變借用
```

**白話解釋：**
- Rust 的借用檢查器防止數據競爭
- 同一時間只能有一個可變借用，或多個不可變借用

##### 2.1.3 生命週期

**C++（常見錯誤）:**
```cpp
int* dangerous_function() {
    int local = 42;
    return &local;  // 錯誤！返回局部變量的引用
}
```

**Rust（編譯時防止）:**
```rust
fn dangerous_function() -> &i32 {
    let local = 42;
    &local  // 編譯錯誤！生命週期不匹配
}
```

**正確的生命週期:**
```rust
fn longest<'a>(s1: &'a str, s2: &'a str) -> &'a str {
    if s1.len() > s2.len() {
        s1
    } else {
        s2
    }
}
```

### 2.2 宏

**C++:**
```cpp
#define MAX(a, b) ((a) > (b) ? (a) : (b))  // 不安全
```

**Rust:**
```rust
macro_rules! max {
    ($a:expr, $b:expr) => {
        if $a > $b { $a } else { $b }
    };
}
```

**白話解釋：**
- C++ 的宏是簡單的文本替換
- Rust 的宏是語法感知的，更安全

### 2.3 智能指針

##### 2.3.1 什麼是智能指針

**白話解釋：**
- 普通指針：就像房子的鑰匙，但你得記住鎖門
- 智能指針：像自動鎖門的鑰匙，會幫你管理

##### 2.3.2 Box

**C++:**
```cpp
std::unique_ptr<int> ptr = std::make_unique<int>(42);
```

**Rust:**
```rust
let ptr = Box::new(42);
```

##### 2.3.3 Rc（Reference Counting）

**C++:**
```cpp
std::shared_ptr<int> ptr1 = std::make_shared<int>(42);
std::shared_ptr<int> ptr2 = ptr1;  // 引用計數 +1
```

**Rust:**
```rust
use std::rc::Rc;
let ptr1 = Rc::new(42);
let ptr2 = Rc::clone(&ptr1);  // 引用計數 +1
```

##### 2.3.4 RefCell

**白話解釋：**
- 允許在不可變借用中進行可變操作
- 在運行時檢查借用規則，而不是編譯時

```rust
use std::cell::RefCell;
let data = RefCell::new(42);
let mut_ref = data.borrow_mut();
*mut_ref = 100;
```

### 2.4 多線程

##### 2.4.1 什麼是多線程

**白話解釋：**
- 單線程：一個人做所有事情
- 多線程：多個人同時做不同事情

##### 2.4.2 創建線程

**C++:**
```cpp
#include <thread>
std::thread t([]() {
    std::cout << "Hello from thread" << std::endl;
});
t.join();
```

**Rust:**
```rust
use std::thread;
let handle = thread::spawn(|| {
    println!("Hello from thread");
});
handle.join().unwrap();
```

##### 2.4.3 線程間的數據共享

**C++（需要手動同步）:**
```cpp
#include <mutex>
std::mutex mtx;
int shared_data = 0;

void increment() {
    std::lock_guard<std::mutex> lock(mtx);
    shared_data++;
}
```

**Rust（編譯時保證安全）:**
```rust
use std::sync::{Arc, Mutex};
let shared_data = Arc::new(Mutex::new(0));
let data_clone = shared_data.clone();

thread::spawn(move || {
    let mut data = data_clone.lock().unwrap();
    *data += 1;
});
```

### 2.5 錯誤處理

##### 2.5.1 可恢復錯誤

**C++:**
```cpp
#include <optional>
std::optional<int> divide(int a, int b) {
    if (b == 0) {
        return std::nullopt;
    }
    return a / b;
}
```

**Rust:**
```rust
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err("Division by zero".to_string())
    } else {
        Ok(a / b)
    }
}

// 使用
match divide(10, 2) {
    Ok(result) => println!("Result: {}", result),
    Err(error) => println!("Error: {}", error),
}
```

##### 2.5.2 不可恢復錯誤

**C++:**
```cpp
#include <stdexcept>
throw std::runtime_error("Something went wrong");
```

**Rust:**
```rust
panic!("Something went wrong");
```

### 2.6 包和crate

**白話解釋：**
- **C++**: 使用 `#include` 和鏈接器
- **Rust**: 使用 `Cargo.toml` 管理依賴

**Cargo.toml:**
```toml
[package]
name = "my_project"
version = "0.1.0"

[dependencies]
serde = "1.0"
```

### 2.7 模塊

**C++:**
```cpp
// math.h
namespace math {
    int add(int a, int b);
}

// math.cpp
#include "math.h"
int math::add(int a, int b) {
    return a + b;
}
```

**Rust:**
```rust
// lib.rs
mod math {
    pub fn add(a: i32, b: i32) -> i32 {
        a + b
    }
}

// 使用
use math::add;
```

### 2.8 單元測試

**C++（需要外部框架）:**
```cpp
// 使用 Google Test
TEST(MathTest, Addition) {
    EXPECT_EQ(add(2, 3), 5);
}
```

**Rust（內建支援）:**
```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_addition() {
        assert_eq!(add(2, 3), 5);
    }
}
```

### 2.9 調試

**C++:**
```cpp
#include <iostream>
std::cout << "Debug: x = " << x << std::endl;
```

**Rust:**
```rust
println!("Debug: x = {:?}", x);
// 或者使用 debug 宏
dbg!(x);
```

---

---

## Rust 拿掉了 C++ 的什麼？為什麼？

### 1. 拿掉了手動記憶體管理

**C++ 的問題：**
```cpp
void memory_leak_example() {
    int* ptr = new int(42);
    // 忘記 delete ptr; 
    // 記憶體洩漏！
}

void dangling_pointer_example() {
    int* ptr;
    {
        int local = 42;
        ptr = &local;
    }
    // ptr 現在指向無效記憶體！
    cout << *ptr;  // 未定義行為
}
```

**Rust 的解決方案：**
```rust
fn safe_memory_example() {
    let data = Box::new(42);
    // 自動清理，不會洩漏
}

fn no_dangling_pointer() {
    let ptr;
    {
        let local = 42;
        // ptr = &local;  // 編譯錯誤！
    }
    // Rust 不允許懸空指標
}
```

**白話解釋：**
- **問題**：C++ 像是給你一把槍但沒有保險，你可能會意外射到自己
- **解決**：Rust 像是智能槍，有多重安全機制，防止意外傷害
- **好處**：99% 的記憶體相關 bug 在編譯時就被抓到了

### 2. 拿掉了 NULL 指標

**C++ 的問題：**
```cpp
int* ptr = nullptr;
*ptr = 42;  // 程式崩潰！
```

**Rust 的解決方案：**
```rust
let value: Option<i32> = None;
match value {
    Some(v) => println!("值是: {}", v),
    None => println!("沒有值"),
}
// 強制你處理"沒有值"的情況
```

**白話解釋：**
- **問題**：NULL 指標像是不存在的地址，去那裡會迷路
- **解決**：Rust 用 `Option<T>` 明確表示"可能沒有值"
- **好處**：編譯器強制你考慮所有情況，避免意外崩潰

### 3. 拿掉了資料競爭

**C++ 的問題：**
```cpp
int counter = 0;

void thread1() { counter++; }
void thread2() { counter++; }

// 兩個執行緒同時修改 counter，結果不可預測
```

**Rust 的解決方案：**
```rust
use std::sync::{Arc, Mutex};

let counter = Arc::new(Mutex::new(0));
let counter1 = counter.clone();
let counter2 = counter.clone();

thread::spawn(move || {
    let mut num = counter1.lock().unwrap();
    *num += 1;
});

thread::spawn(move || {
    let mut num = counter2.lock().unwrap();
    *num += 1;
});
```

**白話解釋：**
- **問題**：多執行緒像是多人同時編輯同一文件，會亂掉
- **解決**：Rust 強制使用鎖或其他同步機制
- **好處**：編譯時就防止資料競爭，不會有神秘的併發 bug

### 4. 拿掉了未初始化變數

**C++ 的問題：**
```cpp
int x;  // 未初始化
cout << x;  // 印出垃圾值
```

**Rust 的解決方案：**
```rust
let x: i32;  // 聲明但未初始化
// println!("{}", x);  // 編譯錯誤！
x = 42;  // 必須先初始化
println!("{}", x);  // 現在可以用了
```

**白話解釋：**
- **問題**：未初始化變數像是空的盒子，不知道裡面裝什麼
- **解決**：Rust 不允許使用未初始化的變數
- **好處**：避免讀取到隨機值導致的 bug

### 5. 拿掉了隱式類型轉換

**C++ 的問題：**
```cpp
int a = 10;
double b = 3.14;
int result = a + b;  // 隱式轉換，可能失去精度
```

**Rust 的解決方案：**
```rust
let a = 10i32;
let b = 3.14f64;
// let result = a + b;  // 編譯錯誤！
let result = a as f64 + b;  // 必須明確轉換
```

**白話解釋：**
- **問題**：隱式轉換像是自動翻譯，有時會翻錯意思
- **解決**：Rust 要求所有轉換都要明確
- **好處**：避免意外的精度丟失或類型錯誤

### 6. 拿掉了繼承

**C++ 的複雜繼承：**
```cpp
class A { public: virtual void foo() = 0; };
class B { public: virtual void bar() = 0; };
class C : public A, public B {  // 多重繼承
    // 複雜的菱形繼承問題...
};
```

**Rust 的組合方式：**
```rust
trait Foo {
    fn foo(&self);
}

trait Bar {
    fn bar(&self);
}

struct C;

impl Foo for C {
    fn foo(&self) { println!("foo"); }
}

impl Bar for C {
    fn bar(&self) { println!("bar"); }
}
```

**白話解釋：**
- **問題**：繼承像是複雜的家族關係，容易搞混
- **解決**：Rust 用組合和 trait，更清晰
- **好處**：避免繼承帶來的複雜性和菱形問題

---

## Rust 特有的功能

### 1. 所有權系統（Ownership）

**這是 Rust 最獨特的特性！**

```rust
fn take_ownership(s: String) {
    println!("{}", s);
}  // s 在這裡被丟棄

fn main() {
    let s = String::from("hello");
    take_ownership(s);
    // println!("{}", s);  // 編譯錯誤！s 已被移動
}
```

**白話解釋：**
- 就像實體物品，同一時間只能有一個人擁有
- 當你把東西給別人，你就不再擁有它了
- **好處**：自動記憶體管理，無需垃圾回收器

### 2. 借用檢查器（Borrow Checker）

```rust
fn main() {
    let mut s = String::from("hello");
    
    let r1 = &s;        // 不可變借用
    let r2 = &s;        // 可以有多個不可變借用
    // let r3 = &mut s; // 錯誤！不能同時有可變和不可變借用
    
    println!("{} and {}", r1, r2);
    // r1 和 r2 不再使用
    
    let r3 = &mut s;    // 現在可以可變借用了
    println!("{}", r3);
}
```

**白話解釋：**
- 就像圖書館借書規則：
  - 可以多人同時「讀」同一本書
  - 但如果有人要「寫筆記」，就只能一個人用
- **好處**：編譯時防止資料競爭

### 3. 模式匹配（Pattern Matching）

```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}

fn process_message(msg: Message) {
    match msg {
        Message::Quit => println!("退出"),
        Message::Move { x, y } => println!("移動到 ({}, {})", x, y),
        Message::Write(text) => println!("寫入: {}", text),
        Message::ChangeColor(r, g, b) => println!("顏色: ({}, {}, {})", r, g, b),
    }
}
```

**白話解釋：**
- 像是超強的 switch，可以拆解複雜的數據結構
- 編譯器確保你處理了所有可能的情況
- **好處**：安全、強大、表達力強

### 4. 零成本抽象（Zero-Cost Abstractions）

```rust
// 高階寫法
let numbers: Vec<i32> = vec![1, 2, 3, 4, 5];
let sum: i32 = numbers
    .iter()
    .filter(|&x| x % 2 == 0)
    .map(|&x| x * 2)
    .sum();

// 編譯後等同於手寫的迴圈，沒有額外開銷
```

**白話解釋：**
- 像是豪華汽車的自動檔，使用方便但不影響性能
- 高階抽象在編譯時被優化成低階代碼
- **好處**：寫得爽，跑得快

### 5. 強大的類型推斷

```rust
let numbers = vec![1, 2, 3];  // 編譯器知道這是 Vec<i32>
let result = numbers.iter().sum();  // 知道這是 i32

// 複雜的情況也能推斷
let data: HashMap<_, _> = vec![("a", 1), ("b", 2)].into_iter().collect();
```

**白話解釋：**
- 編譯器像是聰明的助手，能猜出你的意思
- 你不用寫一堆類型註釋
- **好處**：程式碼簡潔但類型安全

### 6. 宏系統（Macro System）

```rust
macro_rules! say_hello {
    () => {
        println!("Hello!");
    };
    ($name:expr) => {
        println!("Hello, {}!", $name);
    };
}

say_hello!();           // Hello!
say_hello!("Rust");     // Hello, Rust!
```

**白話解釋：**
- 像是程式碼的模板，可以生成重複的代碼
- 比 C++ 的 `#define` 更安全更強大
- **好處**：減少重複代碼，類型安全

---

## Rust 的整體好處

### 1. 記憶體安全 + 性能

**白話解釋：**
- 以前你只能選擇：要嘛安全但慢（如 Java），要嘛快但危險（如 C++）
- Rust 讓你兩個都要：既安全又快
- **比喻**：像是既安全又跑得快的賽車

### 2. 併發安全

**白話解釋：**
- 多執行緒程式設計不再是「祈禱不要出錯」
- 編譯器幫你檢查，確保執行緒安全
- **比喻**：像是有安全網的走鋼絲

### 3. 現代化的工具鏈

**Cargo（包管理器）：**
```bash
cargo new my_project    # 創建新專案
cargo build            # 編譯
cargo test             # 測試
cargo run              # 執行
```

**白話解釋：**
- 一個工具搞定所有事情
- 不像 C++ 需要學一堆不同的工具
- **比喻**：像是瑞士刀，功能齊全

### 4. 優秀的錯誤訊息

**Rust 的錯誤訊息：**
```
error[E0382]: borrow of moved value: `s`
  --> src/main.rs:5:20
   |
3  |     let s = String::from("hello");
   |         - move occurs because `s` has type `String`
4  |     take_ownership(s);
   |                    - value moved here
5  |     println!("{}", s);
   |                    ^ value borrowed here after move
   |
   = note: this error occurs because `String` does not implement the `Copy` trait
```

**白話解釋：**
- 不只告訴你錯了，還教你怎麼修
- 像是有耐心的老師，不只說「錯」，還解釋為什麼錯
- **好處**：學習過程更順暢

### 5. 向前相容性

**白話解釋：**
- Rust 承諾向前相容：今天能編譯的程式，未來也能編譯
- 不像某些語言會突然改變，讓舊程式無法編譯
- **好處**：投資在 Rust 上比較安全

### 6. 跨平臺

```rust
// 同樣的程式碼可以跨平臺編譯
cargo build --target x86_64-pc-windows-gnu     # Windows
cargo build --target x86_64-apple-darwin       # macOS  
cargo build --target x86_64-unknown-linux-gnu  # Linux
```

**白話解釋：**
- 一次寫，到處跑
- 不用為每個平臺重寫程式
- **好處**：省時省力

---

## 總結：為什麼選擇 Rust？

### 簡單來說：

1. **如果你想要 C++ 的速度，但不想被記憶體問題折磨** → 選 Rust
2. **如果你想寫併發程式，但不想半夜被叫起來修 bug** → 選 Rust  
3. **如果你想要現代化的開發體驗** → 選 Rust
4. **如果你的專案需要長期維護** → 選 Rust

### 用一句話總結：

**Rust 是「如果重新設計 C++，考慮到過去 30 年的經驗教訓」的結果。**

它拿掉了 C++ 中容易出錯的部分，加上了現代程式語言的優秀特性，同時保持了系統級程式語言的性能。

### 學習建議

1. **如果你熟悉 C++**：Rust 的概念不會太陌生，但需要適應所有權系統
2. **如果你是新手**：Rust 可能更適合作為第一門系統語言
3. **選擇依據**：
   - 需要最大效能和控制：C++
   - 需要安全和現代特性：Rust
   - 維護大型代碼庫：Rust
   - 與現有 C++ 代碼集成：C++