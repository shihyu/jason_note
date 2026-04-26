//! 這個模組負責統整並導出所有模型（`Model` Trait 的實作）。
//!
//! 透過 `pub mod` 的方式，讓 `main.rs` 或其他模組可以
//! 輕易地存取到 `cnn`、`linear_manual` 與 `linear_nn`
//! 中定義的模型結構體。

pub mod cnn;
pub mod linear_manual;
pub mod linear_nn;
