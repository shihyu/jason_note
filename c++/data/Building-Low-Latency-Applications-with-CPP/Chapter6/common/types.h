// ============================================================================
// 系統基本型別定義 (Common Types)
// ============================================================================
// 📌 設計原則：
// 1. 型別安全：使用 typedef 明確語義
// 2. 預先分配：編譯期常數避免執行期動態分配
// 3. 無效值標記：使用 _INVALID 常數表示無效狀態

#pragma once

#include <cstdint>
#include <limits>

#include "common/macros.h"

namespace Common
{
// ============================================================================
// 系統容量限制常數
// ============================================================================
constexpr size_t ME_MAX_TICKERS = 8;              // 最大支援商品數量

constexpr size_t ME_MAX_CLIENT_UPDATES = 256 * 1024; // 客戶端更新佇列大小
constexpr size_t ME_MAX_MARKET_UPDATES = 256 * 1024; // 市場更新佇列大小

constexpr size_t ME_MAX_NUM_CLIENTS = 256;        // 最大連線客戶數
constexpr size_t ME_MAX_ORDER_IDS = 1024 * 1024;  // 每個客戶最大訂單 ID
constexpr size_t ME_MAX_PRICE_LEVELS = 256;       // 訂單簿最大價格層級深度

// ============================================================================
// 訂單 ID (Order ID)
// ============================================================================
typedef uint64_t OrderId;
constexpr auto OrderId_INVALID = std::numeric_limits<OrderId>::max();

inline auto orderIdToString(OrderId order_id) -> std::string
{
    if (UNLIKELY(order_id == OrderId_INVALID)) {
        return "INVALID";
    }

    return std::to_string(order_id);
}

// ============================================================================
// 商品 ID (Ticker ID)
// ============================================================================
typedef uint32_t TickerId;
constexpr auto TickerId_INVALID = std::numeric_limits<TickerId>::max();

inline auto tickerIdToString(TickerId ticker_id) -> std::string
{
    if (UNLIKELY(ticker_id == TickerId_INVALID)) {
        return "INVALID";
    }

    return std::to_string(ticker_id);
}

// ============================================================================
// 客戶 ID (Client ID)
// ============================================================================
typedef uint32_t ClientId;
constexpr auto ClientId_INVALID = std::numeric_limits<ClientId>::max();

inline auto clientIdToString(ClientId client_id) -> std::string
{
    if (UNLIKELY(client_id == ClientId_INVALID)) {
        return "INVALID";
    }

    return std::to_string(client_id);
}

// ============================================================================
// 價格 (Price)
// ============================================================================
// ⚡ 使用 int64_t 避免浮點數精度問題
// 通常代表最小價格變動單位（ticks）或乘以倍數後的金額
typedef int64_t Price;
constexpr auto Price_INVALID = std::numeric_limits<Price>::max();

inline auto priceToString(Price price) -> std::string
{
    if (UNLIKELY(price == Price_INVALID)) {
        return "INVALID";
    }

    return std::to_string(price);
}

// ============================================================================
// 數量 (Quantity)
// ============================================================================
typedef uint32_t Qty;
constexpr auto Qty_INVALID = std::numeric_limits<Qty>::max();

inline auto qtyToString(Qty qty) -> std::string
{
    if (UNLIKELY(qty == Qty_INVALID)) {
        return "INVALID";
    }

    return std::to_string(qty);
}

// ============================================================================
// 優先級 (Priority)
// ============================================================================
// 用於 Price-Time Priority 撮合規則中的時間優先權
typedef uint64_t Priority;
constexpr auto Priority_INVALID = std::numeric_limits<Priority>::max();

inline auto priorityToString(Priority priority) -> std::string
{
    if (UNLIKELY(priority == Priority_INVALID)) {
        return "INVALID";
    }

    return std::to_string(priority);
}

// ============================================================================
// 買賣方向 (Side)
// ============================================================================
// ⚡ 設計巧思：BUY=1, SELL=-1 便於倉位計算
// position_delta = qty * static_cast<int>(side)
enum class Side : int8_t {
    INVALID = 0,
    BUY = 1,
    SELL = -1
};

inline auto sideToString(Side side) -> std::string
{
    switch (side) {
    case Side::BUY:
        return "BUY";

    case Side::SELL:
        return "SELL";

    case Side::INVALID:
        return "INVALID";
    }

    return "UNKNOWN";
}
}
