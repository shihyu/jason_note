//!
//! # Criterion Benchmark 範例：Fibonacci 效能測量
//!
//! 展示如何使用 Rust 官方標準化效能測試工具 Criterion
//! 對函式進行統計顯著 (statistically significant) 的效能測量。
//!
//! ## 架構圖
//!
//! ```text
//! ┌──────────────────────────────────────────────────────────────────────┐
//! │                     Criterion Benchmark 流程                           │
//! │                                                                       │
//! │   測量階段                                                          │
//! │   ┌──────────────────────┐  ┌──────────────────────┐           │
//! │   │ fibonacci(10)        │  │ fibonacci(20)        │           │
//! │   └──────────┬──────────┘  └──────────┬──────────┘           │
//! │              │                              │                         │
//! │              └──────────────┬──────────────┘                         │
//! │                         ▼                                            │
//! │              ┌──────────────────────┐                        │
//! │              │  black_box(input)     │  ← 防止編譯器過度優化    │
//! │              └──────────┬──────────┘                        │
//! │                         ▼                                            │
//! │              ┌──────────────────────┐                        │
//! │              │  多次執行取平均值      │                        │
//! │              │  計算信賴區間        │                        │
//! │              │  判定統計顯著差異      │                        │
//! │              └──────────────────────┘                        │
//! │                         ▼                                            │
//! │              bench_reports/ (HTML 報告)                       │
//! └──────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 情境              | Python (timeit / pytest-benchmark) 写法              | Rust (Criterion) 写法                              |
//! |-------------------|---------------------------------------------|---------------------------------------------|
//! | 基本測量         | `timeit(lambda: f(20), number=1000)`         | `criterion_benchmark` 函式 + `b.iter(...)` |
//! | 防止編譯器優化   | 無內建機制                                     | `black_box(n)` — 編譯器無法窺視內容           |
//! | 統計顯著性       | 需手動計算                                    | 內建信賴區間、變異數分析                   |
//! | 報告格式         |文字輸出                                       | HTML 互動式圖表 + CSV                        |
//! | 多次測量         | `repeat(5, lambda: ...)`                    | Criterion 自動執行多次測量取平均                  |
//!
//! ## 關鍵技法
//!
//! - `black_box(n)`：防止編譯器因窺視常數輸入而對結果進行常數折疊 (constant folding)
//! - `criterion_group!` + `criterion_main!`：Criterion 的標準巨集注册方式
//! - `b.iter(|| fibonacci(black_box(20)))`：Closure 形式，Criterion 自動重複執行
//! - `mut group`：建立多輸入基準測試群組
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch12_profiling/01_rust_benchmark
//! cargo bench
//! # 報告會生成在 target/criterion/
//! ```
//!
use std::hint::black_box;

use criterion::{Criterion, criterion_group, criterion_main};

// 假設這是我們想要測試的函數
fn fibonacci(n: u64) -> u64 {
    match n {
        0 => 0,
        1 => 1,
        n => fibonacci(n - 1) + fibonacci(n - 2),
    }
}

// 這是一個 criterion 的 benchmark 函數
fn criterion_benchmark(c: &mut Criterion) {
    // 我們可以建立一個 benchmark 群組
    let mut group = c.benchmark_group("Fibonacci");

    // 針對不同的輸入值進行測試
    group.bench_function("Fibonacci 20", |b| {
        // b.iter 會多次執行內部的閉包
        // black_box() 是一個技巧，用來防止編譯器
        // 對我們的測試程式碼進行過度的優化 (例如把結果快取起來)
        b.iter(|| fibonacci(black_box(20)))
    });

    group.bench_function("Fibonacci 10", |b| b.iter(|| fibonacci(black_box(10))));

    group.finish();
}

// 透過這兩個巨集，將 benchmark 函數註冊到 criterion 的
// 測試啟動器中
criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
