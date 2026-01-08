#include "market_data_consumer.h"

namespace Trading
{
/**
 * 構造函式實現
 *
 * 初始化流程：
 * 1. 儲存配置參數（網路介面、快照 IP/Port）
 * 2. 建立兩個 Multicast Sockets（增量通道、快照通道）
 * 3. 設置接收回調函式
 * 4. 訂閱增量更新多播群組（立即開始接收）
 * 5. 快照通道暫不訂閱（只在需要恢復時才訂閱）
 *
 * 注意：
 * - 增量通道在構造時就訂閱（join），確保不遺失訊息
 * - 快照通道延遲訂閱，僅在偵測到訊息遺失時才啟動
 */
MarketDataConsumer::MarketDataConsumer(Common::ClientId client_id,
                                       Exchange::MEMarketUpdateLFQueue* market_updates,
                                       const std::string& iface,
                                       const std::string& snapshot_ip, int snapshot_port,
                                       const std::string& incremental_ip, int incremental_port)
    : incoming_md_updates_(market_updates), run_(false),
      logger_("trading_market_data_consumer_" + std::to_string(client_id) + ".log"),
      incremental_mcast_socket_(logger_), snapshot_mcast_socket_(logger_),
      iface_(iface), snapshot_ip_(snapshot_ip), snapshot_port_(snapshot_port)
{
    // 建立接收回調 Lambda（兩個 socket 共用同一個回調函式）
    auto recv_callback = [this](auto socket) {
        recvCallback(socket);
    };

    // === 初始化增量更新通道 ===
    incremental_mcast_socket_.recv_callback_ = recv_callback;

    // 建立 Multicast Socket（is_listening=true 表示接收模式）
    ASSERT(incremental_mcast_socket_.init(incremental_ip, iface,
                                          incremental_port, /*is_listening*/ true) >= 0,
           "Unable to create incremental mcast socket. error:" + std::string(std::strerror(
                       errno)));

    // 加入多播群組（發送 IGMP 訊息，開始接收市場數據）
    ASSERT(incremental_mcast_socket_.join(incremental_ip),
           "Join failed on:" + std::to_string(incremental_mcast_socket_.socket_fd_) +
           " error:" + std::string(std::strerror(errno)));

    // === 初始化快照通道（但不立即訂閱）===
    // 設置接收回調，但不呼叫 init() 和 join()
    // 只有在偵測到訊息遺失時才會在 startSnapshotSync() 中訂閱
    snapshot_mcast_socket_.recv_callback_ = recv_callback;
}

/**
 * run() - 主事件迴圈（在獨立執行緒中執行）
 *
 * 設計理念：
 * - 極簡迴圈，減少延遲
 * - 輪詢兩個 multicast sockets
 * - 所有複雜邏輯都在回調函式中處理
 *
 * 職責：
 * 1. 輪詢增量更新 socket（incremental_mcast_socket_）
 * 2. 輪詢快照 socket（snapshot_mcast_socket_）
 * 3. 自動觸發 recvCallback() 處理接收到的訊息
 *
 * 效能特性：
 * - 緊密迴圈（tight loop），無 sleep 或阻塞操作
 * - 每次迭代延遲：< 5 μs
 * - 雙 socket 輪詢確保不遺失訊息
 *
 * 注意：
 * - 快照 socket 在正常模式下不會接收資料（未訂閱）
 * - 只有進入恢復模式後，快照 socket 才會開始接收
 */
auto MarketDataConsumer::run() noexcept -> void
{
    // 記錄執行緒啟動時間
    logger_.log("%:% %() %\n", __FILE__, __LINE__, __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_));

    // 主事件迴圈（run_ = false 時停止）
    while (run_) {
        // 輪詢增量更新 socket（接收實時市場數據）
        incremental_mcast_socket_.sendAndRecv();

        // 輪詢快照 socket（僅在恢復模式下有資料）
        snapshot_mcast_socket_.sendAndRecv();
    }
}

