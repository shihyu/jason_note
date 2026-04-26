//! # Arc：原子參考計數（跨執行緒共享）
//!
//! 本範例展示 `Arc<T>`（Atomic Reference Counted）如何在**多執行緒**中安全共享資料。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 多執行緒共享 | `multiprocessing.Manager().list()` | `Arc::clone()` |
//! | 執行緒安全參考 | GC 保護 | `Arc` 原子計數 |
//! | 計數歸零 | GC 回收 | 自動 Drop（無 GC）|
//!
//! ## Arc vs Rc
//!
//! ```text
//! Rc   → 單執行緒，non-atomic（快速）
//! Arc  → 多執行緒，atomic（慢一些，但安全）
//! ```
//!
//! ## 生命週期
//!
//! ```text
//! Arc::new(data)        → count = 1
//! Arc::clone(&data)     → count = 2
//! data_clone 被 move 進執行緒 → 執行緒結束 → count = 1
//! 主執行緒結束            → count = 0 → data 被 Drop
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch08_concurrency/09_arc
//! cargo run
//! ```

use std::sync::Arc;
use std::thread;

fn main() {
    // 1. 使用 Arc::new 建立，計數器 = 1
    let data = Arc::new(String::from("跨執行緒共用資料"));
    // 2. 使用 Arc::clone 複製指標，計數器 = 2
    let data_clone = Arc::clone(&data);
    let handle = thread::spawn(move || {
        // 3. data_clone 的所有權被移入新執行緒
        println!("子執行緒看到: {}", data_clone);
        // 4. 執行緒結束，data_clone 離開作用域，計數器 = 1
    });
    // 5. 主執行緒依然擁有 data
    println!("主執行緒看到: {}", data);
    handle.join().unwrap(); // 等待子執行緒結束
    // 6. 主執行緒結束，data 離開作用域，計數器 = 0，資料釋放
}
