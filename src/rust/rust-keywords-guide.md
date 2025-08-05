# Rust 保留關鍵字完整範例指南

## 關鍵字總覽

### 完整涵蓋的關鍵字類別：
- **變數與常數**：`let`, `const`, `static`, `mut`
- **函數與控制流**：`fn`, `return`, `if`, `else`, `match`
- **循環結構**：`loop`, `while`, `for`, `break`, `continue`
- **類型定義**：`struct`, `enum`, `union`, `type`
- **特徵與實現**：`trait`, `impl`
- **模組系統**：`mod`, `pub`, `use`, `crate`, `super`, `self`
- **引用模式**：`ref`
- **異步編程**：`async`, `await`
- **類型約束與轉換**：`where`, `as`
- **安全性**：`unsafe`
- **外部接口**：`extern`
- **所有權與移動**：`move`
- **迭代**：`in`
- **模式匹配**：`_`

---

## 1. 變數與常數

### `let` - 變數綁定
```rust
fn main() {
    let x = 5;              // 不可變變數
    let mut y = 10;         // 可變變數
    y = 20;                 // 可以修改
    println!("x={}, y={}", x, y);
}
```

### `const` - 編譯時常數
```rust
const PI: f64 = 3.14159;
const MAX_USERS: usize = 1000;

fn main() {
    println!("PI = {}", PI);
    println!("最大用戶數: {}", MAX_USERS);
}
```

### `static` - 全域靜態變數
```rust
static LANGUAGE: &str = "Rust";
static mut COUNTER: i32 = 0;

fn main() {
    println!("語言: {}", LANGUAGE);
    
    unsafe {
        COUNTER += 1;
        println!("計數器: {}", COUNTER);
    }
}
```

### `mut` - 可變性修飾符
```rust
fn main() {
    let mut score = 0;
    println!("初始分數: {}", score);
    
    score += 10;
    println!("更新分數: {}", score);
}
```

## 2. 函數與控制流

### `fn` - 函數定義
```rust
fn greet(name: &str) {
    println!("你好, {}!", name);
}

fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    greet("小明");
    let result = add(5, 3);
    println!("5 + 3 = {}", result);
}
```

### `return` - 提前返回
```rust
fn check_age(age: i32) -> String {
    if age < 0 {
        return "年齡不能為負數".to_string();
    }
    if age > 150 {
        return "年齡過大".to_string();
    }
    "年齡正常".to_string()
}

fn main() {
    println!("{}", check_age(25));
    println!("{}", check_age(-5));
}
```

### `if` / `else` - 條件判斷
```rust
fn main() {
    let temperature = 25;
    
    if temperature > 30 {
        println!("天氣很熱");
    } else if temperature > 20 {
        println!("天氣溫暖");
    } else {
        println!("天氣涼爽");
    }
    
    // if 表達式
    let weather = if temperature > 25 { "熱" } else { "涼" };
    println!("天氣: {}", weather);
}
```

### `match` - 模式匹配
```rust
enum Direction {
    Up,
    Down,
    Left,
    Right,
}

fn main() {
    let dir = Direction::Up;
    
    match dir {
        Direction::Up => println!("向上"),
        Direction::Down => println!("向下"),
        Direction::Left => println!("向左"),
        Direction::Right => println!("向右"),
    }
    
    let number = 3;
    match number {
        1 => println!("一"),
        2 => println!("二"),
        3 => println!("三"),
        _ => println!("其他數字"),
    }
}
```

## 3. 循環

### `loop` - 無限循環
```rust
fn main() {
    let mut count = 0;
    
    loop {
        count += 1;
        println!("計數: {}", count);
        
        if count >= 3 {
            break;
        }
    }
    
    // 帶返回值的 loop
    let result = loop {
        count += 1;
        if count > 5 {
            break count * 2;
        }
    };
    println!("結果: {}", result);
}
```

### `while` - 條件循環
```rust
fn main() {
    let mut number = 3;
    
    while number > 0 {
        println!("倒數: {}", number);
        number -= 1;
    }
    println!("發射!");
    
    // while let 模式
    let mut stack = vec![1, 2, 3];
    while let Some(top) = stack.pop() {
        println!("彈出: {}", top);
    }
}
```

