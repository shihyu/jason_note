//!
//! # Rust 效能Benchmark工具
//!
//! 示範如何使用 Rust 內建的 `cargo bench` 以及 Criterion.rs 進行效能基準測試。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! | 測量執行時間 | `time.time()` + 迴圈 | `std::time::Instant` + 迭代器 |
//! | 基準測試框架 | `pytest-benchmark` | `criterion` crate |
//! | 記憶體配置追蹤 | `memory_profiler` | `dhat` / `tracy` |
//!
//! ## 關鍵技法
//!
//! - `std::time::Instant`：精確計時，適用於測量程式區塊執行時間
//! - `criterion::black_box()`：防止編譯器優化掉待測表達式
//! - `cargo bench`：Rust 官方基準測試命令，基於 Criterion.rs
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch12_profiling/01_rust_benchmark
//! cargo bench
//! ```
//!
fn main() {
    println!("Hello, world!");
}
