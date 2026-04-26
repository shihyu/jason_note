//! # `04_constructor` - 建構子回傳 Result（密碼驗證）
//!
//! ## 概念說明
//!
//! Rust 的建構子（Constructor）慣例：
//! **驗證失敗 → 回傳 `Err`**，而非 `panic!`。
//! 這樣呼叫者有權決定如何處理（使用預設值、重試、告知使用者等）。
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │  Result 建構子流程                                              │
//! │                                                               │
//! │   SecurePassword::new("12345")                               │
//! │              │                                                │
//! │              ▼                                                │
//! │   password.len() < 8  ?                                      │
//! │      │                                                        │
//! │      ├─ true  ──► Err("密碼長度不足...")                   │
//! │      │                                                        │
//! │      └─ false ──► Ok(SecurePassword { value })             │
//! │                                                               │
//! │  ┌──────────────────────────────────────────────┐           │
//! │  │  呼叫者處理方式                            │           │
//! │  │  match pw_a {                            │           │
//! │  │      Ok(pw) => ...,                      │           │
//! │  │      Err(e) => eprintln!("{}", e),       │           │
//! │  │  }                                      │           │
//! │  └──────────────────────────────────────────────┘           │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python 對照表
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 建構失敗表示 | 回傳 `None` / 拋例外 | 回傳 `Result<T, E>` |
//! | 驗證邏輯位置 | `__init__` 內拋 ValueError | 建構子內回傳 `Err` |
//! | 呼叫者處理 | `try/except` | `match` / `?` |
//! | 錯誤訊息 | exception message | `Err` 中的字串或 enum |
//!
//! ## 重點解析
//!
//! - 建構子回傳 `Result` 是 **Rust 慣例**（不同於 Java/C++ 的例外）
//! - 驗證失敗不回 `panic!`，而是**將控制權交還呼叫者**
//! - 使用 `eprintln!` 而非 `println!` 區分錯誤輸出
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
//! 成功建立安全密碼：SecurePassword { value: "a-strong-password" }
//! 建立密碼 B 失敗：密碼長度不足，至少需要 8 個字元。
//! ```

#[derive(Debug)]
struct SecurePassword {
    value: String,
}

impl SecurePassword {
    // 建構子回傳 Result
    pub fn new(password: &str) -> Result<Self, &'static str> {
        if password.len() < 8 {
            // 驗證失敗，回傳中文 Err
            Err("密碼長度不足，至少需要 8 個字元。")
        } else {
            // 驗證成功
            Ok(Self {
                value: password.to_string(),
            })
        }
    }
}

fn main() {
    let pw_a = SecurePassword::new("a-strong-password");
    let pw_b = SecurePassword::new("12345"); // 嘗試建立一個無效的密碼
                                              // 處理 pw_a
    match pw_a {
        Ok(pw) => println!("成功建立安全密碼：{:?}", pw),
        Err(e) => eprintln!("建立密碼 A 失敗：{}", e), // 注意: eprintln!
    }
    // 處理 pw_b
    match pw_b {
        Ok(pw) => println!("成功建立安全密碼：{:?}", pw),
        Err(e) => eprintln!("建立密碼 B 失敗：{}", e), // 注意: eprintln!
    }
}