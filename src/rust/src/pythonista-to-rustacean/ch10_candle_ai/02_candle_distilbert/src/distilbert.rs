//!
//! # DistilBERT 模型主體
//!
//! 整合 Embeddings、Transformer 和 MLM Head，構成完整的 DistilBERT 模型。
//! 提供 `DistilBertModel`（純編碼器）和 `DistilBertForMaskedLM`（完整 MLM 模型）兩種結構。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! | 建立模型 | `DistilBertModel.from_pretrained()` | `DistilBertForMaskedLM::load(vb, &config)` |
//! | 前向傳播 | `model(input_ids, attention_mask)` | `model.forward(&input_ids, &attention_mask)` |
//! | 彈性路徑處理 | try/except 載入不同路徑 | `match` + `if let Some()` 組合處理 |
//!
//! ## 關鍵技法
//!
//! - `vb.pp("prefix")`：Path helper 動態調整載入路徑
//! - `match` 表達式：優雅處理可能的錯誤並提供備援路徑
//! - `#[allow(non_snake_case)]`：保持 PyTorch 風格的命名相容性
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch10_candle_ai/02_candle_distilbert
//! cargo build --release
//! ```
//!
// 宣告子模組
pub mod attention;
pub mod config;
pub mod embeddings;
pub mod encoder;
pub mod head;
pub mod layer;
pub mod nn;
pub mod utils;

use candle_core::{Device, Result, Tensor};
use candle_nn::{Module, VarBuilder};

use config::DistilBertConfig;
use embeddings::Embeddings;
use encoder::Transformer;
use head::DistilBertOnlyMLMHead;

pub struct DistilBertModel {
    embeddings: Embeddings,
    transformer: Transformer,
    pub device: Device,
}

impl DistilBertModel {
    pub fn load(vb: VarBuilder, config: &DistilBertConfig) -> Result<Self> {
        let (embeddings, transformer) = match (
            Embeddings::load(vb.pp("embeddings"), config),
            Transformer::load(vb.pp("transformer"), config),
        ) {
            (Ok(embeddings), Ok(encoder)) => (embeddings, encoder),
            (Err(err), _) | (_, Err(err)) => {
                if let Some(model_type) = &config.model_type {
                    if let (Ok(embeddings), Ok(encoder)) = (
                        Embeddings::load(vb.pp(&format!("{model_type}.embeddings")), config),
                        Transformer::load(vb.pp(&format!("{model_type}.transformer")), config),
                    ) {
                        (embeddings, encoder)
                    } else {
                        return Err(err);
                    }
                } else {
                    return Err(err);
                }
            }
        };

        Ok(Self {
            embeddings,
            transformer,
            device: vb.device().clone(),
        })
    }

    pub fn forward(&self, input_ids: &Tensor, attention_mask: &Tensor) -> Result<Tensor> {
        let embedding_output = self.embeddings.forward(input_ids)?;

        // 將 2D 的 attention_mask (batch_size, seq_len) 擴展為 4D (batch_size, 1, 1, seq_len)，
        // 以便它能被正確地廣播 (broadcast) 到注意力分數張量 (batch_size, num_heads, seq_len, seq_len) 上。
        let extended_attention_mask = attention_mask.unsqueeze(1)?.unsqueeze(2)?;
        let sequence_output = self
            .transformer
            .forward(&embedding_output, &extended_attention_mask)?;
        Ok(sequence_output)
    }
}

pub struct DistilBertForMaskedLM {
    pub bert: DistilBertModel,
    cls: DistilBertOnlyMLMHead,
}

impl DistilBertForMaskedLM {
    pub fn load(vb: VarBuilder, config: &DistilBertConfig) -> Result<Self> {
        let bert = DistilBertModel::load(vb.pp("distilbert"), config)?;
        let cls = DistilBertOnlyMLMHead::load(vb.clone(), config)?;
        Ok(Self { bert, cls })
    }

    pub fn forward(&self, input_ids: &Tensor, attention_mask: &Tensor) -> Result<Tensor> {
        let sequence_output = self.bert.forward(input_ids, attention_mask)?;
        self.cls.forward(&sequence_output)
    }
}
