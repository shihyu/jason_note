#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <thread>
#include <chrono>

// 模擬 On-CPU: 較重的計算負載
void cpu_intensive_task() {
    double result = 0;
    // 減少迴圈次數以免執行太久，但要足夠產生 CPU 負載
    for (int i = 0; i < 5000000; ++i) {
        result += std::sin(i) * std::cos(i);
    }
    if (result == 1234.567) std::cout << "Rare!" << std::endl;
}

// 模擬 Off-CPU: 睡眠/等待
void io_intensive_task() {
    // 睡眠 100ms
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
}

int main() {
    std::cout << "Starting mixed workload (CPU + Sleep)..." << std::endl;
    
    // 執行多次以收集足夠樣本
    // 假設做 20 次，每次 CPU 耗時約 0.1-0.2s, Sleep 0.1s
    // 總時間約數秒
    for (int i = 0; i < 20; ++i) {
        if (i % 5 == 0) std::cout << "Iteration " << i << "..." << std::endl;
        cpu_intensive_task();
        io_intensive_task();
    }
    
    std::cout << "Finished." << std::endl;
    return 0;
}
