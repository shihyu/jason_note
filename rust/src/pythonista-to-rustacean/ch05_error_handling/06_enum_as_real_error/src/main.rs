//! # `06_enum_as_real_error` - 實作 `std::error::Error` 特徵
//!
//! ## 概念說明
//!
//! 若要讓自訂錯誤與 Rust 生態系（如 `?`、`anyhow`、`thiserror`）相容，
//! 必須實作 `std::error::Error` + `std::fmt::Display`。
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │  實作 Error trait 的三個要件                                    │
//! │                                                               │
//! │   1. #[derive(Debug)]  ── 讓錯誤可被印出（除錯用）         │
//! │   2. impl Display    ── 給人類看的錯誤訊息                   │
//! │   3. impl Error     ── 給 Rust 生態系用的標準介面           │
//! │                                                               │
//! │   ┌──────────────────────────────────────────────┐           │
//! │   │  Display 實作                                │           │
//! │   │  match self {                               │           │
//! │   │      TooShort(len) => write!(f, "長度 {} 太短", len) │   │
//! │   │      MissingNumber => write!(f, "需要數字")  │           │
//! │   │  }                                          │           │
//! │   └──────────────────────────────────────────────┘           │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python 對照表
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 錯誤介面 | `BaseException` | `std::error::Error` trait |
//! | 顯示訊息 | `__str__` | `impl Display` |
//! | 除錯訊息 | `__repr__` | `#[derive(Debug)]` |
//! | 錯誤鏈 | `raise X from Y` | `Error::source()` |
//!
//! ## 重點解析
//!
//! - `Error` 的 `source()` 方法可回傳**錯誤鏈**（cause）
//! - `Display` 是給**使用者**看的訊息；`Debug` 是給**開發者**除錯用
//! - 簡單 enum 的 `impl Error {}` 內容通常為空（只需要 trait object）
//!
//! ## 執行方式
//!
//! ```bash
//! cargo run
//! ```
//!
//! ## 預期輸出
//!
//! ```text
//! 操作失敗：密碼長度 (5) 太短，至少需要 8 個字元。
//! ```

use std::error::Error;
use std::fmt; // 引入 Error 特徵

// 1. 實作 Debug ( 之前已做過)
#[derive(Debug)]
enum PasswordError {
    TooShort(usize), // <-- 變更：讓 enum 攜帶錯誤的長度
    MissingNumber,
}

// 2. 實作 Display (給使用者看)
impl fmt::Display for PasswordError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        // 根據不同的錯誤變體，撰寫友善的錯誤訊息
        match self {
            PasswordError::TooShort(len) => {
                write!(f, "密碼長度 ({}) 太短，至少需要 8 個字元。", len)
            }
            PasswordError::MissingNumber => write!(f, "密碼必須包含至少一個數字。"),
        }
    }
}
// 3. 實作 Error (給 Rust 生態系用)
// 對於簡單的 enum，內容通常是空的
impl Error for PasswordError {}

// --- 更新 SecurePassword 的實作 ---
#[derive(Debug)]
struct SecurePassword {
    value: String,
}

impl SecurePassword {
    pub fn new(password: &str) -> Result<Self, PasswordError> {
        if password.len() < 8 {
            // <-- 變更：傳入當前不正確的長度
            Err(PasswordError::TooShort(password.len()))
        } else if !password.chars().any(char::is_numeric) {
            Err(PasswordError::MissingNumber)
        } else {
            Ok(Self {
                value: password.to_string(),
            })
        }
    }
}

// --- 更新 main 函式 ---
fn main() {
    let pw_b = SecurePassword::new("12345"); // 這個會觸發 TooShort 錯誤
    match pw_b {
        Ok(pw) => println!("成功建立安全密碼：{:?}", pw),
        Err(e) => {
            // 現在 e 可以直接用 {} 印出了
            eprintln!("操作失敗：{}", e);
        }
    }
}