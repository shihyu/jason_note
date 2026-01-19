# C++ Move 語意完整指南

## 什麼是 Move 語意？

Move 語意是 C++11 引入的重要特性，用於避免不必要的複製操作，提升程式效能。`std::move` 本身不會移動任何東西，而是將左值轉換為右值引用，告訴編譯器可以安全地「竊取」物件的資源。

## 核心概念

### 基本原理
- **複製語意**：建立物件的完整副本（兩個物件都有完整資料）
- **移動語意**：轉移物件的資源（只有一個物件擁有資料）
- **右值引用**：`std::move` 將左值轉換為右值引用，啟用移動語意

### 一定要提右值嗎？
是。移動語意是透過「右值引用 + 重載解析」觸發的：`std::move` 只是把左值轉成右值引用，讓 `T&&` 的移動建構/賦值被選中；不提右值會讓讀者誤解「move 是魔法」。

### 白話說明 + 示意圖
白話：`std::move(x)` 不會搬東西，它只是舉手說「這個 x 可以被搬走」。真正搬不搬，要看你有沒有寫/使用到 `T&&` 的移動建構或移動賦值。

示意圖：
```
        lvalue x
           |
           | std::move(x)  (只是轉型/表態)
           v
        rvalue ref (T&&)
           |
           | overload resolution
           v
   move ctor / move assign
```

對照：
```
T&   -> copy ctor / copy assign
T&&  -> move ctor / move assign
```

小例子：
```cpp
struct X {
    X() = default;
    X(const X&) { std::cout << "copy\n"; }
    X(X&&) { std::cout << "move\n"; }
};

void use(X& )  { X y = X{}; (void)y; }    // 這裡只示意 T& 版本存在
void use(X&&)  { X y = X{}; (void)y; }    // 這裡只示意 T&& 版本存在

int main() {
    X a;
    use(a);            // T& 版本
    use(std::move(a)); // T&& 版本
}
```

### 移動 vs 複製

| 操作 | 複製 | 移動 |
|------|------|------|
| **資源分配** | 新分配記憶體 | 轉移現有資源 |
| **效能** | 較慢（需要深拷貝） | 較快（只改變指標） |
| **原物件狀態** | 保持不變 | 可能變為空狀態 |
| **適用場景** | 需要保留原物件 | 不再需要原物件 |

## 基本語法和範例

### 1. 字串移動
```cpp
#include <iostream>
#include <string>

void string_move_example() {
    std::string str1 = "Hello, World!";
    std::cout << "移動前 str1: " << str1 << std::endl;
    
    // 移動語意
    std::string str2 = std::move(str1);
    
    std::cout << "移動後 str1: '" << str1 << "' (通常為空)" << std::endl;
    std::cout << "移動後 str2: '" << str2 << "'" << std::endl;
}
```

### 2. 容器移動
```cpp
#include <vector>

void vector_move_example() {
    std::vector<int> vec1 = {1, 2, 3, 4, 5};
    std::cout << "移動前 vec1 大小: " << vec1.size() << std::endl;
    
    // 移動整個向量
    std::vector<int> vec2 = std::move(vec1);
    
    std::cout << "移動後 vec1 大小: " << vec1.size() << std::endl;  // 通常為 0
    std::cout << "移動後 vec2 大小: " << vec2.size() << std::endl;  // 5
}
```

### 3. 自定義類別的移動
```cpp
#include <iostream>
#include <string>

class Person {
public:
    Person(std::string name) : name_(std::move(name)) {
        std::cout << "建構: " << name_ << std::endl;
    }
    
    // 複製建構函數
    Person(const Person& other) : name_(other.name_) {
        std::cout << "複製建構: " << name_ << std::endl;
    }
    
    // 移動建構函數
    Person(Person&& other) noexcept : name_(std::move(other.name_)) {
        std::cout << "移動建構: " << name_ << std::endl;
    }
    
    ~Person() {
        std::cout << "解構: " << name_ << std::endl;
    }
    
    const std::string& getName() const { return name_; }
    
private:
    std::string name_;
};

void class_move_example() {
    Person person1("Alice");
    
    // 複製 vs 移動比較
    Person person2 = person1;              // 複製建構
    Person person3 = std::move(person1);   // 移動建構
    
    std::cout << "person1: '" << person1.getName() << "'" << std::endl;
    std::cout << "person2: '" << person2.getName() << "'" << std::endl;
    std::cout << "person3: '" << person3.getName() << "'" << std::endl;
}
```

## 實際應用場景

### 1. 函數參數傳遞
```cpp
// 接受字串參數的函數
void processString(std::string str) {
    std::cout << "處理: " << str << std::endl;
    // 對字串進行處理...
}

void function_parameter_example() {
    std::string text = "重要資料";
    
    // 方法1: 複製傳遞（text 保持不變）
    processString(text);
    std::cout << "複製後 text: " << text << std::endl;
    
    // 方法2: 移動傳遞（text 可能變空）
    processString(std::move(text));
    std::cout << "移動後 text: '" << text << "'" << std::endl;
}
```

### 2. 容器操作
```cpp
#include <vector>

void container_operations() {
    std::vector<std::string> names;
    
    // 方法1: 複製加入
    std::string name1 = "Alice";
    names.push_back(name1);  // name1 仍然有效
    std::cout << "name1 仍然存在: " << name1 << std::endl;
    
    // 方法2: 移動加入
    std::string name2 = "Bob";
    names.push_back(std::move(name2));  // name2 可能變空
    std::cout << "name2 狀態: '" << name2 << "'" << std::endl;
    
    // 方法3: 直接建構（最有效率）
    names.emplace_back("Charlie");
    
    // 顯示容器內容
    for (const auto& name : names) {
        std::cout << "容器中: " << name << std::endl;
    }
}
```

