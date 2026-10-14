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
   - [白話解釋：左值 vs 右值](#白話解釋左值-vs-右值)
   - [為什麼需要移動語義？](#為什麼需要移動語義)
   - [std::move() 的作用](#stdmove-的作用)
   - [右值參考 (&&) 是什麼？](#右值參考--是什麼)
   - [何時該用 std::move？](#何時該用-stdmove)
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

透過右值參考 (`&&`) 實現資源的「移動」而非「複製」，大幅提升效能。

### 白話解釋：左值 vs 右值

先搞懂什麼是「左值」和「右值」：

```
左值 (lvalue)：有名字、有地址、可以取址的東西
右值 (rvalue)：臨時的、沒名字、即將消失的東西
```

**生活化比喻**：

```
左值 = 你的房子（有地址、長期存在）
右值 = 搬家公司的卡車（臨時的、用完就走）
```

**程式碼範例**：

```cpp
int x = 10;        // x 是左值（有名字、有地址）
int y = x + 5;     // "x + 5" 是右值（臨時計算結果）

std::string s1 = "hello";              // s1 是左值
std::string s2 = s1 + " world";        // "s1 + world" 是右值（臨時字串）
std::string s3 = std::string("temp");  // 右邊是右值（臨時物件）
```

### 為什麼需要移動語義？

**問題場景**：複製大型物件很浪費

```
┌──────────────────────────────────────────────────────────────┐
│  傳統複製（深拷貝）- 浪費資源！                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   原始物件 A                    新物件 B                     │
│   ┌─────────┐                  ┌─────────┐                   │
│   │ name_   │                  │ name_   │                   │
│   │ size_   │   ══複製══>      │ size_   │                   │
│   │ data_ ──┼──┐               │ data_ ──┼──┐                │
│   └─────────┘  │               └─────────┘  │                │
│                ▼                            ▼                │
│         ┌──────────────┐            ┌───────────────┐        │
│         │ 1GB 資料     │  複製整塊  │ 1GB 資料      │        │
│         │ [...........]│ ═══════>   │ [...........] │        │
│         └──────────────┘            └───────────────┘        │
│                                                              │
│   💀 如果原始物件馬上要被銷毀，這 1GB 的複製完全是浪費！     │
└──────────────────────────────────────────────────────────────┘
```

**解決方案**：移動語義 - 直接「偷」資源

```
┌───────────────────────────────────────────────────────────────┐
│  移動語義（搬家）- 超高效！                                   │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│   原始物件 A（即將銷毀）         新物件 B                     │
│   ┌─────────┐                  ┌─────────┐                    │
│   │ name_   │                  │ name_   │                    │
│   │ size_   │   ══移動══>      │ size_   │                    │
│   │ data_ ──┼──┐               │ data_ ──┼──────────┐         │
│   └─────────┘  │               └─────────┘          │         │
│                │                                    │         │
│                ▼                                    │         │
│         ┌──────────────┐                            │         │
│         │ nullptr      │   指標直接轉移 ────────────┘         │
│         └──────────────┘                                      │
│                                          ▼                    │
│                                   ┌──────────────┐            │
│                                   │ 1GB 資料     │            │
│                                   │ [...........]│            │
│                                   └──────────────┘            │
│                                                               │
│   ✅ 只是改了指標的指向，資料完全沒動！O(1) 時間複雜度        │
└───────────────────────────────────────────────────────────────┘
```

### std::move() 的作用

`std::move()` **不會移動任何東西**！它只是一個「型別轉換」：

```
┌─────────────────────────────────────────────────────────────┐
│  std::move() 的真正作用                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   std::move(x)  的意思是：                                  │
│                                                             │
│   「我承諾不再使用 x 了，你可以把它的資源搶走」             │
│                                                             │
│   ┌─────────┐     std::move()      ┌─────────┐              │
│   │  左值   │  ═══════════════>    │  右值   │              │
│   │ (lvalue)│     型別轉換         │(rvalue) │              │
│   └─────────┘                      └─────────┘              │
│                                                             │
│   它讓編譯器選擇「移動建構子」而不是「複製建構子」          │
└─────────────────────────────────────────────────────────────┘
```

**白話版**：

```cpp
std::string a = "hello";
std::string b = a;              // 複製！a 還要用
std::string c = std::move(a);   // 移動！告訴編譯器：a 我不要了，搶走吧

// 移動後，a 處於「有效但未定義」狀態（通常是空的）
// 可以重新賦值，但不要讀取它的值
```

### 右值參考 (&&) 是什麼？

```
┌───────────────────────────────────────────────────────────┐
│  參考類型對照表                                           │
├───────────────────────────────────────────────────────────┤
│                                                           │
│   T&   = 左值參考   → 只能綁定到左值（有名字的東西）      │
│   T&&  = 右值參考   → 只能綁定到右值（臨時的東西）        │
│                                                           │
│   void foo(std::string& s);   // 只接受左值               │
│   void foo(std::string&& s);  // 只接受右值               │
│                                                           │
├───────────────────────────────────────────────────────────┤
│   範例：                                                  │
│                                                           │
│   std::string name = "Alice";                             │
│   foo(name);                    // 呼叫 foo(string&)      │
│   foo(std::string("temp"));     // 呼叫 foo(string&&)     │
│   foo(std::move(name));         // 呼叫 foo(string&&)     │
└───────────────────────────────────────────────────────────┘
```

### 移動建構子 vs 複製建構子

```
┌───────────────────────────────────────────────────────────┐
│  編譯器如何選擇？                                         │
├───────────────────────────────────────────────────────────┤
│                                                           │
│   MyClass(const MyClass& other);    // 複製建構子         │
│   MyClass(MyClass&& other);         // 移動建構子         │
│                                                           │
│   ┌─────────────────┬─────────────────────────────────┐   │
│   │ 呼叫方式        │  選擇哪個建構子                 │   │
│   ├─────────────────┼─────────────────────────────────┤   │
│   │ MyClass b(a);   │ 複製建構子（a 是左值）          │   │
│   │ MyClass b(f()); │ 移動建構子（f() 回傳右值）      │   │
│   │ MyClass b(      │ 移動建構子                      │   │
│   │  std::move(a)); │ （std::move 把 a 轉成右值）     │   │
│   └─────────────────┴─────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
```

### 完整範例：理解移動的過程

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

### 常見使用情境

```
┌─────────────────────────────────────────────────────────────┐
│  什麼時候會自動觸發移動？                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 函式回傳區域變數（RVO/NRVO 不適用時）                   │
│     std::vector<int> getVector() {                          │
│         std::vector<int> v = {1,2,3};                       │
│         return v;  // 自動移動（或 RVO 優化）               │
│     }                                                       │
│                                                             │
│  2. 容器操作                                                │
│     vec.push_back(std::move(obj));  // 移動進容器           │
│     vec.emplace_back(...);          // 原地建構，更好       │
│                                                             │
│  3. 標準演算法                                              │
│     std::sort, std::unique 等會自動使用移動                 │
│                                                             │
│  4. 智慧指標轉移                                            │
│     auto p2 = std::move(p1);  // unique_ptr 必須移動        │
└─────────────────────────────────────────────────────────────┘
```

### 移動後的物件狀態

```
┌─────────────────────────────────────────────────────────────┐
│  ⚠️ 重要：移動後物件的狀態                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   std::string s = "hello";                                  │
│   std::string t = std::move(s);                             │
│                                                             │
│   // s 現在是「有效但未定義」狀態                           │
│   // ✅ 可以做的事：                                        │
│   //    - 銷毀它（解構子會正常執行）                        │
│   //    - 重新賦值：s = "new value";                        │
│   //    - 清空：s.clear();                                  │
│   //                                                        │
│   // ❌ 不要做的事：                                        │
│   //    - 讀取它的值（未定義行為）                          │
│   //    - 假設它是空的（標準沒保證）                        │
│                                                             │
│   s = "world";  // OK，重新賦值後可正常使用                 │
└─────────────────────────────────────────────────────────────┘
```

### 何時該用 std::move？

```
┌────────────────────────────────────────────────────────────┐
│  ✅ 該用 std::move 的情況                                  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. 明確知道物件不再需要                                   │
│     void process(Widget w) {                               │
│         widgets.push_back(std::move(w));  // w 不再使用    │
│     }                                                      │
│                                                            │
│  2. unique_ptr 的轉移（必須用）                            │
│     auto p2 = std::move(p1);                               │
│                                                            │
│  3. 成員初始化（轉移參數所有權）                           │
│     MyClass(std::string name) : name_(std::move(name)) {}  │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  ❌ 不該用 std::move 的情況                                │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. return 區域變數（會阻止 RVO 優化）                     │
│     std::string foo() {                                    │
│         std::string s = "hello";                           │
│         return s;              // ✅ 不要加 std::move      │
│         // return std::move(s); // ❌ 反而更慢             │
│     }                                                      │
│                                                            │
│  2. 之後還要使用該變數                                     │
│     auto b = std::move(a);                                 │
│     std::cout << a;  // ❌ 未定義行為                      │
│                                                            │
│  3. 對 const 物件（移動會變成複製）                        │
│     const std::string s = "hello";                         │
│     auto t = std::move(s);  // 實際上是複製！              │
└────────────────────────────────────────────────────────────┘
```

### 效能對比示意

```
┌─────────────────────────────────────────────────────────────┐
│  std::vector<std::string> 操作效能對比                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  假設字串長度 1MB：                                         │
│                                                             │
│  ┌──────────────────────┬──────────────┬─────────────────┐  │
│  │ 操作                 │ 複製         │ 移動            │  │
│  ├──────────────────────┼──────────────┼─────────────────┤  │
│  │ push_back            │ ~1ms         │ ~0.00001ms      │  │
│  │ vector 擴容(10元素)  │ ~10ms        │ ~0.0001ms       │  │
│  │ sort (1000元素)      │ ~10000ms     │ ~1ms            │  │
│  └──────────────────────┴──────────────┴─────────────────┘  │
│                                                             │
│  移動只是指標操作，複製要拷貝整塊記憶體                     │
└─────────────────────────────────────────────────────────────┘
```

### 一句話總結

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   移動語義 = 「搬家」而不是「影印」                         │
│                                                             │
│   - 右值 = 即將被丟掉的東西（臨時物件）                     │
│   - std::move() = 告訴編譯器「這東西我不要了」              │
│   - 移動建構子 = 把別人的資源搶過來用                       │
│                                                             │
│   記住：std::move 不移動，它只是允許移動發生                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
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
