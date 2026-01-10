// ============================================================================
// Memory Pool 使用範例
// ============================================================================
// 📌 範例目的：
// 展示如何使用 MemPool 進行快速、零碎片化的記憶體管理
//
// 關鍵學習點：
// 1. ⚡ O(1) 分配/釋放：無需遍歷 Free List，直接透過索引存取
// 2. 零碎片化：所有物件大小相同，記憶體連續排列
// 3. Free List 重用：deallocate() 釋放的記憶體可被後續 allocate() 重用
// 4. 預配置：啟動時一次性配置所有記憶體，執行時零配置
//
// 📊 效能比較：
// - malloc/new：延遲 ~50-200 ns，可能觸發系統呼叫
// - std::allocator：類似 malloc，有額外虛擬函式呼叫開銷
// - MemPool：延遲 ~1-5 ns (5-50x faster)

#include "mem_pool.h"

struct MyStruct {
    int d_[3];
};

int main(int, char**)
{
    using namespace Common;

    // 建立兩個記憶體池
    // 參數：物件數量上限（編譯期決定，無法動態擴展）
    MemPool<double> prim_pool(50);        // 儲存基本型別 (8 bytes)
    MemPool<MyStruct> struct_pool(50);    // 儲存結構 (12 bytes)

    // ⚡ 分配與釋放測試
    for (auto i = 0; i < 50; ++i) {
        // 分配並初始化記憶體
        // allocate() 內部使用 Placement New：new (ptr) T(value)
        auto p_ret = prim_pool.allocate(i);
        auto s_ret = struct_pool.allocate(MyStruct{i, i + 1, i + 2});

        std::cout << "prim elem:" << *p_ret << " allocated at:" << p_ret << std::endl;
        std::cout << "struct elem:" << s_ret->d_[0] << "," << s_ret->d_[1] << "," <<
                  s_ret->d_[2] << " allocated at:" << s_ret << std::endl;

        // ⚡ 每 5 個物件就釋放一次
        // 展示 Free List 的重用機制
        if (i % 5 == 0) {
            std::cout << "deallocating prim elem:" << *p_ret << " from:" << p_ret <<
                      std::endl;
            std::cout << "deallocating struct elem:" << s_ret->d_[0] << "," << s_ret->d_[1]
                      << "," << s_ret->d_[2] << " from:" << s_ret << std::endl;

            // deallocate() 將物件加回 Free List
            // ⚠️ 不會呼叫解構子（假設簡單型別）
            prim_pool.deallocate(p_ret);
            struct_pool.deallocate(s_ret);
        }
    }

    // ⚠️ 程式結束時，MemPool 解構子會釋放所有記憶體
    // 若物件有非平凡解構子，需手動呼叫

    return 0;
}
