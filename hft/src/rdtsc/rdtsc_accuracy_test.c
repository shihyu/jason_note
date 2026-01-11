#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include <math.h>

static inline uint64_t rdtsc() {
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

// 測試 RDTSC 本身的開銷
void test_rdtsc_overhead() {
    const int iterations = 1000;
    uint64_t min = UINT64_MAX;
    uint64_t max = 0;
    uint64_t total = 0;

    printf("測試 RDTSC 指令本身的開銷 (連續呼叫 %d 次):\n", iterations);

    for (int i = 0; i < iterations; i++) {
        uint64_t start = rdtsc();
        uint64_t end = rdtsc();
        uint64_t diff = end - start;

        if (diff < min) min = diff;
        if (diff > max) max = diff;
        total += diff;
    }

    uint64_t avg = total / iterations;
    printf("  最小值: %lu cycles\n", min);
    printf("  最大值: %lu cycles\n", max);
    printf("  平均值: %lu cycles\n", avg);
    printf("  變異範圍: %lu cycles\n\n", max - min);
}

// 測試空操作的測量精度
void test_empty_measurement() {
    const int iterations = 100;
    printf("測試空操作測量 (執行 %d 次):\n", iterations);

    for (int i = 0; i < 10; i++) {
        uint64_t start = rdtsc();
        // 完全空的操作
        uint64_t end = rdtsc();
        printf("  測試 %d: %lu cycles\n", i + 1, end - start);
    }
    printf("\n");
}

// 使用 clock_gettime 交叉驗證
void test_clock_comparison() {
    printf("與 clock_gettime 交叉驗證:\n");

    struct timespec ts_start, ts_end;
    uint64_t rdtsc_start, rdtsc_end;

    // 預熱
    for (int i = 0; i < 1000000; i++) {
        volatile int x = i * 2;
        (void)x;
    }

    clock_gettime(CLOCK_MONOTONIC, &ts_start);
    rdtsc_start = rdtsc();

    // 執行相同操作
    for (int i = 0; i < 1000000; i++) {
        volatile int x = i * 2;
        (void)x;
    }

    rdtsc_end = rdtsc();
    clock_gettime(CLOCK_MONOTONIC, &ts_end);

    uint64_t cycles = rdtsc_end - rdtsc_start;
    double ns_clock = (ts_end.tv_sec - ts_start.tv_sec) * 1e9 +
                      (ts_end.tv_nsec - ts_start.tv_nsec);

    printf("  RDTSC 測量: %lu cycles\n", cycles);
    printf("  clock_gettime 測量: %.0f ns\n", ns_clock);
    printf("  推算 CPU 頻率: %.2f GHz\n\n", cycles / ns_clock);
}

// 測試測量的可重複性
void test_repeatability() {
    const int iterations = 20;
    printf("測試測量可重複性 (相同操作執行 %d 次):\n", iterations);

    uint64_t results[iterations];
    uint64_t sum = 0;

    // 預熱
    for (int i = 0; i < 10000; i++) {
        volatile int x = i;
        (void)x;
    }

    for (int i = 0; i < iterations; i++) {
        uint64_t start = rdtsc();
        for (int j = 0; j < 10000; j++) {
            volatile int x = j;
            (void)x;
        }
        uint64_t end = rdtsc();
        results[i] = end - start;
        sum += results[i];
    }

    uint64_t avg = sum / iterations;
    uint64_t min = results[0];
    uint64_t max = results[0];

    for (int i = 0; i < iterations; i++) {
        if (results[i] < min) min = results[i];
        if (results[i] > max) max = results[i];
    }

    // 計算標準差
    double variance = 0;
    for (int i = 0; i < iterations; i++) {
        double diff = (double)results[i] - (double)avg;
        variance += diff * diff;
    }
    double std_dev = sqrt(variance / iterations);

    printf("  平均值: %lu cycles\n", avg);
    printf("  最小值: %lu cycles\n", min);
    printf("  最大值: %lu cycles\n", max);
    printf("  標準差: %.2f cycles\n", std_dev);
    printf("  變異係數: %.2f%%\n\n", (std_dev / avg) * 100);
}

int main() {
    printf("=== RDTSC 準確性與穩定性測試 ===\n\n");

    test_rdtsc_overhead();
    test_empty_measurement();
    test_clock_comparison();
    test_repeatability();

    return 0;
}
