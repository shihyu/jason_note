// 日誌基準測試：隔離 I/O 影響，量測批次吞吐。
// ⚡ 效能關鍵：固定工作集，避免 cache 污染。
// ⚠️ 注意：需固定 CPU affinity 以降低抖動。

#include "common/logging.h"
#include "common/opt_logging.h"
#include "common/perf_utils.h"

std::string random_string(size_t length)
{
    auto randchar = []() -> char {
        // ⚡ 關鍵路徑：函式內避免鎖/分配，保持快取局部性。
        const char charset[] =
        "0123456789"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz";
        const size_t max_index = (sizeof(charset) - 1);
        return charset[rand() % max_index];
    };
    std::string str(length, 0);
    std::generate_n(str.begin(), length, randchar);
    return str;
}

template<typename T>
size_t benchmarkLogging(T* logger)
{
    constexpr size_t loop_count = 100000;
    size_t total_rdtsc = 0;

    for (size_t i = 0; i < loop_count; ++i) {
        const auto s = random_string(128);
        // ⚡ 週期計數：用於微秒級量測。
        const auto start = Common::rdtsc();
        logger->log("%\n", s);
        // ⚡ 週期計數：用於微秒級量測。
        total_rdtsc += (Common::rdtsc() - start);
    }

    return (total_rdtsc / loop_count);
}

int main(int, char**)
{
    using namespace std::literals::chrono_literals;

    {
        Common::Logger logger("logger_benchmark_original.log");
        const auto cycles = benchmarkLogging(&logger);
        std::cout << "ORIGINAL LOGGER " << cycles << " CLOCK CYCLES PER OPERATION." <<
                  std::endl;
        std::this_thread::sleep_for(10s);
    }

    {
        OptCommon::OptLogger opt_logger("logger_benchmark_optimized.log");
        const auto cycles = benchmarkLogging(&opt_logger);
        std::cout << "OPTIMIZED LOGGER " << cycles << " CLOCK CYCLES PER OPERATION." <<
                  std::endl;
        std::this_thread::sleep_for(10s);
    }

    exit(EXIT_SUCCESS);
}
