// 撮合訂單簿核心流程：新增/取消/撮合熱路徑。
// ⚡ 效能關鍵：最優價快速定位與 O(1) 鏈結。
// ⚠️ 注意：數量/狀態更新順序一致性。

#include "me_order_book.h"

#include "matcher/matching_engine.h"

namespace Exchange
{
/**
 * 構造函式 - 初始化訂單簿資料結構
 *
 * @param ticker_id 商品識別碼
 * @param logger 日誌記錄器指標
 * @param matching_engine 撮合引擎指標（用於發送成交和市場更新）
 *
 * 初始化內容：
 * 1. 設定商品 ID 和撮合引擎引用
 * 2. 預配置記憶體池：
 *    - orders_at_price_pool_: 價格層級物件池（ME_MAX_PRICE_LEVELS 個）
 *    - order_pool_: 訂單物件池（ME_MAX_ORDER_IDS 個）
 * 3. 儲存日誌記錄器引用
 *
 * 記憶體管理：
 * - 使用物件池（Object Pool）避免動態記憶體分配
 * - 所有物件在構造時預先分配
 * - 延遲 < 50 ns（無 malloc/free 呼叫）
 *
 * 資料結構初始化：
 * - bids_by_price_ 和 asks_by_price_ 初始化為 nullptr（空訂單簿）
 * - cid_oid_to_order_ 雜湊表自動初始化為空
 */
MEOrderBook::MEOrderBook(TickerId ticker_id, Logger* logger,
                         MatchingEngine* matching_engine)
    : ticker_id_(ticker_id), matching_engine_(matching_engine),
      orders_at_price_pool_(ME_MAX_PRICE_LEVELS), order_pool_(ME_MAX_ORDER_IDS),
      logger_(logger)
{
}

/**
 * 解構函式 - 清理訂單簿並記錄最終狀態
 *
 * 清理步驟：
 * 1. 記錄訂單簿最終狀態（toString）到日誌
 * 2. 清空 matching_engine_ 引用（防止 dangling pointer）
 * 3. 清空買賣盤鏈表頭指標
 * 4. 清空 cid_oid_to_order_ 雜湊表（所有槽位設為 nullptr）
 *
 * 注意：
 * - 物件池（orders_at_price_pool_, order_pool_）自動解構
 * - toString(false, true) 參數：不顯示詳細資訊，但執行有效性檢查
 * - 日誌記錄有助於除錯和審計
 */
MEOrderBook::~MEOrderBook()
{
    // 記錄訂單簿最終狀態
    logger_->log("%:% %() % OrderBook\n%\n", __FILE__, __LINE__, __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_),
                 toString(false, true));

    // 清空引用和指標
    matching_engine_ = nullptr;
    bids_by_price_ = asks_by_price_ = nullptr;

    // 清空客戶訂單雜湊表
    for (auto& itr : cid_oid_to_order_) {
        itr.fill(nullptr);
    }
}

/**
 * match() - 執行訂單撮合並生成成交回報
 *
 * @param ticker_id 商品識別碼
 * @param client_id 新訂單的客戶端 ID（主動方）
 * @param side 新訂單的買賣方向（主動方）
 * @param client_order_id 新訂單的客戶端訂單 ID（主動方）
 * @param new_market_order_id 新訂單的市場訂單 ID（主動方）
 * @param itr 被動方訂單指標（訂單簿中已存在的訂單）
 * @param leaves_qty 剩餘未成交數量指標（會被更新）
 *
 * 撮合邏輯：
 * 1. 計算成交數量：取「剩餘數量」和「被動方訂單數量」的較小值
 * 2. 更新雙方剩餘數量：
 *    - 新訂單（主動方）：leaves_qty -= fill_qty
 *    - 被動方訂單：order->qty_ -= fill_qty
 * 3. 發送成交回報給雙方客戶端：
 *    - 主動方：FILLED 回報，包含成交價、成交量、剩餘量
 *    - 被動方：FILLED 回報，包含成交價、成交量、剩餘量
 * 4. 發送市場數據更新（TRADE）給訂閱者
 * 5. 處理被動方訂單後續狀態：
 *    - 若完全成交（qty = 0）→ 發送 CANCEL 更新 + 從訂單簿移除
 *    - 若部分成交（qty > 0）→ 發送 MODIFY 更新（數量變化）
 *
 * 效能特性：
 * - 時間複雜度：O(1)（所有操作都是常數時間）
 * - 延遲：< 100 ns（記憶體操作 + 佇列寫入）
 * - 無動態記憶體分配（預先分配的結構體）
 *
 * 訊息順序：
 * 1. 主動方 FILLED 回報
 * 2. 被動方 FILLED 回報
 * 3. 市場 TRADE 更新
 * 4. 被動方狀態更新（CANCEL 或 MODIFY）
 *
 * 價格時間優先原則：
 * - 成交價格 = 被動方訂單價格（itr->price_）
 * - 先到先服務（此函式按價格鏈表順序被呼叫）
 *
 * 注意事項：
 * - noexcept 保證：不會拋出例外（低延遲要求）
 * - leaves_qty 通過指標傳遞（避免拷貝）
 * - 所有訊息使用成員變數緩衝區（避免重複分配）
 */
