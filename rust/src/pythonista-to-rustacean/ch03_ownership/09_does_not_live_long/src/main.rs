//! # Dangling Reference：懸空參考
//!
//! 本範例展示 Rust 最重要規則之一：**參考的生命週期必須被它指向的資料所涵蓋**。
//! 試圖建立一個指向已銷毀資料的參考，稱為「懸空參考」，Rust 在**編譯期**就會阻止。
//!
//! ## 懸空參考的視覺化
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │              懸空參考的形成                                      │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                 │
//! │   let config_ref: &Config;        // 宣告一個參考                 │
//! │                                                                 │
//! │   {                                // 臨時作用域                  │
//! │       let temp_config = Config {                                │
//! │           value: String::from("臨時設定"),                       │
//! │       };                                                        │
//! │       config_ref = &temp_config;  // ❌ 參考指向即將銷毀的資料  │
//! │   } // temp_config 在此被 drop                                  │
//! │                                                                 │
//! │   // config_ref 指向的資料已消失！                              │
//! │   println!("{}", config_ref.value);  // 懸空參考！               │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## 正確的生命週期涵蓋
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │              正確的生命週期涵蓋                                  │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                 │
//! │   let main_config = Config { ... };   // 主要設定                 │
//! │        │                                                               │
//! │        ▼                                                               │
//! │   let config_ref = &main_config;   // OK!                          │
//! │   //        ────────────────────────                               │
//! │   //        main_config 的生命週期涵蓋了 config_ref                │
//! │   //        config_ref 存活多久，main_config 就活多久              │
//! │                                                                 │
//! │   println!("{}", config_ref.value);  // ✅ 安全使用                 │
//! │   } // main_config 最後被 drop                                  │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust：生命週期
//!
//! | 情境 | Python | Rust |
//! |------|---------|------|
//! | 臨時物件 | `return obj.method()`（GC 回收）| 編譯期確保無懸空參考 |
//! | 參考存活判斷 | GC 运行时追蹤 | 編譯期分析生命週期 |
//! | 錯誤處理 | `None` 或異常 | 編譯錯誤 |
//!
//! ## Rust 的承諾
//!
//! Rust 編譯器能靜態證明：**任何參考永遠有效**。
//! 不會有 use-after-free，不會有 dangling pointer。
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch03_ownership/09_does_not_live_long
//! cargo run
//! ```

struct Config {
    value: String,
}

fn main() {
    let config_ref: &Config; // 宣告一個設定檔參考，生命週期始於此

    /// Bad
    {
        // 在一個臨時的作用域中，我們建立了一個臨時設定
        let temp_config = Config {
            value: String::from("臨時設定"),
        };
        // config_ref = &temp_config; // 💥 錯誤！
    } // `temp_config` 在此被銷毀

    // 當我們想使用時，它指向的資料早已消失
    // println!(" 使用的設定是: {}", config_ref.value);

    /// Fixed
    // 將主要設定檔移到與參考相同或更長的作用域
    let main_config = Config {
        value: String::from("主要設定"),
    };
    let config_ref = &main_config; // OK! `main_config` 的生命週期涵蓋了 `config_ref`
    println!("使用的設定是: {}", config_ref.value);
}