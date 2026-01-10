// client_request.h: 客戶端訂單請求協議定義
//
// 職責：
// - 定義客戶端 → 交易所的訂單請求訊息格式
// - 支援兩種操作：NEW（新訂單）、CANCEL（取消訂單）
// - 使用 Lock-Free Queue 傳輸，確保低延遲
//
// 通訊流程：
// ┌────────────┐                    ┌────────────────┐
// │   Client   │ ── MEClientRequest → │ Order Server   │
// └────────────┘                    └────────┬───────┘
//                                            │
//                                            ▼
//                                   ┌────────────────┐
//                                   │ Matching Engine│
//                                   └────────────────┘
//
// ⚡ 低延遲設計：
// - #pragma pack(1)：緊密封裝，減少記憶體和網路開銷
// - uint8_t enum：最小化型別大小（1 byte）
// - Lock-Free Queue：無鎖訊息傳遞
// - 預定義常數：*_INVALID 用於快速初始化
//
// ⚠️ 協議不變性：
// - 此協議定義在客戶端和交易所之間共享
// - 修改時必須確保二進位相容性（Binary Compatibility）
// - 欄位順序不可改變（影響記憶體佈局）

#pragma once

#include <sstream>

#include "common/types.h"
#include "common/lf_queue.h"

using namespace Common;

namespace Exchange
{
// #pragma pack(1)：緊密封裝
// ⚡ 移除結構填充（Padding），減少記憶體使用
// ⚠️ 注意：可能影響對齊效能，需在空間與速度間權衡
#pragma pack(push, 1)

// ClientRequestType: 客戶端請求類型
//
// 支援的操作：
// - NEW: 提交新訂單（市價單或限價單）
// - CANCEL: 取消現有訂單
// - INVALID: 無效操作（初始值或錯誤狀態）
//
// ⚡ 使用 uint8_t（1 byte）：
// - 最小化網路傳輸開銷
// - 256 種操作類型已足夠（當前只用 3 種）
//
// 擴展性：
// - 可添加 MODIFY（修改訂單）、REPLACE（替換訂單）
// - 保留值 3-255 供未來使用
enum class ClientRequestType : uint8_t {
    INVALID = 0,  // 無效請求（預設值）
    NEW = 1,      // 新訂單請求
    CANCEL = 2    // 取消訂單請求
};

// clientRequestTypeToString: 請求類型轉字串（除錯用）
//
// 用途：
// - 日誌輸出：toString() 方法使用
// - 錯誤訊息：顯示人類可讀的請求類型
// - 除錯工具：追蹤訂單流程
//
// ⚡ inline 優化：
// - 編譯器會內聯此函式，避免函式呼叫開銷
// - 適合頻繁呼叫的小函式
inline std::string clientRequestTypeToString(ClientRequestType type)
{
    switch (type) {
    case ClientRequestType::NEW:
        return "NEW";

    case ClientRequestType::CANCEL:
        return "CANCEL";

    case ClientRequestType::INVALID:
        return "INVALID";
    }

    return "UNKNOWN";  // 不應該到達這裡（防禦性程式設計）
}

// MEClientRequest: 撮合引擎客戶端請求結構
//
// 用途：
// - 從客戶端接收訂單請求
// - 透過 Lock-Free Queue 傳遞給 Order Server
// - Order Server 驗證後轉發給 Matching Engine
//
// 欄位說明：
// - type_: 請求類型（NEW 或 CANCEL）
// - client_id_: 客戶端 ID（用於追蹤和風控）
// - ticker_id_: 交易標的 ID（股票/期貨代碼）
// - order_id_: 客戶端訂單 ID（客戶端自行分配）
// - side_: 買賣方向（BUY 或 SELL）
// - price_: 價格（限價單）或 0（市價單）
// - qty_: 數量（股數/張數）
//
// 記憶體佈局（#pragma pack(1)）：
// ┌──────────────┬──────┐
// │ type_        │ 1 B  │
// ├──────────────┼──────┤
// │ client_id_   │ 4 B  │ (假設 ClientId = uint32_t)
// ├──────────────┼──────┤
// │ ticker_id_   │ 4 B  │
// ├──────────────┼──────┤
// │ order_id_    │ 8 B  │ (假設 OrderId = uint64_t)
// ├──────────────┼──────┤
// │ side_        │ 1 B  │
// ├──────────────┼──────┤
// │ price_       │ 8 B  │ (假設 Price = int64_t)
// ├──────────────┼──────┤
// │ qty_         │ 4 B  │ (假設 Qty = uint32_t)
// └──────────────┴──────┘
// 總計：~30 bytes（視型別定義而定）
//
// ⚡ 效能優化：
// - 緊密封裝（pack(1)）：減少網路傳輸
// - 預設值初始化：使用 *_INVALID 常數
// - POD 型別：Plain Old Data，可安全 memcpy
//
// ⚠️ 使用注意：
// - NEW 請求：必須設定 ticker_id, side, price, qty
// - CANCEL 請求：必須設定 order_id（用於查找訂單）
// - client_id_：由 Order Server 填入（客戶端不設定）
struct MEClientRequest {
    ClientRequestType type_ = ClientRequestType::INVALID;  // 請求類型

