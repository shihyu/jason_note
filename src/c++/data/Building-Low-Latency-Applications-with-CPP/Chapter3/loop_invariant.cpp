#include <cstdlib>

int main()
{
    auto doSomething = [](double r) noexcept {
        // ⚡ 關鍵路徑：函式內避免鎖/分配，保持快取局部性。
        return 3.14 * r * r;
    };
    [[maybe_unused]] int a[100], b = rand();

    // ❌ 原始版本：在迴圈內重複計算不變量
    // 問題：doSomething(50) 和 b*2 在每次迭代都重新計算
    // 成本：100 次函式呼叫 + 100 次乘法（浪費數千個 CPU 週期）
    for (auto i = 0; i < 100; ++i) {
        a[i] = (doSomething(50) + b * 2) + 1;
    }

    // ✅ 迴圈不變量提取：將不變的計算移到迴圈外
    // ⚡ 效能關鍵：只計算一次，節省 99 次重複計算
    // 原理：表達式結果不依賴迴圈變數 i，可安全提取
    auto temp = (doSomething(50) + b * 2) + 1;

    for (auto i = 0; i < 100; ++i) {
        a[i] = temp;  // 直接使用快取結果
    }
}