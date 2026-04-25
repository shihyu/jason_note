//!
//! # 基礎神經網路元件
//!
//! 提供 Embedding、Linear、LayerNorm 等基礎元件的建構函式。
//! 同時實作自訂的 LayerNorm 和 HiddenActLayer，確保與 PyTorch 模型權重的完全相容。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! | 建立 Embedding | `nn.Embedding(vocab, dim)` + load weights | `vb.get((vocab, dim), "weight")?` + `Embedding::new()` |
//! | 建立 Linear | `nn.Linear(in, out)` + load weights | `vb.get((out, in), "weight")?` + `Linear::new()` |
//! | LayerNorm forward | `(x - mean) / sqrt(var + eps) * gamma + beta` | 手動實作完整標準化流程 |
//!
//! ## 關鍵技法
//!
//! - `vb.get()`：從 VarBuilder 載入權重張量
//! - 備援命名：嘗試 "weight"/"bias" 失敗後嘗試 "gamma"/"beta"
//! - 精度提升：F16/BF16 臨時轉 F32 計算，避免精度損失
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch10_candle_ai/02_candle_distilbert
//! cargo build --release
//! ```
//!
use candle_core::{DType, Result, Tensor};
use candle_nn::{Embedding, Linear, Module, VarBuilder};

use super::config::HiddenAct;

// --- Helpers ---

/// 從 VarBuilder 建立一個 Embedding 層。
pub fn embedding(vocab_size: usize, hidden_size: usize, vb: VarBuilder) -> Result<Embedding> {
    let embeddings = vb.get((vocab_size, hidden_size), "weight")?;
    Ok(Embedding::new(embeddings, hidden_size))
}

/// 從 VarBuilder 建立一個包含 bias 的 Linear 層。
pub fn linear(in_dim: usize, out_dim: usize, vb: VarBuilder) -> Result<Linear> {
    let weight = vb.get((out_dim, in_dim), "weight")?;
    let bias = vb.get(out_dim, "bias")?;
    Ok(Linear::new(weight, Some(bias)))
}

// --- LayerNorm ---

/// LayerNorm 層的結構，包含可學習的權重（gamma）、偏移（beta）以及 epsilon 值。
pub struct LayerNorm {
    /// 可學習的縮放參數 (gamma)。
    weight: Tensor,
    /// 可學習的偏移參數 (beta)。
    bias: Tensor,
    /// 為了數值穩定而加入分母的一個極小值。
    eps: f64,
}

impl LayerNorm {
    /// 建立一個新的 LayerNorm 實例。
    pub fn new(weight: Tensor, bias: Tensor, eps: f64) -> Self {
        Self { weight, bias, eps }
    }

