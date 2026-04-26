//!
//! # JSON 解析與並行計算範例
//!
//! 展示如何在 PyO3 中結合 `serde_json` 進行 JSON 解析，
//! 並使用 `Rayon` 實現無 GIL 的 CPU-bound 並行計算。
//!
//! ## 架構圖
//!
//! ```text
//! ┌──────────────────────────────────────────────────────────────────────┐
//! │                         Python 呼叫層                                 │
//! │                                                                       │
//! │   json_parser.parse_and_sum_parallel(json_strings)                    │
//! │            │                                                         │
//! │            ▼                                                         │
//! │   ┌─────────────────────────────────────────────────────────────┐     │
//! │   │  階段一：持有 GIL，將 Python list 轉為 Rust Vec<String>      │     │
//! │   └─────────────────────────────────────────────────────────────┘     │
//! │                           │                                          │
//! │                           ▼                                          │
//! │   ┌─────────────────────────────────────────────────────────────┐     │
//! │   │  階段二：py.detach() 釋放 GIL                              │     │
//! │   │                                                          │     │
//! │   │    ┌────┐  ┌────┐  ┌────┐  ┌────┐                       │     │
//! │   │    │ T0 │  │ T1 │  │ T2 │  │ T3 │  ← Rayon執行緒池      │     │
//! │   │    └──┬─┘  └──┬─┘  └──┬─┘  └──┬─┘                       │     │
//! │   │       │       │       │       │                            │     │
//! │   │       ▼       ▼       ▼       ▼                            │     │
//! │   │    ┌────────────────────────────────────────────┐            │     │
//! │   │    │  rayon::par_iter() → 並行解析 JSON        │            │     │
//! │   │    │  serde_json::from_str::<LogEntry>        │            │     │
//! │   │    └────────────────────────────────────────────┘            │     │
//! │   └─────────────────────────────────────────────────────────────┘     │
//! │                           │                                          │
//! │                           ▼                                          │
//! │   ┌─────────────────────────────────────────────────────────────┐     │
//! │   │  階段三：GIL 自動重新取得，回傳 f64 結果                    │     │
//! │   └─────────────────────────────────────────────────────────────┘     │
//! └──────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 情境              | Python 写法                              | Rust/PyO3 写法                              |
//! |-------------------|------------------------------------------|---------------------------------------------|
//! | JSON 解析         | `json.loads(s)['value']`                  | `serde_json::from_str::<LogEntry>(s)`        |
//! | 序列迭代          | `for s in strings: total += ...`         | `.iter().map(...).sum()`                    |
//! | 並行迭代          | `with ThreadPool() as pool: ...`          | `.par_iter().map(...).sum()` (Rayon)       |
//! | GIL 管理          | Python 原生自動                          | `py.detach(|| ...)` 釋放 / 自動重新取得     |
//! | 錯誤處理（Rust）  | `try/except`                             | `Result.unwrap_or(default)`                 |
//!
//! ## 關鍵技法
//!
//! - `rayon::prelude::ParallelIterator`：透過 `.par_iter()` 將序列迭代轉為並行
//! - `serde::Deserialize`：derive macro 自動產生 JSON → Rust 結構體解析碼
//! - `py.detach()`：釋放 GIL，讓無關的 Python 執行緒得以並行
//! - `.unwrap_or(0.0)`：優雅處理解析失敗，不讓單筆錯誤拖垮整體
//!
//! ## 使用方式
//!
//! ```python
//! import json_parser
//!
//! logs = ['{"value": 1.5}', '{"value": 2.3}', '{"invalid": true}']
//! # 並行版本（推薦）
//! result = json_parser.parse_and_sum_parallel(logs)  # 3.8
//!
//! # 序列版本（對照組）
//! result = json_parser.parse_and_sum_sequential(logs)  # 3.8
//!
//! # GIL 釋放的序列版本（可在 Python 多執行緒中並行的序列計算）
//! result = json_parser.parse_and_sum_sequential_detached(logs)  # 3.8
//! ```
//!
use pyo3::prelude::*;
use rayon::prelude::*;
use serde::Deserialize;

#[pymodule]
mod json_parser {
    use super::*;

    /// 使用 Serde 的 derive macro，讓 Rust 能自動從 JSON 字串解析並建構出這個結構體。
    /// Rust 只會關心它認識的欄位 ( 如此處的 `value`)，JSON 中任何其他的欄位都會被安全地忽略。
    #[derive(Deserialize)]
    struct LogEntry {
        value: f64,
    }

    /// 使用 Rayon 並行解析 JSON 字串並加總 'value' 欄位。
    #[pyfunction]
    fn parse_and_sum_parallel(json_strings: Vec<String>) -> f64 {
        json_strings
            // .par_iter()：由 Rayon 提供，將標準的迭代器轉換為「並行迭代器」。
            // 這會自動將後續的操作 ( 如 .map) 分配到多個 CPU 核心上執行。
            .par_iter()
            // .map()：對集合中的每一個元素 (這裡的 `s` 是一個 JSON 字串) 套用一個閉包。
            .map(|s| {
                // serde_json::from_str：一個以速度著稱的 JSON 解析函式。
                // 它會嘗試將字串 `s` 解析成一個 `LogEntry` 結構體。
                // 這個操作會返回一個 `Result` 型別，代表成功或失敗。
                serde_json::from_str::<LogEntry>(s)
                    // .map()：這是 `Result` 型別的方法。如果解析成功 (Ok)，
                    // 就執行閉包內的程式碼，取出 LogEntry 中的 `value` 欄位。
                    .map(|entry| entry.value)
                    // .unwrap_or(0.0)：這也是 `Result` 的方法。如果解析失敗 (Err)，
                    // ( 例如 JSON 格式錯誤或沒有 'value' 欄位)，則提供一個預設值 0.0。
                    // 這讓我們的程式碼更穩健，不會因為單筆資料錯誤而崩潰。
                    .unwrap_or(0.0)
            })
            // .sum()：由 Rayon 提供，它會迅速地將所有並行計算出的 `value` 值加總起來，返回最終結果。
            .sum()
    }

    /// 序列化版本的實作，作為對照組。
    #[pyfunction]
    fn parse_and_sum_sequential(json_strings: Vec<String>) -> f64 {
        json_strings
            // .iter()：這是 Rust 標準的迭代器。
            // 這意味著 .map() 操作將會在單一執行緒上一個接一個地執行。
            .iter()
            .map(|s| {
                serde_json::from_str::<LogEntry>(s)
                    .map(|entry| entry.value)
                    .unwrap_or(0.0)
            })
            .sum()
    }

    /// 序列化的 GIL 釋放版本。
    /// 讓這個函式能在 Python 的多執行緒環境中順暢運行。
    #[pyfunction]
    fn parse_and_sum_sequential_detached(py: Python<'_>, json_strings: Vec<String>) -> f64 {
        // 關鍵：py.detach() 用於釋放 GIL。
        py.detach(|| {
            // 在這個閉包 `{...}` 內執行的 Rust 程式碼，是在「沒有」持有 GIL 的狀態下運行的。
            // 這允許 Python 的其他執行緒繼續執行它們的工作，從而實現真正的並行。
            parse_and_sum_sequential(json_strings)
        })
    }
}
