// 高效能關鍵技術示例
// 章節：Essential Utilities - 檔案：Widget.cpp

#include <exception>

#include <variant>
#include <iostream>

struct Widget {
    explicit Widget(int) { throw std::exception(); }
};

// 關鍵技術：variant/visit 分派降低虛擬呼叫成本。
void attempt1(std::variant<double, Widget> &v) {
    try {
        v.emplace<1>(42);
        std::cout << "v = " << std::get<0>(v) << '\n';
    } catch (...) {
        std::cout << "exception caught\n";
        if (v.valueless_by_exception()) {
            std::cout << "valueless\n";
        } else {
            std::cout << std::get<0>(v) << '\n';
        }
    }
}

void attempt2(std::variant<double, Widget> &v) {
    try {
        v.emplace<1>(Widget(42));
        std::cout << "v = " << std::get<0>(v) << '\n';
    } catch (...) {
        std::cout << "exception caught\n";
        if (v.valueless_by_exception()) {
            std::cout << "valueless\n";
        } else {
            std::cout << std::get<0>(v) << '\n';
        }
    }
}

void attempt3(std::variant<double, Widget> v) {
    try {
        v.emplace<0>(6.9);
        std::cout << "v = " << std::get<0>(v) << '\n';
    } catch (...) {
        std::cout << "exception caught\n";
        if (v.valueless_by_exception()) {
            std::cout << "valueless\n";
        } else {
            std::cout << std::get<0>(v) << '\n';
        }
    }
}

int main()
{
    // 關鍵技術：variant/visit 分派降低虛擬呼叫成本。
    std::variant<double, Widget> v = 1.0;
    std::cout << "v = " << std::get<0>(v) << '\n';
    
    attempt1(v);
    attempt2(v);
    attempt3(v);
    
    return 0;
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// OUTPUT  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

// v = 1
// exception caught
// valueless
// exception caught
// valueless
// v = 6.9
// Program ended with exit code: 0
