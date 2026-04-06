---
title: Rust
tags: [rust, systems, memory-safety]
sources: []
created: 2026-04-07
updated: 2026-04-07
---

# Rust

## 語言定位

> Rust 是一種追求記憶體安全、併發安全、效能的系統程式語言。

## 核心特性

- **所有權系統**：編譯時記憶體安全，無 GC
- **zero-cost abstractions**：抽象不帶來執行期成本
- **fearless concurrency**：編譯時防止資料競爭
- **pattern matching**：強大的型別匹配
- **ownership + borrowing**：取代 GC 的安全記憶體模型

## 語法速查

```rust
// 變數綁定
let x = 5;
let mut y = 10;

// 函式
fn add(a: i32, b: i32) -> i32 {
    a + b
}

// 結構體
struct Point {
    x: f64,
    y: f64,
}

// 枚舉 + Match
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

fn move(dir: Direction) {
    match dir {
        Direction::Up => println!("up"),
        Direction::Down => println!("down"),
        _ => println!("other"),
    }
}

// Result 錯誤處理
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err("cannot divide by zero".to_string())
    } else {
        Ok(a / b)
    }
}

// Option
fn find(haystack: &str, needle: char) -> Option<usize> {
    haystack.find(needle)
}
```

## 併發模型

- `std::thread` - 原生執行緒
- `Arc<Mutex<T>>` - 共享記憶體
- `mpsc` - 訊息傳遞
- `Send + Sync` - trait 標記執行緒安全

## Rust 生態

| 領域 | 常用 crate |
|------|-----------|
| Web 框架 | Axum, Actix-web |
| 非同步 | Tokio, async-std |
| 嵌入式 | embedded-hal |
| 機器學習 | candle, tch-rs |

## 相關概念

- [[concepts/記憶體管理]]
- [[concepts/併發模型]]
- [[concepts/錯誤處理]]

## 相關專案

- [[projects/gpio-driver|GPIO Driver]] - 可能使用 Rust 嵌入式

## 外部資源

- [Rust Book](https://doc.rust-lang.org/book/)
- [Rust By Example](https://doc.rust-lang.org/rust-by-example/)
