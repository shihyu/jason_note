#pragma once

// 低延遲模組：關鍵路徑避免鎖與分配。
// ⚡ 效能關鍵：固定佈局、批次處理。
// ⚠️ 注意：狀態一致性。

#include <iostream>
#include <atomic>
#include <thread>
#include <unistd.h>

#include <sys/syscall.h>

namespace Common
{
/**
 * setThreadCore() - 設定執行緒的 CPU 親和力（Thread Affinity）
 *
 * @param core_id CPU 核心 ID（0-based，例如 0 表示第一個核心）
 * @return 成功返回 true，失敗返回 false
 *
 * 功能：
 * - 將當前執行緒綁定（pin）到指定的 CPU 核心
 * - 防止作業系統將執行緒調度到其他核心
 *
 * 低延遲優化：
 * 1. **減少上下文切換（Context Switch）**：
 *    - 執行緒固定在一個核心上，減少核心間遷移
 *    - 避免 L1/L2 Cache 失效（Cache Invalidation）
 *
 * 2. **減少 Cache Miss**：
 *    - 資料和指令保留在同一個 CPU Cache 中
 *    - L1 Cache 命中率提高 → 延遲減少 10-50 ns
 *
 * 3. **預測性延遲**：
 *    - 固定核心 → 延遲變異降低
 *    - 適合實時系統和高頻交易
 *
 * 使用建議：
 * - 關鍵執行緒（交易引擎、市場數據處理）應綁定到專用核心
 * - 避免與系統執行緒共用核心（例如核心 0 通常處理中斷）
 * - 使用 `isolcpus` 核心參數隔離專用核心
 *
 * 注意事項：
 * - 需要 root 權限或 CAP_SYS_NICE 能力
 * - 過度使用會降低整體系統效能（CPU 利用率不平衡）
 * - 綁定錯誤的核心可能增加延遲（例如跨 NUMA 節點）
 *
 * 典型配置範例：
 * - 核心 0-1：系統和中斷處理
 * - 核心 2：交易引擎主執行緒
 * - 核心 3：市場數據接收執行緒
 * - 核心 4：訂單閘道執行緒
 * - 核心 5-7：其他輔助執行緒
 */
inline auto setThreadCore(int core_id) noexcept
{
    cpu_set_t cpuset;  // CPU 集合結構

    CPU_ZERO(&cpuset);            // 清空 CPU 集合
    CPU_SET(core_id, &cpuset);    // 設定目標 CPU 核心

    // 使用 pthread API 設定執行緒親和力
    // pthread_self() 取得當前執行緒 ID
    return (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t),
                                   &cpuset) == 0);
}

/**
 * createAndStartThread() - 建立並啟動執行緒（可選 CPU 綁定）
 *
 * @tparam T 函式物件類型（function, lambda, functor）
 * @tparam A 函式參數類型（可變參數模板）
 * @param core_id CPU 核心 ID（-1 表示不綁定，>= 0 表示綁定到指定核心）
 * @param name 執行緒名稱（用於日誌和除錯）
 * @param func 要在執行緒中執行的函式
 * @param args 傳遞給函式的參數（完美轉發）
 * @return 指向新建立執行緒的指標
 *
 * 功能：
 * 1. 建立新執行緒
 * 2. 若 core_id >= 0，設定 CPU 親和力（綁定到指定核心）
 * 3. 輸出日誌記錄執行緒啟動資訊
 * 4. 執行指定的函式
 *
 * 設計理念：
 * - 模板參數支援任意函式類型（Lambda、函式指標、Functor）
 * - 完美轉發（Perfect Forwarding）避免不必要的拷貝
 * - 返回原始指標（呼叫者負責生命週期管理）
 *
 * 使用範例：
 * ```cpp
 * // 綁定到核心 2，無參數函式
 * auto thread1 = createAndStartThread(2, "TradeEngine", []() {
     // ⚡ 關鍵路徑：函式內避免鎖/分配，保持快取局部性。
 *     while (true) { process(); }
 * });
 *
 * // 綁定到核心 3，帶參數函式
 * auto thread2 = createAndStartThread(3, "OrderGateway",
 *     &OrderGateway::run, gateway_ptr);
 *
 * // 不綁定核心（-1），讓 OS 調度
 * auto thread3 = createAndStartThread(-1, "Logger", log_func);
 * ```
 *
 * 低延遲考量：
 * - core_id >= 0：適合延遲敏感的執行緒（交易引擎、市場數據）
 * - core_id = -1：適合非關鍵執行緒（日誌、監控）
 * - 等待 1 秒：確保執行緒完全啟動並穩定
 *
 * 錯誤處理：
 * - 若 CPU 綁定失敗 → 輸出錯誤訊息並立即終止程式（exit）
 * - 嚴格的錯誤處理確保低延遲保證不被破壞
 *
 * 注意事項：
 * - 返回的指標需要呼叫者管理（通常在程式結束時 join 或 detach）
 * - Lambda 捕獲引用 [&] 要注意生命週期（避免 dangling reference）
 * - 1 秒等待會增加啟動時間（適合長期運行的執行緒）
 *
 * 記憶體管理：
 * - 使用 new 分配執行緒物件（堆上分配）
 * - 呼叫者需負責釋放（通常在程式退出時）
 * - 考慮使用 unique_ptr<thread> 自動管理生命週期
 */
template<typename T, typename... A>
inline auto createAndStartThread(int core_id, const std::string& name, T&& func,
                                 A&& ... args) noexcept
{
    // 建立新執行緒（Lambda 閉包捕獲所有參數）
    auto t = new std::thread([&]() {
        // 若 core_id >= 0，嘗試綁定到指定 CPU 核心
        if (core_id >= 0 && !setThreadCore(core_id)) {
            // 綁定失敗 → 輸出錯誤並終止程式
            std::cerr << "Failed to set core affinity for " << name << " " << pthread_self()
                      << " to " << core_id << std::endl;
            exit(EXIT_FAILURE);  // 嚴格錯誤處理（低延遲保證不可妥協）
        }

        // 記錄執行緒啟動資訊（包含執行緒 ID 和綁定的核心）
        std::cerr << "Set core affinity for " << name << " " << pthread_self() << " to "
                  << core_id << std::endl;

        // 執行指定的函式（完美轉發參數）
        // std::forward 保持參數的值類別（左值/右值）
        std::forward<T>(func)((std::forward<A>(args))...);
    });

    // 等待 1 秒，確保執行緒完全啟動並穩定
    // 避免主執行緒在子執行緒初始化完成前繼續執行
    using namespace std::literals::chrono_literals;
    std::this_thread::sleep_for(1s);

    // 返回執行緒指標（呼叫者負責生命週期管理）
    return t;
}
}
