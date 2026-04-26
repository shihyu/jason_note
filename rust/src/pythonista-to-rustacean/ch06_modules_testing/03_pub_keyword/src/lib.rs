//! # `pub` 關鍵字與可見度 (Visibility)
//!
//! 本範例展示 Rust 的**五級可見度**，說明為何封裝是 Rust 設計的核心。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 公開成員 | `def public_api(self)` | `pub fn public_api()` |
//! | 私有成員 | `def _private(self)` | `fn private()` (預設) |
//! | 受保護（跨 crate） | `def protected(self)` | `pub(crate) fn` |
//! | 結露式封裝 | 依賴命名慣例 | 依賴編譯器強制 |
//!
//! ## 五級可見度
//!
//! ```text
//! pub              ← 任意位置可存取
//! pub(crate)      ← 同 crate 內可存取
//! pub(super)      ← 父模組可存取
//! pub(in path)    ← 指定路徑內可存取
//! (無標記)         ← 僅同模組可存取 (private)
//! ```
//!
//! ## 架構圖：data_prep 模組
//!
//! ```text
//! lib.rs
//! └── data_prep (data_prep.rs)
//!     ├── pub fn impute_missing_values()  ← 公開，lib 可用
//!     │   └── calls calculate_mean()     ← 私有，僅內部呼叫
//!     ├── fn calculate_mean()            ← 私有，外部無法見
//!     ├── pub struct NormalizationParams
//!     │   ├── pub feature_name: String   ← 公開欄位
//!     │   ├── mean: f64                   ← 私有欄位
//!     │   └── std_dev: f64                ← 私有欄位
//!     │   └── pub fn new()                ← 公開建構子
//!     ├── pub enum ImputationStrategy     ← 公開列舉（所有變體）
//!     └── pub(crate) fn log_processing_step() ← 同 crate 可用
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch06_modules_testing/03_pub_keyword
//! cargo build && cargo run
//! ```

// 宣告 `data_prep` 模組，編譯器會尋找 `src/data_prep.rs`
mod data_prep;

use crate::data_prep::NormalizationParams; // `NormalizationParams` 本身是公開的，可以 `use`
// 我們可以 `use` Enum 本身...
use crate::data_prep::ImputationStrategy;

// 假設這是 Crate 的主要進入點，用來執行分析
pub fn run_analysis_pipeline(raw_data: &Vec<f64>) -> Vec<f64> {
    println!("Pipeline starting...");
    data_prep::log_processing_step("lib", "Pipeline starting...");
    // 1. 呼叫公開的 `impute_missing_values` 函式
    // 編譯成功！
    // `impute_missing_values` 被標記為 `pub`，
    // 因此 `lib.rs` ( 其父模組) 可以存取它。
    let cleaned_data = data_prep::impute_missing_values(raw_data);
    // 2. 嘗試直接呼叫內部的 `calculate_mean` 函式
    // 編譯失敗！
    // `calculate_mean` 是 `data_prep` 模組的私有項目
    // let mean = data_prep::calculate_mean(raw_data);
    data_prep::log_processing_step("lib", "Pipeline finished.");
    println!("Pipeline finished.");
    cleaned_data
}

fn try_create_params() {
    let sample_data = vec![1.0, 2.0];
    // 1. 透過公開的建構子 `new`
    // 編譯成功！
    let params = NormalizationParams::new("age".to_string(), &sample_data);
    // 2. 存取公開欄位
    // 編譯成功！ `feature_name` 欄位是 `pub`
    println!("Feature: {}", params.feature_name);
    // 3. 存取私有欄位
    // 編譯失敗！ `mean` 欄位是私有的
    // println!("Mean: {}", params.mean);
    // 4. 嘗試直接存取欄位 (Struct Literal 語法)
    // 編譯失敗！
    // 因為 `mean` 和 `std_dev` 欄位是私有的
    // let manual_params = NormalizationParams {
    // feature_name: "age".to_string(),
    // mean: 10.0,
    // std_dev: 3.0,
    // };
}

fn select_strategy() {
    // ... 也可以直接存取它所有的變體
    // 這在 struct 上是行不通的，但在 enum 上完全合法
    let strategy = ImputationStrategy::Median;
    // 我們可以輕鬆地在 match 中使用它們
    match strategy {
        ImputationStrategy::Mean => println!("Using Mean"),
        ImputationStrategy::Median => println!("Using Median"),
        ImputationStrategy::Mode => println!("Using Mode"),
    }
}
