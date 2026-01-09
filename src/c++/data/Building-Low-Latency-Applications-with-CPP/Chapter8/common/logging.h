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
    //
    // ⚠️ 佇列滿時的行為：
    // - 當前實作：無檢查，直接覆寫舊資料 (Ring Buffer 特性)
    // - 風險：日誌丟失，且無任何警告
    // - 觸發條件：日誌產生速度 > 後台寫入磁碟速度
    //
    // 📊 佇列容量分析：
    // - 佇列大小：8 MB (LOG_QUEUE_SIZE)
    // - 每個 LogElement：約 16 bytes (union + type 欄位)
    // - 最大容量：8 MB ÷ 16 bytes ≈ 500,000 個元素
    // - 若每秒產生 100 萬個日誌元素，佇列會在 0.5 秒內填滿
    //
    // 🔧 生產環境建議改進：
    // 1. 檢查佇列大小（丟棄或等待）：
    //    ```cpp
    //    auto pushValue(const LogElement& log_element) noexcept {
    //        if (queue_.size() >= LOG_QUEUE_SIZE - 1024) {  // 保留 1024 空間避免覆寫
    //            // 方案 A：靜默丟棄
    //            return;
    //
    //            // 方案 B：輸出警告（可能影響效能）
    //            std::cerr << "Logger queue full, dropping log\n";
    //            return;
    //
    //            // 方案 C：等待（阻塞，不推薦）
    //            while (queue_.size() >= LOG_QUEUE_SIZE - 1024) {
    //                std::this_thread::yield();
    //            }
    //        }
    //        *(queue_.getNextToWriteTo()) = log_element;
    //        queue_.updateWriteIndex();
    //    }
    //    ```
    //
    // 2. 使用更大的佇列：
    //    ```cpp
    //    constexpr size_t LOG_QUEUE_SIZE = 64 * 1024 * 1024;  // 64 MB
    //    ```
    //    - 代價：佔用更多記憶體
    //
    // 3. 動態調整後台執行緒 flush 頻率：
    //    ```cpp
    //    auto flush_interval = (queue_.size() > LOG_QUEUE_SIZE / 2) ? 1ms : 10ms;
    //    std::this_thread::sleep_for(flush_interval);
    //    ```
    //
    // 4. 使用條件變數通知後台執行緒：
    //    ```cpp
    //    std::condition_variable queue_not_empty_;
    //    // pushValue() 時通知
    //    queue_not_empty_.notify_one();
    //    // flushQueue() 時等待
    //    queue_not_empty_.wait_for(lock, 10ms);
    //    ```
    //    - 優點：佇列有資料時立即處理
    //    - 缺點：增加同步開銷（需要 Mutex）
    //
    // 📊 監控建議：
    // - 定期檢查 queue_.size()，若長期接近上限則需優化
    // - 記錄峰值佇列大小：
    //   ```cpp
    //   static size_t max_queue_size = 0;
    //   max_queue_size = std::max(max_queue_size, queue_.size());
    //   ```
    // - 若峰值 > 80% 容量，考慮：
    //   1. 減少日誌量（提高日誌級別過濾）
    //   2. 增加佇列大小
    //   3. 使用更快的儲存裝置（SSD、RAM Disk）
    //
    // ⚠️ 特殊情況：磁碟 I/O 阻塞
    // - 若磁碟寫入速度慢（例如 HDD、網路檔案系統）
    // - 後台執行緒會長時間阻塞在 file_.flush()
    // - 主執行緒會持續寫入佇列，最終覆寫舊資料
    // - 緩解措施：
    //   1. 使用 SSD 或 RAM Disk (tmpfs)
    //   2. 使用非同步 I/O (io_uring、libaio)
    //   3. 定期輪轉日誌檔案（避免單一大檔案）
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
