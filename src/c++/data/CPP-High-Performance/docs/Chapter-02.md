# Chapter 02 - Essential C++ Techniques

重點摘要
- Rule of Five 與移動語意的資源管理。
- Copy-and-swap 與例外安全的更新流程。
- RAII 與鎖的基本用法，降低錯誤與同步開銷。
- 介面設計避免不必要拷貝。

關鍵程式碼
- foo.cpp
```cpp
    // 關鍵技術：std::move 觸發移動語意，降低拷貝成本。
    std::move(bar).func();
    
    // rvalue
    Foo().func();
```

程式碼清單
- foo.cpp
- menu.cpp
- mutex.cpp
- rule_of_five.cpp
- widget.cpp
