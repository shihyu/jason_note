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
    //
    // ⚠️ ABA 問題不存在的原因：
    // - SPSC 架構下，只有一個生產者修改 next_write_index_
    // - 只有一個消費者修改 next_read_index_
    // - 因此不會出現「索引被覆蓋後又回到原值」的競爭條件
    //
    // 🔧 若改為 MPSC/MPMC，需要：
    // - 使用 CAS (Compare-And-Swap) 原子操作
    // - 或使用版本標記 (Tagged Pointer) 避免 ABA 問題
    //   ```cpp
    //   struct TaggedIndex {
    //       size_t index;
    //       size_t version;  // 每次更新遞增
    //   };
    //   std::atomic<TaggedIndex> next_write_index_;
    //   ```
    auto getNextToWriteTo() noexcept
    {
        return &store_[next_write_index_];
    }

    // 更新寫入索引 (發布資料)
    // 必須在資料填寫完成後呼叫
    //
    // 📊 使用模式：
    // ```cpp
    // auto* elem = queue.getNextToWriteTo();  // 取得寫入位置
    // *elem = my_data;                        // 填入資料
    // queue.updateWriteIndex();               // 發布資料
    // ```
    //
    // ⚠️ 順序保證：
    // - 必須先完成資料寫入，再呼叫 updateWriteIndex()
    // - 否則消費者可能讀取到未初始化的資料 (Data Race)
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

    // ⚠️ 記憶體順序 (Memory Ordering)：
    // - 當前使用預設的 std::memory_order_seq_cst (Sequential Consistency)
    // - 保證所有執行緒看到一致的操作順序 (最強的記憶體順序保證)
    //
    // 📊 效能影響：
    // - seq_cst 會插入記憶體屏障 (Memory Fence)，開銷約 5-10 個時鐘週期
    // - 在高頻交易場景下，可能累積可觀的延遲
    //
    // 🔧 極致效能優化建議 (需謹慎測試)：
    // - 寫入者使用 memory_order_release：
    //   ```cpp
    //   next_write_index_.store((next_write_index_.load(std::memory_order_relaxed) + 1) % store_.size(),
    //                           std::memory_order_release);
    //   ```
    //   - 保證：此操作前的所有寫入對讀取者可見
    //   - 效果：資料寫入完成後才發布索引
    //
    // - 讀取者使用 memory_order_acquire：
    //   ```cpp
    //   auto read_idx = next_read_index_.load(std::memory_order_acquire);
    //   ```
    //   - 保證：此操作後的所有讀取看到最新值
    //   - 效果：讀取索引後才讀取資料
    //
    // - size() 使用 memory_order_relaxed：
    //   ```cpp
    //   return num_elements_.load(std::memory_order_relaxed);
    //   ```
    //   - 理由：size() 僅用於參考，不影響正確性
    //
    // ⚠️ 重要警告：
    // - 更改記憶體順序需要徹底理解 C++ Memory Model
    // - 錯誤的記憶體順序可能導致難以重現的 Data Race
    // - 建議使用 Thread Sanitizer 工具驗證：
    //   ```bash
    //   g++ -fsanitize=thread -g your_code.cpp
    //   ```
    // - 效能提升通常 < 5%，不值得冒險（除非已測量證實為瓶頸）
    //
    // 📚 參考資料：
    // - C++ Memory Model：https://en.cppreference.com/w/cpp/atomic/memory_order
    // - "C++ Concurrency in Action" by Anthony Williams (Chapter 5)
    std::atomic<size_t> next_write_index_ = {0};
    std::atomic<size_t> next_read_index_ = {0};

    std::atomic<size_t> num_elements_ = {0};
};
}
