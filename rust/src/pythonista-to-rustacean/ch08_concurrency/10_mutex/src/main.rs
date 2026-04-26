//! # Mutex + Arc：安全的多執行緒共享可變狀態
//!
//! 本範例展示 `Arc<Mutex<T>>`——執行緒安全的多執行緒共享可變狀態，是 Rust 並行編程的核心模式。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 鎖保護 | `threading.Lock()` | `Mutex::new()` |
//! | 取得鎖 | `with lock:` / `lock.acquire()` | `mutex.lock().unwrap()` |
//! | 釋放鎖 | context manager 自動釋放 | RAII：Guard 離開作用域自動釋放 |
//! | 執行緒共享 | `multiprocessing.Manager().list()` | `Arc::clone()` |
//!
//! ## `Arc<Mutex<T>>` 組合
//!
//! ```text
//! Arc    → 跨執行緒共享指標（atomic 計數）
//! Mutex  → 執行緒安全可變性（一次只有一個執行緒能訪問）
//! Arc<Mutex<T>> → 多人共享 + 一次只有一人能改
//! ```
//!
//! ## MutexGuard 的 RAII 語意
//!
//! ```text
//! let guard = mutex.lock().unwrap();
//! // ... 使用 guard ...
//! guard 離開作用域 ──────> 鎖自動釋放
//! ```
//!
//! 這與 Python 的 `with lock:` 語義相同，但 Rust 是**編譯期靜態**確保不會忘記釋放。
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch08_concurrency/10_mutex
//! cargo run
//! ```

use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    // 1. 建立一個被 Mutex 保護、並被 Arc 共享的 Vec
    // shared_log 的型別是 Arc<Mutex<Vec<String>>>
    let shared_log = Arc::new(Mutex::new(vec![]));
    let mut handles = vec![];
    // 2. 建立 5 個執行緒
    for i in 0..5 {
        // 3. 複製 Arc ( 只增加引用計數，非常快)
        // 我們將這個複製的 Arc「move」到新執行緒中
        let log_clone = Arc::clone(&shared_log);
        let handle = thread::spawn(move || {
            // 4. 鎖定 Mutex，取得 MutexGuard
            // .lock() 會阻擋，直到取得鎖
            let mut log = log_clone.lock().unwrap();
            // 5. 修改資料 (log 是 MutexGuard<Vec<String>>)
            log.push(format!("執行緒 {} 登入", i));
            // 6. 'log' (MutexGuard) 在此離開作用域，鎖自動釋放
        });
        handles.push(handle);
    }
    // 7. 等待所有 5 個執行緒都完成
    for handle in handles {
        handle.join().unwrap();
    }
    // 8. 鎖定並印出最終日誌內容
    println!("--- 最終日誌 ---");
    let log = shared_log.lock().unwrap();
    for entry in log.iter() {
        println!("{}", entry);
    }
    println!("日誌總條數: {}", log.len()); // 應印出 5
}
