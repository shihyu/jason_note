// snapshot_synthesizer.cpp: 快照合成器實作
//
// 職責：
// - 維護完整的訂單簿副本（Order Book Replica）
// - 週期性發布市場快照（Snapshot）供客戶端重建狀態
// - 處理增量更新（Incremental Updates），保持副本同步
//
// 使用場景：
// 1. 新客戶端連線：取得最新快照後，再訂閱增量更新
// 2. 封包遺失恢復：客戶端偵測到序列號跳號，重新請求快照
// 3. 定期校驗：比對本地訂單簿與快照的一致性
//
// 快照協議（Snapshot Protocol）：
// ┌─────────────────┐
// │ SNAPSHOT_START  │ (含 last_inc_seq_num_)
// └────────┬────────┘
//          ▼
// ┌─────────────────┐
// │ CLEAR (Ticker 0)│ 清空該商品
// ├─────────────────┤
// │ ADD (Order 1)   │ 發送所有訂單
// │ ADD (Order 2)   │
// │ ...             │
// ├─────────────────┤
// │ CLEAR (Ticker 1)│
// │ ADD (...)       │
// └────────┬────────┘
//          ▼
// ┌─────────────────┐
// │ SNAPSHOT_END    │
// └─────────────────┘
//
// ⚡ 低延遲設計：
// - 獨立執行緒：不阻塞主增量發布路徑
// - Memory Pool：預配置訂單物件，避免動態記憶體配置
// - Lock-Free Queue：從 MarketDataPublisher 接收更新
//
// ⚠️ 狀態一致性：
// - 序列號檢查：確保沒有遺漏增量更新
// - ASSERT 驗證：ADD/MODIFY/CANCEL 操作必須符合狀態邏輯

#include "snapshot_synthesizer.h"

