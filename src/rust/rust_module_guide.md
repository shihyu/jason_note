# Rust 模組系統完全指南

## 📚 目錄
1. [基本概念](#基本概念)
2. [檔案與模組的關係](#檔案與模組的關係)
3. [pub 可見性規則](#pub-可見性規則)
4. [實戰範例](#實戰範例)
5. [常見模式](#常見模式)

---

## 基本概念

### 什麼是模組 (Module)?
模組是 Rust 組織代碼的方式，用來：
- 分組相關的功能
- 控制可見性（什麼能被外部使用）
- 組織檔案結構

### 核心規則
```rust
// 預設：一切都是私有的
struct Private;        // ❌ 外部不可見
pub struct Public;     // ✅ 外部可見

fn private_fn() {}     // ❌ 外部不可見
pub fn public_fn() {}  // ✅ 外部可見
```

---

## 模組 vs 檔案

### ⚠️ 重要觀念：模組 ≠ 檔案（但大部分時候是）

| 概念 | 說明 |
|------|------|
| **檔案** | 物理上的 `.rs` 檔案 |
| **模組** | 邏輯上的代碼組織單位 |

### 🎯 三種關係

#### 1️⃣ 一個檔案 = 一個模組（最常見 99%）
```
src/
├── main.rs     → 模組 crate
├── counter.rs  → 模組 counter
└── utils.rs    → 模組 utils
```

#### 2️⃣ 一個檔案 = 多個模組（內嵌模組）
```rust
// main.rs（一個檔案）
mod database {  // 模組 1
    pub fn connect() {
        println!("連接資料庫");
    }
}

mod cache {     // 模組 2
    pub fn get(key: &str) -> Option<String> {
        None
    }
}

mod utils {     // 模組 3
    pub fn format(s: &str) -> String {
        s.to_uppercase()
    }
}

fn main() {
    database::connect();
    cache::get("key1");
    utils::format("hello");
}
```
**一個檔案包含三個模組！**

#### 3️⃣ 一個資料夾 = 一個模組（模組樹）
```
src/
└── database/         → 模組 database
    ├── mod.rs        → 模組入口
    ├── query.rs      → 子模組 database::query
    └── connection.rs → 子模組 database::connection
```

```rust
// database/mod.rs
pub mod query;
pub mod connection;

pub fn init() {
    println!("初始化資料庫");
}

// database/query.rs
pub fn execute(sql: &str) {
    println!("執行: {}", sql);
}

// database/connection.rs
pub struct Connection {
    url: String,
}
```

### 📊 關係總結

```
檔案與模組的關係：
┌─────────────┐
│  一個檔案   │ ──┬──→ 通常是一個模組（最常見 ⭐）
└─────────────┘   │
                  └──→ 也可包含多個模組（用 mod {}）

┌─────────────┐
│ 一個資料夾  │ ─────→ 可以是一個模組（用 mod.rs 或同名.rs）
└─────────────┘
```

### 💡 實用建議

**什麼時候用內嵌模組（一個檔案多個模組）？**
- ✅ 小型輔助模組
- ✅ 測試模組 `#[cfg(test)] mod tests {}`
- ✅ 關係緊密的小型模組

**什麼時候用獨立檔案？**
- ✅ 功能完整的模組（推薦！）
- ✅ 代碼超過 100 行
- ✅ 需要被多處引用

**什麼時候用資料夾模組？**
- ✅ 模組有多個子模組
- ✅ 需要清楚的層級結構
- ✅ 大型功能模組

### 🎯 簡單記法

**99% 的情況可以這樣理解：**
1. **一個 `.rs` 檔案 = 一個模組**（最常見，優先使用）
2. **檔案內可以用 `mod {}` 創建子模組**（小型輔助功能）
3. **資料夾 + `mod.rs` 或同名 `.rs` = 一個模組**（大型模組）

**快速判斷公式：**
```
模組 ≈ 檔案（經驗法則，適用大部分情況）
```

**但要知道：**
- 模組是**邏輯概念**（組織代碼）
- 檔案是**物理概念**（.rs 文件）
- 它們通常一對一，但可以一對多或多對一

**記住這個就夠了：先把每個檔案當作一個模組，遇到例外再調整！**

---

## 檔案與模組的關係

### 規則 1️⃣：一個檔案 = 一個模組（標準做法）

```
src/
├── main.rs          → 模組 crate (根模組)
├── lib.rs           → 模組 crate (函式庫根模組)
├── counter.rs       → 模組 counter
└── utils.rs         → 模組 utils
```

### 規則 2️⃣：資料夾 = 模組 + mod.rs

```
src/
├── main.rs
└── database/
    ├── mod.rs       → 模組 database
    ├── query.rs     → 模組 database::query
    └── connection.rs → 模組 database::connection
```

**或使用新語法（推薦）：**
```
src/
├── main.rs
├── database.rs      → 模組 database
└── database/
    ├── query.rs     → 模組 database::query
    └── connection.rs → 模組 database::connection
```

---

## pub 可見性規則

### 🔒 可見性層級

| 關鍵字 | 說明 | 範圍 |
|--------|------|------|
| (無) | 私有 | 只有同模組可見 |
| `pub` | 公開 | 所有地方可見 |
| `pub(crate)` | crate 內公開 | 只有本專案內可見 |
| `pub(super)` | 父模組公開 | 只有上一層模組可見 |
| `pub(in path)` | 指定路徑公開 | 指定模組路徑可見 |

### 範例

```rust
// lib.rs
mod utils {
    pub struct Public;           // ✅ 所有地方可見
    pub(crate) struct CrateOnly; // ✅ 只有本專案可見
    pub(super) struct ParentOnly; // ✅ 只有 lib.rs 可見
    struct Private;               // ❌ 只有 utils 模組內可見
}

pub use utils::Public;  // ✅ 重新導出給外部
```

---

## 實戰範例

### 📁 範例 1：基本專案結構

```
my_project/
├── Cargo.toml
└── src/
    ├── main.rs
    ├── lib.rs
    ├── counter.rs
    └── utils.rs
```

#### 📄 `lib.rs`
```rust
// 宣告模組（告訴 Rust 這些檔案存在）
pub mod counter;
pub mod utils;

// 重新導出（簡化使用）
pub use counter::Counter;
```

#### 📄 `counter.rs`
```rust
pub struct Counter {
    count: u32,  // 私有欄位
}

impl Counter {
    pub fn new() -> Self {
        Counter { count: 0 }
    }
    
    pub fn increment(&mut self) {
        self.count += 1;
    }
    
    pub fn get(&self) -> u32 {
        self.count
    }
}

impl Iterator for Counter {
    type Item = u32;
    
    fn next(&mut self) -> Option<Self::Item> {
        self.count += 1;
        if self.count < 6 {
            Some(self.count)
        } else {
            None
        }
    }
}
```

#### 📄 `utils.rs`
```rust
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

// 只在本專案內可見
pub(crate) fn internal_helper() {
    println!("內部輔助函數");
}

// 私有函數
fn private_helper() {
    println!("完全私有");
}
```

#### 📄 `main.rs`
```rust
// 方式 1：使用完整路徑
use my_project::counter::Counter;

// 方式 2：使用重新導出
use my_project::Counter;

// 方式 3：導入整個模組
use my_project::utils;

fn main() {
    let mut counter = Counter::new();
    counter.increment();
    println!("Count: {}", counter.get());
    
    // 使用迭代器
    for num in Counter::new() {
        println!("{}", num);  // 1, 2, 3, 4, 5
    }
    
    // 使用 utils
    let sum = utils::add(5, 3);
    println!("Sum: {}", sum);
}
```

---

### 📁 範例 2：複雜的模組結構

```
my_app/
├── Cargo.toml
└── src/
    ├── main.rs
    ├── lib.rs
    ├── models.rs          → 模組 models
    ├── models/
    │   ├── user.rs        → 模組 models::user
    │   └── product.rs     → 模組 models::product
    ├── database.rs        → 模組 database
    └── database/
        ├── query.rs       → 模組 database::query
        └── connection.rs  → 模組 database::connection
```

#### 📄 `lib.rs`
```rust
// 宣告頂層模組
pub mod models;
pub mod database;

// 重新導出常用項目
pub use models::{User, Product};
pub use database::Connection;
```

#### 📄 `models.rs`
```rust
// 宣告子模組
pub mod user;
pub mod product;

// 重新導出（讓外部可以用 models::User）
pub use user::User;
pub use product::Product;
```

#### 📄 `models/user.rs`
```rust
pub struct User {
    pub id: u32,
    pub name: String,
    email: String,  // 私有欄位
}

impl User {
    pub fn new(id: u32, name: String, email: String) -> Self {
        User { id, name, email }
    }
    
    pub fn email(&self) -> &str {
        &self.email
    }
}
```

#### 📄 `models/product.rs`
```rust
pub struct Product {
    pub id: u32,
    pub name: String,
    pub price: f64,
}

impl Product {
    pub fn new(id: u32, name: String, price: f64) -> Self {
        Product { id, name, price }
    }
}
```

#### 📄 `database.rs`
```rust
pub mod query;
pub mod connection;

pub use connection::Connection;
```

#### 📄 `database/connection.rs`
```rust
pub struct Connection {
    url: String,
}

impl Connection {
    pub fn new(url: String) -> Self {
        Connection { url }
    }
    
    pub fn connect(&self) {
        println!("連接到: {}", self.url);
    }
}
```

#### 📄 `database/query.rs`
```rust
use super::connection::Connection;

pub struct Query<'a> {
    conn: &'a Connection,
}

impl<'a> Query<'a> {
    pub fn new(conn: &'a Connection) -> Self {
        Query { conn }
    }
    
    pub fn execute(&self, sql: &str) {
        println!("執行 SQL: {}", sql);
    }
}
```

#### 📄 `main.rs`
```rust
use my_app::{User, Product, Connection};
use my_app::database::query::Query;

fn main() {
    // 使用 models
    let user = User::new(1, "Alice".to_string(), "alice@example.com".to_string());
    println!("用戶: {}", user.name);
    
    let product = Product::new(1, "筆電".to_string(), 30000.0);
    println!("產品: {} - ${}", product.name, product.price);
    
    // 使用 database
    let conn = Connection::new("postgresql://localhost".to_string());
    conn.connect();
    
    let query = Query::new(&conn);
    query.execute("SELECT * FROM users");
}
```

---

## 常見模式

### 🎯 模式 1：扁平結構（小專案）

```
src/
├── main.rs
├── counter.rs
├── utils.rs
└── config.rs
```

```rust
// main.rs
mod counter;
mod utils;
mod config;

use counter::Counter;

fn main() {
    let c = Counter::new();
}
```

---

### 🎯 模式 2：分層結構（中型專案）

```
src/
├── main.rs
├── lib.rs
├── models/
│   ├── mod.rs (或 models.rs)
│   ├── user.rs
│   └── product.rs
├── services/
│   ├── mod.rs
│   ├── auth.rs
│   └── payment.rs
└── utils/
    ├── mod.rs
    └── helpers.rs
```

---

### 🎯 模式 3：完整應用結構（大型專案）

```
src/
├── main.rs
├── lib.rs
├── models/
│   ├── mod.rs
│   ├── user.rs
│   ├── product.rs
│   └── order.rs
├── services/
│   ├── mod.rs
│   ├── auth/
│   │   ├── mod.rs
│   │   ├── login.rs
│   │   └── register.rs
│   └── payment/
│       ├── mod.rs
│       ├── stripe.rs
│       └── paypal.rs
├── database/
│   ├── mod.rs
│   ├── connection.rs
│   └── migrations/
│       └── mod.rs
├── api/
│   ├── mod.rs
│   ├── routes.rs
│   └── handlers.rs
└── utils/
    ├── mod.rs
    ├── validation.rs
    └── formatting.rs
```

---

## 🔑 重點整理

### ✅ 一定要記住

1. **預設私有**：沒有 `pub` = 只有同模組可用
2. **一個檔案 = 一個模組**
3. **`mod` 宣告**：要使用其他檔案必須先 `mod filename;`
4. **`use` 導入**：簡化路徑，讓代碼更簡潔
5. **`pub use` 重新導出**：為使用者提供簡潔的 API

### 📋 檢查清單

- [ ] 結構體加了 `pub`？
- [ ] 方法加了 `pub`？
- [ ] 在 `lib.rs` 或父模組中宣告了 `mod`？
- [ ] 需要的話用 `pub use` 重新導出？
- [ ] 檔案結構清晰易懂？

### 🚫 常見錯誤

```rust
// ❌ 忘記宣告模組
use counter::Counter;  // 錯誤：找不到 counter

// ✅ 正確
mod counter;
use counter::Counter;

// ❌ 結構體沒有 pub
struct Counter { count: u32 }  // 其他檔案用不到

// ✅ 正確
pub struct Counter { count: u32 }

// ❌ 欄位沒有 pub，但想直接訪問
pub struct Counter { count: u32 }
let c = Counter { count: 5 };  // 錯誤

// ✅ 正確：用建構函數
pub struct Counter { count: u32 }
impl Counter {
    pub fn new() -> Self { Counter { count: 0 } }
}
```

---

## 🎓 進階技巧

### 條件編譯
```rust
#[cfg(test)]
mod tests {
    use super::*;  // 導入父模組的所有項目
    
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
```

### 內聯模組（小型輔助模組）
```rust
// main.rs
mod utils {
    pub fn helper() {
        println!("輔助函數");
    }
}

fn main() {
    utils::helper();
}
```

### 路徑簡化
```rust
// 使用 super 訪問父模組
use super::Config;

// 使用 crate 從根開始
use crate::models::User;

// 使用 self 當前模組
use self::internal::Helper;
```

---

**現在你已經掌握 Rust 模組系統了！🎉**