    /// Layer Normalization 的前向傳播計算。
    ///
    /// 這個函數會沿著最後一個維度（通常是 `hidden_size` 或特徵維度）對輸入張量 `x` 進行標準化，
    /// 然後再應用可學習的縮放（weight/gamma）和偏移（bias/beta）。
    ///
    /// 公式為： y = (x - E[x]) / sqrt(Var[x] + eps) * gamma + beta
    ///
    /// # Arguments
    ///
    /// * `x`: 輸入張量，形狀通常為 `(batch_size, seq_len, hidden_size)`。
    pub fn forward(&self, x: &Tensor) -> Result<Tensor> {
        let x_dtype = x.dtype();

        // 為了計算精度，臨時將 F16/BF16 提升至 F32 進行計算。
        let internal_dtype = match x_dtype {
            DType::F16 | DType::BF16 => DType::F32,
            dtype => dtype,
        };

        // 獲取輸入張量 x 的維度，通常是 (批次大小, 序列長度, 隱藏層大小)。
        let (_bsize, _seq_len, hidden_size) = x.dims3()?;
        let x = x.to_dtype(internal_dtype)?;

        // --- 開始計算平均值 (Mean) ---
        // 1. `x.sum_keepdim(2)?`: 沿著最後一個維度（維度索引為 2，即 hidden_size 維度）對所有元素求和。
        //    `keepdim` 表示保持維度，結果張量的形狀會是 (bsize, seq_len, 1)。
        // 2. `/ hidden_size as f64`: 將總和除以該維度的元素數量 (hidden_size)，得到平均值。
        let mean_x = (x.sum_keepdim(2)? / hidden_size as f64)?;

        // --- 計算 x 減去平均值 (x - E[x]) ---
        // `broadcast_sub` 會自動將 mean_x (形狀為 bsize, seq_len, 1) 廣播到
        // 與 x 相同的形狀 (bsize, seq_len, hidden_size)，然後執行逐元素的減法。
        let x = x.broadcast_sub(&mean_x)?;

        // --- 開始計算變異數 (Variance) ---
        // 1. `x.sqr()?`: 將上一步得到的 (x - E[x]) 張量中的每個元素進行平方。
        // 2. `.sum_keepdim(2)?`: 同樣沿著最後一個維度求和。
        // 3. `/ hidden_size as f64`: 將總和除以 hidden_size，得到變異數。
        let norm_x = (x.sqr()?.sum_keepdim(2)? / hidden_size as f64)?;

        // --- 執行標準化 (Normalization) ---
        // 這是 LayerNorm 的核心步驟：(x - E[x]) / sqrt(Var[x] + eps)
        // 1. `(norm_x + self.eps)?`: 將變異數加上一個極小的數 self.eps，防止開根號時分母為零。
        // 2. `.sqrt()?`: 對 (變異數 + eps) 取平方根，得到標準差。
        // 3. `x.broadcast_div(...)`: 將 (x - E[x]) 除以剛算出的標準差。
        //    標準差張量會被廣播以匹配 x 的形狀。
        let x_normed = x.broadcast_div(&(norm_x + self.eps)?.sqrt()?)?;

        // --- 進行縮放 (Scale) 與偏移 (Shift)，並轉回原始資料型別 ---
        let x = x_normed
            .to_dtype(x_dtype)?
            .broadcast_mul(&self.weight)?
            .broadcast_add(&self.bias)?;

        Ok(x)
    }
}

/// 從 VarBuilder 建立一個 LayerNorm 層。
///
/// 此函數會嘗試從權重中載入 `weight` 和 `bias`。如果失敗，
/// 則會嘗試備用的 `gamma` 和 `beta` 名稱，以提高模型相容性。
///
/// # Arguments
///
/// * `size`: 正規化維度的大小，通常等於 `hidden_size`。
/// * `eps`: 用於維持數值穩定性的 epsilon。
/// * `vb`: 用於載入權重張量的 `VarBuilder`。
pub fn layer_norm(size: usize, eps: f64, vb: VarBuilder) -> Result<LayerNorm> {
    // 嘗試載入 "weight" 和 "bias"
    let (weight, bias) = match (vb.get(size, "weight"), vb.get(size, "bias")) {
        // 如果成功，直接使用
        (Ok(weight), Ok(bias)) => (weight, bias),
        // 如果失敗，嘗試備用名稱 "gamma" 和 "beta"
        (Err(err), _) | (_, Err(err)) => {
            if let (Ok(weight), Ok(bias)) = (vb.get(size, "gamma"), vb.get(size, "beta")) {
                (weight, bias)
            } else {
                // 如果兩種命名都失敗，則返回最初的錯誤
                return Err(err);
            }
        }
    };

    Ok(LayerNorm::new(weight, bias, eps))
}

// --- Activation ---
pub struct HiddenActLayer {
    act: HiddenAct,
}

impl HiddenActLayer {
    pub fn new(act: HiddenAct) -> Self {
        Self { act }
    }
}

impl Module for HiddenActLayer {
    fn forward(&self, xs: &Tensor) -> Result<Tensor> {
        match self.act {
            HiddenAct::Gelu => xs.gelu(),
            HiddenAct::Relu => xs.relu(),
        }
    }
}
