### 變量聲明和賦值

在Rust中，使用let關鍵字聲明變量，使用等號進行賦值。類型可以自動推斷或顯式指定。

```rust
let x = 10; // 自動推斷類型
let y: f64 = 3.14; // 顯式指定類型
```

在C ++中，使用類型名稱聲明變量，使用等號進行賦值。

```c++
int x = 10;
double y = 3.14;

```

## 整數運算

在Rust中，整數運算符號使用和C ++相同。但是，除法操作符號使用/而不是C ++中的整數除法符號//。

```rust
let x = 10;
let y = 3;
let z = x + y;
let w = x * y;
let q = x / y; // 此處使用/操作符號
```

在C ++中，整數運算符號使用和Rust相同。

```c++
int x = 10;
int y = 3;
int z = x + y;
int w = x * y;
int q = x / y;
```

### 浮點數運算

在Rust中，浮點數運算符號使用和C ++相同。

```rust
let x = 3.14;
let y = 2.71;
let z = x + y;
let w = x * y;
let q = x / y;
```

在C ++中，浮點數運算符號使用和Rust相同。

```c++
double x = 3.14;
double y = 2.71;
double z = x + y;
double w = x * y;
double q = x / y;
```

### 布爾運算

在Rust中，布爾運算符號使用and（&&）和or（||）。

```rust
let x = true;
let y = false;
let z = x && y;
let w = x || y;
```

在C ++中，布爾運算符號使用and（&&）和or（||）。

```c++
bool x = true;
bool y = false;
bool z = x && y;
bool w = x || y;
```

### 條件語句

在Rust中，if / else語句可以作為表達式使用，並且必須包含在大括號內。

```rust
let x = 10;
if x < 5 {
    println!("x is less than 5");
} else {
    println!("x is greater than or equal to 5");
}
```

在C ++中，if / else語句不能作為表達式使用，並且可以省略大括號。

```c++
int x = 10;
if (x < 5) {
    cout << "x is less than 5" << endl;
} else {
    cout << "x is greater than or equal to 5" << endl;
}
```

### 迴圈

迴圈 在Rust中，for循環可用於迭代集合，並且可以使用range運算符號創建集合。

```rust
for i in 0..5 {
    println!("{}", i);
}

let arr = [1, 2, 3, 4, 5];
for i in arr.iter() {
    println!("{}", i);
}
```

在C ++中，for循環可用於迭代集合，並且可以使用range運算符號創建集合。

```cpp
for (int i = 0; i < 5; i++) {
    cout << i << endl;
}

int arr[] = {1, 2, 3, 4, 5};
for (int i : arr) {
    cout << i << endl;
}
```

### 函數定義和調用

在Rust中，函數定義使用fn關鍵字，並且可以指定參數和返回類型。

```rust
fn add(x: i32, y: i32) -> i32 {
    x + y
}

let result = add(2, 3);
```

在C ++中，函數定義使用函數名稱，並且可以指定參數和返回類型。

```cpp
int add(int x, int y) {
    return x + y;
}

int result = add(2, 3);
```

### 字符串處理

在Rust中，字符串是utf8編碼的unicode字符集，使用&str類型表示。

```rust
let s1 = "hello";
let s2 = "world";
let s3 = format!("{} {}", s1, s2);
println!("{}", s3);
```

在C ++中，字符串是char類型的數組，使用std :: string類型表示。

```cpp
#include <string>

std::string s1 = "hello";
std::string s2 = "world";
std::string s3 = s1 + " " + s2;
cout << s3 << endl;
```

### 指標

在Rust中，指針是具有所有權語義的智能指針，使用&和*運算符號。

```rust
let x = 10;
let p = &x;
let y = *p;
```

在C ++中，指針是一個可以存儲變量地址的變量，使用*和&運算符號。

```cpp
int x = 10;
int* p = &x;
int y = *p;
```

### 類別

在Rust中，類是結構體struct和實現trait的組合，使用impl關鍵字實現方法。

```rust
struct Person {
    name: String,
    age: i32,
}

impl Person {
    fn new(name: &str, age: i32) -> Self {
        Person { name: name.to_string(), age }
}

fn say_hello(&self) {
    println!("Hello, my name is {} and I am {} years old.", self.name, self.age);
}
    
let person = Person::new("Alice", 30);
person.say_hello();
```

在C ++中，類是具有成員變量和成員函數的結構，使用class關鍵字定義。

```cpp
#include <iostream>
#include <string>

class Person {
public:
    Person(const std::string& name, int age) : name(name), age(age) {}

    void say_hello() {
        std::cout << "Hello, my name is " << name << " and I am " << age << " years old." << std::endl;
    }

private:
    std::string name;
    int age;
};

Person person("Alice", 30);
person.say_hello();
```

