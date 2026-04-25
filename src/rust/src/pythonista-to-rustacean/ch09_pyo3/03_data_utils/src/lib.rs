//! # Data Utils: Module Export and Re-export
//!
//! 本範例展示 PyO3 中 `#[pymodule_export]` 與巢狀模組的用法。
//!
//! ## ASCII 架構圖
//! ```text
//! data_utils (Rust)              Python 視角
//! ┌─────────────────────────┐  ┌──────────────────────────────┐
//! │ #[pymodule]            │  │ from data_utils import (     │
//! │ mod data_utils {       │  │     normalize_vector,      │
//! │   #[pymodule_export]   │  │     calculate_mean,         │
//! │   use super::norm...    │──│     DataPoint,              │
//! │   #[pyfunction]        │  │     stats.calculate_variance │
//! │   fn calculate_mean   │  │ )                           │
//! │   #[pyclass]          │  └──────────────────────────────┘
//! │   struct DataPoint    │
//! │   #[pymodule]        │
//! │   mod stats { ... }  │
//! └─────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 概念 | Python | Rust (PyO3) |
//! |------|--------|--------------|
//! | 重新導出 | `from parent import child` | `#[pymodule_export] use super::func` |
//! | 類別定義 | `class DataPoint:` | `#[pyclass] struct DataPoint` |
//! | 子模組 | `import pkg.stats` | `#[pymodule] mod stats` |
//!
//! ## Rust 特有概念
//!
//! - `#[pymodule_export]`: 將外部（父層）定義的函式/類別納入此模組
//! - `#[pyclass]`: 將 Rust struct 標記為 Python 類別
//! - `#[pyo3(get)]`: 自動產生 Python 屬性 getter

use pyo3::prelude::*;

// 這是一個在模組外部定義的輔助函式
#[pyfunction]
fn normalize_vector(v: Vec<f64>) -> Vec<f64> {
    let sum: f64 = v.iter().sum();
    if sum == 0.0 {
        return v;
    }
    v.into_iter().map(|x| x / sum).collect()
}

#[pymodule]
mod data_utils {
    use super::*;

    // 透過 #[pymodule_export] 將外部函式匯入，成為模組的一部分
    #[pymodule_export]
    use super::normalize_vector;

    // 直接在模組內定義的 #[pyfunction] 會自動被加入
    #[pyfunction]
    fn calculate_mean(data: Vec<f64>) -> f64 {
        let sum: f64 = data.iter().sum();
        sum / data.len() as f64
    }

    // 在模組內定義的 #[pyclass] 也會自動被加入
    #[pyclass]
    struct DataPoint {
        #[pyo3(get)]
        id: String,
        #[pyo3(get)]
        value: f64,
    }

    // 巢狀的子模組也同樣適用
    #[pymodule]
    mod stats {
        use super::*;
        #[pyfunction]
        fn calculate_variance(data: Vec<f64>) -> f64 {
            let mean = calculate_mean(data.clone()); // 借用父模組的函式
            let n = data.len() as f64;
            data.iter().map(|val| (val - mean).powi(2)).sum::<f64>() / n
        }
    }
}
