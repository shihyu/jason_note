#pragma once

#include <sstream>

#include "common/types.h"
#include "common/lf_queue.h"

using namespace Common;

namespace Exchange
{
enum class ClientRequestType : uint8_t {
    INVALID = 0,
    NEW = 1,       // 新增訂單
    CANCEL = 2     // 取消訂單
};

inline std::string clientRequestTypeToString(ClientRequestType type)
{
    switch (type) {
    case ClientRequestType::NEW:
        return "NEW";

    case ClientRequestType::CANCEL:
        return "CANCEL";

    case ClientRequestType::INVALID:
        return "INVALID";
    }

    return "UNKNOWN";
}

// ⚡ 緊湊封裝 (Tight Packing): 強制 1-byte 對齊
// 目的: 
// 1. 減少網路傳輸量 (避免 padding)
// 2. 確保跨平台/語言的記憶體佈局一致
#pragma pack(push, 1)

// 撮合引擎客戶端請求 (Matching Engine Client Request)
// 這是透過 Lock-Free Queue 傳遞給 ME 的內部格式
struct MEClientRequest {
    ClientRequestType type_ = ClientRequestType::INVALID;

    ClientId client_id_ = ClientId_INVALID;
    TickerId ticker_id_ = TickerId_INVALID;
    OrderId order_id_ = OrderId_INVALID;
    Side side_ = Side::INVALID;
    Price price_ = Price_INVALID;
    Qty qty_ = Qty_INVALID;

    auto toString() const
    {
        std::stringstream ss;
        ss << "MEClientRequest"
           << " ["
           << "type:" << clientRequestTypeToString(type_)
           << " client:" << clientIdToString(client_id_)
           << " ticker:" << tickerIdToString(ticker_id_)
           << " oid:" << orderIdToString(order_id_)
           << " side:" << sideToString(side_)
           << " qty:" << qtyToString(qty_)
           << " price:" << priceToString(price_)
           << "]";
        return ss.str();
    }
};

// 訂單管理客戶端請求 (Order Manager Client Request)
// 這是從網路上接收到的原始格式 (包含序列號)
struct OMClientRequest {
    size_t seq_num_ = 0;              // ⚡ 序列號: 用於檢測丟包與重複
    MEClientRequest me_client_request_; // 實際請求內容

    auto toString() const
    {
        std::stringstream ss;
        ss << "OMClientRequest"
           << " ["
           << "seq:" << seq_num_
           << " " << me_client_request_.toString()
           << "]";
        return ss.str();
    }
};

#pragma pack(pop)

typedef LFQueue<MEClientRequest> ClientRequestLFQueue;
}