    ClientId client_id_ = ClientId_INVALID;    // 客戶端 ID（由 Server 填入）
    TickerId ticker_id_ = TickerId_INVALID;    // 交易標的 ID
    OrderId order_id_ = OrderId_INVALID;       // 客戶端訂單 ID
    Side side_ = Side::INVALID;                // 買賣方向
    Price price_ = Price_INVALID;              // 價格（0 表示市價單）
    Qty qty_ = Qty_INVALID;                    // 數量

    // toString: 序列化為字串（除錯和日誌用）
    //
    // 輸出範例：
    // "MEClientRequest [type:NEW client:1 ticker:0 oid:12345 side:BUY qty:100 price:5000]"
    //
    // 用途：
    // - 日誌記錄：追蹤訂單流程
    // - 除錯輸出：查看訂單詳細資訊
    // - 監控告警：偵測異常訂單
    //
    // ⚠️ 效能注意：
    // - std::stringstream 有動態記憶體配置開銷
    // - 僅用於除錯，不應在關鍵路徑使用
    // - 生產環境應使用二進位日誌（Binary Logging）
    auto toString() const
    {
        std::stringstream ss;
        ss << "MEClientRequest"
           << " ["
           << "type:" << clientRequestTypeToString(type_)
           << " client:" << clientIdToString(client_id_)
           << " ticker:" << tickerIdToString(ticker_id_)
           << " oid:" << orderIdToString(order_id_)
           << " side:" << sideToString(side_)
           << " qty:" << qtyToString(qty_)
           << " price:" << priceToString(price_)
           << "]";
        return ss.str();
    }
};

// 恢復預設對齊（結束 pack(1) 區域）
// ⚠️ 必須與 #pragma pack(push, 1) 成對使用
#pragma pack(pop)

// ClientRequestLFQueue: 客戶端請求 Lock-Free 佇列
//
// 用途：
// - Order Server 接收客戶端請求的訊息佇列
// - 單生產者單消費者（SPSC）模式
// - 生產者：TCP Server（接收客戶端連線）
// - 消費者：Order Server（處理訂單請求）
//
// ⚡ 低延遲特性：
// - 無鎖設計：避免 mutex 競爭
// - Cache 對齊：減少 False Sharing
// - 預配置記憶體：避免動態配置
//
// 使用範例：
// ClientRequestLFQueue queue(1024);  // 預配置 1024 個元素
// auto* req = queue.getNextToWriteTo();
// req->type_ = ClientRequestType::NEW;
// queue.updateWriteIndex();
typedef LFQueue<MEClientRequest> ClientRequestLFQueue;
}