### 命名空間

在C ++中，命名空間是一種將名稱分類為一個範圍的方式，可以避免名稱衝突。

```cpp
namespace math {
    const double PI = 3.14159265358979323846;

    double sin(double x) {
        // ...
    }

    double cos(double x) {
        // ...
    }
}

double x = math::PI;
double y = math::sin(x);
```

在Rust中，沒有傳統意義上的命名空間，但可以使用模塊來組織代碼，並且可以使用pub關鍵字公開模塊內的項目。

```rust
mod math {
    pub const PI: f64 = 3.14159265358979323846;

    pub fn sin(x: f64) -> f64 {
        // ...
    }

    pub fn cos(x: f64) -> f64 {
        // ...
    }
}

let x = math::PI;
let y = math::sin(x);
```

### 結構體

在C ++中，結構體是一種自定義的數據類型，可以包含多個成員變量。

```cpp
struct Point {
    double x;
    double y;
};

Point p = { 1.0, 2.0 };
double x = p.x;
double y = p.y;
```

在Rust中，結構體struct也是一種自定義的數據類型，可以包含多個字段。

```rust
struct Point {
    x: f64,
    y: f64,
}

let p = Point { x: 1.0, y: 2.0 };
let x = p.x;
let y = p.y;
```

### 枚舉

在C ++中，枚舉是一種自定義的數據類型，可以包含多個常量值。

```cpp
enum Color {
    Red,
    Green,
    Blue,
};

Color c = Color::Green;
```

在Rust中，枚舉enum也是一種自定義的數據類型，可以包含多個變體variant。

```rust
enum Color {
    Red,
    Green,
    Blue,
}

let c = Color::Green;
```

### 泛型

在C ++中，泛型是一種將代碼寫成可以處理多種數據類型的方式。

```cpp
template <typename T>
T max(T a, T b) {
    return a > b ? a : b;
}

int x = max(1, 2);
double y = max(1.0, 2.0);
```

在Rust中，泛型是一種類型參數化的方式。

```rust
fn max<T: std::cmp::PartialOrd>(a: T, b: T) -> T {
    if a > b {
        a
    } else {
        b
    }
}

fn main() {
    let x = max(1.0f32, 2.0f32);
    let y = max(1.0f64, 2.0f64);
}
```

### 介面

在Rust中，Trait是一種定義方法簽名的接口。

```rust
trait Animal {
    fn name(&self) -> &'static str;
    fn make_sound(&self) -> &'static str;
}

struct Dog;
impl Animal for Dog {
    fn name(&self) -> &'static str {
        "Dog"
    }

    fn make_sound(&self) -> &'static str {
        "Bark"
    }
}

struct Cat;
impl Animal for Cat {
    fn name(&self) -> &'static str {
        "Cat"
    }

    fn make_sound(&self) -> &'static str {
        "Meow"
    }
}

fn main() {
    let animals: [&dyn Animal; 2] = [&Dog, &Cat];

    for animal in animals.iter() {
        println!("{} says {}", animal.name(), animal.make_sound());
    }
}
```

在C ++中，類似的概念是接口interface。

```cpp
#include <iostream>

class Animal {
public:
    virtual const char* name() = 0;
    virtual const char* make_sound() = 0;
};

class Dog : public Animal {
public:
    const char* name() override { return "Dog"; }
    const char* make_sound() override { return "Bark"; }
};

class Cat : public Animal {
public:
    const char* name() override { return "Cat"; }
    const char* make_sound() override { return "Meow"; }
};

int main() {
    Animal* animals[2] = { new Dog(), new Cat() };

    for (int i = 0; i < 2; i++) {
        std::cout << animals[i]->name() << " says " << animals[i]->make_sound() << std::endl;
    }

    return 0;
}
```

### Ownership and Borrowing

在 Rust 中，每個值都有一個擁有者(Owner)，該擁有者負責管理其值的生命週期，並自動在不再需要該值時銷毀它。

```rust
fn print_string(s: String) {
    println!("{}", s);
}

fn main() {
    let s = String::from("Hello, Rust!");

    print_string(s);

    // s has been moved and is no longer valid
    // println!("{}", s); // error: use of moved value: `s`
}
```

在C++中，類似的概念是對象的所有權(Ownership)，但是C++沒有自動回收機制，因此需要使用智能指針等手段來管理資源的生命週期。

```cpp
#include <iostream>
#include <memory>
#include <string>

void print_string(const std::string& s) {
    std::cout << s << std::endl;
}

int main() {
    std::unique_ptr<std::string> s = std::make_unique<std::string>("Hello, C++!");

    print_string(*s);

    // s will be automatically destroyed when it goes out of scope
    return 0;
}
```

