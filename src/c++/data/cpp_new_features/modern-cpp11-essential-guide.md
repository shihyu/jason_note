# 現代 C++ 必備特性完整指南

> 本文整合自兩篇重要文章的精華，涵蓋 C++11 開發者必須掌握的核心特性。

---

## 目錄

1. [auto 自動型別推導](#1-auto-自動型別推導)
2. [nullptr 空指標字面值](#2-nullptr-空指標字面值)
3. [基於範圍的 for 迴圈](#3-基於範圍的-for-迴圈-range-based-for-loops)
4. [強型別列舉](#4-強型別列舉-strongly-typed-enums)
5. [智慧指標](#5-智慧指標-smart-pointers)
6. [Lambda 表達式](#6-lambda-表達式)
7. [override 和 final 識別符](#7-override-和-final-識別符)
8. [static_assert 編譯期斷言](#8-static_assert-編譯期斷言)
9. [移動語義](#9-移動語義-move-semantics)
10. [noexcept 例外規格](#10-noexcept-例外規格)
11. [初始化列表](#11-初始化列表-initializer-lists)
12. [可變參數模板](#12-可變參數模板-variadic-templates)
13. [std::thread 執行緒](#13-stdthread-執行緒)
14. [非成員 begin() 和 end()](#14-非成員-begin-和-end)
15. [無序容器](#15-無序容器-unordered-containers)
16. [default 和 delete 特殊成員函式](#16-default-和-delete-特殊成員函式)

---

## 1. auto 自動型別推導

C++11 將 `auto` 關鍵字的用途改為型別推導，編譯器會從初始化值自動推斷變數型別。

```cpp
auto i = 42;        // int
auto l = 42LL;      // long long
auto p = new foo(); // foo*

// 簡化 STL 迭代器
std::map<std::string, std::vector<int>> map;
for(auto it = begin(map); it != end(map); ++it) {
    // ...
}
```

**優點**：減少冗長的型別宣告，讓程式碼更簡潔。

**注意**：搭配尾隨回傳型別可用於函式：

```cpp
template <typename T1, typename T2>
auto compose(T1 t1, T2 t2) -> decltype(t1 + t2) {
    return t1 + t2;
}
```

---

## 2. nullptr 空指標字面值

C++11 引入 `nullptr` 取代傳統的 `NULL` 或 `0`，避免隱式轉換為整數型別的問題。

```cpp
int* p1 = NULL;      // 舊式寫法
int* p2 = nullptr;   // 新式寫法（推薦）

foo(nullptr);        // 明確傳遞空指標
bar(nullptr);

bool f = nullptr;    // OK，轉為 false
int i = nullptr;     // 錯誤！不能轉為整數
```

---

## 3. 基於範圍的 for 迴圈 (Range-Based for Loops)

支援 `foreach` 風格的迭代，適用於 C 陣列、初始化列表及任何實作 `begin()`/`end()` 的容器。

```cpp
std::map<std::string, std::vector<int>> map;
for(const auto& kvp : map) {
    std::cout << kvp.first << std::endl;
    for(auto v : kvp.second) {
        std::cout << v << std::endl;
    }
}

int arr[] = {1, 2, 3, 4, 5};
for(int& e : arr) {
    e = e * e;  // 原地修改
}
```

---

## 4. 強型別列舉 (Strongly-typed Enums)

使用 `enum class` 解決傳統 enum 的問題：

- 列舉值不會洩漏到外圍作用域
- 不會隱式轉換為整數
- 可指定底層型別

```cpp
enum class Options { None, One, All };
Options o = Options::All;

// 可繼承底層型別
enum class Color : uint8_t { Red, Green, Blue };
```

---

## 5. 智慧指標 (Smart Pointers)

標準化的智慧指標，告別手動記憶體管理：

| 類型 | 用途 |
|------|------|
| `unique_ptr` | 獨佔所有權，不可複製，可移動 |
| `shared_ptr` | 共享所有權，參考計數 |
| `weak_ptr` | 弱參考，不增加計數，用於打破循環參考 |

```cpp
// unique_ptr
std::unique_ptr<int> p1(new int(42));
std::unique_ptr<int> p2 = std::move(p1);  // 轉移所有權

// shared_ptr
auto p3 = std::make_shared<int>(42);  // 推薦寫法
std::shared_ptr<int> p4 = p3;  // 共享所有權

// weak_ptr
std::weak_ptr<int> wp = p3;
if(auto sp = wp.lock()) {  // 取得 shared_ptr
    std::cout << *sp << std::endl;
}
```

**注意**：`auto_ptr` 已棄用，請勿使用。

---

## 6. Lambda 表達式

匿名函式，可用於任何需要函式物件的地方：

```cpp
std::vector<int> v = {1, 2, 3};

// 基本用法
std::for_each(std::begin(v), std::end(v),
    [](int n) { std::cout << n << std::endl; });

// 儲存為變數
auto is_odd = [](int n) { return n % 2 == 1; };
auto pos = std::find_if(std::begin(v), std::end(v), is_odd);

// 遞迴 lambda（需明確指定型別）
std::function<int(int)> fib = [&fib](int n) {
    return n < 2 ? 1 : fib(n-1) + fib(n-2);
};
```

---

## 7. override 和 final 識別符

防止虛擬函式覆寫的常見錯誤：

```cpp
class Base {
public:
    virtual void f(short) { }
};

class Derived : public Base {
public:
    // 編譯器會檢查是否真正覆寫基類方法
    virtual void f(short) override { }

    // 禁止子類再覆寫
    virtual void g(int) override final { }
};
```

**常見錯誤範例**：

```cpp
class B {
public:
    virtual void f(short) { std::cout << "B::f" << std::endl; }
};

class D : public B {
public:
    // 錯誤：參數型別不同，這是 overload 不是 override！
    virtual void f(int) { std::cout << "D::f" << std::endl; }
};
```

使用 `override` 可讓編譯器捕捉這類錯誤。

---

## 8. static_assert 編譯期斷言

在編譯時期檢查條件，特別適合模板參數驗證：

```cpp
template <typename T, size_t Size>
class Vector {
    static_assert(Size >= 3, "Size is too small");
    T _points[Size];
};

// 搭配 type traits 使用
template <typename T1, typename T2>
auto add(T1 t1, T2 t2) -> decltype(t1 + t2) {
    static_assert(std::is_integral<T1>::value, "T1 must be integral");
    static_assert(std::is_integral<T2>::value, "T2 must be integral");
    return t1 + t2;
}
```

---

## 9. 移動語義 (Move Semantics)

透過右值參考 (`&&`) 實現資源的「移動」而非「複製」，大幅提升效能：

```cpp
class Buffer {
    std::string name_;
    std::unique_ptr<int[]> data_;
    size_t size_;

public:
    // 建構子
    Buffer(const std::string& name, size_t size)
        : name_(name), size_(size), data_(new int[size]) {}

    // 複製建構子
    Buffer(const Buffer& copy)
        : name_(copy.name_)
        , size_(copy.size_)
        , data_(new int[copy.size_])
    {
        std::copy(copy.data_.get(), copy.data_.get() + size_, data_.get());
    }

    // 移動建構子
    Buffer(Buffer&& temp) noexcept
        : name_(std::move(temp.name_))
        , data_(std::move(temp.data_))
        , size_(temp.size_)
    {
        temp.size_ = 0;
    }

    // 移動指派運算子
    Buffer& operator=(Buffer&& temp) noexcept {
        if (this != &temp) {
            name_ = std::move(temp.name_);
            data_ = std::move(temp.data_);
            size_ = temp.size_;
            temp.size_ = 0;
        }
        return *this;
    }
};
```

**關鍵**：使用 `std::move()` 將左值轉為右值參考。

**替代實作（使用 swap）**：

```cpp
class Buffer {
    // ... 成員變數同上

public:
    // 複製指派運算子（複製並交換慣用法）
    Buffer& operator=(Buffer copy) {
        swap(*this, copy);
        return *this;
    }

    // 移動建構子
    Buffer(Buffer&& temp) : Buffer() {
        swap(*this, temp);
    }

    friend void swap(Buffer& first, Buffer& second) noexcept {
        using std::swap;
        swap(first.name_, second.name_);
        swap(first.size_, second.size_);
        swap(first.data_, second.data_);
    }
};
```

---

## 10. noexcept 例外規格

宣告函式不會拋出例外，有助於編譯器優化：

```cpp
void foo() noexcept {
    // 保證不拋出例外
}

// 條件式 noexcept
template<typename T>
void bar(T& x) noexcept(noexcept(x.swap(x))) {
    // ...
}
```

---

## 11. 初始化列表 (Initializer Lists)

統一的初始化語法，適用於任何容器：

```cpp
void process(std::initializer_list<int> values) {
    for (auto v : values) {
        std::cout << v << " ";
    }
}

process({1, 2, 3, 4, 5});

std::vector<int> v = {1, 2, 3};
std::map<std::string, int> m = {{"one", 1}, {"two", 2}};
```

---

## 12. 可變參數模板 (Variadic Templates)

接受任意數量、任意型別的模板參數：

```cpp
// C++11 遞迴展開
template<typename T>
void print(T value) {
    std::cout << value << std::endl;
}

template<typename T, typename... Args>
void print(T first, Args... rest) {
    std::cout << first << " ";
    print(rest...);
}

print(1, 2.5, "hello");

// C++17 fold expression（更簡潔）
template<typename... Args>
void print17(Args... args) {
    (std::cout << ... << args) << std::endl;
}
```

---

## 13. std::thread 執行緒

標準化的多執行緒支援：

```cpp
#include <thread>

void worker(int id) {
    std::cout << "Worker " << id << std::endl;
}

int main() {
    std::thread t1(worker, 1);
    std::thread t2([]() { std::cout << "Lambda thread\n"; });

    t1.join();
    t2.join();

    return 0;
}
```

---

## 14. 非成員 begin() 和 end()

統一的介面，支援所有容器和 C 陣列：

```cpp
int arr[] = {1, 2, 3};
std::vector<int> v = {4, 5, 6};

// 相同的程式碼適用於陣列和容器
for (auto it = std::begin(arr); it != std::end(arr); ++it) { }
for (auto it = std::begin(v); it != std::end(v); ++it) { }

// 更容易寫出泛型程式碼
template<typename Container>
void process(Container& c) {
    std::for_each(std::begin(c), std::end(c), [](auto& e) { });
}
```

**對比舊式 C 陣列處理**：

```cpp
// 舊式（繁瑣）
int arr[] = {1, 2, 3};
auto begin = &arr[0];
auto end = &arr[0] + sizeof(arr)/sizeof(arr[0]);

// 新式（簡潔）
auto begin = std::begin(arr);
auto end = std::end(arr);
```

---

## 15. 無序容器 (Unordered Containers)

基於雜湊表的高效容器：

| 容器 | 說明 |
|------|------|
| `unordered_map` | 無序鍵值對 |
| `unordered_set` | 無序集合 |
| `unordered_multimap` | 允許重複鍵的無序映射 |
| `unordered_multiset` | 允許重複元素的無序集合 |

```cpp
std::unordered_map<std::string, int> scores;
scores["Alice"] = 100;
scores["Bob"] = 95;

// 平均 O(1) 的查找時間
if (scores.find("Alice") != scores.end()) {
    std::cout << "Found!" << std::endl;
}
```

---

## 16. default 和 delete 特殊成員函式

明確控制編譯器生成的特殊成員函式：

```cpp
class NonCopyable {
public:
    NonCopyable() = default;  // 使用預設實作

    // 禁止複製
    NonCopyable(const NonCopyable&) = delete;
    NonCopyable& operator=(const NonCopyable&) = delete;

    // 允許移動
    NonCopyable(NonCopyable&&) = default;
    NonCopyable& operator=(NonCopyable&&) = default;
};
```

---

## 總結

### 優先掌握（必學）

| 特性 | 重要性 |
|------|--------|
| `auto` | 簡化型別宣告 |
| `nullptr` | 型別安全的空指標 |
| 範圍 for | 簡潔的迭代語法 |
| 智慧指標 | 自動記憶體管理 |
| Lambda | 靈活的匿名函式 |

### 進階特性（重要）

| 特性 | 重要性 |
|------|--------|
| 移動語義 | 效能優化關鍵 |
| `override`/`final` | 防止覆寫錯誤 |
| `static_assert` | 編譯期檢查 |

### 實用特性

| 特性 | 重要性 |
|------|--------|
| 強型別 enum | 更安全的列舉 |
| 初始化列表 | 統一初始化語法 |
| 無序容器 | O(1) 查找效能 |
| `std::thread` | 標準多執行緒 |

---

## 參考資料

- [C++ Reference](https://en.cppreference.com/)
- [Bjarne Stroustrup's C++11 FAQ](http://www.stroustrup.com/C++11FAQ.html)
- [CppDepend Blog](https://cppdepend.com/blog/)
- [CodeProject - Ten C++11 Features](https://www.codeproject.com/Articles/570638/Ten-Cplusplus11-Features-Every-Cplusplus-Developer)
