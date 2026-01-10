// ============================================================================
// 時間工具函式庫 (Time Utilities)
// ============================================================================
// 設計目標：
// 1. 高精度時間戳：使用奈秒(nanosecond)作為基礎單位
// 2. 低延遲取樣：使用 std::chrono 系統時鐘
// 3. 型別安全：使用 typedef 明確表示時間單位

#pragma once

#include <chrono>
#include <ctime>

namespace Common
{
// ============================================================================
// 時間單位定義
// ============================================================================
// ⚡ 使用 int64_t 作為奈秒時間戳
// - 範圍：±292 年（從 1970-01-01 00:00:00 UTC）
// - 精度：1 奈秒 (1e-9 秒)
typedef int64_t Nanos;

// 時間單位轉換常數
constexpr Nanos NANO_TO_MICROS = 1000;                                     // 奈秒 → 微秒
constexpr Nanos MICROS_TO_MILLIS = 1000;                                   // 微秒 → 毫秒
constexpr Nanos MILLIS_TO_SECS = 1000;                                     // 毫秒 → 秒
constexpr Nanos NANOS_TO_MILLIS = NANO_TO_MICROS * MICROS_TO_MILLIS;     // 奈秒 → 毫秒 (1e6)
constexpr Nanos NANOS_TO_SECS = NANOS_TO_MILLIS * MILLIS_TO_SECS;        // 奈秒 → 秒 (1e9)

// ============================================================================
// getCurrentNanos() - 取得當前奈秒時間戳
// ============================================================================
// 返回值：自 Unix Epoch (1970-01-01 00:00:00 UTC) 以來的奈秒數
//
// 實作：
// - 使用 std::chrono::system_clock::now()
// - 轉換為奈秒精度
//
// 📊 效能特性：
// - 延遲：~20-30 ns（視平台而定）
// - 系統呼叫：現代 Linux 使用 vDSO，無需真正的系統呼叫
//
// 使用場景：
// - 訂單時間戳
// - 延遲測量
// - 日誌時間記錄
//
// 📌 注意事項：
// - system_clock 可能受 NTP 調整影響（時間可能回撥）
// - 若需單調遞增時間，應使用 steady_clock
inline auto getCurrentNanos() noexcept
{
    return std::chrono::duration_cast<std::chrono::nanoseconds>
           (std::chrono::system_clock::now().time_since_epoch()).count();
}

// ============================================================================
// getCurrentTimeStr() - 取得當前時間的字串表示
// ============================================================================
// 參數：
// - time_str: 輸出字串的指標
//
// 返回值：time_str 的參考（方便鏈式呼叫）
//
// 格式：
// - "Day Mon DD HH:MM:SS YYYY\0"
// - 例如："Fri Jan 10 23:15:30 2026"
//
// 實作細節：
// - 使用 std::chrono::system_clock::to_time_t() 轉換為 time_t
// - 使用 ctime() 轉換為可讀字串
// - 移除末尾的換行符號 '\n'
//
// ⚠️ 效能警告：
// - ctime() 不是執行緒安全（使用靜態緩衝區）
// - 格式化字串操作相對昂貴（~1-5 μs）
// - 不應在熱路徑（Hot Path）中使用
//
// 使用場景：
// - 日誌檔案時間戳
// - 除錯輸出
// - 人類可讀的時間顯示
inline auto& getCurrentTimeStr(std::string* time_str)
{
    const auto time = std::chrono::system_clock::to_time_t(
                          std::chrono::system_clock::now());
    time_str->assign(ctime(&time));

    // 移除 ctime() 產生的末尾換行符號
    if (!time_str->empty()) {
        time_str->at(time_str->length() - 1) = '\0';
    }

    return *time_str;
}
}
