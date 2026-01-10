// release_benchmark.cpp: Memory Pool 基準測試
//
// 測試目標：
// - 比較原始 MemPool 與優化 OptMemPool 的效能差異
// - 量化移除斷言檢查對延遲的影響
//
// 測試方法：
// - 使用 RDTSC 指令量測 CPU 週期數（~0.3ns 精度）
// - 重複 100,000 次配置/釋放操作（256 個物件/批次）
// - 計算平均每次操作的 CPU 週期數
//
// 優化重點（OptMemPool vs MemPool）：
// 1. 移除 ASSERT 斷言檢查（減少分支預測失誤）
// 2. NDEBUG 條件編譯（完全移除除錯程式碼）
// 3. 保留核心邏輯（Free List 管理）
//
// 預期結果：
// - 原始版本：~50-80 cycles/op（含斷言檢查）
// - 優化版本：~30-50 cycles/op（移除斷言）
// - 加速比：約 1.3-1.6x

#include "common/mem_pool.h"
#include "common/opt_mem_pool.h"
#include "common/perf_utils.h"

#include "exchange/market_data/market_update.h"

// benchmarkMemPool: 記憶體池基準測試函式
//
// 測試流程：
// 1. 配置 256 個物件（批次配置）
// 2. 釋放 256 個物件（批次釋放）
// 3. 重複 100,000 次（模擬實際負載）
// 4. 計算平均每次操作的 CPU 週期數
//
// ⚡ 效能量測技巧：
// - 使用 RDTSC：直接讀取 CPU 時間戳計數器（Time Stamp Counter）
// - 批次測試：減少迴圈開銷對測試結果的影響
// - 預熱快取：第一輪迭代會預熱 CPU Cache
//
// ⚠️ 測量注意事項：
// - RDTSC 開銷：約 10-40 cycles（已包含在總時間中）
// - 編譯器優化：需使用 -O3 -DNDEBUG 編譯
// - CPU 頻率波動：關閉 Turbo Boost 可提高測試穩定性
//
// @param mem_pool: 記憶體池指標（支援泛型，可測試不同實作）
// @return 平均每次操作的 CPU 週期數
template<typename T>
size_t benchmarkMemPool(T* mem_pool)
{
    constexpr size_t loop_count = 100000;      // 迭代次數（10萬次）
    size_t total_rdtsc = 0;                    // 累計 CPU 週期數
    std::array<Exchange::MDPMarketUpdate*, 256> allocated_objs;  // 批次配置緩衝區（256 個物件）

    // 主測試迴圈：重複配置/釋放循環
    for (size_t i = 0; i < loop_count; ++i) {
        // 批次配置：連續配置 256 個物件
        // ⚡ 測試記憶體池的配置效能（Free List pop 操作）
        for (size_t j = 0; j < allocated_objs.size(); ++j) {
            const auto start = Common::rdtsc();              // 開始計時
            allocated_objs[j] = mem_pool->allocate();        // 配置物件（O(1)）
            total_rdtsc += (Common::rdtsc() - start);        // 累計 CPU 週期數
        }

        // 批次釋放：連續釋放 256 個物件
        // ⚡ 測試記憶體池的釋放效能（Free List push 操作）
        for (size_t j = 0; j < allocated_objs.size(); ++j) {
            const auto start = Common::rdtsc();              // 開始計時
            mem_pool->deallocate(allocated_objs[j]);         // 釋放物件（O(1)）
            total_rdtsc += (Common::rdtsc() - start);        // 累計 CPU 週期數
        }
    }

    // 計算平均每次操作的 CPU 週期數
    // 總操作次數 = loop_count × allocated_objs.size() × 2（配置 + 釋放）
    return (total_rdtsc / (loop_count * allocated_objs.size() * 2));
}

// main: 基準測試入口
//
// 測試對比：
// 1. 原始 MemPool（含 ASSERT 斷言檢查）
// 2. 優化 OptMemPool（移除斷言，NDEBUG 模式）
//
// 輸出範例：
// ORIGINAL MEMPOOL 65 CLOCK CYCLES PER OPERATION.
// OPTIMIZED MEMPOOL 42 CLOCK CYCLES PER OPERATION.
// 加速比：65/42 = 1.55x（約 35% 效能提升）
int main(int, char**)
{
    // 測試 1：原始 MemPool
    // 包含 ASSERT 斷言檢查（DEBUG 模式）
    {
        Common::MemPool<Exchange::MDPMarketUpdate> mem_pool(512);
        const auto cycles = benchmarkMemPool(&mem_pool);
        std::cout << "ORIGINAL MEMPOOL " << cycles << " CLOCK CYCLES PER OPERATION." <<
                  std::endl;
    }

    // 測試 2：優化 OptMemPool
    // 移除斷言檢查（NDEBUG 模式）
    // ⚡ 優化重點：
    // - 減少分支預測失誤（無 ASSERT 條件判斷）
    // - 減少函式呼叫開銷（無斷言處理函式）
    // - 更緊湊的指令序列（更好的 CPU 流水線利用）
    {
        OptCommon::OptMemPool<Exchange::MDPMarketUpdate> opt_mem_pool(512);
        const auto cycles = benchmarkMemPool(&opt_mem_pool);
        std::cout << "OPTIMIZED MEMPOOL " << cycles << " CLOCK CYCLES PER OPERATION." <<
                  std::endl;
    }

    exit(EXIT_SUCCESS);
}
