//! # 資料預處理測試 (Data Prep Unit Tests)
//!
//! 本範例展示 Rust **內聯測試**的完整寫法——測試與實作放在同一個 `.rs` 檔案中，編譯器自動只在使用 `cargo test` 時編譯測試碼。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python (`pytest`) | Rust |
//! |---|---|---|
//! | 測試位置 | 單獨 `test_*.py` 或 `tests/` | 同檔案 `#[cfg(test)]` |
//! | 私有函式測試 | 需透過公共 API 間接測試 | 可直接測試私有函式（同一模組）|
//! | 測試隔離 | `pytest` 自動隔離 | `#[cfg(test)]` 編譯時排除 |
//! | 邊界測試 | 手動寫多個 `test_` 函式 | 每個 `#[test]` 函式獨立 |
//!
//! ## 測試覆蓋：正常 + 邊界
//!
//! ```text
//! test_calculate_mean_basic   → 一般 vec![1,2,3,4,5], 平均 3.0
//! test_calculate_mean_empty   → 空 vec![], 預期 0.0
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
//!
//! test result: ok. 2 passed; 0 failed
//! ```

fn calculate_mean(data: &Vec<f64>) -> f64 {
    if data.is_empty() {
        return 0.0;
    }
    data.iter().sum::<f64>() / (data.len() as f64)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_calculate_mean_basic() {
        // 1. 準備 (Arrange)
        let numbers = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        // 2. 執行 (Act)
        let result = calculate_mean(&numbers);
        // 3. 驗證 (Assert)
        assert_eq!(result, 3.0);
    }

    #[test]
    fn test_calculate_mean_empty() {
        // 1. 準備
        let empty_vec = vec![];
        // 2. 執行
        let result = calculate_mean(&empty_vec);
        // 3. 驗證
        assert_eq!(result, 0.0);
    }
}
