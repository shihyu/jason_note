//! # `01_match_result` - `match` 處理 `Result<T, E>`
//!
//! ## 概念說明
//!
//! `Result<T, E>` 是 Rust 用於**可恢復錯誤**（recoverable error）的型別。
//! - `Ok(T)`：成功，攜帶值
//! - `Err(E)`：失敗，攜帶錯誤資訊
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │  Result<T, E> 結構成員                                         │
//! │                                                               │
//! │   enum Result<T, E> {                                        │
//! │       Ok(T),     // 成功變體                                  │
//! │       Err(E),    // 失敗變體                                  │
//! │   }                                                         │
//! │                                                               │
//! │   "42".parse::<i32>()                                        │
//! │         │                                                    │
//! │         ▼                                                    │
//! │   Ok(42)  或  Err(ParseIntError { ... })                   │
//! │                                                               │
//! │   ┌─────────────────────────────────────────────┐           │
//! │   │  match number_result {                     │           │
//! │   │      Ok(num) => { ... },                  │           │
//! │   │      Err(e) => { panic!("...") }        │           │
//! │   │  }                                       │           │
//! │   └─────────────────────────────────────────────┘           │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python 對照表
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 錯誤表示 | 例外（Exception） | `Result<T, E>` (`Ok` / `Err`) |
//! | 錯誤處理 | `try/except` | `match` / `if let` |
//! | 不可恢復錯誤 | `raise Exception` | `panic!` |
//! | 類型化錯誤 | 自由（任何物件） | `Result<T, ConcreteError>` |
//!
//! ## 重點解析
//!
//! - `parse::<i32>()` 回傳 `Result<i32, ParseIntError>`
//! - `.kind()` 可進一步分析錯誤**種類**（如 `Empty`）
//! - `panic!` 適合不可恢復的錯誤；一般錯誤用 `Result` 傳播
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
//! 解析成功: 42
//! 結果是： 42
//! 輸入為空，使用預設值 0。
//! 最終數字為: 0
//! ```

use std::num::IntErrorKind;

fn main() {
    let input_str = "42";
    let number_result = input_str.parse::<i32>();

    let number = match number_result {
        Ok(num) => {
            println!("解析成功: {}", num);
            num // 回傳 num
        }
        Err(error) => {
            // error 變數的型別是 std::num::ParseIntError
            panic!("解析字串失敗: {:?}", error);
        }
    };

    println!("結果是： {}", number);

    // 假設這是一個可選的設定值，為空是可接受的
    let input_str = "";
    let number_result = input_str.parse::<i32>();
    let number = match number_result {
        Ok(num) => num, // 成功，直接回傳
        Err(error) => match error.kind() {
            // 失敗, 呼叫 .kind() 檢查錯誤種類
            IntErrorKind::Empty => {
                // 如果是「空字串」
                println!("輸入為空，使用預設值 0。");
                0 // 回傳預設值
            }
            other_kind => {
                // 其他所有錯誤 ( 例如：格式錯誤 "abc", 數字太大)
                panic!("因 {:?} 導致解析字串失敗", other_kind);
            }
        },
    };
    println!("最終數字為: {}", number);
}