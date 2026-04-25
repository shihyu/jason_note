//!
//! # Multi-Head Self-Attention
//!
//! 實現 DistilBERT 的自注意力機制，透過 Q/K/V 線性投影將輸入分割成多個注意力頭，
//! 計算注意力分數並對值進行加權求和，最終合併多頭結果輸出。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! | 建立線性層 | `nn.Linear(dim, dim)` | `linear(dim, dim, vb.pp("q_lin"))` |
//! | 分割多頭 | `.view(*hidden_shape).transpose(1, 2)` | `reshape(shape)?.transpose(1, 2)?` |
//! | 計算注意力 | `torch.matmul(query, key.transpose(-1, -2))` | `query_layer.matmul(&key_layer.transpose(2, 3)?)` |
//! | 遮罩填充 | `attn_weights + attention_mask` | `masked_fill(&scores, &fill_mask, f32::NEG_INFINITY)` |
//!
//! ## 關鍵技法
//!
//! - `vb.pp("name")`：Path helper，幫助組織變量命名空間
//! - `broadcast_as`：自動將小型張量廣播到目標形狀
//! - `.contiguous()`：確保張量在記憶體中連續布局，提升運算效率
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch10_candle_ai/02_candle_distilbert
//! cargo build --release
//! ```
//!
use core::f32;

use candle_core::{Result, Tensor};
use candle_nn::{Linear, Module, VarBuilder};

use super::config::DistilBertConfig;
use super::nn::linear;
use super::utils::masked_fill;

pub struct DistilBertSelfAttention {
    q_lin: Linear,
    k_lin: Linear,
    v_lin: Linear,
    out_lin: Linear,
    n_heads: usize,
    attention_head_size: usize,
}

impl DistilBertSelfAttention {
    pub fn load(vb: VarBuilder, config: &DistilBertConfig) -> Result<Self> {
        // PyTorch: self.attention_head_size = self.dim // self.n_heads
        // usize / usize 等價於 Python 的 self.dim // self.n_heads
        let attention_head_size = config.dim / config.n_heads;
        // 雖然數值上等於 `config.dim`，但使用 `all_head_size` 這個名稱能更清晰地傳達意圖：此維度是用於容納所有注意力頭合併後的結果。
        // 這對應了 PyTorch 中 Q/K/V 線性層的 out_features=config.dim
        let all_head_size = config.n_heads * attention_head_size;
        let dim = config.dim;
        // PyTorch: self.q_lin = nn.Linear(in_features=config.dim, out_features=config.dim)
        let q_lin = linear(dim, all_head_size, vb.pp("q_lin"))?;
        // PyTorch: self.v_lin = nn.Linear(in_features=config.dim, out_features=config.dim)
        let k_lin = linear(dim, all_head_size, vb.pp("k_lin"))?;
        // PyTorch: self.k_lin = nn.Linear(in_features=config.dim, out_features=config.dim)
        let v_lin = linear(dim, all_head_size, vb.pp("v_lin"))?;
        // PyTorch: self.out_lin = nn.Linear(in_features=config.dim, out_features=config.dim)
        let out_lin = linear(all_head_size, dim, vb.pp("out_lin"))?;

        Ok(Self {
            q_lin,
            k_lin,
            v_lin,
            out_lin,
            n_heads: config.n_heads,
            attention_head_size,
        })
    }

    pub fn forward(&self, hidden_states: &Tensor, attention_mask: &Tensor) -> Result<Tensor> {
        // --- 準備階段 ---
        // PyTorch: input_shape = hidden_states.shape[:-1]
        let (bsize, q_length, _dim) = hidden_states.dims3()?;
        let dim_per_head = self.attention_head_size;
        // PyTorch: hidden_shape = (*input_shape, -1, self.attention_head_size)
        let hidden_shape = (bsize, q_length, self.n_heads, dim_per_head);

        // --- 1. Q, K, V 的線性投影 ---
        // PyTorch: query_layer = self.q_lin(hidden_states)
        let query_layer = self.q_lin.forward(hidden_states)?;
        // PyTorch: key_layer = self.k_lin(hidden_states)
        let key_layer = self.k_lin.forward(hidden_states)?;
        // PyTorch: value_layer = self.v_lin(hidden_states)
        let value_layer = self.v_lin.forward(hidden_states)?;

        // --- 2. 將 Q, K, V 分割成多個頭 ---
        // PyTorch: .view(*hidden_shape).transpose(1, 2)
        let query_layer = query_layer.reshape(hidden_shape)?.transpose(1, 2)?;
        let key_layer = key_layer.reshape(hidden_shape)?.transpose(1, 2)?;
        let value_layer = value_layer.reshape(hidden_shape)?.transpose(1, 2)?;

        // --- 3. 計算注意力分數 ---
        let context = {
            // --- 對應 eager_attention_forward ---
            // PyTorch (eager): `... * scaling` (註: 此處先縮放 Q)
            let query_layer = (query_layer / (dim_per_head as f64).sqrt())?;

            // PyTorch (eager): torch.matmul(query, key.transpose(-1, -2))
            // (註: key_layer 經 transpose 後非連續，.contiguous() 確保記憶體佈局)
            let scores = query_layer.matmul(&key_layer.transpose(2, 3)?.contiguous()?)?;

            // PyTorch (eager): attn_weights + attention_mask (註: self-attention 場景省略 slicing)
            // `attention_mask` 的慣例是 1 = 保留, 0 = 遮蔽。
            // 我們的 `masked_fill` 函式需要一個「填充遮罩」，其中 1 = 填充。
            // 所以，我們在這裡進行邏輯轉換：找到 `attention_mask` 中為 0 的位置。
            let fill_mask = attention_mask.eq(0u8)?.broadcast_as(scores.shape())?;
            // 現在 `fill_mask` 中為 1 的位置，就是原始 `attention_mask` 中為 0 的位置。
            // 我們用 -inf 來填充這些位置。

            let scores = masked_fill(&scores, &fill_mask, f32::NEG_INFINITY)?;

            // PyTorch (eager): nn.functional.softmax(attn_weights, dim=-1)
            let weights = candle_nn::ops::softmax(&scores, candle_core::D::Minus1)?;
            // PyTorch (eager): nn.functional.dropout(...) (註: 推論模式省略)

            // PyTorch (eager): torch.matmul(attn_weights, value)
            // (註: value_layer 經 transpose 後非連續，.contiguous() 確保記憶體佈局)
            let context = weights.matmul(&value_layer.contiguous()?)?;

            // PyTorch (eager): attn_output.transpose(1, 2).contiguous()
            context.transpose(1, 2)?.contiguous()?
        };

        // --- 4. 合併多頭並投影  ---
        // PyTorch: attn_output.reshape(*input_shape, -1).contiguous()
        let context = context
            .reshape((bsize, q_length, self.n_heads * dim_per_head))?
            .contiguous()?;
        // PyTorch: self.out_lin(attn_output)
        let context = self.out_lin.forward(&context)?;

        Ok(context)
    }
}
