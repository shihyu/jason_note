# Chapter 07 - Memory Management

重點摘要
- 自訂 allocator 與小物件配置策略。
- Arena/記憶體池降低配置與釋放開銷。
- 配置器包裝以整合標準容器。

關鍵程式碼
- Arena.h
```cpp
    // 關鍵技術：自訂配置器降低記憶體配置成本。
    Arena() noexcept : ptr_(buffer_) { }
    
    Arena(const Arena&) = delete;
    Arena& operator=(const Arena&) = delete;
```

程式碼清單
- Arena.h
- main.cpp
- main.cpp
- mallocator.h
- short_alloc.h
