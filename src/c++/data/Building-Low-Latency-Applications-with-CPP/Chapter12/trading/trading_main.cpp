/**
 * @file trading_main.cpp
 * @brief 交易系統主程式入口
 *
 * 🎯 系統架構：
 * - TradeEngine：交易引擎（策略執行、風險管理、訂單管理）
 * - OrderGateway：訂單閘道（與交易所通訊，發送訂單、接收回報）
 * - MarketDataConsumer：行情消費者（接收並處理市場數據）
 *
 * 📊 執行流程：
 * 1. 解析命令列參數（CLIENT_ID、ALGO_TYPE、各標的風險配置）
 * 2. 初始化 Lock-Free 佇列（client_requests、client_responses、market_updates）
 * 3. 啟動三個主要元件（各自獨立執行緒）
 * 4. 等待系統穩定（10 秒）
 * 5. 若為 RANDOM 演算法，產生隨機訂單測試
 * 6. 監控系統活動，無活動 60 秒後優雅關閉
 *
 * ⚡ 命令列格式：
 * ./trading_main CLIENT_ID ALGO_TYPE [CLIP_1 THRESH_1 MAX_ORDER_SIZE_1 MAX_POS_1 MAX_LOSS_1] ...
 * - CLIENT_ID: 客戶識別碼（用於區分不同交易實例）
 * - ALGO_TYPE: MAKER（做市商）/ TAKER（趨勢跟隨）/ RANDOM（隨機測試）
 * - 每組 5 個參數代表一個標的的配置：
 *   * CLIP: 市場流動性門檻（最小成交量）
 *   * THRESH: 觸發信號閾值（價格變動百分比）
 *   * MAX_ORDER_SIZE: 單筆最大訂單量
 *   * MAX_POS: 最大持倉量
 *   * MAX_LOSS: 最大虧損（觸發停損）
 *
 * 📝 範例：
 * ./trading_main 123 MAKER 100 0.05 500 1000 10000.0 200 0.03 300 800 5000.0
 * → 客戶 123, 做市商策略, 配置 2 個標的
 */
#include <csignal>

#include "strategy/trade_engine.h"
#include "order_gw/order_gateway.h"
#include "market_data/market_data_consumer.h"

#include "common/logging.h"

/// 主要元件全域指標（便於異常處理和清理）
Common::Logger* logger = nullptr;
Trading::TradeEngine* trade_engine = nullptr;
Trading::MarketDataConsumer* market_data_consumer = nullptr;
Trading::OrderGateway* order_gateway = nullptr;

