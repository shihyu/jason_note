#include <cstdint>

int main()
{
    const auto price = 10.125; // prices are like: 10.125, 10.130, 10.135...
    constexpr auto min_price_increment = 0.005;  // 最小價格跳動單位
    [[maybe_unused]] int64_t int_price = 0;

    // ❌ 無強度削減：使用除法（極慢）
    // 成本：DIVSD 指令需要 20-40 個 CPU 週期
    int_price = price / min_price_increment;

    // ✅ 強度削減：將除法轉換為乘法
    // ⚡ 效能關鍵：MULSD 指令只需 4-5 個週期（5-8 倍快）
    // 原理：預先計算倒數（編譯期常數），執行期只需乘法
    constexpr auto inv_min_price_increment = 1 / min_price_increment;  // 200.0
    int_price = price * inv_min_price_increment;
}