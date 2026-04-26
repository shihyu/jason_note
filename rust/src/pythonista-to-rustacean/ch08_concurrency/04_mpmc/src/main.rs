//! # MPMC 通道：多生產者 → 多消費者
//!
//! 本範例展示 `crossbeam_channel` 的 MPMC（多生產者、多消費者）通道，支援 `clone()` 複製發送/接收端。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 多生產者 | `queue.Queue()` 自動支援 | `tx.clone()` 複製 transmitter |
//! | 多消費者 | `queue.Queue()` 自動支援 | `rx.clone()` 複製 receiver |
//! | 訊息競爭 | 佇列自動同步 | 消費者競爭接收訊息 |
//!
//! ## 架構圖
//!
//! ```text
//!        tx1 ──┐
//!              ├── MPMC 通道 ──┬── rx1 (消費者 1)
//!        tx2 ──┘            └── rx2 (消費者 2)
//! ```
//!
//! ## 執行緒競爭
//!
//! ```text
//! 消費者 1 和消費者 2 同時等待 rx.recv()
//! 誰先收到 → 不確定（看 OS 調度）
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch08_concurrency/04_mpmc
//! cargo run
//! ```

use crossbeam_channel::unbounded;
use std::thread;
fn main() {
    // 1. 建立一個 MPMC 通道
    let (tx1, rx1) = unbounded();

    // 2. 複製發送端 (Multiple Producer)
    let tx2 = tx1.clone();

    // 3. 複製接收端 (Multiple Consumer)
    let rx2 = rx1.clone();

    // 4. 建立多個發送者
    thread::spawn(move || {
        tx1.send("來自發送者 1").unwrap();
    });
    thread::spawn(move || {
        tx2.send("來自發送者 2").unwrap();
    });
    // 5. 建立多個接收者
    let handle1 = thread::spawn(move || {
        // rx1 和 rx2 會競爭訊息
        println!("接收者 1 收到: {}", rx1.recv().unwrap());
    });
    let handle2 = thread::spawn(move || {
        println!("接收者 2 收到: {}", rx2.recv().unwrap());
    });
    handle1.join().unwrap();
    handle2.join().unwrap();
}
