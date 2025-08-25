# Rust 標準庫完整執行範例

## 1. Vec - 動態陣列

```rust
fn main() {
    // 創建空的 Vec
    let mut numbers = Vec::new();
    numbers.push(10);
    numbers.push(20);
    numbers.push(30);
    println!("Vec: {:?}
```

## 17. 排序和比較

```rust
use std::cmp::Ordering;

#[derive(Debug, Eq, PartialEq, Clone)]
struct Person {
    name: String,
    age: u32,
}

// 自定義排序
impl Ord for Person {
    fn cmp(&self, other: &Self) -> Ordering {
        self.age.cmp(&other.age)
    }
}

impl PartialOrd for Person {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

fn main() {
    // 基本排序
    println!("=== 基本排序 ===");
    let mut numbers = vec![3, 1, 4, 1, 5, 9, 2, 6];
    println!("原始: {:?}", numbers);
    
    numbers.sort();
    println!("升序: {:?}", numbers);
    
    numbers.sort_by(|a, b| b.cmp(a));
    println!("降序: {:?}", numbers);
    
    // 浮點數排序 (需要特別處理)
    let mut floats = vec![3.5, 1.2, 4.7, 2.3];
    floats.sort_by(|a, b| a.partial_cmp(b).unwrap());
    println!("\n浮點數排序: {:?}", floats);
    
    // sort_by_key
    let mut words = vec!["apple", "pie", "zoo", "cat"];
    words.sort_by_key(|s| s.len());
    println!("\n按長度排序: {:?}", words);
    
    // 穩定排序 vs 不穩定排序
    let mut data = vec![(1, "a"), (1, "b"), (2, "c"), (1, "d")];
    data.sort_by_key(|k| k.0); // 穩定排序
    println!("\n穩定排序: {:?}", data);
    
    // 自定義結構排序
    let mut people = vec![
        Person { name: "Alice".to_string(), age: 25 },
        Person { name: "Bob".to_string(), age: 30 },
        Person { name: "Charlie".to_string(), age: 20 },
    ];
    
    println!("\n=== 結構體排序 ===");
    println!("原始: {:?}", people);
    
    people.sort();
    println!("按年齡: {:?}", people);
    
    people.sort_by_key(|p| p.name.clone());
    println!("按名字: {:?}", people);
    
    // 複合排序
    let mut students = vec![
        ("Alice", 85),
        ("Bob", 90),
        ("Charlie", 85),
        ("David", 95),
    ];
    
    students.sort_by(|a, b| {
        // 先按分數降序，分數相同則按名字升序
        b.1.cmp(&a.1).then(a.0.cmp(&b.0))
    });
    println!("\n複合排序: {:?}", students);
    
    // 比較操作
    println!("\n=== 比較操作 ===");
    let a = 5;
    let b = 10;
    
    match a.cmp(&b) {
        Ordering::Less => println!("{} < {}", a, b),
        Ordering::Greater => println!("{} > {}", a, b),
        Ordering::Equal => println!("{} = {}", a, b),
    }
    
    // max 和 min
    println!("\n最大值: {}", std::cmp::max(10, 20));
    println!("最小值: {}", std::cmp::min(10, 20));
    
    let numbers = vec![3, 7, 2, 9, 1];
    let max = numbers.iter().max().unwrap();
    let min = numbers.iter().min().unwrap();
    println!("陣列最大值: {}", max);
    println!("陣列最小值: {}", min);
    
    // clamp - 限制範圍
    let value = 15;
    let clamped = value.clamp(5, 10);
    println!("\n{} 限制在 5-10: {}", value, clamped);
    
    // 二分搜尋 (需要先排序)
    let mut sorted = vec![1, 3, 5, 7, 9, 11, 13];
    println!("\n=== 二分搜尋 ===");
    println!("陣列: {:?}", sorted);
    
    match sorted.binary_search(&7) {
        Ok(index) => println!("找到 7 在索引: {}", index),
        Err(index) => println!("沒找到，應該插入在索引: {}", index),
    }
    
    match sorted.binary_search(&8) {
        Ok(index) => println!("找到 8 在索引: {}", index),
        Err(index) => println!("沒找到 8，應該插入在索引: {}", index),
    }
    
    // partition - 分割
    let numbers = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    let (evens, odds): (Vec<_>, Vec<_>) = numbers
        .into_iter()
        .partition(|n| n % 2 == 0);
    
    println!("\n=== 分割 ===");
    println!("偶數: {:?}", evens);
    println!("奇數: {:?}", odds);
    
    // 自定義比較函數
    fn compare_ignore_case(a: &str, b: &str) -> Ordering {
        a.to_lowercase().cmp(&b.to_lowercase())
    }
    
    let mut names = vec!["alice", "Bob", "CHARLIE", "david"];
    names.sort_by(|a, b| compare_ignore_case(a, b));
    println!("\n忽略大小寫排序: {:?}", names);
    
    // 反轉
    let mut nums = vec![1, 2, 3, 4, 5];
    nums.reverse();
    println!("\n反轉: {:?}", nums);
    
    // is_sorted (需要 nightly 或自己實作)
    let sorted = vec![1, 2, 3, 4, 5];
    let unsorted = vec![1, 3, 2, 4, 5];
    
    let is_sorted = |slice: &[i32]| {
        slice.windows(2).all(|w| w[0] <= w[1])
    };
    
    println!("\n{:?} 已排序: {}", sorted, is_sorted(&sorted));
    println!("{:?} 已排序: {}", unsorted, is_sorted(&unsorted));
}
```

## 18. Box, Rc, RefCell - 智慧指標

```rust
use std::rc::{Rc, Weak};
use std::cell::RefCell;

// 遞迴類型需要 Box
#[derive(Debug)]
enum List {
    Cons(i32, Box<List>),
    Nil,
}

// 樹結構使用 Rc 和 RefCell
#[derive(Debug)]
struct Node {
    value: i32,
    children: RefCell<Vec<Rc<Node>>>,
    parent: RefCell<Weak<Node>>,
}

fn main() {
    // Box - 堆分配
    println!("=== Box 智慧指標 ===");
    let b = Box::new(5);
    println!("Box 值: {}", b);
    println!("解引用: {}", *b);
    
    // Box 用於遞迴類型
    use List::{Cons, Nil};
    let list = Cons(1, 
        Box::new(Cons(2, 
            Box::new(Cons(3, 
                Box::new(Nil))))));
    println!("遞迴列表: {:?}", list);
    
    // Box 用於大型資料
    let large_array = Box::new([0; 1000]);
    println!("大陣列第一個元素: {}", large_array[0]);
    
    // Rc - 引用計數
    println!("\n=== Rc 引用計數 ===");
    let a = Rc::new(String::from("Hello"));
    println!("計數: {}", Rc::strong_count(&a));
    
    {
        let b = Rc::clone(&a);
        println!("clone 後計數: {}", Rc::strong_count(&a));
        
        let c = Rc::clone(&a);
        println!("再次 clone 後計數: {}", Rc::strong_count(&a));
    }
    
    println!("離開作用域後計數: {}", Rc::strong_count(&a));
    
    // Rc 共享所有權
    let shared_vec = Rc::new(vec![1, 2, 3]);
    let vec1 = Rc::clone(&shared_vec);
    let vec2 = Rc::clone(&shared_vec);
    
    println!("\n共享向量: {:?}", shared_vec);
    println!("vec1: {:?}", vec1);
    println!("vec2: {:?}", vec2);
    
    // RefCell - 內部可變性
    println!("\n=== RefCell 內部可變性 ===");
    let value = RefCell::new(5);
    
    // 借用規則在執行時檢查
    {
        let mut borrow_mut = value.borrow_mut();
        *borrow_mut += 10;
    }
    
    println!("修改後的值: {}", value.borrow());
    
    // Rc + RefCell 組合
    println!("\n=== Rc + RefCell 組合 ===");
    let shared_value = Rc::new(RefCell::new(vec![1, 2, 3]));
    
    let value1 = Rc::clone(&shared_value);
    let value2 = Rc::clone(&shared_value);
    
    // 透過任一引用修改
    value1.borrow_mut().push(4);
    println!("value1 修改後: {:?}", value1.borrow());
    
    value2.borrow_mut().push(5);
    println!("value2 修改後: {:?}", value2.borrow());
    
    println!("原始值: {:?}", shared_value.borrow());
    
    // 樹結構範例
    println!("\n=== 樹結構 (Rc + RefCell + Weak) ===");
    let root = Rc::new(Node {
        value: 1,
        children: RefCell::new(vec![]),
        parent: RefCell::new(Weak::new()),
    });
    
    let child1 = Rc::new(Node {
        value: 2,
        children: RefCell::new(vec![]),
        parent: RefCell::new(Rc::downgrade(&root)),
    });
    
    let child2 = Rc::new(Node {
        value: 3,
        children: RefCell::new(vec![]),
        parent: RefCell::new(Rc::downgrade(&root)),
    });
    
    root.children.borrow_mut().push(Rc::clone(&child1));
    root.children.borrow_mut().push(Rc::clone(&child2));
    
    println!("根節點值: {}", root.value);
    println!("子節點數: {}", root.children.borrow().len());
    
    // Weak 引用避免循環引用
    println!("\n=== Weak 引用 ===");
    let strong = Rc::new(100);
    let weak = Rc::downgrade(&strong);
    
    println!("強引用計數: {}", Rc::strong_count(&strong));
    println!("弱引用計數: {}", Rc::weak_count(&strong));
    
    // 升級 Weak 到 Rc
    if let Some(strong_ref) = weak.upgrade() {
        println!("Weak 升級成功: {}", strong_ref);
    }
    
    // 當強引用都釋放後
    drop(strong);
    if weak.upgrade().is_none() {
        println!("Weak 升級失敗 (原始值已釋放)");
    }
    
    // RefCell 的 try_borrow
    println!("\n=== RefCell try_borrow ===");
    let cell = RefCell::new(50);
    
    let borrow1 = cell.borrow();
    
    // 嘗試可變借用會失敗
    match cell.try_borrow_mut() {
        Ok(_) => println!("可變借用成功"),
        Err(_) => println!("可變借用失敗 (已有不可變借用)"),
    }
    
    drop(borrow1);
    
    // 現在可以可變借用
    match cell.try_borrow_mut() {
        Ok(mut borrow) => {
            *borrow += 50;
            println!("可變借用成功，新值: {}", *borrow);
        }
        Err(_) => println!("可變借用失敗"),
    }
    
    // 實用範例：共享計數器
    println!("\n=== 共享計數器 ===");
    let counter = Rc::new(RefCell::new(0));
    
    let counter1 = Rc::clone(&counter);
    let counter2 = Rc::clone(&counter);
    
    *counter1.borrow_mut() += 1;
    println!("Counter1 增加: {}", counter1.borrow());
    
    *counter2.borrow_mut() += 2;
    println!("Counter2 增加: {}", counter2.borrow());
    
    println!("最終計數: {}", counter.borrow());
}
```