在 Rust 中，為了避免所有權所有權被移動，可以使用引用(Reference)。引用是對某個值的參考，而不擁有該值本身。

```rust
fn print_string(s: &String) {
    println!("{}", s);
}

fn main() {
    let s = String::from("Hello, Rust!");

    print_string(&s);

    // s is still valid
    println!("{}", s);
}
```

在C++中，引用與Rust中的引用類似，但在C++中引用是非空的，而且可以在函數中更改值。

```cpp
#include <iostream>
#include <string>

void print_string(const std::string& s) {
    std::cout << s << std::endl;
}

int main() {
    std::string s = "Hello, C++!";

    print_string(s);

    // s is still valid
    std::cout << s << std::endl;

    return 0;
}
```

在Rust中，為了同時允許讀取和寫入某個值，可以使用可變引用(Mutable Reference)。

```rust
fn add_one(mut x: &mut i32) {
    *x += 1;
}

fn main() {
    let mut x = 0;

    add_one(&mut x);

    // x is now 1
    println!("{}", x);
}
```

在C++中，類似的概念是指針(Pointer)。指針是一種特殊的變數，其值是另一個變數的地址。

```cpp
#include <iostream>

void add_one(int* x) {
    (*x)++;
}

int main() {
    int x = 0;

    add_one(&x);

    // x is now 1
    std::cout << x << std::endl;

    return 0;
}
```

### Pattern Matching

在 Rust 中，可以使用模式匹配(Pattern Matching)來進行分支處理。模式匹配可以用於匹配不同類型的值，比如整數、枚舉、結構體、元組等。

```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
}

fn handle_message(msg: Message) {
    match msg {
        Message::Quit => println!("Quit"),
        Message::Move { x, y } => println!("Move to ({}, {})", x, y),
        Message::Write(text) => println!("Write '{}'", text),
    }
}

fn main() {
    let msg1 = Message::Quit;
    let msg2 = Message::Move { x: 10, y: 20 };
    let msg3 = Message::Write(String::from("Hello"));

    handle_message(msg1);
    handle_message(msg2);
    handle_message(msg3);
}
```

在C++中，也可以使用switch語句來進行分支處理，但是switch語句只能匹配整數值。

```cpp
#include <iostream>
#include <string>

enum class Message { Quit, Move, Write };

struct MoveMessage {
    int x, y;
};

void handle_message(Message msg) {
    switch (msg) {
        case Message::Quit:
            std::cout << "Quit" << std::endl;
            break;
        case Message::Move:
            {
                MoveMessage move_msg = {10, 20};
                std::cout << "Move to (" << move_msg.x << ", " << move_msg.y << ")" << std::endl;
            }
            break;
        case Message::Write:
            std::cout << "Write 'Hello'" << std::endl;
            break;
    }
}

int main() {
    Message msg1 = Message::Quit;
    Message msg2 = Message::Move;
    Message msg3 = Message::Write;

    handle_message(msg1);
    handle_message(msg2);
    handle_message(msg3);

    return 0;
}
```

在Rust中，模式匹配也可以用於解構(Deconstruction)元組和結構體。

```rust
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let point = Point { x: 10, y: 20 };

    match point {
        Point { x, y } => println!("({}, {})", x, y),
    }

    let tuple = (1, "hello");

    match tuple {
        (i, s) => println!("({}, {})", i, s),
    }
}
```

在C++中，也可以使用解構來獲取元組和結構體的成員。

```cpp
#include <iostream>
#include <tuple>
#include <string>

struct Point {
    int x, y;
};

int main() {
    Point point = {10, 20};
    std::tie(std::ignore, std::ignore, point.y) = point;

    std::cout << "(" << point.x << ", " << point.y << ")" << std::endl;

    std::tuple<int, std::string> tuple = std::make_tuple(1, "hello");
    int i;
    std::string s;
    std::tie(i, s) = tuple;

    std::cout << "(" << i << ", " << s << ")" << std::endl;

    return 0;
}
```

### 智能指針

Rust 中有三種智能指針：Box、Rc、Arc。

Box<T> 表示一個指向堆上的 T 類型值的指針，它是唯一所有權的。Box<T> 主要用於解決擁有大量資料或者需要在運行時創建出來的資料的所有權問題。Box<T> 的內存佈局和指針類似，只是多了一個 vtable 指向 T 的方法表。

```rust
fn main() {
    let x = Box::new(42);

    println!("{}", x);
}
```

在 C++ 中也有智能指針，主要有 unique_ptr、shared_ptr 和 weak_ptr。

unique_ptr<T> 表示一個唯一所有權的指針，它負責釋放 T 類型對象的內存。unique_ptr<T> 可以通過 move 轉移所有權，也可以使用 std::move 函數轉移所有權。

