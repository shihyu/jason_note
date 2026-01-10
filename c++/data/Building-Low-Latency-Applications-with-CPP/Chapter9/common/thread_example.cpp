// ============================================================================
// Thread Utilities 使用範例
// ============================================================================
// 📌 範例目的：
// 展示如何使用 createAndStartThread() 建立執行緒並綁定 CPU 核心
//
// 關鍵學習點：
// 1. ⚡ CPU Affinity：將執行緒綁定到特定 CPU 核心，減少 Context Switch
// 2. 執行緒命名：便於除錯時識別執行緒（例如透過 htop、perf）
// 3. 可變參數模板：支援任意函式簽名
//
// 📊 效能影響：
// - 無 CPU Affinity：Context Switch 開銷 ~1-10 μs
// - 有 CPU Affinity：減少 Cache Miss，降低 Context Switch 頻率
// - 在 NUMA 系統上：避免跨 NUMA Node 記憶體存取（延遲 ~100 ns → ~40 ns）

#include "thread_utils.h"

// 測試用函式
// 接受兩個整數相加，並可選擇是否睡眠
auto dummyFunction(int a, int b, bool sleep)
{
    std::cout << "dummyFunction(" << a << "," << b << ")" << std::endl;
    std::cout << "dummyFunction output=" << a + b << std::endl;

    if (sleep) {
        std::cout << "dummyFunction sleeping..." << std::endl;

        using namespace std::literals::chrono_literals;
        // 模擬長時間運算（5 秒）
        std::this_thread::sleep_for(5s);
    }

    std::cout << "dummyFunction done." << std::endl;
}

int main(int, char**)
{
    using namespace Common;

    // 建立執行緒 t1
    // 參數：
    // - core_id = -1：不綁定特定 CPU 核心（由 OS 調度）
    // - name = "dummyFunction1"：執行緒名稱
    // - function = dummyFunction：要執行的函式
    // - args = 12, 21, false：傳遞給函式的參數
    auto t1 = createAndStartThread(-1, "dummyFunction1", dummyFunction, 12, 21,
                                   false);

    // 建立執行緒 t2
    // ⚡ core_id = 1：綁定到 CPU 核心 1（提升效能）
    // ⚠️ 注意：若系統只有 1 個核心，綁定會失敗但不會崩潰
    auto t2 = createAndStartThread(1, "dummyFunction2", dummyFunction, 15, 51,
                                   true);

    // 等待兩個執行緒完成
    std::cout << "main waiting for threads to be done." << std::endl;
    t1->join();
    t2->join();
    std::cout << "main exiting." << std::endl;

    return 0;
}
