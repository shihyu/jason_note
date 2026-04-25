//!
//! # Safetensors 模型載入與推論
//!
//! 此模組展示如何使用 Burn 框架載入由 Python (PyTorch) 匯出的 Safetensors 格式模型。
//! 定義了一個三層全連接網路 (FCN)，用於演示 Rust 與 Python 模型權重的相容性。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! | 模型定義 | `nn.Linear(in, out)` | `Linear::new()` |
//! | 無 bias 層 | `bias=False` | `.with_bias(false)` |
//! | 模組衍生 | `nn.Module` | `#[derive(Module)]` |
//! | 前饋運算 | `forward(x)` | `forward(&self, x)` |
//!
//! ## 關鍵技法
//!
//! - `#[derive(Module)]`：為結構體自動實作 Burn 的 `Module` trait
//! - `LinearConfig::new()`：建立線性層的設定組態器
//! - `.with_bias(false)`：明確指定不使用 bias，須與 PyTorch 模型精確匹配
//! - `Tensor<B, 2>`：Burn 的二維張量型別 (Batch, Features)
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch11_burn_ai/05_burn_safetensors
//! cargo run --release
//! ```
//!
use burn::{
    nn::{Linear, LinearConfig},
    prelude::*,
};

#[derive(Module, Debug)]
pub struct FCN<B: Backend> {
    fc1: Linear<B>,
    fc2: Linear<B>,
    fc3: Linear<B>,
}

impl<B: Backend> FCN<B> {
    /// 建立一個「空」的模型實例
    /// 結構必須與 PyTorch 版本匹配
    pub fn init(device: &B::Device) -> Self {
        // 匹配 PyTorch: self.fc1 = nn.Linear(10, 50)
        // (預設有 bias)
        let fc1 = LinearConfig::new(10, 50).init(device);

        // 匹配 PyTorch: self.fc2 = nn.Linear(50, 20, bias=False)
        // 必須明確指定 .with_bias(false)！
        let fc2 = LinearConfig::new(50, 20)
            .with_bias(false) // <--- 必須精確匹配 PyTorch 的設定
            .init(device);

        // 匹配 PyTorch: self.fc3 = nn.Linear(20, 5)
        // (預設有 bias)
        let fc3 = LinearConfig::new(20, 5).init(device);

        Self { fc1, fc2, fc3 }
    }

    pub fn forward(&self, x: Tensor<B, 2>) -> Tensor<B, 2> {
        let x = self.fc1.forward(x);
        let x = self.fc2.forward(x);
        self.fc3.forward(x)
    }
}
