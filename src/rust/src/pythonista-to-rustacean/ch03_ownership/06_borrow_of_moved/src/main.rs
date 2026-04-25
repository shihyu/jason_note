//! # Borrow of Moved：迭代中的借用
//!
//! 本範例展示 `for ... in` 迴圈中的**所有權陷阱**：
//! 直接迭代會**移動**集合的所有權，借用迭代則只**借用**。
//!
//! ## for 迴圈的兩種模式
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │              for 迴圈的所有權行為                                 │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                 │
//! │  直接迭代（移動所有權）                                          │
//! │  ─────────────────────────────                                   │
//! │  for task in tasks {          // tasks 的所有權移動到迴圈       │
//! │      println!("{}", task);     // task 取得每個元素的所有權     │
//! │  }                             // 迴圈結束，tasks 已被消耗    │
//! │  println!("{:?}", tasks);     // ❌ 編譯錯誤！                 │
//! │                                                                 │
//! │  借用迭代（只借用）                                            │
//! │  ─────────────────────────                                   │
//! │  for task in &tasks {        // 只借用，tasks 不會被移動       │
//! │      println!("{}", task);    // task 是 &String 參考         │
//! │  }                             // 迴圈結束，借用結束           │
//! │  println!("{:?}", tasks);     // ✅ 正常！tasks 仍有效        │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust：迭代中的所有權
//!
//! | 情境 | Python | Rust |
//! |------|---------|------|
//! | 迭代 list | `for x in list:`（複製元素）| `for x in &list:`（借用）|
//! | 移動所有權 | `for x in list:`（參照）| `for x in list:`（移動所有權）|
//! | 迭代並修改 | `for i in range(len(lst)): lst[i] += 1` | `for x in &mut list:` |
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch03_ownership/06_borrow_of_moved
//! cargo run
//! ```

fn main() {
    /// Bad
    let tasks = [
        String::from("打開冰箱"),
        String::from("放進大象"),
        String::from("關上冰箱"),
    ];
    println!("開始處理任務...");
    // `tasks` 陣列的所有權被移動到 for 迴圈中。
    // 迴圈會開始迭代陣列中的每一個元素。
    for task in tasks {
        // 在每一次迭代中：
        // 1. `tasks` 陣列中的一個 String 元素的所有權，被移動到 `task` 變數中。
        println!("- {}", task);
        // 2. 當 `task` 變數離開這個迭代的作用域時，
        // 它所擁有的 String 就會在這裡被丟棄 (drop)，其記憶體會被釋放。
    } // <-- `task` 在此被 drop
      // 此時，不僅 `tasks` 陣列本身的所有權已經被消耗，
      // 其內部的三個 String 元素也都在上面的迴圈中被依序 drop 完畢了。
      // 迴圈結束後，想再次使用 tasks
      // println!(" 總共有 {} 個任務。", tasks.len()); // 💥 錯誤！ `tasks` 已失效

    /// Fixed
    let tasks = [
        String::from("打開冰箱"),
        String::from("放進大象"),
        String::from("關上冰箱"),
    ];
    println!("開始處理任務...");
    // 透過 & 借用 tasks，觸發 .iter() 模式
    for task in &tasks {
        println!("- {}", task);
    }
    // `tasks` 依然有效，因為我們只借用了它
    println!("總共有 {} 個任務。", tasks.len()); // OK!
}