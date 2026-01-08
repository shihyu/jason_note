#include <cstdio>
#include <cstdint>
#include <cstdlib>

// 使用 enum class 定義 BUY/SELL，值設為 1/-1 便於數學運算
enum class Side : int16_t { BUY = 1, SELL = -1 };

int main()
{
    const auto fill_side = (rand() % 2 ? Side::BUY : Side::SELL);
    const int fill_qty = 10;
    printf("fill_side:%s fill_qty:%d.\n",
           (fill_side == Side::BUY ? "BUY" : (fill_side == Side::SELL ? "SELL" :
                   "INVALID")), fill_qty);

    {
        // ❌ 有分支版本：使用 if-else
        // 問題：若分支結果不可預測，Branch Misprediction 會導致 15-20 週期的懲罰
        int last_buy_qty = 0, last_sell_qty = 0, position = 0;

        if (fill_side == Side::BUY) {
            position += fill_qty;
            last_buy_qty = fill_qty;
        } else if (fill_side == Side::SELL) {
            position -= fill_qty;
            last_sell_qty = fill_qty;
        }

        printf("With branching - position:%d last-buy:%d last-sell:%d.\n", position,
               last_buy_qty, last_sell_qty);
    }

    {
        // ✅ 無分支版本：使用算術運算取代條件判斷
        // ⚡ 效能關鍵：延遲穩定（5 ns），不受分支預測影響
        int last_qty[3] = {0, 0, 0}, position = 0;

        auto sideToInt = [](Side side) noexcept {
            return static_cast<int16_t>(side);
        };

        const auto int_fill_side = sideToInt(fill_side);  // BUY=1, SELL=-1
        position += int_fill_side * fill_qty;  // BUY: +10, SELL: -10
        last_qty[int_fill_side + 1] = fill_qty;  // SELL: index 0, BUY: index 2

        printf("Without branching - position:%d last-buy:%d last-sell:%d.\n", position,
               last_qty[sideToInt(Side::BUY) + 1], last_qty[sideToInt(Side::SELL) + 1]);
    }
}