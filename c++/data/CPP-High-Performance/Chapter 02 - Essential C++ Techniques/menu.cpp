// 高效能關鍵技術示例
// 章節：Essential C++ Techniques - 檔案：menu.cpp

#include <iostream>
#include <utility>

#include <initializer_list>
#include <string>
#include <vector>

class Menu {
public:
    Menu(const std::initializer_list<std::string> &items) : items_(items) { }
    
    Menu(Menu &&rhs) noexcept
    {
        // 關鍵技術：交換避免重複配置，常用於 copy-and-swap。
        std::swap(items_, rhs.items_);
        std::swap(index_, rhs.index_);
    }
    
    Menu& operator=(Menu &&rhs) noexcept
    {
        if (this != &rhs) {
            std::swap(items_, rhs.items_);
            std::swap(index_, rhs.index_);
        }
        return *this;
    }
    
    void select(int i) { index_ = i; }
    
    std::string selected() const
    {
        return index_ != -1 ? items_[index_] : "";
    }
    
private:
    std::vector<std::string> items_;
    int index_ = -1;
};

int main() {
    Menu a = { "New", "Open", "Close", "Save" };
    a.select(2);
    std::cout << a.selected() << std::endl;
    
    Menu b = std::move(a);
    
    // will crash programme without std::swap move semantics
    // std::swap in the move/move-assignment operations helps preserve ...
    // ...the no-throw guarantee
    std::string s = a.selected();
}
