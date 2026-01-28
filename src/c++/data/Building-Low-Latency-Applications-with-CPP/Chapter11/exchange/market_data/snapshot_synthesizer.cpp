/**
 * @file snapshot_synthesizer.cpp
 * @brief 快照合成器實作檔案
 *
 * 實作 SnapshotSynthesizer 類別的核心功能，負責：
 * 1. 維護完整訂單簿狀態的記憶體副本
 * 2. 處理增量更新（ADD/MODIFY/CANCEL）並更新副本狀態
 * 3. 定期發布完整快照（每 60 秒）給所有訂閱者
 *
 * 核心設計：
 * - 狀態維護：ticker_orders_ 維護每個商品的所有活躍訂單
 * - 增量處理：從 Lock-Free Queue 接收增量更新並應用到狀態
 * - 快照發布：定時透過 UDP Multicast 發送完整訂單簿狀態
 * - 序列號追蹤：last_inc_seq_num_ 記錄最後處理的增量更新序列號
 *
 * 快照格式：
 * SNAPSHOT_START → CLEAR(ticker_0) → ADD(order_1) → ADD(order_2) → ... → CLEAR(ticker_1) → ... → SNAPSHOT_END
 *
 * 使用場景：
 * - 新訂閱者加入：需要完整快照來初始化訂單簿
 * - 丟包恢復：如果增量更新丟包過多，客戶端可用快照重建狀態
 * - 狀態驗證：客戶端可定期比對快照與本地狀態，確保一致性
 */
#include "snapshot_synthesizer.h"

