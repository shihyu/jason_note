// ============================================================================
// MarketOrder 實作檔案
// ============================================================================
//
// 職責:
// - 實作 MarketOrder::toString() 序列化方法（用於日誌與除錯）
//
// 說明:
// MarketOrder 是 Trading Client 觀察到的市場訂單（來自 Order Book Update）
// 此檔案僅包含字串序列化函式，其他建構與資料成員定義在 header 中。
//
// 與 Chapter6 的 MEOrder 對比:
// - MEOrder:    Exchange 側的訂單（包含執行狀態、Fill 資訊）
// - MarketOrder: Trading Client 側的訂單（市場可見部分, 簡化版）
//
// ============================================================================

#include "market_order.h"

namespace Trading
{
// ============================================================================
// 序列化為字串（用於日誌輸出與除錯）
// ============================================================================
//
// 輸出格式:
// MarketOrder[oid:123 side:BUY price:100.50 qty:200 prio:12345 prev:122 next:124]
//
// 欄位說明:
// - oid:   Order ID（訂單唯一識別碼）
// - side:  買賣方向（BUY/SELL）
// - price: 限價
// - qty:   數量
// - prio:  優先權（Price-Time Priority, 越小越優先）
// - prev:  雙向鏈結串列前一個節點的 Order ID（同價位 FIFO 順序）
// - next:  雙向鏈結串列下一個節點的 Order ID
//
// ⚠️ 效能考量:
// - 此函式使用 std::stringstream (動態記憶體分配)
// - 僅用於日誌與除錯, 不應在交易主迴圈（Hot Path）中呼叫
// - 生產環境應使用二進位日誌系統（參考 Chapter4 的 Logger）
//
auto MarketOrder::toString() const -> std::string
{
    std::stringstream ss;
    ss << "MarketOrder" << "["
       << "oid:" << orderIdToString(order_id_) << " "        // 訂單 ID
       << "side:" << sideToString(side_) << " "              // 買/賣方向
       << "price:" << priceToString(price_) << " "           // 限價
       << "qty:" << qtyToString(qty_) << " "                 // 數量
       << "prio:" << priorityToString(priority_) << " "      // 優先權 (時間戳)
       << "prev:" << orderIdToString(prev_order_ ? prev_order_->order_id_ :
                                     OrderId_INVALID) << " "  // 前一個訂單
       << "next:" << orderIdToString(next_order_ ? next_order_->order_id_ :
                                     OrderId_INVALID) << "]"; // 下一個訂單

    return ss.str();
}
} // namespace Trading
