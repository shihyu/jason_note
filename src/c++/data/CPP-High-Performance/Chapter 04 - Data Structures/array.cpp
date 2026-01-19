// 高效能關鍵技術示例
// 章節：Data Structures - 檔案：array.cpp

#include <array>

// 關鍵技術：資料結構配置與快取區域性。
void f(const std::array<int, 1024> &stl_arr) {
    // 關鍵技術：資料結構配置與快取區域性。
    /* do stuff */
}
void g(const int c_arr[]) { /* do stuff */ }

int main()
{
    std::array<int, 16> stl_arr;
    int c_arr[16];
    
    // f(stl_arr);  // will not compile
    g(c_arr);    // will compile, but unsafe (array decay)
    
    return 0;
}
