//! # 神經網路模型定義模組
//!
//! 本模組定義了用於 MNIST 手寫數字分類的卷積神經網路模型。
//! 模型包含兩個卷積層、池化層、Dropout 層和兩個全連接層。
//!
//! ## 與其他模組的相依關係：
//! - `training.rs`: 使用本模組的 `Model` 和 `ModelConfig` 進行訓練
//! - `inference.rs`: 透過 `training.rs` 間接使用本模組進行推論
//! - `main.rs`: 透過 `training.rs` 間接使用 `ModelConfig` 配置模型參數

use burn::{
    nn::{
        Dropout, DropoutConfig, Linear, LinearConfig, Relu,
        conv::{Conv2d, Conv2dConfig},
        pool::{MaxPool2d, MaxPool2dConfig},
    },
    prelude::*,
};

/// 卷積神經網路模型結構定義
///
/// 這是一個用於 MNIST 手寫數字分類的卷積神經網路，架構如下：
/// 1. 兩個卷積層 (Conv2d) 用於特徵提取
/// 2. 兩個最大池化層 (MaxPool2d) 用於降維
/// 3. 兩個全連接層 (Linear) 用於分類
/// 4. Dropout 層用於防止過擬合
/// 5. ReLU 啟動函數用於非線性變換
///
/// ## 泛型參數
/// * `B`: 後端類型，必須實現 `Backend` trait
///   - 在訓練時使用 `Autodiff<Wgpu<f32, i32>>`
///   - 在推論時使用 `Wgpu<f32, i32>`
///
/// ## 使用者
/// - `training.rs` 中的 `TrainStep` 和 `ValidStep` implementations
/// - `inference.rs` 中的推論函數
#[derive(Module, Debug)]
pub struct Model<B: Backend> {
    conv1: Conv2d<B>,   // 第一個卷積層：1→32 通道，5x5 核心
    conv2: Conv2d<B>,   // 第二個卷積層：32→64 通道，5x5 核心
    pool1: MaxPool2d,   // 第一個最大池化層：2x2 核心，步長 2
    pool2: MaxPool2d,   // 第二個最大池化層：2x2 核心，步長 2
    dropout: Dropout,   // Dropout 層：防止過擬合
    linear1: Linear<B>, // 第一個全連接層：64*4*4 → hidden_size
    linear2: Linear<B>, // 第二個全連接層：hidden_size → num_classes
    activation: Relu,   // ReLU 啟動函數
}

// Forward pass
impl<B: Backend> Model<B> {
    /// 模型的前向傳播函數
    ///
    /// 這是模型的核心計算邏輯，定義了資料如何在網路中流動。
    /// 輸入的 MNIST 圖像經過以下處理步驟：
    /// 1. 重塑為 4D 張量（增加通道維度）
    /// 2. 通過兩個 卷積-啟動-池化 區塊進行特徵提取
    /// 3. 展平後通過全連接層進行分類
    ///
    /// ## 被呼叫者
    /// - `training.rs` 中的 `forward_classification` 方法
    /// - `inference.rs` 中的推論邏輯
    ///
    /// ## 參數
    /// * `images` - 輸入圖像張量，形狀 [batch_size, height, width]
    ///
    /// ## 返回值
    /// * 分類機率張量，形狀 [batch_size, num_classes]
    ///
    /// ## 張量形狀變化
    /// ```
    /// [batch_size, 28, 28]           # 輸入 MNIST 圖像
    /// → [batch_size, 1, 28, 28]      # 增加通道維度
    /// → [batch_size, 32, 24, 24]     # conv1 (5x5 核心，無填充)
    /// → [batch_size, 32, 12, 12]     # pool1 (2x2 核心，步長 2)
    /// → [batch_size, 64, 8, 8]       # conv2 (5x5 核心，無填充)
    /// → [batch_size, 64, 4, 4]       # pool2 (2x2 核心，步長 2)
    /// → [batch_size, 1024]           # 展平 (64*4*4=1024)
    /// → [batch_size, hidden_size]    # 第一個全連接層
    /// → [batch_size, num_classes]    # 第二個全連接層（輸出）
    /// ```
    pub fn forward(&self, images: Tensor<B, 3>) -> Tensor<B, 2> {
        let [batch_size, height, width] = images.dims();

        // 在第二個維度創建一個通道維度
        // MNIST 是灰階圖像，所以只有 1 個通道
        let x = images.reshape([batch_size, 1, height, width]);

        // --- LeNet-5 風格區塊 ---

        // 第一個卷積區塊
        let x = self.conv1.forward(x);
        let x = self.activation.forward(x);
        let x = self.pool1.forward(x);
        let x = self.dropout.forward(x); // 在區塊後應用 Dropout

        // 第二個卷積區塊
        let x = self.conv2.forward(x);
        let x = self.activation.forward(x);
        let x = self.pool2.forward(x);
        let x = self.dropout.forward(x); // 再次應用 dropout

        // 將 4D 張量展平為 2D，為全連接層準備
        let x = x.reshape([batch_size, 64 * 4 * 4]); // [batch_size, 1024]

        // --- 分類器 (全連接層) ---
        let x = self.linear1.forward(x); // [batch_size, hidden_size]
        let x = self.activation.forward(x);
        let x = self.dropout.forward(x); // 應用 dropout

        // 最終輸出：通過第二個全連接層得到分類機率
        self.linear2.forward(x) // [batch_size, num_classes]
    }
}