/**
 * startSnapshotSync() - 啟動快照同步
 *
 * 觸發時機：
 * - recvCallback() 偵測到增量訊息序列號跳躍（遺失訊息）
 *
 * 職責：
 * 1. 清空所有暫存的訊息佇列
 * 2. 初始化快照 socket
 * 3. 加入快照多播群組（發送 IGMP 訊息）
 * 4. 開始接收快照訊息流
 *
 * 狀態轉換：
 * - in_recovery_ 已在 recvCallback() 中設為 true
 * - 後續接收到的增量訊息會被暫存到 incremental_queued_msgs_
 * - 快照訊息會被暫存到 snapshot_queued_msgs_
 *
 * 注意：
 * - 清空佇列是因為舊的暫存訊息已經無效（快照會提供完整狀態）
 * - IGMP 加入可能需要幾毫秒，期間可能遺失部分快照訊息（無妨，會重新同步）
 */
auto MarketDataConsumer::startSnapshotSync() -> void
{
    // 清空暫存佇列（重新開始）
    snapshot_queued_msgs_.clear();
    incremental_queued_msgs_.clear();

    // 初始化快照 Multicast Socket
    ASSERT(snapshot_mcast_socket_.init(snapshot_ip_, iface_,
                                       snapshot_port_, /*is_listening*/ true) >= 0,
           "Unable to create snapshot mcast socket. error:" + std::string(std::strerror(
                       errno)));

    // 加入快照多播群組（發送 IGMP 訊息，開始接收快照資料）
    ASSERT(snapshot_mcast_socket_.join(
               snapshot_ip_), // IGMP multicast subscription.
           "Join failed on:" + std::to_string(snapshot_mcast_socket_.socket_fd_) +
           " error:" + std::string(std::strerror(errno)));
}

/**
 * checkSnapshotSync() - 檢查快照同步進度並嘗試完成恢復
 *
 * 呼叫時機：
 * - 每次收到快照或增量訊息後（在 queueMessage() 中呼叫）
 *
 * 職責：
 * 1. 驗證快照訊息的完整性（是否有遺失）
 * 2. 驗證快照是否包含開始和結束標記
 * 3. 檢查暫存的增量訊息是否能與快照銜接
 * 4. 若所有條件滿足，重建市場狀態並恢復正常模式
 *
 * 完整快照的條件：
 * 1. 第一條訊息類型為 SNAPSHOT_START
 * 2. 所有訊息序列號連續（無間隙）
 * 3. 最後一條訊息類型為 SNAPSHOT_END
 * 4. 暫存的增量訊息能與快照末尾序列號銜接
 *
 * 恢復流程：
 * 1. 驗證快照完整性
 * 2. 收集快照中的市場更新（排除 START/END 標記）
 * 3. 驗證增量訊息完整性（從快照結束序列號+1 開始）
 * 4. 收集可銜接的增量訊息
 * 5. 依序將所有訊息寫入輸出佇列
 * 6. 清空暫存佇列，恢復正常模式（in_recovery_ = false）
 * 7. 解除訂閱快照多播群組
 *
 * 失敗情境（會清空佇列並等待下一次快照）：
 * - 快照未開始（缺少 SNAPSHOT_START）
 * - 快照有間隙（序列號不連續）
 * - 快照未結束（缺少 SNAPSHOT_END）
 * - 增量訊息無法銜接（有間隙）
 */