## 19. 生命週期範例

```rust
use std::fmt::Display;

// 基本生命週期
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

// 結構體生命週期
#[derive(Debug)]
struct ImportantExcerpt<'a> {
    part: &'a str,
}

impl<'a> ImportantExcerpt<'a> {
    fn level(&self) -> i32 {
        3
    }
    
    fn announce_and_return_part(&self, announcement: &str) -> &str {
        println!("Attention please: {}", announcement);
        self.part
    }
}

// 多個生命週期參數
fn first_word<'a>(s: &'a str, _t: &str) -> &'a str {
    let bytes = s.as_bytes();
    
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }
    
    &s[..]
}

// 生命週期界限
fn longest_with_an_announcement<'a, T>(
    x: &'a str,
    y: &'a str,
    ann: T,
) -> &'a str
where
    T: Display,
{
    println!("Announcement! {}", ann);
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

// 靜態生命週期
fn get_static_str() -> &'static str {
    "I have a static lifetime!"
}

fn main() {
    // 基本生命週期範例
    println!("=== 基本生命週期 ===");
    let string1 = String::from("long string is long");
    let result;
    {
        let string2 = String::from("xyz");
        result = longest(string1.as_str(), string2.as_str());
        println!("最長的字串: {}", result);
    }
    
    // 生命週期和作用域
    let string1 = String::from("abcd");
    let string2 = "xyz";
    
    let result = longest(string1.as_str(), string2);
    println!("最長: {}", result);
    
    // 結構體生命週期
    println!("\n=== 結構體生命週期 ===");
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().expect("Could not find a '.'");
    let excerpt = ImportantExcerpt {
        part: first_sentence,
    };
    
    println!("摘錄: {:?}", excerpt);
    println!("等級: {}", excerpt.level());
    
    // 方法中的生命週期
    let announcement = "這是重要公告";
    let part = excerpt.announce_and_return_part(announcement);
    println!("返回部分: {}", part);
    
    // 靜態生命週期
    println!("\n=== 靜態生命週期 ===");
    let s: &'static str = "我有 'static 生命週期";
    println!("{}", s);
    
    let static_string = get_static_str();
    println!("靜態字串: {}", static_string);
    
    // 字串字面量都有 'static 生命週期
    let literal: &'static str = "字串字面量";
    println!("{}", literal);
    
    // 生命週期省略規則
    println!("\n=== 生命週期省略 ===");
    let my_string = String::from("hello world");
    let word = first_word(&my_string, "ignore");
    println!("第一個單詞: {}", word);
    
    // 泛型類型參數、trait bounds 和生命週期
    println!("\n=== 組合範例 ===");
    let string1 = String::from("這是一個測試");
    let string2 = "另一個測試";
    let ann = "比較兩個字串的長度！";
    
    let result = longest_with_an_announcement(
        string1.as_str(),
        string2,
        ann,
    );
    println!("結果: {}", result);
    
    // 生命週期子類型化
    println!("\n=== 生命週期關係 ===");
    fn print_refs<'a, 'b>(x: &'a i32, y: &'b i32) 
    where 
        'a: 'b  // 'a 的生命週期至少和 'b 一樣長
    {
        println!("x: {}, y: {}", x, y);
    }
    
    let x = 5;
    let y = 10;
    print_refs(&x, &y);
    
    // 生命週期和閉包
    println!("\n=== 閉包中的生命週期 ===");
    let closure_example = |x: &str| -> &str {
        println!("閉包接收: {}", x);
        x
    };
    
    let input = "測試輸入";
    let output = closure_example(input);
    println!("閉包返回: {}", output);
    
    // 複雜生命週期範例
    #[derive(Debug)]
    struct Context<'s>(&'s str);
    
    struct Parser<'c, 's: 'c> {
        context: &'c Context<'s>,
    }
    
    impl<'c, 's> Parser<'c, 's> {
        fn parse(&self) -> Result<(), &'s str> {
            Err(&self.context.0[1..])
        }
    }
    
    let context = Context("資料內容");
    let parser = Parser { context: &context };
    
    match parser.parse() {
        Ok(_) => println!("解析成功"),
        Err(e) => println!("解析錯誤: {}", e),
    }
}
```

## 20. 泛型 (Generics)

