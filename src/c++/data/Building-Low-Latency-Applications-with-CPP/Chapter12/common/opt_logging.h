#pragma once

#include <string>
#include <fstream>
#include <cstdio>
#include <cstring>

#include "macros.h"
#include "lf_queue.h"
#include "thread_utils.h"
#include "time_utils.h"

namespace OptCommon
{
/// Maximum size of the lock free queue of data to be logged.
constexpr size_t LOG_QUEUE_SIZE = 8 * 1024 * 1024;

/// Type of LogElement message.
enum class LogType : int8_t {
    CHAR = 0,
    INTEGER = 1,
    LONG_INTEGER = 2,
    LONG_LONG_INTEGER = 3,
    UNSIGNED_INTEGER = 4,
    UNSIGNED_LONG_INTEGER = 5,
    UNSIGNED_LONG_LONG_INTEGER = 6,
    FLOAT = 7,
    DOUBLE = 8,
    STRING = 9
};

/// Represents a single and primitive log entry.
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
        char s[256];
    } u_;
};

// OptLogger: 優化版非同步記錄器
//
// ⚡ 優化重點: 
// 1. 支持 LogType::STRING: 透過固定大小的字元陣列 (256 bytes) 直接儲存字串
// 2. 減少佇列操作: 原始版本需逐字元 pushValue (O(N))，此版本僅需一次寫入 (O(1))
// 3. 適用於高頻路徑中的固定長度描述字串
class OptLogger final
{
public:
    /// Consumes from the lock free queue of log entries and writes to the output log file.
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
                case LogType::STRING:
                    // ⚡ 直接寫入整個字串，效率高於逐字元輸出
                    file_ << next->u_.s;
                    break;
                }

                queue_.updateReadIndex();
            }

            file_.flush();

            using namespace std::literals::chrono_literals;
            std::this_thread::sleep_for(10ms);
        }
    }

    // ...

    // 基礎推入函式: 將 LogElement 寫入佇列
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

    // ⚡ 優化後的字串寫入
    // 使用 strncpy 將字串拷貝到 LogElement 的 union 緩衝區中
    // 這樣只需操作一次無鎖佇列的寫入索引
    auto pushValue(const char* value) noexcept
    {
        LogElement l{LogType::STRING, {.s = {}}};
        strncpy(l.u_.s, value, sizeof(l.u_.s) - 1);
        pushValue(l);
    }

    auto pushValue(const std::string& value) noexcept
    {
        pushValue(value.c_str());
    }

    /// Parse the format string, substitute % with the variable number of arguments passed and write the string to the lock free queue.
    template<typename T, typename... A>
    auto log(const char* s, const T& value, A... args) noexcept
    {
        while (*s) {
            if (*s == '%') {
                // ⚡ 分支預測提示：降低誤判成本。
                if (UNLIKELY(*(s + 1) == '%')) { // to allow %% -> % escape character.
                    ++s;
                } else {
                    pushValue(value); // substitute % with the value specified in the arguments.
                    log(s + 1, args...); // pop an argument and call self recursively.
                    return;
                }
            }

            pushValue(*s++);
        }

        FATAL("extra arguments provided to log()");
    }

    /// Overload for case where no substitution in the string is necessary.
    /// Note that this is overloading not specialization. gcc does not allow inline specializations.
    auto log(const char* s) noexcept
    {
        while (*s) {
            if (*s == '%') {
                // ⚡ 分支預測提示：降低誤判成本。
                if (UNLIKELY(*(s + 1) == '%')) { // to allow %% -> % escape character.
                    ++s;
                } else {
                    FATAL("missing arguments to log()");
                }
            }

            pushValue(*s++);
        }
    }

    explicit OptLogger(const std::string& file_name)
        : file_name_(file_name), queue_(LOG_QUEUE_SIZE)
    {
        file_.open(file_name);
        ASSERT(file_.is_open(), "Could not open log file:" + file_name);

        logger_thread_ = Common::createAndStartThread(-1,
        "OptCommon/OptLogger " + file_name_, [this]() {
            flushQueue();
        });
        ASSERT(logger_thread_ != nullptr, "Failed to start OptLogger thread.");
    }

    ~OptLogger()
    {
        std::string time_str;
        std::cerr << Common::getCurrentTimeStr(&time_str) <<
                  " Flushing and closing OptLogger for " << file_name_ << std::endl;

        while (queue_.size()) {
            using namespace std::literals::chrono_literals;
            std::this_thread::sleep_for(1s);
        }

        running_ = false;
        logger_thread_->join();
        file_.close();

        delete logger_thread_;
        logger_thread_ = nullptr;
    }

    /// Deleted default, copy & move constructors and assignment-operators.
    OptLogger() = delete;

    OptLogger(const OptLogger&) = delete;

    OptLogger(const OptLogger&&) = delete;

    OptLogger& operator=(const OptLogger&) = delete;

    OptLogger& operator=(const OptLogger&&) = delete;

private:
    /// File to which the log entries will be written.
    const std::string file_name_;
    std::ofstream file_;

    /// Lock free queue of log elements from main logging thread to background formatting and disk writer thread.
    Common::LFQueue<LogElement> queue_;
    // ⚡ 原子操作：避免鎖但需注意記憶體序。
    std::atomic<bool> running_ = {true};

    /// Background logging thread.
    std::thread* logger_thread_ = nullptr;
};
}
