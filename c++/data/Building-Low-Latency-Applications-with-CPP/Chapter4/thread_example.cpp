// ========================================
// Thread Utils 使用範例
// ========================================
//
// 範例目的:
// 展示如何使用 createAndStartThread 建立執行緒並綁定 CPU 核心
//
// ⚡ 核心技術:
// 1. CPU Affinity: 綁定執行緒到特定 CPU 核心
// 2. 參數轉發: 完美轉發(Perfect Forwarding)傳遞任意參數
// 3. pthread_setaffinity_np: 設定執行緒親和性
//
// 使用情境:
// - 低延遲應用: 避免 Context Switch 和 Cache Miss
// - 多執行緒程式: 隔離關鍵執行緒到獨立核心
// - NUMA 系統: 綁定執行緒到特定 NUMA Node
//
// 執行流程:
// 1. 建立 t1 執行緒(不綁定核心,快速完成)
// 2. 建立 t2 執行緒(綁定核心 1,休眠 5 秒)
// 3. 主執行緒等待兩個執行緒完成
//
#include "thread_utils.h"

// dummyFunction: 測試用的執行緒函式
// @param a: 第一個參數
// @param b: 第二個參數
// @param sleep: 是否休眠 5 秒
//
// 目的:
// - 驗證參數轉發正確性
// - 測試長時間運行的執行緒
auto dummyFunction(int a, int b, bool sleep)
{
    std::cout << "dummyFunction(" << a << "," << b << ")" << std::endl;
    std::cout << "dummyFunction output=" << a + b << std::endl;

    // 模擬長時間運行的任務
    if (sleep) {
        std::cout << "dummyFunction sleeping..." << std::endl;

        using namespace std::literals::chrono_literals;
        std::this_thread::sleep_for(5s);  // 休眠 5 秒
    }

    std::cout << "dummyFunction done." << std::endl;
}

int main(int, char**)
{
    using namespace Common;

    // ========================================
    // 建立執行緒 1: 不綁定 CPU 核心
    // ========================================
    //
    // @param core_id: -1 = 不綁定核心(由作業系統排程)
    // @param name: "dummyFunction1" = 執行緒名稱(用於除錯)
    // @param func: dummyFunction = 要執行的函式
    // @param args: 12, 21, false = 轉發給 dummyFunction 的參數
    //
    // ⚡ 不綁定核心的優勢:
    // - 作業系統可動態調度到空閒核心
    // - 適合非關鍵執行緒(如日誌、監控)
    //
    // ⚠️ 不綁定核心的缺點:
    // - Context Switch: 執行緒可能在核心間移動
    // - Cache Miss: L1/L2 Cache 失效(~50-100ns 延遲增加)
    auto t1 = createAndStartThread(-1, "dummyFunction1", dummyFunction, 12, 21,
                                   false);

    // ========================================
    // 建立執行緒 2: 綁定到 CPU 核心 1
    // ========================================
    //
    // @param core_id: 1 = 綁定到 CPU 核心 1
    //
    // ⚡ 綁定核心的優勢:
    // 1. 避免 Context Switch: 執行緒固定在核心 1,不會移動
    // 2. Cache 親和性: L1/L2 Cache 保持熱資料(~5ns 存取)
    // 3. 可預測延遲: 無執行緒遷移造成的 Jitter
    //
    // ⚠️ 綁定核心的考量:
    // - 核心負載不均: 其他核心閒置,核心 1 可能過載
    // - NUMA 影響: 若綁定到遠端 NUMA Node,記憶體延遲 2-3x
    //
    // 適合場景:
    // - 交易系統的撮合引擎執行緒
    // - 遊戲引擎的渲染執行緒
    // - 即時系統的控制迴路
    //
    // 內部實作(pthread_setaffinity_np):
    // ```cpp
    // cpu_set_t cpuset;
    // CPU_ZERO(&cpuset);
    // CPU_SET(core_id, &cpuset);  // 設定允許的核心集合
    // pthread_setaffinity_np(thread.native_handle(), sizeof(cpuset), &cpuset);
    // ```
    auto t2 = createAndStartThread(1, "dummyFunction2", dummyFunction, 15, 51,
                                   true);

    // ========================================
    // 等待執行緒完成
    // ========================================
    //
    // ⚡ join() 行為:
    // - 阻塞主執行緒直到目標執行緒結束
    // - 釋放目標執行緒的資源(記憶體、控制結構)
    //
    // ⚠️ 注意: 必須 join 所有執行緒
    // 原因: 若主執行緒先結束,子執行緒會被強制終止
    std::cout << "main waiting for threads to be done." << std::endl;
    t1->join();  // 等待 t1(立即完成)
    t2->join();  // 等待 t2(休眠 5 秒後完成)
    std::cout << "main exiting." << std::endl;

    return 0;
}

