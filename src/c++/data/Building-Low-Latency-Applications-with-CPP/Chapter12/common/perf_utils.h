#pragma once

#include <cstdint>
#include "common/perf_utils.h"

#include "time_utils.h"

// 效能量測工具：使用 RDTSC 降低量測開銷。
// ⚡ 效能關鍵：最小化序列化與記錄成本。
// ⚠️ 注意：跨核心 TSC 同步與頻率變化。

namespace Common
{
/// Read from the TSC register and return a uint64_t value to represent elapsed CPU clock cycles.
inline auto rdtsc() noexcept
{
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t) hi << 32) | lo;
}
}

/// Start latency measurement using rdtsc(). Creates a variable called TAG in the local scope.
#define START_MEASURE(TAG) const auto TAG = Common::rdtsc()

/// End latency measurement using rdtsc(). Expects a variable called TAG to already exist in the local scope.
#define END_MEASURE(TAG, LOGGER)                                                              \
      do {                                                                                    \
        const auto end = Common::rdtsc();                                                     \
        LOGGER.log("% RDTSC "#TAG" %\n", Common::getCurrentTimeStr(&time_str_), (end - TAG)); \
      } while(false)

/// Log a current timestamp at the time this macro is invoked.
#define TTT_MEASURE(TAG, LOGGER)                                                              \
      do {                                                                                    \
        const auto TAG = Common::getCurrentNanos();                                           \
        LOGGER.log("% TTT "#TAG" %\n", Common::getCurrentTimeStr(&time_str_), TAG);           \
      } while(false)
