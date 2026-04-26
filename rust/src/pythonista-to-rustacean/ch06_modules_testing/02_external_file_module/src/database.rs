//! # 資料庫模組 (Database Module)
//!
//! 本範例展示一個簡潔的**單檔模組**，用於封裝資料庫遷移功能。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 封裝單位 | 類別或函式 | `pub fn` 在模組內 |
//! | 呼叫方式 | `Database.migrate()` | `database::migrate()` |
//! | 隱藏實作 | 私有方法 `_migrate` | 不標記 `pub` 的項目 |
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
//! Database: Running migrations...
//! ```

// 這個檔案的「所有內容」，
// 就被視為 `database` 模組的內容。
pub fn migrate() {
    println!("Database: Running migrations...");
}
