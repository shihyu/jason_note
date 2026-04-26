//! # GIL: Implicit vs Explicit Borrowing
//!
//! 本範例展示 PyO3 中 GIL（全域直譯器鎖）的使用方式。
//!
//! ## ASCII 架構圖
//! ```text
//! Python Runtime
//! ┌──────────────────────────────────────────────────────────┐
//! │  when Python calls Rust function:                       │
//! │                                                          │
//! │  Implicit GIL         Explicit GIL                      │
//! │  ┌────────────────┐    ┌─────────────────────────────┐   │
//! │  │ fn f(v: Vec)  │    │ fn f(py: Python<'_>)      │   │
//! │  │   接收 Rust   │    │   手動取得 GIL Token        │   │
//! │  │   _owned_ val │    │   才能呼叫 py.import()      │   │
//! │  └────────────────┘    └─────────────────────────────┘   │
//! │         ↑                         ↑                     │
//! │   Bound<'_, T>              Python<'_>                   │
//! │   自動保證 GIL              明確的生命周期                │
//! └──────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 概念 | Python | Rust (PyO3) |
//! |------|--------|--------------|
//! | GIL 持有 | 始终（单线程）| `Python<'_>` token 明確生命週期 |
//! | 隱式接收 | 自動 | `#[pyfunction] fn f(v: Vec<u64>)` |
//! | 顯式存取 | N/A | `#[pyfunction] fn f(py: Python<'_>)` |
//! | Python 模組 | `import uuid` | `py.import("uuid")?` |
//!
//! ## Rust 特有概念
//!
//! - `Bound<'_, PyList>`: PyO3 0.23+ 的所有權安全 GIL 借用
//! - `Python<'_>`: GIL token，代表此函式執行期間 Python 直譯器被鎖定
//! - `py.import()`: 透過 GIL token 取得 Python 模組

use pyo3::prelude::*;
use pyo3::types::PyList;

#[pymodule]
mod python_native_example {
    use super::*;

    // #[pyfunction]
    // fn print_number_list(numbers: &PyList) {
    //     // 這裡會編譯失敗
    //     for num in numbers {
    //         println!("{num}");
    //     }
    // }

    #[pyfunction]
    fn print_number_list(
        // `'_` 是 Rust 慣用的「生命週期省略」寫法，
        // 在此處它會被編譯器自動推導為代表 GIL 有效範圍的 `'py`。
        list: Bound<'_, PyList>,
    ) {
        println!(">>> [Rust] print_number_list 被呼叫");
        // `Bound` 作為參數，靜態地保證了 GIL 在此函式作用域内已被持有
        for item in list.iter() {
            println!("{}", item);
        }
    }

    // 雖然未聲明，但因為是由 Python 呼叫，
    // 所以執行時依然持有 GIL
    #[pyfunction]
    fn implicit_gil(list: Vec<u64>) {
        // ... 這段程式碼依然在 GIL 保護下安全執行 ...
        println!(">>> [Rust] implicit_gil 被呼叫");
        println!("Rust 收到的 Vec: {:?}", list);
        // 在 Rust 這裡做運算非常快，且完全型別安全
        let sum: u64 = list.iter().sum();

        println!("計算結果 (Sum): {}", sum);
    }

    // 明確聲明需要 GIL 令牌，
    // 以便在函式內部使用 Python 的 API
    #[pyfunction]
    fn explicit_gil(py: Python<'_>) -> PyResult<()> {
        println!(">>> [Rust] explicit_gil 被呼叫");

        // `py` 這個變數現在可以用來操作 Python 直譯器
        let uuid_module = py.import("uuid")?;
        let uuid_obj = uuid_module.getattr("uuid4")?.call0()?;
        println!("從 Python 取得的 UUID: {}", uuid_obj);
        Ok(())
    }
}
