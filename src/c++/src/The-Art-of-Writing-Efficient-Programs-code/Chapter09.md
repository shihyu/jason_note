# Chapter 09: 高性能 C++ 技術

## 本章重點

探討現代 C++ 的高性能程式設計技術，包括移動語義、完美轉發、模板元編程和 constexpr 等。

## 移動語義和完美轉發

### 1. 移動語義
```cpp
class Buffer {
    size_t size_;
    int* data_;

public:
    // 移動建構函數
    Buffer(Buffer&& other) noexcept
        : size_(other.size_), data_(other.data_) {
        other.size_ = 0;
        other.data_ = nullptr;
    }

    // 移動賦值運算子
    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            delete[] data_;
            size_ = other.size_;
            data_ = other.data_;
            other.size_ = 0;
            other.data_ = nullptr;
        }
        return *this;
    }
};
```

### 2. 完美轉發
```cpp
template<typename T, typename... Args>
std::unique_ptr<T> make_unique(Args&&... args) {
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
}

// 通用引用和 std::forward
template<typename T>
void wrapper(T&& arg) {
    process(std::forward<T>(arg));
}
```

## 編譯時計算

### 1. constexpr 函數
```cpp
constexpr int factorial(int n) {
    return n <= 1 ? 1 : n * factorial(n - 1);
}

// C++14 擴展 constexpr
constexpr int fibonacci(int n) {
    int a = 0, b = 1;
    for (int i = 0; i < n; ++i) {
        int temp = a + b;
        a = b;
        b = temp;
    }
    return a;
}

// 編譯時陣列
constexpr std::array<int, 10> generate_squares() {
    std::array<int, 10> arr{};
    for (int i = 0; i < 10; ++i) {
        arr[i] = i * i;
    }
    return arr;
}
```

### 2. consteval (C++20)
```cpp
consteval int compile_time_only(int n) {
    return n * n;  // 必須在編譯時執行
}

// if constexpr
template<typename T>
auto process(T value) {
    if constexpr (std::is_integral_v<T>) {
        return value * 2;
    } else if constexpr (std::is_floating_point_v<T>) {
        return value / 2;
    } else {
        return value;
    }
}
```

## 模板元編程

### 1. SFINAE 和 std::enable_if
```cpp
template<typename T>
typename std::enable_if<std::is_arithmetic<T>::value, T>::type
sum(T a, T b) {
    return a + b;
}

// C++20 concepts
template<typename T>
concept Arithmetic = std::is_arithmetic_v<T>;

template<Arithmetic T>
T sum(T a, T b) {
    return a + b;
}
```

### 2. 變參模板
```cpp
template<typename... Args>
void print(Args... args) {
    ((std::cout << args << " "), ...);  // C++17 折疊運算式
}

// 遞迴展開
template<typename First, typename... Rest>
void process(First&& first, Rest&&... rest) {
    handle(std::forward<First>(first));
    if constexpr (sizeof...(rest) > 0) {
        process(std::forward<Rest>(rest)...);
    }
}
```

## SIMD 優化

### 1. 編譯器內建函數
```cpp
#include <immintrin.h>

void add_vectors_avx(float* a, float* b, float* c, size_t n) {
    size_t simd_size = n / 8 * 8;

    for (size_t i = 0; i < simd_size; i += 8) {
        __m256 va = _mm256_load_ps(&a[i]);
        __m256 vb = _mm256_load_ps(&b[i]);
        __m256 vc = _mm256_add_ps(va, vb);
        _mm256_store_ps(&c[i], vc);
    }

    // 處理剩餘元素
    for (size_t i = simd_size; i < n; ++i) {
        c[i] = a[i] + b[i];
    }
}
```

### 2. std::simd (C++23)
```cpp
#include <experimental/simd>
namespace stdx = std::experimental;

void simd_operation(float* data, size_t n) {
    using simd_t = stdx::native_simd<float>;
    size_t simd_size = n / simd_t::size() * simd_t::size();

    for (size_t i = 0; i < simd_size; i += simd_t::size()) {
        simd_t v(&data[i], stdx::vector_aligned);
        v = v * 2.0f + 1.0f;
        v.copy_to(&data[i], stdx::vector_aligned);
    }
}
```

