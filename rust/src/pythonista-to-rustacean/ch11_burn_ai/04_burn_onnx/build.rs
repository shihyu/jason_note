//!
//! # ONNX 模型建置腳本
//!
//! 此建置腳本使用 `burn-import` 將 ResNet18 ONNX 模型轉換為 Rust 程式碼。
//! 執行後會在 `onnx_infer/` 目錄生成對應的 Rust 模組。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! | 模型交換格式 | ONNX (.onnx) | burn-import 轉換 |
//! | 建置時生成碼 | `torch.onnx.export()` | `burn_import::onnx::ModelGen` |
//! | 輸出位置 | 同目錄 | `OUT_DIR/onnx_infer/` |
//!
//! ## 關鍵技法
//!
//! - `burn_import::onnx::ModelGen`：ONNX 到 Burn 模型轉換器
//! - `.input()`：指定輸入 ONNX 檔案路徑
//! - `.out_dir()`：設定產出 Rust 程式碼的目錄
//! - `.run_from_script()`：執行轉換並生成程式碼
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch11_burn_ai/04_burn_onnx
//! cargo build --release
//! ```
//!
//! 建置完成後，生成的 Rust 程式碼會輸出到 `onnx_infer/` 目錄。
//!
use burn_import::onnx::ModelGen;

fn main() {
    // 1. 實例化 ONNX 程式碼生成器
    ModelGen::new()
        // 2. 指定輸入的 .onnx 藍圖路徑 (相對於專案根目錄)
        .input("resnet18_Opset18_torch_hub.onnx")
        // 3. 指定生成的 .rs 檔案要放在「輸出目錄」的哪個子資料夾
        .out_dir("onnx_infer/")
        // 4. 執行翻譯！
        .run_from_script();
}