namespace Exchange
{
/**
 * @brief SnapshotSynthesizer 建構子
 *
 * 初始化快照合成器的核心元件：
 * 1. UDP Multicast Socket（用於發送快照）
 * 2. Memory Pool（用於維護訂單副本）
 * 3. 訂單狀態陣列（ticker_orders_）
 *
 * @param market_updates Lock-Free Queue 指標（從 MarketDataPublisher 接收增量更新）
 * @param iface 網路介面名稱（例如 "eth0"）
 * @param snapshot_ip 快照通道的 Multicast IP 位址
 * @param snapshot_port 快照通道的 UDP Port
 *
 * 初始化流程：
 * 1. 綁定 Lock-Free Queue（snapshot_md_updates_）
 * 2. 建立快照發布的 UDP Multicast Socket
 * 3. 初始化 Memory Pool（預分配 ME_MAX_ORDER_IDS 個訂單物件）
 * 4. 初始化 ticker_orders_ 陣列（所有指標設為 nullptr）
 *
 * ⚡ 效能考量：
 * - Memory Pool：避免動態記憶體分配，快速分配/釋放訂單物件
 * - UDP Multicast：低延遲，一次發送給所有訂閱者
 * - Lock-Free Queue：與 MarketDataPublisher 無鎖通訊
 *
 * ⚠️ 注意：
 * - snapshot_socket_ 的 is_listening 參數為 false（發送端模式）
 * - ticker_orders_ 是二維陣列：ticker_orders_[ticker_id][order_id] = MEMarketUpdate*
 * - 所有訂單指標初始化為 nullptr（表示訂單不存在）
 */
SnapshotSynthesizer::SnapshotSynthesizer(MDPMarketUpdateLFQueue* market_updates,
        const std::string& iface,
        const std::string& snapshot_ip, int snapshot_port)
    : snapshot_md_updates_(market_updates),  // 綁定 Lock-Free Queue
      logger_("exchange_snapshot_synthesizer.log"),  // 日誌記錄器
      snapshot_socket_(logger_),  // 快照發布的 UDP Multicast Socket
      order_pool_(ME_MAX_ORDER_IDS)  // Memory Pool（預分配訂單物件）
{
    // 初始化快照發布的 UDP Multicast Socket
    // ⚠️ is_listening = false：發送端模式（不接收任何資料）
    ASSERT(snapshot_socket_.init(snapshot_ip, iface,
                                 snapshot_port, /*is_listening*/ false) >= 0,
           "Unable to create snapshot mcast socket. error:" + std::string(std::strerror(
                       errno)));

    // 初始化 ticker_orders_ 陣列（所有訂單指標設為 nullptr）
    // ticker_orders_[ticker_id][order_id] = MEMarketUpdate*
    // nullptr 表示該訂單不存在
    for (auto& orders : ticker_orders_) {
        orders.fill(nullptr);
    }
}

SnapshotSynthesizer::~SnapshotSynthesizer()
{
    stop();
}

void SnapshotSynthesizer::start()
{
    run_ = true;
    ASSERT(Common::createAndStartThread(-1,
    "Exchange/SnapshotSynthesizer", [this]() {
        run();
    }) != nullptr,
    "Failed to start SnapshotSynthesizer thread.");
}

void SnapshotSynthesizer::stop()
{
    run_ = false;
}

/**
 * @brief ⚡ 處理增量更新並更新快照狀態（效能關鍵路徑）
 *
 * 根據增量更新的類型（ADD/MODIFY/CANCEL）更新 ticker_orders_ 狀態。
 * 這個函式維護完整訂單簿的記憶體副本，供定期快照發布使用。
 *
 * 處理邏輯：
 * - ADD：從 Memory Pool 分配新訂單物件並加入 ticker_orders_
 * - MODIFY：更新現有訂單的數量與價格
 * - CANCEL：釋放訂單物件回 Memory Pool 並從 ticker_orders_ 移除
 * - TRADE/SNAPSHOT_START/SNAPSHOT_END/CLEAR：忽略（不影響訂單簿狀態）
 *
 * @param market_update MDPMarketUpdate 指標（包含序列號與市場更新）
 *
 * ⚡ 效能優化：
 * - Memory Pool：allocate/deallocate 都是 O(1) 操作
 * - 直接索引：ticker_orders_[ticker_id][order_id] 直接存取，O(1) 時間複雜度
 * - 序列號檢查：確保增量更新按順序處理（檢測丟包或亂序）
 *
 * 📊 狀態維護範例：
 * 1. 收到 ADD order_id=100, qty=50
 *    → ticker_orders_[0][100] = order_pool_.allocate(...)
 * 2. 收到 MODIFY order_id=100, qty=30
 *    → ticker_orders_[0][100]->qty_ = 30
 * 3. 收到 CANCEL order_id=100
 *    → order_pool_.deallocate(ticker_orders_[0][100])
 *    → ticker_orders_[0][100] = nullptr
 *
 * ⚠️ 注意：
 * - ASSERT 檢查確保狀態一致性（ADD 時訂單不存在，MODIFY/CANCEL 時訂單存在）
 * - 序列號必須連續遞增（last_inc_seq_num_ + 1），否則觸發 ASSERT
 * - TRADE 事件不影響訂單簿狀態（只影響成交記錄），故忽略
 */
auto SnapshotSynthesizer::addToSnapshot(const MDPMarketUpdate* market_update)
{
    // 取得市場更新結構
    const auto& me_market_update = market_update->me_market_update_;

    // 取得該商品的訂單陣列指標（ticker_orders_[ticker_id]）
    auto* orders = &ticker_orders_.at(me_market_update.ticker_id_);

    // 根據更新類型處理狀態變更
    switch (me_market_update.type_) {
    case MarketUpdateType::ADD: {
            // 新增訂單：從 Memory Pool 分配新訂單物件
            auto order = orders->at(me_market_update.order_id_);

            // ⚠️ 狀態一致性檢查：ADD 時訂單必須不存在（nullptr）
            ASSERT(order == nullptr,
                   "Received:" + me_market_update.toString() + " but order already exists:" +
                   (order ? order->toString() : ""));

            // 從 Memory Pool 分配訂單物件並加入 ticker_orders_
            // ⚡ allocate() 是 O(1) 操作（從 Free List 取得）
            orders->at(me_market_update.order_id_) = order_pool_.allocate(me_market_update);
        }
        break;

    case MarketUpdateType::MODIFY: {
            // 修改訂單：更新現有訂單的數量與價格
            auto order = orders->at(me_market_update.order_id_);

            // ⚠️ 狀態一致性檢查：MODIFY 時訂單必須存在
            ASSERT(order != nullptr,
                   "Received:" + me_market_update.toString() + " but order does not exist.");
            ASSERT(order->order_id_ == me_market_update.order_id_,
                   "Expecting existing order to match new one.");
            ASSERT(order->side_ == me_market_update.side_,
                   "Expecting existing order to match new one.");

            // 更新訂單數量與價格
            order->qty_ = me_market_update.qty_;
            order->price_ = me_market_update.price_;
        }
        break;

    case MarketUpdateType::CANCEL: {
            // 取消訂單：釋放訂單物件回 Memory Pool
            auto order = orders->at(me_market_update.order_id_);

            // ⚠️ 狀態一致性檢查：CANCEL 時訂單必須存在
            ASSERT(order != nullptr,
                   "Received:" + me_market_update.toString() + " but order does not exist.");
            ASSERT(order->order_id_ == me_market_update.order_id_,
                   "Expecting existing order to match new one.");
            ASSERT(order->side_ == me_market_update.side_,
                   "Expecting existing order to match new one.");

            // 釋放訂單物件回 Memory Pool
            // ⚡ deallocate() 是 O(1) 操作（加回 Free List）
            order_pool_.deallocate(order);

            // 從 ticker_orders_ 移除（設為 nullptr）
            orders->at(me_market_update.order_id_) = nullptr;
        }
        break;

    // 以下類型不影響訂單簿狀態，故忽略
    case MarketUpdateType::SNAPSHOT_START:  // 快照開始標記
    case MarketUpdateType::CLEAR:           // 清空訂單簿標記
    case MarketUpdateType::SNAPSHOT_END:    // 快照結束標記
    case MarketUpdateType::TRADE:           // 成交事件（不影響掛單）
    case MarketUpdateType::INVALID:         // 無效類型
        break;
    }

    // ⚠️ 序列號一致性檢查：增量更新必須按順序處理
    // 如果 seq_num 不是 last_inc_seq_num_ + 1，表示丟包或亂序
    ASSERT(market_update->seq_num_ == last_inc_seq_num_ + 1,
           "Expected incremental seq_nums to increase.");

    // 更新最後處理的序列號
    last_inc_seq_num_ = market_update->seq_num_;
}

/**
 * @brief 發布完整快照
 *
 * 透過 UDP Multicast 發送完整訂單簿狀態給所有訂閱者。
 *
 * 快照格式（按順序發送）：
 * 1. SNAPSHOT_START - 快照開始標記（包含 last_inc_seq_num_）
 * 2. 對每個商品（ticker）：
 *    a. CLEAR - 清空該商品的訂單簿
 *    b. ADD - 逐筆發送該商品的所有活躍訂單
 * 3. SNAPSHOT_END - 快照結束標記（包含 last_inc_seq_num_）
 *
 * 客戶端處理流程：
 * 1. 收到 SNAPSHOT_START → 準備接收快照
 * 2. 收到 CLEAR(ticker_id) → 清空本地訂單簿的該商品資料
 * 3. 收到 ADD → 將訂單加入本地訂單簿
 * 4. 收到 SNAPSHOT_END → 快照接收完成，開始接收增量更新
 *
 * 📊 快照範例：
 * SNAPSHOT_START (seq=1000)
 * → CLEAR (ticker_0)
 * → ADD (order_1: 100 張 @ $50)
 * → ADD (order_2: 50 張 @ $51)
 * → CLEAR (ticker_1)
 * → ADD (order_3: 200 張 @ $100)
 * → SNAPSHOT_END (seq=1000)
 *
 * ⚡ 效能考量：
 * - UDP Multicast：一次發送，所有訂閱者都能收到
 * - 批次發送：sendAndRecv() 在每個商品結束後呼叫（減少系統呼叫次數）
 * - snapshot_size 計數器：記錄快照包含的總訊息數（用於統計）
 *
 * ⚠️ 注意：
 * - last_inc_seq_num_ 記錄快照對應的增量更新序列號
 *   → 客戶端收到快照後，可從 last_inc_seq_num_ + 1 開始接收增量更新
 * - snapshot_size 從 0 開始計數（用於標識快照中每筆訊息的順序）
 * - 只發送非 nullptr 的訂單（nullptr 表示訂單不存在）
 */
auto SnapshotSynthesizer::publishSnapshot()
{
    size_t snapshot_size = 0;  // 快照訊息計數器

    // 步驟 1：發送 SNAPSHOT_START 標記
    // 包含 last_inc_seq_num_（客戶端可用此序列號同步增量更新）
    const MDPMarketUpdate start_market_update{snapshot_size++, {MarketUpdateType::SNAPSHOT_START, last_inc_seq_num_}};
    logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                getCurrentTimeStr(&time_str_), start_market_update.toString());
    // ⚡ Socket 收發：熱路徑避免額外拷貝。
    snapshot_socket_.send(&start_market_update, sizeof(MDPMarketUpdate));

