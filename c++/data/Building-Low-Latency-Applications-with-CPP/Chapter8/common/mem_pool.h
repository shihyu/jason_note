#pragma once

#include <cstdint>
#include <vector>
#include <string>

#include "macros.h"

namespace Common
{
// ============================================================================
// 記憶體池 (Memory Pool)
// ============================================================================
// 📌 設計目的：避免執行期動態記憶體分配 (malloc/new)
//
// ⚡ 效能優勢：
// 1. 零碎片化：預先分配連續記憶體區塊
// 2. 快取友善 (Cache Friendly)：物件在記憶體中緊密排列
// 3. 確定性延遲：分配/釋放操作的時間複雜度低且穩定
//
// ⚠️ 實作細節：
// - 使用 std::vector 作為底層儲存 (堆積分配，但在啟動時完成)
// - 使用 Placement New 在已分配的記憶體上建構物件
// - 簡單的線性搜尋找空閒區塊 (next_free_index_)
template<typename T>
class MemPool final
{
public:
    explicit MemPool(std::size_t num_elems) :
        store_(num_elems,
    {
        T(), true
    }) /* pre-allocation of vector storage. */
    {
        // 確保 T 物件是 ObjectBlock 的第一個成員 (對齊檢查)
        ASSERT(reinterpret_cast<const ObjectBlock*>(&(store_[0].object_)) == &
               (store_[0]), "T object should be first member of ObjectBlock.");
    }

    // 分配物件
    // ⚡ 使用 Placement New 在預分配的記憶體塊上建構物件
    template<typename... Args>
    T* allocate(Args... args) noexcept
    {
        auto obj_block = &(store_[next_free_index_]);
        ASSERT(obj_block->is_free_,
               "Expected free ObjectBlock at index:" + std::to_string(next_free_index_));
        T* ret = &(obj_block->object_);
        
        // ⚡ Placement New: 不分配記憶體，只呼叫建構函式
        ret = new (ret) T(args...); 
        obj_block->is_free_ = false;

        updateNextFreeIndex();

        return ret;
    }

    // 釋放物件
    // 實際上只是標記該區塊為 "free"，不釋放記憶體
    auto deallocate(const T* elem) noexcept
    {
        // 計算元素在 vector 中的索引
        const auto elem_index = (reinterpret_cast<const ObjectBlock*>
                                 (elem) - &store_[0]);
        ASSERT(elem_index >= 0 &&
               static_cast<size_t>(elem_index) < store_.size(),
               "Element being deallocated does not belong to this Memory pool.");
        ASSERT(!store_[elem_index].is_free_,
               "Expected in-use ObjectBlock at index:" + std::to_string(elem_index));
        store_[elem_index].is_free_ = true;
    }

    // Deleted default, copy & move constructors and assignment-operators.
    MemPool() = delete;

    MemPool(const MemPool&) = delete;

    MemPool(const MemPool&&) = delete;

    MemPool& operator=(const MemPool&) = delete;

    MemPool& operator=(const MemPool&&) = delete;

private:
    // 更新下一個可用區塊索引
    // ⚡ 線性搜尋：雖然看似低效，但在高負載下通常很快能找到 (因為釋放也會發生)
    auto updateNextFreeIndex() noexcept
    {
        const auto initial_free_index = next_free_index_;

        while (!store_[next_free_index_].is_free_) {
            ++next_free_index_;

            // 循環搜尋
            if (UNLIKELY(next_free_index_ ==
                         store_.size())) { // hardware branch predictor should almost always predict this to be false any ways.
                next_free_index_ = 0;
            }

            if (UNLIKELY(initial_free_index == next_free_index_)) {
                ASSERT(initial_free_index != next_free_index_, "Memory Pool out of space.");
            }
        }
    }

    // 內部儲存單元
    // 包含物件本身與一個布林標記
    //
    // ✅ Cache Locality 優勢：
    // - 狀態標記 (is_free_) 與物件資料緊鄰
    // - 查詢空閒區塊時，物件資料可能已在 Cache 中
    //
    // ⚠️ False Sharing 風險：
    // - 定義：多個 CPU 核心同時存取同一 Cache Line 的不同位置
    // - Cache Line 大小通常為 64 bytes (x86/x64)
    // - 若 ObjectBlock 小於 64 bytes，多個區塊會共享同一 Cache Line
    //
    // 🔬 問題場景：
    // ```
    // Cache Line (64 bytes)：
    // [ObjectBlock 0 (32B)] [ObjectBlock 1 (32B)]
    // ```
    // - 執行緒 A 在核心 0 修改 ObjectBlock 0 的 is_free_
    // - 執行緒 B 在核心 1 修改 ObjectBlock 1 的 is_free_
    // - 結果：兩個核心反覆使對方的 Cache 失效 (Cache Invalidation)
    // - 效能影響：延遲增加 10-50 倍 (取決於跨核心距離)
    //
    // 📊 效能數據：
    // - 本地 Cache 存取：~4 個時鐘週期 (~1ns @ 3GHz)
    // - 跨核心 Cache 同步：~40 個時鐘週期 (~13ns @ 3GHz)
    // - False Sharing 懲罰：可達數百個時鐘週期
    //
    // 🔧 解決方案 1：快取行對齊 (Cache Line Alignment)
    // ```cpp
    // struct alignas(64) ObjectBlock {
    //     T object_;
    //     bool is_free_ = true;
    // };
    // ```
    // - 效果：每個 ObjectBlock 獨佔一個 Cache Line
    // - 代價：記憶體使用增加 (若 T 很小，浪費空間)
    // - 範例：若 T 是 8 bytes，每個 ObjectBlock 佔用 64 bytes (浪費 56 bytes)
    //
    // 🔧 解決方案 2：分離資料與元資料
    // ```cpp
    // std::vector<T> objects_;           // 物件儲存
    // std::vector<bool> is_free_flags_;  // 狀態標記（獨立陣列）
    // ```
    // - 效果：避免 False Sharing，但失去 Cache Locality
    //
    // 🔧 解決方案 3：使用 Padding
    // ```cpp
    // struct ObjectBlock {
    //     T object_;
    //     bool is_free_ = true;
    //     char padding_[63];  // 填充至 64 bytes
    // };
    // ```
    //
    // ✅ 當前實作適用場景：
    // - 單執行緒環境 (無 False Sharing 風險)
    // - 低競爭多執行緒環境 (不同執行緒存取不同區塊)
    // - T 本身較大 (例如 >= 32 bytes，減少 False Sharing 機率)
    //
    // ⚠️ 不適用場景：
    // - 多執行緒頻繁分配/釋放小物件 (高 False Sharing 風險)
    // - 此時建議改用 Per-Thread Memory Pool (每個執行緒獨立的記憶體池)
    //
    // 📚 進階優化：Per-Thread Memory Pool
    // ```cpp
    // thread_local MemPool<T> local_pool(1024);  // 每個執行緒獨立
    // ```
    // - 優點：完全避免跨執行緒競爭
    // - 缺點：記憶體無法跨執行緒共享
    struct ObjectBlock {
        T object_;
        bool is_free_ = true;
    };

    // 底層儲存容器
    // 使用 vector 在 Heap 上分配連續空間
    std::vector<ObjectBlock> store_;

    size_t next_free_index_ = 0;
};
}