auto MarketDataConsumer::checkSnapshotSync() -> void
{
    // 提前返回：尚未收到任何快照訊息
    if (snapshot_queued_msgs_.empty()) {
        return;
    }

    // === 第一階段：驗證快照開始標記 ===
    const auto& first_snapshot_msg = snapshot_queued_msgs_.begin()->second;

    if (first_snapshot_msg.type_ != Exchange::MarketUpdateType::SNAPSHOT_START) {
        // 缺少開始標記 → 清空佇列，等待下一個完整快照
        logger_.log("%:% %() % Returning because have not seen a SNAPSHOT_START yet.\n",
                    __FILE__, __LINE__, __FUNCTION__, Common::getCurrentTimeStr(&time_str_));
        snapshot_queued_msgs_.clear();
        return;
    }

    // 準備最終輸出的市場更新序列
    std::vector<Exchange::MEMarketUpdate> final_events;

    // === 第二階段：驗證快照序列號連續性 ===
    auto have_complete_snapshot = true;
    size_t next_snapshot_seq = 0;  // 預期的下一個序列號

    // 遍歷所有快照訊息（std::map 保證按序列號排序）
    for (auto& snapshot_itr : snapshot_queued_msgs_) {
        logger_.log("%:% %() % % => %\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), snapshot_itr.first,
                    snapshot_itr.second.toString());

        // 檢查序列號是否連續
        if (snapshot_itr.first != next_snapshot_seq) {
            have_complete_snapshot = false;
            logger_.log("%:% %() % Detected gap in snapshot stream expected:% found:% %.\n",
                        __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_), next_snapshot_seq, snapshot_itr.first,
                        snapshot_itr.second.toString());
            break;  // 發現間隙，停止檢查
        }

        // 收集實際的市場更新（排除開始和結束標記）
        if (snapshot_itr.second.type_ != Exchange::MarketUpdateType::SNAPSHOT_START &&
            snapshot_itr.second.type_ != Exchange::MarketUpdateType::SNAPSHOT_END) {
            final_events.push_back(snapshot_itr.second);
        }

        ++next_snapshot_seq;  // 遞增預期序列號
    }

    // 快照不完整 → 清空佇列，等待下一次快照
    if (!have_complete_snapshot) {
        logger_.log("%:% %() % Returning because found gaps in snapshot stream.\n",
                    __FILE__, __LINE__, __FUNCTION__, Common::getCurrentTimeStr(&time_str_));
        snapshot_queued_msgs_.clear();
        return;
    }

    // === 第三階段：驗證快照結束標記 ===
    const auto& last_snapshot_msg = snapshot_queued_msgs_.rbegin()->second;

    if (last_snapshot_msg.type_ != Exchange::MarketUpdateType::SNAPSHOT_END) {
        // 快照尚未結束 → 繼續等待更多訊息
        logger_.log("%:% %() % Returning because have not seen a SNAPSHOT_END yet.\n",
                    __FILE__, __LINE__, __FUNCTION__, Common::getCurrentTimeStr(&time_str_));
        return;
    }

    // === 第四階段：驗證增量訊息銜接性 ===
    auto have_complete_incremental = true;
    size_t num_incrementals = 0;

    // 設置預期的增量序列號（從快照結束序列號的下一個開始）
    // order_id_ 在 SNAPSHOT_END 訊息中表示最後一個快照序列號
    next_exp_inc_seq_num_ = last_snapshot_msg.order_id_ + 1;

    // 遍歷暫存的增量訊息
    for (auto inc_itr = incremental_queued_msgs_.begin();
         inc_itr != incremental_queued_msgs_.end(); ++inc_itr) {
        logger_.log("%:% %() % Checking next_exp:% vs. seq:% %.\n", __FILE__, __LINE__,
                    __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), next_exp_inc_seq_num_, inc_itr->first,
                    inc_itr->second.toString());

        // 跳過已包含在快照中的訊息（序列號小於預期值）
        if (inc_itr->first < next_exp_inc_seq_num_) {
            continue;
        }

        // 檢查序列號是否連續
        if (inc_itr->first != next_exp_inc_seq_num_) {
            // 發現間隙 → 增量訊息無法銜接
            logger_.log("%:% %() % Detected gap in incremental stream expected:% found:% %.\n",
                        __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_), next_exp_inc_seq_num_, inc_itr->first,
                        inc_itr->second.toString());
            have_complete_incremental = false;
            break;
        }

        // 記錄可銜接的增量訊息
        logger_.log("%:% %() % % => %\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), inc_itr->first,
                    inc_itr->second.toString());

        // 收集實際的市場更新（排除標記）
        if (inc_itr->second.type_ != Exchange::MarketUpdateType::SNAPSHOT_START &&
            inc_itr->second.type_ != Exchange::MarketUpdateType::SNAPSHOT_END) {
            final_events.push_back(inc_itr->second);
        }

        ++next_exp_inc_seq_num_;
        ++num_incrementals;
    }

    // 增量訊息有間隙 → 清空佇列，等待下一次快照
    if (!have_complete_incremental) {
        logger_.log("%:% %() % Returning because have gaps in queued incrementals.\n",
                    __FILE__, __LINE__, __FUNCTION__, Common::getCurrentTimeStr(&time_str_));
        snapshot_queued_msgs_.clear();
        return;
    }

    // === 第五階段：恢復完成，輸出所有市場更新 ===
    // 將 final_events（快照 + 增量訊息）依序寫入輸出佇列
    for (const auto& itr : final_events) {
        auto next_write = incoming_md_updates_->getNextToWriteTo();
        *next_write = itr;
        incoming_md_updates_->updateWriteIndex();
    }

    // 記錄恢復統計
    logger_.log("%:% %() % Recovered % snapshot and % incremental orders.\n",
                __FILE__, __LINE__, __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_), snapshot_queued_msgs_.size() - 2,  // -2 排除 START/END 標記
                num_incrementals);

    // === 第六階段：清理並恢復正常模式 ===
    snapshot_queued_msgs_.clear();      // 清空快照暫存
    incremental_queued_msgs_.clear();   // 清空增量暫存
    in_recovery_ = false;               // 退出恢復模式

    // 解除訂閱快照多播群組（節省網路頻寬）
    snapshot_mcast_socket_.leave(snapshot_ip_, snapshot_port_);
}

