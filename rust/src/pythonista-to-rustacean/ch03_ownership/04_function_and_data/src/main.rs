//! # Borrowing in Functions：函式中的借用模式
//!
//! 本範例展示 Rust 函式中三種**借用模式**：
//!
//! ## 三種借用模式
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │              函式借用的三種模式                                   │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                 │
//! │  1. 不可變借用  (&T)                                           │
//! │  ─────────────────────                                         │
//! │  fn calculate_sum(numbers: &Vec<i32>) -> i32                 │
//! │      numbers.iter().sum()  // 只讀取，不取得所有權                │
//! │                                                                 │
//! │  2. 可變借用    (&mut T)                                       │
//! │  ─────────────────────                                         │
//! │  fn add_greeting(text: &mut String)                           │
//! │      text.push_str(", world!")  // 修改內容，所有權不移動         │
//! │                                                                 │
//! │  3. 取得所有權  (T)                                           │
//! │  ───────────────────────                                       │
//! │  fn filter_out_negatives(numbers: Vec<i32>) -> Vec<i32>       │
//! │      numbers.into_iter().filter(|&n| n >= 0).collect()         │
//! │      // 取得 Vec 的所有權，回傳新的 Vec                           │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust：函式參數對照
//!
//! | 情境 | Python | Rust |
//! |------|---------|------|
//! | 唯讀 | `def f(x):`（參照）| `fn f(&x):` |
//! | 修改傳入 | `x.append(...)`（原地修改）| `fn f(&mut x):` |
//! | 消耗並回傳 | 回傳新值，原值不變 | `fn f(x: T) -> T`（移動並回傳）|
//! | 複製後傳入 | 手動 `.copy()` | 自動 Copy 型別複製 |
//!
//! ## 借用的生命週期
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │              借用 vs 所有權轉移                                 │
//! │                                                                 │
//! │   let my_numbers = vec![10, 20, 30];                         │
//! │   let sum = calculate_sum(&my_numbers);                       │
//! │   //                          └── & 借用，不移動所有權         │
//! │   println!("{:?}", my_numbers);  // ✅ 仍然有效                 │
//! │                                                                 │
//! │   ────────────────────────────────────────────────────────     │
//! │                                                                 │
//! │   let positive = filter_out_negatives(my_numbers);             │
//! │   //                                      無 &，所有權移動      │
//! │   println!("{:?}", my_numbers);  // ❌ 編譯錯誤！已無效       │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch03_ownership/04_function_and_data
//! cargo run
//! ```

// 這個函式「借用」一個 Vec 來計算總和
fn calculate_sum(numbers: &Vec<i32>) -> i32 {
    numbers.iter().sum()
}

// 這個函式「可變地借用」一個 String 來附加資料
fn add_greeting(text: &mut String) {
    text.push_str(", world!");
}

// 這個函式「取得」一個 Vec 的所有權，並回傳一個新的（已過濾的）Vec
fn filter_out_negatives(numbers: Vec<i32>) -> Vec<i32> {
    numbers.into_iter().filter(|&n| n >= 0).collect()
}

fn main() {
    /// Immutable borrow
    let my_numbers = vec![10, 20, 30];
    // 我們傳遞了一個參考，而非轉交所有權
    let sum = calculate_sum(&my_numbers);
    println!("The sum is: {}", sum);
    // my_numbers 在此依然完全有效，因為所有權從未離開過 main 函式
    println!("The numbers are still: {:?}", my_numbers);

    /// Mutable borrow
    // 材料本身也需是可變的，代表擁有者同意它被修改
    let mut my_text = String::from("Hello");
    // 傳遞可變參考，賦予工匠修改的權力
    add_greeting(&mut my_text);
    // 材料的內容已被原地修改
    println!("{}", my_text); // 輸出 "Hello, world!"

    /// Move
    let my_numbers = vec![10, -20, 30];
    // my_numbers 的所有權被「移動」到工匠手中，像交出原料
    let positive_numbers = filter_out_negatives(my_numbers);
    println!("Positive numbers: {:?}", positive_numbers);
    // 下一行會編譯失敗，因為 my_numbers 的所有權已經轉讓，變數已失效
    // println!("Original numbers: {:?}", my_numbers);
}