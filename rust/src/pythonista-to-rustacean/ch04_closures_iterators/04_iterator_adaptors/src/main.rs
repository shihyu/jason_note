//! # `04_iterator_adaptors` - 迭代器適配器（filter / map 鏈）
//!
//! ## 概念說明
//!
//! **迭代器適配器（Iterator Adaptors）** transform an iterator into another iterator
//! without consuming it. They are **lazy** — nothing happens until a consuming adaptor
//! is called.
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │  .filter() 與 .map() 的型別演化                                  │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                  │
//! │  v.iter()                                                        │
//! │    │ Iterator<Item = &i32>                                        │
//! │    ▼                                                            │
//! │  .filter(|x| *x % 2 == 0)  ◄── 只保留偶數                      │
//! │    │ Iterator<Item = &i32>  (型別不變，值被過濾)                │
//! │    ▼                                                            │
//! │  .map(|x| x * 2)                                                │
//! │    │ Iterator<Item = i32>  (參考 → 值，*x % 2 == 0 時)          │
//! │    ▼                                                            │
//! │  .collect()  ◄── 消費，觸發整條鏈的執行                         │
//! │                                                                  │
//! ├─────────────────────────────────────────────────────────────────┤
//! │  範例 a: filter → map（先過濾再映射）                            │
//! │                                                                  │
//! │  v = [1, 2, 3, 4]                                              │
//! │                                                                  │
//! │  filter 後: [2, 4]          只保留 2, 4                        │
//! │  map *2 後: [4, 8]                                              │
//! │                                                                  │
//! ├─────────────────────────────────────────────────────────────────┤
//! │  範例 b: map → filter（先映射再過濾）                            │
//! │                                                                  │
//! │  v = [1, 2, 3, 4]                                              │
//! │                                                                  │
//! │  map *2 後: [2, 4, 6, 8]                                        │
//! │  filter 偶數後: [2, 4, 6, 8]  ◄── 全部都仍是偶數！           │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python 對照表
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 過濾 | `[x for x in iter if pred(x)]` 或 `filter(pred, iter)` | `.filter(\|x\| pred)` |
//! | 映射 | `[func(x) for x in iter]` 或 `map(func, iter)` | `.map(\|x\| func(x))` |
//! | 惰性執行 | `filter`/`map` 回傳惰性物件 | 相同，呼叫 `.collect()` 才執行 |
//! | 鏈式呼叫 | `map(...).filter(...)` (回傳 map object) | `.map(...).filter(...)` (回傳迭代器) |
//!
//! ## 重點解析
//!
//! - `filter` 的閉包收到 **`&i32`**，需用 `*x` 解參考
//! - `map` 的閉包收到 **`&i32`**（filter 不改型別）
//! - **順序很重要**：先 filter 再 map 與先 map 再 filter 結果可能不同！
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
//! a: [4, 8], b: [2, 4, 6, 8]
//! ```

fn main() {
    let v = vec![1, 2, 3, 4];
    // 範例 a: 先 filter 再 map
    let a: Vec<_> = v
        .iter()
        .filter(|x| *x % 2 == 0) // (1) x 的型別是 &&i32
        .map(|x| x * 2) // (2) x 的型別是 &i32
        .collect();
    // 範例 b: 先 map 再 filter
    let b: Vec<_> = v
        .iter()
        .map(|x| x * 2) // (3) x 的型別是 &i32
        .filter(|x| x % 2 == 0) // (4) x 的型別是 &i32
        .collect();
    println!("a: {:?}, b: {:?}", a, b);
    // a: [4, 8]
    // b: [2, 4, 6, 8]
}