```rust
use std::fmt::Display;
use std::cmp::PartialOrd;

// 泛型函數
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    
    for item in list {
        if item > largest {
            largest = item;
        }
    }
    
    largest
}

// 泛型結構體
#[derive(Debug)]
struct Point<T> {
    x: T,
    y: T,
}

impl<T> Point<T> {
    fn new(x: T, y: T) -> Self {
        Point { x, y }
    }
    
    fn x(&self) -> &T {
        &self.x
    }
}

// 特定類型的方法
impl Point<f32> {
    fn distance_from_origin(&self) -> f32 {
        (self.x.powi(2) + self.y.powi(2)).sqrt()
    }
}

// 多個泛型參數
struct Pair<T, U> {
    first: T,
    second: U,
}

impl<T, U> Pair<T, U> {
    fn new(first: T, second: U) -> Self {
        Pair { first, second }
    }
    
    fn mixup<V, W>(self, other: Pair<V, W>) -> Pair<T, W> {
        Pair {
            first: self.first,
            second: other.second,
        }
    }
}

// 泛型枚舉
enum Option<T> {
    Some(T),
    None,
}

enum Result<T, E> {
    Ok(T),
    Err(E),
}

// Trait 界限
fn print_item<T: Display>(item: T) {
    println!("{}", item);
}

// 多個 trait 界限
fn compare_and_display<T: Display + PartialOrd>(a: &T, b: &T) {
    if a > b {
        println!("{} 大於另一個值", a);
    } else {
        println!("{} 小於或等於另一個值", b);
    }
}

// where 子句
fn some_function<T, U>(t: &T, u: &U) -> i32
where
    T: Display + Clone,
    U: Clone + std::fmt::Debug,
{
    println!("t: {}", t);
    println!("u: {:?}", u);
    42
}

fn main() {
    // 泛型函數
    println!("=== 泛型函數 ===");
    let number_list = vec![34, 50, 25, 100, 65];
    let result = largest(&number_list);
    println!("最大數字: {}", result);
    
    let char_list = vec!['y', 'm', 'a', 'q'];
    let result = largest(&char_list);
    println!("最大字元: {}", result);
    
    // 泛型結構體
    println!("\n=== 泛型結構體 ===");
    let integer_point = Point::new(5, 10);
    let float_point = Point::new(1.0, 4.0);
    
    println!("整數點: {:?}", integer_point);
    println!("浮點數點: {:?}", float_point);
    println!("x 座標: {}", integer_point.x());
    
    // 特定類型方法
    let p = Point { x: 3.0_f32, y: 4.0_f32 };
    println!("距離原點: {}", p.distance_from_origin());
    
    // 多個泛型參數
    println!("\n=== 多個泛型參數 ===");
    let pair1 = Pair::new(5, "hello");
    let pair2 = Pair::new("world", 3.14);
    
    let mixed = pair1.mixup(pair2);
    println!("混合後: first = {}, second = {}", mixed.first, mixed.second);
    
    // Trait 界限
    println!("\n=== Trait 界限 ===");
    print_item("Hello, generics!");
    print_item(42);
    
    compare_and_display(&10, &20);
    compare_and_display(&"apple", &"banana");
    
    // where 子句
    println!("\n=== Where 子句 ===");
    let s = String::from("測試");
    let v = vec![1, 2, 3];
    some_function(&s, &v);
    
    // 泛型和生命週期
    println!("\n=== 泛型和生命週期 ===");
    fn longest_generic<'a, T>(x: &'a T, y: &'a T) -> &'a T
    where
        T: PartialOrd,
    {
        if x > y { x } else { y }
    }
    
    let a = 10;
    let b = 20;
    let result = longest_generic(&a, &b);
    println!("較大值: {}", result);
    
    // 預設泛型參數
    println!("\n=== 預設泛型參數 ===");
    use std::ops::Add;
    
    #[derive(Debug)]
    struct Millimeters(u32);
    #[derive(Debug)]
    struct Meters(u32);
    
    impl Add<Meters> for Millimeters {
        type Output = Millimeters;
        
        fn add(self, other: Meters) -> Millimeters {
            Millimeters(self.0 + other.0 * 1000)
        }
    }
    
    let mm = Millimeters(1500);
    let m = Meters(2);
    let result = mm.add(m);
    println!("1500mm + 2m = {:?}", result);
    
    // 關聯類型
    println!("\n=== 關聯類型 ===");
    trait Container {
        type Item;
        fn contains(&self, item: &Self::Item) -> bool;
    }
    
    struct NumberContainer {
        items: Vec<i32>,
    }
    
    impl Container for NumberContainer {
        type Item = i32;
        
        fn contains(&self, item: &Self::Item) -> bool {
            self.items.contains(item)
        }
    }
    
    let container = NumberContainer {
        items: vec![1, 2, 3, 4, 5],
    };
    
    println!("包含 3: {}", container.contains(&3));
    println!("包含 6: {}", container.contains(&6));
    
    // 泛型常數
    println!("\n=== 泛型陣列 ===");
    fn print_array<T: std::fmt::Debug, const N: usize>(arr: &[T; N]) {
        println!("陣列 (長度 {}): {:?}", N, arr);
    }
    
    let arr1 = [1, 2, 3];
    let arr2 = [1, 2, 3, 4, 5];
    
    print_array(&arr1);
    print_array(&arr2);
}
```", numbers);
    
    // 使用 vec! 巨集
    let fruits = vec!["apple", "banana", "orange"];
    println!("水果: {:?}", fruits);
    
    // 存取元素
    println!("第一個數字: {}", numbers[0]);
    println!("最後一個水果: {:?}", fruits.last());
    
    // 迭代
    print!("所有數字: ");
    for num in &numbers {
        print!("{} ", num);
    }
    println!();
    
    // 修改
    numbers[1] = 25;
    numbers.pop();
    numbers.insert(0, 5);
    println!("修改後: {:?}", numbers);
    
    // 常用方法
    println!("長度: {}", numbers.len());
    println!("是否為空: {}", numbers.is_empty());
    println!("是否包含 25: {}", numbers.contains(&25));
    
    // 排序
    numbers.sort();
    println!("排序後: {:?}", numbers);
    
    // 過濾和轉換
    let doubled: Vec<i32> = numbers.iter().map(|x| x * 2).collect();
    println!("加倍: {:?}", doubled);
    
    let evens: Vec<&i32> = numbers.iter().filter(|x| *x % 2 == 0).collect();
    println!("偶數: {:?}", evens);
}
```

## 2. HashMap - 雜湊表

```rust
use std::collections::HashMap;

fn main() {
    // 創建 HashMap
    let mut scores = HashMap::new();
    
    // 插入資料
    scores.insert("Alice", 90);
    scores.insert("Bob", 85);
    scores.insert("Charlie", 95);
    
    // 存取值
    match scores.get("Alice") {
        Some(score) => println!("Alice 的分數: {}", score),
        None => println!("找不到 Alice"),
    }
    
    // 更新值
    scores.insert("Bob", 88); // 覆蓋舊值
    
    // entry API - 只在不存在時插入
    scores.entry("David").or_insert(80);
    scores.entry("Alice").or_insert(70); // 不會覆蓋
    
    // 修改值
    let alice_score = scores.entry("Alice").or_insert(0);
    *alice_score += 5;
    
    // 迭代
    println!("\n所有分數:");
    for (name, score) in &scores {
        println!("{}: {}", name, score);
    }
    
    // 檢查是否包含 key
    if scores.contains_key("Bob") {
        println!("\nBob 在名單中");
    }
    
    // 移除
    if let Some(removed) = scores.remove("Charlie") {
        println!("移除 Charlie，分數是: {}", removed);
    }
    
    // 從陣列創建 HashMap
    let teams = vec!["Blue", "Red", "Green"];
    let initial_scores = vec![10, 20, 30];
    let team_scores: HashMap<_, _> = teams.iter().zip(initial_scores.iter()).collect();
    println!("\n隊伍分數: {:?}", team_scores);
    
    // 統計字數
    let text = "hello world hello rust world";
    let mut word_count = HashMap::new();
    for word in text.split_whitespace() {
        let count = word_count.entry(word).or_insert(0);
        *count += 1;
    }
    println!("\n字數統計: {:?}", word_count);
}
```

## 3. HashSet - 集合

```rust
use std::collections::HashSet;

fn main() {
    // 創建 HashSet
    let mut languages = HashSet::new();
    
    // 插入元素
    languages.insert("Rust");
    languages.insert("Python");
    languages.insert("JavaScript");
    languages.insert("Rust"); // 重複插入會被忽略
    
    println!("程式語言: {:?}", languages);
    println!("數量: {}", languages.len());
    
    // 檢查是否包含
    if languages.contains("Rust") {
        println!("包含 Rust");
    }
    
    // 從 Vec 創建 HashSet
    let numbers = vec![1, 2, 3, 3, 4, 4, 5];
    let unique_numbers: HashSet<_> = numbers.into_iter().collect();
    println!("\n唯一數字: {:?}", unique_numbers);
    
    // 集合運算
    let set_a: HashSet<_> = [1, 2, 3, 4].iter().cloned().collect();
    let set_b: HashSet<_> = [3, 4, 5, 6].iter().cloned().collect();
    
    // 交集
    let intersection: HashSet<_> = set_a.intersection(&set_b).cloned().collect();
    println!("\n交集: {:?}", intersection);
    
    // 聯集
    let union: HashSet<_> = set_a.union(&set_b).cloned().collect();
    println!("聯集: {:?}", union);
    
    // 差集
    let difference: HashSet<_> = set_a.difference(&set_b).cloned().collect();
    println!("差集 (A - B): {:?}", difference);
    
    // 對稱差集
    let symmetric_difference: HashSet<_> = set_a.symmetric_difference(&set_b).cloned().collect();
    println!("對稱差集: {:?}", symmetric_difference);
    
    // 子集和超集
    let small: HashSet<_> = [1, 2].iter().cloned().collect();
    println!("\n{:?} 是 {:?} 的子集: {}", small, set_a, small.is_subset(&set_a));
    println!("{:?} 是 {:?} 的超集: {}", set_a, small, set_a.is_superset(&small));
}
```

## 4. VecDeque - 雙端佇列

```rust
use std::collections::VecDeque;

