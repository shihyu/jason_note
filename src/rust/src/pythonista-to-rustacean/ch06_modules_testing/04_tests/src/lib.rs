//! # 單元測試 (Unit Tests)
//!
//! 本範例展示 Rust 內建的**單元測試框架**——在 `#[cfg(test)]` 模組中撰寫測試，使用 `#[test]` 屬性標記測試函式，遵循 AAA（Arrange-Act-Assert）模式。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python (`unittest`) | Rust |
//! |---|---|---|
//! | 測試框架 | `unittest.TestCase` | 內建測試屬性 |
//! | 測試標記 | `def test_xxx(self)` | `#[test]` |
//! | 測試模組 | 在類別內或单独檔案 | `#[cfg(test)] mod tests` |
//! | 斷言 | `self.assertEqual(a, b)` | `assert_eq!(a, b)` |
//! | 執行 | `python -m pytest` | `cargo test` |
//!
//! ## AAA 模式
//!
//! ```text
//! #[test]
//! fn test_feature() {
//!     // 1. Arrange — 準備測試資料
//!     let numbers = vec![1.0, 2.0, 3.0];
//!     // 2. Act — 執行要測試的函式
//!     let result = calculate_mean(&numbers);
//!     // 3. Assert — 驗證結果
//!     assert_eq!(result, 2.0);
//! }
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch06_modules_testing/04_tests
//! cargo test
//! ```
//!
//! ## 預期輸出
//!
//! ```text
//! running 2 tests
//! test data_prep::tests::test_calculate_mean_basic ... ok
//! test data_prep::tests::test_calculate_mean_empty ... ok
//! ```

// 宣告 `data_prep` 模組，編譯器會尋找 `src/data_prep.rs`
mod data_prep;
