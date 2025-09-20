# Chapter 11: 高性能函式庫設計

## 本章重點

探討如何設計和實作高性能的 C++ 函式庫，包括 API 設計、ABI 穩定性、頭檔優化等考量。

## API 設計原則

### 1. 零成本抽象
```cpp
// 使用模板避免虛函數開銷
template<typename Impl>
class Algorithm {
    Impl impl;
public:
    void execute() {
        impl.process();  // 編譯時多型
    }
};

// vs 虛函數（有執行時開銷）
class VirtualAlgorithm {
public:
    virtual void execute() = 0;  // 虛函數表查找
};
```

### 2. 移動語義優先
```cpp
class Library {
public:
    // 支援移動語義
    Library(Library&&) noexcept = default;
    Library& operator=(Library&&) noexcept = default;

    // 完美轉發
    template<typename... Args>
    void process(Args&&... args) {
        internal_process(std::forward<Args>(args)...);
    }

    // 回傳值優化 (RVO)
    static Library create() {
        Library lib;
        // 設定...
        return lib;  // NRVO
    }
};
```

## 頭檔組織

### 1. 前向宣告
```cpp
// forward.h
namespace mylib {
    class Implementation;  // 前向宣告
    template<typename T> class Container;
}

// library.h
#include "forward.h"
namespace mylib {
    class Library {
        std::unique_ptr<Implementation> pimpl;  // 減少編譯依賴
    };
}
```

### 2. 頭檔最小化
```cpp
// 分離介面和實作
// interface.h (最小依賴)
class Interface {
public:
    virtual ~Interface() = default;
    virtual void process() = 0;
};

// implementation.h (完整實作)
#include "interface.h"
#include <heavy_dependencies.h>
class Implementation : public Interface {
    // 實作細節
};
```

## Pimpl 慣用法

```cpp
// library.h
class Library {
    class Impl;
    std::unique_ptr<Impl> pimpl;

public:
    Library();
    ~Library();  // 必須在 .cpp 定義

    Library(Library&&) noexcept;
    Library& operator=(Library&&) noexcept;

    void process();
};

// library.cpp
#include "library.h"
#include <complex_dependencies.h>

class Library::Impl {
    // 私有實作，可以自由修改
    ComplexType data;
public:
    void process() { /* ... */ }
};

Library::Library() : pimpl(std::make_unique<Impl>()) {}
Library::~Library() = default;  // 這裡定義，Impl 已完整

Library::Library(Library&&) noexcept = default;
Library& Library::operator=(Library&&) noexcept = default;

void Library::process() {
    pimpl->process();
}
```

## 模板函式庫優化

### 1. 顯式實例化
```cpp
// template_lib.h
template<typename T>
class Container {
public:
    void process();
};

// template_lib.cpp
template<typename T>
void Container<T>::process() {
    // 實作
}

// 顯式實例化常用類型
template class Container<int>;
template class Container<double>;
template class Container<std::string>;
```

### 2. CRTP (Curiously Recurring Template Pattern)
```cpp
template<typename Derived>
class Base {
public:
    void interface() {
        static_cast<Derived*>(this)->implementation();
    }

    // 提供預設實作
    void implementation() {
        // 預設行為
    }
};

class Derived : public Base<Derived> {
public:
    void implementation() {
        // 特化行為
    }
};
```

## 記憶體管理策略

### 1. 自訂配置器介面
```cpp
template<typename T>
class CustomAllocator {
public:
    using value_type = T;

    CustomAllocator() = default;

    template<typename U>
    CustomAllocator(const CustomAllocator<U>&) {}

    T* allocate(size_t n) {
        return static_cast<T*>(memory_pool.allocate(n * sizeof(T)));
    }

    void deallocate(T* p, size_t n) {
        memory_pool.deallocate(p, n * sizeof(T));
    }

private:
    static MemoryPool memory_pool;
};
```

