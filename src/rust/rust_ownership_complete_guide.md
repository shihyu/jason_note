# Rust 所有權完整指南 - 從基礎到精通 🦀

## 🎯 核心概念速覽

**最重要的理解**：
- ✅ **擁有權 (Ownership)**：我的東西，沒有生命週期問題
- ⚠️ **借用 (Borrowing)**：別人的東西，需要生命週期保護
- 📊 **記憶體管理**：Stack vs Heap 決定了不同的行為
- 🔄 **資料複製**：Copy vs Clone 的關鍵差異

---

## 📚 第一部分：記憶體基礎 - Stack vs Heap

### 🏗️ Stack（堆疊）- 快速且簡單

**特徵**：
- 速度快，像疊盤子一樣 LIFO（後進先出）
- 大小在編譯時就知道
- 自動管理，不需要手動清理
- **沒有 ownership 問題！**

**存放內容**：
```rust
// 這些都存在 Stack 上
let age: i32 = 25;           // 4 bytes，固定大小
let height: f64 = 175.5;     // 8 bytes，固定大小
let is_student: bool = true; // 1 byte，固定大小
let coordinates: (i32, i32) = (10, 20); // 8 bytes，固定大小

// 這些是 Stack 上的「指標」，指向 Heap 的資料
let name: String = String::from("小明");  // String 本身在 Stack，內容在 Heap
let numbers: Vec<i32> = vec![1, 2, 3];   // Vec 本身在 Stack，內容在 Heap
```

### 🏠 Heap（堆積）- 靈活但複雜

**特徵**：
- 較慢，需要記憶體分配器尋找空間
- 大小可以在執行時改變
- 需要手動管理（Rust 幫你做）
- **這裡才有 ownership 問題！**

**存放內容**：
```rust
// String 的資料存在 Heap
let mut message = String::from("Hello");
message.push_str(" World");  // 可以動態增長

// Vec 的資料存在 Heap  
let mut numbers = Vec::new();
numbers.push(1);  // 可以動態添加元素
numbers.push(2);
```

### 🧠 記憶體布局視覺化

```
Stack                    Heap
┌─────────────┐         ┌──────────────────┐
│ age: 25     │         │                  │
├─────────────┤         │  "Hello World"   │ ← message 指向這裡
│ message: ●──┼────────→│  (11 bytes)      │
├─────────────┤         │                  │
│ numbers: ●──┼────────→│  [1, 2, 3]       │
└─────────────┘         │  (12 bytes)      │
                        └──────────────────┘
```

---

## 🎭 第二部分：Copy vs Clone - 資料複製的兩種方式

### 📋 Copy Trait - 像影印身分證

**什麼是 Copy**：
- 在 Stack 上的簡單位元複製
- 非常快速，像影印一樣
- **自動發生，不需要手動呼叫**
- **原始變數仍然有效**

**哪些類型實作了 Copy**：
```rust
// 基本數值類型 - 都實作了 Copy
let x: i32 = 5;
let y = x;  // 自動 copy，x 仍然可用
println!("x = {}, y = {}", x, y);  // ✅ 都可以用

// 其他 Copy 類型
let a: u32 = 10;
let b: f64 = 3.14;
let c: bool = true;
let d: char = '🦀';
let e: (i32, i32) = (1, 2);  // 如果元素都是 Copy，tuple 也是 Copy

// 陣列（如果元素是 Copy）
let arr1: [i32; 3] = [1, 2, 3];
let arr2 = arr1;  // Copy
println!("{:?} {:?}", arr1, arr2);  // ✅ 都可以用
```

**為什麼這些類型可以 Copy**：
- 它們的大小固定且已知
- 都存在 Stack 上
- 複製成本很低
- 沒有指向 Heap 的指標

### 🖨️ Clone Trait - 蓋一間一模一樣的房子

**什麼是 Clone**：
- 深度複製，包括 Heap 上的資料
- 可能很耗時和記憶體
- **需要手動呼叫 `.clone()`**
- 創建完全獨立的副本

```rust
// String 需要 Clone（因為資料在 Heap）
let s1 = String::from("Hello");
let s2 = s1.clone();  // 手動 clone
println!("s1 = {}, s2 = {}", s1, s2);  // ✅ 都可以用

// Vec 需要 Clone
let v1 = vec![1, 2, 3];
let v2 = v1.clone();  // 複製整個向量和所有元素
println!("v1 = {:?}, v2 = {:?}", v1, v2);  // ✅ 都可以用

// 複雜結構的 Clone
#[derive(Clone)]
struct Person {
    name: String,
    age: i32,
}

let person1 = Person {
    name: String::from("小明"),
    age: 25,
};
let person2 = person1.clone();  // 深度複製所有字段
```

