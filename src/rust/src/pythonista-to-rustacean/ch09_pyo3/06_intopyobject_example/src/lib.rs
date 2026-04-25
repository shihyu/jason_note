//! # IntoPyObject: Custom Type → Python Object
//!
//! 本範例展示如何自訂 Rust 型別到 Python 物件的轉換。
//!
//! ## ASCII 架構圖
//! ```text
//! Rust: Config struct
//! ┌─────────────────────────────────────────────────────┐
//! │  struct Config { key: String, value: i32 }         │
//! │           │                                          │
//! │           │  impl IntoPyObject for Config           │
//! │           ↓                                          │
//! │  into_pyobject(py) → Bound<PyDict>                  │
//! │           │                                          │
//! └───────────│──────────────────────────────────────────┘
//!              ↓
//! Python: {"key": "my_setting", "value": 123}
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 概念 | Python | Rust (PyO3) |
//! |------|--------|--------------|
//! | 回傳任意型別 | `def f(): return obj` | `fn f() -> Config` + `IntoPyObject` |
//! | 轉換目標 | Python 原生物件 | `Bound<'py, PyDict>` |
//! | 錯誤處理 | N/A（總是成功）| `type Error = Infallible` |
//!
//! ## Rust 特有概念
//!
//! - `IntoPyObject<'py>`: 定義 Rust 型別如何轉換為 Python 物件
//! - `type Target = PyDict`: 指定要轉換成哪種 Python 內建型別
//! - `Bound<'py, PyDict>`: PyO3 0.23+ 的 GIL 安全 possession

use pyo3::prelude::*;

#[pymodule]
mod intopyobject_example {
    use super::*;

    use pyo3::types::PyDict;
    use std::convert::Infallible;

    // 一個自定義的 Rust 結構體
    struct Config {
        key: String,
        value: i32,
    }
    // 為 Config 實作 IntoPyObject
    impl<'py> IntoPyObject<'py> for Config {
        // 1. 指定目標 Python 型別是 PyDict
        type Target = PyDict;
        // 2. 指定輸出包裹型別是 Bound<PyDict>
        type Output = Bound<'py, PyDict>;
        // 3. 指定錯誤型別為 Infallible
        type Error = Infallible;
        // 4. 實現轉換邏輯
        fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
            // 使用 GIL 令牌 `py` 創建一個新的 Python 字典
            let dict = PyDict::new(py);

            // 將 Rust 結構體的欄位設定為字典的鍵值。
            // 在此處使用 .unwrap() 是安全的，因為我們確定操作不會失敗。
            dict.set_item("key", self.key).unwrap();
            dict.set_item("value", self.value).unwrap();

            // 回傳包裹好的字典物件
            Ok(dict)
        }
    }

    // #[pyfunction]
    // 定義一個 Python 可以呼叫的函式，其回傳型別為 Config
    // PyO3 會自動利用上面的 IntoPyObject 實作，將回傳的 Config 轉換成 Python 字典
    #[pyfunction]
    fn get_config() -> Config {
        Config {
            key: "my_setting".to_string(),
            value: 123,
        }
    }
}
