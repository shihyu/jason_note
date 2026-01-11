/**
 * @file market_order.cpp
 * @brief 客戶端市場訂單（Market Order）實作檔案
 *
 * 功能：
 * - 提供訂單物件的字串序列化方法（toString）
 * - 用於日誌記錄、除錯、監控
 *
 * 與 Exchange::MEOrder 的差異：
 * - MarketOrder：客戶端訂單簿中的訂單（本地副本）
 * - MEOrder：交易所端訂單簿中的訂單（權威版本）
 * - MarketOrder 缺少 client_id、ticker_id 欄位（只關心市場訂單 ID）
 *
 * 設計原則：
 * - 簡單實作：僅包含輔助方法，無複雜邏輯
 * - 非效能關鍵路徑：toString 僅用於日誌和除錯
 *
 * 效能考量：
 * - 使用 std::stringstream（涉及記憶體分配）
 * - 不應在交易時段熱路徑中頻繁呼叫
 * - 適合用於低頻事件記錄
 */

#include "market_order.h"

namespace Trading
{
/**
 * toString() - 將訂單物件轉換為可讀字串
 *
 * @return 訂單的字串表示，包含所有欄位資訊
 *
 * 輸出格式：
 * ```
 * MarketOrder[oid:50000 side:BUY price:150 qty:500 prio:1 prev:49999 next:50001]
 * ```
 *
 * 欄位說明：
 * - oid: 市場訂單 ID（Market Order ID）
 * - side: 買賣方向（BUY/SELL）
 * - price: 訂單價格
 * - qty: 訂單數量（剩餘未成交數量）
 * - prio: 優先序號（同價格按時間順序，越小越優先）
 * - prev: 前一個訂單的市場訂單 ID（環狀鏈表）
 * - next: 下一個訂單的市場訂單 ID（環狀鏈表）
 *
 * 與 Exchange::MEOrder 的欄位差異：
 * - 缺少 ticker: 商品識別碼（客戶端已知商品）
 * - 缺少 cid: 客戶端識別碼（客戶端不關心其他客戶）
 * - 缺少 client_order_id: 客戶端訂單 ID（客戶端只關心市場訂單 ID）
 *
 * 訂單鏈表指標：
 * - prev 和 next 指向同價格層級的其他訂單
 * - 若指標為 nullptr，輸出 INVALID
 * - 環狀鏈表：最後一個訂單的 next 指向第一個訂單
 *
 * 使用場景：
 * 1. 日誌記錄：記錄本地訂單簿更新事件
 * 2. 除錯：檢查訂單簿同步狀態
 * 3. 監控：人工檢查本地訂單簿
 * 4. 測試：驗證訂單簿同步正確性
 *
 * 效能特性：
 * - 非 noexcept：std::stringstream 可能拋出例外
 * - 時間複雜度：O(1)（固定欄位數量）
 * - 記憶體分配：stringstream 內部分配記憶體
 * - 不應在高頻路徑中呼叫（例如訂單簿更新迴圈內）
 *
 * 注意事項：
 * - const 函式：不修改訂單狀態
 * - 使用輔助函式轉換型別（orderIdToString、sideToString 等）
 * - 輸出格式固定，便於日誌解析和監控工具處理
 */
auto MarketOrder::toString() const -> std::string
{
    std::stringstream ss;
    ss << "MarketOrder" << "["
       << "oid:" << orderIdToString(order_id_) << " "
       << "side:" << sideToString(side_) << " "
       << "price:" << priceToString(price_) << " "
       << "qty:" << qtyToString(qty_) << " "
       << "prio:" << priorityToString(priority_) << " "
       << "prev:" << orderIdToString(prev_order_ ? prev_order_->order_id_ :
                                     OrderId_INVALID) << " "
       << "next:" << orderIdToString(next_order_ ? next_order_->order_id_ :
                                     OrderId_INVALID) << "]";

    return ss.str();
}
}
