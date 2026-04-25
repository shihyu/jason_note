//!
//! # Masked Language Model 預測頭
//!
//! 實現 MLM 任務的預測頭，包含特徵轉換層 (transform) 和解碼層 (decoder)。
//! 負責將 Transformer 的輸出投影回詞彙表空間，產生每個位置每個詞彙的分數。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! | 預測頭結構 | `nn.Sequential(dense, activation, layer_norm)` | 多struct實作 + Module trait |
//! | 權重綑綁 | `tie_weights()` | 手動從 embeddings 載入權重並分開 bias |
//! | 投影到詞彙 | `nn.Linear(dim, vocab_size)` | `Linear::new(weight, Some(bias))` |
//!
//! ## 關鍵技法
//!
//! - `vb.pp("distilbert.embeddings.word_embeddings")`：跨模組引用權重
//! - `candle_nn::init::DEFAULT_KAIMING_NORMAL`：初始化策略
//! - `Module` trait：統一套件 forward 行為的標準介面
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

use super::config::DistilBertConfig;
use super::nn::{HiddenActLayer, LayerNorm, layer_norm, linear};

// --- 1. 特徵精煉器 ---
// 對應 PyTorch DistilBertForMaskedLM 中的 self.vocab_transform, self.activation, self.vocab_layer_norm。
// 負責在投影到詞彙表前，對 Transformer 的輸出進行一次特徵轉換。
struct DistilBertPredictionHeadTransform {
    dense: Linear,
    activation: HiddenActLayer,
    layer_norm: LayerNorm,
}

impl DistilBertPredictionHeadTransform {
    fn load(vb: VarBuilder, config: &DistilBertConfig) -> Result<Self> {
        // PyTorch: self.vocab_transform = nn.Linear(config.dim, config.dim)
        let dense = linear(config.dim, config.dim, vb.pp("vocab_transform"))?;
        // PyTorch: self.activation = get_activation(config.activation)
        let activation = HiddenActLayer::new(config.activation);
        // PyTorch: self.vocab_layer_norm = nn.LayerNorm(config.dim, eps=1e-12)
        let layer_norm = layer_norm(config.dim, 1e-12, vb.pp("vocab_layer_norm"))?;
        Ok(Self {
            dense,
            activation,
            layer_norm,
        })
    }
}

impl Module for DistilBertPredictionHeadTransform {
    fn forward(&self, hidden_states: &Tensor) -> Result<Tensor> {
        // 執行 `dense` -> `activation` -> `layer_norm` 的轉換流程。
        // PyTorch: prediction_logits = self.vocab_transform(hidden_states)
        // PyTorch: prediction_logits = self.activation(prediction_logits)
        let hidden_states = self
            .activation
            .forward(&self.dense.forward(hidden_states)?)?;
        // PyTorch: prediction_logits = self.vocab_layer_norm(prediction_logits)
        self.layer_norm.forward(&hidden_states)
    }
}

// --- 2. 預測產生器 ---
// 包含特徵精煉器，並加上最終的解碼/投影層 (decoder)，產生詞彙表分數。
// 對應 PyTorch 中的 self.vocab_projector 以及其前面的 transform 層。
pub struct DistilBertLMPredictionHead {
    transform: DistilBertPredictionHeadTransform,
    decoder: Linear,
}

impl DistilBertLMPredictionHead {
    pub fn load(vb: VarBuilder, config: &DistilBertConfig) -> Result<Self> {
        // 首先載入特徵精煉器。
        let transform = DistilBertPredictionHeadTransform::load(vb.clone(), config)?;

        // --- 處理權重綑綁 (Weight Tying) ---
        // 在許多模型中 (包含我們將要使用的 distil_bert_uncased)，為了節省參數和提升效能，
        // 輸出投影層的權重 (weight) 與詞嵌入層 (word embeddings) 的權重是共享的，
        // 但 bias 是獨立的。因此這裡需要分開載入。

        // 從詞嵌入層的路徑載入權重。
        let vocab_projector_weight_vb = vb.pp("distilbert.embeddings.word_embeddings");
        let init_ws = candle_nn::init::DEFAULT_KAIMING_NORMAL;
        let ws = vocab_projector_weight_vb.get_with_hints(
            (config.vocab_size, config.dim),
            "weight",
            init_ws,
        )?;

        // bias 則是獨立的，從 'vocab_projector' 路徑載入。
        let bound = 1. / (config.dim as f64).sqrt();
        let init_bs = candle_nn::Init::Uniform {
            lo: -bound,
            up: bound,
        };
        let vocab_projector_bias_vb = vb.pp("vocab_projector");
        let bs = vocab_projector_bias_vb.get_with_hints(config.vocab_size, "bias", init_bs)?;

        // 手動組合權重與偏置，建立最終的解碼/投影層。
        let decoder = Linear::new(ws, Some(bs));

        Ok(Self { transform, decoder })
    }
}

impl Module for DistilBertLMPredictionHead {
    fn forward(&self, hidden_states: &Tensor) -> Result<Tensor> {
        // 先進行特徵轉換，再通過解碼層投影到詞彙表維度，產生最終的 logits。
        self.decoder
            .forward(&self.transform.forward(hidden_states)?)
    }
}

// --- 3. 任務封裝器 ---
// 這是 MLM 任務的「頭 (Head)」。
// 在架構上，它將所有預測相關的邏輯封裝起來，使整體模型結構更清晰、更模組化。
// 這個結構的角色由 PyTorch 中的 `DistilBertForMaskedLM` 類別本身來扮演。
pub struct DistilBertOnlyMLMHead {
    predictions: DistilBertLMPredictionHead,
}

impl DistilBertOnlyMLMHead {
    pub fn load(vb: VarBuilder, config: &DistilBertConfig) -> Result<Self> {
        // 載入包含轉換和投影邏輯的預測產生器。
        let predictions = DistilBertLMPredictionHead::load(vb.clone(), config)?;
        Ok(Self { predictions })
    }
}

impl Module for DistilBertOnlyMLMHead {
    fn forward(&self, sequence_output: &Tensor) -> Result<Tensor> {
        // 直接呼叫內層的 forward，執行完整的預測流程。
        self.predictions.forward(sequence_output)
    }
}
