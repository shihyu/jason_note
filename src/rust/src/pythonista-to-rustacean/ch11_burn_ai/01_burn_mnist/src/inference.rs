//! # 模型推論模組
//!
//! 本模組負責使用預先訓練好的模型進行推論（預測）。
//! 主要功能包括：
//! 1. 載入訓練時儲存的模型設定和權重
//! 2. 對單一 MNIST 樣本進行預測
//! 3. 展示預測結果與實際標籤的比較
//!
//! ## 與其他模組的相依關係：
//! - `training.rs`: 載入訓練時儲存的 `TrainingConfig`
//! - `data.rs`: 使用 `MnistBatcher` 處理推論樣本
//! - `model.rs`: 透過 `TrainingConfig` 間接重建模型架構
//! - `main.rs`: 被主函數呼叫執行推論

// 引入本 crate 的其他模組
use crate::{
    data::MnistBatcher,       // 從 data.rs：用於處理推論樣本的批次化
    training::TrainingConfig, // 從 training.rs：載入訓練時的完整設定
};

// 引入 Burn 框架的相關組件
use burn::{
    data::{dataloader::batcher::Batcher, dataset::vision::MnistItem}, // 資料處理和 MNIST 項目
    prelude::*,                                                       // 常用的 traits 和類型
    record::{CompactRecorder, Recorder},                              // 模型載入器
};

/// 推論函數：使用訓練好的模型進行預測
///
/// 此函數展示了完整的模型推論流程，包括載入、預測和結果展示。
/// 這是訓練後模型應用的典型範例。
///
/// ## 推論流程說明
/// ```
/// 1. 載入設定 → 2. 載入模型 → 3. 處理輸入 → 4. 執行預測 → 5. 解釋結果
/// ```
///
/// ## 與訓練的對應關係
/// - 使用相同的 `TrainingConfig` 確保模型架構一致
/// - 使用相同的 `MnistBatcher` 確保資料處理一致
/// - 載入的模型權重來自訓練階段的儲存
///
/// ## 參數
/// * `artifact_dir` - 訓練成品目錄，包含設定和模型檔案
/// * `device` - 計算設備（注意：推論不需要自動微分功能）
/// * `item` - 要進行預測的 MNIST 樣本
///
/// ## 錯誤處理
/// 使用 `expect` 來處理檔案載入錯誤，並提供有意義的錯誤訊息
/// 指導使用者先執行訓練。
pub fn infer<B: Backend>(artifact_dir: &str, device: B::Device, item: MnistItem) {
    // === 1. 載入訓練設定 ===
    // 載入訓練時儲存的完整設定，包含模型架構資訊
    let config = TrainingConfig::load(format!("{artifact_dir}/config.json"))
        .expect("Config should exist for the model; run train first");

    // === 2. 載入模型權重 ===
    // 使用 CompactRecorder 載入訓練好的模型參數
    let record = CompactRecorder::new()
        .load(format!("{artifact_dir}/model").into(), &device)
        .expect("Trained model should exist; run train first");

    // === 3. 重建完整模型 ===
    // 使用載入的設定初始化模型架構，然後載入訓練好的權重
    let model = config.model.init::<B>(&device).load_record(record);

    // === 4. 準備推論資料 ===
    // 取得原始標籤用於比較
    let label = item.label;

    // 使用與訓練相同的批次處理器處理單一樣本
    // 注意：即使只有一個樣本，也要包裝成 Vec 來符合批次介面
    let batcher = MnistBatcher::default();
    let batch = batcher.batch(vec![item], &device);

    // === 5. 執行推論 ===
    // 透過模型的 forward 方法獲得預測結果
    // output 是形狀為 [1, 10] 的張量，包含 10 個類別的未歸一化分數
    let output = model.forward(batch.images);

    // === 6. 解釋預測結果 ===
    // argmax(1) 找出第 1 維（類別維）上的最大值索引
    // flatten 將結果從 [1] 形狀的張量轉換為標量
    // into_scalar() 提取實際的數值
    let predicted = output.argmax(1).flatten::<1>(0, 1).into_scalar();

    // === 7. 顯示結果 ===
    println!("Predicted: {}, Actual: {}", predicted, label);
}