### `for` - 迭代循環
```rust
fn main() {
    // 範圍迭代
    for i in 1..=5 {
        println!("數字: {}", i);
    }
    
    // 集合迭代
    let fruits = vec!["蘋果", "香蕉", "橘子"];
    for fruit in fruits {
        println!("水果: {}", fruit);
    }
    
    // 帶索引的迭代
    let colors = vec!["紅", "綠", "藍"];
    for (index, color) in colors.iter().enumerate() {
        println!("顏色 {}: {}", index, color);
    }
}
```

### `break` / `continue` - 循環控制
```rust
fn main() {
    // break 示例
    for i in 1..10 {
        if i == 5 {
            break;
        }
        println!("數字: {}", i);
    }
    
    // continue 示例
    for i in 1..6 {
        if i == 3 {
            continue;
        }
        println!("處理: {}", i);
    }
    
    // 標籤式 break
    'outer: for i in 1..4 {
        for j in 1..4 {
            if i == 2 && j == 2 {
                break 'outer;
            }
            println!("i={}, j={}", i, j);
        }
    }
}
```

## 4. 類型與結構

### `struct` - 結構體
```rust
struct Person {
    name: String,
    age: u32,
    email: String,
}

struct Point(i32, i32); // 元組結構體

struct Unit; // 單元結構體

fn main() {
    let person = Person {
        name: String::from("張三"),
        age: 25,
        email: String::from("zhang@example.com"),
    };
    
    println!("姓名: {}", person.name);
    println!("年齡: {}", person.age);
    
    let point = Point(10, 20);
    println!("座標: ({}, {})", point.0, point.1);
    
    let _unit = Unit;
}
```

### `enum` - 枚舉
```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}

enum Option<T> {
    Some(T),
    None,
}

fn main() {
    let msg1 = Message::Quit;
    let msg2 = Message::Move { x: 10, y: 20 };
    let msg3 = Message::Write(String::from("Hello"));
    let msg4 = Message::ChangeColor(255, 0, 0);
    
    match msg2 {
        Message::Quit => println!("退出"),
        Message::Move { x, y } => println!("移動到 ({}, {})", x, y),
        Message::Write(text) => println!("寫入: {}", text),
        Message::ChangeColor(r, g, b) => println!("顏色: RGB({}, {}, {})", r, g, b),
    }
}
```

### `union` - 聯合體
```rust
union MyUnion {
    i: i32,
    f: f32,
}

fn main() {
    let mut u = MyUnion { i: 42 };
    
    unsafe {
        println!("整數值: {}", u.i);
        u.f = 3.14;
        println!("浮點值: {}", u.f);
    }
}
```

### `type` - 類型別名
```rust
type UserId = u64;
type Result<T> = std::result::Result<T, String>;
type Point = (i32, i32);

fn get_user_id() -> UserId {
    12345
}

fn divide(a: f64, b: f64) -> Result<f64> {
    if b == 0.0 {
        Err("除零錯誤".to_string())
    } else {
        Ok(a / b)
    }
}

fn main() {
    let id = get_user_id();
    println!("用戶 ID: {}", id);
    
    let point: Point = (10, 20);
    println!("點: ({}, {})", point.0, point.1);
    
    match divide(10.0, 2.0) {
        Ok(result) => println!("結果: {}", result),
        Err(error) => println!("錯誤: {}", error),
    }
}
```

## 5. 特徵與實現

### `trait` - 特徵定義
```rust
trait Drawable {
    fn draw(&self);
    fn area(&self) -> f64;
}

trait Printable {
    fn print(&self) {
        println!("正在打印...");
    }
}

struct Circle {
    radius: f64,
}

struct Rectangle {
    width: f64,
    height: f64,
}

fn main() {
    let circle = Circle { radius: 5.0 };
    let rect = Rectangle { width: 4.0, height: 6.0 };
    
    circle.draw();
    rect.draw();
    
    println!("圓形面積: {}", circle.area());
    println!("矩形面積: {}", rect.area());
}
```

