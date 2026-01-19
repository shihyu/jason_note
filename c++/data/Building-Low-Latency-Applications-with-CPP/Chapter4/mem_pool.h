#pragma once

#include <cstdint>
#include <vector>
#include <string>

#include "macros.h"

namespace Common
{
// Memory Pool: 固定大小物件的預配置記憶體池
//
// 設計原理:
// 1. 預先配置: 啟動時一次性配置所有記憶體,執行時零配置
// 2. 零碎片化: 所有物件大小相同,記憶體連續排列
// 3. O(1)~O(N) 分配: 使用線性探測法尋找空閒槽位
//
// 使用場景: 訂單物件池、市場數據快照池等頻繁分配/釋放相同大小物件的場景
template<typename T>
class MemPool final
{
public:
    // 建構函式: 預先配置所有記憶體
    // @param num_elems: 記憶體池容量(固定大小)
    //
    // ⚠️ 關鍵斷言: 確保 T object_ 是 ObjectBlock 的第一個成員
    // 原因: 允許透過 T* 指標反向計算 ObjectBlock 索引(指標算術)
    explicit MemPool(std::size_t num_elems) :
        store_(num_elems,
    {
        T(), true  // ⚡ 預設建構 T(),標記為空閒
    }) /* ⚡ 預先配置: 避免執行時記憶體分配,延遲穩定 */
    {
        ASSERT(reinterpret_cast<const ObjectBlock*>(&(store_[0].object_)) == &
               (store_[0]), "T object should be first member of ObjectBlock.");
    }

    // 分配新物件: 使用 Placement New 在預配置的記憶體上建構物件
    // @param args: 轉發給 T 建構子的參數
    // @return: 指向新物件的指標
    //
    // ⚡ Placement New: 只呼叫建構子,不分配記憶體(記憶體已預先配置)
    // 優勢: 避免 malloc 呼叫,節省 50-10000ns
    template<typename... Args>
    T* allocate(Args... args) noexcept
    {
        auto obj_block = &(store_[next_free_index_]);
        ASSERT(obj_block->is_free_,
               "Expected free ObjectBlock at index:" + std::to_string(next_free_index_));
        T* ret = &(obj_block->object_);
        // ⚡ Placement new：物件池避免動態分配。
        ret = new (ret) T(args...); // ⚡ Placement New: 在指定記憶體位置呼叫建構子
        obj_block->is_free_ = false;

        updateNextFreeIndex();  // 線性探測法尋找下一個空閒槽位

        return ret;
    }

    // 釋放物件: 標記槽位為空閒
    // @param elem: 要釋放的物件指標
    //
    // ⚠️ 注意: 本實作未呼叫解構子!
    // 如果 T 持有資源(如 std::string),必須手動呼叫 elem->~T()
    auto deallocate(const T* elem) noexcept
    {
        // 🔍 指標算術: 透過指標減法計算元素索引
        // 前提: T object_ 必須是 ObjectBlock 的第一個成員
        const auto elem_index = (reinterpret_cast<const ObjectBlock*>
                                 (elem) - &store_[0]);
        ASSERT(elem_index >= 0 &&
               static_cast<size_t>(elem_index) < store_.size(),
               "Element being deallocated does not belong to this Memory pool.");
        ASSERT(!store_[elem_index].is_free_,
               "Expected in-use ObjectBlock at index:" + std::to_string(elem_index));
        store_[elem_index].is_free_ = true;  // 只標記為空閒,未呼叫解構子
    }

    // Deleted default, copy & move constructors and assignment-operators.
    MemPool() = delete;

    MemPool(const MemPool&) = delete;

    MemPool(const MemPool&&) = delete;

    MemPool& operator=(const MemPool&) = delete;

    MemPool& operator=(const MemPool&&) = delete;

private:
    auto updateNextFreeIndex() noexcept
    {
        const auto initial_free_index = next_free_index_;

        while (!store_[next_free_index_].is_free_) {
            ++next_free_index_;

            // ⚡ 分支預測提示：降低誤判成本。
            if (UNLIKELY(next_free_index_ ==
                         store_.size())) { // hardware branch predictor should almost always predict this to be false any ways.
                next_free_index_ = 0;
            }

            // ⚡ 分支預測提示：降低誤判成本。
            if (UNLIKELY(initial_free_index == next_free_index_)) {
                ASSERT(initial_free_index != next_free_index_, "Memory Pool out of space.");
            }
        }
    }

    // It is better to have one vector of structs with two objects than two vectors of one object.
    // Consider how these are accessed and cache performance.
    struct ObjectBlock {
        T object_;
        bool is_free_ = true;
    };

    // We could've chosen to use a std::array that would allocate the memory on the stack instead of the heap.
    // We would have to measure to see which one yields better performance.
    // It is good to have objects on the stack but performance starts getting worse as the size of the pool increases.
    std::vector<ObjectBlock> store_;

    size_t next_free_index_ = 0;
};
}
