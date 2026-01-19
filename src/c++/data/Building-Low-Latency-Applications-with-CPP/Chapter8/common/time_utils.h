#pragma once

// 時間工具：奈秒級時間戳，避免高開銷 API。
// ⚡ 效能關鍵：VDSO/clock_gettime 走捷徑。
// ⚠️ 注意：時鐘來源一致性。

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
//
// ⚠️ 時鐘選擇：使用 system_clock 而非 steady_clock
// - system_clock：反映真實世界時間 (Wall-clock time)
//   ✅ 優點：可與外部時間戳記比對 (如交易所發送的訂單時間)
//   ❌ 缺點：會受 NTP 時間同步影響 (可能向後跳躍或速率調整)
//
// - steady_clock：單調遞增時鐘 (Monotonic Clock)
//   ✅ 優點：不受 NTP 影響，適合測量延遲 (Latency Measurement)
//   ❌ 缺點：無法與外部時間對應，不適合業務邏輯時間戳記
//
// 🔧 建議使用場景：
// - 延遲測量 (Latency Measurement)：使用 steady_clock
//   ```cpp
//   auto start = std::chrono::steady_clock::now();
//   // ... 執行操作 ...
//   auto end = std::chrono::steady_clock::now();
//   auto latency = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
//   ```
//
// - 業務時間戳記 (Business Timestamp)：使用 system_clock (本函式)
//   ```cpp
//   auto order_time = getCurrentNanos();  // 用於比對交易所時間
//   ```
//
// ⚠️ NTP 時間同步影響：
// - NTP 調整方式：
//   1. Step 模式：時間直接跳躍 (誤差 > 128ms 時)
//      - 可能導致時間倒退 (Backward Jump)
//      - 範例：13:00:05 -> 13:00:03 (倒退 2 秒)
//   2. Slew 模式：漸進式調整時鐘速率 (誤差 < 128ms 時)
//      - 時鐘走快或走慢，但不會倒退
//      - 調整速率約 0.5ms/s (需時較長)
//
// - 高頻交易風險：
//   - 時間倒退可能導致序列號錯亂
//   - 時間速率變化影響延遲統計準確性
//
// - 緩解措施：
//   1. 配置 NTP 使用 Slew 模式：
//      - 編輯 /etc/ntp.conf：`tinker panic 0`
//   2. 使用 PTP (Precision Time Protocol) 替代 NTP：
//      - 精度：< 1 μs (vs NTP 的 1-10ms)
//      - 需要硬體支援 (網卡須支援 PTP)
//   3. 定期檢查時間跳躍：
//      ```cpp
//      static auto last_time = getCurrentNanos();
//      auto current_time = getCurrentNanos();
//      if (current_time < last_time) {
//          logger.log("WARNING: Time jumped backward by % ns\n", last_time - current_time);
//      }
//      last_time = current_time;
//      ```
//
// 🔧 高精度時間戳記替代方案：
// 1. RDTSC (Read Time-Stamp Counter)：
//    - 延遲：< 50 ns (vs system_clock 的 100-200ns)
//    - 精度：CPU 時鐘週期級別 (例如 3 GHz CPU = 0.33ns)
//    - 實作範例：
//      ```cpp
//      inline uint64_t rdtsc() {
    // ⚡ 關鍵路徑：函式內避免鎖/分配，保持快取局部性。
//          unsigned int lo, hi;
//          __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
//          return ((uint64_t)hi << 32) | lo;
//      }
//      ```
//    - ⚠️ 注意事項：
//      - 需要校準轉換為實際時間 (ticks to nanoseconds)
//      - 須停用 CPU 頻率縮放 (固定在最高頻率)
//      - 不同 CPU 核心的 TSC 可能不同步 (需 constant_tsc 特性)
//
// 2. PTP (Precision Time Protocol / IEEE 1588)：
//    - 精度：< 1 μs (vs NTP 的 1-10ms)
//    - 需要硬體支援：網卡、交換機
//    - 使用 linuxptp 工具：
//      ```bash
//      sudo ptp4l -i eth0 -m  # 啟動 PTP daemon
//      sudo phc2sys -s eth0 -m  # 同步系統時鐘與 PTP 硬體時鐘
//      ```
//
// 📊 精度與延遲分析：
// - system_clock (clock_gettime(CLOCK_REALTIME))：
//   - 呼叫延遲：100-200 ns (取決於內核配置)
//   - 精度：1-10 μs (受 NTP 影響)
//   - 穩定性：受 NTP 調整影響
//
// - steady_clock (clock_gettime(CLOCK_MONOTONIC))：
//   - 呼叫延遲：100-200 ns
//   - 精度：1 ns (理論值)
//   - 穩定性：高（不受 NTP 影響）
//
// - RDTSC：
//   - 呼叫延遲：< 50 ns
//   - 精度：< 1 ns (CPU 時鐘週期)
//   - 穩定性：高（需固定 CPU 頻率）
//
// - PTP：
//   - 同步精度：< 1 μs
//   - 需要硬體支援
//
// 🔧 生產環境建議：
// - 延遲測量：使用 RDTSC 或 steady_clock
// - 業務時間戳記：使用 system_clock + PTP 同步
// - 監控時間跳躍：定期檢查時間連續性
// - 固定 CPU 頻率：停用 Turbo Boost 與省電模式
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
