/**
 * neon_test_compare.c - NEON 向量比較測試
 *
 * 測試 NEON 比較指令的效能
 * 應用場景：圖像閾值處理、條件篩選、遮罩產生
 *
 * 比較指令：
 *   - vcgtq_f32: Greater Than (>)
 *   - vcltq_f32: Less Than (<)
 *   - vceqq_f32: Equal (==)
 *   - vcgeq_f32: Greater or Equal (>=)
 *   - vcleq_f32: Less or Equal (<=)
 */

#include "common.h"

/**
 * 純 C 實作：閾值處理（大於閾值設為 255，否則設為 0）
 */
void threshold_c(const float *input, uint8_t *output, size_t n, float threshold) {
    for (size_t i = 0; i < n; i++) {
        output[i] = (input[i] > threshold) ? 255 : 0;
    }
}

/**
 * NEON 實作：閾值處理
 *
 * 使用 vcgtq_f32 比較，結果為 0xFFFFFFFF (true) 或 0x00000000 (false)
 */
void threshold_neon(const float *input, uint8_t *output, size_t n, float threshold) {
    size_t i = 0;
    size_t vec_size = n / 4;

    // 建立閾值向量
    float32x4_t vthreshold = vdupq_n_f32(threshold);
    uint8x8_t true_val = vdup_n_u8(255);
    uint8x8_t false_val = vdup_n_u8(0);

    for (i = 0; i < vec_size; i++) {
        // 載入 4 個 float
        float32x4_t vinput = vld1q_f32(input + i * 4);

        // 比較：input > threshold
        // 結果：0xFFFFFFFF (true) 或 0x00000000 (false)
        uint32x4_t vcmp = vcgtq_f32(vinput, vthreshold);

        // 轉換為 uint8: 取每個 32-bit 的最低 byte
        uint16x4_t vcmp16 = vmovn_u32(vcmp);  // 32 -> 16
        uint8x8_t vcmp8 = vmovn_u16(vcombine_u16(vcmp16, vcmp16));  // 16 -> 8

        // 根據比較結果選擇 255 或 0
        uint8x8_t vresult = vbsl_u8(vcmp8, true_val, false_val);

        // 只儲存前 4 個 bytes
        vst1_lane_u32((uint32_t *)(output + i * 4), vreinterpret_u32_u8(vresult), 0);
    }

    // 處理剩餘元素
    for (i = vec_size * 4; i < n; i++) {
        output[i] = (input[i] > threshold) ? 255 : 0;
    }
}

/**
 * 純 C 實作：範圍檢查（min <= value <= max）
 */
void range_check_c(const float *input, uint8_t *output, size_t n, float min, float max) {
    for (size_t i = 0; i < n; i++) {
        output[i] = (input[i] >= min && input[i] <= max) ? 255 : 0;
    }
}

/**
 * NEON 實作：範圍檢查
 *
 * 使用 vcgeq_f32 和 vcleq_f32 組合
 */
void range_check_neon(const float *input, uint8_t *output, size_t n, float min, float max) {
    size_t i = 0;
    size_t vec_size = n / 4;

    float32x4_t vmin = vdupq_n_f32(min);
    float32x4_t vmax = vdupq_n_f32(max);
    uint8x8_t true_val = vdup_n_u8(255);
    uint8x8_t false_val = vdup_n_u8(0);

    for (i = 0; i < vec_size; i++) {
        float32x4_t vinput = vld1q_f32(input + i * 4);

        // input >= min
        uint32x4_t vcmp_ge = vcgeq_f32(vinput, vmin);
        // input <= max
        uint32x4_t vcmp_le = vcleq_f32(vinput, vmax);

        // 邏輯 AND：兩個條件都成立
        uint32x4_t vcmp = vandq_u32(vcmp_ge, vcmp_le);

        // 轉換為 uint8
        uint16x4_t vcmp16 = vmovn_u32(vcmp);
        uint8x8_t vcmp8 = vmovn_u16(vcombine_u16(vcmp16, vcmp16));

        uint8x8_t vresult = vbsl_u8(vcmp8, true_val, false_val);
        vst1_lane_u32((uint32_t *)(output + i * 4), vreinterpret_u32_u8(vresult), 0);
    }

    // 處理剩餘元素
    for (i = vec_size * 4; i < n; i++) {
        output[i] = (input[i] >= min && input[i] <= max) ? 255 : 0;
    }
}

/**
 * 測試閾值處理
 */
