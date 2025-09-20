# Chapter 04: 記憶體架構和性能影響

## 本章重點

深入探討記憶體階層結構、快取行為、記憶體存取模式對程式性能的關鍵影響。

## 核心概念

### 1. 快取記憶體測試系列
- **檔案**: `01a_cache_random_read.C`, `01b_cache_random_write.C`
- **重點**: 隨機存取模式的快取效能

- **檔案**: `01c_cache_sequential_read.C`, `01d_cache_sequential_write.C`
- **重點**: 循序存取模式的快取效能

- **檔案**: `01e_cache_sequential_readi.C`, `01f_cache_sequential_writei.C`
- **重點**: 帶索引的循序存取優化

### 2. 記憶體存取模式比較
- **檔案**: `02a_cache_random_read.C`, `02b_cache_random_read.C`
- **重點**: 不同隨機存取實作的性能差異

## 記憶體階層結構

### 典型快取階層
```
暫存器 (Registers)     : ~1 cycle
L1 快取 (32-64 KB)     : ~4 cycles
L2 快取 (256-512 KB)   : ~12 cycles
L3 快取 (8-32 MB)      : ~40 cycles
主記憶體 (RAM)          : ~200 cycles
```

### 快取行 (Cache Line)
- 典型大小: 64 bytes
- 資料以快取行為單位載入
- 空間局部性的重要性

## 關鍵技術要點

### 循序 vs 隨機存取
```cpp
// 循序存取 - 快取友善
for (int i = 0; i < N; ++i) {
    sum += array[i];  // 連續記憶體存取
}

// 隨機存取 - 快取不友善
for (int i = 0; i < N; ++i) {
    sum += array[random_index[i]];  // 跳躍式存取
}
```

### 行主序 vs 列主序遍歷
```cpp
// 行主序遍歷（C/C++ 友善）
for (int i = 0; i < rows; ++i) {
    for (int j = 0; j < cols; ++j) {
        process(matrix[i][j]);  // 連續記憶體
    }
}

// 列主序遍歷（快取不友善）
for (int j = 0; j < cols; ++j) {
    for (int i = 0; i < rows; ++i) {
        process(matrix[i][j]);  // 跳躍式存取
    }
}
```

### 資料結構對齊
```cpp
// 對齊的結構（較佳）
struct alignas(64) CacheAligned {
    int data[16];  // 剛好一個快取行
};

// 填充避免偽共享
struct PaddedCounter {
    alignas(64) int counter1;
    alignas(64) int counter2;  // 不同快取行
};
```

## 快取優化技術

### 1. 預取 (Prefetching)
```cpp
// 手動預取
for (int i = 0; i < N; ++i) {
    __builtin_prefetch(&array[i + 8], 0, 3);  // 預取未來資料
    process(array[i]);
}
```

### 2. 循環分塊 (Loop Tiling)
```cpp
// 分塊矩陣乘法
const int TILE = 64;
for (int ii = 0; ii < N; ii += TILE) {
    for (int jj = 0; jj < N; jj += TILE) {
        for (int kk = 0; kk < N; kk += TILE) {
            // 處理 TILE x TILE 的子矩陣
            for (int i = ii; i < min(ii + TILE, N); ++i) {
                for (int j = jj; j < min(jj + TILE, N); ++j) {
                    for (int k = kk; k < min(kk + TILE, N); ++k) {
                        C[i][j] += A[i][k] * B[k][j];
                    }
                }
            }
        }
    }
}
```

### 3. 資料結構重組
```cpp
// Array of Structures (AoS) - 可能導致快取浪費
struct Point { float x, y, z; };
Point points[N];

// Structure of Arrays (SoA) - 更好的快取利用
struct Points {
    float x[N], y[N], z[N];
};
```

## 記憶體存取模式分析

### 測量快取效能
```bash
# 使用 perf 測量快取命中/失效
perf stat -e L1-dcache-loads,L1-dcache-load-misses ./program
perf stat -e LLC-loads,LLC-load-misses ./program

# Valgrind cachegrind
valgrind --tool=cachegrind ./program
```

## 偽共享 (False Sharing)

### 問題範例
```cpp
// 偽共享問題
struct Counter {
    int count1;  // 線程 1 使用
    int count2;  // 線程 2 使用，但在同一快取行
};

// 解決方案
struct Counter {
    alignas(64) int count1;
    alignas(64) int count2;  // 獨立快取行
};
```

## 最佳實踐

1. **資料局部性**
   - 保持相關資料緊密存放
   - 按存取順序組織資料
   - 重用已載入的快取行

2. **存取模式**
   - 優先循序存取
   - 避免大步幅存取
   - 考慮資料預取

3. **資料結構設計**
   - 考慮快取行大小
   - 避免偽共享
   - 使用快取友善的演算法

## 實驗建議

1. 測量不同陣列大小的存取時間，觀察快取層級
2. 比較行主序和列主序遍歷的性能差異
3. 實作並測試循環分塊的效果
4. 分析偽共享對多執行緒性能的影響

## 重要觀察

- L1 快取命中比主記憶體快約 50-200 倍
- 良好的快取利用可帶來 10x 以上的性能提升
- 記憶體頻寬往往是性能瓶頸
- 簡單的存取模式讓硬體預取更有效