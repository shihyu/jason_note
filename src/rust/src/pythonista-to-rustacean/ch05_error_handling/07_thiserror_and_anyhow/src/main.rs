//! # `07_thiserror_and_anyhow` - thiserror 宏與錯誤自動轉換
//!
//! ## 概念說明
//!
//! `thiserror` 是用於**定義錯誤型別**的宏，
//! 大幅簡化 `Error` + `Display` 的 boilerplate。
//! `#[from]` 屬性更可自動產生 `From` 實作，讓 `?` 自動轉換錯誤型別。
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │  thiserror 簡化後的錯誤定義                                      │
//! │                                                               │
//! │   #[derive(Error, Debug)]                                      │
//! │   enum PasswordError {                                        │
//! │       #[error("長度 ({0}) 太短，至少需要 8 個字元。")]         │
//! │       TooShort(usize),                                        │
//! │       #[error("必須包含數字")]                                │
//! │       MissingNumber,                                          │
//! │   }                                                           │
//! │                                                               │
//! │  ┌──────────────────────────────────────────────┐           │
//! │  │  #[from] 自動錯誤轉換                      │           │
//! │  │                                           │           │
//! │  │  enum RegistrationError {                │           │
//! │  │      #[from]                             │           │
//! │  │      InvalidPassword(PasswordError),      │           │
//! │  │      TermsReadError(#[from] io::Error),  │           │
//! │  │  }                                      │           │
//! │  │                                           │           │
//! │  │  read_to_string("f")?  ◄── io::Error    │           │
//! │  │         │                              │           │
//! │  │         ▼ #[from]                      │           │
//! │  │  RegistrationError::TermsReadError     │           │
//! │  └──────────────────────────────────────────────┘           │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python 對照表
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 錯誤定義 | `class MyError(Exception):` | `#[derive(Error)]` + `thiserror` |
//! | 錯誤訊息格式化 | `def __str__(self): f"..."` | `#[error("...")]` |
//! | 錯誤轉換 | `except KeyError as e: raise ValueError() from e` | `#[from]` + `?` |
//! | 統一錯誤入口 | `except Exception as e:` | `Box<dyn Error>` |
//!
//! ## 重點解析
//!
//! - `#[from]` 讓 `?` **自動呼叫 `From::from()`** 轉換錯誤型別
//! - `thiserror` 產生的 `Display` 代碼完全由 attribute 描述，零 boilerplate
//! - `anyhow` 是另一 crate，適合**應用層**（如 main）動態錯誤；`thiserror` 適合**函式庫**
//!
//! ## 執行方式
//!
//! ```bash
//! cargo run
//! ```
//!
//! ## 預期輸出（terms.txt 不存在則印出錯誤）
//!
//! ```text
//! 操作失敗：密碼長度 (5) 太短，至少需要 8 個字元。
//! 失敗啦：無法讀取使用者條款檔案：...
//! ```

// 1. 引入 thiserror::Error
use thiserror::Error;

// 2. 加上 #[derive(Error, Debug)]
#[derive(Error, Debug)]

enum PasswordError {
    // 3. 使用 #[error("...")] 來定義 Display 實作
    #[error("密碼長度 ({0}) 太短，至少需要 8 個字元。")]
    TooShort(usize),
    #[error("密碼必須包含至少一個數字。")]
    MissingNumber,
}

#[derive(Debug)]
struct SecurePassword {
    value: String,
}
impl SecurePassword {
    pub fn new(password: &str) -> Result<Self, PasswordError> {
        if password.len() < 8 {
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

#[derive(Error, Debug)]
enum RegistrationError {
    // #[from] 會自動產生 From<PasswordError>
    // 這使得 ? 運算子可以自動轉換錯誤
    #[error("提供的密碼無效：{0}")]
    InvalidPassword(#[from] PasswordError),
    // 同樣地，自動從 std::io::Error 轉換
    #[error("無法讀取使用者條款檔案：{0}")]
    TermsReadError(#[from] std::io::Error),
    // 一個不包含 #[from] 的自訂變體
    #[error("使用者名稱 '{username}' 已被使用")]
    UsernameTaken { username: String },
}

#[derive(Debug)]
struct User {
    username: String,
    password: SecurePassword,
}

// 我們的函式現在可以回傳 RegistrationError
fn register_user(username: &str, pw_str: &str) -> Result<User, RegistrationError> {
    // 1. 呼叫 read_to_string，它回傳 Result<String, io::Error>
    // 如果失敗，? 會自動將 io::Error 轉換為 RegistrationError::TermsReadError
    let _terms = std::fs::read_to_string("terms.txt")?;
    // 2. 呼叫 SecurePassword::new，它回傳 Result<Self, PasswordError>
    // 如果失敗，? 會自動將 PasswordError 轉換為 RegistrationError::InvalidPassword
    let password = SecurePassword::new(pw_str)?;
    // 3. 檢查資料庫 ( 假設 "admin" 已被佔用)
    if username == "admin" {
        return Err(RegistrationError::UsernameTaken {
            username: username.to_string(),
        });
    }
    Ok(User {
        username: username.to_string(),
        password,
    })
}

fn main() {
    let pw_b = SecurePassword::new("12345"); // 這個會觸發 TooShort 錯誤
    match pw_b {
        Ok(pw) => println!("成功建立安全密碼：{:?}", pw),
        Err(e) => {
            eprintln!("操作失敗：{}", e);
        }
    }

    let user = register_user("", "");
    match user {
        Ok(user) => println!("{:?}", user),
        Err(e) => {
            eprint!("失敗啦：{}", e)
        }
    }
}