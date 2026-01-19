// 高效能關鍵技術示例
// 章節：Essential C++ Techniques - 檔案：mutex.cpp

// 關鍵技術：鎖保護臨界區，避免資料競爭。
#include <mutex>
#include <exception>

auto func(std::mutex &m, bool x, bool y) {
    // 關鍵技術：移動語意與例外安全更新。
    std::scoped_lock guard(m);
    if (x) {
        // guard releases mutex at early exit
        return;
    }
    
    if (y) {
        // guard releases mutex if exception is thrown
        throw std::exception();
    }
} // guard also releases mutex at function exit