// instantiate the model for training
/// 模型設定結構體
///
/// 此結構體定義了創建模型所需的所有超參數。
/// 使用 `#[derive(Config)]` 巨集可以：
/// 1. 自動生成設定相關的方法
/// 2. 支援從 JSON 檔案載入/儲存設定
/// 3. 提供預設值和驗證功能
///
/// ## 相依關係
/// - `training.rs` 使用此設定來創建模型實例
/// - `main.rs` 透過 `TrainingConfig` 間接使用此設定
/// - `inference.rs` 透過載入訓練時保存的設定來重建模型
#[derive(Config, Debug)]
pub struct ModelConfig {
    num_classes: usize, // 分類數量（MNIST 有 10 個數字：0-9）
    hidden_size: usize, // 第一個全連接層的隱藏單元數量
    #[config(default = "0.5")]
    dropout: f64, // Dropout 機率（預設 0.5，即 50% 的神經元會被隨機關閉）
}

impl ModelConfig {
    /// 根據設定初始化模型
    ///
    /// 此方法是模型創建的工廠方法，它會：
    /// 1. 根據設定參數創建所有神經網路層
    /// 2. 將各層組裝成完整的模型
    /// 3. 在指定的設備上初始化所有權重
    ///
    /// ## 被呼叫者
    /// - `training.rs` 中的訓練邏輯
    /// - `inference.rs` 中載入模型時（透過儲存的設定）
    ///
    /// ## 層級設計說明
    /// - Conv1: 1→32 通道，5x5 核心，提取基本特徵
    /// - Pool1: 2x2 最大池化，降採樣
    /// - Conv2: 32→64 通道，5x5 核心，提取更複雜的特徵
    /// - Pool2: 2x2 最大池化，再次降採樣
    /// - Linear1: 1024 (64*4*4)→hidden_size，學習特徵的高級表示
    /// - Linear2: hidden_size→num_classes，最終分類決策
    ///
    /// ## 參數
    /// * `device` - 計算設備（CPU 或 GPU），所有層都會在此設備上創建
    ///
    /// ## 返回值
    /// * 完全初始化的模型實例
    pub fn init<B: Backend>(&self, device: &B::Device) -> Model<B> {
        Model {
            // 第一個卷積層：輸入 1 通道（灰階），輸出 32 通道，5x5 卷積核
            conv1: Conv2dConfig::new([1, 32], [5, 5]).init(device),

            // 第二個卷積層：輸入 32 通道，輸出 64 通道，5x5 卷積核
            conv2: Conv2dConfig::new([32, 64], [5, 5]).init(device),

            // 池化層：2x2 核心，步長為 2
            pool1: MaxPool2dConfig::new([2, 2]).with_strides([2, 2]).init(),
            pool2: MaxPool2dConfig::new([2, 2]).with_strides([2, 2]).init(),

            // ReLU 啟動函數：提供非線性變換
            activation: Relu::new(),

            // 第一個全連接層：從展平的特徵（64*4*4=1024）到隱藏層
            linear1: LinearConfig::new(64 * 4 * 4, self.hidden_size).init(device),

            // 第二個全連接層：從隱藏層到最終分類輸出
            linear2: LinearConfig::new(self.hidden_size, self.num_classes).init(device),

            // Dropout 層：使用設定的機率進行正則化
            dropout: DropoutConfig::new(self.dropout).init(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    use burn::backend::Wgpu;

    #[test]
    fn test_model_param_count() {
        type MyBackend = Wgpu<f32, i32>;

        let device = Default::default();
        let model = ModelConfig::new(10, 512).init::<MyBackend>(&device);

        println!("{model}");
        assert_eq!(model.num_params(), 582026)
    }
}
