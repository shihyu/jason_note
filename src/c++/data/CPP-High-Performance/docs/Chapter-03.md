# Chapter 03 - Analysing and Measuring Performance

重點摘要
- 基準測試方法與量測誤差控制。
- 線性搜尋與二分搜尋的複雜度差異。
- 範例 profiler 與測試流程。

關鍵程式碼
- binary_search.cpp
```cpp
    // 關鍵技術：透過區間縮減達到 O(log n) 搜尋。
    while (lo <= hi) {
        auto mid = lo;
        std::advance(mid, (hi - lo) / 2);
```

程式碼清單
- binary_search.cpp
- bm_linear_search.cpp
- bm_linear_search_with_range.cpp
- example_profiler.cpp
- linear_search.cpp
- linear_vs_binary.cpp
