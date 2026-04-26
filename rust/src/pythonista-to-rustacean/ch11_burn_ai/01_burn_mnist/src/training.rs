//! # 模型訓練模組
//!
//! 本模組實現了完整的神經網路訓練流程，包括：
//! 1. 訓練和驗證步驟的定義
//! 2. 損失函數和評估指標的設定
//! 3. 資料載入器的建立
//! 4. 訓練循環的執行
//!
//! ## 與其他模組的相依關係：
//! - `model.rs`: 使用 `Model` 和 `ModelConfig` 定義模型架構
//! - `data.rs`: 使用 `MnistBatch` 和 `MnistBatcher` 處理資料
//! - `main.rs`: 透過 `TrainingConfig` 接收訓練參數
//! - `inference.rs`: 儲存訓練好的模型供推論使用

// 引入本 crate 的其他模組
use crate::{
    data::{MnistBatch, MnistBatcher}, // 從 data.rs：資料批次和批次處理器
    model::{Model, ModelConfig},      // 從 model.rs：模型結構和設定
};

// 引入 Burn 框架的相關組件
use burn::{
    data::{dataloader::DataLoaderBuilder, dataset::vision::MnistDataset}, // 資料載入和 MNIST 資料集
    nn::loss::CrossEntropyLossConfig, // 交叉熵損失函數（用於分類任務）
    optim::AdamConfig,                // Adam 優化器設定
    prelude::*,                       // 常用的 traits 和類型
    record::CompactRecorder,          // 模型檢查點記錄器
    tensor::backend::AutodiffBackend, // 自動微分後端 trait
    train::{
        ClassificationOutput,
        LearnerBuilder,
        TrainOutput,
        TrainStep,
        ValidStep,
        metric::{AccuracyMetric, LossMetric}, // 訓練相關組件和評估指標
    },
};

// 建立 Output struct 以供訓練使用
impl<B: Backend> Model<B> {
    /// 分類任務的前向傳播（包含損失計算）
    ///
    /// 此方法擴展了模型的基本 `forward` 方法，加入了損失計算，
    /// 專門用於分類任務的訓練和驗證。
    ///
    /// ## 與其他方法的關係
    /// - 呼叫 `model.rs` 中的 `forward` 方法獲得預測結果
    /// - 被 `TrainStep` 和 `ValidStep` 的 `step` 方法使用
    /// - 使用交叉熵損失函數，這是多分類任務的標準選擇
    ///
    /// ## 參數
    /// * `images` - 輸入圖像張量，來自 `MnistBatch.images`
    /// * `targets` - 目標標籤張量，來自 `MnistBatch.targets`
    ///
    /// ## 返回值
    /// * `ClassificationOutput` - 包含損失、預測結果和目標標籤的結構體
    ///
    /// ## 損失函數說明
    /// 交叉熵損失 (Cross-Entropy Loss) 用於衡量預測機率分佈和真實標籤的差異：
    /// - 當預測正確且信心高時，損失接近 0
    /// - 當預測錯誤或信心低時，損失較大
    /// - 適合多分類問題（如 MNIST 的 10 個數字類別）
    pub fn forward_classification(
        &self,
        images: Tensor<B, 3>,
        targets: Tensor<B, 1, Int>,
    ) -> ClassificationOutput<B> {
        // 獲得模型的原始輸出（未歸一化的邏輯值）
        let output = self.forward(images);

        // 計算交叉熵損失
        // CrossEntropyLossConfig 會自動：
        // 1. 對 output 應用 softmax 得到機率分佈
        // 2. 計算與 targets 的交叉熵
        let loss = CrossEntropyLossConfig::new()
            .init(&output.device())
            .forward(output.clone(), targets.clone());

        // 包裝成分類輸出格式
        ClassificationOutput::new(loss, output, targets)
    }
}