fn main() {
    // 創建 VecDeque
    let mut deque = VecDeque::new();
    
    // 從兩端添加元素
    deque.push_back(2);
    deque.push_back(3);
    deque.push_front(1);
    deque.push_front(0);
    
    println!("佇列: {:?}", deque);
    
    // 從兩端移除元素
    println!("移除前端: {:?}", deque.pop_front());
    println!("移除後端: {:?}", deque.pop_back());
    println!("佇列現在: {:?}", deque);
    
    // 存取元素
    if let Some(front) = deque.front() {
        println!("前端元素: {}", front);
    }
    if let Some(back) = deque.back() {
        println!("後端元素: {}", back);
    }
    
    // 使用索引存取
    println!("索引 0: {}", deque[0]);
    
    // 旋轉
    let mut rotating = VecDeque::from(vec![1, 2, 3, 4, 5]);
    rotating.rotate_left(2);
    println!("\n左旋轉 2: {:?}", rotating);
    rotating.rotate_right(1);
    println!("右旋轉 1: {:?}", rotating);
    
    // 作為佇列使用 (FIFO)
    println!("\n佇列操作:");
    let mut queue = VecDeque::new();
    queue.push_back("First");
    queue.push_back("Second");
    queue.push_back("Third");
    
    while let Some(item) = queue.pop_front() {
        println!("處理: {}", item);
    }
    
    // 作為堆疊使用 (LIFO)
    println!("\n堆疊操作:");
    let mut stack = VecDeque::new();
    stack.push_back("First");
    stack.push_back("Second");
    stack.push_back("Third");
    
    while let Some(item) = stack.pop_back() {
        println!("處理: {}", item);
    }
}
```

## 5. String 字串處理

```rust
fn main() {
    // 創建 String
    let mut s1 = String::new();
    let s2 = String::from("Hello");
    let s3 = "World".to_string();
    
    // 字串拼接
    s1.push_str("Rust ");
    s1.push('🦀');
    println!("s1: {}", s1);
    
    // 使用 + 運算子
    let greeting = s2 + " " + &s3;
    println!("greeting: {}", greeting);
    
    // 使用 format!
    let name = "Alice";
    let age = 30;
    let info = format!("{} is {} years old", name, age);
    println!("info: {}", info);
    
    // 字串切片
    let hello = String::from("Hello, 世界!");
    let slice = &hello[0..5];
    println!("切片: {}", slice);
    
    // 迭代字元
    print!("字元: ");
    for ch in hello.chars() {
        print!("{} ", ch);
    }
    println!();
    
    // 迭代位元組
    print!("位元組: ");
    for b in hello.bytes() {
        print!("{} ", b);
    }
    println!();
    
    // 字串方法
    let text = "  Hello Rust  ";
    println!("\n原始: '{}'", text);
    println!("trim: '{}'", text.trim());
    println!("大寫: '{}'", text.to_uppercase());
    println!("小寫: '{}'", text.to_lowercase());
    println!("替換: '{}'", text.replace("Rust", "World"));
    
    // 分割字串
    let csv = "apple,banana,orange";
    let fruits: Vec<&str> = csv.split(',').collect();
    println!("\n水果: {:?}", fruits);
    
    // 檢查字串
    let email = "user@example.com";
    println!("\nEmail: {}", email);
    println!("包含 @: {}", email.contains('@'));
    println!("開頭是 user: {}", email.starts_with("user"));
    println!("結尾是 .com: {}", email.ends_with(".com"));
    
    // 查找位置
    if let Some(pos) = email.find('@') {
        println!("@ 的位置: {}", pos);
    }
    
    // 解析數字
    let num_str = "42";
    match num_str.parse::<i32>() {
        Ok(num) => println!("\n解析數字: {}", num),
        Err(e) => println!("解析錯誤: {}", e),
    }
}
```

## 6. Option 類型

```rust
fn main() {
    // Option 基本用法
    let some_number = Some(5);
    let no_number: Option<i32> = None;
    
    // 使用 match
    match some_number {
        Some(n) => println!("數字是: {}", n),
        None => println!("沒有數字"),
    }
    
    // 使用 if let
    if let Some(n) = some_number {
        println!("使用 if let: {}", n);
    }
    
    // 實際範例：除法函數
    fn divide(dividend: f64, divisor: f64) -> Option<f64> {
        if divisor == 0.0 {
            None
        } else {
            Some(dividend / divisor)
        }
    }
    
    let result1 = divide(10.0, 2.0);
    let result2 = divide(10.0, 0.0);
    
    println!("\n10 ÷ 2 = {:?}", result1);
    println!("10 ÷ 0 = {:?}", result2);
    
    // unwrap_or 提供預設值
    let value1 = result1.unwrap_or(0.0);
    let value2 = result2.unwrap_or(0.0);
    println!("\n使用 unwrap_or:");
    println!("value1: {}", value1);
    println!("value2: {}", value2);
    
    // map 轉換值
    let maybe_string = Some("hello");
    let maybe_len = maybe_string.map(|s| s.len());
    println!("\n字串長度: {:?}", maybe_len);
    
    // and_then 鏈式操作
    fn square(x: i32) -> Option<i32> {
        Some(x * x)
    }
    
    fn double(x: i32) -> Option<i32> {
        Some(x * 2)
    }
    
    let number = Some(5);
    let result = number.and_then(square).and_then(double);
    println!("5 平方後加倍: {:?}", result);
    
    // filter 過濾
    let numbers = vec![Some(1), None, Some(3), Some(4), None];
    let filtered: Vec<_> = numbers
        .into_iter()
        .filter_map(|x| x)
        .filter(|x| x % 2 == 0)
        .collect();
    println!("\n過濾偶數: {:?}", filtered);
    
    // 實際應用：查找陣列元素
    let names = vec!["Alice", "Bob", "Charlie"];
    let search_name = "Bob";
    let position = names.iter().position(|&name| name == search_name);
    
    match position {
        Some(index) => println!("\n{} 在索引 {}", search_name, index),
        None => println!("\n找不到 {}", search_name),
    }
}
```

## 7. Result 錯誤處理

```rust
use std::fs::File;
use std::io::{self, Read, Write};

