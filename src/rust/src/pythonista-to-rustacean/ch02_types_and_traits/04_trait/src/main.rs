//! # Trait 泛型界限與預設實作：通勤支付系統
//!
//! 本範例展示 Trait 的三個進階特性：
//!
//! ## 1. Trait 泛型界限（Trait Bound）
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │                 Trait Bound：約束泛型必須實作特定 Trait            │
//! │                                                                 │
//! │   fn enter_station<T: CommutePay>(card: T) {                   │
//! │                   ────────────────                                │
//! │                   ↑ T 必須實作 CommutePay                       │
//! │       card.beep();  // 確定有 .beep() 才會編譯                  │
//! │   }                                                               │
//! │                                                                 │
//! │   // 呼叫時，編譯器會檢查傳入的型別是否真的實作了 CommutePay      │
//! │   enter_station(EasyCard);  // ✅ EasyCard 有實作               │
//! │   enter_station(String);    // ❌ 編譯錯誤！String 沒有實作        │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## 2. 預設實作（Default Implementation）
//!
//! Trait 可以提供**預設方法實作**，讓結構體選擇使用或覆寫：
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │                    預設實作機制                                 │
//! │                                                                 │
//! │   trait InvoiceHandling {                                        │
//! │       fn process_invoice(&self) -> String {                     │
//! │           String::from("(預設：捐贈發票)")  ← 預設行為           │
//! │       }                                                        │
//! │   }                                                            │
//! │                                                                 │
//! │   impl InvoiceHandling for StorePurchase {}  ← 空實作 = 全部用預設 │
//! │                                                                 │
//! │   impl InvoiceHandling for MobileBarcodePurchase {               │
//! │       fn process_invoice(&self) -> String {  ← 覆寫自訂行為     │
//! │           format!("(存入載具：{})", self.barcode)              │
//! │       }                                                        │
//! │   }                                                            │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## 3. 多型（Polymorphism）透過 Trait 實現
//!
//! Python 用繼承實現多型，Rust 用 **Trait Bound**：
//!
//! | 概念 | Python | Rust |
//! |------|--------|------|
//! | 多型基底 | `class Base:` + `class Child(Base):` | `trait Pay { ... }` |
//! | 介面約束 | 繼承時自動繼承 | `<T: Pay>` 編譯期檢查 |
//! | 呼叫方法 | `obj.method()`（dynamic dispatch） | `card.beep()`（static dispatch） |
//!
//! ## Trait Bound 語法
//!
//! ```rust
//! // 完整語法（適用於多個約束）
//! fn func<T: TraitA + TraitB>(x: T) { ... }
//!
//! // where 子句（適用於複雜約束）
//! fn func<T>(x: T)
//! where
//!     T: TraitA + TraitB,
//! { ... }
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch02_types_and_traits/04_trait
//! cargo run
//! ```

// 定義一個 Trait，宣告「通勤支付」的能力
trait CommutePay {
    // 任何實作 CommutePay 的型別，都必須提供這個方法
    fn beep(&self); // 嗶卡
}

// 為 EasyCard (悠遊卡) 實作 CommutePay Trait
struct EasyCard;
impl CommutePay for EasyCard {
    fn beep(&self) {
        println!("嗶！ (悠遊卡)");
    }
}
// 為 IPass (一卡通) 實作 CommutePay Trait
struct IPass;
impl CommutePay for IPass {
    fn beep(&self) {
        println!("嗶！ (一卡通)");
    }
}
// 為 Tpass (行政院通勤月票) 實作 CommutePay Trait
struct Tpass;
impl CommutePay for Tpass {
    fn beep(&self) {
        println!("嗶！ (TPASS 月票)");
    }
}

// <T: CommutePay> 是一個帶有特徵邊界的泛型宣告
// T 代表「任何實作了 CommutePay 的型別」
fn enter_station<T: CommutePay>(card: T) {
    print!("進站 - ");
    card.beep(); // <-- 現在編譯器知道 T 一定有 .beep() 方法了
}

// 1. 定義「發票處理」的 Trait
trait InvoiceHandling {
    // 提供一個預設實作：如果沒特別指定，就捐贈
    fn process_invoice(&self) -> String {
        String::from("(預設處理：捐贈發票)")
    }
}
// 2. 定義一個「商店消費」的結構
struct StorePurchase {
    item_name: String,
    amount: u32,
}
// 3. 只需要一行空的 impl，就能讓「商店消費」採用預設的發票處理行為
impl InvoiceHandling for StorePurchase {}

// 假設另一個型別需要「覆蓋」預設行為
struct MobileBarcodePurchase {
    item_name: String,
    amount: u32,
    barcode: String,
}
// 覆蓋預設的 process_invoice 方法
impl InvoiceHandling for MobileBarcodePurchase {
    fn process_invoice(&self) -> String {
        format!("(存入載具：{})", self.barcode)
    }
}

fn main() {
    let card_a = EasyCard;
    let card_b = IPass;
    let card_c = Tpass;
    card_a.beep();
    card_b.beep();
    card_c.beep();

    let card1 = EasyCard;
    let card2 = IPass;
    let card3 = Tpass;
    enter_station(card1); // 印出: 進站 - 嗶！ (悠遊卡)
    enter_station(card2); // 印出: 進站 - 嗶！ (一卡通)
    enter_station(card3); // 印出: 進站 - 嗶！ (TPASS 月票)

    // Default implementation
    let purchase = StorePurchase {
        item_name: "茶葉蛋".to_string(),
        amount: 10,
    };
    // 顧客沒有指定發票載具...
    // 呼叫由 Trait 提供的預設方法
    println!("商品：{}", purchase.item_name);
    println!("發票處理方式：{}", purchase.process_invoice()); // 印出: (預設處理：捐贈發票)

    let purchase_2 = MobileBarcodePurchase {
        item_name: "飛機".to_string(),
        amount: 100,
        barcode: "/+ABC123".to_string(),
    };
    println!("商品：{}", purchase_2.item_name);
    println!("發票處理方式：{}", purchase_2.process_invoice()); // 印出: (存入載具：/+ABC123)
}