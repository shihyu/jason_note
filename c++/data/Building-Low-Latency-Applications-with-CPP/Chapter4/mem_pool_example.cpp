// ========================================
// Memory Pool 使用範例
// ========================================
//
// 範例目的:
// 展示如何使用 Memory Pool 實現高效的記憶體分配與釋放
//
// ⚡ Memory Pool 核心優勢:
// 1. 零碎片化: 預分配固定大小區塊
// 2. O(1) 分配: 從 Free List 取出即可
// 3. Cache-Friendly: 連續記憶體佈局
// 4. 可預測延遲: 無 malloc/free 的不確定性
//
// 使用情境:
// - 高頻分配/釋放相同大小的物件
// - 延遲敏感應用(交易系統、遊戲引擎)
// - 避免記憶體碎片(長時間運行的服務)
//
// 與 new/delete 比較:
// - new: 每次呼叫核心 malloc,延遲 ~100-500ns,可能觸發缺頁
// - MemPool: 從預分配區塊取出,延遲 ~10-20ns
//
#include "mem_pool.h"

// MyStruct: 測試用的自訂結構
// 目的: 驗證 Memory Pool 支援任意型別
struct MyStruct {
    int d_[3];
};

int main(int, char**)
{
    using namespace Common;

    // 建立兩個 Memory Pool
    // @param size: 預分配的物件數量(容量)
    //
    // ⚡ 初始化行為:
    // 1. 一次性分配 50 * sizeof(T) 的連續記憶體
    // 2. 建立 Free List 鏈結串列(串接所有空閒區塊)
    // 3. 初始化管理結構(next_free_index_, object_pool_)
    //
    // 記憶體佈局:
    // [obj0][obj1][obj2]...[obj49]  (連續區塊)
    //   ↓    ↓    ↓           ↓
    // Free List: 0→1→2→...→49→null
    MemPool<double> prim_pool(50);     // 基本型別 Pool
    MemPool<MyStruct> struct_pool(50); // 自訂結構 Pool

    // 測試循環: 分配 50 個物件,每 5 個釋放一次
    for (auto i = 0; i < 50; ++i) {
        // ⚡ allocate(): O(1) 時間複雜度分配
        // @param args: 用於建構物件的參數(轉發給建構子)
        // @return: 指向新物件的指標
        //
        // 內部實作:
        // 1. 從 Free List 取出一個空閒區塊
        // 2. 使用 Placement New 在該位置建構物件
        // 3. 返回物件指標
        //
        // ⚠️ 若 Pool 已滿(Free List 空),返回 nullptr
        auto p_ret = prim_pool.allocate(i);  // 建構 double(i)
        auto s_ret = struct_pool.allocate(MyStruct{i, i + 1, i + 2});  // 建構 MyStruct

        std::cout << "prim elem:" << *p_ret << " allocated at:" << p_ret << std::endl;
        std::cout << "struct elem:" << s_ret->d_[0] << "," << s_ret->d_[1] << "," <<
                  s_ret->d_[2] << " allocated at:" << s_ret << std::endl;

        // 每 5 個元素釋放一次(測試記憶體重用)
        // 目的: 驗證 Free List 的正確性
        //
        // ⚡ 預期行為:
        // - 第 5 次分配會重用第 0 次釋放的區塊
        // - 記憶體位址應該重複出現
        // - 無需向系統請求新記憶體
        if (i % 5 == 0) {
            std::cout << "deallocating prim elem:" << *p_ret << " from:" << p_ret <<
                      std::endl;
            std::cout << "deallocating struct elem:" << s_ret->d_[0] << "," << s_ret->d_[1]
                      << "," << s_ret->d_[2] << " from:" << s_ret << std::endl;

            // ⚡ deallocate(): O(1) 時間複雜度釋放
            // @param ptr: 要釋放的物件指標
            //
            // 內部實作:
            // 1. 呼叫物件的解構子
            // 2. 將此區塊插入 Free List 頭部
            // 3. 更新 next_free_index_
            //
            // ⚠️ 注意: 不會真的釋放記憶體給系統
            // 原因: 保持連續記憶體佈局,避免缺頁中斷
            prim_pool.deallocate(p_ret);
            struct_pool.deallocate(s_ret);
        }
    }

    // ⚡ 程式結束時:
    // MemPool 解構子會釋放整塊預分配的記憶體
    // 無需手動 deallocate 剩餘的物件
    return 0;
}

// ========================================
// 預期輸出分析:
// ========================================
//
// 前 5 次分配(i=0 到 i=4):
// - 記憶體位址: 0x1000, 0x1008, 0x1010, 0x1018, 0x1020 (連續)
// - Free List: 5→6→7→...→49→null
//
// 第 5 次分配(i=5):
// - 記憶體位址: 0x1000 (重用第 0 次釋放的區塊)
// - Free List: 10→6→7→...→49→null
//
// 觀察重點:
// - 記憶體位址會循環出現(證明重用機制)
// - 位址始終在初始分配範圍內(0x1000~0x1190)
//
// ========================================
// 效能分析:
// ========================================
//
// allocate() 時間複雜度:
// - 最佳情況(Free List 非空): O(1), ~10-20ns
// - 最壞情況(Pool 已滿): O(1), 返回 nullptr
//
// deallocate() 時間複雜度:
// - 永遠 O(1), ~5-10ns (解構子 + Free List 插入)
//
// 與 new/delete 比較:
// | 操作        | new/delete | MemPool   | 加速比 |
// |-------------|------------|-----------|--------|
// | 分配        | ~100-500ns | ~10-20ns  | 5-50x  |
// | 釋放        | ~50-200ns  | ~5-10ns   | 5-40x  |
// | 碎片化      | 嚴重       | 零碎片    | -      |
// | 缺頁中斷    | 可能       | 不會      | -      |
// | 延遲穩定性  | 不穩定     | 非常穩定  | -      |
//
// ========================================
// 使用建議:
// ========================================
//
// ✅ 適合場景:
// - 高頻分配/釋放(每秒數萬~數百萬次)
// - 物件大小固定
// - 需要可預測延遲(交易系統、即時系統)
//
// ⚠️ 不適合場景:
// - 物件大小差異大(Memory Pool 針對單一大小優化)
// - 分配次數極少(初始化開銷不划算)
// - 長期持有物件(記憶體無法歸還系統)
//
// ⚠️ 常見陷阱:
// 1. Pool 容量不足
//    ❌ MemPool<Order> pool(10);  // 只能容納 10 個 Order
//    若分配第 11 個會失敗,需檢查返回值
//    ✅ if (auto* obj = pool.allocate(); obj != nullptr) { ... }
//
// 2. 重複釋放(Double Free)
//    ❌ pool.deallocate(ptr); pool.deallocate(ptr);
//    會破壞 Free List 結構,導致未定義行為
//
// 3. 釋放錯誤的指標
//    ❌ pool.deallocate(new Order());  // 不是從 Pool 分配的
//    只能釋放從同一個 Pool 分配的指標
//
// ========================================
// 進階優化:
// ========================================
//
// 1. Cache Line 對齊:
//    若物件大小不是 64 的倍數,考慮填充到 Cache Line 邊界
//    避免 False Sharing(多執行緒存取相鄰物件)
//
// 2. NUMA 感知:
//    在 NUMA 系統上,為每個 NUMA Node 建立獨立的 Pool
//    避免跨 Node 記憶體存取(延遲 2-3x)
//
// 3. 容量規劃:
//    Pool 大小 = (峰值併發數) * 1.2 (20% 緩衝)
//    範例: 峰值有 1000 個活躍 Order,Pool 容量設為 1200
//
