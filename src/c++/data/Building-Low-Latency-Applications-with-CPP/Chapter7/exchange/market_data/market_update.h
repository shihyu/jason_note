#pragma once

#include <sstream>

#include "common/types.h"

using namespace Common;

namespace Exchange
{
// MarketUpdateType: 市場數據更新類型
//
// 設計原理:
// 1. 區分增量更新(ADD/MODIFY/CANCEL/TRADE)與快照控制(SNAPSHOT_START/END/CLEAR)
// 2. 使用 uint8_t 節省空間(1 byte vs 4 bytes)
//
// 使用場景: 市場數據發布系統的消息分類
enum class MarketUpdateType : uint8_t {
    INVALID = 0,
    CLEAR = 1,          // 清空訂單簿 (用於快照開始時)
    ADD = 2,            // 新增訂單 (訂單被接受且未立即成交)
    MODIFY = 3,         // 修改訂單 (部分成交後剩餘數量變動)
    CANCEL = 4,         // 取消訂單 (訂單被取消或完全成交)
    TRADE = 5,          // 成交事件 (買賣雙方訂單撮合)
    SNAPSHOT_START = 6, // 快照開始標記
    SNAPSHOT_END = 7    // 快照結束標記
};

inline std::string marketUpdateTypeToString(MarketUpdateType type)
{
    switch (type) {
    case MarketUpdateType::CLEAR:
        return "CLEAR";

    case MarketUpdateType::ADD:
        return "ADD";

    case MarketUpdateType::MODIFY:
        return "MODIFY";

    case MarketUpdateType::CANCEL:
        return "CANCEL";

    case MarketUpdateType::TRADE:
        return "TRADE";

    case MarketUpdateType::SNAPSHOT_START:
        return "SNAPSHOT_START";

    case MarketUpdateType::SNAPSHOT_END:
        return "SNAPSHOT_END";

    case MarketUpdateType::INVALID:
        return "INVALID";
    }

    return "UNKNOWN";
}

// ⚡ 緊湊封裝：消除結構體填充（padding）
// #pragma pack(push, 1) 強制 1 byte 對齊
// 效果：未封裝可能 24 bytes，封裝後 17 bytes，節省 ~29%
#pragma pack(push, 1)

// MEMarketUpdate: 撮合引擎市場數據更新
//
// 設計原理:
// 1. 緊湊封裝: 使用 #pragma pack(1) 消除填充，減少網路傳輸大小
// 2. 固定大小: 所有欄位都是固定大小，便於序列化
// 3. 零動態記憶體: 所有資料都在結構體內，可直接透過 UDP 發送
//
// 資料流向:
// Matching Engine → Lock-Free Queue → MarketDataPublisher → UDP Multicast
//
// 使用場景: 增量更新（Incremental Updates）的消息格式
struct MEMarketUpdate {
    MarketUpdateType type_ = MarketUpdateType::INVALID;  // 更新類型

    OrderId order_id_ = OrderId_INVALID;      // 訂單 ID
    TickerId ticker_id_ = TickerId_INVALID;   // 交易標的 ID
    Side side_ = Side::INVALID;               // 買/賣方向
    Price price_ = Price_INVALID;             // 價格
    Qty qty_ = Qty_INVALID;                   // 數量
    Priority priority_ = Priority_INVALID;    // 時間優先權

    auto toString() const
    {
        std::stringstream ss;
        ss << "MEMarketUpdate"
           << " ["
           << " type:" << marketUpdateTypeToString(type_)
           << " ticker:" << tickerIdToString(ticker_id_)
           << " oid:" << orderIdToString(order_id_)
           << " side:" << sideToString(side_)
           << " qty:" << qtyToString(qty_)
           << " price:" << priceToString(price_)
           << " priority:" << priorityToString(priority_)
           << "]";
        return ss.str();
    }
};

// MDPMarketUpdate: 市場數據發布器專用的更新消息
//
// 設計原理:
// 1. 序列號封裝: 在 MEMarketUpdate 基礎上添加序列號
// 2. 丟包檢測: 接收方透過序列號檢測是否有消息遺失
// 3. 亂序處理: 序列號用於重新排序收到的消息
//
// 序列號用途:
// - 檢測丟包：收到 seq=1,2,3,5 發現丟失 seq=4
// - 排序：收到 seq=5,3,4,2 重新排序為 2,3,4,5
// - 快照定位：快照 seq=1000 表示包含所有 ≤1000 的更新
//
// 使用場景: UDP Multicast 傳輸的消息格式
struct MDPMarketUpdate {
    size_t seq_num_ = 0;                      // ⚡ 序列號（單調遞增）
    MEMarketUpdate me_market_update_;         // 實際市場數據

    auto toString() const
    {
        std::stringstream ss;
        ss << "MDPMarketUpdate"
           << " ["
           << " seq:" << seq_num_
           << " " << me_market_update_.toString()
           << "]";
        return ss.str();
    }
};

#pragma pack(pop)  // 恢復預設對齊

// Lock-Free Queue 型別定義
// ⚡ SPSC 佇列: 撮合引擎 → 市場數據發布器（單生產者單消費者）
typedef Common::LFQueue<Exchange::MEMarketUpdate> MEMarketUpdateLFQueue;    // 不帶序列號（撮合引擎輸出）
typedef Common::LFQueue<Exchange::MDPMarketUpdate> MDPMarketUpdateLFQueue;  // 帶序列號（發布器 → 快照合成器）
}