### 2. Small Object Optimization
```cpp
template<typename T, size_t SmallSize = 64>
class SmallVector {
    union {
        T small_buffer[SmallSize / sizeof(T)];
        T* large_buffer;
    };
    size_t size_;
    size_t capacity_;
    bool is_small_;

public:
    void push_back(const T& value) {
        if (size_ == capacity_) {
            grow();
        }
        if (is_small_) {
            new (&small_buffer[size_]) T(value);
        } else {
            new (&large_buffer[size_]) T(value);
        }
        ++size_;
    }
};
```

## ABI 穩定性

### 1. 版本控制
```cpp
namespace mylib {
    namespace v1 {
        class Library {
            // 版本 1 API
        };
    }

    namespace v2 {
        class Library {
            // 版本 2 API，向後相容
        };
    }

    // 當前版本別名
    using namespace v2;
}
```

### 2. 虛函數表穩定性
```cpp
class StableInterface {
public:
    virtual ~StableInterface() = default;

    // 現有虛函數不能改變順序
    virtual void method1() = 0;
    virtual void method2() = 0;

    // 新增函數只能加在最後
    virtual void method3() { /* 預設實作 */ }

protected:
    // 保留虛函數槽位供未來使用
    virtual void reserved1() {}
    virtual void reserved2() {}
};
```

## 編譯時優化

### 1. constexpr 函式庫
```cpp
template<size_t N>
class ConstexprString {
    char data[N]{};

public:
    constexpr ConstexprString(const char (&str)[N]) {
        for (size_t i = 0; i < N; ++i) {
            data[i] = str[i];
        }
    }

    constexpr size_t size() const { return N - 1; }
    constexpr const char* c_str() const { return data; }
};

// 編譯時字串處理
template<size_t N>
ConstexprString(const char (&)[N]) -> ConstexprString<N>;
```

### 2. Expression Templates
```cpp
template<typename L, typename R>
struct AddExpression {
    const L& left;
    const R& right;

    AddExpression(const L& l, const R& r) : left(l), right(r) {}

    auto operator[](size_t i) const {
        return left[i] + right[i];
    }
};

template<typename L, typename R>
auto operator+(const L& left, const R& right) {
    return AddExpression<L, R>(left, right);
}
```

## 並行函式庫設計

### 1. 執行策略
```cpp
namespace execution {
    class sequenced_policy {};
    class parallel_policy {};
    class parallel_unsequenced_policy {};

    inline constexpr sequenced_policy seq{};
    inline constexpr parallel_policy par{};
    inline constexpr parallel_unsequenced_policy par_unseq{};
}

template<typename ExecutionPolicy, typename Iterator, typename UnaryOp>
void transform(ExecutionPolicy&& policy,
               Iterator first, Iterator last,
               UnaryOp op) {
    if constexpr (std::is_same_v<std::decay_t<ExecutionPolicy>,
                                 execution::parallel_policy>) {
        // 平行實作
        parallel_transform(first, last, op);
    } else {
        // 循序實作
        std::transform(first, last, first, op);
    }
}
```

## 性能測試框架

```cpp
class BenchmarkLibrary {
public:
    template<typename Func>
    static void benchmark(const std::string& name,
                          Func&& func,
                          size_t iterations = 1000000) {
        // 預熱
        for (size_t i = 0; i < 100; ++i) {
            func();
        }

        auto start = std::chrono::high_resolution_clock::now();
        for (size_t i = 0; i < iterations; ++i) {
            func();
        }
        auto end = std::chrono::high_resolution_clock::now();

        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
                       (end - start).count();

        std::cout << name << ": "
                  << duration / iterations << " ns/op\n";
    }
};
```

## 最佳實踐

1. **最小化頭檔依賴**
   - 使用前向宣告
   - Pimpl 慣用法
   - 模組化設計

2. **提供多層次 API**
   - 高階易用介面
   - 低階高性能介面
   - 可客製化的中間層

3. **編譯時檢查**
   - static_assert
   - concepts (C++20)
   - SFINAE

4. **文件和範例**
   - 性能特性文件
   - 使用範例
   - 基準測試結果

5. **版本管理**
   - 語意版本控制
   - ABI 相容性檢查
   - 棄用警告