# C++ vs. Rust: 全面特性比較

本文檔旨在全面比較 C++ 和 Rust 這兩種高效能系統程式語言的關鍵特性。C++ 以其悠久的歷史、強大的生態系統和對硬體的精細控制而聞名，而 Rust 則以其創新的所有權系統、對記憶體安全和併發安全的編譯期保證而備受關注。

每個範例都提供可直接編譯和執行的程式碼。

## 1. 記憶體管理

這是兩種語言最根本的區別。C++ 依賴手動管理和智慧指標，而 Rust 引入了所有權系統。

### C++: RAII 與智慧指標

C++ 透過 RAII (Resource Acquisition Is Initialization) 模式管理資源。現代 C++ 強烈推薦使用智慧指標 (`std::unique_ptr`, `std::shared_ptr`) 來自動化記憶體管理，避免手動 `new` 和 `delete`。

**範例 (`main.cpp`):**
```cpp
#include <iostream>
#include <memory>
#include <string>

class Entity {
private:
    std::string name;
public:
    Entity(const std::string& name) : name(name) {
        std::cout << "Entity '" << name << "' created." << std::endl;
    }
    ~Entity() {
        std::cout << "Entity '" << name << "' destroyed." << std::endl;
    }
    void greet() {
        std::cout << "Hello, I am " << name << "." << std::endl;
    }
};

int main() {
    // 使用 unique_ptr，當 ptr 離開作用域時，記憶體會被自動釋放
    auto ptr = std::make_unique<Entity>("Player1");
    ptr->greet();
    
    // 不需要手動 delete ptr;
    return 0;
}
```

**編譯與執行:**
```bash
g++ main.cpp -o main_cpp -std=c++17
./main_cpp
```

### Rust: 所有權、借用與生命週期

Rust 的核心是其所有權系統，它在編譯期強制執行記憶體安全規則：
1.  每個值都有一個擁有者（owner）。
2.  同一時間只能有一個擁有者。
3.  當擁有者離開作用域時，值會被丟棄（dropped）。

可以透過「借用」（borrowing）來臨時參考一個值，而不會轉移所有權。

**範例 (`main.rs`):**
```rust
struct Entity {
    name: String,
}

impl Entity {
    fn new(name: &str) -> Self {
        println!("Entity '{}' created.", name);
        Self { name: name.to_string() }
    }

    fn greet(&self) {
        println!("Hello, I am {}.", self.name);
    }
}

impl Drop for Entity {
    fn drop(&mut self) {
        println!("Entity '{}' destroyed.", self.name);
    }
}

fn main() {
    // e 擁有 Entity 的所有權
    let e = Entity::new("Player1");
    e.greet();
    
    // 當 main 函式結束時，e 離開作用域，其擁有的資源會被自動釋放
}
```

**編譯與執行:**
```bash
rustc main.rs -o main_rs
./main_rs
```

---

## 2. 資料型別 (Structs & Enums)

### C++: Structs 與 Enum Classes

C++ 的 `struct` 用於組合資料。`enum class` 是現代 C++ 中推薦的列舉類型，因為它提供了型別安全。

**範例 (`main.cpp`):**
```cpp
#include <iostream>

struct Point {
    double x;
    double y;
};

enum class Color {
    Red,
    Green,
    Blue
};

void print_color(Color c) {
    switch(c) {
        case Color::Red:
            std::cout << "Color is Red" << std::endl;
            break;
        case Color::Green:
            std::cout << "Color is Green" << std::endl;
            break;
        case Color::Blue:
            std::cout << "Color is Blue" << std::endl;
            break;
    }
}

int main() {
    Point p = {10.5, 20.3};
    std::cout << "Point: (" << p.x << ", " << p.y << ")" << std::endl;
    
    Color c = Color::Green;
    print_color(c);
    
    return 0;
}
```

**編譯與執行:**
```bash
g++ main.cpp -o main_cpp -std=c++17
./main_cpp
```

