#pragma once

#include <cstring>
#include <iostream>

// ========================================
// 低延遲編程核心巨集 (Low-Latency Core Macros)
// ========================================

// LIKELY/UNLIKELY: 分支預測提示巨集
//
// 原理:
// - 使用 GCC/Clang 內建函式 __builtin_expect() 提示編譯器
// - 編譯器會將"可能執行"的分支安排在"fall-through"位置
// - CPU 分支預測器會優先預測順序執行的分支
//
// 效能影響:
// - 正確提示: 減少 CPU 流水線刷新,節省 5-20 個 CPU 週期
// - 錯誤提示: 增加分支預測失敗率,反而降低效能
//
// 使用時機:
// ✅ 正確用法:
//    if (LIKELY(price > 0)) { /* 正常交易路徑 */ }
//    if (UNLIKELY(error)) { /* 錯誤處理 */ }
//
// ❌ 錯誤用法:
//    if (LIKELY(random_bool)) { /* 50/50 機率,不要使用 */ }
//
// ⚡ 效能案例:
// - 正常交易路徑 (99.99% 執行): 使用 LIKELY
// - 錯誤處理路徑 (0.01% 執行): 使用 UNLIKELY

// LIKELY: 提示編譯器條件"很可能為真"
// 範例: if (LIKELY(order != nullptr)) { process(order); }
#define LIKELY(x) __builtin_expect(!!(x), 1)

// UNLIKELY: 提示編譯器條件"很可能為假"
// 範例: if (UNLIKELY(fd < 0)) { handle_error(); }
#define UNLIKELY(x) __builtin_expect(!!(x), 0)

// ========================================
// 斷言與錯誤處理 (Assertions & Error Handling)
// ========================================

// ASSERT: 條件斷言,失敗時立即終止程式
// @param cond: 必須為真的條件
// @param msg: 斷言失敗時的錯誤訊息
//
// 使用場景:
// - 偵測程式邏輯錯誤 (如索引越界、空指標)
// - 驗證前置條件 (如檔案已開啟、連線已建立)
//
// ⚠️ 與標準 assert() 的差異:
// 1. 始終啟用: 不受 NDEBUG 巨集影響 (生產環境也會檢查)
// 2. noexcept: 保證不拋出例外 (直接呼叫 exit)
// 3. 自訂訊息: 可提供詳細的錯誤資訊
//
// 效能考量:
// - 正常路徑: 僅一次分支檢查 (配合 UNLIKELY 優化)
// - 失敗路徑: 程式終止,無需考慮效能
inline auto ASSERT(bool cond, const std::string& msg) noexcept
{
    if (UNLIKELY(!cond)) {  // 提示編譯器:斷言失敗是罕見事件
        std::cerr << "ASSERT : " << msg << std::endl;

        exit(EXIT_FAILURE);  // 立即終止程式
    }
}

// FATAL: 無條件終止程式並輸出錯誤訊息
// @param msg: 致命錯誤的描述
//
// 使用場景:
// - 不可恢復的錯誤 (如記憶體耗盡、關鍵資源初始化失敗)
// - switch-case 的 default 分支 (處理不應該發生的情況)
//
// 範例:
//   switch(msg_type) {
    // ⚡ 關鍵路徑：函式內避免鎖/分配，保持快取局部性。
//     case NEW_ORDER: ...
//     case CANCEL: ...
//     default: FATAL("Unknown message type");
//   }
inline auto FATAL(const std::string& msg) noexcept
{
    std::cerr << "FATAL : " << msg << std::endl;

    exit(EXIT_FAILURE);
}
