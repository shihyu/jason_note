#include "me_order.h"

namespace Exchange
{
// ============================================================================
// MEOrder::toString() - 撮合引擎訂單物件序列化為字串
// ============================================================================
//
// 📌 功能：將撮合引擎內部的訂單物件轉換為人類可讀的字串格式
//
// 🔗 與 Trading::MarketOrder 的差異：
// - MEOrder：交易所撮合引擎端的訂單（伺服器端）
// - MarketOrder：交易客戶端的訂單簿副本（客戶端）
// - MEOrder 包含額外的客戶端 ID 和雙重訂單 ID（client_order_id_ + market_order_id_）
//
// 用途：
// 1. 日誌記錄（Logger）：追蹤訂單生命週期
// 2. 除錯輸出：觀察撮合引擎內部狀態
// 3. 審計追蹤：記錄所有訂單操作
// 4. 單元測試：驗證訂單資料正確性
//
// ⚠️ 效能警告：
// - std::stringstream：動態記憶體分配（heap allocation）
// - 字串拼接：多次複製操作
// - **絕對不可在撮合熱路徑中呼叫！**
// - 僅限除錯、日誌記錄、測試場景使用
//
// 📊 輸出格式範例：
// MEOrder[ticker:AAPL cid:1 oid:12345 moid:67890 side:BUY price:100.50 qty:500 prio:1234567890 prev:67889 next:67891]
//
// 欄位說明：
// - ticker: 交易標的 ID
// - cid: 客戶端 ID（Client ID）
// - oid: 客戶端訂單 ID（Client Order ID）
// - moid: 市場訂單 ID（Market Order ID，撮合引擎內部 ID）
// - side: 買賣方向（BUY/SELL）
// - price: 訂單價格
// - qty: 訂單數量
// - prio: 優先權（Priority，通常是接收時間戳）
// - prev: 前一個訂單的 ID（環狀雙向鏈結串列）
// - next: 下一個訂單的 ID（環狀雙向鏈結串列）
//
// 🔗 環狀鏈結串列資訊：
// - prev/next 用於同價位訂單的 FIFO 排序（Price-Time Priority）
// - OrderId_INVALID 表示該方向沒有訂單（nullptr）
//
// ⚡ 效能數據：
// - 執行時間：約 1-5 μs（微秒）
// - 記憶體分配：約 100-200 bytes（stringstream 緩衝區）
// - 與撮合引擎相比：慢 100-1000 倍（撮合約 1-10 ns）
//
// 📌 使用建議：
// - 只在日誌級別為 DEBUG 時呼叫
// - 不要在 MEOrderBook::match() 中呼叫
// - 不要在 addOrder()/removeOrder() 熱路徑中呼叫
auto MEOrder::toString() const -> std::string
{
    std::stringstream ss;
    ss << "MEOrder" << "["
       << "ticker:" << tickerIdToString(ticker_id_) << " "
       << "cid:" << clientIdToString(client_id_) << " "
       << "oid:" << orderIdToString(client_order_id_) << " "
       << "moid:" << orderIdToString(market_order_id_) << " "
       << "side:" << sideToString(side_) << " "
       << "price:" << priceToString(price_) << " "
       << "qty:" << qtyToString(qty_) << " "
       << "prio:" << priorityToString(priority_) << " "
       << "prev:" << orderIdToString(prev_order_ ? prev_order_->market_order_id_ :
                                     OrderId_INVALID) << " "
       << "next:" << orderIdToString(next_order_ ? next_order_->market_order_id_ :
                                     OrderId_INVALID) << "]";

    return ss.str();
}
}
