# C++11 ~ C++23 與 Rust 功能對照表

> 詳細對比 C++ 各版本新增功能與 Rust 對應實現方式

---

## 目錄
- [C++11](#c11)
- [C++14](#c14)
- [C++17](#c17)
- [C++20](#c20)
- [C++23](#c23)
- [總結](#總結)

---

## C++11

### 1. Auto 型別推導

**C++11:**
```cpp
auto x = 42;
auto y = 3.14;
auto lambda = [](int x) { return x * 2; };
```

**Rust:**
```rust
let x = 42;        // 自動推導為 i32
let y = 3.14;      // 自動推導為 f64
let lambda = |x: i32| x * 2;
```

**說明:** Rust 的型別推導更強大，幾乎所有地方都能使用，且更安全。

---

### 2. Lambda 表達式 / 閉包

**C++11:**
```cpp
// 基本 lambda
auto add = [](int a, int b) { return a + b; };

// 捕獲外部變數
int x = 10;
auto capture_by_value = [x](int y) { return x + y; };
auto capture_by_ref = [&x](int y) { x += y; return x; };
auto capture_all = [=](int y) { return x + y; };  // 全部按值捕獲
```

**Rust:**
```rust
// 基本閉包
let add = |a: i32, b: i32| a + b;

// 自動捕獲（不可變借用）
let x = 10;
let capture_immut = |y| x + y;

// 可變捕獲
let mut x = 10;
let mut capture_mut = |y| {
    x += y;
    x
};

// 移動所有權
let s = String::from("hello");
let take_ownership = move |suffix| format!("{}{}", s, suffix);
```

**說明:** Rust 的閉包自動推斷捕獲方式（不可變借用、可變借用、移動），更安全且語法更簡潔。

---

### 3. Move Semantics（移動語義）

**C++11:**
```cpp
std::vector<int> v1 = {1, 2, 3};
std::vector<int> v2 = std::move(v1);  // v1 被移動後處於未定義狀態

// 右值引用
void process(std::vector<int>&& vec) {
    // 接受右值
}
```

**Rust:**
```rust
let v1 = vec![1, 2, 3];
let v2 = v1;  // v1 自動移動，之後無法使用

// v1 在這裡已經無效，編譯器會阻止使用
// println!("{:?}", v1);  // 編譯錯誤！

fn process(vec: Vec<i32>) {
    // 接受所有權
}
```

**說明:** Rust 的移動是**預設行為**，且編譯器強制檢查，避免 use-after-move 錯誤。C++ 需要手動 `std::move`，且移動後的物件仍可訪問（危險）。

---

### 4. 智慧指標 (Smart Pointers)

**C++11:**
```cpp
#include <memory>

// unique_ptr - 獨佔所有權
std::unique_ptr<int> p1 = std::make_unique<int>(42);
std::unique_ptr<int> p2 = std::move(p1);  // 轉移所有權

// shared_ptr - 共享所有權（引用計數）
std::shared_ptr<int> s1 = std::make_shared<int>(100);
std::shared_ptr<int> s2 = s1;  // 引用計數 +1

// weak_ptr - 弱引用，避免循環引用
std::weak_ptr<int> w1 = s1;
```

**Rust:**
```rust
use std::rc::Rc;
use std::sync::Arc;

// Box - 堆上分配（類似 unique_ptr）
let b1 = Box::new(42);
let b2 = b1;  // 所有權移動

// Rc - 單執行緒引用計數（類似 shared_ptr）
let r1 = Rc::new(100);
let r2 = Rc::clone(&r1);  // 引用計數 +1

// Arc - 多執行緒安全的引用計數
let a1 = Arc::new(200);
let a2 = Arc::clone(&a1);

// Weak - 弱引用
let w1 = Rc::downgrade(&r1);
```

**說明:** 
- Rust 區分單執行緒 (`Rc`) 和多執行緒 (`Arc`) 的引用計數
- Rust 沒有預設的垃圾回收，所有權系統更明確
- C++ 的 `shared_ptr` 在多執行緒下也是安全的（使用原子操作）

---

### 5. 範圍 for 迴圈 (Range-based for)

**C++11:**
```cpp
std::vector<int> vec = {1, 2, 3, 4, 5};

// 遍歷
for (int x : vec) {
    std::cout << x << " ";
}

// 引用遍歷（可修改）
for (int& x : vec) {
    x *= 2;
}

// const 引用（不可修改）
for (const auto& x : vec) {
    std::cout << x << " ";
}
```

**Rust:**
```rust
let vec = vec![1, 2, 3, 4, 5];

// 不可變遍歷（借用）
for x in &vec {
    println!("{}", x);
}

// 可變遍歷
let mut vec = vec![1, 2, 3];
for x in &mut vec {
    *x *= 2;
}

// 消耗迭代器（移動所有權）
for x in vec {
    println!("{}", x);
}
// vec 在這裡已失效
```

**說明:** Rust 強制明確指定是借用 `&`、可變借用 `&mut` 還是移動所有權，避免意外修改。

---

### 6. nullptr

**C++11:**
```cpp
int* ptr = nullptr;  // 取代 NULL 或 0

void func(int* p) { }
void func(int i) { }

func(nullptr);  // 明確呼叫指標版本
func(NULL);     // C++11 前可能有歧義
```

**Rust:**
```rust
// Rust 沒有 null 指標！
// 使用 Option<T> 表示可能為空的值

let ptr: Option<Box<i32>> = None;
let ptr2: Option<Box<i32>> = Some(Box::new(42));

// 使用 match 處理
match ptr2 {
    Some(val) => println!("值: {}", val),
    None => println!("空值"),
}

// 或使用 if let
if let Some(val) = ptr2 {
    println!("值: {}", val);
}
```

**說明:** Rust 徹底消除了 null pointer 問題，使用 `Option<T>` 型別系統強制處理空值情況，這是**十億美元的錯誤**的解決方案。

---

### 7. 強型別列舉 (Enum class)

**C++11:**
```cpp
// 傳統 enum（全域命名空間污染）
enum Color { RED, GREEN, BLUE };

// C++11 enum class（強型別）
enum class Status {
    Success,
    Failed,
    Pending
};

Status s = Status::Success;
// int x = Status::Success;  // 編譯錯誤，無法隱式轉換
```

**Rust:**
```rust
// Rust 的 enum 更強大，可以帶資料
enum Status {
    Success,
    Failed,
    Pending,
}

let s = Status::Success;

// 帶資料的 enum
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}

let msg = Message::Write(String::from("hello"));

// 使用 match 處理
match msg {
    Message::Quit => println!("退出"),
    Message::Move { x, y } => println!("移動到 ({}, {})", x, y),
    Message::Write(text) => println!("訊息: {}", text),
    Message::ChangeColor(r, g, b) => println!("顏色: ({}, {}, {})", r, g, b),
}
```

**說明:** Rust 的 enum 是**代數資料型別**（ADT），比 C++ 強大得多，類似 Haskell/OCaml 的 sum types。

---

### 8. 初始化列表 (Initializer List)

**C++11:**
```cpp
std::vector<int> vec = {1, 2, 3, 4, 5};
std::map<std::string, int> map = {
    {"apple", 1},
    {"banana", 2}
};

// 自定義類型
struct Point {
    int x, y;
};
Point p = {10, 20};
```

**Rust:**
```rust
let vec = vec![1, 2, 3, 4, 5];

use std::collections::HashMap;
let mut map = HashMap::new();
map.insert("apple", 1);
map.insert("banana", 2);

// 或使用宏
let map: HashMap<_, _> = [
    ("apple", 1),
    ("banana", 2),
].iter().cloned().collect();

// 結構體初始化
struct Point {
    x: i32,
    y: i32,
}
let p = Point { x: 10, y: 20 };
```

**說明:** Rust 使用 `vec![]` 宏來創建向量，結構體初始化語法類似但必須具名。

---

### 9. 右值引用與完美轉發

**C++11:**
```cpp
// 右值引用
void process(std::string&& s) {
    // s 是右值引用
}

// 完美轉發
template<typename T>
void wrapper(T&& arg) {
    process(std::forward<T>(arg));
}
```

**Rust:**
```rust
// Rust 沒有引用類別的區分
// 所有權系統自動處理

fn process(s: String) {
    // 接受所有權
}

fn process_ref(s: &String) {
    // 借用
}

// 泛型函數
fn wrapper<T>(arg: T) {
    // 根據需要傳遞所有權或借用
}
```

**說明:** Rust 的所有權系統簡化了這些概念，不需要區分左值/右值引用。

---

### 10. 可變參數模板 (Variadic Templates)

**C++11:**
```cpp
// 遞迴展開
template<typename T>
void print(T arg) {
    std::cout << arg << std::endl;
}

template<typename T, typename... Args>
void print(T first, Args... args) {
    std::cout << first << ", ";
    print(args...);
}

print(1, 2.5, "hello", 'c');
```

**Rust:**
```rust
// Rust 使用宏來處理可變參數
macro_rules! print_all {
    ($($arg:expr),*) => {
        $(
            println!("{:?}", $arg);
        )*
    };
}

print_all!(1, 2.5, "hello", 'c');

// 或使用 println! 內建宏
println!("{}, {}, {}, {}", 1, 2.5, "hello", 'c');
```

**說明:** Rust 使用宏系統處理可變參數，比 C++ 模板更直觀。

---

### 11. 靜態斷言 (static_assert)

**C++11:**
```cpp
static_assert(sizeof(int) == 4, "int must be 4 bytes");

template<typename T>
void func() {
    static_assert(std::is_integral<T>::value, "T must be integral");
}
```

**Rust:**
```rust
// 編譯期斷言
const _: () = assert!(std::mem::size_of::<i32>() == 4);

// 使用 trait bounds 限制型別
fn func<T: std::ops::Add>() {
    // T 必須實作 Add trait
}

// 或使用 where 子句
fn func2<T>() 
where
    T: std::ops::Add + Clone
{
    // T 必須實作 Add 和 Clone
}
```

**說明:** Rust 使用 trait bounds 來限制泛型，在編譯期就能檢查型別約束。

---

### 12. 預設和刪除函數

**C++11:**
```cpp
class MyClass {
public:
    MyClass() = default;  // 使用編譯器生成的預設建構子
    MyClass(const MyClass&) = delete;  // 禁止拷貝
    MyClass& operator=(const MyClass&) = delete;
};
```

**Rust:**
```rust
// Rust 預設不實作 Copy/Clone
struct MyStruct {
    data: i32,
}

// 需要明確標記才能複製
#[derive(Clone)]
struct Copyable {
    data: i32,
}

// 需要 Copy trait 才能隱式複製（只適用於簡單型別）
#[derive(Copy, Clone)]
struct SimpleCopy {
    data: i32,
}
```

**說明:** Rust 預設禁止複製，需要明確實作 `Clone` 或 `Copy` trait。

---

### 13. 委託建構子 (Delegating Constructors)

**C++11:**
```cpp
class Point {
    int x, y;
public:
    Point(int x, int y) : x(x), y(y) {}
    Point() : Point(0, 0) {}  // 委託給另一個建構子
};
```

**Rust:**
```rust
struct Point {
    x: i32,
    y: i32,
}

impl Point {
    fn new(x: i32, y: i32) -> Self {
        Point { x, y }
    }
    
    fn default() -> Self {
        Point::new(0, 0)  // 呼叫另一個建構函數
    }
}
```

**說明:** Rust 使用關聯函數模擬建構子，可以互相呼叫。

---

### 14. constexpr（編譯期計算）

**C++11:**
```cpp
constexpr int factorial(int n) {
    return n <= 1 ? 1 : n * factorial(n - 1);
}

constexpr int val = factorial(5);  // 編譯期計算
```

**Rust:**
```rust
const fn factorial(n: u32) -> u32 {
    if n <= 1 {
        1
    } else {
        n * factorial(n - 1)
    }
}

const VAL: u32 = factorial(5);  // 編譯期計算
```

**說明:** Rust 的 `const fn` 類似 C++ 的 `constexpr`，但限制更嚴格（逐漸放寬中）。

---

### 15. 執行緒支援

**C++11:**
```cpp
#include <thread>
#include <mutex>

std::mutex mtx;

void worker() {
    std::lock_guard<std::mutex> lock(mtx);
    // 臨界區
}

int main() {
    std::thread t1(worker);
    std::thread t2(worker);
    t1.join();
    t2.join();
}
```

**Rust:**
```rust
use std::sync::Mutex;
use std::thread;

fn main() {
    let mutex = Mutex::new(0);
    
    let handles: Vec<_> = (0..2).map(|_| {
        thread::spawn(move || {
            let mut data = mutex.lock().unwrap();
            *data += 1;
        })
    }).collect();
    
    for handle in handles {
        handle.join().unwrap();
    }
}
```

**說明:** Rust 的執行緒安全是**編譯期保證**的（通過 Send/Sync trait），C++ 只能在執行期檢查。

---

## C++14

### 1. 泛型 Lambda

**C++14:**
```cpp
auto lambda = [](auto x, auto y) { return x + y; };
std::cout << lambda(1, 2) << std::endl;      // 3
std::cout << lambda(1.5, 2.5) << std::endl;  // 4.0
```

**Rust:**
```rust
// Rust 需要明確型別，或使用 trait
fn add<T: std::ops::Add<Output = T>>(x: T, y: T) -> T {
    x + y
}

println!("{}", add(1, 2));      // 3
println!("{}", add(1.5, 2.5));  // 4.0

// 或使用閉包 + impl Trait (Rust 2018+)
fn make_adder() -> impl Fn(i32, i32) -> i32 {
    |x, y| x + y
}
```

**說明:** Rust 的泛型更明確，需要指定 trait bounds。

---

### 2. Lambda 捕獲表達式

**C++14:**
```cpp
int x = 10;
auto lambda = [y = x + 1](int z) { return y + z; };
```

**Rust:**
```rust
let x = 10;
let lambda = {
    let y = x + 1;
    move |z| y + z
};
```

**說明:** Rust 使用 `move` 關鍵字明確表示捕獲所有權。

---

### 3. 返回型別推導

**C++14:**
```cpp
auto add(int a, int b) {
    return a + b;  // 自動推導返回 int
}
```

**Rust:**
```rust
// Rust 一直都支援，但仍建議明確寫出
fn add(a: i32, b: i32) -> i32 {
    a + b
}

// 或使用型別推導（較少用）
fn add_auto(a: i32, b: i32) {
    a + b  // 錯誤！必須有返回型別
}
```

**說明:** Rust 強制函數簽名必須明確，但內部可以推導。

---

### 4. 變數模板 (Variable Templates)

**C++14:**
```cpp
template<typename T>
constexpr T pi = T(3.1415926535897932385);

std::cout << pi<float> << std::endl;
std::cout << pi<double> << std::endl;
```

**Rust:**
```rust
// Rust 使用 const 泛型
const fn pi<T>() -> f64 {
    3.1415926535897932385
}

// 或使用 trait
trait PI {
    const VALUE: Self;
}

impl PI for f32 {
    const VALUE: f32 = 3.14159265;
}

impl PI for f64 {
    const VALUE: f64 = 3.1415926535897932385;
}
```

**說明:** Rust 的常數泛型功能較新，但已經很強大。

---

### 5. Binary Literals

**C++14:**
```cpp
int binary = 0b1010'1100;  // 二進位字面值，分隔符
```

**Rust:**
```rust
let binary = 0b1010_1100;  // 二進位字面值，底線分隔
```

**說明:** 語法幾乎相同，只是分隔符不同。

---

## C++17

### 1. 結構化綁定 (Structured Bindings)

**C++17:**
```cpp
std::tuple<int, double, std::string> get_data() {
    return {42, 3.14, "hello"};
}

auto [i, d, s] = get_data();
std::cout << i << ", " << d << ", " << s << std::endl;

// 用於 map
std::map<std::string, int> map = {{"a", 1}, {"b", 2}};
for (const auto& [key, value] : map) {
    std::cout << key << ": " << value << std::endl;
}
```

**Rust:**
```rust
fn get_data() -> (i32, f64, String) {
    (42, 3.14, String::from("hello"))
}

let (i, d, s) = get_data();
println!("{}, {}, {}", i, d, s);

// 用於 HashMap
use std::collections::HashMap;
let map: HashMap<_, _> = [("a", 1), ("b", 2)].iter().cloned().collect();
for (key, value) in &map {
    println!("{}: {}", key, value);
}
```

**說明:** Rust 的模式匹配比 C++ 更強大，且一直都有此功能。

---

### 2. if/switch 初始化語句

**C++17:**
```cpp
if (auto it = map.find("key"); it != map.end()) {
    std::cout << it->second << std::endl;
}

switch (auto val = get_value(); val) {
    case 1: break;
    case 2: break;
}
```

**Rust:**
```rust
// if let 模式匹配
if let Some(value) = map.get("key") {
    println!("{}", value);
}

// match 初始化
match get_value() {
    1 => {},
    2 => {},
    _ => {},
}
```

**說明:** Rust 的 `if let` 和 `match` 更優雅，一直都有。

---

### 3. std::optional

**C++17:**
```cpp
#include <optional>

std::optional<int> find_value(bool exists) {
    if (exists) return 42;
    return std::nullopt;
}

auto result = find_value(true);
if (result.has_value()) {
    std::cout << result.value() << std::endl;
}
```

**Rust:**
```rust
fn find_value(exists: bool) -> Option<i32> {
    if exists {
        Some(42)
    } else {
        None
    }
}

let result = find_value(true);
if let Some(val) = result {
    println!("{}", val);
}

// 或使用 match
match result {
    Some(val) => println!("{}", val),
    None => println!("沒有值"),
}
```

**說明:** Rust 的 `Option<T>` 是核心型別，從一開始就有，且更安全。

---

### 4. std::variant

**C++17:**
```cpp
#include <variant>

std::variant<int, double, std::string> data;
data = 42;
data = 3.14;
data = "hello";

// 訪問
std::visit([](auto&& arg) {
    std::cout << arg << std::endl;
}, data);
```

**Rust:**
```rust
enum Data {
    Integer(i32),
    Float(f64),
    Text(String),
}

let data = Data::Integer(42);

// 訪問
match data {
    Data::Integer(i) => println!("{}", i),
    Data::Float(f) => println!("{}", f),
    Data::Text(s) => println!("{}", s),
}
```

**說明:** Rust 的 enum 更強大，是原生的 tagged union。

---

### 5. std::any

**C++17:**
```cpp
#include <any>

std::any data = 42;
data = std::string("hello");

if (data.type() == typeid(std::string)) {
    std::cout << std::any_cast<std::string>(data) << std::endl;
}
```

**Rust:**
```rust
use std::any::Any;

fn print_any(value: &dyn Any) {
    if let Some(s) = value.downcast_ref::<String>() {
        println!("String: {}", s);
    } else if let Some(i) = value.downcast_ref::<i32>() {
        println!("i32: {}", i);
    }
}

let data: Box<dyn Any> = Box::new(42);
print_any(&*data);
```

**說明:** Rust 的 `Any` trait 提供執行期型別資訊，但較少用（推薦用 enum）。

---

### 6. std::string_view

**C++17:**
```cpp
#include <string_view>

void process(std::string_view sv) {
    std::cout << sv << std::endl;
}

std::string s = "hello";
process(s);  // 不複製
process("world");  // 不複製
```

**Rust:**
```rust
fn process(s: &str) {
    println!("{}", s);
}

let s = String::from("hello");
process(&s);  // 字串切片，不複製
process("world");  // 字串字面值，不複製
```

**說明:** Rust 的 `&str` 一直都是字串切片，預設就是 zero-copy。

---

### 7. Fold Expressions（摺疊表達式）

**C++17:**
```cpp
template<typename... Args>
auto sum(Args... args) {
    return (args + ...);  // 一元右摺疊
}

std::cout << sum(1, 2, 3, 4, 5) << std::endl;  // 15
```

**Rust:**
```rust
// Rust 使用迭代器
fn sum(args: &[i32]) -> i32 {
    args.iter().sum()
}

println!("{}", sum(&[1, 2, 3, 4, 5]));  // 15

// 或使用宏
macro_rules! sum {
    ($($x:expr),*) => {
        0 $(+ $x)*
    };
}

println!("{}", sum!(1, 2, 3, 4, 5));
```

**說明:** Rust 傾向使用迭代器而非模板元編程。

---

### 8. inline 變數

**C++17:**
```cpp
// header.h
inline int global_var = 42;  // 多個編譯單元共享
```

**Rust:**
```rust
// Rust 沒有全域可變變數問題
// 使用靜態變數
static GLOBAL_VAR: i32 = 42;

// 需要可變性時使用 Mutex
use std::sync::Mutex;
static GLOBAL_MUT: Mutex<i32> = Mutex::new(42);
```

**說明:** Rust 的全域變數預設不可變，需要可變性時必須使用同步原語。

---

### 9. constexpr if

**C++17:**
```cpp
template<typename T>
auto get_value(T t) {
    if constexpr (std::is_integral_v<T>) {
        return t + 1;
    } else {
        return t + 0.1;
    }
}
```

**Rust:**
```rust
// Rust 使用 trait 和泛型
trait GetValue {
    type Output;
    fn get_value(self) -> Self::Output;
}

impl GetValue for i32 {
    type Output = i32;
    fn get_value(self) -> i32 {
        self + 1
    }
}

impl GetValue for f64 {
    type Output = f64;
    fn get_value(self) -> f64 {
        self + 0.1
    }
}
```

**說明:** Rust 使用 trait 系統實現編譯期多態。

---

### 10. Class Template Argument Deduction (CTAD)

**C++17:**
```cpp
std::pair p(1, 2.5);  // 推導為 std::pair<int, double>
std::vector v = {1, 2, 3};  // 推導為 std::vector<int>
```

**Rust:**
```rust
// Rust 一直都有型別推導
let p = (1, 2.5);  // (i32, f64)
let v = vec![1, 2, 3];  // Vec<i32>
```

**說明:** Rust 的型別推導更自然，不需要特殊語法。

---

## C++20

### 1. Concepts（概念）

**C++20:**
```cpp
#include <concepts>

template<typename T>
concept Addable = requires(T a, T b) {
    { a + b } -> std::convertible_to<T>;
};

template<Addable T>
T add(T a, T b) {
    return a + b;
}
```

**Rust:**
```rust
// Rust 的 trait 就是 concepts
trait Addable: std::ops::Add<Output = Self> + Sized {}

fn add<T: Addable>(a: T, b: T) -> T {
    a + b
}

// 或直接使用 trait bound
fn add2<T>(a: T, b: T) -> T
where
    T: std::ops::Add<Output = T>
{
    a + b
}
```

**說明:** Rust 的 trait 系統從一開始就有，比 C++20 的 concepts 更成熟。

---

### 2. Ranges（範圍庫）

**C++20:**
```cpp
#include <ranges>
#include <vector>

std::vector<int> vec = {1, 2, 3, 4, 5};

auto result = vec 
    | std::views::filter([](int x) { return x % 2 == 0; })
    | std::views::transform([](int x) { return x * 2; });

for (int x : result) {
    std::cout << x << " ";  // 4 8
}
```

**Rust:**
```rust
let vec = vec![1, 2, 3, 4, 5];

let result: Vec<_> = vec.iter()
    .filter(|&&x| x % 2 == 0)
    .map(|&x| x * 2)
    .collect();

println!("{:?}", result);  // [4, 8]
```

**說明:** Rust 的迭代器從一開始就有，且更優雅（零成本抽象）。

---

### 3. Coroutines（協程）

**C++20:**
```cpp
#include <coroutine>
#include <iostream>

struct Generator {
    struct promise_type {
        int current_value;
        auto get_return_object() { return Generator{this}; }
        auto initial_suspend() { return std::suspend_always{}; }
        auto final_suspend() noexcept { return std::suspend_always{}; }
        void return_void() {}
        void unhandled_exception() {}
        
        auto yield_value(int value) {
            current_value = value;
            return std::suspend_always{};
        }
    };
    
    std::coroutine_handle<promise_type> handle;
    
    Generator(promise_type* p) : handle(std::coroutine_handle<promise_type>::from_promise(*p)) {}
    ~Generator() { if (handle) handle.destroy(); }
};

Generator counter() {
    for (int i = 0; i < 5; ++i) {
        co_yield i;
    }
}
```

**Rust:**
```rust
// Rust 的 async/await 就是協程
async fn fetch_data(url: &str) -> String {
    // 模擬網路請求
    tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;
    format!("Data from {}", url)
}

// Generator 可以用迭代器實現
fn counter() -> impl Iterator<Item = i32> {
    (0..5)
}

// 或手動實現
struct Counter {
    count: i32,
}

impl Iterator for Counter {
    type Item = i32;
    
    fn next(&mut self) -> Option<i32> {
        if self.count < 5 {
            let result = self.count;
            self.count += 1;
            Some(result)
        } else {
            None
        }
    }
}
```

**說明:** 
- Rust 的 async/await 已經穩定（2019），比 C++20 早
- C++20 的協程很底層，需要手動實現 promise_type
- Rust 的 Generator trait 還在實驗階段

---

### 4. Modules（模組）

**C++20:**
```cpp
// math.cppm
export module math;

export int add(int a, int b) {
    return a + b;
}

// main.cpp
import math;

int main() {
    std::cout << add(1, 2) << std::endl;
}
```

**Rust:**
```rust
// math.rs
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

// main.rs
mod math;

fn main() {
    println!("{}", math::add(1, 2));
}
```

**說明:** Rust 從一開始就有現代化的模組系統，C++20 才加入（編譯器支援仍不完整）。

---

### 5. Three-way Comparison（太空船運算子 <=>）

**C++20:**
```cpp
#include <compare>

struct Point {
    int x, y;
    
    auto operator<=>(const Point&) const = default;
};

Point p1{1, 2}, p2{1, 3};
if (p1 < p2) { /* ... */ }
```

**Rust:**
```rust
#[derive(PartialOrd, Ord, PartialEq, Eq)]
struct Point {
    x: i32,
    y: i32,
}

let p1 = Point { x: 1, y: 2 };
let p2 = Point { x: 1, y: 3 };

if p1 < p2 { /* ... */ }
```

**說明:** Rust 使用 derive 宏自動實作比較 trait，更簡潔。

---

### 6. constexpr 虛擬函數

**C++20:**
```cpp
struct Base {
    virtual constexpr int get() const { return 1; }
};

struct Derived : Base {
    constexpr int get() const override { return 2; }
};

constexpr int value = Derived{}.get();  // 編譯期計算
```

**Rust:**
```rust
// Rust 的 const fn 不支援 trait objects
// 但可以用泛型 + trait
trait GetValue {
    fn get(&self) -> i32;
}

struct Base;
impl GetValue for Base {
    fn get(&self) -> i32 { 1 }
}

struct Derived;
impl GetValue for Derived {
    fn get(&self) -> i32 { 2 }
}

// 編譯期計算
const fn get_static() -> i32 {
    2  // 必須是具體型別
}
```

**說明:** Rust 的 const fn 限制較嚴格，不支援動態分派。

---

### 7. constinit

**C++20:**
```cpp
constinit int global = 42;  // 保證編譯期初始化
```

**Rust:**
```rust
// Rust 的 static 預設就是編譯期初始化
static GLOBAL: i32 = 42;

// const 也是編譯期計算
const CONST_VAL: i32 = 42;
```

**說明:** Rust 的靜態變數預設就是編譯期初始化，不需要特殊關鍵字。

---

### 8. std::span

**C++20:**
```cpp
#include <span>

void process(std::span<int> data) {
    for (int x : data) {
        std::cout << x << " ";
    }
}

std::vector<int> vec = {1, 2, 3};
int arr[] = {4, 5, 6};

process(vec);
process(arr);
```

**Rust:**
```rust
fn process(data: &[i32]) {
    for x in data {
        print!("{} ", x);
    }
}

let vec = vec![1, 2, 3];
let arr = [4, 5, 6];

process(&vec);
process(&arr);
```

**說明:** Rust 的切片 `&[T]` 從一開始就有，且更安全。

---

### 9. format 格式化

**C++20:**
```cpp
#include <format>

std::string s = std::format("Hello, {}! The answer is {}.", "world", 42);
```

**Rust:**
```rust
let s = format!("Hello, {}! The answer is {}.", "world", 42);
```

**說明:** Rust 的 `format!` 宏一直都有，且編譯期檢查格式字串。

---

### 10. std::source_location

**C++20:**
```cpp
#include <source_location>

void log(std::string_view message, 
         const std::source_location& location = std::source_location::current()) {
    std::cout << location.file_name() << ":" << location.line() << " - " << message << std::endl;
}
```

**Rust:**
```rust
// Rust 使用宏獲取位置資訊
macro_rules! log {
    ($msg:expr) => {
        println!("{}:{} - {}", file!(), line!(), $msg);
    };
}

log!("Hello");
```

**說明:** Rust 使用宏在編譯期捕獲位置資訊。

---

## C++23

### 1. std::expected

**C++23:**
```cpp
#include <expected>

std::expected<int, std::string> divide(int a, int b) {
    if (b == 0) {
        return std::unexpected("除以零錯誤");
    }
    return a / b;
}

auto result = divide(10, 2);
if (result) {
    std::cout << "結果: " << *result << std::endl;
} else {
    std::cout << "錯誤: " << result.error() << std::endl;
}
```

**Rust:**
```rust
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err(String::from("除以零錯誤"))
    } else {
        Ok(a / b)
    }
}

let result = divide(10, 2);
match result {
    Ok(val) => println!("結果: {}", val),
    Err(e) => println!("錯誤: {}", e),
}

// 或使用 ? 運算子
fn compute() -> Result<i32, String> {
    let result = divide(10, 2)?;  // 自動傳播錯誤
    Ok(result * 2)
}
```

**說明:** Rust 的 `Result<T, E>` 從一開始就有，且有 `?` 運算子簡化錯誤處理。

---

### 2. std::print / std::println

**C++23:**
```cpp
#include <print>

std::print("Hello, {}!\n", "world");
std::println("The answer is {}", 42);
```

**Rust:**
```rust
print!("Hello, {}!\n", "world");
println!("The answer is {}", 42);
```

**說明:** Rust 一直都有 `print!` 和 `println!` 宏，且編譯期檢查。

---

### 3. Deducing this（顯式物件參數）

**C++23:**
```cpp
struct MyClass {
    void func(this MyClass& self) {  // 顯式 self
        // ...
    }
    
    void func_by_value(this MyClass self) {  // 按值傳遞
        // ...
    }
};
```

**Rust:**
```rust
struct MyClass {
    data: i32,
}

impl MyClass {
    fn func(&self) {  // 不可變借用
        // ...
    }
    
    fn func_mut(&mut self) {  // 可變借用
        // ...
    }
    
    fn func_by_value(self) {  // 按值傳遞（移動）
        // ...
    }
}
```

**說明:** Rust 從一開始就有顯式 `self` 參數，且強制明確借用類型。

---

### 4. if consteval

**C++23:**
```cpp
constexpr int func() {
    if consteval {
        return 1;  // 編譯期執行
    } else {
        return 2;  // 執行期執行
    }
}
```

**Rust:**
```rust
// Rust 沒有直接對應，但可以用條件編譯
const fn func_const() -> i32 {
    1
}

fn func_runtime() -> i32 {
    2
}

// 使用者根據需要選擇
const VAL: i32 = func_const();
```

**說明:** Rust 的 const fn 和普通函數分離更明確。

---

### 5. Multidimensional subscript operator

**C++23:**
```cpp
struct Matrix {
    int operator[](int i, int j) {  // 多維下標
        return data[i][j];
    }
    
    int data[10][10];
};

Matrix m;
int val = m[3, 4];  // 使用逗號
```

**Rust:**
```rust
struct Matrix {
    data: [[i32; 10]; 10],
}

impl std::ops::Index<(usize, usize)> for Matrix {
    type Output = i32;
    
    fn index(&self, (i, j): (usize, usize)) -> &i32 {
        &self.data[i][j]
    }
}

let m = Matrix { data: [[0; 10]; 10] };
let val = m[(3, 4)];  // 使用 tuple
```

**說明:** Rust 使用 tuple 作為索引，更明確。

---

### 6. std::flat_map / std::flat_set

**C++23:**
```cpp
#include <flat_map>

std::flat_map<int, std::string> map;
map[1] = "one";
map[2] = "two";
```

**Rust:**
```rust
// Rust 標準庫沒有 flat_map
// 但可以用 BTreeMap（類似功能）
use std::collections::BTreeMap;

let mut map = BTreeMap::new();
map.insert(1, "one");
map.insert(2, "two");

// 或使用第三方庫如 indexmap
```

**說明:** Rust 的 `BTreeMap` 提供排序的 map，類似 flat_map 的性能特性。

---

### 7. std::mdspan

**C++23:**
```cpp
#include <mdspan>

int data[12];
std::mdspan<int, std::dextents<size_t, 2>> matrix(data, 3, 4);
matrix[1, 2] = 42;
```

**Rust:**
```rust
// Rust 使用第三方庫如 ndarray
use ndarray::Array2;

let mut matrix = Array2::<i32>::zeros((3, 4));
matrix[(1, 2)] = 42;

// 或手動實現
struct Matrix {
    data: Vec<i32>,
    rows: usize,
    cols: usize,
}

impl Matrix {
    fn get(&self, i: usize, j: usize) -> &i32 {
        &self.data[i * self.cols + j]
    }
}
```

**說明:** Rust 生態系統中有成熟的多維陣列庫。

---

### 8. std::stacktrace

**C++23:**
```cpp
#include <stacktrace>

void func() {
    std::cout << std::stacktrace::current() << std::endl;
}
```

**Rust:**
```rust
// Rust 使用 backtrace crate
use backtrace::Backtrace;

fn func() {
    let bt = Backtrace::new();
    println!("{:?}", bt);
}

// Panic 時自動顯示 backtrace
// RUST_BACKTRACE=1 cargo run
```

**說明:** Rust 的 backtrace 功能已經很成熟（第三方庫）。

---

### 9. Literal suffix for size_t

**C++23:**
```cpp
auto size = 42uz;  // size_t 字面值
auto ssize = 42z;  // ssize_t 字面值
```

**Rust:**
```rust
let size: usize = 42;
let ssize: isize = 42;

// Rust 沒有字面值後綴，但型別推導通常足夠
```

**說明:** Rust 依賴型別推導，較少需要字面值後綴。

---

### 10. std::generator (預計)

**C++23:**
```cpp
#include <generator>

std::generator<int> fibonacci() {
    int a = 0, b = 1;
    while (true) {
        co_yield a;
        int next = a + b;
        a = b;
        b = next;
    }
}
```

**Rust:**
```rust
// Rust 的 Generator trait 還在實驗階段
// 但可以用迭代器
fn fibonacci() -> impl Iterator<Item = i32> {
    let mut a = 0;
    let mut b = 1;
    std::iter::from_fn(move || {
        let current = a;
        let next = a + b;
        a = b;
        b = next;
        Some(current)
    })
}

// 使用
for num in fibonacci().take(10) {
    println!("{}", num);
}
```

**說明:** Rust 的迭代器提供類似功能，Generator trait 正在開發中。

---

## 總結

### Rust 已經有的功能（甚至更好）

| C++ 功能 | Rust 對應 | 優勢 |
|---------|----------|------|
| Move semantics | 所有權系統 | 預設行為，編譯器強制檢查 |
| Smart pointers | Box, Rc, Arc | 更明確的單/多執行緒區分 |
| nullptr | Option<T> | 型別系統強制處理，無 null pointer |
| Lambda | 閉包 | 自動捕獲，更簡潔 |
| Range-based for | for in | 強制明確借用類型 |
| Concepts | Trait 系統 | 更成熟，從一開始就有 |
| Ranges | Iterator | 零成本抽象，更優雅 |
| optional | Option<T> | 核心型別，模式匹配 |
| variant | Enum | 更強大的代數資料型別 |
| string_view | &str | 預設 zero-copy |
| expected | Result<T, E> | 有 ? 運算子簡化錯誤處理 |
| Modules | mod 系統 | 從一開始就有，更成熟 |
| Coroutines | async/await | 更早穩定，生態系統成熟 |

### C++ 特有或更強的功能

| 功能 | 說明 |
|------|------|
| Template metaprogramming | C++ 的模板元編程更靈活 |
| constexpr 的廣度 | C++20/23 的編譯期計算能力更廣 |
| 多重繼承 | Rust 沒有繼承，用 trait 組合 |
| 操作符重載靈活性 | C++ 更自由（也更危險） |
| 與 C 的無縫互操作 | C++ 天生兼容 C |

### 關鍵差異總結

1. **設計哲學**
   - C++: 向後兼容，功能不斷疊加
   - Rust: 從零開始，一致性優先

2. **安全性**
   - C++: 執行期檢查（或無檢查）
   - Rust: 編譯期保證記憶體安全

3. **學習曲線**
   - C++: 語法複雜，陷阱多
   - Rust: 前期陡峭，但之後更平穩

4. **生態系統**
   - C++: 成熟但碎片化
   - Rust: 現代化工具鏈（Cargo），快速成長

5. **性能**
   - 兩者都提供零成本抽象，性能相當

### 結論

Rust 並非「追趕」C++，而是從一開始就選擇了不同的道路。很多 C++11-23 才加入的功能，Rust 在設計之初就內建了更優雅的解決方案。C++ 的優勢在於成熟的生態系統和極致的靈活性，而 Rust 的優勢在於編譯期安全保證和現代化的語言設計。

選擇哪個語言取決於：
- **專案需求**: 需要與 C/C++ 生態整合？選 C++
- **團隊背景**: 團隊已經熟悉 C++？或願意投資學習 Rust？
- **安全要求**: 對記憶體安全有嚴格要求？選 Rust
- **開發效率**: 想要更好的工具鏈和包管理？選 Rust

兩者都是優秀的系統程式語言，可以根據實際情況選擇！
