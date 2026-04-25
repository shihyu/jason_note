//!
//! # HuggingFace 資料集載入範例
//!
//! 展示如何使用 Burn 的 `HuggingfaceDatasetLoader` 從 Hugging Face Hub
//! 動態下載並載入 SQLite 格式的資料集。
//!
//! ## 架構圖
//!
//! ```text
//! ┌────────────────────────────────────────────────────────────────────────┐
//! │              HuggingFace 資料集載入流程                            │
//! │                                                                        │
//! │   HuggingfaceDatasetLoader::new("google/boolq")                      │
//! │          │                                                           │
//! │          ▼                                                           │
//! │   ┌─────────────────────────┐                                    │
//! │   │  線上下載 SQLite 檔案   │                                    │
//! │   │  (自動快取至本地目錄)    │                                    │
//! │   └──────────┬────────────┘                                    │
//! │              ▼                                                    │
//! │   ┌─────────────────────────┐                                    │
//! │   │  SqliteDataset<BoolqItem> │ ← 泛型結構，編譯期安全        │
//! │   └─────────────────────────┘                                    │
//! └────────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 情境              | Python (Datasets) 写法                                | Rust (Burn) 写法                              |
//! |-------------------|---------------------------------------------------|---------------------------------------------|
//! | 動態下載         | `load_dataset("google/boolq", split="train")` | `HuggingfaceDatasetLoader::new("google/boolq")` |
//! | 資料集查詢       | `dataset[0]` / `dataset["question"]`              | `dataset.get(0)` / 手動欄位投影                |
//! | 序列化           | `dataset.save_to_disk("./cache")`                  | `SqliteDataset<T>` 原生支援 SQLite 持久化     |
//!
//! ## 關鍵技法
//!
//! - `HuggingfaceDatasetLoader::new`：自動從 HF Hub 下載資料集
//! - `SqliteDataset<T>`：泛型容器，編譯期確保型別安全
//! - `#[derive(serde::Serialize, serde::Deserialize)]`：序列化結構體供 dataset 使用
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch11_burn_ai/03_burn_huggingface_dataset
//! cargo run --release
//! ```
//!
use burn::data::dataset::HuggingfaceDatasetLoader;
use burn::data::dataset::SqliteDataset;

#[derive(Clone, Debug, serde::Serialize, serde::Deserialize)]
struct BoolqItem {
    question: String,
    answer: bool,
    passage: String,
}

fn main() {
    let dataset: SqliteDataset<BoolqItem> = HuggingfaceDatasetLoader::new("google/boolq")
        .dataset("train")
        .unwrap();
    println!("{:?}", dataset);
}
