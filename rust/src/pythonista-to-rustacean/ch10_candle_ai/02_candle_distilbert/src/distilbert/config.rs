//!
//! # DistilBERT 設定檔
//!
//! 定義 DistilBERT 模型的所有超參數，包括維度、層數、注意力頭數、激活函數等。
//! 實作 `Default` trait 提供合理的預設值，方便快速建立模型。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! | 列舉型別 | `class HiddenAct(str, Enum)` | `enum HiddenAct { Gelu, Relu }` |
//! | 結構定義 | `dataclass` 或 `NamedTuple` | `struct` + `derive` macro |
//! | 預設值 | `self.dim = 768` 在 `__init__` | `Default::default()` trait |
//! | 反序列化 | `@dataclass` + `from_dict` | `#[derive(Deserialize)]` |
//!
//! ## 關鍵技法
//!
//! - `#[serde(rename_all = "lowercase")]`: 自動處理 JSON key 命名風格
//! - `#[serde(default)]`: 允許缺失欄位使用預設值
//! - `pub enum` + `pub struct`: 所有欄位公開，方便外部存取組態
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch10_candle_ai/02_candle_distilbert
//! cargo build --release
//! ```
//!
use serde::Deserialize;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum HiddenAct {
    Gelu,
    Relu,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum PositionEmbeddingType {
    #[default]
    Absolute,
}

#[derive(Debug, Clone, PartialEq, Deserialize)]
pub struct DistilBertConfig {
    pub activation: HiddenAct,
    pub dim: usize,
    pub hidden_dim: usize,
    pub initializer_range: f64,
    pub max_position_embeddings: usize,
    pub model_type: Option<String>,
    pub n_heads: usize,
    pub n_layers: usize,
    pub pad_token_id: usize,
    pub vocab_size: usize,
    #[serde(default)]
    pub position_embedding_type: PositionEmbeddingType,
    #[serde(default)]
    pub use_cache: bool,
}

impl Default for DistilBertConfig {
    fn default() -> Self {
        Self {
            activation: HiddenAct::Gelu,
            dim: 768,
            hidden_dim: 3072, // 4 * 768
            initializer_range: 0.02,
            max_position_embeddings: 512,
            model_type: Some("distilbert".to_string()),
            n_heads: 12,
            // PyTorch 用 6，但 candle_transformers 用 12
            // 這裡先放 6，晚點改 12 看看差別
            n_layers: 6,
            pad_token_id: 0,
            vocab_size: 30522,
            // 以下是 Rust 專有的
            position_embedding_type: PositionEmbeddingType::Absolute,
            use_cache: true,
        }
    }
}
