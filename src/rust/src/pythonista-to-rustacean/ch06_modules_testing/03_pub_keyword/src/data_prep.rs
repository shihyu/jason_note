//! # 資料預處理模組 (Data Preparation Module)
//!
//! 本範例展示 Rust 的**細粒度可見度控制**——struct 的每個欄位、impl 的每個方法都可以獨立設定可見度。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | Struct 封裝 | 全部公開或 `@property` | 每欄位 `pub`/私有 |
//! | 建構子 | `__init__` 自動呼叫 | `impl` 中自訂 `new()` |
//! | Enum 變體 | 全部公開 | 預設全部公開（Rust 特殊設計）|
//! | 模組層級日誌 | `logging` 模組 | `pub(crate) fn` |
//!
//! ## Enum vs Struct 可見度差異
//!
//! ```text
//! Enum（所有變體皆公開）：
//! pub enum ImputationStrategy {
//!     Mean,   ← 直接 use crate::ImputationStrategy::Mean
//!     Median,
//!     Mode,
//! }
//!
//! Struct（欄位可独立設定）：
//! pub struct NormalizationParams {
//!     pub feature_name: String,  ← 公開
//!     mean: f64,                ← 私有
//!     std_dev: f64,            ← 私有
//! }
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch06_modules_testing/03_pub_keyword
//! cargo build && cargo run
//! ```
//!
//! ## 預期輸出
//!
//! ```text
//! Pipeline starting...
//! [DATA_PREP] Imputing values...
//! (Simulating mean calculation...)
//! DataPrep: Imputing with mean value 5.0...
//! [DATA_PREP] Imputing values...
//! [DATA_PREP] Imputing values...
//! Pipeline finished.
//! ```

// 1. 標記為 `pub`，使其對「父模組」(src/lib.rs) 可見
// 這是我們希望使用者呼叫的公開 API
pub fn impute_missing_values(data: &Vec<f64>) -> Vec<f64> {
    // 在模組內部，我們可以自由呼叫自己的私有函式
    let mean = calculate_mean(data);
    log_processing_step("data_prep", "Imputing values...");
    log_processing_step("data_prep", "Imputing values...");
    println!("DataPrep: Imputing with mean value {}...", mean);
    // ... 實作插補邏輯 ( 這裡只是範例)...
    data.clone()
}

// 2. 沒有 `pub`，預設為私有
// 這是內部的實作細節，父模組不應依賴它
fn calculate_mean(data: &Vec<f64>) -> f64 {
    // ... 實作計算平均數的邏輯 ...
    println!("(Simulating mean calculation...)");
    5.0 // 假設平均值是 5.0
}

// 結構體本身是 `pub`
pub struct NormalizationParams {
    pub feature_name: String, // 這個欄位是公開的
    mean: f64,                // 這個欄位是私有的
    std_dev: f64,             // 這個欄位是私有的
}

// 實作一個「建構子」(constructor)
impl NormalizationParams {
    // `new` 函式本身也必須是 `pub` 才能被外部呼叫
    pub fn new(name: String, data: &Vec<f64>) -> Self {
        // ... 假設這裡有複雜的計算 ...
        let mean = 5.0; // 範例: 計算得到的平均值
        let std_dev = 1.5; // 範例: 計算得到的標準差
        println!("Calculated params for '{}'", name);
        NormalizationParams {
            feature_name: name,
            mean,
            std_dev,
        }
    }
}

pub enum ImputationStrategy {
    Mean,
    Median,
    Mode,
}

pub(crate) fn log_processing_step(module: &str, message: &str) {
    println!("[{}] {}", module.to_uppercase(), message);
}
