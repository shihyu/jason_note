#pragma once

#include <string>
#include <chrono>
#include <ctime>

namespace Common
{
typedef int64_t Nanos; // 奈秒 (Nanoseconds)

constexpr Nanos NANOS_TO_MICROS = 1000;
constexpr Nanos MICROS_TO_MILLIS = 1000;
constexpr Nanos MILLIS_TO_SECS = 1000;
constexpr Nanos NANOS_TO_MILLIS = NANOS_TO_MICROS * MICROS_TO_MILLIS;
constexpr Nanos NANOS_TO_SECS = NANOS_TO_MILLIS * MILLIS_TO_SECS;

// 取得當前時間 (奈秒)
// 使用系統時鐘 (System Clock)
inline auto getCurrentNanos() noexcept
{
    return std::chrono::duration_cast<std::chrono::nanoseconds>
           (std::chrono::system_clock::now().time_since_epoch()).count();
}

// 取得當前時間字串
// 格式：Thu Jan  1 00:00:00 1970 (移除換行符號)
inline auto& getCurrentTimeStr(std::string* time_str)
{
    const auto time = std::chrono::system_clock::to_time_t(
                          std::chrono::system_clock::now());
    time_str->assign(ctime(&time));

    if (!time_str->empty()) {
        time_str->at(time_str->length() - 1) = '\0';
    }

    return *time_str;
}
}
