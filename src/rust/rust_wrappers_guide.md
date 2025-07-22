# Rust 包裝類型白話指南 📦

> 用最簡單的話解釋 Rust 的各種"盒子"

## 基礎概念 🎯

想像你有很多不同的盒子，每個盒子都有不同的特殊能力：

## 1. Box<T> - 普通紙盒 📦

**白話解釋：** 把東西放到堆上的盒子，你是唯一的主人。

**使用時機：** 東西太大放不進棧，或者需要遞歸結構。

```rust
// 簡單例子
let big_data = Box::new([0; 1000000]); // 把大陣列放到堆上
println!("數據在堆上：{}", big_data.len());

// 遞歸結構（鏈表）
enum List {
    Node(i32, Box<List>),  // 沒有 Box 就編譯不過
    Empty,
}
```

**關鍵特點：**
- ✅ 獨占所有權（只有你能用）
- ✅ 自動清理（離開作用域就釋放）
- ❌ 不能共享

---

## 2. Rc<T> - 共享盒子（單線程）🔗

**白話解釋：** 可以被多個人同時使用的盒子，有引用計數器。

**使用時機：** 單線程中多個地方需要使用同一個數據。

```rust
use std::rc::Rc;

let data = Rc::new("共享數據".to_string());
let reference1 = data.clone();  // 引用計數 +1
let reference2 = data.clone();  // 引用計數 +1

println!("引用計數：{}", Rc::strong_count(&data)); // 輸出：3
println!("數據：{}", reference1);
```

**關鍵特點：**
- ✅ 多個所有者
- ✅ 自動清理（引用計數為 0 時）
- ❌ 不能修改內容
- ❌ 不是線程安全

---

## 3. Arc<T> - 共享盒子（多線程）🌐

**白話解釋：** 線程安全版本的 `Rc`，可以在不同線程間傳遞。

**使用時機：** 多線程程序中共享數據。

```rust
use std::sync::Arc;
use std::thread;

let data = Arc::new("多線程共享數據".to_string());

let mut handles = vec![];
for i in 0..3 {
    let data_clone = data.clone();
    let handle = thread::spawn(move || {
        println!("線程 {} 看到：{}", i, data_clone);
    });
    handles.push(handle);
}

for handle in handles {
    handle.join().unwrap();
}
```

**關鍵特點：**
- ✅ 多個所有者
- ✅ 線程安全
- ❌ 不能修改內容

---

## 4. RefCell<T> - 魔法盒子（運行時借用）🎭

**白話解釋：** 可以在「不可變」的情況下修改內容的魔法盒子。

**使用時機：** 需要在不可變環境中修改數據。

```rust
use std::cell::RefCell;

let data = RefCell::new(42);

// 讀取
println!("值：{}", data.borrow()); // 42

// 修改
*data.borrow_mut() = 100;
println!("修改後：{}", data.borrow()); // 100

// 在不可變函數中修改
fn modify_data(cell: &RefCell<i32>) {  // 注意：不可變引用
    *cell.borrow_mut() = 999;  // 但還是能修改！
}
modify_data(&data);
```

**關鍵特點：**
- ✅ 內部可變性
- ✅ 運行時借用檢查
- ❌ 違反規則會 panic
- ❌ 不是線程安全

---

## 5. Cell<T> - 簡單替換盒子 🔄

**白話解釋：** 只能整個替換，不能借用內部的簡單盒子。

**使用時機：** 簡單類型的內部可變性。

```rust
use std::cell::Cell;

let data = Cell::new(42);

println!("原值：{}", data.get()); // 42
data.set(100);                    // 整個替換
println!("新值：{}", data.get()); // 100

// 交換
let old = data.replace(200);
println!("舊值：{}，新值：{}", old, data.get());
```

**關鍵特點：**
- ✅ 比 RefCell 簡單
- ✅ 沒有運行時借用檢查開銷
- ❌ 只能整體替換
- ❌ 不能借用內部值

---

## 6. Mutex<T> - 帶鎖的盒子 🔒

**白話解釋：** 多線程環境下帶鎖的盒子，同時只能一個人用。

**使用時機：** 多線程中需要修改共享數據。

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..5 {
    let counter = counter.clone();
    let handle = thread::spawn(move || {
        let mut num = counter.lock().unwrap(); // 獲取鎖
        *num += 1;
    }); // 鎖自動釋放
    handles.push(handle);
}

for handle in handles {
    handle.join().unwrap();
}

println!("最終計數：{}", *counter.lock().unwrap());
```

**關鍵特點：**
- ✅ 線程安全
- ✅ 內部可變性
- ❌ 可能阻塞
- ❌ 可能死鎖

---

## 7. Option<T> - 可能空的盒子 📦❓

**白話解釋：** 可能有東西，也可能沒東西的盒子。

**使用時機：** 表示可能不存在的值。

```rust
fn find_number(numbers: &[i32], target: i32) -> Option<usize> {
    for (index, &num) in numbers.iter().enumerate() {
        if num == target {
            return Some(index);  // 找到了
        }
    }
    None  // 沒找到
}

let numbers = vec![1, 2, 3, 4, 5];

