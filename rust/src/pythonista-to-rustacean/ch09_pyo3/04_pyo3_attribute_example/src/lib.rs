//! # PyO3 Attributes: Warning, Signature, and More
//!
//! 本範例展示 PyO3 各種 attribute 的用法。
//!
//! ## ASCII 架構圖
//! ```text
//! #[pyfunction] 屬性對照
//! ┌────────────────────────────────────────────────────────────┐
//! │  #[pyo3(warn(message = "..."))]                          │
//! │      └── 發出 Python Warning                             │
//! │                                                           │
//! │  #[pyo3(signature = (a, /, *args, k=v))]               │
//! │      ├── /  : 位置參數                                   │
//! │      ├── *  : 可變參數 (*args)                          │
//! │      └── kw  : 關鍵字參數帶預設值                         │
//! │                                                           │
//! │  #[pyo3(text_signature = "(a, b=3)")]                  │
//! │      └── 控制 Python help() 顯示格式                     │
//! └────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 概念 | Python | Rust (PyO3) |
//! |------|--------|--------------|
//! | 警告 | `warnings.warn("msg")` | `#[pyo3(warn(message = "..."))]` |
//! | 函式簽名 | `def f(a, /, *args, k=3)` | `#[pyo3(signature = (a, /, *args, k=3))]` |
//! | help 文件 | `"""doc"""` | `#[pyo3(text_signature = "...")]` |
//!
//! ## Rust 特有概念
//!
//! - `#[pyo3(warn(...))]`: 編譯期標記，函式被呼叫時發出 Python 警告
//! - `signature = (...)`: 定義 Python 端的函式簽名，支援 `/`、`*`、`=` 語法
//! - `text_signature`: 控制 `help(func)` 的顯示格式

use pyo3::exceptions::PyFutureWarning;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyTuple};

#[pymodule]
mod pyo3_attribute_example {
    use super::*;

    // 範例一：發出一個「函式已棄用」的通用警告 (UserWarning)
    #[pyfunction]
    #[pyo3(warn(message = "此函式已棄用，請改用 new_function()。"))]
    fn function_with_warning() -> bool {
        true
    }

    // 範例二：使用特定的警告種類 (FutureWarning)，預告未來的變更
    #[pyfunction]
    #[pyo3(warn(
        message = "此函式的回傳值型別未來將從布林值變更為整數。",
        category = PyFutureWarning
    ))]
    fn function_with_warning_and_custom_category() -> bool {
        true
    }

    #[pyfunction]
    #[pyo3(signature = (
        source,          // 第一個參數是 source
        /,               // 分隔線，代表 source 只能用位置傳入
        *steps,          // * 開頭，代表接收任意數量的「位置參數 (*args)」
        retries=3,       // 帶有預設值的參數
        verbose=false,   // 另一個帶預設值的參數
        **extra_config   // ** 開頭，代表接收任意數量的「關鍵字參數 (**kwargs)」
    ))]
    fn run_job(
        // source 對應到 Python 的字串，在 Rust 這邊用 &str 接收
        source: &str,
        // *steps 會被打包成一個 PyTuple，這是在 Rust 中對 Python tuple 的表示
        steps: &Bound<'_, PyTuple>,
        // retries 和 verbose 是帶有預設值的普通參數
        retries: u8,
        verbose: bool,
        // **extra_config 會被打包成 PyDict，用 Option 包裹是因為它可能不存在
        extra_config: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        println!("== 工作開始 ==");
        println!("資料來源: {}", source);
        if !steps.is_empty() {
            println!("執行步驟: {:?}", steps);
        }
        println!("重試次數: {}", retries);
        if verbose {
            println!("詳細模式: 開啟");
        }
        if let Some(config) = extra_config {
            println!("額外設定: {:?}", config);
        }
        println!("== 工作完成 ==");
        Ok(())
    }

    // 假設這個函式會從某處讀取預設的重試次數
    fn default_retries() -> u8 { 3 }

    #[pyfunction]
    #[pyo3(
        // 「內部藍圖」：功能上，retries 的預設值由函式呼叫決定
        signature = (source, /, *steps, retries = default_retries(), **extra_config),
        
        // 「外部說明書」：呈現上，我們直接告訴使用者這個預設值通常是 3
        text_signature = "(source, /, *steps, retries=3, **extra_config)"
    )]
    fn run_job_with_dynamic_default(
        source: &str,
        steps: &Bound<'_, PyTuple>,
        retries: u8,
        extra_config: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> { 
        println!("== 動態重試工作開始 ==");
        println!("資料來源: {}", source);
        if !steps.is_empty() {
            println!("執行步驟: {:?}", steps);
        }
        println!("重試次數: {}", retries);
      
        if let Some(config) = extra_config {
            println!("額外設定: {:?}", config);
        }
        println!("== 動態重試工作結束 ==");
        Ok(()) 
    }

}