### 3. 智能指標轉移
```cpp
#include <memory>

void smart_pointer_example() {
    // unique_ptr 只能移動，不能複製
    std::unique_ptr<int> ptr1 = std::make_unique<int>(42);
    std::cout << "ptr1 指向值: " << *ptr1 << std::endl;
    
    // 轉移所有權
    std::unique_ptr<int> ptr2 = std::move(ptr1);
    
    // 檢查狀態
    std::cout << "ptr1 是否為空: " << (ptr1 == nullptr) << std::endl;  // true
    std::cout << "ptr2 指向值: " << *ptr2 << std::endl;                // 42
}
```

### 4. 函數返回值優化
```cpp
#include <vector>

// 返回大型物件
std::vector<int> createLargeVector() {
    std::vector<int> result(1000000, 42);
    return result;  // 編譯器通常會自動優化（RVO/NRVO）
}

// 明確使用移動
std::vector<int> moveVector(std::vector<int> input) {
    // 對 input 進行處理...
    return std::move(input);  // 明確移動
}

void return_value_example() {
    auto vec1 = createLargeVector();     // 高效率
    auto vec2 = moveVector(std::move(vec1));  // 明確移動
    
    std::cout << "vec1 大小: " << vec1.size() << std::endl;  // 可能為 0
    std::cout << "vec2 大小: " << vec2.size() << std::endl;  // 1000000
}
```

## 進階技巧

### 1. 完美轉發 (Perfect Forwarding)
```cpp
#include <utility>

template<typename T>
void wrapper(T&& arg) {
    // 使用 std::forward 保持參數的值類別
    actual_function(std::forward<T>(arg));
}
```

### 2. 移動賦值運算子
```cpp
class MyClass {
public:
    // 移動賦值運算子
    MyClass& operator=(MyClass&& other) noexcept {
        if (this != &other) {
            // 釋放當前資源
            // 移動 other 的資源
            data_ = std::move(other.data_);
        }
        return *this;
    }
    
private:
    std::string data_;
};
```

### 3. 條件移動
```cpp
template<typename T>
void conditionalMove(T&& value, bool shouldMove) {
    if (shouldMove) {
        process(std::move(value));
    } else {
        process(value);  // 複製
    }
}
```

## 常見陷阱和注意事項

### 1. 移動後不要使用原物件
```cpp
std::string str = "Hello";
std::string moved = std::move(str);
// 危險：str 可能已經無效
// std::cout << str << std::endl;  // 可能輸出空字串或未定義行為
```

### 2. 不要移動 const 物件
```cpp
const std::string str = "Hello";
// std::move(str);  // 無效果，const 物件不能被移動
```

### 3. 返回值不需要明確 move
```cpp
std::string func() {
    std::string result = "Hello";
    return result;  // 編譯器會自動優化，不需要 std::move(result)
}
```

### 4. 小物件移動可能沒有優勢
```cpp
// 對於 int, char 等小型物件，移動和複製效能相似
int a = 42;
int b = std::move(a);  // 沒有明顯優勢
```

## 效能比較

### 測試範例
```cpp
#include <chrono>
#include <vector>

void performance_test() {
    // 建立大型容器
    std::vector<int> large_vector(1000000, 42);
    
    // 測試複製
    auto start = std::chrono::high_resolution_clock::now();
    std::vector<int> copied = large_vector;
    auto end = std::chrono::high_resolution_clock::now();
    
    auto copy_time = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    // 測試移動
    start = std::chrono::high_resolution_clock::now();
    std::vector<int> moved = std::move(large_vector);
    end = std::chrono::high_resolution_clock::now();
    
    auto move_time = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    std::cout << "複製耗時: " << copy_time.count() << " 微秒" << std::endl;
    std::cout << "移動耗時: " << move_time.count() << " 微秒" << std::endl;
}
```

## 最佳實踐

### 1. 何時使用 Move
- ✅ 不再需要原物件時
- ✅ 傳遞大型物件給函數
- ✅ 在容器中插入臨時物件
- ✅ 實現高效的資源轉移

### 2. 何時不要使用 Move
- ❌ 還需要使用原物件
- ❌ 物件很小（如 int, char）
- ❌ const 物件
- ❌ 函數返回值（編譯器會自動優化）

### 3. 實現移動語意的準則
- 移動建構函數應該標記為 `noexcept`
- 移動後的物件應該處於有效但未指定的狀態
- 自我賦值要安全處理
- 資源管理要正確

## 總結

Move 語意是現代 C++ 的重要特性，能夠：

- **提升效能**：避免不必要的深拷貝
- **資源管理**：高效轉移物件所有權
- **語意清晰**：明確表達資源轉移意圖
- **記憶體效率**：減少記憶體分配和釋放

記住核心原則：**當你不再需要某個物件時，使用 `std::move` 將其資源轉移給其他物件，避免昂貴的複製操作。**

## 完整範例程式

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>

int main() {
    // 字串移動
    std::string str1 = "Hello, World!";
    std::string str2 = std::move(str1);
    std::cout << "移動後 str1: '" << str1 << "', str2: '" << str2 << "'" << std::endl;
    
    // 容器移動
    std::vector<int> vec1 = {1, 2, 3, 4, 5};
    std::vector<int> vec2 = std::move(vec1);
    std::cout << "移動後 vec1 大小: " << vec1.size() 
              << ", vec2 大小: " << vec2.size() << std::endl;
    
    // 智能指標移動
    auto ptr1 = std::make_unique<int>(42);
    auto ptr2 = std::move(ptr1);
    std::cout << "ptr1 為空: " << (ptr1 == nullptr) 
              << ", ptr2 值: " << *ptr2 << std::endl;
    
    return 0;
}
```