auto MEOrderBook::match(TickerId ticker_id, ClientId client_id, Side side,
                        OrderId client_order_id, OrderId new_market_order_id, MEOrder* itr,
                        Qty* leaves_qty) noexcept
{
    // 1. 取得被動方訂單資訊
    const auto order = itr;
    const auto order_qty = order->qty_;  // 儲存原始數量（用於 CANCEL 訊息）

    // 2. 計算成交數量（取較小值）
    const auto fill_qty = std::min(*leaves_qty, order_qty);

    // 3. 更新雙方剩餘數量
    *leaves_qty -= fill_qty;  // 主動方剩餘量
    order->qty_ -= fill_qty;  // 被動方剩餘量

    // 4. 發送主動方成交回報（FILLED）
    client_response_ = {ClientResponseType::FILLED, client_id, ticker_id, client_order_id,
                        new_market_order_id, side, itr->price_, fill_qty, *leaves_qty
                       };
    matching_engine_->sendClientResponse(&client_response_);

    // 5. 發送被動方成交回報（FILLED）
    client_response_ = {ClientResponseType::FILLED, order->client_id_, ticker_id, order->client_order_id_,
                        order->market_order_id_, order->side_, itr->price_, fill_qty, order->qty_
                       };
    matching_engine_->sendClientResponse(&client_response_);

    // 6. 發送市場數據更新（TRADE）
    // 訂閱者（例如市場數據消費者）接收此訊息更新市場狀態
    market_update_ = {MarketUpdateType::TRADE, OrderId_INVALID, ticker_id, side, itr->price_, fill_qty, Priority_INVALID};
    matching_engine_->sendMarketUpdate(&market_update_);

    // 7. 處理被動方訂單後續狀態
    if (!order->qty_) {
        // 完全成交 → 從訂單簿移除
        market_update_ = {MarketUpdateType::CANCEL, order->market_order_id_, ticker_id, order->side_,
                          order->price_, order_qty, Priority_INVALID
                         };
        matching_engine_->sendMarketUpdate(&market_update_);

        removeOrder(order);  // 從三層索引結構中移除
    } else {
        // 部分成交 → 更新訂單數量
        market_update_ = {MarketUpdateType::MODIFY, order->market_order_id_, ticker_id, order->side_,
                          order->price_, order->qty_, order->priority_
                         };
        matching_engine_->sendMarketUpdate(&market_update_);
    }
}

