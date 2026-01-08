#pragma once

namespace Common
{
// rdtsc: 讀取時鐘週期暫存器 (Read Time-Stamp Counter)
// 
// ⚡ 效能關鍵: 這是目前最精確且開銷最低的計時方式
// 1. 直接讀取 CPU 內部的 64 位元計數器
// 2. 開銷僅需約 10-15 個時鐘週期
// 3. 適用於量測奈秒級的程式碼執行區塊
inline auto rdtsc() noexcept
{
    unsigned int lo, hi;
    // 透過彙編指令直接存取
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t) hi << 32) | lo;
}
}

// START_MEASURE: 開始延遲量測
// 在區域作用域中建立一個 TAG 變數，記錄當前的 RDTSC 值
#define START_MEASURE(TAG) const auto TAG = Common::rdtsc()

// END_MEASURE: 結束延遲量測並記錄
// 計算當前值與 TAG 值的差值 (即消耗的時鐘週期數)，並透過日誌輸出
// 📊 TAG 名稱會被轉化為字串標籤
#define END_MEASURE(TAG, LOGGER)                                                              \
      do {                                                                                    \
        const auto end = Common::rdtsc();                                                     \
        LOGGER.log("% RDTSC "#TAG" %\n", Common::getCurrentTimeStr(&time_str_), (end - TAG)); \
      } while(false)

// TTT_MEASURE: 記錄絕對時間點 (Tick-to-Trade Trace)
// 記錄當前的絕對納秒時間戳，用於追蹤封包流轉生命週期
#define TTT_MEASURE(TAG, LOGGER)                                                              \
      do {                                                                                    \
        const auto TAG = Common::getCurrentNanos();                                           \
        LOGGER.log("% TTT "#TAG" %\n", Common::getCurrentTimeStr(&time_str_), TAG);           \
      } while(false)