### `impl` - 實現
```rust
struct Calculator {
    value: f64,
}

trait Math {
    fn add(&mut self, x: f64);
    fn multiply(&mut self, x: f64);
}

impl Calculator {
    fn new() -> Self {
        Calculator { value: 0.0 }
    }
    
    fn get_value(&self) -> f64 {
        self.value
    }
}

impl Math for Calculator {
    fn add(&mut self, x: f64) {
        self.value += x;
    }
    
    fn multiply(&mut self, x: f64) {
        self.value *= x;
    }
}

fn main() {
    let mut calc = Calculator::new();
    calc.add(10.0);
    calc.multiply(2.0);
    println!("計算結果: {}", calc.get_value());
}
```

## 6. 模組與可見性

### `mod` - 模組定義
```rust
mod math {
    pub fn add(a: i32, b: i32) -> i32 {
        a + b
    }
    
    fn private_function() {
        println!("私有函數");
    }
    
    pub mod advanced {
        pub fn power(base: i32, exp: u32) -> i32 {
            base.pow(exp)
        }
    }
}

fn main() {
    let result = math::add(5, 3);
    println!("5 + 3 = {}", result);
    
    let power_result = math::advanced::power(2, 3);
    println!("2^3 = {}", power_result);
}
```

### `pub` - 公開可見性
```rust
pub struct PublicStruct {
    pub public_field: i32,
    private_field: String,
}

impl PublicStruct {
    pub fn new(value: i32) -> Self {
        PublicStruct {
            public_field: value,
            private_field: String::from("私有"),
        }
    }
    
    pub fn get_private(&self) -> &str {
        &self.private_field
    }
}

fn main() {
    let mut s = PublicStruct::new(42);
    s.public_field = 100; // 可以直接訪問
    println!("公開欄位: {}", s.public_field);
    println!("私有欄位: {}", s.get_private());
}
```

### `use` - 引入項目
```rust
use std::collections::HashMap;
use std::fs::File;
use std::io::prelude::*;

mod utilities {
    pub fn helper() {
        println!("輔助函數");
    }
}

use utilities::helper;

fn main() {
    let mut map = HashMap::new();
    map.insert("key", "value");
    println!("HashMap: {:?}", map);
    
    helper();
}
```

### `crate` - 當前 crate 根
```rust
mod my_module {
    pub fn public_function() {
        println!("公共函數");
    }
}

fn main() {
    // 使用 crate 關鍵字從根開始引用
    crate::my_module::public_function();
}
```

### `super` - 父模組
```rust
fn parent_function() {
    println!("父模組函數");
}

mod child_module {
    pub fn call_parent() {
        super::parent_function(); // 調用父模組函數
    }
    
    mod grandchild {
        pub fn call_grandparent() {
            super::super::parent_function(); // 調用祖父模組函數
        }
    }
}

fn main() {
    child_module::call_parent();
    child_module::grandchild::call_grandparent();
}
```

### `self` - 當前模組或實例
```rust
mod my_module {
    pub fn function() {
        println!("模組函數");
    }
    
    pub fn call_self() {
        self::function(); // 調用當前模組的函數
    }
}

struct MyStruct {
    value: i32,
}

impl MyStruct {
    fn new(value: i32) -> Self { // Self 指向 MyStruct
        MyStruct { value }
    }
    
    fn get_value(&self) -> i32 { // &self 指向實例
        self.value
    }
    
    fn set_value(&mut self, value: i32) { // &mut self 指向可變實例
        self.value = value;
    }
}

fn main() {
    my_module::call_self();
    
    let mut obj = MyStruct::new(42);
    println!("值: {}", obj.get_value());
    obj.set_value(100);
    println!("新值: {}", obj.get_value());
}
```

## 7. 引用與模式

### `ref` - 引用模式
```rust
fn main() {
    let x = 5;
    
    match x {
        ref r => println!("通過引用: {}", r), // r 是 &i32
    }
    
    let tuple = (1, 2);
    match tuple {
        (ref a, ref b) => println!("引用: {} 和 {}", a, b),
    }
    
    // 與 & 的區別
    let y = &10;
    match y {
        &val => println!("解引用後的值: {}", val),
    }
}
```

## 8. 異步編程