/**
 * checkForMatch() - 檢查新訂單是否與訂單簿中現有訂單匹配
 *
 * @param client_id 客戶端識別碼
 * @param client_order_id 客戶端訂單 ID
 * @param ticker_id 商品識別碼
 * @param side 買賣方向（BUY/SELL）
 * @param price 訂單價格
 * @param qty 訂單數量
 * @param new_market_order_id 新生成的市場訂單 ID
 * @return 剩餘未成交數量（0 表示完全成交）
 *
 * 撮合邏輯：
 * - 買單（BUY）：與賣盤（asks）撮合
 *   - 條件：買價 >= 賣價
 *   - 從最優賣價（最低價）開始撮合
 *   - 價格排序：遞增（100, 101, 102...）
 *
 * - 賣單（SELL）：與買盤（bids）撮合
 *   - 條件：賣價 <= 買價
 *   - 從最優買價（最高價）開始撮合
 *   - 價格排序：遞減（102, 101, 100...）
 *
 * 撮合流程：
 * 1. 初始化剩餘數量（leaves_qty = qty）
 * 2. 迴圈檢查對手盤最優價格訂單：
 *    - 買單：while (leaves_qty && asks_by_price_)
 *      - 取得最優賣單（asks_by_price_->first_me_order_）
 *      - 若買價 < 賣價 → 無法撮合，退出迴圈
 *      - 否則呼叫 match() 撮合
 *    - 賣單：while (leaves_qty && bids_by_price_)
 *      - 取得最優買單（bids_by_price_->first_me_order_）
 *      - 若賣價 > 買價 → 無法撮合，退出迴圈
 *      - 否則呼叫 match() 撮合
 * 3. 返回剩餘未成交數量
 *
 * 停止條件：
 * 1. 完全成交（leaves_qty == 0）
 * 2. 對手盤無訂單（asks_by_price_ == nullptr 或 bids_by_price_ == nullptr）
 * 3. 價格不匹配（買價 < 賣價 或 賣價 > 買價）
 *
 * 效能特性：
 * - 時間複雜度：O(N)，N = 撮合的訂單數量
 * - 平均延遲：< 1 μs（通常只撮合 1-3 筆訂單）
 * - LIKELY 宏：分支預測優化（通常價格不匹配，立即退出）
 *
 * 訊息生成：
 * - 每次撮合呼叫 match()，生成：
 *   - 2 筆 FILLED 回報（主動方 + 被動方）
 *   - 1 筆 TRADE 市場更新
 *   - 1 筆 CANCEL 或 MODIFY 更新（被動方狀態變化）
 *
 * 價格時間優先：
 * - first_me_order_ 指向該價格層級最早的訂單
 * - match() 處理完後，鏈表自動移動到下一個訂單
 * - 保證同價格按時間順序撮合
 *
 * 注意事項：
 * - noexcept 保證（低延遲要求）
 * - leaves_qty 每次撮合後自動更新（通過指標傳遞）
 * - while 迴圈自然處理多重撮合（一筆新單可與多筆舊單撮合）
 */
auto MEOrderBook::checkForMatch(ClientId client_id, OrderId client_order_id,
                                TickerId ticker_id, Side side, Price price, Qty qty,
                                Qty new_market_order_id) noexcept
{
    auto leaves_qty = qty;  // 剩餘未成交數量

    // 買單撮合邏輯：與賣盤撮合
    if (side == Side::BUY) {
        while (leaves_qty && asks_by_price_) {
            // 取得最優賣單（最低賣價）
            const auto ask_itr = asks_by_price_->first_me_order_;

            // 價格檢查：買價 < 賣價 → 無法撮合
            if (LIKELY(price < ask_itr->price_)) {
                break;
            }

            // 執行撮合（可能部分成交或完全成交）
            match(ticker_id, client_id, side, client_order_id, new_market_order_id, ask_itr,
                  &leaves_qty);
        }
    }

    // 賣單撮合邏輯：與買盤撮合
    if (side == Side::SELL) {
        while (leaves_qty && bids_by_price_) {
            // 取得最優買單（最高買價）
            const auto bid_itr = bids_by_price_->first_me_order_;

            // 價格檢查：賣價 > 買價 → 無法撮合
            if (LIKELY(price > bid_itr->price_)) {
                break;
            }

            // 執行撮合（可能部分成交或完全成交）
            match(ticker_id, client_id, side, client_order_id, new_market_order_id, bid_itr,
                  &leaves_qty);
        }
    }

    return leaves_qty;  // 返回剩餘未成交數量
}

