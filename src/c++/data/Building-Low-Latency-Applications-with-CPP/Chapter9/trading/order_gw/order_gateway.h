#pragma once

// 訂單閘道：策略端與交易所間的低延遲轉送層。
// ⚡ 效能關鍵：序列號檢測 + 非阻塞收發。
// ⚠️ 注意：斷線重連與狀態恢復。

#include <functional>

#include "common/thread_utils.h"
#include "common/macros.h"
#include "common/tcp_server.h"

#include "exchange/order_server/client_request.h"
#include "exchange/order_server/client_response.h"

namespace Trading
{
class OrderGateway
{
public:
    OrderGateway(ClientId client_id,
                 Exchange::ClientRequestLFQueue* client_requests,
                 Exchange::ClientResponseLFQueue* client_responses,
                 std::string ip, const std::string& iface, int port);

    ~OrderGateway()
    {
        stop();

        using namespace std::literals::chrono_literals;
        std::this_thread::sleep_for(5s);
    }

    auto start()
    {
        run_ = true;
        ASSERT(tcp_socket_.connect(ip_, iface_, port_, false) >= 0,
               "Unable to connect to ip:" + ip_ + " port:" + std::to_string(
                   port_) + " on iface:" + iface_ + " error:" + std::string(std::strerror(errno)));
        ASSERT(Common::createAndStartThread(-1, "Trading/OrderGateway", [this]() {
            // ⚡ 關鍵路徑：函式內避免鎖/分配，保持快取局部性。
            run();
        }) != nullptr, "Failed to start OrderGateway thread.");
    }

    auto stop() -> void
    {
        run_ = false;
    }

    // Deleted default, copy & move constructors and assignment-operators.
    OrderGateway() = delete;

    OrderGateway(const OrderGateway&) = delete;

    OrderGateway(const OrderGateway&&) = delete;

    OrderGateway& operator=(const OrderGateway&) = delete;

    OrderGateway& operator=(const OrderGateway&&) = delete;

private:
    const ClientId client_id_;

    std::string ip_;
    const std::string iface_;
    const int port_ = 0;

    Exchange::ClientRequestLFQueue* outgoing_requests_ = nullptr;
    Exchange::ClientResponseLFQueue* incoming_responses_ = nullptr;

    volatile bool run_ = false;

    std::string time_str_;
    Logger logger_;

    size_t next_outgoing_seq_num_ = 1;
    size_t next_exp_seq_num_ = 1;
    Common::TCPSocket tcp_socket_;

private:
    auto run() noexcept -> void;

    auto recvCallback(TCPSocket* socket, Nanos rx_time) noexcept -> void;
};
}