/**
 * queueMessage() - 將訊息加入暫存佇列
 *
 * @param is_snapshot true=快照訊息, false=增量訊息
 * @param request 市場更新訊息指標
 *
 * 職責：
 * 1. 根據訊息類型選擇正確的暫存佇列
 * 2. 偵測重複訊息（僅針對快照）
 * 3. 將訊息加入 std::map（自動按序列號排序）
 * 4. 呼叫 checkSnapshotSync() 嘗試完成恢復
 *
 * 重複訊息處理：
 * - 快照訊息：若收到重複序列號，表示有封包遺失（Multicast 不可靠）
 *   → 清空快照佇列，等待下一次完整快照
 * - 增量訊息：允許重複（會在 checkSnapshotSync() 中跳過）
 *
 * 注意：
 * - 使用 std::map 自動排序，確保處理順序正確
 * - 每次加入訊息後都嘗試檢查恢復條件
 */
auto MarketDataConsumer::queueMessage(bool is_snapshot,
                                      const Exchange::MDPMarketUpdate* request)
{
    if (is_snapshot) {
        // 檢查快照訊息是否重複（表示有封包遺失）
        if (snapshot_queued_msgs_.find(request->seq_num_) !=
            snapshot_queued_msgs_.end()) {
            logger_.log("%:% %() % Packet drops on snapshot socket. Received for a 2nd time:%\n",
                        __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_), request->toString());
            // 清空快照佇列，重新開始（因為快照已不完整）
            snapshot_queued_msgs_.clear();
        }

        // 加入快照暫存佇列（std::map 自動按序列號排序）
        snapshot_queued_msgs_[request->seq_num_] = request->me_market_update_;
    } else {
        // 加入增量訊息暫存佇列
        incremental_queued_msgs_[request->seq_num_] = request->me_market_update_;
    }

    // 記錄暫存佇列大小
    logger_.log("%:% %() % size snapshot:% incremental:% % => %\n", __FILE__,
                __LINE__, __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_), snapshot_queued_msgs_.size(),
                incremental_queued_msgs_.size(), request->seq_num_, request->toString());

    // 嘗試檢查是否可以完成恢復
    checkSnapshotSync();
}

/**
 * recvCallback() - Multicast 接收回調函式
 *
 * @param socket 收到資料的 multicast socket 指標
 *
 * 觸發時機：
 * - sendAndRecv() 偵測到新資料到達時自動呼叫
 *
 * 職責：
 * 1. 識別訊息來源（快照 or 增量）
 * 2. 偵測序列號異常並觸發恢復機制
 * 3. 正常模式：直接處理增量訊息
 * 4. 恢復模式：暫存所有訊息到佇列
 *
 * 三種處理模式：
 * 1. 正常模式 + 增量訊息 → 直接寫入輸出佇列
 * 2. 正常模式 + 快照訊息 → 丟棄（不應該收到）
 * 3. 恢復模式 + 任何訊息 → 加入暫存佇列
 *
 * 序列號檢查：
 * - 若收到的序列號 != 預期值 → 進入恢復模式
 * - 恢復模式下，所有訊息都暫存，等待 checkSnapshotSync() 重建狀態
 *
 * 效能優化：
 * - UNLIKELY 宏標記罕見分支（幫助 CPU 分支預測）
 * - 批次處理多個訊息（減少函式呼叫）
 * - 零拷貝到 Lock-Free Queue（move 語意）
 */
