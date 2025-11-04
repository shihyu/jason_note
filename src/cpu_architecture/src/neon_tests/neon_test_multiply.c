/**
 * neon_test_multiply.c - NEON 向量乘法測試
 *
 * 比較 NEON intrinsics 與純 C 迴圈的效能差異
 * 測試項目：
 *   - float32 向量乘法
 *   - 不同資料量測試 (1KB, 1MB, 10MB)
 */

#include "common.h"

/**
 * 純 C 實作：float 陣列乘法
 */
void multiply_float_c(const float *a, const float *b, float *result, size_t n) {
    for (size_t i = 0; i < n; i++) {
        result[i] = a[i] * b[i];
    }
}

/**
 * NEON 實作：float 陣列乘法
 *
 * 使用 vmulq_f32 一次處理 4 個 float
 */
void multiply_float_neon(const float *a, const float *b, float *result, size_t n) {
    size_t i = 0;

    // 每次處理 4 個 float (128-bit 向量)
    size_t vec_size = n / 4;
    for (i = 0; i < vec_size; i++) {
        // 載入 4 個 float
        float32x4_t va = vld1q_f32(a + i * 4);
        float32x4_t vb = vld1q_f32(b + i * 4);

        // 向量乘法
        float32x4_t vresult = vmulq_f32(va, vb);

        // 儲存結果
        vst1q_f32(result + i * 4, vresult);
    }

    // 處理剩餘元素
    for (i = vec_size * 4; i < n; i++) {
        result[i] = a[i] * b[i];
    }
}

/**
 * 測試指定大小的資料
 */
void test_multiply_with_size(size_t num_elements, int iterations) {
    char size_str[64];
    format_size(num_elements * sizeof(float), size_str, sizeof(size_str));

    printf("\n  測試資料大小: %zu 個 float (%s)\n", num_elements, size_str);
    printf("  ─────────────────────────────────────\n");

    // 分配記憶體
    float *a = (float *)memalign(16, num_elements * sizeof(float));
    float *b = (float *)memalign(16, num_elements * sizeof(float));
    float *result_c = (float *)memalign(16, num_elements * sizeof(float));
    float *result_neon = (float *)memalign(16, num_elements * sizeof(float));

    if (!a || !b || !result_c || !result_neon) {
        print_error("記憶體分配失敗");
        return;
    }

    // 產生測試資料
    generate_random_float_array(a, num_elements, -100.0f, 100.0f);
    generate_random_float_array(b, num_elements, -100.0f, 100.0f);

    // 測試純 C 實作
    Timer timer;
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        multiply_float_c(a, b, result_c, num_elements);
    }
    timer_stop(&timer);
    double time_c = timer_get_ms(&timer);

    // 測試 NEON 實作
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        multiply_float_neon(a, b, result_neon, num_elements);
    }
    timer_stop(&timer);
    double time_neon = timer_get_ms(&timer);

    // 驗證正確性
    int passed = float_array_equal(result_c, result_neon, num_elements, EPSILON);

    if (passed) {
        print_success("正確性驗證通過");
    } else {
        print_error("正確性驗證失敗");
    }

    // 顯示效能比較
    print_performance_comparison("向量乘法", time_c, time_neon);

    // 釋放記憶體
    free(a);
    free(b);
    free(result_c);
    free(result_neon);
}

/**
 * 主程式
 */
int main(void) {
    print_test_header("NEON 向量乘法測試");

    printf("\n  測試說明:\n");
    printf("  - 比較純 C 與 NEON intrinsics 的效能\n");
    printf("  - NEON 使用 vmulq_f32 一次處理 4 個 float\n");
    printf("  - 測試不同資料量的效能表現\n");

    // 初始化亂數種子
    srand(time(NULL));

    // 測試不同資料大小
    print_subtest_header("小資料量測試 (1KB)");
    test_multiply_with_size(SIZE_1KB / sizeof(float), 10000);

    print_subtest_header("中資料量測試 (1MB)");
    test_multiply_with_size(SIZE_1MB / sizeof(float), 100);

    print_subtest_header("大資料量測試 (10MB)");
    test_multiply_with_size(SIZE_10MB / sizeof(float), 10);

    // 總結
    printf("\n");
    printf(COLOR_CYAN "════════════════════════════════════════\n");
    printf("  測試完成！\n");
    printf("════════════════════════════════════════\n" COLOR_RESET);

    printf("\n" COLOR_BOLD "預期結果:\n" COLOR_RESET);
    printf("  - 小資料量: NEON 加速 2-3x\n");
    printf("  - 大資料量: NEON 加速 3-4x\n");
    printf("  - 所有測試正確性驗證應通過\n\n");

    return 0;
}