```cpp
#include <iostream>
#include <memory>

int main() {
    std::unique_ptr<int> x(new int(42));

    std::cout << *x << std::endl;

    return 0;
}
```

shared_ptr<T> 表示一個共享所有權的指針，多個 shared_ptr<T> 可以指向同一個 T 類型對象，它們共享 T 類型對象的所有權。shared_ptr<T> 使用引用計數的方式來實現所有權管理，當引用計數為 0 時，shared_ptr<T> 會自動釋放對象的內存。

```c++
#include <iostream>
#include <memory>

int main() {
    std::shared_ptr<int> x(new int(42));

    std::cout << *x << std::endl;

    return 0;
}
```

weak_ptr<T> 表示一個弱引用指針，它不擁有對 T 類型對象的所有權，可以從一個 shared_ptr<T> 構造出來。

```cpp
#include <iostream>
#include <memory>

int main() {
    std::shared_ptr<int> x(new int(42));
    std::weak_ptr<int> y(x);

    std::cout << *x << std::endl;
    std::cout << *y.lock() << std::endl;

    return 0;
}
```

### Trait 和 Interface

在 Rust 中，Trait 是一個定義方法的集合，可以實現多態性。一個類型可以實現多個 Trait，實現 Trait 的類型必須實現 Trait 中定義的方法。Trait 可以與泛型一起使用，讓函數和類型更加通用。

```rust
trait Printable {
    fn print(&self);
}

struct Point {
    x: i32,
    y: i32,
}

impl Printable for Point {
    fn print(&self) {
        println!("({}, {})", self.x, self.y);
    }
}

fn print_all<T: Printable>(list: Vec<T>) {
    for item in list {
        item.print();
    }
}

fn main() {
    let list = vec![Point { x: 1, y: 2 }, Point { x: 3, y: 4 }];
    print_all(list);
}
```

在 C++ 中，Interface 是一個包含純虛函數的抽象基類，純虛函數沒有實現，需要子類實現。Interface 可以實現多態性，也可以與泛型一起使用，讓函數和類型更加通用。

```cpp
#include <iostream>
#include <vector>

class Printable {
public:
    virtual void print() = 0;
};

class Point : public Printable {
public:
    Point(int x, int y) : x(x), y(y) {}

    void print() override {
        std::cout << "(" << x << ", " << y << ")" << std::endl;
    }

private:
    int x, y;
};

template<typename T>
void print_all(std::vector<T>& list) {
    for (auto& item : list) {
        item.print();
    }
}

int main() {
    std::vector<Point> list = { Point(1, 2), Point(3, 4) };
    print_all(list);

    return 0;
}
```

### OO

Rust 支持面向對象編程，但與 C++ 相比，其面向對象特性較為簡化。Rust 的結構體可以包含方法，但是不能繼承和多態，也沒有 C++ 中的訪問控制和友元等機制。

```rust
struct Circle {
    x: f64,
    y: f64,
    radius: f64,
}

impl Circle {
    fn area(&self) -> f64 {
        std::f64::consts::PI * (self.radius * self.radius)
    }
}

fn main() {
    let c = Circle { x: 0.0, y: 0.0, radius: 2.0 };
    println!("The area of the circle is {}", c.area());
}
```

C++ 

```cpp
#include <iostream>
#include <cmath>

class Circle {
private:
    double x;
    double y;
    double radius;

public:
    Circle(double _x, double _y, double _r) : x(_x), y(_y), radius(_r) {}

    double area() {
        return M_PI * (radius * radius);
    }
};

int main() {
    Circle c(0.0, 0.0, 2.0);
    std::cout << "The area of the circle is " << c.area() << std::endl;
    return 0;
}
```

### 異常處理

Rust 和 C++ 都支援異常處理，但是 Rust 推崇使用 Result 類型來處理錯誤，而 C++ 則常常使用 try-catch 塊來捕獲和處理異常。

```rust
use std::fs::File;
use std::io::prelude::*;
use std::io::Error;

fn read_file(path: &str) -> Result<String, Error> {
    let mut file = File::open(path)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    Ok(contents)
}

fn main() {
    let path = "test.txt";
    match read_file(path) {
        Ok(contents) => println!("The contents of the file are:\n{}", contents),
        Err(err) => eprintln!("Error reading file: {}", err),
    }
}
```

```cpp
#include <iostream>
#include <fstream>

void read_file(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error("Error opening file");
    }
    std::string line;
    while (getline(file, line)) {
        std::cout << line << std::endl;
    }
}

int main() {
    std::string path = "test.txt";
    try {
        read_file(path);
    } catch (const std::exception& e) {
        std::cerr << "Exception caught: " << e.what() << std::endl;
    }
    return 0;
}
```

