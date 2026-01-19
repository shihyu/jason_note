// 分支預測/斷言巨集：熱路徑微優化。
// ⚡ 效能關鍵：LIKELY/UNLIKELY 降低誤判成本。
// ⚠️ 注意：NDEBUG 行為差異。

// ============================================================================
// 低延遲編程核心巨集 (Low-Latency Core Macros)
// ============================================================================

#pragma once

#include <cstring>
#include <iostream>

// ============================================================================
// LIKELY/UNLIKELY: 分支預測提示巨集
// ============================================================================
// 原理：
// - 使用 GCC/Clang 內建函式 __builtin_expect() 提示編譯器分支機率
// - 編譯器會將「可能」執行的程式碼放在主執行路徑（減少跳轉）
// - 將「不可能」執行的程式碼放在冷路徑（Cold Path）
//
// 使用場景：
// - LIKELY：正常流程（例如：訂單驗證通過、網路連線成功）
// - UNLIKELY：異常處理（例如：錯誤檢查、邊界條件、assert 失敗）
//
// 📊 效能影響：
// - CPU 分支預測正確：0 個 cycle（流水線不中斷）
// - CPU 分支預測錯誤：10-20 個 cycle（需清空流水線）
// - 使用提示可將預測準確率從 ~50% 提升到 ~95%
//
// 範例：
// if (LIKELY(order.qty > 0)) { /* 主流程 */ }
// if (UNLIKELY(order.qty <= 0)) { /* 錯誤處理 */ }
#define LIKELY(x) __builtin_expect(!!(x), 1)
#define UNLIKELY(x) __builtin_expect(!!(x), 0)

// ============================================================================
// ASSERT: 執行期斷言檢查
// ============================================================================
// 與標準 assert() 的差異：
// - assert()：僅在 Debug 模式啟用（定義 NDEBUG 會停用）
// - ASSERT()：永遠啟用（即使 Release 也檢查）
//
// 使用時機：
// - 關鍵不變量（Invariant）檢查（例如：指標非空、索引範圍）
// - 絕對不能違反的前置條件（Precondition）
//
// ⚠️ 效能考量：
// - 使用 UNLIKELY 優化：假設斷言檢查通常為真
// - 若斷言失敗，程式立即終止（exit(EXIT_FAILURE)）
// - 不應在熱路徑（Hot Path）中使用複雜的斷言檢查
//
// 範例：
// ASSERT(ptr != nullptr, "Null pointer detected");
// ASSERT(index < size, "Index out of bounds");
inline auto ASSERT(bool cond, const std::string& msg) noexcept
{
    // ⚡ 分支預測提示：降低誤判成本。
    if (UNLIKELY(!cond)) {
        std::cerr << "ASSERT : " << msg << std::endl;

        exit(EXIT_FAILURE);
    }
}

// ============================================================================
// FATAL: 致命錯誤處理
// ============================================================================
// 用途：
// - 遇到無法恢復的錯誤時立即終止程式
// - 記錄錯誤訊息到 stderr
//
// 使用場景：
// - 記憶體分配失敗
// - 配置檔案讀取失敗
// - 網路初始化失敗
//
// 範例：
// if (!config.load()) {
//     FATAL("Failed to load configuration file");
// }
inline auto FATAL(const std::string& msg) noexcept
{
    std::cerr << "FATAL : " << msg << std::endl;

    exit(EXIT_FAILURE);
}