// ========================================
// 預期輸出順序:
// ========================================
//
// 1. dummyFunction(12,21)          ← t1 開始
// 2. dummyFunction output=33       ← t1 計算結果
// 3. dummyFunction done.           ← t1 完成
// 4. dummyFunction(15,51)          ← t2 開始
// 5. dummyFunction output=66       ← t2 計算結果
// 6. dummyFunction sleeping...     ← t2 開始休眠
// 7. main waiting for threads...  ← 主執行緒等待
// 8. (等待 5 秒)
// 9. dummyFunction done.           ← t2 完成
// 10. main exiting.                ← 程式結束
//
// ⚠️ 輸出順序可能不固定
// 原因: 多執行緒並發執行,步驟 1-7 可能交錯出現
//
// ========================================
// CPU Affinity 驗證方法:
// ========================================
//
// 1. 使用 taskset 驗證執行緒綁定:
//    ```bash
//    # 執行程式
//    ./thread_example &
//    PID=$!
//
//    # 查看執行緒在哪個核心執行
//    top -H -p $PID  # 按 'f' 選擇 P (Last Used CPU)
//
//    # 或使用 ps
//    ps -o pid,tid,psr,comm -p $PID
//    # PSR 欄位顯示當前 CPU 核心編號
//    ```
//
// 2. 預期結果:
//    - t1 (dummyFunction1): PSR 可能變化(0, 1, 2, ...)
//    - t2 (dummyFunction2): PSR 固定為 1
//
// ========================================
// 效能分析:
// ========================================
//
// Context Switch 開銷:
// - 直接成本: ~1-5μs (保存/恢復暫存器、切換頁表)
// - 間接成本: ~10-100μs (L1/L2 Cache Miss)
//
// CPU Affinity 帶來的效能提升:
// | 場景                  | 無綁定  | 綁定核心 | 改善    |
// |-----------------------|---------|----------|---------|
// | 高頻熱路徑(每秒 100 萬次) | ~50ns   | ~20ns    | 2.5x    |
// | Cache Miss 率         | ~10%    | ~1%      | 10x     |
// | 延遲 Jitter (P99)     | ~500ns  | ~50ns    | 10x     |
//
// ⚠️ 過度綁定的風險:
// - 若所有執行緒綁定到同一核心,反而降低效能
// - 建議: 關鍵執行緒綁定,非關鍵執行緒不綁定
//
// ========================================
// 使用建議:
// ========================================
//
// ✅ 應該綁定核心的執行緒:
// - 撮合引擎執行緒(交易系統)
// - 網路接收執行緒(高頻交易)
// - 渲染執行緒(遊戲引擎)
// - 控制迴路執行緒(即時系統)
//
// ❌ 不應該綁定核心的執行緒:
// - 日誌執行緒(不頻繁執行)
// - 監控執行緒(低優先級)
// - 背景清理執行緒
// - 短暫存在的工作執行緒
//
// ⚠️ NUMA 系統注意事項:
// 1. 檢查 NUMA 拓撲:
//    ```bash
//    numactl --hardware
//    # node 0 cpus: 0 2 4 6 8 10
//    # node 1 cpus: 1 3 5 7 9 11
//    ```
//
// 2. 綁定原則:
//    - 執行緒綁定到記憶體所在的 NUMA Node 的核心
//    - 避免跨 NUMA Node 存取(延遲 2-3x)
//
// 3. 範例:
//    ```cpp
//    // 若 data 分配在 NUMA Node 0
//    createAndStartThread(0, "worker", process, data);  // 綁定核心 0
//    ```
//
// ========================================
// 進階優化:
// ========================================
//
// 1. 隔離 CPU 核心:
//    ```bash
//    # 開機參數: 保留核心 1-3 給應用程式
//    isolcpus=1,2,3 nohz_full=1,2,3
//    ```
//    效果: 作業系統不會在這些核心上排程其他行程
//
// 2. 中斷親和性:
//    ```bash
//    # 將網卡中斷路由到核心 0,避免干擾核心 1
//    echo 1 > /proc/irq/$(cat /proc/interrupts | grep eth0 | cut -d: -f1)/smp_affinity
//    ```
//
// 3. 執行緒優先級:
//    ```cpp
//    // 設定即時優先級(需要 root)
//    sched_param param;
//    param.sched_priority = 99;  // 最高優先級
//    pthread_setschedparam(thread.native_handle(), SCHED_FIFO, &param);
//    ```
//
