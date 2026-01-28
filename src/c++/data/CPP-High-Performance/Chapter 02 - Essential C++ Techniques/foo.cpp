// 高效能關鍵技術示例
// 章節：Essential C++ Techniques - 檔案：foo.cpp

#include <iostream>
#include <utility>

struct Foo {
    // performs like "const"
    void func() && { std::cout << "This object is an rvalue" << std::endl; }
    
    // for normal lvalue refs
    void func() & { std::cout << "This object is an lvalue ref" << std::endl; }
};

int main() {
    Foo bar;
    
    // without separate & and && member function modifiers we receive the following error:
    // 'this' argument to member function 'func' is an lvalue, but function has rvalue ref-qualifier
    
    // lvalue ref
    bar.func();
    
    // rvalue
    // 關鍵技術：std::move 觸發移動語意，降低拷貝成本。
    std::move(bar).func();
    
    // rvalue
    Foo().func();
}
