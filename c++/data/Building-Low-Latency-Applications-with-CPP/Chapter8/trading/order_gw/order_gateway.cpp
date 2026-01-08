#include "order_gateway.h"

namespace Trading
{
/**
 * 構造函式實現
 *
 * 初始化流程：
 * 1. 儲存連接參數（client_id, ip, port, iface）
 * 2. 綁定佇列指標（outgoing_requests_, incoming_responses_）
 * 3. 建立日誌記錄器（每個 client_id 獨立日誌檔案）
 * 4. 設置 TCP 接收回調函式（Lambda 閉包）
 */
OrderGateway::OrderGateway(ClientId client_id,
                           Exchange::ClientRequestLFQueue* client_requests,
                           Exchange::ClientResponseLFQueue* client_responses,
                           std::string ip, const std::string& iface, int port)
    : client_id_(client_id), ip_(ip), iface_(iface), port_(port),
      outgoing_requests_(client_requests), incoming_responses_(client_responses),
      logger_("trading_order_gateway_" + std::to_string(client_id) + ".log"),
      tcp_socket_(logger_)
{
    // 設置 TCP Socket 接收回調函式
    // 當 TCP 收到資料時，會自動呼叫 recvCallback()
    tcp_socket_.recv_callback_ = [this](auto socket, auto rx_time) {
        recvCallback(socket, rx_time);
    };
}

/**
 * run() - 主事件迴圈（在獨立執行緒中執行）
 *
 * 職責：
 * 1. 輪詢 TCP Socket 收發資料
 * 2. 從 outgoing_requests_ 佇列讀取客戶端請求
 * 3. 將請求序列化並發送到交易所
 * 4. 自動觸發 recvCallback() 處理接收到的回應
 *
 * 效能特性：
 * - 緊密迴圈（tight loop），無 sleep 或阻塞操作
 * - 每次迭代延遲：< 10 μs
 * - Lock-Free Queue 讀取：O(1) 時間複雜度
 *
 * 訊息格式（發送到交易所）：
 * [序列號：8 bytes][訂單請求：sizeof(MEClientRequest) bytes]
 */
auto OrderGateway::run() noexcept -> void
{
    // 記錄執行緒啟動時間
    logger_.log("%:% %() %\n", __FILE__, __LINE__, __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_));

    // 主事件迴圈（run_ = false 時停止）
    while (run_) {
        // 1. 處理 TCP 收發
        //    - 發送緩衝區中待發送的資料
        //    - 接收新資料並觸發 recvCallback()
        tcp_socket_.sendAndRecv();

        // 2. 從佇列讀取並發送客戶端請求
        //    使用 for 迴圈批次處理（減少函式呼叫開銷）
        for (auto client_request = outgoing_requests_->getNextToRead(); client_request;
             client_request = outgoing_requests_->getNextToRead()) {

            // 記錄發送日誌（包含序列號）
            logger_.log("%:% %() % Sending cid:% seq:% %\n", __FILE__, __LINE__,
                        __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_), client_id_, next_outgoing_seq_num_,
                        client_request->toString());

            // 3. 發送序列號（8 bytes，用於交易所檢測遺失訊息）
            tcp_socket_.send(&next_outgoing_seq_num_, sizeof(next_outgoing_seq_num_));

            // 4. 發送訂單請求資料
            tcp_socket_.send(client_request, sizeof(Exchange::MEClientRequest));

            // 5. 更新佇列讀取索引（通知交易引擎該槽位已讀取完成）
            outgoing_requests_->updateReadIndex();

            // 6. 遞增序列號（下一條訊息使用）
            next_outgoing_seq_num_++;
        }
    }
}

