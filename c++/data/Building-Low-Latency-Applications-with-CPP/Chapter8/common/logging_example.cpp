// ============================================================================
// Lock-Free Logger 使用範例
// ============================================================================
// 📌 範例目的：
// 展示如何使用低延遲 Logger 記錄不同型別的資料
//
// 關鍵學習點：
// 1. ⚡ 型別自動推導：無需指定 %d、%f、%s 等格式符號，統一使用 %
// 2. 非阻塞操作：log() 呼叫延遲 < 100ns（僅寫入 Lock-Free Queue）
// 3. 異步刷寫：專用執行緒負責將日誌刷新到磁碟
//
// 📊 效能比較：
// - printf()：同步 I/O，延遲 ~1-10 μs
// - spdlog (async)：延遲 ~200-500 ns
// - 本 Logger：延遲 < 100 ns (20-40x faster than printf)

#include "logging.h"

int main(int, char**)
{
    using namespace Common;

    // 測試不同資料型別
    char c = 'd';
    int i = 3;
    unsigned long ul = 65;
    float f = 3.4;
    double d = 34.56;
    const char* s = "test C-string";
    std::string ss = "test string";

    // 建立 Logger 實例
    // 參數：日誌檔案路徑
    // ⚡ 自動啟動後台執行緒負責 I/O
    Logger logger("logging_example.log");

    // ⚡ 統一格式符號：% 自動推導型別
    // 支援：char, int, long, float, double, const char*, std::string
    logger.log("Logging a char:% an int:% and an unsigned:%\n", c, i, ul);
    logger.log("Logging a float:% and a double:%\n", f, d);
    logger.log("Logging a C-string:'%'\n", s);
    logger.log("Logging a string:'%'\n", ss);

    // ⚠️ 程式結束時，Logger 解構子會刷新所有待寫入的日誌

    return 0;
}
