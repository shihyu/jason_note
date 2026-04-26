//! # #[derive] 巨集與常用 Trait
//!
//! 本範例展示 Rust 最常用的 **derive 巨集**，自動為結構體衍生常見 Trait，
//! 大幅減少樣板程式碼。
//!
//! ## #[derive(...)] 是什麼？
//!
//! `#[derive(...)]` 是 **編譯器代碼產生器**——告訴 Rust 自動為你的型別實作特定 Trait。
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │                    #[derive] 視覺化                              │
//! │                                                                 │
//! │   #[derive(Debug, Clone, Copy, PartialEq, Eq)]                 │
//! │   struct Foo { x: i32, y: String }                             │
//! │                                                                 │
//! │   展開後，編譯器自動幫你生成大約 200 行程式碼：                  │
//! │                                                                 │
//! │   impl Debug for Foo { ... }  // 可用 {:?} 格式化               │
//! │   impl Clone for Foo { ... }  // 可.clone()                     │
//! │   impl Copy for Foo { ... }   // 可直接複製（所有權不移動）      │
//! │   impl PartialEq for Foo {    // 可用 == 比較                   │
//! │       fn eq(&self, other: &Foo) -> bool { ... }                │
//! │   }                                                            │
//! │   impl Eq for Foo { }     // 反身性保證（a == a 必為 true）     │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## 各 Trait 詳細說明
//!
//! | Trait | 功用 | Python 對應 | 何時需要手動實作 |
//! |-------|------|------------|------------------|
//! | `Debug` | 除錯用格式化 `{:#?}` | `__repr__` | 自訂顯示格式時 |
//! | `Clone` | 深拷貝 `.clone()` | `copy`（需自己定義）| 欄位含 `*const T` 等指標時 |
//! | `Copy` | 位元複製（所有權不移動）| — | 欄位全為 `Copy` 型別時 |
//! | `PartialEq` | `==` 比較 | `__eq__` | 自訂相等邏輯時 |
//! | `Eq` | 反身性 `a == a` 必為 true | — | 與 `PartialEq` 配對 |
//!
//! ## Copy vs Clone 的重要區別
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │                    Copy vs Clone                               │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                 │
//! │   Copy（隱含在賦值中，型別元自動繼承）                            │
//! │   ─────────────────────────────                                 │
//! │   let a = Foo { x: 1 };                                         │
//! │   let b = a;          // a 的所有權「複製」到 b，a 仍可用        │
//! │   println!("{:?}", a); // ✅ 正常                             │
//! │                                                                 │
//! │   Clone（需明確呼叫）                                            │
//! │   ─────────────────────                                         │
//! │   let a = Foo { x: 1 };                                         │
//! │   let b = a.clone();   // 明確複製，a 的所有權不變               │
//! │   println!("{:?}", a); // ✅                                    │
//! │                                                                 │
//! │   Move（無 Copy/Clone 時，所有權會轉移）                          │
//! │   ───────────────────────                                       │
//! │   let a = String::from("hello");                                │
//! │   let b = a;           // String 沒有 Copy，a 失效              │
//! │   println!("{}", a);    // ❌ 編譯錯誤！                         │
//! │   let c = a.clone();   // ✅ 必須 clone                         │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch02_types_and_traits/05_derive_macro
//! cargo run
//! ```

// 如果沒有 #[derive(Debug)]，下一行的 println! 會編譯失敗
#[derive(Debug)]
struct NightMarketOrder {
    food: String,
    quantity: u8,
}

// 像 u8, u32, bool 這種簡單型別都內建了 Copy
// 但我們的自訂型別需要手動加上
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct TablePosition(u8, u8);

fn main() {
    let order = NightMarketOrder {
        food: String::from("豆花"),
        quantity: 1,
    };

    // {:#?} 則是更美觀的 "pretty-print"
    println!("{:#?}", order);

    let table1 = TablePosition(1, 5);
    let table2 = table1; // 這裡是「複製」，不是「搬移」
                         // 因為 TablePosition 有 Copy，table1 依然可用
    println!("{:?}", table1); // 印出: TablePosition(1, 5)
    println!("{:?}", table2); // 印出: TablePosition(1, 5)

    let table1 = TablePosition(1, 5);
    let table2 = TablePosition(1, 5);
    let table3 = TablePosition(2, 1);
    // 如果沒有 #[derive(PartialEq)]，底下會編譯失敗
    println!("table1 == table2: {}", table1 == table2); // true
    println!("table1 != table3: {}", table1 != table3); // true
}