### Rust: Structs 與強大的 Enums (代數資料型別)

Rust 的 `struct` 與 C++ 類似。然而，Rust 的 `enum` 是功能強大的代數資料型別（Sum Types），每個變體都可以攜帶不同型別和數量的資料。`match` 控制流程運算式是處理 `enum` 的理想方式。

**範例 (`main.rs`):**
```rust
struct Point {
    x: f64,
    y: f64,
}

// Rust 的 enum 可以包含資料
enum Shape {
    Circle(Point, f64), // 中心點和半徑
    Rectangle(Point, Point), // 左上角和右下角點
}

impl Shape {
    fn area(&self) -> f64 {
        match self {
            Shape::Circle(_, radius) => std::f64::consts::PI * radius * radius,
            Shape::Rectangle(p1, p2) => ((p2.x - p1.x) * (p2.y - p1.y)).abs(),
        }
    }
}

fn main() {
    let p = Point { x: 0.0, y: 0.0 };
    println!("Point: ({}, {})", p.x, p.y);

    let circle = Shape::Circle(Point { x: 0.0, y: 0.0 }, 10.0);
    let rect = Shape::Rectangle(Point { x: 0.0, y: 0.0 }, Point { x: 10.0, y: 20.0 });

    println!("Circle area: {}", circle.area());
    println!("Rectangle area: {}", rect.area());
}
```

**編譯與執行:**
```bash
rustc main.rs -o main_rs
./main_rs
```

---

## 3. 錯誤處理

### C++: 例外 (Exceptions)

C++ 的主要錯誤處理機制是例外。當錯誤發生時，可以 `throw` 一個例外，並在 `try...catch` 區塊中捕獲它。

**範例 (`main.cpp`):**
```cpp
#include <iostream>
#include <stdexcept>

double divide(double a, double b) {
    if (b == 0.0) {
        throw std::runtime_error("Division by zero!");
    }
    return a / b;
}

int main() {
    try {
        double result = divide(10.0, 0.0);
        std::cout << "Result: " << result << std::endl;
    } catch (const std::runtime_error& e) {
        std::cerr << "Error caught: " << e.what() << std::endl;
    }
    return 0;
}
```

**編譯與執行:**
```bash
g++ main.cpp -o main_cpp -std=c++17
./main_cpp
```

### Rust: `Result` 與 `Option` Enums

Rust 沒有例外。它使用 `Result<T, E>` 和 `Option<T>` 這兩個 `enum` 來處理可恢復和不可恢復的錯誤。`Result` 用於可能失敗的操作，`Option` 用於可能為空的值。這使得錯誤處理在型別系統中是明確的。

**範例 (`main.rs`):**
```rust
// 函式返回一個 Result，Ok 包含成功的值，Err 包含錯誤資訊
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err("Division by zero!".to_string())
    } else {
        Ok(a / b)
    }
}

fn main() {
    match divide(10.0, 0.0) {
        Ok(result) => println!("Result: {}", result),
        Err(e) => eprintln!("Error caught: {}", e),
    }
    
    match divide(10.0, 2.0) {
        Ok(result) => println!("Result: {}", result),
        Err(e) => eprintln!("Error caught: {}", e),
    }
}
```

**編譯與執行:**
```bash
rustc main.rs -o main_rs
./main_rs
```

---

## 4. 併發 (Concurrency)

### C++: `std::thread` 與 Mutexes

C++11 引入了標準的執行緒支援。開發者需要手動使用 `std::mutex` 等同步原語來防止資料競爭（Data Races）。

**範例 (`main.cpp`):**
```cpp
#include <iostream>
#include <thread>
#include <vector>
#include <mutex>

std::mutex mtx;
int counter = 0;

void increment() {
    for (int i = 0; i < 10000; ++i) {
        std::lock_guard<std::mutex> lock(mtx); // RAII-style lock
        counter++;
    }
}

int main() {
    std::vector<std::thread> threads;
    for (int i = 0; i < 10; ++i) {
        threads.push_back(std::thread(increment));
    }

    for (auto& th : threads) {
        th.join();
    }

    std::cout << "Final counter: " << counter << std::endl;
    return 0;
}
```