// 訓練需要前向傳播、計算損失與梯度 (反向傳播)
impl<B: AutodiffBackend> TrainStep<MnistBatch<B>, ClassificationOutput<B>> for Model<B> {
    /// 訓練步驟實現
    ///
    /// 這是訓練過程中每個批次的處理邏輯。`TrainStep` trait 是 Burn 訓練框架
    /// 的核心介面，定義了如何處理一個訓練批次。
    ///
    /// ## 與自動微分的關係
    /// - 泛型約束 `B: AutodiffBackend` 確保後端支援自動微分
    /// - `loss.backward()` 會自動計算所有可訓練參數的梯度
    /// - Burn 框架會自動使用這些梯度更新模型參數
    ///
    /// ## 與驗證步驟的區別
    /// - 訓練步驟：計算損失 + 反向傳播（梯度計算）
    /// - 驗證步驟：只計算損失，不進行反向傳播
    ///
    /// ## 參數
    /// * `batch` - 一批訓練資料，包含圖像和標籤
    ///
    /// ## 返回值
    /// * `TrainOutput` - 包含模型、梯度資訊和分類輸出的結構體
    ///
    /// ## 訓練流程
    /// 1. 前向傳播：計算預測結果和損失
    /// 2. 反向傳播：計算梯度
    /// 3. 返回結果供優化器使用
    fn step(&self, batch: MnistBatch<B>) -> TrainOutput<ClassificationOutput<B>> {
        // 執行前向傳播並計算損失
        let item = self.forward_classification(batch.images, batch.targets);

        // 執行反向傳播並返回訓練輸出
        // self: 當前模型狀態
        // item.loss.backward(): 損失的梯度（自動微分計算得出）
        // item: 包含損失、預測和目標的分類輸出
        TrainOutput::new(self, item.loss.backward(), item)
    }
}

// 驗證僅需要前向傳播與計算損失
impl<B: Backend> ValidStep<MnistBatch<B>, ClassificationOutput<B>> for Model<B> {
    /// 驗證步驟實現
    ///
    /// 驗證步驟與訓練步驟的主要區別是不進行反向傳播。
    /// 這是因為驗證的目的是評估模型性能，而不是更新模型參數。
    ///
    /// ## 為什麼不需要自動微分
    /// - 泛型約束只需要 `B: Backend`，不需要 `AutodiffBackend`
    /// - 驗證過程不計算梯度，因此可以在任何後端上運行
    /// - 這樣可以節省記憶體和計算資源
    ///
    /// ## 與訓練步驟的對比
    /// ```
    /// 訓練：forward_classification → loss.backward() → 參數更新
    /// 驗證：forward_classification → 只評估損失和準確率
    /// ```
    ///
    /// ## 使用時機
    /// - 每個 epoch 結束後評估模型在驗證集上的表現
    /// - 用於監控過擬合和模型收斂情況
    /// - 為早停（early stopping）等訓練策略提供指標
    ///
    /// ## 參數
    /// * `batch` - 一批驗證資料，格式與訓練資料相同
    ///
    /// ## 返回值
    /// * `ClassificationOutput` - 包含損失、預測和目標的分類結果
    fn step(&self, batch: MnistBatch<B>) -> ClassificationOutput<B> {
        // 只執行前向傳播，不進行反向傳播
        self.forward_classification(batch.images, batch.targets)
    }
}

/// 訓練設定結構體
///
/// 此結構體集中管理所有訓練相關的超參數和設定。
/// 使用 `#[derive(Config)]` 巨集提供：
/// 1. JSON 序列化/反序列化功能
/// 2. 預設值支援
/// 3. 設定驗證功能
///
/// ## 與其他模組的介面
/// - `main.rs`: 創建 `TrainingConfig` 實例並傳遞給訓練函數
/// - `inference.rs`: 從檔案載入此設定以重建模型
/// - `model.rs`: 透過 `model` 欄位配置模型架構
///
/// ## 設定說明
/// - `model`: 模型架構設定，來自 `model.rs`
/// - `optimizer`: 優化器設定，使用 Adam 演算法
/// - 其他欄位控制訓練流程的各個方面
#[derive(Config)]
pub struct TrainingConfig {
    pub model: ModelConfig,    // 模型設定（來自 model.rs）
    pub optimizer: AdamConfig, // Adam 優化器設定

    #[config(default = 10)]
    pub num_epochs: usize, // 訓練週期數：完整遍歷訓練集的次數

    #[config(default = 64)]
    pub batch_size: usize, // 批次大小：每次更新參數時處理的樣本數

    #[config(default = 4)]
    pub num_workers: usize, // 資料載入器的並行工作線程數

    #[config(default = 42)]
    pub seed: u64, // 隨機種子：確保結果可重現

    #[config(default = 1.0e-4)]
    pub learning_rate: f64, // 學習率：控制參數更新的步長
}

