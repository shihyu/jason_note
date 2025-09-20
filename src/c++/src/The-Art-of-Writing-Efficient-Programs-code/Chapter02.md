# Chapter 02: 性能測量基礎

## 本章重點

本章介紹了如何測量和比較程式性能的基本概念，包括時間測量、性能基準測試以及微基準測試的實作。

## 核心概念

### 1. 子字串排序範例 (substring_sort系列)
- **檔案**: `01_substring_sort.C`, `02_substring_sort.C`, `03_substring_sort.C`, `04_substring_sort.C`
- **重點**:
  - 展示不同排序演算法的性能差異
  - 使用 `std::sort` 與自訂比較函數
  - 計算比較次數來評估演算法效率
  - 使用 `std::chrono` 進行精確時間測量

### 2. 計時器比較 (compare_timer系列)
- **檔案**: `05_compare_timer.C` ~ `09_compare_timer.C`
- **重點**:
  - 不同計時方法的精度比較
  - `system_clock` vs `steady_clock` vs `high_resolution_clock`
  - 避免編譯器優化對測量的影響
  - 使用 `volatile` 關鍵字防止優化

### 3. 微基準測試 (MicroBenchmarking, MBM)
- **檔案**: `10_compare_mbm.C`, `11_compare_mbm.C`, `12_compare_mbm.C`系列
- **重點**:
  - 建立可重複的性能測試框架
  - 處理測量誤差和變異性
  - 多次運行取平均值
  - 預熱快取的重要性

## 關鍵技術要點

### 時間測量
```cpp
using std::chrono::duration_cast;
using std::chrono::milliseconds;
using std::chrono::system_clock;

system_clock::time_point t1 = system_clock::now();
// 執行待測程式碼
system_clock::time_point t2 = system_clock::now();
cout << "Time: " << duration_cast<milliseconds>(t2 - t1).count() << "ms" << endl;
```

### 防止編譯器優化
```cpp
volatile int result = 0;  // volatile 防止編譯器優化掉計算
for (int i = 0; i < N; ++i) {
    result += compute_something(i);
}
```

### 性能計數器
- 使用比較次數作為演算法複雜度指標
- 記錄快取命中/失效率
- 測量記憶體存取模式的影響

## 最佳實踐

1. **測量前的準備**
   - 確保系統負載穩定
   - 關閉不必要的背景程式
   - 使用 Release 模式編譯（-O2 或 -O3）

2. **測量方法**
   - 多次執行取平均值
   - 排除異常值（outliers）
   - 記錄標準差以了解變異性

3. **避免常見陷阱**
   - 編譯器可能優化掉空迴圈
   - 快取效應可能影響結果
   - 第一次執行通常較慢（冷啟動）

## 編譯指令範例
```bash
g++ 01_substring_sort.C 01_substring_sort_a.C -g -O3 -I. --std=c++17 -o 01_substring_sort
```

## 實驗建議

1. 比較不同優化等級（-O0, -O1, -O2, -O3）的影響
2. 測試不同資料大小的擴展性
3. 分析快取對性能的影響
4. 使用 perf 或 vtune 進行更深入的性能分析