# Rust 記憶體配置指南：Stack vs Heap

在 Rust 中，變數的記憶體配置有其獨特的規則，主要由**所有權系統**和**型別特性**決定。

## Stack 上的變數

### 實作 Copy trait 的型別
```rust
fn main() {
    let x = 42;           // i32, stack 上
    let y = 3.14;         // f64, stack 上
    let flag = true;      // bool, stack 上
    let ch = 'A';         // char, stack 上
    let tuple = (1, 2);   // (i32, i32), stack 上
}
```

### 固定大小的陣列
```rust
fn main() {
    let arr = [1, 2, 3, 4, 5];  // [i32; 5], stack 上
    let bytes = [0u8; 1024];    // [u8; 1024], stack 上
}
```

## Heap 上的變數

### 使用 Box<T>
```rust
fn main() {
    let boxed = Box::new(42);        // Box<i32>, 值在 heap
    let large_array = Box::new([0; 1000000]);  // 大陣列在 heap
}
```

### Vec、String 等集合型別
```rust
fn main() {
    let mut vec = Vec::new();        // 資料在 heap
    vec.push(1);
    
    let s = String::from("hello");   // 字串資料在 heap
}
```

### 自定義結構體（預設在 stack）
```rust
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p1 = Point { x: 1, y: 2 };      // stack 上
    let p2 = Box::new(Point { x: 3, y: 4 }); // heap 上
}
```

## 判斷方法

### 1. 檢查型別特性
```rust
use std::mem;

fn main() {
    let x = 42;
    let s = String::from("hello");
    
    // 如果型別實作了 Copy，通常在 stack
    fn is_copy<T: Copy>() {}
    is_copy::<i32>();  // 編譯通過，i32 在 stack
    // is_copy::<String>();  // 編譯錯誤，String 不是 Copy
}
```

### 2. 觀察所有權轉移
```rust
fn main() {
    let x = 5;
    let y = x;  // Copy，x 仍可使用，說明在 stack
    println!("{}", x); // OK
    
    let s1 = String::from("hello");
    let s2 = s1;  // Move，s1 不可再使用，說明涉及 heap
    // println!("{}", s1); // 編譯錯誤
}
```

### 3. 使用記憶體分析工具
```rust
fn main() {
    let x = 42;
    let boxed = Box::new(42);
    
    println!("stack variable address: {:p}", &x);
    println!("box pointer address: {:p}", &boxed);
    println!("heap value address: {:p}", boxed.as_ref());
}
```

## 特殊情況

### 智慧指標
```rust
use std::rc::Rc;
use std::sync::Arc;

fn main() {
    let rc = Rc::new(42);     // 值在 heap，Rc 本身在 stack
    let arc = Arc::new(42);   // 值在 heap，Arc 本身在 stack
}
```

### 閉包捕獲
```rust
fn main() {
    let x = 42;  // stack
    
    let closure = move || {
        println!("{}", x);  // x 被移動到閉包中
    };
    // 閉包可能在 stack 或 heap，取決於使用方式
}
```

## 編譯器最佳化

Rust 編譯器會進行各種最佳化：

- **逃逸分析**：如果堆疊變數不會逃出函數範圍，可能保持在 stack
- **內聯展開**：小函數可能被內聯，影響變數位置
- **LLVM 最佳化**：後端最佳化可能重新安排記憶體配置

## 實用檢查方法

要準確瞭解變數位置，可以：

1. **查看型別是否實作 Copy trait**
2. **觀察所有權轉移行為**
3. **使用 `cargo expand` 查看巨集展開後的程式碼**
4. **使用記憶體分析工具**如 Valgrind 或 heaptrack

## 快速判斷表

| 型別類型 | 位置 | 範例 |
|---------|------|------|
| 基本型別 (i32, f64, bool, char) | Stack | `let x = 42;` |
| 固定陣列 | Stack | `let arr = [1, 2, 3];` |
| Box<T> | Heap (值) | `let boxed = Box::new(42);` |
| Vec<T> | Heap (資料) | `let vec = vec![1, 2, 3];` |
| String | Heap (資料) | `let s = String::from("hello");` |
| &str | Stack (指標) | `let s = "hello";` |
| 自定義 struct | Stack (預設) | `let p = Point { x: 1, y: 2 };` |

## 記憶要點

- **Copy trait**: 實作此 trait 的型別通常在 stack
- **所有權轉移**: 發生 move 的型別通常涉及 heap
- **明確配置**: 使用 `Box::new()` 強制放在 heap
- **編譯器智慧**: 最終位置可能因最佳化而改變