**編譯與執行:**
```bash
g++ main.cpp -o main_cpp -std=c++17 -pthread
./main_cpp
```

### Rust: 安全的併發

Rust 的所有權和借用規則在編譯期就能防止資料競爭。跨執行緒共享資料需要使用 `Arc<Mutex<T>>` (原子引用計數的互斥鎖)，Rust 編譯器會確保你在存取資料前正確地鎖定了互斥鎖。

**範例 (`main.rs`):**
```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    // Arc 用於多所有權，Mutex 用於互斥存取
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter_clone = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter_clone.lock().unwrap(); // 鎖定 Mutex
            for _ in 0..10000 {
                *num += 1;
            }
        }); // Mutex 在這裡自動解鎖
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Final counter: {}", *counter.lock().unwrap());
}
```

**編譯與執行:**
```bash
rustc main.rs -o main_rs
./main_rs
```

---

## 5. 泛型 (Generics)

### C++: 樣板 (Templates)

C++ 使用樣板來實現泛型程式設計。樣板在編譯期進行實體化，非常強大靈活，但錯誤訊息可能很冗長。C++20 引入了 Concepts 來約束樣板參數。

**範例 (`main.cpp`):**
```cpp
#include <iostream>

template<typename T>
void print_value(T value) {
    std::cout << "Value: " << value << std::endl;
}

int main() {
    print_value(42);
    print_value(3.14);
    print_value("Hello C++");
    return 0;
}
```

**編譯與執行:**
```bash
g++ main.cpp -o main_cpp -std=c++17
./main_cpp
```

### Rust: 泛型與 Trait 約束

Rust 的泛型透過 `trait` 來約束。`trait` 類似於介面，定義了泛型型別必須實現的行為。這使得泛型程式碼更安全，錯誤訊息也更清晰。

**範例 (`main.rs`):**
```rust
use std::fmt::Display;

// T 必須實現 Display trait，這樣才能被格式化輸出
fn print_value<T: Display>(value: T) {
    println!("Value: {}", value);
}

fn main() {
    print_value(42);
    print_value(3.14);
    print_value("Hello Rust");
}
```

**編譯與執行:**
```bash
rustc main.rs -o main_rs
./main_rs
```

---

## 6. 可變性 (Mutability)

### C++: 預設可變

在 C++ 中，變數預設是可變的。`const` 關鍵字用於宣告不可變的變數、指標或方法。

**範例 (`main.cpp`):**
```cpp
#include <iostream>

int main() {
    int mutable_var = 10;
    mutable_var = 20; // OK

    const int immutable_var = 30;
    // immutable_var = 40; // 編譯錯誤
    
    std::cout << "mutable_var: " << mutable_var << std::endl;
    std::cout << "immutable_var: " << immutable_var << std::endl;
    return 0;
}
```

**編譯與執行:**
```bash
g++ main.cpp -o main_cpp -std=c++17
./main_cpp
```

### Rust: 預設不可變

在 Rust 中，變數預設是不可變的。必須使用 `mut` 關鍵字來明確宣告一個變數是可變的。這有助於編寫更安全、更易於推理的程式碼。

**範例 (`main.rs`):**
```rust
fn main() {
    let immutable_var = 10;
    // immutable_var = 20; // 編譯錯誤

    let mut mutable_var = 30;
    mutable_var = 40; // OK

    println!("immutable_var: {}", immutable_var);
    println!("mutable_var: {}", mutable_var);
}
```

**編譯與執行:**
```bash
rustc main.rs -o main_rs
./main_rs
```

---

## 7. 巨集 (Macros)

### C++: 前置處理器巨集

C++ 的巨集由前置處理器處理，基本上是文字替換。功能強大但缺乏型別安全，且容易產生意想不到的副作用。