void test_threshold(size_t num_elements, int iterations) {
    char size_str[64];
    format_size(num_elements * sizeof(float), size_str, sizeof(size_str));

    printf("\n  測試資料大小: %zu 個 float (%s)\n", num_elements, size_str);
    printf("  ─────────────────────────────────────\n");

    float *input = (float *)memalign(16, num_elements * sizeof(float));
    uint8_t *output_c = (uint8_t *)memalign(16, num_elements);
    uint8_t *output_neon = (uint8_t *)memalign(16, num_elements);

    if (!input || !output_c || !output_neon) {
        print_error("記憶體分配失敗");
        return;
    }

    generate_random_float_array(input, num_elements, 0.0f, 255.0f);
    float threshold = 128.0f;

    // 測試純 C
    Timer timer;
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        threshold_c(input, output_c, num_elements, threshold);
    }
    timer_stop(&timer);
    double time_c = timer_get_ms(&timer);

    // 測試 NEON
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        threshold_neon(input, output_neon, num_elements, threshold);
    }
    timer_stop(&timer);
    double time_neon = timer_get_ms(&timer);

    // 驗證
    int passed = uint8_array_equal(output_c, output_neon, num_elements);
    if (passed) {
        print_success("閾值處理正確性驗證通過");
    } else {
        print_error("閾值處理正確性驗證失敗");
    }

    print_performance_comparison("閾值處理", time_c, time_neon);

    free(input);
    free(output_c);
    free(output_neon);
}

/**
 * 測試範圍檢查
 */
void test_range_check(size_t num_elements, int iterations) {
    char size_str[64];
    format_size(num_elements * sizeof(float), size_str, sizeof(size_str));

    printf("\n  測試資料大小: %zu 個 float (%s)\n", num_elements, size_str);
    printf("  ─────────────────────────────────────\n");

    float *input = (float *)memalign(16, num_elements * sizeof(float));
    uint8_t *output_c = (uint8_t *)memalign(16, num_elements);
    uint8_t *output_neon = (uint8_t *)memalign(16, num_elements);

    if (!input || !output_c || !output_neon) {
        print_error("記憶體分配失敗");
        return;
    }

    generate_random_float_array(input, num_elements, 0.0f, 255.0f);
    float min = 50.0f, max = 200.0f;

    // 測試純 C
    Timer timer;
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        range_check_c(input, output_c, num_elements, min, max);
    }
    timer_stop(&timer);
    double time_c = timer_get_ms(&timer);

    // 測試 NEON
    timer_start(&timer);
    for (int i = 0; i < iterations; i++) {
        range_check_neon(input, output_neon, num_elements, min, max);
    }
    timer_stop(&timer);
    double time_neon = timer_get_ms(&timer);

    // 驗證
    int passed = uint8_array_equal(output_c, output_neon, num_elements);
    if (passed) {
        print_success("範圍檢查正確性驗證通過");
    } else {
        print_error("範圍檢查正確性驗證失敗");
    }

    print_performance_comparison("範圍檢查", time_c, time_neon);

    free(input);
    free(output_c);
    free(output_neon);
}

int main(void) {
    print_test_header("NEON 向量比較測試");

    printf("\n  測試說明:\n");
    printf("  - 測試 vcgtq, vcgeq, vcleq 等比較指令\n");
    printf("  - 應用：圖像閾值處理、條件篩選\n");
    printf("  - 比較結果為全 1 或全 0 的遮罩\n");

    srand(time(NULL));

    print_subtest_header("閾值處理測試 (Thresholding)");
    printf("  閾值 = 128.0, 大於閾值輸出 255，否則輸出 0\n");
    test_threshold(SIZE_1MB / sizeof(float), 100);
    test_threshold(SIZE_10MB / sizeof(float), 10);

    print_subtest_header("範圍檢查測試 (Range Check)");
    printf("  範圍 = [50.0, 200.0], 在範圍內輸出 255，否則輸出 0\n");
    test_range_check(SIZE_1MB / sizeof(float), 100);
    test_range_check(SIZE_10MB / sizeof(float), 10);

    printf("\n");
    printf(COLOR_CYAN "════════════════════════════════════════\n");
    printf("  測試完成！\n");
    printf("════════════════════════════════════════\n" COLOR_RESET);

    printf("\n" COLOR_BOLD "預期結果:\n" COLOR_RESET);
    printf("  - NEON 比較指令加速 3-4x\n");
    printf("  - 應用於圖像處理效果顯著\n\n");

    return 0;
}
