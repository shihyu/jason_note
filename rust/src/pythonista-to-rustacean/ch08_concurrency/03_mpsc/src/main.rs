//! # MPSC 通道：單生產者 → 單消費者
//!
//! 本範例展示 Rust 標準庫的 `mpsc::channel`——單生產者、單消費者的訊息傳遞。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 通道建立 | `queue.Queue()` | `mpsc::channel()` |
//! | 發送訊息 | `queue.put(data)` | `tx.send(data).unwrap()` |
//! | 接收訊息 | `queue.get()` | `rx.recv().unwrap()` |
//! | 所有權轉移 | 無（GC）| `send()` 轉移所有權 |
//!
//! ## 通道運作
//!
//! ```text
//! tx (transmitter) ──────── 通道 ────────> rx (receiver)
//!         │                                        │
//!         └── send(val)  ──────────────────>  recv()
//!                                                       │
//!                                               主執行緒 unblocked
//! ```
//!
//! ## `.send()` 會轉移所有權
//!
//! ```text
//! tx.send(val)      → val 的所有權被轉移到接收端
//! println!("{}", val);  → 編譯錯誤！val 已被移走
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch08_concurrency/03_mpsc
//! cargo run
//! ```

use std::sync::mpsc;
use std::thread;

fn main() {
    // 建立一個通道 (tx = transmitter, rx = receiver)
    let (tx, rx) = mpsc::channel();

    thread::spawn(move || {
        let val = String::from("來自子執行緒的訊息");
        println!("子執行緒：準備發送...");
        // (1) .send() 會取得 val 的所有權
        tx.send(val).unwrap();
        // (2) 下面這行無法編譯！
        // println!(" 子執行緒：val is {}", val);
    });

    // (3) .recv() 會阻擋主執行緒，直到有訊息進來
    let received = rx.recv().unwrap();
    println!("主執行緒：收到訊息: {}", received);
}
