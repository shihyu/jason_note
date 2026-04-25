//!
//! # 無 GIL 模組範例：真正的並行計算
//!
//! 展示如何設定 `#[pymodule(gil_used = false)]` 讓整個 Rust 模組脫離 GIL 束縛，
//! 在 Python 多執行緒環境中實現零同步成本的並行。
//!
//! ## 架構圖
//!
//! ```text
//! ┌──────────────────────────────────────────────────────────────────────┐
//! │  一般 PyO3 模組（ gil_used = true, 預設值）                           │
//! │                                                                       │
//! │   Python 執行緒 A ───────┐                                           │
//! │                          ├──▶ GIL ──▶ Rust 計算 ──▶ GIL ──▶ Python  │
//! │   Python 執行緒 B ───────┘         ▲                                 │
//! │                                    │                                 │
//! │                            必須等 GIL 釋放                           │
//! └──────────────────────────────────────────────────────────────────────┘
//!
//! ┌──────────────────────────────────────────────────────────────────────┐
//! │  Free-Threaded 模組（ gil_used = false）                           │
//! │                                                                       │
//! │   Python 執行緒 A ───────▶ Rust 計算 ◀─────── Python 執行緒 B      │
//! │                                    ▲                                 │
//! │                                    │                                 │
//! │                        各自獨立的 Py<RedEnvelope>                    │
//! │                        透過 .borrow() 臨時借用 GIL                    │
//! │                                                                       │
//! │   ✅ 真正並行，無 GIL 競爭                                            │
//! │   ⚠️ 必須手動管理每個 Rust 物件的生命週期                            │
//! │   ⚠️ 不可與持有 GIL 的 Python 物件隨意共享                            │
//! └──────────────────────────────────────────────────────────────────────┘
//!
//! ┌──────────────────────────────────────────────────────────────────────┐
//! │                    Py<RedEnvelope> 生命週期                         │
//! │                                                                       │
//! │   outer_py.detach():                                                  │
//! │   ┌─────────────────────────────────────────────────────────────┐   │
//! │   │  1. outer_py.new(RedEnvelope::new(amount))                  │   │
//! │   │     → 建立 Py<RedEnvelope>，attached to outer_py           │   │
//! │   │                                                            │   │
//! │   │  2. .par_iter() → 各執行緒並行處理                          │   │
//! │   │                                                            │   │
//! │   │  3. Python::attach(|inner_py| {                            │   │
//! │   │        envelope.borrow(inner_py).validate_and_process()      │   │
//! │   │     })                                                        │   │
//! │   │     → 臨時借用該物件的 GIL，執行方法                         │   │
//! │   │                                                            │   │
//! │   │  4. 執行緒結束，Py 物件保持 alive（由 outer_py持有）        │   │
//! │   └─────────────────────────────────────────────────────────────┘   │
//! └──────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 情境              | Python 写法                        | Rust/PyO3 写法                                    |
//! |-------------------|------------------------------------|---------------------------------------------------|
//! | 定義無 GIL 模組   | （不適用）                        | `#[pymodule(gil_used = false)]`                  |
//! | 建立 Python 物件  | `RedEnvelope(amount)`             | `Py::new(outer_py, RedEnvelope::new(amount))`   |
//! | 跨執行緒共享物件  | `threading.Thread` 原生支援       | `Py<RedEnvelope>` 可安全 Send + Sync           |
//! | 讀取物件欄位     | `self.amount`                     | `envelope.borrow(inner_py).amount`               |
//! | 釋放 GIL          | Python 自動                        | `outer_py.detach(|| { ... })`                    |
//! | 臨時借用 GIL      | （不適用）                        | `Python::attach(|inner_py| { ... })`             |
//!
//! ## 關鍵技法
//!
//! - `#[pymodule(gil_used = false)]`：模組層級宣告，整個模組脫離 GIL
//! - `Py::new(py, RedEnvelope::new(amount))`：在指定 Python 上下文建立物件
//! - `.borrow(inner_py)`：臨時取得該物件的 GIL 讀取鎖，執行方法後自動歸還
//! - `rayon::current_num_threads()`：查詢 Rayon 目前的實際並行執行緒數
//!
//! ## 使用方式
//!
//! ```python
//! from free_threaded_example import process_red_envelopes_parallel, get_thread_count
//!
//! # 查詢 Rayon 執行緒池大小
//! print(get_thread_count())  # 例如：8（取決於 CPU 核心數）
//!
//! # 並行處理紅包驗證
//! results = process_red_envelopes_parallel()
//! print(results)  # [True, False, True, ...]（100 個紅包的驗證結果）
//! ```
//!
use pyo3::prelude::*;
use rayon::prelude::*;

#[pymodule(gil_used = false)]
mod free_threaded_example {
    use super::*;

    #[pyclass]
    struct RedEnvelope {
        amount: u32,
    }

    #[pymethods]
    impl RedEnvelope {
        #[new]
        fn new(amount: u32) -> Self {
            Self { amount }
        }

        /// 模擬紅包驗證的 CPU 密集計算
        /// 例如：驗證紅包的有效性、計算幸運值等
        fn validate_and_process(&self) -> bool {
            let mut result = 0u64;
            let iterations = 1_000_000;

            // 模擬複雜的紅包驗證邏輯
            for i in 0..iterations {
                result = result.wrapping_add(i);
                result = result.wrapping_mul(42);
                result = result.wrapping_add(self.amount as u64);
                result = result ^ (result >> 16);
                // 模擬額外的驗證步驟（如檢查幸運數字）
                if i % 1000 == 0 {
                    result = result.rotate_left(7);
                }
            }
            result % 2 == 0 && self.amount > 0
        }
    }

    #[pyfunction]
    fn process_red_envelopes_parallel() -> PyResult<Vec<bool>> {
        let valid_envelopes: Vec<bool> = Python::attach(|outer_py| {
            // 創建 100 個不同金額的紅包
            let envelopes: Vec<Py<RedEnvelope>> = (0..100)
                .map(|x| {
                    let amount = (x * 88) % 1000 + 1; // 金額 1~1000
                    Py::new(outer_py, RedEnvelope::new(amount)).unwrap()
                })
                .collect();

            outer_py.detach(|| {
                envelopes
                    .par_iter()
                    .map(|envelope| {
                        Python::attach(|inner_py: Python<'_>| {
                            envelope.borrow(inner_py).validate_and_process()
                        })
                    })
                    .collect()
            })
        });
        Ok(valid_envelopes)
    }

    #[pyfunction]
    fn get_thread_count() -> PyResult<usize> {
        Ok(rayon::current_num_threads())
    }
}
