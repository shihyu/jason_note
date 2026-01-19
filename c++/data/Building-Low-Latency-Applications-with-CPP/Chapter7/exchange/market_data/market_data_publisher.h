#pragma once

#include <functional>

#include "market_data/snapshot_synthesizer.h"

namespace Exchange
{
// MarketDataPublisher: 市場數據發布器
//
// 設計原理:
// 1. 增量更新發布: 透過 UDP Multicast 即時發送訂單簿變動
// 2. 雙佇列設計: 同時轉發給快照合成器
// 3. 序列號管理: 為每個更新分配單調遞增的序列號
//
// 資料流向:
// Matching Engine → MEMarketUpdateLFQueue → MarketDataPublisher
//                          ↓                          ↓
//                   UDP Multicast          MDPMarketUpdateLFQueue
//                  (Incremental)            (Snapshot Synthesizer)
//
// ⚡ 效能特性:
// - 零複製: 直接從 Lock-Free Queue 讀取並發送
// - 即時發送: 無批次處理,每個更新立即發送
// - 低延遲: UDP 無確認機制,單向發送
//
// 使用場景: 交易所行情發布系統
class MarketDataPublisher
{
public:
    MarketDataPublisher(MEMarketUpdateLFQueue* market_updates,
                        const std::string& iface,
                        const std::string& snapshot_ip, int snapshot_port,
                        const std::string& incremental_ip, int incremental_port);

    ~MarketDataPublisher()
    {
        stop();

        using namespace std::literals::chrono_literals;
        std::this_thread::sleep_for(5s);  // 等待執行緒完全終止

        delete snapshot_synthesizer_;
        snapshot_synthesizer_ = nullptr;
    }

    // 啟動市場數據發布器
    // 創建發布執行緒並啟動快照合成器
    auto start()
    {
        run_ = true;

        // ⚡ 創建專用執行緒（未綁定 CPU 核心）
        ASSERT(Common::createAndStartThread(-1,
        "Exchange/MarketDataPublisher", [this]() {
            run();
        }) != nullptr, "Failed to start MarketData thread.");

        snapshot_synthesizer_->start();
    }

    // 停止市場數據發布器
    auto stop() -> void
    {
        run_ = false;

        snapshot_synthesizer_->stop();
    }

    // 主事件迴圈（在專用執行緒中執行）
    // ⚡ 效能關鍵: 忙碌輪詢 Lock-Free Queue,即時發送更新
    auto run() noexcept -> void;

    // Deleted default, copy & move constructors and assignment-operators.
    MarketDataPublisher() = delete;

    MarketDataPublisher(const MarketDataPublisher&) = delete;

    MarketDataPublisher(const MarketDataPublisher&&) = delete;

    MarketDataPublisher& operator=(const MarketDataPublisher&) = delete;

    MarketDataPublisher& operator=(const MarketDataPublisher&&) = delete;

private:
    // 序列號生成器
    // ⚡ 單調遞增: 每發送一個更新,序列號 +1
    // ⚠️ 注意: 64位元序列號實務上不會溢位（58億年）
    size_t next_inc_seq_num_ = 1;

    // Lock-Free Queue 通訊通道
    // ⚡ SPSC: Matching Engine (Producer) → MarketDataPublisher (Consumer)
    MEMarketUpdateLFQueue* outgoing_md_updates_ = nullptr;  // 來自撮合引擎的更新佇列

    // 轉發給快照合成器的佇列
    // ⚡ SPSC: MarketDataPublisher (Producer) → SnapshotSynthesizer (Consumer)
    MDPMarketUpdateLFQueue snapshot_md_updates_;  // 帶序列號的更新佇列

    // 執行狀態控制
    // ⚠️ volatile: 防止編譯器優化,確保主執行緒能正確停止事件迴圈
    volatile bool run_ = false;

    std::string time_str_;  // 時間字串緩衝區（重複使用,避免記憶體分配）
    Logger logger_;         // 日誌記錄器

    // UDP Multicast Socket
    // ⚡ 用途: 發送增量更新（Incremental Updates）
    // 特性: 一次發送,多方接收（廣播）
    Common::McastSocket incremental_socket_;

    // 快照合成器
    // 職責: 維護完整訂單簿狀態,定期發布快照
    SnapshotSynthesizer* snapshot_synthesizer_ = nullptr;
};
}
