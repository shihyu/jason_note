/**
 * common.h - ARM NEON 測試專案共用標頭檔
 *
 * 提供效能測量、結果驗證等共用函數
 */

#ifndef COMMON_H
#define COMMON_H

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <math.h>
#include <malloc.h>  // for memalign
#include <arm_neon.h>

// 顏色輸出（在 Android shell 中可用）
#define COLOR_RESET   "\033[0m"
#define COLOR_RED     "\033[31m"
#define COLOR_GREEN   "\033[32m"
#define COLOR_YELLOW  "\033[33m"
#define COLOR_BLUE    "\033[34m"
#define COLOR_MAGENTA "\033[35m"
#define COLOR_CYAN    "\033[36m"
#define COLOR_BOLD    "\033[1m"

// 測試資料大小（bytes）
#define SIZE_1KB   (1024)
#define SIZE_1MB   (1024 * 1024)
#define SIZE_10MB  (10 * 1024 * 1024)

// 預設測試次數
#define DEFAULT_ITERATIONS 100

// 錯誤容差（浮點數比較）
#define EPSILON 1e-6f

/**
 * 計時器結構
 */
typedef struct {
    struct timespec start;
    struct timespec end;
    double elapsed_ms;
} Timer;

/**
 * 測試結果結構
 */
typedef struct {
    const char *name;
    double time_c;        // 純 C 實作時間（毫秒）
    double time_neon;     // NEON 實作時間（毫秒）
    double speedup;       // 加速比
    int passed;           // 正確性測試是否通過
} TestResult;

/**
 * 啟動計時器
 */
static inline void timer_start(Timer *timer) {
    clock_gettime(CLOCK_MONOTONIC, &timer->start);
}

/**
 * 停止計時器並計算經過時間（毫秒）
 */
static inline void timer_stop(Timer *timer) {
    clock_gettime(CLOCK_MONOTONIC, &timer->end);
    timer->elapsed_ms = (timer->end.tv_sec - timer->start.tv_sec) * 1000.0 +
                        (timer->end.tv_nsec - timer->start.tv_nsec) / 1000000.0;
}

/**
 * 取得經過時間（毫秒）
 */
static inline double timer_get_ms(const Timer *timer) {
    return timer->elapsed_ms;
}

/**
 * 比較兩個浮點數陣列是否相等（容許誤差）
 *
 * @param a 陣列 A
 * @param b 陣列 B
 * @param n 元素個數
 * @param epsilon 容許誤差
 * @return 1 表示相等，0 表示不相等
 */
static inline int float_array_equal(const float *a, const float *b, size_t n, float epsilon) {
    for (size_t i = 0; i < n; i++) {
        float diff = fabsf(a[i] - b[i]);
        if (diff > epsilon) {
            printf(COLOR_RED "  ✗ 位置 %zu: %.6f vs %.6f (差異 %.6f)\n" COLOR_RESET,
                   i, a[i], b[i], diff);
            return 0;
        }
    }
    return 1;
}

/**
 * 比較兩個整數陣列是否相等
 */
static inline int int_array_equal(const int *a, const int *b, size_t n) {
    for (size_t i = 0; i < n; i++) {
        if (a[i] != b[i]) {
            printf(COLOR_RED "  ✗ 位置 %zu: %d vs %d\n" COLOR_RESET,
                   i, a[i], b[i]);
            return 0;
        }
    }
    return 1;
}

/**
 * 比較兩個 uint8_t 陣列是否相等
 */
static inline int uint8_array_equal(const uint8_t *a, const uint8_t *b, size_t n) {
    for (size_t i = 0; i < n; i++) {
        if (a[i] != b[i]) {
            printf(COLOR_RED "  ✗ 位置 %zu: %u vs %u\n" COLOR_RESET,
                   i, a[i], b[i]);
            return 0;
        }
    }
    return 1;
}

/**
 * 產生隨機浮點數陣列
 *
 * @param data 輸出陣列
 * @param n 元素個數
 * @param min 最小值
 * @param max 最大值
 */
