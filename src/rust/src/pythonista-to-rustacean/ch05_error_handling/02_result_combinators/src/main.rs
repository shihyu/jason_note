//! # `02_result_combinators` - Result combinators 與 unwrap/expect
//!
//! ## 概念說明
//!
//! `Result` 提供豐富的 **combinator 鏈**，
//! 讓你能用宣告式寫法處理錯誤，而不必每次都用 `match`。
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │  常見 Result / Option Combinators                                 │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                  │
//! │  .unwrap_or(default)  ──► 取值，失敗則用 default             │
//! │  .unwrap_or_else(fn)  ──► 取值，失敗則延遲執行 fn            │
//! │  .map(fn)            ──► 成功時轉換值                         │
//! │  .map_err(fn)        ──► 失敗時轉換錯誤                      │
//! │  .and_then(fn)       ──► 成功時執行 fn，回傳新的 Result      │
//! │                                                                  │
//! │  ┌──────────────────────────────────────────────┐              │
//! │  │  .unwrap_or_else 延遲執行範例             │              │
//! │  │                                              │              │
//! │  │  parse::<i32>().unwrap_or_else(|e| {    │              │
//! │  │      // 只在 Err 時才執行                   │              │
//! │  │      match e.kind() { ... }              │              │
//! │  │  })                                       │              │
//! │  └──────────────────────────────────────────────┘              │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python 對照表
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 取值/錯誤處理 | `value if cond else default` | `opt.unwrap_or(default)` |
//! | 延遲計算 fallback | `value if cond else expensive()` | `opt.unwrap_or_else(\|\| expensive())` |
//! | unwrap（危險） | 無直接對應 | `.unwrap()` 失敗則 panic |
//! | expect（推薦） | 無直接對應 | `.expect("msg")` 失敗顯示 msg 後 panic |
//! | map 錯誤 | `try/except` 中重新 raise | `.map_err(\|e\| new_error)` |
//!
//! ## 重點解析
//!
//! - `unwrap_or_else` vs `unwrap_or`：前者閉包**延遲執行**，適合昂貴計算
//! - `.expect()` 是 `.unwrap()` 的**加強版**，帶錯誤訊息
//! - Regex 的 `expect` 範例：hardcoded regex 錯誤代表**程式設計師 bug**，直接 panic
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
//! 輸入為空，使用預設值 0。
//! 最終數字為: 0
//! Regex compiled successfully: r"^\d{4}-\d{2}-\d{2}$"
//! ```

use std::num::IntErrorKind;

use regex::Regex;

fn main() {
    let input_str = "";
    let number = input_str.parse::<i32>().unwrap_or_else(|error| {
        // 這個閉包只會在 .parse() 回傳 Err 時執行
        // 'error' 參數就是 Err 裡面的 std::num::ParseIntError
        match error.kind() {
            IntErrorKind::Empty => {
                println!("輸入為空，使用預設值 0。");
                0 // 回傳這個 0 作為 'number' 變數的值
            }
            other_kind => {
                // 其他錯誤，依然 panic!
                panic!("因 {:?} 導致解析字串失敗", other_kind);
            }
        }
    });
    println!("最終數字為: {}", number);

    // 範例 1: 使用 unwrap ( 較不推薦)
    // 假設我們在測試一個固定會成功的函式
    fn get_hardcoded_answer() -> Result<i32, String> {
        Ok(42)
    }
    let answer = get_hardcoded_answer().unwrap(); // 快速取出 42

    // 範例 2: 使用 expect ( 強烈推薦)
    // 我們 100% 確定這個寫死的正則表達式是有效的
    // 如果它無效 ( 例如打錯字)，這代表程式設計師的錯誤，應立即 panic!
    let date_regex = Regex::new(r"^\d{4}-\d{2}-\d{2}$")
        .expect("Hardcoded regex pattern is guaranteed to be valid");
    println!("Regex compiled successfully: {:?}", date_regex);
}