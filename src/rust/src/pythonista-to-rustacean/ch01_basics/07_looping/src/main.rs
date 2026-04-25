//! # Looping（迴圈）
//!
//! ## 📖 概念說明
//!
//! Rust 提供四種迴圈結構：`loop`、`while`、`for`、以及標記迴圈。
//!
//! ```text
//! ┌──────────────────────────────────────────────────────────────────────┐
//! │  迴圈類型對比                                                      │
//! ├──────────────────────────────────────────────────────────────────────┤
//! │                                                                      │
//! │  1. loop ── 無限迴圈，直到遇到 break                                │
//! │     ┌─────────┐                                                    │
//! │     │  loop { │                                                    │
//! │     │   ...   │ ──→ break ──→ 跳出迴圈                             │
//! │     │ }        │                                                    │
//! │     └─────────┘                                                    │
//! │                                                                      │
//! │  2. while ── 條件為 true 時執行                                    │
//! │     ┌──────────────┐                                               │
//! │     │ while cond { │                                               │
//! │     │   ...        │ ──→ 條件 false → 跳出                        │
//! │     │ }            │                                               │
//! │     └──────────────┘                                               │
//! │                                                                      │
//! │  3. for ── 迭代集合                                                │
//! │     ┌──────────────┐                                               │
//! │     │ for item in coll { │                                          │
//! │     │   ...          │ ──→ 迭代完成 → 跳出                         │
//! │     │ }              │                                              │
//! │     └──────────────┘                                               │
//! │                                                                      │
//! │  4. 標記迴圈 ── 指定break 哪一層                                  │
//! │     'outer: for ... {                                              │
//! │       'inner: for ... {                                           │
//! │         break 'outer;  ← 直接跳出外層迴圈                          │
//! │       }                                                            │
//! │     }                                                              │
//! │                                                                      │
//! └──────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## 📝 與 Python 的對比
//!
//! | Python | Rust |
//! |--------|------|
//! | `while True: ...` | `loop { ... }` |
//! | `while condition:` | `while condition { }` |
//! | `for item in list:` | `for item in collection { }` |
//! | `for i in range(3):` | `for i in 0..3 { }` 或 `for i in 0..=3 { }` |
//!
//! ## ⚡ 特殊語法
//!
//! - `(1..=3).rev()`：反轉範圍
//! - `break "value"`：從 `loop` 回傳值
//! - `'label: for ...`：標記迴圈，指定 break 哪一層

fn check_system_ready() -> bool {
    false
}

fn main() {
    /// Loop
    let mut counter = 1;
    loop {
        if counter > 3 {
            break; // 達到條件，跳出迴圈
        }
        println!("Step {counter}");
        counter += 1;
    }

    let mut attempts = 0;
    let max_attempts = 5;

    let status = loop {
        attempts += 1;
        // 假設 check_system_ready() 是某個檢查函式
        if check_system_ready() {
            break "System ready"; // 成功，break 並回傳字串
        }
        if attempts >= max_attempts {
            break "Timeout reached"; // 失敗，break 並回傳另一個字串
        }
        std::thread::sleep(std::time::Duration::from_secs(1)); // 模擬等待
    };
    println!("Final status: {status}");

    /// While Loop
    let mut temperature = 20;
    while temperature < 25 {
        println!("Current temperature: {temperature}˚C");
        temperature += 1;
    }
    println!("It's warm enough!");

    /// For Loop
    let fruits = vec!["apple", "banana", "cherry"];
    // 'fruit' 會依序 " 借用" 'fruits' 中的每個元素
    for fruit in fruits {
        println!("I like {fruit}");
    }

    // (1..=3) 是一個包含 1, 2, 3 的範圍
    // .rev() 則是將範圍反轉
    for countdown in (1..=3).rev() {
        println!("{countdown}...");
    }
    println!("Go!");

    /// Loop Labels
    let matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]];
    let mut found = false;
    'outer: for row in matrix {
        'inner: for item in row {
            if item == 5 {
                found = true;
                break 'outer; // 找到了！直接 break 'outer 迴圈
            }
        }
    }
    println!("Found 5: {found}");
}