match find_number(&numbers, 3) {
    Some(index) => println!("找到了，在位置：{}", index),
    None => println!("沒找到"),
}

// 或者用更簡潔的方式
if let Some(index) = find_number(&numbers, 3) {
    println!("找到了，在位置：{}", index);
}
```

**關鍵特點：**
- ✅ 強制處理空值情況
- ✅ 沒有空指針異常
- ✅ 表達力強

---

## 8. Result<T, E> - 可能出錯的盒子 ⚠️

**白話解釋：** 操作可能成功也可能失敗的盒子。

**使用時機：** 可能失敗的操作。

```rust
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err("不能除零！".to_string())
    } else {
        Ok(a / b)
    }
}

match divide(10.0, 2.0) {
    Ok(result) => println!("結果：{}", result),
    Err(error) => println!("錯誤：{}", error),
}

// 或者用 ? 運算符傳播錯誤
fn calculate() -> Result<f64, String> {
    let result = divide(10.0, 2.0)?;  // 如果錯誤就直接返回錯誤
    Ok(result * 2.0)
}
```

**關鍵特點：**
- ✅ 強制處理錯誤
- ✅ 類型安全
- ✅ 可以鏈式操作

---

## 9. Weak<T> - 弱引用盒子 🔗💔

**白話解釋：** 不增加引用計數的「弱」引用，避免循環依賴。

**使用時機：** 避免 `Rc` 循環引用導致內存洩漏。

```rust
use std::rc::{Rc, Weak};
use std::cell::RefCell;

struct Parent {
    children: RefCell<Vec<Rc<Child>>>,
}

struct Child {
    parent: RefCell<Weak<Parent>>,  // 用 Weak 避免循環
}

let parent = Rc::new(Parent {
    children: RefCell::new(vec![]),
});

let child = Rc::new(Child {
    parent: RefCell::new(Rc::downgrade(&parent)),  // 創建弱引用
});

parent.children.borrow_mut().push(child.clone());

// 通過弱引用訪問父節點
if let Some(parent_ref) = child.parent.borrow().upgrade() {
    println!("子節點找到了父節點！");
}
```

**關鍵特點：**
- ✅ 避免循環引用
- ✅ 自動清理
- ❌ 可能訪問失敗

---

## 10. Cow<T> - 寫時複製盒子 🐄

**白話解釋：** 平時借用，需要修改時才複製的聰明盒子。

**使用時機：** 大部分時候只讀，偶爾需要修改的情況。

```rust
use std::borrow::Cow;

fn process_text(input: &str) -> Cow<str> {
    if input.contains("bug") {
        // 需要修改，創建新的
        Cow::Owned(input.replace("bug", "feature"))
    } else {
        // 不需要修改，直接借用
        Cow::Borrowed(input)
    }
}

let text1 = "Hello world";
let result1 = process_text(text1);
println!("'{}'，沒有複製", result1);

let text2 = "This is a bug";  
let result2 = process_text(text2);
println!("'{}'，發生了複製", result2);
```

**關鍵特點：**
- ✅ 性能優化
- ✅ 按需複製
- ✅ 透明使用

---

## 常用組合套餐 🍱

### 單線程共享可變數據
```rust
Rc<RefCell<T>>
```
**說明：** 多個地方共享，還能修改

### 多線程共享可變數據  
```rust
Arc<Mutex<T>>
```
**說明：** 多線程共享，帶鎖修改

### 可選的共享數據
```rust
Option<Rc<T>>
```
**說明：** 可能沒有，如果有就是共享的

### 可能失敗的操作
```rust
Result<Option<T>, Error>
```
**說明：** 操作可能失敗，成功了也可能沒有值

## 選擇指南 🎯

| 需求 | 選擇 | 理由 |
|------|------|------|
| 堆分配 | `Box<T>` | 簡單直接 |
| 單線程共享 | `Rc<T>` | 多個所有者 |
| 多線程共享 | `Arc<T>` | 線程安全 |
| 內部可變性 | `RefCell<T>` | 運行時檢查 |
| 簡單內部可變性 | `Cell<T>` | 整體替換 |
| 多線程可變 | `Mutex<T>` | 帶鎖保護 |
| 可選值 | `Option<T>` | 可能沒有 |
| 錯誤處理 | `Result<T,E>` | 可能失敗 |
| 避免循環引用 | `Weak<T>` | 弱引用 |
| 性能優化 | `Cow<T>` | 寫時複製 |

## 記憶小貼士 💡

- **Box**: 📦 = 普通盒子，一個主人
- **Rc**: 🔗 = Reference Counting，多個主人（單線程）
- **Arc**: 🌐 = Atomic Rc，多個主人（多線程）
- **RefCell**: 🎭 = 運行時魔法，可變的不可變
- **Cell**: 🔄 = 簡單替換
- **Mutex**: 🔒 = 互斥鎖
- **Option**: ❓ = 可能有可能沒有
- **Result**: ⚠️ = 成功或失敗  
- **Weak**: 💔 = 弱引用，不算數
- **Cow**: 🐄 = 寫時複製，聰明牛

記住：每個「盒子」都是為了解決特定問題，選對盒子事半功倍！ 🚀