//! # 生命週期與函式簽名 (Lifetimes in Function Signatures)
//!
//! 本範例展示 Rust 必須標注生命週期的時機——**當函式回傳參考時**。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 生命週期 | 無（GC 管理）| 編譯器靜態分析 |
//! | 回傳參考 | 幾乎不回傳純參考 | 必須標注 `'a` |
//! | 編譯錯誤 | 無（執行期錯誤）| 編譯期即可發現懸空參考 |
//!
//! ## 為何需要生命週期？
//!
//! ```text
//! Rust 需知道：回傳的 `&str` 到底借用自哪個輸入？
//!           這樣才能確保回傳值在呼叫者使用時仍有效。
//!
//! "The returned reference must not outlive the inputs."
//! ```
//!
//! ## 無法編譯的範例（被註解掉）
//!
//! ```ignore
//! fn longest_learning_note(attempt_one: &str, attempt_two: &str) -> &str {
//!     if attempt_one.len() > attempt_two.len() { attempt_one }
//!     else { attempt_two }
//! }
//! // 編譯錯誤：無法推斷回傳值生命週期
//! ```
//!
//! ## 正確寫法（需標注 `'a`）
//!
//! ```rust
//! fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
//!     if x.len() > y.len() { x } else { y }
//! }
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch07_lifetimes/01_function_signature
//! cargo build  # 觀察註解範例的編譯錯誤
//! ```

// 這無法編譯！
// fn longest_learning_note(attempt_one: &str, attempt_two: &str) -> &str {
//     if attempt_one.len() > attempt_two.len() {
//         attempt_one
//     } else {
//         attempt_two
//     }
// }

// fn invalid_return() -> &str {
// let my_excuse = String::from("我家的貓會後空翻");
// &my_excuse // 錯誤！
// }

fn main() {
    println!("Hello, world!");
}
