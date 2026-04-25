//! # 資料處理和批次化模組
//!
//! 本模組負責處理 MNIST 資料集的批次化和前處理。
//! 主要功能包括：
//! 1. 將個別的 MNIST 樣本組合成批次
//! 2. 對圖像資料進行標準化處理
//! 3. 將資料轉換為適合神經網路訓練的張量格式
//!
//! ## 與其他模組的相依關係：
//! - `training.rs`: 使用 `MnistBatcher` 來處理訓練和驗證資料
//! - `inference.rs`: 使用 `MnistBatcher` 來處理單一推論樣本
//! - `model.rs`: 接收本模組產生的 `MnistBatch` 作為輸入

use burn::{
    data::{dataloader::batcher::Batcher, dataset::vision::MnistItem},
    prelude::*,
};

/// MNIST 批次處理器
///
/// `MnistBatcher` 負責將個別的 `MnistItem` 組合成批次，並進行必要的前處理。
/// 它實現了 `Batcher` trait，這是 Burn 資料載入流程的核心組件。
///
/// ## 功能說明
/// 1. **批次化**: 將多個單獨的樣本組合成一個批次
/// 2. **圖像前處理**: 標準化像素值，使模型訓練更穩定
/// 3. **張量轉換**: 將原始資料轉換為神經網路可處理的張量格式
///
/// ## 使用者
/// - `training.rs`: 在建立 DataLoader 時使用
/// - `inference.rs`: 處理單一推論樣本時使用
///
/// ## 設計模式
/// 使用 `Clone` 和 `Default` 讓此結構體可以輕鬆實例化和複製，
/// 符合 Burn 框架對 Batcher 的要求。
#[derive(Clone, Default)]
pub struct MnistBatcher {}

/// MNIST 批次資料結構
///
/// `MnistBatch` 代表一個批次的 MNIST 資料，包含圖像和對應的標籤。
/// 這是模型訓練和推論時的輸入格式。
///
/// ## 設計考慮
/// - 使用泛型 `B: Backend` 讓此結構體可以在不同的計算後端上使用
/// - 圖像使用浮點張量（用於神經網路計算）
/// - 標籤使用整數張量（用於分類任務）
///
/// ## 與模型的介面
/// - `model.rs` 中的 `forward` 方法接收 `batch.images`
/// - `training.rs` 中的分類任務同時使用 `images` 和 `targets`
///
/// ## 欄位說明
/// * `images`: 形狀為 `[batch_size, 28, 28]` 的 3D 張量，代表一批圖像
///   - 每個元素是標準化後的像素值（約在 -2 到 2 之間）
/// * `targets`: 形狀為 `[batch_size]` 的 1D 整數張量，代表對應的標籤
///   - 每個元素是 0-9 的整數，代表手寫數字
#[derive(Clone, Debug)]
pub struct MnistBatch<B: Backend> {
    pub images: Tensor<B, 3>,       // 圖像張量：[batch_size, height, width]
    pub targets: Tensor<B, 1, Int>, // 標籤張量：[batch_size]
}

