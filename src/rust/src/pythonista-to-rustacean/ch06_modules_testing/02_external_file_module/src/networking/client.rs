//! # 網路用戶端子模組 (Networking Client Submodule)
//!
//! 本範例展示 Rust 中**最細粒度的模組封裝**——每個子模組通常為一個獨立的 `.rs` 檔案。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 子模組位置 | `mymodule/submodule.py` | `src/outer/submodule.rs` |
//! | 宣告方式 | `from . import submodule` | `pub mod submodule;` |
//! | 公開 API | 函式與類別 | `pub fn` + `pub mod` |
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch06_modules_testing/02_external_file_module
//! cargo build && cargo run
//! ```
//!
//! ## 預期輸出
//!
//! ```text
//! PING!!
//! ```

pub fn ping() {
    println!("PING!!")
}
