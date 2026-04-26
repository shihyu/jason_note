//! # Cell：內部可變性（不可變參考上的修改）
//!
//! 本範例展示 `Cell<T>` 如何在**不可變參考 `&self`** 上修改內部值，適用於 `Copy` 型別（如 `bool`、`i32`）。
//!
//! ## 概念對照：Python vs Rust
//!
//! | 概念 | Python | Rust |
//! |---|---|---|
//! | 內部可變性 | 無 | `Cell<T>` / `RefCell<T>` |
//! | 不可變參考修改 | `self.attr = val`（always allowed）| `self.field.set(val)` via Cell |
//! | 執行緒安全 | GIL 保護 | `Cell` 僅單執行緒 |
//!
//! ## `Cell<T>` 允許在 `&self` 上修改
//!
//! ```text
//! Python: class Config:
//!             def enable_feature(self):  # 標準寫法
//!                 self.use_experimental = True
//!
//! Rust:   struct Config {
//!             use_experimental: Cell<bool>,
//!         }
//!         impl Config {
//!             fn enable_feature(&self) {  # &self 但可修改
//!                 self.use_experimental.set(true);
//!             }
//!         }
//! ```
//!
//! ## 限制
//!
//! ```text
//! Cell<T>  → 只能存 Copy 型別（T: Copy）
//! RefCell<T> → 可存任何 T，但借用量有執行期檢查
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch08_concurrency/07_cell
//! cargo run
//! ```

use std::cell::Cell;
// 一個應用程式的設定
struct Config {
    use_experimental_feature: Cell<bool>,
}
impl Config {
    // 一個在不可變參考 &self 上的方法
    fn enable_feature(&self) {
        // 即使 &self 是不可變的，Cell 允許我們修改內部值
        self.use_experimental_feature.set(true);
    }
    fn is_feature_enabled(&self) -> bool {
        // .get() 會複製一份 bool 值出來
        self.use_experimental_feature.get()
    }
}
fn main() {
    // config 是一個不可變綁定
    let config = Config {
        use_experimental_feature: Cell::new(false),
    };
    println!("Feature enabled: {}", config.is_feature_enabled()); // false
    config.enable_feature(); // 呼叫 &self 的方法
    println!("Feature enabled: {}", config.is_feature_enabled()); // true
}
