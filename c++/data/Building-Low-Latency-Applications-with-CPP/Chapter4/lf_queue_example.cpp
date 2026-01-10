// ========================================
// Lock-Free Queue 使用範例
// ========================================
//
// 範例目的:
// 展示如何使用 LFQueue 實現高效的生產者-消費者模式
//
// 關鍵學習點:
// 1. ⚡ 兩步驟寫入: getNextToWriteTo() → 寫入資料 → updateWriteIndex()
// 2. ⚡ 兩步驟讀取: getNextToRead() → 讀取資料 → updateReadIndex()
// 3. ⚠️ 索引更新順序: 必須先完成資料操作,再更新索引
// 4. 無鎖通訊: 生產者與消費者無需 mutex/lock
//
// 執行流程:
// - 主執行緒(生產者): 每秒產生 1 筆資料,共 50 筆
// - 消費者執行緒: 延遲 5 秒後開始消費,每秒處理 1 筆
// - 預期行為: 佇列會先累積到約 5-6 筆,然後穩定消費
//
#include "thread_utils.h"
#include "lf_queue.h"

// MyStruct: 測試用的資料結構
// 目的: 驗證非基本型別的資料也能正確傳遞
struct MyStruct {
    int d_[3];
};

using namespace Common;

// consumeFunction: 消費者執行緒函式
// @param lfq: Lock-Free Queue 指標
//
// ⚡ 消費者行為:
// 1. 延遲 5 秒開始(模擬啟動延遲)
// 2. 循環讀取佇列直到清空
// 3. 每處理一筆資料休眠 1 秒
//
// ⚠️ 正確的讀取步驟:
// 1. getNextToRead(): 取得指向下一筆資料的指標
// 2. 讀取資料內容(複製或處理)
// 3. updateReadIndex(): 標記此位置已讀取完畢
//
// 為什麼分兩步驟?
// - 保證原子性: 避免生產者覆蓋尚未讀完的資料
// - 無鎖設計: 使用 Memory Ordering 保證可見性
auto consumeFunction(LFQueue<MyStruct>* lfq)
{
    using namespace std::literals::chrono_literals;
    std::this_thread::sleep_for(5s);  // ⚡ 模擬消費者啟動延遲

    while (lfq->size()) {
        // 步驟 1: 取得指向下一筆資料的指標
        // ⚡ 零拷貝: 直接讀取環狀緩衝區中的資料
        const auto d = lfq->getNextToRead();

        // 步驟 2: 更新讀取索引(標記此位置已空)
        // ⚠️ 注意: 必須在讀取完資料後立即更新
        // 原因: 生產者依賴此索引判斷是否可寫入
        lfq->updateReadIndex();

        std::cout << "consumeFunction read elem:" << d->d_[0] << "," << d->d_[1] << ","
                  << d->d_[2] << " lfq-size:" << lfq->size() << std::endl;

        std::this_thread::sleep_for(1s);  // 模擬資料處理時間
    }

    std::cout << "consumeFunction exiting." << std::endl;
}

int main(int, char**)
{
    // 建立容量為 20 的 Lock-Free Queue
    // ⚠️ 容量選擇: 需大於 (生產速度 - 消費速度) * 時間窗口
    // 本範例: 前 5 秒累積 5 筆,容量 20 足夠
    LFQueue<MyStruct> lfq(20);

    // 建立消費者執行緒
    // -1: 不綁定 CPU 核心
    // "": 執行緒名稱為空
    auto ct = createAndStartThread(-1, "", consumeFunction, &lfq);

    // 生產者循環: 產生 50 筆資料
    for (auto i = 0; i < 50; ++i) {
        const MyStruct d{i, i * 10, i * 100};

        // ⚡ 步驟 1: 取得指向下一個可寫入位置的指標
        // 返回值: 指向環狀緩衝區中某個位置的指標
        // ⚠️ 若佇列已滿,會返回 nullptr(需檢查)
        auto* write_ptr = lfq.getNextToWriteTo();

        // 步驟 2: 寫入資料到緩衝區
        // ⚡ 零拷貝: 直接寫入環狀緩衝區,無額外分配
        *write_ptr = d;

        // 步驟 3: 更新寫入索引(標記此位置已有資料)
        // ⚠️ 關鍵: 必須在資料寫入完成後才更新索引
        // 原因: 消費者依賴此索引判斷資料是否可讀
        // Memory Ordering: store-release 保證資料寫入對消費者可見
        lfq.updateWriteIndex();

        std::cout << "main constructed elem:" << d.d_[0] << "," << d.d_[1] << "," <<
                  d.d_[2] << " lfq-size:" << lfq.size() << std::endl;

        using namespace std::literals::chrono_literals;
        std::this_thread::sleep_for(1s);  // 模擬每秒產生 1 筆資料
    }

    // 等待消費者執行緒結束
    ct->join();

    std::cout << "main exiting." << std::endl;

    return 0;
}

// ========================================
// 預期輸出分析:
// ========================================
//
// 時間軸 0-5 秒:
// - 生產者產生 5 筆資料,佇列大小增加到 5
// - 消費者尚未開始(在休眠中)
//
// 時間軸 5 秒後:
// - 消費者開始處理,每秒消費 1 筆
// - 生產者每秒產生 1 筆
// - 佇列大小穩定在 5 左右
//
// 時間軸 50 秒後:
// - 生產者完成,停止產生資料
// - 消費者繼續處理剩餘的 5 筆資料
// - 佇列清空,消費者退出
//
// ========================================
// 常見錯誤範例:
// ========================================
//
// ❌ 錯誤 1: 忘記更新索引
// auto* ptr = lfq.getNextToWriteTo();
// *ptr = data;
// // 忘記呼叫 updateWriteIndex()!
// // 結果: 消費者永遠讀不到這筆資料
//
// ❌ 錯誤 2: 索引更新順序錯誤
// lfq.updateWriteIndex();  // 先更新索引
// *lfq.getNextToWriteTo() = data;  // 後寫入資料
// // 結果: 消費者可能讀到未初始化的資料(Race Condition)
//
// ✅ 正確做法:
// auto* ptr = lfq.getNextToWriteTo();
// *ptr = data;  // 先完成資料寫入
// lfq.updateWriteIndex();  // 再更新索引(Memory Barrier 保證順序)
//