namespace Exchange
{
// SnapshotSynthesizer 建構子
//
// 初始化流程：
// 1. 關聯輸入佇列：從 MarketDataPublisher 接收增量更新（指標共享）
// 2. 創建日誌系統：獨立日誌檔案（exchange_snapshot_synthesizer.log）
// 3. 初始化快照 Socket：設定 UDP Multicast 通道（發送快照）
// 4. 創建訂單記憶體池：預配置 ME_MAX_ORDER_IDS 個訂單物件
// 5. 初始化訂單簿副本：所有商品的訂單陣列初始化為 nullptr
//
// 資料結構設計：
// - ticker_orders_：二維陣列 [ticker_id][order_id] -> MEMarketUpdate*
// - order_pool_：記憶體池，管理 MEMarketUpdate 物件生命週期
// - snapshot_md_updates_：Lock-Free Queue，接收增量更新
//
// ⚡ 效能優化：
// - Memory Pool：避免 new/delete 開銷（O(1) 配置/釋放）
// - 預配置陣列：ticker_orders_ 使用 std::array，無動態配置
// - 非監聽模式：snapshot_socket_ 只發送，不接收（is_listening=false）
//
// @param market_updates: 來自 MarketDataPublisher 的增量更新佇列
// @param iface: 網路介面名稱（例如 "eth0"）
// @param snapshot_ip: 快照服務 Multicast 群組 IP
// @param snapshot_port: 快照服務 Multicast Port
SnapshotSynthesizer::SnapshotSynthesizer(MDPMarketUpdateLFQueue* market_updates,
        const std::string& iface,
        const std::string& snapshot_ip, int snapshot_port)
    : snapshot_md_updates_(market_updates),               // 外部佇列（指標共享）
      logger_("exchange_snapshot_synthesizer.log"),       // 獨立日誌檔案
      snapshot_socket_(logger_),                          // UDP Multicast Socket
      order_pool_(ME_MAX_ORDER_IDS)                       // 訂單記憶體池（預配置）
{
    // 初始化快照 Socket（UDP Multicast）
    // ⚡ 非監聽模式（is_listening=false）：只發送快照，不接收請求
    // ⚠️ 失敗時中止程式：ASSERT 確保網路通道正常
    ASSERT(snapshot_socket_.init(snapshot_ip, iface,
                                 snapshot_port, /*is_listening*/ false) >= 0,
           "Unable to create snapshot mcast socket. error:" + std::string(std::strerror(
                       errno)));

    // 初始化所有商品的訂單陣列（全部設為 nullptr）
    // ⚡ 迴圈展開：編譯器可能會優化成 memset
    // 📊 記憶體使用：ME_MAX_TICKERS × ME_MAX_ORDER_IDS × sizeof(MEMarketUpdate*)
    for (auto& orders : ticker_orders_) {
        orders.fill(nullptr);
    }
}

// 解構子：停止執行緒並清理資源
//
// 清理流程：
// 1. 呼叫 stop() 設定 run_ = false
// 2. 等待執行緒結束（由 createAndStartThread 管理）
// 3. Memory Pool 自動釋放（order_pool_ 的解構子處理）
//
// ⚠️ 注意：
// - 必須先停止執行緒，再釋放資源
// - ticker_orders_ 中的指標會被 order_pool_ 自動回收
SnapshotSynthesizer::~SnapshotSynthesizer()
{
    stop();  // 設定 run_ = false，通知執行緒停止
}

// start: 啟動快照合成器執行緒
//
// 執行緒配置：
// - CPU 親和性：-1（不綁定特定核心，由 OS 調度）
// - 執行緒名稱："Exchange/SnapshotSynthesizer"（用於除錯）
// - 執行函式：run() 主事件迴圈（Lambda 捕獲 this 指標）
//
// ⚡ 設計考量：
// - 獨立執行緒：不阻塞主增量發布路徑（MarketDataPublisher）
// - 低優先度：快照發布不如增量更新緊急
// - 週期性任務：每 60 秒發布一次快照
//
// ⚠️ 失敗處理：
// - ASSERT 確保執行緒創建成功
// - 執行緒創建失敗會中止程式
void SnapshotSynthesizer::start()
{
    run_ = true;  // 設定執行標誌

    // 創建並啟動執行緒
    // - CPU 親和性：-1（不綁定）
    // - Lambda：捕獲 this，呼叫 run() 方法
    ASSERT(Common::createAndStartThread(-1,
    "Exchange/SnapshotSynthesizer", [this]() {
        run();
    }) != nullptr,
    "Failed to start SnapshotSynthesizer thread.");
}

// stop: 停止快照合成器執行緒
//
// 停止機制：
// - 設定 run_ = false
// - run() 迴圈會在下一次檢查時退出
// - 執行緒自然結束（非強制終止）
//
// ⚡ 優雅停止：
// - 不使用 pthread_cancel（避免資源洩漏）
// - 等待當前快照發布完成
// - 確保日誌完整性
void SnapshotSynthesizer::stop()
{
    run_ = false;  // 清除執行標誌，通知執行緒停止
}

/**
 * addToSnapshot() - 處理增量更新並維護訂單簿狀態
 *
 * @param market_update 帶有序列號的市場數據更新 (Incremental Update)
 *
 * 職責：
 * 1. 根據增量更新 (ADD/MODIFY/CANCEL) 修改本地訂單簿副本 (ticker_orders_)
 * 2. 驗證序列號連續性 (Sequence Number Check)
 *
 * 處理邏輯：
 * - ADD: 分配新訂單並存入 ticker_orders_
 * - MODIFY: 更新現有訂單的數量和價格
 * - CANCEL: 釋放訂單並從 ticker_orders_ 移除
 *
 * 安全性檢查：
 * - ASSERT(order == nullptr/nullptr): 確保操作狀態正確
 * - ASSERT(seq_num): 確保沒有漏掉任何增量更新，保證狀態一致性
 */
auto SnapshotSynthesizer::addToSnapshot(const MDPMarketUpdate* market_update)
{
    const auto& me_market_update = market_update->me_market_update_;
    auto* orders = &ticker_orders_.at(me_market_update.ticker_id_);

    switch (me_market_update.type_) {
    case MarketUpdateType::ADD: {
            auto order = orders->at(me_market_update.order_id_);
            ASSERT(order == nullptr,
                   "Received:" + me_market_update.toString() + " but order already exists:" +
                   (order ? order->toString() : ""));
            orders->at(me_market_update.order_id_) = order_pool_.allocate(me_market_update);
        }
        break;

    case MarketUpdateType::MODIFY: {
            auto order = orders->at(me_market_update.order_id_);
            ASSERT(order != nullptr,
                   "Received:" + me_market_update.toString() + " but order does not exist.");
            ASSERT(order->order_id_ == me_market_update.order_id_,
                   "Expecting existing order to match new one.");
            ASSERT(order->side_ == me_market_update.side_,
                   "Expecting existing order to match new one.");

            order->qty_ = me_market_update.qty_;
            order->price_ = me_market_update.price_;
        }
        break;

    case MarketUpdateType::CANCEL: {
            auto order = orders->at(me_market_update.order_id_);
            ASSERT(order != nullptr,
                   "Received:" + me_market_update.toString() + " but order does not exist.");
            ASSERT(order->order_id_ == me_market_update.order_id_,
                   "Expecting existing order to match new one.");
            ASSERT(order->side_ == me_market_update.side_,
                   "Expecting existing order to match new one.");

            order_pool_.deallocate(order);
            orders->at(me_market_update.order_id_) = nullptr;
        }
        break;

    case MarketUpdateType::SNAPSHOT_START:
    case MarketUpdateType::CLEAR:
    case MarketUpdateType::SNAPSHOT_END:
    case MarketUpdateType::TRADE:
    case MarketUpdateType::INVALID:
        break;
    }

    ASSERT(market_update->seq_num_ == last_inc_seq_num_ + 1,
           "Expected incremental seq_nums to increase.");
    last_inc_seq_num_ = market_update->seq_num_;
}

/**
 * publishSnapshot() - 發布完整快照
 *
 * 頻率：每 60 秒發布一次
 * 目的：讓新加入的客戶端或丟包的客戶端重建訂單簿狀態
 *
 * 協議流程：
 * 1. SNAPSHOT_START: 包含 last_inc_seq_num_，告知此快照對應哪個增量序列號
 * 2. 對每個商品 (Ticker):
 *    a. CLEAR: 通知客戶端清空該商品的本地訂單簿
 *    b. ADDs: 發送該商品所有有效訂單 (Active Orders)
 * 3. SNAPSHOT_END: 標記快照結束
 *
 * 效能：
 * - 使用 UDP Multicast (McastSocket)
 * - 批次發送 (sendAndRecv 在 McastSocket 內部處理緩衝區)
 */
auto SnapshotSynthesizer::publishSnapshot()
{
    size_t snapshot_size = 0;

    // 1. 發送 SNAPSHOT_START
    const MDPMarketUpdate start_market_update{snapshot_size++, {MarketUpdateType::SNAPSHOT_START, last_inc_seq_num_}};
    logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                getCurrentTimeStr(&time_str_), start_market_update.toString());
    snapshot_socket_.send(&start_market_update, sizeof(MDPMarketUpdate));