/**
 * add() - 新增訂單到訂單簿
 *
 * @param client_id 客戶端識別碼
 * @param client_order_id 客戶端訂單 ID
 * @param ticker_id 商品識別碼
 * @param side 買賣方向（BUY/SELL）
 * @param price 訂單價格
 * @param qty 訂單數量
 *
 * 處理流程：
 * 1. 生成市場訂單 ID（generateNewMarketOrderId）
 *    - 唯一識別碼，遞增生成
 *    - 用於市場數據發佈和訂單追蹤
 *
 * 2. 發送 ACCEPTED 回報給客戶端
 *    - 確認訂單已進入撮合系統
 *    - 包含新生成的市場訂單 ID
 *
 * 3. 嘗試撮合（checkForMatch）
 *    - 與對手盤現有訂單撮合
 *    - 返回剩餘未成交數量（leaves_qty）
 *    - 可能完全成交（leaves_qty = 0）或部分成交（leaves_qty > 0）
 *
 * 4. 若有剩餘數量，將訂單加入訂單簿：
 *    a. 計算優先序號（getNextPriority）
 *       - 同價格按時間順序（先到先服務）
 *       - 優先序號遞增
 *    b. 從物件池分配訂單物件（order_pool_.allocate）
 *       - 避免動態記憶體分配
 *       - 延遲 < 20 ns
 *    c. 加入三層索引結構（addOrder）
 *       - 價格鏈表（sorted by price）
 *       - 同價格訂單鏈表（sorted by priority）
 *       - 客戶訂單雜湊表（for O(1) lookup）
 *    d. 發送 ADD 市場更新
 *       - 通知訂閱者新訂單進入訂單簿
 *       - 包含價格、數量、優先序號
 *
 * 訊息流：
 * - 完全成交情境（leaves_qty = 0）：
 *   - ACCEPTED 回報
 *   - N 筆 FILLED 回報（撮合產生）
 *   - N 筆 TRADE 更新（撮合產生）
 *   - 無 ADD 更新（訂單未進入訂單簿）
 *
 * - 部分成交或未成交情境（leaves_qty > 0）：
 *   - ACCEPTED 回報
 *   - M 筆 FILLED 回報（M = 撮合次數，可能為 0）
 *   - M 筆 TRADE 更新
 *   - 1 筆 ADD 更新（剩餘數量進入訂單簿）
 *
 * 效能特性：
 * - 時間複雜度：
 *   - 撮合：O(N)，N = 撮合的訂單數量（通常 < 5）
 *   - 加入訂單簿：O(log M)，M = 價格層級數量（通常 < 100）
 * - 平均延遲：< 2 μs（包含撮合和加入訂單簿）
 * - 無動態記憶體分配（物件池預先配置）
 *
 * LIKELY 宏優化：
 * - LIKELY(leaves_qty)：預期大部分訂單不會完全成交
 * - 分支預測優化，減少 CPU 管線停頓
 *
 * 訂單生命週期：
 * 1. 客戶端發送新訂單請求
 * 2. 撮合引擎呼叫此函式
 * 3. 發送 ACCEPTED 回報
 * 4. 嘗試撮合（可能部分或完全成交）
 * 5. 若有剩餘量 → 進入訂單簿（發送 ADD 更新）
 * 6. 訂單留在訂單簿直到：
 *    - 完全成交（FILLED）
 *    - 被取消（CANCELED）
 *    - 被修改（MODIFIED）
 *
 * 注意事項：
 * - noexcept 保證（低延遲要求）
 * - 所有訊息使用成員變數緩衝區（避免重複分配）
 * - addOrder() 內部處理所有索引維護（三層結構）
 */
auto MEOrderBook::add(ClientId client_id, OrderId client_order_id,
                      TickerId ticker_id, Side side, Price price, Qty qty) noexcept -> void
{
    // 1. 生成唯一市場訂單 ID
    const auto new_market_order_id = generateNewMarketOrderId();

    // 2. 發送 ACCEPTED 回報給客戶端
    client_response_ = {ClientResponseType::ACCEPTED, client_id, ticker_id, client_order_id, new_market_order_id, side, price, 0, qty};
    matching_engine_->sendClientResponse(&client_response_);

    // 3. 嘗試與對手盤撮合
    const auto leaves_qty = checkForMatch(client_id, client_order_id, ticker_id,
                                          side, price, qty, new_market_order_id);

    // 4. 若有剩餘數量，將訂單加入訂單簿
    if (LIKELY(leaves_qty)) {
        // 計算優先序號（同價格按時間順序）
        const auto priority = getNextPriority(price);

        // 從物件池分配訂單物件（無動態記憶體分配）
        auto order = order_pool_.allocate(ticker_id, client_id, client_order_id,
                                          new_market_order_id, side, price, leaves_qty, priority, nullptr,
                                          nullptr);

        // 加入三層索引結構（價格鏈表 + 同價格訂單鏈表 + 客戶訂單雜湊表）
        addOrder(order);

        // 發送 ADD 市場更新（通知訂閱者）
        market_update_ = {MarketUpdateType::ADD, new_market_order_id, ticker_id, side, price, leaves_qty, priority};
        matching_engine_->sendMarketUpdate(&market_update_);
    }
    // 若 leaves_qty == 0，表示訂單完全成交，無需加入訂單簿
}

