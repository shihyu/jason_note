//! # Move 關鍵字：所有權轉移進執行緒
//!
//! 本範例展示 `move` 如何將變數的**所有權**轉移進執行緒閉包，防止懸空參考。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 執行緒閉包捕獲 | 自動引用（GC 管理）| 預設借用，`move` 才能轉移所有權 |
//! | 資料所有權 | 無明確概念 | 明確的 `move` 語義 |
//! | 懸空參考 | 無（GC 保護）| 編譯期杜絕 |
//!
//! ## `move` 的作用
//!
//! ```text
//! 沒有 move：閉包借用語義
//! let handle = thread::spawn(|| { println!("{:?}", v) }); // 借用 v
//!
//! 有 move：    閉包取得所有權
//! let handle = thread::spawn(move || { println!("{:?}", v) }); // v 被轉移
//! ```
//!
//! ## 語意對照
//!
//! ```text
//! Python:  threading.Thread(target=fn, args=(data,))
//!           → 執行緒獲得資料的引用（Copy on Write，GC 保護）
//!
//! Rust:    thread::spawn(move || { ... })
//!           → 執行緒獲得資料的所有權（編譯期靜態保證）
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch08_concurrency/02_move_keyword
//! cargo run
//! ```

use std::thread;
fn main() {
    let v = vec![10, 20, 30];

    // 在閉包前加上 'move'
    let handle = thread::spawn(move || {
        // 現在閉包「擁有」 v
        println!("子執行緒取得所有權的向量：{:?}", v);
    });

    // 'v' 的所有權已經被轉移到 new thread
    // 下面這行會編譯失敗，因為 v 已不在 main 執行緒的作用域中
    // drop(v);
    handle.join().unwrap();
}
