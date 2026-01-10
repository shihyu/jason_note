#include "liquidity_taker.h"

#include "trade_engine.h"

namespace Trading
{
// LiquidityTaker 建構子
//
// 策略初始化流程：
// 1. 儲存核心元件參考（FeatureEngine, OrderManager, 配置）
// 2. 覆寫 TradeEngine 的 Lambda 回調（策略主動權模式）
//
// 設計模式：
// - 策略模式（Strategy Pattern）：與 MarketMaker 共享相同架構
// - 依賴注入（Dependency Injection）：TradeEngine 提供基礎設施
// - Lambda 回調（Callback）：避免虛函式，內聯展開
//
// ⚡ 效能考量：
// - Lambda 捕獲 this：編譯器內聯展開，零虛函式開銷
// - 策略主動權：由策略決定如何回應事件，TradeEngine 僅分發
//
// 流動性獲取者策略特性：
// - 市價成交：使用市價單（Market Order）立即成交
// - 趨勢跟隨：偵測激進買賣訊號，順勢交易
// - 單邊操作：只在判斷趨勢方向時下單（不雙邊報價）
// - 高週轉：快速進出，捕捉短期價格變動
//
// @param logger: 日誌記錄器
// @param trade_engine: 交易引擎（提供事件分發）
// @param feature_engine: 特徵引擎（激進成交比率、趨勢判斷）
// @param order_manager: 訂單管理器（訂單狀態機）
// @param ticker_cfg: 交易標的配置表（策略參數）
LiquidityTaker::LiquidityTaker(Common::Logger* logger,
                               TradeEngine* trade_engine, const FeatureEngine* feature_engine,
                               OrderManager* order_manager,
                               const TradeEngineCfgHashMap& ticker_cfg)
    : feature_engine_(feature_engine), order_manager_(order_manager),
      logger_(logger),
      ticker_cfg_(ticker_cfg)
{
    // 覆寫 TradeEngine 的訂單簿更新回調
    // ⚡ Lambda 捕獲 this：成員函式指標包裝
    //
    // 📌 設計理念：LiquidityTaker 通常不太關注訂單簿變動（更關注成交事件）
    // 原因：
    // 1. 被動報價變動（Passive Order Book Update）不代表趨勢
    // 2. 成交事件（Trade Event）才能確認流動性消耗方向
    // 3. 過度回應報價變動會產生虛假信號（False Signal）
    //
    // ⚠️ 注意：此回調僅用於日誌記錄，不執行交易邏輯
    trade_engine->algoOnOrderBookUpdate_ = [this](auto ticker_id, auto price,
    auto side, auto book) {
        onOrderBookUpdate(ticker_id, price, side, book);
    };

    // 覆寫 TradeEngine 的成交事件回調
    // ⚡ 關鍵回調：LiquidityTaker 主要依據成交事件判斷趨勢
    //
    // 📊 策略核心邏輯：
    // 1. 從 FeatureEngine 取得激進成交比率（Aggressive Trade Qty Ratio）
    // 2. 判斷比率是否超過閾值（threshold_）→ 確認強勢趨勢
    // 3. 趨勢確認後，立即市價成交跟隨：
    //    - 激進買入（Aggressive Buy）→ 跟隨買入（預期推高價格）
    //    - 激進賣出（Aggressive Sell）→ 跟隨賣出（預期壓低價格）
    //
    // 📊 範例：
    // - 市場出現 1000 張買入成交，其中 800 張為激進買入
    // - 激進成交比率 = 800/1000 = 0.8
    // - 若 threshold_ = 0.6，則觸發跟隨買入信號
    //
    // ⚠️ 風險：追高殺跌、滑價成本、趨勢反轉（需搭配止損機制）
    trade_engine->algoOnTradeUpdate_ = [this](auto market_update, auto book) {
        onTradeUpdate(market_update, book);
    };

    // 覆寫 TradeEngine 的訂單回應回調
    //
    // 📌 功能：處理自己發送的訂單狀態變化通知
    // 訂單生命週期事件：
    // 1. ACCEPTED：訂單被交易所接受（進入排隊）
    // 2. FILLED：訂單完全成交（更新倉位、計算 PnL）
    // 3. PARTIALLY_FILLED：訂單部分成交（需追蹤剩餘量）
    // 4. CANCELLED：訂單被取消（釋放訂單資源）
    // 5. REJECTED：訂單被拒絕（風控失敗、參數錯誤等）
    //
    // 📊 LiquidityTaker 特別注意：
    // - 使用市價單（Market Order）通常會立即成交（FILLED）
    // - 很少會收到 PENDING 或 PARTIALLY_FILLED 狀態
    // - 如果收到 REJECTED，可能是風控閾值觸發或倉位不足
    //
    // ⚡ 效能考量：委託給 OrderManager 處理，避免策略層重複邏輯
    trade_engine->algoOnOrderUpdate_ = [this](auto client_response) {
        onOrderUpdate(client_response);
    };
}
}
