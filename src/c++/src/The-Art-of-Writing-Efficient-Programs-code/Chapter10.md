# Chapter 10: 編譯器優化技術

## 本章重點

深入了解編譯器優化技術，包括優化等級、編譯器提示、Profile-Guided Optimization (PGO) 等。

## 編譯器優化等級

### GCC/Clang 優化選項
```bash
# 基本優化等級
-O0  # 無優化（預設）
-O1  # 基本優化
-O2  # 推薦的優化等級
-O3  # 激進優化
-Os  # 優化程式大小
-Ofast  # 忽略嚴格標準合規性的最快優化

# 特定優化
-march=native  # 針對當前 CPU 優化
-mtune=native  # 調校給當前 CPU
-ffast-math    # 快速但不精確的浮點運算
```

## 常見編譯器優化

### 1. 內聯展開 (Inlining)
```cpp
// 提示編譯器內聯
inline int add(int a, int b) {
    return a + b;
}

// 強制內聯 (GCC/Clang)
__attribute__((always_inline)) inline int fast_add(int a, int b) {
    return a + b;
}

// 防止內聯
__attribute__((noinline)) int dont_inline(int x) {
    return complex_calculation(x);
}
```

### 2. 循環優化
```cpp
// 循環展開 (Loop Unrolling)
// 編譯器可能自動展開：
for (int i = 0; i < n; ++i) {
    sum += arr[i];
}

// 展開後的等效程式碼：
for (int i = 0; i < n; i += 4) {
    sum += arr[i];
    sum += arr[i+1];
    sum += arr[i+2];
    sum += arr[i+3];
}

// 提示編譯器展開
#pragma GCC unroll 4
for (int i = 0; i < n; ++i) {
    process(arr[i]);
}
```

### 3. 向量化 (Vectorization)
```cpp
// 自動向量化提示
void add_arrays(float* __restrict a,
                float* __restrict b,
                float* __restrict c,
                int n) {
    #pragma GCC ivdep  // 忽略相依性
    for (int i = 0; i < n; ++i) {
        c[i] = a[i] + b[i];
    }
}

// OpenMP SIMD
#pragma omp simd
for (int i = 0; i < n; ++i) {
    c[i] = a[i] * b[i];
}
```

## 連結時優化 (LTO)

### 啟用 LTO
```bash
# 編譯和連結都需要 -flto
g++ -c -O3 -flto file1.cpp -o file1.o
g++ -c -O3 -flto file2.cpp -o file2.o
g++ -O3 -flto file1.o file2.o -o program

# 或一次編譯
g++ -O3 -flto file1.cpp file2.cpp -o program

# 平行 LTO
g++ -O3 -flto=auto *.cpp -o program
```

## Profile-Guided Optimization (PGO)

### PGO 工作流程
```bash
# 步驟 1: 使用儀器化編譯
g++ -fprofile-generate -O2 program.cpp -o program

# 步驟 2: 執行程式收集 profile
./program < typical_input.txt

# 步驟 3: 使用 profile 重新編譯
g++ -fprofile-use -O3 program.cpp -o program_optimized
```

### Clang PGO
```bash
# 儀器化
clang++ -fprofile-instr-generate program.cpp -o program

# 執行並生成原始 profile
LLVM_PROFILE_FILE=program.profraw ./program

# 轉換 profile
llvm-profdata merge program.profraw -o program.profdata

# 優化編譯
clang++ -fprofile-instr-use=program.profdata -O3 program.cpp
```

## 編譯器特定屬性

### 1. 函數屬性
```cpp
// 純函數（無副作用）
__attribute__((pure)) int compute(int x, int y);

// const 函數（只依賴參數）
__attribute__((const)) int square(int x);

// 熱函數/冷函數
__attribute__((hot)) void frequently_called();
__attribute__((cold)) void rarely_called();

// 建構/解構優先級
__attribute__((constructor(101))) void early_init();
__attribute__((destructor)) void cleanup();
```

### 2. 分支預測
```cpp
// GCC/Clang
#define likely(x)   __builtin_expect(!!(x), 1)
#define unlikely(x) __builtin_expect(!!(x), 0)

if (likely(ptr != nullptr)) {
    // 常見情況
}

// C++20
if (condition) [[likely]] {
    // 常見路徑
} else [[unlikely]] {
    // 罕見路徑
}
```

## 限制指標 (Restrict)

```cpp
// C99 restrict in C++
void process(float* __restrict a,
             float* __restrict b,
             float* __restrict c, int n) {
    // 編譯器知道 a, b, c 不會重疊
    for (int i = 0; i < n; ++i) {
        c[i] = a[i] + b[i];
    }
}
```

## 編譯器優化障礙

```cpp
// 防止編譯器重排
void memory_barrier() {
    asm volatile("" ::: "memory");
}

// 防止優化掉變數
template<typename T>
void do_not_optimize(T& value) {
    asm volatile("" : "+r,m"(value) : : "memory");
}

// volatile 避免優化
volatile int counter = 0;
```

## 診斷優化

### 1. 優化報告
```bash
# GCC
g++ -O3 -fopt-info-vec-optimized program.cpp

# 詳細向量化報告
g++ -O3 -ftree-vectorize -fopt-info-vec-all program.cpp

# Clang
clang++ -O3 -Rpass=loop-vectorize program.cpp
```

### 2. 組合語言輸出
```bash
# 生成組合語言
g++ -S -O3 -fverbose-asm program.cpp

# Intel 語法
g++ -S -O3 -masm=intel program.cpp

# 只看特定函數（使用 objdump）
g++ -O3 -c program.cpp
objdump -d -M intel -C program.o | grep -A 20 "function_name"
```

## 特定架構優化

### x86/x64 優化
```cpp
// 使用特定指令集
#ifdef __AVX2__
    // AVX2 程式碼
#elif __SSE4_2__
    // SSE4.2 程式碼
#else
    // 通用程式碼
#endif

// 編譯時檢查
#include <immintrin.h>
#if defined(__AVX512F__)
    void process_avx512(float* data) {
        // AVX-512 實作
    }
#endif
```

## 編譯時計算優化

```cpp
// constexpr 確保編譯時計算
template<int N>
struct Fibonacci {
    static constexpr int value = Fibonacci<N-1>::value +
                                 Fibonacci<N-2>::value;
};

template<> struct Fibonacci<0> { static constexpr int value = 0; };
template<> struct Fibonacci<1> { static constexpr int value = 1; };

// 使用
constexpr int fib10 = Fibonacci<10>::value;  // 編譯時計算
```

## 最佳實踐

1. **從 -O2 開始**
   - 平衡優化和編譯時間
   - 較好的除錯體驗

2. **謹慎使用 -O3**
   - 可能增加程式大小
   - 某些情況可能更慢

3. **使用 PGO**
   - 對實際工作負載優化
   - 可提升 10-30% 性能

4. **測試不同選項**
   - 每個程式不同
   - 使用基準測試驗證

5. **了解目標架構**
   - 使用 -march=native
   - 考慮部署環境

## 常見陷阱

1. **過度依賴編譯器優化**
2. **忽略演算法複雜度**
3. **未定義行為導致錯誤優化**
4. **忽略快取效應**
5. **過早優化**