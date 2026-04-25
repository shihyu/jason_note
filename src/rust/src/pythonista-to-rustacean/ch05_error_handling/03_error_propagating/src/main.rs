//! # `03_error_propagating` - `?` 運算子與錯誤傳播
//!
//! ## 概念說明
//!
//! `?` 運算子是 Rust 最優雅的錯誤處理語法糖：
//! 成功時自動 unwrap 並繼續；失敗時**立即 return Err**。
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │  ? 運算子的行為                                                  │
//! │                                                               │
//! │   File::open("config.ini")?;                                 │
//! │         │                                                    │
//! │         ▼                                                    │
//! │   Ok(file)  ──► 繼續下一行                                  │
//! │   Err(e)    ──► return Err(e)  (提早退出)                   │
//! │                                                               │
//! │  ┌──────────────────────────────────────────────┐           │
//! │  │  match 版本 (冗長)                          │           │
//! │  │  let file = match File::open(...) {       │           │
//! │  │      Ok(f) => f,                         │           │
//! │  │      Err(e) => return Err(e),             │           │
//! │  │  };                                      │           │
//! │  └──────────────────────────────────────────────┘           │
//! │                                                               │
//! │  ┌──────────────────────────────────────────────┐           │
//! │  │  ? 版本 (簡潔)                              │           │
//! │  │  let mut file = File::open("config.ini")?; │           │
//! │  └──────────────────────────────────────────────┘           │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python 對照表
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 錯誤傳播 | `raise` / 回傳 None | `?` 運算子 |
//! | 提早退出 | `return None` / `return False` | `return Err(e)` |
//! | 鏈式錯誤處理 | `try/except` 巢狀 | `?` 鏈 |
//! | main 回傳錯誤 | `sys.exit(1)` | `Result<(), Box<dyn Error>>` |
//!
//! ## 重點解析
//!
//! - `?` 讓錯誤傳播**鏈式化**：`File::open()?; file.read_to_string()?;`
//! - `main() -> Result<(), Box<dyn Error>>` 允許 `?` 在 main 中使用
//! - `Box<dyn Error>` 是**彈性錯誤型別**，可容納任何實作 `Error` 的錯誤
//!
//! ## 執行方式
//!
//! ```bash
//! cargo run
//! ```
//!
//! ## 預期輸出（config.ini 不存在則印出錯誤）
//!
//! ```text
//! Config value: ... （或錯誤訊息）
//! ```

use std::error::Error;
use std::fs::File;
use std::io::{self, Read};

// 範例：從設定檔讀取一個值
fn read_config_value() -> Result<String, io::Error> {
    // 第一步：嘗試開啟檔案
    let file_result = File::open("config.ini");
    let mut file = match file_result {
        Ok(f) => f,
        Err(e) => return Err(e), // Failure: Propagate the error to the caller
    };
    // 第二步：嘗試讀取內容
    let mut content = String::new();
    match file.read_to_string(&mut content) {
        Ok(_) => Ok(content),    // Success: Return Ok(content)
        Err(e) => return Err(e), // Failure: Propagate again
    }
}

// '?' 運算子版本
fn read_config_value_with_q() -> Result<String, io::Error> {
    let mut file = File::open("config.ini")?; // 1. ?
    let mut content = String::new();
    file.read_to_string(&mut content)?; // 2. ?
    Ok(content)
}

// 觀察 main 函式的簽章
fn main() -> Result<(), Box<dyn Error>> {
    // 我們現在可以在 main 裡面使用 '?' 了！
    let config = read_config_value_with_q()?;
    println!("Config value: {}", config);
    // 如果一切順利，我們回傳 Ok(())
    Ok(())
}