### ⚖️ Copy vs Clone 對比表

| 特徵 | Copy | Clone |
|------|------|-------|
| **觸發方式** | 自動（賦值時） | 手動（`.clone()`） |
| **速度** | 非常快 | 可能較慢 |
| **記憶體** | 只複製 Stack | 可能複製 Heap |
| **原變數** | 仍然有效 | 仍然有效 |
| **適用類型** | 簡單類型 | 所有實作 Clone 的類型 |
| **成本** | 幾乎為零 | 取決於資料大小 |

### 🔍 實際例子：何時用 Copy vs Clone

```rust
fn copy_example() {
    let x = 42;
    let y = x;  // Copy 自動發生
    
    println!("x: {}, y: {}", x, y);  // 兩個都能用
    // 沒有性能問題，因為只是複製了 4 bytes
}

fn clone_example() {
    let big_string = "A".repeat(1_000_000);  // 100萬個字元
    let another_string = big_string.clone();  // 手動 clone
    
    // 這會複製 1MB 的資料！考慮是否真的需要
    println!("Original length: {}", big_string.len());
    println!("Clone length: {}", another_string.len());
}

fn better_approach() {
    let big_string = "A".repeat(1_000_000);
    let string_ref = &big_string;  // 借用，不複製
    
    // 只是借用，沒有複製成本
    println!("Length: {}", string_ref.len());
}
```

---

## 🏠 第三部分：Ownership 系統詳解

### 📜 基本規則（用房子比喻）

1. **每個值都有一個所有者** - 每間房子都有房主
2. **同時只能有一個所有者** - 一間房子只能有一個房主
3. **所有者離開時，值被銷毀** - 房主搬走，房子拆除

### 🚨 重要：Ownership 只發生在 Heap 資料！

```rust
// Stack 資料 - 沒有 ownership 問題
let x = 5;
let y = x;  // Copy，兩個都有效
println!("{} {}", x, y);  // ✅ 完全沒問題

// Heap 資料 - 有 ownership 問題
let s1 = String::from("hello");
let s2 = s1;  // Move！s1 失效
// println!("{}", s1);  // ❌ 編譯錯誤！s1 已經無效
println!("{}", s2);     // ✅ s2 有效
```

**為什麼只有 Heap 資料有 ownership 問題？**

1. **Stack 資料**：
   - 大小固定，複製成本低
   - 自動管理，作用域結束就清理
   - 可以安全地複製多份

2. **Heap 資料**：
   - 大小可變，複製成本高
   - 需要明確的清理策略
   - 多個指標指向同一塊記憶體會造成問題

### 📦 Move：轉移所有權

```rust
fn move_example() {
    let house = String::from("豪華別墅");  // house 是房主
    let new_owner = house;               // 房契轉移給 new_owner
    
    // println!("{}", house);  // ❌ house 已經不是房主了
    println!("{}", new_owner); // ✅ new_owner 現在是房主
    
    // 函數調用也會 move
    take_ownership(new_owner);  // new_owner 的所有權轉移到函數內
    // println!("{}", new_owner);  // ❌ new_owner 已經無效
}

fn take_ownership(some_string: String) {
    println!("{}", some_string);
}  // some_string 在這裡被銷毀
```

---

## 🔗 第四部分：借用 (Borrowing) 與生命週期

### 🎯 核心概念：只有借用才有生命週期問題！

| 類型 | 生命週期 | 範例 | 說明 |
|------|----------|------|------|
| **擁有類型** | ❌ 不需要 | `String`, `Vec<T>`, `i32` | 我的東西，隨便用 |
| **借用類型** | ✅ 需要 | `&str`, `&Vec<T>`, `&i32` | 別人的東西，要小心 |

### 🔍 不可變借用：借來看看

```rust
fn immutable_borrow() {
    let book = String::from("Rust 程式設計");
    let page_count = count_pages(&book);  // 借用去數頁數
    
    println!("《{}》有 {} 頁", book, page_count);  // ✅ book 還在
}

fn count_pages(book_ref: &String) -> usize {
    book_ref.len()  // 只是看看，不修改
}
```

### ✏️ 可變借用：借來修改

```rust
fn mutable_borrow() {
    let mut note = String::from("今天學 Rust");
    add_comment(&mut note);  // 可變借用
    
    println!("{}", note);    // ✅ note 被修改了
}

fn add_comment(note_ref: &mut String) {
    note_ref.push_str("，很有趣！");
}
```

