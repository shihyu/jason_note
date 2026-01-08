#include <cstdio>
#include <cstdint>

int main()
{
    double x = 100;
    const auto orig_x = x;

    // ⚠️ 違反嚴格別名規則（Strict Aliasing Rule）
    // 問題：不同類型的指標不應指向同一記憶體（會導致未定義行為）
    // 後果：編譯器基於別名規則進行優化，可能將 x 快取在暫存器中，
    //       導致 *x_as_ui 的修改不可見（x 仍顯示為 100.00）
    auto x_as_ui = (uint64_t*) (&x);
    *x_as_ui |= 0x8000000000000000;  // 試圖修改 double 的符號位

    // ⚡ 正確做法：使用 std::memcpy、union 或 std::bit_cast（C++20）
    printf("orig_x:%0.2f x:%0.2f &x:%p &x_as_ui:%p\n", orig_x, x, &x, x_as_ui);
}
