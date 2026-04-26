//! # Partially Moved：部分移動與欄位借用
//!
//! 本範例展示 Rust 中**部分移動**（partial move）的陷阱：
//! 當結構成員被移動出去後，整個結構體就**不能再使用**了。
//!
//! ## 部分移動的陷阱
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │              部分移動視覺化                                      │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                 │
//! │   struct Report { title: String, content: String }            │
//! │                                                                 │
//! │   let report = Report { ... };                                │
//! │                                                                 │
//! │   let title = report.title;  // title 移動出來                  │
//! │   //         ────────────────                                   │
//! │   //         report.title 的所有權移動到 title                   │
//! │   println!("{}", title);     // ✅ title 有效                  │
//! │   // report.title 已經無效！                                   │
//! │   process_report(report);    // ❌ 編譯錯誤！report 不完整      │
//! │                                                                 │
//! │   // 解決方案：借用語法                                        │
//! │   let title_ref = &report.title;  // 只借用，不移動              │
//! │   process_report(report);     // ✅ 正常！report 仍完整         │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Option 的部分移動
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │              Option 中的部分移動                                │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                 │
//! │   fn check_message(data: Option<String>) {                     │
//! │       match data {                                             │
//! │           Some(s) => println!("{}", s), // s 移動進入          │
//! │           None => ...                                          │
//! │       }                                                         │
//! │       // data 已被消耗，if data.is_some() 會錯誤                 │
//! │   }                                                            │
//! │                                                                 │
//! │   // 正確做法：借用                                             │
//! │   fn check_message_fixed(data: &Option<String>) {               │
//! │       match data.as_ref() { ... }  // 不移動，只窺視           │
//! │       if data.is_some() { ... }  // ✅ 正常                   │
//! │   }                                                            │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust：部分移動對照
//!
//! | 情境 | Python | Rust |
//! |------|---------|------|
//! | 解構取欄位 | `title = obj.title`（複製或參照）| `let title = obj.title`（**移動**）|
//! | 取欄位參照 | `title = obj.title`（不影響原物件）| `let title = &obj.title` |
//! | Option 取值 | `if let Some(s) = x: pass`（不消耗）| `match x { Some(s) => ... }`（消耗）|
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch03_ownership/07_use_of_partially_moved
//! cargo run
//! ```

struct Report {
    title: String,
    content: String,
}
// 一個消耗性的函式，它會取得 Report 的所有權
fn process_report(report: Report) {
    println!("正在處理報告：'{}'...", report.title);
    // ... 假設這裡有一些消耗性的操作
}

fn check_message(data: Option<String>) {
    match data {
        Some(s) => println!("訊息是：{}", s), // s 取得了 String 的所有權
        None => println!("沒有訊息"),
    }
    // if data.is_some() { // 💥 錯誤！
    //     println!(" 我的 data 裡有值");
    // }
}

fn check_message_fixed(data: &Option<String>) {
    // 改為接收參考
    match data.as_ref() {
        // 窺視內部，而非移動
        Some(s) => println!("訊息是：{}", s), // s 現在是 &String
        None => println!("沒有訊息"),
    }
    if data.is_some() {
        // OK! data 從未被移動
        println!("data 依然存在！");
    }
}

fn main() {
    /// Bad
    let report = Report {
        title: String::from("第三季財報"),
        content: String::from("本季營收穩健成長..."),
    };
    // 為了方便處理，我們將 title 欄位的所有權移出
    let title = report.title;
    println!("已取得報告標題：{}", title);
    // 接著，我們想把整個 report 交給另一個函式處理
    // process_report(report); // 💥 錯誤！

    /// Fixed
    let report = Report {
        title: String::from("第三季財報"),
        content: String::from("本季營收穩健成長..."),
    };
    // 透過 & 借用 title 欄位
    let title_ref = &report.title;
    println!("報告標題：{}", title_ref);

    // report 依然完整，可以繼續使用
    process_report(report); // OK!

    let my_message = Some(String::from("這是一則秘密訊息"));
    check_message_fixed(&my_message); // 傳遞參考
    println!("在 main 中，訊息依然可用：{:?}", my_message); // my_message 仍有效
}