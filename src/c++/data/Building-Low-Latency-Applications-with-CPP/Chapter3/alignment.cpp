#include <cstdio>
#include <cstdint>
#include <cstddef>

// ⚠️ 不良對齊：成員順序導致大量 padding 浪費
// 記憶體佈局：[c][pad][u][pad][d][i][pad] = 16 bytes（浪費 7 bytes）
struct PoorlyAlignedData {
    char c;        // 1 byte
    uint16_t u;    // 2 bytes（需對齊到 2 的倍數）
    double d;      // 8 bytes（需對齊到 8 的倍數）
    int16_t i;     // 2 bytes
};

// ✅ 良好對齊：將最大對齊要求的成員放最前面
// 記憶體佈局：[d][u][i][c][pad] = 16 bytes（只浪費 3 bytes）
// ⚡ 效能關鍵：對齊存取比未對齊快 10-15 倍
struct WellAlignedData {
    double d;      // 8 bytes（放最前面，對齊到 8）
    uint16_t u;    // 2 bytes
    int16_t i;     // 2 bytes
    char c;        // 1 byte
};

// 🗜️ Packed 結構：完全移除 padding
// 記憶體佈局：[d][u][i][c] = 13 bytes
// ⚠️ 注意：未對齊存取會嚴重降低效能，僅適用於網路協定/檔案格式
#pragma pack(push, 1)
struct PackedData {
    double d;
    uint16_t u;
    int16_t i;
    char c;
};
#pragma pack(pop)

int main()
{
    // 輸出各成員的記憶體偏移量，觀察 padding 的影響
    printf("PoorlyAlignedData c:%lu u:%lu d:%lu i:%lu size:%lu\n",
           offsetof(struct PoorlyAlignedData, c), offsetof(struct PoorlyAlignedData, u),
           offsetof(struct PoorlyAlignedData, d), offsetof(struct PoorlyAlignedData, i),
           sizeof(PoorlyAlignedData));
    printf("WellAlignedData d:%lu u:%lu i:%lu c:%lu size:%lu\n",
           offsetof(struct WellAlignedData, d), offsetof(struct WellAlignedData, u),
           offsetof(struct WellAlignedData, i), offsetof(struct WellAlignedData, c),
           sizeof(WellAlignedData));
    printf("PackedData d:%lu u:%lu i:%lu c:%lu size:%lu\n",
           offsetof(struct PackedData, d), offsetof(struct PackedData, u),
           offsetof(struct PackedData, i), offsetof(struct PackedData, c),
           sizeof(PackedData));
}
