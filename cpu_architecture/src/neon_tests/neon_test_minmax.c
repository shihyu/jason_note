/**
 * neon_test_minmax.c - NEON 最大/最小值測試
 *
 * 測試 NEON 最大/最小值指令的效能
 * 應用場景：
 *   - 陣列最大值/最小值搜尋
 *   - Clamp 運算（限制數值範圍）
 *   - Pooling 運算（神經網路）
 *
 * 指令：
 *   - vmaxq_f32: 元素最大值
 *   - vminq_f32: 元素最小值
 *   - vmaxvq_f32: 水平最大值（ARMv8）
 *   - vminvq_f32: 水平最小值（ARMv8）
 */

#include "common.h"

/**
 * 純 C 實作：尋找陣列最大值
 */
float find_max_c(const float *data, size_t n) {
    float max_val = data[0];
    for (size_t i = 1; i < n; i++) {
        if (data[i] > max_val) {
            max_val = data[i];
        }
    }
    return max_val;
}

/**
 * NEON 實作：尋找陣列最大值
 */
float find_max_neon(const float *data, size_t n) {
    if (n == 0) return 0.0f;

    size_t i = 0;
    size_t vec_size = n / 4;

    // 初始化最大值向量
    float32x4_t vmax = vld1q_f32(data);

    // 處理 4 個元素一組
    for (i = 1; i < vec_size; i++) {
        float32x4_t vdata = vld1q_f32(data + i * 4);
        vmax = vmaxq_f32(vmax, vdata);  // 元素級最大值
    }

    // 水平歸約：找出 4 個元素中的最大值
    float max_val = vmaxvq_f32(vmax);  // ARMv8 指令

    // 處理剩餘元素
    for (i = vec_size * 4; i < n; i++) {
        if (data[i] > max_val) {
            max_val = data[i];
        }
    }

    return max_val;
}

/**
 * 純 C 實作：尋找陣列最小值
 */
float find_min_c(const float *data, size_t n) {
    float min_val = data[0];
    for (size_t i = 1; i < n; i++) {
        if (data[i] < min_val) {
            min_val = data[i];
        }
    }
    return min_val;
}

/**
 * NEON 實作：尋找陣列最小值
 */
float find_min_neon(const float *data, size_t n) {
    if (n == 0) return 0.0f;

    size_t i = 0;
    size_t vec_size = n / 4;

    float32x4_t vmin = vld1q_f32(data);

    for (i = 1; i < vec_size; i++) {
        float32x4_t vdata = vld1q_f32(data + i * 4);
        vmin = vminq_f32(vmin, vdata);
    }

    float min_val = vminvq_f32(vmin);

    for (i = vec_size * 4; i < n; i++) {
        if (data[i] < min_val) {
            min_val = data[i];
        }
    }

    return min_val;
}

/**
 * 純 C 實作：Clamp（限制數值範圍）
 */
void clamp_c(const float *input, float *output, size_t n, float min_val, float max_val) {
    for (size_t i = 0; i < n; i++) {
        float val = input[i];
        if (val < min_val) val = min_val;
        if (val > max_val) val = max_val;
        output[i] = val;
    }
}

/**
 * NEON 實作：Clamp
 */
void clamp_neon(const float *input, float *output, size_t n, float min_val, float max_val) {
    size_t i = 0;
    size_t vec_size = n / 4;

    float32x4_t vmin = vdupq_n_f32(min_val);
    float32x4_t vmax = vdupq_n_f32(max_val);

    for (i = 0; i < vec_size; i++) {
        float32x4_t vdata = vld1q_f32(input + i * 4);

        // 限制範圍：max(min_val, min(max_val, data))
        vdata = vmaxq_f32(vdata, vmin);  // data = max(data, min_val)
        vdata = vminq_f32(vdata, vmax);  // data = min(data, max_val)

        vst1q_f32(output + i * 4, vdata);
    }

    // 處理剩餘元素
    for (i = vec_size * 4; i < n; i++) {
        float val = input[i];
        if (val < min_val) val = min_val;
        if (val > max_val) val = max_val;
        output[i] = val;
    }
}

/**
 * 測試最大值搜尋
 */