int main(int argc, char** argv)
{
    // 步驟 1：檢查命令列參數（最少需要 CLIENT_ID 和 ALGO_TYPE）
    if (argc < 3) {
        FATAL("USAGE trading_main CLIENT_ID ALGO_TYPE [CLIP_1 THRESH_1 MAX_ORDER_SIZE_1 MAX_POS_1 MAX_LOSS_1] [CLIP_2 THRESH_2 MAX_ORDER_SIZE_2 MAX_POS_2 MAX_LOSS_1] ...");
    }

    // 步驟 2：解析基本參數
    const Common::ClientId client_id = atoi(argv[1]);
    srand(client_id);  // ⚡ 使用 client_id 初始化隨機種子（確保每個實例隨機序列不同）

    const auto algo_type = stringToAlgoType(argv[2]);  // MAKER / TAKER / RANDOM

    logger = new Common::Logger("trading_main_" + std::to_string(
                                    client_id) + ".log");

    // ⚡ 測試模式下的睡眠時間（microseconds）
    const int sleep_time = 20 * 1000;  // 20 毫秒

    // 步驟 3：初始化 Lock-Free 佇列（元件間通訊的核心）
    // ⚡ 無鎖設計：避免 mutex 延遲，確保微秒級響應時間
    Exchange::ClientRequestLFQueue client_requests(ME_MAX_CLIENT_UPDATES);      // TradeEngine → OrderGateway
    Exchange::ClientResponseLFQueue client_responses(ME_MAX_CLIENT_UPDATES);    // OrderGateway → TradeEngine
    Exchange::MEMarketUpdateLFQueue market_updates(ME_MAX_MARKET_UPDATES);      // MarketDataConsumer → TradeEngine

    std::string time_str;  // 時間字串緩衝（避免重複分配）

    // 步驟 4：解析標的配置參數
    // 📊 資料結構：std::array<TradeEngineCfg, ME_MAX_TICKERS>
    TradeEngineCfgHashMap ticker_cfg;

    // 命令列參數格式：[CLIP THRESH MAX_ORDER_SIZE MAX_POS MAX_LOSS] × N
    // 每組 5 個參數對應一個標的（ticker）
    size_t next_ticker_id = 0;

    for (int i = 3; i < argc; i += 5, ++next_ticker_id) {
        ticker_cfg.at(next_ticker_id) = {
            static_cast<Qty>(std::atoi(argv[i])),      // clip：市場流動性門檻
            std::atof(argv[i + 1]),                     // threshold：觸發信號閾值
            {
                static_cast<Qty>(std::atoi(argv[i + 2])),  // max_order_size：單筆最大訂單量
                static_cast<Qty>(std::atoi(argv[i + 3])),  // max_position：最大持倉量
                std::atof(argv[i + 4])                      // max_loss：最大虧損額度
            }
        };
    }

    logger->log("%:% %() % Starting Trade Engine...\n", __FILE__, __LINE__,
                __FUNCTION__, Common::getCurrentTimeStr(&time_str));
    trade_engine = new Trading::TradeEngine(client_id, algo_type,
                                            ticker_cfg,
                                            &client_requests,
                                            &client_responses,
                                            &market_updates);
    trade_engine->start();

    const std::string order_gw_ip = "127.0.0.1";
    const std::string order_gw_iface = "lo";
    const int order_gw_port = 12345;

    logger->log("%:% %() % Starting Order Gateway...\n", __FILE__, __LINE__,
                __FUNCTION__, Common::getCurrentTimeStr(&time_str));
    order_gateway = new Trading::OrderGateway(client_id, &client_requests,
            &client_responses, order_gw_ip, order_gw_iface, order_gw_port);
    order_gateway->start();

    const std::string mkt_data_iface = "lo";
    const std::string snapshot_ip = "233.252.14.1";
    const int snapshot_port = 20000;
    const std::string incremental_ip = "233.252.14.3";
    const int incremental_port = 20001;

    logger->log("%:% %() % Starting Market Data Consumer...\n", __FILE__, __LINE__,
                __FUNCTION__, Common::getCurrentTimeStr(&time_str));
    market_data_consumer = new Trading::MarketDataConsumer(client_id,
            &market_updates, mkt_data_iface, snapshot_ip, snapshot_port, incremental_ip,
            incremental_port);
    market_data_consumer->start();

    usleep(10 * 1000 * 1000);

    // 步驟 8：初始化事件時間（用於監控系統活動）
    trade_engine->initLastEventTime();

    // 步驟 9：RANDOM 演算法實作（壓力測試用）
    // 📊 測試目的：
    // - 驗證系統在高頻訂單流下的穩定性
    // - 測試撮合引擎、訂單簿、風控的正確性
    // - 模擬真實交易場景（新增 + 取消混合）
    if (algo_type == AlgoType::RANDOM) {
        // 初始化訂單 ID（使用 client_id * 1000 確保不同客戶端 ID 不衝突）
        Common::OrderId order_id = client_id * 1000;
        std::vector<Exchange::MEClientRequest> client_requests_vec;  // 保存已發送的訂單（用於取消）
        std::array<Price, ME_MAX_TICKERS> ticker_base_price;         // 各標的基準價格

        // 為每個標的生成基準價格（100-200 之間）
        for (size_t i = 0; i < ME_MAX_TICKERS; ++i) {
            ticker_base_price[i] = (rand() % 100) + 100;
        }

        // 主測試迴圈：產生 10000 筆訂單
        for (size_t i = 0; i < 10000; ++i) {
            // 隨機選擇標的和訂單屬性
            const Common::TickerId ticker_id = rand() % Common::ME_MAX_TICKERS;
            const Price price = ticker_base_price[ticker_id] + (rand() % 10) + 1;  // 基準價 ± 10
            const Qty qty = 1 + (rand() % 100) + 1;                                 // 1-101 股
            const Side side = (rand() % 2 ? Common::Side::BUY : Common::Side::SELL);

            // 步驟 9.1：發送新訂單
            Exchange::MEClientRequest new_request{Exchange::ClientRequestType::NEW, client_id, ticker_id, order_id++, side,
                                                  price, qty};
            trade_engine->sendClientRequest(&new_request);
            usleep(sleep_time);  // ⚡ 睡眠 20ms 模擬真實訂單間隔

            // 步驟 9.2：隨機取消一筆已發送的訂單
            client_requests_vec.push_back(new_request);
            const auto cxl_index = rand() % client_requests_vec.size();
            auto cxl_request = client_requests_vec[cxl_index];
            cxl_request.type_ = Exchange::ClientRequestType::CANCEL;
            trade_engine->sendClientRequest(&cxl_request);
            usleep(sleep_time);

            // 步驟 9.3：檢查系統是否已無活動（提前結束測試）
            if (trade_engine->silentSeconds() >= 60) {
                logger->log("%:% %() % Stopping early because been silent for % seconds...\n",
                            __FILE__, __LINE__, __FUNCTION__,
                            Common::getCurrentTimeStr(&time_str), trade_engine->silentSeconds());

                break;
            }
        }
    }

    // 步驟 10：監控系統活動，等待無活動狀態
    // ⚡ 優雅關閉條件：連續 60 秒無任何訂單或行情事件
    while (trade_engine->silentSeconds() < 60) {
        logger->log("%:% %() % Waiting till no activity, been silent for % seconds...\n",
                    __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str), trade_engine->silentSeconds());

        using namespace std::literals::chrono_literals;
        std::this_thread::sleep_for(30s);  // 每 30 秒檢查一次
    }

    // 步驟 11：停止所有元件（順序很重要）
    // ⚠️ 先停止交易引擎（不再處理新事件）→ 行情消費者 → 訂單閘道
    trade_engine->stop();
    market_data_consumer->stop();
    order_gateway->stop();

    // 等待執行緒完全結束
    using namespace std::literals::chrono_literals;
    std::this_thread::sleep_for(10s);

    // 步驟 12：清理資源（釋放記憶體）
    // 📊 順序與停止順序相同，避免 dangling pointer
    delete logger;
    logger = nullptr;
    delete trade_engine;
    trade_engine = nullptr;
    delete market_data_consumer;
    market_data_consumer = nullptr;
    delete order_gateway;
    order_gateway = nullptr;

    // 最終等待（確保所有日誌寫入完成）
    std::this_thread::sleep_for(10s);

    exit(EXIT_SUCCESS);
}
