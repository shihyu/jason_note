//! # Borrow of Borrowed：借用的生命週期
//!
//! 本範例展示當**參考存在時，無法進行可變借用**的規則——
//! 這是 Rust 借用規則的核心：**有_reader 就不能有_writer**。
//!
//! ## 借用的排他性
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │              借用的排他性                                        │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                 │
//! │   let mut counter = Counter { value: 0 };                       │
//! │                                                                 │
//! │   // 第一步：建立不可變借用                                      │
//! │   let first_report = counter.report();                          │
//! │   //              ────────────────────────                       │
//! │   //              first_report 是 &i32，&counter 的生命週期     │
//! │   //              會持續到 first_report 最後一次被使用           │
//! │                                                                 │
//! │   // 第二步：想修改，但有借用存在！                             │
//! │   counter.increment();  // ❌ 編譯錯誤！counter 正在被借用       │
//! │                                                                 │
//! │   // 第三步：使用列印後，借用結束                               │
//! │   println!("{}", first_report);                                 │
//! │   // ────────────────────────────────────────                  │
//! │   // first_report 最後一次使用，借用在此結束                      │
//! │                                                                 │
//! │   // 第四步：現在可以修改了                                    │
//! │   counter.increment();  // ✅                                    │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## 解決方案：不要長期持有借用
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │              正確做法：不要長期持有                              │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                 │
//! │   println!("{}", counter.report());  // 直接使用，不持有         │
//! │   // ────────────────────────────────                             │
//! │   // counter.report() 的借用只在這一行內有效                    │
//! │   // 離開這一行後，借用立即結束                                 │
//! │                                                                 │
//! │   counter.increment();  // ✅ 沒有借用，可以修改                 │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust：同時讀寫
//!
//! | 情境 | Python | Rust |
//! |------|---------|------|
//! | 同時讀取 | `r1 = obj.method(); r2 = obj.method()` | `let r1 = &obj; let r2 = &obj;` |
//! | 有讀取時修改 | `def modifier(): obj.x += 1`（可）| `obj.method(); obj.mutate()`（❌）|
//! | 解決方案 | 不需要 | 不要長期持有借用 |
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch03_ownership/08_cannot_borrow_as_mutable
//! cargo run
//! ```

struct Counter {
    value: i32,
}
impl Counter {
    // 回傳一個參考，讓回傳值持續借用 self
    fn report(&self) -> &i32 {
        &self.value
    }
    // 一個可變的方法，用來修改計數
    fn increment(&mut self) {
        self.value += 1;
    }
}
fn main() {
    /// Bad
    let mut counter = Counter { value: 0 };
    // 我們先讀取一次計數，first_report 現在是一個 &i32 參考
    // counter 上的不可變借用會持續到 first_report 被最後一次使用
    let first_report = counter.report();
    // 接著，我們想修改計數器
    // counter.increment(); // 💥 錯誤！
    // first_report 在這裡被使用，所以不可變借用必須持續到此行
    println!("第一次的報告值：{}", first_report);

    /// Fixed
    let mut counter = Counter { value: 0 };
    // 我們先讀取一次，但這次不把參考存起來
    // 而是直接在 println! 中使用它
    println!("第一次的報告值：{}", counter.report());
    // counter.report() 建立的不可變借用，其生命週期只在這一行內，用完即逝
    // 現在 counter 沒有任何借用，可以安全地進行可變操作
    counter.increment(); // OK!
    println!("遞增後的值：{}", counter.report());
}