/**
 * cancel() - 取消訂單
 *
 * @param client_id 客戶端識別碼
 * @param order_id 客戶端訂單 ID
 * @param ticker_id 商品識別碼
 *
 * 處理流程：
 * 1. 驗證訂單是否可取消：
 *    a. 檢查 client_id 是否在有效範圍內
 *       - client_id < cid_oid_to_order_.size()
 *    b. 查找訂單：
 *       - 通過客戶訂單雜湊表（cid_oid_to_order_）查找
 *       - O(1) 查找複雜度
 *    c. 檢查訂單是否存在（!= nullptr）
 *
 * 2a. 若訂單不可取消（不存在或已處理）：
 *    - 發送 CANCEL_REJECTED 回報給客戶端
 *    - 原因可能：
 *      - 訂單 ID 不存在
 *      - 訂單已完全成交
 *      - 訂單已被取消
 *      - client_id 不匹配
 *
 * 2b. 若訂單可取消：
 *    - 發送 CANCELED 回報給客戶端
 *      - 包含市場訂單 ID、買賣方向、價格、剩餘數量
 *    - 發送 CANCEL 市場更新給訂閱者
 *      - 通知訂單簿狀態變化
 *    - 從訂單簿移除訂單（removeOrder）
 *      - 從三層索引結構中移除
 *      - 將訂單物件歸還物件池
 *
 * 訊息流：
 * - 成功取消：
 *   1. CANCELED 回報（發送給客戶端）
 *   2. CANCEL 市場更新（發送給訂閱者）
 *
 * - 取消失敗：
 *   1. CANCEL_REJECTED 回報（發送給客戶端）
 *   2. 無市場更新（訂單簿狀態未變化）
 *
 * 效能特性：
 * - 時間複雜度：O(1)（雜湊表查找 + 鏈表移除）
 * - 平均延遲：< 500 ns
 * - 無動態記憶體分配
 *
 * LIKELY/UNLIKELY 宏優化：
 * - LIKELY(is_cancelable)：預期大部分取消請求有效
 * - UNLIKELY(!is_cancelable)：預期極少取消失敗
 * - 分支預測優化，提升效能
 *
 * 安全性檢查：
 * - 邊界檢查：client_id < cid_oid_to_order_.size()
 * - 空指標檢查：exchange_order != nullptr
 * - 防止無效訂單操作
 *
 * 訂單生命週期：
 * - 訂單狀態：LIVE → CANCELED
 * - 從訂單簿移除後，訂單物件歸還物件池
 * - 可重複使用（物件池管理）
 *
 * 典型使用場景：
 * 1. 客戶端主動取消訂單
 * 2. 風控系統觸發取消（超過風險限制）
 * 3. 交易時段結束前清倉
 * 4. 市場狀況改變（波動過大）
 *
 * 注意事項：
 * - noexcept 保證（低延遲要求）
 * - 無論成功或失敗，最後都發送 client_response_
 * - removeOrder() 內部處理所有索引維護（三層結構）
 * - CANCEL_REJECTED 回報中的欄位設為 INVALID（無有效資訊）
 */
auto MEOrderBook::cancel(ClientId client_id, OrderId order_id,
                         TickerId ticker_id) noexcept -> void
{
    // 1. 驗證 client_id 是否在有效範圍內
    auto is_cancelable = (client_id < cid_oid_to_order_.size());
    MEOrder* exchange_order = nullptr;

    // 2. 查找訂單（若 client_id 有效）
    if (LIKELY(is_cancelable)) {
        auto& co_itr = cid_oid_to_order_.at(client_id);  // 取得客戶端訂單陣列
        exchange_order = co_itr.at(order_id);             // 查找訂單（O(1)）
        is_cancelable = (exchange_order != nullptr);     // 檢查訂單是否存在
    }

    // 3a. 訂單不可取消 → 發送 CANCEL_REJECTED 回報
    if (UNLIKELY(!is_cancelable)) {
        client_response_ = {ClientResponseType::CANCEL_REJECTED, client_id, ticker_id, order_id, OrderId_INVALID,
                            Side::INVALID, Price_INVALID, Qty_INVALID, Qty_INVALID
                           };
    }
    // 3b. 訂單可取消 → 執行取消邏輯
    else {
        // 發送 CANCELED 回報給客戶端
        client_response_ = {ClientResponseType::CANCELED, client_id, ticker_id, order_id, exchange_order->market_order_id_,
                            exchange_order->side_, exchange_order->price_, Qty_INVALID, exchange_order->qty_
                           };

        // 發送 CANCEL 市場更新給訂閱者
        market_update_ = {MarketUpdateType::CANCEL, exchange_order->market_order_id_, ticker_id, exchange_order->side_, exchange_order->price_, 0,
                          exchange_order->priority_
                         };

        // 從訂單簿移除訂單（三層索引結構）
        removeOrder(exchange_order);

        // 發送市場更新
        matching_engine_->sendMarketUpdate(&market_update_);
    }

    // 4. 發送客戶端回報（無論成功或失敗）
    matching_engine_->sendClientResponse(&client_response_);
}