impl<B: Backend> Batcher<B, MnistItem, MnistBatch<B>> for MnistBatcher {
    /// 批次化方法：將 `MnistItem` 列表轉換為 `MnistBatch`
    ///
    /// 這是資料處理管線的核心方法，負責：
    /// 1. **圖像前處理**: 標準化、重塑張量
    /// 2. **批次組合**: 將個別樣本組合成批次張量
    /// 3. **設備放置**: 將資料移動到指定的計算設備
    ///
    /// ## 圖像前處理流程
    /// ```
    /// 原始像素 [0, 255]
    /// → 正規化 [0, 1]           (除以 255)
    /// → 標準化 [-2.4, 2.1]       (減去均值，除以標準差)
    /// → 增加暫時批次維度 [1, 28, 28] (為後續拼接準備)
    /// ```
    ///
    /// ## 標準化參數來源
    /// 均值 0.1307 和標準差 0.3081 來自 PyTorch MNIST 範例。
    /// 這些值是在整個 MNIST 訓練集上計算得出的統計數據，
    /// 使用相同的標準化可以讓模型更容易收斂。
    ///
    /// ## 參數
    /// * `items` - `MnistItem` 的向量，每個包含一張 28x28 圖像和一個標籤
    /// * `device` - 目標計算設備（CPU 或 GPU）
    ///
    /// ## 返回值
    /// * `MnistBatch` - 包含批次化圖像和標籤的結構體
    ///
    /// ## 使用時機
    /// - 訓練期間：DataLoader 自動呼叫此方法處理每個批次
    /// - 推論期間：手動呼叫處理單一樣本（包裝成向量）
    fn batch(&self, items: Vec<MnistItem>, device: &<B as Backend>::Device) -> MnistBatch<B> {
        // === 圖像處理流程 ===
        let images = items
            .iter()
            // 步驟 1: 從 item.image 創建 TensorData
            // item.image 是 [[u8; 28]; 28] 格式的二維陣列
            .map(|item| TensorData::from(item.image).convert::<B::FloatElem>())
            // 步驟 2: 創建 2D 張量並放置到指定設備
            .map(|data| Tensor::<B, 2>::from_data(data, device))
            // 步驟 3: 重塑為 3D 張量，增加一個大小為 1 的維度
            // [28, 28] → [1, 28, 28]，此處的 1 是為了後續拼接 (cat) 成批次
            .map(|tensor| tensor.reshape([1, 28, 28]))
            // 步驟 4: 圖像標準化
            // 4a. 將像素值從 [0, 255] 縮放到 [0, 1]
            // 4b. 使用 MNIST 資料集的統計數據進行標準化
            //     這些數值來自 PyTorch 官方範例：
            //     https://github.com/pytorch/examples/blob/54f4572509891883a947411fd7239237dd2a39c3/mnist/main.py#L122
            .map(|tensor| ((tensor / 255) - 0.1307) / 0.3081)
            // 收集所有處理過的圖像張量
            .collect();

        // === 標籤處理流程 ===
        let targets = items
            .iter()
            .map(|item| {
                // 將標籤從 u8 轉換為後端所需的整數類型
                // 創建形狀為 [1] 的張量（稍後會拼接成批次）
                Tensor::<B, 1, Int>::from_data([(item.label as i64).elem::<B::IntElem>()], device)
            })
            // 收集所有標籤張量
            .collect();

        // === 批次組合 ===
        // 將圖像張量列表沿著第 0 維（批次維）拼接
        // Vec<Tensor<B, 3>> (每個 shape [1, 28, 28]) → Tensor<B, 3> (shape [batch_size, 28, 28])
        let images = Tensor::cat(images, 0);

        // 將標籤張量列表沿著第 0 維拼接
        // Vec<Tensor<B, 1, Int>> → Tensor<B, 1, Int> with shape [batch_size]
        let targets = Tensor::cat(targets, 0);

        // 創建並返回最終的批次
        MnistBatch { images, targets }
    }
}

#[cfg(test)]
mod tests {
    use super::*; // 匯入 MnistBatcher

    use burn::backend::Wgpu;
    use burn::data::{dataloader::DataLoaderBuilder, dataset::vision::MnistDataset};

    #[test]
    fn test_dataloader_num_items() {
        let batcher = MnistBatcher::default();

        // 建立資料載入器
        let dataloader_train = DataLoaderBuilder::<Wgpu, _, _>::new(batcher)
            .batch_size(64) // 批次大小不應影響 `num_items` 的結果
            .build(MnistDataset::train());

        // 驗證 num_items() 回傳的是資料集中的項目總數
        assert_eq!(dataloader_train.num_items(), 60_000);
    }

    #[test]
    fn test_dataloader_batch_shape() {
        let batcher = MnistBatcher::default();

        // 建立資料載入器，設定批次大小為 64
        let dataloader_train = DataLoaderBuilder::<Wgpu, _, _>::new(batcher)
            .batch_size(64)
            .build(MnistDataset::train());

        // 我們必須從迭代器中取出第一個批次來進行檢查
        let first_batch = dataloader_train
            .iter()
            .next()
            .expect("資料載入器應至少能產生一個批次");

        // 檢查 `targets` 張量的形狀
        // 根據 data.rs，images 的形狀是 [batch_size, 28, 28]
        assert_eq!(first_batch.images.dims(), [64, 28, 28]);
    }
}
