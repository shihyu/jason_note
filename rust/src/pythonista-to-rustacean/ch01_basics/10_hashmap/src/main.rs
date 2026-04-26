//! # HashMap（雜湊映射）
//!
//! ## 📖 概念說明
//!
//! HashMap 是 Rust 中用於儲存鍵值對的資料結構，類似 Python 的 `dict`。
//!
//! ```text
//! ┌──────────────────────────────────────────────────────────────────────┐
//! │  HashMap 內部結構                                                    │
//! ├──────────────────────────────────────────────────────────────────────┤
//! │                                                                      │
//! │  let mut scores = HashMap::new();                                   │
//! │  scores.insert(String::from("Blue"), 10);                           │
//! │  scores.insert(String::from("Yellow"), 50);                         │
//! │                                                                      │
//! │  ┌───────────────┐                                                  │
//! │  │  HashMap     │                                                  │
//! │  ├───────────────┤                                                  │
//! │  │  "Blue"  → 10│  ← 鍵與值的配對                                 │
//! │  │  "Yellow"→ 50│                                                  │
//! │  └───────────────┘                                                  │
//! │                                                                      │
//! └──────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## 🔑 核心操作
//!
//! | 操作 | 語法 | 說明 |
//! |------|------|------|
//! | 新建 | `HashMap::new()` | 建立空的 HashMap |
//! | 插入 | `.insert(k, v)` | 插入鍵值對 |
//! | 讀取 | `.get(&k)` | 取得值，回傳 `Option<&V>` |
//! | 迭代 | `for (k, v) in &map` | 遍歷所有鍵值對 |
//! | 計數 | `.entry(k).or_insert(0)` | 存在時更新，不存在時插入預設值 |
//!
//! ## 📝 與 Python 的對比
//!
//! | Python | Rust |
//! |--------|------|
//! | `d = {}` | `let mut d: HashMap<K, V> = HashMap::new();` |
//! | `d["key"] = value` | `d.insert("key", value);` |
//! | `d.get("key")` | `d.get(&"key")` |
//! | `d.get("key", 0)` | `d.entry("key").or_insert(0)` |
//!
//! ## ⚡ 計數模式詳解
//!
//! ```text
//! for word in text.split_whitespace() {
//!     let count = map.entry(word).or_insert(0);  // 取得或插入 0
//!     *count += 1;  // 解引用後遞增
//! }
//! ```

use std::collections::HashMap;

fn main() {
    let mut scores = HashMap::new();

    // 插入鍵值對
    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Yellow"), 50);

    // 讀取值
    // .get() 會回傳一個 Option<&V>
    let team_name = String::from("Blue");
    let score = scores.get(&team_name);

    match score {
        Some(s) => println!("Score for Blue: {}", s),
        None => println!("Team Blue not found."),
    }

    // 迭代
    for (key, value) in &scores {
        println!("{}: {}", key, value);
    }

    let text = "hello world wonderful world";
    let mut map = HashMap::new();
    for word in text.split_whitespace() {
        // 這一行是精華
        let count = map.entry(word).or_insert(0);
        *count += 1;
    }
    println!("{:?}", map); // {"world": 2, "hello": 1, "wonderful": 1}
}
