//!
//! # 詞嵌入層
//!
//! 將輸入的 token IDs 轉換為密集向量表示，並加入位置編碼資訊。
//! 最後透過 LayerNorm 進行標準化輸出，為 Transformer 編碼器提供輸入表示。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! | 建立嵌入層 | `nn.Embedding(vocab_size, dim)` | `embedding(vocab_size, dim, vb.pp(...))` |
//! | 生成位置 ID | `torch.arange(0, seq_len)` | `Tensor::arange(0, seq_len as u32, device)` |
//! | 嵌入相加 | `input_embeds + position_embeds` | `input_embeds.broadcast_add(&position_embeddings)` |
//! | LayerNorm | `nn.LayerNorm(dim, eps=1e-12)` | `layer_norm(dim, 1e-12, vb.pp(...))` |
//!
//! ## 關鍵技法
//!
//! - `Tensor::arange`：建立連續序列，類似 Python 的 `torch.arange`
//! - `broadcast_add`：自動廣播後相加，處理維度相容的張量
//! - `embedding()` helper：封裝 candle_nn::Embedding 的建立過程
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch10_candle_ai/02_candle_distilbert
//! cargo build --release
//! ```
//!
use candle_core::{Result, Tensor};
use candle_nn::{Embedding, Module, VarBuilder};

use super::config::DistilBertConfig;
use super::nn::{LayerNorm, embedding, layer_norm};

pub struct Embeddings {
    word_embeddings: Embedding,
    position_embeddings: Embedding,
    layer_norm: LayerNorm,
}

impl Embeddings {
    pub fn load(vb: VarBuilder, config: &DistilBertConfig) -> Result<Self> {
        let word_embeddings = embedding(config.vocab_size, config.dim, vb.pp("word_embeddings"))?;
        let position_embeddings = embedding(
            config.max_position_embeddings,
            config.dim,
            vb.pp("position_embeddings"),
        )?;
        let layer_norm = layer_norm(config.dim, 1e-12, vb.pp("LayerNorm"))?;

        Ok(Self {
            word_embeddings,
            position_embeddings,
            layer_norm,
        })
    }

    pub fn forward(&self, input_ids: &Tensor) -> Result<Tensor> {
        let input_embeds = self.word_embeddings.forward(input_ids)?;

        let (_bsize, seq_len) = input_ids.dims2()?;
        let position_ids = Tensor::arange(0, seq_len as u32, input_ids.device())?;

        let position_embeddings = self.position_embeddings.forward(&position_ids)?;
        let embeddings = input_embeds.broadcast_add(&position_embeddings)?;
        let embeddings = self.layer_norm.forward(&embeddings)?;

        Ok(embeddings)
    }
}
