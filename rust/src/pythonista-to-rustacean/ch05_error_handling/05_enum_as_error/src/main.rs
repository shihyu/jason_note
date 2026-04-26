//! # `05_enum_as_error` - 自訂錯誤 enum（精確匹配）
//!
//! ## 概念說明
//!
//! 將錯誤建模為 **enum** 而非字串，呼叫者可以：
//! 1. 精確知道錯誤種類
//! 2. 根據錯誤變體給予不同回應
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │  錯誤 enum 設計                                               │
//! │                                                               │
//! │   enum PasswordError {                                        │
//! │       TooShort,      // 密碼太短                              │
//! │       MissingNumber, // 缺少數字                              │
//! │   }                                                         │
//! │                                                               │
//! │   ┌──────────────────────────────────────────────┐           │
//! │   │  呼叫者精確匹配                          │           │
//! │   │  match e {                               │           │
//! │   │      TooShort      => "請延長密碼"       │           │
//! │   │      MissingNumber => "請加入數字"        │           │
//! │   │  }                                      │           │
//! │   └──────────────────────────────────────────────┘           │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python 對照表
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 錯誤種類 | 自訂 Exception 類別 | `enum ErrorType { Variant1, Variant2 }` |
//! | 精確匹配 | `except ValueError:` / `except TypeError:` | `match e { Error::V1 => ..., Error::V2 => ... }` |
//! | 錯誤攜帶資料 | `raise CustomError(msg)` | `Err(Error::Variant(data))` |
//! | 可擴展性 | 新增 Exception 類別 | 新增 enum 變體 |
//!
//! ## 重點解析
//!
//! - `#[derive(Debug)]`：讓錯誤可以被 `println!("{:?}")` 印出
//! - 比起 `&str`，enum 可以攜帶**結構化資料**（如長度不足時的實際長度）
//! - 呼叫者可以針對**每個變體**給予不同回應，而非統一的錯誤訊息
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
//! 錯誤：密碼必須包含至少一個數字。
//! ```

// 1. 定義一個具體的錯誤 enum
#[derive(Debug)] // 加上 Debug 以便印出或除錯
enum PasswordError {
    TooShort,
    MissingNumber,
}

#[derive(Debug)]
struct SecurePassword {
    value: String,
}

impl SecurePassword {
    // 2. 將回傳型別從 &str 改為我们自訂的 enum
    pub fn new(password: &str) -> Result<Self, PasswordError> {
        if password.len() < 8 {
            // 3. 回傳具體的 enum 變體
            Err(PasswordError::TooShort)
        } else if !password.chars().any(char::is_numeric) {
            // 3. 回傳具體的 enum 變體
            Err(PasswordError::MissingNumber)
        } else {
            Ok(Self {
                value: password.to_string(),
            })
        }
    }
}

fn main() {
    // 嘗試建立一個長度足夠，但沒有數字的密碼
    let pw_b = SecurePassword::new("abcdefghi");
    // 呼叫者現在可以精確地 match 錯誤了
    match pw_b {
        Ok(pw) => println!("成功建立安全密碼：{:?}", pw),
        Err(e) => match e {
            // 針對 PasswordError 進行巢狀 match
            PasswordError::TooShort => eprintln!("錯誤：密碼長度不足。"),
            PasswordError::MissingNumber => eprintln!("錯誤：密碼必須包含至少一個數字。"),
        },
    }
}