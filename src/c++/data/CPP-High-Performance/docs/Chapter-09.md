# Chapter 09 - Essential Utilities

重點摘要
- variant/visit 的分派成本與用法。
- tuple 走訪與編譯期迭代技巧。
- 模板技巧支援泛用工具。

關鍵程式碼
- Widget.cpp
```cpp
    // 關鍵技術：variant/visit 分派降低虛擬呼叫成本。
    std::variant<double, Widget> v = 1.0;
    std::cout << "v = " << std::get<0>(v) << '\n';
    
    attempt1(v);
```

程式碼清單
- Widget.cpp
- any_of_tuple.cpp
- for_each_tuple.cpp
- in_variant_vec.cpp
- reflection.cpp
- sizeof_tuple.cpp
- the_quest_for_terseness.cpp
- visit.cpp