fn main() {
    // Result 基本用法
    fn divide(a: f64, b: f64) -> Result<f64, String> {
        if b == 0.0 {
            Err(String::from("除數不能為零"))
        } else {
            Ok(a / b)
        }
    }
    
    // 使用 match 處理
    let result = divide(10.0, 2.0);
    match result {
        Ok(value) => println!("10 ÷ 2 = {}", value),
        Err(e) => println!("錯誤: {}", e),
    }
    
    // 使用 ? 運算子
    fn read_username_from_file() -> Result<String, io::Error> {
        let mut file = File::open("username.txt")?;
        let mut username = String::new();
        file.read_to_string(&mut username)?;
        Ok(username)
    }
    
    // 處理檔案讀取
    match read_username_from_file() {
        Ok(name) => println!("使用者名稱: {}", name),
        Err(e) => println!("讀取錯誤: {}", e),
    }
    
    // unwrap_or_else
    let value = divide(10.0, 0.0).unwrap_or_else(|e| {
        println!("使用預設值，因為: {}", e);
        0.0
    });
    println!("結果: {}", value);
    
    // map 和 map_err
    let doubled = divide(10.0, 2.0)
        .map(|x| x * 2.0)
        .map_err(|e| format!("計算失敗: {}", e));
    println!("\n加倍結果: {:?}", doubled);
    
    // 多個錯誤類型
    fn complex_operation(s: &str) -> Result<i32, String> {
        s.parse::<i32>()
            .map_err(|e| format!("解析錯誤: {}", e))
            .and_then(|n| {
                if n < 0 {
                    Err(String::from("數字不能為負"))
                } else {
                    Ok(n * 2)
                }
            })
    }
    
    println!("\n複雜操作:");
    println!("\"10\" -> {:?}", complex_operation("10"));
    println!("\"-5\" -> {:?}", complex_operation("-5"));
    println!("\"abc\" -> {:?}", complex_operation("abc"));
    
    // 收集 Results
    let strings = vec!["10", "20", "abc", "30"];
    let numbers: Result<Vec<i32>, _> = strings
        .iter()
        .map(|s| s.parse::<i32>())
        .collect();
    
    match numbers {
        Ok(nums) => println!("\n所有數字: {:?}", nums),
        Err(e) => println!("解析失敗: {}", e),
    }
    
    // 只收集成功的結果
    let valid_numbers: Vec<i32> = strings
        .iter()
        .filter_map(|s| s.parse::<i32>().ok())
        .collect();
    println!("有效數字: {:?}", valid_numbers);
}
```

## 8. 迭代器 Iterator

```rust
fn main() {
    let numbers = vec![1, 2, 3, 4, 5];
    
    // 基本迭代
    println!("基本迭代:");
    for n in &numbers {
        print!("{} ", n);
    }
    println!();
    
    // map - 轉換每個元素
    let squared: Vec<i32> = numbers.iter().map(|x| x * x).collect();
    println!("\n平方: {:?}", squared);
    
    // filter - 過濾元素
    let evens: Vec<&i32> = numbers.iter().filter(|x| *x % 2 == 0).collect();
    println!("偶數: {:?}", evens);
    
    // filter_map - 同時過濾和轉換
    let strings = vec!["1", "2", "abc", "4"];
    let parsed: Vec<i32> = strings
        .iter()
        .filter_map(|s| s.parse().ok())
        .collect();
    println!("\n解析成功的數字: {:?}", parsed);
    
    // fold - 累積計算
    let sum = numbers.iter().fold(0, |acc, x| acc + x);
    let product = numbers.iter().fold(1, |acc, x| acc * x);
    println!("\n總和: {}", sum);
    println!("乘積: {}", product);
    
    // reduce - 類似 fold 但沒有初始值
    let max = numbers.iter().reduce(|a, b| if a > b { a } else { b });
    println!("最大值: {:?}", max);
    
    // take 和 skip
    let first_three: Vec<&i32> = numbers.iter().take(3).collect();
    let skip_two: Vec<&i32> = numbers.iter().skip(2).collect();
    println!("\n前三個: {:?}", first_three);
    println!("跳過兩個: {:?}", skip_two);
    
    // enumerate - 取得索引
    println!("\n帶索引:");
    for (i, v) in numbers.iter().enumerate() {
        println!("索引 {}: 值 {}", i, v);
    }
    
    // zip - 配對兩個迭代器
    let names = vec!["Alice", "Bob", "Charlie"];
    let ages = vec![25, 30, 35];
    let people: Vec<_> = names.iter().zip(ages.iter()).collect();
    println!("\n配對: {:?}", people);
    
    // chain - 連接迭代器
    let first = vec![1, 2, 3];
    let second = vec![4, 5, 6];
    let combined: Vec<i32> = first.iter().chain(second.iter()).copied().collect();
    println!("\n連接: {:?}", combined);
    
    // any 和 all
    let has_even = numbers.iter().any(|x| x % 2 == 0);
    let all_positive = numbers.iter().all(|x| *x > 0);
    println!("\n包含偶數: {}", has_even);
    println!("全部為正: {}", all_positive);
    
    // find - 查找第一個符合條件的元素
    let first_even = numbers.iter().find(|x| *x % 2 == 0);
    println!("\n第一個偶數: {:?}", first_even);
    
    // position - 查找位置
    let pos = numbers.iter().position(|x| *x == 3);
    println!("3 的位置: {:?}", pos);
    
    // partition - 分割成兩組
    let (evens, odds): (Vec<i32>, Vec<i32>) = numbers
        .into_iter()
        .partition(|x| x % 2 == 0);
    println!("\n偶數組: {:?}", evens);
    println!("奇數組: {:?}", odds);
    
    // 無限迭代器
    let powers_of_2: Vec<i32> = std::iter::successors(Some(1), |x| Some(x * 2))
        .take(5)
        .collect();
    println!("\n2 的冪: {:?}", powers_of_2);
    
    // 自定義迭代器鏈
    let result: i32 = (1..=100)
        .filter(|x| x % 2 == 0)
        .take(5)
        .map(|x| x * x)
        .sum();
    println!("\n前5個偶數的平方和: {}", result);
}
```

## 9. 檔案 I/O

```rust
use std::fs::{self, File};
use std::io::{self, BufRead, BufReader, Write};

fn main() -> io::Result<()> {
    // 寫入檔案 - 簡單方式
    let content = "Hello, Rust!\n這是測試檔案。";
    fs::write("test.txt", content)?;
    println!("檔案寫入成功");
    
    // 讀取整個檔案
    let read_content = fs::read_to_string("test.txt")?;
    println!("\n讀取內容:\n{}", read_content);
    
    // 逐行寫入
    let mut file = File::create("lines.txt")?;
    writeln!(file, "第一行")?;
    writeln!(file, "第二行")?;
    writeln!(file, "第三行")?;
    file.write_all(b"第四行\n")?;
    println!("\n多行檔案寫入成功");
    
    // 逐行讀取
    let file = File::open("lines.txt")?;
    let reader = BufReader::new(file);
    
    println!("\n逐行讀取:");
    for (index, line) in reader.lines().enumerate() {
        let line = line?;
        println!("行 {}: {}", index + 1, line);
    }
    
    // 追加內容
    let mut file = fs::OpenOptions::new()
        .append(true)
        .open("lines.txt")?;
    writeln!(file, "追加的行")?;
    println!("\n內容追加成功");
    
    // 讀取為位元組
    let bytes = fs::read("test.txt")?;
    println!("\n前10個位元組: {:?}", &bytes[..10.min(bytes.len())]);
    
    // 檢查檔案是否存在
    if fs::metadata("test.txt").is_ok() {
        println!("\ntest.txt 存在");
    }
    
    // 取得檔案資訊
    let metadata = fs::metadata("test.txt")?;
    println!("檔案大小: {} bytes", metadata.len());
    println!("是檔案: {}", metadata.is_file());
    println!("是目錄: {}", metadata.is_dir());
    println!("唯讀: {}", metadata.permissions().readonly());
    
    // 複製檔案
    fs::copy("test.txt", "test_copy.txt")?;
    println!("\n檔案複製成功");
    
    // 重命名檔案
    fs::rename("test_copy.txt", "test_renamed.txt")?;
    println!("檔案重命名成功");
    
    // 創建目錄
    fs::create_dir_all("test_dir/sub_dir")?;
    println!("\n目錄創建成功");
    
    // 讀取目錄內容
    println!("\n當前目錄內容:");
    for entry in fs::read_dir(".")? {
        let entry = entry?;
        let path = entry.path();
        let file_type = if path.is_dir() { "目錄" } else { "檔案" };
        println!("{}: {:?}", file_type, path.file_name().unwrap());
    }
    
    // 清理測試檔案
    fs::remove_file("test.txt")?;
    fs::remove_file("lines.txt")?;
    fs::remove_file("test_renamed.txt")?;
    fs::remove_dir_all("test_dir")?;
    println!("\n測試檔案已清理");
    
    Ok(())
}
```

## 10. 執行緒 Thread

```rust
use std::thread;
use std::time::Duration;
use std::sync::mpsc;

