//!
//! # GIL 精細控制範例：就地修改與分塊計算
//!
//! 展示兩種不同的 GIL 控制策略，適用於不同的使用情境。
//!
//! ## 架構圖
//!
//! ```text
//! ┌──────────────────────────────────────────────────────────────────────┐
//! │                    策略一：隔離計算區塊                                │
//! │                                                                       │
//! │   Python list  ──extract()──▶  Rust Vec<String>                      │
//! │                                        │                              │
//! │                              py.detach() 釋放 GIL                      │
//! │                                        │                              │
//! │                           ╔════════════════════════════╗              │
//! │                           ║  純 Rust 計算（無 GIL）     ║              │
//! │                           ║  Vec<u64> checksums        ║              │
//! │                           ╚════════════════════════════╝              │
//! │                                        │                              │
//! │                     PyList::new(py, &checksums)                      │
//! │                                        │                              │
//! │                              自動重新取得 GIL                          │
//! │                                        │                              │
//! │                              新 Python list                           │
//! └──────────────────────────────────────────────────────────────────────┘
//!
//! ┌──────────────────────────────────────────────────────────────────────┐
//! │                    策略二：按需取得 GIL                               │
//! │                                                                       │
//! │   source_logs: &Bound<PyList>  ──clone().unbind()──▶  Py<PyList>  │
//! │   destination_checksums: &Bound<PyList> ──clone().unbind()──▶       │
//! │                                                          Py<PyList>  │
//! │                                        │                              │
//! │                              py.detach() 釋放 GIL                      │
//! │                                        │                              │
//! │    ┌─────────────────────────────────────────────────────────────────┐ │
//! │    │  for i in 0..len:                                              │ │
//! │    │    Python::attach(|py| {           ← 每次迭代重新取得 GIL     │ │
//! │    │        let log = logs_ref.bind(py).get_item(i)?              │ │
//! │    │        let checksum = calculate_checksum(&log);               │ │
//! │    │        checksums_ref.bind(py).set_item(i, checksum)?         │ │
//! │    │    })                                                          │ │
//! │    └─────────────────────────────────────────────────────────────────┘ │
//! └──────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 情境              | Python 写法                              | Rust/PyO3 写法                                   |
//! |-------------------|------------------------------------------|--------------------------------------------------|
//! | 建立 list         | `[1, 2, 3]`                             | `PyList::new(py, &[1, 2, 3])`                  |
//! | 轉換為 Rust 型別  | （原生就是 Python）                     | `logs.extract::<Vec<String>>()?`                  |
//! | 釋放 GIL          | （由 GIL 控制）                         | `py.detach(|| { ... })`                          |
//! | 重新取得 GIL      | （自動）                                | `Python::attach(|py| { ... })`                  |
//! | 讀取 list 元素   | `logs[i]`                               | `logs_ref.bind(py).get_item(i)?`                |
//! | 寫入 list 元素   | `checksums[i] = x`                      | `checksums_ref.bind(py).set_item(i, x)?`        |
//!
//! ## 關鍵技法
//!
//! - `Bound<'_, PyList>`：PyO3 0.22+ 的安全引用型別，編譯期確保 GIL 有效性
//! - `.unbind()`：將 `Bound` 轉為 `Py`，擺脫生命週期束縛，帶入無 GIL 閉包
//! - `.bind(py)`：在需要時將 `Py` 重新「綁定」回 `Bound`，附著於當前 GIL 狀態
//! - `Python::attach(|py| { ... })`：在無 GIL 區塊內臨時重新取得 GIL 的標準手法
//!
//! ## 使用方式
//!
//! ```python
//! import checksum_engine
//!
//! logs = ["log1", "log2", "log3"]
//!
//! # 策略一：隔離計算，一次性更新
//! checksums = checksum_engine.generate_checksums(logs)
//! # 回傳新的 list：[99, 98, 99]（各 byte sum）
//!
//! # 策略二：就地修改預先存在的 list
//! dest = [0, 0, 0]
//! checksum_engine.generate_checksums_in_place(logs, dest)
//! # dest 被原地修改為 [99, 98, 99]
//! ```
//!
use pyo3::prelude::*;
use pyo3::types::PyList;

#[pymodule]
mod checksum_engine {
    use super::*;

    /// 策略一：隔離計算區塊，一次性更新
    #[pyfunction]
    fn generate_checksums(py: Python<'_>, logs: &Bound<'_, PyList>) -> PyResult<Py<PyList>> {
        // 階段一：持有 GIL，將 Python list 高效轉換為 Rust Vec
        let rust_logs: Vec<String> = logs.extract()?;
        // 階段二：釋放 GIL，執行 CPU 密集型運算
        // py.detach() 會釋放 GIL，讓閉包內的程式碼在無鎖狀態下執行。
        let checksums: Vec<u64> = py.detach(|| {
            rust_logs
                .iter()
                .map(|log| calculate_checksum(log))
                .collect()
        });
        // 階段三：運算結束後，GIL 會自動重新取得。
        // 我們再次持有 GIL，將 Rust Vec 轉換回新的 Python list。
        Ok(PyList::new(py, &checksums)?.into())
    }

    fn calculate_checksum(s: &str) -> u64 {
        // 模擬一個純粹的、耗時的計算任務
        s.bytes().fold(0, |acc, byte| acc.wrapping_add(byte as u64))
    }

    /// 策略二：在無鎖區塊中，按需取得 GIL
    /// 這個函式會就地修改傳入的 destination_checksums list
    #[pyfunction]
    fn generate_checksums_in_place<'py>(
        py: Python<'py>,
        source_logs: &Bound<'py, PyList>, // 注意這裡傳入的是共享參考
        destination_checksums: &Bound<'py, PyList>,
    ) -> PyResult<()> {
        let len = source_logs.len();
        if len != destination_checksums.len() {
            // 在真實情境中，應回傳一個 Python 異常，例如 ValueError
            return Ok(());
        }
        // 將活躍的 `Bound` 物件轉換為可儲存的 `Py` 物件，以便帶入無鎖區塊
        let logs_ref = source_logs.clone().unbind();
        let checksums_ref = destination_checksums.clone().unbind();
        // 釋放 GIL，進入無鎖運算區域
        py.detach(move || -> PyResult<()> {
            for i in 0..len {
                // 運算前，透過 `attach` 重新取得 GIL，
                // 並將 `Py` 物件 `bind` 回一個暫時的 `Bound` 物件來讀取資料
                let log_entry: String =
                    Python::attach(|py| logs_ref.bind(py).get_item(i)?.extract())?;
                // 在無 GIL 狀態下，進行繁重的運算
                let checksum = calculate_checksum(&log_entry);
                // 運算後，再次取得 GIL，將結果寫回目標 list
                Python::attach(|py| checksums_ref.bind(py).set_item(i, checksum))?;
            }
            Ok(())
        })
    }
}
