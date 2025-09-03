#include <iostream>
#include <vector>
#include <string>

int main()
{
    std::vector<std::string> messages = {
        "Hello from GCC 15!",
        "C++17 is the default standard",
        "Docker + GCC = 🚀"
    };

    for (const auto & msg : messages) {
        std::cout << msg << std::endl;
    }

    // 顯示 GCC 版本
    std::cout << "\nCompiled with GCC version: " << __VERSION__ << std::endl;

    return 0;
}
