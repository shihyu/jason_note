#![recursion_limit = "256"]

//! # 學習 Burn 機器學習框架的範例
//!
//! 展示了如何使用 Rust 的 Burn 機器學習框架來構建、訓練和推論一個簡單的神經網路模型。
//! 模型將在 MNIST 手寫數字資料集上進行訓練和測試。
//!
//! ## 模組組織：
//! - `data`: 資料處理和批次化邏輯
//! - `model`: 神經網路模型定義
//! - `training`: 訓練邏輯和設定
//! - `inference`: 推論（預測）邏輯

// 引入本項目的各個模組
mod data; // 負責 MNIST 資料的批次處理和前處理
mod inference; // 負責使用訓練好的模型進行預測
mod model; // 定義神經網路模型架構
mod training; // 負責模型訓練流程

// 從 crate 內部引入結構體
use crate::{model::ModelConfig, training::TrainingConfig};

// 從 burn 套件引入所需的模組
use burn::{
    backend::Autodiff,      // Autodiff 用於自動微分（訓練時需要）
    backend::Wgpu,          // Wgpu 是 GPU 加速後端
    data::dataset::Dataset, // 資料集 trait
    optim::AdamConfig,      // Adam 優化器的設定（訓練時需要）
};

// [新增] 引入 std::env 以讀取命令列參數
use std::env;

// [新增] 為了推論範例，我們需要載入 MnistDataset
use burn::data::dataset::vision::MnistDataset;

fn main() {
    // 定義後端類型
    type MyBackend = Wgpu<f32, i32>;
    type MyAutodiffBackend = Autodiff<MyBackend>;

    // 獲取預設的 Wgpu 設備
    let device = burn::backend::wgpu::WgpuDevice::default();

    // 設定儲存訓練成品的目錄
    let artifact_dir = "./tmp/burn_mnist_artifact";

    // --- [修改] 根據命令列參數選擇執行區塊 ---
    let args: Vec<String> = env::args().collect();

    // args[0] 是程式名稱，args[1] 才是第一個參數
    if args.len() < 2 {
        eprintln!("用法: cargo run -- [COMMAND]");
        eprintln!("COMMANDS:");
        eprintln!("  train    訓練新模型並儲存");
        eprintln!("  infer    載入模型並對範例進行推論");
        std::process::exit(1);
    }

    let command = &args[1];

    match command.as_str() {
        "train" => {
            println!("=== 執行訓練模式 ===");
            // 呼叫訓練函數
            crate::training::train::<MyAutodiffBackend>(
                artifact_dir,
                TrainingConfig::new(ModelConfig::new(10, 512), AdamConfig::new()),
                device.clone(),
            );
            println!("=== 訓練完成 ===");
        }
        "infer" => {
            println!("=== 執行推論模式 ===");

            // 取得一個測試樣本 (例如第 44 個)
            // 確保你已經先執行過 'train'，否則 artifact_dir 會是空的
            let item = MnistDataset::test()
                .get(44)
                .expect("無法從 MNIST 測試集取得項目 #44");

            // 呼叫推論函數 (原先被註解的區塊)
            crate::inference::infer::<MyBackend>(artifact_dir, device, item);
            println!("=== 推論完成 ===");
        }
        _ => {
            eprintln!("錯誤: 未知的指令 '{}'", command);
            eprintln!("請使用 'train' 或 'infer'");
            std::process::exit(1);
        }
    }
}