void test_find_max(size_t num_elements, int iterations) {
    char size_str[64];
    format_size(num_elements * sizeof(float), size_str, sizeof(size_str));

    printf("\n  測試資料大小: %zu 個 float (%s)\n", num_elements, size_str);
    printf("  ─────────────────────────────────────\n");

    float *data = (float *)memalign(16, num_elements * sizeof(float));
    if (!data) {
        print_error("記憶體分配失敗");
        return;
    }

    generate_random_float_array(data, num_elements, -1000.0f, 1000.0f);

    // 測試純 C
    Timer timer;
    float max_c = 0.0f;
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        max_c = find_max_c(data, num_elements);
    }
    timer_stop(&timer);
    double time_c = timer_get_ms(&timer);

    // 測試 NEON
    float max_neon = 0.0f;
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        max_neon = find_max_neon(data, num_elements);
    }
    timer_stop(&timer);
    double time_neon = timer_get_ms(&timer);

    // 驗證
    if (fabsf(max_c - max_neon) < EPSILON) {
        print_success("最大值搜尋正確性驗證通過");
        printf("  找到的最大值: %.2f\n", max_c);
    } else {
        print_error("最大值搜尋正確性驗證失敗");
        printf("  C: %.2f, NEON: %.2f\n", max_c, max_neon);
    }

    print_performance_comparison("最大值搜尋", time_c, time_neon);

    free(data);
}

/**
 * 測試 Clamp 運算
 */
void test_clamp(size_t num_elements, int iterations) {
    char size_str[64];
    format_size(num_elements * sizeof(float), size_str, sizeof(size_str));

    printf("\n  測試資料大小: %zu 個 float (%s)\n", num_elements, size_str);
    printf("  ─────────────────────────────────────\n");

    float *input = (float *)memalign(16, num_elements * sizeof(float));
    float *output_c = (float *)memalign(16, num_elements * sizeof(float));
    float *output_neon = (float *)memalign(16, num_elements * sizeof(float));

    if (!input || !output_c || !output_neon) {
        print_error("記憶體分配失敗");
        return;
    }

    generate_random_float_array(input, num_elements, -100.0f, 100.0f);
    float min_val = -50.0f, max_val = 50.0f;

    // 測試純 C
    Timer timer;
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        clamp_c(input, output_c, num_elements, min_val, max_val);
    }
    timer_stop(&timer);
    double time_c = timer_get_ms(&timer);

    // 測試 NEON
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        clamp_neon(input, output_neon, num_elements, min_val, max_val);
    }
    timer_stop(&timer);
    double time_neon = timer_get_ms(&timer);

    // 驗證
    int passed = float_array_equal(output_c, output_neon, num_elements, EPSILON);
    if (passed) {
        print_success("Clamp 運算正確性驗證通過");
    } else {
        print_error("Clamp 運算正確性驗證失敗");
    }

    print_performance_comparison("Clamp 運算", time_c, time_neon);

    free(input);
    free(output_c);
    free(output_neon);
}

int main(void) {
    print_test_header("NEON 最大/最小值測試");

    printf("\n  測試說明:\n");
    printf("  - 測試 vmaxq, vminq, vmaxvq, vminvq 指令\n");
    printf("  - 應用：陣列搜尋、Clamp 運算\n");
    printf("  - 水平歸約可快速找出全域最大/最小值\n");

    srand(time(NULL));

    print_subtest_header("最大值搜尋測試");
    test_find_max(SIZE_1MB / sizeof(float), 100);
    test_find_max(SIZE_10MB / sizeof(float), 10);

    print_subtest_header("Clamp 運算測試");
    printf("  範圍限制: [-50.0, 50.0]\n");
    test_clamp(SIZE_1MB / sizeof(float), 100);
    test_clamp(SIZE_10MB / sizeof(float), 10);

    printf("\n");
    printf(COLOR_CYAN "════════════════════════════════════════\n");
    printf("  測試完成！\n");
    printf("════════════════════════════════════════\n" COLOR_RESET);

    printf("\n" COLOR_BOLD "預期結果:\n" COLOR_RESET);
    printf("  - 最大值搜尋: NEON 加速 4-6x\n");
    printf("  - Clamp 運算: NEON 加速 3-4x\n");
    printf("  - 水平歸約指令效能優異\n\n");

    return 0;
}
