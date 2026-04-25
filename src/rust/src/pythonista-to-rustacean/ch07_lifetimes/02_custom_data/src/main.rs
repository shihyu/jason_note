//! # 自訂資料結構與生命週期 (Custom Data with Lifetimes)
//!
//! 本範例展示當 struct 或 enum 持有參考時，必須為其標注**生命週期參數**。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 泛型生命週期 | 無 | `<'a>` 標注在型別後 |
//! | 結構體持參考 | 通常複製而非借用 | 明確標注 `&'a str` |
//! | 生命週期繼承 | 無 | 跟隨結構體實例 |
//!
//! ## Struct + 生命週期
//!
//! ```text
//! struct CourseProgress<'a> {
//!     excuse:   &'a str,   // 借用的資料，壽命由外部擁有者決定
//!     framework: &'a str,
//! }
//!
//! 'a 不代表「資料活多久」
//! 而是「這兩個 &str 參考，與結構體本身活得一样久」
//! ```
//!
//! ## Enum + 生命週期
//!
//! ```text
//! enum OnboardingStep<'a> {
//!     WelcomeMessage(&'a str),
//!     TutorialVideo(&'a str),
//! }
//! ```
//!
//! ## `impl` 區塊的省略規則
//!
//! ```text
//! 規則：若只有一個輸入參考（&self/&mut self），
//!       編譯器自動將回傳值生命週期與 &self 綁定。
//!
//! // 編譯器自動推斷：
//! fn procrastination(&self) -> &str { self.excuse }
//! // 等同於：fn procrastination<'a>(&'a self) -> &'a str { ... }
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch07_lifetimes/02_custom_data
//! cargo run
//! ```

// 結構體：教學地獄生存指南
struct CourseProgress<'a> {
    excuse: &'a str,    // 為什麼還沒完成專案的理由
    framework: &'a str, // 這週正在學的第三個框架
}

// 同樣地，如果 enum 需要持有參考，也必須標註：
enum OnboardingStep<'a> {
    WelcomeMessage(&'a str),
    TutorialVideo(&'a str),
}

// 必須宣告 <'a> 以匹配 CourseProgress<'a> 的型別定義，
// 無論內部的方法是否實際使用了該生命週期參數。
impl<'a> CourseProgress<'a> {
    // 省略規則自動處理了生命週期：
    // 編譯器會隱式地將回傳值 &str 的生命週期與 &self 綁定。
    fn procrastination(&self) -> &str {
        self.excuse
    }

    // 即便此方法不需要回傳參考，也未直接使用 'a，
    // 它依然必須定義在宣告了生命週期的 impl 區塊中。
    fn current_framework_count(&self) -> u32 {
        // 假設 'framework' 欄位是一個用逗號分隔的字串
        if self.framework.is_empty() {
            0
        } else {
            self.framework.split(',').count() as u32
        }
    }
}
fn main() {
    println!("Hello, world!");
}
