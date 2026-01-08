#include "snapshot_synthesizer.h"

namespace Exchange
{
SnapshotSynthesizer::SnapshotSynthesizer(MDPMarketUpdateLFQueue* market_updates,
        const std::string& iface,
        const std::string& snapshot_ip, int snapshot_port)
    : snapshot_md_updates_(market_updates),
      logger_("exchange_snapshot_synthesizer.log"), snapshot_socket_(logger_),
      order_pool_(ME_MAX_ORDER_IDS)
{
    ASSERT(snapshot_socket_.init(snapshot_ip, iface,
                                 snapshot_port, /*is_listening*/ false) >= 0,
           "Unable to create snapshot mcast socket. error:" + std::string(std::strerror(
                       errno)));

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