**範例 (`main.cpp`):**
```cpp
#include <iostream>

#define SQUARE(x) ((x) * (x))

int main() {
    int a = 5;
    std::cout << "Square of 5 is " << SQUARE(a) << std::endl;
    // 容易出錯的例子: SQUARE(2 + 3) -> ((2 + 3) * (2 + 3)) -> 25 (正確)
    // 如果定義為 #define SQUARE(x) x * x, 則 SQUARE(2+3) -> 2+3*2+3 -> 11 (錯誤)
    return 0;
}
```

**編譯與執行:**
```bash
g++ main.cpp -o main_cpp -std=c++17
./main_cpp
```

### Rust: 程序化與宣告式巨集

Rust 的巨集系統更先進，是語法層面的抽象，直接操作 AST（抽象語法樹）。它們是衛生的（Hygienic），避免了變數名稱衝突，並且型別安全。

**範例 (`main.rs`):**
```rust
// 宣告式巨集
macro_rules! create_function {
    ($func_name:ident, $output:expr) => {
        fn $func_name() {
            println!("{}", $output);
        }
    };
}

// 使用巨集來建立一個函式
create_function!(say_hello, "Hello from a macro!");

fn main() {
    // 呼叫由巨集產生的函式
    say_hello();
}
```

**編譯與執行:**
```bash
rustc main.rs -o main_rs
./main_rs
```

---

## 8. 建置系統與套件管理

### C++: 破碎的生態系

C++ 沒有官方統一的建置系統或套件管理器。`CMake` 是事實上的標準建置系統，但學習曲線陡峭。套件管理通常依賴 `Conan`、`vcpkg` 或手動管理。

**典型流程 (CMake):**
1.  撰寫 `CMakeLists.txt`。
2.  `mkdir build && cd build`
3.  `cmake ..`
4.  `make`

### Rust: Cargo - 整合式工具鏈

Rust 內建了 `Cargo`，一個極其強大的建置系統和套件管理器。它處理：
*   專案建立 (`cargo new`)
*   建置 (`cargo build`)
*   執行 (`cargo run`)
*   測試 (`cargo test`)
*   文件產生 (`cargo doc`)
*   依賴管理 (透過 `Cargo.toml`)
*   發布到 `crates.io` (`cargo publish`)

**典型流程 (Cargo):**
1.  `cargo new my_project`
2.  `cd my_project`
3.  (在 `Cargo.toml` 中加入依賴)
4.  `cargo run`

---

## 結論

| 特性 | C++ | Rust |
| :--- | :--- | :--- |
| **核心哲學** | 你不為你不使用的東西付費，信任程式設計師 | 安全性、併發性、效能，不信任程式設計師 |
| **記憶體管理** | 手動、RAII、智慧指標 | 所有權、借用、生命週期 (編譯期保證) |
| **安全性** | 容易出現未定義行為 (懸垂指標、緩衝區溢位) | 記憶體安全和執行緒安全 (編譯期保證) |
| **錯誤處理** | 例外 (Exceptions) | `Result` 和 `Option` Enums |
| **併發** | 手動鎖定，容易出錯 | 無資料競爭的併發 (編譯期保證) |
| **可變性** | 預設可變 | 預設不可變 |
| **工具鏈** | 破碎 (CMake, Make, Conan, vcpkg...) | 統一且強大 (Cargo) |
| **學習曲線** | 極其陡峭，充滿陷阱 | 陡峭，但主要是所有權系統，一旦掌握就相對平滑 |

**選擇建議:**

*   **選擇 C++**：當你需要與龐大的現有 C++ 程式碼庫整合、利用成熟的 C++ 函式庫生態、或需要進行極低階的硬體操作時。
*   **選擇 Rust**：當你開始一個新專案，且對系統的可靠性、記憶體安全和併發安全有極高要求時。Rust 的現代化工具鏈和強大的編譯期保證可以顯著提高開發效率和軟體品質。
