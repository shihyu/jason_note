//! # 執行緒基礎：Spawn + Join
//!
//! 本範例展示 Rust 最基本的執行緒用法：`thread::spawn` 建立執行緒、`handle.join()` 等待結束。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 建立執行緒 | `threading.Thread(target=fn).start()` | `thread::spawn(|| {...})` |
//! | 等待執行緒 | `t.join()` | `handle.join().unwrap()` |
//! | 執行緒睡眠 | `time.sleep(ms)` | `thread::sleep(Duration::from_millis(ms))` |
//! | 閉包綁定 | 自動捕獲外部變數 | 預設借用，需 `move` 才能取得所有權 |
//!
//! ## 執行緒生命週期
//!
//! ```text
//! main thread ──────────────────────────────────
//!                │
//!                ├── thread::spawn(|| { ... }) ──┐
//!                │                             │ child thread
//!                │                             │
//!                │                      handle.join() ──┘
//!                │
//!                └── 主執行緒自己的工作...
//! ```
//!
//! ## 重點：`handle.join()` 阻塞 vs 不阻塞
//!
//! ```text
//! 不呼叫 join()：主執行緒繼續跑，不等子執行緒
//! 呼叫 join()：    主執行緒會等子執行緒跑完才繼續
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch08_concurrency/01_spawn_thread
//! cargo run
//! ```

use std::thread;
use std::time::Duration;

fn main() {
    let handle = thread::spawn(|| {
        for i in 1..=3 {
            println!("子執行緒：計數 {} ！ ", i);
            thread::sleep(Duration::from_millis(5));
        }
    });

    // handle.join().unwrap(); // 立刻阻擋，等同於序列執行

    // 在這裡，main 執行緒會繼續往下跑
    println!("主執行緒的訊息。");

    // 主執行緒也可以做自己的工作
    for i in 'a'..='b' {
        println!("主執行緒：字母 {}", i);
        thread::sleep(Duration::from_millis(1));
    }

    // 呼叫 .join() 來等待子執行緒結束
    // .unwrap() 是用於處理 join 可能回傳的 Err ( 如果子執行緒 panic)
    handle.join().unwrap();
    println!("主執行緒：子執行緒已結束。");
}
