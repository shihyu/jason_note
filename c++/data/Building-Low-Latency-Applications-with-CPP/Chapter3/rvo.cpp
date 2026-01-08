#include <iostream>

struct LargeClass {
    int i;
    char c;
    double d;
};

// ✅ RVO（Return Value Optimization）：編譯器直接在返回值位置構造物件
// ⚡ 效能關鍵：避免複製（節省 1 次複製建構子 + 1 次解構子）
// 原理：編譯器將返回值的記憶體地址作為隱藏參數傳入，直接在該位置構造
auto rvoExample(int i, char c, double d)
{
    return LargeClass{i, c, d};  // C++17 保證無複製
}

int main()
{
    LargeClass lc_obj = rvoExample(10, 'c', 3.14);  // 無臨時物件，直接構造
}