//! # PyClass Methods: Instance Methods
//!
//! 本範例展示 `#[pymethods]` 區塊中實作 Python 實例方法。
//!
//! ## ASCII 架構圖
//! ```text
//! #[pymethods] impl RedEnvelope
//! ┌──────────────────────────────────────────────────────────┐
//! │  #[new]              → Python: RedEnvelope(amount)     │
//! │  fn new(amount) -> Self                              │
//! │                                                    │
//! │  fn add_money(&mut self, money)                   │
//! │      └── Python: obj.add_money(100)                │
//! │                                                    │
//! │  fn take_money(&mut self, money) -> PyResult<()>  │
//! │      └── Python: obj.take_money(50)               │
//! └──────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 概念 | Python | Rust (PyO3) |
//! |------|--------|--------------|
//! | 建構子 | `def __init__(self, v):` | `#[new] fn new(v) -> Self` |
//! | 實例方法 | `def add(self, v):` | `fn add(&mut self, v)` |
//! | 屬性讀取 | `self.amount` | `#[pyo3(get)]` |
//! | 屬性寫入 | `self.amount = v` | `#[pyo3(set)]` |
//!
//! ## Rust 特有概念
//!
//! - `#[pymethods]`: 標記以下 impl 區塊為 Python 類別方法
//! - `#[new]`: 標記為建構子（Python `__init__`）
//! - `&mut self`: PyO3 中修改實例狀態的必要標記

use pyo3::prelude::*;

#[pymodule]
mod method_example {
    use super::*;

    // 將 Rust 結構體標註為可供 Python 使用的類別
    #[pyclass]
    struct RedEnvelope {
        // 這個標籤會自動為 amount 屬性產生 getter 和 setter，
        // 讓 Python 端能直接用 envelope.amount 的方式讀取和修改。
        // 先別擔心，我們稍後會詳細說明它的用法。
        #[pyo3(get, set)]
        amount: u32,
    }

    // 這個區塊內的方法將會暴露給 Python
    #[pymethods]
    impl RedEnvelope {
        // 這個標籤會將下方的 new 函式，指定為 Python 類別的建構子，
        // 也就是我們在 Python 中用 `RedEnvelope(...)` 建立物件時會呼叫的函式。
        // 關於建構子的細節我們馬上就會談到，先有個印象即可。
        #[new]
        fn new(amount: u32) -> Self {
            RedEnvelope { amount }
        }

        // 往紅包裡加錢
        fn add_money(&mut self, money: u32) {
            self.amount += money;
        }

        // 從紅包裡拿錢出來
        fn take_money(&mut self, money: u32) -> PyResult<()> {
            if money <= self.amount {
                self.amount -= money;
                Ok(())
            } else {
                // 這裡可以回傳一個錯誤，但為簡化範例先省略
                Ok(())
            }
        }
    }
}
