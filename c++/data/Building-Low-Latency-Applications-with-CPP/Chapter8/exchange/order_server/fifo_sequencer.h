#pragma once

#include "common/thread_utils.h"
#include "common/macros.h"

#include "order_server/client_request.h"

namespace Exchange
{
constexpr size_t ME_MAX_PENDING_REQUESTS = 1024;

// FIFOSequencer: 請求排序器 (確保公平性)
//
// 設計原理:
// 1. 公平性保證: 確保來自不同 TCP 連線的請求按 "接收時間 (rx_time)" 順序處理
// 2. 批次處理: 先收集一輪 poll() 收到的所有請求, 再統一排序發送
// 3. 避免亂序: 解決 TCP Server 輪詢 socket 順序導致的潛在不公平問題
//
// 運作流程:
// addClientRequest() [收集] → sequenceAndPublish() [排序 & 發布] → Matching Engine
class FIFOSequencer
{
public:
    FIFOSequencer(ClientRequestLFQueue* client_requests, Logger* logger)
        : incoming_requests_(client_requests), logger_(logger)
    {
    }

    ~FIFOSequencer()
    {
    }

    // 收集客戶端請求
    // @param rx_time: 封包接收時間 (Kernel Timestamp / Software Timestamp)
    // @param request: 客戶端請求內容
    //
    // ⚡ 效能關鍵: 僅存入陣列, 不做排序 (O(1))
    auto addClientRequest(Nanos rx_time, const MEClientRequest& request)
    {
        if (pending_size_ >= pending_client_requests_.size()) {
            FATAL("Too many pending requests");
        }

        pending_client_requests_.at(pending_size_++) = std::move(RecvTimeClientRequest{rx_time, request});
    }

    // 排序並發布請求到撮合引擎
    //
    // 邏輯:
    // 1. 檢查是否有待處理請求
    // 2. 依據 recv_time_ 進行排序 (std::sort)
    // 3. 依序寫入 Lock-Free Queue (incoming_requests_)
    //
    // ⚡ 時間複雜度: O(N log N), N = pending_size_
    auto sequenceAndPublish()
    {
        if (UNLIKELY(!pending_size_)) {
            return;
        }

        logger_->log("%:% %() % Processing % requests.\n", __FILE__, __LINE__,
                     __FUNCTION__, Common::getCurrentTimeStr(&time_str_), pending_size_);

        // 1. 按接收時間排序
        std::sort(pending_client_requests_.begin(),
                  pending_client_requests_.begin() + pending_size_);

        // 2. 依序寫入 Lock-Free Queue
        for (size_t i = 0; i < pending_size_; ++i) {
            const auto& client_request = pending_client_requests_.at(i);

            logger_->log("%:% %() % Writing RX:% Req:% to FIFO.\n", __FILE__, __LINE__,
                         __FUNCTION__, Common::getCurrentTimeStr(&time_str_),
                         client_request.recv_time_, client_request.request_.toString());

            auto next_write = incoming_requests_->getNextToWriteTo();
            *next_write = std::move(client_request.request_);
            incoming_requests_->updateWriteIndex();
        }

        // 3. 重置計數器
        pending_size_ = 0;
    }

    // Deleted default, copy & move constructors and assignment-operators.
    FIFOSequencer() = delete;

    FIFOSequencer(const FIFOSequencer&) = delete;

    FIFOSequencer(const FIFOSequencer&&) = delete;

    FIFOSequencer& operator=(const FIFOSequencer&) = delete;

    FIFOSequencer& operator=(const FIFOSequencer&&) = delete;

private:
    ClientRequestLFQueue* incoming_requests_ = nullptr;

    std::string time_str_;
    Logger* logger_ = nullptr;

    struct RecvTimeClientRequest {
        Nanos recv_time_ = 0;
        MEClientRequest request_;

        auto operator<(const RecvTimeClientRequest& rhs) const
        {
            return (recv_time_ < rhs.recv_time_);
        }
    };

    std::array<RecvTimeClientRequest, ME_MAX_PENDING_REQUESTS>
    pending_client_requests_;
    size_t pending_size_ = 0;
};
}
