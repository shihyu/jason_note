//!
//! # dhat 記憶體配置分析器
//!
//! 示範如何使用 dhat ( allocator for tracking heap allocations ) 進行記憶體配置分析。
//!
//! ## Python vs Rust 對照表
//!
//! | 情境 | Python 写法 | Rust 写法 |
//! |------|------------|--------|
//! | 全域配置器 | `import sys` + `sys.setrecursionlimit` | `#[global_allocator]` + `static` |
//! | 記憶體追蹤 | `tracemalloc` / `memory_profiler` | `dhat::Profiler::new_heap()` |
//! | 配置瓶頸定位 | `line_profiler` | `dhat` 報告 + 原始碼對照 |
//!
//! ## 關鍵技法
//!
//! - `#[global_allocator]`：將自訂配置器設為全域預設，僅能同時存在一個
//! - `dhat::Alloc`：dhat 提供的配置器包裝，記錄所有堆積配置
//! - `dhat::Profiler::new_heap()`：建立分析器實例，生命週期結束時寫出報告
//! - `tracemalloc` vs `dhat`：兩者皆追蹤配置，但 dhat 專為 Rust 設計且零額外成本
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch12_profiling/02_dhat
//! cargo run --features dhat-heap
//! # 分析報告會產生於 dhat-heap.json
//! ```
//!
//! ----------------------------------------------------
//! Dhat 分析器所需的設定
//! ----------------------------------------------------

// 1. 只有在 "dhat-heap" feature 啟用時，才使用 Dhat 作為全域配置器
#[cfg(feature = "dhat-heap")]
#[global_allocator]
static ALLOCATOR: dhat::Alloc = dhat::Alloc;
// ----------------------------------------------------
// 這是我們想要進行效能分析的「範例程式邏輯」
// ----------------------------------------------------
fn run_demo() {
    println!("開始執行範例...");
    let mut total_len = 0;
    // 3. 這是一個我們懷疑的「熱迴圈」，每次都會配置新的 String
    for i in 0..10_000 {
        let s = String::from("這是一個重複配置的字串"); // 這裡是第 19 行
        if i % 100 == 0 {
            total_len += s.len();
        }
    }
    println!("執行完畢。總長度: {}", total_len);
}
// ----------------------------------------------------
// 主函數 (main) - 負責啟動 Dhat 並執行範例
// ----------------------------------------------------
fn main() {
    // 2. 啟動分析器。
    // _profiler 變數的生命週期決定了分析的區間
    #[cfg(feature = "dhat-heap")]
    let _profiler = dhat::Profiler::new_heap();
    // 執行我們真正要分析的程式
    run_demo();
    // _profiler 在 main 函數結束時被 drop，分析報告會在此時寫入檔案
}
