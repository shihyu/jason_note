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
// ========================================
// 無鎖日誌系統 (Lock-Free Logging System)
// ========================================
//
// 設計目標:
// 1. 極低延遲: 日誌呼叫延遲 < 100ns (僅寫入佇列,不執行 I/O)
// 2. 零鎖競爭: 使用 Lock-Free Queue,避免 Mutex 阻塞
// 3. 非同步 I/O: 專用執行緒負責將日誌刷新到磁碟,不影響交易路徑
//
// 核心架構:
// - Producer (交易執行緒): 呼叫 log() → 將 LogElement 推入 LFQueue
// - Consumer (日誌執行緒): 從 LFQueue 讀取 → 寫入檔案 → flush
//
// 效能關鍵:
// - Tagged Union: LogElement 使用 union 存放不同類型,避免虛擬函式開銷
// - Type Erasure: 所有類型統一儲存為 LogElement,減少模板實例化
// - 批次 Flush: 累積多筆日誌後一次刷新,降低 I/O 開銷

// 日誌佇列大小: 8MB (約可容納 500,000+ LogElement)
// ⚠️ 權衡: 太小會導致佇列滿溢,太大會浪費記憶體
constexpr size_t LOG_QUEUE_SIZE = 8 * 1024 * 1024;

// LogElement 類型標籤: 使用 int8_t 節省空間
// ⚡ 效能考量: enum class 防止隱式轉換,編譯器可優化 switch-case
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

// 日誌元素: Tagged Union 設計
//
// 記憶體佈局 (64位元平台):
// - type_: 1 byte (對齊後可能佔 4 bytes)
// - u_: 8 bytes (union 取最大成員 long long/double)
// 總計: ~16 bytes (含對齊)
//
// ⚡ 為何使用 union 而非 std::variant?
// 1. 零開銷: variant 需額外 discriminator,union 直接使用 type_
// 2. Cache 友善: 緊湊記憶體佈局,減少 Cache Miss
// 3. 避免動態分配: variant 可能在某些情況下分配記憶體
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

// Logger: 無鎖日誌記錄器
//
// 執行緒模型:
// - 主執行緒(Producer): 呼叫 log() 寫入 LFQueue
// - 日誌執行緒(Consumer): 執行 flushQueue() 將佇列內容寫入檔案
//
// ⚡ 效能保證:
// - log() 延遲: < 100ns (僅涉及記憶體寫入)
// - flushQueue() 延遲: 10ms 批次間隔 (可調整)
class Logger final
{
public:
    // 日誌刷新執行緒的主迴圈
    //
    // 處理流程:
    // 1. 從 LFQueue 批次讀取所有可用的 LogElement
    // 2. 根據 type_ 標籤解析 union,寫入檔案流
    // 3. 呼叫 file_.flush() 確保資料寫入作業系統緩衝區
    // 4. 睡眠 10ms 後重複(避免 CPU 空轉)
    //
    // ⚠️ 批次處理的重要性:
    // - 每次迴圈處理所有已入佇列的元素(while queue_.size())
    // - 減少 flush() 呼叫頻率,降低 I/O 開銷
    // - 10ms 間隔在延遲和 CPU 使用率間取得平衡
    auto flushQueue() noexcept
    {
        while (running_) {  // 執行緒生命週期標誌

            // 🔁 批次消費: 一次處理佇列中的所有元素
            for (auto next = queue_.getNextToRead(); queue_.size() &&
                 next; next = queue_.getNextToRead()) {
                // Tagged Union 解包: 根據 type_ 存取正確的 union 成員
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

                queue_.updateReadIndex();  // 釋放佇列槽位供 Producer 重用
            }

            // ⚡ 批次 flush: 減少系統呼叫次數
            file_.flush();

            // 睡眠 10ms 避免 CPU 空轉
            // ⚖️ 權衡: 較短間隔(1ms)降低延遲但增加 CPU 使用率
            //          較長間隔(100ms)可能導致日誌積壓
            using namespace std::literals::chrono_literals;
            std::this_thread::sleep_for(10ms);
        }
    }

    // 建構函式: 初始化日誌系統並啟動日誌執行緒
    // @param file_name: 日誌檔案路徑
    //
    // 初始化流程:
    // 1. 預先配置 LFQueue (LOG_QUEUE_SIZE = 8MB)
    // 2. 開啟日誌檔案
    // 3. 啟動專用日誌執行緒,執行 flushQueue()
    //
    // ⚡ CPU 親和性: createAndStartThread(-1, ...) 使用 -1 表示不綁定特定 CPU
    //              實際生產環境可能需要將日誌執行緒綁定到低優先順序 CPU
    explicit Logger(const std::string& file_name)
        : file_name_(file_name), queue_(LOG_QUEUE_SIZE)
    {
        file_.open(file_name);
        ASSERT(file_.is_open(), "Could not open log file:" + file_name);

        // 啟動日誌刷新執行緒
        // ⚠️ Lambda 捕獲 this: 確保 flushQueue() 可存取成員變數
        logger_thread_ = createAndStartThread(-1,
        "Common/Logger " + file_name_, [this]() {
            flushQueue();
        });
        ASSERT(logger_thread_ != nullptr, "Failed to start Logger thread.");
    }

