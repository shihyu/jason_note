//! 這個模組同樣定義了一個用於 MNIST 分類的兩層全連接神經網路。
//!
//! 與 `linear_manual` 不同，此版本使用了 `candle_nn` 提供的 `Linear` 結構體
//! 和 `Module` Trait。這展示了在 Candle 中建立模型的更常見、更簡潔的慣用方法。

use candle_core::{Result, Tensor};
use candle_nn::{Linear, Module, VarBuilder, linear};

// --- 結構體定義區 ---

/// 使用 `candle_nn::Linear` 的兩層神經網路分類器。
///
/// ## 網路架構
/// 1. `candle_nn::Linear` (784 -> 100)
/// 2. ReLU 激活
/// 3. `candle_nn::Linear` (100 -> 10)
pub struct MnistClassifier {
    hidden_layer: Linear,
    output_layer: Linear,
}

impl MnistClassifier {
    /// 創建一個新的 `MnistClassifier` 模型。
    ///
    /// `candle_nn::linear` 是一個輔助函式，它會自動處理權重和偏差的初始化，
    /// 使模型的建立過程更加簡潔。
    pub fn new(var_builder: VarBuilder) -> Result<Self> {
        const INPUT_SIZE: usize = 28 * 28;
        const HIDDEN_SIZE: usize = 100;
        const NUM_CLASSES: usize = 10;

        // 使用 `candle_nn::linear` 快速創建隱藏層。
        let hidden_layer = linear(INPUT_SIZE, HIDDEN_SIZE, var_builder.pp("hidden"))?;
        // 創建輸出層。
        let output_layer = linear(HIDDEN_SIZE, NUM_CLASSES, var_builder.pp("output"))?;

        Ok(Self {
            hidden_layer,
            output_layer,
        })
    }
}

// 實作 `Module` Trait 來定義模型的前向傳播邏輯。
// 這是在 Candle 中定義可重用模型組件的標準模式。
impl Module for MnistClassifier {
    fn forward(&self, image: &Tensor) -> Result<Tensor> {
        // 步驟 1: `candle_nn::Linear` 內部已封裝了 matmul 和 add bias 的邏輯。
        let hidden_pre_activation = self.hidden_layer.forward(image)?;
        // 步驟 2: 應用激活函數。
        let hidden_activated = hidden_pre_activation.relu()?;
        // 步驟 3: 通過輸出層得到 logits。
        let logits = self.output_layer.forward(&hidden_activated)?;
        Ok(logits)
    }
}
