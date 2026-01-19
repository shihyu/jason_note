// 訂單伺服器主流程：接收、排序、轉送。
// ⚡ 效能關鍵：最小化拷貝與 syscall 次數。
// ⚠️ 注意：TCP 粘包與半包處理。

#include "order_server.h"

namespace Exchange
{
OrderServer::OrderServer(ClientRequestLFQueue* client_requests,
                         ClientResponseLFQueue* client_responses, const std::string& iface, int port)
    : iface_(iface), port_(port), outgoing_responses_(client_responses),
      logger_("exchange_order_server.log"),
      tcp_server_(logger_), fifo_sequencer_(client_requests, &logger_)
{
    cid_next_outgoing_seq_num_.fill(1);
    cid_next_exp_seq_num_.fill(1);
    cid_tcp_socket_.fill(nullptr);

    tcp_server_.recv_callback_ = [this](auto socket, auto rx_time) {
        // ⚡ 關鍵路徑：函式內避免鎖/分配，保持快取局部性。
        recvCallback(socket, rx_time);
    };
    tcp_server_.recv_finished_callback_ = [this]() {
        recvFinishedCallback();
    };
}

OrderServer::~OrderServer()
{
    stop();

    using namespace std::literals::chrono_literals;
    std::this_thread::sleep_for(1s);
}

/// Start and stop the order server main thread.
auto OrderServer::start() -> void
{
    run_ = true;
    tcp_server_.listen(iface_, port_);

    ASSERT(Common::createAndStartThread(-1, "Exchange/OrderServer", [this]() {
        run();
    }) != nullptr, "Failed to start OrderServer thread.");
}

auto OrderServer::stop() -> void
{
    run_ = false;
}
}
