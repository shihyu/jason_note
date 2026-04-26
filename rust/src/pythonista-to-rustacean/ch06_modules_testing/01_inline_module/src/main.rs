//! # 內嵌模組 (Inline Module)
//!
//! 本範例展示如何在同一個 `.rs` 檔案中使用 `mod` 關鍵字定義**內嵌模組**。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 程式碼組織 | `class` / 模組檔案 | `mod` 區塊 |
//! | 隱藏實作 | `_private_func()` | 無標記 `pub` 的項目 |
//! | 公開 API | `def public_api()` | `pub fn public_api()` |
//! | 呼叫方式 | `module.func()` | `module::func()` |
//!
//! ## 架構圖
//!
//! ```text
//! main.rs (crate root)
//! └── config (inline module)
//!     ├── pub fn load_config()  ← 公開 API，main 可呼叫
//!     │   └── calls parse_env()
//!     └── fn parse_env()        ← 私有，僅內部使用
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch06_modules_testing/01_inline_module
//! cargo run
//! ```
//!
//! ## 預期輸出
//!
//! ```text
//! App running...
//! Loading configuration...
//! Parsing environment variables...
//! ```

// 應用程式的主要邏輯
fn main() {
    println!("App running...");
    // 透過 模組名稱:: 函式名稱 來呼叫
    config::load_config();
}

// ------------------------------------
// 定義一個名為 `config` 的內嵌模組
// ------------------------------------
mod config {
    // 標記為 `pub`，`main` 函式才能呼叫它
    pub fn load_config() {
        println!("Loading configuration...");
        // 模組可以有自己的內部輔助函式
        parse_env();
    }
    // 這個函式預設是私有的 (private)，
    // 只能在 `config` 模組內部被呼叫
    fn parse_env() {
        println!("Parsing environment variables...");
    }
}
