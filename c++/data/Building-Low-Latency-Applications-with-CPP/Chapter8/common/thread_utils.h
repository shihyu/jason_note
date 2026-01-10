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
//
// ⚠️ NUMA (Non-Uniform Memory Access) 架構注意事項：
// - 確保綁定的 CPU 核心與記憶體節點在同一個 NUMA node
// - 跨 NUMA 存取延遲可能增加 100-300ns（相比本地存取的 50-100ns）
// - 查看 NUMA 拓撲：`numactl --hardware` 或 `lscpu`
// - 範例：
//   ```bash
//   # 查看 NUMA 節點配置
//   numactl --hardware
//   # available: 2 nodes (0-1)
//   # node 0 cpus: 0 2 4 6 8 10 12 14
//   # node 1 cpus: 1 3 5 7 9 11 13 15
//   ```
// - 建議：使用 `numactl --membind=0 --cpunodebind=0 ./your_app` 綁定記憶體與 CPU
//
// 🔧 生產環境 CPU 隔離建議：
// 1. 使用 isolcpus 內核參數隔離關鍵核心：
//    - 編輯 /etc/default/grub：
//      `GRUB_CMDLINE_LINUX="isolcpus=2-7 nohz_full=2-7 rcu_nocbs=2-7"`
//    - 更新 grub：`sudo update-grub && sudo reboot`
//    - 效果：核心 2-7 不會被 Linux 排程器分配一般任務
//
// 2. 停用不必要的系統服務（減少 CPU 中斷）：
//    - irqbalance（中斷平衡服務）
//    - 定時任務（cron、systemd-timers）
//
// 3. 停用省電功能（避免頻率縮放）：
//    - `echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`
//
// ⚠️ 超執行緒 (Hyper-Threading / SMT) 警告：
// - Intel/AMD CPU 的物理核心共享 L1/L2 Cache
// - 範例拓撲（16 邏輯核心，8 物理核心）：
//   - 物理核心 0：邏輯核心 0, 8
//   - 物理核心 1：邏輯核心 1, 9
//   - ...依此類推
// - 查看拓撲：`lscpu -e` 或 `cat /sys/devices/system/cpu/cpu0/topology/thread_siblings_list`
//
// ❌ 錯誤做法：將兩個關鍵執行緒綁定到同一物理核心
//   ```cpp
//   setThreadCore(0);  // 撮合引擎執行緒
//   setThreadCore(8);  // 市場數據執行緒（與核心 0 共享 L1/L2）
//   ```
//   - 結果：兩個執行緒爭搶 Cache，效能下降 30-50%
//
// ✅ 正確做法：綁定到不同物理核心
//   ```cpp
//   setThreadCore(0);  // 撮合引擎 -> 物理核心 0
//   setThreadCore(1);  // 市場數據 -> 物理核心 1
//   ```
//
// 🔧 生產環境建議：完全停用超執行緒
// - BIOS 設定中關閉 Hyper-Threading / SMT
// - 或使用內核參數：`nosmt=force`
// - 理由：避免非確定性效能變異（兩個邏輯核心的競爭不可預測）
//
// ⚠️ 作業系統排程影響：
// - 親和性設定後，Linux 排程器不會自動平衡負載
// - 若綁定的核心過載，也不會將任務遷移到閒置核心
// - 需要手動規劃執行緒分配策略
//
// 📊 效能數據參考：
// - Cache 熱度保持：延遲減少 20-40% (相比頻繁遷移)
// - 跨 NUMA 存取懲罰：+100-300ns per access
// - 超執行緒競爭懲罰：吞吐量下降 30-50%
// - CPU 隔離效果：99 百分位延遲降低 50-80%
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
