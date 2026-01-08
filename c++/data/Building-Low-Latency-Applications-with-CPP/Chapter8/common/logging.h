#pragma once

#include <string>
#include <fstream>
#include <cstdio>

#include "macros.h"
#include "lf_queue.h"
#include "thread_utils.h"
#include "time_utils.h"

namespace Common
{
// 日誌佇列大小 (8 MB)
// ⚡ 足夠緩衝大量日誌，避免阻塞主執行緒
constexpr size_t LOG_QUEUE_SIZE = 8 * 1024 * 1024;

// 日誌資料類型
enum class LogType : int8_t {
    CHAR = 0,
    INTEGER = 1,
    LONG_INTEGER = 2,
    LONG_LONG_INTEGER = 3,
    UNSIGNED_INTEGER = 4,
    UNSIGNED_LONG_INTEGER = 5,
    UNSIGNED_LONG_LONG_INTEGER = 6,
    FLOAT = 7,
    DOUBLE = 8
};

// 日誌元素結構 (Tagged Union)
// ⚡ 避免動態記憶體分配 (Zero Allocation)
// 每個日誌片段 (字元、整數、浮點數) 都存為一個固定大小的結構
struct LogElement {
    LogType type_ = LogType::CHAR;
    union {
        char c;
        int i;
        long l;
        long long ll;
        unsigned u;
        unsigned long ul;
        unsigned long long ull;
        float f;
        double d;
    } u_;
};

// ============================================================================
// 低延遲日誌系統 (Low Latency Logger)
// ============================================================================
// 📌 設計原則：
// 1. 非同步寫入 (Asynchronous)：主執行緒只寫入記憶體佇列，後台執行緒寫入磁碟
// 2. 零記憶體分配 (Zero Allocation)：日誌內容不轉為 std::string，直接存入 Ring Buffer
// 3. 無鎖佇列 (Lock-Free Queue)：確保寫入操作極快且不阻塞
class Logger final
{
public:
    // 後台執行緒函式：消費佇列並寫入檔案
    auto flushQueue() noexcept
    {
        while (running_) {

            for (auto next = queue_.getNextToRead(); queue_.size() &&
                 next; next = queue_.getNextToRead()) {
                switch (next->type_) {
                case LogType::CHAR:
                    file_ << next->u_.c;
                    break;

                case LogType::INTEGER:
                    file_ << next->u_.i;
                    break;

                case LogType::LONG_INTEGER:
                    file_ << next->u_.l;
                    break;

                case LogType::LONG_LONG_INTEGER:
                    file_ << next->u_.ll;
                    break;

                case LogType::UNSIGNED_INTEGER:
                    file_ << next->u_.u;
                    break;

                case LogType::UNSIGNED_LONG_INTEGER:
                    file_ << next->u_.ul;
                    break;

                case LogType::UNSIGNED_LONG_LONG_INTEGER:
                    file_ << next->u_.ull;
                    break;

                case LogType::FLOAT:
                    file_ << next->u_.f;
                    break;

                case LogType::DOUBLE:
                    file_ << next->u_.d;
                    break;
                }

                queue_.updateReadIndex();
            }

            file_.flush();

            // ⚡ 避免佔用過多 CPU，適度休眠
            using namespace std::literals::chrono_literals;
            std::this_thread::sleep_for(10ms);
        }
    }

    explicit Logger(const std::string& file_name)
        : file_name_(file_name), queue_(LOG_QUEUE_SIZE)
    {
        file_.open(file_name);
        ASSERT(file_.is_open(), "Could not open log file:" + file_name);
        
        // 啟動獨立的日誌執行緒
        logger_thread_ = createAndStartThread(-1,
        "Common/Logger " + file_name_, [this]() {
            flushQueue();
        });
        ASSERT(logger_thread_ != nullptr, "Failed to start Logger thread.");
    }

