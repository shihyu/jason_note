#pragma once

#include <iostream>
#include <vector>
#include <atomic>

#include "macros.h"

namespace Common
{
// ============================================================================
// 無鎖佇列 (Lock-Free Queue)
// ============================================================================
// 📌 設計類型：SPSC (Single-Producer Single-Consumer)
//
// ⚡ 核心原理：
// 1. 環狀緩衝區 (Ring Buffer)：使用 std::vector 作為底層儲存，預先分配記憶體。
// 2. 原子索引 (Atomic Indices)：next_write_index_ 和 next_read_index_ 使用 std::atomic 管理。
// 3. 無鎖機制：
//    - 生產者 (Producer) 只修改 next_write_index_
//    - 消費者 (Consumer) 只修改 next_read_index_
//    - 因此不需要 Mutex 或 Semaphore，避免了 Context Switch 開銷。
//
// ⚠️ 限制：此實作僅適用於「單一寫入執行緒」對「單一讀取執行緒」。
//    若有多個生產者或消費者，需要使用 CAS (Compare-And-Swap) 或 MPSC/MPMC 佇列。
template<typename T>
class LFQueue final
{
public:
    LFQueue(std::size_t num_elems) :
        store_(num_elems, T()) /* pre-allocation of vector storage. */
    {
    }

    // 取得下一個寫入位置的指標
    // ⚡ 零拷貝 (Zero-Copy) 寫入：直接返回指標供外部填入資料
    auto getNextToWriteTo() noexcept
    {
        return &store_[next_write_index_];
    }

    // 更新寫入索引 (發布資料)
    // 必須在資料填寫完成後呼叫
    auto updateWriteIndex() noexcept
    {
        next_write_index_ = (next_write_index_ + 1) % store_.size();
        num_elements_++;
    }

    // 取得下一個讀取位置的指標
    // ⚡ 零拷貝 (Zero-Copy) 讀取：直接返回內部指標
    // @return 若佇列為空則返回 nullptr
    auto getNextToRead() const noexcept -> const T*
    {
        return (size() ? &store_[next_read_index_] : nullptr);
    }

    // 更新讀取索引 (標記資料已消費)
    auto updateReadIndex() noexcept
    {
        next_read_index_ = (next_read_index_ + 1) % store_.size();
        ASSERT(num_elements_ != 0,
               "Read an invalid element in:" + std::to_string(pthread_self()));
        num_elements_--;
    }

    // 取得目前佇列大小
    // ⚠️ 近似值：在多執行緒環境下，此數值可能在讀取瞬間變動
    auto size() const noexcept
    {
        return num_elements_.load();
    }

    // Deleted default, copy & move constructors and assignment-operators.
    LFQueue() = delete;

    LFQueue(const LFQueue&) = delete;

    LFQueue(const LFQueue&&) = delete;

    LFQueue& operator=(const LFQueue&) = delete;

    LFQueue& operator=(const LFQueue&&) = delete;

private:
    std::vector<T> store_; // 預先分配的環狀緩衝區

    std::atomic<size_t> next_write_index_ = {0};
    std::atomic<size_t> next_read_index_ = {0};

    std::atomic<size_t> num_elements_ = {0};
};
}