fn main() {
    // 基本執行緒
    let handle = thread::spawn(|| {
        for i in 1..=5 {
            println!("執行緒 1: 計數 {}", i);
            thread::sleep(Duration::from_millis(100));
        }
    });
    
    // 主執行緒同時執行
    for i in 1..=3 {
        println!("主執行緒: 計數 {}", i);
        thread::sleep(Duration::from_millis(150));
    }
    
    // 等待執行緒完成
    handle.join().unwrap();
    println!("\n執行緒 1 已完成");
    
    // 傳遞資料到執行緒 (move)
    let data = vec![1, 2, 3, 4, 5];
    let handle = thread::spawn(move || {
        let sum: i32 = data.iter().sum();
        println!("\n資料總和: {}", sum);
        sum // 返回值
    });
    
    let result = handle.join().unwrap();
    println!("執行緒返回: {}", result);
    
    // 多個執行緒
    let mut handles = vec![];
    
    for i in 0..3 {
        let handle = thread::spawn(move || {
            thread::sleep(Duration::from_millis(100 * i));
            println!("執行緒 {} 完成", i);
            i * 2
        });
        handles.push(handle);
    }
    
    println!("\n等待所有執行緒...");
    let mut results = vec![];
    for handle in handles {
        results.push(handle.join().unwrap());
    }
    println!("所有結果: {:?}", results);
    
    // 使用通道通信
    let (tx, rx) = mpsc::channel();
    
    thread::spawn(move || {
        let messages = vec![
            String::from("訊息 1"),
            String::from("訊息 2"),
            String::from("訊息 3"),
        ];
        
        for msg in messages {
            tx.send(msg).unwrap();
            thread::sleep(Duration::from_millis(200));
        }
    });
    
    println!("\n接收訊息:");
    for received in rx {
        println!("收到: {}", received);
    }
    
    // 多個生產者
    let (tx, rx) = mpsc::channel();
    let tx1 = tx.clone();
    
    thread::spawn(move || {
        tx.send("來自執行緒 A").unwrap();
    });
    
    thread::spawn(move || {
        tx1.send("來自執行緒 B").unwrap();
    });
    
    for received in rx {
        println!("收到: {}", received);
    }
    
    // 取得執行緒 ID
    println!("\n主執行緒 ID: {:?}", thread::current().id());
    
    let handle = thread::spawn(|| {
        println!("新執行緒 ID: {:?}", thread::current().id());
    });
    
    handle.join().unwrap();
    
    // 建立具名執行緒
    let builder = thread::Builder::new()
        .name("worker".to_string())
        .stack_size(4 * 1024 * 1024);
    
    let handle = builder.spawn(|| {
        println!("\n執行緒名稱: {:?}", thread::current().name());
    }).unwrap();
    
    handle.join().unwrap();
}
```

## 11. Arc 和 Mutex - 共享狀態

```rust
use std::sync::{Arc, Mutex, RwLock};
use std::thread;

