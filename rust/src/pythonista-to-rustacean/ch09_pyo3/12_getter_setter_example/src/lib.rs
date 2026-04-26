//! # Getter and Setter: Property Control
//!
//! 本範例展示 PyO3 中自訂 getter/setter 的各種方式。
//!
//! ## ASCII 架構圖
//! ```text
//! 屬性存取控制
//! ┌─────────────────────────────────────────────────────────────┐
//! │  #[pyo3(get)]              → Python: obj.amount (唯讀)     │
//! │  fn set_amount(&mut self)  → Python: obj.amount = v (寫入) │
//! │                                                    │
//! │  #[setter(bling_bling)]                                 │
//! │      └── 自訂 setter 名稱：obj.bling_bling = v           │
//! └─────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 概念 | Python | Rust (PyO3) |
//! |------|--------|--------------|
//! | 唯讀屬性 | `@property` | `#[pyo3(get)]` |
//! | 讀寫屬性 | `@name.setter` | `#[pyo3(get, set)]` |
//! | 自訂 setter | `def name_setter(self, v):` | `#[setter]` + 驗證邏輯 |
//!
//! ## Rust 特有概念
//!
//! - `#[setter]`: 標記自訂 setter 函式
//! - `#[setter(name)]`: 給 setter 命名（可用不同於欄位的名稱）
//! - 驗證模式：setter 中呼叫 `Self::check()?` 確保資料完整性

use pyo3::prelude::*;

#[pymodule]
mod getter_setter_example {
    use super::*;
    use pyo3::exceptions::PyValueError;

    #[pyclass]
    struct RedEnvelope {
        // 我們繼續使用預設的 getter，沒問題
        #[pyo3(get)]
        amount: u32,
    }

    const MIN_LUCKY_MONEY: u32 = 1; // 紅包最少要 1 塊錢才有意思

    #[pymethods]
    impl RedEnvelope {
        #[new]
        fn new(amount: u32) -> PyResult<Self> {
            Self::check_amount(amount)?;
            Ok(Self { amount })
        }

        // 為 amount 欄位手動定義一個 setter 函式
        #[setter]
        fn set_amount(&mut self, value: u32) -> PyResult<()> {
            Self::check_amount(value)?; // 在實際寫入前，先呼叫檢查邏輯
            self.amount = value;
            Ok(())
        }

        #[setter(bling_bling)]
        fn update_value(&mut self, amount: u32) -> PyResult<()> {
            Self::check_amount(amount)?;
            self.amount = amount;
            Ok(())
        }
    }

    // 為了讓 pymethods 區塊保持乾淨，
    // 我們可以把這個純 Rust 內部的輔助函式放在另一個 impl 區塊
    impl RedEnvelope {
        fn check_amount(amount: u32) -> PyResult<()> {
            if amount <= MIN_LUCKY_MONEY {
                Err(PyValueError::new_err(
                    "紅包金額不能少於 1 塊錢，不要跟我說什麼一元復始！",
                ))
            } else {
                Ok(())
            }
        }
    }
}
