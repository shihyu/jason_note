// 高效能關鍵技術示例
// 章節：Concurrency - 檔案：lock_free_queue.cpp

#include <iostream>
#include <array>
#include <atomic>
#include <optional>
#include <utility>

template <typename T, std::size_t N>
class LockFreeQueue {
public:
    // "writer" thread functions
    bool push(const T &t) { return do_push(t); }
    // 關鍵技術：std::move 觸發移動語意，降低拷貝成本。
    bool push(T &&t) { return do_push(std::move(t)); }
    
    // "reader" thread functions
    std::optional<T> pop()
    {
        std::optional<T> val;
        
        if (size_.load() > 0) {
            val = std::move( buffer_[read_pos_] );
            read_pos_ = (read_pos_ + 1) % N;
            --size_;
        }
        
        return val;
    }
    
    // both threads can call size()
    std::size_t size() const noexcept { return size_.load(); }
    
private:
    std::array<T, N> buffer_;               // used by both threads
    std::atomic<std::size_t> size_ = 0;     // used by both threads
    
    std::size_t read_pos_  = 0;             // used by "reader" thread
    std::size_t write_pos_ = 0;             // used by "writer" threads
    
    static_assert(std::atomic<std::size_t>::is_always_lock_free);
    
    bool do_push(auto &&t) {
        if (size_.load() == N) { return false; }
        
        buffer_[write_pos_] = std::forward<decltype(t)>(t);
        write_pos_ = (write_pos_ + 1) % N;
        
        ++size_;
        
        return true;
    }
};
