//! # Constructor: Validation and Singleton Pattern
//!
//! 本範例展示 `#[new]` 建構子中的參數驗證與單例模式。
//!
//! ## ASCII 架構圖
//! ```text
//! #[new] 建構子流程
//! ┌─────────────────────────────────────────────────────────────┐
//! │  RedEnvelope.new(amount)                                   │
//! │       │                                                  │
//! │       ├─── amount == 0  ──→ Err(ValueError)             │
//! │       │                                                  │
//! │       ├─── amount == 888 ──→ Singleton (PyOnceLock)     │
//! │       │                       └─── return shared instance │
//! │       │                                                  │
//! │       └─── otherwise ──→ Py::new() ──→ New instance      │
//! └─────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 概念 | Python | Rust (PyO3) |
//! |------|--------|--------------|
//! | 建構驗證 | `if not valid: raise` | `if !valid { return Err(...) }` |
//! | 單例模式 | `cls._instance = x` | `PyOnceLock<Py<RedEnvelope>>` |
//! | 回傳指標 | N/A（總是實值）| `PyResult<Py<Self>>` |
//!
//! ## Rust 特有概念
//!
//! - `PyOnceLock<T>`: 執行緒安全的延遲初始化單例容器
//! - `Py::new(py, val)`: 在給定的 Python 執行緒中建立新 Python 物件
//! - `Py<Self>`: Rust 持有的 Python 物件指標（參數計數）

use pyo3::prelude::*;

#[pymodule]
mod constructor_example {
    use super::*;
    use pyo3::exceptions::PyValueError;
    use pyo3::sync::PyOnceLock;

    // `Clone` trait 是必要的，因為實例在首次被存入 PyOnceLock 時需要被複製。
    #[derive(Clone)]
    #[pyclass(get_all, set_all)]
    struct RedEnvelope {
        amount: u32,
    }

    // 使用 PyOnceLock 建立一個全域、需要時才初始化資料的容器，
    // 用於安全地存放我們想要共用的「幸運紅包」單一實例。
    static LUCKY_ENVELOPE: PyOnceLock<Py<RedEnvelope>> = PyOnceLock::new();

    #[pymethods]
    impl RedEnvelope {
        #[new]
        fn new(py: Python<'_>, amount: u32) -> PyResult<Py<Self>> {
            // 模式一：參數驗證。如果金額為 0，就回傳一個 Python 的 ValueError。
            if amount == 0 {
                return Err(PyValueError::new_err("紅包金額不得為零"));
            }

            // 模式二：單例模式。如果金額為 888，則回傳共用的實例。
            if amount == 888 {
                // 嘗試取得 PyOnceLock 中的實例，如果不存在（第一次呼叫），則執行閉包來建立並存入。
                let singleton = LUCKY_ENVELOPE
                    .get_or_try_init(py, || Py::new(py, RedEnvelope { amount: 888 }))?;
                // 回傳指標的複本 (clone_ref)，使其指向同一個 Python 物件。
                return Ok(singleton.clone_ref(py));
            }

            // 預設行為：為所有其他金額建立一個全新的實例。
            Py::new(py, RedEnvelope { amount })
        }
    }
}
