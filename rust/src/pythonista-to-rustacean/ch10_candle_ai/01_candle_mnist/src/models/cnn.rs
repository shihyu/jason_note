//! 這個模組實作了一個 LeNet-5 風格的卷積神經網路 (CNN)。
//!
//! 此模型專為圖像分類任務設計，特別是像 MNIST 這樣的數據集。
//! 它利用 `candle_nn` 提供的 `Conv2d`、`Linear` 等高階模組來建構網路架構。

use candle_core::{Module, Result, Tensor};
use candle_nn::{Conv2d, Conv2dConfig, Linear, VarBuilder, conv2d, linear};

// --- 結構體定義區 ---

/// LeNet-5 風格的卷積神經網路模型，用於 MNIST 分類任務。
///
/// ## 架構
/// 1. **Conv Block 1**: `Conv2d` (in=1, out=32, kernel=5) -> `ReLU` -> `MaxPool2d`(2)
/// 2. **Conv Block 2**: `Conv2d` (in=32, out=64, kernel=5) -> `ReLU` -> `MaxPool2d`(2)
/// 3. **Flatten**
/// 4. **FC Block 1**: `Linear` (in=1024, out=1024) -> `ReLU`
/// 5. **FC Block 2**: `Linear` (in=1024, out=10) -> Logits
#[derive(Debug)]
pub struct MnistClassifierCNN {
    conv1: Conv2d,
    conv2: Conv2d,
    fc1: Linear,
    fc2: Linear,
}

impl MnistClassifierCNN {
    /// 創建一個新的 CNN 模型。
    ///
    /// 此函式負責定義並初始化網路中的所有層。
    pub fn new(vb: VarBuilder) -> Result<Self> {
        // 定義卷積層共享的設定：步長為 1，無填充。
        let conv_config = Conv2dConfig {
            stride: 1,
            padding: 0,
            ..Default::default()
        };

        // 第一層卷積：1 個輸入通道 (灰階) -> 32 個輸出通道，5x5 卷積核。
        let conv1 = conv2d(1, 32, 5, conv_config, vb.pp("conv1"))?;
        // 第二層卷積：32 個輸入通道 -> 64 個輸出通道，5x5 卷積核。
        let conv2 = conv2d(32, 64, 5, conv_config, vb.pp("conv2"))?;

        // 第一層全連接層。
        // 輸入維度計算：
        // 原始圖片 28x28
        // 經過 conv1 (5x5, stride 1): 28-5+1 = 24 -> 24x24
        // 經過 max_pool(2): 24/2 = 12 -> 12x12
        // 經過 conv2 (5x5, stride 1): 12-5+1 = 8 -> 8x8
        // 經過 max_pool(2): 8/2 = 4 -> 4x4
        // 最終特徵圖大小為 64 (通道數) * 4 * 4 = 1024
        let fc1 = linear(1024, 1024, vb.pp("fc1"))?;

        // 第二層全連接層 (輸出層)。
        // 將 1024 維特徵向量映射到 10 個分類的 logits。
        let fc2 = linear(1024, 10, vb.pp("fc2"))?;

        Ok(Self {
            conv1,
            conv2,
            fc1,
            fc2,
        })
    }
}

impl Module for MnistClassifierCNN {
    /// 定義 CNN 的前向傳播路徑。
    fn forward(&self, xs: &Tensor) -> Result<Tensor> {
        let (b_sz, _) = xs.dims2()?;

        // 1. 輸入張量塑形
        // 原始的 `xs` 是一個扁平化的張量，需要將其重塑為卷積層期望的 4D 張量格式。
        // Shape: (batch_size, 784) -> (batch_size, 1, 28, 28)
        // [批次大小, 輸入通道, 高度, 寬度]
        let xs = xs.reshape((b_sz, 1, 28, 28))?;

        // 2. 第一個卷積與池化區塊
        // Shape: (b_sz, 1, 28, 28) -> Conv2d -> (b_sz, 32, 24, 24) -> ReLU -> MaxPool2d -> (b_sz, 32, 12, 12)
        let xs = self.conv1.forward(&xs)?.relu()?.max_pool2d(2)?;

        // 3. 第二個卷積與池化區塊
        // Shape: (b_sz, 32, 12, 12) -> Conv2d -> (b_sz, 64, 8, 8) -> ReLU -> MaxPool2d -> (b_sz, 64, 4, 4)
        let xs = self.conv2.forward(&xs)?.relu()?.max_pool2d(2)?;

        // 4. 展平 (Flatten)
        // 為了將特徵圖傳遞給全連接層，需要將其從 4D 張量展平為 2D 張量。
        // `flatten_from(1)` 會保持第 0 維 (批次大小) 不變，將後續所有維度展平。
        // Shape: (b_sz, 64, 4, 4) -> (b_sz, 1024)
        let xs = xs.flatten_from(1)?;

        // 5. 第一個全連接層
        // Shape: (b_sz, 1024) -> (b_sz, 1024)
        let xs = self.fc1.forward(&xs)?.relu()?;

        // 6. 第二個全連接層 (輸出層)
        // Shape: (b_sz, 1024) -> (b_sz, 10)
        let xs = self.fc2.forward(&xs)?;

        Ok(xs)
    }
}
