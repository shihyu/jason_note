#pragma once

#include <iostream>
#include <atomic>
#include <thread>
#include <unistd.h>

#include <sys/syscall.h>

namespace Common
{
// setThreadCore: 設定 CPU 親和性 (CPU Affinity)
// 
// ⚡ 優化原理:
// 1. 固定核心: 防止作業系統將執行緒遷移到其他核心 (Thread Migration)
// 2. 快取熱度: 保持 L1/L2 快取數據的一致性，減少快取失效 (Cache Miss)
// 3. 減少抖動: 避免作業系統排程導致的 context switch 延遲
inline auto setThreadCore(int core_id) noexcept
{
    cpu_set_t cpuset;

    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);

    return (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t),
                                   &cpuset) == 0);
}

// createAndStartThread: 建立並啟動綁定核心的執行緒
//
// 流程:
// 1. 建立 std::thread 實例
// 2. 在新執行緒中呼叫 setThreadCore() 綁定核心
// 3. 執行用戶指定的函式 (func)
// 4. 主執行緒等待 1 秒確保初始化完成
template<typename T, typename... A>
inline auto createAndStartThread(int core_id, const std::string& name, T&& func,
                                 A&& ... args) noexcept
{
    auto t = new std::thread([&]() {
        // 如果指定 core_id >= 0，則進行核心綁定
        if (core_id >= 0 && !setThreadCore(core_id)) {
            std::cerr << "Failed to set core affinity for " << name << " " << pthread_self()
                      << " to " << core_id << std::endl;
            exit(EXIT_FAILURE);
        }

        std::cerr << "Set core affinity for " << name << " " << pthread_self() << " to "
                  << core_id << std::endl;

        // ⚡ 完美轉發參數並執行
        std::forward<T>(func)((std::forward<A>(args))...);
    });

    // ⚠️ 注意: 等待 1 秒是為了讓系統完成執行緒排程與核心綁定
    using namespace std::literals::chrono_literals;
    std::this_thread::sleep_for(1s);

    return t;
}
}
