//! # Exception Handling: Rust → Python Errors
//!
//! 本範例展示 PyO3 中 Rust 錯誤到 Python 例外的各種轉換方式。
//!
//! ## ASCII 架構圖
//! ```text
//! Rust Result 錯誤 → Python 例外
//! ┌─────────────────────────────────────────────────────────────┐
//! │  Result<T, ParseIntError>  ──自動轉換──→  TypeError       │
//! │  Result<T, io::Error>      ──map_err──→  OSError          │
//! │  Result<T, MyError>       ──From impl──→  ValueError     │
//! │  Result<T, JsonParseError>───Newtype──→  ValueError     │
//! │                                                           │
//! │  create_exception!(module, MyError, Base)                 │
//! │      └── 自訂 Python 例外類別                              │
//! └─────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 概念 | Python | Rust (PyO3) |
//! |------|--------|--------------|
//! | 定義例外 | `class MyError(Exception):` | `create_exception!(module, MyError, PyException)` |
//! | 拋出例外 | `raise ValueError("msg")` | `Err(PyValueError::new_err("msg"))` |
//! | 自動轉換 | N/A | `impl From<MyError> for PyErr` |
//! | 錯誤 enum | `class ErrorCode:` | `enum ExitCode { Success, Fail }` |
//!
//! ## Rust 特有概念
//!
//! - `create_exception!()`: 在模組外部建立 Python 例外類別
//! - `From<MyError> for PyErr`: 告訴 PyO3 如何將自訂錯誤轉換為 Python 例外
//! - `map_err()`: 將一種錯誤型別轉換為另一種（包裝上下文）

use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;

// 定義 Python 的專屬例外
// 步驟 1: 在 `mod` 區塊的外部，使用 create_exception! 來定義例外類型。
// - `exception_example` 應與模組名稱一致。
// - `InvalidInputError` 是我們想建立的例外類型名稱。
// - `PyException` 則是它在 Python 世界中要繼承的基礎例外。
create_exception!(exception_example, InvalidInputError, PyException);

#[pymodule]
mod exception_example {
    use super::*;

    use std::fs;
    use std::num::ParseIntError;
    use std::{error::Error, fmt};

    use pyo3::exceptions::{PyOSError, PyValueError};
    use pyo3::types::PyAny;
    use serde::Deserialize;
    use serde_json;

    /// 沿用 Rust 的錯誤處理習慣
    #[pyfunction]
    fn sum_as_i64(a: &Bound<'_, PyAny>, b: &Bound<'_, PyAny>) -> PyResult<i64> {
        // .extract() 本身就回傳 PyResult<T>
        // 如果 a 無法被轉換成 i64，? 會直接讓函式帶著 TypeError 提早回傳
        let num_a = a.extract::<i64>()?;

        // 同樣地，如果 b 無法被轉換，也會在這裡提早回傳
        let num_b = b.extract::<i64>()?;

        Ok(num_a + num_b)
    }

    /// 自動轉換：讓 Rust 錯誤化身為 Python 例外
    #[pyfunction]
    // 注意回傳型別是標準 Result，它會被 PyO3 自動轉換
    fn sum_as_i64_from_str(a: &str, b: &str) -> Result<i64, ParseIntError> {
        let num_a = a.parse::<i64>()?;
        let num_b = b.parse::<i64>()?;
        Ok(num_a + num_b)
    }

    /// 主動回報特定的內建例外
    #[pyfunction]
    fn read_user_age(path: &str) -> PyResult<u8> {
        // 步驟 1：處理底層 I/O 錯誤
        // 我們使用 map_err 將通用的 io::Error 轉換成帶有上下文的 PyOSError
        let content = fs::read_to_string(path)
            .map_err(|err| PyOSError::new_err(format!("無法讀取設定檔 '{}'：{}", path, err)))?;

        // 步驟 2：處理內容解析的錯誤
        // 我們再次使用 map_err 將 ParseIntError 轉換成更友善的 PyValueError
        let age = content
            .trim()
            .parse::<u8>()
            .map_err(|err| PyValueError::new_err(format!("設定檔內容非有效數字：{}", err)))?;

        // 步驟 3：處理商業邏輯的錯誤
        // 這裡的錯誤與任何底層操作無關，純粹是我們的邏輯要求
        if age > 150 {
            return Err(PyValueError::new_err(format!(
                "無效的年齡：{}，不能超過 150",
                age
            )));
        }

        Ok(age)
    }

