//! # Rc + RefCell：單執行緒的內部可變性共享
//!
//! 本範例結合 `Rc<RefCell<T>>`，展示如何在**單執行緒**中讓多個擁有者共享且可變動同一份資料。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 共享且可變 | 多個指標指向同一 list | `Rc::clone()` + `RefCell` |
//! | 借用規則 | GC 動態處理 | 編譯期靜態 + 執行期動態檢查 |
//! | 觀察者模式 | 直接持有可變參考 | 持有 `Rc<RefCell<T>>` |
//!
//! ## 組合的意義
//!
//! ```text
//! Rc<T>       → 多個擁有者，共享 T
//! RefCell<T>  → 在 &self 上提供內部可變性
//! Rc<RefCell<T>> → 多個擁有者 + 可變 + 單執行緒
//! ```
//!
//! ## 借用規則（執行期檢查）
//!
//! ```text
//! .borrow()     → 不可變借用（類似 &T）
//! .borrow_mut() → 可變借用（類似 &mut T）
//! 同時有多個 borrow 時 panic！
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch08_concurrency/08_rc_refcell
//! cargo run
//! ```

use std::cell::RefCell;
use std::rc::Rc;

// 被共享的狀態
struct Subject {
    value: i32,
}

// 為了方便，使用型別別名
type SharedSubject = Rc<RefCell<Subject>>;

// 觀察者，它「共享」著 Subject
struct Observer {
    id: i32,
    subject: SharedSubject,
}
impl Observer {
    fn read_value(&self) {
        // 使用 .borrow() 進行不可變借用
        println!(
            "Observer {} 看到 value: {}",
            self.id,
            self.subject.borrow().value
        );
    }
}
fn main() {
    // 建立一個可共享、可變動的 Subject
    let subject: SharedSubject = Rc::new(RefCell::new(Subject { value: 0 }));
    // 建立兩個觀察者，它們都共享同一個 subject
    let observer1 = Observer {
        id: 1,
        subject: Rc::clone(&subject),
    };
    let observer2 = Observer {
        id: 2,
        subject: Rc::clone(&subject),
    };
    observer1.read_value(); // 0
    observer2.read_value(); // 0
    // 現在，我們從外部修改這個共享的狀態
    {
        // 使用 .borrow_mut() 取得可變借用
        subject.borrow_mut().value = 10;
    } // RefMut<T> 在這裡離開作用域，釋放借用
    println!("--- 狀態已改變 ---");
    // 兩個觀察者都能讀取到最新的值
    observer1.read_value(); // 10
    observer2.read_value(); // 10
}
