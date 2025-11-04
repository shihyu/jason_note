/**
 * neon_test_fma.c - NEON FMA (Fused Multiply-Add) 測試
 *
 * 測試 FMA 的效能優勢：result = a * b + c
 * FMA 在單一指令中完成乘法和加法，並且只有一次捨入誤差
 *
 * 比較：
 *   1. 純 C 分開計算 (multiply + add)
 *   2. NEON 分開計算 (vmulq + vaddq)
 *   3. NEON FMA (vfmaq_f32 或 vmlaq_f32)
 */

#include "common.h"

/**
 * 純 C 實作：分開計算乘法和加法
 */
void fma_float_c(const float *a, const float *b, const float *c, float *result, size_t n) {
    for (size_t i = 0; i < n; i++) {
        result[i] = a[i] * b[i] + c[i];
    }
}

/**
 * NEON 實作：分開計算 (multiply + add)
 */
void fma_float_neon_separate(const float *a, const float *b, const float *c, float *result, size_t n) {
    size_t i = 0;
    size_t vec_size = n / 4;

    for (i = 0; i < vec_size; i++) {
        float32x4_t va = vld1q_f32(a + i * 4);
        float32x4_t vb = vld1q_f32(b + i * 4);
        float32x4_t vc = vld1q_f32(c + i * 4);

        // 分開計算：先乘法，再加法
        float32x4_t vmul = vmulq_f32(va, vb);
        float32x4_t vresult = vaddq_f32(vmul, vc);

        vst1q_f32(result + i * 4, vresult);
    }

    // 處理剩餘元素
    for (i = vec_size * 4; i < n; i++) {
        result[i] = a[i] * b[i] + c[i];
    }
}

/**
 * NEON 實作：使用 FMA 指令
 *
 * vfmaq_f32(c, a, b) = c + a * b
 * 或
 * vmlaq_f32(c, a, b) = c + a * b (舊版 ARMv7 NEON)
 */
void fma_float_neon_fused(const float *a, const float *b, const float *c, float *result, size_t n) {
    size_t i = 0;
    size_t vec_size = n / 4;

    for (i = 0; i < vec_size; i++) {
        float32x4_t va = vld1q_f32(a + i * 4);
        float32x4_t vb = vld1q_f32(b + i * 4);
        float32x4_t vc = vld1q_f32(c + i * 4);

        // FMA: result = c + a * b (單一指令)
        float32x4_t vresult = vfmaq_f32(vc, va, vb);

        vst1q_f32(result + i * 4, vresult);
    }

    // 處理剩餘元素
    for (i = vec_size * 4; i < n; i++) {
        result[i] = a[i] * b[i] + c[i];
    }
}

/**
 * 測試指定大小的資料
 */
void test_fma_with_size(size_t num_elements, int iterations) {
    char size_str[64];
    format_size(num_elements * sizeof(float), size_str, sizeof(size_str));

    printf("\n  測試資料大小: %zu 個 float (%s)\n", num_elements, size_str);
    printf("  ─────────────────────────────────────\n");

    // 分配記憶體
    float *a = (float *)memalign(16, num_elements * sizeof(float));
    float *b = (float *)memalign(16, num_elements * sizeof(float));
    float *c = (float *)memalign(16, num_elements * sizeof(float));
    float *result_c = (float *)memalign(16, num_elements * sizeof(float));
    float *result_neon_sep = (float *)memalign(16, num_elements * sizeof(float));
    float *result_neon_fma = (float *)memalign(16, num_elements * sizeof(float));

    if (!a || !b || !c || !result_c || !result_neon_sep || !result_neon_fma) {
        print_error("記憶體分配失敗");
        return;
    }

    // 產生測試資料
    generate_random_float_array(a, num_elements, -10.0f, 10.0f);
    generate_random_float_array(b, num_elements, -10.0f, 10.0f);
    generate_random_float_array(c, num_elements, -10.0f, 10.0f);

    // 測試純 C 實作
    Timer timer;
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        fma_float_c(a, b, c, result_c, num_elements);
    }
    timer_stop(&timer);
    double time_c = timer_get_ms(&timer);

    // 測試 NEON 分開計算
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        fma_float_neon_separate(a, b, c, result_neon_sep, num_elements);
    }
    timer_stop(&timer);
    double time_neon_sep = timer_get_ms(&timer);

    // 測試 NEON FMA
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        fma_float_neon_fused(a, b, c, result_neon_fma, num_elements);
    }
    timer_stop(&timer);
    double time_neon_fma = timer_get_ms(&timer);

    // 驗證正確性（注意：FMA 的捨入誤差可能略有不同）
    int passed_sep = float_array_equal(result_c, result_neon_sep, num_elements, EPSILON * 10);
    int passed_fma = float_array_equal(result_c, result_neon_fma, num_elements, EPSILON * 10);

    if (passed_sep && passed_fma) {
        print_success("正確性驗證通過");
    } else {
        if (!passed_sep) print_error("NEON 分開計算驗證失敗");
        if (!passed_fma) print_warning("NEON FMA 驗證失敗（可能因捨入誤差）");
    }

    // 顯示效能比較
    printf("  純 C 實作:            %8.3f ms\n", time_c);
    printf("  NEON 分開 (mul+add):  %8.3f ms (%.2fx)\n",
           time_neon_sep, calculate_speedup(time_c, time_neon_sep));
    printf("  NEON FMA:             %8.3f ms (", time_neon_fma);

    double speedup_vs_c = calculate_speedup(time_c, time_neon_fma);
    double speedup_vs_sep = calculate_speedup(time_neon_sep, time_neon_fma);

    if (speedup_vs_c >= 2.0) {
        printf(COLOR_GREEN "%.2fx vs C" COLOR_RESET, speedup_vs_c);
    } else {
        printf("%.2fx vs C", speedup_vs_c);
    }

    printf(", ");

    if (speedup_vs_sep >= 1.3) {
        printf(COLOR_GREEN "%.2fx vs 分開)" COLOR_RESET, speedup_vs_sep);
    } else {
        printf("%.2fx vs 分開)", speedup_vs_sep);
    }
    printf("\n");

    // 釋放記憶體
    free(a);
    free(b);
    free(c);
    free(result_c);
    free(result_neon_sep);
    free(result_neon_fma);
}

/**
 * 主程式
 */
int main(void) {
    print_test_header("NEON FMA (Fused Multiply-Add) 測試");

    printf("\n  測試說明:\n");
    printf("  - FMA 在單一指令完成 a*b+c\n");
    printf("  - 比較三種實作方式的效能\n");
    printf("  - FMA 優勢：指令數少、延遲低、只有一次捨入誤差\n");

    // 初始化亂數種子
    srand(time(NULL));

    // 測試不同資料大小
    print_subtest_header("小資料量測試 (1KB)");
    test_fma_with_size(SIZE_1KB / sizeof(float), 10000);

    print_subtest_header("中資料量測試 (1MB)");
    test_fma_with_size(SIZE_1MB / sizeof(float), 100);

    print_subtest_header("大資料量測試 (10MB)");
    test_fma_with_size(SIZE_10MB / sizeof(float), 10);

    // 總結
    printf("\n");
    printf(COLOR_CYAN "════════════════════════════════════════\n");
    printf("  測試完成！\n");
    printf("════════════════════════════════════════\n" COLOR_RESET);

    printf("\n" COLOR_BOLD "預期結果:\n" COLOR_RESET);
    printf("  - FMA 比分開計算快 1.3-1.5x\n");
    printf("  - FMA 比純 C 快 2-3x\n");
    printf("  - 在深度學習等應用中優勢明顯\n\n");

    return 0;
}
