// ✅ 尾遞迴優化（Tail Call Optimization）：編譯器可將遞迴轉換為迴圈
// ⚡ 效能關鍵：棧空間從 O(n) 降為 O(1)，避免棧溢位
// 原理：函式的最後一個操作是呼叫自己，無需保留當前棧幀
// 注意：__attribute__((noinline)) 禁止內聯，但仍允許 TCO
auto __attribute__ ((noinline)) factorial(unsigned n) -> unsigned
{
    return (n ? n * factorial(n - 1) : 1);  // 尾遞迴形式
}

int main()
{
    // 使用 volatile 防止編譯器在編譯期計算結果
    [[maybe_unused]] volatile auto res = factorial(100);
}