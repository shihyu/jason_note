#pragma once

#include "common/types.h"
#include "common/thread_utils.h"
#include "common/lf_queue.h"
#include "common/macros.h"
#include "common/mcast_socket.h"
#include "common/mem_pool.h"
#include "common/logging.h"

#include "market_data/market_update.h"
#include "matcher/me_order.h"

using namespace Common;

namespace Exchange
{
// SnapshotSynthesizer: 快照合成器
//
// 設計原理:
// 1. 狀態維護: 維護完整訂單簿狀態副本（透過處理增量更新）
// 2. 定期發布: 每60秒發布一次完整快照
// 3. 容錯機制: 快照供客戶端恢復丟失的增量更新
//
// 資料流向:
// MarketDataPublisher → MDPMarketUpdateLFQueue → SnapshotSynthesizer
//                                ↓                         ↓
//                      addToSnapshot()            publishSnapshot()
//                      (狀態更新)                  (UDP Multicast)
//                           ↓                           ↓
//                  ticker_orders_                 市場參與者
//                  (訂單簿狀態)                   (快照訂閱者)
//
// ⚡ 快照用途:
// - 新訂閱者加入: 快速取得當前市場狀態
// - 丟包恢復: 重建正確的訂單簿狀態
// - 狀態校驗: 驗證本地訂單簿是否正確
//
// 使用場景: 交易所行情發布系統的容錯機制
class SnapshotSynthesizer
{
public:
    SnapshotSynthesizer(MDPMarketUpdateLFQueue* market_updates,
                        const std::string& iface,
                        const std::string& snapshot_ip, int snapshot_port);

    ~SnapshotSynthesizer();

    // 啟動快照合成器執行緒
    auto start() -> void;

    // 停止快照合成器執行緒
    auto stop() -> void;

    // 處理增量更新,維護訂單簿狀態
    // @param market_update: 帶序列號的市場數據更新
    //
    // ⚡ 狀態轉換:
    // - ADD: 新增訂單到 ticker_orders_
    // - MODIFY: 更新訂單的 qty/price
    // - CANCEL: 移除訂單並歸還記憶體池
    //
    // ⚠️ 斷言檢查:
    // - ADD: 訂單必須不存在
    // - MODIFY/CANCEL: 訂單必須存在
    // - 序列號必須連續（檢測丟包）
    auto addToSnapshot(const MDPMarketUpdate* market_update);

    // 發布完整快照
    //
    // ⚡ 快照格式:
    // 1. SNAPSHOT_START (seq=last_inc_seq_num_)
    // 2. CLEAR (ticker_id=0)
    // 3. ADD (所有有效訂單, ticker_id=0)
    // 4. CLEAR (ticker_id=1)
    // 5. ADD (所有有效訂單, ticker_id=1)
    // ...
    // N. SNAPSHOT_END (seq=last_inc_seq_num_)
    //
    // ⚠️ 注意: 快照包含的序列號表示此快照涵蓋 ≤ seq 的所有更新
    auto publishSnapshot();

    // 主事件迴圈（在專用執行緒中執行）
    // 職責:
    // 1. 處理增量更新（維護訂單簿狀態）
    // 2. 定期發布快照（每60秒）
    auto run() -> void;

    // Deleted default, copy & move constructors and assignment-operators.
    SnapshotSynthesizer() = delete;

    SnapshotSynthesizer(const SnapshotSynthesizer&) = delete;

    SnapshotSynthesizer(const SnapshotSynthesizer&&) = delete;

    SnapshotSynthesizer& operator=(const SnapshotSynthesizer&) = delete;

    SnapshotSynthesizer& operator=(const SnapshotSynthesizer&&) = delete;

private:
    // Lock-Free Queue 通訊通道
    // ⚡ SPSC: MarketDataPublisher (Producer) → SnapshotSynthesizer (Consumer)
    MDPMarketUpdateLFQueue* snapshot_md_updates_ = nullptr;

    Logger logger_;  // 日誌記錄器

    // 執行狀態控制
    // ⚠️ volatile: 防止編譯器優化,確保主執行緒能正確停止事件迴圈
    volatile bool run_ = false;

    std::string time_str_;  // 時間字串緩衝區（重複使用,避免記憶體分配）

    // UDP Multicast Socket
    // ⚡ 用途: 發送完整快照（Snapshots）
    McastSocket snapshot_socket_;

    // 訂單簿狀態副本: ticker_orders_[ticker_id][order_id] → MEMarketUpdate*
    // ⚡ 設計原理:
    // - 二維陣列索引: 快速定位訂單 O(1)
    // - nullptr 表示訂單不存在
    // - 配合 Memory Pool 管理訂單物件生命週期
    //
    // 空間複雜度: O(ME_MAX_TICKERS × ME_MAX_ORDER_IDS) 指標
    // 實際佔用: 8 tickers × 1M orders × 8 bytes = 64 MB
    std::array<std::array<MEMarketUpdate*, ME_MAX_ORDER_IDS>, ME_MAX_TICKERS>
    ticker_orders_;

    // 最後處理的增量更新序列號
    // ⚡ 用途:
    // - 檢測序列號連續性（發現丟包）
    // - 快照的序列號標記（表示涵蓋 ≤ seq 的所有更新）
    size_t last_inc_seq_num_ = 0;

    // 最後快照發布時間（奈秒）
    // ⚡ 用途: 定時發布機制（每60秒發布一次）
    Nanos last_snapshot_time_ = 0;

    // 訂單物件記憶體池
    // ⚡ 容量: ME_MAX_ORDER_IDS (1,048,576 個訂單)
    // 用途: 預先配置所有訂單記憶體,零碎片化
    MemPool<MEMarketUpdate> order_pool_;
};
}
}
