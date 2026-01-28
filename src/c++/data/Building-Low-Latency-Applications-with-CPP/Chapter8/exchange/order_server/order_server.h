#pragma once

#include <functional>

#include "common/thread_utils.h"
#include "common/macros.h"
#include "common/tcp_server.h"

#include "order_server/client_request.h"
#include "order_server/client_response.h"
#include "order_server/fifo_sequencer.h"

namespace Exchange
{
// OrderServer: 訂單伺服器 (Exchange Side)
//
// 職責:
// 1. 連線管理: 接受 Trading Client 的 TCP 連線
// 2. 請求接收: 接收 NEW/CANCEL 訂單請求
// 3. 序列號管理: 驗證請求序列號 (Sequence Number), 檢測丟包或重複
// 4. 公平轉發: 透過 FIFOSequencer 排序後發送到 Matching Engine
// 5. 回應發送: 將 Matching Engine 的執行結果回傳給 Client
//
// 架構:
// Clients (TCP) ↔ OrderServer ↔ FIFOSequencer ↔ Matching Engine (Lock-Free Queue)
class OrderServer
{
public:
    OrderServer(ClientRequestLFQueue* client_requests,
                ClientResponseLFQueue* client_responses, const std::string& iface, int port);

    ~OrderServer();

    /// Start and stop the order server main thread.
    auto start() -> void;

    auto stop() -> void;

