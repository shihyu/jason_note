//! # PyClass: Rust Struct → Python Class
//!
//! 本範例展示用 `#[pyclass]` 將 Rust struct 對應為 Python 類別。
//!
//! ## ASCII 架構圖
//! ```text
//! Rust: #[pyclass] struct RedEnvelope
//! ┌──────────────────────────────────────────────────────────┐
//! │  #[pyclass]                    Python: RedEnvelope     │
//! │  struct RedEnvelope {          ─────────────────────    │
//! │      amount: u32,              class RedEnvelope:        │
//! │  }                            │   def __init__(amount)  │
//! │       │                       └────────────────────────┘
//! │       └── PyO3 自動 registration
//! └──────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 概念 | Python | Rust (PyO3) |
//! |------|--------|--------------|
//! | 類別定義 | `class MyClass:` | `#[pyclass] struct MyClass` |
//! | 實例屬性 | `self.amount = v` | `amount: u32` (欄位) |
//! | 建構子 | `def __init__(self, v):` | `#[new]` 或預設初始化 |
//!
//! ## Rust 特有概念
//!
//! - `#[pyclass]`: 將 Rust struct 標記為 Python 類別（PyO3 會自動處理 registration）

use pyo3::prelude::*;

#[pymodule]
mod classes_example {
    use super::*;

    // 不需要任何手動註冊程式碼，
    // PyO3 會自動找到並註冊這個 RedEnvelope 類別。
    #[pyclass]
    struct RedEnvelope {
        amount: u32,
    }
}
