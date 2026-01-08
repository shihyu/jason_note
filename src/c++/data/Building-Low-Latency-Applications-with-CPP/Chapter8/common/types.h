#pragma once

#include <cstdint>
#include <limits>
#include <sstream>
#include <array>

#include "common/macros.h"

namespace Common
{
// ============================================================================
// 系統容量限制常數 (System Limits)
// ============================================================================
// 📌 設計原則：
// 1. 預先分配：所有陣列大小在編譯期決定，避免執行期動態分配 (malloc/new)
// 2. 2 的冪次方：便於位元運算優化 (雖現代編譯器已足夠聰明，但保持習慣)
constexpr size_t ME_MAX_TICKERS = 8;              // 最大支援商品數量

constexpr size_t ME_MAX_CLIENT_UPDATES = 256 * 1024; // 客戶端更新佇列大小
constexpr size_t ME_MAX_MARKET_UPDATES = 256 * 1024; // 市場更新佇列大小

constexpr size_t ME_MAX_NUM_CLIENTS = 256;        // 最大連線客戶數
constexpr size_t ME_MAX_ORDER_IDS = 1024 * 1024;  // 每個客戶最大訂單 ID (1M)
constexpr size_t ME_MAX_PRICE_LEVELS = 256;       // 訂單簿最大價格層級深度

// ============================================================================
// 基本型別定義 (Basic Types)
// ============================================================================

// 訂單 ID
// ⚠️ 使用 uint64_t 避免溢位
typedef uint64_t OrderId;
constexpr auto OrderId_INVALID = std::numeric_limits<OrderId>::max();

inline auto orderIdToString(OrderId order_id) -> std::string
{
    // ⚡ UNLIKELY 優化：絕大多數情況下 ID 都是有效的
    if (UNLIKELY(order_id == OrderId_INVALID)) {
        return "INVALID";
    }

    return std::to_string(order_id);
}

// 商品 ID (Ticker)
typedef uint32_t TickerId;
constexpr auto TickerId_INVALID = std::numeric_limits<TickerId>::max();

inline auto tickerIdToString(TickerId ticker_id) -> std::string
{
    if (UNLIKELY(ticker_id == TickerId_INVALID)) {
        return "INVALID";
    }

    return std::to_string(ticker_id);
}

// 客戶 ID
typedef uint32_t ClientId;
constexpr auto ClientId_INVALID = std::numeric_limits<ClientId>::max();

inline auto clientIdToString(ClientId client_id) -> std::string
{
    if (UNLIKELY(client_id == ClientId_INVALID)) {
        return "INVALID";
    }

    return std::to_string(client_id);
}

// 價格 (Price)
// ⚡ 效能關鍵：使用 int64_t 而非 double
// 1. 避免浮點數精度問題 (Floating Point Precision Issues)
// 2. 整數運算比浮點數快
// 3. 通常代表 "ticks" (最小價格變動單位) 或乘以倍數後的金額
typedef int64_t Price;
constexpr auto Price_INVALID = std::numeric_limits<Price>::max();

inline auto priceToString(Price price) -> std::string
{
    if (UNLIKELY(price == Price_INVALID)) {
        return "INVALID";
    }

    return std::to_string(price);
}

// 數量 (Quantity)
typedef uint32_t Qty;
constexpr auto Qty_INVALID = std::numeric_limits<Qty>::max();

inline auto qtyToString(Qty qty) -> std::string
{
    if (UNLIKELY(qty == Qty_INVALID)) {
        return "INVALID";
    }

    return std::to_string(qty);
}

// 優先級 (Priority)
// 用於 Price-Time Priority 撮合規則中的時間優先權
// 數值越小代表越早到達，優先級越高
typedef uint64_t Priority;
constexpr auto Priority_INVALID = std::numeric_limits<Priority>::max();

inline auto priorityToString(Priority priority) -> std::string
{
    if (UNLIKELY(priority == Priority_INVALID)) {
        return "INVALID";
    }

    return std::to_string(priority);
}

// 買賣方向 (Side)
// 使用 int8_t 節省空間 (1 byte)
enum class Side : int8_t {
    INVALID = 0,
    BUY = 1,
    SELL = -1,
    MAX = 2
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

    case Side::MAX:
        return "MAX";
    }

    return "UNKNOWN";
}

inline constexpr auto sideToIndex(Side side) noexcept
{
    return static_cast<size_t>(side) + 1;
}

inline constexpr auto sideToValue(Side side) noexcept
{
    return static_cast<int>(side);
}

enum class AlgoType : int8_t {
    INVALID = 0,
    RANDOM = 1,
    MAKER = 2,
    TAKER = 3,
    MAX = 4
};

inline auto algoTypeToString(AlgoType type) -> std::string
{
    switch (type) {
    case AlgoType::RANDOM:
        return "RANDOM";

    case AlgoType::MAKER:
        return "MAKER";

    case AlgoType::TAKER:
        return "TAKER";

    case AlgoType::INVALID:
        return "INVALID";

    case AlgoType::MAX:
        return "MAX";
    }

    return "UNKNOWN";
}

inline auto stringToAlgoType(const std::string& str) -> AlgoType
{
    for (auto i = static_cast<int>(AlgoType::INVALID);
         i <= static_cast<int>(AlgoType::MAX); ++i) {
        const auto algo_type = static_cast<AlgoType>(i);

        if (algoTypeToString(algo_type) == str) {
            return algo_type;
        }
    }

    return AlgoType::INVALID;
}

struct RiskCfg {
    Qty max_order_size_ = 0;
    Qty max_position_ = 0;
    double max_loss_ = 0;

    auto toString() const
    {
        std::stringstream ss;

        ss << "RiskCfg{"
           << "max-order-size:" << qtyToString(max_order_size_) << " "
           << "max-position:" << qtyToString(max_position_) << " "
           << "max-loss:" << max_loss_
           << "}";

        return ss.str();
    }
};

struct TradeEngineCfg {
    Qty clip_ = 0;
    double threshold_ = 0;
    RiskCfg risk_cfg_;

    auto toString() const
    {
        std::stringstream ss;
        ss << "TradeEngineCfg{"
           << "clip:" << qtyToString(clip_) << " "
           << "thresh:" << threshold_ << " "
           << "risk:" << risk_cfg_.toString()
           << "}";

        return ss.str();
    }
};

typedef std::array<TradeEngineCfg, ME_MAX_TICKERS> TradeEngineCfgHashMap;
}
