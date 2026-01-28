# Chapter 14 - Parallel Algorithms

重點摘要
- divide-and-conquer 的平行拆分策略。
- parallel transform/copy_if 等並行演算法。
- 平行基準測試與負載切割。

關鍵程式碼
- divide_and_benchmark.cpp
```cpp
    // 關鍵技術：執行緒生命週期管理。
    std::size_t n_cores = std::thread::hardware_concurrency();
    std::size_t n_tasks = std::max(n_cores, std::size_t(1));
    std::size_t chunk_sz = (n + n_tasks - 1) / n_tasks;
```

程式碼清單
- divide_and_benchmark.cpp
- divide_and_conquer.cpp
- divide_and_count_if.cpp
- naive_par_transform.cpp
- par_copy_if.cpp
- par_copy_n_move.cpp
- parallel_benchmark.cpp
