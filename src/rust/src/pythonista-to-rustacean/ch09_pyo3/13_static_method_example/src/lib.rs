//! # Static Method and Class Method
//!
//! 本範例展示 `#[staticmethod]` 與 `#[classmethod]` 的用法。
//!
//! ## ASCII 架構圖
//! ```text
//! 靜態方法 vs 類別方法
//! ┌─────────────────────────────────────────────────────────────┐
//! │  #[staticmethod]              │  #[classmethod]            │
//! │  fn super_lucky()            │  fn from_blessing(cls, ..) │
//! │      └── Python:             │      └── Python:           │
//! │         RedEnvelope.super_lucky()  RedEnvelope.from_blessing("發發發") │
//! │      不綁定任何實例         │  cls = 動態類別參照       │
//! └─────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 概念 | Python | Rust (PyO3) |
//! |------|--------|--------------|
//! | 靜態方法 | `@staticmethod` | `#[staticmethod]` |
//! | 類別方法 | `@classmethod` | `#[classmethod]` |
//! | cls 參數 | `cls` (隱式) | `cls: &Bound<'_, PyType>` (顯式) |
//!
//! ## Rust 特有概念
//!
//! - `#[staticmethod]`: 對應 Python 的 `@staticmethod`
//! - `#[classmethod]`: 對應 Python 的 `@classmethod`，`cls` 為 `&Bound<'_, PyType>`
//! - `cls.call1((args,))?`: 在 Rust 中呼叫 Python 類別建構

use pyo3::prelude::*;

#[pymodule]
mod static_method_example {
    use super::*;
    use pyo3::exceptions::PyValueError;
    use pyo3::types::PyType;

    // 為了讓接下來的「繼承」範例能順利運作，
    // 我們得在定義上做點微調，加上 `subclass` 和 `Clone`。
    // 關於它們的詳細設定未來會深入說明，這裡先有個印象即可。
    #[pyclass(subclass)]
    #[derive(Clone)]
    struct RedEnvelope {
        #[pyo3(get)]
        amount: u32,
    }

    #[pymethods]
    impl RedEnvelope {
        #[new]
        fn new(amount: u32) -> Self {
            Self { amount }
        }

        // 這個 #[staticmethod] 標籤，
        // 會讓 PyO3 在 Python 端把它轉換成 @staticmethod
        #[staticmethod]
        fn super_lucky() -> Self {
            // 這個函式不接收 self，代表它與任何特定的紅包物件無關
            Self { amount: 888 } // 敬祝各位讀者發大財
        }

        #[classmethod]
        fn from_blessing(cls: &Bound<'_, PyType>, blessing: &str) -> PyResult<Self> {
            let amount = match blessing {
                "發發發" => 888,
                "一路發" => 168,
                "我愛你" => 520,
                "六六大順" => 666,
                _ => return Err(PyValueError::new_err("聽不懂你的吉祥話！")),
            };

            // `cls` 參數會動態地代表呼叫此方法的 Python 類別。
            // `cls.call1` 會呼叫 Python 端的建構流程 (等同於 `cls(amount)`)
            // 接著 `.extract()` 會從那個 Python 物件中，提取出我們 Rust 函式簽名裡要求的 `Self`
            cls.call1((amount,))?.extract()
        }
    }
}
