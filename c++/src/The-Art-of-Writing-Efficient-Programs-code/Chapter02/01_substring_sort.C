// 子字串排序程式
// 編譯方式：
// $CXX 01_substring_sort.C 01_substring_sort_a.C -g -O3 -I. --std=c++17 -o 01_substring_sort
#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <memory>
#include <random>
#include <vector>

// 使用 std 命名空間的時間相關類別
using std::chrono::duration_cast;
using std::chrono::milliseconds;
using std::chrono::system_clock;
using std::cout;
using std::endl;
using std::minstd_rand;
using std::unique_ptr;
using std::vector;

// 比較函數宣告：比較兩個字串前 l 個字元
bool compare(const char* s1, const char* s2, unsigned int l);

int main() {
// 引入初始化程式碼（包含測試資料準備）
#include "00_substring_sort_prep.C"

    size_t count = 0; // 比較次數計數器
    // 使用 lambda 函數對字串向量進行排序，同時計算比較次數
    std::sort(vs.begin(), vs.end(), [&](const char* a, const char* b) { ++count; return compare(a, b, L); });
    //for (unsigned int i = 0; i < N; ++i) cout << "vs[" << i << "]=" << vs[i] << endl;

    // 記錄排序結束時間
    system_clock::time_point t2 = system_clock::now();
    // 輸出排序時間和比較次數
    cout << "Sort time: " << duration_cast<milliseconds>(t2 - t1).count() << "ms (" << count << " comparisons)" << endl;
}