## 表達式模板

```cpp
template<typename E>
class VecExpression {
public:
    double operator[](size_t i) const {
        return static_cast<const E&>(*this)[i];
    }
    size_t size() const {
        return static_cast<const E&>(*this).size();
    }
};

template<typename E1, typename E2>
class VecSum : public VecExpression<VecSum<E1, E2>> {
    const E1& u;
    const E2& v;

public:
    VecSum(const E1& u, const E2& v) : u(u), v(v) {}
    double operator[](size_t i) const { return u[i] + v[i]; }
    size_t size() const { return u.size(); }
};

// 延遲計算，避免臨時物件
template<typename E1, typename E2>
VecSum<E1, E2> operator+(const VecExpression<E1>& u,
                         const VecExpression<E2>& v) {
    return VecSum<E1, E2>(*static_cast<const E1*>(&u),
                          *static_cast<const E2*>(&v));
}
```

## 零成本抽象

### 1. 強類型
```cpp
template<typename T, typename Tag>
class StrongType {
    T value;

public:
    explicit StrongType(T v) : value(v) {}
    T get() const { return value; }
};

using Meters = StrongType<double, struct MetersTag>;
using Seconds = StrongType<double, struct SecondsTag>;

// 編譯時類型安全，執行時零開銷
Meters distance{100.0};
Seconds time{10.0};
// auto speed = distance / time;  // 編譯錯誤
```

### 2. Policy-Based Design
```cpp
template<typename StoragePolicy, typename CheckingPolicy>
class SmartPtr : public StoragePolicy, public CheckingPolicy {
public:
    template<typename... Args>
    SmartPtr(Args&&... args)
        : StoragePolicy(std::forward<Args>(args)...) {}

    auto operator->() {
        CheckingPolicy::check(StoragePolicy::get());
        return StoragePolicy::get();
    }
};
```

## 分支預測提示

```cpp
// C++20 [[likely]] 和 [[unlikely]]
int process(int value) {
    if (value > 0) [[likely]] {
        return value * 2;
    } else [[unlikely]] {
        return handle_error();
    }
}

// GCC/Clang 特定
#define LIKELY(x)   __builtin_expect(!!(x), 1)
#define UNLIKELY(x) __builtin_expect(!!(x), 0)

if (LIKELY(condition)) {
    // 常見路徑
} else {
    // 罕見路徑
}
```

## 內聯和連結時優化

### 1. 強制內聯
```cpp
// 編譯器特定
#ifdef _MSC_VER
    #define FORCE_INLINE __forceinline
#else
    #define FORCE_INLINE __attribute__((always_inline)) inline
#endif

FORCE_INLINE int fast_function(int x) {
    return x * 2;
}
```

### 2. LTO (Link Time Optimization)
```bash
# 啟用 LTO
g++ -flto -O3 file1.cpp file2.cpp -o program

# 使用 gold linker
g++ -fuse-ld=gold -flto -O3 *.cpp -o program
```

## 客製化記憶體配置

```cpp
// 池配置器
template<typename T, size_t BlockSize = 4096>
class PoolAllocator {
    union Node {
        char data[sizeof(T)];
        Node* next;
    };

    Node* free_list = nullptr;

public:
    T* allocate() {
        if (!free_list) {
            expand();
        }
        Node* node = free_list;
        free_list = free_list->next;
        return reinterpret_cast<T*>(node);
    }

    void deallocate(T* ptr) {
        Node* node = reinterpret_cast<Node*>(ptr);
        node->next = free_list;
        free_list = node;
    }

private:
    void expand() {
        // 配置新區塊
    }
};
```

## 性能注意事項

1. **避免虛函數在熱路徑**
2. **使用 final 關鍵字優化**
3. **考慮快取行對齊**
4. **減少動態配置**
5. **使用 noexcept 標記**
6. **利用 RVO/NRVO**