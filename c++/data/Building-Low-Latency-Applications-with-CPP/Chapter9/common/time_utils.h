#pragma once

#include <string>
#include <chrono>
#include <ctime>

namespace Common
{
// ========================================
// 時間工具函式庫 (Time Utilities)
// ========================================
//
// 設計目標:
// 1. 高精度時間戳: 使用奈秒(nanosecond)作為基礎單位
// 2. 低延遲取樣: 避免系統呼叫開銷
// 3. 型別安全: 使用 typedef 明確表示時間單位
//
// 使用場景:
// - 延遲測量: 計算訊息處理時間
// - 時間戳記: 為日誌和事件打上時間標記
// - 效能剖析: 測量關鍵路徑的執行時間

// Nanos: 奈秒時間戳類型
// ⚡ 範圍: int64_t 可表示約 292 年的奈秒時間
// 使用 int64_t 而非 uint64_t 的原因:
// - 支援時間差計算 (可能為負值)
// - std::chrono 系統預設使用有符號整數
typedef int64_t Nanos;

// 時間單位轉換常數
// 範例: latency_micros = latency_nanos / NANOS_TO_MICROS
constexpr Nanos NANOS_TO_MICROS = 1000;          // 1 微秒 = 1000 奈秒
constexpr Nanos MICROS_TO_MILLIS = 1000;         // 1 毫秒 = 1000 微秒
constexpr Nanos MILLIS_TO_SECS = 1000;           // 1 秒 = 1000 毫秒
constexpr Nanos NANOS_TO_MILLIS = NANOS_TO_MICROS * MICROS_TO_MILLIS;  // 1,000,000
constexpr Nanos NANOS_TO_SECS = NANOS_TO_MILLIS * MILLIS_TO_SECS;      // 1,000,000,000

// getCurrentNanos: 取得當前系統時間 (奈秒精度)
//
// 時鐘來源: std::chrono::system_clock
// - 優點: 跨平台一致性,對應 UNIX 時間戳
// - 缺點: 受 NTP 時間同步影響,可能不單調遞增
//
// ⚠️ 時鐘選擇權衡:
// - system_clock: 可與外部系統時間比對,但可能跳變
// - steady_clock: 單調遞增保證,但無法轉換為掛鐘時間
//
// 效能: 約 20-30ns (取決於 CPU 和 TSC 頻率)
// 底層實作: Linux 上通常使用 VDSO clock_gettime(CLOCK_REALTIME)
//
// 使用範例:
//   Nanos start = getCurrentNanos();
//   process_order();
//   Nanos latency = getCurrentNanos() - start;
inline auto getCurrentNanos() noexcept
{
    return std::chrono::duration_cast<std::chrono::nanoseconds>
           (std::chrono::system_clock::now().time_since_epoch()).count();
}

// getCurrentTimeStr: 取得當前時間的可讀字串
// @param time_str: 輸出參數,接收格式化後的時間字串
// @return: time_str 的引用 (支援鏈式呼叫)
//
// 輸出格式: "Fri Jan 10 12:34:56 2026" (ctime 格式)
//
// ⚠️ 效能考量:
// - 涉及格式化操作,延遲約 1-5 微秒
// - 僅適用於日誌/除錯,不應在關鍵路徑使用
//
// 使用範例:
//   std::string time_str;
//   logger.log("Current time: %\n", getCurrentTimeStr(&time_str));
inline auto& getCurrentTimeStr(std::string* time_str)
{
    const auto time = std::chrono::system_clock::to_time_t(
                          std::chrono::system_clock::now());
    time_str->assign(ctime(&time));  // ctime 格式: "Fri Jan 10 12:34:56 2026\n"

    // 移除 ctime 添加的換行符
    if (!time_str->empty()) {
        time_str->at(time_str->length() - 1) = '\0';
    }

    return *time_str;
}
}