    // 主執行緒迴圈
    //
    // 流程:
    // 1. tcp_server_.poll(): 檢查網路 IO 事件 (Epoll)
    // 2. tcp_server_.sendAndRecv(): 執行收發 (觸發 recvCallback)
    // 3. 處理撮合回應: 從 outgoing_responses_ 讀取並轉發給 Client
    auto run() noexcept
    {
        logger_.log("%:% %() %\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_));

        while (run_) {
            // 1. 網路輪詢
            tcp_server_.poll();

            // 2. 接收與發送 (觸發 recvCallback → FIFOSequencer)
            tcp_server_.sendAndRecv();

            // 3. 處理撮合引擎的回應 (Matching Engine → Order Server → Client)
            for (auto client_response = outgoing_responses_->getNextToRead();
                 outgoing_responses_->size() &&
                 client_response; client_response = outgoing_responses_->getNextToRead()) {
                
                // 3a. 取得該客戶端的下一個發送序列號
                auto& next_outgoing_seq_num =
                    cid_next_outgoing_seq_num_[client_response->client_id_];
                
                logger_.log("%:% %() % Processing cid:% seq:% %\n", __FILE__, __LINE__,
                            __FUNCTION__, Common::getCurrentTimeStr(&time_str_),
                            client_response->client_id_, next_outgoing_seq_num,
                            client_response->toString());

                ASSERT(cid_tcp_socket_[client_response->client_id_] != nullptr,
                       "Dont have a TCPSocket for ClientId:" + std::to_string(
                           client_response->client_id_));
                
                // 3b. 發送序列號 + 回應內容
                cid_tcp_socket_[client_response->client_id_]->send(&next_outgoing_seq_num,
                        sizeof(next_outgoing_seq_num));
                // ⚡ Socket 收發：熱路徑避免額外拷貝。
                cid_tcp_socket_[client_response->client_id_]->send(client_response,
                        sizeof(MEClientResponse));

                outgoing_responses_->updateReadIndex();

                // 3c. 更新序列號
                ++next_outgoing_seq_num;
            }
        }
    }

    // 接收回調函式 (處理 TCP 接收到的數據)
    //
    // 邏輯:
    // 1. 解析完整封包 (OMClientRequest)
    // 2. 綁定 ClientId 與 Socket (首次連線)
    // 3. 驗證序列號 (Sequence Number Check)
    // 4. 加入 FIFOSequencer 等待排序
    //
    // ⚡ 效能關鍵: 處理 TCP 粘包 (Packet Concatenation) 與序列號檢查
    auto recvCallback(TCPSocket* socket, Nanos rx_time) noexcept
    {
        logger_.log("%:% %() % Received socket:% len:% rx:%\n", __FILE__, __LINE__,
                    __FUNCTION__, Common::getCurrentTimeStr(&time_str_),
                    socket->socket_fd_, socket->next_rcv_valid_index_, rx_time);

        if (socket->next_rcv_valid_index_ >= sizeof(OMClientRequest)) {
            size_t i = 0;

            // 循環處理接收緩衝區中的所有完整訊息
            for (; i + sizeof(OMClientRequest) <= socket->next_rcv_valid_index_;
                 i += sizeof(OMClientRequest)) {
                auto request = reinterpret_cast<const OMClientRequest*>
                               (socket->inbound_data_.data() + i);
                logger_.log("%:% %() % Received %\n", __FILE__, __LINE__, __FUNCTION__,
                            Common::getCurrentTimeStr(&time_str_), request->toString());

                // 1. 首次連接: 建立映射
                if (UNLIKELY(cid_tcp_socket_[request->me_client_request_.client_id_] ==
                             nullptr)) { // first message from this ClientId.
                    cid_tcp_socket_[request->me_client_request_.client_id_] = socket;
                }

                // 2. 安全檢查: 確保 ClientId 來自正確的 Socket
                if (cid_tcp_socket_[request->me_client_request_.client_id_] !=
                    socket) { // TODO - change this to send a reject back to the client.
                    logger_.log("%:% %() % Received ClientRequest from ClientId:% on different socket:% expected:%\n",
                                __FILE__, __LINE__, __FUNCTION__,
                                Common::getCurrentTimeStr(&time_str_), request->me_client_request_.client_id_,
                                socket->socket_fd_,
                                cid_tcp_socket_[request->me_client_request_.client_id_]->socket_fd_);
                    continue;
                }

                // 3. 序列號驗證
                auto& next_exp_seq_num =
                    cid_next_exp_seq_num_[request->me_client_request_.client_id_];

                if (request->seq_num_ !=
                    next_exp_seq_num) { // TODO - change this to send a reject back to the client.
                    logger_.log("%:% %() % Incorrect sequence number. ClientId:% SeqNum expected:% received:%\n",
                                __FILE__, __LINE__, __FUNCTION__,
                                Common::getCurrentTimeStr(&time_str_), request->me_client_request_.client_id_,
                                next_exp_seq_num, request->seq_num_);
                    continue;
                }

                ++next_exp_seq_num;

                // 4. 加入排序器
                fifo_sequencer_.addClientRequest(rx_time, request->me_client_request_);
            }

            // 移除已處理數據, 保留剩餘部分 (處理粘包)
            memcpy(socket->inbound_data_.data(), socket->inbound_data_.data() + i,
                   socket->next_rcv_valid_index_ - i);
            socket->next_rcv_valid_index_ -= i;
        }
    }

    // 接收完成回調
    //
    // 觸發時機: 完成所有 Socket 的讀取後
    // 動作: 觸發 FIFOSequencer 進行排序與發布
    auto recvFinishedCallback() noexcept
    {
        fifo_sequencer_.sequenceAndPublish();
    }

    /// Deleted default, copy & move constructors and assignment-operators.
    OrderServer() = delete;

    OrderServer(const OrderServer&) = delete;

    OrderServer(const OrderServer&&) = delete;

    OrderServer& operator=(const OrderServer&) = delete;

    OrderServer& operator=(const OrderServer&&) = delete;

private:
    const std::string iface_;
    const int port_ = 0;

    /// Lock free queue of outgoing client responses to be sent out to connected clients.
    ClientResponseLFQueue* outgoing_responses_ = nullptr;

    // ⚠️ 注意：volatile 僅防優化，非同步原語。
    volatile bool run_ = false;

    std::string time_str_;
    Logger logger_;

    /// Hash map from ClientId -> the next sequence number to be sent on outgoing client responses.
    std::array<size_t, ME_MAX_NUM_CLIENTS> cid_next_outgoing_seq_num_;

    /// Hash map from ClientId -> the next sequence number expected on incoming client requests.
    std::array<size_t, ME_MAX_NUM_CLIENTS> cid_next_exp_seq_num_;

    /// Hash map from ClientId -> TCP socket / client connection.
    std::array<Common::TCPSocket*, ME_MAX_NUM_CLIENTS> cid_tcp_socket_;

    /// TCP server instance listening for new client connections.
    Common::TCPServer tcp_server_;

    /// FIFO sequencer responsible for making sure incoming client requests are processed in the order in which they were received.
    FIFOSequencer fifo_sequencer_;
};
}
