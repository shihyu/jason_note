#pragma once

#include <functional>

#include "socket_utils.h"

#include "logging.h"

namespace Common
{
// ========================================
// McastSocket: UDP 多播 Socket
// ========================================
//
// 設計目標:
// 1. 一對多廣播: 一個發送者,多個接收者
// 2. 低延遲行情發布: 交易所使用多播發送市場數據
// 3. 無連線狀態: UDP 不需要維護連線,減少開銷
//
// 使用場景:
// - 市場數據發布 (MarketDataPublisher)
// - 行情訂閱 (MarketDataConsumer)
// - 內部廣播通知
//
// ⚡ 多播 vs 單播的效能優勢:
// - 網路頻寬: N 個訂閱者只需 1 份資料流
// - 交換機負載: 硬體層級的封包複製
// - 發送延遲: 避免循環發送的延遲累積

// 多播緩衝區大小: 64MB
// ⚠️ 權衡考量:
// - 太小: 高頻率數據可能溢位,遺失封包
// - 太大: 浪費記憶體,初始化時間長
// - 64MB: 以 1000 字節/封包計算,可容納約 65,536 個封包
//
// 實際場景:
// - 市場數據 1000 updates/sec: 64MB 可緩衝約 65 秒的數據
// - 高頻交易所: 可能需要更大緩衝區 (128MB+)
constexpr size_t McastBufferSize = 64 * 1024 * 1024;

// McastSocket: UDP 多播 Socket 封裝
//
// 雙向支援:
// - 發送端 (Publisher): 使用 outbound_data_ 緩衝區
// - 接收端 (Subscriber): 使用 inbound_data_ 緩衝區
// - 單向使用: 通常只需要一個緩衝區,但預先配置兩者
//
// 記憶體佈局:
// - outbound_data_: 64MB 發送緩衝區
// - inbound_data_: 64MB 接收緩衝區
// - 總計: 128MB (每個 McastSocket 實例)
struct McastSocket {
    // 建構函式: 預先配置收發緩衝區
    // @param logger: 日誌記錄器
    //
    // ⚡ 記憶體預配置:
    // - resize(McastBufferSize): 一次性分配,避免執行時重新配置
    // - 初始化時間: ~1-5ms (取決於系統記憶體)
    McastSocket(Logger& logger)
        : logger_(logger)
    {
        outbound_data_.resize(McastBufferSize);  // 預先配置發送緩衝區
        inbound_data_.resize(McastBufferSize);   // 預先配置接收緩衝區
    }

    // init: 初始化多播 Socket
    // @param ip: 多播群組位址 (224.0.0.0 ~ 239.255.255.255)
    // @param iface: 網卡名稱 (如 "eth0")
    // @param port: 多播埠號
    // @param is_listening: true=接收端, false=發送端
    // @return: socket 檔案描述符
    //
    // ⚠️ 注意: 此方法只建立 Socket,不加入多播群組
    // 接收端必須額外呼叫 join() 才能接收數據
    auto init(const std::string& ip, const std::string& iface, int port,
              bool is_listening) -> int;

    // join: 加入多播群組
    // @param ip: 多播群組位址
    // @return: true=成功, false=失敗
    //
    // IP_ADD_MEMBERSHIP 原理:
    // - 通知作業系統核心訂閱此多播群組
    // - 網卡硬體過濾: 只接收匹配群組位址的封包
    // - IGMP 協議: 向網路通知訂閱意圖
    //
    // ⚡ 效能影響:
    // - 硬體過濾: 減少核心處理的封包數量
    // - 降低 CPU 負載: 不匹配的封包在網卡層級被丟棄
    auto join(const std::string& ip) -> bool;

    // leave: 離開多播群組
    // @param ip: 多播群組位址 (未使用)
    // @param port: 埠號 (未使用)
    //
    // 實作方式: 直接關閉 Socket
    // ⚠️ 簡化設計: 不使用 IP_DROP_MEMBERSHIP
    // 原因: close() 會自動清理所有多播訂閱
    auto leave(const std::string& ip, int port) -> void;

    // sendAndRecv: 非阻塞式收發數據
    // @return: true=收到資料, false=無資料
    //
    // 處理流程:
    // 1. 接收: 從 socket 讀取到 inbound_data_
    // 2. 回呼: 呼叫 recv_callback_ 通知上層
    // 3. 發送: 將 outbound_data_ 發送到多播群組
    //
    // ⚡ UDP vs TCP 的差異:
    // - 無連線: 不需要 accept/connect
    // - 訊息邊界: recv 一次返回一個完整封包
    // - 不保證順序: 封包可能亂序到達
    // - 不保證送達: 封包可能遺失
    auto sendAndRecv() noexcept -> bool;

    // send: 將資料複製到發送緩衝區
    // @param data: 要發送的資料
    // @param len: 資料長度
    //
    // 緩衝機制:
    // - 資料先複製到 outbound_data_
    // - 下次呼叫 sendAndRecv() 時才實際發送
    //
    // ⚠️ 緩衝區溢位檢查:
    // - ASSERT 確保不超過 McastBufferSize
    // - 建議在呼叫前檢查剩餘空間
    auto send(const void* data, size_t len) noexcept -> void;

    // ========================================
    // 成員變數
    // ========================================

    int socket_fd_ = -1;  // UDP Socket 檔案描述符

    // 發送緩衝區
    // ⚡ 設計考量:
    // - 預先配置: 避免執行時記憶體分配
    // - 單一緩衝區: 批次累積多個更新後一次發送
    // - 64MB 容量: 可容納大量市場數據更新
    std::vector<char> outbound_data_;
    size_t next_send_valid_index_ = 0;  // 下一個可寫入位置

    // 接收緩衝區
    // ⚡ 設計考量:
    // - UDP 訊息邊界: 每次 recv 返回一個完整封包
    // - 64MB 容量: 防止高頻數據溢位
    // - 索引追蹤: next_rcv_valid_index_ 追蹤已接收的資料量
    std::vector<char> inbound_data_;
    size_t next_rcv_valid_index_ = 0;   // 已接收的資料長度

    // 接收回呼函式
    // 觸發時機: sendAndRecv() 接收到資料時
    // 參數: McastSocket* - 指向當前 socket 的指標
    // 用途: 通知上層應用處理新接收的資料
    std::function<void(McastSocket* s)> recv_callback_ = nullptr;

    std::string time_str_;  // 時間字串緩衝區(避免重複分配)
    Logger& logger_;        // 日誌記錄器引用
};
}
