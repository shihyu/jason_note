#pragma once

#include <sstream>

#include "common/types.h"
#include "common/lf_queue.h"

using namespace Common;

namespace Exchange
{
enum class ClientResponseType : uint8_t {
    INVALID = 0,
    ACCEPTED = 1,         // 訂單已接受 (新增成功)
    CANCELED = 2,         // 訂單已取消
    FILLED = 3,           // 訂單已成交 (部分或全部)
    CANCEL_REJECTED = 4   // 取消被拒絕 (e.g. 訂單已成交或不存在)
};

inline std::string clientResponseTypeToString(ClientResponseType type)
{
    switch (type) {
    case ClientResponseType::ACCEPTED:
        return "ACCEPTED";

    case ClientResponseType::CANCELED:
        return "CANCELED";

    case ClientResponseType::FILLED:
        return "FILLED";

    case ClientResponseType::CANCEL_REJECTED:
        return "CANCEL_REJECTED";

    case ClientResponseType::INVALID:
        return "INVALID";
    }

    return "UNKNOWN";
}

// ⚡ 緊湊封裝 (Tight Packing): 強制 1-byte 對齊
#pragma pack(push, 1)

// 撮合引擎客戶端回應 (Matching Engine Client Response)
// 這是透過 Lock-Free Queue 從 ME 傳回給 Order Server 的格式
struct MEClientResponse {
    ClientResponseType type_ = ClientResponseType::INVALID;
    ClientId client_id_ = ClientId_INVALID;
    TickerId ticker_id_ = TickerId_INVALID;
    OrderId client_order_id_ = OrderId_INVALID; // 客戶端定義的 Order ID
    OrderId market_order_id_ = OrderId_INVALID; // 交易所分配的 Order ID (Unique)
    Side side_ = Side::INVALID;
    Price price_ = Price_INVALID;
    Qty exec_qty_ = Qty_INVALID;    // 本次成交數量
    Qty leaves_qty_ = Qty_INVALID;  // 剩餘未成交數量

    auto toString() const
    {
        std::stringstream ss;
        ss << "MEClientResponse"
           << " ["
           << "type:" << clientResponseTypeToString(type_)
           << " client:" << clientIdToString(client_id_)
           << " ticker:" << tickerIdToString(ticker_id_)
           << " coid:" << orderIdToString(client_order_id_)
           << " moid:" << orderIdToString(market_order_id_)
           << " side:" << sideToString(side_)
           << " exec_qty:" << qtyToString(exec_qty_)
           << " leaves_qty:" << qtyToString(leaves_qty_)
           << " price:" << priceToString(price_)
           << "]";
        return ss.str();
    }
};

// 訂單管理客戶端回應 (Order Manager Client Response)
// 這是透過 TCP 發送回客戶端的格式 (包含序列號)
struct OMClientResponse {
    size_t seq_num_ = 0;              // ⚡ 序列號: 供客戶端檢測丟包
    MEClientResponse me_client_response_; // 實際回應內容

    auto toString() const
    {
        std::stringstream ss;
        ss << "OMClientResponse"
           << " ["
           << "seq:" << seq_num_
           << " " << me_client_response_.toString()
           << "]";
        return ss.str();
    }
};

#pragma pack(pop)

typedef LFQueue<MEClientResponse> ClientResponseLFQueue;
}
