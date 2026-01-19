# Chapter 10 - Proxy Objects and Lazy Evaluation

重點摘要
- 代理物件延遲評估避免中間資料。
- 小型基準比較字串與向量操作成本。

關鍵程式碼
- bm_Vec2D.cpp
```cpp
    // 關鍵技術：reserve 預先配置容量，降低重新配置成本。
    vvec.reserve(n);
    
    for (std::size_t i = 0; i != n; ++i) {
        vvec.push_back(Vec2D(coord(), coord()));
```

程式碼清單
- bm_Vec2D.cpp
- bm_strcmp.cpp
- concat_proxy.cpp