### 🚨 借用規則

1. **可以有多個不可變借用**
2. **只能有一個可變借用**
3. **可變借用期間，不能有其他借用**

```rust
fn borrowing_rules() {
    let mut data = String::from("資料");
    
    // ✅ 多個不可變借用 OK
    let r1 = &data;
    let r2 = &data;
    println!("{} 和 {}", r1, r2);
    
    // ✅ 可變借用（在不可變借用結束後）
    let r3 = &mut data;
    r3.push_str("更新");
    println!("{}", r3);
    
    // ❌ 這樣會錯誤：同時有可變和不可變借用
    // let r4 = &data;
    // let r5 = &mut data;  // 錯誤！
}
```

---

## ⚠️ 第五部分：生命週期詳解

### 🤔 什麼時候需要生命週期標註？

**函數接收引用並返回引用** → 必須寫生命週期標註！

```rust
// ❌ 編譯錯誤：缺少生命週期標註
fn longest(x: &str, y: &str) -> &str {
    if x.len() > y.len() { x } else { y }
}

// ✅ 正確：明確生命週期關係
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

### 🧠 編譯器的困惑

編譯器需要知道：
- 返回的引用來自哪個參數？
- 這個引用能活多久？
- 如何確保不會產生懸空指標？

```rust
fn lifetime_example() {
    let string1 = "long string is long";
    
    {
        let string2 = "xyz";
        let result = longest(string1, string2);
        println!("最長的是：{}", result);
        // result 在這裡還能用，因為兩個輸入都還活著
    }
    // string2 死了，但沒關係，我們已經用完 result
}
```

### 💡 避免生命週期的方法

#### 方案 1：返回擁有權
```rust
fn longest_owned(x: &str, y: &str) -> String {
    if x.len() > y.len() {
        x.to_string()  // 創建新的 String
    } else {
        y.to_string()
    }
}
```

#### 方案 2：返回其他資訊
```rust
fn is_first_longer(x: &str, y: &str) -> bool {
    x.len() > y.len()
}
```

---

## 📋 第六部分：結構體中的選擇

### ✅ 方案 A：全用擁有權（推薦新手）

```rust
struct Person {
    name: String,        // 擁有
    email: String,       // 擁有
    age: u32,           // 擁有（Copy 類型）
}

impl Person {
    fn new(name: String, email: String, age: u32) -> Self {
        Person { name, email, age }
    }
    
    // 完全沒有生命週期問題！
    fn introduction(&self) -> String {
        format!("我是 {}，{}歲，email: {}", 
                self.name, self.age, self.email)
    }
}

fn owned_example() {
    let person = Person::new(
        "小明".to_string(),
        "ming@example.com".to_string(),
        25
    );
    
    println!("{}", person.introduction());
}
```

### ⚠️ 方案 B：使用借用（需要生命週期）

```rust
struct PersonRef<'a> {
    name: &'a str,       // 借用 - 需要 'a
    email: &'a str,      // 借用 - 需要 'a  
    age: u32,           // 擁有 - 不需要 'a
}

impl<'a> PersonRef<'a> {
    fn new(name: &'a str, email: &'a str, age: u32) -> Self {
        PersonRef { name, email, age }
    }
    
    fn introduction(&self) -> String {
        format!("我是 {}，{}歲，email: {}", 
                self.name, self.age, self.email)
    }
}

fn borrowed_example() {
    let name = "小華";
    let email = "hua@example.com";
    
    let person = PersonRef::new(name, email, 30);
    println!("{}", person.introduction());
    // name 和 email 必須比 person 活得更久
}
```

---

## 🎯 第七部分：實用指南

### 🚀 什麼時候用借用？

**✅ 適合借用的情況**：
1. **函數參數** - 避免不必要的所有權轉移
2. **大型資料** - 避免昂貴的複製
3. **短期使用** - 臨時操作

```rust
// 函數參數借用
fn print_info(name: &str, age: u32) {
    println!("{} 今年 {} 歲", name, age);
}

// 處理大型資料
fn analyze_data(data: &Vec<u8>) -> usize {
    data.len()  // 只需要讀取，不需要擁有
}