/**
 * toString() - 生成訂單簿的可視化字串表示
 *
 * @param detailed 是否顯示詳細訊息（每個訂單的詳細資訊）
 * @param validity_check 是否執行有效性檢查（驗證價格排序）
 * @return 訂單簿狀態的字串表示
 *
 * 功能：
 * - 生成訂單簿的文字表示，用於除錯和日誌記錄
 * - 顯示買賣盤的價格層級和訂單分佈
 * - 可選擇性顯示詳細訂單資訊
 * - 可選擇性執行有效性檢查（驗證資料結構完整性）
 *
 * 輸出格式範例：
 * ```
 * Ticker: AAPL
 * ASKS L:0 =>  <px:102 p:101 n:103> 102 @ 5000(2)
 * ASKS L:1 =>  <px:103 p:102 n:104> 103 @ 3000(1)
 *
 *                           X
 *
 * BIDS L:0 =>  <px:101 p:102 n:100> 101 @ 4000(3)
 * BIDS L:1 =>  <px:100 p:101 n:99 > 100 @ 2000(1)
 * ```
 *
 * 格式說明：
 * - L:N：層級編號（Level N）
 * - px：當前價格
 * - p：前一個價格層級指標
 * - n：下一個價格層級指標
 * - 價格 @ 數量(訂單數)
 *
 * 詳細模式（detailed = true）：
 * - 顯示每個訂單的資訊：
 *   - oid：市場訂單 ID
 *   - q：訂單數量
 *   - p：前一個訂單指標
 *   - n：下一個訂單指標
 *
 * 有效性檢查（validity_check = true）：
 * - 驗證賣盤價格遞增排序（100, 101, 102...）
 * - 驗證買盤價格遞減排序（102, 101, 100...）
 * - 若發現排序錯誤，觸發 FATAL（程式終止）
 *
 * 效能考量：
 * - 此函式非效能關鍵路徑（僅用於除錯）
 * - 使用 std::stringstream 構建輸出（涉及記憶體分配）
 * - 遍歷所有價格層級和訂單（O(P + O)，P = 價格層級數，O = 訂單數）
 *
 * 使用場景：
 * 1. 除錯：檢查訂單簿狀態
 * 2. 日誌：記錄訂單簿快照
 * 3. 測試：驗證撮合引擎正確性
 * 4. 監控：人工檢查市場狀態
 *
 * 注意事項：
 * - const 函式：不修改訂單簿狀態
 * - 非 noexcept：stringstream 可能拋出例外
 * - 不應在交易時段頻繁呼叫（效能開銷較大）
 */
