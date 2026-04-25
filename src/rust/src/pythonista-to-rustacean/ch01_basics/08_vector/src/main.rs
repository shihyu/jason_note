//! # Vector（動態陣列）
//!
//! ## 📖 概念說明
//!
//! Vector 是 Rust 中**動態大小**、**同質型別**的資料結構，類似 Python 的 `list`。
//!
//! ```text
//! ┌──────────────────────────────────────────────────────────────────────┐
//! │  Vec<T> vs Array[T; N]                                             │
//! ├──────────────────────────────────────────────────────────────────────┤
//! │                                                                      │
//! │  Vec<T> (動態大小)              Array[T; N] (固定大小)              │
//! │  ┌───┬───┬───┬                 ┌───┬───┬───┐                      │
//! │  │ 1 │ 2 │ 3 │ → 可 push()     │ 1 │ 2 │ 3 │                      │
//! │  └───┴───┴───┴                 └───┴───┴───┘                      │
//! │    heap（堆積）                    stack（棧）                        │
//! │    大小可變                        大小固定                          │
//! │                                                                      │
//! └──────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## 🔑 建立方式
//!
//! | 方式 | 語法 | 說明 |
//! |------|------|------|
//! | `Vec::new()` | `let v: Vec<i32> = Vec::new();` | 宣告型別後建立空 Vec |
//! | `vec![]` 巨集 | `let v = vec![1, 2, 3];` | 推導型別並初始化 |
//!
//! ## 📝 與 Python 的對比
//!
//! | Python | Rust |
//! |--------|------|
//! | `lst = []` | `let mut lst: Vec<i32> = Vec::new();` |
//! | `lst.append(1)` | `lst.push(1)` |
//! | `lst[2]` | `&lst[2]` 或 `lst.get(2)` |
//! | `lst[99]` (崩潰) | `lst.get(99)` → `None` |
//!
//! ## ⚡ Vec vs Array 選擇指南
//!
//! - **Vec**：大小需要動態增減時使用
//! - **Array**：大小固定且已知時使用（效能更好）

fn main() {
    let mut numbers: Vec<i32> = Vec::new(); // 必須宣告為 mut 才能修改
    numbers.push(1);
    numbers.push(2);
    numbers.push(3);

    // Rust 會自動推導型別為 Vec<i32>
    let numbers = vec![1, 2, 3];

    let v = vec![10, 20, 30, 40, 50];
    // 方法一：使用索引 [] ( 不推薦)
    // 如果索引越界 ( 例如 v[99])，程式會立刻 panic ( 崩潰)
    let third: &i32 = &v[2];
    println!("The third element is {}", third);
    // 方法二：使用 .get() ( 推薦)
    // .get() 不會 panic，而是回傳一個 Option 型別
    let third: Option<&i32> = v.get(2);
    match third {
        Some(value) => println!("The third element is {}", value),
        None => println!("There is no third element."),
    }
    // 嘗試存取不存在的索引
    let ninety_ninth: Option<&i32> = v.get(99); // 會回傳 None
    match ninety_ninth {
        Some(value) => println!("The 99th element is {}", value),
        None => println!("There is no 99th element."), // 程式會安全地印出這行
    }
}