// 字串切片
fn get_first_word(text: &str) -> &str {
    match text.find(' ') {
        Some(index) => &text[..index],
        None => text,
    }
}
```

**❌ 不適合借用的情況**：
1. **結構體字段** - 複雜的生命週期管理
2. **返回值** - 避免懸空引用
3. **長期存儲** - 所有權更清晰

### 🧠 記憶口訣與決策樹

#### 生命週期決策樹
```
是否需要寫生命週期標註？
├─ 有 `&` 符號嗎？
│  ├─ 沒有 → ❌ 不需要
│  └─ 有 → 繼續判斷
│      ├─ 函數接收引用並返回引用？
│      │  ├─ 是 → ✅ 需要生命週期標註
│      │  └─ 否 → ❌ 不需要
│      └─ 結構體存儲引用？
│         └─ 是 → ✅ 需要生命週期標註
```

#### 記憶口訣
- **Stack 資料 Copy，Heap 資料 Move**
- **擁有權在 Heap，Copy 在 Stack**
- **借用要歸還，生命週期保安全**
- **函數進出都是引用，生命週期必須標**

### 🎨 實用範例：配置管理

```rust
// 推薦：全擁有權版本
#[derive(Debug, Clone)]
struct Config {
    database_url: String,
    api_key: String,
    max_connections: u32,
    debug_mode: bool,
}

impl Config {
    fn from_env() -> Self {
        Config {
            database_url: std::env::var("DATABASE_URL")
                .unwrap_or_else(|_| "localhost:5432".to_string()),
            api_key: std::env::var("API_KEY")
                .unwrap_or_else(|_| "default_key".to_string()),
            max_connections: 10,
            debug_mode: false,
        }
    }
    
    fn connection_string(&self) -> String {
        format!("{}?max_conn={}", self.database_url, self.max_connections)
    }
}

// 使用
fn main() {
    let config = Config::from_env();
    println!("設定：{:?}", config);
    println!("連接字串：{}", config.connection_string());
    
    // 可以輕鬆複製配置
    let backup_config = config.clone();
    println!("備份設定：{:?}", backup_config);
}
```

---

## 📊 第八部分：性能考慮

### ⚡ 性能對比

| 操作 | Stack | Heap | 說明 |
|------|-------|------|------|
| **分配** | 極快 | 較慢 | Stack 只需移動指標 |
| **存取** | 極快 | 較慢 | Stack 有更好的局部性 |
| **複製** | 快 | 慢 | Stack 是簡單的記憶體複製 |
| **清理** | 自動 | 自動 | Rust 的 RAII 系統 |

### 🔧 優化建議

```rust
// ❌ 不必要的分配
fn bad_example() -> String {
    let mut result = String::new();
    for i in 0..1000 {
        result = format!("{}{}", result, i);  // 每次都重新分配！
    }
    result
}

// ✅ 更好的方法
fn good_example() -> String {
    let mut result = String::with_capacity(4000);  // 預分配容量
    for i in 0..1000 {
        result.push_str(&i.to_string());
    }
    result
}

// ✅ 最佳方法（如果可能的話）
fn best_example(buffer: &mut String) {
    buffer.clear();
    for i in 0..1000 {
        buffer.push_str(&i.to_string());
    }
}
```

---

## 🏆 總結：掌握 Rust 所有權的關鍵

### 🎯 核心理解框架

1. **記憶體模型**：
   - Stack = 快速 + 自動管理 + Copy
   - Heap = 靈活 + 手動管理 + Move

2. **所有權規則**：
   - 只有 Heap 資料有所有權問題
   - Stack 資料自動 Copy，沒有所有權轉移

3. **借用系統**：
   - 不可變借用：隨意多個
   - 可變借用：獨佔一個
   - 生命週期確保安全

4. **生命週期標註**：
   - 只在必要時使用
   - 函數輸入輸出都是引用時需要
   - 結構體存儲引用時需要

### 🚀 實踐建議

**初學者策略**：
1. 優先使用擁有權類型（String, Vec, etc.）
2. 函數參數使用借用（&str, &[T], etc.）
3. 避免在結構體中存儲引用
4. 理解 Copy vs Clone 的差異

**進階優化**：
1. 合理使用借用減少複製
2. 理解生命週期標註的時機
3. 選擇合適的資料結構
4. 考慮性能影響

**記憶要點**：
- 🏠 **擁有權** = 房子是我的，我控制何時拆除
- 📞 **借用** = 朋友借房子，朋友搬家前要還回來
- 📋 **Copy** = 像影印身分證，簡單快速
- 🖨️ **Clone** = 蓋一間一樣的房子，費時費力
- 🧠 **生命週期** = 確保借用安全的編譯時檢查

Rust 的所有權系統看似複雜，但掌握這些核心概念後，你就能寫出既安全又高效的程式碼！🎉