    for (size_t ticker_id = 0; ticker_id < ticker_orders_.size(); ++ticker_id) {
        const auto& orders = ticker_orders_.at(ticker_id);

        // 2a. 發送 CLEAR (清空該商品)
        MEMarketUpdate me_market_update;
        me_market_update.type_ = MarketUpdateType::CLEAR;
        me_market_update.ticker_id_ = ticker_id;

        const MDPMarketUpdate clear_market_update{snapshot_size++, me_market_update};
        logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                    getCurrentTimeStr(&time_str_), clear_market_update.toString());
        snapshot_socket_.send(&clear_market_update, sizeof(MDPMarketUpdate));

        // 2b. 發送所有現存訂單 (ADD)
        for (const auto order : orders) {
            if (order) {
                const MDPMarketUpdate market_update{snapshot_size++, *order};
                logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                            getCurrentTimeStr(&time_str_), market_update.toString());
                snapshot_socket_.send(&market_update, sizeof(MDPMarketUpdate));
                snapshot_socket_.sendAndRecv();
            }
        }
    }

    // 3. 發送 SNAPSHOT_END
    const MDPMarketUpdate end_market_update{snapshot_size++, {MarketUpdateType::SNAPSHOT_END, last_inc_seq_num_}};
    logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                getCurrentTimeStr(&time_str_), end_market_update.toString());
    snapshot_socket_.send(&end_market_update, sizeof(MDPMarketUpdate));
    snapshot_socket_.sendAndRecv();

    logger_.log("%:% %() % Published snapshot of % orders.\n", __FILE__, __LINE__,
                __FUNCTION__, getCurrentTimeStr(&time_str_), snapshot_size - 1);
}

