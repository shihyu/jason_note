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
    // 結構體設計有助於 Cache Locality (狀態標記就在物件旁)
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