    /// 為自訂錯誤啟用自動轉換
    // 1. 定義我們自己的 Rust 錯誤 enum，精確描述失敗原因
    #[derive(Debug)]
    enum ProfileParseError {
        MissingComma,
        InvalidAge(String), // 欄位用來存放解析失敗的字串內容
    }

    // 讓它成為一個合法的錯誤型別
    impl Error for ProfileParseError {}

    // 定義錯誤要如何被「顯示」出來
    impl fmt::Display for ProfileParseError {
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            match self {
                Self::MissingComma => write!(f, "格式錯誤，應為 '名字,年齡'"),
                Self::InvalidAge(s) => write!(f, "無效的年齡：'{}'", s),
            }
        }
    }

    // 2. 實作轉換規則：讓 PyO3 懂得如何將 ProfileParseError 轉換成 Python 例外
    impl From<ProfileParseError> for PyErr {
        fn from(err: ProfileParseError) -> PyErr {
            // 在這裡，我們統一將自訂錯誤轉換成 Python 的 ValueError，
            // 並將 Display 印出的訊息作為例外內容。
            PyValueError::new_err(err.to_string())
        }
    }

    // 3. 在 #[pyfunction] 中，就能直接回傳包含我們自訂錯誤的 Result
    #[pyfunction]
    fn parse_profile(profile_str: &str) -> Result<(String, u8), ProfileParseError> {
        let parts: Vec<&str> = profile_str.split(',').collect();
        if parts.len() != 2 {
            return Err(ProfileParseError::MissingComma);
        }

        let name = parts[0].to_string();
        match parts[1].trim().parse::<u8>() {
            Ok(age) => Ok((name, age)),
            Err(_) => Err(ProfileParseError::InvalidAge(parts[1].to_string())),
        }
    }

    /// 處理外部函式庫的錯誤：Newtype 模式
    // 這是一個我們希望能從 JSON 解析出來的目標結構
    #[derive(Deserialize)]
    struct User {
        name: String,
        age: u8,
    }

    // 1. 建立一個 Newtype，將 `serde_json::Error` 包裝起來
    //    這個 struct 現在是我們自己的型別。
    struct JsonParseError(serde_json::Error);

    // 2. 為我們的 Wrapper 實作 `From`，讓 `?` 能自動轉換
    //    這是為了告訴 Rust 編譯器：如何將外部錯誤 `serde_json::Error`，
    //    變成我們自己的 `JsonParseError`。
    impl From<serde_json::Error> for JsonParseError {
        fn from(err: serde_json::Error) -> Self {
            JsonParseError(err)
        }
    }

    // 3. 再次為我們的 Wrapper 實作 `From`，這次是為了 PyO3
    //    這是為了告訴 PyO3：如何將我們的 `JsonParseError`，
    //    變成 Python 的例外物件 `PyErr`。
    impl From<JsonParseError> for PyErr {
        fn from(err: JsonParseError) -> PyErr {
            PyValueError::new_err(err.0.to_string())
        }
    }

    #[pyfunction]
    // 4. 函式的回傳型別，使用我們自己的錯誤 Wrapper
    fn user_from_json(json_str: &str) -> Result<(String, u8), JsonParseError> {
        // serde_json::from_str 回傳 Result<User, serde_json::Error>
        // 當它失敗時，? 會透過步驟 2 的規則，將錯誤自動轉為 JsonParseError
        let user: User = serde_json::from_str(json_str)?;
        Ok((user.name, user.age))
    }

    /// 定義 Python 的專屬例外
    // 步驟 2: 使用 `#[pymodule_export]` 將外部定義的 `InvalidInputError` 類型匯入。
    // 如此一來，Python 就能以 `exception_example.InvalidInputError` 的形式存取它。
    #[pymodule_export]
    use super::InvalidInputError;

    #[pyfunction]
    fn validate_input(input: &str) -> PyResult<()> {
        if input == "bad" {
            // 步驟 3: 使用 new_err 方法來建立一個新的例外實例並回傳。
            // PyO3 看到這個 Result::Err，就會在 Python 端將它轉換為
            // `raise InvalidInputError(...)` 的行為。
            return Err(InvalidInputError::new_err("輸入的內容不能是 'bad'"));
        }
        Ok(())
    }
}
