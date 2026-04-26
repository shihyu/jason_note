//! # `02_iterator` - 迭代器基礎
//!
//! ## 概念說明
//!
//! Rust 的迭代器是一種**惰性（lazy）**的資料處理工具：
//! 直到呼叫 `.collect()` 或其他消費 adaptor 之前，什麼都不會發生。
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────┐
//! │  vec![1, 2, 3, 4, 5]                                   │
//! │       │                                                │
//! │       ▼                                                │
//! │  .iter()  ──► Iterator<Item = &i32>  (還不做事)      │
//! │       │                                                │
//! │       ▼                                                │
//! │  .map(|x| x + 1)  ──► Map<I, Closure>  (還不做事)     │
//! │       │                                                │
//! │       ▼                                                │
//! │  .collect()  ──► Vec<i32>  (此時才真正開始迭代)       │
//! └─────────────────────────────────────────────────────────┘
//!
//! ┌────────────────────────────────────────┐
//! │         兩種遍歷方式對比                  │
//! ├────────────────────────────────────────┤
//! │  手動 for 迴圈：                       │
//! │  for num in &numbers {                 │
//! │      plus_one.push(num + 1);           │
//! │  }                                    │
//! │  • 需要手動建立目標容器                  │
//! │  • 需要手動 push                       │
//! │                                        │
//! │  迭代器鏈（宣告式）：                    │
//! │  let plus_one: Vec<_> =               │
//! │      numbers.iter()                    │
//! │          .map(|num| num + 1)          │
//! │          .collect();                   │
//! │  • 一行表達「轉換」意圖                 │
//! │  • 編譯器可極致優化                    │
//! └────────────────────────────────────────┘
//! ```
//!
//! ## Python 對照表
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 可迭代物件 | `list`, `tuple`, `range` | `Vec<T>`, `HashMap`, `Range` 等 |
//! | 迭代器建立 | `iter(obj)` | `obj.iter()`, `obj.into_iter()`, `obj.iter_mut()` |
//! | 惰性 map | `map(func, iterable)` (lazy in Python 3) | `.map(\|x\| ...)` (always lazy) |
//! | 收集結果 | `list(map(...))` | `.collect()` |
//! | 遍歷時保留原資料 | 直接用 `for x in list:` | `for x in &list:` 借用手動存取 |
//!
//! ## 重點解析
//!
//! - `.iter()` 產生**不可變參考**的迭代器，原容器仍可使用
//! - `.map()` 是**惰性**的——只改變迭代器型別，不執行任何運算
//! - `.collect()` 是**消費 adaptor**，會實際遍歷並產生結果
//!
//! ## 執行方式
//!
//! ```bash
//! cargo run
//! ```
//!
//! ## 預期輸出
//!
//! ```text
//! [1, 2, 3, 4, 5]
//! [1, 2, 3, 4, 5]
//! ```

fn main() {
    let numbers = vec![1, 2, 3, 4, 5];
    let mut plus_one = vec![];

    // 透過 `&numbers` 取得不可變參考來遍歷
    for num in &numbers {
        plus_one.push(num + 1);
    }

    // `numbers` 仍然可用
    println!("{:?}", numbers); // [1, 2, 3, 4, 5]

    let numbers = vec![1, 2, 3, 4, 5];
    let plus_one: Vec<_> = numbers.iter().map(|num| num + 1).collect();
    // `numbers` 仍然可用
    println!("{:?}", numbers); // [1, 2, 3, 4, 5]
}