fn main() {
    // Mutex 基本用法
    let m = Mutex::new(5);
    {
        let mut num = m.lock().unwrap();
        *num = 6;
    }
    println!("Mutex 值: {:?}", m);
    
    // Arc + Mutex 在多執行緒中共享
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];
    
    for i in 0..5 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();
            *num += 1;
            println!("執行緒 {} 將計數器增加到 {}", i, *num);
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("\n最終計數: {}", *counter.lock().unwrap());
    
    // 共享向量
    let shared_vec = Arc::new(Mutex::new(Vec::new()));
    let mut handles = vec![];
    
    for i in 0..3 {
        let vec = Arc::clone(&shared_vec);
        let handle = thread::spawn(move || {
            let mut v = vec.lock().unwrap();
            v.push(i);
            println!("執行緒 {} 添加了 {}", i, i);
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("共享向量: {:?}", *shared_vec.lock().unwrap());
    
    // RwLock - 讀寫鎖
    let lock = Arc::new(RwLock::new(vec![1, 2, 3]));
    let mut handles = vec![];
    
    // 多個讀取者
    for i in 0..3 {
        let lock = Arc::clone(&lock);
        let handle = thread::spawn(move || {
            let data = lock.read().unwrap();
            println!("讀取者 {} 看到: {:?}", i, *data);
        });
        handles.push(handle);
    }
    
    // 一個寫入者
    let lock_write = Arc::clone(&lock);
    let write_handle = thread::spawn(move || {
        let mut data = lock_write.write().unwrap();
        data.push(4);
        println!("寫入者添加了 4");
    });
    
    for handle in handles {
        handle.join().unwrap();
    }
    write_handle.join().unwrap();
    
    println!("\nRwLock 最終值: {:?}", *lock.read().unwrap());
    
    // 避免死鎖 - 使用 try_lock
    let lock1 = Arc::new(Mutex::new(1));
    let lock2 = Arc::new(Mutex::new(2));
    
    let l1 = Arc::clone(&lock1);
    let l2 = Arc::clone(&lock2);
    
    let handle = thread::spawn(move || {
        let _guard1 = l1.lock().unwrap();
        println!("執行緒 1 取得 lock1");
        thread::sleep(std::time::Duration::from_millis(100));
        
        match l2.try_lock() {
            Ok(_guard2) => println!("執行緒 1 取得 lock2"),
            Err(_) => println!("執行緒 1 無法取得 lock2"),
        }
    });
    
    let _guard2 = lock2.lock().unwrap();
    println!("主執行緒取得 lock2");
    thread::sleep(std::time::Duration::from_millis(50));
    
    match lock1.try_lock() {
        Ok(_guard1) => println!("主執行緒取得 lock1"),
        Err(_) => println!("主執行緒無法取得 lock1"),
    }
    
    handle.join().unwrap();
}
```

## 12. 通道 Channel

```rust
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

fn main() {
    // 基本通道
    let (tx, rx) = mpsc::channel();
    
    thread::spawn(move || {
        let val = String::from("你好");
        tx.send(val).unwrap();
    });
    
    let received = rx.recv().unwrap();
    println!("收到: {}", received);
    
    // 發送多個值
    let (tx, rx) = mpsc::channel();
    
    thread::spawn(move || {
        let vals = vec![
            String::from("訊息"),
            String::from("來自"),
            String::from("執行緒"),
        ];
        
        for val in vals {
            tx.send(val).unwrap();
            thread::sleep(Duration::from_millis(200));
        }
    });
    
    // 作為迭代器接收
    for received in rx {
        println!("收到: {}", received);
    }
    
    // 多個生產者
    println!("\n多個生產者:");
    let (tx, rx) = mpsc::channel();
    
    for i in 0..3 {
        let tx = tx.clone();
        thread::spawn(move || {
            tx.send(format!("生產者 {} 的訊息", i)).unwrap();
            thread::sleep(Duration::from_millis(100 * i));
        });
    }
    
    drop(tx); // 關閉原始發送端
    
    for received in rx {
        println!("收到: {}", received);
    }
    
    // 同步通道 (有界通道)
    println!("\n同步通道:");
    let (tx, rx) = mpsc::sync_channel(2); // 緩衝區大小為 2
    
    thread::spawn(move || {
        for i in 0..5 {
            println!("發送: {}", i);
            tx.send(i).unwrap();
            println!("已發送: {}", i);
        }
    });
    
    thread::sleep(Duration::from_millis(1000));
    
    for received in rx {
        println!("接收: {}", received);
        thread::sleep(Duration::from_millis(200));
    }
    
    // try_recv - 非阻塞接收
    println!("\n非阻塞接收:");
    let (tx, rx) = mpsc::channel();
    
    thread::spawn(move || {
        thread::sleep(Duration::from_millis(500));
        tx.send("延遲訊息").unwrap();
    });
    
    loop {
        match rx.try_recv() {
            Ok(msg) => {
                println!("收到: {}", msg);
                break;
            }
            Err(mpsc::TryRecvError::Empty) => {
                println!("還沒有訊息...");
                thread::sleep(Duration::from_millis(100));
            }
            Err(mpsc::TryRecvError::Disconnected) => {
                println!("通道已關閉");
                break;
            }
        }
    }
    
    // 超時接收
    println!("\n超時接收:");
    let (tx, rx) = mpsc::channel();
    
    thread::spawn(move || {
        thread::sleep(Duration::from_secs(2));
        tx.send("很慢的訊息").unwrap();
    });
    
    match rx.recv_timeout(Duration::from_secs(1)) {
        Ok(msg) => println!("收到: {}", msg),
        Err(_) => println!("接收超時!"),
    }
    
    // 選擇性接收 (使用 select 邏輯)
    println!("\n多通道接收:");
    let (tx1, rx1) = mpsc::channel();
    let (tx2, rx2) = mpsc::channel();
    
    thread::spawn(move || {
        thread::sleep(Duration::from_millis(100));
        tx1.send("通道 1").unwrap();
    });
    
    thread::spawn(move || {
        thread::sleep(Duration::from_millis(200));
        tx2.send("通道 2").unwrap();
    });
    
    // 簡單的輪詢方式
    let mut received_count = 0;
    while received_count < 2 {
        if let Ok(msg) = rx1.try_recv() {
            println!("從通道 1 收到: {}", msg);
            received_count += 1;
        }
        if let Ok(msg) = rx2.try_recv() {
            println!("從通道 2 收到: {}", msg);
            received_count += 1;
        }
        thread::sleep(Duration::from_millis(10));
    }
}
```

## 13. 時間處理

```rust
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};
use std::thread;

fn main() {
    // SystemTime - 系統時間
    let now = SystemTime::now();
    println!("現在時間: {:?}", now);
    
    // Unix 時間戳
    let timestamp = now.duration_since(UNIX_EPOCH)
        .expect("時間錯誤");
    println!("Unix 時間戳 (秒): {}", timestamp.as_secs());
    println!("Unix 時間戳 (毫秒): {}", timestamp.as_millis());
    
    // 時間運算
    let later = now + Duration::from_secs(60);
    println!("一分鐘後: {:?}", later);
    
    let duration_between = later.duration_since(now).unwrap();
    println!("時間差: {:?}", duration_between);
    
    // Instant - 測量經過時間
    println!("\n測量執行時間:");
    let start = Instant::now();
    
    // 模擬一些工作
    let mut sum = 0;
    for i in 0..1_000_000 {
        sum += i;
    }
    
    let elapsed = start.elapsed();
    println!("計算總和: {}", sum);
    println!("花費時間: {:?}", elapsed);
    println!("花費時間 (微秒): {} μs", elapsed.as_micros());
    
    // Duration - 時間長度
    let five_seconds = Duration::from_secs(5);
    let five_millis = Duration::from_millis(5);
    let five_micros = Duration::from_micros(5);
    let five_nanos = Duration::from_nanos(5);
    
    println!("\n不同的 Duration:");
    println!("5 秒 = {:?}", five_seconds);
    println!("5 毫秒 = {:?}", five_millis);
    println!("5 微秒 = {:?}", five_micros);
    println!("5 奈秒 = {:?}", five_nanos);
    
    // Duration 運算
    let total = five_seconds + five_millis;
    println!("5秒 + 5毫秒 = {:?}", total);
    
    let half = five_seconds / 2;
    println!("5秒 / 2 = {:?}", half);
    
    // 自定義 Duration
    let custom = Duration::new(2, 500_000_000); // 2.5 秒
    println!("自定義 2.5 秒 = {:?}", custom);
    
    // 延遲執行
    println!("\n延遲執行:");
    println!("開始...");
    thread::sleep(Duration::from_millis(500));
    println!("500 毫秒後");
    
    // 定時執行
    println!("\n定時執行 (每秒一次，共3次):");
    let mut last_time = Instant::now();
    for i in 1..=3 {
        thread::sleep(Duration::from_secs(1));
        let now = Instant::now();
        let interval = now.duration_since(last_time);
        println!("執行 {} - 間隔: {:?}", i, interval);
        last_time = now;
    }
    
    // 超時檢查
    println!("\n超時檢查:");
    let operation_start = Instant::now();
    let timeout = Duration::from_millis(100);
    
    loop {
        // 模擬某個操作
        thread::sleep(Duration::from_millis(20));
        
        if operation_start.elapsed() > timeout {
            println!("操作超時!");
            break;
        }
        println!("操作進行中...");
    }
    
    // 比較時間
    let time1 = SystemTime::now();
    thread::sleep(Duration::from_millis(10));
    let time2 = SystemTime::now();
    
    if time2 > time1 {
        println!("\ntime2 比 time1 晚");
    }
    
    // 檢查是否經過特定時間
    let deadline = Instant::now() + Duration::from_millis(50);
    while Instant::now() < deadline {
        // 等待直到期限
    }
    println!("已達到期限");
}
```

## 14. 路徑處理

```rust
use std::path::{Path, PathBuf};
use std::env;

fn main() {
    // Path - 不可變路徑
    let path = Path::new("/home/user/documents/file.txt");
    
    println!("路徑: {:?}", path);
    println!("是否存在: {}", path.exists());
    println!("是否為檔案: {}", path.is_file());
    println!("是否為目錄: {}", path.is_dir());
    println!("是否為絕對路徑: {}", path.is_absolute());
    
    // 路徑組件
    println!("\n路徑組件:");
    println!("父目錄: {:?}", path.parent());
    println!("檔名: {:?}", path.file_name());
    println!("檔名主幹: {:?}", path.file_stem());
    println!("副檔名: {:?}", path.extension());
    
    // 迭代路徑組件
    print!("所有組件: ");
    for component in path.components() {
        print!("{:?} ", component);
    }
    println!();
    
    // PathBuf - 可變路徑
    let mut path_buf = PathBuf::new();
    path_buf.push("/home");
    path_buf.push("user");
    path_buf.push("documents");
    println!("\n建構路徑: {:?}", path_buf);
    
    // 添加檔名
    path_buf.push("report.txt");
    println!("加入檔名: {:?}", path_buf);
    
    // 修改副檔名
    path_buf.set_extension("pdf");
    println!("改變副檔名: {:?}", path_buf);
    
    // 修改檔名
    path_buf.set_file_name("final_report.pdf");
    println!("改變檔名: {:?}", path_buf);
    
    // pop 移除最後一個組件
    path_buf.pop();
    println!("移除檔名後: {:?}", path_buf);
    
    // 從字串創建
    let path_str = "data/images/photo.jpg";
    let path_from_str = PathBuf::from(path_str);
    println!("\n從字串創建: {:?}", path_from_str);
    
    // 連接路徑
    let base = Path::new("home/user");
    let full = base.join("downloads").join("file.zip");
    println!("\n連接路徑: {:?}", full);
    
    // 當前目錄
    match env::current_dir() {
        Ok(path) => println!("\n當前目錄: {:?}", path),
        Err(e) => println!("無法取得當前目錄: {}", e),
    }
    
    // 相對路徑轉絕對路徑
    let relative = Path::new("./src/main.rs");
    if let Ok(absolute) = relative.canonicalize() {
        println!("絕對路徑: {:?}", absolute);
    }
    
    // 家目錄
    if let Some(home) = env::var_os("HOME") {
        let home_path = PathBuf::from(home);
        println!("\n家目錄: {:?}", home_path);
        
        // 建構家目錄下的路徑
        let config = home_path.join(".config").join("myapp");
        println!("設定目錄: {:?}", config);
    }
    
    // 路徑比較
    let path1 = Path::new("/home/user/file.txt");
    let path2 = Path::new("/home/user/../user/file.txt");
    println!("\n路徑相等: {}", path1 == path2);
    
    // strip_prefix - 移除前綴
    let full_path = Path::new("/home/user/documents/report.pdf");
    let base_path = Path::new("/home/user");
    
    match full_path.strip_prefix(base_path) {
        Ok(relative) => println!("相對路徑: {:?}", relative),
        Err(e) => println!("錯誤: {}", e),
    }
    
    // 檢查是否有特定副檔名
    let file = Path::new("image.png");
    let is_image = match file.extension() {
        Some(ext) => ext == "png" || ext == "jpg" || ext == "gif",
        None => false,
    };
    println!("\n是圖片檔案: {}", is_image);
    
    // 建立多層目錄路徑
    let deep_path = PathBuf::from("level1")
        .join("level2")
        .join("level3")
        .join("file.txt");
    println!("\n多層路徑: {:?}", deep_path);
    
    // 取得所有祖先路徑
    println!("\n祖先路徑:");
    for ancestor in deep_path.ancestors() {
        println!("  {:?}", ancestor);
    }
}
```

## 15. 環境變數和命令列參數

```rust
use std::env;
use std::process;

fn main() {
    // 命令列參數
    let args: Vec<String> = env::args().collect();
    
    println!("程式路徑: {}", &args[0]);
    println!("參數數量: {}", args.len());
    
    if args.len() > 1 {
        println!("\n命令列參數:");
        for (i, arg) in args.iter().enumerate() {
            println!("  參數[{}]: {}", i, arg);
        }
    } else {
        println!("\n沒有額外的命令列參數");
        println!("試試: cargo run -- arg1 arg2 arg3");
    }
    
    // 簡單的命令列解析
    if args.len() > 1 {
        match args[1].as_str() {
            "--help" | "-h" => {
                println!("\n幫助資訊:");
                println!("用法: {} [選項]", args[0]);
                println!("選項:");
                println!("  --help, -h    顯示此幫助");
                println!("  --version     顯示版本");
            }
            "--version" => {
                println!("版本 1.0.0");
            }
            _ => {
                println!("未知選項: {}", args[1]);
            }
        }
    }
    
    // 環境變數 - 讀取
    println!("\n=== 環境變數 ===");
    
    // 讀取特定環境變數
    match env::var("PATH") {
        Ok(val) => {
            println!("PATH 環境變數 (前100字元): {}...", &val[..100.min(val.len())]);
        }
        Err(e) => println!("無法讀取 PATH: {}", e),
    }
    
    // 讀取 HOME 或 USERPROFILE (跨平台)
    let home = env::var("HOME")
        .or_else(|_| env::var("USERPROFILE"))
        .unwrap_or_else(|_| String::from("未找到"));
    println!("家目錄: {}", home);
    
    // 設定環境變數
    env::set_var("MY_APP_CONFIG", "debug");
    println!("\n設定 MY_APP_CONFIG = debug");
    
    // 讀取剛設定的變數
    if let Ok(val) = env::var("MY_APP_CONFIG") {
        println!("MY_APP_CONFIG = {}", val);
    }
    
    // 移除環境變數
    env::remove_var("MY_APP_CONFIG");
    println!("移除 MY_APP_CONFIG");
    
    // 檢查變數是否存在
    if env::var("MY_APP_CONFIG").is_err() {
        println!("MY_APP_CONFIG 已不存在");
    }
    
    // 迭代所有環境變數 (顯示前5個)
    println!("\n前 5 個環境變數:");
    for (key, value) in env::vars().take(5) {
        println!("  {} = {}", key, value);
    }
    
    // 當前工作目錄
    match env::current_dir() {
        Ok(path) => println!("\n當前工作目錄: {:?}", path),
        Err(e) => println!("錯誤: {}", e),
    }
    
    // 改變當前目錄
    if let Ok(home_dir) = env::var("HOME") {
        if env::set_current_dir(&home_dir).is_ok() {
            println!("已切換到家目錄");
            if let Ok(new_dir) = env::current_dir() {
                println!("新的工作目錄: {:?}", new_dir);
            }
        }
    }
    
    // 取得執行檔路徑
    match env::current_exe() {
        Ok(path) => println!("\n執行檔路徑: {:?}", path),
        Err(e) => println!("錯誤: {}", e),
    }
    
    // 系統相關資訊
    println!("\n=== 系統資訊 ===");
    println!("作業系統: {}", env::consts::OS);
    println!("架構: {}", env::consts::ARCH);
    println!("系列: {}", env::consts::FAMILY);
    
    // 實用範例：設定檔路徑
    let config_path = env::var("CONFIG_PATH")
        .unwrap_or_else(|_| String::from("./config.toml"));
    println!("\n設定檔路徑: {}", config_path);
    
    // 實用範例：除錯模式
    let debug_mode = env::var("DEBUG")
        .map(|v| v == "1" || v.to_lowercase() == "true")
        .unwrap_or(false);
    println!("除錯模式: {}", debug_mode);
    
    // 實用範例：連接埠設定
    let port = env::var("PORT")
        .ok()
        .and_then(|p| p.parse::<u16>().ok())
        .unwrap_or(8080);
    println!("伺服器埠: {}", port);
    
    // 結束程式 (可選)
    if args.len() > 1 && args[1] == "--exit" {
        println!("\n使用 --exit 參數，程式結束");
        process::exit(0);
    }
}
```

## 16. 格式化輸出和 Display/Debug

```rust
use std::fmt;

// 自定義結構體
#[derive(Debug)]
struct Point {
    x: i32,
    y: i32,
}

// 實作 Display
impl fmt::Display for Point {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

// 另一個結構體
struct Color {
    red: u8,
    green: u8,
    blue: u8,
}

impl fmt::Display for Color {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "RGB({}, {}, {})", self.red, self.green, self.blue)
    }
}

