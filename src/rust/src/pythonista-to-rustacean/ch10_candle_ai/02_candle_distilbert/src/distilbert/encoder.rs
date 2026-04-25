//!
//! # Transformer 編碼器
//!
//! 將多層 Transformer 區塊堆疊在一起，構成完整的編碼器主體。
//! 負責將嵌入層的輸出經過 N 層Transformer 區塊的變換，產生上下文相關的序列表示。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! | 堆疊多層 | `for layer in self.layers:` | `for layer_module in self.layers.iter()` |
//! | 建立多層模組 | `nn.ModuleList([...])` | `Vec<TransformerBlock>` |
//! | 逐一傳遞 hidden_states | `layer(hidden_states)` | `layer_module.forward(&hidden_states, ...)` |
//!
//! ## 關鍵技法
//!
//! - `vb.pp(&format!("layer.{index}"))`：動態路徑 helper，區分不同層的權重
//! - `map().collect()`：將迭代器結果收集為 Vec，優雅處理多層建立
//! - `Result<Vec<_>>`：利用 Rust 的錯誤傳播機制，任意一層失敗即返回錯誤
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch10_candle_ai/02_candle_distilbert
//! cargo build --release
//! ```
//!
use candle_core::{Result, Tensor};
use candle_nn::VarBuilder;

use super::config::DistilBertConfig;
use super::layer::TransformerBlock;

pub struct Transformer {
    pub layers: Vec<TransformerBlock>,
}

impl Transformer {
    pub fn load(vb: VarBuilder, config: &DistilBertConfig) -> Result<Self> {
        let layers = (0..config.n_layers)
            .map(|index| TransformerBlock::load(vb.pp(&format!("layer.{index}")), config))
            .collect::<Result<Vec<_>>>()?;

        Ok(Transformer { layers })
    }

    pub fn forward(&self, hidden_states: &Tensor, attention_mask: &Tensor) -> Result<Tensor> {
        let mut hidden_states = hidden_states.clone();
        for layer_module in self.layers.iter() {
            hidden_states = layer_module.forward(&hidden_states, attention_mask)?;
        }

        Ok(hidden_states)
    }
}
