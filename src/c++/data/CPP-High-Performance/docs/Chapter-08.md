# Chapter 08 - Compile-Time Programming

重點摘要
- constexpr 計算降低執行期成本。
- concepts 與型別約束協助最佳化。
- 靜態多型與動態多型成本比較。
- 編譯期基準測試觀念。

關鍵程式碼
- AnimalConstexpr.cpp
```cpp
    // 關鍵技術：編譯期計算降低執行期成本。
    if constexpr (std::is_same_v<Animal, Bear>) {
        a.roar();
    // } else if (std::is_same_v<Animal, Dog>){
    } else if constexpr (std::is_same_v<Animal, Dog>){
```

程式碼清單
- AnimalConstexpr.cpp
- AnimalPolymorphic.cpp
- Point2D.cpp
- Point2D_concepts.cpp
- bm_animal.cpp
- cts_benchmark.cpp
- generic_mod.cpp