    // 步驟 2：遍歷所有商品，發送每個商品的訂單簿狀態
    for (size_t ticker_id = 0; ticker_id < ticker_orders_.size(); ++ticker_id) {
        const auto& orders = ticker_orders_.at(ticker_id);

        // 步驟 2a：發送 CLEAR 標記（通知客戶端清空該商品的本地訂單簿）
        MEMarketUpdate me_market_update;
        me_market_update.type_ = MarketUpdateType::CLEAR;
        me_market_update.ticker_id_ = ticker_id;

        const MDPMarketUpdate clear_market_update{snapshot_size++, me_market_update};
        logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                    getCurrentTimeStr(&time_str_), clear_market_update.toString());
        // ⚡ Socket 收發：熱路徑避免額外拷貝。
        snapshot_socket_.send(&clear_market_update, sizeof(MDPMarketUpdate));

        // 步驟 2b：發送該商品的所有活躍訂單（逐筆發送 ADD 訊息）
        for (const auto order : orders) {
            // 只發送非 nullptr 的訂單（nullptr 表示訂單不存在）
            if (order) {
                const MDPMarketUpdate market_update{snapshot_size++, *order};
                logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                            getCurrentTimeStr(&time_str_), market_update.toString());
                // ⚡ Socket 收發：熱路徑避免額外拷貝。
                snapshot_socket_.send(&market_update, sizeof(MDPMarketUpdate));

                // ⚡ 批次發送：每個訂單發送後立即呼叫 sendAndRecv()
                // 這會實際發送 UDP 封包（減少緩衝區堆積）
                snapshot_socket_.sendAndRecv();
            }
        }
    }

    // 步驟 3：發送 SNAPSHOT_END 標記（通知客戶端快照發送完成）
    // 包含 last_inc_seq_num_（客戶端可從此序列號 +1 開始接收增量更新）
    const MDPMarketUpdate end_market_update{snapshot_size++, {MarketUpdateType::SNAPSHOT_END, last_inc_seq_num_}};
    logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                getCurrentTimeStr(&time_str_), end_market_update.toString());
    // ⚡ Socket 收發：熱路徑避免額外拷貝。
    snapshot_socket_.send(&end_market_update, sizeof(MDPMarketUpdate));
    snapshot_socket_.sendAndRecv();

    // 記錄快照統計資訊（snapshot_size - 1 是因為計數從 0 開始）
    logger_.log("%:% %() % Published snapshot of % orders.\n", __FILE__, __LINE__,
                __FUNCTION__, getCurrentTimeStr(&time_str_), snapshot_size - 1);
}

