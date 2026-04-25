//!
//! # Candle MNIST 訓練範例
//!
//! 展示如何使用 Hugging Face Candle 框架訓練 MNIST 手寫數字分類模型。
//!
//! ## 架構圖
//!
//! ```text
//! ┌──────────────────────────────────────────────────────────────────────┐
//! │                     MNIST 分類器訓練流程                             │
//! │                                                                       │
//! │   Hugging Face Hub                                                  │
//! │          │                                                         │
//! │          ▼                                                         │
//! │   ┌──────────────────────────────────────────────────────────┐   │
//! │   │  MnistDataset::new()                                     │   │
//! │   │  - 下載 Parquet 格式的 MNIST                             │   │
//! │   │  - Rayon 並行解碼 PNG 圖片                              │   │
//! │   │  - 標準化為 [0.0, 1.0] Tensor                          │   │
//! │   └──────────────────────────────────────────────────────────┘   │
//! │                      │                                             │
//! │                      ▼                                             │
//! │   ┌──────────────────────────────────────────────────────────┐   │
//! │   │  模型訓練                                                 │   │
//! │   │  - 訓練回合 (1): 基礎線性模型 + 權重儲存               │   │
//! │   │  - 訓練回合 (2): CNN 模型 + Batcher                     │   │
//! │   └──────────────────────────────────────────────────────────┘   │
//! │                      │                                             │
//! │                      ▼                                             │
//! │   model_weights.safetensors (輸出)                              │
//! └──────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 情境              | Python (PyTorch) 写法                       | Rust (Candle) 写法                          |
//! |-------------------|------------------------------------------|---------------------------------------------|
//! | 資料集下載       | `datasets.load_dataset("mnist")`         | `from_hub()` + Parquet reader              |
//! | 資料迭代器        | `DataLoader(dataset, batch_size=64)`    | `MnistDataset::train_iter(64)` + Batcher   |
//! | 模型定義          | `nn.Linear(784, 10)`                   | `linear(784, 10, vb)`                     |
//! | 設備選擇         | `device = torch.device("cuda")`        | `Device::new_metal(0)` 或 `Device::Cpu` |
//! | 權重儲存         | `torch.save(model.state_dict(), ...)`   | `parameter_storage.save("model.safetensors")`|
//!
//! ## 關鍵技法
//!
//! - `VarMap`：全域參數儲存，支援序列化與反序列化
//! - `VarBuilder`：從 VarMap 建立變數，綁定至特定設備
//! - `Batcher::new2`：將任意迭代器包裝為批次迭代器
//! - `.to_dtype(DType::F32)`：u8 → f32 標準化 / 255.0
//! - `Device::new_metal(0)`：macOS GPU 加速（CUDA 等效寫法）
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch10_candle_ai/01_candle_mnist
//! cargo run --release
//! ```
//!
use anyhow::Result;
use candle_core::{DType, Device};
use candle_nn::{VarBuilder, VarMap};

mod data;
mod models;
mod ops;
mod training;

fn main() -> Result<()> {
    // --- 1. 全域初始化設定 (Global Initialization) ---
    println!("==================================================");
    println!("          MNIST 分類器訓練程式          ");
    println!("==================================================");

    println!("\n[1] 正在從 Hugging Face Hub 拉取並載入 MNIST 原始資料集...");
    let dataset = data::MnistDataset::new()?;
    // let computation_device = Device::Cpu;
    let computation_device =
        Device::new_metal(0).map_err(|e| anyhow::anyhow!("無法初始化 Metal 設備: {}", e))?;

    println!("> 原始資料載入完成。");
    println!("    - 訓練集圖片 Shape: {:?}", dataset.train_images.shape());
    println!(
        "    - 測試集標籤 Shape:   {:?}",
        dataset.test_labels.shape()
    );
    println!("> 使用設備: {:?}", computation_device.location());
    println!("\n--------------------------------------------------");

    // --- 2. 驗證資料批次器 (Batcher Verification) ---
    {
        println!("\n[2] 驗證資料批次器 (Batcher)...");
        // 從已載入的資料集中建立一個迭代器 (batch size: 64)
        let mut train_loader = dataset.train_iter(64)?;

        // 取出第一個批次作為示範
        if let Some(r) = train_loader.next() {
            let (batch_data, batch_labels) = r?;
            println!("> 成功從訓練集 Batcher 取得一個批次！");
            println!("    - 批次資料 Shape: {:?}", batch_data.shape());
            println!("    - 批次標籤 Shape: {:?}", batch_labels.shape());
        } else {
            println!("> 未能從 Batcher 中取得任何批次。");
        }
    }
    println!("\n--------------------------------------------------");

    // --- 3. 訓練回合 (1): 基礎訓練 (不使用 Batcher) ---
    {
        println!("\n[3] 執行訓練回合 (1): 基礎訓練 (Foundational Training)");

        // 為此訓練回合建立獨立的模型與參數
        let parameter_storage = VarMap::new();
        let variable_builder =
            VarBuilder::from_varmap(&parameter_storage, DType::F32, &computation_device);
        let model = models::linear_manual::MnistClassifier::new(variable_builder)?;
        println!("> 模型與參數已建立...");

        // 執行基礎訓練
        training::run_foundational_training(
            &model,
            &parameter_storage,
            &computation_device,
            &dataset,
        )?;

        println!("> 訓練回合 (1) 完成。");
        parameter_storage
            .save("model_weights.safetensors")
            .map_err(|e| anyhow::anyhow!("保存模型權重失敗: {}", e))?;
    }
    println!("\n--------------------------------------------------");

    // --- 4. 訓練回合 (2): 使用 Batcher 進行訓練 ---
    {
        println!("\n[4] 執行訓練回合 (2): 使用 Batcher 進行高效訓練");

        // 建立一組全新的模型與參數，確保訓練是從頭開始
        let parameter_storage = VarMap::new();
        let variable_builder =
            VarBuilder::from_varmap(&parameter_storage, DType::F32, &computation_device);
        let model = models::cnn::MnistClassifierCNN::new(variable_builder)?;
        println!("> 為新回合重新建立模型與參數...");

        // 執行使用 Batcher 的訓練
        training::run_training_with_batcher(
            &model,
            &parameter_storage,
            &computation_device,
            &dataset,
        )?;

        println!("> 訓練回合 (2) 完成。");
    }

    println!("\n==================================================");
    println!("      所有流程已執行完畢      ");
    println!("==================================================");

    Ok(())
}