/**
 * recvCallback() - TCP 接收回調函式
 *
 * 觸發時機：
 * - tcp_socket_.sendAndRecv() 偵測到新資料到達時自動呼叫
 *
 * 職責：
 * 1. 從 TCP 緩衝區讀取訊息
 * 2. 反序列化為 OMClientResponse 結構
 * 3. 驗證 client_id 和序列號
 * 4. 將有效回應寫入 incoming_responses_ 佇列
 * 5. 處理不完整訊息（留在緩衝區等待下一次）
 *
 * 訊息格式（從交易所接收）：
 * 每個回應：sizeof(OMClientResponse) bytes
 * 包含：[序列號][ClientResponse 資料]
 *
 * 錯誤處理：
 * - Client ID 不符 → 記錄 ERROR，跳過該訊息
 * - 序列號不符 → 記錄 ERROR，跳過該訊息（可能遺失訊息）
 * - 緩衝區不足 → 保留在緩衝區，等待下一次接收
 *
 * 效能考量：
 * - 批次處理多個回應（減少函式呼叫）
 * - memcpy 處理不完整訊息（避免複雜邏輯）
 * - 零拷貝到 Lock-Free Queue（move 語意）
 */
auto OrderGateway::recvCallback(TCPSocket* socket,
                                Nanos rx_time) noexcept -> void
{
    // 記錄接收事件（包含 socket FD 和緩衝區長度）
    logger_.log("%:% %() % Received socket:% len:% %\n", __FILE__, __LINE__,
                __FUNCTION__, Common::getCurrentTimeStr(&time_str_), socket->socket_fd_,
                socket->next_rcv_valid_index_, rx_time);

    // 檢查緩衝區是否包含至少一個完整訊息
    if (socket->next_rcv_valid_index_ >= sizeof(Exchange::OMClientResponse)) {
        size_t i = 0;  // 當前處理位置（bytes）

        // 批次處理所有完整訊息
        for (; i + sizeof(Exchange::OMClientResponse) <= socket->next_rcv_valid_index_;
             i += sizeof(Exchange::OMClientResponse)) {

            // 1. 反序列化訊息（零拷貝，直接使用緩衝區記憶體）
            auto response = reinterpret_cast<const Exchange::OMClientResponse*>
                            (socket->inbound_data_.data() + i);

            logger_.log("%:% %() % Received %\n", __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_), response->toString());

            // 2. 驗證 Client ID（防止交易所路由錯誤）
            if (response->me_client_response_.client_id_ !=
                client_id_) {
                // 這不應該發生（TCP 連接是點對點的）
                logger_.log("%:% %() % ERROR Incorrect client id. ClientId expected:% received:%.\n",
                            __FILE__, __LINE__, __FUNCTION__,
                            Common::getCurrentTimeStr(&time_str_), client_id_,
                            response->me_client_response_.client_id_);
                continue;  // 跳過錯誤訊息，繼續處理下一個
            }

            // 3. 驗證序列號（偵測遺失訊息）
            if (response->seq_num_ !=
                next_exp_seq_num_) {
                // 這不應該發生（TCP 保證可靠傳輸）
                // 如果發生，可能是交易所 bug 或網路異常
                logger_.log("%:% %() % ERROR Incorrect sequence number. ClientId:%. SeqNum expected:% received:%.\n",
                            __FILE__, __LINE__, __FUNCTION__,
                            Common::getCurrentTimeStr(&time_str_), client_id_, next_exp_seq_num_,
                            response->seq_num_);
                continue;  // 跳過錯誤訊息
            }

            // 4. 序列號驗證通過，遞增預期序列號
            ++next_exp_seq_num_;

            // 5. 寫入 Lock-Free Queue（通知交易引擎）
            auto next_write = incoming_responses_->getNextToWriteTo();
            *next_write = std::move(response->me_client_response_);  // 移動語意（零拷貝）
            incoming_responses_->updateWriteIndex();
        }

        // 6. 處理不完整訊息（將剩餘資料移到緩衝區開頭）
        //    例如：接收到 1.5 個訊息，保留 0.5 個等待下一次接收
        memcpy(socket->inbound_data_.data(), socket->inbound_data_.data() + i,
               socket->next_rcv_valid_index_ - i);
        socket->next_rcv_valid_index_ -= i;  // 更新有效資料長度
    }
}
}
