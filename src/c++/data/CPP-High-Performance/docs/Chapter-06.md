# Chapter 06 - Ranges and Views

重點摘要
- view 的延遲計算避免中間容器。
- range 組合提高表達力並控制成本。
- materialize 與 lazy 的取捨。

關鍵程式碼
- flatten.cpp
```cpp
    // 關鍵技術：view 延遲計算避免中間容器。
    auto flattened_view = std::views::join(list_of_lists);
    
    for (auto element : flattened_view) {
        std::cout << element << " ";
```

程式碼清單
- flatten.cpp
- generic.cpp
- get_max_score.cpp
- get_max_score_refactor.cpp
- get_max_score_views.cpp
- lazy.cpp
- materialise.cpp
- take.cpp