    ~Logger()
    {
        std::string time_str;
        std::cerr << Common::getCurrentTimeStr(&time_str) <<
                  " Flushing and closing Logger for " << file_name_ << std::endl;

        // 等待所有日誌寫入完成
        while (queue_.size()) {
            using namespace std::literals::chrono_literals;
            std::this_thread::sleep_for(1s);
        }

        running_ = false;
        logger_thread_->join();

        file_.close();
        std::cerr << Common::getCurrentTimeStr(&time_str) << " Logger for " <<
                  file_name_ << " exiting." << std::endl;
    }

    // 寫入基礎型別到佇列 (多載函式)
    auto pushValue(const LogElement& log_element) noexcept
    {
        *(queue_.getNextToWriteTo()) = log_element;
        queue_.updateWriteIndex();
    }

    auto pushValue(const char value) noexcept
    {
        pushValue(LogElement{LogType::CHAR, {.c = value}});
    }

    auto pushValue(const int value) noexcept
    {
        pushValue(LogElement{LogType::INTEGER, {.i = value}});
    }

    auto pushValue(const long value) noexcept
    {
        pushValue(LogElement{LogType::LONG_INTEGER, {.l = value}});
    }

    auto pushValue(const long long value) noexcept
    {
        pushValue(LogElement{LogType::LONG_LONG_INTEGER, {.ll = value}});
    }

    auto pushValue(const unsigned value) noexcept
    {
        pushValue(LogElement{LogType::UNSIGNED_INTEGER, {.u = value}});
    }

    auto pushValue(const unsigned long value) noexcept
    {
        pushValue(LogElement{LogType::UNSIGNED_LONG_INTEGER, {.ul = value}});
    }

    auto pushValue(const unsigned long long value) noexcept
    {
        pushValue(LogElement{LogType::UNSIGNED_LONG_LONG_INTEGER, {.ull = value}});
    }

    auto pushValue(const float value) noexcept
    {
        pushValue(LogElement{LogType::FLOAT, {.f = value}});
    }

    auto pushValue(const double value) noexcept
    {
        pushValue(LogElement{LogType::DOUBLE, {.d = value}});
    }

    // 字串處理：逐字元寫入，避免字串拷貝
    auto pushValue(const char* value) noexcept
    {
        while (*value) {
            pushValue(*value);
            ++value;
        }
    }

    auto pushValue(const std::string& value) noexcept
    {
        pushValue(value.c_str());
    }

    // ⚡ Variadic Template 實作 printf 風格的日誌記錄
    // 編譯期展開遞迴呼叫，無執行期格式化開銷
    template<typename T, typename... A>
    auto log(const char* s, const T& value, A... args) noexcept
    {
        while (*s) {
            if (*s == '%') {
                if (UNLIKELY(*(s + 1) == '%')) { // to allow %% -> % escape character.
                    ++s;
                } else {
                    pushValue(value); // 寫入當前參數
                    log(s + 1, args...); // 遞迴處理剩餘參數
                    return;
                }
            }

            pushValue(*s++);
        }

        FATAL("extra arguments provided to log()");
    }

    // 遞迴終止條件 (無參數時)
    auto log(const char* s) noexcept
    {
        while (*s) {
            if (*s == '%') {
                if (UNLIKELY(*(s + 1) == '%')) { // to allow %% -> % escape character.
                    ++s;
                } else {
                    FATAL("missing arguments to log()");
                }
            }

            pushValue(*s++);
        }
    }

    // Deleted default, copy & move constructors and assignment-operators.
    Logger() = delete;

    Logger(const Logger&) = delete;

    Logger(const Logger&&) = delete;

    Logger& operator=(const Logger&) = delete;

    Logger& operator=(const Logger&&) = delete;

private:
    const std::string file_name_;
    std::ofstream file_;

    LFQueue<LogElement> queue_; // 無鎖佇列
    std::atomic<bool> running_ = {true};
    std::thread* logger_thread_ = nullptr;
};
}
