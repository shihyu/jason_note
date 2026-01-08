#include <cstddef>

int main()
{
    const size_t size = 1024;
    [[maybe_unused]] float x[size], a[size], b[size];

    // ❌ 無向量化：一次處理 1 個 float
    // 成本：1024 次迭代，每次 1 個加法
    for (size_t i = 0; i < size; ++i) {
        x[i] = a[i] + b[i];
    }

    // ✅ 向量化（SIMD）：一次處理多個 float
    // ⚡ 效能關鍵：編譯器會使用 SSE/AVX 指令，一次處理 4-16 個 float
    // 收益：吞吐量提升 4-16 倍（取決於 SIMD 指令集）
    // 原理：展開迴圈 + 編譯器自動向量化（需要 -O3 -march=native）
    for (size_t i = 0; i < size; i += 4) {
        x[i] = a[i] + b[i];
        x[i + 1] = a[i + 1] + b[i + 1];
        x[i + 2] = a[i + 2] + b[i + 2];
        x[i + 3] = a[i + 3] + b[i + 3];
    }
}