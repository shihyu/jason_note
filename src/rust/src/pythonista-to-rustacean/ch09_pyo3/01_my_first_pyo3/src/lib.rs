//! # Python-Rust FFI: Your First Extension Module
//!
//! 本範例展示用 PyO3 建立最基礎的 Python 原生擴充模組。
//!
//! ## ASCII 架構圖
//! ```text
//! ┌─────────────────────────────────────────────────────────────┐
//! │                        Python Runtime                        │
//! │  ┌─────────────────┐    import my_first_pyo3                │
//! │  │  Python Code    │──────────→  sum_as_string(a, b)       │
//! │  └─────────────────┘              │                          │
//! │                                  ↓                          │
//! │                     ┌─────────────────────┐                 │
//! │                     │  PyO3 FFI Bridge    │                 │
//! │                     │  (lib.rs)           │                 │
//! │                     └─────────────────────┘                 │
//! │                                  │                          │
//! │                                  ↓                          │
//! │                     ┌─────────────────────┐                 │
//! │                     │  Rust Native Code   │                 │
//! │                     │  fn sum_as_string   │                 │
//! │                     └─────────────────────┘                 │
//! └─────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 概念 | Python | Rust (PyO3) |
//! |------|--------|--------------|
//! | 模組定義 | `def my_module` | `#[pymodule] fn my_module` |
//! | 導出函式 | `def func(): ...` | `#[pyfunction] fn func()` |
//! | 錯誤處理 | `raise TypeError` | `PyResult<T>` + `?` |
//! | 物件存取 | 直接使用 | `Bound<'_, PyModule>` |
//!
//! ## Rust 特有概念
//!
//! - `#[pymodule]`: 將 Rust 函式標記為 Python 模組入口
//! - `#[pyfunction]`: 將 Rust 函式標記為可從 Python 呼叫
//! - `PyResult<T>`: 可能失敗的操作，回傳 `PyResult<T>` 而非 `Result<T, Err>`
//! - `Bound<'_, PyModule>`: PyO3 0.23+ 的所有權安全 API
//!
//! ## 建置方式
//! ```bash
//! # 開發模式（連結到 current Python 環境）
//! pip install maturin && maturin develop
//!
//! # 或發布模式
//! maturin build --release
//! ```

use pyo3::prelude::*;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// 一個用 Rust 實作的 Python 模組。
/// 這段文件註解，會自動變成 Python 模組的 docstring。
#[pymodule]
fn my_first_pyo3(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}
