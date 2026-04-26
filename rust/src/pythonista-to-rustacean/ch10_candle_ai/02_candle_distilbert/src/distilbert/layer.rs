//!
//! # Transformer 區塊與前饋網路
//!
//! 實現 Transformer 的核心區塊，包含注意力層和 FFN 兩部分。
//! 每個區塊包含：自注意力、残差連接與 LayerNorm、以及 FFN 結構。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! |殘差連接 | `output = attention + input` | `attention_output.broadcast_add(hidden_states)` |
//! |鏈式呼叫 | `x.apply(lin1).apply(activation).apply(lin2)` | `x.apply(&lin1)?.apply(&activation)?.apply(&lin2)` |
//! |停用命名規範 | `# noqa: N815` | `#[allow(clippy::upper_case_acronyms)]` |
//!
//! ## 關鍵技法
//!
//! - `.apply()`：Module trait 的語法糖， equivalent to `.forward()`
//! - `#[allow(clippy::upper_case_acronyms)]`：FFN 是標準縮寫，保持領域可讀性
//! - `broadcast_add`：自動廣播殘差連接，處理維度相容性
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch10_candle_ai/02_candle_distilbert
//! cargo build --release
//! ```
//!
use candle_core::{Result, Tensor};
use candle_nn::{Linear, Module, VarBuilder};

use super::attention::DistilBertSelfAttention;
use super::config::DistilBertConfig;
use super::nn::{HiddenActLayer, LayerNorm, layer_norm, linear};

// 停用 upper_case_acronyms 規則。
// FFN 是 "Feed-Forward Network" 的標準縮寫。
// 若依照 Clippy 建議改為 `Ffn`，反而會降低領域內開發者的可讀性。
#[allow(clippy::upper_case_acronyms)]
pub struct FFN {
    lin1: Linear,
    lin2: Linear,
    activation: HiddenActLayer,
}

impl FFN {
    pub fn load(vb: VarBuilder, config: &DistilBertConfig) -> Result<Self> {
        let lin1 = linear(config.dim, config.hidden_dim, vb.pp("lin1"))?;
        let lin2 = linear(config.hidden_dim, config.dim, vb.pp("lin2"))?;
        Ok(Self {
            lin1,
            lin2,
            activation: HiddenActLayer::new(config.activation),
        })
    }
}

impl Module for FFN {
    fn forward(&self, hidden_states: &Tensor) -> Result<Tensor> {
        // tensor.apply(module) 是一個語法糖，本質上等同於 module.forward(tensor)
        hidden_states
            .apply(&self.lin1)?
            .apply(&self.activation)?
            .apply(&self.lin2)
    }
}

pub struct TransformerBlock {
    attention: DistilBertSelfAttention,
    sa_layer_norm: LayerNorm,
    ffn: FFN,
    output_layer_norm: LayerNorm,
}

impl TransformerBlock {
    pub fn load(vb: VarBuilder, config: &DistilBertConfig) -> Result<Self> {
        let attention = DistilBertSelfAttention::load(vb.pp("attention"), config)?;
        let sa_layer_norm = layer_norm(config.dim, 1e-12, vb.pp("sa_layer_norm"))?;
        let ffn = FFN::load(vb.pp("ffn"), config)?;
        let output_layer_norm = layer_norm(config.dim, 1e-12, vb.pp("output_layer_norm"))?;
        Ok(Self {
            attention,
            sa_layer_norm,
            ffn,
            output_layer_norm,
        })
    }

    pub fn forward(&self, hidden_states: &Tensor, attention_mask: &Tensor) -> Result<Tensor> {
        let attention_output = self.attention.forward(hidden_states, attention_mask)?;
        let attention_output = attention_output.broadcast_add(hidden_states)?;
        let attention_output = self.sa_layer_norm.forward(&attention_output)?;

        let ffn_output = self.ffn.forward(&attention_output)?;
        let ffn_output = (ffn_output + attention_output)?;
        let output = self.output_layer_norm.forward(&ffn_output)?;

        Ok(output)
    }
}