impl fmt::Debug for Color {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Color {{ r: {:#x}, g: {:#x}, b: {:#x} }}", 
               self.red, self.green, self.blue)
    }
}

fn main() {
    // 基本格式化
    println!("=== 基本格式化 ===");
    println!("字串: {}", "Hello, Rust!");
    println!("整數: {}", 42);
    println!("浮點數: {}", 3.14159);
    println!("布林值: {}", true);
    
    // 位置參數
    println!("\n=== 位置參數 ===");
    println!("{0} {1} {0}", "Hello", "World");
    println!("{1} {0} {1}", "World", "Hello");
    
    // 命名參數
    println!("\n=== 命名參數 ===");
    println!("{name} 今年 {age} 歲", name="小明", age=25);
    println!("{subject} {verb} {object}", 
             subject="貓", verb="追", object="老鼠");
    
    // 格式化規格
    println!("\n=== 數字格式化 ===");
    let num = 42;
    println!("十進制: {}", num);
    println!("二進制: {:b}", num);
    println!("八進制: {:o}", num);
    println!("十六進制 (小寫): {:x}", num);
    println!("十六進制 (大寫): {:X}", num);
    println!("帶前綴十六進制: {:#x}", num);
    
    // 寬度和對齊
    println!("\n=== 寬度和對齊 ===");
    println!("'{:5}'", "Hi");        // 右對齊，寬度5
    println!("'{:<5}'", "Hi");       // 左對齊
    println!("'{:^5}'", "Hi");       // 置中
    println!("'{:>5}'", "Hi");       // 右對齊
    println!("'{:*<5}'", "Hi");      // 左對齊，用*填充
    println!("'{:=>5}'", 7);         // 右對齊，用=填充
    println!("'{:0>5}'", 42);        // 用0填充
    
    // 浮點數精度
    println!("\n=== 浮點數精度 ===");
    let pi = 3.141592653589793;
    println!("預設: {}", pi);
    println!("2位小數: {:.2}", pi);
    println!("5位小數: {:.5}", pi);
    println!("寬度10，3位小數: {:10.3}", pi);
    println!("科學記號: {:e}", pi);
    println!("科學記號 (大寫): {:E}", pi);
    
    // 正負號
    println!("\n=== 正負號 ===");
    println!("正數: {:+}", 42);
    println!("負數: {:+}", -42);
    println!("前導空格: {: }", 42);
    println!("前導空格: {: }", -42);
    
    // Debug 和 Display
    println!("\n=== Debug vs Display ===");
    let point = Point { x: 10, y: 20 };
    println!("Display: {}", point);
    println!("Debug: {:?}", point);
    println!("Pretty Debug: {:#?}", point);
    
    let color = Color { red: 128, green: 255, blue: 64 };
    println!("\nColor Display: {}", color);
    println!("Color Debug: {:?}", color);
    
    // 複雜結構的 Debug
    let complex = vec![
        Point { x: 1, y: 2 },
        Point { x: 3, y: 4 },
        Point { x: 5, y: 6 },
    ];
    println!("\n複雜結構 Debug: {:?}", complex);
    println!("複雜結構 Pretty: {:#?}", complex);
    
    // format! 巨集
    println!("\n=== format! 巨集 ===");
    let formatted = format!("Point: x={}, y={}", 10, 20);
    println!("格式化字串: {}", formatted);
    
    // 其他格式化巨集
    print!("不換行輸出 ");
    print!("繼續 ");
    println!("換行");
    
    eprint!("錯誤輸出 ");
    eprintln!("(到 stderr)");
    
    // 條件格式化
    println!("\n=== 條件格式化 ===");
    let value = Some(42);
    println!("Option: {:?}", value);
    
    let result: Result<i32, &str> = Ok(100);
    println!("Result: {:?}", result);
    
    // 跳脫字元
    println!("\n=== 跳脫字元 ===");
    println!("換行：第一行\n第二行");
    println!("Tab：欄位1\t欄位2\t欄位3");
    println!("引號：\"雙引號\" \'單引號\'");
    println!("反斜線：\\");
    println!("Unicode：\u{1F980}"); // 🦀
    
    // 自定義格式化輸出
    println!("\n=== 表格式輸出 ===");
    println!("{:<10} {:<10} {:<10}", "Name", "Age", "City");
    println!("{:-<30}", "");
    println!("{:<10} {:<10} {:<10}", "Alice", 25, "Taipei");
    println!("{:<10} {:<10} {:<10}", "Bob", 30, "Tokyo");
    println!("{:<10} {:<10} {:<10}", "Charlie", 35, "NYC");
}
    