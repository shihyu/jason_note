//! # 綜合生命週期：泛型 + 生命週期 + Trait Bound
//!
//! 本範例展示生命週期與泛型參數**可以同時存在**——`<>'a, T>` 宣告多個參數，T 可綁定 Trait。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 多參數泛型 | `def foo(x, y): ...` | `<'a, T>` 多參數並存 |
//! | 泛型約束 | `isinstance(x, int)` | `T: Display` Trait Bound |
//! | 生命週期標注 | 無 | `'a` 顯式標注 |
//!
//! ## 語法結構
//!
//! ```text
//! fn longest_note_with_purchase_count<'a, T>(
//!     note1: &'a str,        ← 生命週期：輸入參考
//!     note2: &'a str,        ← 生命週期：輸入參考（同一個 'a）
//!     total_courses: T,       ← 泛型：任意實作了 Display 的型別
//! ) -> &'a str             ← 回傳值生命週期
//! where
//!     T: Display,          ← Trait Bound：可被 println! 格式化
//! ```
//!
//! ## 為何 `where T: Display`？
//!
//! ```text
//! 因為我們用 `println!("{}", total_courses)` 格式化它。
//! 若 T 沒有實作 Display，編譯器會在這裡阻止我。
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch07_lifetimes/03_put_everything_together
//! cargo run
//! ```

use std::fmt::Display;
// 綜合：比較筆記並顯示購買的第幾個課程
fn longest_note_with_purchase_count<'a, T>(
    note1: &'a str,
    note2: &'a str,
    total_courses: T, // 購物車裡的課程數量
) -> &'a str
where
    T: Display, // T 必須實作 Display Trait
{
    println!("已購買但未完成的課程數：{}", total_courses);
    if note1.len() > note2.len() {
        note1
    } else {
        note2
    }
}

fn main() {
    println!("Hello, world!");
}
