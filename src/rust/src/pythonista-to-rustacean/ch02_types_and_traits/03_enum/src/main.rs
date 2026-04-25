//! # Enum 與 Pattern Matching：夜市美食列舉
//!
//! 本範例展示 Rust Enum 的強大能力——不只儲存資料，還能攜帶**不同型別的附加資料**，
//! 並透過 `match` 進行**窮舉式**模式比對。
//!
//! ## Enum 的三種使用情境
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │                    Enum 三種使用情境                             │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                 │
//! │  1. 簡單列舉（像 Python 的 Enum）                              │
//! │     ─────────────────────────────────                          │
//! │     enum SpiceLevel {                                          │
//! │         NoSpice,     # 臭豆腐不要辣                            │
//! │         Medium,      # 中辣                                   │
//! │         ExtraHot,    # 麻辣                                   │
//! │     }                                                          │
//! │                                                                 │
//! │  2. 攜帶資料的 Variant（Python 無直接對應）                    │
//! │     ──────────────────────────────────────────────             │
//! │     enum NightMarketFood {                                     │
//! │         StinkyTofu(u32, SpiceLevel),   # 價格 + 辣度          │
//! │         OysterOmelet(u32, bool),      # 價格 + 是否加蛋      │
//! │         WheelCake(u32, String),       # 價格 + 口味          │
//! │     }                                                          │
//! │                                                                 │
//! │  3. Option（類似 Python 的 Optional[T]，但更安全）            │
//! │     ─────────────────────────────────────                       │
//! │     enum Option<T> {                                          │
//! │         Some(T),    # 有值                                    │
//! │         None,      # 無值                                    │
//! │     }                                                          │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Option vs None
//!
//! | 情境 | Python | Rust |
//! |------|---------|------|
//! | 可能無值 | `Optional[T]` 或 `T \| None` | `Option<T>` |
//! | 有值 | `Some(value)` | `Some(value)` |
//! | 無值 | `None` | `None` |
//! | 取值 | `x if x else default` | `match x { Some(v) => v, None => default }` |
//! | 安全感 | 需手動判斷 None | **編譯器強制檢查** |
//!
//! ## match 必須窮舉
//!
//! Rust 的 `match` 是**窮舉式**（exhaustive），編譯器會確保所有變體都被處理。
//! 這比 Python 的 `if-elif-else` 更安全——漏寫分支會直接編譯錯誤。
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │                    match 必須處理所有變體                         │
//! │                                                                 │
//! │   match food {                                                 │
//! │       StinkyTofu(..) => ...,   ← 每一個 Variant 都要處理       │
//! │       OysterOmelet(..) => ...,                                  │
//! │       ChickenCutlet(..) => ...,                                 │
//! │       WheelCake(..) => ...,                                     │
//! │   }                                                            │
//! │                                                                 │
//! │   // 不想處理所有？用 `if let` 單一匹配：                        │
//! │   if let Some(num) = table_number { ... }                      │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch02_types_and_traits/03_enum
//! cargo run
//! ```

enum NightMarketFoodSimple {
    StinkyTofu,    // 臭豆腐
    OysterOmelet,  // 蚵仔煎
    ChickenCutlet, // 雞排
    WheelPie,      // 車輪餅
}

enum SpiceLevel {
    NoSpice,
    Medium,
    ExtraHot,
}

// Enum 變體可以攜帶不同資料
enum NightMarketFood {
    StinkyTofu(u32, SpiceLevel), // 價格 + 辣度
    OysterOmelet(u32, bool),     // 價格 + 是否加蛋
    ChickenCutlet(u32, bool),    // 價格 + 是否切塊
    WheelCake(u32, String),      // 價格 + 口味
}

fn order_food(food: NightMarketFood) {
    match food {
        NightMarketFood::StinkyTofu(price, spice) => {
            println!("臭豆腐 {price} 元！");
            match spice {
                SpiceLevel::NoSpice => println!("不要辣"),
                SpiceLevel::Medium => println!("中辣"),
                SpiceLevel::ExtraHot => println!("變態辣！小心！"),
            }
        }
        NightMarketFood::OysterOmelet(price, add_egg) => {
            if add_egg {
                println!("蚵仔煎加蛋 {price} 元！");
            } else {
                println!("蚵仔煎不加蛋 {price} 元！");
            }
        }
        NightMarketFood::ChickenCutlet(price, cut) => {
            if cut {
                println!("雞排切塊 {price} 元！");
            } else {
                println!("雞排不切 {price} 元！");
            }
        }
        NightMarketFood::WheelCake(price, flavor) => {
            println!("車輪餅 {flavor} 口味 {price} 元！");
        }
    }
}

fn main() {
    /// Enum
    let my_order = NightMarketFood::StinkyTofu(60, SpiceLevel::Medium);
    let friend_order = NightMarketFood::WheelCake(25, String::from("紅豆"));

    order_food(friend_order);

    /// Option
    let table_number: Option<u32> = Some(8);
    // let table_number: Option<u32> = None; // 還在等位子
    match table_number {
        Some(num) => println!("請到 {num} 號桌！"),
        None => println!("請稍等，正在安排座位！"),
    }

    let table_number: Option<u32> = None;
    if let Some(num) = table_number {
        println!("請到 {num} 號桌！");
    } else {
        println!("請稍等，正在安排座位！");
    }
}