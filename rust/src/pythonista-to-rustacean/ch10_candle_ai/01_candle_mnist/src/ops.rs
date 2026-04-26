//! 這個模組提供了手動實作的神經網路核心運算（Operations）。
//!
//! 這裡的函式，例如 `log_softmax` 和 `nll_loss`，是為了教學目的而存在，
//! 用於深入理解這些運算背後的數學原理與數值穩定性技巧。
//! 在實際應用中，通常建議使用 `candle_nn::loss` 中經過優化且更穩健的版本。

use candle_core::{D, Result, Tensor};

// --- 核心運算函式區 ---

/// 手動實作 Log Softmax 函數。
///
/// Log Softmax 是分類任務中常用的激活函數，它將 logits 轉換為對數機率。
/// 為了數值穩定性，這個實作使用了 "log-sum-exp" 技巧。
/// 公式為： `log_softmax(x) = x - log(sum(exp(x)))`
pub fn log_softmax(xs: &Tensor, dim: D) -> Result<Tensor> {
    // 步驟 1: 找出每個樣本 logits 中的最大值。
    let max = xs.max_keepdim(dim)?;
    // 步驟 2: 從原始 logits 中減去最大值。
    // 這個技巧可以防止 `exp()` 因輸入過大而溢位 (overflow)，同時不改變最終結果。
    let a = xs.broadcast_sub(&max)?;
    // 步驟 3: 計算 e 的次方。
    let exp_a = a.exp()?;
    // 步驟 4: 沿著指定維度加總。
    let sum_exp_a = exp_a.sum_keepdim(dim)?;
    // 步驟 5: 取自然對數，並加回先前減去的最大值，得到 log-sum-exp 的結果。
    let log_sum_exp = sum_exp_a.log()?.broadcast_add(&max)?;
    // 步驟 6: 從原始 logits 減去 log-sum-exp，即為最終的 log probabilities。
    let log_probs = xs.broadcast_sub(&log_sum_exp)?;

    Ok(log_probs)
}

/// 手動實作 Negative Log Likelihood (NLL) 損失函數。
///
/// NLL Loss 用於多分類問題，它計算模型對於「正確答案」所預測的對數機率的負值。
/// 我們的目標是最小化這個損失，也就是最大化正確答案的對數機率。
pub fn nll_loss(log_probs: &Tensor, targets: &Tensor) -> Result<Tensor> {
    // 使用 `gather` 從 `log_probs` 張量中，根據 `targets` 的索引，挑選出對應的數值。
    // 這等同於 PyTorch/NumPy 中的 `log_probs[range(B), targets]` 操作。
    // `targets` 需要先擴展一個維度以符合 `gather` 的 API 要求。
    let gathered_log_probs = log_probs.gather(&targets.unsqueeze(1)?, 1)?.squeeze(1)?;

    // 計算所有樣本的負對數概似值的平均值，作為最終的損失。
    let loss = gathered_log_probs.neg()?.mean_all()?;
    Ok(loss)
}
