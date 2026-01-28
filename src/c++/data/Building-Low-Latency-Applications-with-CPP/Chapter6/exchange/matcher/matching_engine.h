#pragma once

#include "common/thread_utils.h"
#include "common/lf_queue.h"
#include "common/macros.h"

#include "order_server/client_request.h"
#include "order_server/client_response.h"
#include "market_data/market_update.h"

#include "me_order_book.h"

namespace Exchange
{
// MatchingEngine: 撮合引擎主控制器
//
// 設計原理:
// 1. 事件驅動架構(Event-Driven): 從 Lock-Free Queue 讀取客戶請求
// 2. FIFO 撮合邏輯: 先到先撮合(First In First Out)
// 3. 單執行緒處理: 避免鎖競爭,確保撮合順序的確定性
//
// 資料流向:
// Order Gateway → incoming_requests_ (Lock-Free Queue)
//                       ↓
//                MatchingEngine::run() (主事件迴圈)
//                       ↓
//            processClientRequest() (NEW/CANCEL 路由)
//                       ↓
//         MEOrderBook::add() / cancel() (訂單簿操作)
//                       ↓
//      ┌────────────────┴────────────────┐
//      ↓                                 ↓
// outgoing_ogw_responses_        outgoing_md_updates_
// (客戶回應 Lock-Free Queue)     (市場數據更新 Lock-Free Queue)
//      ↓                                 ↓
// Order Gateway                    Market Data Publisher
//
// ⚡ 撮合演算法: FIFO (First In First Out)
// - 價格優先: 買單取最高買價,賣單取最低賣價
// - 時間優先: 同價位依據 Priority 排序 (越小越優先)
// - 撮合方向: 新買單與賣單簿撮合,新賣單與買單簿撮合
//
// 使用場景: 交易所撮合引擎的事件處理器
class MatchingEngine final
{
public:
    MatchingEngine(ClientRequestLFQueue* client_requests,
                   ClientResponseLFQueue* client_responses,
                   MEMarketUpdateLFQueue* market_updates);

    ~MatchingEngine();

    auto start() -> void;

    auto stop() -> void;

    // 處理客戶請求 (路由到對應的訂單簿)
    // @param client_request: 客戶請求 (NEW/CANCEL)
    //
    // ⚡ 路由邏輯:
    // - NEW: 新增訂單 → MEOrderBook::add()
    // - CANCEL: 取消訂單 → MEOrderBook::cancel()
    //
    // ⚠️ 注意: 此方法在主事件迴圈中呼叫,是效能關鍵路徑
    auto processClientRequest(const MEClientRequest* client_request) noexcept
    {
        // 根據 ticker_id 查詢對應的訂單簿
        auto order_book = ticker_order_book_[client_request->ticker_id_];

        switch (client_request->type_) {
        case ClientRequestType::NEW: {
                // 新增訂單: 嘗試撮合,剩餘數量加入訂單簿
                // ⚡ FIFO 撮合: 依據價格-時間優先權撮合
                order_book->add(client_request->client_id_, client_request->order_id_,
                                client_request->ticker_id_,
                                client_request->side_, client_request->price_, client_request->qty_);
            }
            break;

        case ClientRequestType::CANCEL: {
                // 取消訂單: 從訂單簿移除
                order_book->cancel(client_request->client_id_, client_request->order_id_,
                                   client_request->ticker_id_);
            }
            break;

        default: {
                FATAL("Received invalid client-request-type:" + clientRequestTypeToString(
                          client_request->type_));
            }
            break;
        }
    }

    // 發送客戶回應 (透過 Lock-Free Queue)
    // @param client_response: 客戶回應 (ACCEPTED/CANCELED/FILLED)
    //
    // ⚡ 零複製優化: 使用 std::move 避免資料複製
    auto sendClientResponse(const MEClientResponse* client_response) noexcept
    {
        logger_.log("%:% %() % Sending %\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), client_response->toString());
        auto next_write = outgoing_ogw_responses_->getNextToWriteTo();
        *next_write = std::move(*client_response);  // ⚡ 移動語義,避免複製
        outgoing_ogw_responses_->updateWriteIndex();
    }

    // 發送市場數據更新 (透過 Lock-Free Queue)
    // @param market_update: 市場數據更新 (成交/訂單簿變動)
    auto sendMarketUpdate(const MEMarketUpdate* market_update) noexcept
    {
        logger_.log("%:% %() % Sending %\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), market_update->toString());
        auto next_write = outgoing_md_updates_->getNextToWriteTo();
        *next_write = *market_update;
        outgoing_md_updates_->updateWriteIndex();
    }

    // 主事件迴圈 (單執行緒)
    //
    // ⚡ 事件驅動架構:
    // 1. 從 incoming_requests_ 讀取客戶請求
    // 2. 呼叫 processClientRequest() 處理
    // 3. 撮合結果透過 sendClientResponse() 和 sendMarketUpdate() 發送
    //
    // ⚠️ 效能關鍵:
    // - 忙碌輪詢(Busy Polling): 不使用 sleep(),持續檢查 Lock-Free Queue
    // - CPU Affinity: 綁定到專用 CPU 核心,避免 Context Switch
    // - LIKELY 提示: 分支預測優化,假設大部分時間都有請求
    auto run() noexcept
    {
        logger_.log("%:% %() %\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_));

        while (run_) {
            // 從 Lock-Free Queue 讀取下一個客戶請求
            const auto me_client_request = incoming_requests_->getNextToRead();

            // ⚡ 分支預測提示：降低誤判成本。
            if (LIKELY(me_client_request)) {  // ⚡ 分支預測: 假設大部分時間有請求
                logger_.log("%:% %() % Processing %\n", __FILE__, __LINE__, __FUNCTION__,
                            Common::getCurrentTimeStr(&time_str_),
                            me_client_request->toString());
                processClientRequest(me_client_request);  // 處理請求
                incoming_requests_->updateReadIndex();    // 更新讀取索引
            }
        }
    }

    // Deleted default, copy & move constructors and assignment-operators.
    MatchingEngine() = delete;

    MatchingEngine(const MatchingEngine&) = delete;

    MatchingEngine(const MatchingEngine&&) = delete;

    MatchingEngine& operator=(const MatchingEngine&) = delete;

    MatchingEngine& operator=(const MatchingEngine&&) = delete;

private:
    // 訂單簿雜湊表: ticker_id → MEOrderBook*
    // ⚡ 容量: ME_MAX_TICKERS (8 個交易標的)
    // 複雜度: O(1) 查詢
    OrderBookHashMap ticker_order_book_;

    // Lock-Free Queue 通訊通道
    // ⚡ 設計原理: SPSC (Single Producer Single Consumer)
    // - incoming_requests_: Order Gateway → Matching Engine
    // - outgoing_ogw_responses_: Matching Engine → Order Gateway
    // - outgoing_md_updates_: Matching Engine → Market Data Publisher
    ClientRequestLFQueue* incoming_requests_ = nullptr;          // 客戶請求佇列 (輸入)
    ClientResponseLFQueue* outgoing_ogw_responses_ = nullptr;    // 客戶回應佇列 (輸出)
    MEMarketUpdateLFQueue* outgoing_md_updates_ = nullptr;       // 市場數據更新佇列 (輸出)

    // 執行狀態控制
    // ⚠️ volatile: 防止編譯器優化,確保主執行緒能正確停止事件迴圈
    volatile bool run_ = false;

    std::string time_str_;  // 時間字串緩衝區 (重複使用,避免記憶體分配)
    Logger logger_;         // 日誌記錄器
};
}
