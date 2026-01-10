// client_response.h: 交易所回應協議定義
//
// 職責：
// - 定義交易所 → 客戶端的訂單執行回應訊息格式
// - 支援四種狀態：ACCEPTED（已接受）、CANCELED（已取消）、FILLED（已成交）、CANCEL_REJECTED（取消被拒）
// - 使用 Lock-Free Queue 傳輸，確保低延遲
//
// 通訊流程：
// ┌────────────────┐                    ┌────────────┐
// │ Matching Engine│ ── MEClientResponse → │   Client   │
// └────────────────┘                    └────────────┘
//         ▲                                      │
//         │                                      │
//         └──────── MEClientRequest ─────────────┘
//
// ⚡ 低延遲設計：
// - #pragma pack(1)：緊密封裝，減少記憶體和網路開銷
// - uint8_t enum：最小化型別大小（1 byte）
// - Lock-Free Queue：無鎖訊息傳遞
// - exec_qty + leaves_qty：無需重複查詢訂單狀態
//
// ⚠️ 協議不變性：
// - 此協議定義在客戶端和交易所之間共享
// - 修改時必須確保二進位相容性（Binary Compatibility）
// - 欄位順序不可改變（影響記憶體佈局）

#pragma once

#include <sstream>

#include "common/types.h"
#include "common/lf_queue.h"

using namespace Common;

namespace Exchange
{
// #pragma pack(1)：緊密封裝
// ⚡ 移除結構填充（Padding），減少記憶體使用
// ⚠️ 注意：可能影響對齊效能，需在空間與速度間權衡
#pragma pack(push, 1)

// ClientResponseType: 客戶端回應類型
//
// 支援的狀態：
// - ACCEPTED: 訂單已接受（進入訂單簿）
// - CANCELED: 訂單已取消（成功移除）
// - FILLED: 訂單已成交（全部或部分）
// - CANCEL_REJECTED: 取消請求被拒（訂單不存在或已成交）
// - INVALID: 無效回應（初始值或錯誤狀態）
//
// 訂單生命週期：
// NEW → ACCEPTED → FILLED（成交）
//                 ↘ CANCELED（取消）
//
// CANCEL → CANCEL_REJECTED（失敗）
//         ↘ CANCELED（成功）
//
// ⚡ 使用 uint8_t（1 byte）：
// - 最小化網路傳輸開銷
// - 256 種狀態類型已足夠（當前只用 5 種）
enum class ClientResponseType : uint8_t {
    INVALID = 0,         // 無效回應（預設值）
    ACCEPTED = 1,        // 訂單已接受
    CANCELED = 2,        // 訂單已取消
    FILLED = 3,          // 訂單已成交（全部或部分）
    CANCEL_REJECTED = 4  // 取消請求被拒絕
};

// clientResponseTypeToString: 回應類型轉字串（除錯用）
//
// 用途：
// - 日誌輸出：toString() 方法使用
// - 錯誤訊息：顯示人類可讀的回應類型
// - 除錯工具：追蹤訂單執行狀態
//
// ⚡ inline 優化：
// - 編譯器會內聯此函式，避免函式呼叫開銷
// - 適合頻繁呼叫的小函式
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

    return "UNKNOWN";  // 不應該到達這裡（防禦性程式設計）
}

// MEClientResponse: 撮合引擎客戶端回應結構
//
// 用途：
// - 從 Matching Engine 發送執行結果給客戶端
// - 透過 Lock-Free Queue 傳遞給 Order Server
// - Order Server 轉發給對應的客戶端連線
//
// 欄位說明：
// - type_: 回應類型（ACCEPTED, CANCELED, FILLED, CANCEL_REJECTED）
// - client_id_: 客戶端 ID（用於路由回應）
// - ticker_id_: 交易標的 ID
// - client_order_id_: 客戶端訂單 ID（客戶端用於對應請求）
// - market_order_id_: 市場訂單 ID（撮合引擎內部 ID）
// - side_: 買賣方向
// - price_: 成交價格
// - exec_qty_: 本次成交數量（Executed Quantity）
// - leaves_qty_: 剩餘未成交數量（Leaves Quantity）
//
// 關鍵欄位解釋：
// ┌──────────────┬──────────────────────────────────┐
// │ exec_qty_    │ 本次成交數量                     │
// │ leaves_qty_  │ 剩餘未成交數量                   │
// └──────────────┴──────────────────────────────────┘
// 範例：提交 100 股訂單
// - ACCEPTED: exec_qty=0, leaves_qty=100（全部待成交）
// - FILLED: exec_qty=30, leaves_qty=70（部分成交 30 股）
// - FILLED: exec_qty=70, leaves_qty=0（全部成交）
//
// 雙重 Order ID 設計：
// - client_order_id_: 客戶端自行分配（追蹤用）
// - market_order_id_: 撮合引擎分配（系統內部用）
// - 好處：客戶端可用自己的 ID 對應回應，無需維護映射表
//
// ⚡ 效能優化：
// - 緊密封裝（pack(1)）：減少網路傳輸
// - 預設值初始化：使用 *_INVALID 常數
// - POD 型別：Plain Old Data，可安全 memcpy
// - exec_qty + leaves_qty：避免重複查詢訂單狀態
//
// ⚠️ 使用注意：
// - FILLED 回應可能多次觸發（部分成交）
// - leaves_qty = 0 表示訂單完全成交
// - CANCEL_REJECTED 表示訂單已不存在或已完全成交
struct MEClientResponse {
    ClientResponseType type_ = ClientResponseType::INVALID;  // 回應類型
    ClientId client_id_ = ClientId_INVALID;      // 客戶端 ID
    TickerId ticker_id_ = TickerId_INVALID;      // 交易標的 ID
    OrderId client_order_id_ = OrderId_INVALID;  // 客戶端訂單 ID
    OrderId market_order_id_ = OrderId_INVALID;  // 市場訂單 ID
    Side side_ = Side::INVALID;                  // 買賣方向
    Price price_ = Price_INVALID;                // 成交價格
    Qty exec_qty_ = Qty_INVALID;                 // 本次成交數量
    Qty leaves_qty_ = Qty_INVALID;               // 剩餘未成交數量

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

#pragma pack(pop)

typedef LFQueue<MEClientResponse> ClientResponseLFQueue;
}
