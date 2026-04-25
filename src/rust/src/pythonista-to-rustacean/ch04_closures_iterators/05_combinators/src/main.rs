//! # `05_combinators` - Option  combinators（map / filter / or_else / unwrap_or_else）
//!
//! ## 概念說明
//!
//! `Option<T>` 是 Rust 內建的**可 null 型別**。
//! 傳統處理方式需要 `match`；使用 combinators 可以鏈式處理，程式碼更簡潔。
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │  Option<T> 的 combinators 家族                                    │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                  │
//! │  .map(fn)        ──► Option<U>  Some(x) → Some(fn(x)), None → None │
//! │  .filter(pred)  ──► Option<T>   Some(x) → Some(x) if pred(x), else None │
//! │  .or_else(f)     ──► Option<T>  None → Some(f()), Some(x) → Some(x)   │
//! │  .unwrap_or_else(f) ──► T         None → f(), Some(x) → x              │
//! │                                                                  │
//! │  ┌──────────────────────────────────────────┐                    │
//! │  │  .map()  combinator 範例                 │                    │
//! │  │                                          │                    │
//! │  │  maybe_num() → Some(5)                   │                    │
//! │  │       │                                  │                    │
//! │  │       ▼ .map(|n| n + 1)                 │                    │
//! │  │  Some(6)  ◄── 只在 Some 時執行閉包      │                    │
//! │  │                                          │                    │
//! │  │  maybe_num() → None                      │                    │
//! │  │       │                                  │                    │
//! │  │       ▼ .map(|n| n + 1)                 │                    │
//! │  │  None     ◄── None 直接穿過，不執行閉包 │                    │
//! │  └──────────────────────────────────────────┘                    │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python 對照表
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 可 null 值 | `Optional[T]` (typing) / `None` | `Option<T>` (`Some(T)` 或 `None`) |
//! | if-let 解構 | `if let Some(x) = opt:` | `if let Some(x) = opt { ... }` |
//! | map 轉換 | `opt.map(lambda x: x + 1)` (Python 3.10+) | `opt.map(\|x\| x + 1)` |
//! | filter | `opt.filter(pred)` (Python 3.11+) | `opt.filter(\|x\| pred)` |
//! | None fallback | `opt or fallback` / `opt if opt else fallback` | `opt.unwrap_or(fallback)` / `opt.unwrap_or_else(\|\| fallback)` |
//! | or_else (延遲) | `opt.or_else(lambda: fallback)` | `opt.or_else(\|\| fallback)` |
//!
//! ## 重點解析
//!
//! - `Some` 內的 `num` 是**值**，不是參考；可直接使用
//! - `filter` 會**消耗** `Option`，若值不符合述詞就變成 `None`
//! - `or_else` vs `unwrap_or`：前者閉包**延遲執行**（只在需要時），適合昂貴運算
//! - `unwrap_or_else` 同理，但用於**取值**時的 fallback
//!
//! ## 執行方式
//!
//! ```bash
//! cargo run
//! ```
//!
//! ## 預期輸出
//!
//! ```text
//! Some(6)
//! Some(10)
//! None
//! Some(0)
//! Some(10)
//! 0
//! 10
//! ```

fn maybe_num() -> Option<i32> {
    // ...
    Some(5) // 假設回傳 Some(5)
}

fn main() {
    let plus_one = match maybe_num() {
        Some(num) => Some(num + 1), // 轉換 Some(5) -> Some(6)
        None => None,               // 保持 None
    };

    // .map() 的閉包只會在 Some(5) 時執行
    let plus_one: Option<i32> = maybe_num().map(|num| num + 1);

    println!("{:?}", plus_one);

    let a = Some(10);
    let b = Some(5);
    // 10 == 10，回傳 true，a 保持 Some(10)
    let a_filtered = a.filter(|num| *num == 10); // 結果是 Some(10)
    // 5 != 10，回傳 false，b 變成 None
    let b_filtered = b.filter(|num| *num == 10); // 結果是 None
    println!("{:?}", a_filtered);
    println!("{:?}", b_filtered);

    let a: Option<i32> = None;
    let b = Some(10);
    // a 是 None，執行閉包，回傳 Some(0)
    let a_with_fallback = a.or_else(|| Some(0)); // 結果是 Some(0)
    // b 是 Some(10)，不執行閉包，直接回傳 Some(10)
    let b_with_fallback = b.or_else(|| Some(0)); // 結果是 Some(10)
    println!("{:?}", a_with_fallback);
    println!("{:?}", b_with_fallback);

    let a: Option<i32> = None;
    let b = Some(10);
    // a 是 None，執行閉包，回傳預設值 0
    let value_a = a.unwrap_or_else(|| 0); // value_a 是 i32 型別的 0
    // b 是 Some(10)，不執行閉包，解開並回傳 10
    let value_b = b.unwrap_or_else(|| 0); // value_b 是 i32 型別的 10
    println!("{:?}", value_a);
    println!("{:?}", value_b);
}