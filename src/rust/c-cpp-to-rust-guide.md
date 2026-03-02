# C/C++ 開發者學 Rust：完整差異指南

![Rust 標誌](images/rust-logo-blk.svg)

如果你有 C/C++ 底子，學 Rust 最難的通常不是語法，而是把「先寫、再小心避錯」改成「先讓編譯器證明安全」。這份筆記用對照方式整理最重要的差異。

## 快速對照

| 主題 | C/C++ 習慣 | Rust 做法 |
| --- | --- | --- |
| 記憶體管理 | 手動管理或倚賴 RAII | 所有權 + 借用 + 編譯期檢查 |
| 空值 | `NULL` / `nullptr` | `Option<T>` |
| 錯誤處理 | 錯誤碼或例外 | `Result<T, E>` |
| 多型 | 繼承、虛函式 | Trait |
| 並行安全 | 靠慣例與審查 | 型別系統直接限制 |

## 1. 所有權系統（Ownership）

這是 Rust 最核心的差異，C/C++ 沒有完全對應的概念。

```rust
let s1 = String::from("hello");
let s2 = s1; // s1 被 move，之後不能再使用

// println!("{}", s1); // ❌ 編譯錯誤
println!("{}", s2); // ✅
```

對比 C++：

```cpp
std::string s1 = "hello";
std::string s2 = s1; // 複製後兩個都能用
```

重點規則：

- 每個值同一時間只有一個 owner。
- owner 離開 scope，值就會自動釋放。
- 沒有 GC，也不鼓勵手動控制釋放時機。

## 2. 借用（Borrowing）與指標的差異

Rust 不是不讓你參考資料，而是要求你用可驗證的方式參考。

```rust
fn print_len(s: &String) {
    println!("{}", s.len());
}

fn append_world(s: &mut String) {
    s.push_str(" world");
}
```

同一時間只能滿足其中一種情況：

- 多個不可變借用 `&T`
- 一個可變借用 `&mut T`

這代表很多 C/C++ 常見的懸空指標、重複釋放、資料競態，會在編譯期就被擋下來。

## 3. 沒有 `null`，改用 `Option<T>`

```rust
let maybe: Option<i32> = Some(42);
let nothing: Option<i32> = None;

match maybe {
    Some(value) => println!("{}", value),
    None => println!("空值"),
}
```

Rust 不讓你假裝空值不存在，而是強迫你顯式處理。

## 4. 錯誤處理：`Result<T, E>`

Rust 用 `Result<T, E>` 取代「回傳錯誤碼但常被忽略」或「例外一路往外炸」的做法。

```rust
use std::io;

fn read_file(path: &str) -> Result<String, io::Error> {
    std::fs::read_to_string(path)
}

fn process() -> Result<(), io::Error> {
    let _content = read_file("a.txt")?;
    Ok(())
}
```

`?` 運算子代表「失敗就往上回傳」，簡潔但仍然是顯式流程。

## 5. 編譯器非常嚴格

| C/C++ 常見問題 | Rust 的處理方式 |
| --- | --- |
| 懸空指標導致執行期崩潰 | 編譯期拒絕 |
| data race / 未定義行為 | 編譯期拒絕 |
| use-after-free | 編譯期拒絕 |
| 未初始化變數 | 編譯期拒絕 |

Rust 的學習成本，有很大一部分就是把這些風險前移到編譯階段。

## 6. Trait 與繼承的差異

Rust 沒有傳統類別繼承，主要靠 Trait 組合行為。

```rust
trait Animal {
    fn speak(&self) -> &str;

    fn description(&self) -> String {
        format!("我會說：{}", self.speak())
    }
}

struct Dog;
struct Cat;

impl Animal for Dog {
    fn speak(&self) -> &str {
        "汪"
    }
}

impl Animal for Cat {
    fn speak(&self) -> &str {
        "喵"
    }
}
```

這種做法通常比深層繼承鏈更直觀，也更容易維護。

## 7. 泛型與 Trait Bound

Rust 的泛型比 C++ template 更明確，因為能力需求會先寫在型別約束上。

```rust
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];

    for item in list {
        if item > largest {
            largest = item;
        }
    }

    largest
}
```

你不用等模板展開失敗才知道缺了什麼能力。

## 8. 模式比對：`match`

`match` 幾乎是 Rust 控制流程的核心工具之一。

```rust
enum Shape {
    Circle(f64),
    Rectangle(f64, f64),
    Triangle(f64, f64, f64),
}

let shape = Shape::Circle(3.0);

let area = match shape {
    Shape::Circle(radius) => std::f64::consts::PI * radius * radius,
    Shape::Rectangle(width, height) => width * height,
    Shape::Triangle(a, b, c) => {
        let semi = (a + b + c) / 2.0;
        (semi * (semi - a) * (semi - b) * (semi - c)).sqrt()
    }
};
```

少一個分支就不能編譯，這和 C 的 `switch` 是完全不同的安全等級。

## 9. 沒有隱式數值轉型

```rust
let x: i32 = 5;
// let y: i64 = x; // ❌ 編譯錯誤
let y: i64 = x as i64; // ✅ 必須明確轉型
```

這能少掉很多 C/C++ 因隱式轉型帶來的細碎 bug。

## 10. 記憶體模型更直接

```rust
use std::rc::Rc;
use std::sync::Arc;

let a = 5; // stack 上的值
let b = Box::new(5); // heap 配置，類似 unique_ptr
let c = Rc::new(5); // 單執行緒引用計數
let d = Arc::new(5); // 可跨執行緒共享的引用計數
```

Rust 不會把擁有權、共享、可變性混在一起讓你猜。

## 11. 並行安全

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let data = Arc::new(Mutex::new(vec![1, 2, 3]));
let data_clone = Arc::clone(&data);

let handle = thread::spawn(move || {
    let mut guard = data_clone.lock().unwrap();
    guard.push(4);
});

handle.join().unwrap();
```

在 Rust 裡，共享狀態要不要加鎖、能不能跨執行緒傳遞，通常會先反映在型別上，而不是留到執行期出事。

## 12. Cargo：內建工具鏈

C/C++ 的建置、測試、套件管理常常要自己拼；Rust 直接把常用流程整合在 `cargo`。

```bash
cargo new my_project
cargo build
cargo test
cargo add serde
cargo doc --open
```

這讓 Rust 專案從初始化到測試都有一致入口。

## 心態對照

| C/C++ 思維 | Rust 思維 |
| --- | --- |
| 我知道這個指標現在是安全的 | 讓編譯器證明它安全 |
| 手動管理生命週期 | 由所有權模型管理 |
| `NULL` / `nullptr` 表示沒有值 | `Option<T>` 強迫處理 |
| 錯誤碼或 exception | `Result<T, E>` 顯式傳播 |
| 用繼承複用程式碼 | 用 Trait 組合行為 |
| 我小心一點就不會有競態 | 編譯器直接限制危險寫法 |

## 學習路線

1. **[The Rust Book](https://doc.rust-lang.org/book/)**：官方教材，優先看。
2. **[Rustlings](https://github.com/rust-lang/rustlings)**：用小題目熟悉語法與觀念。
3. **[Rust by Example](https://doc.rust-lang.org/rust-by-example/)**：查語法與小範例很快。
4. 先把第 4 章所有權吃透，再往後學會順很多。

> 關鍵心態：C/C++ 常是「你自己保證正確」；Rust 是「先證明正確，才能編譯通過」。
