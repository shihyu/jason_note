#include <stdint.h>
#include <stdio.h>
#include <unistd.h>

// 使用 RDTSC(讀取時間戳記計數器)測量 CPU 週期
static inline uint64_t rdtsc() {
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

// 模擬待測量的函式
void process_order() {
    volatile int sum = 0;
    for (int i = 0; i < 1000000; i++) {
        sum += i;
    }
}

int main() {
    // 預熱 CPU(避免初次執行的快取影響)
    process_order();

    // 測量 CPU 週期
    uint64_t start = rdtsc();
    process_order();
    uint64_t end = rdtsc();

    uint64_t cycles = end - start;

    // 換算為奈秒(假設 CPU 頻率 3.0 GHz)
    // 注意: 實際應用中應動態取得 CPU 頻率
    double ns = cycles / 3.0;

    printf("CPU Cycles: %lu\n", cycles);
    printf("Estimated time: %.2f ns (假設 3.0 GHz)\n", ns);
    printf("Estimated time: %.2f us\n", ns / 1000.0);

    // 多次測量取平均值(更準確)
    printf("\n執行 10 次測量:\n");
    uint64_t total_cycles = 0;
    const int iterations = 10;

    for (int i = 0; i < iterations; i++) {
        start = rdtsc();
        process_order();
        end = rdtsc();
        total_cycles += (end - start);
    }

    uint64_t avg_cycles = total_cycles / iterations;
    double avg_ns = avg_cycles / 3.0;

    printf("平均 CPU Cycles: %lu\n", avg_cycles);
    printf("平均時間: %.2f ns\n", avg_ns);
    printf("平均時間: %.2f us\n", avg_ns / 1000.0);

    return 0;
}
