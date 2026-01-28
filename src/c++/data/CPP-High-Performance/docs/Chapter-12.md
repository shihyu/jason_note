# Chapter 12 - Coroutines and Lazy Generators

重點摘要
- generator 與協程協議的基本結構。
- lazy range/iterator 的互通與延遲生產。
- co_await/co_yield 的實際範例。

關鍵程式碼
- callback.cpp
```cpp
    // 關鍵技術：協程與 lazy generator。
    T diff = static_cast<T>(stop - start) / (n - 1);
    for (int i = 0; i != n; ++i) {
        f(start + diff * i);
    }
```

程式碼清單
- callback.cpp
- co_lambda.cpp
- co_member.cpp
- co_thread.cpp
- coro_iota.cpp
- coro_printVec.cpp
- eager.cpp
- gap_encode_decode.cpp
- generator.cpp
- generator.h
- include_check.h
- iterator.cpp
- lazy_coro.cpp
- lazy_range.cpp
- variable_bytes.cpp
