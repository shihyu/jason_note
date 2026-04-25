//! # Rc：單執行緒參考計數（不可複製型別的共享）
//!
//! 本範例展示 `Rc<T>`（Reference Counted）如何讓**不可複製**的型別（如 `String`、`Vec`）在單執行緒中被多個擁有者共享。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 共享資料 | 多變數指向同一物件（GC）| `Rc::clone()` 增加計數 |
//! | 參考計數 | GC 自動追蹤 | `Rc::strong_count()` 手動查詢 |
//! | 計數歸零 | GC 回收記憶體 | 自動 Drop（無 GC）|
//!
//! ## 計數生命週期
//!
//! ```text
//! Rc::new(String)     → count = 1
//! Rc::clone(&data)    → count = 2
//! data_clone_1 超出作用域 → count = 1
//! data 超出作用域     → count = 0 → String 被 Drop
//! ```
//!
//! ## 限制：單執行緒
//!
//! ```text
//! Rc     → 單執行緒，簡單快速
//! Arc    → 多執行緒， atomic 計數
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch08_concurrency/06_rc
//! cargo run
//! ```

use std::rc::Rc;

fn main() {
    // 建立一個新的 Rc，計數器 = 1
    let data = Rc::new(String::from("共用資料"));
    println!("計數器: {}", Rc::strong_count(&data)); // 印出: 1
    {
        // 複製 Rc，計數器 = 2
        let data_clone_1 = Rc::clone(&data);
        println!("計數器: {}", Rc::strong_count(&data)); // 印出: 2
    } // data_clone_1 離開作用域，計數器 = 1
    println!("計數器: {}", Rc::strong_count(&data)); // 印出: 1
}