/// 創建並清理成品目錄
///
/// 此函數負責準備訓練成品的儲存目錄。成品包括：
/// - config.json: 訓練設定參數
/// - model: 訓練好的模型權重和架構
/// - 訓練過程中的檢查點和日誌
///
/// ## 為什麼要清理現有目錄
/// 1. 確保訓練結果的一致性
/// 2. 避免舊的成品干擾新的訓練
/// 3. 獲得準確的學習器摘要和指標
///
/// ## 參數
/// * `artifact_dir` - 成品目錄路徑
#[allow(dead_code)] // 函數被註解掉的訓練函數使用
fn create_artifact_dir(artifact_dir: &str) {
    // 移除現有的成品目錄以獲得乾淨的開始
    // .ok() 表示忽略錯誤（如目錄不存在）
    std::fs::remove_dir_all(artifact_dir).ok();

    // 創建新的成品目錄（包含所有必要的父目錄）
    std::fs::create_dir_all(artifact_dir).ok();
}

/// 主要訓練函數
///
/// 這是整個訓練流程的協調者，負責：
/// 1. 環境準備（目錄創建、設定儲存、隨機種子）
/// 2. 資料載入器建立（訓練集和測試集）
/// 3. 學習器配置（模型、優化器、指標、檢查點）
/// 4. 模型訓練和儲存
///
/// ## 與其他模組的協作
/// - 使用 `data.rs` 的 `MnistBatcher` 處理資料
/// - 使用 `model.rs` 的 `ModelConfig` 初始化模型
/// - 創建的模型可被 `inference.rs` 載入使用
/// - 透過 `main.rs` 的呼叫開始訓練流程
///
/// ## 參數
/// * `artifact_dir` - 成品儲存目錄
/// * `config` - 完整的訓練設定
/// * `device` - 計算設備（支援自動微分的後端）
///
/// ## 訓練流程說明
/// ```
/// 1. 準備環境 → 2. 建立資料載入器 → 3. 配置學習器 → 4. 執行訓練 → 5. 儲存模型
/// ```
#[allow(dead_code)] // 目前在 main.rs 中被註解掉
pub fn train<B: AutodiffBackend>(artifact_dir: &str, config: TrainingConfig, device: B::Device) {
    // === 1. 環境準備 ===
    create_artifact_dir(artifact_dir);

    // 儲存訓練設定，供後續推論使用
    config
        .save(format!("{artifact_dir}/config.json"))
        .expect("Config should be saved successfully");

    // 設定隨機種子以確保結果可重現
    B::seed(config.seed);

    // === 2. 資料處理準備 ===
    let batcher = MnistBatcher::default();

    // 建立訓練資料載入器
    // 特點：啟用隨機洗牌，多線程載入
    let dataloader_train = DataLoaderBuilder::new(batcher.clone())
        .batch_size(config.batch_size)
        .shuffle(config.seed) // 使用設定的種子進行洗牌
        .num_workers(config.num_workers) // 並行載入資料
        .build(MnistDataset::train());

    // 建立測試資料載入器
    // 注意：測試集也使用相同的洗牌種子，但這主要是為了一致性
    let dataloader_test = DataLoaderBuilder::new(batcher)
        .batch_size(config.batch_size)
        .shuffle(config.seed)
        .num_workers(config.num_workers)
        .build(MnistDataset::test());

    // === 3. 學習器配置 ===
    let learner = LearnerBuilder::new(artifact_dir)
        // 設定評估指標
        .metric_train_numeric(AccuracyMetric::new()) // 訓練準確率
        .metric_valid_numeric(AccuracyMetric::new()) // 驗證準確率
        .metric_train_numeric(LossMetric::new()) // 訓練損失
        .metric_valid_numeric(LossMetric::new()) // 驗證損失
        // 設定檢查點儲存器（用於保存訓練過程和最終模型）
        .with_file_checkpointer(CompactRecorder::new())
        // 設定計算設備
        .devices(vec![device.clone()])
        // 設定訓練週期數
        .num_epochs(config.num_epochs)
        // 顯示訓練摘要
        .summary()
        // 建立學習器
        .build(
            config.model.init::<B>(&device), // 初始化模型
            config.optimizer.init(),         // 初始化優化器
            config.learning_rate,            // 設定學習率
        );

    // === 4. 執行訓練 ===
    // fit 方法會執行完整的訓練循環：
    // - 對每個 epoch，遍歷訓練資料進行參數更新
    // - 在驗證集上評估模型性能
    // - 記錄指標和儲存檢查點
    let model_trained = learner.fit(dataloader_train, dataloader_test);

    // === 5. 儲存最終模型 ===
    // 儲存訓練好的模型供推論使用
    model_trained
        .save_file(format!("{artifact_dir}/model"), &CompactRecorder::new())
        .expect("Trained model should be saved successfully");
}
