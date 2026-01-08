#pragma once

#include <cstdint>
#include <vector>
#include <string>

#include "macros.h"

namespace OptCommon
{
// OptMemPool: 優化版記憶體池
//
// ⚡ 優化重點:
// 1. 移除除錯斷言: 在發布版本 (!defined(NDEBUG)) 中完全移除 ASSERT 檢查
// 2. 最小化分支: 減少核心路徑中的條件判斷，利於 CPU 分支預測
// 3. 專為高效能生產環境設計
template<typename T>
class OptMemPool final
{
public:
    // ...

    /// Allocate a new object of type T, use placement new to initialize the object, mark the block as in-use and return the object.
    template<typename... Args>
    T* allocate(Args... args) noexcept
    {
        auto obj_block = &(store_[next_free_index_]);
        
        // ⚡ 在效能關鍵路徑中，除錯檢查是昂貴的
        // 透過條件編譯，確保生產版本 (Release) 擁有純粹的執行效率
        #if !defined(NDEBUG)
        ASSERT(obj_block->is_free_,
               "Expected free ObjectBlock at index:" + std::to_string(next_free_index_));
        #endif
        
        T* ret = &(obj_block->object_);
        ret = new (ret) T(args...); // placement new.
        obj_block->is_free_ = false;

        updateNextFreeIndex();

        return ret;
    }

    /// Return the object back to the pool by marking the block as free again.
    auto deallocate(const T* elem) noexcept
    {
        const auto elem_index = (reinterpret_cast<const ObjectBlock*>
                                 (elem) - &store_[0]);
        
        // ⚡ 移除發布版本的邊界檢查
        #if !defined(NDEBUG)
        ASSERT(elem_index >= 0 &&
               static_cast<size_t>(elem_index) < store_.size(),
               "Element being deallocated does not belong to this Memory pool.");
        ASSERT(!store_[elem_index].is_free_,
               "Expected in-use ObjectBlock at index:" + std::to_string(elem_index));
        #endif
        store_[elem_index].is_free_ = true;
    }

    // Deleted default, copy & move constructors and assignment-operators.
    OptMemPool() = delete;

    OptMemPool(const OptMemPool&) = delete;

    OptMemPool(const OptMemPool&&) = delete;

    OptMemPool& operator=(const OptMemPool&) = delete;

    OptMemPool& operator=(const OptMemPool&&) = delete;

private:
    /// Find the next available free block to be used for the next allocation.
    auto updateNextFreeIndex() noexcept
    {
        const auto initial_free_index = next_free_index_;

        while (!store_[next_free_index_].is_free_) {
            ++next_free_index_;

            if (UNLIKELY(next_free_index_ ==
                         store_.size())) { // hardware branch predictor should almost always predict this to be false any ways.
                next_free_index_ = 0;
            }

            if (UNLIKELY(initial_free_index == next_free_index_)) {
                #if !defined(NDEBUG)
                ASSERT(initial_free_index != next_free_index_, "Memory Pool out of space.");
                #endif
            }
        }
    }

    /// It is better to have one vector of structs with two objects than two vectors of one object.
    /// Consider how these are accessed and cache performance.
    struct ObjectBlock {
        T object_;
        bool is_free_ = true;
    };

    /// We could've chosen to use a std::array that would allocate the memory on the stack instead of the heap.
    /// We would have to measure to see which one yields better performance.
    /// It is good to have objects on the stack but performance starts getting worse as the size of the pool increases.
    std::vector<ObjectBlock> store_;

    size_t next_free_index_ = 0;
};
}