auto MarketDataConsumer::recvCallback(McastSocket* socket) noexcept -> void
{
    // 判斷訊息來源（通過 socket FD 比較）
    const auto is_snapshot = (socket->socket_fd_ ==
                              snapshot_mcast_socket_.socket_fd_);

    // === 異常情境：正常模式下收到快照訊息 ===
    // 這不應該發生（正常模式下未訂閱快照通道）
    if (UNLIKELY(is_snapshot &&
                 !in_recovery_)) {
        // 清空緩衝區，丟棄訊息
        socket->next_rcv_valid_index_ = 0;

        logger_.log("%:% %() % WARN Not expecting snapshot messages.\n",
                    __FILE__, __LINE__, __FUNCTION__, Common::getCurrentTimeStr(&time_str_));

        return;
    }

    // 檢查緩衝區是否包含至少一個完整訊息
    if (socket->next_rcv_valid_index_ >= sizeof(Exchange::MDPMarketUpdate)) {
        size_t i = 0;  // 當前處理位置（bytes）

        // 批次處理所有完整訊息
        for (; i + sizeof(Exchange::MDPMarketUpdate) <= socket->next_rcv_valid_index_;
             i += sizeof(Exchange::MDPMarketUpdate)) {

            // 1. 反序列化訊息（零拷貝，直接使用緩衝區記憶體）
            auto request = reinterpret_cast<const Exchange::MDPMarketUpdate*>
                           (socket->inbound_data_.data() + i);
            logger_.log("%:% %() % Received % socket len:% %\n", __FILE__, __LINE__,
                        __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_),
                        (is_snapshot ? "snapshot" : "incremental"), sizeof(Exchange::MDPMarketUpdate),
                        request->toString());

            // 2. 檢查序列號（僅針對增量訊息）
            const bool already_in_recovery = in_recovery_;

            // 若收到的序列號不符預期 → 進入恢復模式
            // 注意：快照訊息在恢復模式下不檢查序列號（會在 checkSnapshotSync() 中處理）
            in_recovery_ = (already_in_recovery ||
                            request->seq_num_ != next_exp_inc_seq_num_);

            // === 恢復模式分支 ===
            if (UNLIKELY(in_recovery_)) {
                // 若剛進入恢復模式（序列號異常）
                if (UNLIKELY(
                        !already_in_recovery)) {
                    logger_.log("%:% %() % Packet drops on % socket. SeqNum expected:% received:%\n",
                                __FILE__, __LINE__, __FUNCTION__,
                                Common::getCurrentTimeStr(&time_str_),
                                (is_snapshot ? "snapshot" : "incremental"), next_exp_inc_seq_num_,
                                request->seq_num_);
                    // 啟動快照同步（訂閱快照多播群組）
                    startSnapshotSync();
                }

                // 將訊息加入暫存佇列（快照或增量）
                // queueMessage() 會呼叫 checkSnapshotSync() 嘗試完成恢復
                queueMessage(is_snapshot, request);

            // === 正常模式分支 ===
            } else if (
                !is_snapshot) { // 正常模式且收到增量訊息（序列號正確）
                logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                            Common::getCurrentTimeStr(&time_str_), request->toString());

                // 3. 遞增預期序列號
                ++next_exp_inc_seq_num_;

                // 4. 寫入 Lock-Free Queue（通知交易引擎）
                auto next_write = incoming_md_updates_->getNextToWriteTo();
                *next_write = std::move(request->me_market_update_);  // 移動語意（零拷貝）
                incoming_md_updates_->updateWriteIndex();
            }
        }

        // 5. 處理不完整訊息（將剩餘資料移到緩衝區開頭）
        //    例如：接收到 2.5 個訊息，保留 0.5 個等待下一次接收
        memcpy(socket->inbound_data_.data(), socket->inbound_data_.data() + i,
               socket->next_rcv_valid_index_ - i);
        socket->next_rcv_valid_index_ -= i;  // 更新有效資料長度
    }
}
}
