//! # Methods 與 Borrowing：方法中的三種 borrowing
//!
//! 本範例展示 Rust 方法中 `self`、`&self`、`&mut self` 三種取用的差異，
//! 及 Python 方法的對應關係。
//!
//! ## 三種 self 取用方式
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │              三種 self 取用方式                                   │
//! ├─────────────────────────────────────────────────────────────────┤
//! │                                                                 │
//! │   fn get_mean(&self)           // 唯讀借用，儀器的「顯示螢幕」      │
//! │   ──────────────────────                                            │
//! │   - 可多次同時呼叫                                                │
//! │   - 只能讀取狀態                                                 │
//! │                                                                 │
//! │   fn normalize_mut(&mut self)  // 可變借用，儀器的「校準旋鈕」    │
//! │   ──────────────────────────                                      │
//! │   - 独占修改                                                    │
//! │   - 期間不可有其他借用                                           │
//! │                                                                 │
//! │   fn into_report(self)          // 消耗，儀器的「產出報告」        │
//! │   ────────────────────                                            │
//! │   - 取得所有權                                                  │
//! │   - 方法名慣例前綴 "into_"                                     │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust：方法中的 self
//!
//! | Rust | Python | 說明 |
//! |------|---------|------|
//! | `&self` | `self` | 唯讀，參照傳遞 |
//! | `&mut self` | 無法直接表達 | 需回傳新物件或使用可變屬性 |
//! | `self` | 無法直接表達 | 消耗物件，常用於「轉換」類型方法 |
//!
//! ## 生命週期的影響
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────┐
//! │              &self vs self 的生命週期                           │
//! │                                                                 │
//! │   let mean = pipeline.get_mean();   // &self，pipeline 仍有效   │
//! │                                                                 │
//! │   pipeline.normalize_mut();          // &mut self，pipeline 仍有效 │
//! │                                                                 │
//! │   let report = pipeline.into_report(); // self，pipeline 被消耗  │
//! │   // pipeline 已被 drop，無法再使用                               │
//! │   pipeline.get_mean();              // ❌ 編譯錯誤！             │
//! └─────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## 執行方式
//!
//! ```bash
//! cd ch03_ownership/05_method_and_data
//! cargo run
//! ```

struct DataPipeline {
    data: Vec<f64>,
}
impl DataPipeline {
    // &self：唯讀借用，像儀器的「顯示螢幕」，安全地讀取狀態而不改變它。
    // 返回 Option 是因為平均值可能在資料為空時不存在，這是穩健的 API 設計。
    fn get_mean(&self) -> Option<f64> {
        if self.data.is_empty() {
            None
        } else {
            Some(self.data.iter().sum::<f64>() / self.data.len() as f64)
        }
    }
    // &mut self：可變借用，像儀器的「校準旋鈕」，獨佔地修改內部資料。
    // 注意，此方法會直接改變 data 欄位的內容。
    fn normalize_mut(&mut self) {
        if let Some(mean) = self.get_mean() {
            for value in &mut self.data {
                *value -= mean;
            }
        }
    }
    // self：取得所有權，像儀器的「產出報告」功能，消耗物件以產生最終結果。
    // 方法名中的 "into_" 是一個常見慣例，暗示此方法會進行所有權轉移。
    fn into_report(self) -> String {
        let mean = self.get_mean().unwrap_or(0.0);
        format!("Final dataset mean: {:.2}", mean)
    }
}

fn main() {
    let mut pipeline = DataPipeline {
        data: vec![1.0, 2.0, 3.0],
    };

    let mean = pipeline.get_mean().unwrap();
    println!("{}", mean);

    pipeline.normalize_mut();
    println!("{:?}", pipeline.data);

    let report = pipeline.into_report();
    println!("{}", report);
}