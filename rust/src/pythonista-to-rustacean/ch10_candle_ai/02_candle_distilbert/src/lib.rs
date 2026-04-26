//!
//! # DistilBERT Candle 實作
//!
//! 本 crate 提供 DistilBERT 模型在 Hugging Face Candle 框架下的純 Rust 實作。
//! 支援 Masked Language Model (MLM) 任務的推理，可用於填充被遮罩的 token。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! | 引用子模組 | `from .distilbert import DistilBertConfig` | `pub mod distilbert;` + `use distilbert::config::DistilBertConfig` |
//! | 匯出 public API | `__all__ = ["DistilBertConfig", ...]` | `pub use distilbert::...` |
//!
//! ## 關鍵技法
//!
//! - `pub mod`：將子模組公開供外部使用
//! - `pub use`：重新匯出，提供更簡潔的 public API
//! - `Result` 型別：Rust 風格的錯誤處理，取代 Python 的例外
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch10_candle_ai/02_candle_distilbert
//! cargo build --release
//! ```
//!
pub mod distilbert;

pub use distilbert::config::DistilBertConfig;
pub use distilbert::{DistilBertForMaskedLM, DistilBertModel};