/**
 * @brief ⚡ 快照合成器主事件迴圈（效能關鍵路徑）
 *
 * 持續處理增量更新並定期發布快照。
 *
 * 執行流程：
 * 1. 從 Lock-Free Queue 讀取增量更新
 * 2. 呼叫 addToSnapshot() 更新訂單簿狀態
 * 3. 檢查是否超過 60 秒（快照發布週期）
 * 4. 如果超過 60 秒，呼叫 publishSnapshot() 發布完整快照
 *
 * ⚡ 效能優化：
 * - Lock-Free Queue：與 MarketDataPublisher 無鎖通訊
 * - 批次處理：for 迴圈處理完所有佇列中的更新後才檢查快照發布時間
 * - 定時發布：60 秒週期（平衡網路流量與客戶端同步需求）
 *
 * 📊 時間軸範例：
 * T=0s: run() 啟動，last_snapshot_time_ = 0
 * T=1s: 處理增量更新 1-100
 * T=30s: 處理增量更新 101-500
 * T=60s: 檢查時間 → 發布快照（包含所有活躍訂單）
 * T=61s: 處理增量更新 501-600
 * T=120s: 檢查時間 → 發布快照
 *
 * ⚠️ 注意：
 * - 快照發布週期為 60 秒（60 * NANOS_TO_SECS）
 * - getCurrentNanos() 使用高精度時間戳（奈秒級）
 * - run_ 標誌由 start() 設為 true，stop() 設為 false
 * - 快照發布期間仍會繼續處理增量更新（不阻塞）
 */
void SnapshotSynthesizer::run()
{
    // 記錄啟動時間
    logger_.log("%:% %() %\n", __FILE__, __LINE__, __FUNCTION__,
                getCurrentTimeStr(&time_str_));

    // ⚡ 主事件迴圈：持續處理增量更新並定期發布快照
    while (run_) {
        // ⚡ 批次處理：從 Lock-Free Queue 讀取所有可用的增量更新
        // 迴圈條件：佇列非空 且 getNextToRead() 回傳非 nullptr
        for (auto market_update = snapshot_md_updates_->getNextToRead();
             snapshot_md_updates_->size() &&
             market_update; market_update = snapshot_md_updates_->getNextToRead()) {

            // 記錄處理日誌
            logger_.log("%:% %() % Processing %\n", __FILE__, __LINE__, __FUNCTION__,
                        getCurrentTimeStr(&time_str_),
                        market_update->toString().c_str());

            // 處理增量更新並更新訂單簿狀態
            addToSnapshot(market_update);

            // 更新讀取索引（通知 Lock-Free Queue 該元素已處理完畢）
            snapshot_md_updates_->updateReadIndex();
        }

        // 檢查是否超過 60 秒（快照發布週期）
        // getCurrentNanos() - last_snapshot_time_ 計算自上次快照以來經過的時間（奈秒）
        // 60 * NANOS_TO_SECS 將 60 秒轉換為奈秒
        if (getCurrentNanos() - last_snapshot_time_ > 60 * NANOS_TO_SECS) {
            // 更新快照時間戳
            last_snapshot_time_ = getCurrentNanos();

            // 發布完整快照
            publishSnapshot();
        }
    }
}
}
