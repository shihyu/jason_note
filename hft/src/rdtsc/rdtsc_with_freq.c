#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>

// 使用 RDTSC 測量 CPU 週期
static inline uint64_t rdtsc() {
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

// 動態校準 CPU 頻率(透過實際測量)
double calibrate_cpu_freq() {
    struct timespec start_time, end_time;
    uint64_t start_cycles, end_cycles;

    // 測量 1 秒鐘的 CPU 週期數
    clock_gettime(CLOCK_MONOTONIC, &start_time);
    start_cycles = rdtsc();

    sleep(1);  // 等待 1 秒

    end_cycles = rdtsc();
    clock_gettime(CLOCK_MONOTONIC, &end_time);

    // 計算實際經過的時間(秒)
    double elapsed = (end_time.tv_sec - start_time.tv_sec) +
                     (end_time.tv_nsec - start_time.tv_nsec) / 1e9;

    // 計算 CPU 頻率(GHz)
    uint64_t cycles = end_cycles - start_cycles;
    double freq_ghz = cycles / elapsed / 1e9;

    return freq_ghz;
}

void process_order() {
    volatile int sum = 0;
    for (int i = 0; i < 1000000; i++) {
        sum += i;
    }
}

int main() {
    printf("正在校準 CPU 頻率...\n");
    double cpu_freq_ghz = calibrate_cpu_freq();
    printf("測得 CPU 頻率: %.2f GHz\n\n", cpu_freq_ghz);

    // 預熱
    process_order();

    // 測量 10 次取平均
    const int iterations = 10;
    uint64_t total_cycles = 0;

    printf("執行 %d 次測量:\n", iterations);
    for (int i = 0; i < iterations; i++) {
        uint64_t start = rdtsc();
        process_order();
        uint64_t end = rdtsc();
        total_cycles += (end - start);
    }

    uint64_t avg_cycles = total_cycles / iterations;
    double avg_ns = avg_cycles / cpu_freq_ghz;

    printf("平均 CPU Cycles: %lu\n", avg_cycles);
    printf("平均時間: %.2f ns\n", avg_ns);
    printf("平均時間: %.2f us\n", avg_ns / 1000.0);
    printf("平均時間: %.4f ms\n", avg_ns / 1e6);

    return 0;
}
