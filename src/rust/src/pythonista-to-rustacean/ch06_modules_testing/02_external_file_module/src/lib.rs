//! # 外置模組 (External File Module)
//!
//! 本範例展示如何將模組拆分到**不同檔案**，並透過 `pub mod` 宣告讓編譯器自動找到對應的 `.rs` 檔案。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 檔案組織 | `mymodule.py` + `mymodule/sub.py` | `src/lib.rs` + `src/networking.rs` |
//! | 匯入方式 | `from mymodule import func` | `use crate::module::func` |
//! | 隱藏實作 | `_private` 前綴 | 不標記 `pub` |
//! | 多層次組織 | 資料夾/子資料夾 | `pub mod` + 子模組檔案 |
//!
//! ## 架構圖
//!
//! ```text
//! src/
//! ├── lib.rs              ← 模組入口，宣告子模組
//! │   ├── pub mod networking;  → 找 networking.rs
//! │   │   └── pub mod client;  → networking/client.rs
//! │   └── pub mod database;    → database.rs
//! ├── networking.rs
//! │   └── client.rs
//! └── database.rs
//! ```
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
//! Initializing application...
//! Networking: Connecting...
//! PING!!
//! Database: Running migrations...
//! ```

// 宣告一個名為 `networking` 的模組。
// Rust 編譯器會自動去尋找 `src/networking.rs` 檔案。
// `pub` 表示這個模組本身也是 Crate 公開 API 的一部分。
pub mod networking;

// 宣告一個名為 `database` 的模組。
// Rust 編譯器會自動去尋找 `src/database.rs` 檔案。
pub mod database;
// 這個 Crate 的公開 API 可以組合來自不同模組的功能
pub fn initialize_app() {
    println!("Initializing application...");
    networking::connect();
    database::migrate();
}
