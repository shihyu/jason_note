#pragma once

#include <iostream>
#include <vector>
#include <atomic>

#include "macros.h"

namespace Common
{
// Lock-Free Queue: 單生產者單消費者(SPSC)無鎖佇列
//
// 設計原理:
// 1. Ring Buffer: 使用固定大小的環形緩衝區,避免動態記憶體分配
// 2. 原子索引: next_write_index_(Producer)與 next_read_index_(Consumer)各自獨立修改
// 3. 無鎖設計: 使用 std::atomic 保證可見性,不需要 Mutex
//
// 使用場景: 市場數據管道、訂單佇列等單執行緒生產/消費場景
template<typename T>
class LFQueue final
{
public:
    // 建構函式: 預先配置所有元素,確保執行時零記憶體分配
    // @param num_elems: 佇列容量(固定大小)
    LFQueue(std::size_t num_elems) :
        store_(num_elems, T()) /* ⚡ 預先配置: 避免執行時記憶體分配,延遲穩定 */
    {
    }

    // 取得下一個可寫入的位置(Producer 呼叫)
    // @return: 指向可寫入槽位的指標,避免資料複製
    // ⚡ 效能關鍵: 返回指標而非引用,允許原地構造(in-place construction)
    auto getNextToWriteTo() noexcept
    {
        return &store_[next_write_index_];
    }

    // 更新寫入索引(Producer 呼叫)
    // ⚠️ 注意: 必須在資料寫入完成後才呼叫,否則 Consumer 可能讀到未完成的資料
    //
    // Memory Ordering: 當前使用預設的 seq_cst(循序一致性)
    // 優化方向: 可改用 memory_order_release,減少記憶體屏障開銷
    auto updateWriteIndex() noexcept
    {
        next_write_index_ = (next_write_index_ + 1) % store_.size();  // Ring Buffer 環繞
        num_elements_++;  // ⚡ 原子遞增,無需鎖
    }

    // 取得下一個可讀取的元素(Consumer 呼叫)
    // @return: 指向可讀取元素的指標,若佇列為空則返回 nullptr
    //
    // ⚠️ ABA 問題: 本實作不受影響,因為:
    // 1. SPSC 限制: 只有一個 Producer 修改 next_write_index_
    // 2. 不使用 CAS 操作
    auto getNextToRead() const noexcept -> const T*
    {
        return (size() ? &store_[next_read_index_] : nullptr);
    }

    // 更新讀取索引(Consumer 呼叫)
    // ⚠️ 注意: 必須在處理完資料後才呼叫,否則 Producer 可能覆蓋未處理的資料
    auto updateReadIndex() noexcept
    {
        next_read_index_ = (next_read_index_ + 1) % store_.size();  // Ring Buffer 環繞
        ASSERT(num_elements_ != 0,
               "Read an invalid element in:" + std::to_string(pthread_self()));
        num_elements_--;  // ⚡ 原子遞減
    }

    // 取得當前佇列中的元素數量
    // @return: 當前元素數量(原子讀取)
    auto size() const noexcept
    {
        // ⚡ 記憶體序：影響可見性與效能。
        return num_elements_.load();  // 預設使用 memory_order_seq_cst
    }

    // Deleted default, copy & move constructors and assignment-operators.
    // 禁止複製/移動: Lock-Free Queue 的語義不允許複製
    LFQueue() = delete;

    LFQueue(const LFQueue&) = delete;

    LFQueue(const LFQueue&&) = delete;

    LFQueue& operator=(const LFQueue&) = delete;

    LFQueue& operator=(const LFQueue&&) = delete;

private:
    // Ring Buffer 底層儲存: 預先配置的固定大小向量
    // Cache 友善性: 元素在記憶體中緊密排列
    std::vector<T> store_;

    // ⚠️ Cache Line False Sharing 風險:
    // next_write_index_(Producer 頻繁修改)和 next_read_index_(Consumer 頻繁修改)
    // 若在同一 Cache Line(64 bytes),會導致 Cache 乒乓效應
    //
    // 優化方向: 使用 alignas(64) 強制對齊到不同的 Cache Line
    std::atomic<size_t> next_write_index_ = {0};  // Producer 專用: 下一個寫入位置
    std::atomic<size_t> next_read_index_ = {0};   // Consumer 專用: 下一個讀取位置

    std::atomic<size_t> num_elements_ = {0};      // 當前元素數量(雙方共享)
};
}
