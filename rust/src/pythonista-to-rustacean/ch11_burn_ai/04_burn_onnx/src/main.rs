//!
//! # Burn + ONNX 推論範例
//!
//! 展示如何透過 Burn 框架執行 ONNX 格式模型的推論。
//! 使用 `burn-import` 將 ONNX 模型匯入為原生 Rust 程式碼，再以 Burn 的 `Module` trait 執行。
//!
//! ## 架構圖
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────────────┐
//! │                    Burn + ONNX 推論流程                               │
//! │                                                                         │
//! │   模型訓練階段                                                         │
//! │   ResNet-18 (PyTorch/TensorFlow)  →  ONNX (.onnx)                  │
//! │                                    │                                  │
//! │                                    ▼                                  │
//! │   ┌──────────────────────────────────────────────┐                │
//! │   │  burn-import 工具                                    │                │
//! │   │  ONNX → Rust 程式碼 (.rs) + 權重 (.mpk)         │                │
//! │   └─────────────────────┬────────────────────────┘                │
//! │                         │                                             │
//! │                         ▼                                             │
//! │   ┌──────────────────────────────────────────────┐                │
//! │   │  build.rs (Build Script)                            │                │
//! │   │  將 .mpk 權重複製至 OUT_DIR                         │                │
//! │   └─────────────────────┬────────────────────────┘                │
//! │                         │                                             │
//! │                         ▼                                             │
//! │   ┌──────────────────────────────────────────────┐                │
//! │   │  Model::default()                                   │                │
//! │   │  ← 自動從 OUT_DIR 載入 .mpk 權重                  │                │
//! │   └─────────────────────┬────────────────────────┘                │
//! │                         │                                             │
//! │                         ▼                                             │
//! │              ┌──────────────────┐                               │
//! │              │  model.forward()   │  ← Burn Module trait         │
//! │              └──────────────────┘                               │
//! └─────────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 情境              | Python (ONNX Runtime) 写法                         | Rust (Burn + burn-import) 写法              |
//! |-------------------|--------------------------------------------------|------------------------------------------|
//! | 模型載入         | `ort.InferenceSession("model.onnx")`            | `Model::<B>::default()` (自動載入 .mpk)  |
//! | 輸入格式         | `session.run(None, {"input": data})`            | `Tensor::<B, 4>::zeros([1, 3, 224, 224])` |
//! | 推論執行         | `output = session.run(...)`                    | `model.forward(input)`                      |
//! | 權重來源         | ONNX 內含權重                                   | build.rs 將 .mpk 複製至編譯輸出目錄           |
//!
//! ## 關鍵技法
//!
//! - `burn-import`：將 ONNX 模型轉換為 Rust 程式碼 + 元資料 (.mpk)
//! - `build.rs`：建置腳本，在編譯時將權重檔複製到 `OUT_DIR`
//! - `Model::default()`：自動從 `OUT_DIR` 載入權重，無需手動路徑處理
//! - `type MyBackend = Wgpu<f32>`：純量推論只需 `Wgpu<f32>`，无需 `Autodiff`
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch11_burn_ai/04_burn_onnx
//! cargo run --release
//! ```
//!
//! ## 前提條件
//!
//! 需要先執行 `python convert_to_onnx.py`（在本專案根目錄），
//! 將 PyTorch ResNet-18 模型匯出為 ONNX 格式。
//!
// src/main.rs

// 1. 宣告我們剛剛建立的 `model.rs` 檔案為一個模組
pub mod model;

use burn::backend::Wgpu;
use burn::tensor::Tensor;

// 2. 引入由 burn-import 自動生成的 `Model` 結構體
//    路徑是： `檔案模組::自訂模組::Model`
use model::my_resnet::Model;

// 由於我們只是推論，不需要自動微分，
// 這裡使用 Wgpu<f32> 而非 Autodiff<Wgpu<f32>>
type MyBackend = Wgpu<f32>;

fn main() {
    // 3. 建立 WGPU 裝置
    let device = Default::default();

    // 4. 實例化模型。
    //    ::default() 是一個輔助函數，它會自動
    //    從 OUT_DIR 中尋找由 build.rs 生成的權重檔 (.mpk) 並載入。
    let model: Model<MyBackend> = Model::default();

    // 5. 建立符合 ResNet-18 的輸入張量
    //    格式為 NCHW = [batch, channel, height, width]
    //    這裡用全 0 當示範，實務上請放入前處理後的影像資料
    let input = Tensor::<MyBackend, 4>::zeros([1, 3, 224, 224], &device);

    // 6. 執行推論！
    let output = model.forward(input);

    // 7. 印出輸出張量的形狀
    println!("模型成功執行，輸出 shape: {:?}", output.shape());
}
