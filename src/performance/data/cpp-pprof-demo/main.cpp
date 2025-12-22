#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>

// 模擬較重的計算負載
void slow_function() {
    double result = 0;
    for (int i = 0; i < 20000000; ++i) {
        result += std::sin(i) * std::cos(i);
    }
    // 輸出以防止編譯器優化掉整個迴圈
    if (result == 1234.567) std::cout << "Rare!" << std::endl;
}

// 模擬較輕的計算負載
void fast_function() {
    std::vector<int> data(1000000);
    for (int i = 0; i < 1000000; ++i) {
        data[i] = rand() % 1000;
    }
    std::sort(data.begin(), data.end());
}

int main() {
    std::cout << "Starting CPU intensive tasks..." << std::endl;
    
    for (int i = 0; i < 5; ++i) {
        std::cout << "Iteration " << i + 1 << "..." << std::endl;
        slow_function();
        fast_function();
    }
    
    std::cout << "Finished. Profile data should be generated." << std::endl;
    return 0;
}
