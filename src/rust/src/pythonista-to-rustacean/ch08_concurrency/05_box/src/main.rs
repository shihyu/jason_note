//! # Box：將資料移動到 Heap
//!
//! 本範例展示 `Box<T>` 如何將資料從 Stack 移動到 Heap，適用於大型資料或需要穩定指標的場景。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | Heap 配置 | 物件預設在 Heap | `Box::new()` 配置到 Heap |
//! | Stack vs Heap | GC 管理，無明確區分 | 明確的語意區分 |
//! | 指標大小 | 可變大小 | Stack 上只存指標（固定大小）|
//!
//! ## Box 的使用時機
//!
//! ```text
//! 1. 大型資料：避免 Stack overflow
//! 2. 特徵物件：建立泛型容器的動態分派
//!    `Box<dyn SomeTrait>`
//! 3. 遞迴型別：讓編譯器知道大小
//!    `enum List { Cons(i32, Box<List>), Nil }`
//! 4. 生命週期：在執行緒間傳遞穩定參考
//! ```
//!
//! ## 記憶體佈局
//!
//! ```text
//! 沒有 Box:          有 Box:
//! ┌───────┐          ┌─────────────┐
//! │   a    │ = 1      │ 堆積上的 1  │ ← Box 指向這裡
//! └───────┘          └─────────────┘
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch08_concurrency/05_box
//! cargo run
//! ```

fn main() {
    // v 現在在 Stack 上
    let a = 1;

    // b 是一個在 Stack 上的指標
    // 它指向的 1 這份資料，現在被移動到了 Heap 上
    let b = Box::new(a);
}
