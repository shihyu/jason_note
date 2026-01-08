#include <cstdio>
#include <vector>

struct Order {
    int id;
    double price;
};

// ❌ 繼承版本：公開繼承 std::vector
// 問題：額外的 vtable 指標（8 bytes）、無法內聯（若透過基類指標呼叫）
// 風險：破壞 std::vector 的語義（如呼叫方可能 delete 基類指標）
class InheritanceOrderBook : public std::vector<Order>
{
};

// ✅ 組合版本：將 std::vector 作為成員變數
// ⚡ 效能關鍵：無 vtable 開銷、size() 可完全內聯（編譯器可直接展開為成員存取）
// 原理：保持封裝性，只暴露需要的介面，編譯器優化空間更大
class CompositionOrderBook
{
    std::vector<Order> orders_;

public:
    auto size() const noexcept
    {
        return orders_.size();  // 可內聯為直接讀取 orders_.size_
    }
};

int main()
{
    InheritanceOrderBook i_book;
    CompositionOrderBook c_book;

    printf("InheritanceOrderBook::size():%lu CompositionOrderBook:%lu\n",
           i_book.size(), c_book.size());
}