    // 解構函式: 優雅關閉日誌系統
    //
    // 關閉流程:
    // 1. 等待佇列清空 (最多等待數秒,視佇列大小而定)
    // 2. 設定 running_ = false 通知日誌執行緒停止
    // 3. join() 等待日誌執行緒完全退出
    // 4. 關閉檔案流
    //
    // ⚠️ 資料遺失風險:
    // - 如果程式異常終止(如 SIGKILL),佇列中的日誌可能遺失
    // - 正常關閉時,此解構函式確保所有日誌都已寫入檔案
    ~Logger()
    {
        std::string time_str;
        std::cerr << Common::getCurrentTimeStr(&time_str) <<
                  " Flushing and closing Logger for " << file_name_ << std::endl;

        // 🔁 等待佇列清空: 最多等待 queue_.size() 秒
        while (queue_.size()) {
            using namespace std::literals::chrono_literals;
            std::this_thread::sleep_for(1s);
        }

        // 通知日誌執行緒停止
        running_ = false;
        logger_thread_->join();  // 等待執行緒退出

        file_.close();
        std::cerr << Common::getCurrentTimeStr(&time_str) << " Logger for " <<
                  file_name_ << " exiting." << std::endl;
    }

    // ========================================
    // pushValue 家族: 將不同類型的值推入佇列
    // ========================================
    //
    // 設計模式: Function Overloading + Tagged Union
    // - 使用函式重載提供型別安全的 API
    // - 內部統一轉換為 LogElement 並推入 LFQueue
    //
    // ⚡ 效能特性:
    // - noexcept: 保證不拋出例外,編譯器可進行更積極的優化
    // - 內聯候選: 簡短函式通常會被內聯,減少函式呼叫開銷
    // - 零記憶體分配: 直接在預先配置的 LFQueue 槽位上構造 LogElement

    // 基礎推入函式: 將 LogElement 寫入佇列
    // ⚡ 關鍵路徑: 此函式是所有日誌操作的最終入口
    auto pushValue(const LogElement& log_element) noexcept
    {
        *(queue_.getNextToWriteTo()) = log_element;  // 原地構造
        queue_.updateWriteIndex();  // 原子更新索引,Consumer 可見
    }

    // 型別特化的 pushValue 函式
    // ⚙️ 編譯器行為: 這些函式通常會被內聯,最終只剩下一次函式呼叫
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

    // 字串推入: 逐字元分解
    // ⚠️ 效能影響: 字串 "hello" 會產生 5 次 pushValue(char) 呼叫
    //              對於長字串,這可能影響效能
    auto pushValue(const char* value) noexcept
    {
        while (*value) {
            pushValue(*value);  // 每個字元單獨入佇列
            ++value;
        }
    }

    auto pushValue(const std::string& value) noexcept
    {
        pushValue(value.c_str());
    }

    // ========================================
    // log(): printf 風格的變參模板日誌函式
    // ========================================
    //
    // 使用範例:
    //   logger.log("Order ID: % Price: % Qty: %\n", order_id, price, qty);
    //
    // 實作原理:
    // 1. 編譯期遞迴: 使用 variadic templates 展開參數
    // 2. 格式字串解析: 遇到 '%' 時插入參數值
    // 3. 尾遞迴優化: 編譯器可將遞迴優化為迴圈
    //
    // ⚡ 效能優勢 vs printf():
    // - 無格式字串解析開銷 (編譯期完成)
    // - 無 varargs 開銷 (模板展開)
    // - 型別安全 (編譯期檢查)

    // 變參版本: 處理帶參數的日誌訊息
    // @param s: 格式字串 (包含 '%' 佔位符)
    // @param value: 當前要替換的參數值
    // @param args: 剩餘參數包
    //
    // 🔁 遞迴邏輯:
    // 1. 掃描格式字串直到遇到 '%'
    // 2. 將 '%' 替換為 value,推入佇列
    // 3. 遞迴呼叫 log(s+1, args...) 處理剩餘參數
    template<typename T, typename... A>
    auto log(const char* s, const T& value, A... args) noexcept
    {
        while (*s) {
            if (*s == '%') {
                if (UNLIKELY(*(s + 1) == '%')) {  // %% 逃逸序列 -> 單一 %
                    ++s;
                } else {
                    pushValue(value);  // 替換 % 為參數值
                    log(s + 1, args...);  // 遞迴處理剩餘參數
                    return;
                }
            }

            pushValue(*s++);  // 逐字元推入格式字串
        }

        // 格式字串已耗盡但仍有未使用的參數
        FATAL("extra arguments provided to log()");
    }

    // 終止版本: 處理無參數的日誌訊息
    // @param s: 純文字格式字串 (不應包含未配對的 '%')
    //
    // ⚠️ 注意: 這是函式重載而非模板特化
    // 原因: GCC 不允許內聯的模板特化
    auto log(const char* s) noexcept
    {
        while (*s) {
            if (*s == '%') {
                if (UNLIKELY(*(s + 1) == '%')) {  // %% 逃逸序列
                    ++s;
                } else {
                    // 格式字串中有 '%' 但沒有對應的參數
                    FATAL("missing arguments to log()");
                }
            }

            pushValue(*s++);
        }
    }

    // 禁止複製/移動: Logger 持有執行緒資源,不可複製
    Logger() = delete;

    Logger(const Logger&) = delete;

    Logger(const Logger&&) = delete;

    Logger& operator=(const Logger&) = delete;

    Logger& operator=(const Logger&&) = delete;

private:
    // 成員變數佈局考量:
    // - file_name_: 用於錯誤訊息
    // - file_: 日誌檔案流 (僅 Consumer 執行緒存取)
    // - queue_: Lock-Free Queue (Producer 和 Consumer 執行緒共享)
    // - running_: 原子布林標誌,控制 Consumer 執行緒生命週期
    // - logger_thread_: 日誌刷新執行緒控制代碼
    const std::string file_name_;
    std::ofstream file_;

    LFQueue<LogElement> queue_;  // SPSC Lock-Free Queue
    std::atomic<bool> running_ = {true};  // 執行緒停止信號
    std::thread* logger_thread_ = nullptr;  // 日誌刷新執行緒
};
}
