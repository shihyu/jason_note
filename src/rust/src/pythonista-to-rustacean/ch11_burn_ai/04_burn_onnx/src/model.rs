//!
//! # ONNX 模型載入與推論
//!
//! 此模組展示如何在 Rust 中載入並使用由 `build.rs` 生成的 ONNX 模型。
//! 透過 `include!` 巨集在編譯時嵌入生成的程式碼，建立與 PyTorch 訓練模型相容的推論介面。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! | 模型格式 | ONNX | Rust 程式碼 (burn-import 生成) |
//! | 編譯期嵌入 | `torch.jit.load()` | `include!()` 巨集 |
//! | 模型來源 | Hub/本地 ONNX | 由 build.rs 生成 |
//!
//! ## 關鍵技法
//!
//! - `include!()`：編譯時嵌入其他檔案的內容
//! - `concat!()` + `env!()`：動態組建置輸出目錄中的檔案路徑
//! - `env!("OUT_DIR")`：取得 build script 的輸出目錄
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch11_burn_ai/04_burn_onnx
//! cargo run --example resnet18_infer
//! ```
//!
pub mod my_resnet {
    // 透過 include! 巨集，將建置時期生成的 .rs 檔案內容
    // 在編譯時「貼上」到這個模組中。
    include!(concat!(
        env!("OUT_DIR"),
        "/onnx_infer/resnet18_Opset18_torch_hub.rs"
    ));
}