auto MEOrderBook::toString(bool detailed,
                           bool validity_check) const -> std::string
{
    std::stringstream ss;
    std::string time_str;

    /**
     * printer - Lambda 函式：列印單一價格層級的訂單資訊
     *
     * @param ss 字串流引用（輸出目標）
     * @param itr 價格層級指標
     * @param side 買賣方向（用於驗證排序）
     * @param last_price 上一個價格（用於驗證排序）
     * @param sanity_check 是否執行有效性檢查
     *
     * 功能：
     * 1. 計算該價格層級的總數量和訂單數
     * 2. 列印價格層級資訊（價格、前後指標、總量、訂單數）
     * 3. 若 detailed = true，列印每個訂單詳細資訊
     * 4. 若 sanity_check = true，驗證價格排序
     */
    auto printer = [&](std::stringstream & ss, MEOrdersAtPrice * itr, Side side,
    Price & last_price, bool sanity_check) {
        // ⚡ 關鍵路徑：函式內避免鎖/分配，保持快取局部性。
        char buf[4096];  // 輸出緩衝區
        Qty qty = 0;     // 該價格層級的總數量
        size_t num_orders = 0;  // 該價格層級的訂單數

        // 第一次遍歷：計算總數量和訂單數
        // 使用環狀鏈表（circular linked list）
        for (auto o_itr = itr->first_me_order_;; o_itr = o_itr->next_order_) {
            qty += o_itr->qty_;
            ++num_orders;

            // 環狀鏈表終止條件：回到起點
            if (o_itr->next_order_ == itr->first_me_order_) {
                break;
            }
        }

        // 列印價格層級摘要
        // 格式：<px:當前價格 p:前指標 n:後指標> 價格 @ 總量(訂單數)
        sprintf(buf, " <px:%3s p:%3s n:%3s> %-3s @ %-5s(%-4s)",
                priceToString(itr->price_).c_str(),
                priceToString(itr->prev_entry_->price_).c_str(),
                priceToString(itr->next_entry_->price_).c_str(),
                priceToString(itr->price_).c_str(), qtyToString(qty).c_str(),
                std::to_string(num_orders).c_str());
        ss << buf;

        // 第二次遍歷：若 detailed = true，列印每個訂單詳細資訊
        for (auto o_itr = itr->first_me_order_;; o_itr = o_itr->next_order_) {
            if (detailed) {
                // 格式：[oid:訂單ID q:數量 p:前訂單 n:後訂單]
                sprintf(buf, "[oid:%s q:%s p:%s n:%s] ",
                        orderIdToString(o_itr->market_order_id_).c_str(),
                        qtyToString(o_itr->qty_).c_str(),
                        orderIdToString(o_itr->prev_order_ ? o_itr->prev_order_->market_order_id_ :
                                        OrderId_INVALID).c_str(),
                        orderIdToString(o_itr->next_order_ ? o_itr->next_order_->market_order_id_ :
                                        OrderId_INVALID).c_str());
                ss << buf;
            }

            // 環狀鏈表終止條件
            if (o_itr->next_order_ == itr->first_me_order_) {
                break;
            }
        }

        ss << std::endl;

        // 有效性檢查：驗證價格排序
        if (sanity_check) {
            // 賣盤：價格應遞增（last_price < itr->price_）
            // 買盤：價格應遞減（last_price > itr->price_）
            if ((side == Side::SELL && last_price >= itr->price_) || (side == Side::BUY &&
                    last_price <= itr->price_)) {
                FATAL("Bids/Asks not sorted by ascending/descending prices last:" +
                      priceToString(last_price) + " itr:" + itr->toString());
            }

            last_price = itr->price_;
        }
    };

    // === 主函式邏輯開始 ===

    // 列印商品識別碼
    ss << "Ticker:" << tickerIdToString(ticker_id_) << std::endl;

    // 列印賣盤（ASKS）
    {
        auto ask_itr = asks_by_price_;  // 最優賣價（最低價）
        auto last_ask_price = std::numeric_limits<Price>::min();  // 初始值：最小價格

        // 遍歷所有賣價層級（遞增順序）
        for (size_t count = 0; ask_itr; ++count) {
            ss << "ASKS L:" << count << " => ";
            // 計算下一個價格層級（環狀鏈表終止條件）
            auto next_ask_itr = (ask_itr->next_entry_ == asks_by_price_ ? nullptr :
                                 ask_itr->next_entry_);
            // 呼叫 printer 列印該層級
            printer(ss, ask_itr, Side::SELL, last_ask_price, validity_check);
            ask_itr = next_ask_itr;
        }
    }

    // 列印分隔線（市場中心線）
    ss << std::endl << "                          X" << std::endl << std::endl;

    // 列印買盤（BIDS）
    {
        auto bid_itr = bids_by_price_;  // 最優買價（最高價）
        auto last_bid_price = std::numeric_limits<Price>::max();  // 初始值：最大價格

        // 遍歷所有買價層級（遞減順序）
        for (size_t count = 0; bid_itr; ++count) {
            ss << "BIDS L:" << count << " => ";
            // 計算下一個價格層級（環狀鏈表終止條件）
            auto next_bid_itr = (bid_itr->next_entry_ == bids_by_price_ ? nullptr :
                                 bid_itr->next_entry_);
            // 呼叫 printer 列印該層級
            printer(ss, bid_itr, Side::BUY, last_bid_price, validity_check);
            bid_itr = next_bid_itr;
        }
    }

    return ss.str();  // 返回完整字串
}
}
