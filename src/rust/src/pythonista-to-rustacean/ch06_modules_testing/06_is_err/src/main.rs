//! # `Result` 測試：`is_err()` 與 `unwrap()`
//!
//! 本範例展示如何測試回傳 `Result` 的函式——用 `is_err()` 驗證失敗路徑，用 `.unwrap()` 驗證成功路徑（失敗時自動 panic → 測試失敗）。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 錯誤處理 | `try/except` | `Result<T, E>` + `match` |
//! | 成功判斷 | 無錯誤拋出 | `.is_ok()` / `.is_err()` |
//! | 取值 | `value`（在 `except` 外）| `.unwrap()` / `.unwrap_err()` |
//! | 鏈式組合 | 手動處理 | `.map()` / `.and_then()` |
//!
//! ## 測試策略
//!
//! ```text
//! 成功路徑：.unwrap() 成功 → 測試繼續
//!           .unwrap() 失敗 → panic → 測試失敗
//!
//! 失敗路徑：.is_err() 為 true → 測試通過
//!            .is_err() 為 false → 測試失敗
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch06_modules_testing/06_is_err
//! cargo test
//! ```
//!
//! ## 預期輸出
//!
//! ```text
//! running 2 tests
//! test tests::test_parse_success ... ok
//! test tests::test_parse_failure ... ok
//! ```

// 假設我們有一個函式，回傳 Result
fn try_parse(input: &str) -> Result<i32, String> {
    println!("Try parsing...");
    input.parse::<i32>().map_err(|e| e.to_string())
}

fn main() {
    println!("Hello, world!");
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_parse_success() {
        // 1. 預期 Ok
        // 如果 try_parse 回傳 Err，.unwrap() 會 panic，測試失敗
        let value = try_parse("123").unwrap();
        assert_eq!(value, 123);
    }
    #[test]
    fn test_parse_failure() {
        // 2. 預期 Err
        // 我們改為檢查 .is_err() 是否為 true
        let result = try_parse("not-a-number");
        assert!(result.is_err());
        // 我們也可以進一步檢查錯誤的內容
        // assert_eq!(result.unwrap_err(), "...");
    }
}
