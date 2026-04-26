//!
//! # 張量工具函式
//!
//! 提供常用的張量操作工具，如條件式填充（masked_fill）。
//! 主要用於實現注意力機制中的遮罩操作，將某些位置的值替換為指定內容（如 -inf）。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! | 條件填充 | `torch.where(mask, fill_value, input)` | `mask.where_cond(&value_if_true, input)` |
//! | 建立填充張量 | `torch.full_like(input, fill_value)` | `Tensor::new(fill_value, device)?.broadcast_as(shape)` |
//! | 廣播機制 | 自動廣播至相同形狀 | `broadcast_as()` 明確指定目標形狀 |
//!
//! ## 關鍵技法
//!
//! - `where_cond`：Candle 的條件選擇函式，類似 `torch.where`
//! - `broadcast_as`：將張量廣播到目標形狀
//! - 注意力遮罩：1=保留, 0=遮蔽 的慣例轉換為 filled_value=fill_value
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch10_candle_ai/02_candle_distilbert
//! cargo build --release
//! ```
//!
use candle_core::{Result, Tensor};

/// 對張量進行條件式填充，常用於實現注意力遮罩。
///
/// 這個函式的功能類似於 PyTorch 的 `torch.where(condition, value_if_true, value_if_false)`。
/// 在 DistilBERT 的注意力機制中，此函式所達成的「效果」等同於 PyTorch 版本中常見的「加法遮罩」慣例：
/// `attn_weights = attn_weights + attention_mask`
///
/// PyTorch 的作法是將 `attention_mask` 預處理成一個包含 0 和一個極大負數（如 -10000.0）的張量，
/// 然後直接與注意力分數相加。
///
/// 而此處的作法更為明確：提供一個布林遮罩，並指定在遮罩為 true 的位置上要填充的值。
///
/// # Arguments
/// * `input`: &Tensor - 原始輸入張量，例如注意力分數。當遮罩條件為 false 時，會保留此張量的值。
/// * `mask`: &Tensor - 一個布林（或 0/1）張量，`true` 的位置代表需要被替換。
/// * `fill_value`: f32 - 當遮罩條件為 `true` 時，要用來填充的純量值，例如 `f32::NEG_INFINITY`。
pub fn masked_fill(input: &Tensor, mask: &Tensor, fill_value: f32) -> Result<Tensor> {
    // 建立一個與 input 形狀相同，但所有元素皆為 fill_value 的張量。
    // 這是 `where_cond` 在條件為 true 時需要取值的來源。
    let value_if_true = Tensor::new(fill_value, input.device())?.broadcast_as(input.shape())?;

    // `where_cond` 的邏輯是：`mask.where_cond(tensor_if_true, tensor_if_false)`
    // 在這裡，如果 mask 為 true，就取 `value_if_true` 的值（即我們的 fill_value）；
    // 否則，就取 `input` 的原始值。
    let result = mask.where_cond(&value_if_true, input)?;

    Ok(result)
}
