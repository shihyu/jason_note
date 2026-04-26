//! # Struct、Method 與 Trait：夜市訂單系統
//!
//! 本範例展示 Rust 中三種「自訂型別」的核心理念：
//!
//! ## 1. Struct（結構體）vs Python `class`
//!
//! Rust 的 Struct 類似 Python 的 `dataclass`，但**沒有繼承**。
//! 所有行為都透過 **Trait** 附加，實現「組合優於繼承」。
//!
//! ## 2. 三種 Struct 形態
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────┐
//! │                    Struct 三種形態                            │
//! ├─────────────────────────────────────────────────────────────┤
//! │  Named-field Struct        Tuple Struct       Unit-like     │
//! │  ─────────────────        ───────────       ──────────     │
//! │  struct Foo {             struct Foo(        struct Foo;   │
//! │      x: i32,                  i32,          (marker type)│
//! │      y: String,               String,                        │
//! │  }                        )                                     │
//! │                                                             │
//! │  foo.x 存取            foo.0, foo.1 索引      無欄位        │
//! └─────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## 3. Trait：定義「能力」而非「繼承」
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────┐
//! │                   Trait = 能力清單                          │
//! │                                                             │
//! │   trait Payment {                                          │
//! │       fn process(&self, amount: u32);  ← 能力的「簽名」    │
//! │   }                                                        │
//! │                                                             │
//! │   impl Payment for CashPayment {  ← 具名結構實作能力         │
//! │       fn process(&self, amount: u32) { ... }                │
//! │   }                                                        │
//! │                                                             │
//! │   impl Payment for CreditCardPayment {                      │
//! │       fn process(&self, amount: u32) { ... }               │
//! │   }                                                        │
//! └─────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照
//!
//! | 概念 | Python | Rust |
//! |------|--------|------|
//! | 自訂型別 | `class Foo:` | `struct Foo { ... }` |
//! | 繼承 | `class Child(Parent):` | **無繼承**，用 Trait 組合 |
//! | 方法定義 | `def method(self):` | `impl Foo { fn method(&self) }` |
//! | 介面/能力 | `ABC` + `abstractmethod` | `trait Foo { fn bar(&self); }` |
//! | 實作介面 | `class Foo(ABC):` | `impl Foo for Struct { ... }` |
//! | 無欄位型別 | — | `struct Marker;` (Unit-like struct) |
//!
//! ## Struct Update Syntax（`..base`）
//!
//! 類似 Python 的 `{**base, "新欄位": value}`，但用 `..`：
//!
//! ```rust
//! let second = NightMarketFood { food: String::from("鹽酥雞"), ..first };
//! //              ↑ 新欄位必須明確寫       ↑ 其餘欄位從 first 複製
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch02_types_and_traits/01_struct
//! cargo run
//! ```

struct NightMarketOrder {
    food: String,
    quantity: u8,
    price: u32,
}

struct CashPayment;
struct CreditCardPayment;

// 定義一個「付款方式」的能力清單 (Trait)
trait Payment {
    fn process(&self, amount: u32);
}

// 現金付款的實作
impl Payment for CashPayment {
    fn process(&self, amount: u32) {
        println!("💵 收現金 {} 元，找零中...", amount);
    }
}
// 信用卡付款的實作
impl Payment for CreditCardPayment {
    fn process(&self, amount: u32) {
        println!("💳 刷卡 {} 元，請簽名", amount);
    }
}

fn main() {
    let my_order = NightMarketOrder {
        food: String::from("豆花"),
        quantity: 1,
        price: 30,
    };
    println!("我的{}！ {} 塊∼", my_order.food, my_order.price);

    let food = String::from("豆花");
    let quantity = 2;
    // 原本是 food: food, quantity: quantity
    // 簡寫為
    let order = NightMarketOrder {
        food,
        quantity,
        price: 60,
    };

    /// Struct update syntax
    let first_order = NightMarketOrder {
        food: String::from("臭豆腐"),
        quantity: 1,
        price: 60,
    };

    // 使用結構體更新語法，只更新 food 欄位
    let second_order = NightMarketOrder {
        food: String::from("鹽酥雞"),
        ..first_order
    };

    println!(
        "{} x{} = {} 元",
        second_order.food, second_order.quantity, second_order.price
    );
    println!(
        "{} x{} = {} 元",
        first_order.food, first_order.quantity, first_order.price
    );

    /// Tuple struct
    struct TablePosition(u8, u8); // (區域,桌號)
    let my_table = TablePosition(2, 15); //第 2 區 15 號桌
    // 透過索引存取欄位
    println!("我在第 {} 區 {} 號桌", my_table.0, my_table.1);

    /// Unit-like struct
    let cash = CashPayment;
    let card = CreditCardPayment;
    cash.process(65);
    card.process(120);
}