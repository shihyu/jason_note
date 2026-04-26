//! # `#[should_panic]` 測試 panic 行為
//!
//! 本範例展示如何使用 `#[should_panic]` 屬性測試**預期會 panic 的情境**——當輸入無效時，函式應該崩潰。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python (`pytest`) | Rust |
//! |---|---|---|
//! | 例外測試 | `with pytest.raises(Exception)` | `#[test] #[should_panic]` |
//! | panic 情境 | `raise ValueError("msg")` | `panic!("{}", msg)` |
//! | 錯誤訊息驗證 | `pytest.raises(E, match="pattern")` | `#[should_panic(expected = "pattern")]` |
//!
//! ## 測試策略
//!
//! ```text
//! 1. 預期 panic（panic 發生 → 測試通過）
//!    #[test]
//!    #[should_panic]
//!    fn test_divide_by_zero_panics() { divide_by(0); }
//!
//! 2. 預期特定訊息（panic 發生且訊息匹配 → 測試通過）
//!    #[test]
//!    #[should_panic(expected = "divide by zero")]
//!    fn test_divide_by_zero_panics_with_message() { divide_by(0); }
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch06_modules_testing/05_should_panic
//! cargo test
//! ```
//!
//! ## 預期輸出
//!
//! ```text
//! running 2 tests
//! test tests::test_divide_by_zero_panics ... ok
//! test tests::test_divide_by_zero_panics_with_message ... ok
//! ```

// 假設我們有一個函式，在輸入 0 時會 panic
fn divide_by(val: i32) {
    if val == 0 {
        panic!("Cannot divide by zero!");
    }
    // ...
}

fn main() {
    println!("Hello, world!");
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    #[should_panic]
    fn test_divide_by_zero_panics() {
        divide_by(0);
    }

    #[test]
    #[should_panic(expected = "divide by zero")]
    fn test_divide_by_zero_panics_with_message() {
        divide_by(0);
    }
}
