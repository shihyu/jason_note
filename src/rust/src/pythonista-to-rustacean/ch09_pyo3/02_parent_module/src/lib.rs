//! # Parent Module and Submodule Hierarchy
//!
//! 本範例展示在 PyO3 中建立**巢狀子模組**的結構。
//!
//! ## ASCII 架構圖
//! ```text
//! parent_module (Rust)          Python 視角
//! ┌──────────────────────┐    ┌─────────────────────────────┐
//! │ parent_module.rs     │    │ import parent_module        │
//! │                      │    │                             │
//! │ #[pymodule]         │    │ parent_module.child_func()  │
//! │ fn parent_module    │    │   └── child_module (sub)   │
//! │   │                 │    │                             │
//! │   ├── PyModule::new │──────────→ child_module           │
//! │   └── add_submodule │    │   └── child_func()          │
//! └──────────────────────┘    └─────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 概念 | Python | Rust (PyO3) |
//! |------|--------|--------------|
//! | 建立子模組 | `import child` | `PyModule::new(py, "child")` |
//! | 加入函式 | `def child_func():` | `child.add_function(wrap_pyfunction!(...))` |
//! | 註冊子模組 | `import parent.child` | `m.add_submodule(&child)?` |
//!
//! ## Rust 特有概念
//!
//! - `PyModule::new(py, name)`: 在 Rust 中建立新的 Python 模組物件
//! - `add_submodule()`: 將子模組掛載到父模組下，形成命名空間階層
//! - `wrap_pyfunction!()`: 巨集包裝，讓自由函式可被 PyO3 调用

use pyo3::prelude::*;

#[pyfunction]
fn child_func() -> String {
    "Hello from the child module!".to_string()
}

#[pymodule]
fn parent_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // 1. 直接在父模組中，建立一個新的 PyModule 物件作為子模組
    let child = PyModule::new(m.py(), "child_module")?;
    // 2. 在子模組中註冊它自己的函式
    child.add_function(wrap_pyfunction!(child_func, &child)?)?;
    // 3. 將建立好的子模組，加入到父模組中
    m.add_submodule(&child)?;
    Ok(())
}
