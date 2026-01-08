#pragma once

#include <iostream>
#include <atomic>
#include <thread>
#include <unistd.h>

#include <sys/syscall.h>

namespace Common
{
// 設定執行緒的 CPU 親和性 (CPU Affinity)
// @param core_id: 目標 CPU 核心 ID
//
// ⚡ 效能關鍵：
// 1. 防止執行緒在核心間遷移 (Migration)，保留 L1/L2 Cache 熱度
// 2. 隔離關鍵執行緒 (如撮合引擎)，避免與作業系統或其他雜務爭搶資源
inline auto setThreadCore(int core_id) noexcept
{
    cpu_set_t cpuset;

    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);

    // pthread_setaffinity_np 是 Linux 特有 API (Non-Portable)
    return (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t),
                                   &cpuset) == 0);
}

// 建立並啟動執行緒，同時設定 CPU 親和性
// @param core_id: 綁定的 CPU 核心 ID (-1 表示不綁定)
// @param name: 執行緒名稱 (用於日誌/除錯)
// @param func: 執行緒函式
// @param args: 函式參數
template<typename T, typename... A>
inline auto createAndStartThread(int core_id, const std::string& name, T&& func,
                                 A&& ... args) noexcept
{
    auto t = new std::thread([&]() {
        if (core_id >= 0 && !setThreadCore(core_id)) {
            std::cerr << "Failed to set core affinity for " << name << " " << pthread_self()
                      << " to " << core_id << std::endl;
            exit(EXIT_FAILURE);
        }

        std::cerr << "Set core affinity for " << name << " " << pthread_self() << " to "
                  << core_id << std::endl;

        std::forward<T>(func)((std::forward<A>(args))...);
    });

    // 讓執行緒有時間啟動與初始化
    using namespace std::literals::chrono_literals;
    std::this_thread::sleep_for(1s);

    return t;
}
}
