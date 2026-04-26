//! # Borrowing：借用的藝術
//!
//! 本範例展示 Rust 的兩種**借用**機制：
//!
//! ## 借用分類
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │                    借用分類圖                                   │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                 │
//! │   ┌─────────────┐         ┌─────────────┐                  │
//! │   │ 不可變借用   │         │  可變借用    │                  │
//! │   │    &T       │         │   &mut T    │                  │
//! │   └──────┬──────┘         └──────┬──────┘                  │
//! │          │                        │                           │
//! │          ▼                        ▼                           │
//! │   任意數量同時存在        只能有一個，且持有人                │
//! │   只能讀取              必須是唯一&mut 的持有者              │
//! │                            可讀可寫                           │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## 借用規則
//!
//! | 規則 | 說明 |
//! |------|------|
//! | 任意數量的 `&T` | 同時間可以有多個不可變借用 |
//! | 只能有一個 `&mut T` | 同時間只能有一個可變借用 |
//! | `&T` 和 `&mut T` 互斥 | 有不可變借用存在時，不能有可變借用 |
//!
//! ## 生命週期與借用
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │                    借用生命週期                                  │
//! │                                                                 │
//! │   let y = &mut x;        // 可變借用 y 的生命週期開始          │
//! │   *y += 1;                                                 │
//! │   println!("{}", y);       // y 最後一次被使用                  │
//! │   // ────────────────                                              │
//! │   //  y 的生命週期在此結束                                      │
//! │   // ────────────────                                              │
//! │   let z = &x;             // ✅ 可以了！y 已結束                │
//! │   println!("{}", z);                                              │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust：借用對照
//!
//! | 情境 | Python | Rust |
//! |------|---------|------|
//! | 唯讀傳遞 | `def f(x):`（參照）| `fn f(&x):` |
//! | 修改傳遞 | 無法直接修改，需回傳新值 | `fn f(&mut x):` |
//! | 可變動指標 | `def f(x_list: list): x_list.append(...)` | 明確的 `&mut` |
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch03_ownership/02_borrow
//! cargo run
//! ```

enum Sugar {
    Regular,
    TainanStyle,
}

// 此函式 "借用" 一個 Sugar 的不可變參考
fn display_sugar(sugar: &Sugar) {
    match sugar {
        Sugar::Regular => println!("Regular sweet"),
        Sugar::TainanStyle => println!("Tainan sweet"),
    }
} // sugar 參考在此離開作用域，但 my_drink 的所有權不受影響

fn add_a_little_sugar(sweetness: &mut u32) {
    *sweetness += 10;
}

fn main() {
    let my_drink = Sugar::TainanStyle; // my_drink 是擁有者
    display_sugar(&my_drink); // 我們 "借出" my_drink 的參考
    display_sugar(&my_drink); // 成功！所有權未移動，可以再次借出

    let mut sugar_level: u32 = 20; // 擁有者變數必須是 mut
    add_a_little_sugar(&mut sugar_level);
    println!("New sugar level: {}", sugar_level); // 輸出 30

    let mut x = 10;
    let y = &mut x; // -- 可變借用 y 的生命週期開始
    *y += 1;
    println!("y has been used, its value is: {}", y); // -- y 在此處最後一次被使用，其生命週期結束
    // 因為 y 的生命週期已結束，所以我們可以安全地建立新的借用
    let z = &x;
    println!("x is now readable again: {}", z);
}