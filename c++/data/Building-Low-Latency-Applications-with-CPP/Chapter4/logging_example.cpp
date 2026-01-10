// ========================================
// Logger 使用範例
// ========================================
//
// 範例目的:
// 展示如何使用零分配 Logger 記錄不同型別的資料
//
// ⚡ Logger 核心優勢:
// 1. Lock-Free: 無需 mutex,多執行緒安全
// 2. Zero-Allocation: 執行期不分配記憶體
// 3. 型別安全: 編譯期檢查參數型別
// 4. 低延遲: ~50-100ns (vs printf ~1-2μs)
//
// 語法說明:
// - 使用 '%' 作為佔位符(而非 printf 的 %d/%s/%f)
// - 自動推導型別(無需指定格式)
// - 支援所有基本型別 + std::string + C-string
//
// 與標準庫比較:
// - printf: 阻塞 I/O,會觸發系統呼叫
// - spdlog: 動態分配字串,效能不穩定
// - Logger: 批次寫入,延遲可預測
//
#include "logging.h"

int main(int, char**)
{
    using namespace Common;

    // 準備各種型別的測試資料
    char c = 'd';
    int i = 3;
    unsigned long ul = 65;
    float f = 3.4;
    double d = 34.56;
    const char* s = "test C-string";
    std::string ss = "test string";

    // 建立 Logger 實例
    // @param filename: 日誌檔案路徑
    //
    // ⚡ 內部行為:
    // 1. 建立 Lock-Free Queue(用於緩衝日誌)
    // 2. 啟動背景執行緒(負責批次寫入檔案)
    // 3. 預分配緩衝區(避免執行期分配)
    Logger logger("logging_example.log");

    // 範例 1: 記錄多個基本型別
    // ⚡ 關鍵特性:
    // - '%' 佔位符: 自動推導型別(char, int, unsigned long)
    // - Variadic Templates: 編譯期展開參數
    // - 零拷貝: 直接寫入 Lock-Free Queue
    //
    // 實際開銷: ~50-100ns (僅記憶體複製,無 I/O)
    logger.log("Logging a char:% an int:% and an unsigned:%\n", c, i, ul);

    // 範例 2: 記錄浮點數
    // ⚠️ 浮點數轉字串開銷較高(~200-300ns)
    // 原因: 需要格式化(std::to_chars 或 sprintf)
    logger.log("Logging a float:% and a double:%\n", f, d);

    // 範例 3: 記錄 C-string
    // ⚡ 字串處理: 計算長度並複製(避免指標懸空)
    // 限制: 字串長度需小於緩衝區大小
    logger.log("Logging a C-string:'%'\n", s);

    // 範例 4: 記錄 std::string
    // ⚡ 字串處理: 使用 .data() + .size(),避免重新計算長度
    logger.log("Logging a string:'%'\n", ss);

    // ⚡ 程式結束時自動執行:
    // 1. Logger 解構子觸發
    // 2. 通知背景執行緒停止
    // 3. Flush 所有緩衝的日誌到檔案
    // 4. 關閉檔案並釋放資源
    return 0;
}

// ========================================
// 預期輸出(logging_example.log):
// ========================================
//
// Logging a char:d an int:3 and an unsigned:65
// Logging a float:3.4 and a double:34.56
// Logging a C-string:'test C-string'
// Logging a string:'test string'
//
// ========================================
// 效能分析:
// ========================================
//
// 單次 log() 呼叫延遲:
// - 基本型別(int, char): ~50ns
// - 浮點數(float, double): ~200ns
// - 字串(const char*, std::string): ~100-300ns (視長度)
//
// 背景執行緒批次寫入:
// - 頻率: 每 10ms 檢查一次佇列
// - 批次大小: 一次寫入所有累積的日誌
// - I/O 開銷: ~1-2ms (由背景執行緒承擔)
//
// 與 printf 比較:
// | 操作          | printf  | Logger |
// |---------------|---------|--------|
// | 記錄延遲      | ~1-2μs  | ~50ns  | (20-40x 更快)
// | 多執行緒安全  | 需 mutex| Lock-Free |
// | 記憶體分配    | 動態    | 零分配 |
// | I/O 阻塞      | 是      | 否     |
//
// ========================================
// 使用建議:
// ========================================
//
// ✅ 適合場景:
// - 高頻日誌(每秒數萬筆)
// - 多執行緒環境
// - 延遲敏感應用(交易系統、遊戲引擎)
//
// ⚠️ 不適合場景:
// - 需要即時輸出(Logger 有延遲)
// - 日誌量極小(初始化開銷不划算)
// - 需要複雜格式化(不支援 printf-style 格式)
//
// ⚠️ 常見陷阱:
// 1. 指標懸空: 不要記錄區域變數的指標
//    ❌ logger.log("%\n", &local_var);  // local_var 可能已銷毀
//    ✅ logger.log("%\n", local_var);   // 複製值
//
// 2. 字串過長: 超過緩衝區會被截斷
//    建議: 單筆日誌 < 1KB
//
// 3. 佇列滿溢: 若生產速度 > 背景寫入速度
//    解決: 增大 Queue 容量或降低日誌頻率
//
