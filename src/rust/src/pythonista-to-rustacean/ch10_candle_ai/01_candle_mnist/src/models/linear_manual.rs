//! 這個模組定義了一個用於 MNIST 分類的兩層全連接神經網路。
//!
//! 特別之處在於，此處的 `Linear` 層是手動建立的，僅使用 `candle-core` 的 `Tensor`
//! 來實作前向傳播邏輯。這有助於理解線性層的內部運作機制。

use candle_core::{Result, Tensor};
use candle_nn::VarBuilder;

// --- 結構體定義區 ---

/// 手動實作的線性層。
///
/// 包含一個權重矩陣和一個偏差項向量，並手動定義了前向傳播的矩陣運算。
pub struct Linear {
    weight: Tensor,
    bias: Tensor,
}

impl Linear {
    /// 執行線性層的前向傳播。
    ///
    /// 公式為 `output = input * W^T + b`。
    pub fn forward(&self, input: &Tensor) -> Result<Tensor> {
        // `input` 與權重矩陣的轉置 (`weight.t()`) 進行矩陣乘法。
        let weighted_sum = input.matmul(&self.weight.t()?)?;
        // 使用廣播 (broadcast) 將偏差項向量加到每一個樣本上。
        let output = weighted_sum.broadcast_add(&self.bias)?;
        Ok(output)
    }
}

/// 一個簡單的雙層神經網路，用於 MNIST 手寫數字分類。
///
/// ## 網路架構
/// 1. 輸入層 (784 個節點)
/// 2. 隱藏層 (100 個節點) + ReLU 激活
/// 3. 輸出層 (10 個節點，代表 0-9 的 logits)
pub struct MnistClassifier {
    hidden_layer: Linear,
    output_layer: Linear,
}

impl MnistClassifier {
    /// 創建一個新的 `MnistClassifier` 模型。
    ///
    /// 這個函式會使用 `VarBuilder` 來初始化模型所需的所有可訓練參數
    /// (隱藏層與輸出層的權重和偏差)。
    pub fn new(var_builder: VarBuilder) -> Result<Self> {
        const INPUT_SIZE: usize = 28 * 28; // MNIST 圖片攤平後的大小
        const HIDDEN_SIZE: usize = 100; // 隱藏層的神經元數量
        const NUM_CLASSES: usize = 10; // 最終分類的類別數 (0-9)

        // 創建隱藏層：輸入維度 784，輸出維度 100。
        let hidden_layer = create_linear_layer(var_builder.pp("hidden"), INPUT_SIZE, HIDDEN_SIZE)?;
        // 創建輸出層：輸入維度 100，輸出維度 10。
        let output_layer = create_linear_layer(var_builder.pp("output"), HIDDEN_SIZE, NUM_CLASSES)?;

        Ok(Self {
            hidden_layer,
            output_layer,
        })
    }

    /// 定義模型的前向傳播路徑。
    pub fn forward(&self, image: &Tensor) -> Result<Tensor> {
        // 步驟 1: 輸入通過隱藏層。
        // Shape: (batch_size, 784) -> (batch_size, 100)
        let hidden_pre_activation = self.hidden_layer.forward(image)?;

        // 步驟 2: 應用 ReLU 激活函數，引入非線性。
        // Shape 保持不變: (batch_size, 100)
        let hidden_activated = hidden_pre_activation.relu()?;

        // 步驟 3: 激活後的結果通過輸出層，得到最終的 logits。
        // Shape: (batch_size, 100) -> (batch_size, 10)
        let logits = self.output_layer.forward(&hidden_activated)?;

        Ok(logits)
    }
}

// --- 內部輔助函式區 ---

/// 一個工廠函式，用於創建並初始化一個手動 `Linear` 層。
fn create_linear_layer(
    var_builder: VarBuilder,
    input_features: usize,
    output_features: usize,
) -> Result<Linear> {
    // 使用 Kaiming (He) Normal 初始化權重矩陣。
    // 這種初始化方法對於使用 ReLU 啟動函數的網路特別有效，有助於緩解梯度消失/爆炸問題。
    let weight_matrix = var_builder.get_with_hints(
        (output_features, input_features),
        "weight",
        candle_nn::init::DEFAULT_KAIMING_NORMAL,
    )?;

    // 根據 Kaiming Uniform 的思想計算偏差項的初始化邊界。
    let bias_init_bound = 1.0 / (input_features as f64).sqrt();
    // 使用均勻分佈 (Uniform) 初始化偏差項向量。
    let bias_vector = var_builder.get_with_hints(
        output_features,
        "bias", // 參數名稱
        candle_nn::Init::Uniform {
            lo: -bias_init_bound,
            up: bias_init_bound,
        },
    )?;

    Ok(Linear {
        weight: weight_matrix,
        bias: bias_vector,
    })
}

impl crate::training::Model for MnistClassifier {
    fn forward(&self, xs: &Tensor) -> anyhow::Result<Tensor> {
        self.forward(xs)
            .map_err(|e| anyhow::anyhow!("模型前向傳播失敗: {}", e))
    }
}
