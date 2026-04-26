//! # 網路模組 (Networking Module)
//!
//! 本範例展示**多層次模組組織**——在 `networking.rs` 中再宣告 `client` 子模組。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 巢狀組織 | `package/sub/module.py` | `mod outer { pub mod inner }` |
//! | 相對引用 | `from . import sub` | `mod inner; inner::func()` |
//! | 公開程度 | `__all__` 控制 | `pub` 層層標記 |
//!
//! ## 架構圖
//!
//! ```text
//! networking (networking.rs)
//! ├── pub mod client;  → 找 networking/client.rs
//! │   └── pub fn ping()
//! └── pub fn connect()
//!     └── client::ping()
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch06_modules_testing/02_external_file_module
//! cargo build && cargo run
//! ```

// 宣告 `client` 子模組
// 編譯器會尋找 `src/networking/client.rs`
// `pub` 使 `client` 模組也能被 `networking` 模組的外部看見
pub mod client;

// 這個檔案的「所有內容」，
// 就被視為 `networking` 模組的內容。
pub fn connect() {
    println!("Networking: Connecting...");
    // 我們可以從這裡呼叫子模組的功能
    client::ping();
}
