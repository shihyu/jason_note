use pyo3::prelude::*;

#[pymodule]
mod enum2class_example {
//! # Enum to Python Class Mapping
//!
//! 本範例展示如何用 `#[pyclass]` 將 Rust enum 對應為 Python 類別。
//!
//! ## ASCII 架構圖
//! ```text
//! Rust Enum                    Python Class
//! ┌──────────────────────┐  ┌──────────────────────────────┐
//! │ #[pyclass]          │  │ class ExitCode:             │
//! │ enum ExitCode {     │  │     Success = 0           │
//! │     Success = 0,   │──│     GeneralError = 1       │
//! │     PermissionDen..│  │     PermissionDenied = 126  │
//! │ }                   │  │     CommandNotFound = 127  │
//! └──────────────────────┘  └──────────────────────────────┘
//!
//! 另一個 enum（攜帶資料）：
//! ┌──────────────────────┐  ┌──────────────────────────────┐
//! │ enum Notification {  │  │ class Notification:         │
//! │   Email {..},      │  │     Email                  │
//! │   Sms(..),         │──│     Sms                    │
//! │   NoOp(),          │  │     NoOp                   │
//! └──────────────────────┘  └──────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 概念 | Python | Rust (PyO3) |
//! |------|--------|--------------|
//! | 簡單 enum | `class ExitCode(IntEnum):` | `#[pyclass] enum ExitCode` |
//! | C 風格 enum | `class Codes:` | `#[pyclass(eq, eq_int)]` |
//! | 攜帶資料變體 | N/A | `Email { recipient, subject }` |
//!
//! ## Rust 特有概念
//!
//! - `#[pyclass(eq, eq_int)]`: 讓 C 風格 enum 可用整數比較
//! - 結構體變體 → Python 類別（需手動實作 `__new__` 或 `__init__`）

use pyo3::prelude::*;

    #[pyclass(eq, eq_int)]
    #[derive(PartialEq)]
    enum ExitCode {
        Success = 0,
        GeneralError = 1,
        // 根據 shell 標準，126 代表 "命令無法執行"
        PermissionDenied = 126,
        // 127 代表 "找不到命令"
        CommandNotFound = 127,
    }

    #[pyfunction]
    fn run_cli_tool(command: &str, as_root: bool) -> ExitCode {
        if command.starts_with("sudo") && !as_root {
            // 模擬權限不足的狀況
            return ExitCode::PermissionDenied;
        }
        if command.is_empty() {
            return ExitCode::CommandNotFound;
        }
        // ... 假設這裡有複雜的工具執行邏輯 ...
        println!("Executing command: '{}'", command);
        ExitCode::Success
    }

    #[pyclass]
    enum Notification {
        // 結構體變體：欄位有明確名稱
        Email { recipient: String, subject: String },
        // 元組變體：欄位沒有名稱
        Sms(String), // (電話號碼)

        // 不攜帶資料的變體，必須寫成空元組
        NoOp(),
    }

    #[pyfunction]
    fn create_notification(target: &str) -> Notification {
        if target.contains('@') {
            Notification::Email {
                recipient: target.to_string(),
                subject: "來自 Rust 的問候".to_string(),
            }
        } else {
            Notification::Sms(target.to_string())
        }
    }
}
