//!
//! # Safetensors 權重載入範例
//!
//! 展示如何使用 `burn_import::safetensors` 將 Safetensors 格式的權重檔
//! 載入到 Burn 模型中。
//!
//! ## 架構圖
//!
//! ```text
//! ┌────────────────────────────────────────────────────────────────────────┐
//! │                  Safetensors 權重載入流程                            │
//! │                                                                        │
//! │   ┌─────────────────────┐                                             │
//! │   │  simple_fcn.safetensors │  ← 權重檔案                        │
//! │   └──────────┬──────────┘                                             │
//! │              │                                                         │
//! │              ▼                                                         │
//! │   ┌─────────────────────────────────────────────┐              │
//! │   │  SafetensorsFileRecorder                          │              │
//! │   │  .load(load_args, &device) → Record           │              │
//! │   └──────────┬───────────────────────────────────┘              │
//! │              │                                                       │
//! │              ▼                                                       │
//! │   ┌─────────────────────────────────────────────┐              │
//! │   │  FCN::init(&device)                           │              │
//! │   │  .load_record(record)                           │              │
//! │   └────────────────────┬──────────────────────────┘              │
//! │                        ▼                                          │
//! │              ┌──────────────────┐                             │
//! │              │  模型推論 ready!   │                             │
//! │              └──────────────────┘                             │
//! └────────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 情境              | Python (Safetensors) 写法                           | Rust (Burn) 写法                                |
//! |-------------------|----------------------------------------------|--------------------------------------------|
//! | 權重載入         | `load_file("model.safetensors")`            | `SafetensorsFileRecorder::load(load_args)` |
//! | 權重重映射       | 無需（Safetensors 為標準格式）              | `with_key_remap("model\\.(.*)", "$1")`   |
//! | 初始化空模型     | `Model()` (必須與權重結構吻合)              | `FCN::init(&device)`                       |
//! | 填充權重        | 自動合併                                    | `.load_record(record)`                     |
//! | 精度設定        | `dtype=torch.float32`                     | `FullPrecisionSettings`                   |
//!
//! ## 關鍵技法
//!
//! - `SafetensorsFileRecorder::<FullPrecisionSettings>`：控制載入時的浮點精度
//! - `LoadArgs::new().with_key_remap(...)`：對應 HuggingFace 模型前綴（如 `model.linear.weight` → `linear.weight`）
//! - `.load_record(record)`：兩步驟載入——先建空殼，再填充
//! - `with_debug_print()`：除錯時列印權重名稱，方便確認結構對齊
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch11_burn_ai/05_burn_safetensors
//! cargo run --release
//! ```
//!
#![recursion_limit = "256"]

pub mod model; // 1. 宣告我們手動建立的 model 模組

use burn::{
    backend::Wgpu,
    module::Module,
    record::{FullPrecisionSettings, Recorder}, // 引入 Recorder Trait
    tensor::Tensor,
};
use burn_import::safetensors::{LoadArgs, SafetensorsFileRecorder}; // 2. 引入 Safetensors 載入器

use model::FCN; // 3. 引入我們手動定義的 FCN

type MyBackend = Wgpu<f32>;

fn main() {
    let device = Default::default();

    // 4. 建立一個 Safetensors 檔案載入器
    //    <FullPrecisionSettings> 代表我們期望以 f32 載入
    let recorder = SafetensorsFileRecorder::<FullPrecisionSettings>::default();

    let load_args = LoadArgs::new("simple_fcn.safetensors".into())
        .with_key_remap("model\\.(.*)", "$1")
        .with_debug_print(); // <--- 啟用除錯列印

    // 5. 載入權重到一個 "Record" 物件中
    let record = recorder.load(load_args, &device).expect("權重檔案載入失敗");

    // 6. 載入權重：
    //    先呼叫 ::init() 建立一個結構吻合的「空模型」
    //    再呼叫 .load_record() 將從檔案讀取的權重「裝填」進去
    let model = FCN::<MyBackend>::init(&device).load_record(record);

    println!("Safetensors 權重裝填成功！模型已準備就緒。");

    // (可選) 執行一次推論來驗證
    // FCN 期望 2D 輸入 [batch_size, input_features]
    let input = Tensor::<MyBackend, 2>::zeros([1, 10], &device);
    let output = model.forward(input);

    // 輸出 shape 應為 [1, 5]
    println!("模型成功執行，輸出 shape: {:?}", output.shape());
}