static inline void generate_random_float_array(float *data, size_t n, float min, float max) {
    for (size_t i = 0; i < n; i++) {
        data[i] = min + (max - min) * ((float)rand() / (float)RAND_MAX);
    }
}

/**
 * 產生隨機整數陣列
 */
static inline void generate_random_int_array(int *data, size_t n, int min, int max) {
    for (size_t i = 0; i < n; i++) {
        data[i] = min + rand() % (max - min + 1);
    }
}

/**
 * 產生隨機 uint8_t 陣列
 */
static inline void generate_random_uint8_array(uint8_t *data, size_t n) {
    for (size_t i = 0; i < n; i++) {
        data[i] = rand() % 256;
    }
}

/**
 * 列印測試標題
 */
static inline void print_test_header(const char *title) {
    printf("\n");
    printf(COLOR_CYAN COLOR_BOLD "════════════════════════════════════════\n");
    printf("  %s\n", title);
    printf("════════════════════════════════════════\n" COLOR_RESET);
}

/**
 * 列印子測試標題
 */
static inline void print_subtest_header(const char *title) {
    printf("\n" COLOR_YELLOW "  [%s]\n" COLOR_RESET, title);
}

/**
 * 列印測試結果
 */
static inline void print_test_result(const TestResult *result) {
    printf("\n");
    printf("  測試項目: %s\n", result->name);
    printf("  ─────────────────────────────────────\n");
    printf("  純 C 實作:   %8.3f ms\n", result->time_c);
    printf("  NEON 實作:   %8.3f ms\n", result->time_neon);
    printf("  加速比:      %8.2fx\n", result->speedup);
    printf("  正確性:      ");

    if (result->passed) {
        printf(COLOR_GREEN "✓ 通過\n" COLOR_RESET);
    } else {
        printf(COLOR_RED "✗ 失敗\n" COLOR_RESET);
    }
}

/**
 * 列印效能比較
 */
static inline void print_performance_comparison(const char *name,
                                                 double time_c,
                                                 double time_neon) {
    double speedup = time_c / time_neon;
    printf("  %-20s: C=%.3fms, NEON=%.3fms, ", name, time_c, time_neon);

    if (speedup >= 2.0) {
        printf(COLOR_GREEN "%.2fx ⚡\n" COLOR_RESET, speedup);
    } else if (speedup >= 1.5) {
        printf(COLOR_YELLOW "%.2fx\n" COLOR_RESET, speedup);
    } else {
        printf(COLOR_RED "%.2fx ⚠\n" COLOR_RESET, speedup);
    }
}

/**
 * 列印成功訊息
 */
static inline void print_success(const char *msg) {
    printf(COLOR_GREEN "  ✓ %s\n" COLOR_RESET, msg);
}

/**
 * 列印錯誤訊息
 */
static inline void print_error(const char *msg) {
    printf(COLOR_RED "  ✗ %s\n" COLOR_RESET, msg);
}

/**
 * 列印警告訊息
 */
static inline void print_warning(const char *msg) {
    printf(COLOR_YELLOW "  ⚠ %s\n" COLOR_RESET, msg);
}

/**
 * 列印資訊訊息
 */
static inline void print_info(const char *msg) {
    printf(COLOR_BLUE "  ℹ %s\n" COLOR_RESET, msg);
}

/**
 * 計算加速比
 */
static inline double calculate_speedup(double time_baseline, double time_optimized) {
    if (time_optimized == 0.0) {
        return 0.0;
    }
    return time_baseline / time_optimized;
}

/**
 * 格式化資料大小
 */
static inline void format_size(size_t bytes, char *buffer, size_t buffer_size) {
    if (bytes >= SIZE_1MB) {
        snprintf(buffer, buffer_size, "%.2f MB", bytes / (double)SIZE_1MB);
    } else if (bytes >= SIZE_1KB) {
        snprintf(buffer, buffer_size, "%.2f KB", bytes / (double)SIZE_1KB);
    } else {
        snprintf(buffer, buffer_size, "%zu B", bytes);
    }
}

#endif // COMMON_H
