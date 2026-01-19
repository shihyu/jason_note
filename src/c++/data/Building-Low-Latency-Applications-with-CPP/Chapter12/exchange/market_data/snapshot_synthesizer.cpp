/**
 * @file snapshot_synthesizer.cpp
 * @brief 行情快照合成器（Market Data Snapshot Synthesizer）
 *
 * 🎯 核心功能：
 * - 維護完整訂單簿快照（所有標的的所有活動訂單）
 * - 定期發布快照（每 60 秒一次）
 * - 處理增量更新（ADD/MODIFY/CANCEL）同步訂單簿狀態
 *
 * 📊 快照協議（Snapshot Protocol）：
 * 1. SNAPSHOT_START：標記快照開始，包含最後增量序號
 * 2. 每個標的發送 CLEAR 訊息
 * 3. 發送該標的所有活動訂單
 * 4. SNAPSHOT_END：標記快照結束，包含最後增量序號
 *
 * ⚡ 用途：
 * - 新加入的客戶端可快速恢復完整訂單簿狀態
 * - 客戶端丟失增量更新時可重新同步
 * - 與增量更新（Incremental Feed）配合實現可靠行情分發
 *
 * 🎯 增量 vs 快照：
 * - 增量：即時更新（低延遲），但可能丟失或亂序
 * - 快照：完整狀態（高可靠），但延遲較高（60秒週期）
 * - 客戶端策略：優先使用增量，快照用於恢復
 */
#include "snapshot_synthesizer.h"

namespace Exchange
{
/// 建構函式：初始化快照合成器
SnapshotSynthesizer::SnapshotSynthesizer(MDPMarketUpdateLFQueue* market_updates,
        const std::string& iface,
        const std::string& snapshot_ip, int snapshot_port)
    : snapshot_md_updates_(market_updates),  // 增量更新佇列（輸入）
      logger_("exchange_snapshot_synthesizer.log"),
      snapshot_socket_(logger_),             // UDP Multicast 快照通道（輸出）
      order_pool_(ME_MAX_ORDER_IDS)          // 訂單物件記憶體池
{
    // 初始化快照多播 socket
    // ⚠️ is_listening = false：這是發送端，非接收端
    ASSERT(snapshot_socket_.init(snapshot_ip, iface,
                                 snapshot_port, /*is_listening*/ false) >= 0,
           "Unable to create snapshot mcast socket. error:" + std::string(std::strerror(
                       errno)));

    // 初始化所有標的的訂單陣列（ME_MAX_ORDER_IDS 個指標，初始為 nullptr）
    for (auto& orders : ticker_orders_) {
        orders.fill(nullptr);
    }
}

SnapshotSynthesizer::~SnapshotSynthesizer()
{
    stop();
}

/// Start and stop the snapshot synthesizer thread.
void SnapshotSynthesizer::start()
{
    run_ = true;
    ASSERT(Common::createAndStartThread(-1,
    "Exchange/SnapshotSynthesizer", [this]() {
        // ⚡ 關鍵路徑：函式內避免鎖/分配，保持快取局部性。
        run();
    }) != nullptr,
    "Failed to start SnapshotSynthesizer thread.");
}

void SnapshotSynthesizer::stop()
{
    run_ = false;
}

/// Process an incremental market update and update the limit order book snapshot.
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

/// Publish a full snapshot cycle on the snapshot multicast stream.
auto SnapshotSynthesizer::publishSnapshot()
{
    size_t snapshot_size = 0;

    // The snapshot cycle starts with a SNAPSHOT_START message and order_id_ contains the last sequence number from the incremental market data stream used to build this snapshot.
    const MDPMarketUpdate start_market_update{snapshot_size++, {MarketUpdateType::SNAPSHOT_START, last_inc_seq_num_}};
    logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                getCurrentTimeStr(&time_str_), start_market_update.toString());
    snapshot_socket_.send(&start_market_update, sizeof(MDPMarketUpdate));

    // Publish order information for each order in the limit order book for each instrument.
    for (size_t ticker_id = 0; ticker_id < ticker_orders_.size(); ++ticker_id) {
        const auto& orders = ticker_orders_.at(ticker_id);

        MEMarketUpdate me_market_update;
        me_market_update.type_ = MarketUpdateType::CLEAR;
        me_market_update.ticker_id_ = ticker_id;

        // We start order information for each instrument by first publishing a CLEAR message so the downstream consumer can clear the order book.
        const MDPMarketUpdate clear_market_update{snapshot_size++, me_market_update};
        logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                    getCurrentTimeStr(&time_str_), clear_market_update.toString());
        snapshot_socket_.send(&clear_market_update, sizeof(MDPMarketUpdate));

        // Publish each order.
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

    // The snapshot cycle ends with a SNAPSHOT_END message and order_id_ contains the last sequence number from the incremental market data stream used to build this snapshot.
    const MDPMarketUpdate end_market_update{snapshot_size++, {MarketUpdateType::SNAPSHOT_END, last_inc_seq_num_}};
    logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                getCurrentTimeStr(&time_str_), end_market_update.toString());
    snapshot_socket_.send(&end_market_update, sizeof(MDPMarketUpdate));
    snapshot_socket_.sendAndRecv();

    logger_.log("%:% %() % Published snapshot of % orders.\n", __FILE__, __LINE__,
                __FUNCTION__, getCurrentTimeStr(&time_str_), snapshot_size - 1);
}

/// Main method for this thread - processes incremental updates from the market data publisher, updates the snapshot and publishes the snapshot periodically.
void SnapshotSynthesizer::run()
{
    logger_.log("%:% %() %\n", __FILE__, __LINE__, __FUNCTION__,
                getCurrentTimeStr(&time_str_));

    while (run_) {
        for (auto market_update = snapshot_md_updates_->getNextToRead();
             snapshot_md_updates_->size() &&
             market_update; market_update = snapshot_md_updates_->getNextToRead()) {
            logger_.log("%:% %() % Processing %\n", __FILE__, __LINE__, __FUNCTION__,
                        getCurrentTimeStr(&time_str_),
                        market_update->toString().c_str());

            addToSnapshot(market_update);

            snapshot_md_updates_->updateReadIndex();
        }

        if (getCurrentNanos() - last_snapshot_time_ > 60 * NANOS_TO_SECS) {
            last_snapshot_time_ = getCurrentNanos();
            publishSnapshot();
        }
    }
}
}