// run: 主事件迴圈 - 快照合成核心邏輯
//
// 執行流程：
// 1. 從 Lock-Free Queue 讀取增量更新（批次處理）
// 2. 呼叫 addToSnapshot() 更新本地訂單簿副本
// 3. 每 60 秒檢查並發布完整快照
//
// 雙重職責：
// ┌────────────────────────────┐
// │ 持續處理增量更新           │ → addToSnapshot()
// │ (維護訂單簿副本)          │
// └────────────────────────────┘
//              ↓
// ┌────────────────────────────┐
// │ 週期性發布快照             │ → publishSnapshot()
// │ (每 60 秒)                 │
// └────────────────────────────┘
//
// ⚡ 效能設計：
// - Busy-Wait 迴圈：while(run_) 持續輪詢（低延遲）
// - 批次處理：for 迴圈一次處理多個增量更新
// - 時間檢查：使用 getCurrentNanos() 高精度計時
// - Lock-Free Queue：無鎖讀取，避免執行緒同步
//
// ⚠️ 注意事項：
// - 獨立執行緒：在 start() 中創建
// - 優雅停止：run_ = false 時自然退出
// - 時間間隔：60 秒（可調整為配置參數）
void SnapshotSynthesizer::run()
{
    // 記錄啟動時間（除錯用）
    logger_.log("%:% %() %\n", __FILE__, __LINE__, __FUNCTION__,
                getCurrentTimeStr(&time_str_));

    // 主事件迴圈：Busy-Wait 模式（持續輪詢佇列）
    // ⚡ 與 MarketDataPublisher 相同的迴圈模式
    while (run_) {
        // === 任務 1：處理增量更新（批次處理）===
        // ⚡ 批次處理迴圈：一次處理佇列中的所有更新
        for (auto market_update = snapshot_md_updates_->getNextToRead();
             snapshot_md_updates_->size() &&
             market_update; market_update = snapshot_md_updates_->getNextToRead()) {

            // 記錄處理的增量更新內容（除錯用）
            logger_.log("%:% %() % Processing %\n", __FILE__, __LINE__, __FUNCTION__,
                        getCurrentTimeStr(&time_str_),
                        market_update->toString().c_str());

            // 更新本地訂單簿副本
            // - 處理 ADD/MODIFY/CANCEL 操作
            // - 驗證序列號連續性
            // - 維護 ticker_orders_ 狀態
            addToSnapshot(market_update);

            // 更新讀取索引（標記已處理）
            // ⚡ Lock-Free 操作：無需鎖定，只更新原子索引
            snapshot_md_updates_->updateReadIndex();
        }

        // === 任務 2：週期性發布快照（每 60 秒）===
        // ⚡ 時間檢查：getCurrentNanos() 提供奈秒級精度
        // 📊 NANOS_TO_SECS = 1,000,000,000（1 秒 = 10^9 奈秒）
        if (getCurrentNanos() - last_snapshot_time_ > 60 * NANOS_TO_SECS) {
            // 更新上次快照時間
            last_snapshot_time_ = getCurrentNanos();

            // 發布完整市場快照
            // - 發送 SNAPSHOT_START
            // - 發送所有商品的 CLEAR + ADDs
            // - 發送 SNAPSHOT_END
            // ⚡ UDP Multicast：單次發送，所有訂閱者同時接收
            publishSnapshot();
        }
    }
}
}
