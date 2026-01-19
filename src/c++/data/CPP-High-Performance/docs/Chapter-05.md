# Chapter 05 - Algorithms

重點摘要
- 旋轉與排序等核心演算法的成本差異。
- 基準測試比較不同實作的效能。

關鍵程式碼
- sar.cpp
```cpp
    // 關鍵技術：std::rotate 就地旋轉，避免額外配置。
    std::rotate(t.begin(), t.begin() += n, t.end());
}

template <typename T>
```

程式碼清單
- sar.cpp
- sort_benchmarks.cpp