### `async` / `await` - 異步編程
```rust
use std::time::Duration;

async fn fetch_data(id: u32) -> String {
    // 模擬異步操作
    tokio::time::sleep(Duration::from_millis(100)).await;
    format!("數據-{}", id)
}

async fn process_data() -> Vec<String> {
    let mut results = Vec::new();
    
    for i in 1..=3 {
        let data = fetch_data(i).await;
        results.push(data);
    }
    
    results
}

#[tokio::main]
async fn main() {
    let results = process_data().await;
    for result in results {
        println!("處理完成: {}", result);
    }
}
```

## 9. 其他重要關鍵字

### `where` - 類型約束
```rust
use std::fmt::Debug;

fn print_if_positive<T>(value: T) 
where 
    T: PartialOrd<i32> + Debug,
{
    if value > 0 {
        println!("正數: {:?}", value);
    } else {
        println!("非正數: {:?}", value);
    }
}

fn main() {
    print_if_positive(5);
    print_if_positive(-3);
    print_if_positive(2.5);
}
```

### `unsafe` - 不安全代碼
```rust
fn main() {
    let mut num = 5;
    let r1 = &num as *const i32;
    let r2 = &mut num as *mut i32;
    
    unsafe {
        println!("r1 指向: {}", *r1);
        *r2 = 10;
        println!("修改後 r1 指向: {}", *r1);
    }
    
    // 調用不安全函數
    unsafe {
        dangerous_function();
    }
}

unsafe fn dangerous_function() {
    println!("這是不安全函數");
}
```

### `extern` - 外部函數接口
```rust
// 聲明外部 C 函數
extern "C" {
    fn abs(input: i32) -> i32;
}

// Rust 函數提供給 C 調用
#[no_mangle]
pub extern "C" fn add_numbers(a: i32, b: i32) -> i32 {
    a + b
}

fn main() {
    unsafe {
        let result = abs(-42);
        println!("絕對值: {}", result);
    }
}
```

### `as` - 類型轉換
```rust
fn main() {
    // 數值轉換
    let x: i32 = 10;
    let y: f64 = x as f64;
    println!("i32 {} 轉為 f64 {}", x, y);
    
    // 指針轉換
    let ptr = &x as *const i32;
    println!("指針地址: {:p}", ptr);
    
    // 字符轉換
    let c = 'A';
    let ascii = c as u8;
    println!("字符 '{}' 的 ASCII 值: {}", c, ascii);
    
    // 枚舉轉換
    enum Number {
        Zero = 0,
        One = 1,
        Two = 2,
    }
    
    let num = Number::Two as i32;
    println!("枚舉值: {}", num);
}
```

### `move` - 移動語義
```rust
fn main() {
    let name = String::from("小明");
    
    // 移動捕獲
    let greeting = move || {
        println!("你好, {}!", name); // name 被移動到閉包中
    };
    
    greeting();
    // println!("{}", name); // 錯誤：name 已被移動
    
    // 在線程中使用 move
    let data = vec![1, 2, 3, 4, 5];
    let handle = std::thread::spawn(move || {
        println!("線程中的數據: {:?}", data);
    });
    
    handle.join().unwrap();
}
```

### `in` - 用於 for 循環
```rust
fn main() {
    let numbers = vec![1, 2, 3, 4, 5];
    
    // 標準用法
    for num in numbers.iter() {
        println!("數字: {}", num);
    }
    
    // 範圍用法
    for i in 0..5 {
        println!("索引: {}", i);
    }
    
    // 字符串迭代
    let text = "Hello";
    for ch in text.chars() {
        println!("字符: {}", ch);
    }
}
```

## 10. 模式匹配特殊用法

### `_` - 忽略模式
```rust
fn main() {
    let tuple = (1, 2, 3);
    
    match tuple {
        (1, _, _) => println!("第一個元素是 1"),
        (_, 2, _) => println!("第二個元素是 2"),
        _ => println!("其他情況"),
    }
    
    // 忽略函數返回值
    let _ = some_function();
    
    // 忽略 Result 的錯誤
    let _result = "42".parse::<i32>();
}

fn some_function() -> i32 {
    42
}
```

這個完整的範例指南涵蓋了 Rust 中所有重要的保留關鍵字，每個都配有實際可運行的代碼示例，幫助你理解每個關鍵字的具體用法和應用場景。