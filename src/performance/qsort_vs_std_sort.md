# C `qsort()` vs C++ `std::sort()`：為什麼效能差這麼多？

一句話總結：

> **`std::sort` 能在「編譯期知道型別與比較方式」，而 `qsort` 只能在「執行期透過 `void* + function pointer`」，這讓編譯器最佳化能力差了一整個等級。**

---

## 1️⃣ 核心差異：inline vs function pointer

### C `qsort()`

```c
void qsort(
    void* base,
    size_t num,
    size_t size,
    int (*compar)(const void*, const void*)
);
```

- 每一次比較都必須：
  - 透過 **function pointer 間接呼叫**
  - 將 `void*` 轉型成實際型別
- 對編譯器而言：
  - ❌ 無法 inline
  - ❌ 無法看穿比較邏輯
  - ❌ 幾乎不能做進階最佳化

➡️ **每次 compare 都是昂貴的 indirect call**

---

### C++ `std::sort()`

```cpp
std::sort(begin, end);               // 預設 std::less<T>
std::sort(begin, end, comp);         // comp 通常是 lambda / functor
```

- 比較器是 **template 參數**
- 型別在 **編譯期已知**
- `std::less<int>::operator()` 幾乎一定會 **inline**

實際產生的機器碼通常只是：

```asm
cmp eax, ebx
jl  ...
```

➡️ **零函式呼叫成本**

---

## 2️⃣ 編譯器最佳化能力的巨大落差

### `std::sort` 可以做到：

- inline comparison
- loop unrolling
- better branch prediction
- 去除多餘的 cast / bounds check
- 在某些情況下可 vectorize

### `qsort` 幾乎全部做不到：

- indirect call 會中斷最佳化 pipeline
- `void*` 讓 alias analysis 直接失效
- comparator 可能有 side effect，編譯器不敢動

---

## 3️⃣ 演算法層面：Introsort vs 未規範的 `qsort`

- C 標準 **沒有規定** `qsort` 必須使用的演算法
- 多數實作仍是 quicksort 或其變形
- C++ `std::sort` 的典型實作：
  - 採用 **Introsort**
    - quicksort（平均快）
    - 遞迴過深 → heap sort（保證 O(N log N)）
    - 小區間 → insertion sort（cache friendly）

➡️ 為現代 CPU / cache hierarchy 高度最佳化

---

## 4️⃣ Cache 與 CPU pipeline 友善度

以排序 `int` 為例：

### `std::sort<int*>`
- 連續記憶體
- 比較極輕量
- branch predictable

### `qsort`
- 每次比較都要 function call
- instruction cache 與 branch predictor 容易被打亂

➡️ 資料越簡單、差距越誇張（3～10 倍很常見）

---

## 5️⃣ 型別安全與語言設計差異（非主要效能原因）

- `qsort`
  - C 時代的通用 API
  - 使用 `void*`
  - 無型別安全

- `std::sort`
  - STL + template 設計
  - 為 **編譯期專用最佳化程式碼** 而生
  - 型別安全

---

## 6️⃣ 工程師版一句話結論

> **`qsort` 慢不是因為 C 慢，而是因為它是「執行期多型」；  
> `std::sort` 快，是因為它是「編譯期多型 + inline + 全最佳化」。**

---

## 7️⃣ 完整效能比較範例程式碼（可直接編譯執行）

以下程式展示 **C `qsort()` 與 C++ `std::sort()` 在相同資料下的效能差異**。

```cpp
// C++ program to compare performance of C qsort() and C++ std::sort()
#include <bits/stdc++.h>
using namespace std;

// Number of elements to be sorted
#define N 1000000

// Comparator function used by qsort
int compare(const void* a, const void* b)
{
    return (*(const int*)a - *(const int*)b);
}

int main()
{
    static int arr[N];
    static int dupArr[N];

    // Seed random number generator
    srand(static_cast<unsigned>(time(nullptr)));

    // Generate random input
    for (int i = 0; i < N; i++)
        dupArr[i] = arr[i] = rand() % 100000;

    clock_t begin, end;
    double time_spent;

    // Measure C qsort()
    begin = clock();
    qsort(arr, N, sizeof(int), compare);
    end = clock();
    time_spent = double(end - begin) / CLOCKS_PER_SEC;
    cout << "Time taken by C qsort(): " << time_spent << " sec" << endl;

    // Measure C++ std::sort()
    begin = clock();
    sort(dupArr, dupArr + N);
    end = clock();
    time_spent = double(end - begin) / CLOCKS_PER_SEC;
    cout << "Time taken by C++ std::sort(): " << time_spent << " sec" << endl;

    return 0;
}
```

### 編譯方式（建議）

```bash
g++ -O2 -std=c++17 sort_benchmark.cpp -o sort_benchmark
```

### 範例輸出

```text
Time taken by C qsort():     0.24 sec
Time taken by C++ std::sort(): 0.08 sec
```

> 實際數值會依 CPU、編譯器版本與最佳化選項而異，但 **`std::sort` 幾乎一定顯著快於 `qsort`**。

---

## 9️⃣ 隱藏的代價：Code Bloat (執行檔大小)

雖然 `std::sort` 快，但它有代價：
- **`qsort`**：只有一份 compiled binary code。不管你排 `int` 還是 `struct`，都呼叫同一份函式庫代碼。
- **`std::sort`**：Template 會為**每種型別與比較器組合**產生一份獨立的機械碼。
  - 排 `vector<int>` 是一份 code
  - 排 `vector<double>` 是另一份 code
  - 排 `vector<Player>` 又是另一份 code

➡️ **效能換空間**：在嵌入式系統或對 binary size 極度敏感的場合，這點值得注意。

---

## 🔟 Context Passing (傳遞參數的痛苦)

如果你需要在比較函式中用到額外參數（例如：「根據外部變數 `OrderMode` 來決定排序方向」）：

### C `qsort` 的痛點
標準 `qsort` 的 comparator 格式固定，無法傳入 userdata。
- ❌ **解法 1**：用全域變數 (Global Variable) → **Thread-unsafe**。
- ⚠️ **解法 2**：用非標準/C11 的 `qsort_r` / `qsort_s` → 跨平台相容性差。

### C++ `std::sort` 的優雅
直接用 Lambda Capture：

```cpp
bool ascending = true;
std::sort(vec.begin(), vec.end(), [ascending](int a, int b) {
    return ascending ? (a < b) : (a > b);
});
```

➡️ **C++ Lambda 完美解決了狀態傳遞問題，且依然能 Inline。**

---

## 1️⃣1️⃣ 現代 C++ 的殺手鐧：Parallel Sort (C++17)

如果資料量巨大（例如 1000 萬筆），C++17 標準庫直接支援平行運算：

```cpp
#include <execution>
#include <algorithm>

// 自動使用多核心平行排序
std::sort(std::execution::par, vec.begin(), vec.end());
```

➡️ **一行程式碼就能利用多核心 CPU，這是 `qsort` 永遠做不到的效能維度。**

---

## 延伸討論（可選）

- 為什麼 `qsort_r()` 幾乎救不了效能
- indirect call 在現代 CPU 上的 cycle penalty
- `objdump` 對比 `qsort` vs `std::sort<int*>` 的 assembly
- branch misprediction 對排序效能的實際影響

