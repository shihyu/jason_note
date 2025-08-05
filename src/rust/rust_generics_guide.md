# Rust 泛型完整指南：從簡單到進階

## 目錄
1. [基礎泛型](#1-基礎泛型)
2. [泛型函數](#2-泛型函數)
3. [泛型結構體](#3-泛型結構體)
4. [泛型枚舉](#4-泛型枚舉)
5. [Trait 約束詳解](#5-trait-約束詳解)
6. [常用 Trait 完整說明](#6-常用-trait-完整說明)
7. [生命週期泛型](#7-生命週期泛型)
8. [關聯類型](#8-關聯類型)
9. [高階 Trait 約束](#9-高階-trait-約束)
10. [泛型常數](#10-泛型常數)
11. [進階應用](#11-進階應用)

---

## 1. 基礎泛型

### 1.1 最簡單的泛型函數

```rust
// 基本泛型函數
fn identity<T>(x: T) -> T {
    x
}

fn main() {
    let number = identity(42);       // T = i32
    let text = identity("hello");    // T = &str
    let boolean = identity(true);    // T = bool
    
    println!("{}, {}, {}", number, text, boolean);
}
```

### 1.2 多個泛型參數

```rust
fn pair<T, U>(first: T, second: U) -> (T, U) {
    (first, second)
}

fn main() {
    let p1 = pair(1, "hello");        // (i32, &str)
    let p2 = pair(true, 3.14);        // (bool, f64)
    let p3 = pair("world", 42);       // (&str, i32)
    
    println!("{:?}, {:?}, {:?}", p1, p2, p3);
}
```

## 2. 泛型函數

### 2.1 基本 Trait 約束

```rust
use std::fmt::Display;

// 單一 trait 約束
fn print_it<T: Display>(item: T) {
    println!("{}", item);
}

// 多個 trait 約束
fn compare_and_print<T: PartialEq + Display>(a: T, b: T) {
    if a == b {
        println!("{} equals {}", a, b);
    } else {
        println!("{} not equals {}", a, b);
    }
}

fn main() {
    print_it(42);
    print_it("hello");
    
    compare_and_print(5, 5);
    compare_and_print("rust", "go");
}
```

### 2.2 where 子句

```rust
use std::fmt::Display;
use std::clone::Clone;

// 使用 where 讓函數簽名更清晰
fn complex_function<T, U, V>(t: T, u: U, v: V) -> String
where
    T: Display + Clone,
    U: Clone + Debug,
    V: Display,
{
    format!("t: {}, u: {:?}, v: {}", t, u, v)
}

// 等價的內聯語法（較難讀）
fn complex_function_inline<T: Display + Clone, U: Clone + std::fmt::Debug, V: Display>(
    t: T, u: U, v: V
) -> String {
    format!("t: {}, u: {:?}, v: {}", t, u, v)
}
```

### 2.3 泛型方法

```rust
struct Container<T> {
    value: T,
}

impl<T> Container<T> {
    fn new(value: T) -> Self {
        Container { value }
    }
    
    fn get(&self) -> &T {
        &self.value
    }
    
    // 泛型方法
    fn map<U, F>(self, f: F) -> Container<U>
    where
        F: FnOnce(T) -> U,
    {
        Container { value: f(self.value) }
    }
}

fn main() {
    let container = Container::new(42);
    let string_container = container.map(|x| x.to_string());
    println!("{}", string_container.get()); // "42"
}
```

## 3. 泛型結構體

### 3.1 基本泛型結構體

```rust
// 單一泛型參數
struct Point<T> {
    x: T,
    y: T,
}

// 多個泛型參數
struct Rectangle<T, U> {
    width: T,
    height: U,
}

impl<T> Point<T> {
    fn new(x: T, y: T) -> Self {
        Point { x, y }
    }
}

impl<T: Copy> Point<T> {
    fn x(&self) -> T {
        self.x
    }
}

fn main() {
    let int_point = Point::new(1, 2);
    let float_point = Point::new(1.0, 2.0);
    let rect = Rectangle { width: 10, height: 20.5 };
    
    println!("Point: ({}, {})", int_point.x, int_point.y);
    println!("Rectangle: {} x {}", rect.width, rect.height);
}
```

### 3.2 部分特化實現

```rust
struct Container<T> {
    value: T,
}

// 為所有類型實現
impl<T> Container<T> {
    fn new(value: T) -> Self {
        Container { value }
    }
}

// 只為 String 類型特化實現
impl Container<String> {
    fn len(&self) -> usize {
        self.value.len()
    }
    
    fn is_empty(&self) -> bool {
        self.value.is_empty()
    }
}

fn main() {
    let string_container = Container::new(String::from("hello"));
    let int_container = Container::new(42);
    
    println!("String length: {}", string_container.len());
    // int_container.len(); // 編譯錯誤：i32 沒有 len 方法
}
```

## 4. 泛型枚舉

### 4.1 標準庫範例

```rust
// Option<T> - 標準庫中的泛型枚舉
enum MyOption<T> {
    Some(T),
    None,
}

// Result<T, E> - 錯誤處理的泛型枚舉
enum MyResult<T, E> {
    Ok(T),
    Err(E),
}

impl<T> MyOption<T> {
    fn is_some(&self) -> bool {
        match self {
            MyOption::Some(_) => true,
            MyOption::None => false,
        }
    }
    
    fn unwrap(self) -> T {
        match self {
            MyOption::Some(value) => value,
            MyOption::None => panic!("called unwrap on None"),
        }
    }
}

fn main() {
    let some_number = MyOption::Some(42);
    let no_number: MyOption<i32> = MyOption::None;
    
    println!("Has value: {}", some_number.is_some());
    println!("Value: {}", some_number.unwrap());
}
```

### 4.2 自定義泛型枚舉

```rust
#[derive(Debug)]
enum Either<L, R> {
    Left(L),
    Right(R),
}

impl<L, R> Either<L, R> {
    fn is_left(&self) -> bool {
        matches!(self, Either::Left(_))
    }
    
    fn is_right(&self) -> bool {
        matches!(self, Either::Right(_))
    }
    
    fn map_left<T, F>(self, f: F) -> Either<T, R>
    where
        F: FnOnce(L) -> T,
    {
        match self {
            Either::Left(l) => Either::Left(f(l)),
            Either::Right(r) => Either::Right(r),
        }
    }
}

fn main() {
    let left: Either<i32, String> = Either::Left(42);
    let right: Either<i32, String> = Either::Right("hello".to_string());
    
    let mapped = left.map_left(|x| x * 2);
    println!("{:?}", mapped); // Left(84)
}
```

## 5. Trait 約束詳解

### 5.1 基本約束語法

```rust
// 內聯約束語法
fn function1<T: Display + Debug>(item: T) {
    println!("Display: {}", item);
    println!("Debug: {:?}", item);
}

// where 子句語法（推薦用於複雜約束）
fn function2<T>(item: T)
where
    T: Display + Debug + Clone,
{
    println!("Display: {}", item);
    println!("Debug: {:?}", item);
    let cloned = item.clone();
}

// impl Trait 語法（參數）
fn function3(item: impl Display + Debug) {
    println!("Display: {}", item);
    println!("Debug: {:?}", item);
}

// impl Trait 語法（返回值）
fn function4() -> impl Display + Debug {
    42 // 返回實現了 Display + Debug 的類型
}
```

### 5.2 條件實現 (Conditional Implementation)

```rust
use std::fmt::Display;

struct Wrapper<T> {
    value: T,
}

impl<T> Wrapper<T> {
    fn new(value: T) -> Self {
        Wrapper { value }
    }
}

// 只有當 T 實現了 Display 時，才實現這個方法
impl<T: Display> Wrapper<T> {
    fn print(&self) {
        println!("Value: {}", self.value);
    }
}

// 只有當 T 實現了 Clone 時，才實現這個方法
impl<T: Clone> Wrapper<T> {
    fn duplicate(&self) -> Self {
        Wrapper {
            value: self.value.clone(),
        }
    }
}

// 當 T 同時實現 Display 和 Clone 時
impl<T: Display + Clone> Wrapper<T> {
    fn print_and_duplicate(&self) -> Self {
        self.print();
        self.duplicate()
    }
}

fn main() {
    let wrapper = Wrapper::new("hello");
    wrapper.print(); // 可以呼叫，因為 &str 實現了 Display
    
    let cloned = wrapper.duplicate(); // 可以呼叫，因為 &str 實現了 Clone
    cloned.print();
    
    let wrapper2 = wrapper.print_and_duplicate(); // 兩個 trait 都有
}
```

## 6. 常用 Trait 完整說明

### 6.1 格式化 Traits

#### Display - 用戶友好的格式化
```rust
use std::fmt::{self, Display};

struct Point {
    x: i32,
    y: i32,
}

impl Display for Point {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

// 泛型函數中使用 Display
fn print_nicely<T: Display>(item: T) {
    println!("Nice format: {}", item); // 使用 {} 格式化
}

fn main() {
    let point = Point { x: 10, y: 20 };
    print_nicely(point);           // Nice format: (10, 20)
    print_nicely("hello");         // Nice format: hello
    print_nicely(42);              // Nice format: 42
}
```

#### Debug - 開發者友好的格式化
```rust
use std::fmt::{self, Debug};

// 手動實現 Debug
struct CustomStruct {
    name: String,
    value: i32,
}

impl Debug for CustomStruct {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("CustomStruct")
            .field("name", &self.name)
            .field("value", &self.value)
            .finish()
    }
}

// 自動衍生 Debug
#[derive(Debug)]
struct AutoStruct {
    data: Vec<i32>,
}

// 泛型函數中使用 Debug
fn debug_print<T: Debug>(item: T) {
    println!("Debug format: {:?}", item); // 使用 {:?} 格式化
    println!("Pretty debug: {:#?}", item); // 使用 {:#?} 美化格式
}

fn main() {
    let custom = CustomStruct {
        name: "test".to_string(),
        value: 42,
    };
    
    let auto = AutoStruct {
        data: vec![1, 2, 3],
    };
    
    debug_print(custom);
    debug_print(auto);
    debug_print(vec![1, 2, 3]);
}
```

### 6.2 複製和移動 Traits

#### Copy - 隱式複製
```rust
// Copy trait 只能應用於簡單類型
#[derive(Copy, Clone, Debug)]
struct SimplePoint {
    x: i32,
    y: i32,
}

// 包含非 Copy 類型的結構體不能實現 Copy
#[derive(Clone, Debug)]
struct ComplexPoint {
    x: i32,
    y: i32,
    name: String, // String 不是 Copy
}

fn takes_copy<T: Copy + Debug>(item: T) {
    println!("Original: {:?}", item);
    let copy = item; // 隱式複製
    println!("Copy: {:?}", copy);
    println!("Original still available: {:?}", item); // 原值仍可用
}

fn takes_clone<T: Clone + Debug>(item: T) {
    println!("Original: {:?}", item);
    let cloned = item.clone(); // 明確複製
    println!("Cloned: {:?}", cloned);
    // item 在這裡被移動了，不能再使用
}

fn main() {
    let simple = SimplePoint { x: 1, y: 2 };
    let complex = ComplexPoint { 
        x: 1, 
        y: 2, 
        name: "point".to_string() 
    };
    
    takes_copy(simple);  // 可以傳入 Copy 類型
    takes_copy(42);      // 基本類型都是 Copy
    
    takes_clone(complex); // 需要明確 clone
    takes_clone(simple);  // Copy 類型也可以 clone
}
```

#### Clone - 明確複製
```rust
use std::collections::HashMap;

#[derive(Clone, Debug)]
struct ExpensiveStruct {
    data: HashMap<String, Vec<i32>>,
    cache: Vec<String>,
}

impl ExpensiveStruct {
    fn new() -> Self {
        let mut data = HashMap::new();
        data.insert("key1".to_string(), vec![1, 2, 3]);
        data.insert("key2".to_string(), vec![4, 5, 6]);
        
        ExpensiveStruct {
            data,
            cache: vec!["cached_value".to_string()],
        }
    }
}

// 需要深度複製的泛型函數
fn deep_copy_and_modify<T: Clone + Debug>(mut item: T) -> T {
    let backup = item.clone(); // 創建備份
    println!("Backup created: {:?}", backup);
    item // 返回修改後的項目
}

fn main() {
    let expensive = ExpensiveStruct::new();
    let modified = deep_copy_and_modify(expensive);
    println!("Modified: {:?}", modified);
}
```

### 6.3 比較 Traits

#### PartialEq - 部分相等比較
```rust
use std::collections::HashMap;

#[derive(Debug)]
struct Person {
    name: String,
    age: u32,
    metadata: HashMap<String, String>,
}

// 自定義相等比較 - 只比較 name 和 age
impl PartialEq for Person {
    fn eq(&self, other: &Self) -> bool {
        self.name == other.name && self.age == other.age
        // 故意忽略 metadata
    }
}

// 泛型函數使用 PartialEq
fn are_equal<T: PartialEq + Debug>(a: &T, b: &T) -> bool {
    println!("Comparing: {:?} == {:?}", a, b);
    a == b
}

fn find_item<T: PartialEq + Debug>(items: &[T], target: &T) -> Option<usize> {
    for (index, item) in items.iter().enumerate() {
        if item == target {
            return Some(index);
        }
    }
    None
}

fn main() {
    let person1 = Person {
        name: "Alice".to_string(),
        age: 30,
        metadata: {
            let mut map = HashMap::new();
            map.insert("city".to_string(), "New York".to_string());
            map
        },
    };
    
    let person2 = Person {
        name: "Alice".to_string(),
        age: 30,
        metadata: {
            let mut map = HashMap::new();
            map.insert("city".to_string(), "Boston".to_string()); // 不同的 metadata
            map
        },
    };
    
    println!("Are equal: {}", are_equal(&person1, &person2)); // true（忽略 metadata）
    
    let numbers = vec![1, 2, 3, 4, 5];
    if let Some(index) = find_item(&numbers, &3) {
        println!("Found 3 at index: {}", index);
    }
}
```

#### Eq - 完全相等
```rust
// Eq 是 PartialEq 的子 trait，保證反身性 (a == a 總是 true)
#[derive(PartialEq, Eq, Debug, Hash)]
struct Id(u32);

use std::collections::HashSet;

// 只有實現 Eq 的類型才能用作 HashMap/HashSet 的鍵
fn unique_items<T: Eq + std::hash::Hash + Debug>(items: Vec<T>) -> HashSet<T> {
    items.into_iter().collect()
}

fn main() {
    let ids = vec![Id(1), Id(2), Id(1), Id(3), Id(2)];
    let unique = unique_items(ids);
    println!("Unique IDs: {:?}", unique); // {Id(1), Id(2), Id(3)}
}
```

#### PartialOrd 和 Ord - 排序比較
```rust
use std::cmp::{PartialOrd, Ord, Ordering};

#[derive(Debug, PartialEq, Eq)]
struct Score {
    value: u32,
    name: String,
}

// 實現 PartialOrd
impl PartialOrd for Score {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

// 實現 Ord（完全排序）
impl Ord for Score {
    fn cmp(&self, other: &Self) -> Ordering {
        // 先按分數排序，再按名字排序
        self.value.cmp(&other.value)
            .then_with(|| self.name.cmp(&other.name))
    }
}

// 需要排序的泛型函數
fn sort_items<T: Ord + Debug>(mut items: Vec<T>) -> Vec<T> {
    items.sort();
    println!("Sorted items: {:?}", items);
    items
}

fn find_max<T: Ord + Debug + Clone>(items: &[T]) -> Option<T> {
    items.iter().max().cloned()
}

fn main() {
    let mut scores = vec![
        Score { value: 100, name: "Alice".to_string() },
        Score { value: 85, name: "Bob".to_string() },
        Score { value: 100, name: "Charlie".to_string() },
        Score { value: 92, name: "Diana".to_string() },
    ];
    
    let sorted = sort_items(scores.clone());
    
    if let Some(max_score) = find_max(&scores) {
        println!("Highest score: {:?}", max_score);
    }
}
```

### 6.4 併發 Traits

#### Send - 線程間傳輸
```rust
use std::thread;
use std::sync::Arc;

// Send trait 標記類型可以在線程間安全傳輸
// 大多數類型自動實現 Send，除了 Rc<T> 等

struct SafeData {
    value: i32,
}

// 自動實現 Send，因為 i32 是 Send

struct UnsafeData {
    ptr: *const i32, // 原始指針不是 Send
}

// UnsafeData 不會自動實現 Send

// 需要 Send 的泛型函數
fn process_in_thread<T: Send + 'static>(data: T) -> thread::JoinHandle<T> {
    thread::spawn(move || {
        // 在新線程中處理數據
        println!("Processing in thread: {:?}", thread::current().id());
        data
    })
}

fn parallel_map<T, U, F>(items: Vec<T>, f: F) -> Vec<U>
where
    T: Send + 'static,
    U: Send + 'static,
    F: Fn(T) -> U + Send + Sync + 'static,
{
    let f = Arc::new(f);
    let mut handles = vec![];
    
    for item in items {
        let f_clone = Arc::clone(&f);
        let handle = thread::spawn(move || f_clone(item));
        handles.push(handle);
    }
    
    handles.into_iter()
        .map(|handle| handle.join().unwrap())
        .collect()
}

fn main() {
    let safe_data = SafeData { value: 42 };
    
    // 可以傳輸到其他線程
    let handle = process_in_thread(safe_data);
    let result = handle.join().unwrap();
    println!("Result: {}", result.value);
    
    // 並行處理
    let numbers = vec![1, 2, 3, 4, 5];
    let doubled = parallel_map(numbers, |x| x * 2);
    println!("Doubled: {:?}", doubled);
}
```

#### Sync - 線程間共享
```rust
use std::sync::{Arc, Mutex};
use std::thread;

// Sync trait 標記類型可以在多線程間安全共享引用
// 如果 T: Sync，那麼 &T 是 Send 的

struct Counter {
    value: Mutex<i32>,
}

impl Counter {
    fn new() -> Self {
        Counter {
            value: Mutex::new(0),
        }
    }
    
    fn increment(&self) {
        let mut value = self.value.lock().unwrap();
        *value += 1;
    }
    
    fn get(&self) -> i32 {
        *self.value.lock().unwrap()
    }
}

// Counter 自動實現 Sync，因為 Mutex<i32> 是 Sync

// 需要 Sync 的泛型函數
fn share_across_threads<T: Sync + Send + 'static>(data: Arc<T>) {
    let mut handles = vec![];
    
    for i in 0..3 {
        let data_clone = Arc::clone(&data);
        let handle = thread::spawn(move || {
            println!("Thread {} accessing shared data", i);
            // 可以安全地共享 &T
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}

fn concurrent_operation<T, F>(data: Arc<T>, operation: F)
where
    T: Sync + Send + 'static,
    F: Fn(&T) + Send + Sync + 'static,
{
    let operation = Arc::new(operation);
    let mut handles = vec![];
    
    for _ in 0..3 {
        let data_clone = Arc::clone(&data);
        let op_clone = Arc::clone(&operation);
        
        let handle = thread::spawn(move || {
            op_clone(&*data_clone);
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}

fn main() {
    let counter = Arc::new(Counter::new());
    
    share_across_threads(Arc::clone(&counter));
    
    concurrent_operation(counter, |counter| {
        counter.increment();
        println!("Counter value: {}", counter.get());
    });
}
```

### 6.5 生命週期約束

#### 'static - 靜態生命週期
```rust
// 'static 表示數據在整個程序運行期間都有效

// 字符串字面量具有 'static 生命週期
fn get_static_string() -> &'static str {
    "This string lives for the entire program"
}

// 泛型函數要求 'static 生命週期
fn store_for_later<T: 'static + Send>(data: T) -> Box<dyn Fn() -> T + Send> {
    Box::new(move || data)
}

fn spawn_with_data<T: Send + 'static>(data: T) -> std::thread::JoinHandle<T> {
    std::thread::spawn(move || {
        println!("Processing data in thread");
        data
    })
}

// 結構體與 'static 約束
struct Container<T: 'static> {
    data: T,
}

impl<T: 'static> Container<T> {
    fn new(data: T) -> Self {
        Container { data }
    }
    
    fn into_boxed(self) -> Box<T> {
        Box::new(self.data)
    }
}

fn main() {
    // 靜態字符串
    let static_str = get_static_string();
    println!("{}", static_str);
    
    // 擁有的數據（自動滿足 'static）
    let owned_string = String::from("owned data");
    let stored = store_for_later(owned_string);
    println!("{}", stored());
    
    // 在線程中使用
    let number = 42;
    let handle = spawn_with_data(number);
    let result = handle.join().unwrap();
    println!("Thread result: {}", result);
    
    // 容器
    let container = Container::new(vec![1, 2, 3]);
    let boxed = container.into_boxed();
    println!("Boxed data: {:?}", boxed);
}
```

### 6.6 複雜約束組合

```rust
use std::fmt::{Debug, Display};
use std::thread;
use std::sync::Arc;

// 複雜的多重約束
fn complex_operation<T>(data: T) -> String
where
    T: Display +           // 可以友好顯示
       Debug +             // 可以調試顯示  
       Clone +             // 可以複製
       Send +              // 可以跨線程傳輸
       Sync +              // 可以跨線程共享
       'static +           // 具有靜態生命週期
       PartialEq +         // 可以比較相等
       PartialOrd,         // 可以比較大小
{
    println!("Display: {}", data);
    println!("Debug: {:?}", data);
    
    let cloned = data.clone();
    println!("Cloned: {:?}", cloned);
    
    // 在新線程中處理
    let data_arc = Arc::new(data);
    let handle = thread::spawn({
        let data_clone = Arc::clone(&data_arc);
        move || {
            format!("Processed: {:?}", *data_clone)
        }
    });
    
    handle.join().unwrap()
}

// 條件約束 - 只有滿足條件才有某些方法
struct Processor<T> {
    data: T,
}

impl<T> Processor<T> {
    fn new(data: T) -> Self {
        Processor { data }
    }
}

// 只有 Display 時才能打印
impl<T: Display> Processor<T> {
    fn print(&self) {
        println!("Data: {}", self.data);
    }
}

// 只有 Clone 時才能複製
impl<T: Clone> Processor<T> {
    fn duplicate(&self) -> Self {
        Processor {
            data: self.data.clone(),
        }
    }
}

// 同時有 Display 和 Clone 時的特殊方法
impl<T: Display + Clone> Processor<T> {
    fn print_and_duplicate(&self) -> Self {
        self.print();
        self.duplicate()
    }
}

// 並發處理約束
impl<T: Send + Sync + 'static + Clone> Processor<T> {
    fn process_concurrently(&self) -> Vec<T> {
        let mut handles = vec![];
        
        for _ in 0..3 {
            let data = self.data.clone();
            let handle = thread::spawn(move || {
                // 模擬處理
                thread::sleep(std::time::Duration::from_millis(100));
                data
            });
            handles.push(handle);
        }
        
        handles.into_iter()
            .map(|h| h.join().unwrap())
            .collect()
    }
}

fn main() {
    // 滿足所有約束的類型
    let result = complex_operation(42i32);
    println!("Complex result: {}", result);
    
    // 條件實現範例
    let processor = Processor::new("hello world");
    
    processor.print();                    // 有 Display
    let duplicated = processor.duplicate(); // 有 Clone  
    let combined = processor.print_and_duplicate(); // 兩者都有
    
    // 並發處理
    let concurrent_results = processor.process_concurrently();
    println!("Concurrent results: {:?}", concurrent_results);
}
```

### 6.7 實際應用場景

```rust
use std::collections::HashMap;
use std::hash::Hash;
use std::fmt::Debug;

// 泛型緩存系統
struct Cache<K, V>
where
    K: Eq + Hash + Clone + Debug,
    V: Clone + Debug,
{
    data: HashMap<K, V>,
    max_size: usize,
}

impl<K, V> Cache<K, V>
where
    K: Eq + Hash + Clone + Debug,
    V: Clone + Debug,
{
    fn new(max_size: usize) -> Self {
        Cache {
            data: HashMap::new(),
            max_size,
        }
    }
    
    fn get(&self, key: &K) -> Option<&V> {
        println!("Getting key: {:?}", key);
        self.data.get(key)
    }
    
    fn insert(&mut self, key: K, value: V) {
        if self.data.len() >= self.max_size {
            // 簡單的 LRU：移除第一個元素
            if let Some(first_key) = self.data.keys().next().cloned() {
                self.data.remove(&first_key);
                println!("Evicted key: {:?}", first_key);
            }
        }
        
        println!("Inserting key: {:?}, value: {:?}", key, value);
        self.data.insert(key, value);
    }
}

// 序列化約束
trait Serialize {
    fn serialize(&self) -> String;
}

trait Deserialize: Sized {
    fn deserialize(data: &str) -> Option<Self>;
}

// 需要序列化的泛型存儲
struct PersistentStore<T>
where
    T: Serialize + Deserialize + Debug,
{
    items: Vec<T>,
}

impl<T> PersistentStore<T>
where
    T: Serialize + Deserialize + Debug,
{
    fn new() -> Self {
        PersistentStore { items: Vec::new() }
    }
    
    fn add(&mut self, item: T) {
        println!("Adding item: {:?}", item);
        self.items.push(item);
    }
    
    fn save_to_string(&self) -> String {
        self.items
            .iter()
            .map(|item| item.serialize())
            .collect::<Vec<_>>()
            .join("\n")
    }
    
    fn load_from_string(&mut self, data: &str) {
        self.items.clear();
        for line in data.lines() {
            if let Some(item) = T::deserialize(line) {
                self.items.push(item);
            }
        }
    }
}

// 實現序列化 trait
#[derive(Debug, Clone)]
struct Person {
    name: String,
    age: u32,
}

impl Serialize for Person {
    fn serialize(&self) -> String {
        format!("{}:{}", self.name, self.age)
    }
}

impl Deserialize for Person {
    fn deserialize(data: &str) -> Option<Self> {
        let parts: Vec<&str> = data.split(':').collect();
        if parts.len() == 2 {
            if let Ok(age) = parts[1].parse::<u32>() {
                return Some(Person {
                    name: parts[0].to_string(),
                    age,
                });
            }
        }
        None
    }
}

fn main() {
    // 緩存使用
    let mut cache = Cache::new(2);
    cache.insert("key1".to_string(), 42);
    cache.insert("key2".to_string(), 100);
    cache.insert("key3".to_string(), 200); // 會導致 key1 被移除
    
    if let Some(value) = cache.get(&"key2".to_string()) {
        println!("Found value: {}", value);
    }
    
    // 持久化存儲
    let mut store = PersistentStore::new();
    store.add(Person { name: "Alice".to_string(), age: 30 });
    store.add(Person { name: "Bob".to_string(), age: 25 });
    
    let serialized = store.save_to_string();
    println!("Serialized data:\n{}", serialized);
    
    let mut new_store = PersistentStore::new();
    new_store.load_from_string(&serialized);
    println!("Loaded {} items", new_store.items.len());
}
```

## 7. 生命週期泛型

### 7.1 基本生命週期

```rust
// 生命週期參數
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

// 結構體中的生命週期
struct ImportantExcerpt<'a> {
    part: &'a str,
}

impl<'a> ImportantExcerpt<'a> {
    fn level(&self) -> i32 {
        3
    }
    
    // 生命週期省略規則
    fn announce_and_return_part(&self, announcement: &str) -> &str {
        println!("Attention please: {}", announcement);
        self.part
    }
}

fn main() {
    let string1 = String::from("abcd");
    let string2 = "xyz";
    
    let result = longest(string1.as_str(), string2);
    println!("The longest string is {}", result);
    
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().expect("Could not find a '.'");
    let i = ImportantExcerpt {
        part: first_sentence,
    };
}
```

### 7.2 複雜生命週期約束

```rust
use std::fmt::Display;

// 多個生命週期參數
struct DoubleRef<'a, 'b> {
    first: &'a str,
    second: &'b str,
}

impl<'a, 'b> DoubleRef<'a, 'b> {
    fn new(first: &'a str, second: &'b str) -> Self {
        DoubleRef { first, second }
    }
    
    // 返回較短的生命週期
    fn get_first(&self) -> &'a str {
        self.first
    }
    
    fn get_second(&self) -> &'b str {
        self.second
    }
}

// 生命週期 + 泛型 + trait 約束
fn print_with_lifetime<'a, T>(item: &'a T, prefix: &'a str) -> &'a str
where
    T: Display + 'a,
{
    println!("{}: {}", prefix, item);
    prefix
}

// 高階生命週期約束 (Higher-Rank Trait Bounds)
fn apply_to_strings<F>(f: F) -> String
where
    F: for<'a> Fn(&'a str) -> &'a str,
{
    let s1 = "hello";
    let s2 = "world";
    format!("{} {}", f(s1), f(s2))
}

// 生命週期子類型
fn longer_lifetime<'long: 'short, 'short>(
    long: &'long str,
    short: &'short str,
) -> &'short str {
    // 'long 至少和 'short 一樣長
    if long.len() > short.len() { 
        long // 可以將較長生命週期轉換為較短的
    } else { 
        short 
    }
}

fn main() {
    let first = String::from("first string");
    let second = String::from("second string");
    
    let double_ref = DoubleRef::new(&first, &second);
    println!("First: {}", double_ref.get_first());
    println!("Second: {}", double_ref.get_second());
    
    let number = 42;
    let prefix = print_with_lifetime(&number, "Number");
    println!("Returned prefix: {}", prefix);
    
    let result = apply_to_strings(|s| s);
    println!("Applied result: {}", result);
    
    let long_lived = "long lived string";
    {
        let short_lived = String::from("short");
        let result = longer_lifetime(long_lived, &short_lived);
        println!("Result: {}", result);
    }
}
```

### 7.3 靜態生命週期與所有權

```rust
use std::thread;

// 'static 生命週期的各種用法
fn get_static_str() -> &'static str {
    "This is a static string"
}

// 要求 'static 的泛型函數
fn spawn_thread<T: Send + 'static>(data: T) -> thread::JoinHandle<T> {
    thread::spawn(move || {
        println!("Processing data in thread");
        data
    })
}

// 可選的 'static 約束
fn maybe_static<T: 'static>(data: T) -> Box<T> {
    Box::new(data)
}

// 條件生命週期約束
struct Container<T> 
where 
    T: 'static,  // T 必須是 'static
{
    data: T,
}

impl<T: 'static> Container<T> {
    fn new(data: T) -> Self {
        Container { data }
    }
    
    fn into_static(self) -> &'static T {
        // 這實際上是不安全的，僅作示例
        // 在實際代碼中不要這樣做
        Box::leak(Box::new(self.data))
    }
}

// 生命週期與 trait 對象
trait Drawable {
    fn draw(&self);
}

struct Circle {
    radius: f64,
}

impl Drawable for Circle {
    fn draw(&self) {
        println!("Drawing circle with radius {}", self.radius);
    }
}

// 不同生命週期的 trait 對象
fn draw_all<'a>(drawables: Vec<&'a dyn Drawable>) {
    for drawable in drawables {
        drawable.draw();
    }
}

fn draw_all_static(drawables: Vec<Box<dyn Drawable + 'static>>) {
    for drawable in drawables {
        drawable.draw();
    }
}

fn main() {
    // 靜態字符串
    let static_str = get_static_str();
    println!("{}", static_str);
    
    // 擁有數據在線程中
    let owned_data = String::from("owned");
    let handle = spawn_thread(owned_data);
    let result = handle.join().unwrap();
    println!("Thread result: {}", result);
    
    // 容器與 'static
    let container = Container::new(42);
    // let static_ref = container.into_static(); // 危險操作
    
    // trait 對象
    let circle = Circle { radius: 5.0 };
    draw_all(vec![&circle]);
    
    let boxed_circle = Box::new(Circle { radius: 10.0 });
    draw_all_static(vec![boxed_circle]);
}
```

## 8. 關聯類型

### 8.1 基本關聯類型

```rust
// 使用關聯類型的 trait
trait Iterator {
    type Item;
    
    fn next(&mut self) -> Option<Self::Item>;
}

trait Collect<T> {
    fn collect(self) -> T;
}

// 實現 Iterator trait
struct Counter {
    current: u32,
    max: u32,
}

impl Counter {
    fn new(max: u32) -> Counter {
        Counter { current: 0, max }
    }
}

impl Iterator for Counter {
    type Item = u32;
    
    fn next(&mut self) -> Option<Self::Item> {
        if self.current < self.max {
            let current = self.current;
            self.current += 1;
            Some(current)
        } else {
            None
        }
    }
}

// 複雜的關聯類型
trait Graph {
    type Node;
    type Edge;
    
    fn nodes(&self) -> Vec<Self::Node>;
    fn edges(&self) -> Vec<Self::Edge>;
    fn add_edge(&mut self, from: Self::Node, to: Self::Node) -> Self::Edge;
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
struct NodeId(usize);

#[derive(Debug, Clone)]
struct Edge {
    from: NodeId,
    to: NodeId,
    weight: i32,
}

struct SimpleGraph {
    nodes: Vec<NodeId>,
    edges: Vec<Edge>,
    next_id: usize,
}

impl SimpleGraph {
    fn new() -> Self {
        SimpleGraph {
            nodes: Vec::new(),
            edges: Vec::new(),
            next_id: 0,
        }
    }
    
    fn add_node(&mut self) -> NodeId {
        let id = NodeId(self.next_id);
        self.next_id += 1;
        self.nodes.push(id);
        id
    }
}

impl Graph for SimpleGraph {
    type Node = NodeId;
    type Edge = Edge;
    
    fn nodes(&self) -> Vec<Self::Node> {
        self.nodes.clone()
    }
    
    fn edges(&self) -> Vec<Self::Edge> {
        self.edges.clone()
    }
    
    fn add_edge(&mut self, from: Self::Node, to: Self::Node) -> Self::Edge {
        let edge = Edge {
            from,
            to,
            weight: 1, // 預設權重
        };
        self.edges.push(edge.clone());
        edge
    }
}

fn main() {
    let mut counter = Counter::new(3);
    
    while let Some(value) = counter.next() {
        println!("{}", value);
    }
    
    let mut graph = SimpleGraph::new();
    let node1 = graph.add_node();
    let node2 = graph.add_node();
    let edge = graph.add_edge(node1, node2);
    
    println!("Nodes: {:?}", graph.nodes());
    println!("Edges: {:?}", graph.edges());
}
```

### 8.2 關聯類型 vs 泛型比較

```rust
use std::fmt::Debug;

// 使用泛型 - 允許多種實現
trait GenericTrait<T> {
    fn process(&self, item: T) -> T;
}

// 使用關聯類型 - 每個類型只有一種實現
trait AssociatedTrait {
    type Input;
    type Output;
    
    fn process(&self, input: Self::Input) -> Self::Output;
}

struct Processor;

// 可以為同一個類型實現不同的泛型版本
impl GenericTrait<i32> for Processor {
    fn process(&self, item: i32) -> i32 {
        item * 2
    }
}

impl GenericTrait<String> for Processor {
    fn process(&self, item: String) -> String {
        format!("Processed: {}", item)
    }
}

impl GenericTrait<f64> for Processor {
    fn process(&self, item: f64) -> f64 {
        item * 3.14
    }
}

// 但關聯類型只能有一個實現
impl AssociatedTrait for Processor {
    type Input = String;
    type Output = usize;
    
    fn process(&self, input: Self::Input) -> Self::Output {
        input.len()
    }
}

// 使用關聯類型的泛型函數
fn use_associated_trait<T: AssociatedTrait>(
    processor: &T,
    input: T::Input,
) -> T::Output {
    processor.process(input)
}

// 關聯類型的約束
trait Parser {
    type Item;
    type Error: Debug;
    
    fn parse(&self, input: &str) -> Result<Self::Item, Self::Error>;
}

#[derive(Debug)]
struct ParseError(String);

struct NumberParser;

impl Parser for NumberParser {
    type Item = i32;
    type Error = ParseError;
    
    fn parse(&self, input: &str) -> Result<Self::Item, Self::Error> {
        input.parse().map_err(|_| ParseError(format!("Invalid number: {}", input)))
    }
}

// 泛型函數使用解析器
fn parse_and_double<P: Parser<Item = i32>>(
    parser: &P,
    input: &str,
) -> Result<i32, P::Error> {
    parser.parse(input).map(|n| n * 2)
}

fn main() {
    let processor = Processor;
    
    // 泛型版本需要明確指定類型
    let result1: i32 = processor.process(10);
    let result2: String = processor.process("hello".to_string());
    let result3: f64 = processor.process(2.0);
    
    println!("Generic results: {}, {}, {}", result1, result2, result3);
    
    // 關聯類型版本類型自動推斷
    let result4 = use_associated_trait(&processor, "world".to_string());
    println!("Associated result: {}", result4);
    
    // 解析器範例
    let parser = NumberParser;
    match parse_and_double(&parser, "21") {
        Ok(result) => println!("Parsed and doubled: {}", result),
        Err(e) => println!("Parse error: {:?}", e),
    }
}
```

### 8.3 投影與高階關聯類型

```rust
// 關聯類型投影
trait Functor {
    type Wrapped<T>;
    
    fn map<T, U, F>(input: Self::Wrapped<T>, f: F) -> Self::Wrapped<U>
    where
        F: Fn(T) -> U;
}

// Option 作為 Functor
struct OptionFunctor;

impl Functor for OptionFunctor {
    type Wrapped<T> = Option<T>;
    
    fn map<T, U, F>(input: Self::Wrapped<T>, f: F) -> Self::Wrapped<U>
    where
        F: Fn(T) -> U,
    {
        input.map(f)
    }
}

// Vec 作為 Functor
struct VecFunctor;

impl Functor for VecFunctor {
    type Wrapped<T> = Vec<T>;
    
    fn map<T, U, F>(input: Self::Wrapped<T>, f: F) -> Self::Wrapped<U>
    where
        F: Fn(T) -> U,
    {
        input.into_iter().map(f).collect()
    }
}

// 使用 Functor
fn double_functor<F: Functor>(input: F::Wrapped<i32>) -> F::Wrapped<i32> {
    F::map(input, |x| x * 2)
}

// 關聯類型家族
trait Collection {
    type Item;
    type Iter<'a>: Iterator<Item = &'a Self::Item> where Self: 'a;
    
    fn iter(&self) -> Self::Iter<'_>;
    fn len(&self) -> usize;
    fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

impl<T> Collection for Vec<T> {
    type Item = T;
    type Iter<'a> = std::slice::Iter<'a, T> where T: 'a;
    
    fn iter(&self) -> Self::Iter<'_> {
        self.as_slice().iter()
    }
    
    fn len(&self) -> usize {
        Vec::len(self)
    }
}

use std::collections::HashMap;
use std::hash::Hash;

impl<K: Hash + Eq, V> Collection for HashMap<K, V> {
    type Item = (K, V);
    type Iter<'a> = std::collections::hash_map::Iter<'a, K, V> where K: 'a, V: 'a;
    
    fn iter(&self) -> Self::Iter<'_> {
        HashMap::iter(self)
    }
    
    fn len(&self) -> usize {
        HashMap::len(self)
    }
}

fn print_collection<C: Collection>(collection: &C) 
where
    for<'a> &'a C::Item: Debug,
{
    println!("Collection has {} items:", collection.len());
    for item in collection.iter() {
        println!("  {:?}", item);
    }
}

fn main() {
    // Functor 範例
    let option_input = Some(21);
    let option_result = double_functor::<OptionFunctor>(option_input);
    println!("Option result: {:?}", option_result);
    
    let vec_input = vec![1, 2, 3];
    let vec_result = double_functor::<VecFunctor>(vec_input);
    println!("Vec result: {:?}", vec_result);
    
    // Collection 範例
    let numbers = vec![1, 2, 3, 4, 5];
    print_collection(&numbers);
    
    let mut map = HashMap::new();
    map.insert("a", 1);
    map.insert("b", 2);
    print_collection(&map);
}
```

## 9. 高階 Trait 約束

### 9.1 Higher-Rank Trait Bounds (HRTB)

```rust
// for<'a> 語法 - 對所有生命週期都成立
fn apply_to_all<F>(f: F)
where
    F: for<'a> Fn(&'a str) -> &'a str,
{
    let s1 = "hello";
    let s2 = "world";
    
    println!("{}", f(s1));
    println!("{}", f(s2));
}

fn identity(s: &str) -> &str {
    s
}

// 更複雜的 HRTB
fn process_strings<F, R>(f: F) -> Vec<R>
where
    F: for<'a> Fn(&'a str) -> R,
    R: Clone,
{
    let strings = vec!["hello", "world", "rust"];
    strings.iter().map(|&s| f(s)).collect()
}

// HRTB 與閉包
fn with_callback<F>(callback: F)
where
    F: for<'r> Fn(&'r str) -> String,
{
    let data = vec!["first", "second", "third"];
    for item in data {
        let result = callback(item);
        println!("Processed: {}", result);
    }
}

// HRTB 與 trait 對象
trait Processor {
    fn process<'a>(&self, input: &'a str) -> &'a str;
}

struct UpperCaseProcessor;

impl Processor for UpperCaseProcessor {
    fn process<'a>(&self, input: &'a str) -> &'a str {
        // 實際上這很難實現，因為我們需要返回新的字符串
        // 這裡僅作示例
        input
    }
}

fn use_processor<P>(processor: P)
where
    P: for<'a> Fn(&'a str) -> &'a str,
{
    let test_strings = vec!["hello", "world"];
    for s in test_strings {
        println!("{}", processor(s));
    }
}

fn main() {
    apply_to_all(identity);
    apply_to_all(|s| s);
    
    let lengths = process_strings(|s| s.len());
    println!("Lengths: {:?}", lengths);
    
    let uppercase = process_strings(|s| s.to_uppercase());
    println!("Uppercase: {:?}", uppercase);
    
    with_callback(|s| format!("Processed: {}", s));
    
    use_processor(|s| s);
}
```

### 9.2 複雜的泛型約束組合

```rust
use std::fmt::{Debug, Display};
use std::ops::{Add, Mul};
use std::cmp::PartialOrd;

// 數學運算的複雜約束
fn mathematical_operation<T>(a: T, b: T, c: T) -> T
where
    T: Add<Output = T> +        // 支持加法
       Mul<Output = T> +        // 支持乘法
       PartialOrd +             // 支持比較
       Copy +                   // 可複製
       Display +                // 可顯示
       Debug +                  // 可調試
       Default,                 // 有默認值
{
    println!("Input: a={}, b={}, c={}", a, b, c);
    
    let result = if a > b {
        a * c + T::default()
    } else {
        b * c + a
    };
    
    println!("Result: {} (debug: {:?})", result, result);
    result
}

// 集合操作的約束
use std::collections::HashSet;
use std::hash::Hash;

fn set_operations<T>(items1: Vec<T>, items2: Vec<T>) -> (HashSet<T>, HashSet<T>)
where
    T: Eq + Hash + Clone + Debug,
{
    let set1: HashSet<T> = items1.into_iter().collect();
    let set2: HashSet<T> = items2.into_iter().collect();
    
    let intersection: HashSet<T> = set1.intersection(&set2).cloned().collect();
    let union: HashSet<T> = set1.union(&set2).cloned().collect();
    
    println!("Intersection: {:?}", intersection);
    println!("Union: {:?}", union);
    
    (intersection, union)
}

// 條件約束與關聯類型
trait Container {
    type Item;
    
    fn items(&self) -> &[Self::Item];
}

fn process_container<C>(container: &C)
where
    C: Container,
    C::Item: Display + Clone + PartialEq,
{
    let items = container.items();
    println!("Container has {} items:", items.len());
    
    for (i, item) in items.iter().enumerate() {
        println!("  [{}]: {}", i, item);
    }
    
    // 找到第一個重複的項目
    for i in 0..items.len() {
        for j in (i + 1)..items.len() {
            if items[i] == items[j] {
                println!("Found duplicate: {} at positions {} and {}", items[i], i, j);
                return;
            }
        }
    }
    println!("No duplicates found");
}

struct NumberContainer {
    numbers: Vec<i32>,
}

impl Container for NumberContainer {
    type Item = i32;
    
    fn items(&self) -> &[Self::Item] {
        &self.numbers
    }
}

// 異步約束 (需要 async runtime)
use std::future::Future;
use std::pin::Pin;

trait AsyncProcessor {
    type Output;
    
    fn process_async(&self) -> Pin<Box<dyn Future<Output = Self::Output> + Send + '_>>;
}

// 使用異步處理器
async fn use_async_processor<P>(processor: P) -> P::Output
where
    P: AsyncProcessor,
    P::Output: Debug,
{
    let result = processor.process_async().await;
    println!("Async result: {:?}", result);
    result
}

// 函數指針與約束
fn higher_order_function<F, T, U>(f: F, input: T) -> U
where
    F: Fn(T) -> U + Send + Sync + 'static,
    T: Send + 'static,
    U: Send + 'static + Debug,
{
    let result = f(input);
    println!("Higher order result: {:?}", result);
    result
}

// 遞歸約束
trait RecursiveDisplay {
    fn recursive_display(&self, depth: usize);
}

impl<T: Display> RecursiveDisplay for Vec<T> {
    fn recursive_display(&self, depth: usize) {
        let indent = "  ".repeat(depth);
        println!("{}Vec with {} items:", indent, self.len());
        for item in self {
            println!("{}  {}", indent, item);
        }
    }
}

impl<T: RecursiveDisplay> RecursiveDisplay for Option<T> {
    fn recursive_display(&self, depth: usize) {
        let indent = "  ".repeat(depth);
        match self {
            Some(value) => {
                println!("{}Some:", indent);
                value.recursive_display(depth + 1);
            }
            None => println!("{}None", indent),
        }
    }
}

fn print_recursive<T: RecursiveDisplay>(item: &T) {
    item.recursive_display(0);
}

fn main() {
    // 數學運算
    let result = mathematical_operation(5, 10, 2);
    println!("Math result: {}", result);
    
    let float_result = mathematical_operation(3.14, 2.71, 1.41);
    println!("Float result: {}", float_result);
    
    // 集合操作
    let set1 = vec![1, 2, 3, 4];
    let set2 = vec![3, 4, 5, 6];
    let (intersection, union) = set_operations(set1, set2);
    
    // 容器處理
    let container = NumberContainer {
        numbers: vec![1, 2, 3, 2, 4],
    };
    process_container(&container);
    
    // 高階函數
    let squared = higher_order_function(|x: i32| x * x, 5);
    
    // 遞歸顯示
    let nested = Some(vec![1, 2, 3]);
    print_recursive(&nested);
    
    let nested_vec = vec![Some(vec![1, 2]), None, Some(vec![3, 4, 5])];
    for item in &nested_vec {
        print_recursive(item);
    }
}
```

## 10. 泛型常數

### 10.1 Const 泛型 (Rust 1.51+)

```rust
// 泛型常數參數
struct Array<T, const N: usize> {
    data: [T; N],
}

impl<T, const N: usize> Array<T, N> {
    fn new(data: [T; N]) -> Self {
        Array { data }
    }
    
    fn len(&self) -> usize {
        N
    }
    
    fn get(&self, index: usize) -> Option<&T> {
        self.data.get(index)
    }
    
    // 常數泛型的運算
    fn split_half(&self) -> (&[T], &[T]) 
    where
        T: Debug,
    {
        self.data.split_at(N / 2)
    }
    
    // 轉換到不同大小的陣列
    fn resize<const M: usize>(&self) -> Option<Array<T, M>>
    where
        T: Clone + Default,
    {
        if M > N {
            return None; // 不能擴大
        }
        
        let mut new_data = [T::default(); M];
        for i in 0..M {
            for j in 0..P {
                let mut sum = T::default();
                for k in 0..N {
                    sum = sum + self.data[i][k] * other.data[k][j];
                }
                result.data[i][j] = sum;
            }
        }
        result
    }
}

// 編譯時大小檢查
fn safe_array_access<T, const N: usize>(arr: &Array<T, N>, index: usize) -> Option<&T>
where
    T: Debug,
{
    if index < N {
        arr.get(index)
    } else {
        println!("Index {} is out of bounds for array of size {}", index, N);
        None
    }
}

// 泛型常數與 trait
trait FixedSizeCollection<T, const N: usize> {
    fn as_array(&self) -> &[T; N];
    fn size() -> usize {
        N
    }
}

impl<T, const N: usize> FixedSizeCollection<T, N> for Array<T, N> {
    fn as_array(&self) -> &[T; N] {
        &self.data
    }
}

// 常數表達式
const fn factorial(n: usize) -> usize {
    if n <= 1 {
        1
    } else {
        n * factorial(n - 1)
    }
}

struct FactorialArray<T, const N: usize> {
    data: [T; factorial(N)],
}

impl<T: Default + Copy, const N: usize> FactorialArray<T, N> {
    fn new() -> Self {
        FactorialArray {
            data: [T::default(); factorial(N)],
        }
    }
    
    fn factorial_size() -> usize {
        factorial(N)
    }
}

fn main() {
    let arr1 = Array::new([1, 2, 3, 4, 5]);
    let arr2 = Array::new(["a", "b", "c"]);
    
    println!("Length: {}", arr1.len());
    println!("First element: {:?}", arr1.get(0));
    
    let (first_half, second_half) = arr1.split_half();
    println!("First half: {:?}", first_half);
    println!("Second half: {:?}", second_half);
    
    // 調整大小
    if let Some(smaller) = arr1.resize::<3>() {
        println!("Resized array: {:?}", smaller.data);
    }
    
    process_array([1, 2, 3]);
    process_array(["hello", "world"]);
    
    // 矩陣運算
    let mut matrix1 = Matrix::<i32, 2, 3>::new();
    matrix1.set(0, 0, 1).unwrap();
    matrix1.set(0, 1, 2).unwrap();
    matrix1.set(0, 2, 3).unwrap();
    matrix1.set(1, 0, 4).unwrap();
    matrix1.set(1, 1, 5).unwrap();
    matrix1.set(1, 2, 6).unwrap();
    
    println!("Matrix 1: {:?}", matrix1);
    
    let transposed = matrix1.transpose();
    println!("Transposed: {:?}", transposed);
    
    // 矩陣乘法
    let matrix2 = Matrix::from_array([[1, 2], [3, 4], [5, 6]]);
    let product = matrix1.multiply(&matrix2);
    println!("Product: {:?}", product);
    
    // 階乘陣列
    let fact_arr = FactorialArray::<i32, 3>::new();
    println!("Factorial array size: {}", fact_arr.factorial_size()); // 6
    
    // 安全存取
    safe_array_access(&arr1, 2);
    safe_array_access(&arr1, 10);
}
```

### 10.2 類型級別運算

```rust
use std::marker::PhantomData;

// 類型級別的數字
struct Zero;
struct Succ<N>(PhantomData<N>);

type One = Succ<Zero>;
type Two = Succ<One>;
type Three = Succ<Two>;
type Four = Succ<Three>;
type Five = Succ<Four>;

// 編譯時長度計算
trait Length {
    const LENGTH: usize;
}

impl Length for Zero {
    const LENGTH: usize = 0;
}

impl<N: Length> Length for Succ<N> {
    const LENGTH: usize = N::LENGTH + 1;
}

// 編譯時保證的向量長度
struct Vec<T, N> {
    data: std::vec::Vec<T>,
    _phantom: PhantomData<N>,
}

impl<T, N: Length> Vec<T, N> {
    fn new() -> Self {
        Vec {
            data: std::vec::Vec::with_capacity(N::LENGTH),
            _phantom: PhantomData,
        }
    }
    
    fn push(mut self, item: T) -> Vec<T, Succ<N>> {
        self.data.push(item);
        Vec {
            data: self.data,
            _phantom: PhantomData,
        }
    }
    
    fn len(&self) -> usize {
        N::LENGTH
    }
    
    fn get(&self, index: usize) -> Option<&T> {
        self.data.get(index)
    }
}

// 只有非空向量才能 pop
impl<T, N> Vec<T, Succ<N>> {
    fn pop(mut self) -> (T, Vec<T, N>) {
        let item = self.data.pop().expect("Vector should not be empty");
        (item, Vec {
            data: self.data,
            _phantom: PhantomData,
        })
    }
    
    fn head(&self) -> &T {
        &self.data[0]
    }
}

// 類型級別的布林值
struct True;
struct False;

trait Bool {
    const VALUE: bool;
}

impl Bool for True {
    const VALUE: bool = true;
}

impl Bool for False {
    const VALUE: bool = false;
}

// 條件類型
trait If<Condition> {
    type Output;
}

struct IfImpl<Then, Else> {
    _phantom: PhantomData<(Then, Else)>,
}

impl<Then, Else> If<True> for IfImpl<Then, Else> {
    type Output = Then;
}

impl<Then, Else> If<False> for IfImpl<Then, Else> {
    type Output = Else;
}

// 類型級別比較
trait Equal<Other> {
    type Output: Bool;
}

impl Equal<Zero> for Zero {
    type Output = True;
}

impl<N> Equal<Zero> for Succ<N> {
    type Output = False;
}

impl<N> Equal<Succ<N>> for Zero {
    type Output = False;
}

impl<N, M> Equal<Succ<M>> for Succ<N>
where
    N: Equal<M>,
{
    type Output = N::Output;
}

// 類型級別加法
trait Add<Other> {
    type Output;
}

impl<N> Add<N> for Zero {
    type Output = N;
}

impl<N, M> Add<M> for Succ<N>
where
    N: Add<M>,
{
    type Output = Succ<N::Output>;
}

// 使用類型級別運算的向量連接
impl<T, N, M> Vec<T, N>
where
    N: Add<M>,
{
    fn concat<L: Length>(self, other: Vec<T, M>) -> Vec<T, N::Output>
    where
        M: Length,
        N::Output: Length,
    {
        let mut combined_data = self.data;
        combined_data.extend(other.data);
        Vec {
            data: combined_data,
            _phantom: PhantomData,
        }
    }
}

// 證明類型
struct Proof<Statement>(PhantomData<Statement>);

impl<Statement> Proof<Statement> {
    fn new() -> Self {
        Proof(PhantomData)
    }
}

// 只有當兩個類型相等時才能創建證明
impl<T> Proof<(T, T)>
where
    T: Equal<T, Output = True>,
{
    fn reflexivity() -> Self {
        Proof(PhantomData)
    }
}

fn main() {
    // 類型安全的向量操作
    let vec = Vec::<i32, Zero>::new()
        .push(1)
        .push(2)
        .push(3);
    
    println!("Vector length: {}", vec.len()); // 3
    
    let (head, tail) = vec.pop();
    println!("Head: {}, tail length: {}", head, tail.len()); // 3, 2
    
    let (second, tail2) = tail.pop();
    println!("Second: {}, tail2 length: {}", second, tail2.len()); // 2, 1
    
    // 向量連接
    let vec1 = Vec::<&str, Zero>::new().push("hello");
    let vec2 = Vec::<&str, Zero>::new().push("world").push("!");
    
    let combined = vec1.concat(vec2);
    println!("Combined length: {}", combined.len()); // 3
    
    // 類型級別計算驗證
    assert_eq!(Zero::LENGTH, 0);
    assert_eq!(One::LENGTH, 1);
    assert_eq!(Two::LENGTH, 2);
    assert_eq!(Three::LENGTH, 3);
    
    // 編譯時證明
    let _proof = Proof::<(Zero, Zero)>::reflexivity();
    // let _invalid = Proof::<(Zero, One)>::reflexivity(); // 編譯錯誤
}
```

## 11. 進階應用

### 11.1 泛型建造者模式與類型狀態機

```rust
use std::marker::PhantomData;

// 狀態標記
struct Uninitialized;
struct HasName;
struct HasAge;
struct Complete;

// 建造者結構
struct PersonBuilder<State = Uninitialized> {
    name: Option<String>,
    age: Option<u32>,
    email: Option<String>,
    _state: PhantomData<State>,
}

impl PersonBuilder<Uninitialized> {
    fn new() -> Self {
        PersonBuilder {
            name: None,
            age: None,
            email: None,
            _state: PhantomData,
        }
    }
}

impl<State> PersonBuilder<State> {
    fn set_email(mut self, email: String) -> Self {
        self.email = Some(email);
        self
    }
}

impl PersonBuilder<Uninitialized> {
    fn set_name(mut self, name: String) -> PersonBuilder<HasName> {
        self.name = Some(name);
        PersonBuilder {
            name: self.name,
            age: self.age,
            email: self.email,
            _state: PhantomData,
        }
    }
}

impl PersonBuilder<HasName> {
    fn set_age(mut self, age: u32) -> PersonBuilder<Complete> {
        self.age = Some(age);
        PersonBuilder {
            name: self.name,
            age: self.age,
            email: self.email,
            _state: PhantomData,
        }
    }
}

#[derive(Debug)]
struct Person {
    name: String,
    age: u32,
    email: Option<String>,
}

impl PersonBuilder<Complete> {
    fn build(self) -> Person {
        Person {
            name: self.name.unwrap(),
            age: self.age.unwrap(),
            email: self.email,
        }
    }
    
    fn reset(self) -> PersonBuilder<Uninitialized> {
        PersonBuilder::new()
    }
}

// 更複雜的狀態機：文檔處理器
#[derive(Debug)]
struct Draft;
#[derive(Debug)]
struct Review;
#[derive(Debug)]
struct Published;

struct Document<State> {
    title: String,
    content: String,
    author: String,
    _state: PhantomData<State>,
}

impl Document<Draft> {
    fn new(title: String, author: String) -> Self {
        Document {
            title,
            content: String::new(),
            author,
            _state: PhantomData,
        }
    }
    
    fn write_content(mut self, content: String) -> Self {
        self.content = content;
        self
    }
    
    fn submit_for_review(self) -> Document<Review> {
        println!("Document '{}' submitted for review", self.title);
        Document {
            title: self.title,
            content: self.content,
            author: self.author,
            _state: PhantomData,
        }
    }
}

impl Document<Review> {
    fn approve(self) -> Document<Published> {
        println!("Document '{}' approved for publication", self.title);
        Document {
            title: self.title,
            content: self.content,
            author: self.author,
            _state: PhantomData,
        }
    }
    
    fn reject(self) -> Document<Draft> {
        println!("Document '{}' rejected, back to draft", self.title);
        Document {
            title: self.title,
            content: self.content,
            author: self.author,
            _state: PhantomData,
        }
    }
    
    fn request_changes(mut self, feedback: String) -> Document<Draft> {
        println!("Changes requested for '{}': {}", self.title, feedback);
        self.content.push_str(&format!("\n[FEEDBACK: {}]", feedback));
        Document {
            title: self.title,
            content: self.content,
            author: self.author,
            _state: PhantomData,
        }
    }
}

impl Document<Published> {
    fn get_published_content(&self) -> &str {
        &self.content
    }
    
    fn retract(self) -> Document<Draft> {
        println!("Document '{}' retracted", self.title);
        Document {
            title: self.title,
            content: self.content,
            author: self.author,
            _state: PhantomData,
        }
    }
}

// 泛型狀態機 trait
trait StateMachine {
    type State;
    type Input;
    type Output;
    
    fn transition(self, input: Self::Input) -> Self::Output;
}

fn main() {
    // 建造者模式範例
    let person = PersonBuilder::new()
        .set_name("Alice".to_string())
        .set_age(30)
        .set_email("alice@example.com".to_string())
        .build();
    
    println!("Built person: {:?}", person);
    
    // 這會編譯錯誤，因為沒有設置必要的字段
    // let invalid = PersonBuilder::new().build();
    
    // 文檔狀態機範例
    let doc = Document::new(
        "Rust Generics Guide".to_string(),
        "Rust Developer".to_string(),
    )
    .write_content("This is a comprehensive guide to Rust generics...".to_string())
    .submit_for_review()
    .request_changes("Please add more examples".to_string())
    .write_content("Updated content with more examples...".to_string())
    .submit_for_review()
    .approve();
    
    println!("Published content: {}", doc.get_published_content());
}
```

### 11.2 GADTs (Generalized Algebraic Data Types) 模擬

```rust
use std::marker::PhantomData;

// 類型級別的標記
struct IntType;
struct StringType;
struct BoolType;
struct FloatType;

// 泛型表達式類型
enum Expr<T> {
    IntLit(i32, PhantomData<T>),
    StringLit(String, PhantomData<T>),
    BoolLit(bool, PhantomData<T>),
    FloatLit(f64, PhantomData<T>),
    Add(Box<Expr<IntType>>, Box<Expr<IntType>>, PhantomData<T>),
    Concat(Box<Expr<StringType>>, Box<Expr<StringType>>, PhantomData<T>),
    Equal(Box<dyn EqualExpr>, Box<dyn EqualExpr>, PhantomData<T>),
    If(Box<Expr<BoolType>>, Box<dyn AnyExpr>, Box<dyn AnyExpr>, PhantomData<T>),
}

// 支持相等比較的表達式
trait EqualExpr {
    fn eval_equal(&self) -> Box<dyn std::any::Any>;
    fn type_name(&self) -> &'static str;
}

// 任意類型的表達式
trait AnyExpr {
    fn eval_any(&self) -> Box<dyn std::any::Any>;
    fn type_name(&self) -> &'static str;
}

impl Expr<IntType> {
    fn int_lit(value: i32) -> Self {
        Expr::IntLit(value, PhantomData)
    }
    
    fn add(left: Expr<IntType>, right: Expr<IntType>) -> Self {
        Expr::Add(Box::new(left), Box::new(right), PhantomData)
    }
}

impl Expr<StringType> {
    fn string_lit(value: String) -> Self {
        Expr::StringLit(value, PhantomData)
    }
    
    fn concat(left: Expr<StringType>, right: Expr<StringType>) -> Self {
        Expr::Concat(Box::new(left), Box::new(right), PhantomData)
    }
}

impl Expr<BoolType> {
    fn bool_lit(value: bool) -> Self {
        Expr::BoolLit(value, PhantomData)
    }
    
    fn equal<T: 'static>(left: Expr<T>, right: Expr<T>) -> Self 
    where
        Expr<T>: EqualExpr,
    {
        Expr::Equal(Box::new(left), Box::new(right), PhantomData)
    }
}

impl Expr<FloatType> {
    fn float_lit(value: f64) -> Self {
        Expr::FloatLit(value, PhantomData)
    }
}

// 求值 trait
trait Eval<T> {
    type Output;
    fn eval(self) -> Self::Output;
}

impl Eval<IntType> for Expr<IntType> {
    type Output = i32;
    
    fn eval(self) -> i32 {
        match self {
            Expr::IntLit(n, _) => n,
            Expr::Add(left, right, _) => left.eval() + right.eval(),
            _ => unreachable!(),
        }
    }
}

impl Eval<StringType> for Expr<StringType> {
    type Output = String;
    
    fn eval(self) -> String {
        match self {
            Expr::StringLit(s, _) => s,
            Expr::Concat(left, right, _) => {
                format!("{}{}", left.eval(), right.eval())
            },
            _ => unreachable!(),
        }
    }
}

impl Eval<BoolType> for Expr<BoolType> {
    type Output = bool;
    
    fn eval(self) -> bool {
        match self {
            Expr::BoolLit(b, _) => b,
            Expr::Equal(left, right, _) => {
                let left_val = left.eval_equal();
                let right_val = right.eval_equal();
                // 簡化的相等比較
                format!("{:?}", left_val) == format!("{:?}", right_val)
            },
            _ => unreachable!(),
        }
    }
}

impl Eval<FloatType> for Expr<FloatType> {
    type Output = f64;
    
    fn eval(self) -> f64 {
        match self {
            Expr::FloatLit(f, _) => f,
            _ => unreachable!(),
        }
    }
}

// 實現 trait 以支持異構比較
impl EqualExpr for Expr<IntType> {
    fn eval_equal(&self) -> Box<dyn std::any::Any> {
        Box::new(self.clone().eval())
    }
    
    fn type_name(&self) -> &'static str {
        "IntType"
    }
}

impl Clone for Expr<IntType> {
    fn clone(&self) -> Self {
        match self {
            Expr::IntLit(n, _) => Expr::IntLit(*n, PhantomData),
            Expr::Add(left, right, _) => {
                Expr::Add(left.clone(), right.clone(), PhantomData)
            },
            _ => unreachable!(),
        }
    }
}

// 編譯時類型檢查的 DSL
macro_rules! expr {
    ($value:literal) => {
        {
            match $value {
                val if val.is_integer() => Expr::int_lit(val as i32),
                val if val.is_float() => Expr::float_lit(val as f64),
                val if val.is_string() => Expr::string_lit(val.to_string()),
                val if val.is_bool() => Expr::bool_lit(val),
            }
        }
    };
}

// 類型安全的表達式組合子
struct ExprBuilder;

impl ExprBuilder {
    fn int(value: i32) -> Expr<IntType> {
        Expr::int_lit(value)
    }
    
    fn string(value: &str) -> Expr<StringType> {
        Expr::string_lit(value.to_string())
    }
    
    fn bool(value: bool) -> Expr<BoolType> {
        Expr::bool_lit(value)
    }
    
    fn add(left: Expr<IntType>, right: Expr<IntType>) -> Expr<IntType> {
        Expr::add(left, right)
    }
    
    fn concat(left: Expr<StringType>, right: Expr<StringType>) -> Expr<StringType> {
        Expr::concat(left, right)
    }
}

fn main() {
    // 類型安全的表達式構建和求值
    let int_expr = ExprBuilder::add(
        ExprBuilder::int(10),
        ExprBuilder::int(20)
    );
    
    let string_expr = ExprBuilder::concat(
        ExprBuilder::string("Hello, "),
        ExprBuilder::string("World!")
    );
    
    println!("Int result: {}", int_expr.eval());
    println!("String result: {}", string_expr.eval());
    
    // 這會編譯錯誤，因為類型不匹配
    // let invalid = ExprBuilder::add(
    //     ExprBuilder::int(1), 
    //     ExprBuilder::string("hello")
    // );
    
    let bool_expr = ExprBuilder::bool(true);
    println!("Bool result: {}", bool_expr.eval());
}
```

### 11.3 類型級別編程與異構集合

```rust
use std::any::{Any, TypeId};
use std::collections::HashMap;
use std::marker::PhantomData;

// 類型安全的異構映射
struct TypeMap {
    data: HashMap<TypeId, Box<dyn Any>>,
}

impl TypeMap {
    fn new() -> Self {
        TypeMap {
            data: HashMap::new(),
        }
    }
    
    fn insert<T: 'static>(&mut self, value: T) -> Option<T> {
        let type_id = TypeId::of::<T>();
        self.data
            .insert(type_id, Box::new(value))
            .and_then(|old| old.downcast().ok().map(|boxed| *boxed))
    }
    
    fn get<T: 'static>(&self) -> Option<&T> {
        let type_id = TypeId::of::<T>();
        self.data
            .get(&type_id)
            .and_then(|boxed| boxed.downcast_ref::<T>())
    }
    
    fn get_mut<T: 'static>(&mut self) -> Option<&mut T> {
        let type_id = TypeId::of::<T>();
        self.data
            .get_mut(&type_id)
            .and_then(|boxed| boxed.downcast_mut::<T>())
    }
    
    fn remove<T: 'static>(&mut self) -> Option<T> {
        let type_id = TypeId::of::<T>();
        self.data
            .remove(&type_id)
            .and_then(|boxed| boxed.downcast().ok().map(|boxed| *boxed))
    }
    
    fn contains<T: 'static>(&self) -> bool {
        self.data.contains_key(&TypeId::of::<T>())
    }
}

// 異構列表 (HList)
struct HNil;

struct HCons<Head, Tail> {
    head: Head,
    tail: Tail,
}

// HList 構建宏
macro_rules! hlist {
    () => { HNil };
    ($head:expr) => { HCons { head: $head, tail: HNil } };
    ($head:expr, $($tail:expr),+) => {
        HCons { head: $head, tail: hlist!($($tail),+) }
    };
}

// HList 操作 trait
trait HListOps {
    type Length;
    
    fn length(&self) -> usize;
}

impl HListOps for HNil {
    type Length = Zero;
    
    fn length(&self) -> usize {
        0
    }
}

impl<Head, Tail: HListOps> HListOps for HCons<Head, Tail> {
    type Length = Succ<Tail::Length>;
    
    fn length(&self) -> usize {
        1 + self.tail.length()
    }
}

// HList 索引訪問
trait Get<Index> {
    type Output;
    
    fn get(&self) -> &Self::Output;
}

// 獲取第一個元素
impl<Head, Tail> Get<Zero> for HCons<Head, Tail> {
    type Output = Head;
    
    fn get(&self) -> &Self::Output {
        &self.head
    }
}

// 遞歸獲取後續元素
impl<Head, Tail, Index> Get<Succ<Index>> for HCons<Head, Tail>
where
    Tail: Get<Index>,
{
    type Output = Tail::Output;
    
    fn get(&self) -> &Self::Output {
        self.tail.get()
    }
}

// 異構映射操作
trait HMap<F> {
    type Output;
    
    fn map(self, f: F) -> Self::Output;
}

impl<F> HMap<F> for HNil {
    type Output = HNil;
    
    fn map(self, _f: F) -> Self::Output {
        HNil
    }
}

impl<Head, Tail, F> HMap<F> for HCons<Head, Tail>
where
    F: Fn(Head) -> Head + Clone,
    Tail: HMap<F>,
{
    type Output = HCons<Head, Tail::Output>;
    
    fn map(self, f: F) -> Self::Output {
        HCons {
            head: f(self.head),
            tail: self.tail.map(f.clone()),
        }
    }
}

// 動態分發的異構容器
trait Component: Any + std::fmt::Debug {
    fn as_any(&self) -> &dyn Any;
    fn as_any_mut(&mut self) -> &mut dyn Any;
}

impl<T: Any + std::fmt::Debug> Component for T {
    fn as_any(&self) -> &dyn Any {
        self
    }
    
    fn as_any_mut(&mut self) -> &mut dyn Any {
        self
    }
}

struct Entity {
    components: HashMap<TypeId, Box<dyn Component>>,
}

impl Entity {
    fn new() -> Self {
        Entity {
            components: HashMap::new(),
        }
    }
    
    fn add_component<T: Component + 'static>(&mut self, component: T) {
        self.components.insert(TypeId::of::<T>(), Box::new(component));
    }
    
    fn get_component<T: Component + 'static>(&self) -> Option<&T> {
        self.components
            .get(&TypeId::of::<T>())
            .and_then(|component| component.as_any().downcast_ref::<T>())
    }
    
    fn get_component_mut<T: Component + 'static>(&mut self) -> Option<&mut T> {
        self.components
            .get_mut(&TypeId::of::<T>())
            .and_then(|component| component.as_any_mut().downcast_mut::<T>())
    }
    
    fn has_component<T: Component + 'static>(&self) -> bool {
        self.components.contains_key(&TypeId::of::<T>())
    }
}

// 示例組件
#[derive(Debug)]
struct Position { x: f32, y: f32 }

#[derive(Debug)]
struct Velocity { dx: f32, dy: f32 }

#[derive(Debug)]
struct Health { current: u32, max: u32 }

// 類型級別的數字（重用之前的定義）
struct Zero;
struct Succ<N>(PhantomData<N>);

fn main() {
    // TypeMap 範例
    let mut type_map = TypeMap::new();
    
    type_map.insert(42i32);
    type_map.insert("hello".to_string());
    type_map.insert(true);
    type_map.insert(3.14f64);
    
    println!("i32: {:?}", type_map.get::<i32>());new_data[i] = self.data[i].clone();
        }
        Some(Array::new(new_data))
    }
}

// 泛型常數在函數中
fn process_array<T: Debug, const N: usize>(arr: [T; N])
where
    T: std::fmt::Debug,
{
    println!("Array length: {}", N);
    for (i, item) in arr.iter().enumerate() {
        println!("[{}]: {:?}", i, item);
    }
}

// 矩陣運算與常數泛型
#[derive(Debug, Clone)]
struct Matrix<T, const ROWS: usize, const COLS: usize> {
    data: [[T; COLS]; ROWS],
}

impl<T, const ROWS: usize, const COLS: usize> Matrix<T, ROWS, COLS> 
where
    T: Copy + Default + Debug,
{
    fn new() -> Self {
        Matrix {
            data: [[T::default(); COLS]; ROWS],
        }
    }
    
    fn from_array(data: [[T; COLS]; ROWS]) -> Self {
        Matrix { data }
    }
    
    fn get(&self, row: usize, col: usize) -> Option<&T> {
        self.data.get(row)?.get(col)
    }
    
    fn set(&mut self, row: usize, col: usize, value: T) -> Result<(), &'static str> {
        if row >= ROWS || col >= COLS {
            return Err("Index out of bounds");
        }
        self.data[row][col] = value;
        Ok(())
    }
    
    // 矩陣轉置 (只對方陣有效)
    fn transpose(&self) -> Matrix<T, COLS, ROWS> {
        let mut result = Matrix::<T, COLS, ROWS>::new();
        for i in 0..ROWS {
            for j in 0..COLS {
                result.data[j][i] = self.data[i][j];
            }
        }
        result
    }
}

// 矩陣乘法（編譯時檢查維度）
impl<T, const M: usize, const N: usize, const P: usize> Matrix<T, M, N>
where
    T: Copy + Default + std::ops::Add<Output = T> + std::ops::Mul<Output = T>,
{
    fn multiply(&self, other: &Matrix<T, N, P>) -> Matrix<T, M, P> {
        let mut result = Matrix::<T, M, P>::new();
        
        for i in 0..M {
            

## 6. 生命週期泛型

### 6.1 基本生命週期

```rust
// 生命週期參數
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

// 結構體中的生命週期
struct ImportantExcerpt<'a> {
    part: &'a str,
}

impl<'a> ImportantExcerpt<'a> {
    fn level(&self) -> i32 {
        3
    }
    
    // 生命週期省略規則
    fn announce_and_return_part(&self, announcement: &str) -> &str {
        println!("Attention please: {}", announcement);
        self.part
    }
}

fn main() {
    let string1 = String::from("abcd");
    let string2 = "xyz";
    
    let result = longest(string1.as_str(), string2);
    println!("The longest string is {}", result);
    
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().expect("Could not find a '.'");
    let i = ImportantExcerpt {
        part: first_sentence,
    };
}
```

### 6.2 靜態生命週期

```rust
// 'static 生命週期
fn get_static_str() -> &'static str {
    "This is a static string"
}

struct StaticHolder {
    value: &'static str,
}

// 泛型 + 生命週期 + trait 約束
fn print_with_lifetime<'a, T>(item: &'a T)
where
    T: std::fmt::Display + 'a,
{
    println!("{}", item);
}

fn main() {
    let s = get_static_str();
    let holder = StaticHolder { value: s };
    
    print_with_lifetime(&42);
    print_with_lifetime(&"hello");
}
```

## 7. 關聯類型

### 7.1 基本關聯類型

```rust
// 使用關聯類型的 trait
trait Iterator {
    type Item;
    
    fn next(&mut self) -> Option<Self::Item>;
}

trait Collect<T> {
    fn collect(self) -> T;
}

// 實現 Iterator trait
struct Counter {
    current: u32,
    max: u32,
}

impl Counter {
    fn new(max: u32) -> Counter {
        Counter { current: 0, max }
    }
}

impl Iterator for Counter {
    type Item = u32;
    
    fn next(&mut self) -> Option<Self::Item> {
        if self.current < self.max {
            let current = self.current;
            self.current += 1;
            Some(current)
        } else {
            None
        }
    }
}

fn main() {
    let mut counter = Counter::new(3);
    
    while let Some(value) = counter.next() {
        println!("{}", value);
    }
}
```

### 7.2 關聯類型 vs 泛型

```rust
use std::fmt::Debug;

// 使用泛型 - 允許多種實現
trait GenericTrait<T> {
    fn process(&self, item: T) -> T;
}

// 使用關聯類型 - 每個類型只有一種實現
trait AssociatedTrait {
    type Output;
    
    fn process(&self) -> Self::Output;
}

struct Processor;

// 可以為同一個類型實現不同的泛型版本
impl GenericTrait<i32> for Processor {
    fn process(&self, item: i32) -> i32 {
        item * 2
    }
}

impl GenericTrait<String> for Processor {
    fn process(&self, item: String) -> String {
        format!("Processed: {}", item)
    }
}

// 但關聯類型只能有一個實現
impl AssociatedTrait for Processor {
    type Output = String;
    
    fn process(&self) -> Self::Output {
        "Default processing".to_string()
    }
}

fn main() {
    let processor = Processor;
    
    // 泛型版本需要明確指定類型
    let result1: i32 = processor.process(10);
    let result2: String = processor.process("hello".to_string());
    
    // 關聯類型版本類型自動推斷
    let result3 = processor.process();
    
    println!("{}, {}, {}", result1, result2, result3);
}
```

## 8. 高階 Trait 約束

### 8.1 Higher-Rank Trait Bounds (HRTB)

```rust
// for<'a> 語法 - 對所有生命週期都成立
fn apply_to_all<F>(f: F)
where
    F: for<'a> Fn(&'a str) -> &'a str,
{
    let s1 = "hello";
    let s2 = "world";
    
    println!("{}", f(s1));
    println!("{}", f(s2));
}

fn identity(s: &str) -> &str {
    s
}

fn main() {
    apply_to_all(identity);
    apply_to_all(|s| s);
}
```

### 8.2 複雜的 Trait 約束

```rust
use std::fmt::{Debug, Display};
use std::ops::Add;

// 複雜的泛型約束
fn complex_operation<T, U, V>(a: T, b: U) -> V
where
    T: Display + Debug + Clone + Send + 'static,
    U: Into<V> + Copy,
    V: Add<V, Output = V> + Default + Debug,
{
    println!("Processing: {} (debug: {:?})", a, a);
    let converted: V = b.into();
    let default_val = V::default();
    let result = converted + default_val;
    println!("Result: {:?}", result);
    result
}

// 使用 impl Trait 簡化
fn simple_operation(value: impl Display + Debug + Clone) -> impl Debug {
    println!("Value: {} ({:?})", value, value);
    format!("Processed: {}", value)
}

fn main() {
    let result: i32 = complex_operation("hello".to_string(), 42u8);
    let simple = simple_operation("world");
    
    println!("Complex result: {:?}", result);
    println!("Simple result: {:?}", simple);
}
```

## 9. 泛型常數

### 9.1 Const 泛型 (Rust 1.51+)

```rust
// 泛型常數參數
struct Array<T, const N: usize> {
    data: [T; N],
}

impl<T, const N: usize> Array<T, N> {
    fn new(data: [T; N]) -> Self {
        Array { data }
    }
    
    fn len(&self) -> usize {
        N
    }
    
    fn get(&self, index: usize) -> Option<&T> {
        self.data.get(index)
    }
}

// 泛型常數在函數中
fn process_array<T: Debug, const N: usize>(arr: [T; N])
where
    T: std::fmt::Debug,
{
    println!("Array length: {}", N);
    for (i, item) in arr.iter().enumerate() {
        println!("[{}]: {:?}", i, item);
    }
}

fn main() {
    let arr1 = Array::new([1, 2, 3, 4, 5]);
    let arr2 = Array::new(["a", "b", "c"]);
    
    println!("Length: {}", arr1.len());
    println!("First element: {:?}", arr1.get(0));
    
    process_array([1, 2, 3]);
    process_array(["hello", "world"]);
}
```

### 9.2 類型級別運算

```rust
use std::marker::PhantomData;

// 類型級別的數字
struct Zero;
struct Succ<N>(PhantomData<N>);

type One = Succ<Zero>;
type Two = Succ<One>;
type Three = Succ<Two>;

// 編譯時保證的向量長度
struct Vec<T, N> {
    data: std::vec::Vec<T>,
    _phantom: PhantomData<N>,
}

trait Length {
    const LENGTH: usize;
}

impl Length for Zero {
    const LENGTH: usize = 0;
}

impl<N: Length> Length for Succ<N> {
    const LENGTH: usize = N::LENGTH + 1;
}

impl<T, N: Length> Vec<T, N> {
    fn new() -> Self {
        Vec {
            data: std::vec::Vec::with_capacity(N::LENGTH),
            _phantom: PhantomData,
        }
    }
    
    fn push(mut self, item: T) -> Vec<T, Succ<N>> {
        self.data.push(item);
        Vec {
            data: self.data,
            _phantom: PhantomData,
        }
    }
    
    fn len(&self) -> usize {
        N::LENGTH
    }
}

fn main() {
    let vec = Vec::<i32, Zero>::new()
        .push(1)
        .push(2)
        .push(3);
    
    println!("Vector length: {}", vec.len()); // 3
}
```

## 10. 進階應用

### 10.1 泛型建造者模式

```rust
use std::marker::PhantomData;

// 類型狀態機
struct Uninitialized;
struct Initialized;

struct Builder<T, State = Uninitialized> {
    value: Option<T>,
    _state: PhantomData<State>,
}

impl<T> Builder<T, Uninitialized> {
    fn new() -> Self {
        Builder {
            value: None,
            _state: PhantomData,
        }
    }
    
    fn set_value(self, value: T) -> Builder<T, Initialized> {
        Builder {
            value: Some(value),
            _state: PhantomData,
        }
    }
}

impl<T> Builder<T, Initialized> {
    fn build(self) -> T {
        self.value.unwrap()
    }
    
    fn reset(self) -> Builder<T, Uninitialized> {
        Builder {
            value: None,
            _state: PhantomData,
        }
    }
}

fn main() {
    let value = Builder::new()
        .set_value("Hello, World!")
        .build();
    
    println!("{}", value);
    
    // 這會編譯錯誤，因為沒有設置值就嘗試建造
    // let invalid = Builder::<String>::new().build();
}
```

### 10.2 GADTs (Generalized Algebraic Data Types) 模擬

```rust
use std::marker::PhantomData;

// 類型級別的標記
struct IntType;
struct StringType;
struct BoolType;

// 泛型表達式類型
enum Expr<T> {
    IntLit(i32, PhantomData<T>),
    StringLit(String, PhantomData<T>),
    BoolLit(bool, PhantomData<T>),
    Add(Box<Expr<IntType>>, Box<Expr<IntType>>, PhantomData<T>),
    Concat(Box<Expr<StringType>>, Box<Expr<StringType>>, PhantomData<T>),
}

impl Expr<IntType> {
    fn int_lit(value: i32) -> Self {
        Expr::IntLit(value, PhantomData)
    }
    
    fn add(left: Expr<IntType>, right: Expr<IntType>) -> Self {
        Expr::Add(Box::new(left), Box::new(right), PhantomData)
    }
}

impl Expr<StringType> {
    fn string_lit(value: String) -> Self {
        Expr::StringLit(value, PhantomData)
    }
    
    fn concat(left: Expr<StringType>, right: Expr<StringType>) -> Self {
        Expr::Concat(Box::new(left), Box::new(right), PhantomData)
    }
}

impl Expr<BoolType> {
    fn bool_lit(value: bool) -> Self {
        Expr::BoolLit(value, PhantomData)
    }
}

// 求值函數
trait Eval<T> {
    type Output;
    fn eval(self) -> Self::Output;
}

impl Eval<IntType> for Expr<IntType> {
    type Output = i32;
    
    fn eval(self) -> i32 {
        match self {
            Expr::IntLit(n, _) => n,
            Expr::Add(left, right, _) => left.eval() + right.eval(),
            _ => unreachable!(),
        }
    }
}

impl Eval<StringType> for Expr<StringType> {
    type Output = String;
    
    fn eval(self) -> String {
        match self {
            Expr::StringLit(s, _) => s,
            Expr::Concat(left, right, _) => {
                format!("{}{}", left.eval(), right.eval())
            },
            _ => unreachable!(),
        }
    }
}

fn main() {
    // 類型安全的表達式
    let int_expr = Expr::add(
        Expr::int_lit(10),
        Expr::int_lit(20)
    );
    
    let string_expr = Expr::concat(
        Expr::string_lit("Hello, ".to_string()),
        Expr::string_lit("World!".to_string())
    );
    
    println!("Int result: {}", int_expr.eval());
    println!("String result: {}", string_expr.eval());
    
    // 這會編譯錯誤，因為類型不匹配
    // let invalid = Expr::add(Expr::int_lit(1), Expr::string_lit("hello".to_string()));
}
```

### 10.3 異構集合

```rust
use std::any::{Any, TypeId};
use std::collections::HashMap;

// 類型安全的異構映射
struct TypeMap {
    data: HashMap<TypeId, Box<dyn Any>>,
}

impl TypeMap {
    fn new() -> Self {
        TypeMap {
            data: HashMap::new(),
        }
    }
    
    fn insert<T: 'static>(&mut self, value: T) {
        self.data.insert(TypeId::of::<T>(), Box::new(value));
    }
    
    fn get<T: 'static>(&self) -> Option<&T> {
        self.data.get(&TypeId::of::<T>())
            .and_then(|boxed| boxed.downcast_ref::<T>())
    }
    
    fn get_mut<T: 'static>(&mut self) -> Option<&mut T> {
        self.data.get_mut(&TypeId::of::<T>())
            .and_then(|boxed| boxed.downcast_mut::<T>())
    }
}

fn main() {
    let mut type_map = TypeMap::new();
    
    // 插入不同類型的值
    type_map.insert(42i32);
    type_map.insert("hello".to_string());
    type_map.insert(true);
    type_map.insert(3.14f64);
    
    // 類型安全的檢索
    if let Some(int_val) = type_map.get::<i32>() {
        println!("i32: {}", int_val);
    }
    
    if let Some(string_val) = type_map.get::<String>() {
        println!("String: {}", string_val);
    }
    
    // 修改值
    if let Some(bool_val) = type_map.get_mut::<bool>() {
        *bool_val = false;
        println!("Modified bool: {}", bool_val);
    }
}
```

## 總結

Rust 的泛型系統非常強大，支援：

1. **基礎泛型**：類型參數化
2. **Trait 約束**：限制泛型類型的能力
3. **生命週期**：記憶體安全保證
4. **關聯類型**：更清晰的 API 設計
5. **常數泛型**：編譯時常數參數
6. **高階約束**：複雜的類型關係
7. **類型狀態機**：編譯時狀態驗證
8. **零成本抽象**：運行時無開銷

這些特性讓 Rust 能夠在保證記憶體安全的同時，提供高度的抽象和表達能力。掌握泛型是成為 Rust 高手的關鍵技能之一。